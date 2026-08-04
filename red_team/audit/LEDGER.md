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
```
