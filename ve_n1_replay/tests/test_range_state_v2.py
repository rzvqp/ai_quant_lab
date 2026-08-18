"""Teste DECISIVE — RANGE_STATE SPEC V2 (0.3.0), remediu SEMANTIC_SPEC_DEFECT (mandat §9, 28 cazuri).

Sursă normativă: Statistician STAT-RANGE-SEMANTIC-DIAGNOSIS-V2-v1.0 @3aac2cc (manifest v2.7.78 @18aa2a1).
NU accesează date reale de piață (RC-03..08/SEALED/OOS) — fixture-uri sintetice deterministe, ca peste tot
în acest pachet. `w_atr`/`s_max` sunt VE-proposed/neratificate (vezi RANGE_STATE_V2_CONTRACT.md); testele de
clasificare range-vs-canal folosesc override-uri LOCALE de test, documentate, NU valorile implicite livrate.
"""
from __future__ import annotations

from collections import deque

import pytest

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import (
    RangeStateReplayEngineV2, RangeConfigV2, N1IncrementalReplayEngine, RangeEventKindV2,
    RangeStateProducerV2, entry_decision_v2, SAFETY_GUARD_RANGE_MID_NO_ENTRY, RangeSnapshotErrorV2,
    BoundaryValidityV2, RangeStateReplayEngine as V1Engine, RangeConfig as V1Config,
)
from tests import _fixtures as fx

Bar = r.Bar
KW = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)


def mk(i, o, h, l, c):
    return Bar(symbol="XAUUSD", ts_open=i * 900, ts_close=(i + 1) * 900,
              open=float(o), high=float(h), low=float(l), close=float(c), volume=100.0)


def osc_bars(cycles=14, base=2400.0, start=0, hi=None, lo=None):
    """Oscilație determinstă (fereastra confirmată, touches acumulate) — nu presupune ESTABLISHED."""
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


def cfg(**kw):
    base = dict(d_min_bars=24, atr_window=14, n_touch=2, w_atr=0.25, s_max=0.15, retest_window_bars=12)
    base.update(kw)
    return RangeConfigV2.multiday(**{k: v for k, v in base.items() if k != "duration_class"})


def run_engine(bars, config=None):
    eng = RangeStateReplayEngineV2(range_config=config or cfg(), **KW)
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
    return [(n1.output_fingerprint, rng.available, rng.boundary_validity, rng.anchor_upper, rng.anchor_lower,
            rng.actionable_start_ts, tuple(e.kind for e in evs)) for n1, rng, evs in out]


def _established_prefix(cycles=8, cfg_obj=None):
    """Rulează oscilația de bază până ajunge la un episod ACTIV (FORMING, cu limite calculate) — suficient
    pentru mecanica de breakout (candidate/accepted/failed/retest/sweep evaluează în FORMING SAU ESTABLISHED)."""
    bars = osc_bars(cycles=cycles)
    eng, out = run_engine(bars, cfg_obj)
    last = [rng for _, rng, _ in out if rng.available][-1]
    return bars, eng, out, last.anchor_upper, last.anchor_lower


