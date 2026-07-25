# RED TEAM — STATE & RESUME DOCUMENT
### Read this first. Single source of truth for continuing Red Team work.
**Last updated:** 2026-07-24 · **Maintainer:** Red Team · **Status:** OPERATIONAL — normal standby

> A fresh Claude should be able to resume Red Team exactly from here by reading this file, then the documents it points to. Nothing else is required. **Do not re-derive; read the ledger and the reports.**

---

## 0. WHAT RED TEAM IS (30-second version)

Independent adversarial-review division of the AI Quant Lab. It receives **frozen, submitted Discovery Candidates** and tries to **break** them. It issues **RISK verdicts only** — never laboratory decisions. Governing stance: *every Discovery Candidate is treated as an unverified scientific observation until sufficient evidence justifies further investigation.* Quality control, not destruction; Alpha assumed good-faith; evaluate fairly.

**Authority model (never violate):**
- **Red Team** decides *risk and vulnerability* only.
- **Statistician** decides testable / insufficiently supported / statistically robust / statistically rejected.
- **CEO** alone decides Knowledge-Base promotion, archiving, closure, official status.

Red Team does **NOT**: promote, demote, finally accept/reject, discover, hypothesize, optimize, validate, run statistics, modify any Alpha/KB artifact, contact the Statistician, or change official methodology. It does **NOT** reproduce or run experiments.

---

## 1. WHERE EVERYTHING LIVES

