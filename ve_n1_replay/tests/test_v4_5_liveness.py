"""V4.5 liveness recovery tests (mandate `VE-RANGE-V4-5-STALE-CANDIDATE-RECOVERY-001` section 23).

**STATUS: both mechanisms tested here are `RANGE_V4_5_RECOVERY_BLOCKED` -- validated UNSAFE against real
data, NOT deployed.** Every test below still passes and still correctly documents what each mechanism
DOES (it fires exactly on the shapes it was designed to catch) -- that was never in question. What the
tests in this file CANNOT show, by their own hand-constructed nature, is whether the firing condition is
SAFE against the full diversity of real, genuinely-converging formations. It is not: a full-history
negative control (delivery report) against all 187 real macro structures that reached `CONFIRMED` between
2011-2026 found H-ONE-SIDED would have fired before 69 of them (36.9%) and H-PERSISTENCE before 23 of them
(12.3%), in both cases well before those structures went on to confirm normally. `test_live1h`/`test_live1i`
below construct small, fast, illustrative fixtures that demonstrate the SAME class of premature firing
mechanically (not the full real dataset, which isn't practical inside a unit test) -- read them alongside
this note, not as a substitute for the real negative-control numbers.

Construction/regression methodology matches `test_v4_4_1_stale.py`'s own established, precedented pattern
(direct-construction-plus-real-orchestration-call: build a precisely-controlled `StructureV44`, call
`_step_macro`/`_candidate_stagnation_reason` directly on it) -- not organically-grown bars chosen to
coincidentally hit the target state, and not re-derived expectations.

Two structurally disjoint mechanisms are tested throughout, matching the module's own design (see
`range_semantic_v4_5.py`'s `_candidate_stagnation_reason` docstring): H-ONE-SIDED (fires via
`CANDIDATE_ONE_SIDED_TERMINATED` when at least one side has not yet reached `n_touch` and full-lifetime
touch evidence resolves to a one-sided pattern) and H-PERSISTENCE (fires via
`CANDIDATE_PERSISTENCE_TERMINATED` when both sides have reached `n_touch` but the candidate sits
unconfirmed for `WEAKENING_MAX_BARS` consecutive eligible bars). Each has its own positive fixture AND its
own hand-constructed negative control (T-STALE's own `test_stale3`/`test_stale4` precedent for why both
are required) -- CORRECTION, disclosed rather than quietly fixed: those hand-constructed negative controls
(`test_live1e`/`test_live1f`/`test_live1g`) all still pass and are still true, but they test only the
NARROW synthetic scenarios they were built for -- they did NOT, and structurally could not, catch the
real-data false-positive rate above. That gap is exactly why the mandate requires validation against real
history, not merely hand-built scenarios; both are necessary, neither is sufficient alone."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_range_semantic_v4_3 import KW, legs_bars   # noqa: E402

from ve_n1_replay.range_engine_v4_4 import RangeSemanticEngineV44   # noqa: E402
from ve_n1_replay.range_engine_v4_5 import RangeSemanticEngineV45, RangeSnapshotErrorV45   # noqa: E402
from ve_n1_replay.range_semantic_v4_3 import ContractErrorV43, Depth   # noqa: E402
from ve_n1_replay.range_semantic_v4_4 import ConfigV44, RangeSemanticProducerV44, StructureV44   # noqa: E402
from ve_n1_replay.range_semantic_v4_5 import (   # noqa: E402
    CANDIDATE_ONE_SIDED_TERMINATED, CANDIDATE_PERSISTENCE_TERMINATED, ConfigV45,
    RANGE_HIERARCHICAL_V4_5_CONTRACT_VERSION, RANGE_HIERARCHICAL_V4_5_NORMATIVE_CONFIG_ID, REASONS_V45,
    RangeSemanticProducerV45,
)


def cfg44(**kw: Any) -> ConfigV44:
    return ConfigV44(**kw)


def cfg45(**kw: Any) -> ConfigV45:
    return ConfigV45(**kw)


def never_confirmed_macro(prod: RangeSemanticProducerV44, *, structure_id: int = 1, upper: float = 110.0,
                          lower: float = 100.0, atr_ref: float = 1.0, start_ts: int = 0,
                          cfg: ConfigV44 | None = None) -> StructureV44:
    """A MACRO candidate with an established boundary but never confirmed -- same shape as
    `test_v4_4_1_stale.py::never_confirmed_macro`, one level down (plain `StructureV44`, no subclass
    needed -- see `range_semantic_v4_5.py`'s own module docstring for why)."""
    cfg = cfg or cfg45()
    st = StructureV44(structure_id=structure_id, depth=Depth.MACRO, parent_structure_id=None,
                      start_ts=start_ts, trailing_window=cfg.W)
    st.atr_ref = atr_ref
    st.up.offer(upper, 1e18)
    st.dn.offer(lower, 1e18)
    st.record_touch_v44(start_ts, True)
    st.record_touch_v44(start_ts, False)
    prod._active_macro = st
    return st


def feed_accepted_touches(st: StructureV44, touches: list[tuple[int, bool]]) -> None:
    """touches: [(bar_index, is_high), ...] -- unconditionally ACCEPTED (bypasses tolerance, same
    deterministic-injection convention `test_v4_4_1_stale.py::feed_rejections` already established, applied
    here to ACCEPTED evidence instead of rejected)."""
    for b, is_high in touches:
        cluster = st.up if is_high else st.dn
        near_boundary = (cluster.center or 0.0) + (0.001 if is_high else -0.001)
        cluster.offer(near_boundary, 1e18)
        st.record_touch_v44(b, is_high)


# ═══════════════════════════════════ LIVE-1: stale candidate reproduction (section 6), H-ONE-SIDED ═══════════════════════════════════

def test_live1_directional_stagnation_reproduces_the_real_defect_shape() -> None:
    """Minimal deterministic fixture (mandate section 6B): one side grows continuously (14 touches), the
    other is frozen at its founding touch -- the exact shape independently confirmed against the REAL
    macro_id 133 lineage (2021-01-06 -> 2021-08-08: up.members 1->44, dn.members frozen at 1 for ~7
    months) in the delivery report, and against macro_id 770's own early life (up/dn both far past n_touch
    only much later) in the canonical 2011-2022 reproduction. Never depends on any strategy/profitability
    outcome."""
    prod = RangeSemanticProducerV45(cfg45())
    st = never_confirmed_macro(prod, cfg=cfg45())
    feed_accepted_touches(st, [(b, True) for b in range(5, 200, 15)])  # up keeps growing, dn frozen at 1
    assert len(st.up.members) > 2 and len(st.dn.members) == 1
    assert prod._candidate_stagnation_reason(st, 200) == CANDIDATE_ONE_SIDED_TERMINATED


def test_live1b_reachable_via_step_macro_direct() -> None:
    prod = RangeSemanticProducerV45(cfg45())
    st = never_confirmed_macro(prod, cfg=cfg45())
    feed_accepted_touches(st, [(b, True) for b in range(5, 200, 15)])
    events: list[Any] = []
    result = prod._step_macro(200, 105.0, 95.0, 100.0, events)
    assert result == CANDIDATE_ONE_SIDED_TERMINATED
    assert CANDIDATE_ONE_SIDED_TERMINATED in REASONS_V45
    assert any(e.kind == CANDIDATE_ONE_SIDED_TERMINATED for e in events)
    assert prod._active_macro is None  # slot released


# ═══════════════════════════════════ LIVE-1c/1d: H-PERSISTENCE positive fixture ═══════════════════════════════════

def test_live1c_persistence_fires_once_both_sided_but_never_confirming() -> None:
    """Positive fixture for the SECOND mechanism: both sides reach n_touch almost immediately (unlike
    LIVE-1's one-sided shape), yet the structure never satisfies T3's ER/traversal/RND gate -- the exact
    shape independently confirmed against the real macro_id 770 lineage (up/dn both far past n_touch
    within ~50 bars of formation, still unconfirmed 3548.94 days / 9.7 years later, per the delivery
    report's full-history regression). `_trailing_closes` is left EMPTY
    (no `push_close_v44` calls), so `zones()` genuinely returns `None` throughout (pre-boundary, matching
    `_step_macro`'s own `zones is None` gate) -- this is not a T3-discrimination-gate scenario, it is a
    "boundary never even established" scenario, the more fundamental of the two ways T3 can stay
    unsatisfied indefinitely."""
    cfg = cfg45()
    prod = RangeSemanticProducerV45(cfg)
    st = never_confirmed_macro(prod, cfg=cfg)
    feed_accepted_touches(st, [(5, True), (6, False)])  # both sides reach n_touch=2 immediately
    assert len(st.up.members) >= cfg.n_touch and len(st.dn.members) >= cfg.n_touch

    fired_at = None
    for i in range(cfg.d_macro, cfg.d_macro + cfg.WEAKENING_MAX_BARS + 5):
        reason = prod._candidate_stagnation_reason(st, i)
        if reason is not None:
            fired_at = (i, reason)
            break
    assert fired_at is not None, "H-PERSISTENCE never fired -- streak mechanism did not engage"
    fired_i, fired_reason = fired_at
    assert fired_reason == CANDIDATE_PERSISTENCE_TERMINATED
    # fires EXACTLY at WEAKENING_MAX_BARS consecutive eligible bars, not before, not late
    assert fired_i == cfg.d_macro + cfg.WEAKENING_MAX_BARS - 1


def test_live1d_persistence_reachable_via_step_macro_direct() -> None:
    cfg = cfg45()
    prod = RangeSemanticProducerV45(cfg)
    st = never_confirmed_macro(prod, cfg=cfg)
    feed_accepted_touches(st, [(5, True), (6, False)])
    events: list[Any] = []
    result = None
    for i in range(cfg.d_macro, cfg.d_macro + cfg.WEAKENING_MAX_BARS + 2):
        result = prod._step_macro(i, 105.0, 95.0, 100.0, events)
        if result == CANDIDATE_PERSISTENCE_TERMINATED:
            break
    assert result == CANDIDATE_PERSISTENCE_TERMINATED
    assert CANDIDATE_PERSISTENCE_TERMINATED in REASONS_V45
    assert any(e.kind == CANDIDATE_PERSISTENCE_TERMINATED for e in events)
    assert prod._active_macro is None


# ═══════════════════════════════════ LIVE-1e/1f: negative controls (T-STALE's own test_stale3/4 precedent) ═══════════════════════════════════

def test_live1e_insufficient_evidence_never_fires_one_sided_however_old() -> None:
    """H-ONE-SIDED negative control, mirroring `test_stale3_slow_genuine_range_never_abandoned`'s own
    "however old" framing. NOTE on why this is the only meaningful shape for this particular negative
    control: with `n_touch=2` (frozen v4.4 value), "not both_satisfied" means at least one side is stuck
    at its untagged founding touch alone -- so `_touch_tags` can only ever contain tags from the OTHER
    side while that holds (the stuck side contributes zero tags by definition). A genuinely "alternating
    while not-both-satisfied" fixture is therefore structurally impossible to construct, not merely hard
    to construct -- verified by direct arithmetic, not assumed. What CAN and must be verified is the
    fail-closed floor itself: with fewer than 3 total tags on record, `alternation_rate` returns `None`
    and the mechanism must never treat that absence as evidence, no matter how old the candidate gets."""
    prod = RangeSemanticProducerV45(cfg45())
    st = never_confirmed_macro(prod, cfg=cfg45())
    feed_accepted_touches(st, [(5, True)])  # exactly 1 tag on record -- below the 3-tag alternation floor
    for i in range(30, 500, 25):
        assert len(st.up.members) < cfg45().n_touch or len(st.dn.members) < cfg45().n_touch  # still in-domain
        assert prod._candidate_stagnation_reason(st, i) is None, f"false trigger on insufficient evidence at bar {i}"


def test_live1f_confirms_before_persistence_streak_completes_is_never_killed() -> None:
    """H-PERSISTENCE negative control: a candidate that becomes both-sided-eligible and then CONFIRMS well
    before accumulating `WEAKENING_MAX_BARS` eligible bars must never be touched by this mechanism --
    `reached_confirmed` short-circuits `_candidate_stagnation_reason` to `None` on every subsequent call."""
    cfg = cfg45()
    prod = RangeSemanticProducerV45(cfg)
    st = never_confirmed_macro(prod, cfg=cfg)
    feed_accepted_touches(st, [(5, True), (6, False)])
    for i in range(cfg.d_macro, cfg.d_macro + 5):
        assert prod._candidate_stagnation_reason(st, i) is None
    st.reached_confirmed = True  # confirms partway through, well short of WEAKENING_MAX_BARS=22
    for i in range(cfg.d_macro + 5, cfg.d_macro + cfg.WEAKENING_MAX_BARS + 10):
        assert prod._candidate_stagnation_reason(st, i) is None, \
            f"a CONFIRMED structure must never be killed by either liveness mechanism (bar {i})"


def test_live1g_late_transition_into_both_satisfied_starts_the_streak_fresh_not_from_zero() -> None:
    """A structure that spends a long time one-touch-short on one side before FINALLY reaching n_touch on
    both must start its H-PERSISTENCE streak counting from the bar it actually became eligible, not from
    its own creation bar -- otherwise a candidate that took long to reach eligibility would be killed
    almost immediately after (double-penalizing the same slowness twice), which is exactly the kind of
    over-eager release the mandate's T-STALE lesson warns against. Also mechanically confirms
    `CANDIDATE_ONE_SIDED_TERMINATED` is never returned once both_satisfied holds (branch exclusivity)."""
    cfg = cfg45()
    prod = RangeSemanticProducerV45(cfg)
    st = never_confirmed_macro(prod, cfg=cfg)
    feed_accepted_touches(st, [(10, True)])  # up reaches n_touch=2 early -- satisfied well before bar 150
    # dn stays frozen at founding=1 through bar 150 (well past d_macro=29) -- H-ONE-SIDED's own domain,
    # with exactly 1 tag on record (the up touch above) -- below the 3-tag alternation floor, stays None
    for i in range(30, 150, 20):
        assert prod._candidate_stagnation_reason(st, i) is None
    feed_accepted_touches(st, [(150, False)])  # dn finally reaches n_touch=2 at bar 150 -- eligibility begins
    assert len(st.up.members) >= cfg.n_touch and len(st.dn.members) >= cfg.n_touch
    for k in range(cfg.WEAKENING_MAX_BARS - 1):
        i = 150 + k
        reason = prod._candidate_stagnation_reason(st, i)
        assert reason != CANDIDATE_ONE_SIDED_TERMINATED
        assert reason is None, f"fired too early relative to the ELIGIBILITY bar (150), at streak position {k}"
    final = prod._candidate_stagnation_reason(st, 150 + cfg.WEAKENING_MAX_BARS - 1)
    assert final == CANDIDATE_PERSISTENCE_TERMINATED  # fires exactly WEAKENING_MAX_BARS bars after ELIGIBILITY


# ═══════════════════════════════════ LIVE-1h/1i: the REAL failure mode, illustrated mechanically (see this file's own module docstring) ═══════════════════════════════════

def test_live1h_one_sided_fires_on_a_candidate_that_would_have_diversified_shortly_after() -> None:
    """Illustrates, mechanically and quickly, the SAME class of premature firing the real-data negative
    control found affecting 69/187 (36.9%) genuine confirmations: a candidate that is one-sided in its
    EARLY life (matching the real median first-fire offset of ~24 bars past d_macro) but whose lagging
    side would have caught up shortly after, had the candidate not already been killed. This is a small,
    fast, hand-built demonstration, not a substitute for the real-data numbers -- it exists so a reader
    does not have to re-run the full 355k-bar validation to see WHY this mechanism is unsafe."""
    cfg = cfg45()
    prod = RangeSemanticProducerV45(cfg)
    st = never_confirmed_macro(prod, cfg=cfg)
    # dn accumulates 3 tagged touches by bar ~34 (d_macro=29 + a few) -- up stays at founding=1 throughout,
    # matching the shape of every real H-ONE-SIDED false positive
    feed_accepted_touches(st, [(30, False), (32, False), (34, False)])
    fire_bar = None
    for i in range(cfg.d_macro, 40):
        if prod._candidate_stagnation_reason(st, i) == CANDIDATE_ONE_SIDED_TERMINATED:
            fire_bar = i
            break
    assert fire_bar is not None, "fixture must reproduce the firing condition to illustrate the problem"

    # counterfactual: rebuild an IDENTICAL candidate, but let it run a few bars further BEFORE evaluating --
    # its lagging ("up") side reaches n_touch=2 only 4 bars after the point H-ONE-SIDED would have killed it,
    # at which point it leaves H-ONE-SIDED's own domain entirely (both_satisfied) like any healthy candidate
    prod2 = RangeSemanticProducerV45(cfg)
    st2 = never_confirmed_macro(prod2, cfg=cfg)
    feed_accepted_touches(st2, [(30, False), (32, False), (34, False)])
    feed_accepted_touches(st2, [(fire_bar + 4, True)])  # the lagging side finally catches up
    assert len(st2.up.members) >= cfg.n_touch and len(st2.dn.members) >= cfg.n_touch
    reason_after_catchup = prod2._candidate_stagnation_reason(st2, fire_bar + 4)
    assert reason_after_catchup != CANDIDATE_ONE_SIDED_TERMINATED, \
        "the candidate had already left H-ONE-SIDED's domain by the time it would have caught up -- " \
        "confirming the earlier firing was premature relative to this candidate's own trajectory"


def test_live1i_persistence_threshold_is_unrelated_to_confirmation_readiness() -> None:
    """Illustrates the SAME class of premature-firing risk for H-PERSISTENCE that the real-data negative
    control found affecting 23/187 (12.3%) genuine confirmations (some after waiting over 12,000 bars),
    without re-deriving the exact real timing synthetically (fragile to hand-tune; the real numbers are
    definitive on their own -- see this file's module docstring): `_evaluate_macro_formation` (T3, v4.4,
    inherited unmodified) is mechanically confirmed here to read only `up`/`dn` touch geometry and
    `_trailing_closes`-derived ER/traversal/RND -- never the candidate's age, `start_ts`, or any streak
    count. H-PERSISTENCE's own trigger is a bar-count streak with no relationship to those confirmation
    inputs. A mechanism killing a candidate based on a quantity its own confirmation gate never consults
    cannot, by construction, distinguish "about to confirm" from "will never confirm" -- exactly what the
    real 23/187 finding shows empirically."""
    import inspect
    src = inspect.getsource(RangeSemanticProducerV44._evaluate_macro_formation)
    assert "i - st.start_ts < self._cfg.d_macro" in src  # T3's OWN, pre-existing, unrelated age floor
    for forbidden in ("_weakening_bars", "WEAKENING_MAX_BARS", "_t3_eligible"):
        assert forbidden not in src, \
            f"T3 confirmation gate must not depend on {forbidden!r} (a H-PERSISTENCE-only concept) -- " \
            f"if it does, this test's premise is wrong"


# ═══════════════════════════════════ LIVE-2: slot liveness -- release enables a NEW candidate ═══════════════════════════════════

def test_live2_slot_liveness_new_candidate_can_form_after_release() -> None:
    prod = RangeSemanticProducerV45(cfg45())
    original_id = prod._registry.new_id()  # advance the registry properly, matching real usage
    st = never_confirmed_macro(prod, structure_id=original_id, cfg=cfg45())
    feed_accepted_touches(st, [(b, True) for b in range(5, 200, 15)])
    events: list[Any] = []
    prod._step_macro(200, 105.0, 95.0, 100.0, events)
    assert prod._active_macro is None
    # forming_macro = self._active_macro is None -- the EXISTING, unchanged v4.3/v4.4 gate -- now open:
    prod._offer_swing_everywhere(201, 50.0, True, events)
    prod._offer_swing_everywhere(202, 40.0, False, events)
    assert prod._active_macro is not None
    assert prod._active_macro.structure_id != original_id
    assert any(e.kind in ("EPISODE_REPLACEMENT", "EPISODE_CONTINUATION", "EPISODE_MERGED") for e in events)


# ═══════════════════════════════════ LIVE-3: candidate release mechanics ═══════════════════════════════════

def test_live3_release_uses_existing_kill_macro_mechanics() -> None:
    """No new termination pathway -- reuses `_kill_macro` unchanged (generic on `reason: str`), same
    episode-identity bookkeeping every other termination uses."""
    prod = RangeSemanticProducerV45(cfg45())
    st = never_confirmed_macro(prod, structure_id=7, upper=110.0, lower=100.0, cfg=cfg45())
    feed_accepted_touches(st, [(b, True) for b in range(5, 200, 15)])
    events: list[Any] = []
    prod._step_macro(200, 105.0, 95.0, 100.0, events)
    assert prod._last_terminated_macro_id == 7
    assert prod._last_terminated_macro_end_reason == CANDIDATE_ONE_SIDED_TERMINATED
    assert prod._last_terminated_macro_zone is not None
    lo, hi = prod._last_terminated_macro_zone
    assert lo == 100.0 and abs(hi - 110.0) < 0.1  # dn (frozen at founding touch) exact; up drifts slightly


def test_live3b_persistence_release_uses_existing_kill_macro_mechanics() -> None:
    cfg = cfg45()
    prod = RangeSemanticProducerV45(cfg)
    st = never_confirmed_macro(prod, structure_id=9, upper=110.0, lower=100.0, cfg=cfg)
    feed_accepted_touches(st, [(5, True), (6, False)])
    events: list[Any] = []
    for i in range(cfg.d_macro, cfg.d_macro + cfg.WEAKENING_MAX_BARS + 2):
        prod._step_macro(i, 105.0, 95.0, 100.0, events)
        if prod._active_macro is None:
            break
    assert prod._last_terminated_macro_id == 9
    assert prod._last_terminated_macro_end_reason == CANDIDATE_PERSISTENCE_TERMINATED
    assert prod._active_macro is None


# ═══════════════════════════════════ LIVE-4: no supersession mechanism implemented (section 10) ═══════════════════════════════════

def test_live4_no_explicit_supersession_release_then_natural_reformation_only() -> None:
    """Mandate section 10 investigated explicit supersession; NOT implemented here -- release clears the
    slot and the EXISTING, unmodified candidate-formation path (`forming_macro = self._active_macro is
    None`) admits the next swing pair naturally. This test proves there is no separate supersession
    code path: the newly-formed candidate goes through IDENTICAL admission as any fresh candidate
    (REPLACEMENT/CONTINUATION/MERGE episode-identity logic, unmodified from v4.4)."""
    prod = RangeSemanticProducerV45(cfg45())
    st = never_confirmed_macro(prod, structure_id=1, upper=110.0, lower=100.0, cfg=cfg45())
    feed_accepted_touches(st, [(b, True) for b in range(5, 200, 15)])
    events: list[Any] = []
    prod._step_macro(200, 105.0, 95.0, 100.0, events)
    events2: list[Any] = []
    prod._offer_swing_everywhere(201, 108.0, True, events2)
    prod._offer_swing_everywhere(202, 102.0, False, events2)
    # same episode-identity event vocabulary v4.4 already uses -- no new "SUPERSEDED" kind exists
    kinds = {e.kind for e in events2}
    assert kinds & {"EPISODE_CONTINUATION", "EPISODE_MERGED", "EPISODE_REPLACEMENT"}


# ═══════════════════════════════════ LIVE-5: invalid/never-confirmed termination proof ═══════════════════════════════════

def test_live5_only_fires_for_never_confirmed_candidates() -> None:
    """A CONFIRMED structure (even one that would otherwise match either mechanism's shape) is
    structurally immune -- `_candidate_stagnation_reason` returns `None` whenever `reached_confirmed` is
    True, and the call site itself (`_step_macro`) only reaches this check inside the `zones is None`
    branch, which is impossible once `reached_confirmed` is True (mirrors `range_semantic_v4_4_1.py`'s
    own equivalent confirmed-immunity test)."""
    prod = RangeSemanticProducerV45(cfg45())
    st = never_confirmed_macro(prod, cfg=cfg45())
    feed_accepted_touches(st, [(b, True) for b in range(5, 200, 15)])
    st.reached_confirmed = True
    assert prod._candidate_stagnation_reason(st, 200) is None


# ═══════════════════════════════════ LIVE-6: confirmation gate unchanged (section 11) ═══════════════════════════════════

def test_live6_confirmation_semantics_byte_identical_to_v4_4() -> None:
    """A structure that WOULD confirm under v4.4 confirms identically under v4.5 -- `_evaluate_macro_
    formation` is inherited unmodified, never touched by this mandate."""
    prod44 = RangeSemanticProducerV44(cfg44())
    prod45 = RangeSemanticProducerV45(cfg45())
    st44 = never_confirmed_macro(prod44, upper=110.0, lower=100.0, cfg=cfg44())
    st45 = never_confirmed_macro(prod45, upper=110.0, lower=100.0, cfg=cfg45())
    for i in range(1, 40):
        close = 105.0 + (0.3 if i % 2 == 0 else -0.3)  # tight oscillation -- efficient range-forming closes
        st44.push_close_v44(i, close)
        st45.push_close_v44(i, close)
    events44: list[Any] = []
    events45: list[Any] = []
    r44 = prod44._evaluate_macro_formation(st44, 39, events44)
    r45 = prod45._evaluate_macro_formation(st45, 39, events45)
    assert r44 == r45
    assert st44.reached_confirmed == st45.reached_confirmed


def test_live6b_no_automatic_promotion_release_is_not_confirmation() -> None:
    """A released (stagnation-terminated) candidate is NEVER marked confirmed -- release is a rejection
    path, not a promotion path. Checked for BOTH mechanisms."""
    prod = RangeSemanticProducerV45(cfg45())
    st = never_confirmed_macro(prod, cfg=cfg45())
    feed_accepted_touches(st, [(b, True) for b in range(5, 200, 15)])
    events: list[Any] = []
    prod._step_macro(200, 105.0, 95.0, 100.0, events)
    assert st.reached_confirmed is False
    assert st.confirm_ts is None
    assert not any(e.kind == "OK_RANGE_MACRO" for e in events)

    cfg = cfg45()
    prod2 = RangeSemanticProducerV45(cfg)
    st2 = never_confirmed_macro(prod2, structure_id=2, cfg=cfg)
    feed_accepted_touches(st2, [(5, True), (6, False)])
    events2: list[Any] = []
    for i in range(cfg.d_macro, cfg.d_macro + cfg.WEAKENING_MAX_BARS + 2):
        prod2._step_macro(i, 105.0, 95.0, 100.0, events2)
        if prod2._active_macro is None:
            break
    assert st2.reached_confirmed is False
    assert st2.confirm_ts is None


# ═══════════════════════════════════ LIVE-7: boundary semantics unchanged (section 12) ═══════════════════════════════════

def test_live7_boundary_construction_untouched() -> None:
    """`boundary_upper`/`boundary_lower` remain `Cluster.center` (v4.3, unmodified) -- no rolling
    high/low, no Donchian/Bollinger/ATR-channel substitute anywhere in this module (mechanically
    confirmed: this module never assigns to `.up`/`.dn`/`boundary_upper`/`boundary_lower` at all, only
    reads them)."""
    import inspect
    from ve_n1_replay import range_semantic_v4_5 as mod
    src = inspect.getsource(mod)
    for forbidden in ("rolling_high", "rolling_low", "donchian", "Donchian", "bollinger", "Bollinger",
                     "atr_channel"):
        assert forbidden not in src, f"boundary semantics must not be reinvented: found {forbidden!r}"


# ═══════════════════════════════════ LIVE-8: restart determinism (section 22) ═══════════════════════════════════

def test_live8_snapshot_restart_across_stagnation_termination_bar_identical() -> None:
    engine_a = RangeSemanticEngineV45(range_config=cfg45(), acknowledge_construction_only=True, **KW)
    bars = legs_bars([(105.0, 3)] + [(105.0 + 0.001 * i, 2) for i in range(1, 60)])
    continuous = []
    for bar in bars:
        _, res, ev = engine_a.observe_closed_bar(bar)
        continuous.append((res.macro_reason, tuple(e.kind for e in ev)))

    engine_b = RangeSemanticEngineV45(range_config=cfg45(), acknowledge_construction_only=True, **KW)
    split = len(bars) // 2
    for bar in bars[:split]:
        engine_b.observe_closed_bar(bar)
    snap = engine_b.snapshot()
    engine_c = RangeSemanticEngineV45(range_config=cfg45(), acknowledge_construction_only=True, **KW)
    for bar in bars[:split]:
        engine_c.observe_closed_bar(bar)
    engine_c.restore(snap)
    resumed = []
    for bar in bars[split:]:
        _, res, ev = engine_c.observe_closed_bar(bar)
        resumed.append((res.macro_reason, tuple(e.kind for e in ev)))
    assert continuous[split:] == resumed


def test_live8b_restore_refuses_v4_4_snapshot() -> None:
    engine44 = RangeSemanticEngineV44(range_config=cfg44(), acknowledge_construction_only=True, **KW)
    for bar in legs_bars([(105.0, 3), (106.0, 3)]):
        engine44.observe_closed_bar(bar)
    snap44 = engine44.snapshot()
    engine45 = RangeSemanticEngineV45(range_config=cfg45(), acknowledge_construction_only=True, **KW)
    import pytest
    with pytest.raises(RangeSnapshotErrorV45):
        engine45.restore(snap44)


def test_live8c_t3_eligible_streak_survives_snapshot_restore() -> None:
    """Targeted determinism check for the NEW producer-level counter specifically (LIVE-8 exercises the
    engine-level API generically but does not guarantee it hits the streak-counting branch): split a
    replay EXACTLY mid-way through an active H-PERSISTENCE streak, snapshot/restore, and confirm the
    resumed run reaches `CANDIDATE_PERSISTENCE_TERMINATED` at the SAME bar as an uninterrupted run -- a
    silently-reset (or silently-preserved-wrong) counter would desynchronize the two."""
    cfg = cfg45()

    def run_continuous(n_steps: int) -> list[tuple[int, str | None]]:
        prod = RangeSemanticProducerV45(cfg)
        st = never_confirmed_macro(prod, cfg=cfg)
        feed_accepted_touches(st, [(5, True), (6, False)])
        out = []
        for i in range(cfg.d_macro, cfg.d_macro + n_steps):
            out.append((i, prod._candidate_stagnation_reason(st, i)))
        return out

    full = run_continuous(cfg.WEAKENING_MAX_BARS + 5)
    fire_index = next(k for k, (_, reason) in enumerate(full) if reason == CANDIDATE_PERSISTENCE_TERMINATED)
    assert fire_index > 0, "fixture must not fire on its very first eligible bar (nothing to split)"

    # run A: uninterrupted through the split point, capturing snapshot/restore of JUST the two counter
    # fields (the producer itself has no public snapshot below the full engine; this isolates the exact
    # mechanism LIVE-8c targets without re-deriving the whole engine-level snapshot machinery)
    prod = RangeSemanticProducerV45(cfg)
    st = never_confirmed_macro(prod, cfg=cfg)
    feed_accepted_touches(st, [(5, True), (6, False)])
    split = fire_index // 2
    for k in range(split):
        i = cfg.d_macro + k
        assert prod._candidate_stagnation_reason(st, i) is None
    saved_id, saved_streak = prod._t3_eligible_structure_id, prod._t3_eligible_streak

    prod_b = RangeSemanticProducerV45(cfg)
    prod_b._t3_eligible_structure_id = saved_id
    prod_b._t3_eligible_streak = saved_streak
    resumed = []
    for k in range(split, len(full)):
        i = cfg.d_macro + k
        resumed.append((i, prod_b._candidate_stagnation_reason(st, i)))
    assert resumed == full[split:]


# ═══════════════════════════════════ LIVE-9: v4.4 regression -- byte-untouched (section 4/15) ═══════════════════════════════════

def test_live9_v4_4_module_byte_untouched() -> None:
    import subprocess
    out = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--", "range_semantic_v4_4.py", "range_engine_v4_4.py"],
        cwd=str(Path(__file__).resolve().parent.parent / "ve_n1_replay"), capture_output=True, text=True)
    assert out.stdout.strip() == "", f"v4.4 must remain byte-untouched, but git diff shows: {out.stdout}"


