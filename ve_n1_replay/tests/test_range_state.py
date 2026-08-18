"""Teste DECISIVE pentru RANGE_STATE + evenimente longitudinale (0.2.0), conform mandatului §7 + amendamentul F7.

Acoperă: N1 byte-identic cu 0.1.1; actionable numai după confirm_ts; retrospectiv fără entry timpuriu; warmup≠range;
precedență TREND_PAUSE; RANGE_MID SAFETY_GUARD (refuz executabil, zero entry/candidate/p-value/broker, în audit);
respingeri; candidate→accepted; candidate→failed; accepted&failed exclusive; retest; sweep+reversal; invalidare;
zero-lookahead prin modificarea barelor viitoare; chunk invariance; snapshot/restart în FIECARE stare; două instanțe
fără stare comună; reachability (RANGE_STATE + fiecare din cele 8 evenimente); paritatea stream-ului de swing-uri cu
`detect_swings`; fără importuri MT5/broker/order_send/set_authority/probability_inputs.
"""
from __future__ import annotations

import pytest

import ve_n1_replay as r
from ve_n1_replay._bootstrap import vendored_module
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import (
    RangeStateReplayEngine, RangeConfig, N1IncrementalReplayEngine, RangeEventKind, RangeStateProducer,
    entry_decision, SAFETY_GUARD_RANGE_MID_NO_ENTRY, RangeSnapshotError, MachineState,
)
from tests import _fixtures as fx

Bar = r.Bar
KW = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)
_vb = vendored_module("ai_trader.structural_observer.vendor_bridge")


def mk(i, o, h, l, c):
    return Bar(symbol="XAUUSD", ts_open=i * 900, ts_close=(i + 1) * 900,
              open=float(o), high=float(h), low=float(l), close=float(c), volume=100.0)


def osc_bars(cycles=14, base=2400.0, start=0):
    """Oscilație determinstă care formează un range confirmat (swing highs @base+22, lows @base-22)."""
    bars = []; i = start
    for _ in range(cycles):
        for ph, cl in [(0, base + 8), (1, base + 16), (2, base + 20), (3, base + 12),
                       (4, base - 4), (5, base - 16), (6, base - 20), (7, base - 8)]:
            c = cl; o = c - 1; h = c + 3; l = c - 3
            if ph == 2: h = base + 22
            if ph == 6: l = base - 22
            bars.append(mk(i, o, h, l, c)); i += 1
    return bars


def default_cfg(**kw):
    base = dict(d_min_bars=10, atr_window=14, n_touch=2, tol_atr=0.25, er_max=0.95, retest_window_bars=12)
    base.update(kw)
    return RangeConfig(**base)


def run(bars, cfg=None):
    eng = RangeStateReplayEngine(range_config=cfg or default_cfg(), **KW)
    out = []
    for b in bars:
        out.append(eng.observe_closed_bar(b))
    return eng, out


def all_events(out):
    evs = []
    for _, _, es in out:
        evs.extend(es)
    return evs


def kinds(out):
    return {e.kind for e in all_events(out)}


# ═══════════════════════ N1 byte-identitate (nemodificat vs 0.1.1) ═══════════════════════
@pytest.mark.parametrize("gen", [fx.trend_up_regime_bars, fx.trend_down_regime_bars,
                                 lambda: fx.uncertain_regime_bars(n=200), osc_bars])
def test_n1_byte_identical_to_bare(gen):
    bars = gen()
    eng = RangeStateReplayEngine(range_config=default_cfg(), **KW)
    bare = N1IncrementalReplayEngine(**KW)
    for b in bars:
        n1, _, _ = eng.observe_closed_bar(b)
        assert n1.output_fingerprint == bare.observe_closed_bar(b).output_fingerprint


# ═══════════════════════ warmup / actionable / retrospectiv ═══════════════════════
def test_warmup_is_never_range():
    _, out = run(osc_bars(cycles=2))
    # primele bare (warmup ATR / fractali) NU sunt range
    early = out[0][1]
    assert early.available is False and early.reason in ("WARMUP", "NO_STRUCTURE")


