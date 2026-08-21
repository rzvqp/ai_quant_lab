# RED TEAM — RANGE V4.4.1 T-STALE IMPLEMENTATION AUDIT
### RT-RANGE-V4_4_1-IMPLEMENTATION-AUDIT-001 · Auditor: Red Team · 2026-08-21

Independent static/construction audit of the frozen RANGE V4.4.1 T-STALE implementation (`4ed4eb4`) — the gate
between implementation freeze and a future fresh-blind validation. No redesign, no recalibration, no parameter
change, no FB14/MB3 execution, no fresh blind. Every material VE claim reproduced independently (not accepted by
assertion).

---

## 0 — VERDICT

```
V4_4_1_IMPLEMENTATION_AUDIT_PASS_WITH_NONBLOCKING_NOTES
V4_4_1_FRESH_BLIND_VALIDATION_AUTHORIZED_FOR_CEO_DECISION
```

`4ed4eb4` faithfully implements the independently-approved (`eeb082e`), frozen (`e2b65bf`), and calibrated
(`9116c2b`) T-STALE mechanism **without weakening V4.4 directional protection and without introducing lifecycle,
causality, snapshot, churn, or slow-range regressions**. All 28 audit areas PASS; 0 amendment-required, 0
blocking. Three non-blocking notes (§4) are carried-forward calibration disclosures and a labelling convention —
none is an implementation defect. This is **not** a semantic validation: T-STALE's real-market effect is
unproven until a fresh blind batch (§34).

Not authorized: fresh-blind execution, Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker, orders, live
trading, V4.4/V4.4.1 promotion.

---

## 1 — INTEGRITY & PROVENANCE (§2)

| gate | result |
|---|---|
| all 9 chain commits exist (`3bb61cf dfebe8f b1dcf92 9aba9b7 eeb082e e2b65bf 8605cb2 9116c2b 4ed4eb4`) | PASS |
| linear VE lineage `3bb61cf→b1dcf92→9aba9b7→e2b65bf→8605cb2→9116c2b→4ed4eb4` (each ancestor of next; first-parent walk clean) | PASS |
| calibration `9116c2b` (01:31) **precedes** implementation `4ed4eb4` (02:27) | PASS |
| implementation commit is exactly `4ed4eb4`; it is HEAD; **0 commits after it**; frozen | PASS |
| local = remote on all 4 mirrors (alpha1/discovery/lab/trader), branch discovery-mk-matrix-v1 | PASS |

## 2 — V4.4 / V4.3 / SCORER PRESERVATION (§3) — `V4_4_BYTE_UNTOUCHED = TRUE`

Independent git-blob comparison `3bb61cf` vs `4ed4eb4` — **identical** for every reference file:

| file | blob (both commits) |
|---|---|
| `range_semantic_v4_4.py` | `484bd4fa…` SAME |
| `range_engine_v4_4.py` | `a45b936e…` SAME |
| `range_semantic_v4_3.py` | `a822c78d…` SAME |
| `range_engine_v4_3.py` | `9a6dc728…` SAME |
| `blind_runner/scoring.py` | `664934ab…` SAME |

`4ed4eb4` is purely additive: 2 new source files + 1 test file + report + PROJECT_STATE.md, **zero** modification
of any existing semantic file.

## 3 — AUDIT MATRIX (28 areas; RT reproduced each independently)