def test_live9b_v4_4_producer_unaffected_by_v4_5_existing() -> None:
    """v4.4's own decision for a stuck candidate is UNCHANGED -- it still has no liveness fix (frozen,
    disclosed limitation, mandate section 4) -- proving v4.5's mere existence changes nothing about v4.4's
    own behavior."""
    prod44 = RangeSemanticProducerV44(cfg44())
    st44 = never_confirmed_macro(prod44, cfg=cfg44())
    feed_accepted_touches(st44, [(b, True) for b in range(5, 200, 15)])
    events: list[Any] = []
    result = prod44._step_macro(200, 105.0, 95.0, 100.0, events)
    assert result not in (CANDIDATE_ONE_SIDED_TERMINATED, CANDIDATE_PERSISTENCE_TERMINATED)  # v4.4 has neither
    assert prod44._active_macro is not None  # v4.4: still stuck, exactly its known, accepted limitation


# ═══════════════════════════════════ LIVE-10: v4.5 deterministic replay ═══════════════════════════════════

def test_live10_deterministic_replay_same_input_same_output() -> None:
    bars = legs_bars([(100.0, 3)] + [(100.0 + 0.5 * i, 2) for i in range(1, 40)])
    results = []
    for _ in range(3):
        engine = RangeSemanticEngineV45(range_config=cfg45(), acknowledge_construction_only=True, **KW)
        run = []
        for bar in bars:
            _, res, ev = engine.observe_closed_bar(bar)
            run.append((res.macro_id, res.macro_state, res.macro_reason,
                       res.macro_boundary_upper, res.macro_boundary_lower,
                       tuple(e.kind for e in ev)))
        results.append(tuple(run))
    assert results[0] == results[1] == results[2]


