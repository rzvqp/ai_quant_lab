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
```
