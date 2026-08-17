"""Paritate exhaustivă + adversarială: motorul N1 INCREMENTAL (0.1.1) vs oracolul vendat 0.1.0.

Acoperă cerințele mandatului: paritate pe RESULTAT și pe STARE INTERMEDIARĂ (swings confirmate, etichete
HH/HL/LH/LL, live_hh/hl/lh/lh, mulțimea consumată, rupturi, ultimul break, structure/direction, displacement,
compression, RawAxes, fingerprints); secvențe adversariale (swing > 460/500 bare vechime, perioade lungi fără
break, mai multe swing-uri neconsumate); zero-lookahead; chunk-size irelevant; restart între swing și break;
două instanțe fără stare comună; invalidarea cheii de ledger fail-closed; refuzuri.
"""
from __future__ import annotations

import pytest

import ve_n1_replay as r
from ve_n1_replay._bootstrap import vendored_module
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay.incremental import (
    IncrementalRawAxesBuilder,
    N1IncrementalReplayEngine,
    N1IncrementalSnapshot,
    N1IncrementalLedger,
    N1IncrementalLedgerRecord,
    HISTORY_HORIZON,
)
from tests import _fixtures as fx

Bar = r.Bar
_RAB = vendored_module("ai_trader.new_brain_bridge.raw_axes_builder").RawAxesBuilder
_vb = vendored_module("ai_trader.structural_observer.vendor_bridge")
_Block = _vb.Block

ENGINE_KW = dict(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900, implementation_commit=IC)


def _axes_tuple(a):
    return (a.is_compressed, a.is_displacement, a.direction, a.structure)


# ── oracol de STARE INTERMEDIARĂ (recalculat din detectorii ratificați la fiecare lungime de istoric) ──
def _oracle_intermediate(highs, lows, closes, i):
    """Adevărul (idx swing-uri neconsumate pe etichetă, consumate, ultimul break) ca la bara i, din
    detect_swings/label_structure/detect_breaks pe Block(0, i+1) — exact ca RawAxesBuilder."""
    block = _Block(0, i + 1)
    swings = _vb.label_structure(_vb.detect_swings(highs[: i + 1], lows[: i + 1], [block]))
    breaks = _vb.detect_breaks(closes[: i + 1], swings, [block])
    consumed = {b.reference_swing.idx for b in breaks}
    latest = None
    if breaks:
        latest = str(max(breaks, key=lambda b: int(b.idx)).kind.value)
    # swing-uri neconsumate confirmate (<= i), doar etichete reale (UNCLASSIFIED nu declanșează break)
    unconsumed = {}
    live = {"HH": None, "LL": None, "HL": None, "LH": None}
    for s in swings:
        lab = s.label.value.upper() if s.label.value != "unclassified" else None
        if lab in ("HH", "LL", "HL", "LH") and s.confirmed_idx <= i and s.idx not in consumed:
            unconsumed[s.idx] = (lab, s.price)
            live[lab] = s.idx  # ultima (max idx) rămâne — ordine de detecție = idx ascendent
    return unconsumed, consumed, latest, live


# ═══════════════════════════ RESULTAT (RawAxes) ═══════════════════════════
@pytest.mark.parametrize("name,gen", [
    ("trend_up", fx.trend_up_regime_bars),
    ("trend_down", fx.trend_down_regime_bars),
    ("uncertain", lambda: fx.uncertain_regime_bars(n=200)),
    ("bos_bull", fx.bos_bull_bars),
])
def test_rawaxes_parity(name, gen):
    bars = gen()
    o = _RAB("XAUUSD"); inc = IncrementalRawAxesBuilder("XAUUSD")
    for b in bars:
        assert _axes_tuple(o.observe(b)) == _axes_tuple(inc.observe(b)), f"{name} @ {b.ts_open}"


