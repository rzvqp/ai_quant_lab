# RED TEAM REVIEW REPORT

**Report ID:** REVIEW-DC-0008-v1
**Discovery Candidate:** DC-0008 — "A Large M15 Candle Built From Sustained Multi-Minute Volume, Not Single-Minute Concentration"
**DC freeze hash:** `sha256:ce52a96e39fcd44da03f9549c2ddfd6da63eadefd7edd24b01c205b31594e130`
**Submission received:** 2026-07-23 (frozen 2026-07-22; handoff reconciled at commit 005f837) — includes Addenda A–D
**Reviewer(s):** Red Team | **Battery:** CRITIQUE_BATTERY v1.0

## 0. STANCE
Quality control, not destruction. Good faith; fair. "Worth investigating?", not "true?" Submitted evidence only.

## 1. CANDIDATE UNDER REVIEW (as frozen)
- **Observation:** a large M15 candle can be built two opposite ways — sustained multi-minute participation vs a single dominant minute — distinguishable only on M1/M5; measurable as (largest M1/M5 volume share) ÷ (M15 total) and whether volume returns to baseline before close.
- **Evidence:** original n=2 (one of each type); Addenda A–D add four more 12:30 UTC instances that systematically probe the timing sub-hypothesis (A: sustained, no news slot; B/C: weekday concentration; D: both Fridays sustained → day-of-week, not NFP-specific).

## 2. CRITIQUE BATTERY v1.0
| # | Critique | Answer |
|---|---|---|
| C1 | Observation Quality | Excellent — the two constructions are precisely defined and reduced to a countable ratio; the clearest, most operational observation in the whole portfolio. ✓ |
| C2 | Evidence Quality | Strong for a Discovery Candidate: the *construction distinction* is instantiated ~6× across the addenda, both types repeatedly seen. |
| C3 | Alternative Explanation | The timing/news alternative is *actively tested and weakened by Alpha's own addenda* (A shows the construction without a news slot; D reframes NFP→day-of-week). Exemplary self-examination. ✓ |
| C4 | Claim Discipline | Disciplined — the news association is offered "not a causal claim" and then walked back by the evidence; no over-reach. ✓ |
| C5 | Worth Investigating | Yes: a crisp, countable definition with a clear downstream question (do the two constructions differ in aftermath), and multiple instances already in hand. |

## 3. VERDICT
- **Verdict:** 🟢 CONTINUE INVESTIGATION
- **Reason:** The most foundational and best-operationalised candidate here — a measurable construction distinction with ~6 instances and a self-critiqued sub-hypothesis. Deserves the downstream measurement. (Note only: DC-0008 is the root construction that DC-0010/0011 and the DC-0013…0018 family reference; consolidation is a later-stage decision, not Red Team's — no structural change made.)

## 4. AUDIT
- Battery v1.0 | Source: candidate_v1.md + addendum_2026-07-22_a..d.md, DC-0008 folder (hash above). Intake: FROZEN/SUBMITTED present, metadata==handoff hash, all 4 addenda logged (commit 005f837).
- **Independence attestation:** R1–R10 held. Red Team, 2026-07-23.
