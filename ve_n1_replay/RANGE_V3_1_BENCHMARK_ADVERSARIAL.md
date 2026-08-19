# RANGE V3.1 (0.4.1) — Benchmark adversarial (`d_min_bars=200000`)

**Mandat §7**: benchmark adversarial la `d_min_bars=200000` (fără plafon introdus — vezi §3), care trebuie
să demonstreze că defectul de ~9h e ÎNCHIS. Nu doar un microbenchmark — trebuie o rulare suficientă ca să
demonstreze stabilitatea costului/bară DUPĂ umplerea ferestrei.

## 1. Configurație și metodologie

Motor: `RangeSemanticEngineV31` (0.4.1) = `N1IncrementalReplayEngine` (0.1.1, NEATINS) +
`RangeSemanticProducerV31` (0.4.1). Configurație: `K=4, N=8, w_atr=0.5, d_min_bars=200000,
segment_history_limit=64` — identică (mai puțin `d_min_bars`) cu benchmark-ul canonic al lui 0.4.0
(`RANGE_V3_BENCHMARK.md`), pt. comparabilitate directă. Date: `synth_bars()` din `tools/benchmark_range_v3.py`
(0.4.0, NEATINS) — REFOLOSITĂ byte-identic (import direct), NU regenerată.

**250.000 bare total = 200.000 pt. umplerea COMPLETĂ a ferestrei `closes` + 50.000 coadă POST-umplere**,
măsurate SEPARAT, ca să demonstreze stabilitatea costului/bară (mandat §7), nu doar timpul total.

## 2. Rezultat

```json
{"bars": 250000, "d_min_bars": 200000, "fill_at": 200000,
 "fill_phase_wall_s": 1012.783, "fill_phase_us_per_bar": 5063.915,
 "post_fill_wall_s": 260.036, "post_fill_us_per_bar": 5200.712,
 "total_wall_s": 1272.819, "peak_ws_mb": 119.0}
```

- **Timp total: 21 min 13 s (1272,8 s)** — SUB ținta de 4 ore, cu marjă de **~11,3×**.
- **Stabilitate cost/bară confirmată direct**: faza de umplere (bara 0→200.000, fereastra CREȘTE de la 0 la
  200.000 elemente) costă **5063,9 µs/bară**; coada POST-umplere (bara 200.000→250.000, fereastra e deja
  PLINĂ, fiecare bară evictă+adaugă) costă **5200,7 µs/bară** — diferență de doar **~2,7%**, în limitele
  variației naturale de sarcină a mașinii, NU un trend crescător. Dacă defectul O(`d_min_bars`) ar fi fost
  încă prezent, faza de umplere ar fi arătat un cost CRESCĂTOR pe măsură ce fereastra crește, iar coada
  post-umplere ar fi rămas la un nivel mult mai ridicat, constant la costul "fereastră plină" — nu s-a
  întâmplat: costul e practic IDENTIC în ambele faze, exact semnătura O(1)/bară.
- **`peak_ws_mb: 119,0`** — memorie rezonabilă; `deque(maxlen=200000)` de floats ≈ 1,6MB pt. coada singură,
  restul e overhead normal N1/Python. Memoria a fost ÎNTOTDEAUNA mărginită (nu era ținta remedierii §12 —
  problema era STRICT costul CPU per bară, nu memoria).

## 3. Comparație cu defectul citat de Red Team (RT-RANGE-0004, ledger E79)

| sursă | d_min_bars | µs/bară | metodă |
|---|---|---|---|
| Red Team, 0.4.0 (măsurat direct) | 200 | 90,9 | direct |
| Red Team, 0.4.0 (măsurat direct) | 4.000 | 1.829 | direct |
| Red Team, 0.4.0 (extrapolat) | 200.000 | ~90.000 | extrapolare liniară |
| **VE, 0.4.1 (acest benchmark, măsurat direct)** | **200.000** | **~5.100** | **direct, motor complet** |

Extrapolarea Red Team pt. 0.4.0 la scară completă (355.696 bare, ~90ms/bară) da ~8,9h — peste garanția de 4h.
**0.4.1, măsurat DIRECT (nu extrapolat) la exact aceeași scară adversarială, costă ~5.100µs/bară — un
factor de ordinul a 17-18× sub extrapolarea 0.4.0**, și rămâne SUB ținta de 4h cu marjă largă. Notă de
transparență: cifra 0.4.0 de mai sus e CITATĂ din raportul Red Team (extrapolare, nu re-măsurată aici — o
re-rulare de ~9h a defectului 0.4.0 nu a fost repetată, fiindcă rezultatul e deja documentat independent și
scopul acestui mandat e remedierea, nu redemonstrarea defectului).

**La nivel IZOLAT** (doar `slope()`/`push_close()`, fără N1/producător — vezi `slope_isolated_bench.py`,
verificare separată): 33.378,2µs/operație (0.4.0, `_Segment`) vs 1,0µs/operație (0.4.1, `_SegmentV31`) la
`d_min_bars=200000` — **~33.330× speedup măsurat DIRECT** (ambele versiuni, aceeași mașină, aceeași rulare).
Diferența dintre acest raport (33.330×) și raportul la nivel de motor complet (~17-18×) e AȘTEPTATĂ: motorul
complet include cost N1/detecție-swing/touch-tracking care NU beneficiază de fix-ul pantei — panta nu mai e
factorul dominant la `d_min_bars` mare, deci restul costului (neschimbat) domină raportul la scară completă.

## 4. Extrapolare la scara canonică (355.696 bare) — chiar la `d_min_bars` adversarial

355.696 bare × ~5.100µs/bară ≈ **1.814s ≈ 30,2 minute** — adică 0.4.1, rulat la CEL MAI MARE `d_min_bars`
citat de Red Team (200.000), pe LUNGIMEA COMPLETĂ a benchmark-ului canonic, ar costa aproximativ CÂT COSTA
benchmark-ul canonic al lui 0.4.0 la propriul `d_min_bars=24` (30m41s, `RANGE_V3_BENCHMARK.md`) — o creștere
de 8.333× a lui `d_min_bars` (24→200.000) nu mai produce o creștere proporțională de timp. Aceasta e exact
demonstrația cerută de mandat: defectul O(`d_min_bars`) e ÎNCHIS.

## 5. Concluzie

**Defectul §12 (RT-RANGE-0004) e ÎNCHIS, demonstrat prin măsurătoare directă, nu doar teoretic.** Rularea
completă la `d_min_bars=200000` (250.000 bare, umplere completă + coadă de 50.000) rămâne sub 4 ore cu marjă
de ~11,3×, iar costul/bară e STABIL (variație ~2,7%) înainte și după umplerea ferestrei — semnătura directă a
unui cost O(1)/bară, nu O(`d_min_bars`). Niciun plafon arbitrar nu a fost necesar (Varianta A, conform
mandatului).
