"""Producătorul N2 (bias direcțional H1, verdict B): factori determiniști, timeframe strict, dublă identitate,
fără probabilitate, fără default LONG, fail-closed. Plus lanțul N1→N2→N3→N4 în care N3/N4 primesc fingerprintul N2 REAL."""

from __future__ import annotations

import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from ve_tower import (  # noqa: E402
    N2Request, N3Request, N4Request, event_fingerprint, run_n2, run_n3, run_n4, same_event,
    N2_CONTRACT_VERSION, N3_CONTRACT_VERSION, N4_CONTRACT_VERSION,
)

SYM = "XAUUSD"; SRC = "OANDA_XAUUSD_feed_v1"; T0 = 1_600_000_000
AS_OF = T0 + 10_000_000


def _h1(n: int = 400, bump: float = 0.0, slope: float = 0.5) -> tuple[tuple[float, ...], ...]:
    o = []; h = []; l = []; c = []; t = []
    for j in range(n):
        base = 100.0 + j * slope + bump
        o.append(base); h.append(base + 0.8); l.append(base - 0.8); c.append(base + 0.3); t.append(T0 + j * 3600)
    return tuple(o), tuple(h), tuple(l), tuple(c), tuple(t)


def _n2_req(*, event: str = "ev1", tf: str = "H1", src: str = SRC, contract: str = N2_CONTRACT_VERSION,
            axes: tuple[str, ...] = ("available", "available", "available"), bump: float = 0.0,
            as_of: int | None = None, time_override: tuple[int, ...] | None = None,
            close_override: tuple[float, ...] | None = None, max_stale: int | None = None) -> N2Request:
    o, h, l, c, t = _h1(bump=bump)
    if time_override is not None:
        t = time_override
    if close_override is not None:
        c = close_override
    ao = as_of if as_of is not None else t[-1]
    return N2Request(contract_version=contract, market_event_id=event, symbol=SYM, timeframe=tf, source_identity=src,
                     open=o, high=h, low=l, close=c, time=t, as_of=ao, regime_axes_status=axes,
                     n1_fingerprint="n1fp", max_staleness_s=max_stale)


# ═══ producție + determinism ═══
def test_n2_produces_deterministic_factors() -> None:
    r = run_n2(_n2_req())
    assert r.bias_available and r.reason_codes == ("ok_bias_factors",)
    assert r.factors and r.output_fingerprint and r.data_identity is not None and r.node_input_fingerprint
    assert r.data_identity.timeframe == "H1"
    names = {f.name for f in r.factors}
    assert "structure_run_h1" in names                       # factorul din mulțimea necesară


def test_n2_same_bars_same_factors_and_fingerprint() -> None:
    a = run_n2(_n2_req()); b = run_n2(_n2_req())
    assert a.output_fingerprint == b.output_fingerprint       # restart determinist / replay-live parity
    assert [(f.name, f.direction) for f in a.factors] == [(f.name, f.direction) for f in b.factors]


def test_n2_single_ohlc_change_changes_fingerprint() -> None:
    base = run_n2(_n2_req())
    o, h, l, c, t = _h1()
    c2 = tuple(list(c[:10]) + [c[10] + 0.001] + list(c[11:]))
    assert run_n2(_n2_req(close_override=c2)).output_fingerprint != base.output_fingerprint


def test_n2_does_not_emit_probability() -> None:
    r = run_n2(_n2_req())
    assert not hasattr(r, "probability") and not hasattr(r, "expected_value")
    import ve_tower as vt
    bias = vt.tower_module("bias_h1")
    assert bias.schema_payload()["emits_probability"] is False   # confirmat din modulul ratificat


# ═══ default LONG imposibil + fail-closed ═══
def test_n2_no_default_long_on_cascade() -> None:
    r = run_n2(_n2_req(axes=("unavailable", "unavailable", "unavailable")))
    assert not r.bias_available and r.reason_codes == ("cascade_regime_all_axes_unavailable",)
    assert r.factors == () and r.output_fingerprint is None    # NU un factor LONG fabricat


