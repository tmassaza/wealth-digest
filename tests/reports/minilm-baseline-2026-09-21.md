# Baseline MiniLM — 21 settembre 2026

Per una lettura più semplice insieme agli altri modelli, vedi il [confronto complessivo](confronto-modelli-2026-09-22.md). Qui restano i dettagli della prova MiniLM.

Dataset sintetico v1: 6 profili, 60 news, 360 voti attesi provvisori. Modello `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; profilo utente contro `Titolo: ...\nSummary: ...`. Una news è considerata pertinente con voto 2 o 3. Nessuna chiamata a NewsData o Gemini.

| Utente | Pertinenti nelle Top 10 | Recuperate entro 20 | Entro 30 | Entro 40 | Entro 50 | Posizione per il 90% | Ultima news con voto 3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Giulia | 7/10 | 53% | 84% | 100% | 100% | 37 | 39 |
| Marco | 7/10 | 59% | 82% | 88% | 100% | 46 | 46 |
| Elena | 9/10 | 85% | 92% | 92% | 100% | 23 | 11 |
| Luca | 9/10 | 87% | 93% | 93% | 93% | 22 | 52 |
| Sara | 7/10 | 67% | 83% | 92% | 100% | 31 | 31 |
| Davide | 7/10 | 65% | 82% | 94% | 100% | 40 | 46 |

Le sei Top 10 contengono in totale 5 risultati con voto 0. La Top 20 lascia fuori 30 **coppie utente-news** con voto 2 o 3; non sono necessariamente 30 news diverse.

Casi da riesaminare con una persona prima di trarre conclusioni: `N013` per Elena ha voto 2 ma arriva al posto 47 con score 0,1908; `N032` per Luca ha voto 3 ma arriva al posto 52 con score 0,2960. Anche alcuni voti 0 nelle Top 10 potrebbero richiedere una discussione sulla definizione di pertinenza, per esempio una notizia sul rischio delle obbligazioni speculative per un profilo prudente.

Limiti: questo è un dataset piccolo e inventato, con voti iniziali assegnati da un solo valutatore. Non misura le prestazioni sulle news reali né dimostra che una soglia di score sia sicura. L'API delle raccomandazioni accetta attualmente al massimo `top_n=50`, quindi una news al posto 52 non sarebbe recuperabile con quell'endpoint.
