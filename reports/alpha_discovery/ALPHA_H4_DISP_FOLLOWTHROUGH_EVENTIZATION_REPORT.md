# ALPHA_H4_DISP_FOLLOWTHROUGH_EVENTIZATION_REPORT

**Mandate:** `ALPHA-H4-DISP-FOLLOWTHROUGH-EVENTIZATION-001` (corrective) · **Date:** 2026-08-21 · **Statistician ref:** `STAT_MT_H4_DISPACCEPT_L_INDEPENDENT_VALIDATION_PROTOCOL.md`, commit `c028eb2`.
**Terminal status:** `H4_DISP_FOLLOW_EVENT_POLICY_DEV_PASS` · **`FOLLOWTHROUGH_POLICY_CANDIDATE_READY_FOR_CEO_REVIEW`** — one causal, deterministic event policy (`H4-DISP-FOLLOW-L-COOLDOWN6`) survives all DEVELOPMENT gates. **CALIB NOT run** (returning to CEO first, per §19).
**DEV-only. Signal frozen (no threshold change). No d+1 (lookahead) entry. No V1/protected/2025+. No CALIB for selection.**

---

## 0. Headline
- **Accepted the Statistician's corrections:** (a) `OPEN[d+1]` entry is **non-causal/lookahead** — permanently prohibited; earliest causal entry is `OPEN[d+2]`. (b) The mechanism is **displacement + follow-through (second close)**, not "acceptance" (no structural level).
- **Confirmed the core problem — SIGNAL EDGE ≠ EXECUTABLE POLICY EDGE:** the raw signal is broad and healthy (76 signals, median +0.327, top-4 profit share ≈ 31.5%, positive all years), but the **frozen serialization policy fails Gate I** (top-10% profit concentration **77.5% > 60%**, median −0.070, 2022 negative, CI includes zero).
- **Eventization result:** the "natural" causal policies (first-signal / new-displacement / episode / cluster) all inherit the concentration failure (top-10% 73–101%). **Only a post-exit cooldown policy converts the signal into a broad, executable edge.**
- **Surviving policy `H4-DISP-FOLLOW-L-COOLDOWN6`** (one-at-a-time + 6-H4-bar post-exit cooldown): STRESS +0.264, **median +0.413**, best-10%-removed +0.135, **top-10% concentration 53.2% (PASS)**, incremental +0.249 over PROJECT TREND_UP. **K-robust** across 6–18 bars (monotone-improving). Caveat: n=34, 2021 marginally negative (turns positive at K≥12).

## 1. Frozen signal identity (§1, §4)
Unchanged from `MT-H4-dispaccept-L`. **Displacement** at bar d: `close[d]−open[d] > 1.0·ATR14[d]` (up). **Follow-through** at d+1: `close[d+1] > close[d]`. **Stop** (known at close d+1): `min(low[d−3…d+1]) − 0.15·ATR[d+1]`. **Entry**: `OPEN[d+2]`; `risk = |OPEN[d+2] − stop|` (floor `max(5·tick, 0.10·ATR)`); **target** `OPEN[d+2] + 1.5·risk`. Walk d+2…d+49, **stop-before-target** each bar. Cost tick 0.01 / STRESS 0.24. H4 aggregated from gated M5. **No parameter changed.** The **only** research variable is signal→event conversion (§4).

## 2. Causal chronology (§3) — lookahead corrected
| time | information | action |
|---|---|---|
| close d | OHLC[d], ATR[d] | evaluate displacement |
| close d+1 | OHLC[d+1] | evaluate follow-through; compute stop (lows ≤ d+1) |
| **open d+2** | open price | **ENTRY** (earliest causal) |
`OPEN[d+1]` entry (my prior §7 "acceptance cost" alternative) required knowing close[d+1] before entering at open[d+1] → **lookahead, prohibited**, not reported as executable. The frozen `OPEN[d+2]` is the causal floor.

## 3. Raw opportunity population (§6, §12)
Frozen raw signals built independently of trading: **N=76**, causal per-signal (no serialization): median R **+0.327**, avg R **+0.262** (STRESS), top-4 profit share **≈31.5%** (net convention; reproduces Statistician), positive in all three years (§10). This is the **scientific reference / ceiling** — but it is NOT executable (signals overlap in trade-time; one-at-a-time holding of ~26 bars precludes trading all 76).