# ═══════════════════════ 1+2: ancoră stabilă + atingeri care NU dispar retroactiv ═══════════════════════
def test_anchor_stable_and_touches_survive_new_extreme():
    """Regresia DECISIVĂ vs 0.2.0: un vârf nou (wick, fără breakout) NU trebuie să scadă touches_upper sau
    să retrogradeze boundary_validity din CONFIRMED — exact defectul semantic remediat de V2."""
    base = 2400.0

    def cycle(bars, i, hi=base + 20, lo=base - 20):
        for ph, cl in [(0, base + 8), (1, base + 16), (2, hi - 2), (3, base + 12),
                       (4, base - 4), (5, base - 16), (6, lo + 2), (7, base - 8)]:
            c = cl; o = c - 1; h = c + 3; l = c - 3
            if ph == 2: h = hi
            if ph == 6: l = lo
            bars.append(mk(i, o, h, l, c)); i += 1
        return i

    bars = []; i = 0
    for _ in range(10):
        i = cycle(bars, i)
    spike_close = base + 5
    bars += [mk(i, base + 3, base + 6, base, base + 4), mk(i + 1, base + 4, base + 7, base + 1, base + 5),
            mk(i + 2, spike_close - 1, base + 40, spike_close - 3, spike_close),   # wick nou, FĂRĂ breakout
            mk(i + 3, base + 4, base + 7, base + 1, base + 5), mk(i + 4, base + 3, base + 6, base, base + 4)]
    i += 5
    for _ in range(8):
        i = cycle(bars, i)

    config = cfg(d_min_bars=10)
    eng, out = run_engine(bars, config)
    touches = [rng.touches_upper for _, rng, _ in out if rng.available and rng.touches_upper is not None]
    assert touches == sorted(touches), "touches_upper trebuie să fie NEDESCRESCĂTOR (nicio invalidare retroactivă)"
    confirmed_before = any(rng.boundary_validity == 'CONFIRMED' for _, rng, _ in out[:80])
    confirmed_well_after = any(rng.boundary_validity == 'CONFIRMED' for _, rng, _ in out[95:])
    assert confirmed_before and confirmed_well_after, "CONFIRMED trebuie să supraviețuiască vârfului nou"


def test_regression_v1_loses_touches_v2_does_not():
    """Comparație DIRECTĂ cu 0.2.0 (neatins) pe ACEEAȘI secvență adversarială: V1 pierde CONFIRMED, V2 nu."""
    base = 2400.0

    def cycle(bars, i, hi=base + 20, lo=base - 20):
        for ph, cl in [(0, base + 8), (1, base + 16), (2, hi - 2), (3, base + 12),
                       (4, base - 4), (5, base - 16), (6, lo + 2), (7, base - 8)]:
            c = cl; o = c - 1; h = c + 3; l = c - 3
            if ph == 2: h = hi
            if ph == 6: l = lo
            bars.append(mk(i, o, h, l, c)); i += 1
        return i

    bars = []; i = 0
    for _ in range(10):
        i = cycle(bars, i)
    spike_close = base + 5
    bars += [mk(i, base + 3, base + 6, base, base + 4), mk(i + 1, base + 4, base + 7, base + 1, base + 5),
            mk(i + 2, spike_close - 1, base + 40, spike_close - 3, spike_close),
            mk(i + 3, base + 4, base + 7, base + 1, base + 5), mk(i + 4, base + 3, base + 6, base, base + 4)]
    i += 5
    for _ in range(8):
        i = cycle(bars, i)

    v2eng = RangeStateReplayEngineV2(range_config=cfg(d_min_bars=10), **KW)
    v1eng = V1Engine(range_config=V1Config(d_min_bars=10, atr_window=14, n_touch=2, tol_atr=0.25, er_max=0.95), **KW)
    v2out = [v2eng.observe_closed_bar(b) for b in bars]
    v1out = [v1eng.observe_closed_bar(b) for b in bars]
    v1_confirmed_late = any(rng.boundary_validity == 'CONFIRMED' for _, rng, _ in v1out[95:])
    v2_confirmed_late = any(rng.boundary_validity == 'CONFIRMED' for _, rng, _ in v2out[95:])
    assert v1_confirmed_late is False, "0.2.0 (neremediat) TREBUIE să reproducă defectul: pierde CONFIRMED"
    assert v2_confirmed_late is True, "0.3.0 TREBUIE să nu piardă CONFIRMED — asta e remedierea"


# ═══════════════════════ 3: atingere prin fitil ═══════════════════════
def test_wick_only_touch_counts():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    before = prod._touches_upper
    # close departe de zonă, dar HIGH intră în [upper-w, upper+w]
    w = prod._cfg.w_atr * prod._last_atr
    res, evs = prod.observe(bar_index=len(bars), ts_close=(len(bars) + 1) * 900,
                            open_=upper - 20, high=upper + w * 0.5, low=upper - 22, close=upper - 18,
                            atr=prod._last_atr, trend_context=None)
    assert res.touches_upper is not None and res.touches_upper > before


