# RED TEAM — AUDIT LEDGER
### Append-only, hash-chained record of every review lifecycle event
**Parent:** [CHARTER.md](../CHARTER.md) §13.

> Each entry references the previous entry's hash → the chain is tamper-evident. **Never** edit or delete an entry; corrections are new entries that supersede by reference.

**Entry format**
```
[<seq>] <UTC timestamp>
  prev_hash:   <hash of entry seq-1, or GENESIS>
  event:       INTAKE | MANIFEST | EVIDENCE_READ | CRITIQUE | VERDICT | SEAL | CEO_DELIVERY | ESCALATION | RECUSAL | SUPERSEDE
  dc_id:       DC-<id>
  freeze_hash: <hash of the frozen candidate>
  battery_ver: CRITIQUE_BATTERY vX.Y
  reviewer:    <id>
  detail:      <one line>
  entry_hash:  <hash of this entry's fields above>
```

---

```
[0] GENESIS
  prev_hash:   —
  event:       DIVISION_ESTABLISHED
  detail:      Red Team division approved by CEO 2026-07-21; evidence-reviewer refinement approved same day; implementation authorized. No candidate reviewed.
  entry_hash:  GENESIS

[1] 2026-07-21
  prev_hash:   GENESIS
  event:       CEO_DELIVERY
  detail:      CEO ratified implementation: repository/charter/independence/report-template/audit/verdicts/governance ACCEPTED; division OPERATIONAL. CRITIQUE_BATTERY v1.0 held DRAFT (not ratified) — no Discovery Candidate may be reviewed until battery gets explicit CEO approval. Awaiting further CEO instruction.
  entry_hash:  E1

[2] 2026-07-21
  prev_hash:   E1
  event:       VERDICT              # governance event: battery ratified
  detail:      CEO authorized + ratified CRITIQUE_BATTERY v1.0 — five critiques (C1 Observation Quality, C2 Evidence Quality, C3 Alternative Explanation, C4 Claim Discipline, C5 Worth Investigating) and three verdicts (🟢 CONTINUE INVESTIGATION / 🟡 NEEDS BETTER EVIDENCE / 🔴 NOT RECOMMENDED). Quality-control framing, good-faith, lightweight. Integrated into CHARTER §8/§9/§11, review template, verdict rules. Red Team now FULLY OPERATIONAL. Battery to be revisited after several real reviews. Final authorized infrastructure task. Awaiting first Discovery Candidate + CEO review.
  entry_hash:  E2

[3] 2026-07-21
  prev_hash:   E2
  event:       CEO_DELIVERY          # official acceptance
  detail:      CEO ACCEPTED Red Team v1.0 as COMPLETE. Wording refinements applied: governing stance now "Every Discovery Candidate is treated as an unverified scientific observation until sufficient evidence justifies further investigation" (replaced presume-false language repo-wide); clarified 🟡 NEEDS BETTER EVIDENCE is NOT a rejection — it means the current submission does not yet justify additional laboratory resources. No further infrastructure work authorized. Red Team enters OPERATIONAL STANDBY, awaiting first Discovery Candidate via official Alpha→Red Team interface.
  entry_hash:  E3

[4] 2026-07-23
  prev_hash:   E3
  event:       INTAKE + VERDICT     # first operational review batch
  dc_id:       DC-0001..DC-0018 (13 reviewed; 5 held)
  battery_ver: CRITIQUE_BATTERY v1.0
  reviewer:    Red Team
  detail:      First operational review batch. State reconstructed EXCLUSIVELY from official Alpha
               artifacts in worktree `ai_quant_lab-alpha-automation` (branch alpha-automation-v1) —
               DISCOVERY_CANDIDATE_INDEX.md, OBSERVATION_REGISTRY.md, SESSION_STATE.md, HANDOFF_LOG.md,
               metadata_v1.json. Alpha conversation NOT used. Confirmed: 18 DCs (all FROZEN, all v1,
               all hashed); 16 addendum files across 8 DCs; Observation Registry 7 entries (1 promoted
               → DC-0014). No prior Red Team review existed (baseline zero) — all 18 new.
               Per CEO scope (2026-07-23): reviewed the 13 with a FROZEN/SUBMITTED line in HANDOFF_LOG
               (DC-0001..0007, 0013..0018). Verdicts: 🟢×6 (DC-0002/0003/0004/0013/0016/0017),
               🟡×7 (DC-0001/0005/0006/0007/0014/0015/0018), 🔴×0. DC-0017 continued as NARROWED.
               ESCALATIONS TO CEO:
                 (1) Handoff gap — DC-0008..0012 are FROZEN in the index with content_hashes but have
                     NO FROZEN/SUBMITTED line in HANDOFF_LOG (which claims to be the sole handoff audit
                     trail); the 16 addenda are also unlogged. SESSION_STATE claims "handoff la zi" and
                     "no open admin debts" — contradicted by the log. DC-0008..0012 HELD, not reviewed.
                 (2) Immutability-process breach — DC-0002/0003/0004 had "6. Library Concept Scan"
                     added INSIDE the frozen candidate_v1.md with hash recomputed (logged as ADDENDUM),
                     contradicting each file's own Handoff Statement ("never as an edit to this file";
                     corrections go in a separate dated addendum). Benign/disclosed; verdicts unaffected.
                 (3) Portfolio fragmentation (observation, not a verdict) — DC-0013/0014/0015/0016/0017/
                     0018 are largely single-instance slices of ONE construction (DC-0008 sustained
                     multi-minute expansion) distinguished by post-hoc descriptors (session, duration,
                     ending shape). Their parent, DC-0008, is itself in the HELD/unlogged group. Worth a
                     CEO decision on whether the family should be consolidated before deeper resourcing.
  entry_hash:  E4

[5] 2026-07-23
  prev_hash:   E4
  event:       CEO_DELIVERY         # CEO ruling on the first-batch report
  reviewer:    Red Team
  detail:      CEO ACCEPTED all 13 first-batch verdicts. Rulings on the three escalations:
               (1) Handoff — escalation ACCEPTED. Alpha (not Red Team) will correct HANDOFF_LOG.md to
                   fully reconcile all FROZEN candidates, all addenda, and all official events.
               (2) Next batch — DC-0008..0012 review AUTHORIZED, but GATED: begins only AFTER Alpha's
                   handoff reconciliation is present in the artifact. Verified 2026-07-23: reconciliation
                   NOT yet done (HANDOFF_LOG unchanged, 24 lines; no FROZEN/SUBMITTED lines for
                   DC-0008..0012; 16 addenda still unlogged). DC-0008..0012 remain HELD. Red Team does
                   NOT perform the reconciliation (independence: read-only intake, no writes to Alpha).
               (3) Family fragmentation — observation NOTED; NO consolidation authorized. Discovery
                   Candidates remain separate. Consolidation is a later-stage decision (Statistician +
                   Reasoning Engine), never Red Team. Red Team does NOT modify the DC portfolio structure
                   — and has not (point 3 was an observation only, no structural change was made).
               STATE: standby. On confirming Alpha's handoff reconciliation, re-verify intake for
               DC-0008..0012 and review them under CRITIQUE_BATTERY v1.0.
  entry_hash:  E5

[6] 2026-07-23
  prev_hash:   E5
  event:       INTAKE + VERDICT     # second operational review batch
  dc_id:       DC-0008..DC-0012 (5 reviewed)
  battery_ver: CRITIQUE_BATTERY v1.0
  reviewer:    Red Team
  detail:      Alpha reconciled HANDOFF_LOG (commit 005f837): all 18 DCs now carry FROZEN/SUBMITTED
               lines and all 16 addenda are logged. CEO authorized batch 2 (DC-0008..0012).
               INTAKE RE-VERIFICATION (all pass): FROZEN/SUBMITTED line present for each of the 5;
               metadata content_hash == handoff hash for all 5 (ce52a96/ac7ffde/5855f96/dc0607e/
               4a4791c); all 12 group addenda logged (8=4, 9=4, 10=1, 11=2, 12=1); admin gate CLOSED.
               DC-0001 hash-reproducibility item noted OPEN but separate — does not affect science.
               VERDICTS: 🟢×1 DC-0008 (foundational, measurable construction distinction, ~6 instances,
               news sub-hypothesis self-walked-back by Addendum D); 🟡×4 DC-0009/0010/0011/0012.
               Notable good-faith self-falsification in the addenda: DC-0008-D (NFP→day-of-week),
               DC-0009-D (broken resistance NOT durably support), DC-0010-A (whole-session, not
               hour-specific). 🔴×0.
               OBSERVATION (not a new escalation): the "00:00-01:00 UTC hour is becoming unusual"
               sub-thread shared by DC-0010/DC-0012 is weakened by Alpha's own later OBSERVATION_REGISTRY
               entries (2025-08-11/12/13 ran ordinary; "no consistent characterization"). Reviewers
               noted this per-candidate; no structural action taken (portfolio structure unchanged).
               PORTFOLIO STATUS: all 18 DCs reviewed. Total 🟢 7 / 🟡 11 / 🔴 0. No candidates held.
               No DC or Alpha artifact modified; no families consolidated; portfolio structure untouched.
  entry_hash:  E6

[7] 2026-07-24
  prev_hash:   E6
  event:       INTAKE + VERDICT     # Stage 0 duplicate screening, first Alpha #2 candidate
  dc_id:       AP2-DC-0001 (Alpha Parallel Instance #2)
  reviewer:    Red Team
  detail:      CEO established Stage 0 DUPLICATE SCREENING for all Alpha #2 candidates. Alpha #2 has
               produced exactly one candidate to date: AP2-DC-0001. Intake verified — FROZEN, document
               hash 8192503d… == corrected HANDOFF_LOG_ALPHA2 line, no addenda. Noted (benign, disclosed):
               a post-freeze HASH CORRECTION event moved the hash from 7dab65cd… (rename cascade +
               canonicalisation rule; substantive text unchanged) — same class as the DC-0002/0003/0004
               immutability note. Alpha #2 files no metadata_v1.json.
               SCREENING RESULT: **VARIANT OF DC-0018.** Core mechanism (failed upside expansion →
               larger sustained decline past the origin) is DC-0018's; Alpha #2 adds a distinct condition
               (first-Friday/NFP slot), sequence (multi-candle failure with partial recovery vs DC-0018's
               intracandle round trip) and result property (second leg ~40% larger, overshoot below origin).
               Secondary: RELATED BUT DISTINCT FROM DC-0017 — a direct counter-instance that independently
               corroborates DC-0017's Phase-1 REJECT; RELATED BUT DISTINCT FROM DC-0006. Not a SUPERSET
               (it narrows by adding a condition, it does not generalise). Not comparable to DC-0008 —
               AP2 is M15-only, so the sustained/concentrated axis cannot be evaluated.
               INDEPENDENT REPLICATION: YES — different observer, in-replay date (2024-08-02 vs 2025-09-09),
               price regime (~2455 vs ~3675), session context. Core moves n=1 → n=2 independent instances.
               No contradiction vs the original; it extends DC-0018's scope (failure need not be intracandle).
               DISPOSITION (Red Team determination per CEO delegation): ADDENDUM to DC-0018, NOT a separate
               research line — a separate candidate would reproduce Phase-1 finding F1/F2 (fragmentation by
               post-hoc descriptor) inside the Alpha #2 namespace. Execution referred to CEO: attaching
               evidence would require writing into Alpha #1's folder, which is forbidden.
               BLOCKING EVIDENTIAL ISSUE (A1): AP2 metadata records the feed label alternating between
               OANDA:XAUUSD and FUSIONMARKETS:XAUUSD across the session. Price identity was verified, but
               every load-bearing claim is a *volume ratio to baseline*, and broker tick volume is not
               comparable across brokers. All elevation claims are unsafe until confirmed single-feed.
               Decision document: red_team/duplicate_screening/RT-DS-0001_AP2-DC-0001.md
               Nothing modified, nothing promoted, no re-classification. Awaiting CEO approval.
  entry_hash:  E7

[8] 2026-07-24
  prev_hash:   E7
  event:       CEO_DELIVERY          # governance update ratified + constitution amended
  reviewer:    Red Team
  detail:      CEO ACCEPTED RT-DS-0001; "VARIANT OF DC-0018" stands as the official Duplicate
               Screening verdict. Duplicate Screening becomes an official, permanent stage.
               RED TEAM PIPELINE now mandatory for every candidate:
                 Phase 0 Duplicate Screening -> Phase 1 Adversarial Review ->
                 Phase 2 Contradiction Search -> Phase 3 Methodology Audit.
                 No adversarial analysis begins before Duplicate Screening completes.
               FOUR METHODOLOGY CLARIFICATIONS ratified and written into the constitution:
                 (1) RED TEAM DOES NOT PROMOTE. No promotion, demotion, final acceptance or final
                     rejection. Role is exclusively: vulnerabilities, contradictions, duplicates,
                     methodology problems. Final evaluation = Statistician and/or CEO.
                 (2) COUNTER-INSTANCES. A single observation is never a definitive refutation.
                     Standard wording: "evidence compatible with limitation or non-generalisation
                     of the hypothesis." Refutation only after a sufficient body of evidence — and
                     that conclusion is not Red Team's to issue.
                 (3) DUPLICATE SCREENING classes fixed: GENUINELY NEW / EXACT DUPLICATE / VARIANT /
                     SUPERSET / RELATED BUT DISTINCT. Mechanism-only comparison; never title,
                     wording, timeframe, instrument or example.
                 (4) INDEPENDENT REPLICATION never auto-creates a research line; mark
                     INDEPENDENT REPLICATION OF [DC-ID], attach evidence to the original or
                     recommend an Addendum after mechanistic analysis. Replications are valuable
                     scientific evidence and must be preserved.
               DOCUMENTS AMENDED: CHARTER.md (governance-update block; §4 non-responsibilities +
               exhaustive role statement; §5 repo map; §8 four-phase pipeline; §9.1 verdicts-are-
               findings; §9.2 single-observation rule; §16 Statistician/CEO own final evaluation and
               execution-referral rule). NEW: methodology/DUPLICATE_SCREENING.md v1.0.
               EVIDENCE_RULES.md +E10. VERDICT_RULES.md binding-constraint header.
               PRESERVED UNMODIFIED per CEO instruction: RED_TEAM_PHASE1_REPORT.md and
               RT-DS-0001_AP2-DC-0001.md. New rules apply to future analyses only; DUPLICATE_SCREENING
               §Precedent records that RT-DS-0001 predates rules (1) and (2) and is not the template
               on those two points.
               OPEN QUESTION REFERRED TO CEO: Phase 1's A/B/C scheme (READY FOR STATISTICAL
               VALIDATION / NEEDS MORE EVIDENCE / REJECT) and the battery's 🔴 NOT RECOMMENDED both
               read as promotion/rejection recommendations, which rule (1) now forbids. The issued
               report is untouched; Red Team requests a CEO ruling on how future Phase-1 output
               should be expressed. Pending that ruling, future reports will state findings only.
               STATE: normal operating standby, awaiting the next Discovery Candidate.
  entry_hash:  E8

[9] 2026-07-24
  prev_hash:   E8
  event:       CEO_DELIVERY          # open question from [8] RESOLVED
  reviewer:    Red Team
  detail:      CEO ruled on the conflict raised in [8]. OFFICIAL CLARIFICATION: a Red Team verdict is
               a RISK VERDICT, not a laboratory decision. The two are formally separated.
               AUTHORITY MODEL now written into the constitution:
                 RED TEAM      -> risk and vulnerability only.
                 STATISTICIAN  -> testable / insufficiently supported / statistically robust /
                                  statistically rejected.
                 CEO           -> sole authority for Knowledge-Base promotion, archiving, closure,
                                  and any change of official status.
               Red Team verdicts never mean laboratory acceptance, laboratory rejection, KB promotion,
               or final classification.
               PERMITTED TAXONOMY: LOW / MODERATE / HIGH / CRITICAL RISK, or any equivalent risk
               taxonomy. READY FOR STATISTICAL VALIDATION remains permitted with exactly one meaning —
               "from Red Team's perspective no major vulnerabilities remain that obstruct statistical
               evaluation" — and explicitly NOT accepted / validated / promoted.
               NOT RECOMMENDED restated: no longer means "rejected"; means only that Red Team finds
               vulnerabilities sufficient not to recommend continuation IN THE CURRENT FORM. CEO may
               still choose revision, Addendum, Statistician, or archiving.
               "REJECT" RETIRED from Red Team's vocabulary.
               READING RULE FOR THE ISSUED PHASE 1 REPORT (preserved unmodified): its A/B/C labels are
               risk verdicts. A = LOW RISK (no blocking vulnerability), B = MODERATE/HIGH RISK,
               C = CRITICAL RISK. The word "REJECT" there is superseded terminology and never denoted
               laboratory rejection; DC-0006/0010/0015/0017 remain fully open to CEO decision.
               DOCUMENTS: NEW methodology/RISK_VERDICTS.md v1.0 (authority model, taxonomy, mapping,
               Phase-1 reading rule). AMENDED CHARTER (governance block item 2; §5 repo map; §9 verdict
               table + risk readings + REJECT retirement; §9.1 authority table), VERDICT_RULES.md
               (binding-constraint header), CRITIQUE_BATTERY.md (🔴 restated).
               PRESERVED UNMODIFIED: RED_TEAM_PHASE1_REPORT.md, RT-DS-0001_AP2-DC-0001.md.
               STATE: open question from [8] CLOSED. Normal operating standby.
  entry_hash:  E9

[10] 2026-07-24
  prev_hash:   E9
  event:       CEO_DELIVERY          # full state save for successor continuity
  reviewer:    Red Team
  detail:      Per CEO instruction, Red Team fully saved so a fresh Claude can resume exactly.
               NEW canonical resume document: red_team/RED_TEAM_STATE.md (read-this-first; identity,
               isolation rules, 4-phase pipeline, risk-verdict authority model, complete work log,
               portfolio snapshot, open items, next actions, ledger index). CHARTER repo map updated
               to list it. No analysis performed this entry — documentation/continuity only.
               WORK TO DATE (all committed on branch red-team-foundation): division founded + Critique
               Battery v1.0 ratified; risk verdicts separated from lab decisions ("REJECT" retired);
               4-phase pipeline + non-promotion rule; review batch 1 (13 DCs), batch 2 (DC-0008..0012);
               RED_TEAM_PHASE1_REPORT.md (DC-0001..0018); RT-DS-0001 (AP2-DC-0001 = VARIANT OF DC-0018);
               RT-AUDIT-0001 (Alpha #2, 64/100); RT-AUDIT-0002 (Alpha #1, 24 DC/30 addenda, 72/100).
               OPEN (awaiting CEO): both audits' decisions; RT-DS-0001 addendum execution; verdicts
               ledger not yet populated with A/B/C or audit risk levels; DC-0019..0024 lack individual
               reviews/ files (covered inside RT-AUDIT-0002). Nothing modified outside red_team/.
               STATE: normal operational standby. Next entry [11], prev_hash E10.
  entry_hash:  E10

[11] 2026-07-24
  prev_hash:   E10
  event:       VERDICT               # final falsification pass, all remaining candidates
  reviewer:    Red Team
  detail:      CEO tasked a final falsification pass over all remaining Alpha #1 + Alpha #2 candidates
               with a three-way verdict (REJECTED / NEEDS MORE EVIDENCE / SURVIVED); SURVIVED routed to
               the Statistician. Deliverable: RED_TEAM_FINAL_EVALUATION.md (RT-FINAL-0001).
               GOVERNANCE RECONCILIATION (documented in the report, not silently overridden): the
               2026-07-24 rules retired "REJECT" and reserved final evaluation for Statistician/CEO.
               The three verdicts are treated as Red Team adversarial-SCREENING recommendations, not
               laboratory dispositions — SURVIVED = permitted "READY FOR STATISTICAL VALIDATION" sense;
               REJECTED = "recommend elimination, does not survive falsification"; final elimination
               authority remains the CEO's (confirmed by the task routing SURVIVED to the Statistician).
               REJECTED used only where a sufficient body of contrary evidence exists (E10 respected).
               RESULT (25 candidates: 24 Alpha #1 + AP2-DC-0001):
                 SURVIVED (3) -> DC-0003 (scale-separated re-run of OBS-0017 null), DC-0004 (matched-null,
                   flag: reserved holdout compromised), DC-0008 (M1/M5 concentration-ratio distribution;
                   gates the whole family). Recommended for Statistician hand-off.
                 REJECTED (6) -> DC-0006 (3 corpus counter-instances + self-inversion + DC-0003 confound),
                   DC-0010 (own Addendum A: whole session hot, not the hour; registry counter-instances),
                   DC-0015 (sample-extremum "longest run" = unfalsifiable), DC-0017 (own Addendum B
                   contradicts the "holds" headline), DC-0022 (record claim factually wrong vs DC-0013
                   addenda + unfalsifiable extremum), DC-0024 (record extremum + duplicates recovery-shape
                   family). In every case the legitimate residue survives elsewhere.
                 NEEDS MORE EVIDENCE (16) -> DC-0001, 0002, 0005, 0007, 0009, 0011, 0012, 0013, 0014,
                   0016, 0018, 0019, 0020, 0021, 0023, AP2-DC-0001.
               Nothing modified outside red_team/; no observation, statistics, promotion or consolidation.
               Red Team does not contact the Statistician — hand-off is a recommendation for CEO routing.
               STATE: normal operational standby, awaiting CEO decision. Next entry [12], prev_hash E11.
  entry_hash:  E11

[12] 2026-07-25
  prev_hash:   E11
  event:       VERDICT               # final reconciliation before Statistician hand-off
  reviewer:    Red Team
  detail:      CEO halted any prior hand-off; RT-FINAL-0001 declared not-yet-complete. Reconstructed the
               inventory EXCLUSIVELY from official repos. Deliverable: RED_TEAM_FINAL_EVALUATION_v2.md
               (RT-FINAL-0002), supersedes RT-FINAL-0001 (preserved unmodified).
               INVENTORY DISCREPANCY (headline, flagged for CEO ratification): task stated 27 (Alpha #2 = 1);
               repository actually holds **28** — Alpha #1 = 26 (DC-0001..DC-0026), Alpha #2 = 2. The delta
               is AP2-DC-0002 (FROZEN/SUBMITTED 2026-07-25, hash ff55a8ba…, 1 addendum), frozen after the
               task's inventory was composed; the Alpha #2 instance is now CLOSED by CEO instruction.
               Reconciled to the repository per instruction not to miss candidates; did NOT unilaterally
               expand scope — surfaced for CEO ratification.
               NEW ANALYSIS: DC-0025 (REJECTED — volume-record headline superseded by its own Addenda A/B
               39,353->41,995->42,808; mechanism precedented), DC-0026 (NEEDS MORE EVIDENCE — distinct
               thin-liquidity tail-dislocation mechanism, verified M15/M5/M1, n=1; strongest of the new
               batch), AP2-DC-0002 (RT-DS-0002 = VARIANT OF DC-0023; NEEDS MORE EVIDENCE — catalyst
               untestable in a one-year window, n=1).
               BACKFILLED individual review files per constitution: reviews/DC-0019..DC-0026 (8 files).
               RECONCILED TALLY (28): SURVIVED 3 (DC-0003, DC-0004[flagged], DC-0008) · NEEDS MORE EVIDENCE
               18 · REJECTED 7 (DC-0006, 0010, 0015, 0017, 0022, 0024, 0025). All 25 prior verdicts unchanged.
               DC-0004 HOLDOUT WARNING (CEO-requested, explicit): the reserved post-2025-10-23 holdout —
               DC-0004's named decisive test — has been CONSUMED at lab level by the reopened window
               (DC-0019..0026 are post-cutoff). Any post-cutoff result CANNOT be independent confirmatory
               validation; DC-0004 stays SURVIVED only as an in-sample hypothesis. Recorded in report §6.
               INTEGRITY REGISTER W1–W8 (holdout, DC-0001 hash, record-bookkeeping, missing metadata on
               DC-0025/0026, 42.7% single-anchor, Alpha #2 confidence calibration, feed provenance,
               inventory discrepancy).
               Nothing modified outside red_team/; no observation/statistics/promotion/consolidation;
               nothing sent to the Statistician (SURVIVED list is a CEO-routing recommendation).
               STATE: HAND-OFF HALTED, awaiting CEO approval. Next entry [13], prev_hash E12.
  entry_hash:  E12

[13] 2026-07-25
  prev_hash:   E12
  event:       CEO_DELIVERY          # ratifications — see AUTHORITY note
  authority:   CHIEF ARCHITECT, under CEO delegation dated 2026-07-25. NOT taken directly by the CEO.
  numbering:   The delegation referred to this as entry "[10]". The ledger is append-only and
               hash-chained and was already at [12] (E10 state-save, E11 falsification pass, E12
               reconciliation); per chain integrity these ratifications are recorded as [13],
               prev_hash E12. Flagged, not silently renumbered.
  reviewer:    Red Team
  detail:      Hand-off UNBLOCKED. Four ratifications recorded:
               (R1) INVENTORY = 28 RATIFIED. AP2-DC-0002 formally included as the 28th candidate.
                    Integrity warning W8 (27-vs-28 discrepancy) CLOSED.
               (R2) RT-AUDIT-0001 (Alpha #2) and RT-AUDIT-0002 (Alpha #1) ACCEPTED. **Both Alpha
                    divisions are CLOSED**, so the audit recommendations have no active recipient;
                    they are RETAINED for any future Alpha instance. No producer of candidates remains.
               (R3) The 7 REJECTED (DC-0006, DC-0010, DC-0015, DC-0017, DC-0022, DC-0024, DC-0025)
                    are ARCHIVED, not deleted. Their IDs remain PERMANENTLY RESERVED and are never reused.
               (R4) RT-DS-0001 determination (AP2-DC-0001 = addendum to DC-0018) is recorded in the
                    Red Team consolidated register ONLY; it is NOT written into Alpha's tree. Alpha #1
                    is closed and no one holds a mandate there, so the physical attachment will not occur.
               Recorded in the consolidated register: verdicts_ledger.md (ARCHIVE + consolidation
               sections) and RED_TEAM_STATE.md. Nothing written outside red_team/. No candidate reviewed.
               STATE: ratifications logged; Red Team in terminal standby (no active candidate producer).
               Next entry [14], prev_hash E13.
  entry_hash:  E13

[14] 2026-07-25
  prev_hash:   E13
  event:       ESCALATION            # W9 integrity risk + branch-architecture closure
  authority:   Findings surfaced by the CHIEF ARCHITECT under CEO delegation; recorded by Red Team.
  reviewer:    Red Team
  detail:      BRANCH ARCHITECTURE CLOSED. Per Chief Architect decision, the lab has ONE official line,
               statistician-foundation (only it + flow-c-foundation are on remote). The per-division-branch
               model is abandoned (five divisions share one working tree; no checkout-per-division).
               red-team-foundation was RETRACTED (deleted) — after being advanced it duplicated the whole
               line, not a Red Team-only history. Verified be99c1f (old RT tip) is an ancestor of
               statistician-foundation before deleting → no commit orphaned; all Red Team work lives on
               statistician-foundation, intact and published. NOT pushed. RED_TEAM_STATE.md §1 + header +
               git-habit corrected (previously still claimed red-team-foundation — false for several turns,
               the source of the confusion diagnosed in [13]). Exception: flow-c-foundation stays separate
               (genuinely diverged — see W9).
               W9 ADDED to the integrity register (verdicts_ledger.md; W1–W8 in RT-FINAL-0002 §7). Framed as
               an INTEGRITY RISK, not a statistical verdict:
                 - Defect D3 (PROJECT_AUDIT.md, matched-null miscalibrated, HIGH) is marked RESOLVED
                   2026-07-13 on flow-c-foundation via commits 28c35b6 / aa5bee3 / 69747fd, but is still
                   OPEN on statistician-foundation because those commits were never merged.
                 - RED TEAM VERIFICATION (branch state only; implementation NOT read): all three commits
                   are contained in flow-c-foundation and in NONE of statistician-foundation → "never
                   merged" confirmed.
                 - Consequence (Chief Architect): Validation Engine rebuilt a matched-null calibration in F6
                   that already existed, without the 2026-07-13 adversarial battery; Statistician + Research
                   Lab worked assuming the method was unvalidated. The 2026-07-13 battery reported FPR=0.975
                   under drift_long and 0.925 under trend_short; F6/F6.1 did not test drift.
                 - FINDING: the same defect holds two contradictory states in one repository and divisions
                   worked on the wrong state. Red Team does NOT judge which validation is superior (outside
                   mandate; ran neither). No merge; no implementation read. Resolution handled separately.
               Nothing written outside red_team/. No candidate reviewed.
               STATE: TERMINAL STANDBY. No candidate producer remains. Next entry [15], prev_hash E14.
  entry_hash:  E14

[15] 2026-07-25
  prev_hash:   E14
  event:       CORRECTION            # corrects a factual error in [14]/W9. Append-only: [14] NOT edited.
  authority:   Correction issued by the CHIEF ARCHITECT under CEO delegation; recorded by Red Team.
  reviewer:    Red Team
  detail:      Entry [14] (and W9 as first written) contained a factual error. The ledger is append-only,
               so [14] is left intact and corrected here.
               FALSE STATEMENT IN [14] (quoted exactly): "The 2026-07-13 battery reported FPR=0.975 under
               drift_long and 0.925 under trend_short; F6/F6.1 did not test drift." — the FIRST HALF is false.
               CORRECT STATEMENT (source: docs/MATCHED_NULL_VALIDATION.md §2 on flow-c-foundation, verified
               by Red Team via `git show flow-c-foundation:docs/MATCHED_NULL_VALIDATION.md`, lines 15-19/37):
                 The figures 0.975 / 0.925 / 0.25 are the PRE-FIX state of the first engine version —
                 "First engine version bootstrapped absolute risk. The adversarial battery EXPOSED
                 catastrophic false positives under trend: drift_long FPR=0.975, trend_short=0.925,
                 regime_shift=0.25." They are NOT the battery's result; they are a defect the battery FOUND
                 during validation and which was immediately FIXED (bootstrap risk/ATR ratio, rescaled to
                 the ATR at the null entry). POST-FIX: drift_long 0.00, trend_short 0.00, regime_shift 0.00,
                 across 12 adversarial scenarios, all FPR(0.05) < 0.075, ALL_SCENARIOS_CALIBRATED = True.
                 The fix IS the drift-beta control built for long-biased strategies.
               INDEPENDENT VERIFICATION (already published): Research Lab commit **e89ded1**
                 (docs/TRANSFERABILITY_ADDENDUM_v1.1.md) — confirmed by Red Team to EXIST via `git cat-file`
                 — records that diff 28c35b6..aa5bee3 is exactly the risk/ATR fix and that in the committed
                 state ALL_SCENARIOS_CALIBRATED=true with drift_long FPR05=0.0 and trend_short FPR05=0.0.
               PROVENANCE OF THE ERROR: introduced by the Chief Architect (a grep fragment quoted without
               reading the next five lines) and propagated into [14] by Red Team in good faith. Red Team has
               now verified the corrected text against the source directly — the discipline that failed on
               [14], the same branch/document-state method used for W9's original branch-containment check.
               WHAT REMAINS TRUE (unchanged from [14]/W9): D3 holds two contradictory states in one
               repository; the three commits (28c35b6/aa5bee3/69747fd) were never merged to
               statistician-foundation (Red-Team-verified, factual); divisions worked on the wrong state;
               the Validation Engine rebuilt in F6 a matched-null calibration that already existed; F6/F6.1
               did not test drift.
               SEVERITY OF W9 DOES NOT DECREASE — if anything it is greater: the pre-existing version was
               MORE complete than the F6 reconstruction (it carried the adversarial battery and the drift-beta
               control that F6/F6.1 lack), so VE rebuilt something weaker than what already existed. Red Team
               does NOT judge which validation is superior (outside mandate; ran neither); this is an
               integrity finding about contradictory states, not a statistical verdict.
               W9 in verdicts_ledger.md annotated with a correction marker pointing here. No merge; no
               implementation read (documentation + commit/branch state only). Nothing written outside
               red_team/. No candidate reviewed.
               STATE: TERMINAL STANDBY. Next entry [16], prev_hash E15.
  entry_hash:  E15

[16] 2026-07-25
  prev_hash:   E15
  event:       VERDICT               # policy attack, Phase A — first non-DC target
  reviewer:    Red Team
  detail:      CEO tasked a Phase-A attack on PDH/PDL policy v1.1 (commit 78634d5, alpha-automation-v1,
               POLICY_PDH_PDL_v1.md), PART A (entry mechanism) only; Part B unspecified by decision, not
               attacked. Deliverable: policy_reviews/RT-POLICY-A-0001_PDH_PDL_v1.1.md. Nothing run on data;
               policy not modified; no remedy designed; verification = branch/commit state + primitive defs.
               VERDICT: PART A SURVIVES as a specification (defined, lookahead-safe, falsifiable) BUT the
               HANDOFF IS BLOCKED by a fatal-for-handoff defect:
                 F-A1 / W10 — the ratified primitives Part A is "grounded in" (code/institutional_levels.py:
                 compute_prior_day_levels, detect_level_touches, ...) are NOT in commit 78634d5's tree and
                 NOT on alpha-automation-v1. They exist ONLY on discovery-mk-matrix-v1 (verified via
                 git branch --contains 1930467 → discovery-mk-matrix-v1, not alpha-automation-v1; ls-tree of
                 78634d5 finds no such file). Same failure mode Part B openly declares (v8.5 nonexistent);
                 sibling of W9 (cross-branch, never merged). NOT a mechanism defect — the code exists and is
                 correct where it exists — but the policy's "built on ratified primitives in the repo" is
                 branch-conditional and false on its own branch; a Statistician on alpha-automation-v1 finds
                 the grounding absent. Resolution is an architecture/merge matter, not Red Team's to design.
               TARGET RESULTS: T4 lookahead PASS (available_idx=first bar of current day/Q4, 17:00-NY
               DST-aware anchor, D3_bis block reset, D7 first-touch consumption, entry@next-open — all
               verified against the actual primitives on discovery-mk-matrix-v1); T6 falsifiability PASS
               (precise mechanical rule, disconfirmable on a fixed horizon vs a matched null — a strength,
               opposite of the DC-0015/0022/0024 sample-extremum candidates); T5 circularity — no self-overlap
               in Part A (entry strictly post-trigger j+1), but an unstated interface guard is needed
               (measurement must start at entry, reuse no bar in [available_idx, j]) — W-e010; T1 post-hoc
               selection VALID but neutralised by the policy already de-privileging the 6/7 exploratory
               figure (9-way search → chance expectation ~0.56; 6/7 is not evidence) — test selection-
               corrected, W-sel; T2 level-vs-session confound UNBROKEN — needs session+level(placebo)-matched
               null, W-conf; T3 distinctness plausible (<40% overlap with most) — check the single
               highest-overlap type, W-ovl.
               HANDOFF: conditional PASS to Statistician — blocker W10 must close first; W-sel/W-conf/W-ovl/
               W-e010 are controls the Statistician applies (Red Team designs none). Integrity register: W10.
               Nothing written outside red_team/.
               STATE: awaiting CEO/Statistician routing. Next entry [17], prev_hash E16.
  entry_hash:  E16

[17] 2026-07-25
  prev_hash:   E16
  event:       VERDICT               # code attack, ratification stage 3/4
  reviewer:    Red Team
  detail:      CEO tasked ratification stage 3/4: attack ambiguity/circularity/lookahead in MK-01
               (code/market_structure.py) + MK-02 (code/liquidity_mechanics.py), commit 8edbf99 on
               discovery-mk-matrix-v1. Prior: Stage 1 Statistician 7/7 FIDEL (e642c1c); Stage 2 VE 12/12,
               mypy clean, zero executability/leakage (d586903). Deliverable:
               policy_reviews/RT-CODE-A-0001_MK01_MK02.md. No data run; modules not modified; no ratified
               decision rewritten; verification = reading the frozen code only.
               PASS: lookahead (D1) clean everywhere (confirmed_idx/available_idx discipline correct);
               D6 sweep clean (completed-bar, path-agnostic, forward-free); D3 loss positional & neutral;
               circularity none in-module (measurement window is downstream).
               FINDINGS:
                 F1 (W11) — D2 equality rejection is SELECTIVE, not neutral (answers the CEO's question):
                   strict-both-sides discards plateaus/equal-highs = exactly the equal-extreme liquidity
                   structures MK-02 exists to model (build_pools can never emit an equal-high pool). Bias is
                   regime-dependent (worst at low ATR / 2-decimal gold, the 24.8/42.9/59.7% figures), i.e.
                   confounded with the phenomenon under study. Code correct+lookahead-safe; ratification
                   cost understated. Not a bug; a standing interpretive condition on all output.
                 F2 (W12) — CONSUMPTION CASCADE, strongest finding: in detect_breaks, consuming the live
                   same-label reference re-exposes an OLDER superseded same-label swing, which emits a
                   SPURIOUS break on a later bar (reachable with 2 ascending HHs: break 100.5 then a second
                   BOS vs 100). Over-counts breaks in trends/breakouts. NOT lookahead / leakage / crash, and
                   literal D7 ("consumed by the first break that exceeds it") is satisfied — so stages 1-2
                   pass it by construction; needs a semantic test. It is a D7 AMBIGUITY (is a superseded
                   same-label swing still a live reference? code says yes; correct answer no) resolved the
                   over-counting way. Red Team flags this directly as fatal-for-correctness for detect_breaks;
                   ratification should not proceed on it until the reading is decided. No fix designed.
                 F3 — undeclared/unenforced idx-ordering precondition (VE-flagged; confirmed + EXTENDED to
                   label_structure, not just detect_breaks). Violation = silent wrong labels/breaks, no
                   exception. Canonical pipeline safe; any re-sorted/merged/hand-built list corrupts output.
                 F4 — minor: simultaneous opposite CHoCH on one bar when live_lh.price < close < live_hl.price
                   (crossed structure near a triangle apex).
                 D7 pool consumption — blocks legitimate RE-sweeps of the same level (one-shot); scope
                   limitation, compounds F1.
               HANDOFF: CEO for final ratification. Red Team does not ratify. Recommend: decide F2's reading
               before ratifying detect_breaks; record F1 + D7 as standing interpretive conditions on all
               MK-01/MK-02 output; declare+assert the F3 precondition; no action on lookahead/circularity/
               D3/D6. Integrity register: W11 (F1), W12 (F2). Nothing outside red_team/.
               STATE: awaiting CEO ratification decision. Next entry [18], prev_hash E17.
  entry_hash:  E17

[18] 2026-07-25
  prev_hash:   E17
  event:       VERDICT               # OPERATIONAL MODE — first FIFO batch
  reviewer:    Red Team
  detail:      Red Team entered OPERATIONAL MODE (continuous FIFO processing of the Candidate Queue).
               Batch RT-OPS-A-0001 (policy_reviews/RT-OPS-A-0001_batch.md). Eligible set: CAND-0001,
               CAND-0002, CAND-0003, CAND-0007. BLOCKED/not processed: CAND-0004/0005/0006 (missing
               reaction primitives). Not in handed set: CAND-0008/0009/0010. Six-dimension phase-A gate
               each (lookahead/circularity/duplicate/distinct/falsifiable/logic). No data run, no remedy,
               policies not modified; verification = reading frozen primitives + sha256 of every W10 pin.
               W10 grounding VERIFIED for all: institutional_levels c284fa2c, resample_ny 6c623737,
               market_state 823cf66a, imbalance_mechanics 45f8937e, interactions dafb4804 — all hashes
               MATCH → the RT-POLICY-A-0001/W10 co-location blocker is closed (grounding verifiable
               without co-location). No MK-01/MK-02 contamination: institutional_levels + imbalance_mechanics
               import only the inert `Block` dataclass, not the F1/F2-affected detect_swings/detect_breaks;
               market_state + interactions import neither.
               VERDICTS: CAND-0001 SURVIVED_RED_TEAM_A (carry W-sel/W-conf/W-ovl/W-e010); CAND-0002
               SURVIVED_RED_TEAM_A (compression lookahead verified in code; compression-anchoring
               definitional risk carried, self-disclosed); CAND-0003 SURVIVED_RED_TEAM_A (FVG confirmed_idx
               =i+1, reactions scanned strictly forward — cleanest); CAND-0007 SURVIVED_RED_TEAM_A (distinct
               confluence hypothesis but a strict SUBSET of CAND-0001∩CAND-0003 → carry W-incr mandatory
               incremental-value test vs each constituent; W-dilate honor after=0). 4/4 SURVIVED, 0 REJECTED.
               All carried items are Statistician-stage controls, not phase-A rejections. Part B UNSPECIFIED
               for all (standing structural-stop gap) → Statistician spec request.
               CANDIDATE QUEUE updated: the four state cells set to SURVIVED_RED_TEAM_A (the reviewing
               division sets lifecycle status, per the lifecycle model + explicit operational instruction).
               That edit is on alpha-automation-v1 (the queue's branch); this Red Team record + report are
               in red_team/. Loop idle — no further eligible candidate in the handed set.
               STATE: OPERATIONAL, loop idle. Next entry [19], prev_hash E18.
  entry_hash:  E18

[19] 2026-07-25
  prev_hash:   E18
  event:       VERDICT               # Part B attack, CAND-0001 v2.0 DEMO_BASELINE
  reviewer:    Red Team
  detail:      CEO tasked a Part-B attack on CAND-0001 PDH-PDL v2.0 (POLICY_PDH_PDL_v2.md @ 1558397,
               alpha-automation-v1). Part A not re-attacked (already SURVIVED, RT-OPS-A-0001). Deliverable:
               policy_reviews/RT-OPS-B-0001_PDH_PDL_v2.md. No data run; no alternative risk method proposed;
               policy not modified. Verification = frozen policy + docs/MIN_STOP_FLOOR_PREREG.md.
               Part B = single structural variant: stop = touch-bar extreme (low/high[touch_idx]); target =
               opposite prior-day level (PDL-long→PDH, PDH-short→PDL); resolve at first of stop/target/
               same-day time-stop; management ABSENT; sizing 1R; guards no-trade if next-open already
               beyond stop or target.
               PASS: LOOKAHEAD (all coords known at entry; the day boundary is the 17:00-NY CLOCK anchor
               via resample_ny — deterministic, NOT derived from future OHLC; closing bar observed causally);
               CIRCULARITY (stop anchored on the touch bar but measurement runs strictly touch_idx+1 forward
               — selection and measurement do not overlap); HIDDEN OPTIMIZATION (ZERO tunable numeric
               parameters → no optimization surface; justification is a general/negative fixed-ATR result,
               not a PDH/PDL fit; no results-informed sign).
               TWO DIRECT SAFETY DEFECTS (policy goes to a DEMO account):
                 S1 — same-bar stop∧target: intrabar resolution order UNSPECIFIED and the repo's own
                   worst-case convention (MIN_STOP_FLOOR_PREREG:31 — same-bar ambiguous fill → INVALID
                   EXECUTION) is NOT invoked → optimistic-fill upward bias risk on DEMO. (Also = the
                   AMBIGUITY finding.)
                 S2 — no min_executable_risk floor: the ≤0 case is guarded (no trade), but a tiny-but-
                   positive stop distance yields unbounded 1R position size; the repo floor is not applied.
                   "R-metrics sizing-invariant" does not cover a real DEMO account's margin/fills.
                 S3 (minor) — target touched-and-left earlier in the day / consumed-level-as-target not
                   handled by the at-entry guard.
               VERDICT: SURVIVED_RED_TEAM_A — CONDITIONAL, with a HARD PRE-DEMO SAFETY GATE. The mechanism
               survives every adversarial axis; the safety defects are silence, not mechanism flaws, and are
               governed by an EXISTING ratified convention (Engine v2 / MIN_STOP_FLOOR_PREREG) that Part B
               fails to bind. Gate (Statistician DEMO criteria, not a Red Team remedy): (1) intrabar
               collisions resolve worst-case / INVALID EXECUTION, not optimistic; (2) apply the
               min_executable_risk floor to 1R sizing; (3) define the target-already-visited rule. If the
               DEMO engine cannot be shown to enforce Engine-v2, the policy must NOT trade.
               HANDOFF: Statistician for DEMO criteria (carry the 3-point gate + Part-A controls). Queue
               row annotated. Nothing outside red_team/ except the queue status annotation on alpha-automation-v1.
               STATE: OPERATIONAL. Next entry [20], prev_hash E19.
  entry_hash:  E19

[20] 2026-07-25
  prev_hash:   E19
  event:       VERDICT               # OPERATIONAL MODE — second FIFO batch (Part A)
  reviewer:    Red Team
  detail:      Batch RT-OPS-A-0002 (policy_reviews/RT-OPS-A-0002_batch.md). Part A of CAND-0008
               (VOID-DISPLACEMENT), CAND-0009 (LEVEL-BREAK-DRIVE), CAND-0010 (FVG-STACK-DENSITY),
               policies @ 32236fd on alpha-automation-v1. Part B UNSPECIFIED for all three — not attacked.
               No data run; policies not modified; no remedy.
               W10 HASHES recomputed, all MATCH: order_block_void 6ec7adbf (new); institutional_levels
               c284fa2c, market_state 823cf66a, imbalance_mechanics 45f8937e, interactions dafb4804
               (re-confirmed). MK-01/MK-02 CONTAMINATION CHECK (imports read at 8edbf99): order_block_void,
               market_state, interactions import neither; imbalance_mechanics + institutional_levels import
               ONLY the inert Block dataclass, not the F1/F2-defective detect_swings/detect_breaks. None of
               the three inherits F1/F2. New primitives verified causal: detect_liquidity_voids (void on
               c→c+1, known at c+1), price_in_any_zone (element-wise, no future).
               VERDICTS (3/3 SURVIVED_RED_TEAM_A, 0 REJECTED):
                 CAND-0008 — clean; distinct from CAND-0004 (void alone, untestable) and CAND-0002.
                   (Note: void size term is a fixed $1.20 ratified constant — standing characteristic.)
                 CAND-0009 — distinct (break-continuation, opposite thesis to CAND-0001) but ONE-SIDED
                   boundary: it overlaps CAND-0001 on displacement-touch bars and takes the OPPOSITE side
                   there; CAND-0009 excludes reversals but CAND-0001 does NOT exclude breaks. Carry
                   W-partition (Statistician decide mutual exclusion) + W-dir-mask (confluence expression
                   should be direction-aligned; prose is clear, expression under-specifies).
                 CAND-0010 — distinct (same-polarity FVG density) but a strict SUBSET of CAND-0003 (every
                   trigger is a CAND-0003 CE-50 reaction + density). Carry W-incr (test density's
                   incremental value vs single-FVG CAND-0003, same pattern as CAND-0007).
               All carried items are Statistician-stage controls, not phase-A rejections.
               Lookahead/circularity/falsifiability/logic PASS for all three (verified in code).
               Queue: state cells for CAND-0008/0009/0010 set to SURVIVED_RED_TEAM_A.
               NOTE (surfaced, not processed): the queue has since added CAND-0011/0012/0013, marked
               queued→Red Team (A) — a NEW batch, not in this turn's handed set (0008/0009/0010). Flagged
               for the next FIFO tick; not processed here (not handed, policies not yet read).
               Also observed: Statistician bound the RT-OPS-B-0001 S1/S2/S3 safety gate as executable
               preconditions (STAT-CAND0001-DEMO-CRITERIA-v1.0) — the Part-B condition was carried verbatim.
               STATE: OPERATIONAL, handed batch done. Next entry [21], prev_hash E20.
  entry_hash:  E20

[21] 2026-07-25
  prev_hash:   E20
  event:       VERDICT               # OPERATIONAL — Phase B batch (CAND-0002/0003/0007)
  reviewer:    Red Team
  detail:      Batch RT-OPS-B-0002 (policy_reviews/RT-OPS-B-0002_batch.md). Part B only, policies @ de31dcc.
               Part A not re-attacked. Same targets as RT-OPS-B-0001. No data run; policies not modified;
               no risk method proposed.
               ALL THREE: lookahead PASS (all Part-B coords known at entry; event-exits observed strictly
               forward), circularity PASS (stop anchored on trigger bar but measurement runs entry+1 forward
               — disjoint), hidden-optimization PASS (zero tunable numeric parameters; CAND-0003 R:R≈1 is a
               midpoint-geometry consequence, not chosen). S1 (intrabar "first of" order) unspecified in all
               three — severity differs.
               PER CANDIDATE:
                 CAND-0002 (stop=opposite extreme of expansion bar; exit=first opposing expansion) —
                   SURVIVED_RED_TEAM_A conditional. CEO Q "can the opposing expansion be absent?": YES →
                   fallback is the BLOCK boundary → Finding H: trade can hold to block-end (weeks); much
                   longer horizon than CAND-0001/0007's day time-stop; DEMO must weigh margin/gap exposure.
                   S2 IMMUNE (expansion bar guarantees a wide stop). S1 mild (stop precedes next-open exit).
                 CAND-0003 (stop=FVG far edge/Q4; target=FVG near edge) — SURVIVED_RED_TEAM_A conditional,
                   TIGHTEST GATE. CEO Q "can the distance be arbitrarily small?": YES — stop = ce_50 − lower
                   = FVG_height/2, arbitrarily small for small FVGs → S2 LIVE and ROUTINE (unbounded 1R).
                   S1 ACUTE — stop and target are the two edges of one (small) FVG, one bar routinely spans
                   both. If the floor + worst-case cannot be enforced, CAND-0003 must NOT trade.
                 CAND-0007 (stop=min/max below BOTH structures; exit=opposite day level + day time-stop) —
                   SURVIVED_RED_TEAM_A conditional. CEO Q "wider stop vs min_executable_risk floor?": the
                   deeper-of-two stop is WIDER → rarely hits the floor → PROTECTIVE vs S2 (opposite of
                   CAND-0003). Flip side (risk-quality, not safety): a very wide stop can give R:R<1 vs the
                   opposite-level target. S1 rare (needs a bar spanning the daily range).
               3/3 SURVIVED_RED_TEAM_A (conditional), 0 REJECTED. Every safety item is governed by the
               EXISTING DEMO convention already bound for CAND-0001 (STAT-CAND0001-DEMO-CRITERIA-v1.0:
               worst-case hierarchy + min_executable_risk floor). Handoff: Statistician DEMO criteria, apply
               the same gate with per-candidate emphasis (0002 block-horizon rule; 0003 floor is routine →
               if unenforceable don't trade; 0007 R:R<1 note). Queue Part-B cells annotated.
               STATE: OPERATIONAL. Next entry [22], prev_hash E21.
  entry_hash:  E21

[22] 2026-07-25
  prev_hash:   E21
  event:       VERDICT               # OPERATIONAL — Phase A+B single pass, CAND-0011..0019 (9)
  reviewer:    Red Team
  detail:      Batch RT-OPS-AB-0003 (policy_reviews/RT-OPS-AB-0003_batch.md). Nine candidates, Part A (v1)
               + Part B (v2), policies @ 0806d00. No data run; policies not modified; no risk method.
               W10: order_flow 728fa557 verified (new); others re-confirmed — all match. MK-01/02: clean
               (order_flow imports only order_block_void + market_state.atr14; confluences add only inert
               Block + interactions) — none inherits F1/F2. order_flow causality verified (forward-only,
               formation_idx=i-1, _scan from +2, CEO anti-E010 disjoint windows, Research-Lab-verified).
               DIRECTIVE-BLOCK reconciled: the stale "OB family directive-BLOCKED" header is superseded by
               the CEO ruling "order_flow re-engineered primitives unblocked" (E010/E013/E015/E016 blocked
               as HYPOTHESES; MK-01/02 DRAFT-forbidden). None of the nine is the blocked E010 breaker-
               continuation. Batch clear.
               PHASE A: all 9 SURVIVED (lookahead/circularity/falsifiable/distinct PASS). Batch is a
               base×second-structure lattice: bases OB-Rejection(0011)/OB-Mitigation(0014)/Demand-Zone(0013);
               six confluences each a strict SUBSET of a base (0012/0015/0018⊂0011; 0016⊂0014; 0017/0019⊂0013)
               → W-incr mandatory (test incremental value vs base + vs second structure). Grows the
               multiple-testing family (already =7 cumulative).
               PHASE B: lookahead/circularity/hidden-opt PASS all. S1 unspecified all (existing convention).
               S2 structurally LOW (OB/zone stops anchored to large E010 impulse-bar extremes — inherently
               wide; the CAND-0003 tiny-stop problem does not arise). Possible R:R<1 on deeper stops — note.
               SEVERE — FINDING H' (block-only time-stop → live exit DISAPPEARS): per the Statistician, a
               block is a discovery-data construct, so a block-boundary time-stop NEVER fires live. SIX
               candidates have block-only fallback and thus NO live-valid time-stop — a position that can
               never close if neither stop nor target-zone-edge is hit: CAND-0011, 0013, 0014, 0015, 0017,
               0018. THREE are safe (day time-stop exists live): CAND-0012, 0016, 0019 (level-bearing).
               READ-ACROSS: this WORSENS CAND-0002 too (its expansion block time-stop is likewise inert
               live) — recommend re-opening CAND-0002.
               VERDICTS: all 9 SURVIVED_RED_TEAM_A (Phase A); Part B all CONDITIONAL; 0 REJECTED. The six
               H'-candidates carry a HARD GATE: DEMO criteria must bind a live-valid time-stop, else do not
               trade. HANDOFF: Statistician protocol + DEMO criteria (hard gate; S1/S2 existing gate;
               W-incr; multiple-testing family; doc fix for the stale block header).
               STATE: OPERATIONAL. Next entry [23], prev_hash E22.
  entry_hash:  E22

[23] 2026-07-25
  prev_hash:   E22
  event:       VERDICT               # re-attack of the F2/F3 remediation (ratification stage 3, repeated)
  reviewer:    Red Team
  detail:      CEO tasked a re-attack of the F2/F3 remediation of market_structure.py @ f4f8fab (vs the
               attacked 8edbf99). Do not reopen D2/D7; liquidity_mechanics untouched. Deliverable:
               policy_reviews/RT-CODE-A-0002_MK01_F2F3_remediation.md. No data run; verification = diff +
               remediated functions + regression tests read.
               WHAT CHANGED: F2 = NO code change (consumption loop byte-identical; only a docstring
               ratifying "each distinct swing → one break"; a re-verification, not a repair). F3 = real,
               well-scoped: _assert_ordering_precondition added to the top of BOTH label_structure and
               detect_breaks (my RT-CODE-A-0001 F3 extension, implemented), fail-closed on 4 invariants.
               VERDICT: the remediation SURVIVES. F2 re-arm verified correct (test_c1_c7: bars 10-14 over
               ref idx=7 → 1 BOS; test_c2 consumed-not-reactivated; test_c4 bull/bear symmetric) — docstring-
               only so no regression risk. F3 extension correctly implemented + tested on both consumers.
               NO new code defect introduced.
               TWO FINDINGS (neither blocks ratification):
                 (1) F3 OVER-STRICT (answers CEO's question — YES it can reject legitimate inputs): the
                     precondition enforces GLOBAL idx-ordering, but both consumers only USE per-block order
                     (they segregate by block_index). A per-block-sorted but globally-interleaved list
                     (detect_swings called with blocks out of start-order, or concatenated outputs) is
                     rejected with ValueError though it would process correctly. LOW severity (canonical
                     pipeline never trips it; fail-closed = safe), untested (all F3 tests single-block).
                 (2) NEW — cascade break MIS-TIMING (within ratified count-semantics, NOT reopening D7): the
                     one-break-per-bar loop records older stacked swings' breaks 1..N-1 bars LATE (HH_a=100
                     exceeded at bar c but its break recorded at c+1 after HH_b=110 consumes bar c). Count is
                     ratified; TIMING is an unratified consequence. Reachable; downstream break-timing users
                     affected. Untested — no test sustains a close above ≥2 stacked same-label swings
                     (test_c3 separates its breaks in time, never exercising the cascade).
               COVERAGE: suite solidly covers re-arm + F3 core; gaps = sustained cascade (existence+timing)
               and the per-block-vs-global precondition edge; F4 (simultaneous opposite CHoCH, RT-CODE-A-0001)
               remains OPEN but OUT OF SCOPE for this remediation.
               HANDOFF: CEO for final MK-01/MK-02 ratification. Before ratifying, decide (a) is cascade break
               TIMING acceptable (D7 settled count, not timing); (b) is the GLOBAL precondition scope intended
               or should it match the consumers' PER-BLOCK requirement. Red Team designs no fix; reopens
               neither D2 nor D7; liquidity_mechanics not re-attacked. Nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [24], prev_hash E23.
  entry_hash:  E23

[24] 2026-07-25
  prev_hash:   E23
  event:       VERDICT               # re-attack of the MK-01 cascade break semantics (stage 3, third pass)
  reviewer:    Red Team
  detail:      CEO tasked a re-attack of the cascade break semantics @ 0000225 (vs f4f8fab). Targets:
               BOS∧CHoCH co-occurrence, order, F4. Do not reopen D2/D7-pools/F3; liquidity_mechanics
               untouched. Deliverable: policy_reviews/RT-CODE-A-0003_MK01_cascade_semantics.md. No data run.
               CHANGE: per bar c, ALL active unconsumed swings exceeded by close[c] → hits, sorted DESCENDING
               by idx, one break each at c (both delay vectors fixed: single-slot live_* + intra-direction
               if/elif that SUPPRESSED-and-LOST a same-bar CHoCH). Delivers what D7 already specified; only
               the recording bar changes. My RT-CODE-A-0002 mis-timing finding is RESOLVED. Statistician
               measured 40.9% of break-bars carry ≥2 breaks; 542 references were lost outright under old.
               VERDICT: cascade semantics SURVIVES (count now conserved; emission sound).
               TARGET 1 (BOS∧CHoCH same bar): NOT double-counting (distinct refs/labels, count conserved) —
                 confirmed. Flag: the co-broken pair is often NESTED/dependent (breaking a higher HH implies
                 breaking a lower LH) → downstream counting CHoCH as reversals over-counts in continuations.
               TARGET 2 (order) — FINDING: the "descending-idx keeps the same first reference → strictly
                 TIMING not reference" claim is INACCURATE for the ≥2-break/lost-break population. Old
                 suppressed-and-lost the LH CHoCH so _first_break_after returned the surviving BOS ref; new
                 DELIVERS the LH and, being higher idx, emits it FIRST → _first_break_after returns a DIFFERENT
                 reference+kind. Demonstrable from the code's OWN test_bos_and_choch_same_bar (new br[0]=ref13;
                 old would surface ref8). Holds for same-label cascades, FAILS for cross-kind lost-break.
                 CAVEAT: _first_break_after is NOT in this commit (downstream, e.g. trading_strategies.py
                 s2/s3/s10/s11) — recommend verifying first-reference stability there before relying on
                 "timing-only". This aligns with the earlier note that S2/S3/S11 are affected in principle.
               TARGET 3 (F4 opposite CHoCH): surface GREW (all-hits evaluates every swing) as the Statistician
                 warned; simultaneous CHOCH_BULL∧CHOCH_BEAR / BOS∧opposite-CHoCH now more frequent. NOT a
                 count/consumption defect (distinct refs) but emits contradictory same-bar signals; needs a
                 downstream interpretation rule; does NOT block the cascade fix. Still open, now in scope.
               COVERAGE: solid on the core (sustained cascade, lost-CHoCH-delivered, same-bar distinct refs,
                 descending order). NOT exercised: F4 simultaneous OPPOSITE breaks; the _first_break_after
                 preservation claim (order tested, selection not); aggregate count conservation over a complex
                 series; cross-direction order edge (bearish highest-idx displacing a bullish first); high
                 multiplicity (max-24 measured, tests use ≤3).
               HANDOFF: CEO for MK-01/MK-02 ratification. Before ratifying: (a) verify first-reference
               stability vs the real downstream consumers (not in this commit); (b) decide the F4
               contradictory-signal rule; (c) add the four missing tests. Red Team designs no fix; reopens
               nothing forbidden; liquidity_mechanics not re-attacked. Nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [25], prev_hash E24.
  entry_hash:  E24

[25] 2026-07-25
  prev_hash:   E24
  event:       VERDICT               # code attack, session_levels.py (MK-04 sessions)
  reviewer:    Red Team
  detail:      CEO tasked an attack on code/session_levels.py @ bf02dd2. Targets: lookahead/D3_bis/D7/
               ambiguity + Mid, primitive-B saturation, straddle, backtest↔live. Deliverable:
               policy_reviews/RT-CODE-A-0004_session_levels.md. No data run; module not modified; no remedy.
               Contamination: imports only Block (inert) + session_of + _runs — no MK-01/MK-02 F1/F2.
               session_of = fixed UTC-hour buckets (asia<8/london<13/ny<21/late).
               VERDICT: module SURVIVES. Lookahead PASS (verified per field: level=closed-session max/min/mid,
               available from the next session, touches scanned forward; future-mutation test confirms).
               D3_bis PASS (per-block; A skips block's first session, B caps expiry at block end, no cross-
               block window). D7 PASS (both detectors break at first touch; count_active deactivates at
               min(touch,expiry)).
               T1 Mid: SURVIVES. Containment low≤Mid≤high correct; "covers but doesn't trade" cannot happen
                 for a real bar (range traversed). FLAG: degenerate zero-range session (max=min) → High=Low=Mid
                 coincide → three coincident un-deduped levels/touches; untested.
               T2 Primitive B saturation (median ~89, max 188 active): stated DIRECTLY — B WITHOUT A FILTER
                 IS GUARANTEED TO DILUTE ("reaction at a level" unfalsifiable-by-saturation; the DZ×FVG
                 18,275/−$2,432, CAND-0020 34,006/−15,409R, CAND-0024 18,852/−2,605R loss pattern). Primitive
                 A (2-3) clean. B survives as a primitive (correct/lookahead-safe/D7) but HARD CONDITION: no
                 candidate on B without a filter bounding the active-level count; the module's own
                 count_active_persistent_levels precondition exists for exactly this.
               T3 Straddle (8.32% cross a day boundary): SPECIFIED, not ambiguous — sessions segmented by
                 session_index (session_of UTC), NOT day_index, so a straddling session is one run assigned
                 to its session, never split; the old/new-day question does not arise. No defect.
               T4 Backtest↔live: session_of uses fixed UTC hours; the 21 UTC boundary sits at the OANDA pause
                 (20-21), MT5 differs +3h/23:45 weekend. The UTC label is feed-independent but the BAR SET in
                 a session differs by feed → different High/Low/Mid → an OANDA-validated edge may not reproduce
                 on MT5. CORRECTNESS-OF-TRANSFER (transferability), not mere interpretation; NOT a module defect
                 (pure function). Affects EVERY future session-levels candidate (none yet); attach at creation.
               COVERAGE (7 tests): solid on A/B semantics + lookahead + D3_bis + D7 + exceedance/containment.
                 Gaps: degenerate coincidence; saturation scale (measurement); feed-alignment (cross-feed) —
                 latter two not unit-testable.
               HANDOFF: CEO ratify (sound); bind at candidate creation — (1) primitive B requires an
                 active-level filter (reject B-candidates without one); (2) feed-alignment transferability
                 warning on every session-levels candidate; consider a degenerate-coincidence test. Then Alpha
                 builds candidates. Red Team designs no fix; reopens nothing. Nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [26], prev_hash E25.
  entry_hash:  E25

[26] 2026-07-25
  prev_hash:   E25
  event:       VERDICT               # OPERATIONAL MODE — Phase A+B, session candidates CAND-0026..0031
  reviewer:    Red Team
  detail:      CEO tasked Phase A + Phase B in one pass on the six session-level candidates
               CAND-0026..0031 @ policy commit 0ce1e57 (alpha-automation-v1), like the 0011-0019 batch.
               Deliverable: policy_reviews/RT-OPS-AB-0004_session_batch.md. No data run; policies not
               modified; no remedy.
               GROUNDING (recomputed, all MATCH): all six pin session_levels @ bf02dd2 = 2af2b9e6 (and it
                 hashes to the empty-file value on alpha-automation-v1 → correct not-co-located W10 pin).
                 market_state 823cf66a / institutional_levels c284fa2c / interactions dafb4804 /
                 imbalance_mechanics 45f8937e / order_flow 728fa557 re-confirmed.
               market_structure/liquidity_mechanics CHANGE (0000225→bf02dd2): CLEANLY handled — NO candidate
                 cites either file; session_levels's only transitive touch of market_structure is the Block
                 dataclass, UNCHANGED across that window (verified empty diff); the 6-line change is in break
                 logic (not Block, not used here). No MK-01/MK-02 F1/F2 logic reaches any candidate.
               SWEEP COMPOSITION (CAND-0026): CORRECT — no detect_session_sweeps exists; Alpha composed
                 penetration (high[j]>=price) AND close-back-inside (close[j]<price), close-beyond→NO TRADE
                 fail-closed = faithful PDH/PDL sweep-reject signature. Inherited (not a defect): consume-at-
                 first-penetration (D7) → break-then-sweep sequences not detected; recall limitation, disclose.
               MID DIRECTION (CAND-0028): DISCLOSED choice, not hidden — policy declares direction by approach
                 side (close[j-1]>Mid→LONG, <→SHORT) and explicitly labels it an ASSUMPTION for RT/Statistician;
                 close[j-1]==Mid → NO TRADE (fail-closed) verified. Approach-side rule = load-bearing untested
                 assumption → Statistician must test its edge.
               FINDING H' (block-only time-stop): ABSENT this batch — every candidate has a LIVE-VALID
                 time-stop (session boundary expiry_idx, or day boundary 17:00-NY for CAND-0029). No H'.
               WEEKLY-STRUCTURE SIGNAL: CAND-0026/0027/0029/0030/0031 inherit the touched-by-rallying-up vs
                 short-bias anti-correlation (SESSION_HIGH reached by going UP, faded SHORT = PWH/PWL pathology);
                 milder than daily per the Statistician's own period-length prediction — SIGNAL, measure per
                 session. CAND-0028 (Mid, containment, no exceedance, no intrinsic side) EXEMPT.
               W-incr (mandatory): CAND-0026 ⊂ 0027; 0029 ⊂ 0027∩0001; 0030 ⊂ 0027∩0003; 0031 ⊂ 0027∩0011.
               PART B: lookahead/circularity/hidden-optimization PASS (zero tunable params). S1 intrabar order
                 carried to the existing DEMO convention. S2 min_executable_risk floor: routine on the bases
                 (0026/0027/0028 touch/containment-extreme stops), rarely binds on the confluences (wider
                 min/max stops). Feed-alignment transferability warning (RT-CODE-A-0004) present in all six.
               VERDICTS: 6 processed, 6 SURVIVED_RED_TEAM_A, 0 REJECTED — all Part B CONDITIONAL on the
                 existing DEMO gate (S1 worst-case + min_executable_risk floor).
               HANDOFF: Statistician — protocol + DEMO criteria; carry W-incr, the weekly-structure signal,
                 the CAND-0028 approach-side assumption test, the feed-alignment warning, the sweep recall note.
                 Multiple-testing family grows. Red Team modified no policy, ran no data, proposed no risk
                 method. Nothing outside red_team/ (queue annotation only).
               STATE: OPERATIONAL. Next entry [27], prev_hash E26.
  entry_hash:  E26

[27] 2026-07-26
  prev_hash:   E26
  event:       VERDICT               # OPERATIONAL MODE — Phase A+B, Primitive-B candidates CAND-0032..0036
  reviewer:    Red Team
  detail:      CEO tasked Phase A + Phase B in one pass on the five PERSISTENT (Primitive-B) session
               candidates CAND-0032..0036 @ policy commit ac9f4ab. Primitive B was FORBIDDEN by my
               RT-CODE-A-0004 without a filter bounding active levels; first B use, gated on the
               Statistician's composed ATR-proximity filter. Deliverable:
               policy_reviews/RT-OPS-AB-0005_persistent_session_batch.md. No data run; policies not
               modified; no remedy.
               GROUNDING (recomputed, all MATCH): session_levels 2af2b9e6 @ bf02dd2, market_state 823cf66a,
                 institutional_levels c284fa2c, interactions dafb4804, imbalance_mechanics 45f8937e,
                 order_flow 728fa557.
               T1 FILTER |level.price − close[j−1]| ≤ k·atr14[j−1]: COMPOSITION CORRECT, LOOKAHEAD-FREE.
                 Verified at market_state.py@bf02dd2 — atr14[i]=rolling-14 mean of tr[i−13..i], strictly
                 causal ⇒ atr14[j−1] complete before bar j; close[j−1] complete; level.price from a closed
                 prior session. Precedent-bar denominator matches the ratified `expansion` convention
                 verbatim. RT-CODE-A-0004 SATURATION CONDITION FORMALLY MET (188→6 active, median 0, 83.6%
                 empty, falsifiability restored) — the unfalsifiable-by-saturation defect is CURED.
               T2 OWN SELECTIVITY (real vs decorative): 0032 sweep=REAL (close-back-inside ⊂ touch);
                 0034/0035/0036 confluence=REAL (second independent reference); 0033 Mid containment =
                 THINNEST, claim "materially rarer than 8,833" is ASSERTED-not-measured — for a filter-
                 eligible directionless line a straddling bar ≈ a plain touch ⇒ 0033 is the candidate most
                 exposed to volume-dilution (DZ×FVG pattern); containment-count report is decisive. Not a
                 rejection (falsifiable, fail-closed).
               T3 HORIZON 20-bar GROUP_A_HORIZON: live-valid (fixed bar count, not stale-session-dependent);
                 shared constant (uniform across S01/S09/S11/... + queue), NOT per-candidate tuning; 0034
                 uses the day boundary. FLAG: 20 is a fresh-setup Group-A constant, its fit for an aged-level
                 family is unmeasured (spec question, not a defect).
               T4 HELD plain-touch-B: refusal CORRECT, hides nothing — plain touch on aged B carries only
                 the filter ⇒ the pure ≈8,833/4-per-day dilution loser; its only standalone selectivity IS
                 the sweep (=0032). Consequence: the confluences rest ENTIRELY on the confluence (no sweep);
                 no standalone plain-B-touch arm ⇒ W-incr vs the other constituent or 0032.
               T5 0032 ⊂ 0027? NO. Different primitives (B persistent vs A prior); level sets overlap only
                 at the youngest session-level during A's brief life; triggers differ (sweep ⊂ touch) on a
                 DIFFERENT population; largely DISJOINT. 0032 must NOT be scored as an increment over 0027;
                 disjointness keeps BH-FDR valid.
               FINDING H': ABSENT — all time-stops live-valid (20-bar horizon / day boundary); Alpha
                 correctly rejected the stale source-session boundary.
               PART B: lookahead/circularity PASS; hidden-opt PASS with condition (k=1.0 primary chosen on
                 the level-count distribution not returns; k=0.5/2.0 pre-declared sensitivities MUST be run).
                 S1 → existing DEMO worst-case convention. S2: 0032/0033/0034 exposed→bind min_executable_risk
                 floor; 0035/0036 protected (min/max stops).
               WEEKLY-STRUCTURE SIGNAL — WORST HERE: 0032/0034/0035/0036 fade SESSION_HIGH/LOW; a level
                 untouched for MONTHS is the longest-period extreme ⇒ touched-vs-short anti-correlation is
                 MAXIMAL (inverts my earlier session<daily prediction for the aged population). The
                 persistence that makes B attractive maximizes the pathology. 0033 (Mid) EXEMPT.
               CENTRAL QUESTION: the filter condition is FORMALLY MET (saturation cured); "4/day too much"
                 is a DIFFERENT, MEASURABLE failure mode (volume-dilution), per-candidate, not a Red Team
                 defect — Red Team does not reject on it; 0033 most at risk.
               VERDICTS: 5 processed, 5 SURVIVED_RED_TEAM_A, 0 REJECTED — all Part B CONDITIONAL on the
                 existing DEMO gate (S1 worst-case + min_executable_risk floor) + the trigger-count report.
               HANDOFF: Statistician — protocol + DEMO criteria; carry the trigger-count gate (decisive for
                 0033), the k=0.5/2.0 sensitivities, the WORST-here weekly signal, W-incr (no plain-B-touch
                 arm; 0032 disjoint from 0027), the 0033 approach-side assumption, the unmeasured-horizon
                 flag, the feed-alignment warning. Red Team modified no policy, ran no data, proposed no risk
                 method. Nothing outside red_team/ (queue annotation only).
               STATE: OPERATIONAL. Next entry [28], prev_hash E27.
  entry_hash:  E27

[28] 2026-07-27
  prev_hash:   E27
  event:       VERDICT               # OPERATIONAL MODE — Phase A+B, CAND-0006 reformulated (PWH/PWL v2, Route 3)
  reviewer:    Red Team
  detail:      CEO tasked an attack on CAND-0006 reformulated @ policy commit b636f29,
               POLICY_WEEKLY_LEVELS_v2.md. v1 was NOT_CURRENTLY_TESTABLE; Statistician v2.7.40 (e68e0cd)
               proved the block was THESIS not detector (572 weekly → 275 touched/48.1% healthy → 6
               bias-aligned/2.2% collapse). v2.0 = Route 3: remove the bias stage, direction from level
               kind (WEEKLY_HIGH→short, WEEKLY_LOW→long); population back to 275. Deliverable:
               policy_reviews/RT-OPS-AB-0006_weekly_levels_v2.md. No data run; policy not modified; no remedy.
               GROUNDING: institutional_levels.py @ bf02dd2 = c284fa2c (MATCH; identical at 0000225).
                 Weekly uses derive_week_index (17:00-NY day_ordinal + weekend gap), NOT session_of — the
                 session feed-alignment warning does not transfer verbatim (day-boundary family, feed-robust).
               T3 COMPOSED TOUCH: composition CORRECT, lookahead-free. Verified detect_level_touches SKIPS
                 weekly (`if kind not in (PDH,PDL): continue`, same-day window). Alpha composed penetration
                 (high[j]>=price / low[j]<=price) + D7 consume-once over the derive_week_index week window
                 [available_idx, end of current week]. compute_prior_week_levels: level=max/min over PRIOR
                 week weeks[k-1], available_idx=weeks[k][0] (current week first bar) → known before use, no
                 lookahead; range(1,len(weeks)) → first week per block UNCLASSIFIED (D3_bis). Faithful mirror.
               T4 PARTIAL WEEKS: COMPLETE-only gate VERIFIED via the ratified flag (completeness="COMPLETE"
                 if n_days>=5, computed INSIDE compute_prior_week_levels on source-week distinct day_index;
                 policy only gates; no invented threshold; no lookahead — source week fully past). Exclusion
                 is a LEGITIMATE population definition (structural, pre-data), NOT a performance bias — but
                 NOT frequency-neutral: partial (holiday) weeks have narrower range → closer to price →
                 touched MORE, so excluding shifts to wider/less-touched levels ⇒ DISCLOSE the conditioning
                 (edge measured on COMPLETE subpopulation only); optional robustness = measure partials
                 separately. Not a defect.
               T5 HORIZON: week boundary (last bar of current week, week_index) — live-valid, weekly analog
                 of the PDH/PDL day-boundary time-stop. NOT the 460-bar survey window (that was a measurement,
                 not a trade rule — correctly unused). No Finding H' (week boundary live-valid, unlike the
                 persistent-B stale source session).
               T2 DIRECTION FROM KIND: fade is an ASSUMPTION, not measured. The CAND-0028 inverse-test
                 requirement APPLIES and is DECISIVE here. Difference from 0028: a weekly HIGH/LOW is a
                 real S/R (fade = the screening-POSITIVE level-fade grammar of CAND-0001/0027) ⇒ a transfer
                 test, not a coin-flip. Amplifier: the anti-correlation that collapsed the bias version (high
                 reached by rallying up, shorted) is a reason to doubt fade transfers to weekly, where a
                 bigger level may more often be reached by CONTINUING momentum. Test WEEKLY_HIGH→short vs
                 →long (Route 2, the declined alternative = the null).
               T1 WHAT BIAS-REMOVAL LOSES (+ remove-or-move): bias did two things — (a) contradicted the
                 geometry (correctly deleted), (b) MIGHT have filtered break-through touches, value UNKNOWN
                 (n=6 never measurable). Route 3 SIDESTEPS (b) by adopting the family no-filter default. So
                 the reformulation REMOVES the bias-collapse MECHANISM but MOVES the underlying anti-
                 correlation into the fade DIRECTION, where it is measurable not blocking. Progress
                 (untestable→testable), but the direction assumption now carries the whole bet.
               CROSS-BATCH: does not ESCAPE the weekly-structure problem, RELOCATES it — consistent with my
                 period-length prediction (session mild, daily moderate, persistent-B WORST; weekly between
                 daily and persistent). The policy's session cross-check is CORRECT for the bias-collapse
                 MECHANISM (0026-0031 have no bias stage) but that is distinct from the anti-correlation,
                 which is family-wide (I flagged it milder-at-session RT-OPS-AB-0004, worst persistent-B
                 RT-OPS-AB-0005); weekly severity intermediate.
               STANDARD/PART B: lookahead PASS; circularity PASS; NOT a subset (weekly period population
                 disjoint from daily 0001 / session 0027 — distinct primitive; no W-incr; Statistician MAY
                 group {0001,0027,0006} as one level-fade FDR family); falsifiability INTACT without a
                 density filter (275 sparse, far below Primitive-B saturation). S1 → DEMO convention. S2
                 exposed (touch-bar-extreme stop) → bind min_executable_risk floor. Hidden-opt PASS (no
                 tunable params; completeness>=5 is the ratified D-WEEK flag; Route choice = pre-registered
                 thesis before results, not numeric tuning).
               VERDICT: SURVIVED_RED_TEAM_A — Part B CONDITIONAL (existing DEMO gate). Reformulation correct
                 and disciplined; makes the problem TESTABLE, does NOT solve it; direction assumption (T2) is
                 the decisive open item.
               HANDOFF: Statistician — protocol + DEMO criteria; carry the inverse-direction test (decisive),
                 the COMPLETE-only conditioning disclosure, the {0001,0027,0006} FDR family option, the
                 intermediate weekly-structure severity, the S2 floor. Red Team modified no policy, ran no
                 data, proposed no risk method. Nothing outside red_team/ (queue annotation only).
               STATE: OPERATIONAL. Next entry [29], prev_hash E28.
  entry_hash:  E28

[29] 2026-07-28
  prev_hash:   E28
  event:       AUDIT                 # END-TO-END CHAIN AUDIT (pipeline, not a candidate)
  reviewer:    Red Team
  detail:      CEO tasked a first-ever end-to-end chain audit: find assumptions that propagated from Alpha
               to the DEMO order unattacked. Deliverable: policy_reviews/RT-AUDIT-CHAIN-0001_end_to_end.md.
               Method: six parallel evidence sweeps + Red Team re-read every code claim at source. No data
               run; nothing modified; no remedy.
               HEADLINE (result-invalidating check): NOTHING promoted/validated ⇒ almost nothing to
                 invalidate, and the chain FAIL-CLOSED before live. Task premise CORRECTED: no CAND-xxxx has
                 ever placed a live DEMO order — VE BLOCKED CAND-0001 ("NU tranzacționează pe DEMO", mstrat
                 couldn't be shown to enforce S1/S2/S3); the gate worked. Only real DEMO order = BTCUSD from
                 a different pilot (AI-Trader line). All assumption-carrying candidates still SCREENING.
                 Two result-shaped items already void + on record: DC-0004 (holdout consumed), ALPHA_REGISTRY
                 passed_stat (invalid analytic p, stamped stale). One OPEN latent invalidator: W9 matched-null
                 two-state (RESOLVED flow-c-foundation / OPEN statistician-foundation; VE rebuilt a less-
                 complete F6 without drift-beta) — no promoted result rests on it yet.
               DEFECT C-D1: dynamic_exit_engine.py:6-7,37,67 sets time-stop = BLOCK boundary = un-remediated
                 Finding H' (CAND-0002 class); never remediated at policy level (session/persistent were);
                 DEMO exit not live-faithful. Same DemoSignal.day_end_idx = day boundary in pdh_pdl engine
                 vs block boundary here. Pre-live. Red-Team-verified at source.
               RISK C-R1: demo_gate_engine/ (enforces S1/S2 made hard by 6 verdicts) built AFTER ledger
                 closed [28], NEVER independently attacked — VE self-verifies its own gate (self-verification
                 loop). pdh_pdl engine spot-read CLEAN (day-boundary live-valid, S1/S2/S3 present) but not
                 deeply attacked. Highest structural gap.
               RISK C-R2: statistical stack (matched_null/mn_*/pilot_pvalue/scoped_fdr/synth_price/wp5) zero
                 code attack; W9 HIGH defect still OPEN on official line; every batch defers to "BH-FDR valid"
                 unaudited.
               RISK C-R3: mstrat.py::simulate produced EVERY candidate metric, enforces no gates, never
                 attacked ⇒ all SCREENING numbers are pre-gate.
               RISK C-R4: data/context derivation (resample_ny 17:00-NY anchor, build_gc_bars, M15_v2 context,
                 Block CONSTRUCTION) never audited; every lookahead proof assumes it; VERIFY_M15_v1_DEFECTIVE
                 history exists.
               RISK C-R5: 6 of 9 ratified primitives hash-pinned only; the deeply-attacked 7th
                 (market_structure) yielded W11+W12 ⇒ symmetric unexamined surfaces; institutional_levels
                 underpins CAND-0001 (DEMO pilot), market_state.atr14 underpins every S2 floor + ATR filter.
               RISK C-R6: trading_strategies.py never attacked despite my own [24] "verify first-reference
                 stability before relying on timing-only."
               RISK C-R7: dynamic_exit_engine.py:71 open_[j+1] on undeclared precondition day_end_idx<=n-1
                 (F3-class), no internal assertion; safe under contract, latent. (Verified; the parallel
                 "dropped target guard" claim checked and REJECTED — dynamic-event exit has no target price.)
               RISK C-R8: feed-alignment ~3h magnitude unmeasurable in-repo (no MT5 data; not authorized) —
                 irreducible transferability assumption, correctly disclosed.
               UNDOCUMENTED C-U1: queue labels overstate readiness — DEMO_BASELINE on 0001/0002/0003/0007/0009
                 reads live-ready but none live, 0001 BLOCKED, 0009 has label w/ NO DEMO-criteria doc;
                 live-design doc names CAND-0019 in the live set but it's SCREENING-only w/ no policy artifact.
               UNDOCUMENTED C-U2: DEMO-criteria coverage uneven (dedicated 0001; batch-inherited 0002/0003/
                 0007; none 0009/0019); no roster.
               UNDOCUMENTED C-U3: stale v1 policies (POLICY_OB_MITIGATION_v1) keep the inert block-boundary
                 time-stop on disk beside the v3 fix.
               UNDOCUMENTED C-U4: namespace collisions — Q4/Q5/Q6 differ MK-04 vs MK-03 (only Q5 aligns);
                 day_end_idx day-vs-block; ATR_WINDOW=14 defined twice independently.
               UNDOCUMENTED C-U5: horizon convention not single-valued (session-level = session-boundary in A,
                 20-bar in B; CAND-0009 = 14).
               UNDOCUMENTED C-U6: D2/F1 vs equal-high liquidity carried unresolved; KB strategy S21 trades
                 exactly what the ratified D2 pipeline is blind to.
               UNDOCUMENTED C-U7: legacy-428 ZERO_ALPHA_BASE_RATE conflates insufficient-n with measured-
                 negative under one REJECTED label (disclosed descriptive/non-final).
               UNDOCUMENTED C-U8: RED_TEAM_STATE.md resume doc 15 entries stale (says next [13], is [28]).
               CLEAN (verified): MK triage negative/insufficient separation + CAND-0023 rescue; invalid
                 analytic p not load-bearing; C5 premise mis-stated, context path ratified discovery-safe,
                 holdout never touched, inert for DEMO candidates; S2 formula + Q4 semantics consistent;
                 pdh_pdl demo engine gate code clean; chain fail-closed before live.
               VERDICT: no validated result invalidated (none exists; fail-closed held). Accumulated-
                 unverified mass concentrated at the two ends Red Team never saw — the ENFORCEMENT code
                 (demo_gate_engine) and the VALIDATION code (matched_null/pilot_pvalue/scoped_fdr); one
                 re-embeds an open finding (C-D1/H'), the other carries an open defect (W9). Priority: attack
                 the gate engine before live wiring; resolve W9 + attack the stat stack before any validation;
                 then mstrat/data-derivation/6 primitives; then fix the overstating labels.
               HANDOFF: Statistician, for protocol/prioritisation. Red Team designed no remedy, ran no data,
                 modified nothing outside red_team/ (no queue annotation — this targets the chain, not a
                 candidate).
               STATE: OPERATIONAL. Next entry [30], prev_hash E29.
  entry_hash:  E29

[30] 2026-07-29
  prev_hash:   E29
  event:       VERDICT               # CODE ATTACK — demo_gate_engine (C-R1 realized: independent attack)
  reviewer:    Red Team
  detail:      CEO tasked the first INDEPENDENT attack on the DEMO gate engine (built after ledger close,
               previously only VE self-verified). Targets: demo_gate_engine/pdh_pdl_demo_engine.py @ 86304e7
               (working tree == pinned, verified) + dynamic_exit_engine.py. Deliverable:
               policy_reviews/RT-CODE-A-0005_demo_gate_engine.md. Full source of both engines + both test
               files + MIN_STOP_FLOOR_PREREG.md read at source. No data run; engine not modified; no remedy.
               HEADLINE: the gate does NOT fully impose S1. S2/S3/audit correct and complete; S1 hierarchy
                 correct for every bar AFTER entry — but the ENTRY BAR's own stop is unguarded for
                 non-floored trades.
               DEFECT D1 (highest): both engines scan exits from entry_idx+1 and check the entry bar's stop
                 ONLY when floored (pdh:139-142). For a NON-floored trade the entry bar is skipped, so an
                 intrabar stop-out on ei is never registered. Since the open is the bar's FIRST tick,
                 low[ei]<=exec_stop (long) is a REAL post-entry stop breach → worst-case STOP, ignored.
                 DEMONSTRATED BY THE ENGINE'S OWN FIXTURE: test_invalid_execution_is_narrow_floored_only
                 part (b) (test_pdh:141-143) — long, open 100, stop 99.0 (not floored), low[ei=1]=98.9
                 (through the stop), bar 2 high 105 → engine returns TARGET (WIN); reality = stopped out at
                 99.0 (LOSS). The test asserts only "!= INVALID_EXECUTION" → passes while ENCODING the
                 optimistic misclassification. Turns a loss into a reported win. Majority case (flooring is
                 the exception); symmetric on short; present in BOTH engines. Directly contradicts the S1
                 "STOP over everything" claim — the exact failure S1 exists to prevent.
               DEFECT D2 (confirms C-D1): dynamic_exit_engine.py:6-7,67 uses day_end_idx = BLOCK boundary
                 (Finding H', never fires live) while pdh_pdl_demo_engine.py:57 uses the same DemoSignal
                 field = DAY boundary. One dataclass field, two opposite meanings, no type distinction.
                 Affected: CAND-0002 (DEMO_BASELINE) + any forward-event-exit policy; CAND-0002's Part B H'
                 never remediated, now embedded in code.
               RISK R1: prereg (MIN_STOP_FLOOR_PREREG:29-31) defines THREE INVALID conditions; the engine
                 implements (a) gap-through-floored-at-entry + (b) zero/neg risk, but NOT (c) same-bar
                 ambiguous entry/exit. The one place (c) arises (entry_idx==day_end_idx) resolves as
                 TIME_STOP-at-close (pdh:162-163), optimistic, deviating from the prereg's "mark INVALID."
               RISK R2 (confirms C-R7 + broader): dynamic:71 open_[j+1] safe only if caller sets
                 day_end_idx<=n-1, no assert; broader, NEITHER engine asserts entry_idx<=day_end_idx<=n-1 —
                 entry_idx>day_end_idx yields exit_idx<entry_idx (exit before entry) + garbage net_R. F3-class.
               RISK R3: gap-through-stop on a non-entry bar fills at exec_stop_price not the worse gap open;
                 residual slippage folded into the single observed cost constant (can't capture a tail gap).
                 Ordering mandate met, fill-price worst-case not. Minor.
               UNDOCUMENTED U1: K_SPREAD/K_TICK/K_ATR hardcoded copies of the prereg — silent-divergence
                 hazard (same as ATR_WINDOW).
               SURVIVES (verified): S1 hierarchy on ei+1..end (all collisions incl. triple, short-symmetric,
                 optimistic-target forbidden); S2 (floor on corrected distance, strategy_stop_distance
                 preserved, effective_spread observed) well-tested; S3 (strict ei+1, entry-bar target
                 ignored, prior-day visit irrelevant) well-tested; INVALID narrow (a)+(b); ALL audit fields
                 emitted every path (which is how D1 is provable from the fixture).
               COVERAGE GAPS: entry-bar non-floored stop MASKED not tested (the D1 fixture asserts only
                 !=INVALID); triple collision untested; entry_idx==/>day_end_idx untested; prereg clause-3
                 untested; gap-fill price untested; dynamic engine (3 tests) has NO floor/INVALID/entry-bar/
                 boundary/day-vs-block tests.
               VERDICT: SURVIVES on S2/S3/audit/post-entry-S1; FAILS to fully impose S1 at the entry bar.
                 The gate does NOT impose everything it claims (D1 shown by its own fixture; D2 embeds H').
                 Exactly the class of defect independent review (not self-verification) exists to catch —
                 audit risk C-R1 REALIZED. BLOCK any live wiring of the three waiting policies on this engine
                 until D1 + D2 are closed; the VE BLOCK now holds for a second, independent reason.
               HANDOFF: Statistician then CEO — D1 highest (loss-can-be-reported-as-win, rewrite the masking
                 test to assert STOP); D2 (CAND-0002 must not wire live, separate the field's two meanings);
                 R1/R2/R3/U1 carried; add the missing tests. Next Red Team target: the statistical stack
                 (matched_null/pilot_pvalue/scoped_fdr; W9 open). Red Team designed no remedy, ran no data,
                 modified nothing outside red_team/ (no queue annotation — target is engine code).
               STATE: OPERATIONAL. Next entry [31], prev_hash E30.
  entry_hash:  E30

[31] 2026-07-30
  prev_hash:   E30
  event:       VERDICT               # CODE ATTACK — the statistical stack (C-R2) + W9 correction
  reviewer:    Red Team
  detail:      CEO tasked the second unattacked end from RT-AUDIT-CHAIN-0001 (C-R2): the code that VALIDATES.
               Targets: matched_null.py, mn_calibration/adversarial/power, scoped_fdr_run.py, pilot_pvalue.py,
               synth_price.py, the WP-5' block-bootstrap oracle. Deliverable:
               policy_reviews/RT-CODE-A-0006_statistical_stack.md. Full source read by Red Team + git-level
               W9 reconstruction + WP-5'/verdict-dependency sweeps. No data run; nothing modified; no remedy.
               HEADLINE: NO verdict-producing defect found (unlike the enforcement engine RT-CODE-A-0005).
                 The validation chain is structurally SOUNDER than the DEMO gate — correct FDR, clean window
                 discipline, drift fix present+passing. The exposure is DOMAIN MISMATCH + lenient gates, not
                 wrong math. Nothing promoted; chain fail-closed.
               T1 W9 — CORRECTED (see verdicts_ledger correction [31]/E31): git-verified the flow-c D3 fix was
                 CHERRY-PICKED onto statistician-foundation 2026-07-25 (d4fb426/4259382/d4ee4bb, new SHAs);
                 code/matched_null.py + mn_adversarial.py byte-identical to flow-c (ATR-rescaling + drift
                 battery), results PASS (ALL_SCENARIOS_CALIBRATED=true, drift fpr05=0.0), PROJECT_AUDIT D3 =
                 RESOLVED. W9 read "open" because our check keyed on the ORIGINAL SHAs (uncontained) + flow-c
                 unmerged (true) — BOTH blind to a cherry-pick; and [29]/[30] conflated code/matched_null
                 (fixed) with the VE's separate validation_engine/F6 object (different test, still lacks the
                 drift mechanism). This is a RED TEAM DOCUMENTATION DEFECT (S-D1), corrected append-only.
               T1-bis SCOPE GAP (sharper than W9): PROJECT_AUDIT:8 — matched-null validated ONLY for 1.5xATR
                 stops on generic signals; STRUCTURAL-stop families never in the calibration battery. EVERY
                 current SMC candidate (PDH/PDL, session, weekly, persistent; DEMO pilots 0001/0003/0007) uses
                 structural stops → the primary alpha test would run OUT OF DOMAIN on the actual pipeline.
               T2 WP-5' oracle: validated at a SINGLE n=21,048, L>=H=20, "nu extrapolez", NO minimum-n stated.
                 Predecessor AR(1) invalidation persists at 10x n (not finite-sample). Already applied per-
                 regime at n<validated + on net_R, DISCLOSED (lm001_s1_execution.py:16-19). Block bootstrap
                 degenerates at small n (n=7 CAND-0023 -> zero blocks). Out-of-domain for small-n candidates.
               T3 FDR: bh_reject CORRECT BH step-up (p<=i*ALPHA/M, k-th faces k*alpha/M, NOT Bonferroni).
                 Two distinct m's kept separate: scoped-FDR grammar M=412 vs candidate-family m=16. Residual:
                 plain BH assumes independence/PRDS across same-60%-segment hypotheses — argued (W-partition),
                 not verified.
               T4 CIRCULARITY: NONE. research60/val20/holdout20-sealed disjoint; VALID_IDS from grammar stop-
                 field + frozen n>=25, committed before any p; no selection leakage; matched-null is a causal
                 permutation null, no E010 window nesting. Clean.
               T5 VERDICT DEPENDENCIES: NOTHING promoted on matched-null/scoped-FDR/WP-5'. The one scoped-FDR
                 survivor (S18 ce76669a3b2a) FAILS OOS (val p=0.0779>0.05) AND research_worthy=False (dd 33.4R
                 >25R) -> two criteria disagree, routed to certification not promoted. Engines independent;
                 WP-5' only consumer LM-001 read-only, deferred. So NO existing result is invalidated.
               SEVERITY: S-D1 (defect: our stale W9 record, corrected). RISKS: S-R1 matched-null not validated
                 for structural stops (the actual pipeline); S-R2 WP-5' single-n, small-n out-of-domain; S-R3
                 lenient calibration gates (adversarial 2x, power 3x nominal; small N low power); S-R4 null
                 unstratified (no regime-timing control); S-R5 whole stack inherits unattacked mstrat.simulate
                 (C-R3; may share RT-CODE-A-0005 D1 optimism); S-R6 BH PRDS assumed not verified. UNDOCUMENTED:
                 S-U1 results cherry-picked not re-run; S-U2 two m's unreconciled; S-U3 phase1 n-file untracked.
               SURVIVES: BH correctness; window disjointness + no leakage; causal permutation null; drift fix
                 present+passing (fpr05=0.0); adaptive-MC unbiased; k<25->p=1 fail-closed; nothing promoted.
               VERDICT: the validation code SURVIVES as correct math; its GUARANTEES are narrower than the
                 pipeline assumes (out-of-domain for structural stops + small n; lenient gates). No result
                 invalidated (nothing promoted, near-positive fails OOS) — but any candidate put forward for
                 validation would be judged by an engine outside its validated domain. Answers the CEO's
                 caution: what validates is NOT broken like what enforces, but its scope is over-claimed.
               HANDOFF: Statistician then CEO — correct W9 (done, append-only); extend calibration to
                 structural stops before any candidate validation (S-R1); set WP-5' min-n (S-R2); tighten
                 calibration gates / decide stratification / justify BH-under-dependence (S-R3/4/6); attack
                 mstrat.simulate next (S-R5 = C-R3). Red Team designed no remedy, ran no data, modified nothing
                 outside red_team/.
               STATE: OPERATIONAL. Next entry [32], prev_hash E31.
  entry_hash:  E31

[32] 2026-07-31
  prev_hash:   E31
  event:       VERDICT               # CODE ATTACK — mstrat.simulate (C-R3, the last unattacked end)
  reviewer:    Red Team
  detail:      CEO tasked the last unattacked end from RT-AUDIT-CHAIN-0001 (C-R3): mstrat.simulate, which
               produced EVERY screening number (34 candidates + 1972 legacy + 40 edges), enforces no gate,
               never attacked, inherited by the whole statistical stack (S-R5). Deliverable:
               policy_reviews/RT-CODE-A-0007_mstrat_simulate.md. Full source read + TICK/constant git
               archaeology. No data run; nothing modified; no remedy.
               HEADLINE: execution LOGIC is worst-case-correct (better than the demo engine); the defect is a
                 CONSTANT — TICK=0.1 is 10x the true tick (0.01), documented-wrong 2026-07-29, never fixed.
                 The tick moves every RAW screening/triage number (conservatively) but CANCELS in the matched-
                 null p-values. Nothing falsely promoted.
               T1 INTRABAR: CORRECT and more complete than the demo engine. Exit loop scans from j=ei (entry
                 bar INCLUDED); target_first defaults False = STOP-FIRST worst-case (target_first=True is a
                 measurement-only toggle, bracket_69.py:18-20, no production path sets it); floored trade
                 resolving on its own entry bar -> INVALID/excluded (:80), implementing the prereg clause the
                 demo engine OMITTED (RT-CODE-A-0005 R1). NO D1, NO R1. The demo engine REGRESSED from mstrat.
               T4 LOOKAHEAD: clean where checked. or_high/or_low broadcast (:20, no shift) is GATED SAFE by
                 s5_setups:283 bar_in_sess>=4 (after OR forms); features use shift/running/merge_asof-on-avail.
                 (Full 20-family causal audit not run this pass; shared engine + S5/S6 verified.)
               T3 HORIZON: sound. Pure structural exits + hard 48-bar timeout cap on every trade (to=48
                 default), timeout->close, non-overlap via last=xi cursor. 48 + 1.5xATR trailing are hardcoded.
               T2+T6 TICK (DEFECT): git-verified mstrat.py:10 = TICK=0.1 on ALL 7 branches, introduced
                 8585723 (Jul 13), NEVER changed. True tick = 0.01 (instrument spec, confirmed vs CEO's live
                 account 4033.84/4033.89; 10x error confirmed by STATISTICIAN_COST_CONSTANT_CORRECTION Jul 29).
                 The correction is PROSE ONLY ("verified at the instrument-spec source, NOT the code";
                 "Nimic re-rulat"). simulate uses module TICK not CFG['tick'] (:45,53,82); two independent
                 cost engines (mstrat TICK vs alpha_lab/families CFG['tick']) that would diverge on a partial
                 fix; live-execution repo already at 0.01 while research at 0.1. $0.40 = 2*cost at line 82,
                 not the lines the CEO cited (2*0.1 = 0.20, doubling is line 82). Impact: cost 2x too high
                 universally (0.40 vs corrected 0.20, because spread_ticks re-scales 1->5); 5*TICK floor 10x
                 too large but usually dominated by 0.10*ATR so binds only at low ATR (inflating INVALID
                 exclusions). Direction CONSERVATIVE -> correcting RAISES every expectancy -> cannot have
                 inflated anything.
               T5 PIVOTAL (cancel or bias?): the tick CANCELS in the matched-null p-value. matched_null routes
                 BOTH observed and null through MS.simulate -> identical cost/floor -> a uniform cost shift
                 subtracts equally from both sides -> p invariant. Floor bites on matched risk profiles ->
                 largely cancels. So matched-null calibration + scoped-FDR verdict ROBUST to the tick (unlike
                 the demo D1, an entry-timing optimism that would NOT cancel; mstrat has no timing-dependent
                 optimism). What does NOT cancel: the RAW screening/triage stats (absolute, not differences).
               WHAT MOVES: every raw screening/triage number (all 34 + 1972 + 40), UPWARD, when the tick is
                 fixed (~+0.01-0.08R/trade cost + low-ATR floor); the archival negative/insufficient
                 classifications + "none crossed zero at +0.075R" rest on an ESTIMATE never re-run through a
                 corrected engine and excluding the floor effect -> must be re-verified; 0022(-0.157)/
                 0024(-0.138) closest to zero, ranking not guaranteed stable. WHAT DOESN'T MOVE: matched-null
                 p-values + the scoped-FDR survivor-fails-OOS verdict (cost cancels).
               SEVERITY: M-D1 (defect: TICK 10x wrong, documented, unfixed, every number under it). M-R1
                 (risk: two divergent cost constants; research!=live tick). M-U1 (hardcoded 48/1.5/2500 magic).
                 M-U2 (invalidated analytic_p still in the live path).
               SURVIVES: worst-case intrabar order (no D1/R1); lookahead clean where checked; horizon sound;
                 matched-null robust to the tick; the demo D1 is a regression FROM this engine.
               VERDICT: mstrat.simulate SURVIVES on execution logic (more correct than the enforcement engine);
                 FAILS on a constant. Every raw screening/triage stat is conservatively biased and never re-run
                 corrected; matched-null verdicts shielded (cost cancels). Nothing falsely promoted; the
                 archival ledger must be re-verified under a corrected-engine re-run (which does not exist).
                 Closes the three unattacked ends (enforce/validate/produce).
               HANDOFF: Statistician then CEO — patch TICK + reconcile CFG['tick']+spread_ticks, re-run the
                 full campaign corrected; collapse the two cost constants; matched-null needs no tick re-run
                 (cancels) but keeps RT-CODE-A-0006 out-of-domain caveats; source/retire the magic numbers +
                 the invalidated analytic_p. Red Team designed no remedy, ran no data, modified nothing outside
                 red_team/.
               STATE: OPERATIONAL. Next entry [33], prev_hash E32.
  entry_hash:  E32

[33] 2026-08-01
  prev_hash:   E32
  event:       VERDICT               # CODE ATTACK — decision engine (level 6, CEO target architecture)
  reviewer:    Red Team
  detail:      CEO tasked an attack on decision_engine/decision_engine.py @ bdd15e5 (alpha-automation-v1),
               spec STAT-DECISION-ENGINE-SPEC-v1.0 ccb31d9 / manifest v2.7.47. First new piece of the target
               architecture; level 6, step 3 of 4. Deliverable: policy_reviews/RT-CODE-A-0008_decision_engine.md.
               Full source read + NUMERIC verification on synthetic counts (engine imported read-only). No data
               run; nothing modified; no remedy.
               HEADLINE: SURVIVES. Math sound (Beta ppf verified, n=0 gate-repair works, k handled, three-
                 outcome correction applied, fail-closed named). The 80% gate is REAL but LENIENT (not decor,
                 mostly inert for high-n candidates; teeth at 95%). Real exposure = 3 caller-boundary trusts,
                 not the arithmetic. Nothing wired yet (not invalidating anything).
               BETA PPF (own target): VERIFIED CORRECT incl. tails. Exact on closed forms (Uniform/Beta(2,1)/
                 (1,2)/arcsine to 1e-6); round-trip CDF(ppf)=q holds for realistic a,b (0.5..900) across tails.
                 Only "mismatch" at a,b<=1e-3 (n=0 regime) where it returns ~0 = the CORRECT quantile (mass at
                 {0,1}; round-trip metric uninformative on a near-vertical CDF). Gate impact none (new setup
                 p_t_lcb~0 fail-closes).
               k ESTIMATE (own target): cannot return negative — clamped [0,K_MAX] (:193). Verified: over-
                 dispersed->0 (no shrinkage, wide interval, conservative), homogeneous->K_MAX, <2 sibs->0.
               n=0 REPAIR (own target): works for the GATE in all cases. mu>0 -> p_t_hat = EXACTLY parent
                 (0.400000; k_eff=max(k,1e-6) preserves alpha:beta=mu:(1-mu), k cancels at n=0). RESIDUAL
                 (D-U2): mu=0 corner + n=0 -> p_t_hat=0.5 (old-bug value) in ev_point AUDIT field; gate SAFE
                 (p_t_lcb=3.11e-61~0 -> ev_lcb=-1.0 -> enter=False, verified); UNTESTED (n=0 test uses mu=0.40).
               T1 GATE-OR-FORMALITY: REAL gate, LENIENT. Blocks thin history (n=10 blocked, n=1000 passes,
                 tested). But at 80% ~1 SE haircut; for thousands-of-trades candidates p_t_lcb~=p_t_hat -> near-
                 equivalent to EV_point>0 -> almost nothing falls; bite is on new/low-n only; teeth at 95% post-
                 DEMO. Also LCB pessimizes ONLY p_t (+cost), NOT p_h/E[X|h] (:298) -> not fully worst-case.
                 Direct answer: not a formality, but soft at 80% and mostly inert for high-n candidates.
               T2 MINUS-ONE worst possible or plausible: worst possible IN-MODEL (horizon exits are >-1R by
                 construction, so -1 is below any real E[X|h]) but NOT worst in live -- the whole EV caps per-
                 trade downside at -1R (stop=exactly -1R), inheriting mstrat's no-gap-slippage optimism (RT-CODE
                 -A-0007 R3); a live gap over the stop fills <-1R. Fail-closed closed against the model, not the
                 tail. (D-R2.)
               T3 OPPORTUNISTIC DEEPENING: deepening-for-luck SELF-DEFEATS -- a sparse lucky cell widens its
                 interval -> lowers p_t_lcb -> LCB blocks it (genuine strength). BUT schema-SELECTION (which
                 descriptors/levels to build) is an uncorrected garden-of-forking-paths at the caller; only
                 COUNTS are hashed (prob_table_hash :250), NOT the schema -> no audit proves pre-registration.
               LOOKAHEAD (own target): none IN the engine (pure function of counts, no time/price). Trusts the
                 caller that OutcomeCell counts are strictly prior-to-decision; no as-of-time enforcement; the
                 tally window for p_t/p_h is unverifiable in-engine. (D-R1.)
               CIRCULARITY (own target): real loop IFF counts are executed-only (selection bias + un-blockable
                 freeze: blocked setup never trades -> never accumulates -> can't escape the block); avoided IFF
                 counts are a shadow/paper record of ALL setups. Engine doesn't specify/enforce the source. (D-R1.)
               D-U3: p_t and p_h shrunk INDEPENDENTLY (different k_t,k_h) can sum >1 (author-acknowledged :245);
                 the p_s>=0 clamp then drops the stop penalty = OPTIMISTIC; rare at LCB (p_t pessimized), offset
                 by the horizon term.
               THREE-OUTCOME CORRECTION: confirmed applied -- p_t = target-hit (:288) not winrate; separate
                 p_h/E[X|h]; EV formula :247. CAND-0001 category fix (p_t~0.05 not 0.175) structurally in force.
               SEVERITY: D-R1 (3 caller-boundary trusts: schema-selection, as-of-time, count-source). D-R2
                 (-1R cap inherits mstrat no-gap optimism). D-U1 (80% gate lenient/near-inert high-n). D-U2
                 (n=0 mu=0 residual, audit-only). D-U3 (p_t+p_h>1 clamp optimistic). D-U4 (ppf audit value ~0
                 un-interpretable at n=0).
               SURVIVES: ppf accurate + gate-safe; n=0 mu>0 exact parent; k never negative; three-outcome EV;
                 fail-closed named + D2 strict + feasibility + cost-as-parameter; 13 tests + mypy clean.
               VERDICT: SURVIVES. Arithmetic sound; shrinkage+LCB self-protects against lucky deepening; gate
                 real but lenient at 80% (teeth at 95%). Nothing invalidated (level 6, not wired, step 3 of 4).
                 Real risk displaced to what the engine TRUSTS -- caller-populated hierarchy (schema/as-of/
                 source) + the mstrat-inherited -1R cap -- none enforceable by a pure function.
               HANDOFF: CEO (step 4 of 4) then Statistician -- bind at the caller a pre-registered hashed
                 SCHEMA (not just counts), an as-of-decision-time guarantee, and a shadow/all-setups count
                 source; note the -1R cap depends on mstrat's no-gap model; add the mu=0/n=0 test; decide the
                 p_t+p_h>1 clamp semantics. Red Team designed no remedy, ran no data, modified nothing outside
                 red_team/ (no queue annotation -- not a candidate).
               STATE: OPERATIONAL. Next entry [34], prev_hash E33.
  entry_hash:  E33

[34] 2026-08-02
  prev_hash:   E33
  event:       VERDICT               # CODE ATTACK — level-1 H4 regime classifier (target architecture)
  reviewer:    Red Team
  detail:      CEO tasked an attack on code/regime_classifier.py @ 82b1ca3 (discovery-mk-matrix-v1), spec
               STAT-LEVEL1-REGIME-H4-SPEC-v1.0 7a9013d / manifest v2.7.49. Level 1, step 3 of 4. Checklist:
               lookahead/leakage/circularity/ambiguity/overfitting/hidden-params/reproducibility. Deliverable:
               policy_reviews/RT-CODE-A-0009_regime_classifier.md. Full source read + NUMERIC verification on
               synthetic OHLC (deps imported read-only from branch). No data run; nothing modified; no remedy.
               VERDICT: PASS_WITH_LIMITATIONS.
               LOOKAHEAD: PASS, PROVEN. Trailing windows [i-W+1,i]; run propagated idx<=i; expansion[i] uses
                 atr[i-1]. Numeric proof: classifying bar i on FULL [0,n] vs truncated [0,i+1] = 0 run-mismatch
                 + 0 vol-band-mismatch over 78 bars -> label of i depends only on bars <=i. Retrospective
                 monthly map explicitly forbidden.
               LEAKAGE: PASS (trailing; truncation-stable). REPRODUCIBLE: PASS (deterministic, no RNG, stable
                 under truncation). OVERFITTING: PASS (outcome-agnostic percentile partitions, reported-not-
                 tuned). HIDDEN PARAMS: PASS (every constant named + provenance: W=30 DERIVAT, P33/67 & RUN cuts
                 ALEGERE, K_SWING lab default, N_MIN fail-closed).
               W=30 (own target): derivation CORRECT (30 ~ week of H4 = 29.84; 460 = quarter = unit transplant).
                 "Undetectable downstream" claim REFINED: true under local stationarity (P10 -> ~10% occupancy,
                 verified 9.8% at W=30) but NOT exact under non-stationarity (quarter window mixes vol regimes,
                 rate shifts -- synthetic 9.8% vs 2.1%; per-bar labels differ ~4%). Hid, but not truly invisible.
               DIRECTION FROM BOS RUN (own target): defensible (avoids a 3rd structure def, ADX rejected) but
                 CIRCULAR/REDUNDANT (L-R1) -- detect_breaks is shared with structure-based candidates (S3/S11/
                 MK-01), so the level-1 structure axis is NOT independent context for that candidate class;
                 vol/news axes stay independent.
               COMPRESSION/EXPANSION COLLAPSE (own target): measured-justified (99.5% of expansion in HIGH),
                 near-lossless -- nine states recoverable as axis combos; loss = 0.5% of expansion bars outside
                 HIGH drop their tag (is_expansion only subdivides the HIGH band). Minor, measured (L-U3).
               NO-REGIME->NO-TRADE (own target/CEO condition): the SIGNAL is EMITTED (verified: n<W ->
                 UNAVAILABLE; n<n_min / |run|==1 -> NEUTRAL conf=0; boundary -> low conf + soft weight) but the
                 OUTCOME is NOT wired -- level 6 (RT-CODE-A-0008) consumes hard COUNTS not the soft RegimeState;
                 the propagation low-conf->wider EV_LCB->no-trade needs a level-1->6 mapping that is not in
                 either module. Condition preserved at the classifier, realization deferred to step-4 wiring
                 (L-U2). Direct answer: signal comes out, "no trade" not yet demonstrable.
               STATISTICIAN TARGETS: (a) equal-occupancy = LEGITIMATE convenience (runs geometric/memoryless ->
                 no natural threshold -> any cut arbitrary -> balanced cells best default; declared a choice,
                 not a market boundary). (b) |run|==1 = POST-FLIP not range; "RANGE" is a MISNOMER (verified idx
                 65 run=-1 -> RANGE; code comment itself says "direcție proaspăt răsturnată"); direction NEUTRAL
                 ok, band name misleads (L-U1). (c) soft assignment CAN hide a systematically wrong label -- it
                 is BOUNDARY-LOCAL, gives no protection against a globally mis-defined band; deep-band bars get
                 confidence 1.0 on a possibly-wrong label (this is why the window error hid) (L-R2).
               SEVERITY: L-R1 (structural circularity/redundancy). L-R2 (soft assignment can't guard a mis-
                 defined band + occupancy invariance only under stationarity). L-U1 (RANGE misnomer). L-U2
                 (no-regime->no-trade emitted but unwired). L-U3 (0.5% expansion tag loss).
               SURVIVES: lookahead-free (proven), reproducible, no hidden params, no overfitting, fail-closed,
                 W=30 correct, collapse justified, equal-occupancy a declared convenience.
               HANDOFF: CEO (step 4 of 4) then Statistician -- build+verify the level-1->6 propagation (L-U2 is
                 the CEO condition, only a promise until wired); disclose structure-axis redundancy for
                 structural candidates; note "RANGE"=post-flip; treat W=30 as a real modeling decision (per-bar
                 labels change). Red Team designed no remedy, ran no data, modified nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [35], prev_hash E34.
  entry_hash:  E34

[35] 2026-08-03
  prev_hash:   E34
  event:       VERDICT               # CODE RE-ATTACK — demo_gate_engine repair (D1/D2/R1/R2), gates live wiring
  reviewer:    Red Team
  detail:      CEO tasked a re-attack on demo_gate_engine @ 06e4e00 (the D1/D2/R1/R2 fixes from RT-CODE-A-0005).
               Gates live wiring (4 policies waiting). Checklist + NUMERIC re-verification on synthetic bars incl.
               the exact fixture that exposed D1. Deliverable: policy_reviews/RT-CODE-A-0010_demo_gate_engine_
               repair.md. No data run; nothing modified; no remedy.
               VERDICT: PASS_WITH_LIMITATIONS. All four defects genuinely fixed and independently re-verified;
               residual limitations are CALLER-CONTRACT preconditions the pure function cannot enforce.
               D1 (entry-bar S1 at ALL trades): FIXED, VERIFIED, SYMMETRIC. Re-ran the exposing fixture (long,
                 stop 99 non-floored, entry-bar low 98.9, next high 105): now STOP exit_idx=1 px 99.0 net_R
                 -1.000 stop_at_entry_bar = LOSS (was TARGET/win). Long/short symmetry (CEO target): PASS -- both
                 STOP@1 net_R -1, identical order; boundary-inclusive (low==exec_stop -> stop). No false stop on
                 a non-breaching entry bar (proceeds to scan). Entry-bar target still ignored (S3, conservative).
                 New-defect hunt: none -- fill at exec_stop (wick, not gap; gap pre-empted by NO_TRADE/floored-
                 INVALID); check order worst-case on every branch.
               D2 (day_end_idx -> time_stop_idx): naming separation COMPLETE. One meaning (force-close limit,
                 caller decides representation); both engines consistent; grep -> NO stale day_end_idx consumer
                 (comments only). BUT the rename fixes the NAME collision, not the VALUE's live-validity: a
                 block-boundary time_stop_idx re-introduces Finding H' (never fires live) -- CRITICAL for
                 CAND-0002; the caller must pass a live-valid horizon. Engine honest, not enforcing (DR-L1).
               R1 (third INVALID condition): DECLARED SUBSUMED, argument VALID. The literal clause-(3) guard
                 (entry <= exec_stop) is TAUTOLOGICALLY FALSE (exec_stop derived from entry, dist>0) = fail-
                 closed no-op. The real same-bar ambiguous case is RESOLVED WORST-CASE by D1 (entry-bar stop-
                 first) + S3 (ignore entry-bar target): same-bar stop -> STOP (loss), target never credited.
                 Worst-case resolution is >= as conservative as marking INVALID; no unresolved same-bar
                 ambiguity. (Minor: dead clause-(3) misleadingly labeled 'ambiguous_same_bar_fill', DR-U2.)
               R2 (F3 precondition): FIXED, VERIFIED. 0<=entry_idx<=time_stop_idx<=n-1 raises ValueError in BOTH
                 engines (verified all 3 bad cases raise). Closes the dynamic open_[j+1] risk (RT-CODE-A-0005
                 R7): boundary branch returns before opposing -> opposing only at j<scan_end -> j+1<=time_stop_
                 idx<=n-1, bounds-guaranteed by the assert (verified in bounds).
               CORRECTED FIXTURE: now asserts the CORRECT result -- STOP, exit_idx=1, px 99.0, net_R<0 (loss),
                 stop_at_entry_bar -- not just '!= INVALID'; explicitly notes the old test 'codifica eroarea D1'.
                 Plus new dedicated D1 tests (unfloored-STOP, short-symmetry, no-breach-proceeds). Masking removed.
               CHECKLIST: lookahead PASS (reads only [ei, time_stop_idx]; open first tick; scan ei+1; F3 caps
                 n-1); leakage PASS (pure per-trade); circularity N/A; ambiguity minor (dead clause-3 label);
                 overfitting N/A; hidden-params one carried (K_SPREAD/K_TICK/K_ATR hardcoded copies of prereg =
                 DR-U1; tick is correctly a PARAMETER but caller must pass 0.01 not 0.1 = DR-L2); reproducible
                 PASS (29 tests 22+7 pass, mypy clean, numeric checks reproduce).
               LIMITATIONS (all caller-contract, none an engine bug): DR-L1 time_stop_idx live-validity
                 unenforced (block boundary -> Finding H', critical CAND-0002); DR-L2 tick_size correctness
                 unenforced (must be 0.01 per RT-CODE-A-0007 or S2 floor 10x off); DR-U1 hardcoded prereg
                 constants; DR-U2 dead clause-(3).
               VERDICT: PASS_WITH_LIMITATIONS -- the four RT-CODE-A-0005 defects are closed and verified; live
                 wiring may proceed PROVIDED the caller honors a live-valid time_stop_idx (not a block boundary)
                 and tick_size=0.01. With those, S1 (entry bar + all collisions), S2, S3, the three INVALID
                 conditions, and F3 are all correct; the masking fixture is repaired.
               HANDOFF: CEO (unblock decision) -- confirm CAND-0002's caller passes a live-valid time_stop_idx
                 (DR-L1) and all callers pass tick 0.01 (DR-L2); collapse the hardcoded constants; then the gate
                 is safe to wire. Red Team designed no remedy, ran no data, modified nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [36], prev_hash E35.
  entry_hash:  E35

[36] 2026-08-04
  prev_hash:   E35
  event:       VERDICT               # CODE ATTACK — level-2 H1 bias factors (bias_h1.py)
  reviewer:    Red Team
  detail:      CEO tasked an attack on code/bias_h1.py @ 81a0a62 (discovery-mk-matrix-v1), spec
               STAT-LEVEL2-BIAS-H1-SPEC-v1.0 1b2933c / manifest v2.7.51. Level 2, step 3. Checklist:
               lookahead/leakage/circularity/ambiguity/overfitting/hidden-params/reproducibility. Deliverable:
               policy_reviews/RT-CODE-A-0011_bias_h1.md. Full source + NUMERIC verification on synthetic H1
               (deps read-only from branch). No data run; nothing modified; no remedy.
               VERDICT: PASS_WITH_LIMITATIONS.
               LOOKAHEAD: PASS, PROVEN, stricter than required. compute_bias slices to [0, min(i,len)); reads
                 only last CLOSED bar i-1. Numeric proof: scrambling bars>=i to a sentinel leaves ALL factors
                 + zero_eligible_fraction IDENTICAL -> output is a function of [0,i) alone.
               LEAKAGE: FAIL in the falsifiability DIAGNOSTIC (emitted factor clean). zero_eligible_fraction
                 builds pools ONCE on [0,i) (excluding pools swept anywhere up to i-1) then reuses that set at
                 each historical bar j -> a pool swept AFTER j is dropped from j's count (unknowable at j) ->
                 overstates the zero-fraction. MEASURED (synthetic): code 0.978 vs causal per-bar 0.801 (~18pt
                 too high). The emitted liquidity_above at i-1 is causal/correct; ONLY the metric leaks -- but
                 that metric (99.21% zero) is the JUSTIFICATION that admitted the factor, so it is overstated
                 and must be recomputed causally. (B-L1.)
               CIRCULARITY: spec-disclosed + confirmed. Zero of four factors independent of the primitives
                 candidates trigger on; structure_run_h1 = same detect_breaks as level 1 + structure candidates
                 (redundancy map: detect_breaks/swings/build_pools/detect_sweeps -> gen_cand0020-0025); only
                 NEWS independent. (B-L2.)
               OVERFITTING: PASS (K_ATR=1.0 reused from v2.7.41 not chosen; DAY/WEEK measured 23/115 not
                 transplanted; docstring forbids tuning k). HIDDEN PARAMS: PASS (all named + schema pre-
                 registered). REPRODUCIBLE: PASS (deterministic; 66.39% level-1 agreement reproduces the
                 Statistician; vocab from introspection; 24 tests + mypy). AMBIGUITY: minor (INJECTED
                 attribution coarse, B-U1).
               T1 factor active <1% = decor?: the <1% is INFLATED by B-L1; causally the factor fires ~20% (my
                 synthetic), NOT decor -- the leakage UNDERSTATED coverage; '0 eligible' is a real state. Useful
                 range = not ~0 not ~1; causal coverage is inside the band. Recompute before judging worth.
               T2 lost edges / second tier: the tier WORKS on the known mechanism -- expansion (injected as a
                 param into gen_cand0002/0008/0009, invisible to intra-func inspection) correctly flagged
                 INJECTED (verified). BUT coarse+incomplete: attributes 'all_gen_cand_receiving_it' by name-at-
                 module-level WITHOUT dataflow verification (can OVER-attribute any module-level ratified call),
                 and blind to cross-module / indirect (partial/getattr/tables) injection. Catches the searched,
                 not provably all. (B-U1.)
               T3 vocabulary restriction: PASS, nothing legitimate lost -- functions IN (detect_breaks/
                 expansion/build_pools/atr14/detect_sweeps/detect_swings), classes OUT (Block/PoolSide/BreakKind/
                 LiquidityPool/PoolTier) verified. Limitation: isfunction would drop a ratified callable-class/
                 partial/staticmethod (none today) -- not future-proof (B-U2).
               T4 95% anchor or convenience: declared CONVENIENCE cutoff. At 66.39% agreement structure_run_h1
                 = same detect_breaks at FINER resolution (H1 vs level-1 H4) -> 34% disagreement is resolution,
                 not an independent axis; agreement rate cannot separate info from resolution-noise -> needs
                 level-6 incremental-value measurement. Non-redundancy passes but marginal value unquantified.
                 Consistent with spec (only NEWS independent). (B-U3.)
               SEVERITY: B-L1 (lookahead in falsifiability metric, must recompute causally). B-L2 (redundancy/
                 circularity by construction, marginal value unquantified). B-U1 (second tier coarse+incomplete).
                 B-U2 (vocab function-only, not future-proof). B-U3 (95% convenience, info-vs-noise deferred).
               SURVIVES: lookahead-free by construction (proven); factors-not-probability separated; overfitting-
                 free; params disclosed + schema pre-registered; reproducible; vocab loses nothing legitimate;
                 second tier surfaces the injected displacement edge static inspection had missed.
               VERDICT: PASS_WITH_LIMITATIONS -- the emitted factors are causally sound and disclosed; the
                 falsifiability metric that admitted the liquidity factor is computed with lookahead and
                 overstated (recompute causally), and the factors are redundant-by-construction with the
                 candidates (only NEWS independent; marginal value unquantified).
               HANDOFF: CEO/Statistician -- recompute zero_eligible_fraction causally (B-L1); measure level-6
                 incremental value of structure/displacement over level 1 (agreement != information, B-L2/U3);
                 treat the redundancy inspection as covering the known mechanism only (B-U1/U2). Red Team
                 designed no remedy, ran no data, modified nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [37], prev_hash E36.
  entry_hash:  E36

[37] 2026-08-05
  prev_hash:   E36
  event:       VERDICT               # CODE ATTACK — zone_observer (Level-3 entry, live, never attacked)
  reviewer:    Red Team
  detail:      CEO tasked an attack on ai_trader/zone_observer/ (branch ai-trader-implementation,
               ai_quant_lab-research-main) — the Level-3 entry, records live: session levels A, demand zones,
               IFVG, BPR, PWH/PWL, liquidity voids. Statistician confirmed pure observation (no score/weight/
               threshold). Checklist + byte-verification of vendorization via git + cost scaling measured on
               synthetic bars. Deliverable: policy_reviews/RT-CODE-A-0012_zone_observer.md. No data run on the
               market; nothing modified; no remedy.
               VERDICT: PASS_WITH_LIMITATIONS.
               T1 VENDORIZATION: byte-verified CORRECT, zero drift. Detectors are a submodule pinned at
                 61cbd58c; session_levels a separate vendored file. Verified: order_flow 23b0470 /
                 imbalance_mechanics aa1c6d3 / order_block_void 2b0f3f3 / institutional_levels 23182f4 are
                 IDENTICAL blobs across pin<->bf02dd2 (so pin import = bf02dd2 version); market_structure
                 (52bb1eb vs d734ac9) + liquidity_mechanics (805b8cd vs 45a5219) genuinely DIFFER (reason the
                 pin was NOT moved -- would change structural_observer's live detect_breaks); vendored
                 session_levels blob = 95dc487b = bf02dd2's blob exactly, submodule clean; cross-version deps
                 Block (dataclass) + session_of + _runs + whole market_state byte-IDENTICAL across pin<->bf02dd2
                 (the cascade diff touched detect_breaks/label_structure, not these). zone_observer uses
                 market_structure only for Block (identical) -> never touches the differing code -> no drift.
               T2 OVERLAP: NONE, nothing double-recorded. structural records SWING/STRUCTURE_BREAK/FVG_FORMED/
                 FVG_REACTION/REGIME/ORDER_BLOCK_* and imports detect_order_blocks/mitigations/rejections NOT
                 detect_demand_zones; zone records SESSION/DEMAND/IFVG/BPR/WEEKLY/VOID. detect_demand_zones =
                 zone's unique order_flow fn; detect_fvgs computed in BOTH but recorded only by structural
                 (zone uses it as input to IFVG/BPR, records it nowhere) -> duplicate COMPUTATION (Z-U2), not
                 observation.
               T3 PRIMITIVE B: absent from every path. Only Primitive A imported; compute_persistent_session_
                 levels called nowhere; 'persistent' appears only in the forbidding docstring + an unrelated
                 persistent_state.store import.
               T4 PWH/PWL: formation only. compute_prior_week_levels + derive_week_index imported; observer
                 records WEEKLY_LEVEL_FORMED only; no detect_level_touches, no WEEKLY_LEVEL_TOUCH kind; docs
                 state no weekly-touch detector invented (ratified detect_level_touches excludes weekly).
               T5 COST (Z-U1): measured per-cycle scaling exponent k~1.13 (~LINEAR per cycle, each observe()
                 rescans the whole array) -> total-to-N = O(N^2.1) QUADRATIC. Extrapolated per-cycle @14000 ~
                 376 ms = ~2x AI Trader's <200ms projection (theirs is LINEAR-extrapolated from an 18-bar
                 baseline too small to show scaling -- at 18 bars detectors do near-zero work). WHEN a problem:
                 NEVER live (one H4 bar per 4h, sub-second cycle); YES on COLD REPLAY / restart re-accumulation
                 (~41 min to replay 14000 bars) because history is in-memory (disclosed, doesn't survive
                 restart) + recompute-from-scratch + no restart-persistence compound.
               CHECKLIST: lookahead PASS (one CLOSED bar at a time, LiveBarFeed guarantees; as_of=ts_close;
                 ratified causal detectors on [0,len]); leakage PASS (pure per-observer accumulation);
                 circularity PASS/N-A (no score/weight/threshold/feedback); ambiguity minor (Z-U2 dup compute);
                 overfitting PASS (BPR tolerances declared granularities, K_ATR unused); hidden-params PASS;
                 reproducible PASS (deterministic + key dedup; journal persists across restart, in-memory re-
                 accumulation deterministic = cost only).
               SEVERITY: Z-U1 (cost: per-cycle linear/total quadratic; projection optimistic ~2x; restart/
                 backfill cost). Z-U2 (detect_fvgs computed in both observers -- cost not duplicate observation).
               SURVIVES: vendorization byte-verified zero-drift; no recorded-event overlap; Primitive B absent;
                 PWH/PWL formation-only no invented touch; lookahead-free; no leakage/circularity/overfitting/
                 hidden-params; reproducible. Correctly built as a pure-observation Level-3 entry.
               VERDICT: PASS_WITH_LIMITATIONS -- correctness-relevant items all verified clean; the only
                 limitation is the quadratic cold-replay/restart cost + the optimistic <200ms projection (live
                 is never the bottleneck).
               HANDOFF: CEO/Statistician -- treat <200ms@14000 as optimistic (fine live), budget the quadratic
                 restart/backfill cost if fast recovery needed; the double detect_fvgs is a minor disclosed
                 redundancy. Red Team designed no remedy, ran no data, modified nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [38], prev_hash E37.
  entry_hash:  E37

[38] 2026-08-06
  prev_hash:   E37
  event:       VERDICT               # CODE ATTACK — validation precondition (3 verdict-blocking components)
  reviewer:    Red Team
  detail:      CEO tasked an attack on code/restante_validation.py @ c73d2d5 (statistician-foundation), spec
               STAT-DOMAIN-MISMATCH-AND-RESIDUALS-v1.0 + RT-CODE-A-0006. IF THIS PASSES, the four pilots
               (CAND-0001/0002/0003/0007) get the PROJECT'S FIRST FORMAL VERDICT. Checklist + numeric
               verification of the statistical algorithm on synthetic distributions (pure-function copies, NO
               real-data run -- Red Team does not backtest). Deliverable:
               policy_reviews/RT-CODE-A-0013_restante_validation.md. Nothing modified; no remedy.
               VERDICT: PASS_WITH_LIMITATIONS.
               FPR REPAIR (own target) VERIFIED COMPLETE: bug = inner oracle null centered at global 0 not at
                 the synthetic set's own mean; fix (calibrate_candidate:124 ss_c=ss-obs*sz) re-centers each
                 synthetic set. Numeric proof (synthetic known-null): BUGGY FPR=0.0000 (reproduces the symptom
                 exactly); FIXED FPR=0.045 normal / 0.034 skew / 0.063 heavy. No other mis-centering path
                 (calendar_block_bootstrap centers dsum0 at candidate mean, tests raw observed -- standard
                 correct bootstrap-of-mean). GATE WORKS: heavy-tailed FAILS (0.063, CI-upper 0.080>0.07) -> the
                 per-candidate calibration is a FUNCTIONING check, not a formality; almost certainly why
                 0013/0018/0022/0024 fail (heavy/skew net_R) while the pilots (smoother) pass.
               SPEC TARGET A (day-block contains full TRADE dependence?): NO -- contains BAR (within-day)
                 dependence, ASSUMES cross-day independence. Bootstrap resamples whole days -> within-day
                 preserved (verified); two trades on DIFFERENT days keyed to the SAME structure (level/zone/
                 regime) land in different blocks -> treated independent -> if edge concentrates on recurring
                 structures, overstates effective sample -> anti-conservative p. Spec's 4xH bounds bar-horizon
                 NOT structure-reuse. Severity candidate-dependent + UNMEASURED: day-keyed (0001 PDH/PDL, new
                 level each day) low; persistent-structure (FVG/OB 0002/0003/0007) more exposed. THE one
                 assumption that could invalidate a formal p-value -> Statistician must measure each pilot's
                 cross-day trade autocorrelation. (RV-L1.)
               SPEC TARGET B (centering preserves enough shape?): YES -- resampling whole day-sums preserves
                 skew/tails (verified: shapes flow through, gate reacts); legitimate for a location-shift null
                 of the mean. The residual is cross-day dependence (A), NOT the centering. Adequate.
               OWN TARGET matrix scoping: RESOLVE_MONTHS=48 -> SE(r)~0.145 (matches code 0.14; 10mo->0.38
                 matches reported 0.35). Reasonable not conservative (NEG_MATERIAL=-0.3 ~2*SE, boundary-weak).
                 Gaps: n>=25 trades != >=48 months -> a verdict-eligible short-history candidate's PRDS is never
                 verified yet goes on BH (RV-L3).
               OWN TARGET partition pivot (all 3 negatives share CAND-0016): CANNOT confirm genuine -- possible
                 resolvability-SELECTION artifact (0016 may be in all resolvable negatives only because it has
                 the longest overlap). Code reports noise-excluded negatives as a COUNT not the PAIRS ->
                 Statistician must inspect the noise pairs; if they also center on 0016 -> genuine, else
                 artifact. Plausible but unverified. (RV-L2.)
               OWN TARGET FPR gate 0.07: convenience threshold (1.4x nominal), IMMATERIAL to the pilots (they
                 pass at 0.011/0.022/0.025/0.043, far below any of 0.06/0.07/0.075); at 0.075 three of the four
                 FAILING non-pilots might flip. The gate value only decides non-pilots. (RV-U1.)
               CHECKLIST: lookahead PASS (net_R keyed to entry day/month, bootstrap resamples observed
                 outcomes); leakage PASS; circularity PASS (shape-calibration on the null shape is definitional
                 not circular); ambiguity minor (partition reporting hides noise pairs); overfitting PASS;
                 hidden-params PASS w/ note (0.07/48/-0.3 declared convenience); reproducible PASS w/ fragility
                 note (seed = 7e6+ci*1000, enumeration-index-dependent). (RV-U2.)
               SEVERITY: RV-L1 (day-block cross-day independence -- the only limitation that can invalidate a
                 p-value; measure pilot cross-day autocorrelation). RV-L2 (partition pivot unverified). RV-L3
                 (PRDS only checked for >=48-month pairs). RV-U1/U2 (convenience thresholds; seed fragility).
               SURVIVES: FPR repair complete (buggy=0, fixed~0.05, gate rejects heavy tails); pilots calibrate
                 ROBUSTLY (0.011-0.043); L=28 retracted correctly (block=day, immune to trade frequency);
                 centering preserves shape; lookahead/leakage/circularity clean; gate is a functioning check.
               VERDICT: PASS_WITH_LIMITATIONS -- machinery sound, pilots pass robustly. The four pilots MAY
                 receive the project's first formal verdict, CONDITIONED on the Statistician (a) measuring
                 cross-day trade autocorrelation per pilot (RV-L1, the only p-value-invalidating item) and (b)
                 confirming the 0016 partition vs the noise-negative pairs (RV-L2). RV-L3/U1/U2 disclosures.
               HANDOFF: Statistician then CEO -- close RV-L1 (cross-day autocorrelation) + RV-L2 (noise pairs)
                 before the verdict; decide RV-L3 (short-history PRDS). Repair + pilots' calibration + block-day
                 logic verified clean. Red Team designed no remedy, ran no data, modified nothing outside
                 red_team/.
               STATE: OPERATIONAL. Next entry [39], prev_hash E38.
  entry_hash:  E38

[39] 2026-08-07
  prev_hash:   E38
  event:       VERDICT               # CODE ATTACK — level-4 M5 zone confirmation (zone_confirmation.py)
  reviewer:    Red Team
  detail:      CEO tasked an attack on code/zone_confirmation.py @ ca683ff, spec STAT-LEVEL4-M5-CONFIRMATION-
               SPEC-v1.0 d977446 / manifest v2.7.54. Level 4, step 3 (common validation w/ level 3 DEFERRED by
               CEO -- M5/M15_v2 windows overlap ~40 days, one regime, seal intact). Checklist + NUMERIC
               verification on synthetic M5 (module + market_state read-only). Deliverable:
               policy_reviews/RT-CODE-A-0014_zone_confirmation_m5.md. No real-data run; nothing modified.
               VERDICT: PASS_WITH_LIMITATIONS.
               LOOKAHEAD: PASS, PROVEN. Descriptor reads only [hit+1, hit+W] (win_end=hit+W); entry at
                 hit+W+1; ATR at hit (causal). Numeric: scrambling bars>win_end leaves confirmation/
                 persistence/progress/encounters IDENTICAL -> descriptor is a function of bars <=hit+W.
               T1 tertiles: legitimate equal-occupancy CONVENIENCE (binomial derivation FAILED -- 44.7% not
                 5%, bars not independent -- honestly discarded, declared ALEGERI). Consistent w/ level 1;
                 not a discovered boundary. Classification needs BOTH axes same tertile -> UNDETERMINED
                 majority (conservative). PASS.
               T2 time boundary: eliminates outcome-conditioning (no lookahead) but does NOT just move it --
                 FORCES the confirmation to REPLACE the level-3 trade (entry W=60 M5 bars=5h later, different
                 price/risk), not filter it. Hypothesis CHANGES from 'does the zone hold' (filter) to 'after
                 5h resolution does momentum-entry pay' (new trade). Honest/acceptable given the constraint,
                 but a level-4 result must NOT be read as validating a zone filter. (Z4-L2.)
               T3 effort saturation an artifact of W=60? NO -- it's a RATE (~0.6-0.87 across W=20/40/60/80;
                 real median 38/60=0.63); count scales with W, rate doesn't. Excluding encounters as a
                 threshold is correct at any W. PASS.
               W=60 (own): correct derivation -- 5h/5min=60 M5 bars; 5h calendar horizon (= H=20 M15) transfers
                 across timeframes, bars don't. Same discipline that corrected L=28 + 460.
               persistence/return (own): sum=1 BY CONSTRUCTION not empirical -- return=1-persistence (identity;
                 closes partition beyond/not-beyond), and median(1-X)=1-median(X) always -> 0.517+0.483=1.000
                 guaranteed. Using one is correct, return has ZERO independent info, won't diverge. Code
                 computes only persistence. (Minor Z4-U1: identity framed as empirical.)
               UNDETERMINED chain (own): NOT verifiable here (level-4->6 wiring absent, decision engine
                 consumes counts not a ZoneConfirmation -- analog of RT-CODE-A-0009 L-U2). AND UNDETERMINED is
                 encoded as ordinal value 0 at the arithmetic MIDPOINT of -2..+2 -> a value-consuming
                 downstream reads 0 as NEUTRAL/proceed, NOT block. 'Sentinel by type' holds ONLY if level 6
                 checks the enum member / status, never the value. MOST FRAGILE for the MAJORITY classified-
                 UNDETERMINED case (status=AVAILABLE, only signal is ordinal 0). Fail-closed paths carry
                 status=UNAVAILABLE (verified: zone_unavailable/invalid_side/incomplete_window) -- robust IF
                 status is checked; classified-UNDETERMINED has no status sentinel. As encoded, silent
                 consumption is the DEFAULT of a value-consuming level 6. (Z4-L1, sharpest.)
               CHECKLIST: leakage PASS (pure per-interaction); circularity PASS/N-A; overfitting PASS (tertiles
                 declared, binomial discarded not kept); hidden-params PASS (W derived+declared, tick_volume
                 excluded/OHLC-only, schema_hash pre-registers); reproducible PASS (deterministic, hashed).
               SEVERITY: Z4-L1 (UNDETERMINED silent-consumption -- ordinal-0-at-midpoint; block-by-type needs
                 a level-6 enum/status check, unverified; majority case has only ordinal 0). Z4-L2 (replace-
                 not-filter changes the tested hypothesis). Z4-U1 (identity framed as empirical, cosmetic).
               SURVIVES: lookahead-free (proven); W=60 derived; persistence/return an identity; effort-
                 saturation a rate; tertiles a legitimate convenience; absorption^acceptance inexpressible by
                 type (right structural choice); all fail-closed -> UNDETERMINED+UNAVAILABLE.
               VERDICT: PASS_WITH_LIMITATIONS -- classifier causally+structurally sound; both limitations live
                 at the INTEGRATION boundary (Z4-L1 the ordinal-0 sentinel must be enforced by a type/status
                 check at level 6 or the majority-undetermined interactions trade silently; Z4-L2 the
                 confirmation replaces the level-3 trade, testing a different hypothesis). Neither a defect in
                 this file; both must be honored downstream.
               HANDOFF: CEO/Statistician -- level 6 must treat UNDETERMINED via enum member/status not the
                 ordinal value (Z4-L1); record that level 4 validates a post-window momentum entry not a zone
                 filter (Z4-L2). Classification itself verified clean. Red Team designed no remedy, ran no
                 data, modified nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [40], prev_hash E39.
  entry_hash:  E39

[40] 2026-08-08
  prev_hash:   E39
  event:       VERDICT               # CODE ATTACK — level-3 M15 operational zone map (zone_map.py)
  reviewer:    Red Team
  detail:      CEO tasked an attack on code/zone_map.py @ 11ae360, spec STAT-LEVEL2-CONDITION-AND-LEVEL3-ZONE-
               MAP-SPEC-v1.0 a595cc5 / manifest v2.7.52 Part 3. Level 3, step 3. UNWEIGHTED counter (not a
               weighted score): 4 ratified features in a 1xATR band (pdh_pdl/fvg/liquidity/discount), k 0..4,
               threshold k>=4 = total confluence. Checklist + NUMERIC verification on synthetic M15 (module +
               all detector deps read-only). Deliverable: policy_reviews/RT-CODE-A-0015_zone_map_m15.md. No
               real-data run; nothing modified.
               VERDICT: PASS_WITH_LIMITATIONS.
               LOOKAHEAD: PASS, PROVEN. All features filter to available_idx/confirmed_idx <= i-1; ref=
                 close[i-1], atr[i-1]. Numeric: scrambling the LAST bar leaves counter_k/status/reason/
                 reference IDENTICAL -> reads only <= i-1, doesn't even read the current bar.
               T1 threshold k>=4: DERIVED from falsifiability (1xATR band saturates -- 3/4 coincide 94.87%;
                 k<=3 leaves 0.07/0.38/5.13% empty; only k>=4 leaves 57.18% complement = falsifiable). Genuine
                 derivation, not arbitrary -- BUT forced BY the band collinearity.
               T2 total confluence = map or FILTER? A binary FILTER -- THRESHOLD_K=4 with 4 features emits a
                 zone only when all 4 coincide; k=1/2/3 gradient discarded (ranked_by_k trivially (4,) or ()).
                 Hands level 6 a present/absent, not a gradient. 'Map' overstates it.
               T3 band 1xATR (4th time): reused ratified constant (v2.7.41), consistent -- BUT a PROXIMITY band
                 reused as a CONFLUENCE band imports the collinearity (94.87% coincidence), the source of the
                 saturation that forces k>=4. Anchor by reuse, arguably mis-scoped for confluence.
               CEO SATURATION Q (resolve or move up a level?): MOVES it up. Joint (band,k) RESTORES
                 falsifiability (k<=3 ~99% saturated -> k=4 57% complement) but does NOT resolve the band
                 collinearity: total confluence still fires 42.82% (common coarse state); my RANDOM-WALK
                 synthetic saturated to k=4 with no real structure. Problem moves from 'unfalsifiable counter'
                 to 'falsifiable coarse binary'; value of all-4-vs-not unquantified -> pushed to level 6. (ZM-L1.)
               OWN discount/SESSION_MID + other edges: REDUNDANT_WITH is a HAND-MAINTAINED dict (17 edges),
                 REGRESSION from level 2's mechanical static inspection; docstring says 'doua tiere -- L-R1' but
                 does NOT implement it. Manual list CAN be incomplete (CEO's undisclosed-edges concern). Verified
                 SESSION_MID->0028/0033 complete, but completeness NOT guaranteed by construction. (ZM-L2a.)
               OWN zero independent features: TRUE (all 4 map to candidate triggers; NEWS absent).
               OWN fail-closed UNAVAILABLE vs EMPTY SET: distinguished at the classifier (UNAVAILABLE ->
                 status=UNAVAILABLE; empty-set -> status=AVAILABLE + reason=empty_set_below_threshold) BUT both
                 zones=() -> level 6 must check status AND len(zones)>0; if status alone, the valid empty-set
                 (status=AVAILABLE) is silently consumed as 'map exists'. Same class as level-4 Z4-L1. (ZM-U1.)
               OWN cascade level1/2->3: by IF on caller BOOLEANS (regime_available/bias_available), NOT type-
                 propagated. If the caller mis-derives them, cascade silently fails. Weaker than type. (ZM-L2b.)
               CHECKLIST: leakage PASS; overfitting PASS (k derived, band reused, no fit); hidden-params PASS
                 (band+k jointly in schema_hash; M15 units correct); reproducible PASS; circularity = disclosed
                 redundancy by construction (all 4 candidate-triggered).
               SEVERITY: ZM-L1 (saturation moved not resolved -- coarse binary filter, band mis-scoped, value
                 unquantified). ZM-L2 (manual redundancy dict + if-cascade, both weaker than type-safe). ZM-U1
                 (empty-set silent-consumption).
               SURVIVES: lookahead-free (proven); unweighted counter the right structural choice; k>=4
                 legitimately derived; UNAVAILABLE/empty-set distinguished; zero independent features disclosed;
                 band/k jointly hashed.
               VERDICT: PASS_WITH_LIMITATIONS -- map causally sound, counter/threshold honestly derived; the
                 joint (band,k) derivation RELOCATES the saturation into a coarse falsifiable-binary rather than
                 resolving the band collinearity (ZM-L1), and redundancy/cascade/empty-set rely on manual/if/
                 status-alone mechanisms weaker than the type-safe alternatives (ZM-L2/U1). None a defect in this
                 file; all to be honored/strengthened at integration.
               HANDOFF: CEO/Statistician -- measure all-4-vs-not (ZM-L1) + consider narrower confluence band;
                 replace manual REDUNDANT_WITH with level-2 mechanical inspection + propagate cascade by type
                 (ZM-L2); level 6 NO_TRADE on status==UNAVAILABLE OR len(zones)==0 (ZM-U1). Classification
                 verified clean. Red Team designed no remedy, ran no data, modified nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [41], prev_hash E40.
  entry_hash:  E40

[41] 2026-08-09
  prev_hash:   E40
  event:       AUDIT                 # END-TO-END CHAIN AUDIT #2 — wp5b level tower + bus (DoD d782401)
  reviewer:    Red Team
  detail:      CEO tasked the end-to-end chain attack on the wp5b tower N1->N2->N3->opportunity_id->N4->
               PolicyMatcher->N6 + bus (MarketState/PolicyMatcher/Provenance), branch discovery-mk-matrix-v1,
               DoD d782401. Seven targets: lookahead/leakage/opportunity-identity/cross-tf-alignment/decision-
               clock/TRADE-NO-TRADE-integrity/audit-trail. Deliverable: policy_reviews/RT-AUDIT-CHAIN-0002_
               wp5b_end_to_end.md. Verified on synthetic + source. No real-data run; nothing modified.
               VERDICT: PASS_WITH_LIMITATIONS.
               SILENT-CONSUMPTION CLOSED (verified): LevelOutput=Ok[T]|Unavailable closes L-U2/Z4-L1/ZM-U1 --
                 Unavailable has NO .value (verified) so payload can't be read without narrowing; mypy --strict
                 + assert_never enforce; classified-UNDETERMINED handled by enum-member check in recognizers
                 (conf is UNDETERMINED -> WAITING), not consumed as neutral. A real structural fix.
               TRADE/NO-TRADE integrity: cascade fail-closed with reason -- decide() isinstance(regime,
                 Unavailable) -> NO_TRADE reason=regime_unavailable:<r> propagated (verified); N1 Unavail
                 cascades N2(axes_status)/N3(regime_available=False)/N4(skipped) by isinstance narrowing.
               DECISION CLOCK (sharpest, E2E-L1): opportunity_id.py CORRECTLY implements the CEO discipline --
                 DecisionRecord(decided_at=i0=zone_hit, inputs N1/N2/N3) + EvidenceRecord(attached_at=i0+W+1,
                 N4) linked ONLY by opportunity_id, N4 can't modify decision (point 6, by TYPE). BUT the bus
                 decide() does NOT use it -- it builds its own DecisionRecord from PolicyMatcher matches whose
                 recognizers READ N4 (_first_confirmation->state.confirmations, verified) -> bus decision
                 DEPENDS on N4 (observable only at hit+W+1) -> effective clock hit+W+1, entry moved, the
                 Statistician's forbidden 'clock depends on observed evidence'. DORMANT now (MATCH from N4 but
                 outcome NO_TRADE from edge=False) -> ACTIVATES at Shadow when a policy has validated edge
                 (MATCH-via-N4 -> TRADE at hit+W+1). Fix before Shadow: recognizers key on N1/N2/N3 at
                 zone_hit, N4 evidence-only.
               CROSS-TF ALIGNMENT: as-of correct + auditable -- each level runs on its own tf, provenance
                 records that tf's last-CLOSED-bar timestamp (t4/t1/t15/t5[-1]); a 12:00 H4 regime at a 15:55
                 M5 decision is correct (last closed H4) and visible in provenance (4h age auditable). BUT
                 valid_until is CARRIED (Ok.valid_until, 'carry-forward=type error') but UNENFORCED by the bus
                 -- trusts the caller to cut bars <= as_of per tf; a stale level would be silently used. (E2E-L2.)
               OPPORTUNITY IDENTITY: sound. Geometry-anchored (frozen anchor+band, not bar index -- zone@{bar}
                 named ~5.23 ids/zone). Two clocks: economic band_exit only MARKED (id survives), identity
                 clock i0+W+1 always closes -> identity SURVIVES band-exit (only ~4.77% reach i0+W+1). Re-arm:
                 in-band -> refresh same id (D7, no re-decide); beyond-W -> new opportunity counted, no
                 cooldown. Band frozen (a live band chases price -> fail-dead).
               AUDIT TRAIL: complete. Provenance(who/timeframe/as_of/detector/version) per contribution; full
                 chain in DecisionRecord.provenance; traceable to detector+schema+tf+timestamp; version=
                 'unavailable' for an Unavailable level (no schema_hash, correct).
               LOOKAHEAD/LEAKAGE: causal (each level <= its last closed bar per RT-CODE-A-0008..0015;
                 OpportunityTracker reads j-1; N4 ATR ref = current M15 atr[-1] broadcast, causal). Provided
                 the caller cuts bars <= as_of (ties to E2E-L2).
               T6 VE discrepancies: generalized S1/S16 faithful as RECOGNIZERS (sweep-absorbed->
                 ABSORPTION_PROXY_BEARISH; breakout->ACCEPTANCE_BULLISH) but ordinal proxies not full evaluator
                 logic; S2 (reclaim) NAMED in docstring but ABSENT from default_policies (2 of 3, verified). The
                 minimal edge gate (has_validated_edge bool, all False) vs full EV_LCB engine (bdd15e5): STRICTLY
                 CONSERVATIVE (can't false-trade), always NO_TRADE, but not the real N6. (E2E-U1.)
               SEVERITY: E2E-L1 (decision clock -- bus recognizers key on N4, dormant/activates at Shadow, FIX
                 before Shadow). E2E-L2 (valid_until carried but unenforced). E2E-U1 (S2 unwired, recognizer/
                 edge-gate proxies).
               SURVIVES: LevelOutput closes L-U2/Z4-L1/ZM-U1 (verified); cascade->NO_TRADE with reason; complete
                 audit trail; opportunity identity survives band-exit + re-arm + D7 + geometry anchor; as-of
                 correct+auditable; causal chain; minimal edge gate conservative. DoD auditable NO_TRADE correct.
               VERDICT: PASS_WITH_LIMITATIONS -- tower-under-one-contract a real structural achievement (silent-
                 consumption closed by type; cascade/identity/audit sound). Blocking for Shadow = E2E-L1 (move
                 the bus decision off N4 back to the zone_hit clock; opportunity_id already defines how) + close
                 E2E-L2 (enforce valid_until). E2E-U1 = disclosure (wire S2, full EV before trading).
               HANDOFF: CEO/Statistician before Shadow -- re-point recognizers/decide() to the opportunity_id
                 decision-clock records (E2E-L1, blocking); enforce valid_until>=as_of at the bus (E2E-L2); wire
                 S2 + replace the boolean edge gate with the full EV (E2E-U1). Contract closure/cascade/identity/
                 audit verified clean; the DoD holds. Red Team designed no remedy, ran no data, modified nothing
                 outside red_team/.
               STATE: OPERATIONAL. Next entry [42], prev_hash E41.
  entry_hash:  E41

[42] 2026-08-10
  prev_hash:   E41
  event:       VERDICT               # TARGETED RE-ATTACK — wp5b bus fixes (E2E-L1/L2/U1), diff d782401->ad8b586
  reviewer:    Red Team
  detail:      CEO tasked a targeted re-attack on ONLY the three RT-AUDIT-CHAIN-0002 fixes (diff d782401 ->
               ad8b586, wp5b discovery-mk-matrix-v1); contract/cascade/identity/audit/lookahead already clean,
               not re-run. Deliverable: policy_reviews/RT-CODE-A-0016_wp5b_fixes_reattack.md. Verified on
               synthetic + the repo's own tests + a monkey-patched N4 reintroduction. No real-data run.
               VERDICT: PASS_WITH_LIMITATIONS (nothing blocks Shadow).
               T1 E2E-L1 completely closed? YES, every path checked. All 3 recognizers (pdl_sweep_reversal,
                 pdl_failed_break_fade, pd_close_breakout) read ONLY N1/N2/N3 via _nearest_zone(N3)+
                 _bias_direction(N2) -- grep-verified none touches confirmations/_first_confirmation (deleted).
                 _inputs_hash_n1n2n3 references regime+bias+zones, NOT N4 (verified). decide() computes outcome
                 from matches+edge, packs N4 into EvidenceRecord only. Numeric: same N1/N2/N3 + N4 in
                 {ACCEPTANCE,UNDETERMINED,Unavailable} -> 1 distinct decision + 1 distinct inputs_hash;
                 decided_at=5(zone_hit), attached_at=9(i0+W+1). No path from N4 to the decision.
               T5 (matters most) regression test that FAILS on N4 reintroduction? YES, PROVEN. test_e2e_l1_
                 decision_and_inputs_hash_exclude_n4 + ..._validated_edge_trade_is_also_independent_of_n4 assert
                 decision+inputs_hash invariant to N4 (incl. TRADE path). MONKEY-PATCHED _inputs_hash_n1n2n3 to
                 reintroduce N4 -> the guard test FAILED with AssertionError (unpatched passes). REAL guard,
                 not decorative -> the defect cannot be silently reintroduced. Closes the CEO's central concern.
               T2 did zone_hit move introduce a defect? No. Recognizers now key on zone.attribute(discount/
                 premium, N3)+bias direction(N2) -- FORCED by the fix (N4 not observable at zone_hit). S1=
                 discount+LONG (reversal), S16=premium+LONG (breakout), coherent; no double-match (bias single-
                 valued). Semantic SHIFT confirmed->predicted, but that's the required direction. Coverage gap
                 (not a defect): premium+SHORT quadrant has no policy -> always NO_TRADE.
               T4 S2 recognizer faithful or filler? FILLER with a mismatched label (CEO's suspicion CORRECT).
                 policy_pdl_failed_break_fade = discount+SHORT; classic S2 reclaim of falsely-broken SUPPORT is
                 BULLISH (long, = S1). discount+SHORT is the leftover quadrant, occupied to reach 3/3, with a
                 'fade the failed break short' rationale that doesn't match a support reclaim. State coherent
                 (bearish continuation) but the S2-reclaim LABEL inaccurate. Low severity (edge=False; reads
                 only N1/N2/N3). (E2E-U1.)
               T3 _assert_cut/_require_valid on all paths or the main one? Fire on the PRODUCTION path,
                 procedural not structural. _assert_cut called for all 4 tf in build_market_state, RAISES on a
                 future bar (999>5, verified). _require_valid called for N1/N2/N3, RAISES on stale (valid_until
                 3<as_of 5, verified); NOT applied to N4 (evidence-only). BYPASS: both live in build_market_
                 state, NOT in the MarketState constructor -> direct construction (as the unit tests do)
                 bypasses them. Guards protect the intended entry but aren't type-enforced. (E2E-L2 residual.)
               SEVERITY: E2E-U1 (S2 filler/mislabel, low). E2E-L2 residual (guards procedural/bypassable via
                 direct construction; N4 window unchecked). Coverage (premium+short no policy).
               SURVIVES: E2E-L1 fully closed (recognizers+inputs_hash+decide exclude N4; invariant; guard
                 PROVEN to fail on reintroduction); E2E-L2 _assert_cut+_require_valid raise (verified); E2E-U1
                 S2 wired 3/3; 89-test suite + 5 targeted regression tests pass.
               VERDICT: PASS_WITH_LIMITATIONS -- the three fixes achieve their purpose; the blocking E2E-L1 is
                 fully closed with a WORKING PROVEN regression guard (defect can't be silently reintroduced) ->
                 NOTHING BLOCKS SHADOW. Minor disclosures: S2 filler/mislabel, procedural E2E-L2 guards,
                 premium+short coverage gap.
               HANDOFF: CEO/Statistician -- proceed to Shadow (E2E-L1 closed+guarded); relabel/replace S2
                 (discount+short is continuation not reclaim) + note premium+short gap; optionally move
                 _assert_cut/_require_valid into MarketState construction for structural enforcement. Red Team
                 designed no remedy, ran no data, modified nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [43], prev_hash E42.
  entry_hash:  E42

[43] 2026-08-13
  prev_hash:   E42
  event:       AUDIT                 # MEASUREMENT AUDIT — the two economic-verdict simulators (trade-by-trade)
  reviewer:    Red Team
  detail:      CEO (max priority) tasked auditing the INSTRUMENTS: edge_research/_screen.py (Alpha) vs
               code/mstrat.py (historical) -- do they give the same numbers on the same strategy/data?
               Mandatory addendum: TRADE-BY-TRADE with full fields, a 7-case synthetic fixture with known
               outcomes, an explicit convention matrix, a CANONICAL_TRADE_SIMULATION_CONTRACT, per-defect
               blocks. Deliverable: policy_reviews/RT-AUDIT-MEAS-0001_two_simulators.md. Both simulate loops
               replicated verbatim + run on one fixture. No engine modified; no repair; no market data.
               VERDICT: FAIL -- they diverge on the FIRST trade and on FIVE conventions.
               TRADE-BY-TRADE (fixture, known outcomes): FIRST DIVERGENCE = T1 (first trade) on COST (screen
                 GROSS +1.00 vs mstrat NET +0.80). Every trade diverges on cost. T5 (small stop) diverges 50x:
                 screen stop 99.9 gross +5.00 net +5.00 vs mstrat stop FLOORED to 99.0 gross +0.50 net +0.10.
                 Boundary test: a target hit ONLY on the last window bar = screen TARGET +1.00 vs mstrat TIME
                 -0.20 (off-by-one window). Same-bar SL+TP (T3) AGREE (both stop-first WC). Time-exit (T4)
                 AGREE. Long/short (T1/T6,T2/T7) symmetric AGREE.
               FIVE DIVERGENCES (DEFECT->COMPONENT->CAUSE->HISTORY->SUSPECT->RERUN in the report):
                 M-1 cost: _screen GROSS, mstrat NET(2*cost), demo_gate parametric -- 3 unreconciled; every
                   trade differs by 2*cost/risk.
                 M-2 risk floor: _screen NONE, mstrat floors max(2*spread*tick,5*tick,0.10*ATR); at ATR<5 the
                   binder is 5*tick=0.5 (10x wrong). Crushes small-stop/low-ATR (T5 50x). The eliminated
                   families are all small-stop. CEO evidence: TICK fix flipped 529 neg->pos, S3 -0.39->+0.23.
                 M-3 window off-by-one: _screen [ei,ei+tsb] inclusive vs mstrat [ei,ei+to) exclusive -- a
                   boundary-bar hit = target (screen) vs time (mstrat). NEW finding the aggregate missed.
                 M-4 blocks: _screen >72h gaps vs mstrat manifest segments -> different populations.
                 M-5 TICK=0.1 contamination: entire mstrat ecosystem (mstrat/s1/mtf/synth_price/trading_
                   strategies/task2/lm001/alpha_lab.CFG) carries the 10x error; _screen is TICK-independent.
               CONVENTION MATRIX (all requested): DIVERGE on tick/spread/slippage/risk-floor/window/blocks;
                 AGREE on same-bar precedence/entry/long-short/timezone-anchor(17:00 NY); NOT MODELED by
                 either (agree): point_size/contract_size/commission-line/tick-rounding.
               INVALIDATED/HOLDS: logically robust = Alpha's _screen GROSS-NEGATIVE eliminations (gross-neg =>
                 net-neg) + the level-fade=fat-tail finding (floor/cost/tick-independent), within _screen's own
                 basis. Suspect = mstrat small-stop/low-ATR leaderboard (M-2/M-5) + ALL cross-engine
                 comparisons (M-1/M-3/M-4). PROCEDURAL (CEO directive, overrides): until the audit closes with
                 ONE canonical semantics adopted + both engines re-run against it, NO leaderboard and NO
                 economic elimination is definitive.
               DELIVERED: CANONICAL_TRADE_SIMULATION_CONTRACT (11 clauses -- tick 0.01, next-open, floor
                 max(2*spread,5*tick,0.10*ATR) with tick 0.01 => 5*tick=0.05 required, NET cost 2*(spread+
                 slip)*tick, stop-first WC from entry-bar inclusive, single window convention, live-valid time-
                 stop not block boundary, 17:00-NY, manifest blocks for formal verdicts, fat-tail reporting,
                 provenance-tagged so two numbers compare only when tick/cost/floor/window/blocks match).
               HANDOFF: CEO/Statistician -- FREEZE all leaderboards+eliminations as non-definitive; reconcile
                 _screen/mstrat/demo_gate to the canonical semantics; re-run the mstrat 1972-campaign corrected
                 (529-flip is a lower bound). Red Team modified no engine, ran no data, changed nothing outside
                 red_team/.
               STATE: OPERATIONAL. Next entry [44], prev_hash E43.
  entry_hash:  E43

[44] 2026-08-13
  prev_hash:   E43
  event:       AUDIT                 # MEASUREMENT CONFORMANCE SUITE — the 17 canonical tests (step 5)
  reviewer:    Red Team
  detail:      CEO step 5: build the 17 canonical conformance tests, known-outcome synthetic trades vs EACH
               engine (SCREEN/MSTRAT/DEMO); all must produce the same register + net. Test 12 (tick<->USD)
               decisive; actively hunt a 6th divergence; BLOCK ratification on unexplained differences.
               Deliverable: policy_reviews/RT-AUDIT-MEAS-0002_conformance_17.md. Engines run as verbatim
               behavioral replicas. No engine modified; no repair.
               VERDICT: FAIL -- RATIFICATION BLOCKED. No engine implements the canonical semantics; diverge on
               >=6 axes; every difference explained but NONE reconciled.
               17-TEST RESULTS (per engine): T1 entry@N+1 CONVERGES (all next-open, cost diverges). T2 stop<min
                 -- FLOOR FLIPS OUTCOME: SCREEN no floor -> noise stop -1.0 vs MSTRAT/DEMO floor -> survive +0.1
                 (loss<->win, not just magnitude); SCREEN non-canonical. T3 SL entry bar: all catch, cost
                 diverges. T4 TP entry bar = ***SIXTH DIVERGENCE***: SCREEN/MSTRAT COUNT (win +1.0/+0.8), DEMO
                 S3 IGNORES -> time-exit -0.2 (same trade win vs loss; invisible to the screen-vs-mstrat
                 comparison, surfaces only with DEMO). T5 SL&TP same bar: precedence CONVERGES (stop-first),
                 cost diverges. T6/T7 last-window-bar hit: SCREEN inclusive target vs MSTRAT/DEMO exclusive time
                 (window off-by-one). T8 dataset-end time-exit: ALL THREE clip to n-1 and time-exit at the
                 dataset boundary -> ALL violate the canonical (horizon must be live-valid). T9/T10 17:00-NY +
                 DST: anchor CONVERGES (pandas tz_convert), not in simulate. T11 manifest: gap-blocks vs
                 manifest -> different populations. T14 net calc diverges (gross vs net). T15/T16 fat-tail:
                 _screen has best_share+trimmed_top1pct, mstrat has none -> asymmetric. T17 cross-config
                 rejection: NO engine tags verdicts with config provenance -> canonical clause 11 unmet.
               TEST 12 (MOST IMPORTANT) -- cost tick<->USD DIVERGES on TWO axes: (a) formula 2*(spread+slip)*
                 tick applies SPREAD TWICE = 0.60 USD vs canonical (spread once + slip per fill) 0.35 USD --
                 the tick<->USD CONVERSION is fine (25 ticks*0.01=0.25) but the STRUCTURE double-counts spread;
                 (b) USD-as-ticks unit bug = 2*(0.25+0.05)*0.01 = 0.006 USD ~ 58-100x too small (the CEO's
                 0.0005 failure). Third hazard: spread full-vs-half undocumented (2* only correct if half).
                 Cost triply unsafe: wrong tick + USD-as-ticks + spread-once-vs-twice.
               CONSOLIDATED (8): 1 cost gross-vs-net; 2 floor present/absent (FLIPS outcomes); 3 window off-by-
                 one; 4 block population; 5 TICK ecosystem; 6 ***entry-bar target (new)***; 7 cost formula spread
                 double-count; 8 shared violations (T8 dataset-boundary, T17 no-provenance, T15/16 asymmetric
                 metrics).
               MEANS: no engine is the reference (SCREEN violates floor+window+lacks cost; MSTRAT/DEMO carry
                 tick+floor+cost-structure; DEMO drops entry-bar targets; all violate dataset-boundary +
                 provenance). Ratification BLOCKED -- differences explained, none reconciled; same strategy ->
                 different registers. Freeze stands: no leaderboard/elimination definitive until all engines
                 pass the 17 against the canonical semantics.
               HANDOFF: CEO/Statistician -- adopt the canonical contract + SPECIFY entry-bar-target precedence
                 (T4) and spread half/full (T12/13, both under-specified even in RT-AUDIT-MEAS-0001 §6); make
                 the 17 tests the ratification gate; fix the shared violations; keep the freeze. Red Team
                 modified no engine, ran no data, changed nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [45], prev_hash E44.
  entry_hash:  E44

[45] 2026-08-13
  prev_hash:   E44
  event:       VERDICT
  dc_id:       DC-CANONICAL-EVALUATOR
  freeze_hash: 82acad9 (code/canonical_evaluator.py, v1.0-DRAFT NOT RATIFIED)
  battery_ver: RT-AUDIT-MEAS-0003
  reviewer:    Red Team
  detail:      ATTACK ON THE CANONICAL EVALUATOR @ 82acad9, run against the 17. VERDICT =
               PASS_WITH_LIMITATIONS as a SPEC; NOT YET the ratification gate. First artifact to
               implement ONE coherent semantics: R1 tick 0.01 single-source, R2 next-open, R3
               reject-not-widen (risk un-extended, no fictional P&L), R4 spread-ONCE (BASE 0.05 /
               STRESS 0.24), R5 entry-bar SL+TP inclusive + SL-primacy, R6 explicit window [ei,ei+H-1],
               R7 still-open-not-time-exit. CLOSES 7 of 8 divergences on the normal path; VE's 14 tests
               all pass (re-run 14/14); my 17 axes pass on the normal path.
               ***NINTH DIVERGENCE (actively hunted, found) MEAS-9***: the evaluator DROPS SCREEN's
               gap-open guard (`entry<=stop`/`entry>=tgt: continue`). Entry gapped THROUGH the stop
               (long, entry 97 stop 98) -> immediate 'stop' exit at 98 -> BASE net_R = +0.95, a WIN
               booked from a gapped-through stop (economic defect). Entry gapped THROUGH the target
               (entry 105 tgt 102) -> forced loss -0.436. SCREEN skips both. Same signal+config ->
               no-trade (SCREEN) vs win/forced-loss (evaluator). Untested by VE's 14 and by the first 17.
               SHARED VIOLATIONS repair-or-inherit: T8 dataset-boundary -> REPAIRED (R7 still_open /
               NoEntry). T15/T16 fat-tail -> NOT repaired, DROPPED: StrategyReport has NO best_share /
               trimmed_top1pct / any concentration metric (regression from _screen); CEO fat-tail guard
               UNCOMPUTABLE from canonical output. T17 config provenance -> HALF: config_id PRODUCED +
               immutable (16-hex sha256 over rules+scenarios+code_version -- the tagging VE claims IS
               real) BUT (a) NOT ENFORCED (no function refuses mismatched-config comparison; VE's own
               R11 test asserts only inequality + a 'NON-COMPARABLE' COMMENT) and (b) DATA-BLIND (payload
               omits symbol/date-range/block-manifest -> two runs on DIFFERENT instruments share ONE
               config_id -> falsely comparable; CEO T17 asks for 'block' provenance, absent).
               S3 +0.395 BASE: cost arithmetic verified -- old mstrat 2*(1+1)*0.1=0.40 (doubled) vs
               canonical BASE 0.05 (8x smaller), STRESS 0.24. DIRECTION right, engine now correct on cost;
               VE did NOT swap one engine error for another. BUT +0.395 is NOT a usable verdict:
               (1) BASE = most-optimistic + explicitly UNCALIBRATED, R4 requires BOTH scenarios;
               (2) R3 reject-not-widen CHANGED the eligible population vs the widen-era set;
               (3) comparing +0.395 to prior -0.39 is itself an R11 violation (NON-COMPARABLE config+
               population). Under the freeze S3 is NOT a final positive verdict.
               SUB-SPECS (CEO task 1): T4 entry-bar-target -> R5 CLOSES the normal case but MOVES a
               boundary case open (feeds MEAS-9). T12/13 spread full-vs-half -> R4 CLOSES it (no 2x
               factor; spread once).
               SEVERITY: MEAS-9 gap-open guard (RED, blocks gate); MEAS-10 fat-tail metrics dropped
               (RED, blocks gate); MEAS-11 config_id produced-not-enforced + data-blind (ORANGE);
               MEAS-12 population-shift disclosure (YELLOW).
               HANDOFF: adopt R1-R7/R11 + make all 3 engines CONSUME it; close MEAS-9 (add gap guard =
               test 18) + MEAS-10 (restore best_share/trimmed_top1pct) [both blocking]; close MEAS-11
               (comparison-guard + extend config_id to symbol/period/block); publish S3 BASE+STRESS,
               UNCALIBRATED, no -0.39 comparison. FREEZE HOLDS -- no leaderboard/elimination, and NO S3
               flip, definitive until every engine (incl. this evaluator) passes the expanded suite with
               matching provenance. Any single number presented as final is flagged. Red Team modified no
               engine, ran no data, changed nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [46], prev_hash E45.
  entry_hash:  E45

[46] 2026-08-13
  prev_hash:   E45
  event:       VERDICT
  dc_id:       DC-CANONICAL-EVALUATOR
  freeze_hash: 82acad9 (code/canonical_evaluator.py) + split_manifest v2.7.65
  battery_ver: RT-AUDIT-MEAS-0004
  reviewer:    Red Team
  detail:      SUITE EXTENDED TO 18 + RE-ATTACK PREP + FOUR-BLOCK COMPLETENESS. Re-attack proper waits
               for VE's three fixes (MEAS-9, T17, four-block); this is the preparable verification.
               CEO DECISIONS REGISTERED: (1) spread_price = FULL bid-ask (BASE 0.05 / STRESS 0.08) ->
               CLOSES the T12/T13 full-vs-half contradiction I raised; Statistician proof COST=2xEFF_SPREAD
               shows the old effective_spread was a HALF. (2) canonical population = FOUR blocks; 3 or 15
               NON-COMPARABLE.
               TEST 18 ADDED (red_team/policy_reviews/test_18_gap_open.py, canonical expectations, runs vs
               any engine). Q: does the Statistician spec (open beyond TP -> exit at ENTRY price, never
               nominal TP) CLOSE the gap or MOVE it? ANSWER = MOVES IT. 18A target-gap (open 105 > TP 102):
               spec covers it (exit at entry, -cost); current evaluator books nominal-TP -0.436. 18B
               stop-gap (open 97 < stop 98): spec is TP-ONLY, does NOT cover it; current evaluator books
               +0.95 = a WIN from a gapped-through stop (MEAS-9 survives). Spec must be made SYMMETRIC
               (open beyond ANY level -> cannot fill at that level).
               TENTH DIVERGENCE (novel) MEAS-14: the R3 rejection is SCENARIO-INVARIANT -- floor computed
               ONCE from sig.spread_price, Rejection returned BEFORE the scenario loop -> BASE and STRESS
               share ONE rejection population. CEO's per-scenario R3 components (0.05 vs 0.08) require
               DIFFERENT floors -> DIFFERENT populations, which the architecture cannot express. DISTINCT
               from the R3 2x-spread magnitude, which the manifest ALREADY flags as MATERIAL ('~18% R3 rate
               measured against DOUBLE thresholds') -- I record that as CORROBORATION of a known item, not
               a new find.
               FOUR-BLOCK CORRECTION = INCOMPLETE. Manifest DECLARES 4 (m15_v2_discovery_blocks; m4_block_count
               finding), but the 4th (2022-12->2025-10) is overlap_with_M15-inherited, NOT a regime_segment
               discovery_range. Verified 3 surviving paths: (a) split_manifest.py::segmentation_plan delivers
               3 discovery ranges + docstring SEALS 'the M15_v2 overlap ... never delivered'; (b)
               run_four_regime.py hardcoded 3 regimes (bear/bull/correction), expected bar-counts for 3,
               leaderboard '3 regimes', line-80 assert rejects a 4th (named 'four_regime', computes three);
               (c) _screen.derive_blocks gap-based (~15), manifest-blind. Enumerated regime_segments: bear
               2011, bull 2016, correction 2020 (3 discovery_range) + bull_partial TOO_SHORT_FULLY_SEALED.
               MANIFEST-INTERNAL CONTRADICTION (blocking): m4 provenance_of_the_fourth says the overlap IS
               the 4th discovery block (inherits M15 classification VERBATIM); segmentation_plan's contract
               says the overlap is 'never delivered'. Both cannot hold. CONSEQUENCE: CAND-0037's per-regime
               persistence and every run_four_regime figure are on a THREE-block population discarding the
               newest ~3 years -> non-comparable to four (correctly held non-final by the freeze).
               RE-ATTACK CHECKLIST armed (verify not trust): MEAS-9 both sides + monkey-patch guard; T17
               enforce-on-mismatch + config_id incl symbol/period/block; four-block delivered by ALL paths;
               MEAS-14 + R3 1x per-scenario; suite=18 vs every engine with matching provenance.
               FREEZE HOLDS. Red Team modified no engine, ran no data, changed nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [47], prev_hash E46.
  entry_hash:  E46

[47] 2026-08-13
  prev_hash:   E46
  event:       VERDICT
  dc_id:       DC-CANONICAL-EVALUATOR
  freeze_hash: 3344bff (code/canonical_evaluator.py v2.7.66, diff off 2403aad)
  battery_ver: RT-AUDIT-MEAS-0005
  reviewer:    Red Team
  detail:      RE-ATTACK on canonical_evaluator v2.7.66 @3344bff with the extended 18. VE's own suites
               re-run 23 passed / 2 skipped (T4 non-gap correctly BLOCAT). VERDICT =
               PASS_WITH_LIMITATIONS: measurement semantics PASS; comparability/provenance enforcement NOT
               yet structural.
               FOUR CORRECTIONS VERIFIED CLOSED: (a) MEAS-9 ASYMMETRIC both branches -- §5(a) risk<=0 -> 
               InvalidExecution (long 97/stop 98 -> dir_risk -1.0, NOT the old +0.95 win), COUNTED in report
               (invalid_executions=1) + excluded from returns, silent continue gone; §5(b) reward<=0 ->
               exit at ENTRY price, gap_through_target, R=-cost/risk (entry 105/tgt 102 -> -0.007 NOT -0.436).
               (b) MEAS-10 in the OFFICIAL report: StrategyReport.base/stress_concentration, best_trade_share
               as LevelOutput Unavailable('net_non_positive') when sum_R<=0 -- independently confirmed.
               (e) T12/13 resolved by the half_of ARITHMETIC (R3 = K_SPREAD*half = 2*(full/2) = full once =
               0.05/0.08; cost = full once); the NewTypes only GUARD it, they don't perform the fix.
               run_hash = sha256(config_hash||sha256(data_identity)); compare() raises NonComparableError.
               LIMITATIONS: (c) NewType is RUNTIME-ERASED -> 'unwritable' OVERCLAIMED; minimum_stop_distance
               (SpreadFull(0.05) as half) returns 0.10 DOUBLE with NO runtime error; caught only by mypy
               --strict, and NEITHER repo has ANY mypy config/CI/pre-commit (git-verified) -> guarantee
               currently UNENFORCED. (d) compare()/require_comparable() NEVER invoked internally (zero call
               sites beyond defs) -> opt-in, bypassable by direct comparison = same procedural pattern as
               E2E-L2. (f) MEAS-14 (the TENTH) PERSISTS: R3 rejection decided once from sig.spread_price
               before the scenario loop -> BASE/STRESS share ONE rejection population; per-scenario R3
               (0.05/0.08) unreachable. ELEVENTH (new): run_hash OMITS block_end -> same RunContext,
               block_end 5 vs 18 = identical run_hash but different results (still_open vs time) -> mismatched
               cuts falsely comparable.
               S3 51% INVALID: §5(a) is orientation-EXACT (dirn*(entry-stop)<=0), cannot false-positive a
               correct signal -> 51% is UPSTREAM (real S3 property or adapter orientation bug), NEVER an
               asymmetry artifact. Synthetic probe: stop AT the level the entry oscillates around -> tens-of-%
               INVALID by construction -> 51% PLAUSIBLY REAL (= half of S3 never executable, the audit's most
               consequential finding IF real). BUT no committed code computes it (S3->Signal adapter + run not
               committed) -> NOT independently reproducible; recommend committing adapter+run under a run_hash.
               S3 SAGA +0.23->+0.395->-0.13->-0.17 internally CONSISTENT: -0.17<-0.13 is EXPECTED because the
               excluded 51% exited near-breakeven (~-cost, ABOVE the -0.13 mean); removing them lowers the
               surviving mean. -0.17 = most-correct SO FAR for the executable 49% under BASE, NO new error
               found, but NON-COMPARABLE across the saga (R11) + BASE-uncalibrated + strong selection effect;
               must pair with STRESS. Decomposition spec-§4 NOT required for the gate (only to interpret the
               saga). T4 non-gap stays at Statistician (code counts+SL-first but unratified).
               RECO: ratify the contract's per-trade MEASUREMENT semantics now; WITHHOLD R11 comparability
               ratification until (c)(d)+eleventh are structural and MEAS-14 resolved/accepted. FREEZE HOLDS.
               Red Team modified no engine, ran no data, changed nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [48], prev_hash E47.
  entry_hash:  E47

[48] 2026-08-13
  prev_hash:   E47
  event:       CEO_DELIVERY
  dc_id:       DC-CANONICAL-EVALUATOR
  freeze_hash: 3344bff (superseded by pending VE strict-geometry correction)
  battery_ver: RT-AUDIT-MEAS-0006
  reviewer:    Red Team
  detail:      CEO AMENDMENT received + acknowledged (AMENDMENT_RECEIVED). FOUR parts:
               A2 — MEAS-9 ASYMMETRIC REJECTED. CEO ruling = STRICT GEOMETRY: LONG stop<entry_open<target,
               SHORT target<entry_open<stop; risk<=0 OR reward<=0 -> INVALID_EXECUTION, boundaries (open
               EXACTLY on stop/target) INCLUSIVE. I attack the CORRECTED version, NOT 3344bff. IMPACT: my
               RT-AUDIT-MEAS-0005 'MEAS-9 closed both branches' is SUPERSEDED on the target branch (3344bff's
               gap_through_target ExecutedTrade re-confirmed = the now-rejected asymmetric design). S3 -0.17
               (asymmetric) is PROVISIONAL — NON-COMPARABLE; a fifth S3 figure expected. MEAS-10 + T12/13
               remain CLOSED (orthogonal to A2).
               A5 — T17 not closed by a hash without ENFORCEMENT. run_hash must jointly identify FIVE: data,
               config, STRATEGY, engine, contract-version. VERIFIED on 3344bff: covers 3.5/5 — data PARTIAL
               (block_end omitted), config YES, **STRATEGY MISSING** (S1 and S3 on identical data+config yield
               the SAME run_hash efabefe3856205b1 -> compare() cannot refuse S1-vs-S3 -> T17 stays OPEN),
               engine YES via code_version, contract YES via code_version (conflated with engine). compare()/
               require_comparable() still NEVER invoked internally -> opt-in, bypassable. Existence != closure,
               as CEO states.
               A4 — TWO gates, kept distinct: (i) canonical-contract gate = MINE, whole suite + zero
               unexplained divergences + final CEO approval; (ii) AI Trader's 25 e2e = Mandate 2. I also
               attack the INTERFACE (VE tests <-> AI Trader tests).
               NEW TASK — VE_HANDOFF verification: 12 handoff points -> VE_HANDOFF_PASS|FAIL; only PASS
               authorizes Mandate 2. PASS is FORBIDDEN until the amendment is fully applied -> current state
               = VE_HANDOFF_FAIL (blocked). 12-point checklist armed.
               CURRENT-ATTACK CHANGES: hold for VE strict-geometry correction; rewrite Test 18 so 18A
               (target-gap) ALSO expects INVALID_EXECUTION (was exit-at-entry) + add the two boundary cases;
               build the VE<->AI-Trader interface attack; run the 12-point handoff. No PASS of anything until
               the amendment is fully applied. FREEZE HOLDS/WIDENS: all asymmetric-variant results PROVISIONAL/
               NON-COMPARABLE. Red Team modified no engine, ran no data, changed nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [49], prev_hash E48.
  entry_hash:  E48

[49] 2026-08-13
  prev_hash:   E48
  event:       CEO_DELIVERY
  dc_id:       DC-CANONICAL-EVALUATOR
  freeze_hash: n/a (range decision + handoff extension; artifact not yet built)
  battery_ver: RT-AUDIT-MEAS-0007
  reviewer:    Red Team
  detail:      CEO RANGE DECISION received: BLOCK RANGE, continue the rest. Range-requiring strategies ->
               eligibility=FALSE + reason_code=TRUE_RANGE_NOT_IDENTIFIABLE, never reach EV. Rest continues:
               N1-N6, EV, Risk Manager, LIVE_SHADOW + routing for TREND_UP/TREND_DOWN/MOMENTUM/COMPRESSION/
               BREAKOUT_TRANSITION. Handoff verification EXTENDED 12 -> 17: (13) range strategies fail-closed;
               (14) StructBand.RANGE + Direction.NEUTRAL cannot activate them; (15) reason_code PERSISTED not
               just returned; (16) other families work; (17) NO fallback/implicit routing to range = the
               adversarial priority (bypassable-guard pattern: hunt the indirect path to range eligibility --
               else-arm, enum coercion, direct construction, no-match->range).
               ROUTER FORM = MULTI-AXIAL, no global precedence (CEO): COMPRESSED+UP+STRONG must activate trend
               AND compression strategies SIMULTANEOUSLY; a hidden precedence = disguised selection (Statistician-
               flagged). ★ CONCRETE LEAD: market_intelligence/expansion.py::_state_for collapses the volatility
               axis into a single mutually-exclusive ExpansionState with an INTERNAL precedence ('EXPANDING
               takes priority over COMPRESSED when both true') -> if VE's router keys on .state, compression
               strategies never fire when displacement co-occurs = implicit partition. Mitigant: the raw
               is_compressed/is_displacement flags survive on the reading -> correct router reads RAW axes, not
               .state. Handoff check: confirm VE routes on raw per-axis flags, never a precedence-collapsed label.
               STATE unchanged: VE_HANDOFF = FAIL. A2 (strict geometry) + A5 (T17 five-identity incl STRATEGY +
               require_comparable enforcement) still OPEN; 17 conditions unverified (artifact not delivered).
               PASS forbidden until amendment fully applied. Attack CORRECTED evaluator not 3344bff; Test 18A
               rewritten -> target-gap expects INVALID_EXECUTION + two boundary cases. FREEZE HOLDS/WIDENS:
               asymmetric-variant results incl S3 -0.17 PROVISIONAL/NON-COMPARABLE. Red Team modified no engine,
               ran no data, changed nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [50], prev_hash E49.
  entry_hash:  E49

[50] 2026-08-13
  prev_hash:   E49
  event:       VERDICT
  dc_id:       DC-VE-BRAIN-HANDOFF
  freeze_hash: bd60c7a (ve_brain artifact, Mandate 1)
  battery_ver: RT-HANDOFF-0001
  reviewer:    Red Team
  detail:      VE HANDOFF VERIFICATION of the delivered artifact ve_brain/ @bd60c7a (router multi-axial,
               23 VE tests). VERDICT = **VE_HANDOFF_FAIL** -> Mandate 2 to AI Trader NOT authorized.
               🔴 FAIL-1 ROUTER_BYPASS (Obj5, decisive): n6.py::decide_n6 never requires an EligibilityDecision,
               never calls StrategyRouter/applicable_regimes/_declares_range; the range fail-closed lives ONLY
               in StrategyRouter.route_one. FIXTURE: decide_n6(strategy_id=RANGE_STRAT, regime_label=RANGE,
               RATIFIED, EV-positive) -> decision=TRADE, reason=TRADE_VALIDATED_EDGE (range strat gets a REAL
               trade; TRUE_RANGE_NOT_IDENTIFIABLE never fires). = bypassable-guard pattern a 3rd time (after
               E2E-L2, compare() un-wired). N6 must require route proof + re-assert range block.
               🔴 FAIL-2 IMPLICIT_PARTITION_BY_EXPANSION_STATE (Obj2, .state lead NOT closed): regime_routing.py:63
               applicable_regimes takes a SINGLE `volatility` string, not raw is_compressed/is_displacement.
               COMPRESSION<-vol=='compressed' (:69), BREAKOUT_TRANSITION<-vol=='high_directional' (:71) = mutually
               exclusive; exhaustive check: NO vol value yields {COMPRESSION,BREAKOUT_TRANSITION}. Fixture
               is_compressed=T AND is_displacement=T: if N1 collapses ->high_directional, COMPRESSION ERASED
               before the router. Partition just MOVED from market_intelligence/expansion.py::_state_for to N1's
               volatility axis. Router must consume RAW axes (or a vol SET).
               🟠 FAIL-3 A5 not imposed (Obj6): (a) block_end absent from fingerprint, delegated to
               measurement_run_hash which OMITS it (my eleventh) -> same-strategy/diff-block_end fixture fails
               at ve_brain; (b) require_comparable/compare_decisions NEVER called inside decide_n6/run_ev ->
               opt-in, un-enforced. PASSES within A5: strategy_id+strategy_version in fingerprint (S1!=S3, v1!=v2);
               engine vs contract SEPARATE (d3/d4/d5) -> my earlier 'conflated' finding FIXED.
               🟠 FAIL-4: version.py pins SOURCE_COMMIT=3344bff + MEASUREMENT_CONTRACT_VERSION=canonical-evaluator-
               v2.7.66 = the A2-REJECTED asymmetric evaluator (reason_codes declare strict-geometry INVALID_EXECUTION
               but the pinned engine is asymmetric). Re-pin to corrected evaluator; A2 still open.
               PASSES (so FAIL is precise): Obj4 simultaneity applicable_regimes('compressed','strong','up')=
               {COMPRESSION,TREND_UP} both, set-union no if/elif, multiple eligible kept as SEPARATE decisions;
               Obj1 at the router — RANGE never emitted (exhaustive False), no fallback/else:range, range-block
               precedence before UNCERTAIN (cond17 ok) BUT voided end-to-end by FAIL-1; Obj3 BREAKOUT_TRANSITION —
               |run|=1 alone/warmup(None)->UNCERTAIN, only range+high_directional->BREAKOUT, documented PER-BAR
               PROXY. Reason codes present on every output but persistence/queryability (cond 9/10) DELEGATED
               (ve_brain returns, has no store) = CONDITIONAL. 12 deliverables APPEAR present but do not cure the
               four defects. VE_HANDOFF_PASS forbidden. FREEZE HOLDS. Red Team modified no engine, ran no data,
               changed nothing outside red_team/.
               STATE: OPERATIONAL. Next entry [51], prev_hash E50.
  entry_hash:  E50
```
