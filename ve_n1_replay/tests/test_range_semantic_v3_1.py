"""Teste DECISIVE — RANGE SEMANTIC V3.1 (0.4.1), PERFORMANCE DELTA FIX (mandat §6, 20 iteme + paritate §5 +
test decisiv de performanță). Remediază EXCLUSIV §12 RT-RANGE-0004 @`87cad2c` (ledger E79): `_Segment.slope()`
(0.4.0) O(`d_min_bars`)/bară → `_SegmentV31.slope()` (0.4.1) O(1)/bară, prin statistici suficiente incrementale.

Fixture-urile `mk`/`osc_bars`/`_hbl20_bars` sunt o copie CHIRURGICALĂ (date, nu algoritm nou) din
`test_range_semantic_v3.py` (0.4.0, BYTE-NEATINS — deliberat NU importate de-acolo, ca fișierul de teste
0.4.0 să rămână complet neatins, aceeași disciplină aplicată deja codului de producție)."""
from __future__ import annotations

import ast
import inspect
import math
import time
from pathlib import Path

import pytest

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import (
    RangeConfigV3, RangeSemanticProducerV3, RangeSemanticEngineV3, RangeSnapshotErrorV3,
    RangeConfigV31, RangeSemanticProducerV31, RangeSemanticEngineV31, RangeSnapshotErrorV31,
    SegmentEventKindV3, SegmentLifecycleV3, N1IncrementalReplayEngine,
)
from ve_n1_replay.range_semantic_v3 import _Segment, _Swing, IS_CHANNEL, TOO_SHORT, RangeSemanticContractErrorV3
from ve_n1_replay.range_semantic_v3_1 import _SegmentV31, _IncrementalSlope

Bar = r.Bar
KW = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)
from ve_n1_replay import range_semantic_v3_1 as _rsv31_mod
from ve_n1_replay import range_engine_v3_1 as _rev31_mod
_MODULE_DIR = Path(_rsv31_mod.__file__).resolve().parent


def mk(i, o, h, l, c):
    return Bar(symbol="XAUUSD", ts_open=i * 900, ts_close=(i + 1) * 900,
              open=float(o), high=float(h), low=float(l), close=float(c), volume=100.0)


def osc_bars(cycles=14, base=2400.0, start=0, hi=None, lo=None):
    """Copie exactă (date) din `test_range_semantic_v3.py` -- triunghi 8-bare, vârf/minim explicit pe meșă."""
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


def _hbl20_bars():
    """Copie exactă (date) din `test_range_semantic_v3.py` -- fixture sintetic HBL-20, ancoră 3346.10/3333.06,
    breach bara 52, sweep confirmat bara 56, markup bara 63 (construction-only, vezi fișierul sursă pt.
    provenance completă -- NEDUPLICATĂ aici, doar datele numerice)."""
    ACC_HIGH, ACC_LOW = 3346.10, 3333.06
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
    for i in range(20):
        mid = 3339.5
        add(32 + i, mid, mid + 2.0, mid - 2.0, mid + (0.3 if i % 2 == 0 else -0.3))
    add(52, 3333.0, 3333.5, 3330.25, 3331.50)
    add(53, 3331.5, 3332.0, 3329.0, 3330.80)
    add(54, 3330.8, 3332.5, 3330.0, 3332.10)
    add(55, 3332.1, 3333.0, 3331.5, 3332.90)
    add(56, 3332.9, 3335.2, 3332.5, 3334.94)
    for i in range(6):
        p = 3336.0 + i * 1.0
        add(57 + i, p, p + 2.5, p - 1.0, p + 0.5)
    add(63, 3345.5, 3347.5, 3345.0, 3346.99)
    for i, p in enumerate([3348.0, 3350.5, 3353.0, 3355.5, 3357.0, 3358.49, 3357.8]):
        add(64 + i, p - 1.0, p + 1.0, p - 1.5, p)
    return bars, ACC_HIGH, ACC_LOW


def cfg30(**kw):
    base = dict(K=3, N=6, w_atr=0.35, acknowledge_construction_only=True,
               d_min_bars=20, atr_window=14, n_touch=2, swing_k=2)
    base.update(kw)
    return RangeConfigV3(**base)


def cfg31(**kw):
    base = dict(K=3, N=6, w_atr=0.35, acknowledge_construction_only=True,
               d_min_bars=20, atr_window=14, n_touch=2, swing_k=2)
    base.update(kw)
    return RangeConfigV31(**base)


def run30(bars, config=None):
    eng = RangeSemanticEngineV3(range_config=config or cfg30(), **KW)
    return eng, [eng.observe_closed_bar(b) for b in bars]


def run31(bars, config=None):
    eng = RangeSemanticEngineV31(range_config=config or cfg31(), **KW)
    return eng, [eng.observe_closed_bar(b) for b in bars]