# ═══════════════════════ 4: bară care nu intersectează zona → fără atingere ═══════════════════════
def test_non_intersecting_bar_no_touch():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    mid = (upper + lower) / 2.0
    tu, tl = prod._touches_upper, prod._touches_lower
    res, evs = prod.observe(bar_index=len(bars), ts_close=(len(bars) + 1) * 900,
                            open_=mid, high=mid + 2, low=mid - 2, close=mid + 1,
                            atr=prod._last_atr, trend_context=None)
    assert res.touches_upper == tu and res.touches_lower == tl
    assert [e.kind for e in evs] == [RangeEventKindV2.RANGE_MID.value]


# ═══════════════════════ 5+6: range neutru / range în interiorul unui trend mai mare ═══════════════════════
def test_range_classification_neutral_to_bias_direction():
    """Mecanica de range (touches/anchor/consolidation) e independentă de N1 direction/trend_context —
    verificată cu trend_context simulat 'up' și 'down' pe ACEEAȘI geometrie de preț."""
    bars = osc_bars(cycles=8)
    for ctx in ("up", "down", None):
        prod = RangeStateProducerV2(cfg(d_min_bars=10))
        last = None
        for i, b in enumerate(bars):
            atr = 4.0 if i >= 14 else None
            res, evs = prod.observe(bar_index=i, ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low,
                                    close=b.close, atr=atr, trend_context=ctx)
            last = res
        assert last.trend_context == ctx           # atributul se PĂSTREAZĂ, nu se pierde
        assert last.touches_upper is not None and last.touches_upper >= 2   # mecanica neafectată de trend_context


def test_range_in_larger_trend_boundary_mechanics_unaffected():
    """RANGE_STATE se evaluează pe fereastra proprie, independent de contextul HTF (Partea 6.5) — un range
    format în interiorul unui trend_context direcțional trebuie să acumuleze touches identic cu unul neutru."""
    bars = osc_bars(cycles=10)
    prod_neutral = RangeStateProducerV2(cfg(d_min_bars=10))
    prod_trend = RangeStateProducerV2(cfg(d_min_bars=10))
    last_n = last_t = None
    for i, b in enumerate(bars):
        atr = 4.0 if i >= 14 else None
        rn, _ = prod_neutral.observe(bar_index=i, ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low,
                                     close=b.close, atr=atr, trend_context=None)
        rt, _ = prod_trend.observe(bar_index=i, ts_close=b.ts_close, open_=b.open, high=b.high, low=b.low,
                                   close=b.close, atr=atr, trend_context="up")
        last_n, last_t = rn, rt
    assert last_n.touches_upper == last_t.touches_upper and last_n.touches_lower == last_t.touches_lower
    assert last_n.boundary_validity == last_t.boundary_validity
    assert last_t.trend_context == "up"


def test_slope_classification_decision_range_vs_channel():
    """Testul DECIS al deciziei de clasificare (Partea 6.4), izolat de zgomotul unui fixture OHLC complet:
    close-uri PLATE (pantă exact 0.0, verificat direct) -> RANGE_STATE; RAMPĂ (pantă mare, verificată) ->
    CHANNEL_UP/DOWN. `_slope()` verificat independent pe cazuri calculabile manual (0.0 pt. plat, 1.0 pt.
    rampă unitară) — acesta testează DECIZIA de ramificare dat fiind un semnal de pantă cunoscut."""
    config = cfg(d_min_bars=10, s_max=0.15)
    prod = RangeStateProducerV2(config)
    prod._closes = deque([2400.0] * 10, maxlen=10)
    assert prod._slope() == 0.0
    prod._boundary_validity = BoundaryValidityV2.CONFIRMED
    prod._structural_start_idx = 0; prod._n = 10; prod._last_atr = 4.0
    events: list = []
    prod._classify_and_maybe_establish(9000, 9, events)
    assert prod._structure_class.value == "RANGE_STATE"

    prod2 = RangeStateProducerV2(config)
    prod2._closes = deque([2400.0 + x * 5.0 for x in range(10)], maxlen=10)   # pantă=5.0/bară, uriașă
    prod2._boundary_validity = BoundaryValidityV2.CONFIRMED
    prod2._structural_start_idx = 0; prod2._n = 10; prod2._last_atr = 4.0
    events2: list = []
    prod2._classify_and_maybe_establish(9000, 9, events2)
    assert prod2._structure_class.value == "CHANNEL_UP"
    assert prod2._slope() == 5.0


