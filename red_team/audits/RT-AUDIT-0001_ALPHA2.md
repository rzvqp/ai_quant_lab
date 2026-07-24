# RED TEAM — RESEARCH AUDIT #1 (ALPHA PARALLEL INSTANCE #2)
### Audit of the research *process*, first observation period
**ID:** RT-AUDIT-0001 · **Date:** 2026-07-24 · **Auditor:** Red Team · **Mandate:** CEO — Red Team Research Audit #1

**Sources (read-only, Alpha #2 exclusively):** `SESSION_STATE_ALPHA2.md` (624 lines) · `OBSERVATION_REGISTRY_ALPHA2.md` (10 entries + 12 appended instance-notes) · `DISCOVERY_INDEX_ALPHA2.md` · `HANDOFF_LOG_ALPHA2.md` (6 lines) · `ADDENDUM_INDEX_ALPHA2.md` (4 entries) · `AP2-DC-0001_v1.md` · addenda A–D · `DISCOVERY_CANDIDATE_TEMPLATE_ALPHA2.md`.
**No Alpha #1 information used. No external market knowledge used. Nothing assumed beyond what the artifacts state.**
**Nothing modified.** No artifact altered, no addendum or candidate created, no Knowledge Base touched, no Statistician contacted, no promotion recommended, no official methodology changed.

> **Standing constraints applied.** This is a **risk and vulnerability** assessment, not a laboratory decision ([RISK_VERDICTS](../methodology/RISK_VERDICTS.md)). Where evidence runs against a hypothesis it is reported as *"evidence compatible with limitation or non-generalisation"*, never as refutation ([EVIDENCE_RULES](../methodology/EVIDENCE_RULES.md) E10).

---

## 1. EXECUTIVE SUMMARY

I was asked to try to demonstrate that Alpha #2's process is defective. **It partly is — but not where one would expect, and not through carelessness.**

The process is unusually *honest*. Alpha #2 self-reported every incident that could have been concealed: it edited a frozen document and turned itself in; it discovered its own checkpoint labels had drifted a day and corrected them; it documented a replay failure that silently moved it to the wrong date; it flagged its own filename-collision risk. It repeatedly declined to promote shapes it had seen up to six times, citing a conservative standard. It logged contrast cases that cut against its own candidate. Process discipline and disclosure are genuinely strong, and most attempts to break the process on those grounds failed.

**The defect is structural and sits in one place: how a hypothesis was promoted, and how its confidence then escalated.**

- **AP2-DC-0001 was promoted to Discovery Candidate at n=1.** Every shape that afterwards recurred *more* — sweep-reclaim-extend (**6 instances**), sustained multi-hour decline (**4**), 14:00 UTC breakout-holds (**2**), 12:30 UTC breakout-holds (**2**) — was held back, explicitly "per the conservative standard." The conservative standard was applied to everything except the one thing that got promoted first.
- Because only the promoted hypothesis has an addendum channel, all subsequent evidence accumulation flowed to it (4 addenda), while competitors accumulated as footnotes appended inside other registry entries.
- Addenda B, C and D each assert **"zero contradicting instances"** and escalate confidence **Medium → High**. That claim is **true by construction**: the hypothesis is defined as *"a breakout that fails"*, so an instance where a breakout does not fail cannot contradict it. The hypothesis selects on its own outcome, and therefore cannot currently produce a contradicting instance. A confidence figure derived from "zero contradictions" of an unfalsifiable-as-stated claim carries no information.
- The frozen candidate still reads **Confidence: Medium**; the addenda read **High**. Two live artifacts state different confidence with no precedence rule.

Two environmental facts limit everything this instance produced, both disclosed by Alpha #2 itself: **no M5/M1 was ever examined** (a replay hazard made timeframe switching unsafe), so the stated methodology's core investigative step was never executed once in this period; and the **broker-feed label toggles between two brokers** while essentially every observation rests on volume-versus-baseline ratios.

**Overall Research Quality Score: 64 / 100.**
**Verdict: CONTINUE WITH RECOMMENDED IMPROVEMENTS.**

---

## 2. FINDINGS

### F1 — Promotion asymmetry *(central finding)*
| Shape | Instances by end of period | Promoted? |
|---|---|---|
| AP2-DC-0001 failed-breakout-overshoots | 1 at promotion (5 now) | **YES, at n=1** |
| Sweep-reclaim-extend | **6** (08-02, 08-05, 08-09, 08-29, 09-03, 09-10) | No |
| Sustained multi-hour decline | **4** (08-05, 08-22, 08-30, 09-03) | No |
| 14:00 UTC sharp breakout, net holds | **2** (08-23, 09-04) | No |
| 12:30 UTC breakout **holds** | **2** (08-16, 09-12) | No |

The registry states the standard repeatedly: *"still not promoted to a DC per the conservative standard"*, *"if this shape keeps recurring across different session contexts, it may eventually warrant promotion."* By that standard the 6-instance family qualified long ago. The one candidate that exists is the one that had the least evidence when the decision was made.

### F2 — "Zero contradicting instances" is true by construction
Addendum B: *"no contradicting instance yet observed"*; C: *"Four instances now, zero contradicting instances"*; D: *"Five instances now, zero contradicting instances."*

Meanwhile the same instance's registry records, **at the same 12:30 UTC slot**: two breakouts that HOLD (08-16; 09-12, to a fresh period high), two sweep-reclaim-extends (08-29, 09-10), one CPI-day decline (09-11), one sustained decline (08-30). These are filed as *"contrasting cases, not repeats"* and routed to the registry.

That routing is defensible on its face — a breakout that holds is not an instance of "a failed breakout." **That is precisely the problem.** The hypothesis is conditioned on its own outcome, so the disconfirming region is empty by definition. Under the candidate's own framing, a contradicting instance would be *a failed breakout whose decline was smaller than the breakout, or which reclaimed instead of overshooting.* Alpha #2 never defines that case, never searches for it, and never reports whether any occurred.

*Credit where due:* Addendum C explicitly records that the same slot produces other families and that *"the slot alone is necessary-context but not sufficient."* The awareness exists — it simply does not propagate into the confidence claim in the same document.

### F3 — Confidence escalated outside the frozen artifact
Frozen `AP2-DC-0001_v1.md`: **Medium**. Addendum A: *"Medium toward Medium-High."* B: *"Medium-High toward High."* C: *"remains High."* D: *"remains High."*

The escalation Medium → High happened entirely in addenda, within roughly two hours of wall-clock, while the frozen document — the artifact handed downstream — still reads Medium. **There is no precedence rule stating which value is authoritative.** A downstream reader gets a different answer depending on which file they open.

### F4 — The methodology's core investigative step was never executed
The stated methodology requires dropping to **M5 then M1** on any event meriting investigation. Because of the replay hazard (§6, I1), Alpha #2 correctly refused to switch timeframes during active replay. Consequence: **every observation and every DC/addendum in this period rests on M15 alone.** The instance says so plainly.

This makes specific claims unsupportable by their own evidence. The 2024-08-01 12:30 registry entry asserts *"sustained multi-candle construction, not single-minute concentration"* — a statement about sub-M15 structure, asserted from M15 data, which cannot distinguish the two.

### F5 — Feed provenance unresolved across the entire evidence base
`SESSION_STATE_ALPHA2` and the DC metadata both record the symbol label toggling between **`OANDA:XAUUSD` and `FUSIONMARKETS:XAUUSD`**, verified as *"not a chart-identity change."* That verification addresses **price** identity. It does not address **volume** comparability, and volume-versus-baseline is the primary evidence in essentially every entry this instance filed ("~2x baseline", "~3-4x", "near-record volume 12640"). Broker tick volume is broker-specific. If the label toggled within or between observation windows, baselines and multiples may not be measuring one homogeneous series. Nowhere addressed.

### F6 — Instance independence is overstated
The five AP2-DC-0001 instances are dated: 2024-08-02, **2024-08-15 (Addendum A, ~08:30–10:15)**, **2024-08-15 (Addendum B, ~12:15–14:15)**, 2024-09-05, 2024-09-06.

Two of five are the **same calendar day, same session, roughly two hours apart**, and counted as separate "second" and "third" instances. Two more are **consecutive days** (09-05, 09-06). "Five instances" is therefore four calendar days with clustering, not five independent draws. Serial dependence is never mentioned.

### F7 — Thresholds are verbal, so inclusion decisions are not reproducible
Throughout: *"~2-4x baseline"*, *"borderline"*, *"below the sustained-decline family's intensity threshold"*, *"not exceeding threshold clearly"*. "Baseline" is recomputed locally per event and never defined. No numeric rule exists anywhere for what makes an event registry-worthy, addendum-worthy, or DC-worthy. A second researcher could not reproduce this instance's inclusion set.

### F8 — Early reads of Alpha #1 artifacts
`SESSION_STATE_ALPHA2` (checkpoint 2024-08-07→08-08): *"reading Alpha #1 artifacts is now fully prohibited (previously done only for initial convention reference)."*

Alpha #2 therefore **did** read Alpha #1 material during the session, and the prohibition post-dates AP2-DC-0001's creation. Alpha #2 characterises the reads as convention/format only. That characterisation cannot be verified from artifacts. This is a material qualification on any claim that AP2-DC-0001 was produced in strict independence.

---

## 3. RISK REGISTER

| ID | Risk | Likelihood | Impact | Severity |
|---|---|---|---|---|
| R1 | Confidence claim ("High, zero contradicting") is uninformative because the hypothesis cannot produce a contradiction as stated | Certain (structural) | High — misleads every downstream division | **HIGH** |
| R2 | Volume evidence may span two broker feeds; every observation is volume-anchored | Unknown, unassessed | High — affects the whole evidence base | **HIGH** |
| R3 | Promotion asymmetry: n=1 promoted, n=6 not; evidence channelled to the promoted hypothesis | Certain (observed) | High — distorts the instance's whole output | **HIGH** |
| R4 | Two artifacts state different confidence (Medium vs High), no precedence rule | Certain (observed) | Moderate — downstream ambiguity | **MODERATE** |
| R5 | M15-only; sub-M15 claims unsupported; methodology's investigative core never run | Certain (observed) | Moderate–High — limits what any observation can assert | **MODERATE** |
| R6 | Instance clustering (2 of 5 same day) treated as independent repetition | Certain (observed) | Moderate — inflates apparent sample | **MODERATE** |
| R7 | Verbal thresholds → inclusion set not reproducible | Certain (observed) | Moderate | **MODERATE** |
| R8 | Early Alpha #1 reads qualify the independence claim | Certain (self-reported) | Moderate | **MODERATE** |
| R9 | Pre-edit content of the frozen document is not preserved; audit trail records that a change occurred, not what it replaced | Certain (observed) | Low–Moderate | **MINOR** |
| R10 | Cross-port bug: unknown whether the four affected tools were used before the bug was identified | Unknown | Low–Moderate | **MINOR** |
| R11 | Registry not in chronological order; instance-numbering hard to verify | Certain (observed) | Low | **MINOR** |

---

## 4. CONFIRMATION BIAS ASSESSMENT

*Each charge is stated only where artifact evidence supports it; where I could not find evidence I say so explicitly.*

**Charge 1 — Fell in love with a hypothesis: SUPPORTED (structurally), NOT SUPPORTED (as intent).**
Evidence for the structural claim: promotion at n=1 while 6-, 4- and 2-instance families were withheld (F1); all four addenda attach to that one hypothesis; confidence escalated Medium→High in ~2 hours (F3) on clustered instances (F6). The asymmetry is real and its effect is indistinguishable from favouritism.
Evidence against intent: Alpha #2 filed contrast cases that cut against its own candidate (08-16 and 09-12 "holds", both logged prominently); Addendum A **weakened** its own NFP framing; Addendum C explicitly conceded the slot is *"not sufficient"*. An instance protecting a hypothesis does not usually document its own contrast cases this visibly. **Assessment: a process defect, not motivated reasoning.**

**Charge 2 — Ignored contradictory examples: NOT SUPPORTED as stated; a REFRAMING defect instead.**
No contradictory example was hidden, omitted, or minimised — every one is in the registry with full numbers. What happened is different and more subtle: contrary instances were **reclassified out of the hypothesis's scope** ("contrasting case, not a repeat") rather than counted against it, which let "zero contradicting instances" remain literally true (F2). The evidence was preserved; the accounting was not.

**Charge 3 — Favoured certain explanations: SUPPORTED, narrowly.**
The calendar explanation was retained and successively rescued rather than tested: NFP-specific → *"12:30 UTC US data slot"* (Addendum B) → *"3 of 4 tied to that slot"* (C) → *"direct confirmation on a genuine NFP Friday"* (D). Each reframing preserved a calendar link while the instance's own registry was simultaneously showing that the same slot produces at least four different outcome families. Competing explanations available in its own data (F5 below, §5) were never given comparable treatment.

**Charge 4 — Suppressed or under-reported incidents: NOT SUPPORTED.** I actively looked for this and found the opposite. Every incident in §6 was self-reported by Alpha #2 before any external review, including one (the frozen-document edit) that it could have left unmentioned and that no reader would likely have detected.

---

## 5. DISCOVERY FILTER ASSESSMENT

**Verdict: ASYMMETRIC — simultaneously too permissive and too strict, at different moments.**

- **Too permissive, once:** AP2-DC-0001 promoted on a single instance, with Confidence Medium (already generous at n=1 by the instance's own later standards).
- **Too strict, thereafter:** by the instance's own written criterion, the 6-instance sweep-reclaim-extend family met the promotion bar and was not promoted; likewise the 4-instance sustained-decline family.

**Observations that should have been promoted (by Alpha #2's own stated standard):**
1. **Sweep-reclaim-extend (6 instances, ≥4 distinct session contexts)** — the most-repeated shape the instance found, still living as cross-reference notes appended inside one registry entry.
2. **Sustained multi-hour decline (4 instances, incl. one not tied to 12:30)** — the instance itself noted this *"confirms the family is a general shape, not calendar-slot-specific"*, which is precisely a mechanism claim.

**Discovery Candidate that should not have been promoted when it was:** AP2-DC-0001, at n=1 — not because the observation is poor (it is well documented) but because the instance applied a materially stricter bar to every subsequent shape.

**Structural side-effect:** appending "Nth instance note" inside an existing entry means the most-replicated findings have no object of their own, no ID, no handoff record, and no confidence statement — while the least-replicated finding at promotion time has all four.

---

## 6. INCIDENT ASSESSMENT

| # | Incident | Classification | Justification |
|---|---|---|---|
| **I1** | **Replay incident** — timeframe switch during active replay silently substituted a wrong replay checkpoint (jumped to 2025-10-23, prices ~4090-4120); `replay_start` then entered a stuck `DATA_UNAVAILABLE` loop | **MAJOR** | A *silent* substitution of the observation window is the most dangerous class of failure available here: had it gone unnoticed, observations would have been attributed to the wrong dates. It was caught, a recovery procedure was found and documented, and a standing rule adopted. But its permanent consequence is F4 — no M5/M1 for the entire period, disabling the methodology's core investigative step. Severity is driven by that lasting constraint, not by the incident's own duration. |
| **I2** | **Temporal drift** — checkpoint labels drifted ~1 calendar day over several checkpoints (labels said 08-16/08-17 while epochs were 08-15/08-16), caused by estimating elapsed time from batch sizes | **MODERATE** | Self-detected, self-corrected, remediated with a durable rule (every subsequent checkpoint verified via `date -d @epoch`). Alpha #2 states the epoch values and all dates written to registry/DC/addenda remained correct. It is *not* negligible, however: it left an unreconciled contradiction in the journal (§7, C1), and for a period the running commentary misdescribed which day was being observed. |
| **I3** | **Editing the FROZEN document** — the frozen `AP2-DC-0001_v1.md` body was edited directly to fix an internal cross-reference during the rename cascade | **MODERATE** | A direct violation of the document's own immutability rule and of its recorded hash. Mitigation was exemplary: self-caught, a canonicalisation rule established, hash recomputed, and the correction logged as a **new append-only handoff line** rather than an overwrite — both hashes remain visible in `HANDOFF_LOG_ALPHA2`. Residual defect (R9): the pre-edit content is not preserved anywhere, so the log records *that* the document changed but not *what it said before*. Not MINOR, because immutability is the property downstream divisions rely on. |
| **I4** | **File collision** — Alpha #2's artifacts originally carried the *same basenames* as Alpha #1's official files, differing only by directory | **MODERATE** | A genuine collision-of-appearance hazard for any tool or human resolving by filename, in a laboratory that had just been given a strict isolation directive. Remediated by CEO-directed `_ALPHA2` suffixes. Escalated from MINOR because it is the direct cause of I3 — the rename cascade produced the frozen-document edit. |
| **I5** | **Cross-port bug** — `src/core/tab.js` hardcodes CDP port 9222 regardless of `TV_CDP_PORT`, making `tab_list/tab_switch/tab_close/tab_new` unreliable across the two MCP instances | **MODERATE** | Correctly identified, CEO-registered as technical debt, and mitigated by abandoning those four tools for the session; all other tools route through `connection.js` and are isolated. Not MAJOR because the mitigation is sound and isolation was independently verified via `target_id`. Not MINOR because the failure mode is cross-instance action on the *other* instance's window, and the artifacts do not record whether those tools were used before the bug was found (R10). |
| **I6** | **Early reads of Alpha #1 artifacts** (self-reported, prohibition adopted mid-session) | **MODERATE** | Not an accident but a scope breach relative to the independence design, and it pre-dates AP2-DC-0001's creation. Characterised as convention-only; unverifiable from artifacts. Material because independence is the property that gives a parallel instance's agreement its evidential value. |
| **I7** | **M1 data unavailable via replay for this period** (feed limitation, distinct from I1) | **MINOR** | An environmental constraint, not a process failure; correctly disclosed and treated as an open constraint rather than worked around. |

---

## 7. REGISTRY CONSISTENCY

**What is consistent (verified):**
- `HANDOFF_LOG_ALPHA2` (6 lines: FROZEN, HASH CORRECTION, 4 addenda) ↔ `ADDENDUM_INDEX_ALPHA2` (4 entries) ↔ the 4 addendum files on disk. **Fully reconciled.**
- Frozen document `content_hash` (`8192503d…`) matches the corrected handoff line. **Consistent.**
- `DISCOVERY_INDEX_ALPHA2`: 1 candidate, v1, FROZEN. **Consistent.**
- Session-state running total "10 Observation Registry entries" ↔ registry contains exactly 10 entries. **Consistent.**

**Contradictions found:**

**C1 — Two incompatible descriptions of 2024-08-15 afternoon *(material)*.**
`SESSION_STATE_ALPHA2` journal: *"**2024-08-15 10:15 -> 2024-08-16 00:15 UTC**: quiet, ordinary consolidation (2440-2454), low volume. … No new phenomena."*
Addendum B (AP2-ADD-0002) documents, inside that window: *"2024-08-15, ~12:15-14:15 UTC … declines hard, volume 11152 … roughly 38 points below the peak … settling at 2455-2459 by ~14:15 UTC."*
One artifact says the window was quiet with no new phenomena; the other says it contained the third instance of the candidate's mechanism, with near-record volume. The price ranges also disagree (2440–2454 vs a 2470.11 peak and 2432.23 low). The journal marks the addendum event *"(revisited later in replay order)"* and the drift note (I2) explains how such a mismatch could arise — but **the two statements were never reconciled**, and both stand in the current artifacts.

**C2 — Confidence conflict *(material)*.** Frozen candidate: Medium. Addenda B/C/D: High. No precedence rule. (F3, R4.)

**C3 — Registry not chronological *(minor)*.** Entries appear in the order 08-01, 08-01, 08-05, 08-05, 08-16, **08-02**, 08-22, 08-23, 09-12, 09-11 — the 08-02 sweep-reclaim entry (the *origin* of the 6-instance family) sits sixth, after 08-16, and the last two are inverted. Append-only is satisfied; readability and verification of the "first/second/third instance" numbering are not.

**C4 — Instance-count bookkeeping *(minor)*.** The sweep-reclaim family's instance notes are numbered "third", "fourth", "fifth", "sixth" inside the 08-05 entry, while the family's first and second instances are documented in two *different* entries (08-02 and 08-05). Correct on inspection, but the numbering cannot be validated without reading all entries in a non-obvious order.

---

## 8. REJECTED EVENTS WORTH RE-EXAMINATION

| Event | Why it merited more | Impact |
|---|---|---|
| **2024-08-21 13:30–16:00 UTC** — *"sustained elevated volume (7357–**12201**) across ~4-5 candles"*, swept to 2494.02, bounced to 2506.71 | 12201 is among the three or four largest volume readings in the instance's entire period (record 12999). Dismissed via the 3-question filter as *"resembles an already-documented shape"* | **Highest-impact omission.** A near-record-volume event exists only as a journal line — no registry entry, no comparability record. If magnitude is a criterion anywhere in this instance's reasoning (it is, repeatedly), this event should be recoverable from the registry. It is not. |
| **2024-09-16 09:30–15:45 UTC** — volume bump to 6507 spanning 12:30–14:00 UTC | 12:30 UTC is the instance's most-tracked slot; other 12:30 events were logged at ~2× baseline | Inconsistent application of the instance's own most important conditioning variable. A 12:30 event was screened out at a level comparable to others that were retained. |
| **2024-08-20 09:15–17:30 UTC** — peak 2531.67, then *"first real pullback (~23pt, vol spike to 8733)"* | The first failure of a multi-day rally the instance was actively tracking | Left only in the journal; the rally-thread narrative has a gap where its first reversal should be. |
| **2024-08-27 ~13:00–14:00 UTC** — 5000–8500, *"borderline but resolved as ordinary"* | Explicitly borderline, resolved without a recorded rule | Illustrates F7: "borderline" decisions are unreproducible. |
| **2024-08-28/29 gradual pullbacks** — dismissed as *"below the sustained-decline family's intensity threshold"* | That threshold is nowhere defined numerically | Family membership is decided by an undefined quantity. |

**Common cause:** all five exclusions turn on undefined verbal thresholds (F7). None appears to be motivated omission — the journal documents each decision and its reasoning, which is why they were auditable at all.

---

## 9. RESEARCH QUALITY

| Dimension | Assessment | Basis |
|---|---|---|
| **Discipline** | **HIGH** | Consistent checkpointing with running totals; the 3-question filter is visibly applied and its outcome recorded even when the answer is "don't investigate"; genuine silence across long ordinary stretches (e.g. ~18h on 08-06/07) rather than manufactured findings; scope boundary (2024-08-01→2025-08-01) respected throughout. |
| **Reproducibility** | **LOW** | Verbal, locally-recomputed thresholds (F7); M15-only (F4); unresolved feed provenance (F5); no denominators anywhere. A second researcher could not reconstruct the inclusion set. |
| **Traceability** | **GOOD** | Handoff log, addendum index and files fully reconcile; hash correction handled append-only with both values visible; epoch verification adopted after I2; every incident dated and described. Two gaps: pre-edit frozen content not preserved (R9), and split confidence (C2). |
| **Self-criticism** | **HIGH — the instance's strongest attribute** | Self-reported the frozen-document edit, the date drift, the replay hazard and the collision risk, unprompted. Addendum A actively weakened its own candidate's framing. Contrast cases (08-16, 09-12) that cut against the candidate were logged prominently. Repeatedly refused to promote its own recurring shapes. |
| **Robustness of observations** | **LOW–MODERATE** | Single instrument, single period, in-sample, M15-only, small n with clustering (F6), no base rates, and a hypothesis whose confidence rests on an empty disconfirming set (F2). |

### Overall Research Quality Score: **64 / 100**

Process integrity and disclosure would score around 80 on their own — this instance is more honest about its own failures than most research processes manage. The score is pulled down by the epistemic core: a promotion rule applied asymmetrically (F1), a confidence figure that cannot be wrong as constructed (F2), confidence recorded in two places with two values (F3), and an evidence base whose primary axis (volume) has an unresolved provenance question (F5) and whose supporting resolution (M5/M1) was never available (F4).

---

## 10. RECOMMENDATIONS *(methodology only)*

1. **Define a numeric promotion threshold before the next candidate.** State, in advance, how many instances across how many distinct session contexts justify a Discovery Candidate. Apply it symmetrically — retroactively re-examining, under that same rule, both AP2-DC-0001 and the 6- and 4-instance families now sitting in the registry.
2. **Require every candidate to state its own disconfirming case.** A hypothesis should be accompanied by a written answer to *"what observation, if seen, would count against this?"* If that set is empty — as it currently is for AP2-DC-0001 — the hypothesis needs restating before evidence is accumulated against it.
3. **Stop escalating confidence in addenda, or make precedence explicit.** Either confidence lives only in the frozen candidate (addenda file evidence, not ratings), or each addendum states that it supersedes the frozen value. Two artifacts must never carry two live values.
4. **Count instances, not events.** Record calendar-day and session separation; instances from the same session should not be counted as independent repetitions.
5. **Resolve feed provenance before further volume-based work.** Confirm whether the volume series across an observation window originates from a single broker feed. Until then, volume-multiple claims should be marked provisional.
6. **Replace verbal thresholds with numeric ones.** Define "baseline", and the multiples that make an event registry-, addendum- or candidate-worthy. This alone would make F7, and the five §8 exclusions, reproducible.
7. **Give recurring registry families their own object.** A shape at six instances should have an ID and a tracking record rather than living as appended notes inside another entry.
8. **Keep the registry chronological**, or add an index by date; the current ordering makes instance-numbering unverifiable without a full read.
9. **Preserve pre-edit content whenever a frozen document is corrected**, so the audit trail records what changed, not only that something did.
10. **Record whether the port-affected tools were used before the cross-port bug was identified** — the artifacts currently leave this unanswerable.
11. **Treat the M5/M1 unavailability as a stated scope limit on every claim it touches.** Any assertion about sub-M15 construction should be marked as not evidenced while the constraint holds.

---

## 11. AP2-DC-0001 ASSESSMENT

**Hypothesis (as reconstructed from the frozen document):** on a first-Friday-of-month session, a sharp breakout fully reverses into a larger, extended decline that overshoots the pre-breakout level and settles materially lower.

**Evidence:** origin instance 2024-08-02 (M15 only) + Addenda A–D (2024-08-15 ×2, 2024-09-05, 2024-09-06). Confidence: Medium in the frozen document, High in the addenda.

**Contradictions and limitations identified:**
- The calendar framing has been restated three times under pressure from its own evidence (NFP-specific → 12:30 UTC slot → "direct confirmation on a genuine NFP Friday"), while the instance's own registry shows that slot producing at least four distinct outcome families. **This is evidence compatible with limitation or non-generalisation of the calendar-conditioned form of the hypothesis** — not a refutation, and not for Red Team to conclude.
- "Zero contradicting instances" is structurally guaranteed (F2), so it provides no support for the confidence level.
- Two of five instances are the same session (F6).
- No M5/M1 for any instance (F4); no denominator of failed breakouts that did *not* overshoot; volume provenance unresolved (F5); Medium/High conflict unresolved (F3).

### Risk level: **HIGH**

Justification: the vulnerabilities are concentrated in the parts a downstream division would rely on most. The confidence rating is both internally inconsistent (two live values) and derived from a claim that cannot fail; the sample is smaller and more clustered than "five instances" conveys; the primary evidence axis has an open provenance question; and the resolution needed to check the construction claims was never available. None of this says the observation is wrong — the underlying event is large, well documented, and recurs. It says that **the candidate's stated support is materially weaker than the artifacts assert**, which is precisely what a HIGH risk rating is for.

*Per standing constraints: this is a risk assessment only. Red Team does not promote, demote, accept or reject. Whether AP2-DC-0001 is testable, insufficiently supported, robust or rejected is the Statistician's determination; its official status is the CEO's.*

---

## 12. FINAL VERDICT

> # CONTINUE WITH RECOMMENDED IMPROVEMENTS

**Not CONTINUE UNCHANGED:** the promotion asymmetry (F1), the unfalsifiable-as-stated confidence claim (F2), the split confidence record (F3) and the unresolved feed provenance (F5) are structural and will propagate into every future candidate this instance produces if left alone.

**Not MAJOR METHODOLOGY REVIEW REQUIRED:** I tried to establish this and could not. The methodology itself is sound and was followed; the observation discipline is real; every incident was self-detected and disclosed before any external review; the registry is conservative to a fault; and contrary evidence was preserved rather than buried. The defects are specific and rule-shaped — a promotion threshold, a disconfirmation requirement, a confidence-precedence rule, numeric thresholds, and a provenance check — not a failure of the underlying research model. A process that catches and reports its own frozen-document violation does not need rebuilding; it needs five rules it currently lacks.

---

**Audit ends. Red Team halts and takes no further action, awaiting CEO decision.**