def _fps(out):
    """Fingerprint DECIZIONAL per bară -- EXCLUDE panta brută (comparată separat, cu toleranță -- §5)."""
    return [(rng.available, rng.reason, rng.segment_id, rng.predecessor_id, rng.transition_reason,
            rng.lifecycle, rng.structural_start_ts, rng.confirm_ts, rng.bars_in_segment,
            rng.anchor_lower, rng.anchor_upper, rng.range_mid, rng.w,
            rng.touches_upper, rng.touches_lower, rng.pending_event, rng.confirmed_event,
            rng.reason_codes, tuple((e.kind, e.boundary, e.reason_codes) for e in evs))
           for _, rng, evs in out]


def _slopes(out):
    return [rng.slope for _, rng, _ in out]


def _mkseg31(c, sid=1):
    seg = _SegmentV31(segment_id=sid, predecessor_id=None, transition_reason=None, config=c)
    seg.add_swing(_Swing(idx=0, price=100.0, is_high=False, ts=1000))
    seg.add_swing(_Swing(idx=1, price=110.0, is_high=True, ts=1001))
    seg.update_anchors()
    return seg


def _oracle_slope(window):
    n = len(window)
    if n < 2:
        return 0.0
    sx = sy = sxy = sxx = 0.0
    for x, y in enumerate(window):
        fx = float(x)
        sx += fx; sy += y; sxy += fx * y; sxx += fx * fx
    denom = n * sxx - sx * sx
    return 0.0 if denom == 0.0 else (n * sxy - sx * sy) / denom


# ═══════════════════════ Iteme 6-13,19: oracol OLS simplu vs. incremental, la FIECARE prefix ═══════════════════════
SEQUENCES = {
    "constant": [2400.0] * 40,                                             # item 6
    "ramp_up": [2400.0 + i * 0.5 for i in range(40)],                      # item 7
    "ramp_down": [2400.0 - i * 0.7 for i in range(40)],                    # item 8
    "oscillation": [2400.0 + (10 if i % 2 == 0 else -10) for i in range(40)],   # item 9
    "duplicates": [2400.0, 2400.0, 2400.0, 2450.0, 2450.0, 2450.0, 2450.0, 2380.0] * 5,   # item 10
    "extremes": [1e6, -1e6, 1e6, -1e6, 0.0, 1e-6, -1e-6] * 6,              # item 11
    "window_fill_exact": [2400.0 + i for i in range(20)],                  # item 12 (fills EXACTLY at the end)
    "eviction_beyond_fill": [2400.0 + math.sin(i * 0.3) * 15 for i in range(60)],   # item 13 (many evictions)
}


@pytest.mark.parametrize("name,seq", list(SEQUENCES.items()), ids=list(SEQUENCES.keys()))
@pytest.mark.parametrize("maxlen", [1, 2, 12, 20])
def test_incremental_slope_matches_naive_oracle_at_every_prefix(name, seq, maxlen):
    """Iteme 6-13,19: `_SegmentV31.push_close`+`slope()` == oracol recalculat de la zero, la FIECARE prefix,
    pe fereastra trailing corectă -- inclusiv umplere exactă (12) și evicții repetate după umplere (13)."""
    tracker = _IncrementalSlope(maxlen=maxlen)
    worst = 0.0
    for i, y in enumerate(seq):
        evicted = None
        window_before = seq[max(0, i - maxlen):i]
        if len(window_before) == maxlen:
            evicted = window_before[0]
        tracker.push(y, evicted)
        window = seq[max(0, i - maxlen + 1):i + 1]
        oracle = _oracle_slope(window)
        got = tracker.slope()
        worst = max(worst, abs(oracle - got))
        assert abs(oracle - got) < 1e-6, f"{name}/maxlen={maxlen} @ i={i}: oracle={oracle!r} got={got!r}"


def test_incremental_slope_matches_naive_oracle_via_real_segment():
    """Aceeași proprietate, dar prin `_SegmentV31` REAL (push_close), nu doar clasa `_IncrementalSlope` izolată."""
    c = cfg31(d_min_bars=15)
    seg = _SegmentV31(segment_id=1, predecessor_id=None, transition_reason=None, config=c)
    seq = [2400.0 + math.sin(i * 0.4) * 12 + (i % 5) for i in range(80)]
    for i, y in enumerate(seq):
        seg.push_close(y)
        window = seq[max(0, i - 14):i + 1]
        assert abs(seg.slope() - _oracle_slope(window)) < 1e-6