def test_actionable_only_after_confirm_ts_and_lags_structural():
    _, out = run(osc_bars())
    est = [rng for _, rng, _ in out if rng.available and rng.consolidation_state == "ESTABLISHED"]
    assert est, "range trebuie să devină ESTABLISHED"
    first = est[0]
    assert first.actionable_start_ts is not None
    assert first.structural_start_ts is not None
    # actionable (confirm_ts) întârzie cu >= k bare față de structural (prin construcție)
    assert first.actionable_start_ts >= first.structural_start_ts + 2 * 900


def test_forming_has_no_actionable_ts():
    _, out = run(osc_bars())
    forming = [rng for _, rng, _ in out if rng.available and rng.consolidation_state == "FORMING"]
    assert forming, "trebuie să existe o fază FORMING"
    assert all(f.actionable_start_ts is None for f in forming)


# ═══════════════════════ F7 SAFETY_GUARD — RANGE_MID_NO_ENTRY ═══════════════════════
def test_range_mid_emitted_with_safety_guard():
    _, out = run(osc_bars())
    mids = [e for e in all_events(out) if e.kind == RangeEventKind.RANGE_MID.value]
    assert mids, "RANGE_MID trebuie emis EXPLICIT (nu ca absență)"
    assert all(e.safety_guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY for e in mids)


def test_entry_refused_in_range_mid_zero_entry():
    _, out = run(osc_bars())
    mids = [e for e in all_events(out) if e.kind == RangeEventKind.RANGE_MID.value]
    for e in mids:
        d = entry_decision(e)
        assert d.permitted is False and d.guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
    # orice alt eveniment nu e guvernat de guard
    non_mid = [e for e in all_events(out) if e.kind != RangeEventKind.RANGE_MID.value]
    assert all(entry_decision(e).permitted for e in non_mid)


def test_range_mid_never_produces_candidate():
    """RANGE_MID (close strict în interior) nu poate coincide cu un BREAKOUT_CANDIDATE (close dincolo)."""
    _, out = run(osc_bars())
    for _, _, evs in out:
        ks = {e.kind for e in evs}
        assert not ({RangeEventKind.RANGE_MID.value} & ks and {RangeEventKind.BREAKOUT_CANDIDATE.value} & ks)


def test_safety_guard_in_ledger_audit_not_deduced():
    led = RangeStateReplayEngine(range_config=default_cfg(), **KW).replay_batch(osc_bars())
    assert led.n_guards > 0                                   # contor SEPARAT n_guards (SAFETY_GUARDS)
    assert "RANGE_MID_NO_ENTRY" in [e.get("safety_guard") for rec in led.records for e in rec.events
                                    if e.get("safety_guard")]
    assert led.header()["safety_guards_register"] == ["RANGE_MID_NO_ENTRY"]


def test_guard_persists_after_snapshot_restart():
    cfg = default_cfg()
    bars = osc_bars()
    ref, _ = run(bars, cfg)
    # tăiem în interiorul range-ului, snapshot/restore, apoi verificăm că RANGE_MID + guard încă apar
    cut = 80
    eng = RangeStateReplayEngine(range_config=cfg, **KW)
    for b in bars[:cut]:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = RangeStateReplayEngine(range_config=cfg, **KW)
    eng2.restore(snap)
    tail_mids = 0
    for b in bars[cut:]:
        _, _, evs = eng2.observe_closed_bar(b)
        for e in evs:
            if e.kind == RangeEventKind.RANGE_MID.value:
                assert e.safety_guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
                tail_mids += 1
    assert tail_mids > 0


# ═══════════════════════ evenimente: reachability + tranziții ═══════════════════════
def test_low_and_high_rejection_reachable():
    k = kinds(run(osc_bars())[1])
    assert RangeEventKind.RANGE_LOW_REJECTION.value in k
    assert RangeEventKind.RANGE_HIGH_REJECTION.value in k


