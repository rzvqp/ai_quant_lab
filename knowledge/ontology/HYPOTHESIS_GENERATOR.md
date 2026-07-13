# HYPOTHESIS_GENERATOR — graph-driven candidate generation

**Proposals only — none implemented, backtested, or validated** (CEO constraints). Each candidate is tagged by KIND (alpha-candidate / beta-diagnostic / experiment / mechanism-test), the invariant it tests, source, prior-confidence heuristic, family extended, and next test.

## Rules
A ingredient-transfer onto a negative base; B stacked selectivity (risk: feature-stacking/selection inflation); C beta de-confound (DIAGNOSTICS, not alpha); D contradiction separating-tests (EXPERIMENTS); E data-gated upgrades; **F placebo / mechanism-invariance (Codex-added): survive beta-irrelevant transforms, fail mechanism-breaking placebos.**

## Generated candidates (19)

| id | kind | hypothesis | tests | prior | extends | tier |
|---|---|---|---|---|---|---|
| H001 | alpha-candidate | Value/VWAP reaction (P014) WITH a confirmation stage — precisely define reaction/direction/timing first (Codex: VWAP evidence is weak) | I1,I2,I9 | low | S8/S26/S27 | T0 |
| H002 | alpha-candidate | Breakout (P013) gated by high trend-efficiency — distinguish from P005 to avoid duplication (Codex) | I1,I4 | low | S3/S23 | T0 |
| H003 | alpha-candidate | Breakout (P013) restricted to psychological round levels (from P004) | I8 | low-medium | S3/S46 | T0 |
| H004 | alpha-candidate | Regime router (P016) with a STAND-ASIDE default (deploy only high-conviction sub-setups) | I3 | low | S40 | T0 |
| H005 | experiment | Round-number REJECT leg (P004 negative half) WITH a confirmation stage | I2 | low | S22 | T0 |
| H006 | alpha-candidate | Confirmed liquidity sweep (P001) that occurs AT a psychological round level (P004) — guard against redundant stacking | I1,I8 | medium | S1/S22 | T0 |
| H007 | alpha-candidate | Failed-breakout fade (P002) AT round-number levels (P004) | I8 | medium | S2/S22 | T0 |
| H008 | alpha-candidate | Short-term overreaction fade (P006) AT a structural level (P002/P010) | I5,I8 | low-medium | S42/S2 | T0 |
| H009 | alpha-candidate | Opening-range momentum (P003) WITH a confirmation filter — define base+confirmation precisely (Codex) | I1 | low-medium | S5 | T0 |
| H010 | alpha-candidate | Confirmed sweep (P001) applied to WEEKLY level memory (P010) | I2 | medium | S1/S17 | T0 |
| H011 | beta-diagnostic | Opening-range momentum (P003) short-side / down-flat regimes — BETA DIAGNOSTIC (not an alpha hypothesis) | I7 | n/a | S5 | T0 |
| H012 | beta-diagnostic | MTF alignment (P007) beta-neutralized (residualize vs gold trend) before scoring — BETA DIAGNOSTIC | I7 | n/a | S9/S20 | T0 |
| H013 | experiment | Confirmation-ablation on the sweep signal set (isolate the confirmation contribution) — EXPERIMENT | I2 | n/a | S1/S21 | T0 |
| H014 | experiment | Level-type ablation: structural vs statistical reference for the SAME reversion signal — EXPERIMENT | I8 | n/a | S2/S26 | T0 |
| H015 | alpha-candidate | True volume-profile value area (POC/VA) replacing the sigma-band proxy (P014) | I8 | unknown | S26 | needs finer/volume data |
| H016 | alpha-candidate | Intrabar pressure (P017) at tick/MBO resolution instead of OHLC proxy | I9 | unknown | S44 | T2 (tick/MBO) |
| H017 | mechanism-test | Level-label PLACEBO: confirmed-sweep (P001) with RANDOMIZED level labels (local structure preserved) should LOSE edge; survival implies the edge is not level-driven | I1,I8 | n/a | S1 | T0 |
| H018 | mechanism-test | Timing PLACEBO: a positive edge should survive a beta-preserving TIME-SHIFT but fail a mechanism-breaking random re-timing (matched-null already partly does this) | I7 | n/a | S5/S2/S1 | T0 |
| H019 | mechanism-test | Market-neutral RESIDUAL: test each positive primitive on gold returns residualized vs its own trend/beta; survivors are non-beta alpha, the rest are beta | I7 | n/a | all positives | T0 |

KIND matters: **alpha-candidates** could become families; **beta-diagnostics** and **experiments** test the graph itself; **mechanism-tests** probe WHY an edge exists (non-beta). All gated behind a future CEO decision and the frozen validation pipeline.
