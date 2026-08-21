# ALPHA_XAUUSD_MULTITF_M5_M15_H1_H4_DISCOVERY_REPORT

**Mandate:** `ALPHA-XAUUSD-MULTITF-M5-M15-H1-H4-DISCOVERY-001` · **Date:** 2026-08-21 · **Stat evidence:** commit `b8d0447`.
**Terminal status:** `XAUUSD_MULTITF_ALPHA_DISCOVERY_COMPLETE` · **`NEW_MULTITF_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW`** — 2 robust, CALIB-passing new candidates (`MT-H4-efficiency-L`, `MT-H4-dispaccept-L`).
**Firewall (re-verified):** gated M5 loader only (file sha `cbb6eebe…`); M15/H1/H4 by causal aggregation from gated M5; no `read_csv` on `data/market/`; `N4_M5_TRIGGER_USAGE_COUNT = 0`; `ALPHA_ACCESS_2025_PLUS = 0`; no shadow_driver. 56 IDs (≤80). No promotion; broker disabled; existing candidates frozen.

---

## 0. Headline — answers to §35
1. **New robust strategies:** **`MT-H4-efficiency-L`** (H4 path-efficiency LONG) and **`MT-H4-dispaccept-L`** (H4 displacement+acceptance LONG) — both **CALIB_PASS**, large-move (medTP 320 / 478 pips).
2. **Which TF produced each:** **H4** for both.
3. **M5 — edge, entry, both, or neither?** **Entry only** (for trend-continuation, per prior mandates). **M5-native is NOT an edge timeframe** — 0 of 14 M5-native mechanisms survived; all fail at economic targets.
4. **Does M15 contain Alpha we were missing?** **No** — 0 of 14 M15-native mechanisms survived. We were not skipping M15 Alpha.
5. **Is H1 still the most productive?** **No** — H1's DEV survivors all **failed CALIB**. H4 is more productive.
6. **Does H4 provide stronger large-move Alpha?** **Yes, decisively** — best tail robustness, largest targets, and the only CALIB-passers.
7–8. **Profile A / B:** none land cleanly inside either band; both new candidates are `ROBUST_ALPHA_BUT_PROFILE_MISMATCH` (~44–50% WR @ RR ~1.5).
9. **≥70–80 pip targets:** the H4 candidates median 320–478 pips — far exceed.
10. **Complementary:** both LONG large-move → orthogonal to `H4-bo-raw-S` (short); distinct TF from `HR-TU-pb-L`/`IR-DIR-L-mid`.
11. **Statistician review next:** `MT-H4-efficiency-L` (primary), `MT-H4-dispaccept-L`.

## 1. Evidence integrity
Gated M5 via `edge_research._common.load` (loader `flowA_common_v6…`, manifest v2.7.94, file sha `cbb6eebe…`). DEV bars: M5 121,949 / M15 40,649 / H1 10,168 / H4 2,652 (all causally aggregated from the single gated M5). CALIB reserved; accessed once per frozen survivor only. 0 `read_csv` on `data/market/`; N4 usage 0; 2025+ access 0.

## 2. Search design
Each of M5/M15/H1/H4 screened as a **primary edge timeframe**. 7 mechanism families (pullback, breakout, compression→expansion, momentum, path-efficiency, displacement+acceptance, HL/LH structure) × 2 directions × 4 TFs = 56 IDs. **Corrected architecture (§10):** structural SL on the **edge** timeframe (5-bar swing ± 0.15·ATR), economic RR target (per-TF RR sized to ~economic targets: M5 4.0 / M15 3.0 / H1 2.5 / H4 1.5), coarse edge-TF entry, `mstrat` production engine, cost tick 0.01 / STRESS 0.24. Economic-target filter (median TP ≥70 pips). DEV screen; CALIB after freeze.

