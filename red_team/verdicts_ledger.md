# RED TEAM — VERDICTS LEDGER
### One permanent row per completed review — the public record of what survived and what did not
**Parent:** [CHARTER.md](../CHARTER.md) §6, §13. Append-only. A superseded verdict keeps its row; the new version is added below with a supersede pointer.

| Review id | DC id | Freeze hash (16) | Battery | Verdict | Note | Sealed | Superseded by |
|---|---|---|---|---|---|---|---|
| REVIEW-DC-0001-v1 | DC-0001 | `1f1b3d399f2e9613` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | n=2 visual, no base rate | 2026-07-23 | — |
| REVIEW-DC-0002-v1 | DC-0002 | `9970263b17fdbcb8` | v1.0 | 🟢 CONTINUE INVESTIGATION | pre-registered C4; K05 confound self-named | 2026-07-23 | — |
| REVIEW-DC-0003-v1 | DC-0003 | `e56076c5c4fce6a2` | v1.0 | 🟢 CONTINUE INVESTIGATION | falsifiable re-test of OBS-0017 null | 2026-07-23 | — |
| REVIEW-DC-0004-v1 | DC-0004 | `4560ba15e08226a9` | v1.0 | 🟢 CONTINUE INVESTIGATION | matched-null, sign-stable; Bonferroni/selection flagged; holdout reserved | 2026-07-23 | — |
| REVIEW-DC-0005-v1 | DC-0005 | `7c8750551b31c2e8` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | n=2, folk pattern, no base rate | 2026-07-23 | — |
| REVIEW-DC-0006-v1 | DC-0006 | `ef1e217fd3ff1aeb` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | self-contradicting; scale-confounded | 2026-07-23 | — |
| REVIEW-DC-0007-v1 | DC-0007 | `1823d33ec7394c21` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | n=1 anecdote | 2026-07-23 | — |
| REVIEW-DC-0013-v1 | DC-0013 | `fc8991fbf2f994e7` | v1.0 | 🟢 CONTINUE INVESTIGATION | n=2 (addendum); no-reversal ending recurs | 2026-07-23 | — |
| REVIEW-DC-0014-v1 | DC-0014 | `3cdc39b74e1db801` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | compound shape at n=1 | 2026-07-23 | — |
| REVIEW-DC-0015-v1 | DC-0015 | `f6526ab36f303916` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | distinguishing feature is a sample-extremum | 2026-07-23 | — |
| REVIEW-DC-0016-v1 | DC-0016 | `e1c1c4dce4455e90` | v1.0 | 🟢 CONTINUE INVESTIGATION | n=2 same-hour; ending shape recurs | 2026-07-23 | — |
| REVIEW-DC-0017-v1 | DC-0017 | `dbd07f90a927b2a9` | v1.0 | 🟢 CONTINUE INVESTIGATION | continue as NARROWED — resolution-diversity question, not "hold" (own Addendum B contradicts headline) | 2026-07-23 | — |
| REVIEW-DC-0018-v1 | DC-0018 | `40ce847f27f85220` | v1.0 | 🟡 NEEDS BETTER EVIDENCE | 4-part compound at n=1; sweep-vs-rejection unresolved | 2026-07-23 | — |

**Batch tally (2026-07-23):** 🟢 6 · 🟡 7 · 🔴 0. (🟡 is not a rejection.) 5 further candidates (DC-0008…0012) held at intake pending handoff reconciliation.

---
**Verdict legend:** 🟢 CONTINUE INVESTIGATION · 🟡 NEEDS BETTER EVIDENCE · 🔴 NOT RECOMMENDED — defined in [methodology/VERDICT_RULES.md](methodology/VERDICT_RULES.md). (UNREVIEWABLE is an intake status, not a verdict.)