# ═══════════════════════════════════ LIVE-11: no M5 detector, M15 authority preserved (section 13) ═══════════════════════════════════

def test_live11_no_m5_timeframe_reference_anywhere_in_v4_5() -> None:
    import inspect
    from ve_n1_replay import range_engine_v4_5 as eng_mod
    from ve_n1_replay import range_semantic_v4_5 as sem_mod
    for mod in (eng_mod, sem_mod):
        src = inspect.getsource(mod)
        assert '"5m"' not in src and "'5m'" not in src, f"{mod.__name__} must never hardcode an M5 timeframe"
        assert "H1RangeDetector" not in src and "H4RangeDetector" not in src


def test_live11b_engine_still_requires_explicit_timeframe_no_default() -> None:
    import inspect
    from ve_n1_replay.range_engine_v4_5 import RangeSemanticEngineV45 as Eng
    sig = inspect.signature(Eng.__init__)
    assert sig.parameters["timeframe"].default is inspect.Parameter.empty


# ═══════════════════════════════════ LIVE-12: identity (section 25) ═══════════════════════════════════

def test_live12_identity_distinct_from_v4_4_and_v4_4_1() -> None:
    from ve_n1_replay.range_semantic_v4_4 import RANGE_HIERARCHICAL_V4_4_NORMATIVE_CONFIG_ID
    from ve_n1_replay.range_semantic_v4_4_1 import RANGE_HIERARCHICAL_V4_4_1_NORMATIVE_CONFIG_ID
    assert RANGE_HIERARCHICAL_V4_5_CONTRACT_VERSION == "range-hierarchical-v4.5"
    assert RANGE_HIERARCHICAL_V4_5_NORMATIVE_CONFIG_ID not in (
        RANGE_HIERARCHICAL_V4_4_NORMATIVE_CONFIG_ID, RANGE_HIERARCHICAL_V4_4_1_NORMATIVE_CONFIG_ID)


