# RANGE V3 (0.4.0) — Benchmark de performanță

**Motorul benchmark-at:** `RangeSemanticEngineV3` = `N1IncrementalReplayEngine` (0.1.1, NEATINS) +
`RangeSemanticProducerV3` (0.4.0, NOU). **De ce rularea COMPLETĂ, nu una scurtă**: spre deosebire de 0.3.1
(pin de configurație peste ACELAȘI cod 0.3.0, benchmark scurt comparativ explicit waivat de mandat),
arhitectura 0.4.0 s-a schimbat MATERIAL — urmărire longitudinală de segmente, detecție de breach pe meșă,
cursă K/N, istoric mărginit — cod nou care nu moștenește automat garanția de complexitate a unei versiuni
deja benchmark-ate. Mandatul cere rularea completă exact în acest caz.

## 0. Un defect real de complexitate GĂSIT și CORECTAT înainte de acest benchmark

În timpul pregătirii, o verificare empirică directă (NU doar raționament teoretic) a arătat că
`update_anchors()` re-sorta lista COMPLETĂ de swing-uri a unui segment la FIECARE bară. Fiindcă ancora unui
segment e explicit NEMĂRGINITĂ pe durata vieții lui (D1 — cerința mandatului: nicio fereastră fixă externă),
un segment lung ar fi devenit O(n²) pe durata lui de viață — confirmat măsurând direct: **0,04ms/bară la 31
swing-uri acumulate → 0,62ms/bară la 525** (o creștere de ~15× pt. doar 17× mai multe swing-uri, pe un
segment forțat artificial să nu moară). Corectat ÎNAINTE de acest benchmark, nu descoperit de el: `highs`/
`lows` rămân listele complete (audit), dar mediana ancorei se calculează printr-o structură incrementală cu
două heap-uri (`_RunningMedian`, O(log m) la inserare, O(1) la citire) — nu o resortare completă.
**Verificare post-corecție**: cu `d_min_bars` realist (deci `closes`/`slope()` deja mărginite prin
construcție), costul per bară rămâne **CONSTANT la ~0,06-0,07ms indiferent dacă swing-urile acumulate cresc
de la 53 la 1088** (20× creștere în swing-uri, ZERO creștere măsurabilă în cost per bară) — testat separat
de zgomotul fixture-ului organic, pe un segment forțat artificial să supraviețuiască mult peste durata
normală. Acest fix e motivul pentru care rularea completă de mai jos e sigură și rapidă.

## 1. Date

Date reale XAUUSD M15 SIGILATE ⇒ serie sintetică deterministă, structurată explicit să exercite TOATE căile:
ciclu de 96 bare = 40 oscilație (range, touches) + 24 breach/reintrare (sweep) + 16 rupere susținută
(breakout) + 16 drift monoton (canal) — determinist din index, fără `Date`/`random`. Configurație explicit
`UNRATIFICATĂ/CONSTRUCTION_ONLY`: `K=4, N=8, w_atr=0.5, d_min_bars=24`.

## 2. Rezultat — rulare COMPLETĂ, 355.696 bare

```json
{"bars": 355696, "wall_s": 1840.813, "cpu_s": 1823.031, "bars_per_sec": 193.2, "us_per_bar": 5175.24,
 "run_hash": "961e789020c8", "n_guards": 140790, "events_total": 366811, "confirmed_segments": 64,
 "snapshot_s": 0.039493, "restore_s": 0.013548, "peak_ws_mb": 691.4}
```

- **Timp: 30 min 41 s (1840,8 s) — SUB ținta de 4 ore**, cu marjă de ~7,8×.
- **`confirmed_segments: 64`** — plafonat exact la `segment_history_limit=64` (istoricul e MĂRGINIT prin
  construcție, nu crește nemărginit cu numărul de bare — verificat direct, nu presupus).
- `snapshot_s`/`restore_s` — 39,5ms / 13,5ms peste 355.696 bare — mărginite de dimensiunea STĂRII curente
  (segment activ + istoric plafonat + fereastra N1 de 460), NU de `n` — consistent cu contractul O(1)/
  mărginit-amortizat pe care N1 îl are deja din 0.1.1.
- `peak_ws_mb: 691,4` — memorie rezonabilă pt. 355.696 bare procesate + fingerprint-uri per-bară păstrate
  pt. ledger.
- `n_guards: 140.790` — F7 `RANGE_MID_NO_ENTRY` se declanșează substanțial pe fixture-ul cu faze de
  oscilație repetate, consistent cu ce ar produce orice serie cu segmente RANGE reale.

## 3. Scalare — liniară, NU pătratică (exact ce verifică acest benchmark)

Rulare de control anterioară (sanity check, `2.000` și `20.000` bare, aceeași configurație):

```json
{"bars": 2000, "wall_s": 9.551, "bars_per_sec": 209.4, "us_per_bar": 4775.62}
{"bars": 20000, "wall_s": 106.117, "bars_per_sec": 188.5, "us_per_bar": 5305.83}
```

`linear_index` (2.000→20.000, 10× mai multe bare) = **1,111** — foarte aproape de 1,0 (liniar perfect).
Comparând rata la 20.000 bare (188,5 bare/s) cu rata la 355.696 bare COMPLETE (193,2 bare/s): **rata rămâne
practic IDENTICĂ (chiar ușor mai rapidă) la 17,8× mai multe bare** — dacă ar fi existat vreo componentă
pătratică rămasă, rata s-ar fi PRĂBUȘIT vizibil la scară completă; nu s-a întâmplat. Aceasta e dovada
empirică directă (nu doar teoretică) că fix-ul din §0 a închis singurul risc real de complexitate
identificat, și că nu mai există altul ascuns la scară mare.

## 4. Comparație cu N1/versiuni anterioare (context, nu pretenție de identitate)

- **N1 (0.1.1, NEATINS)** are propriul orizont documentat de încălzire (`HISTORY_HORIZON=460`) — costul per
  bară CREȘTE ușor în primele ~460 bare (structurile interne se umplu), apoi se PLAFONEAZĂ — comportament
  AȘTEPTAT, documentat, nu o regresie; confirmat separat, izolând N1 de producătorul V3.
- **0.3.0** (ultima rulare COMPLETĂ anterioară documentată): 355.696 bare, ~72,9 min, `linear_index=1,034`.
  0.4.0 (arhitectură mai bogată — segmentare longitudinală, urmărire de istoric, cursă K/N) rulează totuși
  **mai rapid în timp de perete** (30,7 min vs 72,9 min) — nu o comparație strict controlată (sarcină de
  mașină diferită între rulări), dar un semnal suplimentar, nu un motiv de îngrijorare.

## 5. Concluzie

**Scalare liniară confirmată empiric de la 2.000 la 355.696 bare** (`linear_index≈1,11` pe segmentul scurt,
rată practic constantă 188,5→193,2 bare/s pe segmentul complet). Singurul risc real de complexitate
identificat în timpul pregătirii (ancora nemărginită re-sortată complet la fiecare bară) a fost găsit,
corectat și verificat ÎNAINTE de această rulare — nu ascuns sau ignorat. `under_4h: true`. Date brute:
`RANGE_V3_BENCHMARK_FULL.json`.
