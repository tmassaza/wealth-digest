# Test del modello di embedding

Il test misura quanto MiniLM riesce ad associare le news ai profili degli utenti. Usa 6 profili e 60 news inventate, con un voto manuale da 0 a 3 per ogni coppia utente-news:

- `3`: molto affine;
- `2`: affine;
- `1`: parzialmente affine;
- `0`: fuori tema.

I voti 2 e 3 sono considerati pertinenti. I dati si trovano in `tests/dati_prova/`.

## Eseguire il test

Dalla root del progetto, con `.venv` attivo:

```powershell
python -m tests.evaluate_retrieval
```

Il comando usa lo stesso modello e la stessa costruzione `titolo + summary` dell'applicazione. Non usa PostgreSQL, NewsData o il modello generativo. Al termine:

- mostra due tabelle brevi nel terminale;
- aggiorna `tests/reports/risultati-minilm.md`;
- mostra affini, parziali e fuori tema nelle Top 10;
- indica quante news pertinenti entrano nelle Top 20 e quante rimangono fuori.

Il primo avvio può scaricare MiniLM se non è già nella cache.

## Analizzare un singolo utente

Per vedere, per esempio, le prime 20 news di Elena:

```powershell
python -m tests.evaluate_retrieval --user U03 --top 20
```

Questa modalità mostra anche score, voto atteso e titolo di ogni risultato.

## Limiti

Il dataset è piccolo, sintetico e basato su una singola revisione manuale dei giudizi di pertinenza. Il test serve a controllare il comportamento del retrieval in modo ripetibile, ma non dimostra le prestazioni sulle news reali.