## 4. Signal clustering (§7) — the overlap is holds, not clusters
Inter-signal gap (H4 bars): **P25 8 / P50 23 / P75 48**; only 11% of gaps ≤2, 19% ≤6. Clustering (gap>2): **68 clusters, 90% size-1** (max 3). **The 76 signals are predominantly isolated, not repeated observations of one episode.** Therefore the executability problem is **not** signal clustering — it is the **long holding period** (median 26 H4 bars) causing the one-trade-at-a-time constraint to skip signals that fall inside an open trade. This reframes eventization from "de-duplicate clusters" to "space trades so the executed subset stays broad."

## 5. Event definitions + policy candidates (§8, §10) — ≤5 IDs
All policies: causal, deterministic, event identity known at event time (§9 — no outcome-dependent selection), one-at-a-time execution.
| policy (new ID) | definition |
|---|---|
| REF_FIRST (= `MT-H4-dispaccept-L`, historical) | greedy: take next signal when flat (the frozen serialization) |
| `H4-DISP-FOLLOW-L-NEWDISP` | only signals whose displacement bar is a *new* displacement (prior bar not itself a >1·ATR up body) |
| `H4-DISP-FOLLOW-L-EPISODE` | first signal of each gap≤2 displacement episode |
| `H4-DISP-FOLLOW-L-CLUSTER6` | first signal of each gap>6 cluster |
| **`H4-DISP-FOLLOW-L-COOLDOWN6`** | greedy + **6-H4-bar (≈1 trading day) post-exit cooldown**, K pre-declared (structural: 1 day) |