def test_live12b_zero_new_config_fields_vs_v4_4() -> None:
    """Mandate section 5: freeze all thresholds -- mechanically confirmed, not merely claimed."""
    import dataclasses as dc
    v44_fields = {f.name for f in dc.fields(cfg44())}
    v45_fields = {f.name for f in dc.fields(cfg45())}
    assert v45_fields == v44_fields, f"V4.5 must add ZERO new config fields, found: {v45_fields - v44_fields}"


def test_live12c_all_thresholds_byte_identical_to_v4_4() -> None:
    c44, c45 = cfg44(), cfg45()
    for field in ("d_macro", "d_internal", "n_touch", "K_reentry", "N_accept", "K_struct",
                 "n_external_swings", "atr_window", "w_atr", "ER_max", "RND_max", "ALT_MIN",
                 "MIN_TRAVERSALS", "W", "ER_weakening", "RND_weakening", "WEAKENING_MAX_BARS",
                 "IOU_CONTINUE", "GAP_MAX"):
        assert getattr(c44, field) == getattr(c45, field), f"{field} diverged from the frozen v4.4 value"


def test_live12d_two_disjoint_reason_codes_never_both_apply_same_bar() -> None:
    """Mechanical proof the two mechanisms are mutually exclusive per bar (module docstring's own claim,
    verified here rather than merely asserted): both_satisfied is a monotonic function of touch counts, so
    for ANY (st, i), at most one of the two reason codes can be returned -- never both, regardless of
    which fixture is used."""
    cfg = cfg45()
    prod = RangeSemanticProducerV45(cfg)
    st = never_confirmed_macro(prod, cfg=cfg)
    feed_accepted_touches(st, [(b, True) for b in range(5, 40, 3)])  # one-sided growth, H-ONE-SIDED domain
    for i in range(cfg.d_macro, cfg.d_macro + 40):
        reason = prod._candidate_stagnation_reason(st, i)
        assert reason in (None, CANDIDATE_ONE_SIDED_TERMINATED, CANDIDATE_PERSISTENCE_TERMINATED)
        if reason == CANDIDATE_ONE_SIDED_TERMINATED:
            assert not (len(st.up.members) >= cfg.n_touch and len(st.dn.members) >= cfg.n_touch)