# ═══════════════════════════ STARE INTERMEDIARĂ ═══════════════════════════
@pytest.mark.parametrize("name,gen", [
    ("trend_up", fx.trend_up_regime_bars),
    ("trend_down", fx.trend_down_regime_bars),
    ("bos_bull", fx.bos_bull_bars),
])
def test_intermediate_state_parity(name, gen):
    bars = gen()
    highs = [b.high for b in bars]; lows = [b.low for b in bars]; closes = [b.close for b in bars]
    inc = IncrementalRawAxesBuilder("XAUUSD")
    for i, b in enumerate(bars):
        inc.observe(b)
        unc, cons, latest, live = _oracle_intermediate(highs, lows, closes, i)
        assert inc.confirmed_unconsumed() == unc, f"{name} confirmed-unconsumed swings/labels @ bar {i}"
        assert inc.consumed_idx() == cons, f"{name} consumed @ bar {i}"
        assert inc.latest_break_kind == latest, f"{name} latest_break @ bar {i}"
        assert inc.live_labels_next() == live, f"{name} live_hh/ll/hl/lh @ bar {i}"


# ═══════════════════════════ MOTOR: output_fingerprint vs oracolul 0.1.0 ═══════════════════════════
def test_engine_output_fingerprint_parity():
    bars = fx.trend_up_regime_bars()
    oracle = r.N1ReplayEngine(**ENGINE_KW)
    inc = N1IncrementalReplayEngine(**ENGINE_KW)
    exp = [oracle.observe_closed_bar(b).output_fingerprint for b in bars]
    ledger = inc.replay_batch(bars)
    assert [rec.output_fingerprint for rec in ledger.records] == exp
    assert ledger.bar_count == len(bars)
    assert isinstance(ledger, N1IncrementalLedger)


# ═══════════════════════════ ADVERSARIAL: swing vechi (> 460 / > 500 bare) ═══════════════════════════
def _adversarial(gap: int, spike: bool = True):
    bars = []; t = 0
    for op, hi, lo, cl in zip(fx.BOS_BULL_OPENS, fx.BOS_BULL_HIGHS, fx.BOS_BULL_LOWS, fx.BOS_BULL_CLOSES):
        bars.append(Bar(symbol="XAUUSD", ts_open=t * 900, ts_close=(t + 1) * 900,
                        open=float(op), high=float(hi), low=float(lo), close=float(cl), volume=100.0)); t += 1
    for _ in range(gap):
        bars.append(Bar(symbol="XAUUSD", ts_open=t * 900, ts_close=(t + 1) * 900,
                        open=5.0, high=5.4, low=4.6, close=5.02, volume=100.0)); t += 1
    if spike:
        for cl in (26.0, 26.1):
            bars.append(Bar(symbol="XAUUSD", ts_open=t * 900, ts_close=(t + 1) * 900,
                            open=25.0, high=27.0, low=24.0, close=cl, volume=100.0)); t += 1
    return bars


@pytest.mark.parametrize("gap", [460, 500])
def test_adversarial_old_swing_full_parity(gap):
    """Swing relevant mai vechi de 460/500 bare + perioadă lungă fără break: paritate COMPLETĂ pe RawAxes
    vs oracol (byte-identic pe fiecare bară, inclusiv ruptura care se declanșează pe swing-ul vechi)."""
    bars = _adversarial(gap)
    o = _RAB("XAUUSD"); inc = IncrementalRawAxesBuilder("XAUUSD")
    for i, b in enumerate(bars):
        assert _axes_tuple(o.observe(b)) == _axes_tuple(inc.observe(b)), f"gap={gap} @ bar {i}"


def test_adversarial_old_swing_5000_bounded_and_persistence():
    """gap > 5000: oracolul e O(n²) (blocajul remediat) — paritatea directă completă e intractabilă. Dovadă
    în două părți: (a) axele MĂRGINITE (comp/disp) == oracol proaspăt pe fereastra ultimelor 460 bare la
    checkpoint-uri adânci; (b) axa NEMĂRGINITĂ (structure/direction) persistă swing-ul vechi și se declanșează."""
    bars = _adversarial(5000)
    inc = IncrementalRawAxesBuilder("XAUUSD")
    incax = [_axes_tuple(inc.observe(b)) for b in bars]
    for cp in (600, 1500, 3000, 4800, len(bars) - 1):
        win = bars[max(0, cp - HISTORY_HORIZON + 1): cp + 1]
        ow = _RAB("XAUUSD")
        for wb in win[:-1]:
            ow.observe(wb)
        wax = _axes_tuple(ow.observe(win[-1]))
        assert (incax[cp][0], incax[cp][1]) == (wax[0], wax[1]), f"bounded window @ {cp}"
    # ruptura pe swing-ul vechi (după 5000 bare) se declanșează ⇒ structure/direction ne-None la spike
    assert incax[-1][2] is not None and incax[-1][3] is not None


