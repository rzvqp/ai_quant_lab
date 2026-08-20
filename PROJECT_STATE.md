# PROJECT STATE — AI Quant Lab (persisted by CEO order)

Repo `ai_quant_lab-wp5b` · branch `discovery-mk-matrix-v1` · mirrored to 4 remotes (alpha1/discovery/lab/trader).
This document is the Git-persisted snapshot of program status; the conversation is not the system of record.

## PRIORITY
- **COMPLETE_AI_TRADER** — the single active critical path.
- Alpha **PAUSED_BY_CEO**; Statistician and Data Acquisition **on pause**.

## BLOCKER
- **MANDATE_2_REVIEW_CONDITIONAL · INTEGRATION_BLOCKED**.
- **LIVE_SHADOW forbidden**.
- Cause: **N3 and N4 were never packaged** into an installable artifact (they lived only in `code/`).

## DELIVERED
- **ve_brain 0.1.3**, wheel built from `a1d2a6d`, **ARTIFACT_PIN_PASS**.
  - SHA-256 `edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11`.
  - `validated_core_commit fbc0f20` · `manifest_schema_version 1.0`.
- **AI Trader** `f4859a5` steps 1–4 · `7d836b3` steps 5–12 partial, **20/25 tests**.
- **ve_tower** — official N1–N4 phenomena provider.
  - **0.1.0 REJECTED** (TOWER_HANDOFF_FAIL: no strict timeframe, no per-node data identity). Wheel SHA-256 `e5457561…f08b2db5` kept for audit.
  - **0.2.0** (contract v2) — TOWER_HANDOFF_CONDITIONAL: identity/timeframe/substitution/byte-integrity closed, but the loader left partial modules on a failed attempt. Wheel SHA-256 `3ea791ba…cc2e91a8` kept for audit.
  - **0.3.0** (contract still v2; bootstrap-only, wheel from `6daf2aa`) — transactional loading: a failed attempt rolls back **everything it introduced**, restores pre-existing modules exactly (same identity), preserves the original exception. Wheel `ve_tower-0.3.0-py3-none-any.whl` SHA-256 `0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2`; 38 tests; empty-venv verified. Sidecar `ve_tower/HANDOFF_MANIFEST-0.3.0.json`. **Physical wheel committed at `ve_tower/release/ve_tower-0.3.0-py3-none-any.whl`** (git-stored bytes hash to the pinned SHA). (2nd condition is at AI Trader: ve_tower runs in a SEPARATE process+venv; import in the main process forbidden.)

  - **0.4.0** (adds N2 producer; N3/N4 stay v2) — exposes `run_n2` over ratified `bias_h1` @850815f. N2_HANDOFF_CONDITIONAL (RT-TOWER-0007): `run_n3/run_n4` trusted any caller `n2_fingerprint`. Wheel SHA-256 `fe9f8b14…9a8852` kept for audit.
  - **0.5.0** (chain orchestrator) — `run_tower_chain` runs N2→N3→N4 internally; caller cannot supply `n2_fingerprint`. Defect: called `run_n4(atr=None)` → N4 always `atr_unavailable`. Wheel SHA-256 `6d99baf6…4cd94df7` kept for audit.
  - **0.5.1** (ATR internal) — computes ATR via canonical `market_state.atr14`; chain reaches N4. Defect (RT-TOWER-0009): N3 `AtrProvenance.atr_value`=`atr14[-1]` but zone_map consumes `atr14[i-1]`. Wheel SHA-256 `297aac5d…268807` kept for audit.
  - **0.5.2** (provenance-only; decision unchanged) — N3 `AtrProvenance.atr_value`=`atr14(M15)[i-1]` (the consumed ATR; `atr_value==level.band/0.25`), added `evaluation_index`/`consumed_atr_index`/`consumed_bar_timestamp`. N4 stays `atr14[-1]`. N3 levels + N4 confirmation identical to 0.5.1. Fixes TOWER_CHAIN_ATR. 76 tests. Awaiting Red Team TOWER_CHAIN_ATR.

