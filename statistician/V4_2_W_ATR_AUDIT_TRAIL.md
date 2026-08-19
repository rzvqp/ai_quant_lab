# AUDIT TRAIL — calculul UNIC al lui `w_atr`, regula R-B @`4684e66`

```
formula     w_atr = MEDIAN over all labelled bands of (band_width / 2) / ATR_ref
ATR_ref     ATR(14) canonic vendorizat, la confirm_ts calculat DOAR din conditii
            independente de w_atr (swings >= n_touch pe fiecare latura SI durata >= d_macro)
n           50 contributii din 25 de segmente
mediana bruta   0.788051
operationala    0.8   (cel mai mic punct al retelei pas 0,05 >= mediana)
tol_cluster     1.6   DERIVAT
★ BLOCAT de R-B litera 6: 0,788051 > plafonul preinregistrat 0,495
```

| # | fereastra | segment | latura | banda | semilatime | bara confirm (rel) | ATR_ref | contributie |
|---|---|---|---|---|---|---|---|---|
| 1 | `BLIND-002` | 56-96 | upper | 0.50 | 0.250 | 28 | 1.0393 | **0.2405** |
| 2 | `BLIND-006` | 58-96 | upper | 0.50 | 0.250 | 28 | 0.9214 | **0.2713** |
| 3 | `BLIND-006` | 58-96 | lower | 0.50 | 0.250 | 28 | 0.9214 | **0.2713** |
| 4 | `BLIND-020` | 0-82 | upper | 0.50 | 0.250 | 28 | 0.8737 | **0.2861** |
| 5 | `BLIND-043` | 20-80 | upper | 0.50 | 0.250 | 28 | 0.8514 | **0.2936** |
| 6 | `BLIND-043` | 20-80 | lower | 0.50 | 0.250 | 28 | 0.8514 | **0.2936** |
| 7 | `BLIND-012` | 0-96 | upper | 3.00 | 1.500 | 28 | 4.8891 | **0.3068** |
| 8 | `BLIND-012` | 0-96 | lower | 3.00 | 1.500 | 28 | 4.8891 | **0.3068** |
| 9 | `BLIND-002` | 56-96 | lower | 0.70 | 0.350 | 28 | 1.0393 | **0.3368** |
| 10 | `BLIND-005` | 0-288 | upper | 2.50 | 1.250 | 28 | 3.3384 | **0.3744** |
| 11 | `BLIND-005` | 0-288 | lower | 2.50 | 1.250 | 28 | 3.3384 | **0.3744** |
| 12 | `BLIND-009` | 0-288 | upper | 3.00 | 1.500 | 28 | 3.8401 | **0.3906** |
| 13 | `BLIND-021` | 174-214 | upper | 4.00 | 2.000 | 28 | 4.4089 | **0.4536** |
| 14 | `BLIND-010` | 316-459 | lower | 2.00 | 1.000 | 28 | 2.0700 | **0.4831** |
| 15 | `BLIND-036` | 40-96 | upper | 1.00 | 0.500 | 28 | 0.9429 | **0.5303** |
| 16 | `BLIND-036` | 40-96 | lower | 1.00 | 0.500 | 28 | 0.9429 | **0.5303** |
| 17 | `BLIND-011` | 0-96 | upper | 3.00 | 1.500 | 28 | 2.6286 | **0.5707** |
| 18 | `BLIND-020` | 0-82 | lower | 1.00 | 0.500 | 28 | 0.8737 | **0.5723** |
| 19 | `BLIND-037` | 24-96 | lower | 2.00 | 1.000 | 28 | 1.5160 | **0.6596** |
| 20 | `BLIND-021` | 174-214 | lower | 6.00 | 3.000 | 28 | 4.4089 | **0.6804** |
| 21 | `BLIND-042` | 215-288 | lower | 3.00 | 1.500 | 28 | 2.1239 | **0.7062** |
| 22 | `BLIND-016` | 180-270 | upper | 2.00 | 1.000 | 28 | 1.3549 | **0.7381** |
| 23 | `BLIND-016` | 180-270 | lower | 2.00 | 1.000 | 28 | 1.3549 | **0.7381** |
| 24 | `BLIND-004` | 0-239 | upper | 2.00 | 1.000 | 28 | 1.3082 | **0.7644** |
| 25 | `BLIND-009` | 0-288 | lower | 6.00 | 3.000 | 28 | 3.8401 | **0.7812** |
| 26 | `BLIND-022` | 0-260 | upper | 2.00 | 1.000 | 28 | 1.2581 | **0.7949** |
| 27 | `BLIND-017` | 275-480 | upper | 3.00 | 1.500 | 28 | 1.8201 | **0.8241** |
| 28 | `BLIND-017` | 275-480 | lower | 3.00 | 1.500 | 28 | 1.8201 | **0.8241** |
| 29 | `BLIND-034` | 230-480 | upper | 3.00 | 1.500 | 28 | 1.8082 | **0.8295** |
| 30 | `BLIND-034` | 230-480 | lower | 3.00 | 1.500 | 28 | 1.8082 | **0.8295** |
| 31 | `BLIND-016` | 0-80 | upper | 2.00 | 1.000 | 28 | 1.1865 | **0.8428** |
| 32 | `BLIND-045` | 0-140 | lower | 2.00 | 1.000 | 28 | 1.1818 | **0.8462** |
| 33 | `BLIND-042` | 215-288 | upper | 4.00 | 2.000 | 28 | 2.1239 | **0.9417** |
| 34 | `BLIND-011` | 0-96 | lower | 5.00 | 2.500 | 28 | 2.6286 | **0.9511** |
| 35 | `BLIND-010` | 316-459 | upper | 4.00 | 2.000 | 28 | 2.0700 | **0.9662** |
| 36 | `BLIND-037` | 24-96 | upper | 3.00 | 1.500 | 28 | 1.5160 | **0.9894** |
| 37 | `BLIND-004` | 0-239 | lower | 3.00 | 1.500 | 28 | 1.3082 | **1.1466** |
| 38 | `BLIND-015` | 0-250 | upper | 5.00 | 2.500 | 28 | 2.0589 | **1.2142** |
| 39 | `BLIND-021` | 224-288 | upper | 4.00 | 2.000 | 28 | 1.3850 | **1.4440** |
| 40 | `BLIND-021` | 224-288 | lower | 4.00 | 2.000 | 28 | 1.3850 | **1.4440** |
| 41 | `BLIND-010` | 108-294 | upper | 4.00 | 2.000 | 28 | 1.2854 | **1.5560** |
| 42 | `BLIND-010` | 108-294 | lower | 4.00 | 2.000 | 28 | 1.2854 | **1.5560** |
| 43 | `BLIND-022` | 0-260 | lower | 4.00 | 2.000 | 28 | 1.2581 | **1.5897** |
| 44 | `BLIND-016` | 0-80 | lower | 4.00 | 2.000 | 28 | 1.1865 | **1.6857** |
| 45 | `BLIND-045` | 0-140 | upper | 4.00 | 2.000 | 28 | 1.1818 | **1.6924** |
| 46 | `BLIND-015` | 0-250 | lower | 9.00 | 4.500 | 28 | 2.0589 | **2.1856** |
| 47 | `BLIND-019` | 0-480 | upper | 4.00 | 2.000 | 28 | 0.7642 | **2.6172** |
| 48 | `BLIND-018` | 142-290 | upper | 4.00 | 2.000 | 28 | 0.6861 | **2.9151** |
| 49 | `BLIND-018` | 142-290 | lower | 4.00 | 2.000 | 28 | 0.6861 | **2.9151** |
| 50 | `BLIND-019` | 0-480 | lower | 6.00 | 3.000 | 28 | 0.7642 | **3.9258** |

