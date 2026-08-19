"""Teste DECISIVE — RANGE SEMANTIC V3 (0.4.0), redesign LONGITUDINAL (mandat §§3-11).

Sursă normativă: Statistician STAT-RANGE-SEMANTIC-SPEC-V3-v1.0 @bf9f780 (manifest v2.7.84 @db098ed,
fingerprint cddaab38…). Lotul `RANGE_HUMAN_LABEL_BATCH_01` e CEO_ASSISTED, construction-only PERMANENT — NU
accesează ferestrele reale (intervalele exacte sunt deliberat NEPUBLICATE, în afara oricărui checkout git).
HBL-20 (§8.4) e reprodus NUMERIC EXACT dintr-un fixture sintetic construit din verificarea proprie, deja
publicată, a Statisticianului (breach bara 52, reintrare/confirmare bara 56, markup bara 63) — construction-
only, NU blind, NU un test de profitabilitate.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import (
    RangeConfigV3, RangeSemanticProducerV3, SegmentEventKindV3, SegmentLifecycleV3,
    ConfirmedSegmentRecordV3, entry_decision_v3, SAFETY_GUARD_RANGE_MID_NO_ENTRY, REASON_CODES_V3,
    ConfigNotRatifiedError, RangeSemanticContractErrorV3,
    RangeSemanticEngineV3, RangeSnapshotErrorV3, N1IncrementalReplayEngine,
    RangeStateReplayEngine as V1Engine, RangeConfig as V1Config,
    RangeStateReplayEngineV2 as V2Engine, RangeConfigV2 as V2Config,
    RangeStateReplayEngineV2Pinned as V2PinnedEngine, RangeConfigV2Pinned as V2PinnedConfig,
)
from ve_n1_replay.range_semantic_v3 import (
    _Segment, _Swing, TOO_SHORT, RANGE_FORMING, OK_RANGE, ZONES_DEGENERATE, IS_CHANNEL,
    SWEEP_WINDOW_EXPIRED, RANGE_FAILED_PRECONDITION, TERMINATED_BY_BREAKOUT, ESTABLISHING_FEW_SWINGS,
    ATR_UNAVAILABLE, BETWEEN_SEGMENTS, FEW_TOUCHES,
)
from tests import _fixtures as fx

Bar = r.Bar
KW = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)
from ve_n1_replay import range_semantic_v3 as _rsv3_mod
_MODULE_DIR = Path(_rsv3_mod.__file__).resolve().parent


def mk(i, o, h, l, c):
    return Bar(symbol="XAUUSD", ts_open=i * 900, ts_close=(i + 1) * 900,
              open=float(o), high=float(h), low=float(l), close=float(c), volume=100.0)


def cfg(**kw):
    base = dict(K=3, N=6, w_atr=0.35, acknowledge_construction_only=True,
               d_min_bars=20, atr_window=14, n_touch=2, swing_k=2)
    base.update(kw)
    return RangeConfigV3(**base)


def run_engine(bars, config=None):
    eng = RangeSemanticEngineV3(range_config=config or cfg(), **KW)
    out = [eng.observe_closed_bar(b) for b in bars]
    return eng, out


def all_events(out):
    evs = []
    for _, _, es in out:
        evs.extend(es)
    return evs


def kinds(out):
    return {e.kind for e in all_events(out)}


def _fps(out):
    return [(n1.output_fingerprint, rng.available, rng.lifecycle, rng.segment_id, rng.anchor_upper,
            rng.anchor_lower, rng.confirm_ts, rng.pending_event, tuple(e.kind for e in evs))
           for n1, rng, evs in out]


def osc_bars(cycles=14, base=2400.0, start=0, hi=None, lo=None):
    """Triunghi 8-bare cu vârf/minim EXPLICIT setat pe meșă — reutilizat identic din 0.3.1 (nu re-inventat,
    deja verificat că NU aliasează prost față de fereastra OLS de pantă trailing)."""
    hi = base + 20 if hi is None else hi
    lo = base - 20 if lo is None else lo
    bars = []; i = start
    for _ in range(cycles):
        for ph, cl in [(0, base + 8), (1, base + 16), (2, base + 18), (3, base + 12),
                       (4, base - 4), (5, base - 16), (6, base - 18), (7, base - 8)]:
            c = cl; o = c - 1; h = c + 3; l = c - 3
            if ph == 2: h = hi
            if ph == 6: l = lo
            bars.append(mk(i, o, h, l, c)); i += 1
    return bars


def _established_prefix(cycles=8, cfg_obj=None):
    bars = osc_bars(cycles=cycles)
    eng, out = run_engine(bars, cfg_obj)
    established = [rng for _, rng, _ in out if rng.available and rng.lifecycle == "ESTABLISHED"]
    assert established, "fixture-ul nu a stabilit niciun range -- verifică parametrii"
    last = established[-1]
    return bars, eng, out, last.anchor_upper, last.anchor_lower


# ═══════════════════════ 1: configurație UNRATIFICATĂ -- refuz fail-closed ═══════════════════════
def test_construction_refused_without_acknowledgement():
    with pytest.raises(ConfigNotRatifiedError):
        RangeConfigV3(K=3, N=6, w_atr=0.35)
    with pytest.raises(ConfigNotRatifiedError):
        RangeConfigV3(K=3, N=6, w_atr=0.35, acknowledge_construction_only=False)
    RangeConfigV3(K=3, N=6, w_atr=0.35, acknowledge_construction_only=True)   # trece


def test_K_N_w_atr_are_required_no_hidden_default():
    """Dovadă STRUCTURALĂ (nu textuală) -- semnătura reală a `__init__` NU are default pt. K/N/w_atr."""
    sig = inspect.signature(RangeConfigV3.__init__)
    for name in ("K", "N", "w_atr"):
        assert sig.parameters[name].default is inspect.Parameter.empty, (
            f"{name} NU trebuie să aibă default ascuns -- e NEIDENTIFICAT, cerut explicit")
    with pytest.raises(TypeError):
        RangeConfigV3(N=6, w_atr=0.35, acknowledge_construction_only=True)   # type: ignore[call-arg]
    with pytest.raises(TypeError):
        RangeConfigV3(K=3, w_atr=0.35, acknowledge_construction_only=True)   # type: ignore[call-arg]
    with pytest.raises(TypeError):
        RangeConfigV3(K=3, N=6, acknowledge_construction_only=True)   # type: ignore[call-arg]


def test_no_anchor_window_parameter_exists():
    """D1 e închis STRUCTURAL -- ancora nu mai are NICIUN parametru numeric de fereastră (512 sau altul).
    Nu există câmp `range_window`/`anchor_window`/`window` în contractul de configurație."""
    fields = {f for f in RangeConfigV3.__dataclass_fields__}
    forbidden = {"range_window", "anchor_window", "window", "anchor_window_bars"}
    assert not (fields & forbidden), f"parametru de fereastră a ancorei reapărut: {fields & forbidden}"


def test_K_greater_than_N_refused():
    """K>N ar face fereastra de reintrare K structural inaccesibilă (segmentul ar muri deja prin breakout
    la bara N<=K) -- exact clasa de defect 'parametru neutilizabil prin construcție'."""
    with pytest.raises(RangeSemanticContractErrorV3):
        cfg(K=7, N=3)
    cfg(K=3, N=7)    # K<=N trece
    cfg(K=5, N=5)    # K==N trece (degenerat -- SWEEP_WINDOW_EXPIRED devine inaccesibil, dar valid)


def test_K_N_w_atr_must_be_positive():
    with pytest.raises(RangeSemanticContractErrorV3):
        cfg(K=0, N=3)
    with pytest.raises(RangeSemanticContractErrorV3):
        cfg(K=3, N=0)
    with pytest.raises(RangeSemanticContractErrorV3):
        cfg(w_atr=0.0)
    with pytest.raises(RangeSemanticContractErrorV3):
        cfg(w_atr=-0.1)


def test_provenance_reports_neidentificat_status():
    prov = cfg().provenance()
    for key in ("K_status", "N_status", "w_atr_status"):
        assert "NEIDENTIFICAT" in prov[key], f"{key} trebuie să declare explicit NEIDENTIFICAT: {prov[key]}"
    assert prov["provenance"] == "CEO_ASSISTED"
    assert prov["statistician_spec_commit"] == "bf9f780"
    assert prov["statistician_manifest_commit"] == "db098ed"
    assert prov["statistician_manifest_fingerprint"] == (
        "cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233")


def test_config_fingerprint_changes_with_K_N_w_atr():
    base = cfg().range_spec_id()
    assert cfg(K=4).range_spec_id() != base
    assert cfg(N=8).range_spec_id() != base
    assert cfg(w_atr=0.30).range_spec_id() != base
    assert cfg().range_spec_id() == base   # determinist -- aceiași parametri => același id


def test_derived_s_max_follows_w_atr_not_carried_from_0_3_1():
    """w_atr NU se transportă din 0.3.1 (0,30 sub ancora VECHE) -- aici e complet liber, cerut explicit."""
    c = cfg(w_atr=0.10)
    assert c.s_max == pytest.approx(0.20)
    c2 = cfg(w_atr=0.47)
    assert c2.s_max == pytest.approx(0.94)


# ═══════════════════════ 2: geometrie -- ZONES_DEGENERATE structural imposibilă ca validă (D2) ═══════════════════════
def test_zones_degenerate_inverted_anchors():
    seg = _Segment(segment_id=1, predecessor_id=None, transition_reason=None, config=cfg())
    seg.anchor_upper, seg.anchor_lower = 100.0, 105.0
    assert not seg.geometry_valid(0.1)


def test_zones_degenerate_width_too_small():
    seg = _Segment(segment_id=1, predecessor_id=None, transition_reason=None, config=cfg())
    seg.anchor_upper, seg.anchor_lower = 105.0, 100.0
    assert not seg.geometry_valid(3.0)   # width=5 <= 2*w=6
    assert seg.geometry_valid(2.49)      # width=5 > 2*w=4.98


def test_zones_degenerate_nan_inf():
    seg = _Segment(segment_id=1, predecessor_id=None, transition_reason=None, config=cfg())
    for bad in (float('nan'), float('inf'), float('-inf')):
        seg.anchor_upper, seg.anchor_lower = bad, 100.0
        assert not seg.geometry_valid(1.0)
        seg.anchor_upper, seg.anchor_lower = 110.0, bad
        assert not seg.geometry_valid(1.0)


def test_geometry_gates_establishment():
    """Un segment cu geometrie degenerată nu poate NICIODATĂ ajunge ESTABLISHED, indiferent de touches/durată."""
    c = cfg(d_min_bars=5, n_touch=1)
    prod = RangeSemanticProducerV3(c)
    seg = _Segment(segment_id=1, predecessor_id=None, transition_reason=None, config=c)
    seg.add_swing(_Swing(idx=0, price=100.0, is_high=False, ts=0))
    seg.add_swing(_Swing(idx=1, price=100.05, is_high=True, ts=1))   # lățime aproape zero
    seg.update_anchors()
    seg.touches_upper = 5; seg.touches_lower = 5
    for i in range(10):
        seg.closes.append(100.0)
        ev = []
        prod._confirm_establish(seg, i, 1000 + i, c.w_atr * 1.0, ev)
    assert seg.lifecycle != SegmentLifecycleV3.ESTABLISHED


# ═══════════════════════ 3: durata reală -- TOO_SHORT demonstrabil reachable (D3) ═══════════════════════
def test_too_short_boundary_d_min_minus_1_exact_d_min_plus_1():
    c = cfg(d_min_bars=20)
    prod = RangeSemanticProducerV3(c)
    seg = _Segment(segment_id=1, predecessor_id=None, transition_reason=None, config=c)
    seg.add_swing(_Swing(idx=0, price=100.0, is_high=False, ts=1000))
    seg.add_swing(_Swing(idx=1, price=110.0, is_high=True, ts=1001))
    seg.update_anchors()
    seg.touches_upper = 2; seg.touches_lower = 2
    w = c.w_atr * 1.0
    for i in range(19):   # bars_in_segment(18) == 19 < 20
        seg.closes.append(105.0)
        ev = []
        prod._confirm_establish(seg, i, 2000 + i, w, ev)
    assert seg.lifecycle != SegmentLifecycleV3.ESTABLISHED
    assert TOO_SHORT in prod._reasons_for(seg, 18, w)          # d_min - 1: refuză
    seg.closes.append(105.0)
    ev = []
    prod._confirm_establish(seg, 19, 2019, w, ev)              # bars_in_segment(19) == 20 == d_min
    assert seg.lifecycle == SegmentLifecycleV3.ESTABLISHED
    assert any(e.kind == SegmentEventKindV3.RANGE_ESTABLISHED.value for e in ev)
    assert TOO_SHORT not in prod._reasons_for(seg, 19, w)      # d_min: trece
    seg.closes.append(105.0)
    ev = []
    prod._confirm_establish(seg, 20, 2020, w, ev)              # d_min + 1: rămâne ESTABLISHED
    assert seg.lifecycle == SegmentLifecycleV3.ESTABLISHED
    assert TOO_SHORT not in prod._reasons_for(seg, 20, w)


def test_too_short_never_saturates_D3_regression():
    """D3: `bars_in_state` sub 0.3.1 satura la ~508 -- aici durata crește NEMĂRGINIT din structural_start,
    fără plafon artificial (nu se auto-limitează niciodată la o valoare falsă)."""
    seg = _Segment(segment_id=1, predecessor_id=None, transition_reason=None, config=cfg())
    seg.structural_start_idx = 0
    for probe in (100, 1000, 10000, 100000):
        assert seg.bars_in_segment(probe - 1) == probe


def test_snapshot_restart_inside_warmup_too_short():
    """Snapshot/restart în plin TOO_SHORT (înainte de d_min) trebuie să continue identic."""
    c = cfg(d_min_bars=24)
    bars = osc_bars(cycles=3)   # prefix scurt, sub d_min
    ref, ref_out = run_engine(bars, c)
    eng = RangeSemanticEngineV3(range_config=c, **KW)
    for b in bars[:15]:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeSemanticEngineV3(range_config=c, **KW)
    eng2.restore(snap)
    out1 = [eng.observe_closed_bar(b) for b in bars[15:]]
    out2 = [eng2.observe_closed_bar(b) for b in bars[15:]]
    assert _fps(out1) == _fps(out2) == _fps(ref_out[15:])


# ═══════════════════════ 4: breach pe MEȘĂ, nu pe close -- wick-sweep dintr-o singură bară (D6/S3) ═══════════════════════
def _mkseg(c, sid=1):
    seg = _Segment(segment_id=sid, predecessor_id=None, transition_reason=None, config=c)
    seg.add_swing(_Swing(idx=0, price=100.0, is_high=False, ts=1000))
    seg.add_swing(_Swing(idx=1, price=110.0, is_high=True, ts=1001))
    seg.update_anchors()
    return seg


def test_same_bar_wick_breach_and_reclaim_is_a_sweep():
    c = cfg(K=5, N=5, w_atr=0.05)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 0, 9000, high=100.5, low=99.0, close=100.2, w=w, events=ev)
    assert SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value in [e.kind for e in ev]
    assert not seg.ended


def test_close_only_touch_without_wick_breach_is_not_a_breach():
    """O bară al cărei close+low/high rămân STRICT în interiorul zonei nu deschide deloc BREACH_PENDING."""
    c = cfg(w_atr=0.5)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 0, 9000, high=110.3, low=109.5, close=110.0, w=w, events=ev)
    assert seg.lifecycle != SegmentLifecycleV3.BREACH_PENDING
    assert SegmentEventKindV3.BOUNDARY_TEST_UPPER.value in [e.kind for e in ev]


# ═══════════════════════ 5: cursa sweep vs. breakout -- K mărginește reintrarea, N breakout-ul ═══════════════════════
def test_multi_bar_sweep_within_K_confirms_at_reentry_not_breach():
    c = cfg(K=5, N=5, w_atr=0.05)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 0, 9000, high=100.5, low=94.0, close=95.0, w=w, events=ev)
    assert seg.pending_consec_outside == 1
    ev = []
    prod._resolve_pending(seg, 1, 9001, high=96.0, low=94.5, close=95.5, events=ev)
    assert seg.pending_consec_outside == 2
    assert not any('SWEEP' in e.kind or 'BREAKOUT' in e.kind for e in ev)
    ev = []
    prod._resolve_pending(seg, 2, 9002, high=101.0, low=95.0, close=100.3, events=ev)   # bars_pending=3<=K=5
    kinds_ = [e.kind for e in ev]
    assert SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value in kinds_
    sweep = [e for e in ev if e.kind == SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value][0]
    assert sweep.confirm_ts == 9002
    assert sweep.confirm_ts != 9000
    assert not seg.ended


def test_sweep_window_expired_real_reentry_too_late():
    """Reintrare REALĂ (close revine în interior) dar cu bars_pending>K și N încă neatins -- nici sweep,
    nici breakout. Reproduce exact ambiguitatea descrisă în spec: 'informația nu există încă'."""
    c = cfg(K=2, N=6, w_atr=0.05)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 0, 9000, high=100.5, low=94.0, close=95.0, w=w, events=ev)
    for i, ts in [(1, 9001), (2, 9002)]:
        ev = []
        prod._resolve_pending(seg, i, ts, high=96.0, low=94.5, close=95.5, events=ev)
    ev = []
    prod._resolve_pending(seg, 3, 9003, high=101.0, low=95.0, close=100.3, events=ev)   # bars_pending=4>K=2
    kinds_ = [e.kind for e in ev]
    assert SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value not in kinds_
    assert not any('BREAKOUT' in k for k in kinds_)
    assert any(SWEEP_WINDOW_EXPIRED in e.reason_codes for e in ev)
    assert not seg.ended
    assert seg.lifecycle in (SegmentLifecycleV3.ESTABLISHING, SegmentLifecycleV3.ESTABLISHED)


def test_breakout_fires_at_Nth_consecutive_outside_close():
    c = cfg(K=2, N=3, w_atr=0.05)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 0, 9000, high=112.0, low=109.0, close=111.0, w=w, events=ev)
    ev = []
    prod._resolve_pending(seg, 1, 9001, high=113.0, low=111.0, close=112.0, events=ev)
    assert not any('BREAKOUT' in e.kind for e in ev)
    ev = []
    prod._resolve_pending(seg, 2, 9002, high=114.0, low=112.0, close=113.0, events=ev)   # bars_pending=3=N
    assert SegmentEventKindV3.BREAKOUT_ACCEPTANCE_UP.value in [e.kind for e in ev]
    assert seg.ended
    assert seg.end_reason == TERMINATED_BY_BREAKOUT


@pytest.mark.parametrize("K,N", [(1, 1), (1, 5), (4, 4), (2, 8)])
def test_K_N_boundary_combinations_do_not_crash(K, N):
    c = cfg(K=K, N=N, w_atr=0.1)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 0, 9000, high=100.5, low=94.0, close=95.0, w=w, events=ev)
    for i in range(1, N + 2):
        if seg.ended or seg.lifecycle != SegmentLifecycleV3.BREACH_PENDING:
            break
        ev = []
        prod._resolve_pending(seg, i, 9000 + i, high=96.0, low=94.5, close=95.5, events=ev)


# ═══════════════════════ 6: HBL-20 reproducere numerică exactă (construction-only) ═══════════════════════
def _hbl20_bars():
    """Fixture sintetic construit din verificarea PROPRIE, deja publicată, a Statisticianului (nu ferestrele
    reale, ale căror intervale exacte sunt deliberat nepublicate în afara oricărui checkout git).
    Ancoră EXACTĂ 3333.06/3346.10 (fiecare swing atinge exact aceste niveluri -- mediana devine exactă)."""
    ACC_HIGH, ACC_LOW = 3346.10, 3333.06
    T0 = 1_755_248_400
    bars = []

    def add(idx, o, h, l, c):
        bars.append(mk(idx, o, h, l, c))

    for cyc in range(4):
        base = cyc * 8
        pts = {0: (3336.0, 3337.0, 3335.0, 3336.5), 1: (3336.5, 3341.0, 3336.0, 3340.5),
              2: (3340.5, ACC_HIGH, 3339.0, 3344.0), 3: (3344.0, 3344.5, 3339.5, 3339.8),
              4: (3339.8, 3340.0, 3335.0, 3336.0), 5: (3336.0, 3337.0, ACC_LOW, 3334.0),
              6: (3334.0, 3337.5, 3333.5, 3337.0), 7: (3337.0, 3339.0, 3336.5, 3338.5)}
        for off, (o, h, l, c) in pts.items():
            add(base + off, o, h, l, c)
    assert len(bars) == 32
    for i in range(20):   # bars 32-51: rămân strict în interior
        mid = 3339.5
        add(32 + i, mid, mid + 2.0, mid - 2.0, mid + (0.3 if i % 2 == 0 else -0.3))
    assert len(bars) == 52
    add(52, 3333.0, 3333.5, 3330.25, 3331.50)          # breach pe LOW (3330.25 < 3333.06)
    add(53, 3331.5, 3332.0, 3329.0, 3330.80)
    add(54, 3330.8, 3332.5, 3330.0, 3332.10)
    add(55, 3332.1, 3333.0, 3331.5, 3332.90)
    add(56, 3332.9, 3335.2, 3332.5, 3334.94)           # reintrare: close 3334.94 > 3333.06
    assert len(bars) == 57
    for i in range(6):   # bars 57-62: rămân sub ACC_HIGH
        p = 3336.0 + i * 1.0
        add(57 + i, p, p + 2.5, p - 1.0, p + 0.5)
    assert len(bars) == 63
    add(63, 3345.5, 3347.5, 3345.0, 3346.99)           # markup: primul close peste 3346.10
    for i, p in enumerate([3348.0, 3350.5, 3353.0, 3355.5, 3357.0, 3358.49, 3357.8]):
        add(64 + i, p - 1.0, p + 1.0, p - 1.5, p)
    return bars, ACC_HIGH, ACC_LOW, T0


def test_hbl20_exact_reproduction_sweep_confirms_at_reentry_not_breach():
    bars, ACC_HIGH, ACC_LOW, _ = _hbl20_bars()
    c = cfg(K=5, N=5, w_atr=0.02, d_min_bars=96, duration_class="MULTIDAY_RANGE")
    prod = RangeSemanticProducerV3(c)
    log = []
    for idx, b in enumerate(bars):
        res, evs = prod.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close,
                                atr=3.0, trend_context=None)
        for e in evs:
            log.append((idx, e))

    breach_bar_events = [(i, e) for i, e in log if i == 52]
    assert breach_bar_events, "bara 52 (breach) trebuie să emită un eveniment"
    assert all(e.kind != SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value for i, e in breach_bar_events), (
        "sweep NU trebuie confirmat pe bara breach-ului (52) -- pe bara 52 informația 'e sweep' nu există încă")
    for bar_idx in (52, 53, 54, 55):
        assert all(e.kind not in (SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value,
                                  SegmentEventKindV3.BREAKOUT_ACCEPTANCE_UP.value,
                                  SegmentEventKindV3.BREAKOUT_ACCEPTANCE_DOWN.value)
                  for i, e in log if i == bar_idx), f"bara {bar_idx} trebuie să rămână ambiguă"

    sweep_events = [(i, e) for i, e in log if e.kind == SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value]
    assert len(sweep_events) == 1, f"exact un sweep așteptat, găsit {len(sweep_events)}"
    sweep_bar, sweep_ev = sweep_events[0]
    assert sweep_bar == 56, f"sweep-ul trebuie confirmat EXACT la bara 56, nu {sweep_bar}"
    assert sweep_ev.confirm_ts == bars[56].ts_close
    assert sweep_ev.confirm_ts != bars[52].ts_close, "confirm_ts NU trebuie să fie timestamp-ul breach-ului"

    # markup (bara 63): breach pe SUS trebuie deschis (ambiguu), NU confirmat imediat ca breakout
    bar63_events = [(i, e) for i, e in log if i == 63]
    assert bar63_events
    assert all(e.kind != SegmentEventKindV3.BREAKOUT_ACCEPTANCE_UP.value for i, e in bar63_events), (
        "o SINGURĂ închidere peste 3346.10 nu poate confirma singură breakout -- necesită N închideri consecutive")
    breakout_events = [(i, e) for i, e in log if e.kind == SegmentEventKindV3.BREAKOUT_ACCEPTANCE_UP.value]
    assert breakout_events and breakout_events[0][0] > 63, (
        "expansiunea/markup-ul trebuie să confirme eventual breakout, dar STRICT DUPĂ bara 63 (nu pe ea)")


# ═══════════════════════ 7: CHANNEL_UP/DOWN -- rădăcina D1×D4, NU un nou prag inventat ═══════════════════════
def test_channel_up_ends_segment_never_reaches_established():
    c = cfg(d_min_bars=20)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    for i in range(c.d_min_bars):
        seg.closes.append(100.0 + i * 2.0)
    ev = []
    prod._evaluate_active(seg, c.d_min_bars - 1, 5000, high=140, low=138, close=139, w=w, events=ev)
    assert SegmentEventKindV3.CHANNEL_UP.value in [e.kind for e in ev]
    assert seg.ended and seg.end_reason == IS_CHANNEL
    assert not seg.reached_established


def test_channel_down_symmetric():
    c = cfg(d_min_bars=20)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    for i in range(c.d_min_bars):
        seg.closes.append(200.0 - i * 2.0)
    ev = []
    prod._evaluate_active(seg, c.d_min_bars - 1, 5000, high=40, low=38, close=39, w=w, events=ev)
    assert SegmentEventKindV3.CHANNEL_DOWN.value in [e.kind for e in ev]
    assert seg.ended and seg.end_reason == IS_CHANNEL


def test_established_range_not_retroactively_reclassified_as_channel():
    """S2: acceptance != invalidation -- odată ESTABLISHED, drift-ul NU poate reclasifica retroactiv segmentul
    ca și canal (root cause D1xD4 -- fixat prin scara ancorei, nu prin re-verificare permanentă)."""
    c = cfg(d_min_bars=20)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    seg.lifecycle = SegmentLifecycleV3.ESTABLISHED
    seg.reached_established = True
    prod._active = seg
    w = c.w_atr * 1.0
    for i in range(c.d_min_bars):
        seg.closes.append(100.0 + i * 2.0)
    ev = []
    prod._evaluate_active(seg, c.d_min_bars - 1, 5000, high=105, low=104, close=104.5, w=w, events=ev)
    assert SegmentEventKindV3.CHANNEL_UP.value not in [e.kind for e in ev]
    assert not seg.ended


@pytest.mark.parametrize("drift", [0.15, 0.3, 0.5, 1.0])
def test_channel_up_never_range_established_organic(drift):
    bars = []; price = 2380.0
    for i in range(140):
        o = price; c = price + drift; h = max(o, c) + 2; l = min(o, c) - 2
        bars.append(mk(i, o, h, l, c)); price = c
    _, out = run_engine(bars, cfg(d_min_bars=24, K=2, N=6))
    assert not any(rng.available and rng.lifecycle == "ESTABLISHED" for _, rng, _ in out)


# ═══════════════════════ 8: segmentare longitudinală -- S1/S2 ═══════════════════════
def test_multi_regime_window_produces_a_sequence_of_segments():
    """O fereastră cu range -> breakout -> range NOU trebuie să producă segment_id-uri DISTINCTE, nu una
    singură pt. toată fereastra (S1: fără amestec automat de regimuri)."""
    bars = osc_bars(cycles=10)
    n = len(bars)
    price = 2440.0
    for i in range(30):   # rupere clară in sus, apoi range nou
        bars.append(mk(n + i, price, price + 3, price - 0.5, price + 2)); price += 2
    bars += osc_bars(cycles=6, base=price, start=len(bars))
    _, out = run_engine(bars, cfg(d_min_bars=20, K=2, N=4))
    seg_ids = sorted({rng.segment_id for _, rng, _ in out if rng.available and rng.segment_id is not None})
    assert len(seg_ids) >= 2, f"o fereastră multi-regim trebuie să producă >=2 segmente, a produs {seg_ids}"


def test_predecessor_chain_links_successive_segments():
    c = cfg(N=3, K=1, w_atr=0.05, d_min_bars=10)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    seg.touches_upper = 2; seg.touches_lower = 2
    prod._active = seg
    prod._next_segment_id = 2
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 0, 9000, high=112.0, low=109.0, close=111.0, w=w, events=ev)
    for i in range(1, 3):
        ev = []
        prod._resolve_pending(seg, i, 9000 + i, high=113.0, low=111.0, close=112.0, events=ev)
    assert seg.ended
    assert len(prod.history) == 1 and prod.history[0].segment_id == 1
    # bara următoare -- un segment nou trebuie creat, purtând predecessor_id = 1
    res, _ = prod.observe(ts_close=9100, open_=112.0, high=113.0, low=111.5, close=112.3, atr=1.0,
                          trend_context=None)
    assert res.predecessor_id == 1
    assert res.segment_id == 2
    assert res.transition_reason == TERMINATED_BY_BREAKOUT


def test_terminated_segment_survives_in_history_not_erased():
    """D4/S2: o rupere acceptată ÎNCHEIE segmentul, NU îl șterge -- rămâne în istoric ca range confirmat."""
    c = cfg(N=3, K=1, w_atr=0.05, d_min_bars=10)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    seg.touches_upper = 2; seg.touches_lower = 2
    seg.was_confirmed = True; seg.confirm_ts = 500; seg.structural_start_idx = 0
    seg.lifecycle = SegmentLifecycleV3.ESTABLISHED; seg.reached_established = True
    prod._active = seg
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 20, 9000, high=112.0, low=109.0, close=111.0, w=w, events=ev)
    for i in range(1, 3):
        ev = []
        prod._resolve_pending(seg, 20 + i, 9000 + i, high=113.0, low=111.0, close=112.0, events=ev)
    assert seg.ended
    hist = prod.history
    assert len(hist) == 1
    assert hist[0].reached_established is True
    assert hist[0].end_reason == TERMINATED_BY_BREAKOUT
    assert hist[0].segment_id == seg.segment_id


def test_no_swing_leak_across_segment_boundary():
    """Fereastra de swing-uri e golită la fiecare tranziție -- niciun swing dintr-un segment MORT nu poate
    fi atribuit succesorului (S1: fără amestec automat de regimuri)."""
    c = cfg(N=1, K=1, w_atr=0.05, d_min_bars=10, swing_k=2)
    prod = RangeSemanticProducerV3(c)
    seg = _mkseg(c)
    prod._active = seg
    w = c.w_atr * 1.0
    ev = []
    prod._evaluate_active(seg, 0, 9000, high=112.0, low=109.0, close=111.0, w=w, events=ev)   # N=1 -> breakout imediat
    assert seg.ended
    assert len(prod._wh) == 0 and len(prod._wl) == 0 and len(prod._wts) == 0, (
        "fereastra de swing-uri trebuie golită la _end_segment")


# ═══════════════════════ 9: F7 SAFETY_GUARD rămâne neschimbat semantic ═══════════════════════
def test_f7_explicit_refusal_zero_entry():
    bars = osc_bars(cycles=8)
    _, out = run_engine(bars, cfg(d_min_bars=10, K=2, N=6))
    mids = [e for e in all_events(out) if e.kind == SegmentEventKindV3.RANGE_MID.value]
    assert mids
    for e in mids:
        assert e.safety_guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
        d = entry_decision_v3(e)
        assert d.permitted is False and d.guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
    led = RangeSemanticEngineV3(range_config=cfg(d_min_bars=10, K=2, N=6), **KW).replay_batch(bars)
    assert led.n_guards > 0
    assert led.header()["safety_guards_register"] == ["RANGE_MID_NO_ENTRY"]


def test_entry_decision_permitted_for_non_range_mid_events():
    d = entry_decision_v3(None)
    assert d.permitted is True and d.guard is None


# ═══════════════════════ 10: toate cele 14 stări/evenimente reachable ═══════════════════════
def test_all_14_events_reachable():
    seen: set[str] = set()
    bars = osc_bars(cycles=14)
    seen |= kinds(run_engine(bars, cfg(d_min_bars=24, K=2, N=6))[1])
    loose = cfg(d_min_bars=24, w_atr=2.0, K=2, N=6)   # w_atr mare -> reachability, nu calibrare implicită
    seen |= kinds(run_engine(bars, loose)[1])

    c = cfg(d_min_bars=20)
    prod = RangeSemanticProducerV3(c)
    w = c.w_atr * 1.0
    # CHANNEL_UP / CHANNEL_DOWN
    for slope_sign, kind in [(1, SegmentEventKindV3.CHANNEL_UP), (-1, SegmentEventKindV3.CHANNEL_DOWN)]:
        seg = _mkseg(c, sid=100 + slope_sign)
        prod._active = seg
        for i in range(c.d_min_bars):
            seg.closes.append(150.0 + slope_sign * i * 2.0)
        ev = []
        prod._evaluate_active(seg, c.d_min_bars - 1, 6000, high=250, low=50, close=150, w=w, events=ev)
        seen |= {e.kind for e in ev}
    # RANGE_ESTABLISHED (boundary reachability, izolat de zgomotul motorului complet)
    seg_e = _mkseg(c, sid=200)
    seg_e.touches_upper = 2; seg_e.touches_lower = 2
    prod._active = seg_e
    for i in range(c.d_min_bars):
        seg_e.closes.append(105.0)
        ev = []
        prod._confirm_establish(seg_e, i, 7000 + i, w, ev)
        seen |= {e.kind for e in ev}
    # RANGE_FAILED via max_duration_bars
    c2 = cfg(d_min_bars=10, max_duration_bars=15, K=2, N=6)
    bars2 = []
    price = 2400.0
    for i in range(40):
        price += 0.3
        bars2.append(mk(i, price, price + 0.4, price - 0.4, price))
    seen |= kinds(run_engine(bars2, c2)[1])
    # UNAVAILABLE (warmup) + RANGE_FAILED (ATR loss mid-segment)
    prod3 = RangeSemanticProducerV3(cfg(d_min_bars=10, atr_window=5, K=2, N=6))
    res, evs = prod3.observe(ts_close=1000, open_=100, high=101, low=99, close=100, atr=None, trend_context=None)
    seen |= {e.kind for e in evs}
    x = 100.0
    for i in range(30):
        x += 0.5
        prod3.observe(ts_close=2000 + i * 900, open_=x, high=x + 0.4, low=x - 0.4, close=x, atr=1.0,
                      trend_context=None)
    _, evs2 = prod3.observe(ts_close=2000 + 30 * 900, open_=x, high=x + 0.4, low=x - 0.4, close=x,
                            atr=None, trend_context=None)
    seen |= {e.kind for e in evs2}
    # LIQUIDITY_SWEEP_UP/DOWN + BREAKOUT_ACCEPTANCE_UP/DOWN -- osc_bars() STAYS inside its own range by
    # design (that's the point of the fixture), so it never breaches; drive the race directly instead.
    c4 = cfg(K=5, N=5, w_atr=0.05)
    for side_sign in (1, -1):
        prod4 = RangeSemanticProducerV3(c4)
        seg = _mkseg(c4, sid=300 + side_sign)
        prod4._active = seg
        w4 = c4.w_atr * 1.0
        ev = []
        if side_sign > 0:
            prod4._evaluate_active(seg, 0, 8000, high=112.0, low=109.0, close=111.0, w=w4, events=ev)
        else:
            prod4._evaluate_active(seg, 0, 8000, high=100.5, low=94.0, close=95.0, w=w4, events=ev)
        seen |= {e.kind for e in ev}
        ev = []
        reentry = dict(high=101.0, low=95.0, close=100.3) if side_sign < 0 else dict(high=101.0, low=99.0, close=100.0)
        prod4._resolve_pending(seg, 1, 8001, **reentry, events=ev)   # bars_pending=2<=K=5 -> sweep
        seen |= {e.kind for e in ev}
    for side_sign in (1, -1):
        prod5 = RangeSemanticProducerV3(cfg(K=2, N=3, w_atr=0.05))
        seg = _mkseg(prod5._cfg, sid=400 + side_sign)
        prod5._active = seg
        w5 = prod5._cfg.w_atr * 1.0
        ev = []
        if side_sign > 0:
            prod5._evaluate_active(seg, 0, 8100, high=112.0, low=109.0, close=111.0, w=w5, events=ev)
            still_out = dict(high=113.0, low=111.0, close=112.0)
            more_out = dict(high=114.0, low=112.0, close=113.0)
        else:
            prod5._evaluate_active(seg, 0, 8100, high=100.5, low=94.0, close=95.0, w=w5, events=ev)
            still_out = dict(high=96.0, low=93.0, close=94.5)
            more_out = dict(high=95.0, low=91.0, close=92.0)
        ev = []
        prod5._resolve_pending(seg, 1, 8101, **still_out, events=ev)
        ev = []
        prod5._resolve_pending(seg, 2, 8102, **more_out, events=ev)   # bars_pending=3=N -> breakout
        seen |= {e.kind for e in ev}

    expected = {e.value for e in SegmentEventKindV3}
    missing = expected - seen
    assert not missing, f"evenimente NEreachable: {missing}"
    assert len(expected) == 14


def test_reason_codes_registry_matches_declared():
    used = {OK_RANGE, RANGE_FORMING, ESTABLISHING_FEW_SWINGS, ATR_UNAVAILABLE, FEW_TOUCHES, TOO_SHORT,
           IS_CHANNEL, ZONES_DEGENERATE, BETWEEN_SEGMENTS, TERMINATED_BY_BREAKOUT, RANGE_FAILED_PRECONDITION,
           SWEEP_WINDOW_EXPIRED}
    assert used <= set(REASON_CODES_V3)


# ═══════════════════════ 11: snapshot/restart bit-identic în orice stare ═══════════════════════
@pytest.mark.parametrize("chunks", [[112], [1, 111], [50, 62], [80, 20, 12], [95, 1, 16]])
def test_snapshot_restart_bit_identical(chunks):
    bars = osc_bars(cycles=14)
    assert sum(chunks) == len(bars)
    config = cfg(d_min_bars=10, K=2, N=6)
    ref, ref_out = run_engine(bars, config)
    got = []
    eng = RangeSemanticEngineV3(range_config=config, **KW)
    pos = 0
    for c in chunks:
        for b in bars[pos:pos + c]:
            got.append(eng.observe_closed_bar(b))
        snap = eng.snapshot()
        eng = RangeSemanticEngineV3(range_config=config, **KW)
        eng.restore(snap)
        pos += c
    assert _fps(got) == _fps(ref_out)


def test_snapshot_restart_inside_breach_pending():
    c = cfg(K=5, N=5, w_atr=0.05, d_min_bars=20, swing_k=2)
    bars, _, _, _ = _hbl20_bars()
    ref_eng = RangeSemanticEngineV3(range_config=c, **KW)
    ref_out = [ref_eng.observe_closed_bar(b) for b in bars[:63]]
    eng = RangeSemanticEngineV3(range_config=c, **KW)
    for b in bars[:53]:   # bara 52 (breach) deja procesată -> segmentul e in BREACH_PENDING
        eng.observe_closed_bar(b)
    assert eng.n1.bars_observed == 53
    snap = eng.snapshot()
    eng2 = RangeSemanticEngineV3(range_config=c, **KW)
    eng2.restore(snap)
    out2 = [eng2.observe_closed_bar(b) for b in bars[53:63]]
    out1 = [eng.observe_closed_bar(b) for b in bars[53:63]]
    assert _fps(out1) == _fps(out2)


def test_snapshot_restart_right_after_breakout_transition():
    # prefix OSCILLATING first -- monotonic data has no local extrema at all, so a fractal detector could
    # never confirm a single swing (highs/lows stay empty forever) and the breakout path would be unreachable.
    bars = osc_bars(cycles=3)   # 24 bars, established geometry with swing high~2420 / low~2380
    n = len(bars)
    price = 2422.0
    for i in range(5):   # decisive break above the swing high, sustained for several consecutive closes
        price += 5.0
        bars.append(mk(n + i, price, price + 2.0, price - 2.0, price))
    # d_min_bars must exceed the 24-bar prefix -- otherwise the channel-drift check (needs >= d_min_bars)
    # can fire mid-oscillation on trailing-window slope noise and kill the segment via CHANNEL_DOWN before
    # the breakout bars ever arrive, leaving nothing with geometry left to breach.
    c = cfg(N=3, K=1, w_atr=0.05, d_min_bars=30)
    ref_eng, ref_out = run_engine(bars, c)
    assert any(rng.transition_reason == TERMINATED_BY_BREAKOUT for _, rng, _ in ref_out if rng.available), (
        "fixture-ul trebuie să producă un breakout confirmat -- altfel testul nu verifică ce pretinde")
    eng = RangeSemanticEngineV3(range_config=c, **KW)
    for b in bars[:n]:   # oprire chiar înainte de mișcarea de breakout
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeSemanticEngineV3(range_config=c, **KW)
    eng2.restore(snap)
    out1 = [eng.observe_closed_bar(b) for b in bars[n:]]
    out2 = [eng2.observe_closed_bar(b) for b in bars[n:]]
    assert _fps(out1) == _fps(out2)
    assert any(rng.transition_reason == TERMINATED_BY_BREAKOUT for _, rng, _ in out1 if rng.available)


def test_legacy_0_2_0_snapshot_refused():
    bars = osc_bars(cycles=6)
    v1 = V1Engine(range_config=V1Config(), **KW)
    for b in bars:
        v1.observe_closed_bar(b)
    v1_snap = v1.snapshot()
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    with pytest.raises(RangeSnapshotErrorV3):
        eng.restore(v1_snap)


def test_legacy_0_3_0_snapshot_refused():
    bars = osc_bars(cycles=6)
    v2 = V2Engine(range_config=V2Config(w_atr=0.25, s_max=0.5, d_min_bars=24), **KW)
    for b in bars:
        v2.observe_closed_bar(b)
    v2_snap = v2.snapshot()
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    with pytest.raises(RangeSnapshotErrorV3):
        eng.restore(v2_snap)


def test_legacy_0_3_1_snapshot_refused():
    bars = osc_bars(cycles=6)
    v21 = V2PinnedEngine(range_config=V2PinnedConfig(d_min_bars=24), **KW)
    for b in bars:
        v21.observe_closed_bar(b)
    v21_snap = v21.snapshot()
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    with pytest.raises(RangeSnapshotErrorV3):
        eng.restore(v21_snap)


def test_corrupted_snapshot_refused_engine_left_unchanged():
    import dataclasses as _dc
    bars = osc_bars(cycles=6)
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    corrupted = _dc.replace(snap, range_state={"n": 5})
    before = eng.bars_observed
    with pytest.raises(RangeSnapshotErrorV3):
        eng.restore(corrupted)
    assert eng.bars_observed == before, "restore eșuat trebuie să lase motorul complet NESCHIMBAT (atomic)"


def test_config_mismatch_refused():
    bars = osc_bars(cycles=6)
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeSemanticEngineV3(range_config=cfg(w_atr=0.5), **KW)
    with pytest.raises(RangeSnapshotErrorV3):
        eng2.restore(snap)


def test_two_instances_no_shared_state():
    bars = osc_bars(cycles=10)
    config = cfg(d_min_bars=10, K=2, N=6)
    ref, ref_out = run_engine(bars, config)
    e1 = RangeSemanticEngineV3(range_config=config, **KW)
    e2 = RangeSemanticEngineV3(range_config=config, **KW)
    for b in bars[:30]:
        e1.observe_closed_bar(b)
    got2 = [e2.observe_closed_bar(b) for b in bars]
    assert _fps(got2) == _fps(ref_out)
    assert e1.bars_observed == 30 and e2.bars_observed == len(bars)


# ═══════════════════════ 12: cauzalitate / zero-lookahead ═══════════════════════
def test_zero_lookahead_prefix_parity():
    bars = osc_bars(cycles=10)
    _, out_full = run_engine(bars)
    _, out_prefix = run_engine(bars[:50])
    for i in range(50):
        assert _fps(out_full)[i] == _fps(out_prefix)[i]


@pytest.mark.parametrize("split", [1, 17, 40, 63, 90])
def test_full_replay_vs_variable_chunks_identical(split):
    bars = osc_bars(cycles=12)
    _, ref_out = run_engine(bars)
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    part1 = [eng.observe_closed_bar(b) for b in bars[:split]]
    part2 = [eng.observe_closed_bar(b) for b in bars[split:]]
    assert _fps(part1 + part2) == _fps(ref_out)


def test_same_history_different_future_identical_up_to_common_point():
    common = osc_bars(cycles=8)
    n = len(common)
    future_a = [mk(n + i, 2450 + i, 2452 + i, 2448 + i, 2451 + i) for i in range(10)]
    future_b = [mk(n + i, 2300 - i, 2302 - i, 2298 - i, 2301 - i) for i in range(10)]
    _, out_a = run_engine(common + future_a)
    _, out_b = run_engine(common + future_b)
    assert _fps(out_a)[:n] == _fps(out_b)[:n]


def test_future_bar_refused():
    """N1 (0.1.1, NEATINS) refuză bare din viitor -- proprietatea se moștenește prin compunere neschimbată."""
    from ve_n1_replay import FutureBarError
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    far_future = Bar(symbol="XAUUSD", ts_open=10**12, ts_close=10**12 + 900,
                     open=100.0, high=101.0, low=99.0, close=100.0, volume=100.0)
    with pytest.raises(FutureBarError):
        eng.observe_closed_bar(far_future, as_of=1000)


def test_out_of_order_bar_refused():
    from ve_n1_replay import OutOfOrderBarError
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    bars = osc_bars(cycles=3)
    for b in bars:
        eng.observe_closed_bar(b)
    with pytest.raises(OutOfOrderBarError):
        eng.observe_closed_bar(bars[0])


def test_identical_duplicate_bar_is_idempotent():
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    bars = osc_bars(cycles=3)
    for b in bars:
        eng.observe_closed_bar(b)
    last = bars[-1]
    r1 = eng.observe_closed_bar(last)
    r2 = eng.observe_closed_bar(last)
    # duplicat identic: N1 (neatins) e idempotent la fingerprint -- proprietate moștenită prin compunere
    assert r1[0].output_fingerprint == r2[0].output_fingerprint


def test_conflicting_duplicate_bar_refused():
    from ve_n1_replay import DuplicateBarError
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    bars = osc_bars(cycles=3)
    for b in bars:
        eng.observe_closed_bar(b)
    conflicting = mk(len(bars) - 1, 9999, 10000, 9998, 9999.5)   # același index, preț DIFERIT
    with pytest.raises(DuplicateBarError):
        eng.observe_closed_bar(conflicting)


def test_determinism():
    bars = osc_bars(cycles=10)
    _, out1 = run_engine(bars)
    _, out2 = run_engine(bars)
    assert _fps(out1) == _fps(out2)


# ═══════════════════════ 13: N1 0.1.1 byte-identic (NEATINS) ═══════════════════════
@pytest.mark.parametrize("gen", [fx.trend_up_regime_bars, fx.trend_down_regime_bars,
                                 lambda: fx.uncertain_regime_bars(n=150), osc_bars])
def test_n1_byte_identical_0_1_1(gen):
    bars = gen()
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    bare = N1IncrementalReplayEngine(**KW)
    for b in bars:
        n1, _, _ = eng.observe_closed_bar(b)
        assert n1.output_fingerprint == bare.observe_closed_bar(b).output_fingerprint


def test_uses_N1IncrementalReplayEngine_literal_class():
    eng = RangeSemanticEngineV3(range_config=cfg(), **KW)
    assert isinstance(eng.n1, N1IncrementalReplayEngine)
    assert type(eng.n1).__module__.endswith("incremental")


# ═══════════════════════ 14: interzise -- fără MT5/broker/order_send/set_authority/fallback ═══════════════════════
def test_no_forbidden_imports_in_source():
    for mod in (_rsv3_mod,):
        src = inspect.getsource(mod).lower()
        for forbidden in ("metatrader5", "import mt5", "mt5.", "order_send", "set_authority",
                          "probability_inputs", "broker"):
            assert forbidden not in src, f"import/termen interzis găsit: {forbidden!r}"
    import sys
    assert "MetaTrader5" not in sys.modules and "mt5" not in sys.modules


def test_ast_guard_no_hardcoded_numeric_default_for_K_N_anchor_window():
    """K/N nu au NICIUN literal numeric folosit ca default în semnătura clasei -- confirmă structural că
    singura sursă e argumentul explicit al apelantului."""
    src = (_MODULE_DIR / "range_semantic_v3.py").read_text(encoding="utf-8")
    tree = ast.parse(src, filename="range_semantic_v3.py")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RangeConfigV3":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    if item.target.id in ("K", "N", "w_atr"):
                        assert item.value is None, (
                            f"{item.target.id} NU trebuie să aibă un default literal în corpul clasei")


def test_range_producer_never_imports_ai_trader_runtime():
    src = inspect.getsource(_rsv3_mod)
    assert "import ai_trader" not in src
    assert "from ai_trader" not in src
    assert "ve_tower" not in src.lower()


# ═══════════════════════ 15: compatibilitate -- toate versiunile anterioare rămân neatinse ═══════════════════════
def test_v2_v2_1_producers_still_importable_unchanged():
    """0.2.0/0.3.0/0.3.1 rămân disponibile pt. audit/rollback -- V3 nu le reimplementează sau elimină."""
    import ve_n1_replay as pkg
    assert pkg.RangeStateProducer is not None
    assert pkg.RangeStateProducerV2 is not None
    assert pkg.RangeConfigV2Pinned is not None


def test_v3_does_not_reuse_or_reinterpret_v2_enums():
    from ve_n1_replay.range_state_v2 import MachineStateV2, RangeEventKindV2
    assert not set(SegmentEventKindV3).intersection(
        {getattr(RangeEventKindV2, m.name, None) for m in RangeEventKindV2})
    v3_values = {e.value for e in SegmentEventKindV3}
    v2_values = {e.value for e in RangeEventKindV2}
    # unele NUME pot coincide textual (RANGE_MID etc.) dar SegmentEventKindV3 e un tip Python DISTINCT
    assert SegmentEventKindV3 is not RangeEventKindV2
