# Risultati del test MiniLM

- Dataset: 6 profili e 60 news sintetiche.
- Input delle news: titolo + summary.
- Voto manuale: da 0 (fuori tema) a 3 (molto affine).
- News pertinente: voto 2 o 3.

## Qualità delle Top 10

| Utente | Affini | Parziali | Fuori tema |
|---|---:|---:|---:|
| Giulia Rossi | 8/10 | 1 | 1 |
| Marco Bianchi | 10/10 | 0 | 0 |
| Elena Conti | 9/10 | 1 | 0 |
| Luca Ferri | 9/10 | 0 | 1 |
| Sara Romano | 7/10 | 1 | 2 |
| Davide Moretti | 8/10 | 1 | 1 |
| **Totale** | **51/60 (85%)** | **4/60 (7%)** | **5/60 (8%)** |

## Recupero delle news pertinenti nella Top 20

| Utente | Pertinenti totali | Nella Top 20 | Fuori dalla Top 20 |
|---|---:|---:|---:|
| Giulia Rossi | 23 | 12/23 (52%) | 11/23 (48%) |
| Marco Bianchi | 28 | 15/28 (54%) | 13/28 (46%) |
| Elena Conti | 13 | 11/13 (85%) | 2/13 (15%) |
| Luca Ferri | 16 | 13/16 (81%) | 3/16 (19%) |
| Sara Romano | 14 | 8/14 (57%) | 6/14 (43%) |
| Davide Moretti | 20 | 12/20 (60%) | 8/20 (40%) |
| **Totale** | **114** | **71/114 (62%)** | **43/114 (38%)** |
