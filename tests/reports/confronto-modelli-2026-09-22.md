# Quale embedding recupera le news giuste?

Questo è il riepilogo leggibile dei test del 21–22 settembre 2026. Abbiamo usato **gli stessi 6 profili e le stesse 60 news inventate** per MiniLM, OpenAI `text-embedding-3-small` e OpenAI `text-embedding-3-large`. Per ogni utente, abbiamo dato a ciascuna news un voto provvisorio:

| Voto | Significato nel test |
|---|---|
| 3 | Molto pertinente |
| 2 | Pertinente |
| 1 | Solo parzialmente pertinente |
| 0 | Fuori tema |

I voti 2 e 3 sono considerati **news da recuperare**. In tutto sono 93 *coppie utente-news*: la stessa news può essere pertinente per più utenti. Gli score di modelli diversi non vanno confrontati direttamente; qui confrontiamo **quali news finiscono nelle prime posizioni**.

## 1. Le prime 10 news sono buone?

Ogni modello restituisce 10 news per ciascuno dei 6 utenti: **60 posizioni in totale**. Più news con voto 2–3 e meno news con voto 0 è meglio.

| Modello | Pertinenti (2–3) | Parziali (1) | Fuori tema (0) |
|---|---:|---:|---:|
| MiniLM | **46/60** | 9/60 | 5/60 |
| OpenAI 3-small | 35/60 | 19/60 | 6/60 |
| OpenAI 3-large | 41/60 | 15/60 | **4/60** |

MiniLM mette più news chiaramente pertinenti nelle prime 10. `3-large` mette meno news completamente fuori tema, ma più news solo parzialmente pertinenti. Non è quindi corretto dire che le sue prime 10 siano piene di risultati assurdi.

| Utente | MiniLM: pertinenti nelle prime 10 | 3-small | 3-large |
|---|---:|---:|---:|
| Giulia | 7 | 5 | **9** |
| Marco | 7 | 7 | 7 |
| Elena | **9** | 8 | **9** |
| Luca | **9** | 5 | 7 |
| Sara | **7** | 6 | 4 |
| Davide | **7** | 4 | 5 |

## 2. Quante news buone recuperiamo scegliendo una Top N?

Qui guardiamo tutte le **93 coppie pertinenti**. Per esempio, `63/93` in Top 20 significa che 63 news pertinenti compaiono entro la ventesima posizione per il rispettivo utente; le altre 30 restano fuori dalla selezione. Più alto è il numero, meno news buone perdiamo.

| News candidate prese per utente | MiniLM | 3-small | 3-large |
|---|---:|---:|---:|
| Top 10 | 46/93 (49%) | 35/93 (38%) | 41/93 (44%) |
| Top 20 | 63/93 (68%) | 64/93 (69%) | 64/93 (69%) |
| Top 30 | 80/93 (86%) | 81/93 (87%) | 81/93 (87%) |
| Top 40 | 87/93 (94%) | 88/93 (95%) | **89/93 (96%)** |
| Top 50 | 92/93 (99%) | **93/93 (100%)** | 92/93 (99%) |

La **Top 20 non basta** se l'obiettivo è recuperare quasi tutte le news pertinenti: con ogni modello ne perdiamo 29–30 su 93. Per arrivare vicino al 90% complessivo bisogna superare la Top 30. Questo non fissa automaticamente il numero da inviare al secondo passaggio: il test è piccolo e inventato.

## 3. Perché non basta una soglia di score?

Uno score alto significa che i testi risultano simili al modello, non che la news sia sicuramente utile. Per Giulia, `3-small` mette al primo posto una news con voto 1 e score 0,5128, mentre una con voto 2 arriva al posto 45 con score circa 0,3466. Abbassare o alzare una soglia fissa non separa perfettamente le due categorie. Inoltre gli score di MiniLM e OpenAI usano scale diverse: uno `0,5` non ha lo stesso significato pratico in entrambi.

## Cosa possiamo concludere, e cosa no

**Su questi esempi sintetici** MiniLM è il più preciso nelle prime 10; i tre modelli recuperano quasi lo stesso numero di news pertinenti nelle Top 20–30. Non abbiamo dimostrato che MiniLM sia migliore su notizie reali: i 360 voti sono stati assegnati inizialmente da una sola persona e alcune news con voto 1 potrebbero essere comunque interessanti per un utente. Prima di scegliere un modello o una Top N definitiva, conviene far rivedere i casi controversi a voi e ripetere la prova su news reali.

Dettagli tecnici e casi specifici: [baseline MiniLM](minilm-baseline-2026-09-21.md) e [test OpenAI](openai-embeddings-2026-09-21.md). Entrambi confrontano i vettori localmente tramite similarità coseno, senza pgvector.
