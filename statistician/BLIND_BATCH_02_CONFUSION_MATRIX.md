# MATRICE DE CONFUZIE — CEO (randuri) vs 0.4.1 (coloane), pe BARE — POPULATIA COMPLETA (48)

Nu exista coloana `ESTABLISHED`: detectorul nu produce niciodata starea de range confirmat.

| CEO \ detector | BREACH_PENDING | ESTABLISHING | total |
|---|---|---|---|
| **RANGE** | 728 (9%) | 7471 (91%) | 8199 |
| **CHANNEL_UP** | 245 (10%) | 2142 (90%) | 2387 |
| **CHANNEL_DOWN** | 209 (10%) | 1959 (90%) | 2168 |
| **TRANSITION** | 120 (12%) | 901 (88%) | 1021 |

## Evenimente — CEO vs detector (48 ferestre)

| eveniment CEO | n | eveniment detector | n | raport |
|---|---|---|---|---|
| BREAKOUT_UP | 34 | BREAKOUT_ACCEPTANCE_UP | 263 | 7.7x supra-emisie |
| BREAKOUT_DOWN | 24 | BREAKOUT_ACCEPTANCE_DOWN | 282 | 11.8x |
| SWEEP_UP + FAILED_BREAKOUT_UP | 33 | LIQUIDITY_SWEEP_UP | 499 | 15.1x |
| SWEEP_DOWN + FAILED_BREAKOUT_DOWN | 44 | LIQUIDITY_SWEEP_DOWN | 505 | 11.5x |
| RANGE (segmente) | 114 | RANGE_ESTABLISHED | **0** | **niciunul** |

> Evenimentele detectorului se emit din segmente NECONFIRMATE si dureaza cel mult 2 bare;
> sweep-urile CEO au mediana 10 si maximul 22. Sunt obiecte diferite cu acelasi nume.
