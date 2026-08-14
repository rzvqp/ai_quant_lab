"""Matricea DECISIVĂ (remediere TOWER_HANDOFF_FAIL): reproduce și ÎNCHIDE atacurile Red Team — timeframe strict,
dublă identitate (event comun + node per-nod distinct), legătura N4↔N3, NaN/Inf/sursă/lookahead → refuz."""

from __future__ import annotations

import dataclasses
import os
import sys

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from ve_tower import (  # noqa: E402
    N3Request, N3Response, N4Request, event_fingerprint, run_n3, run_n4, same_event,
    N3_CONTRACT_VERSION, N4_CONTRACT_VERSION, build_data_identity,
)
from ve_tower.data_identity import DataIdentityError  # noqa: E402
import pytest  # noqa: E402

SYM = "XAUUSD"
SRC = "OANDA_XAUUSD_feed_v1"
T0 = 1_600_000_000


def _m15(n: int = 40, bump: float = 0.0) -> tuple[tuple[float, ...], ...]:
    o = []; h = []; l = []; c = []; t = []
    for j in range(n):
        base = 100.0 + (1.0 if (j // 5) % 2 else -1.0) + bump
        o.append(base); h.append(base + 1.5); l.append(base - 1.5); c.append(base + 0.3); t.append(T0 + j * 900)
    return tuple(o), tuple(h), tuple(l), tuple(c), tuple(t)


def _n3_req(*, event: str = "ev1", tf: str = "M15", regime: bool = True, bias: bool = True, src: str = SRC,
            as_of: int | None = None, contract: str = N3_CONTRACT_VERSION, bump: float = 0.0,
            atr_override: tuple[float, ...] | None = None) -> N3Request:
    o, h, l, c, t = _m15(bump=bump)
    ao = as_of if as_of is not None else t[-1]
    return N3Request(contract_version=contract, market_event_id=event, symbol=SYM, timeframe=tf, source_identity=src,
                     open=o, high=h, low=l, close=c, time=t, as_of=ao, regime_available=regime, bias_available=bias,
                     n1_fingerprint="n1fp", n2_fingerprint="n2fp",
                     atr=atr_override if atr_override is not None else tuple([5.0] * len(c)), max_staleness_s=None)


def _m5(level: float = 100.0, post_off: float = 0.8, bump: float = 0.0
        ) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...]]:
    # bare centrate pe `level`: 2 pre sub nivel, penetrare sus la i2, fereastră [2..5], apoi 3 post-fereastră
    L = level
    p = L + post_off
    rows = [(L - 0.5, L - 1.5, L - 1.0), (L - 0.4, L - 1.4, L - 0.8), (L + 1.0, L - 1.0, L + 0.5),
            (L + 1.2, L + 0.1, L + 0.8), (L + 1.3, L + 0.2, L + 0.9), (L + 1.1, L + 0.0, L + 0.7),
            (p + 1, p - 1, p), (p + 1, p - 1, p), (p + 1, p - 1, p)]
    h = tuple(r[0] + bump for r in rows); l = tuple(r[1] + bump for r in rows); c = tuple(r[2] + bump for r in rows)
    t = tuple(T0 + i * 300 for i in range(len(rows)))
    return h, l, c, t


def _n4_from_n3(n3: N3Response, *, event: str = "ev1", tf: str = "M5", side: int = 1, as_of: int | None = None,
                contract: str = N4_CONTRACT_VERSION, post_off: float = 0.8, bump: float = 0.0, src: str = SRC,
                link_ok: bool = True) -> N4Request:
    lvl = n3.market_map[0] if n3.market_map else None
    level = lvl.price_anchor if lvl else 100.0
    h, l, c, t = _m5(level=level, post_off=post_off, bump=bump)
    ao = as_of if as_of is not None else (n3.data_identity.as_of if n3.data_identity else t[-1])
    return N4Request(
        contract_version=contract, market_event_id=event, symbol=SYM, timeframe=tf, source_identity=src,
        high=h, low=l, close=c, time=t, level=(lvl.price_anchor if lvl else 100.0), side=side, as_of=ao,
        strategy_id="S1", strategy_version="v1", regime_available=True, bias_available=True,
        n1_fingerprint="n1fp", n2_fingerprint="n2fp",
        n3_market_event_id=n3.market_event_id if link_ok else "OTHER",
        n3_event_fingerprint=n3.event_fingerprint if link_ok else "deadbeefdeadbeef",
        n3_node_input_fingerprint=n3.node_input_fingerprint or "",
        n3_market_map_available=n3.market_map_available,
        n3_level_zone_id=(lvl.zone_id if lvl else ""),
        n3_level_provenance=tuple((p.family, p.instance_count) for p in (lvl.provenance if lvl else ())),
        w=3, atr=tuple([1.0] * len(c)), max_staleness_s=None)


# ═══ TIMEFRAME STRICT ═══
def test_n3_rejects_m5() -> None:
    assert run_n3(_n3_req(tf="M5")).reason_codes == ("invalid_timeframe",)


def test_n3_rejects_banana() -> None:
    assert run_n3(_n3_req(tf="BANANA")).reason_codes == ("invalid_timeframe",)


def test_n4_rejects_m15() -> None:
    n3 = run_n3(_n3_req())
    assert run_n4(_n4_from_n3(n3, tf="M15")).reason_codes == ("invalid_timeframe",)


# ═══ dublă identitate ═══
def test_event_fingerprint_common_identical_n3_to_n4() -> None:
    n3 = run_n3(_n3_req(event="evX", as_of=T0 + 39 * 900))
    n4 = run_n4(_n4_from_n3(n3, event="evX", as_of=T0 + 39 * 900))
    assert n3.event_fingerprint == n4.event_fingerprint                       # COMUN, IDENTIC
    assert same_event(n3.event_fingerprint, n3.market_event_id, n4.event_fingerprint, n4.market_event_id)


