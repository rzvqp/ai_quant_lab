# ALPHA_XAUUSD_EARLY_SESSION_LIQUIDITY_TRAP_REPORT

**Mandate:** `ALPHA-XAUUSD-EARLY-SESSION-LIQUIDITY-TRAP-001` · **Date:** 2026-08-22 · **Parent lineage:** commit `722a0e0` (frozen); **Statistician audit:** `ce4b634`.
**Terminal status:** `XAUUSD_EARLY_SESSION_LIQUIDITY_TRAP_DISCOVERY_COMPLETE` · **`EARLY_SESSION_LIQUIDITY_SIGNAL_READY_FOR_CEO_REVIEW`**.
**Firewall:** 100% XAUUSD price-only; gated M5 → causal M15; no `read_csv`; N4=0; 2025+=0; no V1/holdout/CALIB. **~13 univariate + 1 combined + 4 simple-rule signal IDs (≤20), 1 frozen early signal. NO execution/stop/target design (§28).** DEV-only. No promotion; broker disabled; 9 frozen strategies untouched.
**Boundary honored (§28):** an early signal survived → it is **frozen** and this mandate **STOPS**. Execution conversion is a separate future mandate. No entry/SL/TP/RR was optimized.

---

## 0. Headline — answers to the §29 questions
1. **Can a trap be identified at the sweep itself (E0)?** Partially — E0 anatomy (excursion, close-above, attack deceleration) is DISC→CONF stable but modest; the decisive information arrives at **E1**.
2. **Does the sweep candle anatomy carry information?** Yes, modestly (e0_excursion top-vs-bottom-tercile spread +0.256 CONF; smaller excursion → trap).
3. **Does E1 add useful information?** **Yes — decisively.** The E1 close-below-Asia-High + bearish body is the core signal.
4. **Does E2 add useful information?** Yes (e2_lower_high AUC 0.65) — but E2 is *later*; E1 already suffices, so E2 is unnecessary for the frozen early signal.
5. **Probability improvement per bar of waiting?** The jump is E0→E1 (E1 features dominate); E1→E2 adds little for the added latency.
6. **Reward lost per bar of waiting?** Minimal E0→E3 (39→36p remaining). The large loss is E1→S2 (39→10p). **Waiting to E1 is nearly free; waiting to S2 is very costly.**
7. **Earliest useful causal landmark?** **E1 (bar sw+1).**
8. **Does London differ from London/NY overlap?** Both positive; London has larger N (base P(mid) 0.62/0.72 DISC/CONF), overlap smaller (0.55/0.63). The signal works in both — reported separately (§11).
9. **Does bullish deceleration matter?** Yes — slower attack into the sweep (e0_attack_accel, +0.119 spread) and failed extension (e1_extend) both predict the trap.
10. **Does failure of marginal upside progress matter?** Yes — e1_extend (E1 fails to extend the sweep high) is stable (+0.142 spread).
11. **Useful probability lift while ≥20–50p remain?** **Yes — the headline result:** +0.18 CONF lift with **median 23p remaining** (65% of flagged states ≥20p).
12. **Is there one frozen early signal worthy of execution research?** **Yes — `EARLY-TRAP-E1` (rule R2 + its logistic form).**

## 1. Artifact lineage + frozen parent (§3) — UNCHANGED
Parent population recovered mechanically from `session_trap.py` (commit `722a0e0`): **329 Asia-High sweep days**, unchanged session/timezone/DST/Asia-range/Asia-High/sweep/day semantics. DST-correct sessions (Asia fixed-UTC/Tokyo no DST; London/NY via `tz_convert`). Nothing about the parent was altered to improve results.

## 2. Landmark construction + economics (§4, §13) — the reframe, quantified
| landmark | n | median % path consumed | median pips remaining to mid | base P(reach mid) | P(new high > sweep) |
|---|---|---|---|---|---|
| **E0** (sweep bar) | 329 | −1.4% | 39.1p | 0.617 | 0.769 |
| **E1** (sweep+1) | 329 | **0.2%** | **39.1p** | 0.620 | 0.669 |
| E2 (sweep+2) | 329 | −1.1% | 36.6p | 0.626 | 0.614 |
| E3 (sweep+3) | 329 | 1.5% | 36.0p | 0.629 | 0.559 |
| *S2 (reference)* | 86/50 | *~83%* | *~10p* | *0.78* | — |
| *S4 (reference)* | 58/34 | *~109%* | *target passed* | *0.95* | — |
**E0–E3 land while ~0% of the path is consumed and ~36–39p remain — ~4× the room at S2.** This is the window the Statistician identified as missing.

