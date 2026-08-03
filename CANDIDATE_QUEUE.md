# ALPHA DISCOVERY — CANDIDATE QUEUE

Continuous-production queue. Each candidate is grounded in a **verified, ratified** repo primitive
(status checked before citing), formalized in the canonical schema with **Part A (entry mechanism)** and
**Part B (risk management)** separated. Downstream (Red Team → Statistician → VE) consumes in order.
Flow A does not wait.

**Ratified detector modules available** (verified 2026): `institutional_levels.py` (MK-04, PDH/PDL/weekly,
partial-ratified), `market_state.py` (compression/expansion/sessions, ratified Statistician v2.6.1),
`imbalance_mechanics.py` (MK-03 FVG/BPR, CLOSED v2.5.6), `order_block_void.py` (liquidity void,
ratified), `order_flow.py` (order blocks, ratified — but the OB family is directive-BLOCKED).
**NOT ratified (draft — not built on):** `market_structure.py` (MK-01), `liquidity_mechanics.py` (MK-02).

**W10 handoff standard (mandatory, all policies):** every policy declares, for each cited primitive, a
cross-repo reference block — `source_repository`, `source_branch`, `source_commit` (full hash),
`source_file`, `primitive`, `source_hash` (sha256 of the file @ commit) — so a consumer verifies grounding
without the files being co-located. The ratified primitives currently live on
`alpha1/discovery-mk-matrix-v1` @ `8edbf9900b761b774b901a13a5b325be578468e6`, a **different branch** than
these policies (`alpha-automation-v1`). Applied retroactively to CAND-0001/0002 and to every new candidate.

**Standing gap affecting every candidate's Part B:** no ratified **structural** stop/exit primitive exists
(fixed-ATR/RR is disqualified — identical 0.378–0.385 winrate across 6 mechanisms; the cited v8.5 M_031–
M_034 is confirmed nonexistent). Every candidate's Part B is therefore UNSPECIFIED and routed to the
Statistician as a specification request. This is a risk-layer gap, **not** a market-mechanism gap.

