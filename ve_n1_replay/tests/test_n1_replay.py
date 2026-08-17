"""ve_n1_replay — teste decisive: byte-integritate (AI Trader @21ae632 + detectori @61cbd58c separat), izolare +
coliziune fail-closed cu detectorii ve_tower preîncărcați, suprafață + refuzuri, determinism, acoperire de regim,
zero importuri interzise. Se rulează din wheel-ul instalat, cu repo-ul AI Trader ABSENT din sys.path."""

from __future__ import annotations

import hashlib
import math
import os
import sys
import types

import pytest

import ve_n1_replay as r
from ve_n1_replay.version import VENDORED_AI_BLOB_SHA1, VENDORED_DETECTOR_BLOB_SHA1
from tests import _fixtures as fx

_PKG_DIR = os.path.dirname(os.path.abspath(r.__file__))


def _git_blob(data: bytes) -> str:
    h = hashlib.sha1(); h.update(b"blob " + str(len(data)).encode() + b"\x00" + data); return h.hexdigest()


# ═══ byte-integritate (identități SEPARATE) ═══
def test_ai_trader_modules_byte_identical_to_21ae632() -> None:
    for rel, exp in VENDORED_AI_BLOB_SHA1.items():
        data = open(os.path.join(_PKG_DIR, "_ai", "ai_trader", *rel.split("/")), "rb").read()
        assert _git_blob(data) == exp, f"ai_trader/{rel} NU e byte-identic cu @21ae632"


def test_detectors_byte_identical_to_61cbd58c() -> None:
    for name, exp in VENDORED_DETECTOR_BLOB_SHA1.items():
        data = open(os.path.join(_PKG_DIR, "_det", name), "rb").read()
        assert _git_blob(data) == exp, f"{name} NU e byte-identic cu @61cbd58c"
    # market_structure DIFERĂ de ve_tower (identitate proprie, nu substituită)
    assert VENDORED_DETECTOR_BLOB_SHA1["market_structure.py"] == "52bb1eba76d1dee96fae3ed5f5e434c53612176a"


# ═══ izolare + coliziune fail-closed ═══
def test_ai_trader_repo_absent_from_syspath() -> None:
    # niciun element de sys.path nu conține un repo ai_trader real (doar namespace-ul vendat, intern)
    for p in sys.path:
        assert not os.path.isdir(os.path.join(p, "ai_trader", "new_brain_live")), "repo ai_trader real pe path"


def test_no_forbidden_imports_loaded() -> None:
    for bad in ("MetaTrader5", "ve_tower", "ai_trader.new_brain_live", "ai_trader.execution_orchestrator"):
        assert bad not in sys.modules, f"import interzis prezent: {bad}"


def test_collision_with_foreign_detector_is_fail_closed() -> None:
    import ve_n1_replay._bootstrap as b
    saved = {n: sys.modules.get(n) for n in (list(b._DETECTOR_ORDER) + list(b._AITRADER_ORDER) + list(b._NAMESPACE_PACKAGES))}
    foreign = types.ModuleType("market_structure")           # STRĂIN (ex. ve_tower), fără marcaj
    try:
        with b._lock:
            for n in list(b._DETECTOR_ORDER) + list(b._AITRADER_ORDER) + list(b._NAMESPACE_PACKAGES):
                sys.modules.pop(n, None)
            b._loaded = False
        sys.modules["market_structure"] = foreign
        with pytest.raises(b.N1ReplayLoadCollisionError):
            b.ensure_loaded()
        # zero reziduuri: niciun modul al nostru rămas; host neatins (același obiect)
        assert sys.modules["market_structure"] is foreign
        assert "ai_trader.n1_replay.engine" not in sys.modules and "market_state" not in sys.modules
        assert b._loaded is False
    finally:
        sys.modules.pop("market_structure", None)
        for n, m in saved.items():
            if m is not None:
                sys.modules[n] = m
        with b._lock:
            b._loaded = False
        b.ensure_loaded()


def test_two_independent_instances_unshared_state() -> None:
    e1 = r.initialize(symbol="XAUUSD", timeframe="M15", bar_interval_seconds=900)
    e2 = r.initialize(symbol="XAUUSD", timeframe="M15", bar_interval_seconds=900)
    bars = fx.uncertain_regime_bars()
    e1.replay(bars)
    assert e1 is not e2 and e2._observed_bars == []            # e2 neatins de e1


# ═══ suprafață + refuzuri ═══
def _engine() -> object:
    return r.initialize(symbol="XAUUSD", timeframe="M15", bar_interval_seconds=900)


