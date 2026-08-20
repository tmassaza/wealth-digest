# Wealth Digest

POC minimo per il matching semantico tra profili utente e notizie, usando FastAPI, PostgreSQL e pgvector.

## Workflow locale standard

Questo repository usa `uv` come tool Python standard.

### Prerequisiti

- Docker Desktop
- `uv`

### Primo setup

```powershell
cd wealth-digest
python -m uv python install 3.11
python -m uv venv --python 3.11 .venv
python -m uv sync
```

Se `uv` è già nel PATH, puoi usare la forma più corta:

```powershell
uv python install 3.11
uv venv --python 3.11 .venv
uv sync
```

### Interprete VS Code

In VS Code seleziona questo interprete:

`.venv\Scripts\python.exe`

### Avvio in locale

Usa Docker per il database e Python locale per l'app:

```powershell
docker compose up db -d
python -m uv run alembic upgrade head
python -m uv run uvicorn app.main:app --reload
```

Nota: `uv run` verifica prima che l'ambiente sia sincronizzato con `pyproject.toml` e `uv.lock`.
Se vedi `Installing wheels...`, non è un errore: `uv` sta preparando dipendenze mancanti.
Nel nostro progetto questa fase può essere lenta al primo avvio.

Se vuoi eseguire subito i comandi senza attendere la sincronizzazione di `uv run`, usa direttamente il Python del venv:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### Seed dei dati fake

```powershell
.\.venv\Scripts\python.exe scripts\seed_fake_data.py
```

### Verifica rapida (compilazione e import)

Per controllare velocemente errori sintattici nei moduli principali:

```powershell
python -m compileall app scripts alembic
```

Per verificare che i pacchetti core siano risolvibili nell'ambiente:

```powershell
python -m uv run python -c "import fastapi, sqlalchemy, alembic, pgvector; print('ok')"
```

### Comandi Alembic utili

Generare una bozza migration dai modelli (da rivedere a mano):

```powershell
python -m uv run alembic revision --autogenerate -m "descrizione"
```

Stato attuale della migration applicata:

```powershell
python -m uv run alembic current
```

Storico delle revisioni:

```powershell
python -m uv run alembic history
```

Rollback di una migration (solo ambiente di sviluppo):

```powershell
python -m uv run alembic downgrade -1
```

Se `uv run` è lento o resta su `Installing wheels...`, puoi usare gli equivalenti diretti:

```powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic downgrade -1
```

### Spegnimento servizi Docker

Fermare e rimuovere container e rete del progetto:

```powershell
docker compose down
```

Fermare, rimuovere container/rete e anche il volume dati del database:

```powershell
docker compose down -v
```

## Workflow Docker

Per eseguire sia database sia backend in container:

```powershell
docker compose up --build
```

Questo è il flusso di team più riproducibile, perché Python, dipendenze e PostgreSQL sono tutti definiti nel repository.

## Come è costruito l'ambiente Python

La cartella `.venv` viene generata dai comandi di setup, in particolare:

```powershell
python -m uv venv --python 3.11 .venv
python -m uv sync
```

Dentro `.venv` trovi in pratica:

- l'eseguibile Python dell'ambiente virtuale
- gli script installati, come `alembic.exe` e `uvicorn.exe`
- i pacchetti Python installati per il progetto

Questa cartella serve a isolare le dipendenze del progetto dal resto della macchina.

## Regole di team

- Usa Python 3.11 per lo sviluppo locale.
- Usa `uv` per gestire ambiente e lock file.
- Non installare dipendenze del progetto manualmente senza aggiornare `pyproject.toml` e `uv.lock`.
- Esegui le migration tramite Alembic, non modificando il database a mano.
