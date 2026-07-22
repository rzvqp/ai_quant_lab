# OBS-0001 — Prior-day extreme: sweep-and-reject vs break-and-hold

**Type:** Observation Record (internal investigation). **NOT a Discovery Candidate.**
**Date:** 2026-07-22 · **Researcher:** Alpha (autonomous, TVRE) · **Status:** COMPLETE — negative w/ tentative residue

## Identity
- **Instrument / TF:** XAUUSD (OANDA), H1
- **Mode:** `replay_pre_cutoff` — TradingView replay anchored 2025-06-01 (cursor 1748822399, pre-cutoff), verified holdout-safe.
- **Quantitative substrate:** sanctioned fail-closed loader `edge_research/_common.load('H1')`, split `pre_holdout_2025-10-23T09-15-00Z_v1`, cutoff `2025-10-23T09:15:00+00:00`. **16,623 H1 bars, 2023-01-02 → 2025-10-23.**
- **Perspective:** structure / liquidity lens · falsification framing · mechanism-oriented.

## V0 question
On XAUUSD H1, is a **sweep-and-reject** of the prior-day extreme (wick pierces the level, bar closes back inside) descriptively distinguishable in its aftermath from a **break-and-hold** (bar closes beyond the level)? This challenges the widely-held SMC/ICT assumption that a "liquidity sweep" of the prior-day high/low signals reversal.

## Pre-registration (fixed before results)
- **PDH/PDL:** previous available UTC-calendar day's high/low.
- **Interaction (up):** first H1 bar of the day with `high > PDH`; classify `SWEEP_REJECT` if `close < PDH`, else `BREAK_HOLD`. (Down side symmetric on PDL.)
- **Aftermath:** close change over next K∈{3,6,12} bars. Sign-normalized so **+ = continuation in break direction, − = reversion**. v2 also uses **raw** change split by up/down and **detrended** by the unconditional K-bar drift.
- **Falsification target:** SMC predicts REJECT→reversion (−) and HOLD→continuation (+). If REJECT and HOLD aftermaths do not differ, the distinction is descriptively weak.

## TradingView environment observation (qualitative)
Replay at 2025-06-01; SMC [LuxAlgo] + ICT [LuxAlgo] visible. Read 300 live H1 replay bars (2025-05-13→06-01) and the indicators' drawn levels (SMC: 502 lines; ICT: 23). Screenshot: `tv_chart_2026-07-22T06-14-49-978Z.png`. Visual: gold rangey-to-up over the window; prior-day extremes are pierced most days, often intrabar, with no visually obvious reversal signature — motivating the quantitative test over the full history.

## Results
Interactions: **855** (up 472, down 383); SWEEP_REJECT 430, BREAK_HOLD 425.

**Sign-normalized forward displacement (+ = continuation):**
| K | SWEEP_REJECT mean (P cont>0) | BREAK_HOLD mean (P cont>0) | std. gap (HOLD−REJECT) |
|---|---|---|---|
| 3 | −0.11 (0.48) | −0.18 (0.52) | −0.10 |
| 6 | −0.00 (0.49) | +0.03 (0.52) | +0.03 |
| 12 | −0.50 (0.46) | +2.34 (0.53) | +2.30 |

**Detrended, split by direction (excess = rawΔ − unconditional drift):**
| group | K=6 excess (P Δ>0) | K=12 excess (P Δ>0) | SMC-predicted sign |
|---|---|---|---|
| up-reject | +0.36 (0.52) | +0.71 (0.51) | − (**contradicted**) |
| up-hold | +0.14 (0.54) | +1.10 (0.55) | + (weak-match) |
| down-reject | +0.42 (0.55) | +1.84 (0.60) | + (match) |
| down-hold | +0.51 (0.53) | **−3.41 (0.49)** | − (match, largest) |

Unconditional drift (uptrend): K6 +0.82, K12 +1.63.

## Answers to the Discovery questions (applicable subset)
1. **Exists vs noise?** At 3–6h, **no** — reject/hold aftermaths are indistinguishable (std gaps ≤0.10; P(cont) 0.48–0.55). The K=12 raw separation is largely the **uptrend**: detrending removes most of it and flips half the cells.
2. **Which horizon?** Any weak effect is at ~12h, not the 1–6h horizon the concept is used at.
3. **Sessions?** Strong heterogeneity: up-sweep-reject reverses **only in NY** (K12 excess −4.0, P=0.38, n=42); Asia/London contradict. Down-break-hold continuation is more consistent across sessions.
4. **Conditions that invalidate?** The blanket rule is invalidated at short horizon and on the up-side (drift-dominated). Effect, if any, is downside- and NY-concentrated.
5. **OOS?** Not tested; single instrument, in-sample only.

## Verdict
**NEGATIVE for the general SMC claim.** A prior-day-extreme sweep-and-reject is **not** descriptively distinguishable from a break-and-hold at the 1–6h horizon where the concept is applied; the apparent 12h separation is mostly the ambient 2023–25 gold uptrend.

**Tentative residue (hypothesis-generating only):** a weak, asymmetric, **session-dependent** structure at ~12h — downside break-continuation and NY-session upside sweep-reversal. With ~24 uncontrolled session×side×class cells and no multiple-testing correction, this is **not** a finding and **not** a Discovery Candidate.

## Assumption challenged
The popular "liquidity sweep of the prior-day high/low ⇒ reversal" heuristic is **not supported** as a general descriptive rule on XAUUSD H1 at its used horizon. Negative knowledge.

## Newborn research questions
- **NRQ-1:** Is the sweep→reversal effect genuinely a **session** phenomenon (NY only)? Pre-register a NY-only, direction-split test with a matched-null control and holdout.
- **NRQ-2:** Does **sweep depth** (distance pierced beyond the level, ATR-normalized) separate reject outcomes better than the binary close-inside rule? Mechanism: shallow poke vs deep stop-run.
- **NRQ-3:** Downside break-continuation (−3.4 excess/12h) vs upside: is break-continuation asymmetric in a trending regime, i.e. is this a **trend-conditioning** effect, not a level effect? (Test in a non-trending sub-period.)

## Artifacts & reproducibility
- `research_log/scripts/obs0001_sweep_vs_break.py` — main pre-registered analysis.
- `research_log/scripts/obs0001_v2_detrend.py` — self-falsification (detrend + up/down + session).
- Screenshot: `tradingview-mcp/screenshots/tv_chart_2026-07-22T06-14-49-978Z.png`.
- Rerun: lab venv + `PYTHONUTF8=1`; deterministic (no RNG). Holdout-safe by loader construction.