## N1 REPLAY (MANDATE N1 CANONICAL REPLAY PACKAGING)
- **VE-RANGE-V4_4_1-STALE-CANDIDATE-DESIGN-001 — `V4_4_1_STALE_DESIGN_READY_FOR_CALIBRATION`.** CEO
  authorized a focused design+calibration-plan mandate (no implementation, no numeric parameter selection)
  building on the traversal diagnostic (`b1dcf92`). **Design**: a new pre-confirmation transition `T-STALE`
  (`CANDIDATE`/`FORMING → TERMINATED`, reason `STALE_CANDIDATE_ABANDONED`), inserted in `_step_macro`
  between `T-KILL` and `T2`/`T3` (re-read exact lines this mandate: degeneracy_check 889-892, `zones is
  None` branch 894-896), applying only to `reached_confirmed=False` structures with an established boundary.
  **Staleness definition** (chosen after working through 5 candidate concepts, not picked arbitrarily):
  requires BOTH a minimum count of rejected swing touches AND genuine two-sided alternation in those
  rejections, within a bounded trailing window — deliberately NOT touch-scarcity-based (would false-positive
  on legitimately slow/quiet ranges) and NOT price-distance-alone (weaker than the confirmed-structure
  excursion analogy already used for WEAKENING). **The alternation requirement is the anti-churn mechanism**:
  a clean one-directional trend's rejected swings are predominantly one-sided, so they never satisfy
  alternation, protecting against the mandate's named churn risk without any new cooldown parameter. New
  state: one bounded rejected-touch deque on `StructureV44` (kept structurally separate from the existing
  accepted-touch `_touch_tags`), reusing `start_ts`/boundary fields already present — no other new state.
  **Same-bar vs next-bar replacement resolved explicitly (not left open)**: next causal bar only (matches
  every existing slot-freeing precedent — T-KILL/T8/T9 — none of which replay the triggering bar's own
  evidence to an immediate successor; avoids same-bar re-entrancy complexity and keeps snapshot/chunk
  invariance trivial). **Episode-identity interaction resolved via reuse, not a new rule**: calls the
  existing unmodified `_record_macro_termination_for_episode_identity`; a genuinely stale zone naturally
  fails IoU-overlap against its replacement (both traced FB14 cases showed 0.000 price-IoU), so
  CONTINUATION-vs-REPLACEMENT falls out correctly without new logic. Self-falsified against all 16
  mandate-required scenarios (table in the report) — no counterexample found; two scenarios (trend/stair-step)
  explicitly protected by the anti-churn property rather than merely "unaffected." Zero touch to ER/RND/
  traversal/`MIN_TRAVERSALS`/`W`/WEAKENING/INTERNAL — confirmed explicitly section-by-section. 4 new
  parameters inventoried (rejected-touch window — RATIFIED_REUSE-of-`W` hypothesis; min rejection count —
  likely CALIBRATED; min alternation count — possibly DERIVED as a floor like `MIN_TRAVERSALS=1`; min
  candidate age — possibly DERIVED from `n_touch`), none chosen/ranked/swept. Calibration plan designed
  (synthetic construction + ratified reuse, dual-sided acceptance bar protecting BOTH stale-release AND
  slow-range-survival, explicit sensitivity/fragility check) — mirrors `898f149`'s own successful protocol,
  zero FB14/MB3 weight. 10 required tests specified (STALE-1..10) + 1 mutation test disabling the
  alternation requirement specifically (must reopen the churn risk, proving it's load-bearing not vacuous).
  Recommended **V4.4.1** versioning; new `contract_version="range-hierarchical-v4.4.1"`, `REASONS_V441`=41
  (additive), fail-closed snapshot separation via the SAME existing mechanism (no new logic). Full report:
  `ve_n1_replay/VE_RANGE_V4_4_1_STALE_CANDIDATE_DESIGN.md`. Next owner: CEO (authorize a separate future
  calibration mandate for the 4 parameters, BEFORE any implementation mandate). NOT authorized: implementation,
  Strategy Catalog/Alpha/AI Trader/LIVE_SHADOW/broker/live trading/V4.4 promotion.
- **VE-RANGE-V4_4-TRAVERSAL-DIAG-001 — `TRAVERSAL_FAILURE_DIAGNOSED_READY_FOR_FOCUSED_DESIGN`.** Red Team's
  fresh blind batch (`dfebe8f`, RT-RANGE-V4_4-FRESH-BLIND14-VALIDATION-001) found `V4_4_FRESH_BLIND14_
  GENERALIZATION_NOT_SUPPORTED`: H1/H4/H5 PASS (directional FP 13→7, total FP 19→10, precision/F1 up) but
  H2/H3 FAIL (RANGE TP 15→12, recall 0.625→0.500), all 3 lost TP attributed to `INSUFFICIENT_TRAVERSAL`.
  CEO authorized a focused, non-implementing diagnostic. **VE reproduced all 3 lost TP exactly** (byte-
  verified FB14 bars + labels via escrow, config_id/fingerprint cross-checked against `3bb61cf`) and found
  `INSUFFICIENT_TRAVERSAL` is a **downstream symptom, not the root cause**: in all 3 spans, the same single,
  never-confirmed macro candidate persists for the ENTIRE span with **zero price-IoU overlap** against the
  CEO's labeled zone — traversal is computed against a stale, wrong boundary, not a correctly-anchored one.
  Directly proven the market genuinely rotates throughout (38 and 66 alternating swings detected in the two
  traced regions respectively) but every swing is rejected by the stale cluster's tolerance check.
  **Root-cause mechanism** (found by running V4.3 on the identical bars): V4.3's SAME starting candidate
  (identical swings, same start bar) confirms quickly under V4.3's weaker width+touch+duration-only gate,
  later breaks out, freeing the slot for a fresh, correctly-anchored candidate (V4.3's actual matched TP,
  boundary within ~0.001 of the CEO's stated level) — V4.4's discrimination gate (T3) correctly rejects the
  SAME early candidate (genuinely directional at that point in its life) but nothing ever kills it
  afterward (`degeneracy_check`, unchanged since V4.3, checks only width/inversion, never staleness), so it
  blocks `_active_macro` forever. **Classified `TRAVERSAL_FAILURE_CLASS = D — INTERACTION_FAILURE`** (T3 ×
  the pre-existing, V4.3-inherited candidate-replacement architecture) — not A/B/C: no numeric retuning
  fixes a wrong-boundary problem, ER/RND aren't independently also failing, no spec-vs-code drift (Red
  Team's own `845a03c` already independently confirmed T3/degeneracy_check faithfully implement the frozen
  design). One found-and-superseded methodological error disclosed honestly (first reproduction attempt fed
  24 bars of render-padding into the detector as pre-context; caught via cross-check against the frozen
  predictions' exact end_ts values 19/83/111/144, all 4 matched after correcting to canonical-bars-only). A
  related but distinct, NOT-folded-in observation flagged for a future mandate: forced `EPISODE_REPLACEMENT`
  (never `CONTINUATION`) after any `BREAKOUT_ACCEPTED`, which may over-fragment a range the CEO describes as
  continuous through internal deep sweeps. Designed (NOT implemented, NOT parameterized) a candidate
  correction family — additive unconfirmed-candidate "staleness abandonment," a new LIFECYCLE-role
  termination pathway parallel to `degeneracy_check`, touching zero of ER/RND/traversal/alternation/
  WEAKENING/episode-identity/confirmation-timing/snapshot architecture — self-falsified against all 12
  mandate-required adversarial scenarios (no counterexample found; binding constraint recorded: must be
  rejection-count-based, not touch-scarcity-based, to avoid penalizing genuinely slow/quiet ranges).
  Recommended versioning **V4.4.1** (no new state, one new edge into TERMINATED, directional architecture
  fully untouched) and fresh-evidence plan (analytic/synthetic derivation → fresh blind batch, never FB14/
  MB3). Zero implementation, zero parameter selection, zero MB3-025→048 access. Full report:
  `ve_n1_replay/VE_RANGE_V4_4_TRAVERSAL_DIAGNOSTIC.md`. Next owner: CEO (authorize a separate scoped design/
  calibration mandate for the staleness-abandonment family). NOT authorized: implementation, Strategy
  Catalog/Alpha/AI Trader/LIVE_SHADOW/broker/live trading/V4.4 promotion.
- **VE-RANGE-V4_4-IMPLEMENTATION-001 — `V4_4_IMPLEMENTATION_READY_FOR_RED_TEAM_AUDIT`.** Frozen mechanism
  (`c57d103`) + calibrated registry (`898f149`) converted to production code, additively:
  `ve_n1_replay/range_semantic_v4_4.py` (67,340 bytes) + `range_engine_v4_4.py` (9,599 bytes), zero V4.3 bytes
  changed (`git diff HEAD -- range_semantic_v4_3.py range_engine_v4_3.py` = 0 lines). `config_id()` reproduces
  the frozen `23d98c07…` exactly (no `V4_4_CONFIG_ID_MISMATCH`). Implementation fingerprint
  `"v4-4-implementation-freeze-2026-08-20"`, source sha256 recorded (combined
  `b799ec6f…5f85e23`). 40 reason codes (29 V4.3 + 11 new), all 11 new codes mechanically proven reachable via
  the public API except the ONE documented exception (`EPISODE_MERGED`, structurally unreachable while MACRO
  stays single-active-at-a-time — proven, not asserted). **76 new tests** (internal-parity ×5, transitions
  ×27, causality ×7, snapshot-robustness ×14, reason-code-reachability ×2, adversarial-suite ×22 incl.
  count-check) + full **394-test V4.3 baseline** unaffected = **470/470 passing**, reproduced twice
  independently post-freeze. mypy --strict clean. 22/22 pre-registered adversarial scenarios pass against
  frozen expected chronology (`236e8e7` §10 + §12); #21/#22 (slow-drifting-equilibrium, violent-zigzag) both
  CONFIRM as ranges — the exact already-disclosed, non-blocking risk from `898f149` §7 / `236e8e7` §12,
  recorded honestly per mandate, not hidden, not "fixed" by undisclosed recalibration. All 6 mandate-named
  mutations (disable ER gate / remove WEAKENING timeout / reverse gate priority / disable merge / break
  absolute-vs-relative confirmation timing / accept wrong config snapshot) caught by the suite; file
  byte-diff-confirmed identical after revert. Rollback test: removing both V4.4 files leaves the 394-test V4.3
  baseline 100% green (0 errors); restoring V4.4 returns to 470/470. Complexity/memory measured empirically
  (flat ≈0.006s/200-bar-chunk and flat ≈2000-2100-byte snapshot size across 1,440 varied bars; history deques
  directly confirmed to cap at `maxlen=64` via a 100-append ring-buffer-eviction check). **Two real bugs found
  and fixed during construction, before freeze**: (1) `restore_state()` mutated `self` field-by-field in
  place — a failure partway through left the producer in a mixed old/new state, violating "no partial
  mutation"; confirmed as an INHERITED V4.3 weakness too (reproduced identically against
  `RangeSemanticProducerV43`), fixed only in the new V4.4 file via build-into-scratch-then-swap-`__dict__`.
  (2) `_awaiting_role` restore always reconstructed via plain `Structure.restore()` even for MACRO-origin
  entries, silently downcasting a `StructureV44` awaiting post-breakout role resolution — fixed to discriminate
  on `depth`. Plus one disclosed gap-then-fix: `alternation_rate`/`ALT_MIN`/`touches_in_window` were written
  but never wired into T3 — `INSUFFICIENT_ALTERNATION_EVIDENCE` was defined-but-unreachable; wired in as a
  non-blocking additional event (alternation stays SUPPORTING_ONLY, mandate §5, never a gate). Full 25-item
  report: `ve_n1_replay/VE_RANGE_V4_4_IMPLEMENTATION_REPORT.md`. Next owner: Red Team,
  `RT-RANGE-V4_4-IMPLEMENTATION-AUDIT`. NOT authorized: Strategy Catalog/Alpha/AI Trader/LIVE_SHADOW/broker/
  live trading.
- **VE-RANGE-V4_4-CALIBRATION-001 — mechanism frozen, all 7 parameters + 2 anchors resolved,
  `V4_4_CALIBRATION_PASS_WITH_NONBLOCKING_NOTES`** (3 separate, correctly-sequenced, unamended commits:
  freeze `c57d103` → precommitted protocol `967222a` → results/registry/verdict `[this commit]`; all pushed +
  local=remote-verified on all 4 mirrors after EACH commit, not just at the end). Independently re-verified
  `RT-RANGE-V4_4-DESIGN-AUDIT-001` (`ca550d4`, `statistician-foundation`, local=remote ×4) by reading the full
  106-line report — confirmed exact unresolved inventory (`W`/`MIN_TRAVERSALS`/`ER_weakening`/
  `RND_weakening`/`WEAKENING_MAX_BARS`/`IOU_CONTINUE`/`GAP_MAX` + anchors `ER_max`/`RND_max`). **Freeze
  locks mechanism only** (state machine/transitions/priority/signal-roles/WEAKENING/episode-identity/
  invariants/snapshot-plan — every element cross-referenced to its exact source in `236e8e7`/`f241698`, none
  re-derived from memory), explicitly leaves all 9 numeric items open. **Protocol precommitted BEFORE any
  result-guided selection** (`V4_4_CALIBRATION_PROTOCOL_PRECOMMITTED=TRUE`) — fixed candidate
  family/selection-method/failure-criterion per parameter, an eligible-evidence hierarchy excluding MB3
  entirely (checked: no pre-existing non-MB3 calibration corpus exists in this project), and — critically —
  pre-registered the EXACT shallow-channel decision criteria (correct-rejection/acceptable-ambiguity/
  blocker/unacceptable-TP-damage) BEFORE the results were treated as final, specifically so that criterion
  couldn't be reverse-engineered from a desired conclusion. **All 9 items resolved** via synthetic
  construction (known-ground-truth price paths, not MB3) + analytical/ratified-reuse derivation — zero
  forced, zero MB3-influenced: `ER_max=0.5`/`RND_max=1.0` (validated not re-derived — natural-midpoint/
  self-referential anchors), `W=29` (=`d_macro`, ratified reuse), `MIN_TRAVERSALS=1` (floor confirmed exactly
  right via an `H,H,L,L` touch-order counterexample legal under the existing unchanged `n_touch` gate),
  `ER_weakening=0.75`/`RND_weakening=2.0` (deliberate hysteresis margins above the confirmation anchors),
  `WEAKENING_MAX_BARS=22`=`K_reentry`, `IOU_CONTINUE=0.5`/`GAP_MAX=12`=`d_internal` (both ratified-reuse or
  natural-midpoint). **Shallow-channel finding, disclosed not hidden**: synthetic sweep across 9 required
  scenarios + a drift-rate sweep + a `W`-neighborhood sweep CONFIRMS (not just re-asserts) a genuine,
  quantified, reproducible weak-signal blind spot — a gentle channel can show ER/RND comparable to or lower
  than a clean range. Precisely distinguished from the ALREADY-disclosed false-REJECT risk (slow-drift range
  wrongly rejected): this is a related but DISTINCT false-ACCEPT risk (gentle channel wrongly accepted).
  **NOT fixed by retuning** (explicitly refused per protocol's pre-registered no-fishing rule — confirmed via
  computation that tightening `ER_max` within reasonable bounds doesn't catch it without destroying the
  required `clean_range`/`noisy_range` cases) — carried forward as a named, reproducible test case for the
  future fresh-blind-batch stage. Blocker check correctly NOT triggered (`clean_range`/`noisy_range` both
  pass cleanly with margin — the actual bright-line test). Joint sanity (7 fixed yes/no questions, no
  scoring): all clear, no `FOUNDATIONAL_CONFLICT`. `IOU_CONTINUE=0.5` validated on both mandate-required
  cases (internal-rotation→CONTINUE, independent-ranges→REPLACEMENT) + stable across a `{0.4,0.5,0.6}`
  sensitivity sweep. `W`/`IOU_CONTINUE` both classified `STABLE` (no qualitative flip in tested
  neighborhoods) — zero `PARAMETER_FRAGILITY_FLAG`s raised. **`config_id()` now legitimately computable**
  (hashes parameter VALUES, all now resolved — distinct from the `implementation_fingerprint`, which hashes
  SOURCE CODE and correctly stays uncomputed since no V4.4 code exists) =
  `23d98c07488913c1c99a7397b2f8791f4727115e04bdefc283fb6bfc4a468969`, via the exact unmodified `ConfigV43`
  formula. 4 unresolved risks carried forward honestly (weak-signal gap, `RND_weakening`'s weaker derivation,
  `GAP_MAX`/`WEAKENING_MAX_BARS` lacking full-lifecycle tests, TP-preservation still an undischarged
  hypothesis) — none blocking, each named/bounded/next-stepped. Full packages:
  `ve_n1_replay/VE_RANGE_V4_4_DESIGN_FREEZE.md`, `VE_RANGE_V4_4_CALIBRATION_PROTOCOL.md`,
  `VE_RANGE_V4_4_CALIBRATION_RESULTS.md`. `V4_4_IMPLEMENTATION_AUTHORIZED_FOR_CEO_DECISION` stated per
  mandate (this mandate does NOT itself authorize implementation). Zero code/V4.3 file changed throughout;
  `MB3-025→048` never accessed at any point across all 3 commits. Next owner: CEO (implementation
  authorization decision), then the unchanged Red-Team-endorsed sequence (implement → Red Team static audit
  → fresh blind batch, never MB3).
- **VE-RANGE-V4_4-CONVERGENCE-001 — convergence closed, verdict upgraded to
  `V4_4_DESIGN_READY_FOR_RED_TEAM_REVIEW`** (no code/config/V4.3 file touched, `MB3-025..048` never accessed —
  the whole mandate was performable from already-committed artifacts). Independently verified
  `RT-RANGE-DIAG-AUDIT-001` (`3be88a1`, `statistician-foundation`, local=remote ×4) by reading the full 90-line
  report, not the mandate's own summary: Red Team's OWN independent engine re-run reproduces all 62/62
  confirmed MB3 structures — a SEPARATE confirmation of the same instrumentation-fidelity claim VE made in
  `071fbd7`, arrived at independently. **10/10 convergence-matrix rows MATCH, zero conflicts** — Red Team's
  disposition `V4_3_DIAGNOSTIC_FOUNDATION_CONFIRMED` + explicit "no V4.4 design assumption must change" is
  confirmed by direct row-by-row comparison, not merely cited. Two genuinely NEW, stronger pieces of evidence
  incorporated (mechanism unchanged, not a redesign): (1) Red Team directly examined all 9 over-segmentation
  FP and found the exact detector-episodes-vs-CEO-labels granularity ratios (MB3-015 8-vs-2, MB3-021 7-vs-1,
  MB3-024 6-vs-2) — stronger motivating evidence for the episode-identity mechanism than VE had; (2) Red Team
  checked the GT-length/window-length confound VE had disclosed as unchecked (corr=0.40, real) and found it
  REINFORCES rather than undermines `MORE_TIME_TO_FIRE` — incorporated into the confirmation-budget section
  with a new falsifiable acceptance test (confirmation timing must depend on accumulated evidence, not on
  window length, for two scenarios sharing an identical underlying path at different lengths). **Two genuine
  implementation ambiguities found in VE's own re-review and resolved (not new research — mandate's own
  §5/§3-amendment-trigger discipline)**: (a) the `WEAKENING` state's two entry paths (excursion-based vs.
  trailing-window-degradation-based) now have a fully deterministic priority/interaction rule (excursion
  takes priority for labeling; recovery requires BOTH triggers clear; termination fires on EITHER bound first)
  plus a new, fully-specified (though `UNRESOLVED_PARAMETER`-valued) `WEAKENING_MAX_BARS` counter; (b)
  episode-identity's continuation/merge/replacement now has an explicit priority order (MERGE against live
  structures first, then CONTINUATION against terminated/weakening priors, REPLACEMENT forced after any
  accepted breakout regardless of zone overlap). Full exact state-transition table (10 rows, every column
  mandate §5 asked for) now complete and implementable without re-deriving research. Parameter registry
  reformatted to the exact required columns — still zero MB3-fished values, every constant either
  scale-invariant/self-referential-derived or explicit `UNRESOLVED_PARAMETER`. Known-risk register confirms
  both previously-disclosed open risks (slow-drift-equilibrium false-reject; zigzag false-accept) have
  explicit fail-closed handling + a named test and do NOT block freeze, per the mandate's own stated standard.
  Implementation-fingerprint PROCEDURE specified (sha256 of finalized source, reusing the exact F1-only-
  remediation pattern) — no placeholder value generated. Full package
  `ve_n1_replay/VE_RANGE_V4_4_CONVERGENCE_AND_REVIEW_PACKAGE.md` (extends, does not replace, the original
  design doc). Per mandate: this verdict authorizes ONLY the next sequence step (independent Red Team focused
  design audit) — NOT implementation, NOT freeze, NOT threshold selection. Next owner: Red Team (focused
  design audit), then CEO (freeze decision).
