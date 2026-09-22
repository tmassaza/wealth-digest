# Test del retrieval

I dati in `tests/dati_prova/` contengono sei profili, 60 news **inventate** e un voto atteso da 0 a 3 per ogni coppia utente-news. Il voto 2 o 3 conta come pertinente. I voti sono provvisori: un risultato inatteso va discusso prima di cambiare le etichette, per non adattare il test al modello.

Per capire i risultati senza leggere le metriche tecniche, parti dal [confronto dei tre modelli](reports/confronto-modelli-2026-09-22.md): separa la qualità delle prime 10 news dalla quantità di news pertinenti che si perdono scegliendo una Top N.

## Prova locale con MiniLM

Dalla root del progetto, con `.venv` attivo:

```powershell
python -m tests.evaluate_retrieval --summary-only
```

Mostra precisione nelle Top 10, copertura delle news pertinenti nelle Top 20/30/40/50 e la posizione necessaria per recuperarne almeno il 90%. Non usa PostgreSQL, NewsData o Gemini. Per vedere la Top 20 di un solo utente:

```powershell
python -m tests.evaluate_retrieval --user U03 --top 20
```

Il primo avvio può scaricare MiniLM se non è già nella cache. Se il modello è già presente e vuoi evitare controlli di rete, imposta `HF_HUB_OFFLINE=1` nel terminale.

## Confronto locale con gli embedding OpenAI

Metti `OPENAI_API_KEY` nel `.env` locale (non nel repository). Per verificare il dataset senza inviare richieste:

```powershell
python -m tests.evaluate_openai_embeddings --dry-run
```

Per confrontare `text-embedding-3-small` e `text-embedding-3-large` sugli stessi 66 testi:

```powershell
python -m tests.evaluate_openai_embeddings
```

Questo comando effettua una chiamata API a pagamento per modello. Stampa precisione Top 10, copertura Top 20/30/40/50, posizione per recuperare il 90% delle news pertinenti e i voti delle Top 10. Non usa né modifica PostgreSQL o pgvector e non cambia il modello dell'app. Il [confronto leggibile](reports/confronto-modelli-2026-09-22.md) riassume i risultati; i dettagli della prima prova OpenAI sono in `tests/reports/openai-embeddings-2026-09-21.md`.