## Excluderi, toate

| fereastra | segment | motiv |
|---|---|---|
| `BLIND-001` | 72-120 | fara BANDA numerica pe ambele frontiere |
| `BLIND-001` | 133-190 | fara BANDA numerica pe ambele frontiere |
| `BLIND-001` | 216-240 | fara BANDA numerica pe ambele frontiere |
| `BLIND-001` | 240-266 | fara BANDA numerica pe ambele frontiere |
| `BLIND-003` | 70-98 | fara BANDA numerica pe ambele frontiere |
| `BLIND-003` | 163-224 | fara BANDA numerica pe ambele frontiere |
| `BLIND-004` | 384-432 | fara BANDA numerica pe ambele frontiere |
| `BLIND-007` | 49-145 | fara BANDA numerica pe ambele frontiere |
| `BLIND-007` | 210-292 | fara BANDA numerica pe ambele frontiere |
| `BLIND-007` | 306-368 | fara BANDA numerica pe ambele frontiere |
| `BLIND-008` | 0-144 | fara BANDA numerica pe ambele frontiere |
| `BLIND-008` | 180-232 | fara BANDA numerica pe ambele frontiere |
| `BLIND-008` | 272-340 | fara BANDA numerica pe ambele frontiere |
| `BLIND-008` | 430-480 | fara BANDA numerica pe ambele frontiere |
| `BLIND-009` | 110-200 | fara BANDA numerica pe ambele frontiere |
| `BLIND-009` | 270-288 | fara BANDA numerica pe ambele frontiere |
| `BLIND-012` | 0-52 | fara BANDA numerica pe ambele frontiere |
| `BLIND-012` | 88-96 | fara BANDA numerica pe ambele frontiere |
| `BLIND-013` | 0-36 | fara BANDA numerica pe ambele frontiere |
| `BLIND-013` | 49-68 | fara BANDA numerica pe ambele frontiere |
| `BLIND-013` | 82-96 | fara BANDA numerica pe ambele frontiere |
| `BLIND-014` | 0-80 | fara BANDA numerica pe ambele frontiere |
| `BLIND-014` | 96-190 | fara BANDA numerica pe ambele frontiere |
| `BLIND-014` | 205-241 | fara BANDA numerica pe ambele frontiere |
| `BLIND-015` | 356-430 | fara BANDA numerica pe ambele frontiere |
| `BLIND-015` | 454-480 | fara BANDA numerica pe ambele frontiere |
| `BLIND-016` | 281-288 | fara BANDA numerica pe ambele frontiere |
| `BLIND-017` | 110-190 | fara BANDA numerica pe ambele frontiere |
| `BLIND-017` | 205-260 | fara BANDA numerica pe ambele frontiere |
| `BLIND-018` | 305-365 | fara BANDA numerica pe ambele frontiere |
| `BLIND-018` | 415-480 | fara BANDA numerica pe ambele frontiere |
| `BLIND-019` | 48-180 | fara BANDA numerica pe ambele frontiere |
| `BLIND-019` | 468-480 | fara BANDA numerica pe ambele frontiere |
| `BLIND-020` | 60-82 | fara BANDA numerica pe ambele frontiere |
| `BLIND-021` | 0-48 | fara BANDA numerica pe ambele frontiere |
| `BLIND-022` | 155-190 | fara BANDA numerica pe ambele frontiere |
| `BLIND-023` | 0-16 | fara BANDA numerica pe ambele frontiere |
| `BLIND-023` | 20-48 | fara BANDA numerica pe ambele frontiere |
| `BLIND-023` | 64-84 | fara BANDA numerica pe ambele frontiere |
| `BLIND-024` | 24-36 | fara BANDA numerica pe ambele frontiere |
| `BLIND-024` | 55-72 | fara BANDA numerica pe ambele frontiere |
| `BLIND-024` | 76-96 | fara BANDA numerica pe ambele frontiere |
| `BLIND-025` | 34-56 | fara BANDA numerica pe ambele frontiere |
| `BLIND-025` | 78-96 | fara BANDA numerica pe ambele frontiere |
| `BLIND-026` | 61-80 | fara BANDA numerica pe ambele frontiere |
| `BLIND-027` | 0-24 | fara BANDA numerica pe ambele frontiere |
| `BLIND-027` | 125-178 | fara BANDA numerica pe ambele frontiere |
| `BLIND-027` | 210-250 | fara BANDA numerica pe ambele frontiere |
| `BLIND-028` | 132-168 | fara BANDA numerica pe ambele frontiere |
| `BLIND-028` | 280-288 | fara BANDA numerica pe ambele frontiere |
| `BLIND-029` | 0-48 | fara BANDA numerica pe ambele frontiere |
| `BLIND-029` | 150-225 | fara BANDA numerica pe ambele frontiere |
| `BLIND-029` | 225-320 | fara BANDA numerica pe ambele frontiere |
| `BLIND-029` | 320-400 | fara BANDA numerica pe ambele frontiere |
| `BLIND-030` | 165-288 | fara BANDA numerica pe ambele frontiere |
| `BLIND-031` | 60-95 | fara BANDA numerica pe ambele frontiere |
| `BLIND-031` | 205-280 | fara BANDA numerica pe ambele frontiere |
| `BLIND-031` | 320-370 | fara BANDA numerica pe ambele frontiere |
| `BLIND-031` | 400-470 | fara BANDA numerica pe ambele frontiere |
| `BLIND-032` | 0-55 | fara BANDA numerica pe ambele frontiere |
| `BLIND-032` | 100-150 | fara BANDA numerica pe ambele frontiere |
| `BLIND-032` | 190-240 | fara BANDA numerica pe ambele frontiere |
| `BLIND-032` | 258-280 | fara BANDA numerica pe ambele frontiere |
| `BLIND-033` | 18-36 | fara BANDA numerica pe ambele frontiere |
| `BLIND-033` | 68-96 | fara BANDA numerica pe ambele frontiere |
| `BLIND-034` | 360-410 | fara BANDA numerica pe ambele frontiere |
| `BLIND-034` | 410-480 | fara BANDA numerica pe ambele frontiere |
| `BLIND-035` | 0-80 | fara BANDA numerica pe ambele frontiere |
| `BLIND-035` | 170-240 | fara BANDA numerica pe ambele frontiere |
| `BLIND-035` | 265-340 | fara BANDA numerica pe ambele frontiere |
| `BLIND-035` | 430-480 | fara BANDA numerica pe ambele frontiere |
| `BLIND-037` | 24-50 | fara BANDA numerica pe ambele frontiere |
| `BLIND-037` | 70-96 | fara BANDA numerica pe ambele frontiere |
| `BLIND-038` | 320-400 | fara BANDA numerica pe ambele frontiere |
| `BLIND-038` | 400-480 | fara BANDA numerica pe ambele frontiere |
| `BLIND-039` | 0-40 | fara BANDA numerica pe ambele frontiere |
| `BLIND-039` | 68-120 | fara BANDA numerica pe ambele frontiere |
| `BLIND-039` | 215-280 | fara BANDA numerica pe ambele frontiere |
| `BLIND-040` | 60-150 | fara BANDA numerica pe ambele frontiere |
| `BLIND-040` | 172-230 | fara BANDA numerica pe ambele frontiere |
| `BLIND-040` | 230-330 | fara BANDA numerica pe ambele frontiere |
| `BLIND-040` | 450-480 | fara BANDA numerica pe ambele frontiere |
| `BLIND-041` | 0-38 | fara BANDA numerica pe ambele frontiere |
| `BLIND-041` | 72-96 | fara BANDA numerica pe ambele frontiere |
| `BLIND-042` | 0-70 | fara BANDA numerica pe ambele frontiere |
| `BLIND-043` | 92-96 | fara BANDA numerica pe ambele frontiere |
| `BLIND-044` | 0-40 | fara BANDA numerica pe ambele frontiere |
| `BLIND-044` | 62-120 | fara BANDA numerica pe ambele frontiere |
| `BLIND-045` | 140-180 | fara BANDA numerica pe ambele frontiere |
| `BLIND-045` | 240-280 | fara BANDA numerica pe ambele frontiere |
| `BLIND-046` | - | eticheta superseded de addendum, care NU contine benzi |
| `BLIND-047` | - | eticheta superseded de addendum, care NU contine benzi |
| `BLIND-048` | - | eticheta superseded de addendum, care NU contine benzi |
