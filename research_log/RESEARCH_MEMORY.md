# Autonomous Research Memory — XAUUSD (Alpha)

Continuous batch target: **25 Observation Records**. Instrument XAUUSD, mode replay_pre_cutoff /
sanctioned loader (holdout cutoff 2025-10-23). Descriptive only; no strategy/P&L.

## Completed Observation Records
| ID | Question | Verdict | Residue |
|----|----------|---------|---------|
| OBS-0001 | prior-day sweep-reject vs break-hold aftermath | NEGATIVE (SMC sweep→reversal unsupported at 1–6h) | trend contamination; NY reject hint |
| OBS-0002 | is break-hold continuation level vs trend-conditioning | NEGATIVE (dissolves OBS-0001 continuation residue) | — |
| OBS-0003 | is reject-reversion a NY-session phenomenon | TENTATIVE (NY up-reject reverses, CI touches 0) | **leading residue → NRQ-1b** |
| OBS-0004 | does sweep depth predict reject reversion | NEGATIVE (corr≈0) | — |
| OBS-0005 | is prior-day close an intraday magnet | NEGATIVE (opposite: weak continuation, likely confound) | NRQ-4 local-detrend check |
| OBS-0006 | volatility clustering + session condition (ORQ-007) | CONFIRM + refine (session-dependent; lag-24 seasonality) | NRQ-5 hour-of-day profile |

## Discovery Candidates
None. (No-candidate is an accepted outcome.)

## Active residues / open questions (priority order)
1. **NRQ-1b** — NY-only up-reject reversion, pre-registered, matched-null control, powered (~42/qtr). Leading lead.
2. **NRQ-5** — decompose lag-24 vol seasonality into a fixed hour-of-day profile vs same-state clustering.
3. **NRQ-4** — does PDC-relative continuation survive local detrending? (confound test)
4. Underexplored perspectives queued: session-open behaviour, day-of-week (E008), round-number levels, overnight-gap behaviour, ATR-normalized range mean-reversion, equal-highs/lows (E017).

## Contradictions log
- None hard. Consistent theme: **prior-day-level "structure" interactions (sweep/break/magnet) carry little robust descriptive edge on H1 once trend and multiple-testing are controlled.** Volatility (clustering + seasonality) is the robust structure so far.

## Duplicate-avoidance
Do not re-run: binary sweep/break aftermath (0001), regime-split of same (0002), sweep depth (0004),
PDC-magnet global-detrend (0005). Extensions must add a new control/condition.

## Next active investigation
**OBS-0007 = NRQ-5** (volatility hour-of-day profile — builds on the strongest robust structure),
then OBS-0008 = NRQ-1b (NY reject, needs careful control design).