def test_surface_methods_present() -> None:
    e = _engine()
    for m in ("observe_closed_bar", "replay", "snapshot", "restore", "reset"):
        assert callable(getattr(e, m))


def test_duplicate_bar_refused() -> None:
    # re-observing the IDENTICAL bar is idempotent; a CONFLICTING bar for the same slot ⇒ DuplicateBarError
    e = _engine(); bars = fx.uncertain_regime_bars(n=20)
    e.replay(bars)
    same = e.observe_closed_bar(bars[-1])                     # identic ⇒ rezultat cache (fără dublare)
    assert same is e._last_result
    last = bars[-1]
    conflict = r.Bar(symbol=last.symbol, ts_open=last.ts_open, ts_close=last.ts_close, open=last.open,
                     high=last.high + 5.0, low=last.low, close=last.close, volume=last.volume)
    with pytest.raises(r.DuplicateBarError):
        e.observe_closed_bar(conflict)


def test_out_of_order_bar_refused() -> None:
    e = _engine(); bars = fx.uncertain_regime_bars(n=20)
    e.replay(bars)
    with pytest.raises(r.OutOfOrderBarError):
        e.observe_closed_bar(bars[5])                          # timp anterior ⇒ refuz


def test_nan_bar_refused() -> None:
    e = _engine(); bars = fx.uncertain_regime_bars(n=20)
    e.replay(bars[:-1])
    last = bars[-1]
    nan_bar = r.Bar(symbol=last.symbol, ts_open=last.ts_open, ts_close=last.ts_close, open=last.open,
                    high=float("nan"), low=last.low, close=last.close, volume=last.volume)
    with pytest.raises(r.NonFiniteAxesInputError):
        e.observe_closed_bar(nan_bar)


def test_snapshot_restore_continues_identically() -> None:
    bars = fx.trend_up_regime_bars()
    e = _engine(); e.replay(bars[:-5]); snap = e.snapshot()
    tail_a = e.replay(bars[-5:])
    e2 = _engine(); e2.restore(snap); tail_b = e2.replay(bars[-5:])
    assert tuple(x.output_fingerprint for x in tail_a) == tuple(x.output_fingerprint for x in tail_b)


def test_incompatible_snapshot_fail_closed() -> None:
    e = _engine()
    bad = r.N1ReplaySnapshot(identity=e.identity, observed_bars=(), snapshot_taken_at_bars_observed=0)
    e_other = r.initialize(symbol="ES", timeframe="M15", bar_interval_seconds=900)   # altă identitate
    with pytest.raises(r.IncompatibleSnapshotError):
        e_other.restore(bad)


# ═══ determinism + regim ═══
def test_same_bars_same_outputs_and_fingerprints() -> None:
    bars = fx.trend_up_regime_bars()
    a = _engine().replay(bars); b = _engine().replay(bars)
    assert tuple(x.output_fingerprint for x in a) == tuple(x.output_fingerprint for x in b)
    assert tuple(tuple(sorted(x.applicable_regimes)) for x in a) == tuple(tuple(sorted(x.applicable_regimes)) for x in b)


def test_modified_bar_changes_output_identity() -> None:
    # output_fingerprint e amprenta OHLC-sensibilă; o bară din fereastra de influență (spre final) ⇒ altă amprentă
    bars = fx.trend_up_regime_bars()
    base = _engine().replay(bars)[-1]
    mod = list(bars); mb = mod[-1]
    mod[-1] = r.Bar(symbol=mb.symbol, ts_open=mb.ts_open, ts_close=mb.ts_close, open=mb.open, high=mb.high + 25.0,
                    low=mb.low, close=mb.close + 25.0, volume=mb.volume)
    changed = _engine().replay(tuple(mod))[-1]
    assert changed.output_fingerprint != base.output_fingerprint


def test_trend_up_fixture_resolves_trend_up() -> None:
    last = _engine().replay(fx.trend_up_regime_bars())[-1]
    assert "TREND_UP" in last.applicable_regimes and last.availability_status == "FULL"


def test_uncertain_fixture_is_uncertain() -> None:
    last = _engine().replay(fx.uncertain_regime_bars())[-1]
    assert "UNCERTAIN" in last.applicable_regimes


def test_trend_down_fixture_available_and_not_trend_up() -> None:
    last = _engine().replay(fx.trend_down_regime_bars())[-1]
    assert last.availability_status == "FULL" and "TREND_UP" not in last.applicable_regimes


def test_no_probability_or_authority_on_result() -> None:
    last = _engine().replay(fx.uncertain_regime_bars())[-1]
    assert not any(hasattr(last, a) for a in ("probability_inputs", "authority", "order", "broker"))