## 3–6. Per-timeframe native results (the core finding)
| TF | SURVIVE | TAIL_FRAGILE | FAIL | SPARSE | read-out |
|---|---|---|---|---|---|
| **M5** | 0 | 0 | 14 | 0 | **No M5-native edge.** Every mechanism negative at economic RR; WR ≈0; tails collapse. M5 is an *entry* layer, not an edge. |
| **M15** | 0 | 1 | 13 | 0 | **No M15-native edge.** Best (dispaccept-L) is BASE +0.05 / STRESS +0.007, tail-fragile. |
| **H1** | 2 | 8 | 4 | 0 | Real edges but **all DEV survivors fail CALIB** (below). Many positive-but-tail-fragile. |
| **H4** | 4 | 1 | 7 | 2 | **Most productive** — 4 DEV survivors, best tails; **2 pass CALIB.** |
**M5-native (§3):** 14/14 FAIL — micro trend/breakout/compression/momentum all negative after STRESS at economic targets. **M15-native (§4):** 13 FAIL + 1 tail-fragile. **H1-native (§5):** `pullback-L`, `breakout-S` survive DEV; both **CALIB_FAIL**. **H4-native (§6):** `efficiency-L`, `pullback-L`, `dispaccept-L`, `momentum-L` survive DEV; **`efficiency-L` + `dispaccept-L` CALIB_PASS**.

## 7. Multi-timeframe combinations
Not needed for the winners: the two robust candidates are **H4-only** with coarse H4 entry. Per prior mandates, M5 entry adds value only to trend-continuation (`HR-TU-pb-L`), not to these H4 large-move edges (whose structural stops and targets are H4-native). No lower-TF entry layer was required; complexity penalized per §16.

## 8–12. Regime + direction findings
- **Direction (§4):** overwhelming **LONG** dominance. Only `MT-H1-breakout-S` (short) survived DEV, and it **failed CALIB (−0.341)**. Every H4 short failed. Consistent with the long-biased gold 2021–2024 DEV/CALIB window. **No robust SHORT edge found on any native timeframe** (existing `H4-bo-raw-S` short is on a different, earlier population and remains frozen).
- **TREND_UP (§8):** where the edge lives — H4 efficiency/pullback/dispaccept LONG are trend-continuation in up-trending gold.
- **TREND_DOWN (§9):** no robust survivor (shorts fail).
- **RANGE (§10):** covered by the prior branches (mean-reversion failed; `IR-DIR-L-mid` is the range specialist); no new range edge here.
- **TRANSITION / REGIME_INDEPENDENT (§11–12):** compression→expansion (a transition proxy) failed on M5/M15/H1; on H4 it was SPARSE (n=12–13). No robust transition edge.

## 13–15. Profile A / B / other (§7–9)
No candidate lands cleanly in **Profile A** (70–80% WR) or **Profile B** (1:3–4). Both new survivors are **`ROBUST_ALPHA_BUT_PROFILE_MISMATCH`**: `MT-H4-efficiency-L` WR 43.5% (DEV) / 50% (CALIB) @ RR 1.5; `MT-H4-dispaccept-L` WR 34% / 46% @ RR 1.5. Not lottery edges (tails robust, §19). S5 remains the Profile-B exemplar (unmodified).

## 16 & 25. Economic TP geometry — serious survivors
| candidate | median SL | median TP | P-nominal RR | %TP ≥70 / ≥80 |
|---|---|---|---|---|
| **MT-H4-efficiency-L** | 214 pips | **320 pips** ($32) | 1:1.5 | 0.98 / 0.98 |
| **MT-H4-dispaccept-L** | 319 pips | **478 pips** ($48) | 1:1.5 | 1.00 / 1.00 |
These are **large-move** strategies — median targets 320–478 pips, precisely the "meaningful Gold move" (§6) regime. 100% of `dispaccept` and 98% of `efficiency` setups target ≥80 pips.

## 17. Effective RR
Nominal RR 1:1.5. Coarse H4 entry (no timing slippage between arms; M5 entry not used). Effective realized RR is captured in the avg_R (STRESS): efficiency +0.380, dispaccept +0.197 — reflecting favorable time-exits on wide-target trend trades beyond the nominal 1.5R structure.

## 18. Costs
All figures NET of **STRESS round-trip 0.24**, min tick 0.01. The H4 candidates are cost-resilient — the fixed 0.24 is a tiny fraction of the 214–319-pip structural risk (~1.1–0.75%), unlike M5 (risk ~11–25 pips → cost 10–20% of risk), which is a structural reason M5-native fails and H4 survives.

