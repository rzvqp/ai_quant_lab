# AI_TRADER_APPRENTICESHIP_MANIFEST

**Mandate:** CEO DIRECTIVE — FULL PROJECT STATE FREEZE + GIT CHECKPOINT, §§4-5 (scoped to the AI
Trader domain per the CEO's explicit scoping decision this session — see the final report for why
the full company-wide sweep was not attempted). This is the authoritative manifest for
`docs/trader_apprenticeship/`, produced as part of committing that directory to Git for the first
time. SHA256 hashes below were computed directly from the on-disk files at commit time via
`sha256sum`, not estimated or recalled.

---

## Q2 duplicate resolution (mandate §4)

Two files share the name `2020_Q2_H4_LOG.md`:

- `docs/trader_apprenticeship/2020_Q2_H4_LOG.md` — 8,313 lines,
  SHA256 `b2af3d869a89dd615fdeed7025f8e5f03138be7b1864e1dbdb0b8ad2096aaee6`
- `docs/trader_apprenticeship/lane_a_historical/2020_Q2_H4_LOG.md` — 22,570 lines,
  SHA256 `dc22b2940f7cf0448177910176754e02f311c03a9d20e0fea7279b8151bcebb6`

**Mechanical findings:**
- Hashes differ — **not** `IDENTICAL_DUPLICATE`.
- `diff` between the two produces ~30,681 lines of output — they diverge from the very first line.
  The `lane_a_historical/` copy opens with a formal header, `# Lane A —
  HISTORICAL_MARKET_APPRENTICESHIP — 2020-Q2 H4 walk-forward log`, absent from the root copy, which
  opens directly with mid-quarter trade-management material (a "trade #59" entry).
- `docs/trader_apprenticeship/lane_a_historical/2020_Q1_H4_LOG.md` exists with **no** root-level
  counterpart — Q1's log lives *only* under `lane_a_historical/`. This asymmetry is evidence (not
  proof) that `lane_a_historical/` is a distinct, complete, chronologically-earlier logging lineage
  (covering at least all of Q1 and, separately, at least part of Q2), while the root-level
  `2020_Q2_H4_LOG.md` and `2020_Q3_H4_LOG.md` belong to a later or differently-scoped logging
  convention that only ever produced root-level files for Q2 onward.
- `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md`'s own `SOURCES READ` line cites `2020_Q2_H4_LOG.md`
  without a path qualifier; given the checkpoint lives at the root of `docs/trader_apprenticeship/`,
  the most natural reading is the root-level file, but this is an inference, not a proven citation
  target — the checkpoint's text does not disambiguate mechanically.

