# RED TEAM — RESEARCH AUDIT #2 (ALPHA #1)
### Full methodological audit of the complete research portfolio
**ID:** RT-AUDIT-0002 · **Date:** 2026-07-24 · **Auditor:** Red Team · **Mandate:** CEO — Red Team Research Audit #2

**Sources (read-only, Alpha #1 exclusively):** `DISCOVERY_CANDIDATE_INDEX.md` (24 rows) · `HANDOFF_LOG.md` (75 lines) · all 24 `candidate_v1.md` · all **30 addenda** · `OBSERVATION_REGISTRY.md` (10 entries) · `SESSION_STATE.md` (2,826 lines) · `SESSION_CLOSE_ALPHA_DISCOVERY_WINDOW_2025-10-23.md` · `DC-0001_HASH_REPRODUCIBILITY_INVESTIGATION.md` · `DATA_QUALITY_OPEN_ITEM_2025-09-17_1800UTC.md` · `metadata_v1.json` × 24 · checkpoint backups & cycle output.
**Alpha #2 not used. Knowledge Base not used. Statistician not contacted. No external information. Nothing assumed.**
**Nothing modified.** No artifact, addendum, candidate, KB entry or methodology touched. No promotion, no official rejection.

> Risk levels below are **risk and vulnerability assessments only** ([RISK_VERDICTS](../methodology/RISK_VERDICTS.md)). Contrary evidence is reported as *"evidence compatible with limitation or non-generalisation"*, never as refutation ([EVIDENCE_RULES](../methodology/EVIDENCE_RULES.md) E10).

---

## 1. EXECUTIVE SUMMARY

I was asked to demonstrate that Alpha #1's process is defective. **On the dimensions where research processes usually fail, I could not.** On one dimension I did not expect, I could.

What resisted every attack:
- **Confidence discipline is unbroken across the entire corpus.** All 24 candidates sit at Low or Very-low except two (DC-0002 Low-to-medium, DC-0004 Medium-low) — and those two are the best-evidenced. **All 30 addenda leave confidence unchanged**, each stating explicitly that Alpha does not validate or update it. Twenty-four candidates, thirty addenda, zero escalation. I looked for a single instance of inflation and found none.
- **Self-falsification is systematic, not incidental.** DC-0008's addenda progressively dismantle DC-0008's own NFP hypothesis. DC-0009's Addendum D explicitly contradicts its own Addendum C. DC-0017's Addendum B is a counter-instance to DC-0017's own headline. DC-0006 reports a counterexample found the next replay day. DC-0024 reports an M5 ratio that breaches Alpha's own organic-construction convention rather than reclassifying it. The Observation Registry contains entries logged *specifically* so that hedged claims "don't drift into being treated as established."
- **The audit trail fully reconciles.** 24 folders = 24 index rows = 24 handoff FROZEN lines, all FROZEN. 30 addendum files + 3 inline events = 33 handoff ADDENDUM lines. Exact.
- **Two open items were self-opened and left open** rather than resolved prematurely — including one (the 2025-09-17 data artifact) detected by noticing that M1 volume was *too flat*, which is genuinely skilled forensic work.

What broke:
- **"Largest so far" has become a de facto promotion criterion.** Four of the six candidates created in the reopened post-cutoff window are record-framed in their own titles. A running maximum exists by construction in any growing sample and is superseded automatically; promoting it manufactures a guaranteed stream of candidates carrying no information beyond "the sample got bigger." Alpha #1 **states this problem explicitly in DC-0024 §3** — and promoted anyway. Awareness without a rule.
- **Record bookkeeping is factually inconsistent inside the corpus.** DC-0022 declares 86.75pt a family magnitude record; DC-0013's own Addenda D/F/G/H/I already recorded 89.4, 100.97, 90.81, **180.53** and 120.06pt. DC-0024 traces the record chain as "DC-0013's original scale → DC-0022's 86.75pt → 125.685pt", omitting the entire addendum series. **Magnitudes filed as addenda are invisible to candidates that later claim records.**
- **The reserved holdout has been consumed by observation.** DC-0019–0024 all fall past `2025-10-23T09:15Z`. DC-0004 names that exact reserve as "the decisive test… deliberately not been spent." It has now been partly spent.

**Overall Research Quality Score: 72 / 100.**
**Verdict: CONTINUE WITH RECOMMENDED IMPROVEMENTS.**

---

## 2. FINDINGS

### F1 — Record-chasing as a promotion criterion *(central finding)*
Post-cutoff candidates, by their own titles: DC-0019 *"Nearly Double the Prior Record"* · DC-0020 *"Sets a New All-Time Volume Record"* · DC-0022 *"Sets New Duration and Magnitude Records… Nearly Doubling the Prior Longest Run"* · DC-0023 *"Among the Largest-Volume Candles in the Replay"* · DC-0024 *"Sets a New All-Time Magnitude Record (125.7 Points)"*.

Five of six post-cutoff candidates are framed on extremity. Their own texts concede the mechanism is not new: DC-0021 — *"Each phase individually replicates an already-documented mechanism"*; DC-0022 — *"The underlying mechanism… has ample precedent"*; DC-0024 — *"The underlying mechanism has ample precedent."* The novelty being promoted is **magnitude, not mechanism**.

*Mitigating and to Alpha's credit:* DC-0024 §3 states the problem in plain terms — *"each 'largest magnitude so far' record… has so far always been superseded by a subsequent instance. Whether there is a practical ceiling… remains an open question this instance does not resolve."* DC-0022 §5 adds the record *"should not be treated as evidence of any fixed upper bound."* The insight is present and documented; what is missing is a rule that acts on it.

### F2 — Contradictory record bookkeeping (evidence bifurcation)
| Source | Magnitude | Claim |
|---|---|---|
| DC-0013 Addendum D | ~89.4pt | "record la acel moment", consolidation ending |
| DC-0013 Addendum F | ~100.97pt | first instance above the 9–12k band |
| DC-0013 Addendum G | ~90.81pt | 5th distinct session |
| **DC-0013 Addendum H** | **~180.53pt** | *"by far the largest displacement observed in this family"* |
| DC-0013 Addendum I | ~120.06pt | ~97% recovery |
| **DC-0022** (later) | **86.75pt** | *"substantially exceeds prior family records"* |
| **DC-0024** (later still) | **125.685pt** | *"a new all-time magnitude record for any single directional leg observed in this replay"* |

DC-0022's claim is **incorrect against Alpha #1's own artifacts** — Addendum D alone (89.4pt, a clean directional leg ending in consolidation, like-for-like with DC-0022's shape) exceeds it. DC-0024's record chain omits 180.53pt and 120.06pt entirely.

A partial defence exists — "single directional leg" versus multi-leg episode — but the qualifier is doing heavy work, is not stated where a reader would catch it, and does not rescue the Addendum D comparison. **Root cause: the DC series and the addendum series function as two evidence stores that do not consult each other.**

### F3 — The reserved holdout has been consumed by observation
DC-0019 Additional Notes: *"This candidate's observation window falls after the original holdout_cutoff (2025-10-23T09:15 UTC)… observed under the CEO's explicit decision to resume Alpha Discovery past that cutoff in a reopened window."* DC-0019 through DC-0024 are all post-cutoff.

DC-0004 Additional Notes: *"The decisive test is out-of-sample confirmation on the reserved holdout (post 2025-10-23), which is a CEO-gated resource and has deliberately not been spent."*

Both statements are true and both were transparently declared. Their combination is the problem: **the candidate with the strongest quantitative support in the portfolio has named as its decisive test a resource that has since been partly spent on observation.** This is not misconduct — it was CEO-directed and disclosed — but it is the most consequential cross-cutting fact in this audit for anything downstream.

### F4 — Evidence concentration and the DC/addendum mismatch
DC-0013 holds **11 of 30 addenda (37%)**; ten candidates hold none. Those addenda span at least five distinct sessions and a magnitude range from ~71pt to ~180pt. Yet DC-0013's frozen Confidence section still reads *"**Low.** One instance, one instrument, one session type."*

The family's real evidence base (roughly a dozen instances) is recorded under a candidate that formally claims one. Alpha's rule that addenda never alter the frozen text is correct in principle (F6) but here produces a document whose stated evidential basis is an order of magnitude below its actual one, with no pointer reconciling the two.

### F5 — A numeric threshold emerged — from a single anchor
Later work applies a consistent **42.7% M5-concentration ratio** (derived from DC-0018's accepted 7,964/18,652) to classify construction as organically distributed. It is used across DC-0020, 0021, 0022, 0023, 0024 and DC-0013's later addenda. This closes a real gap: earlier candidates classified construction by eye.

The limitation is that 42.7% is anchored to **one accepted instance**, not to a distribution of concentration ratios. It delivers consistency, not justification. DC-0024 reports an instance at **48.1%**, exceeding the convention, and flags it honestly rather than reclassifying — exemplary conduct that also demonstrates the threshold has no principled basis to appeal to.

### F6 — Confidence discipline: no defect found
24 candidates: 21 at Low/Very-low; DC-0002 Low-to-medium; DC-0004 Medium-low. Nothing above Medium-low anywhere. All 30 addenda state they do not validate, reject or update confidence (DC-0021's addendum uses different wording — *"Still Low… does not alter DC-0021's original text, confidence rating, or status"* — and complies identically). **Zero escalation events in the entire corpus.** This resisted every attempt to break it.

### F7 — Falsifiability is uneven
Explicit disconfirming conditions exist in exactly three candidates:
- **DC-0002** — *"if lateral compressions still resolve upward systematically, that is long beta and this candidate should die."*
- **DC-0003** — re-run OBS-0017's 384 exceedances with scale separation; if the pooled null does not decompose, it fails.
- **DC-0004** — the reserved out-of-sample holdout (now compromised, F3).

The remaining 21 offer *"a natural comparison point for future instances"* — a research direction, not a disconfirming condition. The record-framed candidates are structurally worse: **"this was the largest so far" cannot be false**, so DC-0015, 0019, 0020, 0022, 0023 and 0024 have no failure state at all as written.

### F8 — Registry consistency: fully reconciled
24 folders = 24 index rows = 24 handoff FROZEN lines, all marked FROZEN. 30 addendum files + 3 inline "Library Concept Scan" events = 33 handoff ADDENDUM lines — exact. Observation Registry: 10 entries. No orphans, no phantoms, no count mismatches. *Minor:* the handoff log uses one ADDENDUM label for two different event types (separate files vs in-place edits with hash recompute), which obscures the immutability breach of I3 at a glance.

---

## 3. DISCOVERY CANDIDATE REVIEW

*Risk = vulnerability of the candidate's stated support, not a judgement on whether the observation is real.*

| DC | Mechanism (as stated) | Evidence | Principal weakness / counter-evidence | Addenda | Risk |
|---|---|---|---|---|---|
| 0001 | Single-bar velocity outlier → gradual deceleration | n=2 + 1 contrast, visual only | **Content hash does not reproduce (I1)**; pace never measured; no denominator | 0 | **HIGH** |
| 0002 | HTF compression resolves with H4 bias | n=4, one pre-registered | K05 long-beta confound self-declared (3/4 up in a bull); "compression" undefined | 0 | MODERATE |
| 0003 | Scale inversion: boundary inside vs outside noise | micro n=2, HTF n=4 | Scale/liquidity entangled (both micro cases thin Asian tape); makes a real falsifiable prediction | 0 | MODERATE |
| 0004 | NY PDH sweep-reject → reversion | n=42, matched-null p=0.021, sign-stable | Fails Bonferroni; selection over ~12 cells; **its decisive holdout is now compromised (F3)** | 0 | MODERATE |
| 0005 | Third test of a level differs | n=2, one impure ("died inside the range") | Folk knowledge; no base rate of third tests that did nothing | 0 | **HIGH** |
| 0006 | Extreme relative volume fails to extend | ~5 instances | Self-reported inversion next day; contradicted by DC-0008/0013/0017 (extreme-volume candles that extended); confounded with DC-0003 | 0 | **CRITICAL** |
| 0007 | Equal lows swept & reclaimed same candle | n=1 | Excursion (~2.4pt) inside local noise by DC-0003's own criterion | 0 | **HIGH** |
| 0008 | Sustained vs single-minute construction | ~6 instances | Root construction; its own addenda dismantle the NFP framing (a strength) | 4 | MODERATE |
| 0009 | Band survives 7→9 touches | 1 band, full lifecycle | **Addendum D contradicts Addendum C** — level-memory not durable within one level | 4 | **HIGH** |
| 0010 | Quiet hour breaks with sustained expansion | n=1 vs 3-day baseline | **Own Addendum A shows the whole session ran hot**; registry logs the hour running ordinary later | 1 | **CRITICAL** |
| 0011 | Single-minute sweep reclaimed → extends | 3 instances | All on days pre-flagged anomalously active (self-declared, unbroken confound); Addendum B's reclaim was multi-minute, violating the title | 2 | **HIGH** |
| 0012 | Absorption: high volume, no displacement | n=1 | Cleanest operational definition in the corpus; shape seen once | 1 | **HIGH** |
| 0013 | Large NY sustained expansion, no reversal | 1 + 11 addenda (~12 instances) | **Confidence still reads "One instance" (F4)**; family container in fact, single candidate in form | **11** | MODERATE |
| 0014 | 00:00 UTC V-reversal → rally → reversal | n=1 | Compound 3-part shape at an hour the registry says has no consistent behaviour | 0 | **HIGH** |
| 0015 | 11-candle run, longest observed | n=1 | Distinguishing feature is a **sample extremum** — cannot be false; already superseded by later addenda | 0 | **CRITICAL** |
| 0016 | Early-Asia expansion → reversal at marginal high | n=2 same hour | Ending shape genuinely recurs across the two; magnitude shown variable | 1 | MODERATE |
| 0017 | NFP-scale 12:30 impulse holds gains | 1 + 4 addenda | **Addendum B documents a comparable 12:30 print giving back the entire move**; Addendum A shows it drifted rather than held | 4 | **CRITICAL** |
| 0018 | Extreme-volume fresh-high failure → decline | n=1 | 4-part compound; sweep-vs-rejection ambiguity unresolved by its own text | 0 | **HIGH** |
| 0019 | Large weekend gap fails to retrace | n=1, post-cutoff | Record-framed ("nearly double prior record"); triggering condition, session and volume band all new at once | 1 | **HIGH** |
| 0020 | 18:00 sweep → failed reclaim → volume record | n=1 | Record-framed; 18:00 explicitly disclaimed as a mechanism; other 18:00 instance was a suspected data artifact | 0 | **HIGH** |
| 0021 | Decline → absorption, no volume decay | n=1 (n=2 with addendum) | Own text: each phase "individually replicates an already-documented mechanism"; addendum notes both instances same session window, consecutive days | 1 | **HIGH** |
| 0022 | NY-afternoon record duration + magnitude | n=1 | **Record claim factually wrong against DC-0013's addenda (F2)**; mechanism conceded to have ample precedent | 0 | **CRITICAL** |
| 0023 | 8-hour choppy extreme-volume episode | n=1 | All elements precedented; sequencing claim vs DC-0022 is n=1 and self-labelled as observation only | 0 | **HIGH** |
| 0024 | London-morning record decline (125.7pt) | n=1 | Record chain omits larger addendum values (F2); **but honestly reports 48.1% breach of its own 42.7% convention** | 0 | **HIGH** |

**Distribution: CRITICAL 5 · HIGH 13 · MODERATE 6 · LOW 0.**

---

## 4. DISCOVERY FILTER ASSESSMENT

**Verdict: the filter was well-calibrated in the pre-cutoff window and loosened materially in the reopened window.**

**Pre-cutoff (per `SESSION_CLOSE`):** across ~29 replay days, **zero new candidates** and **nine addenda**. The stated rule: *"escalation to a new DC only for phenomena without precedent, otherwise addendum or consolidation into already-documented categories."* That is exactly right, and it was followed — including for events up to 180.53pt, which were filed as addenda rather than promoted.

**Post-cutoff:** **six new candidates in a single day**, five record-framed, all n=1, several conceding in their own text that the mechanism has ample precedent. Under the pre-cutoff rule, DC-0022, DC-0023 and DC-0024 would have been addenda to DC-0013 — which is precisely how a 180.53pt instance was handled weeks earlier.

**Candidates that should not have been promoted (by Alpha's own pre-cutoff rule):** DC-0022, DC-0023, DC-0024 — and DC-0015, whose distinguishing feature is a sample extremum.

**Evidence that should have its own object:** the DC-0013 addendum family (~12 instances, ≥5 distinct sessions, ~71–180pt). It is the best-replicated body of evidence Alpha #1 possesses and has no candidate of its own, no confidence statement of its own, and — per F2 — is not consulted when later candidates declare records.

---

## 5. CONFIRMATION BIAS ASSESSMENT

*Each charge tested against artifacts; where I found no evidence I say so.*

**Active search for counterexamples: SUPPORTED — strongly.** DC-0008 Addenda A/B/C/D progressively dismantle DC-0008's own NFP hypothesis, ending at *"four instances, four different outcomes, the only common thread being the clock time itself."* DC-0009 Addendum D opens by stating it *"directly contradicts a naive reading of Addendum C."* DC-0017 Addendum B files a counter-instance against DC-0017's headline. DC-0006 records a counterexample found the next replay day. The Observation Registry logs counter-instances *expressly* so hedged claims "don't drift into being treated as established." This is the single most convincing evidence against a bias charge.

**Ignoring alternatives: PARTIALLY SUPPORTED.** Session, liquidity and calendar alternatives are frequently named and sometimes tested. But no candidate in the sustained-expansion family tests against a general volatility-persistence explanation, despite the corpus documenting elevated volume decaying over multi-hour windows repeatedly. The alternative is available in Alpha's own data and is not engaged.

**Changing definitions: NOT SUPPORTED as a defect.** DC-0008's NFP → day-of-week reframing is evidence-driven, documented in the addendum that forced it, and *weakens* the original framing. That is correct scientific conduct, not goalpost-moving.

**Convenient reclassification: NOT SUPPORTED.** Contrary evidence is filed as addenda *against the parent candidate*, where it counts, rather than routed into a separate store. DC-0017's own Addendum B is the clearest example — it damages its parent and was filed anyway.

**Artificial confidence inflation: NOT SUPPORTED.** Zero escalation across 24 candidates and 30 addenda (F6).

**The one real bias is selection, not hypothesis-protection (F1/F2):** attention is systematically drawn to extremes, and record claims are benchmarked against a subset of the corpus that happens to exclude larger values. This inflates the apparent novelty rate without anyone defending a favoured hypothesis.

---

## 6. CONFIDENCE ASSESSMENT

- **Consistency: excellent.** 21/24 Low or Very-low; the only two above are the two best-evidenced.
- **Contradictions: none found** between candidate text, index and handoff.
- **Escalation: none** — 30/30 addenda leave confidence untouched.
- **Missing rule (the one real gap):** there is no rule for what should happen when a candidate accumulates a large addendum body. DC-0013 says *"One instance"* while holding 11 addenda spanning ~12 instances (F4). The no-escalation rule is right; the absence of any reconciliation pointer is not.
- **Secondary gap:** confidence vocabulary is free-text ("Low", "Very low", "Low-to-medium", "Medium-low") with no definition of what separates the levels.

---

## 7. ADDENDA ASSESSMENT

| Family | Count | Justified as addenda? | Should have become a separate DC? | Implicitly changed the hypothesis? |
|---|---|---|---|---|
| **DC-0013 (B–K)** | 11 | **Yes** — same construction, correctly not promoted | **No — but the family needs its own object** (F4) | **Yes, materially.** The parent claims one NY-session 4-candle instance; the addenda extend it to ≥5 sessions, 2–13 candles, 71–180pt, and multiple resolution styles. The candidate's scope silently widened. |
| **DC-0008 (A–D)** | 4 | Yes | No | **Yes, and declared.** A/B/C/D progressively remove the NFP framing and reframe to day-of-week. Exemplary. |
| **DC-0009 (A–D)** | 4 | Yes — one lifecycle | No | Yes: D reverses the reading C invited. Correctly filed. |
| **DC-0017 (A–D)** | 4 | Yes | No | **Yes — the headline is contradicted by its own B.** The parent still reads "holds its gains." |
| **DC-0011 (A–B)** | 2 | Yes | No | Yes: B's reclaim is multi-minute, contradicting the title's "single-minute". |
| **DC-0010, 0012, 0016, 0019, 0021** | 1 each | Yes | No | DC-0010's addendum substantially undercuts its parent's hour-specific framing. |

**Cross-cutting:** the addendum instrument is used correctly and honestly — but because addenda never alter the frozen text, **five candidates now carry headline claims their own addenda contradict or have outgrown** (DC-0010, 0011, 0013, 0017, and DC-0009's simplest reading). Nothing in the process reconciles a frozen title with the evidence filed beneath it.

---

## 8. DUPLICATE ASSESSMENT

**Near-identical mechanisms (one construction, many candidates):** DC-0013, 0014, 0015, 0016, 0017, 0018, 0019, 0020, 0021, 0022, 0023, 0024 all state the same underlying construction — sustained, distributed multi-minute participation (DC-0008). They differ by session, duration, magnitude, direction and ending shape, all read off after the event. **Twelve candidates, one mechanism.**

**Should be considered together (not a Red Team decision to execute):**
- DC-0015 / DC-0022 — both "longest run" claims; the second supersedes the first.
- DC-0018 / DC-0020 — both extreme-volume failed moves; DC-0020 explicitly resets DC-0018's volume record.
- DC-0006 / DC-0018 / DC-0020 — one claim (extreme volume fails) across three objects.
- DC-0012 / DC-0021 — absorption as a standalone shape and as a phase.
- DC-0005 / DC-0007 / DC-0009 — level-interaction count at 3, 3-then-swept and 7→9 touches.
- DC-0002 ⊂ DC-0003 — DC-0003 says so itself.

**Should be separated:** DC-0013 is doing two jobs — a specific 2025-08-22 observation *and* a container for a twelve-instance family (F4).

**Outcome-space exhaustion persists:** across this family the corpus now documents consolidation, sharp reversal, modest pullback, hold, drift-up, sustained decline, multi-leg oscillation, ~97% recovery and 8-hour chop. **No observation of a large sustained expansion could contradict the family as a set.**

---

## 9. INCIDENT ASSESSMENT

| # | Incident | Class | Justification |
|---|---|---|---|
| **I1** | **DC-0001 hash does not reproduce.** 17/18 candidates reproduced exactly across three recorded locations; DC-0001 returns `7d6282b2…` instead of the recorded `1f1b3d39…` under every normalisation variant tried | **MODERATE** | The freeze protocol's entire value is that a frozen document can be verified. For the lab's first candidate that verification fails, so its content cannot be confirmed as the content that was frozen. Handling was correct: investigated, documented, explicitly **not** "fixed" by editing, correctly classified as administrative and kept out of the DC lifecycle. Not MAJOR — isolated, disclosed, and no scientific claim depends on it. Not MINOR — it is the integrity guarantee itself. |
| **I2** | **Handoff-log gap** — DC-0008…0012 and all 16 addenda absent from the log that declares itself *"the sole audit trail proving what Alpha handed to Red Team"*, while `SESSION_STATE` asserted "handoff la zi" and "no open administrative debts" | **MODERATE** *(remediated)* | Material while it stood: five frozen candidates and every addendum were unprovable as handed off, and the state file asserted the opposite. Fully backfilled and now reconciles exactly (F8). Classified on impact at the time, not on the remediation. |
| **I3** | **Immutability breach on DC-0002/0003/0004** — a "Library Concept Scan" section added *inside* already-frozen candidate files, with hashes recomputed | **MODERATE** | Directly contrary to those files' own instruction that corrections go in a separate addendum "never as an edit to this file." Disclosed via handoff ADDENDUM lines with both hashes visible. Residual: pre-edit content is not preserved, and the handoff label does not distinguish an in-place edit from a filed addendum (F8). |
| **I4** | **Suspected data artifact, 2025-09-17 18:00 UTC** — 56.3pt range on only 12,556 volume, with M1 volume implausibly flat (800–870 across all 15 minutes) and a sharp wick on volume indistinguishable from neighbours | **MINOR** *(as an incident)* | Not a process failure — a detected external data defect. Handling is the strongest forensic work in the corpus: identified by reasoning from an established range/volume relationship, confirmed on M1, correctly excluded from **both** the DC index and the Observation Registry, left OPEN, and thereafter explicitly excluded from later addenda's organic-construction checks. |
| **I5** | **Holdout cutoff crossed** — observation resumed past `2025-10-23T09:15Z`; DC-0019–0024 all post-cutoff | **MAJOR** *(in consequence, not in conduct)* | CEO-directed and transparently declared in DC-0019, so no misconduct. Classified MAJOR because of what it costs: DC-0004 — the portfolio's only quantitatively-supported candidate — names that reserve as its decisive test, and the reserve is no longer clean in the form that candidate assumes. Irreversible. |

---

## 10. RESEARCH EVOLUTION

**Real, measurable progress across the corpus:**

| Dimension | Early (DC-0001–0007) | Late (DC-0019–0024) |
|---|---|---|
| Construction classification | By eye, prose | Numeric **42.7% M5 concentration** threshold applied consistently |
| Sub-M15 verification | Absent or partial | Routine M5/M1 anatomy, with the known data-artifact signature explicitly excluded |
| Contrary evidence | Noted in prose | Filed as dated addenda against the parent candidate |
| What is *not* claimed | Occasional | Explicit in every late candidate ("makes no claim about cause", "should not be treated as a repeatable signature") |
| Self-reporting of breaches | — | DC-0024 reports its own 48.1% breach of the 42.7% convention rather than reclassifying |
| Process artifacts | — | Handoff reconciliation, two formal OPEN items, a session-close with Red Team prioritisation |
| Boilerplate hygiene | `content_hash_method` says "PENDING" while a real hash is present (DC-0005/0006/0007) | Correct self-referential canonicalisation |

**Regressions in the same period:** the promotion filter loosened sharply post-cutoff (§4), and record benchmarking became internally inconsistent (F2). **Alpha #1 got better at documenting and verifying, and worse at deciding what deserves to be a candidate.**

---

## 11. RESEARCH QUALITY

| Dimension | Assessment | Basis |
|---|---|---|
| **Discipline** | **HIGH** | 2,826-line session state with continuous checkpointing; ~29 replay days producing zero candidates when the filter said none were warranted; long silent stretches genuinely unlogged. |
| **Reproducibility** | **MODERATE** | Improved markedly (42.7% threshold, M5 verification, hash protocol) but the threshold rests on one anchor (F5), promotion decisions remain judgement-based, and I1 shows the freeze protocol is not yet fully verifiable. |
| **Traceability** | **HIGH** | Index, handoff and folders reconcile exactly across 24 candidates and 30 addenda; every addendum dated and hashed; two OPEN items formally registered. Gaps: pre-edit content of I3 not preserved; one handoff label covers two event types. |
| **Self-criticism** | **VERY HIGH** | Systematic, not incidental — addenda routinely damage their own parents (F6, §5). The strongest attribute in the corpus. |
| **Robustness** | **LOW–MODERATE** | Single instrument, in-sample, no denominators anywhere, 18 of 24 candidates at n=1, and an outcome space the family cannot fail to cover (§8). |
| **Consistency** | **MODERATE** | Confidence and audit trail highly consistent; **record bookkeeping and promotion criteria are not** (F1, F2, §4). |

### Overall Research Quality Score: **72 / 100**

Confidence discipline, self-falsification culture, traceability and incident handling would place this well into the 80s. The score is held down by four things: a promotion criterion that manufactures candidates from sample extrema (F1), a factual inconsistency in record bookkeeping inside the corpus (F2), a structural split between where evidence lives and what candidates claim (F4), and the irreversible consumption of the reserve on which the portfolio's best candidate depends (F3).

---

## 12. RECOMMENDATIONS *(methodology only)*

1. **Bar extremity as a promotion criterion.** "Largest/longest/highest so far" should be an addendum to the family it belongs to, never a new candidate. A running maximum is superseded by construction and has no failure state.
2. **Maintain one running-maximum register** for the corpus (magnitude, duration, volume), updated by **both** candidates and addenda. Any record claim must be checked against it before freezing. This alone prevents F2.
3. **Require a disconfirming condition in every candidate.** DC-0002, DC-0003 and DC-0004 already demonstrate the standard; 21 candidates do not meet it. If no observation could count against a candidate, it is not ready to be frozen.
4. **Add a reconciliation pointer when an addendum body outgrows its parent.** Confidence should stay untouched (that rule is right), but a candidate holding 11 addenda should not still read "One instance" with nothing linking the two.
5. **Give the DC-0013 family its own object.** Twelve instances across five sessions is the best-replicated evidence in the portfolio and currently has no candidate, no confidence statement, and no visibility to later record claims.
6. **Derive the concentration threshold from a distribution**, not from one accepted instance. Compute the M5/M1 concentration ratio across all large candles and set the boundary from its shape; until then, mark 42.7% as provisional.
7. **Record the holdout's status explicitly** in any candidate that names it as a decisive test, so downstream divisions are not told a resource is reserved when it is not.
8. **Separate the two ADDENDUM event types in the handoff log** — a filed addendum and an in-place edit with hash recompute are different events and should not share a label.
9. **Preserve pre-edit content whenever a frozen document is corrected**, so the trail shows what changed, not only that something did.
10. **Define the confidence vocabulary** — state what separates Very-low, Low, Low-to-medium and Medium-low, so the (excellent) discipline is anchored to something.
11. **Test the family against a general volatility-persistence alternative.** The corpus repeatedly documents multi-hour elevated-volume decay; no candidate engages it as a competing explanation.

---

## 13. FINAL VERDICT

> # CONTINUE WITH RECOMMENDED IMPROVEMENTS

**Not CONTINUE UNCHANGED.** Four defects are structural and compounding: extremity-driven promotion (F1) is generating candidates at an accelerating rate that carry no mechanism novelty; the record bookkeeping is factually wrong inside the corpus (F2); evidence and claims have separated (F4); and the holdout consumption (F3) is irreversible and undercuts the portfolio's strongest candidate.

**Not MAJOR METHODOLOGY REVIEW REQUIRED.** I tried to justify this and the artifacts refuse it. A process with zero confidence escalation across 24 candidates and 30 addenda, whose addenda routinely damage their own parents, which ran 29 replay days and promoted nothing because its own filter said not to, which detected a data-feed artifact by noticing that volume was *too smooth*, and which opened a formal investigation into a hash mismatch rather than quietly correcting it — that process is not broken. Its judgement about **what deserves to become a candidate** is what slipped, and it slipped in one identifiable window with a rule-shaped cause. Three rules — no promotion on extremity, one running-maximum register, a mandatory disconfirming condition — address the majority of what this audit found.

---

**Audit ends. Red Team halts and takes no further action, awaiting CEO decision.**