| candidate_id | policy | family | file | Part A | Part B | verdict | state |
|---|---|---|---|---|---|---|---|
| **CAND-0001** | PDH-PDL | institutional_reference_levels (MK-04) | `POLICY_PDH_PDL_v2.md` (v2.0; v1.2 = history) | DEFINED | **COMPLETED — DEMO_BASELINE** (structural: stop=touch-bar extreme, target=opposite prior-day level, time-stop=day close; mgmt absent; sizing 1R; NOT VALIDATED / NOT PRODUCTION APPROVED) | **DEFINED (DEMO_BASELINE)** | **STATISTICIAN_PROTOCOL_SPECIFIED** (STAT-BATCH-A-0001; W-conf→matched-null reused from OBDZ, W-sel disclosed not corrected, W-ovl→mandatory diagnostic vs CAND-0007, W-e010→AMBIGUOUS→Red Team) · **Part B now completed → unblocks Validation Engine**; DEMO pipeline: Red Team safety/lookahead → Statistician DEMO criteria → VE → CEO → AI Trader (DEMO only) · **RT-OPS-B-0001 (Part B): SURVIVED_RED_TEAM_A — CONDITIONAL. Lookahead/circularity/hidden-optimization PASS. HARD PRE-DEMO SAFETY GATE: S1 intrabar stop∧target must resolve worst-case/INVALID-EXECUTION (MIN_STOP_FLOOR_PREREG), not optimistic; S2 apply min_executable_risk floor to 1R sizing; S3 define target-already-visited rule. If the DEMO engine cannot be shown to enforce Engine-v2, the policy must NOT trade.** · **STATISTICIAN_DEMO_CRITERIA_DEFINED (STAT-CAND0001-DEMO-CRITERIA-v1.0, manifest v2.7.34): all three gates bound as executable preconditions with named per-trade audit fields — S1 worst-case hierarchy STOP>TIME-STOP>TARGET across all three collisions (INVALID_EXECUTION kept narrow, per convention); S2 min_executable_risk verbatim, 1R sized on the floored distance, effective_spread=realized; S3 target scanned strictly from entry_idx+1. Deferrals resolved: min_trades=25 (a reporting-suppression floor, NOT a power floor — DEMO runs no test), regimes_permitted=no filter (regime not computable live), cost OBSERVED not modeled + mandatory reconciliation vs the lab constant. Red Team condition carried verbatim. DEMO is NOT validation; no result promotes anything.** → **Validation Engine** (executability + mechanical gate verification) |
| **CAND-0002** | COMPRESSION-EXPANSION-BREAKOUT | volatility_state_transition (market_state) | `POLICY_COMPRESSION_EXPANSION_v2.md` (v2.0; v1.1 = history) | DEFINED (with disclosed compression-anchoring risk) | **COMPLETED — DEMO_BASELINE** (structural: stop=opposite extreme of the expansion bar, exit=first opposing expansion; mgmt absent; sizing 1R; NOT VALIDATED / NOT PRODUCTION APPROVED) | **DEFINED (DEMO_BASELINE)** | **STATISTICIAN_PROTOCOL_SPECIFIED** (STAT-BATCH-A-0001; compression-anchoring risk carried) · **Part B now completed → unblocks Validation Engine** · **RT-OPS-B-0002 (Part B): SURVIVED_RED_TEAM_A — conditional. Lookahead/circularity/hidden-opt PASS. Finding H: exit time-stop is the BLOCK boundary (not the day) → a trade with no opposing expansion holds to block-end (weeks) — DEMO must add a horizon rule. S2 immune (expansion guarantees a wide stop). Bind S1 worst-case.** |
| **CAND-0003** | FVG-CE50-REACTION | imbalance_reaction (MK-03) | `POLICY_FVG_REACTION_v2.md` (v2.0; v1.0 = history) | DEFINED | **COMPLETED — DEMO_BASELINE** (structural: stop=FVG far edge = Q4 inversion boundary, target=FVG near edge; mgmt absent; sizing 1R; RR≈1 as midpoint geometry not chosen; NOT VALIDATED / NOT PRODUCTION APPROVED) | **DEFINED (DEMO_BASELINE)** | **STATISTICIAN_PROTOCOL_SPECIFIED** (STAT-BATCH-A-0001; standard protocol) · **Part B now completed → unblocks Validation Engine** · **RT-OPS-B-0002 (Part B): SURVIVED_RED_TEAM_A — conditional, TIGHTEST GATE. Lookahead/circularity/hidden-opt PASS. S2 LIVE & ROUTINE: stop = ce_50−lower = FVG_height/2, arbitrarily small for small FVGs → unbounded 1R; min_executable_risk floor essential. S1 ACUTE: one bar routinely spans both FVG edges (stop∧target). If floor+worst-case unenforceable, CAND-0003 must NOT trade.** |
| **CAND-0004** | LIQUIDITY-VOID | price_discontinuity_void (Mod.5) | `POLICY_LIQUIDITY_VOID_v1.md` | activation DEFINED; trigger FAIL-CLOSED | UNSPECIFIED (moot) | NOT CURRENTLY TESTABLE | spec request → Statistician (ratify a void-reaction detector) |
| **CAND-0005** | BPR | balanced_price_range (MK-03) | `POLICY_BPR_v1.md` | activation DEFINED; trigger FAIL-CLOSED | UNSPECIFIED (moot) | NOT CURRENTLY TESTABLE | spec request → Statistician (ratify a BPR-reaction detector) |
| **CAND-0006** | PWH-PWL | weekly_reference_levels (MK-04) | `POLICY_WEEKLY_LEVELS_v1.md` | activation DEFINED; trigger FAIL-CLOSED | UNSPECIFIED (moot) | NOT CURRENTLY TESTABLE | spec request → Statistician (ratify a weekly-level touch detector) |
| **CAND-0007** | LEVEL-FVG-CONFLUENCE | multi_structure_confluence (MK-04×MK-03 via Mod.7) | `POLICY_LEVEL_FVG_CONFLUENCE_v2.md` (v2.0; v1.0 = history) | DEFINED (3-primitive interaction) | **COMPLETED — DEMO_BASELINE** (structural: stop=below BOTH structures = min(low[touch],FVG.lower), exit=opposite prior-day level + day time-stop; mgmt absent; sizing 1R; NOT VALIDATED / NOT PRODUCTION APPROVED) | **DEFINED (DEMO_BASELINE)** | **STATISTICIAN_PROTOCOL_SPECIFIED** (STAT-BATCH-A-0001; H0=incremental value vs better of CAND-0001/CAND-0003, k=0 primary/{1,2} sensitivity) · **Part B now completed → unblocks Validation Engine** · **RT-OPS-B-0002 (Part B): SURVIVED_RED_TEAM_A — conditional. Lookahead/circularity/hidden-opt PASS. CEO Q answered: stop below BOTH structures is WIDER → rarely hits min_executable_risk floor → PROTECTIVE vs S2 (opposite of CAND-0003). Flip side (risk-quality, not safety): a very wide stop can give R:R<1 vs the opposite-level target. Bind S1 worst-case (rare here).** |
| **CAND-0008** | VOID-DISPLACEMENT | discontinuity_driven_displacement (Mod.5×market_state) | `POLICY_VOID_DISPLACEMENT_v1.md` | DEFINED (2-primitive interaction) | UNSPECIFIED | PARTIALLY DEFINED | **SURVIVED_RED_TEAM_A** (RT-OPS-A-0002; clean) → Statistician; risk → Statistician |
| **CAND-0009** | LEVEL-BREAK-DRIVE | level_break_with_displacement (MK-04×market_state via Mod.7) | `POLICY_LEVEL_BREAK_DRIVE_v1.md` | DEFINED (3-primitive interaction; break-direction, opposite CAND-0001) | UNSPECIFIED | PARTIALLY DEFINED | **SURVIVED_RED_TEAM_A** (RT-OPS-A-0002; carry W-partition = one-sided boundary vs CAND-0001, opposite trades on displacement-touch bars; W-dir-mask) → Statistician; risk → Statistician |
| **CAND-0010** | FVG-STACK-DENSITY | imbalance_density (MK-03 zones via Mod.7) | `POLICY_FVG_STACK_DENSITY_v1.md` | DEFINED (2-primitive interaction; same-polarity stack) | UNSPECIFIED | PARTIALLY DEFINED | **SURVIVED_RED_TEAM_A** (RT-OPS-A-0002; carry W-incr = subset of CAND-0003, test incremental density value) → Statistician; risk → Statistician |
| **CAND-0011** | OB-SWEEP-REJECTION | order_block_rejection (Mod.5, circularity-free) | `POLICY_OB_REJECTION_v1.md` | DEFINED (2-primitive; anti-E010 disjoint windows) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |
| **CAND-0012** | OBREJ-LEVEL-CONFLUENCE | rejection_at_level_confluence (Mod.5×MK-04 via Mod.7) | `POLICY_OBREJ_LEVEL_CONFLUENCE_v1.md` | DEFINED (3-primitive interaction) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |
| **CAND-0013** | DEMAND-ZONE-REENTRY | demand_supply_zone_reaction (Mod.5, non-consumable) | `POLICY_DEMAND_ZONE_v1.md` | DEFINED (2-primitive; full-bar non-consumable zone) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |
| **CAND-0014** | OB-MITIGATION | order_block_mitigation (Mod.5, circularity-free) | `POLICY_OB_MITIGATION_v1.md` | DEFINED (2-primitive; first mitigation, anti-E010 disjoint) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |
| **CAND-0015** | OBREJ-FVG-CONFLUENCE | rejection_imbalance_confluence (Mod.5×MK-03 via Mod.7) | `POLICY_OBREJ_FVG_CONFLUENCE_v1.md` | DEFINED (3-primitive interaction; rejection×FVG pair) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |
| **CAND-0016** | MITIG-LEVEL-CONFLUENCE | mitigation_at_level_confluence (Mod.5×MK-04 via Mod.7) | `POLICY_MITIG_LEVEL_CONFLUENCE_v1.md` | DEFINED (3-primitive interaction; mitigation×level pair) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |
| **CAND-0017** | DZ-FVG-CONFLUENCE | zone_imbalance_confluence (Mod.5×MK-03 via Mod.7) | `POLICY_DZ_FVG_CONFLUENCE_v1.md` | DEFINED (3-primitive interaction; demand-zone×FVG pair) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |

