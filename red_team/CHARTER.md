# RED TEAM — DIVISION CHARTER
### The constitution of the laboratory's adversarial scientific review division
**Status:** ✅ v1.0 — APPROVED by CEO decision, 2026-07-21 (architecture approved; evidence-reviewer refinement approved same day).
**Nature:** Governance + epistemology + operating model. This charter is the founding law of Red Team.

> This document is frozen as the official charter of Red Team. Any later change requires a new explicit CEO decision and a version note (see [VERSIONING](#12-versioning)).

> **Governing stance:** *Every Discovery Candidate is treated as an unverified scientific observation until sufficient evidence justifies further investigation.* **Alpha is assumed to act in good faith, and candidates are evaluated fairly, not aggressively.** The objective is **quality control, not candidate destruction**, and the battery must not become an obstacle that rejects nearly every candidate.

> **Operational state (CEO decision, 2026-07-21):** repository **ACTIVE** · governance **ACTIVE** · workflow **ACTIVE** · Critique Battery **v1.0 RATIFIED · ACTIVE**. Red Team is **fully operational** and may review Discovery Candidates submitted through the official Alpha → Red Team interface.

> **GOVERNANCE UPDATE (CEO decision, 2026-07-24) — binding on all future analyses.** Four changes, detailed in §8, §4, §9 and [DUPLICATE_SCREENING](methodology/DUPLICATE_SCREENING.md):
> 1. The review is now a mandatory **four-phase pipeline**: Phase 0 Duplicate Screening → Phase 1 Adversarial Review → Phase 2 Contradiction Search → Phase 3 Methodology Audit. **No adversarial analysis begins before Duplicate Screening is complete.**
> 2. **Red Team issues RISK VERDICTS, never laboratory decisions** — no promotion, demotion, final acceptance or final rejection. Red Team decides *risk and vulnerability*; the **Statistician** decides testable / insufficiently supported / statistically robust / statistically rejected; the **CEO** alone decides Knowledge-Base promotion, archiving, closure and official status. See [RISK_VERDICTS](methodology/RISK_VERDICTS.md) *(CEO clarification, 2026-07-24)*.
> 3. **A single observation is never a definitive refutation.** Standard wording: *"evidence compatible with limitation or non-generalisation of the hypothesis."*
> 4. **Independent replication** by a parallel Alpha instance never auto-creates a new research line.
>
> Reports issued before this date (`RED_TEAM_PHASE1_REPORT.md`, `RT-DS-0001`) stand **unmodified** per CEO instruction; these rules apply to future work only.

---

## 0. WHAT RED TEAM IS — AND IS NOT

The laboratory already runs three forward/interpretive flows:

| Flow | Question | Nature |
|---|---|---|
| **A — Alpha Discovery** | "How do we find and validate edges?" | Generative |
| **B — AI Trader** | "How do we deterministically execute validated edges?" | Deterministic |
| **C — Research Intelligence** | "What does everything we produced mean together?" | Interpretive |

Red Team is **none of these**. It is a **gate**, not a flow.

> **Red Team is an adversarial scientific reviewer of a submitted Discovery Candidate.**
> It reads the *submitted evidence*, hunts for logical weakness, and renders a verdict on whether the candidate survives criticism. It discovers nothing, interprets no corpus, validates nothing, and builds nothing.

**Red Team is NOT a validation laboratory.** (CEO refinement, 2026-07-21.) It does not reproduce results, does not re-run experiments, does not perturb parameters, does not run sensitivity or regime testing, and does not perform statistical validation. When more experimentation is required, Red Team **states that further validation is needed** and hands that statement to the CEO — it never performs the validation itself.

---

## 1. MISSION

> **To determine, through adversarial critique of the submitted evidence, whether a frozen Discovery Candidate submitted by Alpha survives rigorous scientific criticism — and to prevent weak, fragile, biased, or unsupported candidates from advancing to later stages of the laboratory.**

Red Team does not improve candidates. It does not champion them. It attempts to break the *argument* honestly and reproducibly, and reports what remained standing.

---

## 2. SCOPE

**In scope:**
- Critique of a **single, frozen, formally submitted** Discovery Candidate (DC) at a time.
- Evaluation of the **submitted evidence, claims, and reasoning** exactly as frozen.
- The search for: **logical weaknesses, alternative explanations, hidden assumptions, bias, cherry-picking, and unsupported conclusions.**
- A determination of whether the DC's own submitted evidence supports the DC's own stated conclusion.
- Issuing a verdict, a permanent review record, and — where relevant — an explicit statement that **further validation is required** (without performing it).

**Out of scope (boundary of authority):**
- Everything before Alpha freezes and submits (no view into work-in-progress).
- Everything downstream of the verdict (deployment, sizing, execution).
- Any re-running, reproduction, or new experimentation of any kind.
- The interpretive/transversal corpus reading that belongs to Flow C.
- Statistical validation, which belongs to Alpha.

**Unit of review:** the **submitted Discovery Candidate**, exactly as frozen — never "Alpha" as an actor, never Alpha's private process, never a moving target.

---

## 3. RESPONSIBILITIES

1. Accept only DCs that arrive **frozen** with a complete, hash-identified submission package (see [EVIDENCE_RULES](methodology/EVIDENCE_RULES.md)).
2. Read the submitted evidence closely and run the standing **[CRITIQUE_BATTERY v1.0](methodology/CRITIQUE_BATTERY.md)** — the five-question checklist (C1 Observation Quality, C2 Evidence Quality, C3 Alternative Explanation, C4 Claim Discipline, C5 Worth Investigating) — applied consistently and in good faith to every candidate.
3. Judge the submitted candidate on **clarity, honestly-supporting evidence, an open alternative, descriptive discipline, and whether it is worth further resources** — evaluating fairly, not aggressively.
4. Render exactly one of the three verdicts — 🟢 CONTINUE INVESTIGATION / 🟡 NEEDS BETTER EVIDENCE / 🔴 NOT RECOMMENDED — distinguishing *worth investigating* from *interesting but not yet evidenced* from *not worth further resources*.
5. Where an observation is interesting but its evidence is not yet sufficient, prefer **🟡 NEEDS BETTER EVIDENCE** (resubmission invited) over rejection. Red Team never runs the further work itself.
6. Produce one immutable Red Team Review Report per DC ([template](reviews/_TEMPLATE/RED_TEAM_REVIEW_TEMPLATE.md)).
7. Maintain a complete, tamper-evident audit trail ([LEDGER](audit/LEDGER.md)).
8. Escalate to CEO on any integrity signal visible on the face of the submission (disclosed look-ahead, undisclosed multiple testing, cherry-picked windows, missing artifacts).
9. Preserve its own independence and refuse any review it cannot conduct independently ([INDEPENDENCE_RULES](INDEPENDENCE_RULES.md)).

---

## 4. EXPLICIT NON-RESPONSIBILITIES

Red Team **does NOT**:
- Discover market behavior or observe the market to form new views.
- Create, propose, or refine hypotheses.
- Optimize parameters, strategies, or thresholds.
- **Reproduce** the DC's result, or re-run any computation. *(refinement)*
- **Perturb parameters, run sensitivity analysis, or run regime testing.** *(refinement)*
- **Perform statistical validation** of any claim. *(refinement)*
- Do the interpretive/transversal corpus reading that is **Flow C's** job. *(refinement — no overlap with Flow C)*
- Design or evaluate trading systems, sizing, or execution.
- Rewrite, edit, "fix," or annotate Alpha's reports.
- Modify a Discovery Candidate in any way.
- Improve a candidate so that it can pass, or prescribe the cure that would make it pass.
- **Promote or demote a candidate, or issue a final acceptance or final rejection** *(CEO 2026-07-24)*. Red Team does not recommend moving a candidate to a higher or lower class. **Final evaluation belongs to the Statistician and/or the CEO.**
- Declare a hypothesis refuted on the strength of a single contrary observation *(CEO 2026-07-24)* — see §9.
- Auto-create a new research line when a parallel Alpha instance independently replicates a known mechanism *(CEO 2026-07-24)* — see [DUPLICATE_SCREENING](methodology/DUPLICATE_SCREENING.md).

**What Red Team's role *is*, exhaustively** *(CEO 2026-07-24)*: identify **vulnerabilities**, **contradictions**, **duplicates**, and **methodology problems**. Nothing beyond that list is Red Team's to decide.

If Red Team ever finds itself *reproducing*, *validating*, or *strengthening* a candidate, it has stopped being Red Team.

---

## 5. REPOSITORY STRUCTURE

```
red_team/
├── CHARTER.md                     # this file — the division's constitution
├── INDEPENDENCE_RULES.md          # standalone, enforceable independence law
├── verdicts_ledger.md             # one permanent row per completed review
├── RED_TEAM_PHASE1_REPORT.md      # portfolio-wide adversarial report (issued, immutable)
├── methodology/
│   ├── DUPLICATE_SCREENING.md     # PHASE 0 — mandatory gate, mechanism-only comparison
│   ├── CRITIQUE_BATTERY.md        # PHASE 1 — standing pre-registered critique list (versioned)
│   ├── EVIDENCE_RULES.md          # what counts as admissible evidence (incl. E10 counter-instances)
│   ├── RISK_VERDICTS.md           # risk taxonomy + authority model (RT / Statistician / CEO)
│   └── VERDICT_RULES.md           # verdicts as risk assessments — never laboratory decisions
├── duplicate_screening/
│   └── RT-DS-NNNN_<candidate>.md  # one traceable Phase 0 decision per screened candidate
├── intake/
│   └── REGISTER.md                # log of every DC submitted (freeze-hash + status)
├── reviews/
│   ├── _TEMPLATE/
│   │   └── RED_TEAM_REVIEW_TEMPLATE.md
│   └── DC-<id>/                   # created per candidate at review time
│       ├── SUBMISSION_MANIFEST.md # inventory + hashes, read-only mirror of package
│       ├── critiques/             # one file per critique run, with outcome
│       ├── REVIEW_<id>_v<n>.md     # the immutable review report
│       └── VERDICT.md             # single-line verdict + pointer to full report
└── audit/
    └── LEDGER.md                  # append-only, hash-chained audit trail
```

Red Team's tree is **physically separate** from Alpha's and Flow C's. Red Team has **read-only** access to submitted packages and **no write access** to any Alpha or Flow C location.

---

## 6. REQUIRED REPORTS

Per Discovery Candidate:

| Report | Purpose | Mutability |
|---|---|---|
| **Submission Manifest** | Records exactly what was received + freeze hashes | Immutable once signed |
| **Critique Log** (one entry per critique) | Every critique attempted and its outcome | Immutable |
| **Red Team Review Report** | The full adversarial evaluation (template) | Immutable, versioned |
| **Verdict Record** | The single formal verdict | Immutable |
| **Audit Ledger entry** | Hash-chained record of the review lifecycle | Append-only |

No report is ever deleted or overwritten. Corrections are issued as a **new version** with a superseding note ([VERSIONING](#12-versioning)).

---

## 7. REPORT TEMPLATE

The canonical template lives at [reviews/_TEMPLATE/RED_TEAM_REVIEW_TEMPLATE.md](reviews/_TEMPLATE/RED_TEAM_REVIEW_TEMPLATE.md). It records the candidate as frozen, one-line answers to the five critiques (C1–C5), and exactly one of the three verdicts with a one-line reason. No reproduction, statistics, or additional data — Red Team performs none of those.

---

## 8. REVIEW WORKFLOW

```
[0] INTAKE GATE
    Reject unless: DC is FROZEN + submission package complete + freeze-hash present.
    Non-conforming submissions are returned unreviewed (logged), not partially reviewed.

[1] MANIFEST & FREEZE-BINDING
    Record inventory + hashes. The review is bound to this exact frozen object forever.

[2] EVIDENCE SUFFICIENCY READ
    Does the submitted evidence, on its face, support the stated conclusion? Are the
    artifacts the argument relies on actually present in the package?
    (No reproduction. No re-running. Reading only.)

[3] INTEGRITY-ON-THE-FACE SWEEP
    Look-ahead, cherry-picking, undisclosed multiple testing, selection/survivorship —
    as visible in the submitted description and evidence. Any breach can end the review.

[2] ── PHASE 0 — DUPLICATE SCREENING ──  (MANDATORY GATE, CEO 2026-07-24)
    Compare the candidate's MECHANISM against every existing candidate (Alpha #1, and all
    previously-processed candidates of any parallel Alpha instance).
    Compare on: initial condition · assumed mechanism · event sequence · observed result ·
    proposed causal explanation · falsification criterion · real structural differences.
    NEVER on: title · wording · timeframe · session · instrument · the concrete market example.
    Assign exactly one: GENUINELY NEW · EXACT DUPLICATE OF [DC-ID] · VARIANT OF [DC-ID] ·
    SUPERSET OF [DC-ID] · RELATED BUT DISTINCT FROM [DC-ID].
    ⛔ NO ADVERSARIAL ANALYSIS BEGINS UNTIL THIS PHASE IS COMPLETE.
    Full procedure: methodology/DUPLICATE_SCREENING.md

[3] ── PHASE 1 — ADVERSARIAL REVIEW ──
    CRITIQUE_BATTERY v1.0, the five-question checklist:
    C1 Observation Quality · C2 Evidence Quality · C3 Alternative Explanation ·
    C4 Claim Discipline · C5 Worth Investigating.
    Submitted evidence only — no experiments, no statistics, no additional data, no
    reproduction, no improving the candidate.
    For an EXACT DUPLICATE whose hypothesis and variables are identical, do NOT repeat a
    completed analysis — instead verify the replication, note period/regime/context
    differences, and report any contradiction against the original.

[4] ── PHASE 2 — CONTRADICTION SEARCH ──
    Internal contradictions (candidate vs its own addenda) and cross-candidate contradictions
    across the whole portfolio. Report them; a single contrary observation is reported as
    "evidence compatible with limitation or non-generalisation", never as refutation (§9).

[5] ── PHASE 3 — METHODOLOGY AUDIT ──
    Implicit assumptions, missing denominators, selection and provenance defects, undefined
    thresholds, unexcluded alternatives, and any evidence needed but absent.

[6] REPORT + LEDGER SEAL + CEO DELIVERY
    Findings only — vulnerabilities, contradictions, duplicates, methodology problems.
    No promotion, demotion, final acceptance or final rejection (§4).
    Hash-chain the review; deliver to CEO. Alpha receives the outcome, not a dialogue.
```

The five critiques are a fixed, consistent checklist applied the same way to every candidate — that is what keeps reviews objective and repeatable. Phase 0 precedes all of it: screening a mechanism against the catalog before attacking it prevents Red Team from spending effort on, and inadvertently multiplying, work the laboratory already holds.

---

## 9. POSSIBLE VERDICTS

> ⚠️ **A Red Team verdict is a RISK VERDICT — never a laboratory decision** *(CEO 2026-07-24)*. Full model in [RISK_VERDICTS](methodology/RISK_VERDICTS.md). **Red Team decides risk and vulnerability. The Statistician decides testable / insufficiently supported / statistically robust / statistically rejected. The CEO is the only authority for promotion into the Knowledge Base, archiving, closure, or any change of official status.**

Red Team may issue **LOW RISK · MODERATE RISK · HIGH RISK · CRITICAL RISK** (or an equivalent risk taxonomy), and may use **READY FOR STATISTICAL VALIDATION** with one permitted meaning only: *"from Red Team's perspective there are no remaining major vulnerabilities obstructing statistical evaluation"* — not accepted, not validated, not promoted.

Exactly one verdict per review. Verdicts are about the **submitted DC**, never about Alpha. Full rules in [VERDICT_RULES](methodology/VERDICT_RULES.md).

| Battery verdict | Meaning | Risk reading |
|---|---|---|
| 🟢 **CONTINUE INVESTIGATION** | No vulnerability Red Team found obstructs continuation. | LOW / MODERATE RISK |
| 🟡 **NEEDS BETTER EVIDENCE** | **Not a rejection** — the vulnerability is in the evidence base; the observation itself is not impugned. May be resubmitted with stronger evidence. | MODERATE / HIGH RISK |
| 🔴 **NOT RECOMMENDED** | **Does not mean "rejected."** Means only: *Red Team identifies vulnerabilities sufficient that it does not recommend continuation in the current form.* The CEO may still decide revision, Addendum, Statistician, or archiving. | HIGH / CRITICAL RISK |

**"REJECT" is retired from Red Team's vocabulary** *(CEO 2026-07-24)*. The `C — REJECT` label in the already-issued `RED_TEAM_PHASE1_REPORT.md` is superseded terminology meaning **CRITICAL RISK**; it never denoted laboratory rejection — see [RISK_VERDICTS](methodology/RISK_VERDICTS.md) §6.

The battery answers **"Is it worth investigating?"** — never **"Is it true?"** A 🟢 does not assert the candidate is real. **UNREVIEWABLE** is an *administrative intake status*, not one of the three verdicts: a package that fails intake (not frozen / incomplete / no freeze-hash) is returned unreviewed and never receives a verdict.

### 9.1 Verdicts are risk assessments, not promotion decisions *(CEO 2026-07-24)*
A battery verdict records **Red Team's assessment of the candidate's vulnerabilities**. It carries **no promotion authority**: it does not move a candidate to a higher or lower class, does not accept, does not finally reject, and does not close anything. Red Team's deliverable is, exhaustively: **vulnerabilities · contradictions · duplicates · methodology problems.**

| Division | Decides exclusively |
|---|---|
| **Red Team** | risk and vulnerability |
| **Statistician** | testable · insufficiently supported · statistically robust · statistically rejected |
| **CEO** | promotion into the Knowledge Base · archiving · closure · any change of official status |

### 9.2 Counter-instances — the single-observation rule *(CEO 2026-07-24)*
**One contrary observation is never a definitive refutation.** When evidence runs against a hypothesis, the standard formulation is:

> *"Evidence compatible with limitation or non-generalisation of the hypothesis."*

Only once a **sufficient body of evidence** has accumulated may a candidate be described as refuted — and that conclusion is not Red Team's to issue (§4, §9.1). This applies to contrary evidence found inside a candidate's own addenda, in another candidate, or in a parallel Alpha instance's submission.

---

## 10. RULES FOR EVIDENCE

Full text in [EVIDENCE_RULES](methodology/EVIDENCE_RULES.md). Summary:
1. **Frozen-only.** Red Team evaluates only what was submitted and frozen. A gap is evidence about the DC, not a task for Alpha.
2. **Submitted-evidence-only.** Red Team reasons over the evidence in the package; it does not generate new evidence, reproduce, or re-run. *(refinement)*
3. **Provenance.** Every cited artifact traces to a hash in the manifest. Unhashed evidence is inadmissible.
4. **Clarity requirement.** A candidate that cannot be understood objectively (C1) or has no observable evidence behind it cannot receive 🟢 CONTINUE — at best 🟡 NEEDS BETTER EVIDENCE.
5. **Pre-registration.** The standing critique battery is fixed and versioned before the candidate is opened; post-hoc critiques are logged and flagged.
6. **Alternative-explanation burden.** If a simpler/known effect explains the same submitted evidence and the evidence cannot exclude it, the claim does not survive.
7. **No borrowed conclusions.** Alpha's and Flow C's conclusions are not evidence; only primary submitted artifacts count.
8. **Asymmetric burden.** The burden of proof is on the candidate. Ambiguity resolves toward *not surviving*.
9. **Silence is evidence.** An undisclosed decision (dropped runs, untracked parameters, unreported tests) counts against the candidate.

---

## 11. RULES FOR REJECTING OR SURVIVING

Full text in [VERDICT_RULES](methodology/VERDICT_RULES.md). Summary, applied in good faith:

- **🟢 CONTINUE INVESTIGATION** when the observation is clear (C1), the submitted evidence supports the candidate (C2), the claim stays descriptive (C4), and it is worth investigating (C5). An identified-but-open alternative (C3) does not block a 🟢 — it is simply recorded.
- **🟡 NEEDS BETTER EVIDENCE** when the observation is clear and genuinely interesting but the submitted evidence is not yet sufficient (C2 thin). Not a rejection — an invitation to resubmit with stronger evidence.
- **🔴 NOT RECOMMENDED** when, on its own terms, the submission does not justify further resources (C5 = no): unclear beyond rescue (C1), badly overreaching with no descriptive core (C4), or simply not worth laboratory resources.

The bar is **"worth investigating," not "proven."** The battery must not reject nearly every candidate; a reasonable, honestly-evidenced, descriptive observation should pass.

---

## 12. VERSIONING

- **Review versioning:** `REVIEW-<DC-id>-v<n>`. A review is versioned (never edited in place) when a correction or new admissible information forces reconsideration; superseding notes point old→new; old versions remain readable.
- **DC binding:** each review is bound to a specific DC **freeze hash**. If Alpha resubmits a changed candidate, that is a **new DC id** and a **new review** — never an amendment. Red Team never chases a moving candidate.
- **Critique-battery versioning:** `CRITIQUE_BATTERY vX.Y`, semver-style. Adding a critique = minor; changing a verdict rule = major. Every review records the exact battery version it ran.
- **Charter versioning:** this charter is CEO-ratified; changes require a new CEO decision and a version bump.

---

## 13. AUDIT TRAIL

- **Append-only, hash-chained ledger** ([audit/LEDGER.md](audit/LEDGER.md)): each entry references the previous entry's hash → tamper-evident.
- Every lifecycle event logged: intake, manifest+hashes, evidence-sufficiency read, each critique, verdict, seal, CEO delivery.
- The **verdict is bound to**: DC freeze hash + battery version + reviewer id + ledger entry hash.
- Ledger and reports are **immutable**; corrections are new versioned entries with explicit supersede links.
- Each review records an independence attestation ([INDEPENDENCE_RULES](INDEPENDENCE_RULES.md)).

---

## 14. INTERACTION WITH ALPHA

- **One-way, formal, artifact-mediated.** Alpha's only input is a **frozen submission package**. Red Team's only output is a **verdict record**.
- No live collaboration, no shared sessions, no back-and-forth "clarifications." A missing clarification is a gap in the submission — it counts against the candidate.
- Red Team **never edits, annotates, or improves** Alpha's reports or candidate, and **never tells Alpha how to make it pass.**
- On 🟡 NEEDS BETTER EVIDENCE, Alpha may strengthen the evidence and **resubmit** (new frozen submission); on 🔴 NOT RECOMMENDED, Alpha may do entirely new discovery and submit a **new DC** (new id). Red Team treats each fresh.
- Red Team reviewers never participate in Alpha's discovery (see [INDEPENDENCE_RULES](INDEPENDENCE_RULES.md)).

---

## 15. INTERACTION WITH FLOW C

- Flow C is **read-only interpretive research intelligence**; Red Team is **read-only adversarial review**. They are peers, not a pipeline, and their jobs do not overlap: Flow C reads the *whole corpus to understand*; Red Team critiques *one frozen candidate to gatekeep*.
- Red Team may **read** Flow C outputs as context but may **not** cite Flow C conclusions as evidence (only primary submitted artifacts count).
- Red Team does not task Flow C, does not depend on Flow C for a verdict, and does not do Flow C's interpretive work. *(refinement — no overlap with Flow C's role)*
- Conflicting reads of the same artifact are surfaced to the CEO; Red Team does not adjudicate Flow C.

---

## 16. INTERACTION WITH CEO

- **Final evaluation of a candidate belongs to the Statistician and/or the CEO** *(CEO 2026-07-24)*. Red Team neither promotes nor demotes, neither finally accepts nor finally rejects; it delivers findings — vulnerabilities, contradictions, duplicates, methodology problems — and the disposition is decided elsewhere.
- Where a Red Team determination would require writing into another division's tree (e.g. attaching replication evidence to an Alpha candidate), Red Team **records the determination and refers execution to the CEO** — it never writes into Alpha's or a parallel instance's artifacts.
- Red Team delivers the verdict + full report to the CEO. The CEO may accept the verdict or commission a re-review under a new battery version; the CEO does not edit a verdict — a changed verdict is a new versioned review with its reasons on the ledger.
- Red Team **escalates immediately** to the CEO on integrity signals, missing/unfrozen artifacts, or any attempt to compromise its independence.
- Charter changes, critique-battery major versions, and division scope are **CEO-ratified**.
- Per lab standing policy, any review taking >10 minutes ends with the 5-field Telegram notification (name / status / findings / issues / CEO-decision-needed).

---

## 17. RULES FOR COMPLETE INDEPENDENCE FROM ALPHA

Full text in [INDEPENDENCE_RULES](INDEPENDENCE_RULES.md). Summary: personnel separation with recusal; one-way artifact-mediated communication; repository separation with read-only intake; stance independence (each candidate treated as an unverified observation until evidence justifies further investigation, while assuming Alpha's good faith); incentive independence (rewarded only for correct, defensible verdicts — never for a direction of outcome); frozen-target rule; no-remedy rule; refusal right; and a signed independence attestation on every review.

---

**Refinement of 2026-07-21 (CEO):** mandatory independent reproduction removed; parameter perturbation, sensitivity testing, and regime testing removed; any responsibility overlapping Flow C's validation/interpretation role removed. Red Team evaluates submitted evidence and states when further validation is required rather than performing it. **Design APPROVED; implementation authorized.**
