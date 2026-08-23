# PREREGISTRATION — ASREJ-1 (Asia demand-zone rejection in up-regime, LONG)

Preregistered from BLIND_FORWARD_STRUCTURE_DISCOVERY_V1 (BFSD4 Batch-2, out-of-sample). This is the FIRST emergent morphology cell to
hold above base past n≥100 across eras. Preregistration precedes mechanization + full quant-falsification (§12/§13). **Discovery ≠
edge.** Expectation is TEMPERED: the effect is mild and likely trend/era-flavored; the quant gate (with costs) is expected to be decisive.

## Discovery evidence (frozen, do not retune)
- Cell `BULLISH|up|REJ_low|nearZone|AS`: n=124 out-of-sample, **P2R=0.387** (2R:1R), vs null 0.333 = **+0.054**; base(this batch)=0.297.
- Stability: 0.407 (n81) → 0.387 (n124) as n grew — held, mild regression. Era spread D33 / C39 / **O52** (present incl. OOS).
- Context: overall broadened reader is below null (0.297); this is a CONDITIONAL cell, not a broad edge.

## Formal hypothesis (deterministic, causal — for mechanization)
At M15 candle T, enter LONG iff ALL hold using only bars ≤ T:
1. **N1 (H4 regime) direction = `up`** (strong; NOT `weak_up`) — canonical `regime_classifier.classify_regime` on causal H4.
2. **N2 (H1 bias) direction = `long`** — canonical `bias_h1.compute_bias` on causal H1.
3. **Location:** nearest canonical N3 confluence zone below `reference_price` has `distance_atr ≤ 1.0` (price at/near a demand/discount zone).
4. **Trigger:** candle T is a rejection-of-lows — lower wick ≥ 1.5×body AND ≥ 0.3×ATR (`REJ_low`).
5. **Session:** Asia (00:00–08:00 UTC).
- **Entry** = close[T]. **Invalidation** = prior-20-bar low − 0.2×ATR. **Target** = +2R (2×|entry−invalidation|). Cooldown ≥ 10 bars.
- **Mechanism claim:** in a confirmed up-regime, a wick-rejection of lows into a demand confluence during the Asia session marks a
  higher-low continuation → LONG. **Null:** P(+2R before −1R) = 0.333.

## Falsification plan (MANDATORY before any promotion — §13)
Mechanize as a deterministic strategy, then run the FULL quant gate on causal execution:
DISC / CONF / OOS · realistic costs · STRESS · 2× costs · best-decile-removed (tail) · leave-one-year-out · leave-one-episode-out ·
effective-N · entry delay · neighbor robustness · dedup · regime specificity · portfolio independence vs S5.
**Promotion requires surviving ALL.** Given gross expectancy ≈ +0.16R/trade (thin), rejection under costs is the expected outcome;
that would be a clean negative, not a failure of process. If it survives → FROZEN_PENDING_INDEPENDENT_VALIDATION → CANDIDATE_QUEUE.

## Status
PREREGISTERED 2026-08-24. Next: mechanize (`asrej1.py`) + run the gate. No promotion, no P&L claim, until the gate returns.