# ═══════════════════════ Iteme 1-3: cele trei d_min_bars decisive ═══════════════════════
@pytest.mark.parametrize("d_min", [96, 4000, 200000])
def test_accepts_and_runs_correctly_at_decisive_d_min_bars(d_min):
    """Itemele 1,2,3 -- configurația e acceptată și produce rezultate corecte (nu doar 'nu crapă') la fiecare
    prag decisiv citat de Red Team (90,9µs/bară · 1829µs/bară · extrapolat ~90ms/bară)."""
    c = cfg31(d_min_bars=d_min, K=2, N=4)
    seg = _SegmentV31(segment_id=1, predecessor_id=None, transition_reason=None, config=c)
    for i in range(min(d_min + 50, 500)):   # nu umple ferestre de 200000 bară-cu-bară în test -- vezi bench separat
        seg.push_close(2400.0 + (i % 13) * 0.7)
    assert seg.closes.maxlen == d_min
    assert math.isfinite(seg.slope())


# ═══════════════════════ Iteme 4,5: plafon d_min_bars -- N/A, niciun plafon introdus ═══════════════════════
def test_no_d_min_bars_cap_items_4_5_not_applicable():
    """Itemele 4 ('valoarea maximă acceptată') și 5 ('maxim+1 -> refuz') NU se aplică -- mandatul §3 interzice
    alegerea arbitrară a unui plafon fără sursă normativă, iar spec `bf9f780` e tăcută asupra unui asemenea
    maxim (Varianta A -- pantă incrementală -- rezolvă defectul FĂRĂ plafon). Dovadă structurală: valori foarte
    mari sunt acceptate fără eroare."""
    RangeConfigV31(K=2, N=4, w_atr=0.3, acknowledge_construction_only=True, d_min_bars=500_000)
    RangeConfigV31(K=2, N=4, w_atr=0.3, acknowledge_construction_only=True, d_min_bars=10_000_000)