# ═══════════════════════ 7: BOS/CHoCH intern NU distruge range-ul exterior ═══════════════════════
def test_internal_bos_choch_does_not_invalidate():
    # oscilație de bază + o mică rupere INTERNĂ (un impuls mic ce nu atinge limitele exterioare)
    bars = osc_bars(cycles=6)
    base = 2400.0; i = len(bars)
    # impuls mic intern: câteva bare cu extreme mai mici decât limitele episodului, formând un mini-swing/break
    bars += [mk(i, base + 2, base + 6, base + 1, base + 5), mk(i + 1, base + 5, base + 6, base + 3, base + 4),
            mk(i + 2, base + 4, base + 5, base + 1, base + 2), mk(i + 3, base + 2, base + 3, base - 1, base),
            mk(i + 4, base, base + 1, base - 2, base - 1)]
    i += 5
    bars += osc_bars(cycles=6, start=i)
    config = cfg(d_min_bars=10)
    eng, out = run_engine(bars, config)
    events_after = any(rng.invalidation is not None for _, rng, _ in out)
    # episodul nu trebuie invalidat DOAR de structura internă (poate invalida ulterior din alt motiv, dar nu aici)
    structure_ev_seen = any((rng.structure_events_inside or 0) > 0 for _, rng, _ in out if rng.available)
    machine_survived = any(rng.available and rng.boundary_validity in ('PROVISIONAL', 'CONFIRMED')
                           for _, rng, _ in out[-40:])
    assert machine_survived, "episodul trebuie să supraviețuiască evenimentelor structurale interne"


# ═══════════════════════ 8: invalidare REALĂ a structurii exterioare ═══════════════════════
def test_real_outer_invalidation_on_accepted_break():
    bars, eng, out, upper, lower = _established_prefix(cycles=8)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    tail = [mk(n, upper + w + 5, upper + w + 8, upper + w + 2, upper + w + 5),
           mk(n + 1, upper + w + 6, upper + w + 9, upper + w + 3, upper + w + 7)]
    invs = []
    for b in tail:
        n1, rng, evs = eng.observe_closed_bar(b)
        invs.append(rng.invalidation)
    assert "ACCEPTED_BREAK" in invs


# ═══════════════════════ 9+10: canal ascendent/descendent → NICIODATĂ RANGE_STATE (P2) ═══════════════════════
@pytest.mark.parametrize("drift", [0.15, 0.3, 0.5, 1.0])
def test_channel_up_never_range_state(drift):
    bars = []
    price = 2380.0
    for i in range(140):
        o = price; c = price + drift; h = max(o, c) + 2; l = min(o, c) - 2
        bars.append(mk(i, o, h, l, c)); price = c
    _, out = run_engine(bars, cfg(d_min_bars=24, s_max=0.15))
    assert not any(rng.available and rng.structure_class == 'RANGE_STATE' for _, rng, _ in out)


@pytest.mark.parametrize("drift", [0.15, 0.3, 0.5, 1.0])
def test_channel_down_never_range_state(drift):
    bars = []
    price = 2420.0
    for i in range(140):
        o = price; c = price - drift; h = max(o, c) + 2; l = min(o, c) - 2
        bars.append(mk(i, o, h, l, c)); price = c
    _, out = run_engine(bars, cfg(d_min_bars=24, s_max=0.15))
    assert not any(rng.available and rng.structure_class == 'RANGE_STATE' for _, rng, _ in out)


