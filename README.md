# Wealth Digest

Wealth Digest seleziona notizie finanziarie affini al profilo di un utente. È un progetto FastAPI con PostgreSQL e pgvector: il modello multilingue MiniLM crea gli embedding, mentre il database ordina le news per distanza coseno. L'importazione delle news usa NewsData.io; Gemini è usato separatamente per generare le notifiche.

Lo schema è gestito con SQLAlchemy e Alembic. `uv` gestisce Python, l'ambiente virtuale e le dipendenze definite in `pyproject.toml` e `uv.lock`.

Gli embedding hanno 384 dimensioni. Per l'utente si usa il profilo testuale; per la news si usano titolo e summary, oppure solo il titolo se il summary manca. `content_text` viene conservato, ma non contribuisce allo score.

## Prerequisiti

I comandi seguenti sono per Windows PowerShell, dalla root del repository. Servono Docker Desktop, `uv`, una chiave NewsData.io per importare news e una chiave Gemini per avviare il backend e generare notifiche.

Se `uv` non è installato, puoi installare il gestore (non una dipendenza del progetto) con:

```powershell
python -m pip install uv
```

## Preparare l'ambiente locale

Esegui questi comandi dalla root del repository:

```powershell
uv python install 3.11
```

Installa Python 3.11 tramite `uv`; serve solo al primo setup, se non è già disponibile.

```powershell
uv venv --python 3.11 .venv
```

Crea l'ambiente isolato `.venv`; eseguilo al primo setup o se devi ricreare l'ambiente.

```powershell
uv sync --locked
```

Installa in `.venv` le dipendenze del lock file senza modificarlo; ripetilo quando cambiano le dipendenze o ricrei l'ambiente. Per aggiungere una dipendenza usa `uv add`, che aggiorna anche `pyproject.toml` e `uv.lock`.

```powershell
.\.venv\Scripts\Activate.ps1
```

Attiva `.venv` in ogni nuovo terminale prima di usare i comandi `python` qui sotto. In VS Code seleziona anche `.venv\Scripts\python.exe` come interprete.

```powershell
Copy-Item .env.example .env
```

Crea la configurazione locale al primo setup. Inserisci in `.env` i valori di `NEWSDATA_API_KEY` e `GEMINI_API_KEY`; `.env` è escluso da Git. La fonte predefinita è `ilsole24ore`, modificabile tramite `NEWS_DOMAINS` o il parametro API `domain`. Non mettere chiavi reali in `.env.example`.

## Avviare il progetto

Con `.venv` attivo, usa due terminali: il primo per preparare i dati, il secondo per lasciare in esecuzione FastAPI.

```powershell
docker compose up -d db
```

Avvia PostgreSQL con pgvector; serve ogni volta che il database non è già acceso.

```powershell
python -m alembic upgrade head
```

Applica le migration; eseguilo al primo avvio di un database vuoto e dopo nuove migration.

```powershell
python scripts\seed_fake_data.py
```

Inserisce o aggiorna i sei utenti demo senza cancellare le news; è utile quando vuoi provarne le raccomandazioni.

```powershell
python scripts\extract_news.py
```

Importa da NewsData.io le news della fonte configurata, evitando i link già presenti. Usalo quando vuoi aggiungere news reali: effettua chiamate esterne e può consumare la quota del provider.

```powershell
python -m uvicorn app.main:app --reload
```

Avvia l'API locale; lascialo aperto mentre provi gli endpoint. La documentazione interattiva è su http://127.0.0.1:8000/docs.

In un altro terminale puoi verificare l'avvio e richiedere le Top 20 per l'utente con ID 1 (sostituisci l'ID se necessario):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod 'http://127.0.0.1:8000/recommendations/users/1?top_n=20'
```

Il primo comando verifica che l'API risponda; il secondo mostra le news ordinate per similarità. Per importare news dall'API, con il backend avviato, puoi usare `POST /news/extract` dalla pagina `/docs` e scegliere un dominio diverso se serve.

Per fermare FastAPI premi `Ctrl+C`; per fermare il database senza cancellarne i dati:

```powershell
docker compose down
```

## Alternativa: backend e database in Docker

Se preferisci non usare `.venv` per avviare l'applicazione, dopo aver configurato `.env` esegui:

```powershell
docker compose up --build
```

Avvia entrambi i servizi; il backend applica automaticamente le migration. Quando i container sono attivi, puoi creare gli utenti demo o importare news con:

```powershell
docker compose exec backend python scripts/seed_fake_data.py
docker compose exec backend python scripts/extract_news.py
```

Il primo comando prepara i profili di prova; il secondo interroga NewsData.io. Per leggere i log del backend:

```powershell
docker compose logs -f backend
```

Per fermare entrambi i container senza rimuovere il volume del database usa `docker compose down`.

## Nota sugli embedding

Cambiare modello o testo di input richiede di rigenerare **sia** gli embedding degli utenti **sia** quelli delle news. Attualmente non è presente uno script di re-embedding. Non mescolare vettori prodotti da modelli diversi.