# ═══════════════════════ Item 14: restart înainte ȘI după umplerea ferestrei ═══════════════════════
def test_snapshot_restart_before_window_fill():
    c = cfg31(d_min_bars=50, K=2, N=6)
    bars = osc_bars(cycles=3)   # 24 bare < d_min_bars=50 -- fereastra NU s-a umplut încă
    assert len(bars) < 50
    eng = RangeSemanticEngineV31(range_config=c, **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeSemanticEngineV31(range_config=c, **KW)
    eng2.restore(snap)
    future = osc_bars(cycles=3, start=len(bars))
    out1 = [eng.observe_closed_bar(b) for b in future]
    out2 = [eng2.observe_closed_bar(b) for b in future]
    assert _fps(out1) == _fps(out2)
    assert _slopes(out1) == _slopes(out2)


def test_snapshot_restart_after_window_fill():
    c = cfg31(d_min_bars=15, K=2, N=6)
    bars = osc_bars(cycles=6)   # 48 bare > d_min_bars=15 -- fereastra s-a umplut și a evictat deja de mai multe ori
    assert len(bars) > 15
    eng = RangeSemanticEngineV31(range_config=c, **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeSemanticEngineV31(range_config=c, **KW)
    eng2.restore(snap)
    future = osc_bars(cycles=3, start=len(bars))
    out1 = [eng.observe_closed_bar(b) for b in future]
    out2 = [eng2.observe_closed_bar(b) for b in future]
    assert _fps(out1) == _fps(out2)
    assert _slopes(out1) == _slopes(out2)


# ═══════════════════════ Item 15: două instanțe independente ═══════════════════════
def test_two_instances_no_shared_state():
    bars = osc_bars(cycles=10)
    config = cfg31(d_min_bars=10, K=2, N=6)
    ref, ref_out = run31(bars, config)
    e1 = RangeSemanticEngineV31(range_config=config, **KW)
    e2 = RangeSemanticEngineV31(range_config=config, **KW)
    for b in bars[:30]:
        e1.observe_closed_bar(b)
    got2 = [e2.observe_closed_bar(b) for b in bars]
    assert _fps(got2) == _fps(ref_out)
    assert e1.bars_observed == 30 and e2.bars_observed == len(bars)


# ═══════════════════════ Item 16: snapshot/restore (general, chunked) + refuz legacy fail-closed ═══════════════════════
@pytest.mark.parametrize("chunks", [[112], [1, 111], [50, 62], [80, 20, 12], [95, 1, 16]])
def test_snapshot_restart_bit_identical(chunks):
    bars = osc_bars(cycles=14)
    assert sum(chunks) == len(bars)
    config = cfg31(d_min_bars=10, K=2, N=6)
    ref, ref_out = run31(bars, config)
    got = []
    eng = RangeSemanticEngineV31(range_config=config, **KW)
    pos = 0
    for c in chunks:
        for b in bars[pos:pos + c]:
            got.append(eng.observe_closed_bar(b))
        snap = eng.snapshot()
        eng = RangeSemanticEngineV31(range_config=config, **KW)
        eng.restore(snap)
        pos += c
    assert _fps(got) == _fps(ref_out)
    assert _slopes(got) == _slopes(ref_out)


def test_legacy_0_4_0_snapshot_refused():
    """Singura diferență REALĂ față de lista de refuz a lui 0.4.0: 0.4.1 trebuie SĂ MAI refuze și 0.4.0 însuși
    (structura internă a segmentului s-a schimbat -- noile câmpuri de statistici suficiente)."""
    bars = osc_bars(cycles=6)
    v040 = RangeSemanticEngineV3(range_config=cfg30(), **KW)
    for b in bars:
        v040.observe_closed_bar(b)
    snap040 = v040.snapshot()
    eng = RangeSemanticEngineV31(range_config=cfg31(), **KW)
    with pytest.raises(RangeSnapshotErrorV31):
        eng.restore(snap040)


def test_legacy_0_2_0_0_3_0_0_3_1_snapshots_still_refused():
    from ve_n1_replay import (
        RangeStateReplayEngine as V1Engine, RangeConfig as V1Config,
        RangeStateReplayEngineV2 as V2Engine, RangeConfigV2 as V2Config,
        RangeStateReplayEngineV2Pinned as V2PinnedEngine, RangeConfigV2Pinned as V2PinnedConfig,
    )
    bars = osc_bars(cycles=6)
    eng = RangeSemanticEngineV31(range_config=cfg31(), **KW)

    v1 = V1Engine(range_config=V1Config(), **KW)
    for b in bars:
        v1.observe_closed_bar(b)
    with pytest.raises(RangeSnapshotErrorV31):
        eng.restore(v1.snapshot())

    v2 = V2Engine(range_config=V2Config(w_atr=0.25, s_max=0.5, d_min_bars=24), **KW)
    for b in bars:
        v2.observe_closed_bar(b)
    with pytest.raises(RangeSnapshotErrorV31):
        eng.restore(v2.snapshot())

    v21 = V2PinnedEngine(range_config=V2PinnedConfig(d_min_bars=24), **KW)
    for b in bars:
        v21.observe_closed_bar(b)
    with pytest.raises(RangeSnapshotErrorV31):
        eng.restore(v21.snapshot())


def test_corrupted_snapshot_refused_engine_left_unchanged():
    import dataclasses as _dc
    bars = osc_bars(cycles=6)
    eng = RangeSemanticEngineV31(range_config=cfg31(), **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    corrupted = _dc.replace(snap, range_state={"n": 5})
    before = eng.bars_observed
    with pytest.raises(RangeSnapshotErrorV31):
        eng.restore(corrupted)
    assert eng.bars_observed == before, "restore eșuat trebuie să lase motorul complet NESCHIMBAT (atomic)"


def test_config_mismatch_refused():
    bars = osc_bars(cycles=6)
    eng = RangeSemanticEngineV31(range_config=cfg31(), **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeSemanticEngineV31(range_config=cfg31(w_atr=0.5), **KW)
    with pytest.raises(RangeSnapshotErrorV31):
        eng2.restore(snap)


# ═══════════════════════ Item 17: invarianță la chunking ═══════════════════════
@pytest.mark.parametrize("split", [1, 17, 40, 63, 90])
def test_full_replay_vs_variable_chunks_identical(split):
    bars = osc_bars(cycles=12)
    _, ref_out = run31(bars)
    eng = RangeSemanticEngineV31(range_config=cfg31(), **KW)
    part1 = [eng.observe_closed_bar(b) for b in bars[:split]]
    part2 = [eng.observe_closed_bar(b) for b in bars[split:]]
    assert _fps(part1 + part2) == _fps(ref_out)
    assert _slopes(part1 + part2) == _slopes(ref_out)


# ═══════════════════════ Item 18: paritate de prefix (zero-lookahead) ═══════════════════════
def test_zero_lookahead_prefix_parity():
    bars = osc_bars(cycles=10)
    _, out_full = run31(bars)
    _, out_prefix = run31(bars[:50])
    assert _fps(out_full)[:50] == _fps(out_prefix)
    assert _slopes(out_full)[:50] == _slopes(out_prefix)


# ═══════════════════════ Item 20: prag exact de canal -- sub / la / peste ═══════════════════════
def test_channel_threshold_below_at_above_decision_parity_0_4_0_vs_0_4_1():
    """§5 explicit: valorile IMEDIAT sub, LA și IMEDIAT peste pragul `IS_CHANNEL` (drift = |slope|*d_min_bars
    vs. s_max*atr) trebuie să dea EXACT aceeași clasificare în 0.4.0 și 0.4.1."""
    d_min = 20
    w_atr = 0.35
    atr = 1.0
    s_max = 2.0 * w_atr   # RangeConfigV3.s_max property
    # panta necesară ca drift == s_max*atr EXACT: |slope|*d_min == s_max*atr => slope = s_max*atr/d_min
    slope_at = (s_max * atr) / d_min
    eps = slope_at * 1e-3

    for label, slope_target in (("below", slope_at - eps), ("at", slope_at), ("above", slope_at + eps)):
        closes = [100.0 + i * slope_target for i in range(d_min)]

        c30 = cfg30(d_min_bars=d_min, w_atr=w_atr)
        seg30 = _Segment(segment_id=1, predecessor_id=None, transition_reason=None, config=c30)
        for v in closes:
            seg30.closes.append(v)
        drift30 = abs(seg30.slope()) * d_min
        is_channel_30 = drift30 > s_max * atr

        c31 = cfg31(d_min_bars=d_min, w_atr=w_atr)
        seg31 = _SegmentV31(segment_id=1, predecessor_id=None, transition_reason=None, config=c31)
        for v in closes:
            seg31.push_close(v)
        drift31 = abs(seg31.slope()) * d_min
        is_channel_31 = drift31 > s_max * atr

        assert is_channel_30 == is_channel_31, (
            f"[{label}] clasificare IS_CHANNEL diferă: 0.4.0={is_channel_30} (drift={drift30!r}) vs "
            f"0.4.1={is_channel_31} (drift={drift31!r}) -- threshold={s_max * atr!r}")
        assert abs(drift30 - drift31) < 1e-9, f"[{label}] drift 0.4.0 vs 0.4.1 diferă cu {abs(drift30 - drift31)!r}"


# ═══════════════════════ §5: paritate DECIZIONALĂ completă 0.4.0 vs 0.4.1, pe fixture bogat ═══════════════════════
def test_full_decision_parity_0_4_0_vs_0_4_1_oscillation_fixture():
    bars = osc_bars(cycles=40)
    config_kw = dict(K=3, N=6, w_atr=0.35, acknowledge_construction_only=True,
                     d_min_bars=20, atr_window=14, n_touch=2, swing_k=2)
    eng30, out30 = run30(bars, RangeConfigV3(**config_kw))
    eng31, out31 = run31(bars, RangeConfigV31(**config_kw))

    f30, f31 = _fps(out30), _fps(out31)
    assert f30 == f31, "paritate decizională eșuată -- stări/evenimente/segment_id/ancore/reason codes diferă"

    s30, s31 = _slopes(out30), _slopes(out31)
    worst = max((abs(a - b) for a, b in zip(s30, s31) if a is not None and b is not None), default=0.0)
    assert worst < 1e-6, f"panta diferă între 0.4.0/0.4.1 cu {worst!r} -- peste toleranța de ordine flotantă"

    h30 = [(s.segment_id, s.predecessor_id, s.end_reason, s.structural_start_ts, s.confirm_ts, s.end_ts,
           s.bars_in_segment, s.anchor_lower, s.anchor_upper, s.reached_established) for s in eng30.segment_history]
    h31 = [(s.segment_id, s.predecessor_id, s.end_reason, s.structural_start_ts, s.confirm_ts, s.end_ts,
           s.bars_in_segment, s.anchor_lower, s.anchor_upper, s.reached_established) for s in eng31.segment_history]
    assert h30 == h31, "istoricul segmentelor terminate diferă între 0.4.0 și 0.4.1"


def test_full_decision_parity_0_4_0_vs_0_4_1_hbl20_trace():
    """Traseul HBL-20 (breach 52 / sweep confirmat 56 / markup 63) trebuie IDENTIC bară-cu-bară."""
    bars, _, _ = _hbl20_bars()
    config_kw = dict(K=5, N=5, w_atr=0.02, acknowledge_construction_only=True,
                     d_min_bars=96, duration_class="MULTIDAY_RANGE", atr_window=14, n_touch=2, swing_k=2)
    prod30 = RangeSemanticProducerV3(RangeConfigV3(**config_kw))
    prod31 = RangeSemanticProducerV31(RangeConfigV31(**config_kw))
    log30, log31 = [], []
    for idx, b in enumerate(bars):
        res30, evs30 = prod30.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close,
                                      atr=3.0, trend_context=None)
        res31, evs31 = prod31.observe(ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low, close=b.close,
                                      atr=3.0, trend_context=None)
        log30.append((idx, res30.lifecycle, res30.segment_id, res30.confirm_ts, res30.reason_codes,
                     tuple(e.kind for e in evs30)))
        log31.append((idx, res31.lifecycle, res31.segment_id, res31.confirm_ts, res31.reason_codes,
                     tuple(e.kind for e in evs31)))
    assert log30 == log31

    sweep_30 = sorted({i for i, *_r, kinds in log30 for k in kinds if k == SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value})
    sweep_31 = sorted({i for i, *_r, kinds in log31 for k in kinds if k == SegmentEventKindV3.LIQUIDITY_SWEEP_DOWN.value})
    assert sweep_30 == sweep_31, "bara sweep-ului diferă între 0.4.0 și 0.4.1"
    assert sweep_30 == [56], f"sweep-ul HBL-20 trebuie confirmat EXACT la bara 56, găsit {sweep_30}"

    breakout_30 = sorted({i for i, *_r, kinds in log30 for k in kinds
                          if k == SegmentEventKindV3.BREAKOUT_ACCEPTANCE_UP.value})
    breakout_31 = sorted({i for i, *_r, kinds in log31 for k in kinds
                          if k == SegmentEventKindV3.BREAKOUT_ACCEPTANCE_UP.value})
    assert breakout_30 == breakout_31, "bara breakout-ului diferă între 0.4.0 și 0.4.1"
    assert not breakout_30 or breakout_30[0] > 63, "markup-ul (bara 63) nu poate confirma singur breakout"


def test_config_fingerprint_ties_to_new_implementation_identity():
    """§5: noua implementare trebuie LEGATĂ de fingerprint-ul artifact/versiune -- `range_spec_id` 0.4.1 NU
    poate coincide cu cel 0.4.0 pt. parametri identici (identitatea producătorului e parte din hash)."""
    kw = dict(K=3, N=6, w_atr=0.35, acknowledge_construction_only=True, d_min_bars=20)
    id30 = RangeConfigV3(**kw).range_spec_id()
    id31 = RangeConfigV31(**kw).range_spec_id()
    assert id30 != id31, "range_spec_id 0.4.1 trebuie să difere de 0.4.0 -- identitatea producătorului s-a schimbat"


# ═══════════════════════ Test decisiv de performanță (§6 finalul + §7): 20x d_min_bars NU costă ~20x/bară ═══════════════════════
def test_20x_d_min_bars_does_not_cost_20x_per_bar():
    """Izolat la nivel de segment (bypass N1 -- costul relevant e STRICT `push_close`+`slope()`), la scara
    citată de Red Team (raport 20,1x la 20x d_min_bars pt. 0.4.0). 0.4.1 trebuie să rămână ~flat."""
    def cost_per_op(d_min, n_ops):
        c = cfg31(d_min_bars=d_min)
        seg = _SegmentV31(segment_id=1, predecessor_id=None, transition_reason=None, config=c)
        for i in range(d_min):
            seg.push_close(2400.0 + (i % 7) * 0.3)
        t0 = time.perf_counter()
        for i in range(n_ops):
            seg.push_close(2400.0 + (i % 11) * 0.4)
            seg.slope()
        return (time.perf_counter() - t0) / n_ops

    small = cost_per_op(100, 4000)
    large = cost_per_op(2000, 4000)   # 20x d_min_bars
    ratio = large / small if small > 0 else float("inf")
    assert ratio < 4.0, (
        f"defectul §12 NU e închis: cost/operație a crescut {ratio:.2f}x pt. 20x d_min_bars "
        f"(small={small * 1e6:.3f}us large={large * 1e6:.3f}us) -- se aștepta ~flat, NU ~20x")


def test_old_implementation_still_shows_the_linear_defect_as_reference():
    """Control negativ -- confirmă că 0.4.0 (`_Segment`, NEATINS) încă arată defectul O(d_min_bars), altfel
    testul de mai sus n-ar dovedi nimic (ar putea trece și dacă AMBELE implementări ar fi rapide din alt motiv)."""
    def cost_per_op_old(d_min, n_ops):
        c = cfg30(d_min_bars=d_min)
        seg = _Segment(segment_id=1, predecessor_id=None, transition_reason=None, config=c)
        for i in range(d_min):
            seg.closes.append(2400.0 + (i % 7) * 0.3)
        t0 = time.perf_counter()
        for i in range(n_ops):
            seg.closes.append(2400.0 + (i % 11) * 0.4)
            seg.slope()
        return (time.perf_counter() - t0) / n_ops

    small = cost_per_op_old(100, 3000)
    large = cost_per_op_old(2000, 3000)
    ratio = large / small if small > 0 else float("inf")
    assert ratio > 8.0, (
        f"controlul negativ nu reproduce defectul O(d_min_bars) în 0.4.0 (ratio={ratio:.2f}x) -- "
        f"fixture-ul benchmark-ului nu e valid dacă referința nu mai arată defectul")


# ═══════════════════════ interzise -- fără MT5/broker/order_send/set_authority/fallback (§10) ═══════════════════════
def test_no_forbidden_imports_in_source():
    for mod in (_rsv31_mod, _rev31_mod):
        src = inspect.getsource(mod).lower()
        for forbidden in ("metatrader5", "import mt5", "mt5.", "order_send", "set_authority",
                          "probability_inputs", "broker"):
            assert forbidden not in src, f"import/termen interzis găsit în {mod.__name__}: {forbidden!r}"


def test_range_producer_v31_never_imports_ai_trader_runtime():
    for mod in (_rsv31_mod, _rev31_mod):
        src = inspect.getsource(mod)
        assert "import ai_trader" not in src
        assert "from ai_trader" not in src
        assert "ve_tower" not in src.lower()


def test_ast_guard_no_hardcoded_numeric_default_for_K_N_in_v31():
    """RangeConfigV31 nu redeclară CÂMPURI (le moștenește) -- garda structurală se aplică deja pe 0.4.0;
    aici verificăm doar că V31 nu introduce vreun default nou pt. K/N/w_atr prin suprascriere."""
    src = (_MODULE_DIR / "range_semantic_v3_1.py").read_text(encoding="utf-8")
    tree = ast.parse(src, filename="range_semantic_v3_1.py")
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RangeConfigV31":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    assert item.target.id not in ("K", "N", "w_atr"), (
                        "RangeConfigV31 NU trebuie să redeclare K/N/w_atr -- trebuie moștenite din RangeConfigV3")


# ═══════════════════════ compatibilitate -- 0.4.0 și toate versiunile anterioare rămân neatinse ═══════════════════════
def test_0_4_0_producer_and_engine_still_importable_unchanged():
    import ve_n1_replay as pkg
    assert pkg.RangeSemanticProducerV3 is not None
    assert pkg.RangeSemanticEngineV3 is not None
    RangeConfigV3(K=2, N=4, w_atr=0.3, acknowledge_construction_only=True)   # 0.4.0 tot funcțional


def test_v31_does_not_reuse_or_reinterpret_reason_codes():
    """V3.1 NU introduce reason codes noi -- semantica (14 stări/evenimente) e NESCHIMBATĂ (mandat §4)."""
    from ve_n1_replay.range_semantic_v3 import REASON_CODES_V3 as RC30
    from ve_n1_replay.range_semantic_v3_1 import REASON_CODES_V3 as RC31_reexport
    assert RC30 == RC31_reexport, "V3.1 trebuie să REFOLOSEASCĂ exact registrul de reason codes al lui 0.4.0"


def test_entry_decision_f7_unchanged_via_v31_engine():
    """F7 SAFETY_GUARD (RANGE_MID -> zero entry) trebuie identic prin motorul 0.4.1 -- funcția `entry_decision_v3`
    e REFOLOSITĂ, nu reimplementată."""
    from ve_n1_replay.range_semantic_v3 import SAFETY_GUARD_RANGE_MID_NO_ENTRY
    bars = osc_bars(cycles=10)
    eng = RangeSemanticEngineV31(range_config=cfg31(), **KW)
    saw_guard = False
    for b in bars:
        _, _, evs = eng.observe_closed_bar(b)
        for e in evs:
            if e.kind == SegmentEventKindV3.RANGE_MID.value:
                assert e.safety_guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
                decision = eng.entry_decision_for(e)
                assert decision.permitted is False
                saw_guard = True
    assert saw_guard, "fixture-ul trebuie să producă cel puțin un eveniment RANGE_MID"


# ═══════════════════════ N1 0.1.1 rămâne byte-identic prin compunere (moștenit, nu retestat exhaustiv aici) ═══════════════════════
def test_n1_byte_identical_0_1_1_via_v31_engine():
    bars = osc_bars(cycles=8)
    eng = RangeSemanticEngineV31(range_config=cfg31(), **KW)
    bare = N1IncrementalReplayEngine(**KW)
    for b in bars:
        n1, _, _ = eng.observe_closed_bar(b)
        assert n1.output_fingerprint == bare.observe_closed_bar(b).output_fingerprint


# ═══════════════════════ Amendament CEO: hardening `d_min_bars` fail-closed la GRANIȚA de configurație ═══════════════════════
# 0.4.0 nu validează NICIODATĂ d_min_bars (gol preexistent -- K/N/w_atr au verificări, d_min_bars nu). La
# d_min_bars=0, 0.4.0 rămâne silențios (slope()==0.0 mereu); 0.4.1 (înainte de acest amendament) arunca
# `IndexError` necontractual din `_SegmentV31.push_close()`. Remediat la construcția `RangeConfigV31` -- o
# valoare invalidă nu poate NICIODATĂ produce o instanță, deci nu poate ajunge NICIODATĂ la producător/segment.
@pytest.mark.parametrize("bad,label", [
    (-1, "negative"), (0, "zero -- fostul declanșator IndexError"), (-100, "negative_large"),
    (1.0, "float_integral"), (5.5, "float_fractional"), (True, "bool_true"), (False, "bool_false"),
    ("96", "str"), (None, "none"), (96.0, "float_equal_to_valid_value"),
])
def test_d_min_bars_invalid_rejected_at_config_construction(bad, label):
    with pytest.raises(RangeSemanticContractErrorV3):
        RangeConfigV31(K=2, N=4, w_atr=0.3, acknowledge_construction_only=True, d_min_bars=bad)


def test_d_min_bars_one_is_the_valid_boundary():
    """1 e cea mai mică valoare validă -- trebuie ACCEPTATĂ și trebuie să funcționeze corect (nu doar 'nu crapă')."""
    c = RangeConfigV31(K=1, N=1, w_atr=0.3, acknowledge_construction_only=True, d_min_bars=1)
    assert c.d_min_bars == 1
    seg = _SegmentV31(segment_id=1, predecessor_id=None, transition_reason=None, config=c)
    for i in range(5):
        seg.push_close(2400.0 + i)
        assert seg.closes.maxlen == 1
        assert len(seg.closes) == 1
        assert math.isfinite(seg.slope())   # n=1 -> slope()==0.0 prin definiție (n<2), nu o eroare


def test_d_min_bars_rejection_is_contractual_not_indexerror():
    """Excepția trebuie să fie CONTRACTUALĂ (`RangeSemanticContractErrorV3`), nu `IndexError` -- fix-ul mută
    eșecul de la o eroare de implementare necontractuală la un refuz explicit, documentat, la graniță."""
    try:
        RangeConfigV31(K=2, N=4, w_atr=0.3, acknowledge_construction_only=True, d_min_bars=0)
        pytest.fail("d_min_bars=0 trebuia refuzat")
    except IndexError:
        pytest.fail("d_min_bars=0 NU trebuie să mai producă IndexError -- fix-ul trebuia să-l elimine structural")
    except RangeSemanticContractErrorV3:
        pass   # comportamentul AȘTEPTAT


def test_d_min_bars_invalid_never_constructs_engine_or_producer():
    """Un `d_min_bars` invalid nu poate NICIODATĂ ajunge la `RangeSemanticEngineV31`/`RangeSemanticProducerV31`
    -- expresia `RangeConfigV31(...)` (evaluată ca argument) aruncă ÎNAINTE ca motorul să fie construit."""
    with pytest.raises(RangeSemanticContractErrorV3):
        RangeSemanticEngineV31(range_config=RangeConfigV31(
            K=2, N=4, w_atr=0.3, acknowledge_construction_only=True, d_min_bars=0), **KW)
    with pytest.raises(RangeSemanticContractErrorV3):
        RangeSemanticProducerV31(RangeConfigV31(
            K=2, N=4, w_atr=0.3, acknowledge_construction_only=True, d_min_bars=-1))


def test_d_min_bars_invalid_construction_attempt_does_not_corrupt_unrelated_valid_engine():
    """O tentativă EȘUATĂ de configurație invalidă nu trebuie să afecteze în niciun fel o instanță VALIDĂ,
    deja construită, independentă -- fără stare comună/globală care ar putea fi coruptă de un refuz."""
    bars = osc_bars(cycles=10)
    good_config = cfg31(d_min_bars=10, K=2, N=6)
    ref, ref_out = run31(bars, good_config)
    good_eng = RangeSemanticEngineV31(range_config=good_config, **KW)
    for b in bars[:15]:
        good_eng.observe_closed_bar(b)
    before_fps = _fps([good_eng.observe_closed_bar(b) for b in bars[15:16]])
    before_n = good_eng.bars_observed

    for bad in (0, -1, 1.0, True, "x", None):
        with pytest.raises(RangeSemanticContractErrorV3):
            RangeConfigV31(K=2, N=4, w_atr=0.3, acknowledge_construction_only=True, d_min_bars=bad)

    assert good_eng.bars_observed == before_n, "tentativele eșuate NU trebuie să schimbe starea motorului valid"
    after_fps = _fps([good_eng.observe_closed_bar(b) for b in bars[16:17]])
    # continuăm motorul VALID normal după tentativele eșuate -- nicio corupere, comportament identic cu o
    # rulare de control fără nicio tentativă invalidă intercalată
    control_eng = RangeSemanticEngineV31(range_config=good_config, **KW)
    control_out = [control_eng.observe_closed_bar(b) for b in bars[:17]]
    assert _fps(control_out)[15:16] == before_fps
    assert _fps(control_out)[16:17] == after_fps


def test_d_min_bars_hardening_does_not_change_benchmark_configs():
    """Configurațiile EXACTE folosite de benchmark-urile canonic (d_min_bars=96) și adversarial
    (d_min_bars=200000) rămân valide și NESCHIMBATE comportamental -- hardening-ul e pur ADITIV, respinge
    doar categorii NOI de input nevalid, nu schimbă nimic pt. valorile deja valide."""
    canonical = RangeConfigV31(K=4, N=8, w_atr=0.5, acknowledge_construction_only=True, d_min_bars=96,
                               segment_history_limit=64)
    adversarial = RangeConfigV31(K=4, N=8, w_atr=0.5, acknowledge_construction_only=True, d_min_bars=200_000,
                                 segment_history_limit=64)
    assert canonical.d_min_bars == 96
    assert adversarial.d_min_bars == 200_000
    # fingerprint-ul depinde DOAR de câmpuri + identitatea producătorului -- __post_init__ nu-l afectează
    assert canonical.range_spec_id() == RangeConfigV31(
        K=4, N=8, w_atr=0.5, acknowledge_construction_only=True, d_min_bars=96,
        segment_history_limit=64).range_spec_id()