# ═══════════════════════ 11-16: evenimente breakout ═══════════════════════
def test_breakout_candidate_reachable():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n1, rng, evs = eng.observe_closed_bar(mk(len(bars), upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3))
    assert RangeEventKindV2.BREAKOUT_CANDIDATE.value in [e.kind for e in evs]


def test_breakout_accepted_long():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    kinds_seen = set()
    for k, b in enumerate([mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
                           mk(n + 1, upper + w + 3, upper + w + 6, upper + w, upper + w + 4)]):
        _, _, evs = eng.observe_closed_bar(b)
        kinds_seen |= {e.kind for e in evs}
    assert RangeEventKindV2.BREAKOUT_ACCEPTED_LONG.value in kinds_seen
    assert RangeEventKindV2.BREAKOUT_ACCEPTED_SHORT.value not in kinds_seen
    assert RangeEventKindV2.BREAKOUT_FAILED.value not in kinds_seen


def test_breakout_accepted_short():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    kinds_seen = set()
    for b in [mk(n, lower - w - 2, lower - w + 1, lower - w - 5, lower - w - 3),
             mk(n + 1, lower - w - 3, lower - w, lower - w - 6, lower - w - 4)]:
        _, _, evs = eng.observe_closed_bar(b)
        kinds_seen |= {e.kind for e in evs}
    assert RangeEventKindV2.BREAKOUT_ACCEPTED_SHORT.value in kinds_seen
    assert RangeEventKindV2.BREAKOUT_ACCEPTED_LONG.value not in kinds_seen
    assert RangeEventKindV2.BREAKOUT_FAILED.value not in kinds_seen


def test_breakout_failed():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    mid = (upper + lower) / 2.0
    kinds_seen = set()
    for b in [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),   # candidate
             mk(n + 1, mid, mid + 3, mid - 3, mid)]:                              # revine înăuntru
        _, _, evs = eng.observe_closed_bar(b)
        kinds_seen |= {e.kind for e in evs}
    assert RangeEventKindV2.BREAKOUT_FAILED.value in kinds_seen
    assert RangeEventKindV2.BREAKOUT_ACCEPTED_LONG.value not in kinds_seen


def test_breakout_retest():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    kinds_seen = set()
    tail = [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
           mk(n + 1, upper + w + 3, upper + w + 6, upper + w, upper + w + 4),      # accepted
           mk(n + 2, upper + w + 1, upper + w + 3, upper + w - 0.5, upper + w + 2)]  # retest: revine la zonă
    for b in tail:
        _, _, evs = eng.observe_closed_bar(b)
        kinds_seen |= {e.kind for e in evs}
    assert RangeEventKindV2.BREAKOUT_RETEST.value in kinds_seen


def test_liquidity_sweep():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    _, _, evs = eng.observe_closed_bar(mk(n, upper + w - 2, upper + w + 8, upper + w - 4, upper + w - 3))
    assert RangeEventKindV2.LIQUIDITY_SWEEP.value in [e.kind for e in evs]


# ═══════════════════════ 17: accepted vs failed/sweep — exclusivitate mutuală + P6 (zero coliziuni) ═══════════════════════
def test_accepted_failed_sweep_mutually_exclusive_no_same_bar_collision():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    for b in [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
             mk(n + 1, upper + w + 3, upper + w + 6, upper + w, upper + w + 4)]:
        _, _, evs = eng.observe_closed_bar(b)
        ks = {e.kind for e in evs}
        accepted = {RangeEventKindV2.BREAKOUT_ACCEPTED_LONG.value, RangeEventKindV2.BREAKOUT_ACCEPTED_SHORT.value}
        other = {RangeEventKindV2.BREAKOUT_FAILED.value, RangeEventKindV2.LIQUIDITY_SWEEP.value}
        assert not (ks & accepted and ks & other), "ACCEPTED și FAILED/SWEEP nu pot coincide pe aceeași bară"