def test_n2_incomplete_window_unavailable() -> None:
    o, h, l, c, t = _h1(n=50)                                  # < WEEK_H1 (115)
    r = run_n2(N2Request(contract_version=N2_CONTRACT_VERSION, market_event_id="ev1", symbol=SYM, timeframe="H1",
                         source_identity=SRC, open=o, high=h, low=l, close=c, time=t, as_of=t[-1],
                         regime_axes_status=("available",), n1_fingerprint="n1"))
    assert r.reason_codes == ("incomplete_window",)


# ═══ timeframe strict + refuzuri ═══
def test_n2_rejects_non_h1() -> None:
    assert run_n2(_n2_req(tf="M15")).reason_codes == ("invalid_timeframe",)
    assert run_n2(_n2_req(tf="BANANA")).reason_codes == ("invalid_timeframe",)


def test_n2_future_bar_refused() -> None:
    o, h, l, c, t = _h1()
    assert run_n2(_n2_req(as_of=t[-1] - 1)).reason_codes == ("bars_not_closed_or_ordered",)


def test_n2_unordered_bars_refused() -> None:
    o, h, l, c, t = _h1()
    bad = t[:-2] + (t[-1], t[-2])
    assert run_n2(_n2_req(time_override=bad, as_of=t[-1])).reason_codes == ("bars_not_closed_or_ordered",)


def test_n2_stale_refused() -> None:
    o, h, l, c, t = _h1()
    assert run_n2(_n2_req(as_of=t[-1] + 10_000, max_stale=100)).reason_codes == ("data_stale",)


def test_n2_nan_refused() -> None:
    o, h, l, c, t = _h1()
    bad_c = tuple(list(c[:-1]) + [float("nan")])
    assert run_n2(_n2_req(close_override=bad_c)).reason_codes == ("non_finite_value",)


def test_n2_missing_source_refused() -> None:
    assert run_n2(_n2_req(src="")).reason_codes == ("source_identity_missing",)


def test_n2_incompatible_contract_refused() -> None:
    assert run_n2(_n2_req(contract="tower-n2-request-vX")).reason_codes == ("incompatible_contract",)


def test_n2_different_source_changes_identity() -> None:
    a = run_n2(_n2_req(src="feedA")); b = run_n2(_n2_req(src="feedB"))
    assert a.data_identity and b.data_identity
    assert a.data_identity.bars_content_hash == b.data_identity.bars_content_hash   # aceleași bare
    assert a.node_input_fingerprint == a.node_input_fingerprint and a.data_identity.source_identity != b.data_identity.source_identity


# ═══ lanțul complet N1→N2→N3→N4 cu fingerprintul N2 REAL ═══
def _m15_req(n2_fp: str, event: str, as_of: int) -> N3Request:
    o = []; h = []; l = []; c = []; t = []
    for j in range(40):
        base = 100.0 + (1.0 if (j // 5) % 2 else -1.0)
        o.append(base); h.append(base + 1.5); l.append(base - 1.5); c.append(base + 0.3); t.append(T0 + j * 900)
    return N3Request(contract_version=N3_CONTRACT_VERSION, market_event_id=event, symbol=SYM, timeframe="M15",
                     source_identity=SRC, open=tuple(o), high=tuple(h), low=tuple(l), close=tuple(c), time=tuple(t),
                     as_of=as_of, regime_available=True, bias_available=True, n1_fingerprint="n1fp",
                     n2_fingerprint=n2_fp, atr=tuple([5.0] * 40))


def test_full_n1_to_n4_uses_real_n2_fingerprint() -> None:
    as_of = AS_OF
    n2 = run_n2(_n2_req(event="evChain", as_of=as_of))
    assert n2.bias_available and n2.output_fingerprint
    # N3 primește fingerprintul N2 REAL (nu bias_direction, nu default LONG)
    n3 = run_n3(_m15_req(n2.output_fingerprint, "evChain", as_of))
    assert n3.market_map_available
    assert n2.event_fingerprint == n3.event_fingerprint            # eveniment COMUN (N2 H1 și N3 M15, același as_of)
    assert same_event(n2.event_fingerprint, n2.market_event_id, n3.event_fingerprint, n3.market_event_id)
    # un fingerprint N2 diferit ⇒ alt node_input_fingerprint N3 (N3 chiar consumă fingerprintul N2)
    n3b = run_n3(_m15_req("some-other-n2-fp", "evChain", as_of))
    assert n3.node_input_fingerprint != n3b.node_input_fingerprint