| # | Area | VE claim | RT independent finding | Verdict |
|---|---|---|---|---|
| 1 | provenance | chain valid, frozen | linear lineage + calibration-before-impl + local=remote ×4 verified | PASS |
| 2 | V4.4 preservation | byte-untouched | 5 reference blobs identical `3bb61cf`↔`4ed4eb4` | PASS |
| 3 | implementation diff | additive, subclass, 5 overrides + 1 new | confirmed: `ConfigV441(ConfigV44)`, `StructureV441(StructureV44)`, `RangeSemanticProducerV441(RangeSemanticProducerV44)`; overrides = `__init__`,`_offer_swing_everywhere`,`_step_macro`,`snapshot_state`,`restore_state`; new = `_t_stale_should_fire`. No hidden semantic override | PASS |
| 4 | config / parameters | 29/4/3/12 | read from source; **no env/runtime substitution**; `validate()` fail-closes if rejections < alternation+1 | PASS |
| 5 | config_id | matches registry | RT recomputed `ConfigV441().config_id()` = `d7b6c067…a1f03` == frozen `9116c2b` registry value exactly (31 fields) | PASS |
| 6 | T-STALE eligibility | pre-confirmed only | called only inside `_step_macro`'s `zones is None` branch (reached iff `reached_confirmed` False); confirmed-immunity reproduced (RT probe + engine) | T_STALE_SCOPE_PASS |
| 7 | trigger semantics | boundary+age+count+alternation, none alone | RT probe: age-alone / count-alone / one-sided-alone all → False; only the conjunction fires | PASS |
| 8 | rejected-evidence accounting | only genuine geom rejections | RT probe: accepted swing → not buffered; far swing (`SWING_OUTSIDE_CLUSTER`) → buffered; `ATR_UNAVAILABLE` excluded by source; chronological | PASS |
| 9 | alternation | =3, side-flip count | RT probe: 5 one-sided (0 flips)→False, 4 rej/2 flips→False, 5 rej/3 flips→True | PASS |
| 10 | age boundary | 11 vs 12 | RT probe: age 11→False, age 12→True (uses `start_ts` bar index, no container/timestamp dep) | PASS |
| 11 | rejection-count boundary | 3 vs 4 | RT probe: 3→False, 4→True | PASS |
| 12 | 29-bar expiry | bounded, strict | RT probe: bar exactly at `as_of-29` excluded (strict `>`); in-window count exact; all expire later; deque `maxlen=64` bounds history | PASS |
| 13 | transition priority | after T-KILL, before T2/T3 | source: `degeneracy_check`→kill, then `zones is None`→(T-STALE, then `_evaluate_macro_formation`); no same-bar double transition | PASS |
| 14 | next-bar replacement | next causal bar only | `observe()` runs `_offer_swing_everywhere` (lagged swings) **before** `_step_macro`; `_kill_macro` sets `_active_macro=None`, identical to every existing V4.4 termination; no synchronous re-seed in the firing call. RT: `_pending_*` clear after fire; VE stale6/7/8 (no-same-bar, snapshot-across, prefix-invariance) reproduced green + non-vacuous; RT prefix-invariance probe green | NEXT_BAR_REPLACEMENT_VALID |
| 15 | positive stale release | slot freed, fresh candidate can confirm | VE stale2 reproduced: abandonment → `EPISODE_REPLACEMENT` → fresh candidate reaches `OK_RANGE_MACRO`/`reached_confirmed` | PASS |
| 16 | directional protection | no confirmation bypass | fresh candidate re-enters unchanged `_evaluate_macro_formation` (ER/RND/traversal); VE stale5 reproduced (post-abandon candidate still fails when directional) | DIRECTIONAL_PROTECTION_PRESERVED |
| 17 | anti-churn | 0 fires / 200-bar trend | **RT-generated** 200-bar uptrend through the real engine: **0** T-STALE fires | PASS |
| 18 | slow-range protection | never abandoned | source: accepted touches never enter rejection buffer; VE stale3 reproduced (slow range, 0 fires) | SLOW_RANGE_PROTECTION_PASS |
| 19 | ER/RND/traversal preservation | frozen | registry confirms `ER_max=0.5,RND_max=1.0,MIN_TRAVERSALS=1,W=29` unchanged; `_evaluate_macro_formation` inherited byte-unmodified | PASS |
| 20 | confirmed lifecycle | disjoint | `_step_macro`'s confirmed branch (`zones` not None) never reaches T-STALE; WEAKENING/breakout/re-entry inherited unchanged | PASS |
| 21 | INTERNAL parity | 0 divergence | VE stale10 reproduced: INTERNAL id/reason/state/bounds byte-identical V4.4↔V4.4.1; `_step_internal` inherited unchanged | PASS |
| 22 | episode identity | reuses frozen mechanics | `_kill_macro`→`_record_macro_termination_for_episode_identity` inherited unchanged; stale zone (0-IoU) does not merge with replacement (stale2) | PASS |
| 23 | reason code | 1 new, additive, reachable | `REASONS_V441=41` (asserted at import); `STALE_CANDIDATE_ABANDONED` reachable (RT + stale1), emitted only on the transition, absent from confirmed lifecycle | PASS |
| 24 | snapshot / versioning | new field, fail-closed | `v441_rejected_touches` persisted; `restore_state` builds a scratch instance then atomic `__dict__` swap; RT + VE stale_restore: wrong config/contract/fingerprint refused, `STATE_BEFORE==STATE_AFTER` (no partial mutation) | PASS |
| 25 | fingerprint | covers semantic files | RT git-blobs: `range_semantic_v4_4_1.py ddec2474…`, `range_engine_v4_4_1.py 99e284d3…`; identity label `v4-4-1-implementation-freeze-2026-08-21` (Note 1) | PASS |
| 26 | tests | 18 new / 488 full / mypy strict | RT reran: **18** stale PASS, **76** V4.4 PASS, **488** full PASS; **mypy --strict clean** on both new files; no skip/xfail; assertions substantive; stale7 explicitly guards vacuity | PASS |
| 27 | mutations | 8/8 caught | RT independently applied all 8 at runtime (subclass/config, zero repo edit): **8/8 caught** (2 via `validate()` fail-closed at construction) | PASS |
| 28 | complexity/memory | bounded | `_rejected_touches` deque `maxlen=64`; window scan O(64)/bar; no unbounded list; V4.4.1 state separated from upstream | PASS |