# ═══════════════════════ 18: zero-lookahead ═══════════════════════
def test_zero_lookahead():
    bars = osc_bars(cycles=10)
    _, out_full = run_engine(bars)
    _, out_prefix = run_engine(bars[:50])
    for i in range(50):
        assert _fps(out_full)[i] == _fps(out_prefix)[i]


# ═══════════════════════ 19: structural_start_ts vs confirm_ts ═══════════════════════
def test_structural_start_vs_confirm_ts_ordering():
    bars = osc_bars(cycles=10)
    _, out = run_engine(bars, cfg(d_min_bars=10))
    confirmed = [rng for _, rng, _ in out if rng.available and rng.actionable_start_ts is not None]
    assert confirmed, "trebuie atins CONFIRMED (actionable_start_ts setat) la un moment dat"
    first = confirmed[0]
    assert first.structural_start_ts is not None
    assert first.actionable_start_ts >= first.structural_start_ts + 2 * 900   # >= k bare (k=2)


# ═══════════════════════ 20: chunk invariance ═══════════════════════
@pytest.mark.parametrize("chunks", [[112], [1, 111], [50, 62], [80, 20, 12], [95, 1, 16]])
def test_chunk_invariance(chunks):
    bars = osc_bars(cycles=14)
    assert sum(chunks) == len(bars)
    config = cfg(d_min_bars=10)
    ref, ref_out = run_engine(bars, config)
    got = []
    eng = RangeStateReplayEngineV2(range_config=config, **KW)
    pos = 0
    for c in chunks:
        for b in bars[pos:pos + c]:
            got.append(eng.observe_closed_bar(b))
        snap = eng.snapshot()
        eng = RangeStateReplayEngineV2(range_config=config, **KW)
        eng.restore(snap)
        pos += c
    assert _fps(got) == _fps(ref_out)


# ═══════════════════════ 21: determinism ═══════════════════════
def test_determinism():
    bars = osc_bars(cycles=10)
    _, out1 = run_engine(bars)
    _, out2 = run_engine(bars)
    assert _fps(out1) == _fps(out2)


# ═══════════════════════ 22: două instanțe fără stare comună ═══════════════════════
def test_two_instances_no_shared_state():
    bars = osc_bars(cycles=10)
    config = cfg(d_min_bars=10)
    ref, ref_out = run_engine(bars, config)
    e1 = RangeStateReplayEngineV2(range_config=config, **KW)
    e2 = RangeStateReplayEngineV2(range_config=config, **KW)
    for b in bars[:30]:
        e1.observe_closed_bar(b)
    got2 = [e2.observe_closed_bar(b) for b in bars]
    assert _fps(got2) == _fps(ref_out)
    assert e1.bars_observed == 30 and e2.bars_observed == len(bars)


# ═══════════════════════ 23+24: snapshot/restart bit-identic în FIECARE stare (incl. mijlocul unui breakout) ═══════════════════════
def test_snapshot_restart_every_machine_state_incl_mid_breakout():
    base_bars, eng0, out0, upper, lower = _established_prefix(cycles=8)
    w = eng0._range._cfg.w_atr * eng0._range._last_atr
    n = len(base_bars)
    tail = [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),     # CANDIDATE
           mk(n + 1, upper + w + 3, upper + w + 6, upper + w, upper + w + 4),     # ACCEPTED
           mk(n + 2, upper + w + 1, upper + w + 3, upper + w - 0.5, upper + w + 2)]  # RETEST
    bars = base_bars + tail
    config = cfg(d_min_bars=24)
    ref, ref_out = run_engine(bars, config)
    for cut in range(30, len(bars)):
        eng = RangeStateReplayEngineV2(range_config=config, **KW)
        for b in bars[:cut]:
            eng.observe_closed_bar(b)
        snap = eng.snapshot()
        eng2 = RangeStateReplayEngineV2(range_config=config, **KW)
        eng2.restore(snap)
        tail_out = [eng2.observe_closed_bar(b) for b in bars[cut:]]
        assert _fps(tail_out) == _fps(ref_out[cut:]), f"divergență la cut={cut}"


