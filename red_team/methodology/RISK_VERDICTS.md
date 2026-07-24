# RED TEAM — RISK VERDICTS & AUTHORITY MODEL
### What a Red Team verdict is, what it is not, and who decides what
**Status:** ✅ v1.0 — OFFICIAL by CEO decision, 2026-07-24. Binding on all future analyses.
**Parent:** [CHARTER.md](../CHARTER.md) §9. Resolves the open question raised in LEDGER `[8]`.

> **A Red Team verdict is a RISK VERDICT. It is not a laboratory decision.**
> The two are different things and must never be read as the same.

---

## 1. The authority model

| Division | Decides exclusively |
|---|---|
| **RED TEAM** | **Risk and vulnerability.** How exposed is this candidate — what could break it, what contradicts it, what is duplicated, what is methodologically unsound. |
| **STATISTICIAN** | Whether a candidate is **testable · insufficiently supported · statistically robust · statistically rejected.** |
| **CEO** | **The only authority** for promotion into the Knowledge Base, archiving, closure, and any change of official status. |

Red Team verdicts therefore **never** mean:
- laboratory acceptance;
- laboratory rejection;
- promotion into the Knowledge Base;
- final classification.

They mean exactly one thing: **Red Team's assessment of the candidate's vulnerabilities.**

---

## 2. The official risk taxonomy

Red Team may issue:

| Verdict | Meaning |
|---|---|
| **LOW RISK** | Few or minor vulnerabilities; nothing Red Team found that would obstruct downstream evaluation. |
| **MODERATE RISK** | Real vulnerabilities present; they constrain how far the evidence can be taken but do not undermine the submission's core. |
| **HIGH RISK** | Serious vulnerabilities — an unexcluded alternative, a load-bearing undefined term, a confound that could account for the result, or a missing denominator. |
| **CRITICAL RISK** | Vulnerabilities severe enough that Red Team does not recommend continuation **in the current form** — e.g. the submission's own evidence runs against its stated claim, or its principal evidence rests on an unsafe provenance. |

Any equivalent risk taxonomy is permitted, provided it expresses **vulnerability**, not disposition.

## 3. `READY FOR STATISTICAL VALIDATION`

This phrase remains available to Red Team, with **one permitted meaning only**:

> *"From Red Team's perspective there are no remaining major vulnerabilities that obstruct statistical evaluation."*

It does **NOT** mean accepted. It does **NOT** mean validated. It does **NOT** mean promoted. It is a statement about the **absence of blocking vulnerabilities**, nothing more — the decision to test, and the outcome of testing, belong to the Statistician.

## 4. `NOT RECOMMENDED` — restated

The Critique Battery verdict **NOT RECOMMENDED** no longer carries, and never again carries, the meaning *"rejected."* Its sole meaning is:

> *"Red Team identifies vulnerabilities sufficient that it does not recommend continuation in the current form."*

Following such a verdict the CEO may still decide on **revision · Addendum · referral to the Statistician · archiving.** Red Team's verdict closes nothing.

---

## 5. Mapping the existing instruments

The Critique Battery v1.0 verdicts remain in force and are read as risk statements:

| Battery verdict | Risk reading |
|---|---|
| 🟢 **CONTINUE INVESTIGATION** | LOW / MODERATE RISK — no vulnerability Red Team found obstructs continuation. |
| 🟡 **NEEDS BETTER EVIDENCE** | MODERATE / HIGH RISK — the vulnerability lies in the evidence base; the observation itself is not impugned. |
| 🔴 **NOT RECOMMENDED** | HIGH / CRITICAL RISK — not a rejection; see §4. |

## 6. How to read the already-issued Phase 1 report *(important)*

`RED_TEAM_PHASE1_REPORT.md` was issued before this clarification and is **preserved unmodified** by CEO instruction. Its `A / B / C` labels must be read as **risk verdicts**, never as laboratory decisions:

| Phase 1 label as written | Correct reading under this document |
|---|---|
| **A — READY FOR STATISTICAL VALIDATION** | Red Team found no major vulnerability obstructing statistical evaluation (**LOW RISK**). Not acceptance, not validation, not promotion. |
| **B — NEEDS MORE EVIDENCE** | **MODERATE / HIGH RISK** — vulnerabilities in the evidence base. |
| **C — REJECT** | **CRITICAL RISK.** ⚠️ The word "REJECT" in that report is superseded terminology. It never meant, and must not be read as, laboratory rejection. It means: *Red Team identifies vulnerabilities sufficient that it does not recommend continuation in the current form.* The four candidates so labelled (DC-0006, DC-0010, DC-0015, DC-0017) remain fully open to CEO decision — revision, Addendum, Statistician, or archiving. |

**"REJECT" is retired from Red Team's vocabulary.** Future reports use the risk taxonomy in §2.

---

## 7. Standing constraints (unchanged)

- Red Team does not promote, demote, finally accept or finally reject ([CHARTER](../CHARTER.md) §4).
- A single counter-instance is never a refutation — *"evidence compatible with limitation or non-generalisation of the hypothesis"* ([EVIDENCE_RULES](EVIDENCE_RULES.md) E10).
- Phase 0 [Duplicate Screening](DUPLICATE_SCREENING.md) precedes all adversarial analysis.
- Red Team's deliverable is, exhaustively: **vulnerabilities · contradictions · duplicates · methodology problems.**