- **VE-RANGE-V4_4-DESIGN-001 — RANGE V4.4 design & pre-registration (DESIGN ONLY, NO IMPLEMENTATION, NO
  PARAMETER FISHING, ZERO_VALIDATION_WEIGHT on MB3-001..024, MB3-025..048 never accessed at all this
  mandate)**, run in parallel with the (not-yet-delivered) Red Team audit of `VE-RANGE-DIAG-001`. Addresses
  every defect (D1-D7) from that diagnostic with a coherent NEW state machine, not a patch stack. **Core
  mechanism**: MACRO confirmation gains a 4-signal discrimination gate, computed over a BOUNDED TRAILING
  window (not the falsified whole-life `normalized_drift`) — Kaufman Efficiency Ratio (`ER≤0.5`, self-
  normalized, no ATR dependency), traversal count (`≥1` floor, exact minimum UNRESOLVED), Relative Net
  Displacement (`RND≤1.0`, structure's own width as the unit — the strongest-derived anchor, near-tautological),
  alternation rate (SUPPORTING only, deliberately non-gating — self-falsification found a real false-reject
  risk if made a hard gate). New 5-state lifecycle `CANDIDATE→FORMING→CONFIRMED→WEAKENING→TERMINATED` — the
  `WEAKENING` state is genuinely new (reuses the UNCHANGED `Excursion`/sweep machinery for path (a); adds
  trailing-window degradation detection for path (b)) and is what stops a confirmed RANGE from persisting
  after the market resumes trending (D5, previously unaddressed by any V4.3 mechanism). New episode-identity
  rules (continuation/merge/replacement via the SAME IoU construct the ratified scorer already uses) directly
  target the 9-structure over-segmentation class (D6) empirically observed in MB3-021 (4 sequential episodes)
  and MB3-024 (5). Explicit `RANGE_CANDIDATE_PRESENT` non-authoritative event distinguishes "RANGE PRESENT"
  from "RANGE FIRST CONFIRMED NOW," giving truncated episodes an honest explained-non-confirmation output
  instead of a silent miss (addresses D7's window-truncation FN class). **11 new reason codes**, all 29
  existing ones + all existing mechanisms (`degeneracy_check`/`n_touch`/`Cluster`/promotion/nesting/INTERNAL
  logic/snapshot pattern/ATR provenance) explicitly PRESERVED via a full KEEP/CHANGE matrix — nothing changed
  without a stated reason. Every numeric parameter either derived from a scale-invariant/self-referential
  argument (ER_max/RND_max/ALT_MIN) or explicitly marked `UNRESOLVED_PARAMETER` (trailing-window length `W`,
  min-traversal count, weakening-persistence bound, episode-continuation IoU/gap thresholds) — **zero
  threshold chosen by testing values against MB3 and picking a winner** (mandate's forbidden-list respected).
  **20 adversarial scenarios specified** with expected state chronology (mandatory per mandate §15), directly
  covering the diagnosed failure classes (channel/trend-fits-between-boundaries, sweep-without-termination,
  internal-rotations-fragmenting-one-episode, truncated/right-censored windows). **Mandatory self-
  falsification performed and HONEST**: found a real, undissolved false-reject risk (slow drifting-equilibrium
  range could still exceed RND at any window length) and a real, explicitly-out-of-scope false-accept risk
  (a violent zero-net-displacement "zigzag" could pass all four gates while not being a clean tradeable range
  to a human) — neither hidden nor hand-waved away. Full failure-mode closure table covers every D1-D7 defect
  with mechanism/evidence/response/benefit/risk/adversarial-test/regression-test columns. **Red Team
  convergence (mandate §22) explicitly NOT performable** — verified (not assumed) that no
  `RT-RANGE-DIAG-AUDIT-001` exists yet on any of the 4 mirrors as of delivery — so the mandatory convergence
  table is structurally empty and the formal verdict is **`V4_4_DESIGN_NOT_READY`** (gate-blocked, not
  defect-blocked: the design itself survived its own falsification pass). Full report
  `ve_n1_replay/VE_RANGE_V4_4_DESIGN_AND_PREREGISTRATION.md`. No code/config/threshold/V4.3 file touched (only
  the frozen V4.3 source was READ, for the preservation matrix). Next owner: CEO (schedule the convergence
  step once Red Team's audit of the diagnostic lands), then Red Team (design review, independent of timing).
- **VE-RANGE-DIAG-001 — RANGE V4.3 MACRO discrimination diagnostic (DIAGNOSTIC ONLY, ZERO_VALIDATION_WEIGHT,
  NO code/threshold/config changed)**, on the `bc6b9dc` build (RT-RANGE-0013 PASS) against the CEO-assisted
  blind batch `MB3-001..024` (RT-RANGE-MB3-001, `3496b73`/E89: `MB3_MACRO_GENERALIZATION_NOT_SUPPORTED` —
  recall ~stable 0.684 vs RT-0010 0.705, but precision/F1/IoU degraded and detector doesn't discriminate
  RANGE from CHANNEL/TREND). **Principal defect found (code-traced, not guessed): MACRO confirmation
  (`evaluate_candidate`/`degeneracy_check`) has NO directional-displacement gate** — only width/duration/
  touch-count. The needed signal (`Structure.normalized_drift`/`ConfigV43.s_max`) already exists but per its
  own code comment (line ~1041) was deliberately scoped to INTERNAL-only, as a non-blocking descriptive label
  (`INT_CHANNEL_UP`/`DOWN`), never extended to MACRO. **39/39 FP decomposed** (independently re-derived,
  resolving a provenance discrepancy vs the committed report's "FP 36" — traced to a naive vs dedup-aware
  count, `39` matches this mandate's own CEO citation exactly): 30 directional (14 CHANNEL_UP/8 CHANNEL_DOWN/
  4 TREND_DOWN/3 TREND_UP/1 TRANSITION) + 9 over-segmentation-on-genuine-RANGE (distinct, less-characterized
  mechanism — multiple sequential range→breakout episodes vs coarser CEO labeling granularity, NOT simple
  duplicate detection). **12/12 FN decomposed**: 4 window-truncation (mechanical), 5 touch-count-insufficient,
  3 zones-degenerate-killed, **0 boundary/IoU-quality failures** — recall loss is 100% about confirmation
  timing, never confirmed-but-inaccurate geometry. **Length effect (96≪480) quantified as "more time to fire,
  not better recognition"**: `d_macro=29` warm-up consumes 30% of a 96-bar window's budget vs 6% of 480-bar;
  matched-structure median confirm-delay at L=480 (77.5 bars) alone EXCEEDS L=96's entire eligible-bar budget
  (67 bars); all window-truncation FN occur at L=96/288, zero at L=480. **MB3-007/020 (CEO-declared NO MACRO
  RANGE) traced bar-by-bar**: both show the SAME mechanism directly — persistent directional drift
  (`slope_at_confirm` clearly signed) satisfying width+duration+touch gates with zero drift check;
  MB3-020 additionally shows the detector's OWN post-hoc role machinery (`TREND_CONTINUATION_CONFIRMED`)
  correctly recognizing 2 of its 3 false positives as trend — AFTER already confirming them as RANGE.
  **Mandatory falsification (§13) applied and the naive fix FAILS it**: `normalized_drift>s_max=1.60` as a
  hypothetical MACRO gate would reject 63.3% of directional FPs but ALSO 56.5% of genuine matched true
  positives — comparable collateral damage to benefit, NOT a clean drop-in fix; duration-confound hypothesis
  for the weak separation explicitly tested and REFUTED (correlation ≈0, not what caused the overlap).
  Architecture conclusion: **`MULTIPLE_CORRECTIONS_REQUIRED`** (two distinct mechanisms at different
  evidentiary readiness — dominant/well-characterized directional gap vs secondary/under-characterized
  over-segmentation), not narrow, not architectural redesign. Candidate V4.4 hypothesis stated narrowly in
  the report, explicitly **NOT implemented** — no threshold selected, no parameter search performed (mandate
  §10 respected: diagnostic-only sweeps shown, no winner declared). Cross-validated own instrumentation via
  0-mismatch bar-by-bar replay of the frozen detector against `predictions.json` before trusting any of the
  above. `MB3-025→048` never touched (selection metadata's bare 48 IDs were incidentally visible during
  reconnaissance but never processed beyond confirming the 24-window split). Full report
  `ve_n1_replay/VE_RANGE_DIAG_001_MACRO_DISCRIMINATION_DIAGNOSTIC.md`. `self_declared_pass=false`. Next
  owner: CEO (decision on recommended follow-up mandate), then Red Team (11 audit points listed in report).
- **RANGE HIERARCHICAL V4.3 — mandat "F1-ONLY REMEDIATION AFTER RT-RANGE-0012" (a cincea trecere)** —
  `RANGE_V4_F1_ONLY_REMEDIATION_READY_FOR_RED_TEAM_AUDIT`, `self_declared_pass=false`. Răspuns direct la
  **RT-RANGE-0012 = RANGE_V4_F1_F5_IMPLEMENTATION_AUDIT_FAIL** (`892355f`/E87, audit pe `69af414`): F1
  fost validat COMPLET PASS (inclusiv `F1_ONLY_PATCHED_CLI_PREDICTIONS_MATCH_FREEZE=TRUE`, 48/48, hash
  `62273c1e…` — poarta pe care VE o raportase `NOT_VERIFIABLE_HERE` în mandatul anterior, acum stabilită
  direct de Red Team cu acces la escrow), dar **F5 (corect ca UNITĂȚI) a produs o SCURGERE MATERIALĂ în
  MACRO pe bare reale** — contorul de structure-id partajat MACRO/INTERNAL + promovarea INTERNAL→MACRO +
  starea pending-swing partajată au propagat suprimările F5 din INTERNAL până în MACRO, mutând baseline-ul
  înghețat 62/88 (recall 0,705) → 58/88 (0,659) pe 12/48 ferestre reale — deși F5 era izolat de MACRO ca
  LOCAȚIE de cod, nu ca EFECT. Testul de identitate MACRO al VE (`atr=1,0` exclusiv) declarat **VACUU**:
  la `atr=1,0`, `tol_cluster×atr_ref=tol_cluster` — F5 devenea no-op exact în punctul testat. CEO a ales
  remedierea (b): **F1 SINGUR, F5 amânat complet** (`DEFERRED_RESEARCH_ONLY_NON_BLOCKING`, INTERNAL
  rămâne `RESEARCH_ONLY`/`NON_BLOCKING`). Livrat ca commit NOU (nu amendament la `69af414`, care rămâne
  istoric neatins): linia gardului de re-testare (`range_semantic_v4_3.py`) revertată CARACTER-CU-CARACTER
  la forma exactă `82f27c0` (verificat prin `git diff 82f27c0` — linia executabilă nu apare deloc în
  diff). Infrastructura de fingerprint NU revertată orb (interzis explicit de mandat — un revert complet
  la bytes-ul `f224e7d` ar fi lăsat restaurabil silențios un snapshot din pachetul RESPINS F1+F5, din
  moment ce `contract_version`+`config_id` nu s-au schimbat niciodată în nicio variantă) — valoare nouă
  `f1-only-f5-deferred-2026-08-20`, matrice completă de refuz fail-closed testată (F1-only acceptat;
  bare-`f224e7d` fără câmp respins; `69af414` RESPINS respins; config/contract mismatch respins; restore
  atomic). `FROZEN_PROTOTYPE_COMMIT="f224e7d+F1"`, hash nou `098fa144…41fbc` (fișier NU byte-identic cu
  `f224e7d` — infrastructura de identitate rămâne — dar byte-COMPORTAMENTAL identic, dovedit prin diff
  complet: singurele diferențe sunt constanta de fingerprint + 2 linii aditive de snapshot, NICIUNA
  executată în `observe()`). `construction_reproduction/` (Componenta A) verificat REFUZĂ live acest hash
  nou — pin-ul ține indiferent de câte remedieri urmează. **Dovadă MACRO ne-vacuă** (răspuns direct la
  vacuitatea găsită): gardul exercitat direct + proiecția MACRO pe 48 ferestre sintetice, sweep la 5
  valori ATR distincte (0,65/1,0/1,85/3,2/10,0, nu doar 1,0) — ancora la atr=1,0 coincide exact cu cea din
  mandatul F1+F5 (dovadă că acel punct nu poate distinge F5-prezent de F5-absent), celelalte 4 sunt
  dovadă nouă. **Poarta MACRO pe bare reale/ATR real rămâne `NOT_VERIFIABLE_HERE`** — verificat explicit
  că VE tot nu are acces escrow (un director cu formă de escrow există local, DELIBERAT necitit — rolul
  VE e structural definit să nu-l consume, indiferent de accesibilitatea la nivel de SO); script
  determinist nou (`verify_macro_identity_vs_baseline.py`) livrat pt. ca Red Team să reproducă automat
  tabelul lor §1 pe bare reale. **469/469 teste live PASS** (394 `tests/` + 75 `blind_runner/tests/`; 24
  teste noi înlocuiesc cele 19 șterse din suita F5), mypy `--strict` clean pe 7 fișiere de producție
  atinse. `tests/test_range_semantic_v4_3.py` neatins. `MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED
  = FALSE` — doar Red Team eliberează acest gate. Detaliu complet în
  `ve_n1_replay/RANGE_V4_F1_ONLY_REMEDIATION_DELIVERY_REPORT.md`. Niciun wheel, nicio bară SEALED/OOS
  accesată, niciun parametru RANGE recalibrat. Următorul proprietar: Red Team.
- **RANGE HIERARCHICAL V4.3 — mandat "F1 + F5 CONFORMANCE IMPLEMENTATION" (a patra trecere) — RESPINS
  de Red Team (RT-RANGE-0012, F5-MACRO-LEAK) — vezi intrarea de mai sus pt. remediere** —
  `RANGE_V4_F1_F5_IMPLEMENTATION_READY_FOR_RED_TEAM_AUDIT`, `self_declared_pass=false`. Autorizat
  EXCLUSIV de RT-RANGE-0011 (`8d71fce`) pt. DOUĂ corecții: **F1** (contract toleranță sub-tick OHLC,
  DOAR în `blind_runner/schemas.py` — `epsilon=min_tick/2=0,005` pt. XAUUSD, comparație
  valoare-vs-frontieră-deplasată nu formă-diferență, OHLC niciodată modificat, eveniment de calitate
  `INPUT_OHLC_SUBTICK_TOLERATED` explicit ÎN AFARA celor 29 reason codes, caracterizarea 13/13.824
  bare tolerabile reprodusă exact 9-high/4-low/close-only) + **F5** (fix de unități `tol_cluster` —
  era comparat ca distanță USD, corect e multiplicator ATR adimensional `× atr_ref`; defect găsit
  independent de Statistician `870d3f8` ȘI Red Team `8d71fce` chiar în gardul anti-retest introdus de
  VE într-un mandat anterior, `range_semantic_v4_3.py` linia 745, cale INTERNAL/forming-only STRICT —
  MACRO nu atinge niciodată acest cod). Fingerprint nou de implementare
  (`f1-f5-conformance-2026-08-20`) adăugat în snapshot/restore — refuză fail-closed orice snapshot
  pre-F5 chiar dacă `config_id` se potrivește (`config_id` NESCHIMBAT — nicio valoare de configurație
  s-a modificat). **`MACRO_V4_3_BYTE_IDENTITY_AFTER_F5 = TRUE`**, dovedit printr-un test NOU COMIS
  (nu doar script ad-hoc) care hash-uiește proiecția MACRO completă peste toate cele 48 ferestre —
  ancoră `81b0a7b3336d…c942591`, 973 evenimente MACRO, determinist. INTERNAL confirmat 16→9 (efect
  real, direcție așteptată, NU calibrare — decis strict pe conformanță, nu pe recall, per mandat §6).
  `construction_reproduction/` rămâne pinnat la `f224e7d` original și REFUZĂ fail-closed să ruleze
  contra detectorului curent — verificat prin rulare directă, dovadă vie a separării A/B. **Poarta
  `F1_PATCHED_CLI_PREDICTIONS_MATCH_FREEZE` (mandat §5, predicții CLI patch-uite = `46a9576` byte-exact)
  NU declarată TRUE** — VE nu are acces la escrow-ul cu bare reale (prin proiecție, la fel ca Red
  Team/Statistician), urmează exact precedentul propriului test-skip al Statisticianului
  (`test_21_cele_13_bare_reale...`, condiționat de `ESCROW_DIR`); raportat onest ca
  `NOT_VERIFIABLE_HERE`, nu fabricat. **464/464 teste live PASS** (389 `tests/` + 75
  `blind_runner/tests/`, din care 45 noi: 26 F1 + 19 F5), mypy `--strict` clean pe toate fișierele de
  producție atinse. `tests/test_range_semantic_v4_3.py` și `construction_reproduction/` NEATINSE
  (verificat `git status`/`git diff` gol). Cele 48 ferestre folosite STRICT pt.
  reproducere/regresie/diagnostic — `INDEPENDENT_SEMANTIC_BLIND=FALSE`, `VALIDATION_WEIGHT=ZERO`.
  Niciun F4/INTERNAL semantic schimbat — status rămâne `RESEARCH_ONLY_NOT_VALIDATED`. Detaliu complet
  în `ve_n1_replay/RANGE_V4_3_F1_F5_CONFORMANCE_DELIVERY_REPORT.md`. Niciun wheel, nicio bară
  SEALED/OOS/escrow accesată. Următorul proprietar: Red Team (audit F1+F5, apoi decizie asupra porții
  `46a9576` cu acces la escrow).
- **RANGE HIERARCHICAL V4.3 — mandat "PACHET REPRODUCTIBIL DE RULARE" (a treia trecere; detectorul rămâne `f224e7d`, byte-neatins — verificat `git diff --stat f224e7d` gol pe toate fișierele lui)** — `RANGE_V4_3_REPRODUCIBLE_RUNNER_READY_FOR_RED_TEAM_REVIEW`, `self_declared_pass=false`. Răspuns direct la Red Team RT-RANGE-0007 (`b7c6fa8`): verdict A `RANGE_V4_3_PROTOTYPE_IMPLEMENTATION_PASS` (confirmat independent), verdict B `RANGE_V4_3_CONSTRUCTION_RESULT_NOT_REPRODUCED` (`synth.py`/`run_construction.py`/`construction_run_results.json` trăiau necomise) + finding freeze-fail (rularea a precedat commit-ul la `f224e7d`). **Componenta A** (`construction_reproduction/`, marcată `CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY`/`CIRCULAR_LABEL_DERIVED_BARS`/`ZERO_VALIDATION_WEIGHT`): reproduce EXACT cele 12 cifre citate de mandat (MACRO 57/88, INTERNAL 2/12, sweep 209/breakout 112/reversal 21/promo 94, funnel 725→151/16/558) — `HISTORICAL_SYNTHETIC_RESULT_REPRODUCED`. Etichetele comise ca fixture-uri byte-exacte cu provenance per-commit-sursă (`fixtures/FIXTURE_PROVENANCE.md`), nu mai citite cross-branch la rulare. **Componenta B** (`blind_runner/`, complet separată de A): runner inference/scoring pt. bare reale sigilate, cu separare STRUCTURALĂ verificată prin `ast` (nu convenție) — inference nu importă etichete/scoring, scoring nu importă detectorul, niciun fișier din pachet nu importă simultan ambele. Predicții sigilate (`predictions.json`+`.manifest.json`+`.sha256`, read-only, scorer refuză fail-closed orice hash nepotrivit — un singur bit modificat blochează scorarea). 2 defecte reale găsite+corectate în timpul construcției runnerului (nu în detector): o structură confirmată dar încă deschisă la finalul ferestrei lipsea din output-ul de structuri (doar istoricul ÎNCHIS era citit); scorer-ul dădea IoU=0 garantat pt. orice astfel de structură (fallback greșit pe span de lungime zero). **426/426 teste** (370 anterioare + 7 componenta A + 49 componenta B, toate cele 24 iteme din mandat §11 acoperite explicit), mypy `--strict` clean pe schemas/inference/scoring. Îngheț în ordinea CORECTĂ de data asta: fingerprint-uri calculate ÎNAINTE de commit (spre deosebire de `f224e7d`) — `RANGE_V4_3_RUNNER_PRE_BLIND_FROZEN`. Detaliu complet în `ve_n1_replay/RANGE_V4_3_REPRODUCIBLE_RUNNER_DELIVERY_REPORT.md`. Niciun wheel, nicio bară reală/SEALED/OOS accesată sau comisă. Următorul proprietar: Red Team (audit runner, apoi rulare blind independentă).
- **RANGE HIERARCHICAL V4.3 — mandat "CONSTRUIRE PROTOTIP REAL" (a doua trecere peste bulletul de mai jos, același `config_id`/`contract_version`, neschimbate)** — `RANGE_V4_3_PROTOTYPE_RESULTS_READY_FOR_CEO_REVIEW`, `self_declared_pass=false`. Verificare §1 completă pt. cele 3 surse noi citate (`5a9d5ec`/`4684e66`/`b8cf2a7` — toate strămoși direcți ai `d6e599e`, deja incluse). Găsit+corectat un defect real ÎNAINTE de îngheț: `sweep_reversal_confirmed` (C13) era portat fidel și testat DIRECT, dar NICIODATĂ apelat din bucla per-bară a producătorului — `LIQUIDITY_SWEEP_REVERSAL` nu putea fi emis prin observare reală, doar prin apel manual al funcției pure. Fix aditiv: "reversal watch" nou (`_macro_reversal_watch`/`_internal_reversal_watch`), populat la `SWEEP_CONFIRMED`, verificat dinamic în fiecare bară ulterioară, persistat în snapshot. Verificat end-to-end pe fixture-ul HBL-20 deja validat (bara 75) + re-rulare corpus: 21 emiteri (0 înainte). mypy `--strict` clean, **370/370 teste** (368 anterior + 2 noi: test AST/structural de reachability a celor 29 reason codes prin `ast.walk` + test dedicat reversal-via-`observe()`), 0 regresii. Descompunerea exactă a celor 79 teste harness re-verificată prin execuție instrumentată (nu listă hardcodată): 39 cazuri adversariale (itemele 1-16) + 27 grupe suplimentare (itemele 17-20, C13/C14/C15-17/acoperire) + 13 porți de nevacuitate = 79/79 PASS. Rulare de construcție extinsă (metrici noi, cod/config NESCHIMBATE — extractie pură, nu re-tuning): IoU percentile (MACRO mediană 0,770, mult peste medie 0,641 — media era trasă în jos de câteva potriviri slabe), confirm_ts delay (mediană MACRO = exact `d_macro=29`), funnel complet formare candidați (725 încercări, 23% succes), distribuție completă a stărilor, toate cele 6 exemple explicit cerute verificate cu dovezi concrete din corpus (channel intern `BLIND-034`, sweep+reversal, HBL-20 accumulation, breakout→nou-range `BLIND-001`, INTERNAL-nu-distruge-MACRO în 8 ferestre). Recall/precision/IoU pe segmente NESCHIMBATE de fix (adaugă doar un eveniment nou). Corectat conversațional (nu în fișiere livrate — verificat, nicio cifră greșită era comisă): totalul de bare al corpusului e 13.824, nu 13.536. Detaliu complet în `ve_n1_replay/RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md`. Niciun wheel, `release/`/`SHA256SUMS` neatinse, 0.4.1 verificat din nou byte-neatins. Următorul proprietar: Red Team.
- **RANGE HIERARCHICAL V4.3 PROTOTYPE** — `RANGE_V4_3_PROTOTYPE_RESULTS_READY_FOR_CEO_REVIEW`. Autorizat EXCLUSIV de Red Team `RANGE_V4_IMPLEMENTATION_PACKAGE_STATIC_PASS` (RT-RANGE-0006 @`2c113ef`, E81) peste pachetul Statistician `d6e599e` (contract normativ unic `range-hierarchical-v4.3`; V4.2/harness cu filename vechi rămân DOAR surse istorice/oracol). Fișiere NOI, aditive, izolate — `range_semantic_v4_3.py`/`range_engine_v4_3.py` (`RangeSemanticProducerV43`/`RangeSemanticEngineV43`, orchestrare per-bară pe baza celor 13 porți de nevacuitate + funcțiilor pure ale harness-ului, portate fidel) + `tests/test_range_semantic_v4_3.py` (48 teste, acoperă toate cele 25 iteme §12 + 79 asertări-oracol + 29 reason codes reachability dinamică + 13 porți). **`ve_n1_replay 0.4.1` rămâne BYTE-NEATINS** (`__init__.py`/`version.py` modificate STRICT aditiv — 51 inserții, 0 ștergeri, verificat `git diff`; `__version__` rămâne `"0.4.1"`). `ConfigV43` reproduce exact `config_id` normativ `24f72a60…3826da` (CEO-fixat: d_macro=29/d_internal=12/n_touch=2/K_reentry=22/N_accept=3/K_struct=2/n_external_swings=2/w_atr=0,80; tol_cluster=s_max=1,60 derivate; plafon sanity 1,3952). 6 defecte reale găsite+corectate prin testare empirică pe fixture-uri (nu doar code review): reutilizare de swing-uri MACRO de către candidați INTERNAL; clasificare CHANNEL/SUBRANGE niciodată conectată la bucla per-bară; excursie/breach declanșate ÎNAINTE de confirmare (contra §6); promovare cu declanșare dublă; resetarea ferestrei de promovare la momentul GREȘIT (formare, nu confirmare); pairing de candidați "pending" cu swing-uri VECHI, nerelaționate (inclusiv un caz secundar — re-testarea unei frontiere MACRO ÎNGHEȚATE putea încă ancora un candidat INTERNAL nou). **48/48 teste + suita completă 368/368** (320 baseline 0.4.1 neschimbate + 48 noi), mypy `--strict` clean pe producție ȘI teste. **Faza 4 (construction-only, NU BLIND PASS — comparația reală rămâne mandat Red Team separat pe bare escrow-ate, verificat direct din 3 surse independente că VE nu are acces la ele)**: prototipul rulat O SINGURĂ DATĂ pe cele 48 ferestre `BLIND-001…048` sintetizate MECANIC din etichetele deja publicate (`BLIND_BATCH_02_LEVEL_MAPPING.md` + `PART1-4_LABELS.json` + addendum 046-048) — recall MACRO 0,648/precision 0,445/IoU 0,641 (88 GT); INTERNAL 0,167/0,111/0,249 (12 GT, limitat de metodologia de sintetizare pe 2 straturi, NU de prototip); 26 UNRESOLVED raportate separat, niciodată scorate. Detaliu complet în `ve_n1_replay/RANGE_V4_3_CONSTRUCTION_REPORT.md`. **Faza 5 (performanță)**: 355.696 bare, două regimuri (realist + adversarial cu o singură structură niciodată închisă) — cost/bară PLAT în ambele (~35,7μs/~31,1μs, fără tendință de creștere), istoric mărginit confirmat empiric (`maxlen=64`), snapshot/restore la scară 0,25ms/2,0ms. Detaliu în `ve_n1_replay/RANGE_V4_3_PERFORMANCE_REPORT.md`. **Nu se autodeclară**: PASS semantic, PASS blind, wheel ready, Strategy Catalog/Alpha/AI Trader/LIVE_SHADOW/broker authorized. Niciun wheel construit, `release/`/`SHA256SUMS` neatinse. Proprietar următor: CEO, apoi Red Team.
- **`ve_n1_replay 0.4.1`** (PERFORMANCE DELTA FIX — pantă OLS incrementală O(1)/bară — READY_FOR_RANGE_V3_PERFORMANCE_DELTA_REVALIDATION). Remediază EXCLUSIV `§12` identificat de Red Team (`RT-RANGE-0004` @`87cad2c`, ledger E79, verdict `RANGE_V3_SEMANTIC_FAIL` pe 0.4.0 @`034b919`): restul semanticii V3 a trecut INDEPENDENT verificat — domeniu STRICT performanță. `RangeConfigV3` accepta `d_min_bars` NEMĂRGINIT; `_Segment.slope()` (0.4.0) re-parcurgea ÎNTREAGA coadă `closes` la fiecare bară — O(`d_min_bars`)/bară (Red Team: 20,1× cost pt. 20× `d_min_bars`, extrapolat ~8,9h la `d_min_bars=200000`). **0.4.0 rămâne BYTE-NEATINS** (git diff gol), păstrat audit/rollback. Fix — Varianta A: pantă OLS pe fereastră trailing prin statistici suficiente incrementale O(1)/bară (`Sx`/`Sxx` formă închisă, `Sy`/`Sxy` actualizate la fiecare bară — creștere/evict+append derivate algebric, verificate la fiecare prefix contra unui oracol pe 8 forme de secvență × 4 mărimi fereastră). **Niciun plafon arbitrar pt. `d_min_bars`** (spec `bf9f780` tăcută, mandatul interzice alegerea arbitrară). Fișiere NOI (`range_semantic_v3_1.py`/`range_engine_v3_1.py`, producător `range-producer-0.4.1`): `RangeConfigV31`/`_IncrementalSlope`/`_SegmentV31`/`RangeSemanticProducerV31`/`RangeSemanticEngineV31` (refuză fail-closed snapshot 0.2.0/0.3.0/0.3.1/**0.4.0**). **Amendament CEO** — hardening `d_min_bars` (găsit de VE prin auto-verificare, raportat ÎNAINTE de a fi cerut): `RangeConfigV3` nu validase NICIODATĂ `d_min_bars` — la `0`, 0.4.0 rămânea silențios, 0.4.1 (înainte de amendament) arunca `IndexError` necontractual; corectat cu `RangeConfigV31.__post_init__` (respinge non-`int`/`bool`/`<1` cu `RangeSemanticContractErrorV3`, aceeași excepție ca la K>N) — valoare invalidă nu mai poate produce NICIODATĂ o instanță de configurație, calea de crash devine structural inaccesibilă; cele două benchmark-uri în curs NU repornite (configurațiile lor rămân valide/neschimbate, verificat direct). Paritate decizională COMPLETĂ (`RANGE_V3_1_PARITY_REPORT.md`): 0/320 mismatch fixture oscilație, HBL-20 identic bară-cu-bară (sweep bara 56, breakout nu la/înainte de bara 63), prag exact `IS_CHANNEL` (sub/la/peste) identic Δ<1e-9, snapshot/restore identic înainte/după umplerea ferestrei. Benchmark canonic (355.696 bare, `d_min_bars=96` — cerut explicit, 4× mai greu decât `d_min_bars=24` al lui 0.4.0): 30min18s sub 4h (marjă ~7,9×), statistic indistinctibil de 0.4.0. Benchmark adversarial (`d_min_bars=200000`, 250.000 bare = 200k umplere+50k coadă): 21min13s, cost/bară STABIL (~2,7% diferență umplere/post-umplere — semnătura O(1)); izolat (doar pantă): 33.330× speedup măsurat direct. **320 teste total** (83 noi), mypy --strict clean, wheel instalat testat venv GOL izolat, rollback FUNCȚIONAL pe lanțul `0.4.1→0.4.0→0.3.1→0.1.1→0.4.1` (320/320→237/237→162/162→43/43→320/320, suita PROPRIE a fiecărei versiuni din commit-ul ei exact). `n_generated_total=363`/`m_inference=26`/tombstones/registrul Alpha/F1-F6/F7 NEATINSE; fără SEALED/OOS; `self_declared_pass=false`; Red Team primește EXCLUSIV 0.4.1.
- **`ve_n1_replay 0.4.0`** (RANGE SEMANTIC V3 — redesign LONGITUDINAL, segment-based — READY_FOR_RANGE_V3_SEMANTIC_REVALIDATION). Statistician a demonstrat (`STAT-RANGE-SEMANTIC-SPEC-V3-v1.0` @`bf9f780`, manifest v2.7.84 @`db098ed`, fingerprint `cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233` verificat exact) patru defecte STRUCTURALE în 0.3.1: ancoră pe `range_window=512` vs `d_min=96` (5,3× prea largă); `anchor_upper` putea inversa sub `anchor_lower` fără gardă; `bars_in_state` satura ~508 deci `TOO_SHORT` nu putea fi emis NICIODATĂ; o rupere acceptată ȘTERGEA episodul (76,65% din bare), fără segmentare longitudinală, sweep emis fără nicio stare care să-l consume. **0.3.1 rămâne BYTE-NEATINS** (git diff gol), păstrat audit/rollback. Fix: segmentare longitudinală reală (`predecessor_id`/`transition_reason` explicite, segment ÎNCHEIAT rămâne în `history`, D4 închis); ancoră segment-locală nemărginită pe durata segmentului, calculată printr-o mediană incrementală O(log m) (D1 închis structural — un re-sort complet pe bară ar fi fost O(n²) pe segmente lungi, verificat empiric și corectat înainte de livrare); `ZONES_DEGENERATE` structural imposibilă de reprezentat ca validă (D2); `TOO_SHORT` demonstrabil reachable la limita exactă `d_min-1`/`d_min`/`d_min+1` (D3). Breach detectat pe MEȘĂ (high/low), nu pe close — wick-sweep dintr-o singură bară reprezentabil; rezoluție (sweep/breakout/expirare) pe close, cursă K-vs-N pe același contor, invariant `K<=N` OBLIGATORIU (corectat față de un design intermediar `K>=N` care făcea K structural inaccesibil). `K`/`N`/`w_atr` NEIDENTIFICATE — cerute explicit, fără default ascuns (verificat via `inspect.signature`), construcția refuză fără `acknowledge_construction_only=True`. Toate cele 14 stări/evenimente din spec confirmate reachable. `HBL-20` reprodus NUMERIC EXACT (breach bara 52, sweep confirmat EXACT bara 56 — nu bara 52, markup bara 63) dintr-un fixture sintetic al verificării proprii a Statisticianului; diagnostic construction-only pe toate cele 24 ferestre (`RANGE_V3_HBL_DIAGNOSTIC.md`) — 0/22 sintetizate cu istoric complet gol (vs. majoritatea la 0.3.1). **75 teste noi, 237 total**, mypy --strict clean, wheel instalat testat într-un venv GOL izolat, rollback FUNCȚIONAL 0.4.0→0.3.1→0.1.1→0.4.0 verificat (suita proprie a fiecărei versiuni, nu doar metadata). Benchmark COMPLET 355.696 bare rulat (arhitectură material schimbată, nu doar pin de configurație) — vezi `ve_n1_replay/RANGE_V3_BENCHMARK.md`. `n_generated_total=363`/`m_inference=26`/tombstones/registrul Alpha/F1-F6/F7 NEATINSE; fără SEALED/OOS; `self_declared_pass=false`; Red Team primește EXCLUSIV 0.4.0.
- Handoff `21ae632` (AI Trader, `ai_trader/n1_replay/`, ve_brain 0.1.3, detector `dc28e4a`). Closure git-only in `N1_REPLAY_CLOSURE.md`: 14 ai_trader.* runtime + 5 detectors @ submodule `61cbd58c` (`market_structure` blob `52bb1eba…` ≠ ve_tower) + ve_brain external + numpy.
- Packaged as **`ve_n1_replay 0.1.0`** — standalone, isolated namespace, vendored byte-identical (ai @21ae632 / detectors @61cbd58c), transactional bootstrap fail-closed on foreign collision, surface preserved (N1ReplayEngine: initialize/observe_closed_bar/replay/snapshot/restore/reset). **A/B parity source@21ae632 vs installed wheel = identical** (TREND_UP/UNCERTAIN/BOS_BULL). 18 tests, mypy clean, empty-venv verified. No ai_trader/ve_tower/MT5/broker at runtime; LIVE_SHADOW untouched. Awaiting Red Team; Alpha stays ALPHA_BLOCKED_CANONICAL_N1_HANDOFF (355 hypotheses NOT run).
- **`ve_n1_replay 0.3.1`** (PIN de configurație V2 — READY_FOR_RANGE_V2_BLIND_REVALIDATION). Modificare CHIRURGICALĂ peste 0.3.0: Statistician a rulat protocolul pre-înregistrat (`STAT-RANGE-V2-PREREG-PROTOCOL-v1.0` @`4e69e22`, comis ÎNAINTE de orice atingere a datelor — dovadă de precedență) și a fixat `w_atr=0,30` (`STAT-RANGE-V2-WATR-FINAL-v1.0` @`c29ac98`, manifest v2.7.81 @`2611d22`, fingerprint `432170ff5b6d0d20e125ea318d0293053f10ff0da8df9948bb470dde6d6501f6` verificat exact), înlocuind implicitul NERATIFICAT `0,25` al 0.3.0; `s_max` NU mai e parametru liber — DERIVAT structural `2×w_atr=0,60`. Control de construcție `RC-CONSTRUCTION-CHANNEL-NEW-01` (S=3,3781 CHANNEL_UP, prag DERIVAT nu ales — insensibil la valoarea finală a lui `w_atr`). **0.3.0 rămâne BYTE-NEATINS** (git diff gol), păstrat audit. `RangeConfigV2Pinned` (`range_state_v2_1.py`, nou): `s_max`/`derived_s_max` sunt `@property` calculate, NU câmp stocat — constructorul REFUZĂ `s_max` structural (`TypeError`, parametrul nu există), `from_dict()` (parserul) refuză explicit un `s_max` extern (`LegacyConfigRejectedError`, cod nou UNIC `LEGACY_S_MAX_REJECTED`). Gard AST verifică `0,15` absent ca literal de producție. `RangeStateReplayEngineV2Pinned` (`range_engine_v2_1.py`, nou) REUTILIZEAZĂ `RangeStateProducerV2` (0.3.0) + `N1IncrementalReplayEngine` (0.1.1) NESCHIMBATE, importate — `_to_runtime_config()` traduce configurația pin-uită, dovedit structural (`isinstance`), nu doar comportamental. Snapshot nou (`range-state-snapshot-v2-pinned`) — refuză fail-closed orice snapshot 0.2.0 SAU 0.3.0, incl. `s_max=0,15` legacy explicit testat. **40 teste noi** (22 cazuri mandat + 2 gard-uri AST + regresie structurală), **162 teste total**, mypy --strict clean, empty-venv + rollback 0.3.1→0.3.0→0.1.1 verificate. Benchmark comparativ SCURT (nu 355.696 complet — mandat explicit waivat pt. delta de configurație): 0.3.1 statistic indistinctibil de 0.3.0 (ratio 0,98, n_guards identic 2365=2365). Docs: `RANGE_STATE_V2_1_BENCHMARK.md`. `n_generated_total=363`/`m_inference=26`/tombstones/registrul Alpha/F1-F6/44 `BLOCKED_PENDING_RANGE_SEMANTIC_FIX`/F7 `SAFETY_GUARD` NEATINSE. Fără SEALED/OOS, fără RC-07/RC-08, fără `range1.pdf`/`range2.pdf`. Red Team primește EXCLUSIV 0.3.1 (Statistician: 0.3.0 NU autorizat pt. Red Team).
- **`ve_n1_replay 0.3.0`** (RANGE_STATE SEMANTIC SPEC V2 — READY_FOR_RANGE_SEMANTIC_REVALIDATION). Remediates `SEMANTIC_SPEC_DEFECT` ruled against 0.2.0 by Statistician (`STAT-RANGE-SEMANTIC-DIAGNOSIS-V2-v1.0` @`3aac2cc`, manifest v2.7.78 @`18aa2a1`): 0.2.0's max-anchor boundary was a maximum over a growing set → reaching the required duration forced the window to grow → growing it raised the boundary → raising the boundary retroactively invalidated touches counted against the old, lower boundary — an unsatisfiable definition, not an implementation bug (RT passed 0.2.0; Alpha reproduced zero-occupancy identically twice). **New contract, not a patch — 0.2.0 files (`range_state.py`, `range_engine.py`) are byte-untouched** (verified: empty git diff), kept for audit. Fix: `anchor` = MEDIAN of confirmed swing extremes on a bounded window (not monotone, cannot self-invalidate); `boundary_zone=[anchor-w, anchor+w]` (zone not line); `touch` = any bar whose interval intersects the zone as it existed at that bar, accumulated as a monotone counter, never re-scanned retroactively — **proven directly against 0.2.0 on the identical adversarial fixture**: 0.2.0 loses `CONFIRMED` (touches 8→1), 0.3.0 preserves it. Internal BOS/CHoCH is a non-invalidating descriptor (`structure_events_inside`, reuses `IncrementalRawAxesBuilder` internally, isolated instance). Range/channel separation via `|slope|×d_min <= s_max×ATR` (literal spec formula — `d_min` the fixed constant, not episode length, a bug caught and fixed during delivery) with slope computed over a bounded trailing `d_min_bars` window. Two duration classes (`intraday` d_min=24, `multiday` d_min=96). 11 longitudinal events (`range-events-v2`): RANGE_FORMING/ESTABLISHED/HIGH/LOW/MID, BREAKOUT_CANDIDATE, BREAKOUT_ACCEPTED_LONG/SHORT, BREAKOUT_RETEST, BREAKOUT_FAILED, LIQUIDITY_SWEEP — ACCEPTED_LONG/SHORT/FAILED mutually exclusive by machine construction, zero same-bar collisions verified. F7 `RANGE_MID_NO_ENTRY` SAFETY_GUARD unchanged in meaning. **N1 (0.1.1) byte-identical** throughout (engine untouched, verified). Nine contract versions published (range-state-v2/schema-v2/producer-0.3.0/events-v2/state-machine-v2/snapshot-v2/ledger-v2/reason-codes-v2 + pkg N1/router/axis versions unchanged from 0.2.0) + predecessor/N1-baseline identity citations; cross-version (0.2.0↔0.3.0) snapshot restore refused fail-closed both directions. **Disclosed ambiguity**: `w_atr`/`s_max` are "pre-registered" in the spec but carry no literal numeric value in the document or manifest (verified) — shipped as VE-proposed, Statistician-unratified configurable defaults; no real market data was loaded to calibrate them (forbidden by mandate) — empirical P1-P3 validation against the real corpus is Red Team's task on the BLIND subset (RC-06/07/08), which VE never accessed. 45 new tests (28 mandate items + direct 0.2.0-vs-0.3.0 regression demonstration + reachability + isolated classification-decision test), 122 total, mypy --strict clean, empty-venv + rollback 0.3.0→0.2.0→0.1.1 verified. Docs: `RANGE_STATE_V2_CONTRACT.md`, `RANGE_STATE_V2_BENCHMARK.md`. `RANGE_STATE_HANDOFF_PASS` NOT self-declared for V2 — Red Team blind semantic revalidation pending. `n_generated_total=363`/`m_inference=26`/tombstones/Alpha registry untouched; no SEALED/OOS access; Alpha NOT run; LIVE_SHADOW untouched.
- **`ve_n1_replay 0.2.0`** (RANGE_STATE + longitudinal breakout events — READY_FOR_RANGE_STATE_HANDOFF_REVALIDATION). Additive versioned producer implementing the final reconciled Statistician spec (STAT-RANGE-RECONCILED-SPEC-v1.0 @`aca7801`) + the `m_inference` FINAL amendment (STAT-M-INFERENCE-FINAL-v1.0 @`d0d08c1`, manifest v2.7.77, hash `aec8f07`), on RT reachability RT-RANGE-0001 @`5e56396`. **N1 output byte-identical to 0.1.1** (N1 engine untouched; `RangeStateReplayEngine` composes it). Does NOT reuse/reinterpret `StructBand.RANGE`, does NOT route through `applicable_regimes` (statically incapable of RANGE — RT proof), does NOT touch ve_brain/N3/N4/EV/N6. Seven package-declared contract-version bumps (range identity only; N1 per-bar identity unchanged). `range_state.py`: incremental RANGE_STATE producer (boundaries from ratified `detect_swings` strict-D2 stream, boundary_validity PROVISIONAL/CONFIRMED/EXTENDED/VIOLATED, data_readiness, consolidation_state FORMING/ESTABLISHED/DECAYING, structural_start vs actionable_start=confirm_ts≥structural+k, ER=|Δclose|/Σ|Δclose|, invalidation ACCEPTED_BREAK/MAX_DURATION/INPUT_UNAVAILABLE never retroactive, `range_spec_id`+`run_hash`, zero lookahead) + longitudinal event state-machine `range-events-v1` (8 events; BREAKOUT_ACCEPTED XOR FAILED_BREAKOUT mutually exclusive by construction → disjoint populations; SWEEP reuses D6). Precedence TREND_PAUSE ⊆ RANGE_STATE (`RANGE_STATE_OVER_TREND_PAUSE`, in range_spec_id; trend_context kept). **F7 RANGE_MID_NO_ENTRY = SAFETY_GUARD** (register SAFETY_GUARDS, counter n_guards, no p-value; executable refusal via `entry_decision`; audited, survives snapshot/restart). Bounded combined snapshot/restore (`range-state-snapshot-v1`). Range ledger (`range-state-ledger-v1`) with run_hash + occupancy matrix. 34 range tests (+ 18 N1 + 25 incremental = 77 total): N1 byte-identical, swing-stream byte-identical to detect_swings, all 8 events reachable, actionable-only-after-confirm_ts, warmup≠range, accepted XOR failed, retest, sweep, invalidation, zero-lookahead, chunk-invariance, snapshot/restart in every machine state, two-instance isolation, no MT5/broker/order_send/set_authority/probability_inputs. mypy --strict clean. Docs: `RANGE_STATE_CONTRACT.md`, `RANGE_STATE_BENCHMARK.md`. `RANGE_STATE_HANDOFF_PASS` NOT self-declared — Red Team verdict pending. Alpha registry/357/tombstones/verdicts unchanged; no SEALED access; LIVE_SHADOW untouched; Alpha NOT run.
- **`ve_n1_replay 0.1.1`** (performance remediation — READY_FOR_N1_INCREMENTAL_REVALIDATION). Fixes 0.1.0's O(n²) replay (full 355,696-bar run ~20+ days) with an INCREMENTAL engine whose per-bar result is **byte-identical** to 0.1.0. Dependency horizon derived from code (`N1_INCREMENTAL_HORIZON.md`): bounded axes (is_compressed≤460=COMPRESSION_WINDOW, is_displacement≤15, atr14=14) via a rolling 460-buffer feeding the UNMODIFIED expansion/compression; unbounded axes (structure/direction) via incremental swing/break state replaying the ratified detect_swings/label_structure/detect_breaks (NOT a sliding window, NOT truncation). New API: `IncrementalRawAxesBuilder`, `N1IncrementalReplayEngine`, `replay_batch` (canonical read-only ledger `n1-incremental-ledger-v1`, fail-closed `ledger_key`), bounded incremental snapshot/restore (`n1-incremental-snapshot-v1`, restore O(460) not O(n)). Wheel SHA-256 `2cff7e7be1f9401c10753f751a1189a512f5be39946dfada4260b9c5e1cd29ab` (68937 bytes), committed at `ve_n1_replay/release/`. 43 tests (18 + 25 incremental: result AND intermediate-state parity, adversarial old-swing 460/500/5000, chunk-invariance, snapshot-restart-between-swing-and-break, zero-lookahead, two-instance isolation, ledger-key invalidation, refusals), mypy --strict clean, empty-venv verified, rollback 0.1.1↔0.1.0 verified. Benchmark to 355,696 bars **under the 4h target**, ~O(n) scaling (`N1_INCREMENTAL_BENCHMARK.md`). evaluation_identity UNCHANGED (per-bar result = 0.1.0). ve_brain/N1/Router/EV/LIVE_SHADOW untouched; no SEALED-data access; Alpha NOT re-run. `N1_INCREMENTAL_PASS` NOT self-declared — Red Team verdict pending. Reports: `N1_INCREMENTAL_HORIZON.md`, `N1_INCREMENTAL_PARITY.md`, `N1_INCREMENTAL_LEDGER_SCHEMA.md`, `N1_INCREMENTAL_SNAPSHOT_SCHEMA.md`, `N1_INCREMENTAL_BENCHMARK.md`.

## N2 (MANDATE N2, verdict B — N2_EXISTS_BUT_IS_NOT_PACKAGED)
- N2 = `code/bias_h1.py` @`850815f` (build `81a0a62`, spec STAT-LEVEL2-BIAS-H1-SPEC-v1.0 @`1b2933c` + SPEC3 @`404b6c8`, manifest **v2.7.61**). Deterministic directional factors; `emits_probability=False`. Inventory + verdict in `N2_INVENTORY.md` @`a5241fb`.
- Packaged in **ve_tower 0.4.0** (`run_n2`). AI Trader stays HOLD at `54cf26e` until Red Team N2_HANDOFF_PASS. Hints `v2.7.51`/`RT-CODE-A-0011`/`B-L1` were NOT confirmed in git.

**Artifact delivery channel (process lesson):** wheels must be COMMITTED into the repo (`<pkg>/release/*.whl`, `*.whl binary` in `.gitattributes`) so AI Trader can reach the bytes on any remote — chat/file-send delivery is not reachable by AI Trader's process. Neither wheel was tracked in git before this; ve_tower now is.

## CORRECTIONS (found during Mandate A inventory)
- `zone_map` head is **`5888978`** (re-anchored), not `11ae360`.
- `zone_confirmation` head is **`7f2694f`** (W=3), not `ca683ff`.
- `ve_brain` could not build a wheel — **`project.urls` invalid**; fixed in `a1d2a6d`.

## FROZEN
- **CAND-T05**, EV_net **+0.389R** recent, trimmed **+0.202** — **HIGHEST_PRIORITY_PROVISIONAL_CANDIDATE**.
- Canonical measurement contract **NOT RATIFIED**.
- Data **2025-11 → 2026-07 SEALED**.
- **5 live processes untouched, zero trades**.

## NEXT
- **VE**: Mandate A steps 4–7 **DELIVERED** (ve_tower wheel `e5457561…`). Awaiting Red Team verdict.
- **Red Team**: **TOWER_HANDOFF** on ve_tower, then PASS_FOR_LIVE_SHADOW.
- **AI Trader**: wire ve_tower → N3/N4 flags · the 5 tests · the 3,237 suite · `probability_inputs`.

## GUARDS (standing)
- **GARD 1** `GATED_BY_CTO=True` in `code/run_production_pipeline.py:57` — never commit it flipped.
- **GARD 2** sealed holdout — never touched.

_Last persisted: Mandate A in progress (foundation delivered at `c22c876`; N3/N4 contracts underway)._
