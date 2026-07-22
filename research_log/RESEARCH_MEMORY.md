# Autonomous Research Memory — XAUUSD (Alpha)

Continuous batch target: **25 Observation Records**. Instrument XAUUSD, mode replay_pre_cutoff /
sanctioned loader (holdout cutoff 2025-10-23). Descriptive only; no strategy/P&L.

## Completed Observation Records (11)
| ID | Question | Verdict | Residue |
|----|----------|---------|---------|
| 0001 | prior-day sweep-reject vs break-hold aftermath | NEGATIVE (SMC sweep→reversal unsupported at 1–6h) | trend contamination; NY hint |
| 0002 | break-hold continuation: level vs trend | NEGATIVE (dissolves 0001 residue) | — |
| 0003 | reject-reversion a NY-session effect | TENTATIVE (NY up-reject, CI touches 0) | → 0008 |
| 0004 | sweep depth predicts reversion | NEGATIVE (corr≈0) | — |
| 0005 | prior-day close a magnet | NEGATIVE (opposite; likely confound) | NRQ-4 |
| 0006 | volatility clustering + condition | CONFIRM+refine (session-dep; lag-24) | → 0007 |
| 0007 | vol seasonality decomposition | CONFIRM+refine (hour-profile 4.3× + surviving clustering + daily persistence) | residual daily vol-state |
| 0008 | NY up-reject vs matched null | **STRONG TENTATIVE** (K6 excess −3.6, CI<0, null p=0.021; **selection-uncorrected, n=42**) | **leading lead → 0012** |
| 0009 | day-of-week structure | NEGATIVE returns; weak vol gradient Fri>Mon | — |
| 0010 | round-number clustering of extremes | NEGATIVE (belief refuted) | — |
| 0011 | session-open expansion/bias | CONFIRM NY-open expansion; NEG directional | subsumed by 0007 |

## Discovery Candidates
None frozen. **Leading candidate-precursor:** OBS-0008 (NY up-reject reversion) — pending selection-correction (0012) + holdout.

## Active leads / open questions (priority)
1. **0012 (blocking the lead):** run ALL 8 session×direction reject cells under the same matched null — is NY-up uniquely significant, or one of many? Selection correction for OBS-0008.
2. **NRQ-4** — PDC continuation under local (not global) detrend — confound test.
3. residual daily vol-state (0007c); weekday vol gradient (0009).
4. Queued perspectives: equal-highs/lows (E017), overnight-gap, ATR range mean-reversion, intraday range-extension vs time-of-day, cross-TF alignment.

## Contradictions / theme
Consistent: **prior-day LEVEL structure (sweep/break/magnet/round-number) carries little robust H1 edge** once trend + multiple-testing controlled (0001,0002,0004,0005,0010). **VOLATILITY structure is robust** (clustering, hour-of-day 4.3× profile, daily persistence, weekday gradient — 0006,0007,0009,0011). One genuine level-based lead survives conditioning: NY-session up-reject reversion (0008), pending selection-correction.

## Duplicate-avoidance (do not re-run as-is)
binary sweep/break aftermath (0001), regime-split (0002), sweep depth (0004), PDC global-detrend (0005),
vol clustering raw (0006), NY-only reject same-data (0008 done). Extensions must add a new control/condition/OOS.

## Next active investigation
**OBS-0012** = all-cells matched-null (selection correction for the NY lead). Decides whether OBS-0008 escalates toward a Discovery Candidate or is downgraded to noise.