**28/28 PASS · 0 amendment · 0 blocking.**

## 4 — NON-BLOCKING NOTES (none is an implementation defect)

1. **Implementation fingerprint is a descriptive freeze-label**, not a source digest (`v4-4-1-implementation-freeze-2026-08-21`) — the exact convention V4.3/V4.4 already use. Its integrity role is actually served by the frozen commit's git-blob identity (§2/§25) + the `config_id` snapshot check. Consistent, carried from the V4.4 implementation audit; recorded, not blocking.
2. **`min_alternation = 3` carries the calibration `FRAGILE` flag** (`9116c2b` §5.3: resolved±1 each fail one side). The implementation *faithfully encodes it*, and the `validate()` floor + mutation tests M1/M2/M3 protect against silent weakening — so this is not an implementation issue, but the residual must be watched at fresh-blind, exactly as the design/calibration audits flagged.
3. **Window-length `29` sensitivity "not independently discriminated"** (`9116c2b` §5.1, disclosed calibration limitation). Faithfully implemented; carried forward to the fresh-blind stage.

## 5 — CONSTRAINT COMPLIANCE (CEO Directive)

`FROZEN_COMMIT_4ed4eb4` ✓ · `NO_REDESIGN/NO_RECALIBRATION` ✓ (audit only) · `PARAMETERS_29_4_12_3_FIXED` ✓
(verified in source + config_id) · `NO_FB14_EXECUTION` ✓ · `NO_MB3_ACCESS` ✓ (§30: only governance comments, zero
semantic use; MB3-025→048 sealed) · `NO_FRESH_BLIND` ✓ (construction/static only) · `VERIFY_ANTI_CHURN` ✓ (RT
200-bar) · `VERIFY_SLOW_RANGE_PROTECTION` ✓ · `VERIFY_NEXT_BAR_REPLACEMENT` ✓ · `VERIFY_TEST_NONVACUITY` ✓ ·
`FAIL_CLOSED_ON_SEMANTIC_DEVIATION` — no semantic deviation found. §29 rollback: V4.4/V4.3 do **not** import
V4.4.1 (grep 0); V4.4 remains importable with 76/76 tests green while V4.4.1 is present.

## 6 — WHAT WOULD HAVE MADE THIS AMENDMENT_REQUIRED / BLOCKED (none occurred)

Any of: a modified V4.4/V4.3/scorer byte (§2 SAME); a `config_id` ≠ registry (§5 exact match); a parameter other
than 29/4/3/12 or env-substituted (§4 hardcoded); T-STALE firing on CONFIRMED/WEAKENING/INTERNAL (§6/§20/§21
disjoint); age/count/one-sided-alone firing (§7/§9 conjunction required); a same-bar replacement path (§14 none);
an ER/RND/traversal relaxation (§19 frozen); an unbounded rejected-evidence history (§28 `maxlen=64`); a snapshot
that restores across mismatched identity (§24 fail-closed); a mutation that no test catches (§27 8/8); or FB14/MB3
semantic use (§30 clean). None present.

---

## 7 — NEXT CEO ACTION (§34)

If the CEO accepts this PASS, authorize a **new fresh blind validation batch** that is independent of the V4.4.1
diagnosis, design, calibration, implementation, and this audit — and does **not** reuse FB14, MB3-001→024, or
MB3-025→048. No batch is created in this mandate. The `min_alternation=3` FRAGILE flag and the window-29
sensitivity (Notes 2/3) should be explicit watch-items at that stage. Whether to proceed, or hold at V4.3/V4.4,
remains a CEO decision. This audit does **not** declare V4.4.1 semantically validated.

---

*Red Team · static/construction audit · detectors/labels/scorer/escrow unmodified · changes only in `red_team/` ·
no FB14/MB3 execution · MB3-025→048 sealed · LEDGER E95 (prev E94).*