def _established_then(tail_fn, cfg=None):
    cfg = cfg or default_cfg()
    base = osc_bars(cycles=12)
    eng, out = run(base, cfg)
    # ultimul range disponibil ⇒ upper/lower curente
    last = [rng for _, rng, _ in out if rng.available][-1]
    upper, lower = last.upper, last.lower
    tail = tail_fn(len(base), upper, lower)
    full = base + tail
    return run(full, cfg)[1], upper, lower


def test_breakout_candidate_to_accepted():
    def tail(start, upper, lower):
        return [mk(start, upper + 5, upper + 8, upper + 2, upper + 5),
                mk(start + 1, upper + 6, upper + 9, upper + 3, upper + 7)]  # 2 close-uri consecutive dincolo (N=2)
    out, upper, lower = _established_then(tail)
    k = kinds(out)
    assert RangeEventKind.BREAKOUT_CANDIDATE.value in k
    assert RangeEventKind.BREAKOUT_ACCEPTED.value in k
    assert RangeEventKind.FAILED_BREAKOUT.value not in k


def test_breakout_candidate_to_failed():
    def tail(start, upper, lower):
        mid = (upper + lower) / 2
        return [mk(start, upper + 5, upper + 8, upper + 2, upper + 5),     # candidate (close dincolo)
                mk(start + 1, mid, mid + 3, mid - 3, mid)]                  # close înapoi ÎNĂUNTRU înainte de N
    out, upper, lower = _established_then(tail)
    k = kinds(out)
    assert RangeEventKind.BREAKOUT_CANDIDATE.value in k
    assert RangeEventKind.FAILED_BREAKOUT.value in k
    assert RangeEventKind.BREAKOUT_ACCEPTED.value not in k


def test_accepted_and_failed_mutually_exclusive():
    # pe o singură rulare cu un singur candidate, exact una dintre tranziții apare (niciodată ambele)
    def tail_acc(start, upper, lower):
        return [mk(start, upper + 5, upper + 8, upper + 2, upper + 5), mk(start + 1, upper + 6, upper + 9, upper + 3, upper + 7)]
    out_acc, _, _ = _established_then(tail_acc)
    k = kinds(out_acc)
    assert (RangeEventKind.BREAKOUT_ACCEPTED.value in k) ^ (RangeEventKind.FAILED_BREAKOUT.value in k)


def test_breakout_retest_reachable():
    def tail(start, upper, lower):
        return [
            mk(start, upper + 5, upper + 8, upper + 2, upper + 5),       # candidate
            mk(start + 1, upper + 6, upper + 9, upper + 3, upper + 7),   # accepted (N=2)
            mk(start + 2, upper + 6, upper + 8, upper + 0.5, upper + 4), # retest: low revine la limită, close deasupra
        ]
    out, upper, lower = _established_then(tail)
    assert RangeEventKind.BREAKOUT_RETEST.value in kinds(out)


def test_liquidity_sweep_reversal_reachable():
    def tail(start, upper, lower):
        # wick peste upper + close înăuntru pe ACEEAȘI bară (D6)
        return [mk(start, upper - 2, upper + 8, upper - 4, upper - 3)]
    out, upper, lower = _established_then(tail)
    assert RangeEventKind.LIQUIDITY_SWEEP_REVERSAL.value in kinds(out)


def test_reachability_all_events_and_range_state():
    """RANGE_STATE + fiecare din cele 8 evenimente sunt producibile pe fixture-uri canonice."""
    seen = set()
    # oscilația de bază acoperă MID/rejections/candidate/accepted
    seen |= kinds(run(osc_bars())[1])
    # failed / retest / sweep prin cozi dedicate
    for tail_fn in [
        lambda s, u, l: [mk(s, u + 5, u + 8, u + 2, u + 5), mk(s + 1, (u + l) / 2, (u + l) / 2 + 3, (u + l) / 2 - 3, (u + l) / 2)],
        lambda s, u, l: [mk(s, u + 5, u + 8, u + 2, u + 5), mk(s + 1, u + 6, u + 9, u + 3, u + 7), mk(s + 2, u + 6, u + 8, u + 0.5, u + 4)],
        lambda s, u, l: [mk(s, u - 2, u + 8, u - 4, u - 3)],
    ]:
        seen |= kinds(_established_then(tail_fn)[0])
    expected = {e.value for e in RangeEventKind}
    missing = expected - seen
    assert not missing, f"evenimente nereachable: {missing}"
    # RANGE_STATE însuși producibil (ESTABLISHED atins)
    assert any(rng.available and rng.consolidation_state == "ESTABLISHED" for _, rng, _ in run(osc_bars())[1])


