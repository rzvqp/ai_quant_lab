# RED TEAM — VERDICT RULES
### The three verdicts and how the Critique Battery reaches one
**Status:** ✅ v1.0 — RATIFIED by CEO decision, 2026-07-21 (aligned to CRITIQUE_BATTERY v1.0).
**Parent:** [CHARTER.md](../CHARTER.md) §9, §11. See [CRITIQUE_BATTERY](CRITIQUE_BATTERY.md).

> Exactly one verdict per review. Every verdict is about the **submitted Discovery Candidate**, never about Alpha. The objective is **quality control, not candidate destruction** — assume Alpha acts in good faith and evaluate fairly.

> ⚠️ **BINDING CONSTRAINT (CEO 2026-07-24).** A verdict is a **finding about the evidential state of the submission — not a promotion decision.** Red Team does **not** promote, demote, finally accept or finally reject a candidate. **Final evaluation belongs to the Statistician and/or the CEO.** Read every verdict below in that light: 🟢 does not promote, 🔴 does not finally reject. Red Team's deliverable is vulnerabilities, contradictions, duplicates and methodology problems.
> Also binding: a **single counter-instance is never a refutation** — use *"evidence compatible with limitation or non-generalisation of the hypothesis"* ([EVIDENCE_RULES](EVIDENCE_RULES.md) E10).
> **Phase 0 first:** no verdict is reached before [DUPLICATE_SCREENING](DUPLICATE_SCREENING.md) is complete.

---

## The three verdicts

| Verdict | Meaning | Resource effect |
|---|---|---|
| 🟢 **CONTINUE INVESTIGATION** | The Discovery Candidate deserves further investigation. | Advances (CEO decides next step) |
| 🟡 **NEEDS BETTER EVIDENCE** | Interesting observation; current evidence is insufficient. May be resubmitted later. | Held; resubmission invited |
| 🔴 **NOT RECOMMENDED** | The current submission does not justify further laboratory resources. | Does not advance |

The battery answers **"Is it worth investigating?"** — never **"Is it true?"** A 🟢 does not assert the candidate is real; it asserts the submission is clear, honestly evidenced, disciplined, and worth the laboratory's resources.

> **🟡 NEEDS BETTER EVIDENCE is not a rejection.** It simply indicates that the current submission does not yet justify additional laboratory resources. The observation may be genuinely interesting; the invitation to resubmit with stronger evidence stands.

---

## Reaching the verdict from the five critiques

Answer C1–C5 (one line each), then choose the single verdict:

- **🟢 CONTINUE INVESTIGATION** when C1 is clear, C2's submitted evidence supports the candidate, C4 stays descriptive, and C5 = yes. An identified-but-open C3 alternative does **not** block a 🟢 — it is simply recorded.
- **🟡 NEEDS BETTER EVIDENCE** when the observation is clear and genuinely interesting (C1 ok, C5 leans yes) but C2 is insufficient — the submitted evidence does not yet support the candidate. This is not a rejection; it is an invitation to resubmit with stronger evidence.
- **🔴 NOT RECOMMENDED** when C5 = no: on its own terms the submission does not justify further resources — e.g. C1 unclear beyond rescue, or C4 overreaches badly with no descriptive core worth keeping, or the observation is simply not worth laboratory resources.

Guidance, not a rigid truth table. The battery is deliberately lightweight; the reviewer exercises fair judgment and records a one-line reason for the chosen verdict.

---

## Administrative status (not a review verdict)
**UNREVIEWABLE** is an **intake status, not one of the three verdicts.** A package that fails the administrative intake gate (not frozen / incomplete / no freeze-hash) is returned unreviewed and never receives a battery verdict. Only submissions that pass intake receive one of the three verdicts above.

---

## What a verdict is bound to
Every verdict records: DC freeze-hash + `CRITIQUE_BATTERY v1.0` + reviewer id + ledger entry hash, and an independence attestation ([INDEPENDENCE_RULES](../INDEPENDENCE_RULES.md)). Verdicts are immutable; a corrected verdict is a new versioned review that supersedes by reference — the original row is never deleted.
