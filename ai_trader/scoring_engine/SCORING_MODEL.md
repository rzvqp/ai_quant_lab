# Scoring Model v1 — the deterministic opportunity rubric (design)

This is the complete scoring philosophy. The `OpportunityScore` (0–100) is a **transparent, rule-based composite
of nine fixed components** — **not** a machine-learning prediction, **not** stochastic, **not** learned. Every
component is a pure function of the `StrategySignal` and the strategy's contract **evidence**; identical inputs
always give the identical score. Design only — no code; the formulas below are the specification an implementation
must reproduce exactly.

- **scoring_model_version:** `1.0.0`. Any change to a component, weight, or formula bumps this version so every
  score is reproducible against the exact model that produced it.

---

## 1. Philosophy
1. **Deterministic & explainable.** The score is arithmetic over declared inputs. No training, no probability
   model, no hidden state. Anyone can recompute a score by hand from the components.
2. **Honesty-preserving.** The rubric cannot make an unvalidated or negative-OOS strategy look strong: the
   `historical_confidence` component and the maturity caps hold it down. The Scoring Engine can only *lower*
   confidence relative to the strategy's own claims, never inflate it.
3. **Separation of quality from action.** The score measures the *quality of the opportunity*, not whether to
   trade it, how big, or against what portfolio. `risk_penalty` is a **quality discount** (a fragile / high-
   drawdown / tiny-sample strategy yields a lower-quality opportunity), NOT position risk — position risk is the
   Risk Manager's job.
4. **Batch-aware.** One component (`conflict_penalty`) depends on the whole concurrent batch; the rest are
   per-signal.

---

## 2. The nine components (each normalized to [0, 1])

Seven **quality components** (contribute upward) and two **penalties** (discount the result).

