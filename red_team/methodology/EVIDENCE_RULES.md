# RED TEAM — EVIDENCE RULES
### What Red Team may treat as admissible evidence, and how
**Status:** ✅ v1.0 — APPROVED by CEO decision, 2026-07-21.
**Parent:** [CHARTER.md](../CHARTER.md) §10.

> Red Team is an evidence reviewer, not an experimenter. These rules define what it may reason over and what it must refuse.

---

## E1 — Frozen-only
Red Team evaluates only what was submitted and frozen, bound by the submission's freeze-hash. A gap in the package is **evidence about the candidate**, not a task to send back to Alpha.

## E2 — Submitted-evidence-only *(refinement)*
Red Team reasons over the evidence contained in the package. It does **not** generate new evidence, reproduce results, re-run computations, perturb parameters, or run sensitivity/regime tests. If the observation is interesting but the submitted evidence is not yet sufficient, the verdict is **🟡 NEEDS BETTER EVIDENCE** (resubmission invited) — Red Team never runs the further work itself.

## E3 — Provenance
Every artifact a critique relies on must trace to an entry (with hash) in the Submission Manifest. Evidence that cannot be pinned to a hashed artifact in the package is **inadmissible**.

## E4 — Checkability requirement
A candidate with no observable evidence behind it, or one stated so it could never be checked, cannot receive **🟢 CONTINUE** on the submission alone — at best **🟡 NEEDS BETTER EVIDENCE.**

## E5 — Pre-registration
The standing [CRITIQUE_BATTERY](CRITIQUE_BATTERY.md) is applied at its frozen version. Any critique invented after opening the candidate is logged as **post-hoc** and flagged, so its weight is transparent.

## E6 — Alternative-explanation burden
If a simpler or already-known effect explains the same submitted evidence, and the submitted evidence does not exclude it, the claim does **not** survive. The burden of exclusion is on the candidate's evidence, not on Red Team to run a test.

## E7 — No borrowed conclusions
Conclusions asserted by Alpha or by Flow C are **not** evidence. Only primary submitted artifacts count. Red Team may read Flow C context but may not cite its conclusions to support or reject a verdict.

## E8 — Asymmetric burden
The burden of proof is on the candidate. Where the submitted evidence is ambiguous, the ambiguity resolves toward **not surviving**.

## E9 — Silence is evidence
An undisclosed decision that bears on the result — dropped runs, untracked parameters, unreported tests, an unexplained window boundary — counts **against** the candidate. Non-disclosure is itself a finding.
