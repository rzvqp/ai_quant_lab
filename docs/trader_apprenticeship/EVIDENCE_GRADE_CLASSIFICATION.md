# EVIDENCE_GRADE_CLASSIFICATION

Created 2026-08-25 per CEO Q1 audit correction. This is an audit/record-structure document — it does
not reinterpret any historical market decision and does not edit any frozen artifact
(`observation_candidates/TOC-001.md`, `TOC-002.md`, `checkpoints/TRADER_KNOWLEDGE_CHECKPOINT_2020_Q1.md`
remain unmodified, byte-for-byte, by this file's creation).

## Why this exists

Q1 did not use one uniform observation methodology. Presenting both periods as methodologically
equivalent overstates the strength of anything observed in the earlier period. This document defines
the boundary once, so it can be referenced (not re-derived) going forward.

## The two grades

### EARLY_PILOT
- **RANGE**: 2020-01-01 00:00 UTC → 2020-02-18 ~03:00 UTC (bar 1581980400)
- **METHOD**: H4-primary replay stepping; M15 detail read retrospectively/in batch for
  already-elapsed windows (verified exact against the H4 candle's own O/H/L/C, but not walked
  forward one M15 bar at a time as live-developing information)
- **EVIDENCE_GRADE**: lower apprenticeship evidence grade — genuine data, genuine observation, but
  not produced under the forward-frozen, one-step-one-read discipline the apprenticeship later
  adopted as its standard.

### STRICT_M15_APPRENTICESHIP
- **RANGE**: 2020-02-18 ~03:00 UTC (bar 1581980400) → present (ongoing)
- **METHOD**: M15 is the sole authoritative replay clock; exactly one `replay_step` followed by
  exactly one read, every time; MARKET_THESIS_SNAPSHOTs frozen forward, before outcomes are known,
  never rewritten with hindsight.
- **EVIDENCE_GRADE**: primary apprenticeship evidence grade.

## Retroactive tagging of existing frozen candidates' supporting instances

This tagging is informational only — it does not edit `TOC-001.md` or `TOC-002.md`, both of which
remain frozen as originally written.

**TOC-001** (fresh range-extreme rejection):
| Instance | Date | Grade |
|---|---|---|
| Spike to 1589.7 | 2020-01-03 | EARLY_PILOT |
| Spike to 1611.5 | 2020-01-08 | EARLY_PILOT |
| Fresh high 1592.168 | 2020-02-03 | EARLY_PILOT |
| Fresh high 1593.414 (2-bar hold, confirming) | 2020-02-19 | STRICT_M15_APPRENTICESHIP |
| Fresh high 1598.368 (44+ bar hold, counterexample) | 2020-02-19 | STRICT_M15_APPRENTICESHIP |

**TOC-001 evidence-grade note**: 3 of 4 confirming instances are EARLY_PILOT grade; the one
STRICT_M15_APPRENTICESHIP confirming instance and the single confirmed counterexample both come from
the same day (2020-02-19), immediately after the boundary. TOC-001's supporting record is therefore
weaker under the primary evidence grade than the raw 4-vs-1 count suggests — effectively 1
STRICT_M15_APPRENTICESHIP confirmation against 1 STRICT_M15_APPRENTICESHIP counterexample, with the
other 3 confirmations carrying the lower grade. This does not invalidate TOC-001; it is exactly the
kind of caveat that must travel with it into any future Alpha handoff.

**TOC-002** (multi-bar hold unreliability in extended-volatility regime):
| Instance | Date | Grade |
|---|---|---|
| 1657, 5-bar hold, fail | 2020-03-10 | STRICT_M15_APPRENTICESHIP |
| 1641.7, 6-bar hold, fail | 2020-03-11 | STRICT_M15_APPRENTICESHIP |
| 1641.7, 5-bar hold, fail | 2020-03-12 | STRICT_M15_APPRENTICESHIP |
| 1504.8, 16-bar hold, fail | 2020-03-20 | STRICT_M15_APPRENTICESHIP |
| 1608, break-reclaim, fail | 2020-03-25 | STRICT_M15_APPRENTICESHIP |
| 1620, 5-bar hold, fail | 2020-03-27 | STRICT_M15_APPRENTICESHIP |
| 1596, 2-bar hold, fail | 2020-04-01 | STRICT_M15_APPRENTICESHIP |

**TOC-002 evidence-grade note**: all 7 supporting instances are STRICT_M15_APPRENTICESHIP grade —
TOC-002 carries no EARLY_PILOT-grade evidence at all (it was discovered after the boundary). This is
TOC-002's strongest methodological property relative to TOC-001: its full record is primary-grade.

## Going forward

Every future `TRADER_OBSERVATION_CANDIDATE_<ID>`, `RECURRING_OBSERVATION_<ID>`, and any
`AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1` entry must tag each supporting instance with its evidence
grade (EARLY_PILOT / STRICT_M15_APPRENTICESHIP — the entire apprenticeship is
STRICT_M15_APPRENTICESHIP-grade from 2020-02-18 onward, so this will default to
STRICT_M15_APPRENTICESHIP for all Q2+ material, but the field must still be present so any future
period observed at lower rigor can be flagged the same way, without waiting for another audit to
catch it).