**Verdict: `UNRESOLVED` — reported per the mandate rather than resolved by assumption.** Neither file
is deleted, hidden, or marked non-authoritative. **Both are retained and both are committed as-is**,
since committing a previously-untracked file for the first time is non-destructive regardless of
this ambiguity — no evidence is lost either way. This section documents the open question for a
future, dedicated provenance pass (comparing both files' content against the actual trade evidence
in `TRADE_EVIDENCE_LOG.md` line-by-line would be the mechanical way to resolve it, not attempted
here as it is out of this checkpoint's scope). **This ambiguity does not block staging or committing
the directory** — it blocks only declaring one copy "authoritative" over the other, which this
manifest explicitly does not do.

---

## Authoritative manifest

| PATH | PURPOSE | PERIOD | STATUS | AUTHORITATIVE | SUPERSEDES | SUPERSEDED_BY | SHA256 |
|---|---|---|---|---|---|---|---|
| `checkpoints/TRADER_KNOWLEDGE_CHECKPOINT_2020_Q1.md` | Q1 apprenticeship close-out checkpoint | Q1 2020 | FINAL | YES | — | — | `0a9eb9733bbba0d17003c8fc25770972deac6187033d846518962a3c60aa71e9` |
| `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md` | Q2 apprenticeship close-out checkpoint | Q2 2020 | FINAL | YES | 2 earlier provisional drafts (absorbed, not separately committed) | — | `bbd61fe1735bde8dc525c97d0d4ca4310e95716bb349a5deecaa040bbfe803c1` |
| `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q3.md` | Q3 apprenticeship close-out checkpoint | Q3 2020 | FINAL (amended with a visible correction pointer to the integrity audit) | YES | — | — | `a9659ccaf7761b6647397fc83277b270a5b4d89170990f67b7937db685aa61ed` |
| `AI_TRADER_Q2_VS_Q3_FORENSIC_REVIEW.md` | CEO-mandated Q2→Q3 learning comparison, PATTERN-007 deep review | produced this session | FINAL | YES | — | — | `a73b7301e4a7cdb357d772990b793d2532628750c20916cd159bcc22f85aadd6` |
| `AI_TRADER_Q3_INTEGRITY_AUDIT.md` | CEO-mandated boundary + batching-integrity audit | produced this session | FINAL | YES | — | — | `c13587cee2fd023334da3b3808f2331701ef9a2b25d92c6dcea5c078bef969c4` |
| `TRADER_Q2_FORENSIC_REVIEW_2020.md` | pre-existing Q2 trade-by-trade narrative/causal companion to the Q2 checkpoint | Q2 2020 | FINAL (pre-existing, not modified this session) | YES | — | — | `c311f7e3c50408d81eea62175d93d833bbbaf757ad047f3cdd860a5de4133d7d` |
| `2020_Q2_H4_LOG.md` (root) | root-level Q2 chronological H4 replay log | Q2 2020 | see Q2 duplicate resolution above | UNRESOLVED (retained, not deprioritized) | — | — | `b2af3d869a89dd615fdeed7025f8e5f03138be7b1864e1dbdb0b8ad2096aaee6` |
| `2020_Q3_H4_LOG.md` | Q3 chronological H4 replay log — the primary raw evidence source for PATTERN-007 and every Q3 trade | Q3 2020 | FINAL, complete through the Q3 terminal boundary | YES | — | — | `12e23daabfb5179eb7e51d321c5f3a8de20284459dd0d38af5f9d4fbf0b7a013` |
| `lane_a_historical/2020_Q1_H4_LOG.md` | Q1 chronological H4 replay log (only copy of Q1's log) | Q1 2020 | FINAL, sole source for Q1 | YES | — | — | `388f28c8c381e7b400c14d23e57055344a1196774877d20075cfa091e89cec01` |
| `lane_a_historical/2020_Q2_H4_LOG.md` | alternate/earlier Q2 chronological H4 replay log | Q2 2020 | see Q2 duplicate resolution above | UNRESOLVED (retained, not deprioritized) | — | — | `dc22b2940f7cf0448177910176754e02f311c03a9d20e0fea7279b8151bcebb6` |
| `TRADE_EVIDENCE_LOG.md` | frozen per-trade entry/close evidence for the entire apprenticeship (all quarters) | Q1-Q3 2020 | AUTHORITATIVE, cumulative | YES | — | — | `f9343c7d799634202ac23723eb35dd30cc17f473fedf69e0ce67ea28ead74048` |
| `REPLAY_DATA_GAP_LEDGER.md` | data-integrity gap ledger, GAP-001 through GAP-150 | Q1-Q3 2020 | AUTHORITATIVE, cumulative | YES | — | — | `f8bc0df8600cc9bf40426991eecb77fb8b0248f26e73e1b5a51b3cfb6cc6e2db` |
| `GOLD_BEHAVIOR_MODEL_V1.md` | the primary behavior-pattern deliverable (PATTERN-001 through PATTERN-007b) | built across Q2-Q3 2020, live document | AUTHORITATIVE, live (§7 CEO_REVIEW_GATE_SUMMARY last fully re-synthesized against n=21 — flagged stale relative to the final n=31 tally, per this session's audit) | YES | — | — | `3539a61497db206a3c20b985b79e78880612396a7b807fc621017637752abf5d` |
| `STRATEGY_EVIDENCE_DENOMINATOR.md` | methodology contract for what counts as structured-comparable trade evidence | standing methodology | AUTHORITATIVE | YES | — | — | `cfb27979969b349efca847487de4f10df44fbb9e12f78cea6ea6e5f727b7002a` |
| `TRADER_STRATEGY_CANDIDATES.md` | strategy-candidate registry (currently empty — `NO_STRATEGY_CANDIDATE_READY_YET`) | standing, live | AUTHORITATIVE, live | YES | — | — | `ca290d32f40742a7cc93e8f6a0f106fc80926d364fc1f9cdd332856f64626d96` |
| `AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md` | standing operating standard referenced by the Pine indicator governance record and Q3/Q4 methodology | standing | AUTHORITATIVE | YES | — | — | `73706a95fd60f5cc03a9c1e262a344ede8e374eb178cf1170f517dddf2839e80` |
| `EVIDENCE_UPGRADE_METHODOLOGY_V1.md` | methodology contract for backfilled vs. fully-evidenced trades | standing methodology, referenced by Q2 checkpoint | AUTHORITATIVE | YES | — | — | `e8cdc0e479552e6eedeea4e45c2678887f75d87e61bcd9f65e473d8593a1df9f` |
| `EVIDENCE_GRADE_CLASSIFICATION.md` | methodology contract for evidence-grade tiers | standing methodology | AUTHORITATIVE | YES | — | — | `f395ef4204568d8246ccaf10ff62a2fd0353b37c1bcce5bef930866fd603f3d7` |
| `AI_TRADER_REGIME_STRATEGY_MATRIX.md` | R01-R12 regime/strategy matrix, referenced by both Q2 and Q3 checkpoints | standing, live (summary index flagged stale by both checkpoints) | AUTHORITATIVE, live | YES | — | — | not separately hashed this pass — unmodified this session |
| `AI_TRADER_MARKET_READING_LIBRARY_V1.md` | market-reading concept library, cited by the Pine indicator's session-boundary sourcing decision | standing reference | AUTHORITATIVE | YES | — | — | not separately hashed this pass — unmodified this session |
| `AI_TRADER_EXPERIENCE_LEDGER.md` / `AI_TRADER_THESIS_PERFORMANCE_LEDGER_V1.md` | supporting ledgers referenced by the apprenticeship's own file cross-references | standing | AUTHORITATIVE (not independently re-verified this session) | YES | — | — | not separately hashed this pass — unmodified this session |
| `Q2_TRADE_PLAN_CONTRACT.md`, `REGIME_TRANSITION_WATCH.md`, `README.md` | supporting standing documents | standing | AUTHORITATIVE (not independently re-verified this session) | YES | — | — | not separately hashed this pass — unmodified this session |
| `observation_candidates/TOC-001.md`, `TOC-002.md`, `TOC-003.md`, `TEMPLATE.md` | Q1-era observation-candidate records, cited by the PATTERN-004 lineage (TOC-003) | Q1 2020 origin, live template | AUTHORITATIVE | YES | — | — | not separately hashed this pass — unmodified this session |
| `pine_scripts/AI_TRADER_CONTEXT_V1.pine` + `AI_TRADER_CONTEXT_V1_GOVERNANCE.md` | the installed AI_TRADER_CONTEXT_V1 indicator and its governance/fingerprint record | installed mid-Q3 2020 | AUTHORITATIVE | YES | — | — | not separately hashed this pass — unmodified this session; the governance record's own internally-recorded SHA256 (`c0b053aa900bc463327b694ab9f60c8e35bcd585e7746f584c8a4c03f64900fc`) is the authoritative fingerprint for the `.pine` file itself, per that file's own governance rule |

**Not included as authoritative evidence (excluded from this manifest, per the mandate's explicit
instruction not to include temporary scratch files):** none identified inside
`docs/trader_apprenticeship/` itself — every file in this directory is either a standing
methodology/governance document, a chronological evidence log, or a quarter-close deliverable. (Files
like `scratchpad_verify/`, `full_regression_*_output.txt`, etc. live at the repo root, outside this
directory, and are explicitly excluded from this checkpoint's staging — see the final report's
staging-discipline section.)

---

*This manifest is produced as part of `docs/trader_apprenticeship/`'s first-ever Git commit in this
repository. It does not modify the content of any file it describes.*
