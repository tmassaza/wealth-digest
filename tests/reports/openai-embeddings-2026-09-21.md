# Confronto embedding OpenAI — 21 settembre 2026

Per una lettura più semplice insieme a MiniLM, vedi il [confronto complessivo](confronto-modelli-2026-09-22.md). Qui restano i dettagli delle prime due esecuzioni OpenAI.

Dataset sintetico v1: 6 profili, 60 news, 360 voti provvisori. Stessi testi e stessa funzione di ranking del benchmark MiniLM: profilo utente contro `Titolo: ...\nSummary: ...`, similarità coseno, voto 2 o 3 = pertinente. Nessun database e nessuna modifica all'app. OpenAI ha elaborato 66 testi e 3545 token di input per modello e per esecuzione. Il test è stato eseguito due volte (la seconda per esaminare gli score): 7090 token per modello in totale. Costo teorico ai prezzi pubblici: circa $0,00014 per small e $0,00092 per large per le due esecuzioni; il costo effettivo dipende dalla fatturazione dell'organizzazione.

| Utente | MiniLM Top 10 | 3-small Top 10 | 3-large Top 10 |
|---|---:|---:|---:|
| Giulia | 7/10 | 5/10 | 9/10 |
| Marco | 7/10 | 7/10 | 7/10 |
| Elena | 9/10 | 8/10 | 9/10 |
| Luca | 9/10 | 5/10 | 7/10 |
| Sara | 7/10 | 6/10 | 4/10 |
| Davide | 7/10 | 4/10 | 5/10 |
| **Totale** | **46/60** | **35/60** | **41/60** |

| Metrica complessiva | MiniLM | 3-small | 3-large |
|---|---:|---:|---:|
| News con voto 0 nelle sei Top 10 | 5 | 6 | 4 |
| Coppie pertinenti rimaste oltre la Top 20 | 30/93 | 29/93 | 29/93 |

N90 (posizione minima per recuperare almeno il 90% delle news pertinenti):

| Utente | MiniLM | 3-small | 3-large |
|---|---:|---:|---:|
| Giulia | 37 | 31 | 28 |
| Marco | 46 | 31 | 33 |
| Elena | 23 | 23 | 22 |
| Luca | 22 | 42 | 37 |
| Sara | 31 | 26 | 33 |
| Davide | 40 | 45 | 33 |

**Lettura:** su questo piccolo dataset MiniLM resta il migliore per precisione nelle Top 10. `3-large` migliora Giulia ma peggiora Sara e Davide; `3-small` è inferiore nel complesso. Nessuno dei tre recupera tutte le news pertinenti entro la Top 20. I voti sono provvisori e assegnati da una sola persona: non basta questo test per stabilire quale modello sia migliore sulle news reali.

Gli score si sovrappongono: con `3-small`, per Giulia una news con voto 1 è al primo posto con score 0,5128, mentre una con voto 2/3 arriva al posto 45 con score 0,3464. Con `3-large`, per Elena una news con voto 1 è al posto 6 con score 0,4556, mentre una con voto 2/3 arriva al posto 41 con score 0,3240. Quindi una soglia fissa basata sullo score scarterebbe news giudicate pertinenti senza eliminare tutte quelle poco pertinenti. Il voto 1 significa pertinenza parziale, non totale estraneità.

I valori grezzi di cosine similarity non vanno confrontati direttamente tra modelli diversi: sono utili l'ordine, la precisione e il recupero delle news pertinenti. Per ripetere il test, usare `python -m tests.evaluate_openai_embeddings`.