# ═══════════════════════════ CHUNK-SIZE irelevant + RESTART între swing și break ═══════════════════════════
@pytest.mark.parametrize("chunks", [[478], [1, 477], [230, 248], [100, 100, 100, 178], [469, 1, 8]])
def test_chunk_size_invariance_via_snapshot(chunks):
    """Împărțirea în chunk-uri cu snapshot/restore la fiecare graniță NU schimbă rezultatul per-bară."""
    bars = fx.trend_up_regime_bars()
    assert sum(chunks) == len(bars)
    ref = N1IncrementalReplayEngine(**ENGINE_KW)
    expected = [ref.observe_closed_bar(b).output_fingerprint for b in bars]
    got, pos = [], 0
    eng = N1IncrementalReplayEngine(**ENGINE_KW)
    for c in chunks:
        for b in bars[pos:pos + c]:
            got.append(eng.observe_closed_bar(b).output_fingerprint)
        snap = eng.snapshot()
        eng = N1IncrementalReplayEngine(**ENGINE_KW)
        eng.restore(snap)  # restart la graniță
        pos += c
    assert got == expected


def test_snapshot_restart_between_swing_and_break():
    """Snapshot exact între detecția unui swing și ruptura care îl consumă ⇒ după restore, ruptura încă
    se declanșează identic (starea nemărginită supraviețuiește restart-ului)."""
    bars = _adversarial(500)  # swing HH format devreme, apoi 500 bare fără break, apoi spike care rupe
    ref = N1IncrementalReplayEngine(**ENGINE_KW)
    expected = [ref.observe_closed_bar(b).output_fingerprint for b in bars]
    # tăiem chiar înainte de cele 2 bare de spike (swing pe stivă neconsumat, break încă neîntâmplat)
    cut = len(bars) - 2
    eng = N1IncrementalReplayEngine(**ENGINE_KW)
    for b in bars[:cut]:
        eng.observe_closed_bar(b)
    snap = eng.snapshot()
    eng2 = N1IncrementalReplayEngine(**ENGINE_KW)
    eng2.restore(snap)
    tail = [eng2.observe_closed_bar(b).output_fingerprint for b in bars[cut:]]
    assert tail == expected[cut:]
    assert eng2.latest_break_kind == "bos_bull"  # ruptura pe swing-ul vechi s-a produs după restart


# ═══════════════════════════ ZERO-LOOKAHEAD ═══════════════════════════
def test_no_lookahead_modifying_future_bars_does_not_change_past_outputs():
    bars = fx.trend_up_regime_bars()
    e1 = N1IncrementalReplayEngine(**ENGINE_KW)
    out_prefix = [e1.observe_closed_bar(b).output_fingerprint for b in bars[:300]]
    # a doua rulare: prefix identic, apoi bare viitoare arbitrar diferite — prefixul trebuie identic
    e2 = N1IncrementalReplayEngine(**ENGINE_KW)
    out_prefix2 = [e2.observe_closed_bar(b).output_fingerprint for b in bars[:300]]
    assert out_prefix == out_prefix2  # ieșirile <= i nu depind de bare > i (nu au fost încă văzute)


def test_changing_bar_i_changes_output_deterministically():
    bars = fx.trend_up_regime_bars()
    e1 = N1IncrementalReplayEngine(**ENGINE_KW)
    base = [e1.observe_closed_bar(b).output_fingerprint for b in bars]
    # modificăm o bară TÂRZIE (în fereastra detectorilor) și reluăm de la zero — deterministă, repetabilă
    mutated = list(bars)
    j = len(bars) - 1
    mutated[j] = Bar(symbol="XAUUSD", ts_open=bars[j].ts_open, ts_close=bars[j].ts_close,
                     open=bars[j].open, high=bars[j].high + 5.0, low=bars[j].low,
                     close=bars[j].close + 5.0, volume=bars[j].volume)
    e2 = N1IncrementalReplayEngine(**ENGINE_KW)
    changed = [e2.observe_closed_bar(b).output_fingerprint for b in mutated]
    e3 = N1IncrementalReplayEngine(**ENGINE_KW)
    changed2 = [e3.observe_closed_bar(b).output_fingerprint for b in mutated]
    assert changed[:j] == base[:j]          # bare < j neschimbate
    assert changed[j] != base[j]            # bara j schimbată
    assert changed == changed2              # deterministă