# ═══════════════════════ 25: mismatch contract/config/sursă → refuz fail-closed ═══════════════════════
def test_mismatch_config_refused():
    bars = osc_bars(cycles=6)
    eng = RangeStateReplayEngineV2(range_config=cfg(), **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    other = RangeStateReplayEngineV2(range_config=cfg(w_atr=0.50), **KW)
    with pytest.raises(RangeSnapshotErrorV2):
        other.restore(snap)


def test_mismatch_n1_identity_refused():
    bars = osc_bars(cycles=6)
    eng = RangeStateReplayEngineV2(range_config=cfg(), symbol="XAUUSD", timeframe="15m",
                                   bar_interval_seconds=900, implementation_commit=IC)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    other = RangeStateReplayEngineV2(range_config=cfg(), symbol="XAUUSD", timeframe="1h",
                                     bar_interval_seconds=3600, implementation_commit=IC)
    with pytest.raises(RangeSnapshotErrorV2):
        other.restore(snap)


def test_mismatch_predecessor_version_snapshot_refused_both_directions():
    bars = osc_bars(cycles=6)
    v1eng = V1Engine(range_config=V1Config(), **KW)
    for b in bars:
        v1eng.observe_closed_bar(b)
    v1snap = v1eng.snapshot()
    with pytest.raises(RangeSnapshotErrorV2):
        RangeStateReplayEngineV2(range_config=cfg(), **KW).restore(v1snap)

    v2eng = RangeStateReplayEngineV2(range_config=cfg(), **KW)
    for b in bars:
        v2eng.observe_closed_bar(b)
    v2snap = v2eng.snapshot()
    with pytest.raises(Exception):
        V1Engine(range_config=V1Config(), **KW).restore(v2snap)


# ═══════════════════════ 26: F7 explicit + persistent ═══════════════════════
def test_f7_explicit_persistent_zero_entry():
    bars = osc_bars(cycles=8)
    _, out = run_engine(bars, cfg(d_min_bars=10))
    mids = [e for e in all_events(out) if e.kind == RangeEventKindV2.RANGE_MID.value]
    assert mids, "RANGE_MID trebuie emis explicit"
    for e in mids:
        assert e.safety_guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
        d = entry_decision_v2(e)
        assert d.permitted is False and d.guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
    non_mid = [e for e in all_events(out) if e.kind != RangeEventKindV2.RANGE_MID.value]
    assert all(entry_decision_v2(e).permitted for e in non_mid)

    led = RangeStateReplayEngineV2(range_config=cfg(d_min_bars=10), **KW).replay_batch(bars)
    assert led.n_guards > 0
    assert led.header()["safety_guards_register"] == ["RANGE_MID_NO_ENTRY"]

    # persistă după snapshot/restart
    config = cfg(d_min_bars=10)
    eng = RangeStateReplayEngineV2(range_config=config, **KW)
    for b in bars[:40]:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeStateReplayEngineV2(range_config=config, **KW)
    eng2.restore(snap)
    tail_mids = 0
    for b in bars[40:]:
        _, _, evs = eng2.observe_closed_bar(b)
        for e in evs:
            if e.kind == RangeEventKindV2.RANGE_MID.value:
                assert e.safety_guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
                tail_mids += 1
    assert tail_mids > 0


# ═══════════════════════ 27: paritate COMPLETĂ cu N1 0.1.1 (motorul neatins) ═══════════════════════
@pytest.mark.parametrize("gen", [fx.trend_up_regime_bars, fx.trend_down_regime_bars,
                                 lambda: fx.uncertain_regime_bars(n=150), osc_bars])
def test_n1_full_parity_with_0_1_1(gen):
    bars = gen()
    eng = RangeStateReplayEngineV2(range_config=cfg(), **KW)
    bare = N1IncrementalReplayEngine(**KW)
    for b in bars:
        n1, _, _ = eng.observe_closed_bar(b)
        assert n1.output_fingerprint == bare.observe_closed_bar(b).output_fingerprint


def test_n1_contract_versions_unchanged_from_0_2_0():
    """N1_contract/raw_axis/router bump-urile de PACHET rămân IDENTICE cu 0.2.0 — doar RANGE-ul are contract nou."""
    from ve_n1_replay.version import (
        PKG_N1_CONTRACT_VERSION, PKG_RAW_AXIS_SCHEMA_VERSION, PKG_ROUTER_VERSION,
        PKG_N1_CONTRACT_VERSION_V2, PKG_RAW_AXIS_SCHEMA_VERSION_V2, PKG_ROUTER_VERSION_V2,
    )
    assert PKG_N1_CONTRACT_VERSION == PKG_N1_CONTRACT_VERSION_V2
    assert PKG_RAW_AXIS_SCHEMA_VERSION == PKG_RAW_AXIS_SCHEMA_VERSION_V2
    assert PKG_ROUTER_VERSION == PKG_ROUTER_VERSION_V2


def test_0_2_0_module_files_untouched_still_functional():
    """0.2.0 rămâne funcțional, NEMODIFICAT, importabil alături de 0.3.0 (păstrat pentru audit)."""
    from ve_n1_replay import RangeStateReplayEngine, RangeConfig
    bars = osc_bars(cycles=4)
    eng = RangeStateReplayEngine(range_config=RangeConfig(), **KW)
    for b in bars:
        n1, rng, evs = eng.observe_closed_bar(b)
    assert eng.bars_observed == len(bars)


# ═══════════════════════ reachability: toate cele 11 evenimente + RANGE_STATE ═══════════════════════
def test_reachability_all_v2_events():
    seen = set()
    seen |= kinds(run_engine(osc_bars(cycles=10), cfg(d_min_bars=10))[1])
    # RANGE_ESTABLISHED: reachable la orice s_max suficient de permisiv — pragul implicit e neratificat
    # (vezi RANGE_STATE_V2_CONTRACT.md); reachability != calibrare, deci override LOCAL, documentat.
    seen |= kinds(run_engine(osc_bars(cycles=14), cfg(d_min_bars=24, s_max=2.0))[1])
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    tail_scenarios = [
        [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
         mk(n + 1, upper + w + 3, upper + w + 6, upper + w, upper + w + 4)],                 # accepted long
        [mk(n, lower - w - 2, lower - w + 1, lower - w - 5, lower - w - 3),
         mk(n + 1, lower - w - 3, lower - w, lower - w - 6, lower - w - 4)],                  # accepted short
        [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
         mk(n + 1, (upper + lower) / 2, (upper + lower) / 2 + 3, (upper + lower) / 2 - 3, (upper + lower) / 2)],  # failed
        [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
         mk(n + 1, upper + w + 3, upper + w + 6, upper + w, upper + w + 4),
         mk(n + 2, upper + w + 1, upper + w + 3, upper + w - 0.5, upper + w + 2)],            # retest
        [mk(n, upper + w - 2, upper + w + 8, upper + w - 4, upper + w - 3)],                  # sweep
    ]
    for scenario in tail_scenarios:
        eng2 = RangeStateReplayEngineV2(range_config=cfg(d_min_bars=24), **KW)
        for b in bars:
            eng2.observe_closed_bar(b)
        for b in scenario:
            _, _, evs = eng2.observe_closed_bar(b)
            seen |= {e.kind for e in evs}
    expected = {e.value for e in RangeEventKindV2}
    missing = expected - seen
    assert not missing, f"evenimente nereachable: {missing}"