**Reaction-primitive bottleneck (surfaced by production):** ratified DETECTION primitives exist for many
objects (voids, BPRs, weekly levels), but ratified REACTION/interaction primitives exist only for PDH/PDL
(`detect_level_touches`) and single FVGs (`detect_fvg_reactions`). Candidates on objects **with** a
ratified reaction detector reach PARTIALLY DEFINED (CAND-0001/0003); those **without** stop at NOT
CURRENTLY TESTABLE (CAND-0004/0005) and route a reaction-detector spec request to the Statistician.
CAND-0002 is self-triggering (the expansion bar is its own event), so it needs no separate reaction primitive.

---

## STATE: `PRODUCING` — resumed after CEO ruling on `order_flow.py` (2026)

**CEO RULING (granted):** the order-block-family block covers the OLD circular candidates
(E010/E013/E015/E016) ONLY — NOT the re-engineered `order_flow.py` primitives (`detect_mitigations`,
`detect_rejections`, `detect_demand_zones`, `detect_order_blocks`/`track_breaker` as anchors), whose
selection/measurement windows are disjoint by construction (E010 circularity impossible; Red Team
confirmed MK-01 F1/F2 non-contaminating — only the inert `Block` dataclass is imported). **UNBLOCKED.**
STILL BLOCKED: E010/E013/E015/E016 as hypotheses; `market_structure.py`, `liquidity_mechanics.py` (DRAFT).

