[CmdletBinding()]
param(
    [ValidateRange(1, 3600)]
    [int]$HealthTimeoutSec = 240
)

$ErrorActionPreference = 'Stop'
$apiUrl = 'http://localhost:8000'

Push-Location -LiteralPath $PSScriptRoot
try {
    Write-Host 'Avvio database e backend...'
    docker compose up -d db backend
    if ($LASTEXITCODE -ne 0) {
        throw 'Avvio non riuscito. Verifica che Docker Desktop sia in esecuzione.'
    }

    Write-Host 'Attendo che il backend sia pronto...'
    $deadline = (Get-Date).AddSeconds($HealthTimeoutSec)
    $ready = $false
    do {
        try {
            $health = Invoke-RestMethod -Method Get -Uri "$apiUrl/health" -TimeoutSec 5
            $ready = $health.status -eq 'ok'
        }
        catch {
            # Il backend potrebbe ancora applicare le migration o avviarsi.
        }
        if (-not $ready -and (Get-Date) -lt $deadline) {
            Start-Sleep -Seconds 2
        }
    } until ($ready -or (Get-Date) -ge $deadline)

    if (-not $ready) {
        throw 'Backend non pronto. Controlla con: docker compose logs --tail=80 backend'
    }

    Write-Host 'Importo le notizie da NewsData.io...'
    $import = Invoke-RestMethod -Method Post -Uri "$apiUrl/news/extract" -TimeoutSec 900
    Write-Host "Nuove notizie salvate: $($import.inserted_count)"

    Write-Host 'Aggiorno le notifiche degli utenti...'
    $notifications = Invoke-RestMethod -Method Get -Uri "$apiUrl/notifications/users" -TimeoutSec 1800
    $savedCount = @($notifications | Where-Object { $_.notification.generated_news.Count -gt 0 }).Count
    Write-Host "Nuove notifiche salvate: $savedCount"
}
finally {
    Pop-Location
}