### Quality components
| # | component | source | rule (→ [0,1]) |
|---|---|---|---|
| 1 | `signal_strength` | `StrategySignal.signal_strength` | used directly (already 0–1: the strategy's own setup strength). |
| 2 | `historical_confidence` | contract `evidence` | maturity prior × OOS factor × validation factor, clamped. See §3. |
| 3 | `market_alignment` | `context_ref` / signal | 1.0 if the signal direction agrees with the context's short-term price/momentum tag; 0.5 neutral; 0.0 against. Deterministic from context features. |
| 4 | `regime_alignment` | signal `regime` + contract `market_regime` | 1.0 if current regime ∈ contract `applicable`; 0.5 if `ANY`/unknown; 0.0 if ∈ `avoid`. |
| 5 | `confirmation_quality` | `Explanation.confirmations` + state | `met / (met+pending)`; BUY/SELL (fully confirmed) → 1.0; WAIT_CONFIRMATION scales by the ratio; no confirmations required → 1.0. |
| 6 | `data_quality` | `context_ref.data_quality` | OK→1.0, DEGRADED→0.6, STALE→0.3, INSUFFICIENT→0.0. |
| 7 | `execution_readiness` | signal `state` + `trade_params` | BUY/SELL with valid entry/stop/target → 1.0; LONG_READY/SHORT_READY → 0.6; WAIT_CONFIRMATION → 0.3; non-actionable → 0.0. |

### Penalty components
| # | component | source | rule (→ [0,1], higher = worse) |
|---|---|---|---|
| 8 | `risk_penalty` | contract `evidence` (quality discount, NOT position risk) | rises with historical `drawdown_R`, `fragile=true`, and tiny sample `n`; e.g. `clamp( w_dd·norm(drawdown_R) + w_fr·fragile + w_n·smallN , 0, 1 )`. |
| 9 | `conflict_penalty` | the whole batch | opposing higher-ranked signal on the same symbol → strong penalty; correlated same-direction stacking → mild penalty. See §4. |

All nine are reported in `component_scores` so any score is fully decomposable.

---

## 3. `historical_confidence` (the honesty anchor)
```
maturity_prior:  EXPERIMENTAL 0.15 · EXPLORATORY 0.30 · CANDIDATE 0.45 · VALIDATED 0.75 · PROMOTED 1.00
                 (INVALID / NOT_IMPLEMENTED / RETIRED → 0.0)
oos_factor:      oos_expectancy_R > 0 → 1.0 ; == 0 or null → 0.6 ; < 0 → 0.4      (negative OOS caps the component)
validation_factor: matched_null PASS +0.1, walk_forward PASS +0.1, global_fdr PASS +0.1 (capped so the product ≤ maturity_prior tier)
historical_confidence = clamp( maturity_prior · oos_factor · (0.8 + validation_bonus) , 0, 1 )
```
Today every strategy is `EXPLORATORY`/`CANDIDATE` with `NOT_RUN` gates and (for the flagship sweep) negative OOS,
so `historical_confidence` is structurally low — exactly the intended honesty. The Scoring Engine never overrides
this from live behaviour (that would be learning, which it must not do).

---

## 4. `conflict_penalty` (the only cross-signal component)
Computed over the whole `OpportunityScore` batch for a symbol/`as_of`, in the deterministic ranking pass:
```
opposing:   an actionable signal in the OPPOSITE direction with a strictly higher provisional quality
            → conflict_penalty += 0.5   (this lower-ranked, contradicted opportunity is heavily discounted)
correlated: another actionable signal, SAME direction, from a strategy of the same mechanism class
            → conflict_penalty += 0.2 per additional correlated signal, capped at 0.4  (avoid double-counting one move)
conflict_penalty = clamp(sum, 0, 1)
```
The Scoring Engine only *penalizes* conflicts in the score; it does **not** resolve them (no netting, no
suppression, no selection) — resolution/selection is downstream. Determinism: the provisional quality used for the
opposing comparison is the pre-conflict `base_quality` (§5), so the pass is order-independent and reproducible.

---

## 5. Aggregation → 0–100
```
weights (fixed, scoring_model_version 1.0.0; sum of quality weights = 1.00):
   signal_strength         0.20
   historical_confidence   0.20
   market_alignment        0.12
   regime_alignment        0.15
   confirmation_quality    0.15
   data_quality            0.10
   execution_readiness     0.08

base_quality  = Σ (weight_i · quality_component_i)                      ∈ [0,1]
penalty_factor = (1 − risk_penalty) · (1 − conflict_penalty)           ∈ [0,1]
total_score   = round( 100 · base_quality · penalty_factor )           ∈ [0,100]   (deterministic rounding: half-up)
```
`total_score` is 0 whenever the opportunity is non-actionable (execution_readiness 0 pulls it down, and SKIP/
INVALID paths force it to 0). The weights are **fixed per `scoring_model_version`** — re-weighting is a versioned
change, never a live/learned adjustment.

## 6. Derived fields
```
confidence (enum): from historical_confidence tier   → NONE/VERY_LOW/LOW/MEDIUM/HIGH   (mirrors the contract tiers)
quality (enum):    from total_score bands            → PREMIUM ≥80 · STRONG 65–79 · MODERATE 45–64 · WEAK 25–44 · POOR <25
recommendation:    STRONG_OPPORTUNITY (total ≥65 AND state actionable) · MODERATE_OPPORTUNITY (45–64 actionable) ·
                   WEAK_OPPORTUNITY (25–44 actionable) · WATCH (READY/WAIT_CONFIRMATION) · SKIP (non-actionable/low) ·
                   INVALID (validation failure)
```
`recommendation` is advisory to the Risk Manager — it is NOT an order, not a size, not a decision to trade.

## 7. Ranking (deterministic)
Within a (symbol, `as_of`) batch, order by:
```
1) total_score            (desc)
2) historical_confidence  (desc)     tie-break 1
3) signal_strength        (desc)     tie-break 2
4) strategy_id            (asc)       tie-break 3 (guarantees a total order)
```
`rank` (1 = best) is assigned from this order. **Multiple strategies may hold high scores simultaneously** — the
Scoring Engine ranks them but does not choose; there is no stochastic tie-breaking anywhere.

## 8. Worked example (illustrative, not a live result)
A confirmed BUY from an `EXPLORATORY` sweep in its applicable regime, clean data, no conflict:
```
signal_strength 0.70 · historical_confidence 0.30·1.0·(0.8) ≈ 0.24 (negative-OOS example → 0.30·0.4·0.8 ≈ 0.10)
market_alignment 1.0 · regime_alignment 1.0 · confirmation_quality 1.0 · data_quality 1.0 · execution_readiness 1.0
base_quality = .20·.70 + .20·.10 + .12·1 + .15·1 + .15·1 + .10·1 + .08·1 = .14+.02+.12+.15+.15+.10+.08 = 0.76
risk_penalty 0.2 (moderate drawdown) · conflict_penalty 0 → penalty_factor = 0.8
total_score = round(100 · 0.76 · 0.8) = 61 → quality MODERATE, recommendation MODERATE_OPPORTUNITY, confidence LOW
```
The negative-OOS honesty term is what keeps even a clean live setup out of the PREMIUM band — by design.
