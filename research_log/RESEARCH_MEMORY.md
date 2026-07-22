# Autonomous Research Memory — XAUUSD (Alpha)

Continuous batch target: **25 Observation Records** (batch = OBS-0002…). Instrument XAUUSD, mode
replay_pre_cutoff / sanctioned loader (holdout cutoff 2025-10-23). Descriptive only; no strategy/P&L.

**METHODOLOGY (CEO 2026-07-22): observation-first.** TradingView Replay = PRIMARY (eyes); Python =
VALIDATION only (statistician). Every question must ORIGINATE from replay observation, then Python
validates. OBS-0001..0016 were produced Python-first (pre-correction); OBS-0017+ are observation-first.
Operational learnings: (a) **replay_stop before re-seeking** a new date (stale-state seek defect, the
fail-closed guard catches it, retry-after-stop works); (b) `capture_screenshot` renders a **low-res
horizontal strip** — compensate with SMC/ICT label/box/line structural data for fine detail.

## Completed Observation Records (16; batch 15/25)
| ID | Question | Verdict |
|----|----------|---------|
| 0001 | prior-day sweep-reject vs break-hold | NEGATIVE (SMC sweep→reversal unsupported @1–6h) |
| 0002 | break-hold: level vs trend | NEGATIVE (dissolves 0001 residue) |
| 0003 | reject-reversion a NY effect | TENTATIVE → 0008 |
| 0004 | sweep depth predicts reversion | NEGATIVE |
| 0005 | prior-day close a magnet | NEGATIVE (opposite; confound) |
| 0006 | vol clustering + condition | CONFIRM+refine |
| 0007 | vol seasonality decomposition | CONFIRM+refine (hour-profile 4.3× + clustering + daily persistence) |
| 0008 | NY up-reject vs matched null | STRONG TENTATIVE (K6 CI<0, null p=0.021) |
| 0009 | day-of-week | NEG returns; weak vol gradient Fri>Mon |
| 0010 | round-number clustering | NEGATIVE (refuted) |
| 0011 | session-open expansion | CONFIRM NY-open; NEG directional |
| 0012 | reject all-cells selection test | NY-up uniquely distinguished but fails Bonferroni |
| 0013 | NY lead temporal stability | **sign-stable both halves → candidate-grade, holdout-gated** |
| 0014 | reproduce DC-0001 (velocity outlier) | **CONTRADICTION** — no continuation (n.s.), reconcile spec |
| 0015 | weekend gap fill | NEGATIVE (true but trivial; ~0 ATR gaps) |
| 0016 | equity leverage effect on gold | NEGATIVE (gold vol symmetric; +0.26 daily range persistence) |
| 0017 | **[observation-first]** marginal overshoot of H4 swing high = reversal tell? | NEGATIVE (overshoot uninformative; swing-low bounce = trend confound) |

## Discovery Candidates
**None frozen.** Leading candidate-grade lead: **NY-session prior-day-high sweep-reject → ~6h reversion**
(chain 0001→0003→0008→0012→0013: full-sample matched-null CI<0, uniquely distinguished, sign-stable
both halves; but fails Bonferroni, n=42, in-sample). **CEO decision requested:** authorize a reserved-
holdout (post-2025-10-23) test as the decisive gate before any freeze. Do NOT freeze on in-sample data.

## Contradictions
- **DC-0001** (frozen candidate, "isolated velocity outlier → gradual continuation"): does NOT reproduce
  under an independent H1 operationalization (mild reversal, n.s., n=485). Reconcile against DC-0001's
  exact `candidate_v1.md` definition/timeframes before concluding. (OBS-0014)

## Theme
Level structure (sweep/break/magnet/round-number/gap) = weak on H1 once trend + multiple-testing controlled
(0001,0002,0004,0005,0010,0015). **Volatility structure = robust** (clustering, hour-of-day 4.3× profile,
daily persistence, weekday gradient; and gold vol is SYMMETRIC in return sign, unlike equities —
0006,0007,0009,0011,0016). One surviving level lead: NY up-reject (holdout-gated).

## Duplicate-avoidance (do not re-run as-is)
0001,0002,0004,0005,0008,0010,0012,0013,0015 as specified. Extensions require a new control/condition/OOS.

## Next active investigation
Observation-first from here. **OBS-0018** onward (batch 17→25): each begins in replay, question emerges
from the chart, Python validates. NRQ-6 (swing-low bounce regime control) can be folded into an
observation session. Full batch report at OBS-0026 (25).