## 19. Tail robustness (§26) — decisive quality filter
| candidate | best-1%-rem | best-5%-rem | **best-10%-removed** |
|---|---|---|---|
| **MT-H4-efficiency-L** | — | +0.323 | **+0.267** |
| **MT-H4-dispaccept-L** | — | +0.123 | **+0.049** |
`MT-H4-efficiency-L` survives removing the **top 10%** of trades at +0.267 — an exceptionally broad-based edge (not a few ranges escaping into trends). This is the strongest tail profile any candidate in the whole program has shown. All FAIL/TAIL_FRAGILE candidates had negative best-5%-removed.

## 20. Temporal robustness (§27)
| candidate | 2021 | 2022 | 2023 |
|---|---|---|---|
| MT-H4-efficiency-L | −0.249 | +0.308 | +0.556 |
| MT-H4-dispaccept-L | +0.060 | −0.130 | +0.358 |
Both are **regime-dependent trend-longs**: strong in up-trending years (2022–2023), weak/negative in the 2021 topping year (efficiency) or the 2022 selloff (dispaccept). Honest caveat — these are up-trend specialists, not all-weather. No periods deleted.

## 21. Calibration (§28) — run once, frozen
| candidate | CALIB n | CALIB WR | CALIB avg R | CALIB best-5%-rem | class |
|---|---|---|---|---|---|
| **MT-H4-efficiency-L** | 12 | 0.50 | **+0.357** | +0.253 | **CALIB_PASS** |
| **MT-H4-dispaccept-L** | 13 | 0.46 | **+0.223** | +0.117 | **CALIB_PASS** |
| MT-H4-momentum-L | 25 | 0.36 | +0.023 | −0.038 | CALIB_WEAK |
| MT-H4-pullback-L | 25 | 0.40 | −0.020 | −0.083 | CALIB_FAIL |
| MT-H1-pullback-L | 76 | 0.21 | −0.035 | −0.139 | CALIB_FAIL |
| MT-H1-breakout-S | 43 | 0.09 | −0.341 | −0.479 | CALIB_FAIL |
**Only the two H4 LONG candidates generalize.** (Small CALIB n=12–13 is the honest limit of H4 sampling — flagged for validation.)

## 22. TIMEFRAME RANKING (§31) — the mandate's central answer
**H4 > H1 ≫ M15 ≈ M5.**
| rank | TF | robust-Alpha density | tail robustness | cost resilience | economic TP | verdict |
|---|---|---|---|---|---|---|
| **1** | **H4** | 2 CALIB-pass / 14 | **best** (best-10%-rem +0.27) | best (cost ~1% of risk) | largest (320–478p) | **most productive** |
| 2 | H1 | 0 CALIB-pass (DEV edges die on CALIB) | moderate | good | 150–300p | productive but non-generalizing here |
| 3 | M15 | 0 | weak | poor | 60–150p | essentially barren |
| 4 | M5 | 0 | worst | worst (cost 10–20% of risk) | sub-economic | **not an edge TF (entry only)** |
**Which TF is most productive for XAUUSD Alpha? — H4**, decisively: it is the only timeframe producing CALIB-generalizing, tail-robust, large-move, cost-resilient edges. M5/M15 produce no robust native Alpha at economic targets.

## 23. MECHANISM RANKING (§32)
| mechanism | best TF | classification | reason |
|---|---|---|---|
| **path-efficiency (LONG)** | H4 | **STRONG_SURVIVOR** | +0.38 DEV / +0.36 CALIB, best-10%-rem +0.27 |
| **displacement+acceptance (LONG)** | H4 | **STRONG_SURVIVOR** | +0.20 DEV / +0.22 CALIB, large targets |
| momentum (LONG) | H4 | PROMISING | DEV+, CALIB_WEAK |
| pullback (LONG) | H1/H4 | WEAK | DEV+ but CALIB_FAIL |
| breakout | H1 (S) | WEAK | DEV+ but CALIB_FAIL |
| compression→expansion | — | FALSIFIED | fails M5/M15/H1; SPARSE on H4 |
| all SHORT variants | — | FALSIFIED | negative on all native TFs (long-biased population) |

