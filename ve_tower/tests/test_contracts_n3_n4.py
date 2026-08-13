"""Matricea COMPLETĂ de teste pentru contractele versionate N3/N4 (peste turnul RATIFICAT, byte-identic):
hartă reală + provenianță, N4 fără lookahead, M5 stale/incomplet → indisponibil, identitate de eveniment prin lanț,
contract incompatibil → fail-closed, fixture complet N1→N4, și un fixture NEGATIV pentru fiecare intrare absentă."""

from __future__ import annotations

import os
import sys

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_tower  # noqa: E402
from ve_tower import (  # noqa: E402
    N3Request, N4Request, configuration_fingerprint, run_n3, run_n4, same_event,
    N3_CONTRACT_VERSION, N4_CONTRACT_VERSION,
)

SYM = "XAUUSD"
STEP15 = 900
STEP5 = 300
T0 = 1_600_000_000


def _m15(n: int = 40) -> tuple[tuple[float, ...], ...]:
    o = []; h = []; l = []; c = []; t = []
    for j in range(n):
        base = 100.0 + (1.0 if (j // 5) % 2 else -1.0)
        o.append(base); h.append(base + 1.5); l.append(base - 1.5); c.append(base + 0.3); t.append(T0 + j * STEP15)
    return tuple(o), tuple(h), tuple(l), tuple(c), tuple(t)


def _n3_req(*, event: str = "ev1", regime: bool = True, bias: bool = True, as_of: int | None = None,
            contract: str = N3_CONTRACT_VERSION, max_stale: int | None = None,
            time_override: tuple[int, ...] | None = None) -> N3Request:
    o, h, l, c, t = _m15()
    if time_override is not None:
        t = time_override
    ao = as_of if as_of is not None else t[-1]
    return N3Request(contract_version=contract, market_event_id=event, symbol=SYM, timeframe="M15",
                     open=o, high=h, low=l, close=c, time=t, as_of=ao, regime_available=regime, bias_available=bias,
                     atr=tuple([5.0] * len(c)), max_staleness_s=max_stale)


# ── M5 pentru N4: penetrare la i2, fereastră [2..5], bare post-fereastră care NU trebuie să conteze ──
def _m5(post_close: float) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...]]:
    rows = [(99.5, 98.5, 99.0), (99.6, 98.6, 99.2), (101.0, 99.0, 100.5), (101.2, 100.1, 100.8),
            (101.3, 100.2, 100.9), (101.1, 100.0, 100.7),
            (post_close + 1, post_close - 1, post_close), (post_close + 1, post_close - 1, post_close),
            (post_close + 1, post_close - 1, post_close)]
    h = tuple(r[0] for r in rows); l = tuple(r[1] for r in rows); c = tuple(r[2] for r in rows)
    t = tuple(T0 + i * STEP5 for i in range(len(rows)))
    return h, l, c, t


def _n4_req(*, event: str = "ev1", n3_ok: bool = True, side: int = 1, as_of: int | None = None,
            contract: str = N4_CONTRACT_VERSION, post_close: float = 100.8, max_stale: int | None = None,
            up_event: str | None = None, up_fp: str | None = None,
            time_override: tuple[int, ...] | None = None) -> N4Request:
    h, l, c, t = _m5(post_close)
    if time_override is not None:
        t = time_override
    ao = as_of if as_of is not None else t[-1]
    fp = configuration_fingerprint(market_event_id=event, symbol=SYM, as_of=ao)
    return N4Request(contract_version=contract, market_event_id=event, symbol=SYM, timeframe="M5",
                     high=h, low=l, close=c, time=t, level=100.0, side=side, as_of=ao, strategy_id="S1",
                     regime_available=True, bias_available=True, n3_available=n3_ok,
                     upstream_market_event_id=up_event if up_event is not None else event,
                     upstream_configuration_fingerprint=up_fp if up_fp is not None else fp,
                     w=3, atr=tuple([1.0] * len(c)), max_staleness_s=max_stale)


# ═══ N3 ═══
def test_n3_real_map_from_closed_bars() -> None:
    r = run_n3(_n3_req())
    assert r.market_map_available and r.levels_available
    assert r.reason_codes == ("ok_market_map",) and r.market_map and r.reference_price is not None
    assert r.market_event_id == "ev1" and r.valid_until_index == r.as_of_index + 1


def test_n3_levels_have_provenance() -> None:
    r = run_n3(_n3_req())
    for lvl in r.market_map:
        assert lvl.provenance and all(p.family and p.instance_count >= 1 for p in lvl.provenance)
        assert lvl.relative_rank >= 1


def test_n3_lookahead_bar_fail_closed() -> None:
    # ultima bară cu timp > as_of ⇒ fail-closed (fără lookahead)
    o, h, l, c, t = _m15()
    r = run_n3(_n3_req(as_of=t[-1] - 1))
    assert not r.market_map_available and r.reason_codes == ("bars_not_closed_or_ordered",)


def test_n3_unordered_bars_fail_closed() -> None:
    o, h, l, c, t = _m15()
    bad = t[:-2] + (t[-1], t[-2])                       # neordonate
    r = run_n3(_n3_req(time_override=bad, as_of=t[-1]))
    assert r.reason_codes == ("bars_not_closed_or_ordered",)