# ═══════════════════════ invalidare ═══════════════════════
def test_accepted_break_invalidates_range():
    def tail(start, upper, lower):
        return [mk(start, upper + 5, upper + 8, upper + 2, upper + 5), mk(start + 1, upper + 6, upper + 9, upper + 3, upper + 7)]
    out, _, _ = _established_then(tail)
    invs = [rng.invalidation for _, rng, _ in out if rng.invalidation]
    assert "ACCEPTED_BREAK" in invs


def test_max_duration_invalidation():
    cfg = default_cfg(max_duration_bars=40)
    out = run(osc_bars(cycles=14), cfg)[1]
    invs = [rng.invalidation for _, rng, _ in out if rng.invalidation]
    assert "MAX_DURATION" in invs


# ═══════════════════════ zero-lookahead / chunk / snapshot / instanțe ═══════════════════════
def test_zero_lookahead_future_bars_do_not_change_past():
    bars = osc_bars()
    _, out_full = run(bars)
    _, out_prefix = run(bars[:70])
    for i in range(70):
        a = out_full[i][1]; b = out_prefix[i][1]
        assert (a.available, a.consolidation_state, a.upper, a.lower, a.actionable_start_ts) == \
               (b.available, b.consolidation_state, b.upper, b.lower, b.actionable_start_ts)
        assert [e.as_dict() for e in out_full[i][2]] == [e.as_dict() for e in out_prefix[i][2]]


def _fps(out):
    seq = []
    for n1, rng, evs in out:
        seq.append((n1.output_fingerprint, rng.available, rng.consolidation_state, rng.boundary_validity,
                    rng.upper, rng.lower, rng.actionable_start_ts, tuple(e.kind for e in evs)))
    return seq


@pytest.mark.parametrize("chunks", [[116], [1, 115], [50, 66], [80, 20, 16], [95, 1, 20]])
def test_chunk_invariance_via_snapshot(chunks):
    cfg = default_cfg()
    bars = osc_bars(cycles=14) + [mk(112 + k, 2400, 2403, 2397, 2400) for k in range(4)]
    assert sum(chunks) == len(bars)
    ref, ref_out = run(bars, cfg)
    got = []
    eng = RangeStateReplayEngine(range_config=cfg, **KW)
    pos = 0
    for c in chunks:
        for b in bars[pos:pos + c]:
            got.append(eng.observe_closed_bar(b))
        snap = eng.snapshot()
        eng = RangeStateReplayEngine(range_config=cfg, **KW)
        eng.restore(snap)
        pos += c
    assert _fps(got) == _fps(ref_out)


def test_snapshot_restart_in_every_machine_state():
    """Snapshot/restore în FIECARE stare a mașinii (FORMING/ESTABLISHED/CANDIDATE/ACCEPTED) ⇒ identic."""
    cfg = default_cfg()
    base = osc_bars(cycles=12)
    eng0, out0 = run(base, cfg)
    last = [rng for _, rng, _ in out0 if rng.available][-1]
    u, l = last.upper, last.lower
    bars = base + [mk(len(base), u + 5, u + 8, u + 2, u + 5),        # candidate
                   mk(len(base) + 1, u + 6, u + 9, u + 3, u + 7),    # accepted
                   mk(len(base) + 2, u + 6, u + 8, u + 0.5, u + 4)]  # retest
    ref, ref_out = run(bars, cfg)
    # la fiecare punct de tăiere, snapshot→restore→continuă == continuu
    for cut in range(2 * cfg.swing_k + 2, len(bars)):
        eng = RangeStateReplayEngine(range_config=cfg, **KW)
        for b in bars[:cut]:
            eng.observe_closed_bar(b)
        snap = eng.snapshot()
        eng2 = RangeStateReplayEngine(range_config=cfg, **KW)
        eng2.restore(snap)
        tail = [eng2.observe_closed_bar(b) for b in bars[cut:]]
        assert _fps(tail) == _fps(ref_out[cut:]), f"divergență la restart cut={cut}"