## 24. Independence / overlap (§29)
- `MT-H4-efficiency-L` vs `MT-H4-dispaccept-L`: Jaccard 0.104 (day-level) — largely distinct even same-TF.
- vs `MT-H1-pullback-L`: Jaccard 0.33 (moderate; both trend-long, different TF).
- vs **`H4-bo-raw-S`** (SHORT): directionally orthogonal → **INDEPENDENT**.
- vs `HR-TU-pb-L` (H1 trend, M5-entry) / `IR-DIR-L-mid` (H1 range): different edge TF and much larger targets (H4 320–478p vs H1 90–167p) → **complementary** (H4 large-move specialist vs H1 intraday specialists).

## 25. Graveyard (§33)
| idea | TF | failure | code |
|---|---|---|---|
| all M5-native (7 mech × 2 dir) | M5 | negative STRESS, tails collapse, cost ~15% of risk | NO_EDGE + COST |
| all M15-native | M15 | negative/tail-fragile | NO_EDGE |
| H1 pullback-L, breakout-S | H1 | DEV+ but **CALIB_FAIL** | CALIB |
| H4 pullback-L | H4 | DEV+ but CALIB_FAIL (−0.02) | CALIB |
| H4 momentum-L | H4 | CALIB_WEAK, DEV tail thin | TAIL/CALIB |
| all SHORT (every TF) | all | negative (long-biased 2021–2024) | NO_EDGE |
| compression→expansion | all | fails/sparse everywhere | NO_EDGE |
Recorded in `multitf_records.json`. New `MT-` IDs; existing candidates untouched.

## 26. Candidate portfolio (§30)
Updated program portfolio (research candidates, none promoted):
- **`MT-H4-efficiency-L`** — H4 large-move TREND_UP LONG specialist (NEW, strongest tail profile in the program).
- **`MT-H4-dispaccept-L`** — H4 large-move LONG (NEW, largest targets).
- `HR-TU-pb-L` — H1 trend-pullback + M5 entry (near-Profile-A).
- `IR-DIR-L-mid` — H1 intra-range directional LONG (RANGE specialist).
- `H4-bo-raw-S` / `S5` / `S20` — frozen references (S5 = Profile-B exemplar; H4-bo-raw-S = SHORT).
Together these span TREND_UP (H4 large-move + H1), RANGE (intra-range), and SHORT (H4-bo-raw-S) — **complementary specialists**, per §30.

## 27. Recommendation to CEO
1. **Forward `MT-H4-efficiency-L` (primary) and `MT-H4-dispaccept-L` to Statistician/Red Team** as robust, CALIB-passing, tail-robust, **large-move H4 LONG** candidates. Flags: `ROBUST_ALPHA_BUT_PROFILE_MISMATCH` (~44–50% WR @ 1:1.5); **regime-dependent (up-trend specialists**, weak in 2021 topping); small CALIB n (12–13). They **complement** the portfolio (H4 large-move LONG vs the H1 intraday and H4-short references).
2. **Timeframe verdict (§31):** **H4 is the most productive timeframe for XAUUSD Alpha**; H1 second (but its edges did not generalize here); **M5 and M15 produce no robust native Alpha** at economic targets — **M5's role is entry-timing for trend-continuation, not an edge**. This settles the "H1 must be primary" assumption in the negative: **H4 outranks H1** for robust large-move edges.
3. **Budget:** stopped at 56 of 80 — M5/M15 consistently failed fast-falsification (redirected away per §22), H1/H4 fully covered, and the H4>H1≫M15/M5 pattern + CALIB gate made further cosmetic variants uninformative (§21 early-stop).
4. **No promotion; broker disabled; highest status = research candidate.** `S5`/`S20`/`S9`/`HR-TU-pb-L`/`IR-DIR-L-mid`/`H4-bo-raw-S` unaltered.

**Terminal status:** `XAUUSD_MULTITF_ALPHA_DISCOVERY_COMPLETE` · `NEW_MULTITF_ALPHA_CANDIDATES_READY_FOR_CEO_REVIEW` (2: `MT-H4-efficiency-L`, `MT-H4-dispaccept-L`). **STOP.**
