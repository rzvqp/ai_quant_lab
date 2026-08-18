"""Teste DECISIVE — RANGE V2 PIN de configurație (0.3.1), `w_atr=0.30` RATIFICAT / `s_max=2×w_atr` DERIVAT.

Sursă normativă: Statistician STAT-RANGE-V2-PREREG-PROTOCOL-v1.0 @4e69e22 → STAT-RANGE-V2-WATR-FINAL-v1.0 @c29ac98
→ manifest v2.7.81 @2611d22 (fingerprint 432170ff…). NU accesează RC-07/RC-08/range1.pdf/range2.pdf/SEALED/OOS —
fixture-uri sintetice deterministe peste tot, inclusiv analogul controlului `RC-CONSTRUCTION-CHANNEL-NEW-01` (NU
episodul real, niciodată văzut — un fixture sintetic care reproduce semnătura S>>s_max calitativ).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import (
    RangeStateReplayEngineV2Pinned, RangeConfigV2Pinned, LegacyConfigRejectedError, RangeSnapshotErrorV2Pinned,
    RangeEventKindV2, N1IncrementalReplayEngine, entry_decision_v2, SAFETY_GUARD_RANGE_MID_NO_ENTRY,
    S_MAX_DERIVATION_FORMULA, RangeStateReplayEngineV2, RangeConfigV2, RangeStateProducerV2,
)
from tests import _fixtures as fx

Bar = r.Bar
KW = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)
# rezolvat din modulul chiar IMPORTAT — funcționează atât din arborele sursă, cât și dintr-un wheel instalat
# (site-packages), unde nu există niciun `ve_n1_replay/` FRATE lângă `tests/`
from ve_n1_replay import range_state_v2_1 as _rsv21_mod
_MODULE_DIR = Path(_rsv21_mod.__file__).resolve().parent


def mk(i, o, h, l, c):
    return Bar(symbol="XAUUSD", ts_open=i * 900, ts_close=(i + 1) * 900,
              open=float(o), high=float(h), low=float(l), close=float(c), volume=100.0)


def osc_bars(cycles=14, base=2400.0, start=0, hi=None, lo=None):
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
    base = dict(d_min_bars=24, atr_window=14, n_touch=2, retest_window_bars=12)
    base.update(kw)
    return RangeConfigV2Pinned.multiday(**{k: v for k, v in base.items() if k != "duration_class"})


def run_engine(bars, config=None):
    eng = RangeStateReplayEngineV2Pinned(range_config=config or cfg(), **KW)
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
    bars = osc_bars(cycles=cycles)
    eng, out = run_engine(bars, cfg_obj)
    last = [rng for _, rng, _ in out if rng.available][-1]
    return bars, eng, out, last.anchor_upper, last.anchor_lower


# ═══════════════════════ 1: default w_atr == 0.30 ═══════════════════════
def test_default_w_atr_is_0_30():
    assert RangeConfigV2Pinned().w_atr == 0.30
    assert RangeConfigV2Pinned.multiday().w_atr == 0.30
    assert RangeConfigV2Pinned.intraday().w_atr == 0.30


# ═══════════════════════ 2+3: semi-width / total zone width ═══════════════════════
def test_zone_semi_width_and_total_width():
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    atr = eng._range._last_atr
    established = [rng for _, rng, _ in out if rng.available and rng.w is not None][-1]
    assert established.w == pytest.approx(0.30 * atr)
    zone_span = established.boundary_zone_upper[1] - established.boundary_zone_upper[0]
    assert zone_span == pytest.approx(0.60 * atr)     # semilatime 0.30 x2 = latime totala 0.60xATR


# ═══════════════════════ 4: derived_s_max == 0.60 ═══════════════════════
def test_derived_s_max_is_0_60():
    c = RangeConfigV2Pinned.multiday()
    assert c.s_max == 0.60
    assert c.derived_s_max == 0.60


# ═══════════════════════ 5: modificarea w_atr modifică automat s_max ═══════════════════════
def test_w_atr_override_auto_updates_s_max():
    for w, expected_s in [(0.10, 0.20), (0.20, 0.40), (0.25, 0.50), (0.45, 0.90)]:
        c = RangeConfigV2Pinned(w_atr=w)
        assert c.s_max == pytest.approx(expected_s)
        assert c.derived_s_max == pytest.approx(expected_s)


# ═══════════════════════ 6: constructorul nu acceptă s_max independent ═══════════════════════
def test_constructor_rejects_independent_s_max():
    with pytest.raises(TypeError):
        RangeConfigV2Pinned(s_max=0.15)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        RangeConfigV2Pinned(w_atr=0.30, s_max=0.99)  # type: ignore[call-arg]


# ═══════════════════════ 7: parserul refuză câmpul s_max ═══════════════════════
def test_parser_from_dict_rejects_s_max_field():
    with pytest.raises(LegacyConfigRejectedError) as exc_info:
        RangeConfigV2Pinned.from_dict({"w_atr": 0.30, "s_max": 0.15})
    assert exc_info.value.reason_code == "LEGACY_S_MAX_REJECTED"
    # fara s_max trece
    c = RangeConfigV2Pinned.from_dict({"w_atr": 0.30, "n_touch": 3})
    assert c.w_atr == 0.30 and c.n_touch == 3


# ═══════════════════════ 8: snapshot/config legacy cu s_max=0.15 refuzat ═══════════════════════
def test_legacy_snapshot_s_max_0_15_refused():
    bars = osc_bars(cycles=6)
    legacy = RangeStateReplayEngineV2(range_config=RangeConfigV2(w_atr=0.25, s_max=0.15, d_min_bars=24), **KW)
    for b in bars:
        legacy.observe_closed_bar(b)
    legacy_snap = legacy.snapshot()
    pinned = RangeStateReplayEngineV2Pinned(range_config=cfg(), **KW)
    with pytest.raises(RangeSnapshotErrorV2Pinned):
        pinned.restore(legacy_snap)


def test_legacy_0_2_0_snapshot_also_refused():
    from ve_n1_replay import RangeStateReplayEngine as V1Engine, RangeConfig as V1Config
    bars = osc_bars(cycles=6)
    v1 = V1Engine(range_config=V1Config(), **KW)
    for b in bars:
        v1.observe_closed_bar(b)
    v1_snap = v1.snapshot()
    pinned = RangeStateReplayEngineV2Pinned(range_config=cfg(), **KW)
    with pytest.raises(RangeSnapshotErrorV2Pinned):
        pinned.restore(v1_snap)


# ═══════════════════════ 9: provenance conține formula derivată ═══════════════════════
def test_provenance_contains_derivation_formula():
    c = RangeConfigV2Pinned.multiday()
    prov = c.provenance()
    assert prov["s_max_derivation_formula"] == S_MAX_DERIVATION_FORMULA == "derived_s_max = 2 * w_atr"
    assert prov["derived_s_max"] == 0.60
    assert prov["w_atr"] == 0.30
    assert prov["statistician_prereg_commit"] == "4e69e22"
    assert prov["statistician_result_commit"] == "c29ac98"
    assert prov["statistician_manifest_commit"] == "2611d22"
    assert prov["statistician_manifest_fingerprint"] == (
        "432170ff5b6d0d20e125ea318d0293053f10ff0da8df9948bb470dde6d6501f6")


# ═══════════════════════ 10: fingerprint include w_atr + regula derivării ═══════════════════════
def test_config_fingerprint_includes_w_atr_and_derivation_rule():
    id_030 = RangeConfigV2(w_atr=0.30, s_max=0.60, d_min_bars=24).range_spec_id()
    id_031 = RangeConfigV2Pinned(w_atr=0.30, d_min_bars=24).range_spec_id()
    assert id_030 != id_031     # 0.3.1 include formula/versiune producător distinctă, nu doar valorile numerice
    # schimbarea lui w_atr schimbă fingerprint-ul
    id_a = RangeConfigV2Pinned(w_atr=0.30, d_min_bars=24).range_spec_id()
    id_b = RangeConfigV2Pinned(w_atr=0.20, d_min_bars=24).range_spec_id()
    assert id_a != id_b


# ═══════════════════════ 11: controlul de canal (analog S>>s_max) respins ca range ═══════════════════════
def test_channel_analog_of_construction_control_rejected():
    """Analog SINTETIC al `RC-CONSTRUCTION-CHANNEL-NEW-01` (S=3,3781, CHANNEL_UP) — NU episodul real, niciodată
    văzut de VE. Un drift care produce S apreciabil peste s_max=0,60 trebuie respins ca range."""
    bars = []
    price = 2380.0
    for i in range(140):
        o = price; c = price + 1.2; h = max(o, c) + 2; l = min(o, c) - 2
        bars.append(mk(i, o, h, l, c)); price = c
    _, out = run_engine(bars, cfg(d_min_bars=24))
    assert not any(rng.available and rng.structure_class == 'RANGE_STATE' for _, rng, _ in out)


# ═══════════════════════ 12: accepted range rămâne acceptat cu configurația finală ═══════════════════════
def test_accepted_range_stays_accepted_under_final_config():
    """Test DECIS al deciziei de clasificare (izolat de zgomotul motorului complet, ca la 0.3.0): close-uri
    PLATE (pantă 0.0 verificată direct) -> RANGE_STATE la configurația FINALĂ w_atr=0,30/s_max=0,60."""
    from collections import deque
    from ve_n1_replay.range_state_v2 import BoundaryValidityV2
    config = cfg(d_min_bars=10)._to_runtime_config()
    prod = RangeStateProducerV2(config)
    prod._closes = deque([2400.0] * 10, maxlen=10)
    assert prod._slope() == 0.0
    prod._boundary_validity = BoundaryValidityV2.CONFIRMED
    prod._structural_start_idx = 0; prod._n = 10; prod._last_atr = 4.0
    events: list = []
    prod._classify_and_maybe_establish(9000, 9, events)
    assert prod._structure_class.value == "RANGE_STATE"


# ═══════════════════════ 13+14: channel-up/down nu devine range ═══════════════════════
@pytest.mark.parametrize("drift", [0.15, 0.3, 0.5, 1.0])
def test_channel_up_never_range_state(drift):
    bars = []; price = 2380.0
    for i in range(140):
        o = price; c = price + drift; h = max(o, c) + 2; l = min(o, c) - 2
        bars.append(mk(i, o, h, l, c)); price = c
    _, out = run_engine(bars, cfg(d_min_bars=24))
    assert not any(rng.available and rng.structure_class == 'RANGE_STATE' for _, rng, _ in out)


@pytest.mark.parametrize("drift", [0.15, 0.3, 0.5, 1.0])
def test_channel_down_never_range_state(drift):
    bars = []; price = 2420.0
    for i in range(140):
        o = price; c = price - drift; h = max(o, c) + 2; l = min(o, c) - 2
        bars.append(mk(i, o, h, l, c)); price = c
    _, out = run_engine(bars, cfg(d_min_bars=24))
    assert not any(rng.available and rng.structure_class == 'RANGE_STATE' for _, rng, _ in out)


# ═══════════════════════ 15: cele 11 evenimente rămân reachabile ═══════════════════════
def test_all_11_events_reachable():
    seen = set()
    seen |= kinds(run_engine(osc_bars(cycles=14), cfg(d_min_bars=24))[1])
    # RANGE_ESTABLISHED are nevoie de un s_max mai permisiv, ca la 0.3.0 (reachability != calibrare implicita)
    loose = RangeConfigV2Pinned.multiday(d_min_bars=24, w_atr=2.0)   # w_atr mare -> s_max=4.0, doar pt. reachability
    seen |= kinds(run_engine(osc_bars(cycles=14), loose)[1])
    bars, eng, out, upper, lower = _established_prefix(cycles=6)
    prod = eng._range
    w = prod._cfg.w_atr * prod._last_atr
    n = len(bars)
    scenarios = [
        [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
         mk(n + 1, upper + w + 3, upper + w + 6, upper + w, upper + w + 4)],
        [mk(n, lower - w - 2, lower - w + 1, lower - w - 5, lower - w - 3),
         mk(n + 1, lower - w - 3, lower - w, lower - w - 6, lower - w - 4)],
        [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
         mk(n + 1, (upper + lower) / 2, (upper + lower) / 2 + 3, (upper + lower) / 2 - 3, (upper + lower) / 2)],
        [mk(n, upper + w + 2, upper + w + 5, upper + w - 1, upper + w + 3),
         mk(n + 1, upper + w + 3, upper + w + 6, upper + w, upper + w + 4),
         mk(n + 2, upper + w + 1, upper + w + 3, upper + w - 0.5, upper + w + 2)],
        [mk(n, upper + w - 2, upper + w + 8, upper + w - 4, upper + w - 3)],
    ]
    for scenario in scenarios:
        eng2 = RangeStateReplayEngineV2Pinned(range_config=cfg(d_min_bars=24), **KW)
        for b in bars:
            eng2.observe_closed_bar(b)
        for b in scenario:
            _, _, evs = eng2.observe_closed_bar(b)
            seen |= {e.kind for e in evs}
    expected = {e.value for e in RangeEventKindV2}
    missing = expected - seen
    assert not missing, f"evenimente nereachable: {missing}"


# ═══════════════════════ 16: F7 rămâne refuz explicit ═══════════════════════
def test_f7_explicit_refusal_zero_entry():
    bars = osc_bars(cycles=8)
    _, out = run_engine(bars, cfg(d_min_bars=10))
    mids = [e for e in all_events(out) if e.kind == RangeEventKindV2.RANGE_MID.value]
    assert mids
    for e in mids:
        assert e.safety_guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
        d = entry_decision_v2(e)
        assert d.permitted is False and d.guard == SAFETY_GUARD_RANGE_MID_NO_ENTRY
    led = RangeStateReplayEngineV2Pinned(range_config=cfg(d_min_bars=10), **KW).replay_batch(bars)
    assert led.n_guards > 0
    assert led.header()["safety_guards_register"] == ["RANGE_MID_NO_ENTRY"]


# ═══════════════════════ 17: snapshot/restart bit-identic ═══════════════════════
@pytest.mark.parametrize("chunks", [[112], [1, 111], [50, 62], [80, 20, 12], [95, 1, 16]])
def test_snapshot_restart_bit_identical(chunks):
    bars = osc_bars(cycles=14)
    assert sum(chunks) == len(bars)
    config = cfg(d_min_bars=10)
    ref, ref_out = run_engine(bars, config)
    got = []
    eng = RangeStateReplayEngineV2Pinned(range_config=config, **KW)
    pos = 0
    for c in chunks:
        for b in bars[pos:pos + c]:
            got.append(eng.observe_closed_bar(b))
        snap = eng.snapshot()
        eng = RangeStateReplayEngineV2Pinned(range_config=config, **KW)
        eng.restore(snap)
        pos += c
    assert _fps(got) == _fps(ref_out)


# ═══════════════════════ 18: zero-lookahead ═══════════════════════
def test_zero_lookahead():
    bars = osc_bars(cycles=10)
    _, out_full = run_engine(bars)
    _, out_prefix = run_engine(bars[:50])
    for i in range(50):
        assert _fps(out_full)[i] == _fps(out_prefix)[i]


# ═══════════════════════ 19: N1 0.1.1 byte-identic ═══════════════════════
@pytest.mark.parametrize("gen", [fx.trend_up_regime_bars, fx.trend_down_regime_bars,
                                 lambda: fx.uncertain_regime_bars(n=150), osc_bars])
def test_n1_byte_identical_0_1_1(gen):
    bars = gen()
    eng = RangeStateReplayEngineV2Pinned(range_config=cfg(), **KW)
    bare = N1IncrementalReplayEngine(**KW)
    for b in bars:
        n1, _, _ = eng.observe_closed_bar(b)
        assert n1.output_fingerprint == bare.observe_closed_bar(b).output_fingerprint


# ═══════════════════════ 20: regresie completă 0.3.0→0.3.1 pt. componentele NEAFECTATE ═══════════════════════
def test_0_3_1_reuses_0_3_0_producer_class_unchanged():
    """Dovadă STRUCTURALĂ de reutilizare — nu doar comportamentală: `RangeStateReplayEngineV2Pinned` folosește
    LITERAL clasa `RangeStateProducerV2` (0.3.0), nu o reimplementare."""
    eng = RangeStateReplayEngineV2Pinned(range_config=cfg(), **KW)
    assert isinstance(eng._range, RangeStateProducerV2)
    assert type(eng._range).__module__.endswith("range_state_v2")   # 0.3.0, nu range_state_v2_1


def test_median_anchor_touch_persistence_regression_still_holds_at_0_3_1():
    """Regresia dovedită la 0.3.0 (mediana nu se auto-invalidează) ține IDENTIC la 0.3.1 — logica e literalmente
    aceeași clasă, doar valorile w_atr/s_max diferă."""
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

    config = cfg(d_min_bars=10)
    _, out = run_engine(bars, config)
    touches = [rng.touches_upper for _, rng, _ in out if rng.available and rng.touches_upper is not None]
    assert touches == sorted(touches)
    confirmed_before = any(rng.boundary_validity == 'CONFIRMED' for _, rng, _ in out[:80])
    confirmed_well_after = any(rng.boundary_validity == 'CONFIRMED' for _, rng, _ in out[95:])
    assert confirmed_before and confirmed_well_after


def test_internal_bos_choch_descriptor_still_non_invalidating():
    bars = osc_bars(cycles=6)
    base = 2400.0; i = len(bars)
    bars += [mk(i, base + 2, base + 6, base + 1, base + 5), mk(i + 1, base + 5, base + 6, base + 3, base + 4),
            mk(i + 2, base + 4, base + 5, base + 1, base + 2), mk(i + 3, base + 2, base + 3, base - 1, base),
            mk(i + 4, base, base + 1, base - 2, base - 1)]
    i += 5
    bars += osc_bars(cycles=6, start=i)
    _, out = run_engine(bars, cfg(d_min_bars=10))
    machine_survived = any(rng.available and rng.boundary_validity in ('PROVISIONAL', 'CONFIRMED')
                           for _, rng, _ in out[-40:])
    assert machine_survived


def test_two_instances_no_shared_state():
    bars = osc_bars(cycles=10)
    config = cfg(d_min_bars=10)
    ref, ref_out = run_engine(bars, config)
    e1 = RangeStateReplayEngineV2Pinned(range_config=config, **KW)
    e2 = RangeStateReplayEngineV2Pinned(range_config=config, **KW)
    for b in bars[:30]:
        e1.observe_closed_bar(b)
    got2 = [e2.observe_closed_bar(b) for b in bars]
    assert _fps(got2) == _fps(ref_out)
    assert e1.bars_observed == 30 and e2.bars_observed == len(bars)


def test_determinism():
    bars = osc_bars(cycles=10)
    _, out1 = run_engine(bars)
    _, out2 = run_engine(bars)
    assert _fps(out1) == _fps(out2)


# ═══════════════════════ gard structural/AST: 0.15 NU mai există ca literal de producție ═══════════════════════
def test_ast_guard_no_0_15_literal_in_new_production_modules():
    for fname in ("range_state_v2_1.py", "range_engine_v2_1.py"):
        src = (_MODULE_DIR / fname).read_text(encoding="utf-8")
        tree = ast.parse(src, filename=fname)
        literals = [n.value for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)]
        assert 0.15 not in literals, f"{fname} conține literalul 0.15 (NERATIFICAT, interzis în producția 0.3.1)"


def test_ast_guard_0_30_is_the_only_w_atr_literal_source():
    """`0.30` apare DOAR ca referință la `W_ATR_CANONICAL` (version.py) — nu hard-codat separat în range_state_v2_1."""
    src = (_MODULE_DIR / "range_state_v2_1.py").read_text(encoding="utf-8")
    assert "W_ATR_CANONICAL" in src
    tree = ast.parse(src)
    literals = [n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, float)]
    assert 0.30 not in literals, "0.30 trebuie referențiat prin W_ATR_CANONICAL, nu hard-codat ca literal separat"


def test_no_forbidden_imports_in_source():
    import inspect
    from ve_n1_replay import range_state_v2_1 as m1, range_engine_v2_1 as m2
    for mod in (m1, m2):
        src = inspect.getsource(mod).lower()
        for forbidden in ("metatrader5", "import mt5", "mt5.", "order_send", "set_authority", "probability_inputs"):
            assert forbidden not in src
    import sys
    assert "MetaTrader5" not in sys.modules and "mt5" not in sys.modules