def test_two_instances_no_shared_state():
    bars = osc_bars()
    ref, ref_out = run(bars)
    e1 = RangeStateReplayEngine(range_config=default_cfg(), **KW)
    e2 = RangeStateReplayEngine(range_config=default_cfg(), **KW)
    for b in bars[:40]:
        e1.observe_closed_bar(b)
    got2 = [e2.observe_closed_bar(b) for b in bars]
    assert _fps(got2) == _fps(ref_out)


# ═══════════════════════ precedență TREND_PAUSE ═══════════════════════
def test_trend_context_precedence_attribute():
    # TREND_UP fixture: N1 direction e trend; range (dacă apare) păstrează trend_context, nu-l pierde
    _, out = run(fx.trend_up_regime_bars())
    # precedence_rule intră în range_spec_id (hash-uit)
    cfg = default_cfg()
    assert "RANGE_STATE_OVER_TREND_PAUSE" == cfg.precedence_rule
    # când N1 arată direcție, rezultatele range disponibile poartă trend_context = direcția N1
    for n1, rng, _ in out:
        if rng.available:
            assert rng.trend_context == n1.raw_axes.direction


# ═══════════════════════ paritate stream swing-uri cu detect_swings ratificat ═══════════════════════
def test_confirmed_swing_stream_matches_detect_swings():
    bars = osc_bars()
    highs = [b.high for b in bars]; lows = [b.low for b in bars]
    prod2 = RangeStateProducer(default_cfg())
    stream = []
    for i, b in enumerate(bars):
        prod2._wh.append(b.high); prod2._wl.append(b.low); prod2._wts.append(b.ts_close)
        sw = prod2._detect_confirmed_swing(i)
        if sw is not None:
            stream.append((sw.idx, round(sw.price, 6), sw.is_high))
    # oracol: detect_swings ratificat pe tot istoricul
    block = _vb.Block(0, len(bars))
    oracle = [(s.idx, round(s.price, 6), s.kind.value == "high")
              for s in _vb.detect_swings(highs, lows, [block], k=default_cfg().swing_k)]
    assert stream == oracle


# ═══════════════════════ run_hash + interdicții ═══════════════════════
def test_run_hash_invalidates_on_data_and_config():
    bars = osc_bars()
    k1 = RangeStateReplayEngine(range_config=default_cfg(), **KW).replay_batch(bars).run_hash
    mutated = list(bars)
    mutated[-1] = mk(len(bars) - 1, 2400, 2500, 2300, 2450)
    k2 = RangeStateReplayEngine(range_config=default_cfg(), **KW).replay_batch(mutated).run_hash
    k3 = RangeStateReplayEngine(range_config=default_cfg(tol_atr=0.50), **KW).replay_batch(bars).run_hash
    assert k1 != k2 and k1 != k3


def test_restore_rejects_foreign_identity():
    bars = osc_bars(cycles=6)
    eng = RangeStateReplayEngine(range_config=default_cfg(), **KW)
    for b in bars:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    other_cfg = RangeStateReplayEngine(range_config=default_cfg(tol_atr=0.50), **KW)
    with pytest.raises(RangeSnapshotError):
        other_cfg.restore(snap)


def test_no_forbidden_imports_in_source():
    import ve_n1_replay.range_state as rs
    import ve_n1_replay.range_engine as re_
    import inspect
    for mod in (rs, re_):
        src = inspect.getsource(mod).lower()
        # tokeni de API/import interziși (nu simple mențiuni în proză — verificăm chemări/importuri concrete)
        for forbidden in ("metatrader5", "import mt5", "mt5.", "order_send", "set_authority", "probability_inputs"):
            assert forbidden not in src, f"{forbidden} prezent în {mod.__name__}"
    # niciun modul de broker încărcat la import
    import sys
    assert "MetaTrader5" not in sys.modules and "mt5" not in sys.modules
