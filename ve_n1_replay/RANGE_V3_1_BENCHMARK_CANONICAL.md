# RANGE V3.1 (0.4.1) — Benchmark canonic (`d_min_bars=96`, 355.696 bare)

**Mandat §7**: rulare COMPLETĂ, 355.696 bare, `d_min_bars=96`, confirmă sub 4 ore, raportează timp, bare/sec,
RSS, indice de liniaritate.

## 0. Notă de transparență — `d_min_bars=96` vs. `d_min_bars=24` folosit de benchmark-ul PROPRIU al lui 0.4.0

Benchmark-ul canonic PROPRIU al lui 0.4.0 (`RANGE_V3_BENCHMARK.md`) a rulat la `d_min_bars=24` (K=4,N=8,
w_atr=0.5), nu 96. Mandatul 0.4.1 cere EXPLICIT `d_min_bars=96` pt. acest benchmark — folosit exact așa, fără
ajustare. Raportat transparent: **96 e o configurație STRICT mai grea pt. varianta O(`d_min_bars`) veche
(4× mai mare decât 24)** — deci un benchmark canonic mai conservator pt. verificarea remedierii, nu unul
slăbit. `n_guards`/`events_total` diferă firesc față de raportul 0.4.0 (fixture IDENTIC, dar `d_min_bars`
diferit schimbă dinamica geometriei/segmentării) — nu semnalează nicio discrepanță de implementare.

## 1. Date și configurație

`synth_bars()` din `tools/benchmark_range_v3.py` (0.4.0, NEATINS) — REFOLOSITĂ byte-identic. Configurație
`UNRATIFICATĂ/CONSTRUCTION_ONLY`: `K=4, N=8, w_atr=0.5, d_min_bars=96, segment_history_limit=64`.

## 2. Rezultat — rulare COMPLETĂ, 355.696 bare

```json
{"bars": 355696, "d_min_bars": 96, "wall_s": 1818.323, "cpu_s": 1800.625, "bars_per_sec": 195.6,
 "us_per_bar": 5112.01, "run_hash": "b01b6f106e00", "n_guards": 155609, "events_total": 359402,
 "confirmed_segments": 64, "snapshot_s": 0.027156, "restore_s": 0.014077, "peak_ws_mb": 700.6}
```

- **Timp: 30 min 18 s (1818,3 s) — SUB ținta de 4 ore**, cu marjă de **~7,9×**.
- **`confirmed_segments: 64`** — plafonat exact la `segment_history_limit=64` (istoricul rămâne mărginit
  prin construcție, neschimbat față de 0.4.0).
- `snapshot_s`/`restore_s` — 27,2ms / 14,1ms peste 355.696 bare — mărginite de dimensiunea STĂRII curente
  (segment activ + istoric plafonat + fereastra N1 de 460 + statisticile suficiente ale pantei, O(1) fixe),
  NU de `n`.
- `peak_ws_mb: 700,6` — comparabil cu 0.4.0 (691,4MB la `d_min_bars=24`); diferența mică vine din coada
  `closes` mai mare (96 vs 24 elemente/segment activ), nu dintr-o scurgere sau creștere nemărginită.

## 3. Scalare — liniară, NU pătratică

```json
{"bars": 2000,  "wall_s": 9.203,   "bars_per_sec": 217.3, "us_per_bar": 4601.66}
{"bars": 20000, "wall_s": 103.368, "bars_per_sec": 193.5, "us_per_bar": 5168.42}
{"bars": 355696,"wall_s": 1818.323,"bars_per_sec": 195.6, "us_per_bar": 5112.01}
```

`linear_index` (2.000→355.696, 177,8× mai multe bare) = **1,111** — identic (până la a treia zecimală) cu
`linear_index`-ul propriu al lui 0.4.0 la scara scurtă. Rata la 20.000 bare (193,5/s) și rata la 355.696 bare
COMPLETE (195,6/s) sunt practic IDENTICE (ușor mai rapidă la scară completă) — nicio degradare la scară mare,
confirmare directă a scalării liniare.

## 4. Comparație directă cu 0.4.0 — la un `d_min_bars` de 4× MAI MARE, timp aproape IDENTIC

| | 0.4.0 (`RANGE_V3_BENCHMARK.md`) | 0.4.1 (acest raport) |
|---|---|---|
| `d_min_bars` | 24 | **96 (4× mai mare)** |
| timp total (355.696 bare) | 30min 41s (1840,8s) | **30min 18s (1818,3s)** |
| bare/sec | 193,2 | 195,6 |
| µs/bară | 5175,24 | 5112,01 |
| `linear_index` | 1,111 | 1,111 |
| `peak_ws_mb` | 691,4 | 700,6 |

**0.4.1 la `d_min_bars=96` rulează la fel de rapid (marginal MAI rapid, în limita variației normale de
sarcină a mașinii) ca 0.4.0 la `d_min_bars=24`** — o creștere de 4× a `d_min_bars` NU produce NICIO creștere
de timp măsurabilă. Aceasta e exact semnătura O(1)/bară pt. calculul pantei (fix-ul §12): dacă defectul
O(`d_min_bars`) ar fi fost încă prezent, 96 vs. 24 ar fi trebuit să coste vizibil mai mult (chiar dacă panta
nu domină costul total la valori mici de `d_min_bars`, o creștere de 4× tot ar fi lăsat urmă măsurabilă).

## 5. Concluzie

**Scalare liniară confirmată empiric de la 2.000 la 355.696 bare** (`linear_index≈1,111`), **sub ținta de 4
ore cu marjă de ~7,9×**, la o configurație STRICT mai grea (`d_min_bars=96`, cerută explicit de mandat) decât
propriul benchmark canonic al lui 0.4.0 (`d_min_bars=24`) — și totuși statistic INDISTINCTIBIL ca timp total.
Vezi și `RANGE_V3_1_BENCHMARK_ADVERSARIAL.md` pt. demonstrația la scara adversarială (`d_min_bars=200000`,
citată de Red Team) — împreună, cele două benchmark-uri demonstrează că defectul §12 (RT-RANGE-0004) e ÎNCHIS
pe TOATĂ plaja de `d_min_bars`, nu doar la un singur punct.
