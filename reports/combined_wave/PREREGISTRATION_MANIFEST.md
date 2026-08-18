# COMBINED WAVE — PREREGISTRATION MANIFEST (written before evaluation)

**Data identity:** M15_v2/pre_holdout/4-block/2011-2025 (sha256 57f4ed95…). **Evaluator:** mstrat.simulate@wp5b_reconciled (TICK=0.01).
**Range ledger:** ve_n1_replay 0.2.0 (wheel 04b96a8b…), ve_brain 0.1.3, detector 61cbd58, contracts range-state-v1 / range-events-v1.
**Primary rule (one definition, grid is sensitivity-only):** n_touch=2, tol_atr=0.25, er_max=0.40, d_min_bars=96, n_acceptance=2, width_filter=off, RANGE_STATE_OVER_TREND_PAUSE.

## F1–F6 range families (6 NEW economic mechanisms → n_generated +6; m_inference untouched=26)
| family | event_kind | direction | mechanism_cluster | HSF | disjoint from |
|---|---|---|---|---|---|
| F1 | RANGE_LOW_REJECTION | long (fade low) | RANGE\|F1 | rangefam:e… | F2 (opposite side) |
| F2 | RANGE_HIGH_REJECTION | short (fade high) | RANGE\|F2 | rangefam:… | F1 |
| F3 | BREAKOUT_ACCEPTED | break direction | RANGE\|F3 | rangefam:… | F5 (accepted⊥failed) |
| F4 | BREAKOUT_RETEST | break direction | RANGE\|F4 | rangefam:… | F5 |
| F5 | FAILED_BREAKOUT | fade into range | RANGE\|F5 | rangefam:… | F3/F4 (disjoint by construction) |
| F6 | LIQUIDITY_SWEEP_REVERSAL | reversal (opposite sweep) | RANGE\|F6 | rangefam:… | F3/F4 (opposite thesis) |

- **holding / exit:** NOT ratified in the delivered contract → any NET/inference requires the Statistician's exit spec.
  This wave reports **event reachability only**; F1/F2/F5/F6 = 0 events, F3/F4 = 1 event → all EVENT_TOO_RARE.
- `position_at_regime_end`: HOLD_UNTIL_STRATEGY_EXIT (when an exit spec exists).

## 44 breakout longitudinal remap (HSF preserved, new evaluation_run_hash)
- 28 `bos` → BREAKOUT_ACCEPTED; 16 `bos_retest` → BREAKOUT_RETEST. Economic rule (trade the confirmed break)
  realized exactly by the longitudinal event → **same HSF, new evaluation_run_hash, m_generated unchanged**.
- mechanism_cluster BREAKOUT|accepted / BREAKOUT|retest; disjoint from RANGE families and from FAILED_BREAKOUT.

## F7 — SAFETY_GUARD (NOT a hypothesis)
`RANGE_MID_NO_ENTRY`: executable prohibition; entry_decision.permitted=False; separate `n_guards` register; never in `m_inference`.

## TREND_DOWN/SHORT & TREND_UP
Already registered (127 + 127 in the 357); direction is in the fingerprint (regime TREND_DOWN⇒short, TREND_UP⇒long).
Not regenerated (would clone). Reported from the existing canonical rerun.

**Ruling requested from the Statistician:** exactly **6** new economic mechanisms (F1–F6) enter n_generated_total (→363);
`m_inference` stays **26**; F7 stays in `n_guards`. No p-value or significance is computed by Alpha in this diagnostic wave.