New families now in production: **order-block sweep-rejection (CAND-0011)**, demand-zone reaction,
mitigation (circularity-free), + confluences with levels / FVG / void.

The single-primitive space of the earlier ratified set (CAND-0001…0010) remains covered; no variants forced.

**Unlocks that would immediately resume production** (each opens distinct mechanisms + their confluences):
- ratified **void-reaction / void-fill** detector → completes CAND-0004 + void×level, void-fill confluences;
- ratified **weekly-level touch** detector → completes CAND-0006 + weekly×level/FVG confluences;
- ratified **BPR-reaction** detector → completes CAND-0005 + BPR confluences;
- any ratified **structural stop/exit** primitive → completes Part B for all 10 (PARTIALLY → possibly DEFINED);
- a **void price-zone** concept (the module stores void magnitude, not a fillable zone) → void-zone confluences.

**⚠ FLAGGED FOR CEO RULING — potential immediate unlock, held fail-closed on ambiguity:**
`code/order_flow.py` (Module 5, RATIFIED v2.6.1→v2.7.9) provides **circularity-free** reaction primitives —
`detect_mitigations`, `detect_rejections`, `detect_demand_zones` — built with the **anti-E010 disjoint-
window construction** (selection window a pure function of bars `≤ event_idx`; measurement window
`[event_idx, +H)`; disjoint by construction, the exact defect that failed E010/E013/E016). These reuse
`detect_order_blocks` (OB formation), so they are OB-anchored. The order-block **family** (E010/E013/E015/
E016) is under a STRICT block — but those were the **old circular** candidates; these are the **ratified
re-engineered** primitives. **Ambiguous whether the block covers them; Alpha will not build on them
without a CEO ruling.** If permitted, they unlock: demand-zone reaction, sweep-rejection, mitigation
(circularity-free), and their confluences with levels/FVGs/voids — a substantial new batch.

Producing continuously; auto-resumes on a new ratified primitive or the ruling above.