## 3. Univariate early-feature discrimination (§19) — stable dimensions (landmark E1)
AUC vs reach-mid (DISC | CONF), and DISC→CONF stability:
| feature | DISC AUC | CONF AUC | stable | reading |
|---|---|---|---|---|
| **e1_bear** (bearish E1 body) | 0.673 | 0.630 | ✓ | immediate bearish reaction → trap |
| **e1_close_above** (E1 close vs Asia High) | 0.299 | 0.288 | ✓ | close back below → trap (strongest, flipped) |
| e2_below_hi | 0.255 | 0.260 | ✓ | (E2 — later) |
| e1_extend (failed to extend high) | 0.363 | 0.401 | ✓ | no marginal upside progress → trap |
| e0_close_above | 0.436 | 0.356 | ✓ | weak sweep close → trap |
| e0_excursion | 0.445 | 0.343 | ✓ | smaller excursion → trap |
| e0_attack_accel | 0.411 | 0.401 | ✓ | slower attack → trap |
Univariate CONF top-vs-bottom-tercile P(mid) spreads: **e1_close_above +0.412**, e0_excursion +0.256, e1_bear +0.232, e1_extend +0.142, e0_attack_accel +0.119. All stable, all early.

## 4. Combined early model (§18) + ablation
E1-only interpretable logistic (11 E1-knowable features, ≤12; frozen DISC standardization): **DISC AUC 0.743 → CONF AUC 0.679.** Ablation dropping `e1_close_above` (the "fast-return" proxy): CONF AUC **0.673** — the signal is **not** a fast-return tautology; the remaining anatomy (close location, excursion, deceleration, bearish body) carries it.

## 5. FROZEN EARLY SIGNAL — `EARLY-TRAP-E1` (§29.Q12)
Two equivalent forms, both frozen on DISCOVERY, evaluated once on CONFIRMATION:

**Rule R2 (transparent, primary frozen form):** *At the frozen Asia-High sweep, at E1 (bar sweep+1 close): if the bar **closes back below Asia High** AND has a **bearish body** → flag TRAP.*
| | n | P(reach mid) | base | lift | median remaining | P(new high) |
|---|---|---|---|---|---|---|
| DISCOVERY | 68 | 0.794 | 0.594 | **+0.200** | 20.7p | 0.41 |
| CONFIRMATION | 50 | 0.840 | 0.659 | **+0.181** | 23.3p | 0.54 |

**Logistic form (multivariate):** top-40% early-confidence (p ≥ DISC-frozen 0.649): CONF n50, P(mid) 0.840 (+0.181), median 23.3p remaining — identical economics, confirming R2 captures the signal.

## 6. Remaining-reward gate (§20) — characterization, thresholds not chosen post hoc
Frozen DISC probability thresholds; CONF remaining-distance distribution:
| threshold | CONF n | P(mid) | lift | median remaining | ≥20p | ≥30p | ≥40p | ≥50p |
|---|---|---|---|---|---|---|---|---|
| all (base) | 132 | 0.659 | — | 35.6p | 0.81 | 0.64 | 0.44 | 0.26 |
| p ≥ q0.5 | 63 | 0.778 | +0.119 | 23.8p | 0.65 | 0.40 | 0.14 | 0.06 |
| **p ≥ q0.6** | **50** | **0.840** | **+0.181** | **23.3p** | **0.60** | 0.38 | 0.14 | 0.08 |
| p ≥ q0.7 | 40 | 0.825 | +0.166 | 21.0p | 0.57 | 0.33 | 0.10 | 0.03 |
**Moderate room, honestly stated:** ~23p median remaining, 60% ≥20p, 38% ≥30p, only ~14% ≥40p. This is the CEO's stated preferred trade-off (≈84% hit with ~23p remaining ≫ 90% hit with 5p at S2).

## 7. Temporal robustness (§27) — positive in EVERY block (not a 2023 artifact)
Top-40% early-confidence P(mid) lift by period:
| period | n | P(mid) | base | lift |
|---|---|---|---|---|
| 2021 (DISC) | 33 | 0.818 | 0.561 | +0.257 |
| 2022 (DISC) | 20 | 0.750 | 0.685 | +0.065 |
| 2023<cut (DISC) | 26 | 0.769 | 0.557 | +0.212 |
| **2023 CONF (OOS)** | 50 | 0.840 | 0.659 | **+0.181** |
Positive in all four; 2022 smaller (+0.065) but positive. The signal does **not** depend on one narrow period — the first SHORT-family signal to clear this.

