# Alembic nel progetto Wealth Digest

Questa cartella contiene la configurazione e gli script di migration del database.

## A cosa serve Alembic

Alembic gestisce l'evoluzione dello schema nel tempo.
In pratica evita modifiche manuali non tracciate e consente a tutto il team di avere lo stesso schema.

Comandi principali:

- Creare una nuova migration: `python -m uv run alembic revision -m "descrizione"`
- Creare una bozza automatica dai modelli: `python -m uv run alembic revision --autogenerate -m "descrizione"`
- Applicare tutte le migration: `python -m uv run alembic upgrade head`
- Tornare indietro di una migration: `python -m uv run alembic downgrade -1`
- Vedere lo storico: `python -m uv run alembic history`
- Vedere la revisione corrente: `python -m uv run alembic current`

Se preferisci non usare `uv run`:

- `.\.venv\Scripts\python.exe -m alembic revision -m "descrizione"`
- `.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "descrizione"`
- `.\.venv\Scripts\python.exe -m alembic upgrade head`
- `.\.venv\Scripts\python.exe -m alembic downgrade -1`
- `.\.venv\Scripts\python.exe -m alembic history`
- `.\.venv\Scripts\python.exe -m alembic current`

## Autogenerate: cosa fa davvero

Alembic non fa "auto update" diretto del DB: crea una bozza di migration da rivedere.

Flusso consigliato:

1. Modifichi i modelli SQLAlchemy.
2. Generi la bozza: `alembic revision --autogenerate -m "..."`.
3. Rivedi il file in `versions/` (sempre, a mano).
4. Applichi la migration con `alembic upgrade head`.

Nota pratica:

- Nel tuo progetto `compare_type=True` è già attivo in `env.py`, quindi Alembic prova anche a rilevare cambi di tipo colonna.
- Alcune modifiche complesse possono comunque richiedere intervento manuale nella migration generata.

## Struttura della cartella

- `env.py`: bootstrap di Alembic. Configura connessione DB e metadata SQLAlchemy.
- `versions/`: contiene i file di migration versionati.
- `script.py.mako`: template usato da Alembic quando genera una nuova migration.

## Come leggere script.py.mako

`script.py.mako` non è una migration eseguibile: è un modello testuale.

Placeholder principali:

- `${up_revision}`: id della nuova revisione.
- `${down_revision}`: revisione precedente da cui parte la nuova migration.
- `${upgrades}`: blocco Python da eseguire in `upgrade()`.
- `${downgrades}`: blocco Python da eseguire in `downgrade()`.

Quando lanci `alembic revision`, Alembic copia questo template e sostituisce i placeholder con valori reali.