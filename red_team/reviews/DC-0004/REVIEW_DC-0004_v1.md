# RED TEAM REVIEW REPORT

**Report ID:** REVIEW-DC-0004-v1
**Discovery Candidate:** DC-0004 — "New-York-Session Prior-Day-High Sweep-Reject Is Followed By Reversion"
**DC freeze hash:** `sha256:4560ba15e08226a9614097e1bd500db5a53d5095aa11ed02296876c64d665038` (current; post Library-Concept-Scan recompute)
**Submission received:** 2026-07-23 (frozen 2026-07-22)
**Reviewer(s):** Red Team
**Critique battery version:** CRITIQUE_BATTERY v1.0

## 0. STANCE
Quality control, not destruction. Good faith; fair. "Worth investigating?", not "true?" Submitted evidence only.

## 1. CANDIDATE UNDER REVIEW (as frozen)
- **Observation:** on XAUUSD H1, a first-bar sweep-reject of the prior-day high is followed by reversion **only in the NY session**; Asia/London show no reversion or the opposite sign.
- **Evidence:** matched-null p=0.021 (K6) / 0.029 (K12), CI excludes zero at K6; n=42; sign-stable across both temporal halves; NY-up is the only significant cell of six. 16,623 H1 bars, scripts cited.
- **Scope:** XAUUSD H1/daily, in-sample; holdout untouched.

## 2. CRITIQUE BATTERY v1.0
| # | Critique | Answer |
|---|---|---|
| C1 | Observation Quality | Very clear — level, event, session window, horizon and baseline all precisely specified. ✓ |
| C2 | Evidence Quality | The strongest in this batch: quantified against the NY session's own forward baseline, matched-null tested, sign-stable across halves, uniquely distinguished among 6 cells. |
| C3 | Alternative Explanation | Multiple-testing / selection is the live alternative and is *named by Alpha*: fails Bonferroni (0.021 vs 0.0083), and the cell was chosen after inspecting ~12 cells, so p is not selection-corrected. Per-half CIs both include zero. ✓ |
| C4 | Claim Discipline | Disciplined — "no causal claim"; presents statistics as descriptive, foregrounds the Bonferroni failure and the untouched holdout as the decisive test. ✓ |
| C5 | Worth Investigating | Yes: precisely specified, uniquely distinguished, temporally sign-stable, and it has a single clean decisive test already identified (reserved OOS holdout). |

## 3. VERDICT
- **Verdict:** 🟢 CONTINUE INVESTIGATION
- **Reason:** Clear, quantified, sign-stable, uniquely distinguished, with an honestly-disclosed selection/Bonferroni caveat and a pre-identified decisive OOS test. Exactly the kind of candidate that deserves the next stage. (The selection caveat means it must be treated as a hypothesis for the holdout, not a result — a matter for the validation stage, not Red Team.)

## 4. AUDIT
- Battery v1.0 | Source: candidate_v1.md, DC-0004 folder (hash above).
- **Intake integrity note:** shares the DC-0002/0003/0004 immutability-process breach (Library Concept Scan added inside the frozen file, hash recomputed). Escalated (LEDGER [4]); does not change this verdict.
- **Independence attestation:** R1–R10 held. Red Team, 2026-07-23.
