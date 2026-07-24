# RED TEAM — DUPLICATE SCREENING (PHASE 0)
### Mandatory reconciliation gate before any adversarial analysis
**Status:** ✅ v1.0 — OFFICIAL by CEO decision, 2026-07-24. Binding on all future candidates.
**Parent:** [CHARTER.md](../CHARTER.md) §8 (pipeline), §4 (non-responsibilities).

> The laboratory now runs more than one independent Alpha instance. Parallel instances do **not** consult each other's catalogs before creating candidates, and it is **permitted** for one instance to discover a mechanism another has already found. Phase 0 exists so that the same mechanism does not silently become two research lines.

> ⛔ **NO ADVERSARIAL ANALYSIS BEGINS BEFORE PHASE 0 IS COMPLETE.**

---

## 1. What is compared

Comparison is **on mechanism, and only on mechanism.** Evaluate all seven:

1. **Initial condition** — the state of the market before the event.
2. **Assumed mechanism** — what is proposed to be happening.
3. **Event sequence** — the ordered phases of the event.
4. **Observed result** — what the sequence produced.
5. **Proposed causal explanation** — the offered "why", if any.
6. **Falsification criterion** — what the candidate says would prove it wrong.
7. **Real structural differences** — anything genuinely load-bearing that separates the two.

## 2. What must NOT drive the decision

A candidate is **never** classed as a duplicate merely because it shares:

- the title or the wording;
- the timeframe;
- the instrument;
- the session or clock hour;
- the direction;
- the sweep type or event type;
- the concrete market example.

> **A duplicate exists only if the core of the mechanism is the same.** Superficial similarity of context, vocabulary or geometry is not evidence of duplication, and must not be used to dismiss a candidate.

## 3. Classifications (official, fixed set)

| Class | Definition | Consequence |
|---|---|---|
| **GENUINELY NEW** | The mechanism does not exist in the current catalog. | Proceeds to Phase 1 adversarial review as normal. |
| **EXACT DUPLICATE OF [DC-ID]** | The mechanism is substantially identical to an existing candidate. | **No new research line.** Mark as **INDEPENDENT REPLICATION OF [DC-ID]**; preserve the evidence attached to the original candidate. |
| **VARIANT OF [DC-ID]** | The mechanism's core already exists, but a distinct condition, regime, sequence or result has been identified. | Red Team determines — on the *real mechanistic difference* — whether it becomes an **Addendum** to the original or a **separate candidate**. |
| **SUPERSET OF [DC-ID]** | The candidate contains an existing candidate's mechanism but proposes a more general explanation. | **Do not automatically replace the existing candidate.** Report the relation and refer the decision to the CEO. |
| **RELATED BUT DISTINCT FROM [DC-ID]** | Similar context or behaviour, but the proposed mechanism differs. | Proceeds separately. |

A candidate may carry one **primary** classification plus secondary relations to other candidates; state each explicitly.

## 4. Independent replication *(CEO 2026-07-24)*

When a parallel Alpha instance independently reproduces a mechanism already discovered elsewhere:

- **No new research line is created automatically.**
- Mark it **INDEPENDENT REPLICATION OF [DC-ID]**.
- **Attach the evidence to the original candidate, or recommend an Addendum**, after the mechanistic analysis — not before it.
- **These replications are valuable scientific evidence and must be preserved.** They are never discarded as "redundant."

Assess whether the replication is *genuine* by recording independence across: observer/instance · in-replay date · price regime · session context · data split. Record explicitly whether the replication **contradicts** the original, and if so apply the single-observation rule (§6).

## 5. Handling an EXACT DUPLICATE

Do **not** repeat an already-completed analysis when the hypothesis and variables are identical. Instead:

1. verify the new evidence is a real independent replication;
2. note the differences in period, regime and context;
3. attach the evidence to the original candidate;
4. report any contradiction against the original.

## 6. Counter-instances — single-observation rule *(CEO 2026-07-24)*

A single contrary observation is **never** presented as a definitive refutation. Use:

> *"Evidence compatible with limitation or non-generalisation of the hypothesis."*

A candidate may be described as refuted only after a **sufficient body of evidence** has accumulated — and that conclusion is not Red Team's to issue ([CHARTER](../CHARTER.md) §4, §9.1).

## 7. Boundaries

- Red Team does **not** modify Alpha #1's or any parallel instance's artifacts. Where a determination requires writing into another division's tree (e.g. attaching an addendum), Red Team **records the determination and refers execution to the CEO**.
- Red Team does **not** promote, demote, finally accept or finally reject ([CHARTER](../CHARTER.md) §4). Phase 0 produces a *relation*, not a disposition of the candidate's scientific worth.
- Every screening produces a **separate, traceable Red Team decision document** under `duplicate_screening/`, id `RT-DS-NNNN`.

## 8. Required report opening

Every Red Team report on a candidate from a parallel Alpha instance **must begin** with:

```
DUPLICATE SCREENING RESULT:
  <GENUINELY NEW | EXACT DUPLICATE OF [DC-ID] | VARIANT OF [DC-ID]
   | SUPERSET OF [DC-ID] | RELATED BUT DISTINCT FROM [DC-ID]>
```

Only after this classification does adversarial analysis begin, **if still required**.

---

**Precedent:** [`duplicate_screening/RT-DS-0001_AP2-DC-0001.md`](../duplicate_screening/RT-DS-0001_AP2-DC-0001.md) — first application (VARIANT OF DC-0018), CEO-accepted 2026-07-24 and preserved unmodified. Note that RT-DS-0001 predates §6 and the §4 non-promotion rule; its wording is not the template for future reports on those two points.