| Thing | Path |
|---|---|
| Red Team repo | `ai_quant_lab/red_team/` (git branch **`red-team-foundation`**, off `master`, in repo `ai_quant_lab`) |
| **Alpha #1** official artifacts | worktree `ai_quant_lab-alpha-automation/` (branch `alpha-automation-v1`) — index `DISCOVERY_CANDIDATE_INDEX.md`, `HANDOFF_LOG.md`, `research_log/` |
| **Alpha #2** official artifacts | `ai_quant_lab/alpha_instance_2/` — files carry the **`_ALPHA2`** suffix; local IDs are **`AP2-DC-XXXX`** (not official lab IDs) |
| Stale/ignore | `ai_quant_lab-alpha-discovery/` (old Alpha #1 worktree, DC-0001 only) — **do NOT use** |

**Isolation rules (hard):** Red Team has **read-only** access to Alpha artifacts and writes **only** under `red_team/`. Never modify any Alpha #1 / Alpha #2 / KB / Statistician artifact. When a determination would require writing into another division's tree (e.g. attaching replication evidence), **record it and refer execution to the CEO**. Both Alpha instances are **actively working** — their working trees move; always re-read live state and bind reviews to a freeze-hash.

**Git habit:** commit only `red_team/` (never stage `flow_c/`, `results/`, `statistician/`, `alpha_instance_2/`, or Alpha's own uncommitted changes). Branch stays `red-team-foundation`; unpushed/unmerged unless the CEO says otherwise.

---

## 2. THE PIPELINE (mandatory for every candidate)

```
Phase 0  Duplicate Screening   ← methodology/DUPLICATE_SCREENING.md   (GATE: nothing starts before this)
Phase 1  Adversarial Review    ← methodology/CRITIQUE_BATTERY.md (C1–C5)
Phase 2  Contradiction Search  ← internal + cross-candidate
Phase 3  Methodology Audit     ← assumptions, denominators, provenance, thresholds
```

**Critique Battery v1.0 (RATIFIED):** C1 Observation Quality · C2 Evidence Quality · C3 Alternative Explanation · C4 Claim Discipline · C5 Worth Investigating. Submitted evidence only.

**Verdicts are RISK verdicts** (`methodology/RISK_VERDICTS.md`): LOW / MODERATE / HIGH / CRITICAL RISK, or the battery's 🟢 CONTINUE / 🟡 NEEDS BETTER EVIDENCE / 🔴 NOT RECOMMENDED. `READY FOR STATISTICAL VALIDATION` = "no major vulnerabilities obstruct statistical evaluation" (NOT accepted/validated/promoted). **"REJECT" is retired.** 🔴/NOT RECOMMENDED ≠ rejected; means "not recommended in current form."

**Counter-instance rule:** a single contrary observation is **never** a refutation — write *"evidence compatible with limitation or non-generalisation of the hypothesis."*

**Duplicate screening (Phase 0) classes** (mechanism-only comparison; never title/wording/timeframe/instrument/example): GENUINELY NEW · EXACT DUPLICATE OF [DC-ID] · VARIANT OF [DC-ID] · SUPERSET OF [DC-ID] · RELATED BUT DISTINCT FROM [DC-ID]. Independent replication → mark **INDEPENDENT REPLICATION OF [DC-ID]**, preserve evidence, never auto-create a research line.

---

## 3. CONSTITUTION & METHODOLOGY (read in this order)

1. `CHARTER.md` — the constitution (17 sections + governance blocks).
2. `INDEPENDENCE_RULES.md` — R1–R10.
3. `methodology/RISK_VERDICTS.md` — authority model + risk taxonomy.
4. `methodology/DUPLICATE_SCREENING.md` — Phase 0.
5. `methodology/CRITIQUE_BATTERY.md` — the five critiques.
6. `methodology/EVIDENCE_RULES.md` — E1–E10 (E10 = counter-instance rule).
7. `methodology/VERDICT_RULES.md` — verdicts as risk assessments.
8. `audit/LEDGER.md` — **append-only, hash-chained; the definitive history. Read it.**

---

## 4. WORK COMPLETED (chronological)

| Ledger | Deliverable | Outcome |
|---|---|---|
| E0–E3 | Division founded, Critique Battery v1.0 ratified, risk-verdict wording | CEO-accepted complete |
| E4 | **First review batch** — 13 DCs (DC-0001..0007, 0013..0018) | reviews in `reviews/DC-*/`; 🟢6 / 🟡7 / 🔴0 |
| E5 | CEO ruling on batch 1 | verdicts accepted |
| E6 | **Second review batch** — DC-0008..0012 (post handoff-reconciliation) | 🟢1 (DC-0008) / 🟡4 |
| E7 | **RT-DS-0001** — Stage 0 screening of Alpha #2's `AP2-DC-0001` | **VARIANT OF DC-0018**; independent replication; disposition = addendum to DC-0018 (execution referred to CEO) |
| E8 | Governance update — 4-phase pipeline + non-promotion | constitution amended |
| E9 | Risk verdicts formally separated from lab decisions | "REJECT" retired |
| — | **RED_TEAM_PHASE1_REPORT.md** — full adversarial pass on DC-0001..0018 | A=3 (DC-0003/0004/0008) / B=11 / C=4 (DC-0006/0010/0015/0017). *A/B/C now read as risk verdicts: A=LOW, B=MODERATE/HIGH, C=CRITICAL.* |
| — | **audits/RT-AUDIT-0001_ALPHA2.md** — Alpha #2 process audit | Score 64/100; CONTINUE WITH RECOMMENDED IMPROVEMENTS; AP2-DC-0001 risk HIGH |
| — | **audits/RT-AUDIT-0002_ALPHA1.md** — Alpha #1 full-portfolio audit (24 DC / 30 addenda) | Score 72/100; CONTINUE WITH RECOMMENDED IMPROVEMENTS; risk CRITICAL 5 / HIGH 13 / MODERATE 6 |

**All issued reports are immutable.** `RED_TEAM_PHASE1_REPORT.md` and `RT-DS-0001` predate the risk-verdict/non-promotion rules and are preserved unmodified; read them through `RISK_VERDICTS.md` §6.

---

## 5. PORTFOLIO SNAPSHOT (as observed 2026-07-24)

**Alpha #1:** 24 Discovery Candidates (DC-0001..DC-0024), all FROZEN v1; **30 addenda** (DC-0013 alone holds 11). Index/handoff/folders reconcile exactly. All 24 reviewed at least once (batches 1–2 covered 0001–0018; 0019–0024 covered in RT-AUDIT-0002's per-DC review, not yet in individual `reviews/` files).
**Alpha #2:** 1 candidate (`AP2-DC-0001`), 4 addenda (A–D). Screened (RT-DS-0001) + process-audited (RT-AUDIT-0001).

**Standing findings a successor must keep in view (Alpha #1):**
- **Record-chasing promotion** (F1) — "largest so far" cannot be false; 5 of 6 post-cutoff DCs are record-framed.
- **Record bookkeeping contradiction** (F2) — DC-0022's 86.75pt "family record" is wrong against DC-0013's own addenda (up to 180.53pt).
- **Holdout consumed** (F3) — DC-0019..0024 are post-cutoff; DC-0004's decisive test is compromised.
- **DC-0013 = family container** (F4) — ~12 instances, still reads "One instance."
- Confidence discipline & self-falsification culture are **strong** — do not mistake the above for sloppiness.

---

## 6. OPEN ITEMS / PENDING CEO DECISIONS

1. **Both audits await CEO decision** (RT-AUDIT-0001 Alpha #2, RT-AUDIT-0002 Alpha #1). No follow-up action until the CEO rules.
2. **RT-DS-0001 disposition** — Red Team determined AP2-DC-0001 should be filed as an **addendum to DC-0018**; execution belongs to CEO (would require writing into Alpha #1's tree). Not done.
3. **DC-0001 hash non-reproducibility** — Alpha-side OPEN item (`DC-0001_HASH_REPRODUCIBILITY_INVESTIGATION.md`); separate, does not affect scientific review.
4. **Verdicts ledger** was deliberately **not** updated with Phase-1 A/B/C or with the two audits' risk levels — those await CEO approval before entry.
5. DC-0019..0024 have per-DC coverage inside RT-AUDIT-0002 but **no individual `reviews/DC-00XX/` files yet** — create them if the CEO wants the per-candidate review artifacts to match batches 1–2.

---

## 7. WHAT TO DO NEXT

**Default: normal operational standby.** Wait for the CEO's next instruction or the next submitted candidate.

- **New Alpha candidate arrives** → run the full pipeline (Phase 0 first). Alpha #2 candidates *always* start with Duplicate Screening → a new `duplicate_screening/RT-DS-NNNN_*.md`.
- **CEO responds to an audit** → act only within the ruling; update `audit/LEDGER.md` (next entry `[10]`, prev_hash `E9`) and, if authorized, the verdicts ledger.
- **CEO asks to execute the RT-DS-0001 addendum** → still don't write into Alpha's tree; confirm the mechanism of hand-off.

**Every session:** append a ledger entry for anything you decide; keep reports immutable; re-verify freeze-hashes against the live handoff log before binding a review.

---

## 8. LEDGER INDEX (quick map — full text in `audit/LEDGER.md`)

`[0]` GENESIS · `[1]` operational, battery DRAFT · `[2]` battery ratified · `[3]` v1.0 accepted complete · `[4]` review batch 1 (13 DCs) + 3 escalations · `[5]` CEO ruling batch 1 · `[6]` review batch 2 (DC-0008..0012) · `[7]` RT-DS-0001 (VARIANT OF DC-0018) · `[8]` governance update (pipeline + non-promotion) · `[9]` risk verdicts separated. **Next entry: `[10]`, prev_hash `E9`.**

---

**End of state. Red Team is in normal operational standby, awaiting the CEO's next decision.**