def test_node_fingerprints_are_distinct_n3_vs_n4() -> None:
    n3 = run_n3(_n3_req(event="evX", as_of=T0 + 39 * 900))
    n4 = run_n4(_n4_from_n3(n3, event="evX", as_of=T0 + 39 * 900))
    assert n3.node_input_fingerprint and n4.node_input_fingerprint
    assert n3.node_input_fingerprint != n4.node_input_fingerprint             # date diferite ⇒ amprente distincte


def test_same_event_different_m15_bars_different_node_fingerprint() -> None:
    a = run_n3(_n3_req(event="evSame", as_of=T0 + 39 * 900, bump=0.0))
    b = run_n3(_n3_req(event="evSame", as_of=T0 + 39 * 900, bump=7.0))        # alte bare, ACELAȘI event
    assert a.event_fingerprint == b.event_fingerprint                        # eveniment identic
    assert a.node_input_fingerprint != b.node_input_fingerprint              # dar hărți diferite ⇒ node fp diferit


def test_same_event_different_m5_bars_different_node_fingerprint() -> None:
    n3 = run_n3(_n3_req(event="evSame", as_of=T0 + 39 * 900))
    a = run_n4(_n4_from_n3(n3, event="evSame", as_of=T0 + 39 * 900, bump=0.0))
    b = run_n4(_n4_from_n3(n3, event="evSame", as_of=T0 + 39 * 900, bump=5.0))
    assert a.node_input_fingerprint and b.node_input_fingerprint              # ambele poartă identitatea datelor
    assert a.node_input_fingerprint != b.node_input_fingerprint              # bare M5 diferite ⇒ node fp diferit


def test_different_data_cannot_share_provenance() -> None:
    # două hărți din bare diferite NU pot avea aceeași data_identity/node fingerprint
    a = run_n3(_n3_req(event="ev1", bump=0.0)); b = run_n3(_n3_req(event="ev1", bump=3.0))
    assert a.data_identity and b.data_identity
    assert a.data_identity.bars_content_hash != b.data_identity.bars_content_hash


# ═══ legătura N4↔N3 ═══
def test_n4_with_different_n3_response_refused() -> None:
    n3 = run_n3(_n3_req(event="evReal", as_of=T0 + 39 * 900))
    bad = _n4_from_n3(n3, event="evReal", as_of=T0 + 39 * 900, link_ok=False)   # legătură N3 nepotrivită
    assert run_n4(bad).reason_codes == ("n3_link_mismatch",)


def test_n4_cascade_when_n3_unavailable() -> None:
    n3 = run_n3(_n3_req(event="evC", regime=False, as_of=T0 + 39 * 900))         # N3 indisponibil (cascada)
    r = run_n4(_n4_from_n3(n3, event="evC", as_of=T0 + 39 * 900))
    assert not r.confirmation_available and r.reason_codes == ("zone_unavailable",)


# ═══ refuzuri de date ═══
def test_n3_future_bar_refused() -> None:
    o, h, l, c, t = _m15()
    assert run_n3(_n3_req(as_of=t[-1] - 1)).reason_codes == ("bars_not_closed_or_ordered",)


def test_n3_nan_refused() -> None:
    o, h, l, c, t = _m15()
    bad_atr = tuple([5.0] * (len(c) - 1) + [float("inf")])
    assert run_n3(_n3_req(atr_override=bad_atr)).reason_codes == ("non_finite_value",)


def test_n3_missing_source_refused() -> None:
    assert run_n3(_n3_req(src="")).reason_codes == ("source_identity_missing",)


def test_n4_missing_source_refused() -> None:
    n3 = run_n3(_n3_req(as_of=T0 + 39 * 900))
    assert run_n4(_n4_from_n3(n3, as_of=T0 + 39 * 900, src="")).reason_codes == ("source_identity_missing",)


def test_data_identity_inconsistent_refused_at_builder() -> None:
    with pytest.raises(DataIdentityError):
        build_data_identity(symbol=SYM, timeframe="M15", source_identity=SRC, time=(1, 2, 3),
                            vectors={"close": (1.0, 2.0)}, as_of=3, contract_version=N3_CONTRACT_VERSION)


def test_n3_incompatible_contract_refused() -> None:
    assert run_n3(_n3_req(contract="tower-n3-request-v1")).reason_codes == ("incompatible_contract",)


# ═══ N3 hartă reală + provenianță + N4 confirmă + fără lookahead ═══
def test_n3_real_map_with_provenance_and_data_identity() -> None:
    r = run_n3(_n3_req())
    assert r.market_map_available and r.levels and r.market_map
    assert r.data_identity is not None and r.data_identity.timeframe == "M15" and r.data_identity.source_identity == SRC
    assert r.data_identity.bar_count == 40 and r.node_input_fingerprint
    for lvl in r.market_map:
        assert lvl.provenance and all(p.family and p.instance_count >= 1 for p in lvl.provenance)


def test_n4_confirms_and_no_lookahead() -> None:
    n3 = run_n3(_n3_req(as_of=T0 + 39 * 900))
    a = run_n4(_n4_from_n3(n3, as_of=T0 + 39 * 900, post_off=0.8))
    b = run_n4(_n4_from_n3(n3, as_of=T0 + 39 * 900, post_off=-30.0))          # crash DUPĂ fereastră
    assert a.confirmation_available
    assert a.confirmation_value == b.confirmation_value and a.persistence == b.persistence   # fără lookahead
