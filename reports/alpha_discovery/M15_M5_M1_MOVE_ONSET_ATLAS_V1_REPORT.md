# M15 MOVE → M5 (2021–24) / M1 (2025+) ONSET ATLAS V1

Multi-resolution causal onset discovery — no strategy, no entry/SL/TP/PnL, no ML, no exogenous data. M15 remains the master outcome scale
(100 pips = $10, first-touch over the next 8 M15 bars = 2 h). Precursors measured on the **30-minute wall-clock** window before each M15 anchor —
M5 = last 6 bars, M1 = last 30 bars (equal wall-clock, *not* equal bar count). Ten resolution-invariant families S1–S10. Occurrence (episode vs
matched control) and direction (up vs down) kept strictly separate. `PROTOCOL_HASH = 849c342a72f031619a36`, `FUTURE_FEATURE_OBSERVATIONS = 0`.

## Data inventory (§1) — both gates PASS; M1 genuine but quarantined
| | source | native | start | end | bars |
|---|---|---|---|---|---|
| M5 | OANDA:XAUUSD | YES | 2021-07-27 | 2026-07-27 | 354,669 |
| **M1** | OANDA:XAUUSD | **YES** | **2025-08-04** | 2026-08-04 | 354,177 |

`M5_DATA_GATE = PASS`. `M1_DATA_GATE = PASS` — the M1 is **verified genuine native** (sha256 `8387296e…`; its M1→M5 aggregate reproduces the
canonical native M5 OHLC **exactly** over 69,179 buckets, 0 mismatches — not synthetic, not interpolated, not GC). **But it carries a binding
governance status: `⛔ UNFIT_FOR_VALIDATION` + quarantined** (single bull regime, ~1 yr; cost/R 11–28% vs ~3% on M15). Therefore, per §27, every M1
finding here is a `CURRENT_REGIME_DISCOVERY_CANDIDATE` only — no validation, no edge, no PnL claim; Statistician ratification required before any use.

## Headline — resolution does NOT unlock direction; the binding constraint is REGIME
`CURRENT_M1_DIRECTIONAL_INFORMATION_FOUND = NO` · `M1_INCREMENTAL_DIRECTION_INFORMATION = NO` · `M15_TO_M1_EXECUTION_RESEARCH_JUSTIFIED = NO`.

### Opportunity is abundant and clean in the M1 era
Block A (M5 2021-24): 2,138 episodes (~623/yr). Block B (M1 2025+): **4,886 episodes** over ~1 yr — far denser because $10 is a smaller fraction of
the elevated 2025–26 ATR (a fixed-$ threshold caveat, not more "signal"). UP 49.0% / 49.7% (symmetric). Recent-era path quality: median adverse
only **$3.1 (31 pips)** before 100 pips, MFE/MAE > 2 in **83.7%** — the opportunity remains clean.

### Direction: a real M5 signal in 2021–24 that has DECAYED to nothing by 2025+ (on BOTH resolutions)
| block / resolution | best direction family | AUC | effect | latest-third eff | gate |
|---|---|---|---|---|---|
| **M5 2021–2024** | S2 progressive migration (close-location) | 0.390 | **0.110** | 0.135 | ✅ pass |
| M5 2025+ (same-family) | S2 progressive migration | 0.478 | **0.022** | 0.004 | ✗ |
| **M1 2025+** | S5 impulse | 0.491 | **0.009** | 0.017 | ✗ |

In 2021–2024, M5 micro-sequence carried a genuine directional (short-term **mean-reversion**: up-moves from a low close-location) signal, effect
0.110, sign-consistent 3/3 — the same mechanism the M15 atlas found. **In the current regime that signal has collapsed on M5 (0.110 → 0.022) and is
entirely absent on M1 (0.009 — pure noise, every family AUC 0.49–0.51).** `CURRENT_REGIME_DECAY`.

### The central overlap test (§24): M1 adds nothing over M5 on identical episodes
| family | M1 effect | M5 effect | M1 − M5 |
|---|---|---|---|
| S5 impulse | 0.009 | 0.012 | −0.003 |
| S2 close-location | 0.008 | 0.022 | −0.014 |
| S6 sweep/reclaim | 0.008 | 0.008 | 0.000 |
| S4 15-min displacement | 0.007 | 0.018 | −0.011 |

On the SAME 2025+ episodes, M1 directional discrimination does **not** exceed M5 — it is equal-or-worse for every family (`M1_MINUS_M5 = −0.003`
for the best M1 feature). The finer resolution reveals **no** incremental directional information: sweep/reclaim, microstructure progression, and
onset transition are all non-incremental (`M1_SWEEP_RECLAIM_INCREMENTAL = NO`, `M1_MICROSTRUCTURE_INCREMENTAL = NO`, `M1_ONSET_TRANSITION_FOUND = NO`).

### Onset timing (§25): no directional information at any window
M1 net-return direction AUC ending 30 / 15 / 10 / 5 min before the anchor: 0.498 / 0.493 / 0.489 / 0.489 — flat at chance. `EARLIEST_M1_DIRECTIONAL_INFORMATION_WINDOW = none`. There is no directional onset for M1 to reveal earlier, because there is none to reveal.

