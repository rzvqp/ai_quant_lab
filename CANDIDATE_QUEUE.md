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
| **CAND-0001** | PDH-PDL | institutional_reference_levels (MK-04) | `POLICY_PDH_PDL_v1.md` | DEFINED | UNSPECIFIED | PARTIALLY DEFINED | **SURVIVED_RED_TEAM_A** (RT-OPS-A-0001; carry W-sel/W-conf/W-ovl/W-e010) → Statistician |
| **CAND-0002** | COMPRESSION-EXPANSION-BREAKOUT | volatility_state_transition (market_state) | `POLICY_COMPRESSION_EXPANSION_v1.md` | DEFINED (with disclosed compression-anchoring risk) | UNSPECIFIED | PARTIALLY DEFINED | **SURVIVED_RED_TEAM_A** (RT-OPS-A-0001; carry compression-anchoring risk) → Statistician |
| **CAND-0003** | FVG-CE50-REACTION | imbalance_reaction (MK-03) | `POLICY_FVG_REACTION_v1.md` | DEFINED | UNSPECIFIED | PARTIALLY DEFINED | **SURVIVED_RED_TEAM_A** (RT-OPS-A-0001) → Statistician |
| **CAND-0004** | LIQUIDITY-VOID | price_discontinuity_void (Mod.5) | `POLICY_LIQUIDITY_VOID_v1.md` | activation DEFINED; trigger FAIL-CLOSED | UNSPECIFIED (moot) | NOT CURRENTLY TESTABLE | spec request → Statistician (ratify a void-reaction detector) |
| **CAND-0005** | BPR | balanced_price_range (MK-03) | `POLICY_BPR_v1.md` | activation DEFINED; trigger FAIL-CLOSED | UNSPECIFIED (moot) | NOT CURRENTLY TESTABLE | spec request → Statistician (ratify a BPR-reaction detector) |
| **CAND-0006** | PWH-PWL | weekly_reference_levels (MK-04) | `POLICY_WEEKLY_LEVELS_v1.md` | activation DEFINED; trigger FAIL-CLOSED | UNSPECIFIED (moot) | NOT CURRENTLY TESTABLE | spec request → Statistician (ratify a weekly-level touch detector) |
| **CAND-0007** | LEVEL-FVG-CONFLUENCE | multi_structure_confluence (MK-04×MK-03 via Mod.7) | `POLICY_LEVEL_FVG_CONFLUENCE_v1.md` | DEFINED (3-primitive interaction) | UNSPECIFIED | PARTIALLY DEFINED | **SURVIVED_RED_TEAM_A** (RT-OPS-A-0001; carry W-incr incremental-value vs CAND-0001/0003, W-dilate after=0) → Statistician |
| **CAND-0008** | VOID-DISPLACEMENT | discontinuity_driven_displacement (Mod.5×market_state) | `POLICY_VOID_DISPLACEMENT_v1.md` | DEFINED (2-primitive interaction) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |
| **CAND-0009** | LEVEL-BREAK-DRIVE | level_break_with_displacement (MK-04×market_state via Mod.7) | `POLICY_LEVEL_BREAK_DRIVE_v1.md` | DEFINED (3-primitive interaction; break-direction, opposite CAND-0001) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |
| **CAND-0010** | FVG-STACK-DENSITY | imbalance_density (MK-03 zones via Mod.7) | `POLICY_FVG_STACK_DENSITY_v1.md` | DEFINED (2-primitive interaction; same-polarity stack) | UNSPECIFIED | PARTIALLY DEFINED | queued → Red Team (A); risk → Statistician |

**Reaction-primitive bottleneck (surfaced by production):** ratified DETECTION primitives exist for many
objects (voids, BPRs, weekly levels), but ratified REACTION/interaction primitives exist only for PDH/PDL
(`detect_level_touches`) and single FVGs (`detect_fvg_reactions`). Candidates on objects **with** a
ratified reaction detector reach PARTIALLY DEFINED (CAND-0001/0003); those **without** stop at NOT
CURRENTLY TESTABLE (CAND-0004/0005) and route a reaction-detector spec request to the Statistician.
CAND-0002 is self-triggering (the expansion bar is its own event), so it needs no separate reaction primitive.

---

## STATE: `WAITING_FOR_NEW_PRIMITIVES` (2026, after CAND-0010)

The reasonable distinct-mechanism combinations of the **currently, unambiguously-usable** ratified
primitives are covered (CAND-0001…0010). Further candidates from this set would be parametric variants /
context filters (prohibited) or would require unratified constructs. **No weak or duplicate candidate is
forced.** Discovery auto-resumes the moment a new ratified primitive (or a scope ruling below) lands.

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