## 8. Path survivability (§22) — descriptive only (no stop designed)
For the flagged (R2/top-40%) states: **P(new high above sweep) ≈ 0.50** (vs 0.70 base — the early model also selects better-surviving states), median adverse excursion before mid ≈ 24.5p. **This is characterization, not an execution rule** (§28). It flags a real execution risk: ~half of flagged traps still poke a new high before reverting — the RR study belongs to the execution mandate.

## 9. Session (§11), first-vs-repeat (§9), PDH (§23), width (§24), sweep-size (§25)
- **London vs Overlap:** both positive (London base P(mid) 0.62/0.72, Overlap 0.55/0.63); reported separately, not pooled. NY-only too sparse (diagnostic).
- **First-vs-repeat:** nearly all parent sweeps are "repeat" attacks (≥1 prior same-day touch); first-attack N too small to separate — no claim.
- **PDH:** context diagnostic only; not developed into a strategy (§23).
- **Asia width / sweep magnitude:** used only as continuous controls; per Statistician (`SWEEP_MAGNITUDE_NOT_SUPPORTED`) not reopened as discriminators. The prior wide-range observation is **not** promoted.

## 10. Matched-parent discipline (§14)
All comparisons are S0-all vs S0+early-feature on the **same 329-sweep parent** at the same landmark — matched by construction, not across different populations.

## 11. Candidate ranking
1. **`EARLY-TRAP-E1` (R2 / logistic)** — the frozen early signal. Early (bar sw+1), DISC→CONF stable (+0.20→+0.18), temporally robust (all blocks positive), ~23p remaining, transparent. **Ready for execution research.**
2. (No second candidate frozen; E2/S2/S4 are references only, per §26 — deliberately not retuned.)

## 12. Graveyard
- E0-only classification (sweep candle alone) — stable but too weak to stand alone.
- e1_contraction, n_prior_attacks, e0_closeloc, e0_body — not stable / weak. Recorded in `early_trap.py` / `early_trap2.py`.

## 13. CEO recommendation
1. **`EARLY_SESSION_LIQUIDITY_SIGNAL_READY_FOR_CEO_REVIEW`.** The Statistician's critique is resolved: the trap **can** be identified early. At **E1 (bar sweep+1)** — while ~0% of the path is consumed and ~39p (top-bucket ~23p) remains — a transparent anatomy rule (E1 closes back below Asia High with a bearish body) raises P(reach Asia mid) from 0.66 to **0.84 out-of-sample (+0.18)**, with matching multivariate confirmation (CONF AUC 0.679) and **positive lift in every temporal block (2021/2022/2023)**. This is the earliest useful landmark and materially precedes S2/S4.
2. **Freeze `EARLY-TRAP-E1` and open a separate EXECUTION-RESEARCH mandate** (§28). That mandate must resolve the open execution question this discovery deliberately did not touch: with the structural stop necessarily above the sweep extreme and P(new-high)≈0.5, can ~23p of remaining reward be converted to positive expectancy? (The prior mandate showed *late* mid-targeting did not monetize; this signal's value is that it arrives *early with room* — the exact lever, but execution must be proven, not assumed.)
3. **Honest caveats (unchanged discipline):** the endpoint is P(reach Asia MID) — a **directional/mean-reversion diagnostic, not yet a P&L edge**; CONF is a single 2023 OOS window (mitigated by positive 2021/2022 in-sample lift); remaining reward is moderate (~23p median). No causal claim about *why* the anatomy predicts reversion.
4. **No promotion; broker disabled; DEV-only; no CALIB; no execution optimization.** The 9 frozen strategies are unaltered; portfolio SHORT still only frozen `H4-bo-raw-S`. Recommended reviewers: Statistician (independent multi-year temporal-CV of `EARLY-TRAP-E1`) → then execution mandate.

**Terminal status:** `XAUUSD_EARLY_SESSION_LIQUIDITY_TRAP_DISCOVERY_COMPLETE` · `EARLY_SESSION_LIQUIDITY_SIGNAL_READY_FOR_CEO_REVIEW`. **STOP.**