def test_n3_stale_fail_closed() -> None:
    o, h, l, c, t = _m15()
    r = run_n3(_n3_req(as_of=t[-1] + 10_000, max_stale=100))
    assert r.reason_codes == ("data_stale",)


def test_n3_incompatible_contract_fail_closed() -> None:
    r = run_n3(_n3_req(contract="tower-n3-request-vX"))
    assert not r.market_map_available and r.reason_codes == ("incompatible_contract",)


def test_n3_negative_regime_absent() -> None:
    r = run_n3(_n3_req(regime=False))
    assert not r.market_map_available and r.reason_codes == ("cascade_level1_or_level2_unavailable",)


def test_n3_negative_bias_absent() -> None:
    r = run_n3(_n3_req(bias=False))
    assert r.reason_codes == ("cascade_level1_or_level2_unavailable",)


# ═══ N4 ═══
def test_n4_confirms_with_available_info() -> None:
    r = run_n4(_n4_req())
    assert r.confirmation_available and r.reason_codes == ("ok_confirmation",)
    assert r.confirmation is not None and r.confirmation_value is not None


def test_n4_no_lookahead_post_window_bars_ignored() -> None:
    # două viitoare care diferă DOAR după fereastră ⇒ descriptor IDENTIC (fără lookahead)
    a = run_n4(_n4_req(post_close=100.8))
    b = run_n4(_n4_req(post_close=90.0))               # crash post-fereastră
    assert a.confirmation_available and b.confirmation_available
    assert a.confirmation_value == b.confirmation_value and a.persistence == b.persistence
    assert a.progress_atr == b.progress_atr and a.window_end_idx == b.window_end_idx


def test_n4_cascade_zone_unavailable() -> None:
    r = run_n4(_n4_req(n3_ok=False))                   # harta N3 indisponibilă
    assert not r.confirmation_available and r.reason_codes == ("zone_unavailable",)


def test_n4_invalid_side_fail_closed() -> None:
    r = run_n4(_n4_req(side=0))
    assert r.reason_codes == ("invalid_side",)


def test_n4_stale_fail_closed() -> None:
    h, l, c, t = _m5(100.8)
    r = run_n4(_n4_req(as_of=t[-1] + 10_000, max_stale=100))
    assert r.reason_codes == ("data_stale",)


def test_n4_incompatible_contract_fail_closed() -> None:
    r = run_n4(_n4_req(contract="tower-n4-request-vX"))
    assert r.reason_codes == ("incompatible_contract",)


# ═══ identitate de eveniment prin lanț ═══
def test_event_identity_matches_when_as_of_shared() -> None:
    as_of = T0 + 39 * STEP15
    n3 = run_n3(_n3_req(event="evS", as_of=as_of))
    n4 = run_n4(_n4_req(event="evS", as_of=as_of, up_event="evS",
                        up_fp=configuration_fingerprint(market_event_id="evS", symbol=SYM, as_of=as_of)))
    assert n3.configuration_fingerprint == n4.configuration_fingerprint          # ACELAȘI fingerprint prin lanț
    assert same_event(n3.configuration_fingerprint, n3.market_event_id, n4.configuration_fingerprint, n4.market_event_id)


def test_n4_event_identity_mismatch_fail_closed() -> None:
    r = run_n4(_n4_req(event="evReal", up_event="evReal", up_fp="deadbeefdeadbeef"))   # fingerprint fals de la N3
    assert not r.confirmation_available and r.reason_codes == ("event_identity_mismatch",)


# ═══ fixture complet N1→N2→N3→N4 ═══
def test_full_n1_to_n4_chain() -> None:
    ve_tower.ensure_tower_loaded()
    as_of15 = T0 + 39 * STEP15
    n3 = run_n3(_n3_req(event="evFull", regime=True, bias=True, as_of=as_of15))
    assert n3.market_map_available and n3.levels_available and n3.market_map
    chosen = n3.market_map[0].price_anchor                 # nivelul rank-1 de la N3
    fp = configuration_fingerprint(market_event_id="evFull", symbol=SYM, as_of=as_of15)
    h, l, c, t = _m5(100.8)
    n4 = run_n4(N4Request(
        contract_version=N4_CONTRACT_VERSION, market_event_id="evFull", symbol=SYM, timeframe="M5",
        high=h, low=l, close=c, time=t, level=chosen, side=1, as_of=as_of15, strategy_id="S1",
        regime_available=True, bias_available=True, n3_available=n3.market_map_available,
        upstream_market_event_id=n3.market_event_id, upstream_configuration_fingerprint=n3.configuration_fingerprint,
        w=3, atr=tuple([1.0] * len(c))))
    # N4 poate fi ok sau no_penetration în funcție de nivelul ales — dar lanțul rulează și identitatea ține
    assert n4.market_event_id == "evFull" and n4.configuration_fingerprint == n3.configuration_fingerprint
    assert n4.reason_codes[0] in ("ok_confirmation", "no_penetration")
