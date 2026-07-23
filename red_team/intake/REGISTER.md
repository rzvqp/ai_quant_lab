# RED TEAM — INTAKE REGISTER
### Every Discovery Candidate ever submitted to Red Team
**Parent:** [CHARTER.md](../CHARTER.md) §8 [0]. One row per submission. Append-only; never edit a prior row.

Intake gate: a row is admitted only if the DC is **FROZEN**, the submission package is **complete**, and a **freeze-hash** is present. Otherwise status = `UNREVIEWABLE` (returned, not reviewed).

Source of record: `ai_quant_lab-alpha-automation` worktree (branch `alpha-automation-v1`), the current official Alpha state — NOT the stale `ai_quant_lab-alpha-discovery` worktree. Scope of this intake batch (CEO decision, 2026-07-23): the 13 candidates carrying a `FROZEN / SUBMITTED` line in Alpha's `HANDOFF_LOG.md`. DC-0008…DC-0012 are held (frozen + hashed in the index but **absent from the handoff log**) pending resolution of the handoff discrepancy — see LEDGER entry [4].

| DC id | Title (short) | Freeze hash (sha256, 16) | Received | Intake result | Review id | Verdict | Status |
|---|---|---|---|---|---|---|---|
| DC-0001 | Isolated single-bar velocity outlier → gradual continuation | `1f1b3d399f2e9613` | 2026-07-23 | ACCEPTED | REVIEW-DC-0001-v1 | 🟡 NEEDS BETTER EVIDENCE | UNDER_REVIEW→reviewed |
| DC-0002 | HTF compression resolves with H4 bias | `9970263b17fdbcb8` | 2026-07-23 | ACCEPTED (see integrity note) | REVIEW-DC-0002-v1 | 🟢 CONTINUE INVESTIGATION | reviewed |
| DC-0003 | Scale inversion of break behaviour | `e56076c5c4fce6a2` | 2026-07-23 | ACCEPTED (see integrity note) | REVIEW-DC-0003-v1 | 🟢 CONTINUE INVESTIGATION | reviewed |
| DC-0004 | NY-session PDH sweep-reject → reversion | `4560ba15e08226a9` | 2026-07-23 | ACCEPTED (see integrity note) | REVIEW-DC-0004-v1 | 🟢 CONTINUE INVESTIGATION | reviewed |
| DC-0005 | The third test of a level differs from first two | `7c8750551b31c2e8` | 2026-07-23 | ACCEPTED | REVIEW-DC-0005-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |
| DC-0006 | Extreme-relative-volume candles fail to extend | `ef1e217fd3ff1aeb` | 2026-07-23 | ACCEPTED | REVIEW-DC-0006-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |
| DC-0007 | Equal lows swept & reclaimed same candle | `1823d33ec7394c21` | 2026-07-23 | ACCEPTED | REVIEW-DC-0007-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |
| DC-0013 | Large NY sustained expansion, no reversal (n=2 w/ add.) | `fc8991fbf2f994e7` | 2026-07-23 | ACCEPTED | REVIEW-DC-0013-v1 | 🟢 CONTINUE INVESTIGATION | reviewed |
| DC-0014 | 00:00 UTC V-reversal → 4-candle rally → reversal | `3cdc39b74e1db801` | 2026-07-23 | ACCEPTED | REVIEW-DC-0014-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |
| DC-0015 | 11-candle NY expansion (~2h45m) | `f6526ab36f303916` | 2026-07-23 | ACCEPTED | REVIEW-DC-0015-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |
| DC-0016 | Early-Asia/pre-London expansion → reversal (n=2 w/ add.) | `e1c1c4dce4455e90` | 2026-07-23 | ACCEPTED | REVIEW-DC-0016-v1 | 🟢 CONTINUE INVESTIGATION | reviewed |
| DC-0017 | NFP-scale 12:30 UTC impulse then hold (n=3 w/ 2 add.) | `dbd07f90a927b2a9` | 2026-07-23 | ACCEPTED | REVIEW-DC-0017-v1 | 🟢 CONTINUE INVESTIGATION | reviewed |
| DC-0018 | Extreme-volume fresh-high failure → sustained decline | `40ce847f27f85220` | 2026-07-23 | ACCEPTED | REVIEW-DC-0018-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |

**Batch 2 — admitted after handoff reconciliation (Alpha commit `005f837`, CEO-authorized 2026-07-23).** Intake re-verified: all 5 carry a `FROZEN / SUBMITTED` line, metadata content_hash == handoff hash for all 5, all 12 group addenda logged, admin gate CLOSED. (DC-0001 hash-reproducibility item remains open but is separate and does not affect scientific review.)

| DC id | Title (short) | Freeze hash (sha256, 16) | Received | Intake result | Review id | Verdict | Status |
|---|---|---|---|---|---|---|---|
| DC-0008 | Sustained multi-minute vs single-minute construction (n≈6 w/ 4 add.) | `ce52a96e39fcd44d` | 2026-07-23 | ACCEPTED | REVIEW-DC-0008-v1 | 🟢 CONTINUE INVESTIGATION | reviewed |
| DC-0009 | Resistance band survives 7→9 touches; full lifecycle (4 add.) | `ac7ffdec7dcd1547` | 2026-07-23 | ACCEPTED | REVIEW-DC-0009-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |
| DC-0010 | Quiet hour breaks with sustained expansion (1 add.) | `5855f9606e7070f8` | 2026-07-23 | ACCEPTED | REVIEW-DC-0010-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |
| DC-0011 | Single-minute sweep reclaim→new highs (2 add.) | `dc0607e02329bfa6` | 2026-07-23 | ACCEPTED | REVIEW-DC-0011-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |
| DC-0012 | Absorption: high volume, no displacement (1 add.) | `4a4791c183230291` | 2026-07-23 | ACCEPTED | REVIEW-DC-0012-v1 | 🟡 NEEDS BETTER EVIDENCE | reviewed |

**Portfolio intake now complete: all 18 Discovery Candidates reviewed** (batch 1: 13; batch 2: 5). No candidates held.