### Occurrence (magnitude): weakly predictable both, magnitude-only
Best occurrence AUC: M5-A `s7_rng` 0.576, M1-B `s2_slope` 0.609 (progressive migration) — recent range/expansion weakly predicts *that* a move is
coming, on both resolutions, but tells nothing about direction. `MAGNITUDE_ONLY`.

## §32 CEO answers (abridged)
Native M5 2021-07-27→2026-07-27; native M1 2025-08-04→2026-08-04 (UNFIT/quarantine). 2,138 M5 episodes (2021-24); 4,886 M1-era episodes. Recent
moves **clean** (31-pip median adverse). Best M5 2021-24 direction = S2 close-location (eff 0.110, mean-reversion); it does **not** survive on M5
2025+ (eff 0.022). Best M1 2025+ direction = S5 (eff 0.009, noise); fails all thirds. On identical episodes M1 is **not** stronger than M5
(−0.003). M1 reveals **no** hidden sweep/reclaim, microstructure, expansion, or failed-push direction beyond M5. **No** onset transition in the
final 5–15 min. Earliest directional window = none. Information is **magnitude-only**. Qualifying directional episodes/month = **0**. M1 does **not**
provide incremental information → an M15→M1 execution architecture is **not** justified, and acquiring more historical M1 would **not** help (M1
adds nothing over the M5 already held; the constraint is regime, not resolution or history length).

## §37 FINAL OUTPUT
```
M15_M5_M1_MOVE_ONSET_ATLAS_V1_COMPLETE = YES · PROTOCOL_HASH = 849c342a72f031619a36
M5_DATA_GATE = PASS · M1_DATA_GATE = PASS (genuine native verified; UNFIT_FOR_VALIDATION/QUARANTINE -> CURRENT_REGIME_DISCOVERY_CANDIDATE) · FUTURE_FEATURE_OBSERVATIONS = 0
M5_2021_2024_UNIQUE_100_EPISODES = 2138 · M1_CURRENT_UNIQUE_100_EPISODES = 4886
M5_2021_2024_MOVES_100_PER_YEAR = 623 · M1_CURRENT_MOVES_100_PER_YEAR = ~5000 (fixed-$10 in high-vol regime; not regime-comparable)
BEST_M5_2021_2024_DIRECTION_SEQUENCE = S2 progressive migration (close-location; mean-reversion) · BEST_M5_2021_2024_DIRECTION_EFFECT = AUC 0.390 (eff 0.110)
BEST_M5_CURRENT_DIRECTION_SEQUENCE = S2 progressive migration · BEST_M5_CURRENT_DIRECTION_EFFECT = eff 0.022 (decayed)
BEST_M1_CURRENT_DIRECTION_SEQUENCE = S5 impulse · BEST_M1_CURRENT_DIRECTION_EFFECT = eff 0.009 · BEST_M1_LATEST_THIRD_EFFECT = 0.017
M1_MINUS_M5_SAME_PERIOD_EFFECT = -0.003
EARLIEST_M1_DIRECTIONAL_INFORMATION_WINDOW = none
M1_SWEEP_RECLAIM_INCREMENTAL = NO · M1_MICROSTRUCTURE_INCREMENTAL = NO · M1_ONSET_TRANSITION_FOUND = NO
CURRENT_M1_DIRECTIONAL_INFORMATION_FOUND = NO
M1_INCREMENTAL_DIRECTION_INFORMATION = NO
M15_TO_M1_EXECUTION_RESEARCH_JUSTIFIED = NO
ADDITIONAL_HISTORICAL_M1_ACQUISITION_JUSTIFIED = NO
BINDING_FAILURE_REASON = CURRENT_REGIME_DECAY (M5 direction eff 0.110 in 2021-24 -> 0.022 in 2025+; M1 0.009) + MAGNITUDE_ONLY (both resolutions predict occurrence not direction) + NO_RESOLUTION_ADVANTAGE (M1 not > M5)
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

## Interpretation (§34)
The multi-resolution test is conclusive on its own terms. A genuine short-term mean-reversion **direction** signal existed on M5 in 2021–2024
(eff 0.110), reconfirming the M15 atlas — but it has **decayed to nothing in the current regime on both M5 (0.022) and M1 (0.009)**, and M1's finer
resolution provides **zero incremental directional information** over M5 on identical 2025+ episodes (no earlier onset, no hidden sweep/reclaim, no
microstructure edge). The binding constraint is therefore **regime, not resolution**: `CURRENT_REGIME_DECAY + MAGNITUDE_ONLY`. This forecloses the
"M15 setup → M1 directional trigger" execution architecture as specified — not because M1 is bad data, but because there is no current-regime
directional onset at any resolution for M1 to expose. This is not a claim that XAU direction is impossible or that M1 never works — only that this
representation, in this regime, carries occurrence (magnitude) information but no direction. Per §36 no strategy/entry/stop/target was built and no
additional M1 was acquired. S5 remains the sole validated tradeable XAUUSD edge. Protections intact.
```
M15_M5_M1_MOVE_ONSET_ATLAS_V1 = COMPLETE — M5 direction (mean-reversion) existed 2021-24 but decayed to ~0 by 2025+; M1 adds nothing over M5; occurrence magnitude-only. Binding = REGIME not RESOLUTION. Execution research NOT justified.
```