## 6. Regime baseline (§15) + incremental follow-through value (§16)
**PROJECT TREND_UP = `ema20>ema50 AND effic>0.30`** (the project's stricter regime; reproduced **+0.0144**, n=503 — *not* the weaker ema-only +0.106). The follow-through signal's incremental value over this correct baseline is large and preserved by the surviving policy (COOLDOWN6 incremental **+0.249**). The follow-through distinction (accepted d+2 +0.259 vs rejected −0.073) is preserved by construction — every policy trades only follow-through-confirmed displacements.

## 7. DEV economics + tail concentration (§13, §17) — the gate battery
| policy | N | WR | STRESS avg | median R | PF | best-5%-rem | best-10%-rem | **top-10% share** | incr vs PROJECT | Gate verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| REF_FIRST (frozen) | 41 | 0.341 | +0.197 | −0.070 | 1.48 | +0.123 | +0.049 | **77.5%** | +0.183 | **FAIL (Gate I)** |
| NEWDISP | 42 | 0.357 | +0.203 | −0.040 | 1.50 | +0.131 | +0.060 | 73.4% | +0.189 | FAIL (Gate I) |
| EPISODE | 42 | 0.357 | +0.203 | −0.040 | 1.50 | +0.131 | +0.060 | 73.4% | +0.189 | FAIL (Gate I) |
| CLUSTER6 | 40 | 0.325 | +0.155 | −0.078 | 1.38 | +0.077 | −0.002 | 100.9% | +0.141 | FAIL (Gate I, b10) |
| **COOLDOWN6** | **34** | **0.382** | **+0.264** | **+0.413** | **1.66** | **+0.218** | **+0.135** | **53.2%** | **+0.249** | **ALL PASS** |
**Gate I (top-10% profit concentration ≤ 60%) is the discriminator.** The frozen serialization and its close cousins (NEWDISP/EPISODE) are all over-concentrated (73–78%) — their apparent expectancy rides on a handful of trades, exactly the Statistician's finding. **Only the cooldown policy spreads the executed edge broadly** (53.2%), and it simultaneously flips the median positive (+0.413 vs −0.070) and improves every other metric.

## 8. Temporal robustness (§14)
| policy | 2021 | 2022 | 2023 |
|---|---|---|---|
| raw signal (ceiling) | +0.423 (n15) | +0.017 (n13) | +0.278 (n48) |
| REF_FIRST (frozen) | +0.06 (n9) | **−0.13** (n8) | +0.358 (n24) |
| **COOLDOWN6** | **−0.12** (n8) | +0.162 (n6) | +0.448 (n20) |
**Honest failure reported:** no one-at-a-time policy fully preserves the raw signal's all-years-positive breadth (the holding constraint drops signals unevenly). COOLDOWN6 *fixes* 2022 (−0.13→+0.16) but 2021 is marginally negative (−0.12, n=8). **At larger cooldown (K≥12) 2021 turns positive** (§9) — the negativity is a small-sample edge effect, not a structural break.

## 9. Path robustness (§18) — K-neighborhood (transparent; no best-K selection)
The cooldown policy is deterministic (single path — no arbitration, the very fragility the frozen serialization had). Robustness to the pre-declared K was checked across a structural neighborhood (½–3 trading days), **reporting all, selecting none by outcome:**
| K (bars) | top-10% share | median R | incr | 2021 | verdict |
|---|---|---|---|---|---|
| 3 | 61.6% | +0.124 | +0.201 | −0.12 | FAIL (marginal) |
| **6 (declared)** | **53.2%** | +0.413 | +0.249 | −0.12 | **PASS** |
| 9 | 47.9% | +0.506 | +0.288 | −0.12 | PASS |
| 12 | 43.5% | +0.509 | +0.329 | +0.008 | PASS |
| 18 | 45.5% | +0.506 | +0.324 | +0.008 | PASS |
**Monotone improvement with spacing** (concentration ↓, median ↑, incremental ↑). The pre-declared K=6 is the **minimum** passing value (a conservative choice, not the optimum); the entire 6–18 region passes. **This is a robust structural effect, not a single-parameter fluke** — causally, spacing avoids re-entering the spent aftermath of a resolved move.

## 10. Economic geometry (§17) — `H4-DISP-FOLLOW-L-COOLDOWN6`
N 34 · WR 0.382 · nominal RR 1.5 · **effective RR 1.500** (rr-exit, no floor) · BASE ~+0.28 · **STRESS +0.264** · PF 1.662 · maxDD **3.58R** · max loss −1.019R · median R **+0.413** · avg winner **+1.251R** (n18) · avg loser **−0.846R** (n16) · median MAE 228p · median MFE 237p · median hold 26 H4 bars. **Geometry (large-move):** median SL **307 pips**, median TP **460 pips**; %TP ≥80 = 1.00, ≥100 = 1.00, ≥150 = 1.00, ≥200 = 0.97, **≥300 = 0.85**. Top-1/5/10 profit share 19.9 / 19.9 / **53.2%**.

## 11. Graveyard (§21)
- `OPEN[d+1]` earlier entry — **LOOKAHEAD**, permanently prohibited.
- `REF_FIRST` (frozen serialization) / `NEWDISP` / `EPISODE` — DEV-fail Gate I (top-10% 73–78% concentration; median negative). `CLUSTER6` — fails Gate I + best-10%-removed.
- COOLDOWN K=3 — fails Gate I marginally (61.6%).
Recorded in `eventize_dispfollow.py`. `MT-H4-dispaccept-L` preserved unchanged as `SIGNAL_ALPHA_CONFIRMED / EXECUTION_POLICY_NOT_VALIDATION_ELIGIBLE` (historical).

## 12. Recommended frozen policy + STOP
**Recommended: `H4-DISP-FOLLOW-L-COOLDOWN6`** — the frozen displacement+follow-through signal (causal `OPEN[d+2]` entry, H4 structural SL, RR 1.5), executed one-at-a-time with a **6-H4-bar post-exit cooldown**. It is the **only** causal event policy that converts the confirmed raw signal into a **broad, executable DEV edge** — passing all mandated gates: STRESS +0.264 > 0, best-5%-removed +0.218 > 0, best-10%-removed +0.135 > 0, **top-10% concentration 53.2% ≤ 60% (Gate I)**, positive incremental +0.249 over PROJECT TREND_UP, and K-robust. **Honest caveats for the CEO/Statistician:** small sample (N=34); 2021 marginally negative at K=6 (positive at K≥12); this is a bounded eventization pass, not validation. `MT-H4-efficiency-L` remains failed (trend beta); `MT-H4-dispaccept-L`'s *signal* is confirmed but its *serialized policy* is not — this new cooldown policy is the executable form.

**Per §19: DEVELOPMENT-only policy identity is now frozen. CALIB was NOT inspected. Returning to CEO before any CALIB — to prevent a further layer of selection leakage.**

**Terminal status:** `H4_DISP_FOLLOW_EVENT_POLICY_DEV_PASS` · `FOLLOWTHROUGH_POLICY_CANDIDATE_READY_FOR_CEO_REVIEW` (`H4-DISP-FOLLOW-L-COOLDOWN6`). **STOP.**