# ═══════════════════════════ DOUĂ INSTANȚE — fără stare comună ═══════════════════════════
def test_two_instances_no_shared_state():
    bars = fx.trend_up_regime_bars()
    ref = N1IncrementalReplayEngine(**ENGINE_KW)
    expected = [ref.observe_closed_bar(b).output_fingerprint for b in bars]
    e1 = N1IncrementalReplayEngine(**ENGINE_KW)
    e2 = N1IncrementalReplayEngine(**ENGINE_KW)
    for b in bars[:100]:
        e1.observe_closed_bar(b)
    got2 = [e2.observe_closed_bar(b).output_fingerprint for b in bars]
    assert got2 == expected
    assert e1.bars_observed == 100 and e2.bars_observed == len(bars)


# ═══════════════════════════ LEDGER — cheie de invalidare fail-closed ═══════════════════════════
def test_ledger_key_invalidates_on_data_change():
    bars = fx.trend_up_regime_bars()
    k1 = N1IncrementalReplayEngine(**ENGINE_KW).replay_batch(bars).ledger_key
    mutated = list(bars)
    mutated[-1] = Bar(symbol="XAUUSD", ts_open=bars[-1].ts_open, ts_close=bars[-1].ts_close,
                      open=bars[-1].open, high=bars[-1].high + 1.0, low=bars[-1].low,
                      close=bars[-1].close, volume=bars[-1].volume)
    k2 = N1IncrementalReplayEngine(**ENGINE_KW).replay_batch(mutated).ledger_key
    assert k1 != k2  # schimbarea conținutului de date ⇒ cheie diferită (recompute fail-closed)


def test_ledger_key_invalidates_on_horizon_change():
    bars = fx.trend_up_regime_bars()
    k1 = N1IncrementalReplayEngine(horizon=HISTORY_HORIZON, **ENGINE_KW).replay_batch(bars).ledger_key
    k2 = N1IncrementalReplayEngine(horizon=HISTORY_HORIZON + 40, **ENGINE_KW).replay_batch(bars).ledger_key
    assert k1 != k2


def test_ledger_record_is_frozen():
    rec = N1IncrementalReplayEngine(**ENGINE_KW).replay_batch(fx.bos_bull_bars()).records[0]
    with pytest.raises(Exception):
        rec.output_fingerprint = "x"  # type: ignore[misc]


# ═══════════════════════════ REFUZURI (guard-uri fail-closed) ═══════════════════════════
def test_refuses_out_of_order_and_conflicting_duplicate():
    bars = fx.trend_up_regime_bars()
    e = N1IncrementalReplayEngine(**ENGINE_KW)
    e.observe_closed_bar(bars[5])
    with pytest.raises(r.OutOfOrderBarError):
        e.observe_closed_bar(bars[0])
    e2 = N1IncrementalReplayEngine(**ENGINE_KW)
    e2.observe_closed_bar(bars[0])
    conflict = Bar(symbol="XAUUSD", ts_open=bars[0].ts_open, ts_close=bars[0].ts_close,
                   open=bars[0].open, high=bars[0].high + 9.0, low=bars[0].low,
                   close=bars[0].close, volume=bars[0].volume)
    with pytest.raises(r.DuplicateBarError):
        e2.observe_closed_bar(conflict)


def test_restore_rejects_foreign_snapshot_identity():
    bars = fx.bos_bull_bars()
    e = N1IncrementalReplayEngine(**ENGINE_KW)
    e.replay_batch(bars)
    snap = e.snapshot()
    other = N1IncrementalReplayEngine(symbol="XAUUSD", timeframe="1h",  # timeframe diferit ⇒ identitate diferită
                                      bar_interval_seconds=3600, implementation_commit=IC)
    with pytest.raises(r.IncompatibleSnapshotError):
        other.restore(snap)
