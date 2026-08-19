# MATRICE DE CONFUZIE — CEO (randuri) vs detector 0.4.1 (coloane), pe BARE

Detectorul NU produce niciodata `ESTABLISHED`, deci nu exista coloana de range confirmat.

| CEO \ detector | BREACH_PENDING | ESTABLISHING | total |
|---|---|---|---|
| **RANGE** | 683 (9%) | 7012 (91%) | 7695 |
| **CHANNEL_UP** | 235 (10%) | 2060 (90%) | 2295 |
| **CHANNEL_DOWN** | 190 (10%) | 1780 (90%) | 1970 |
| **TRANSITION** | 112 (12%) | 838 (88%) | 950 |

## Evenimente: CEO vs detector (numar brut, 45 ferestre)

| eveniment CEO | n | eveniment detector | n | raport |
|---|---|---|---|---|
| BREAKOUT_UP | 31 | BREAKOUT_ACCEPTANCE_UP | 247 | 8.0x supra-emisie |
| BREAKOUT_DOWN | 21 | BREAKOUT_ACCEPTANCE_DOWN | 262 | 12.5x |
| SWEEP_UP + FAILED_BREAKOUT_UP | 31 | LIQUIDITY_SWEEP_UP | 473 | 15.3x |
| SWEEP_DOWN + FAILED_BREAKOUT_DOWN | 41 | LIQUIDITY_SWEEP_DOWN | 474 | 11.6x |
| RANGE (segmente) | 103 | RANGE_ESTABLISHED | **0** | **niciunul** |

> Evenimentele detectorului NU sunt aceleasi obiecte ca ale CEO: ele se emit din segmente
> NECONFIRMATE si dureaza cel mult 2 bare, pe cand sweep-urile CEO au mediana 10 si maxim 22 bare.
