"""`real_decision` against the GENUINELY installed `ve_tower` 0.3.0 -- CEO Phase 2 step 4: "ruleaza fixture-ul
N3/N4 prin IPC real." These tests call `real_decision` directly (no socket) to prove the `ve_tower` wiring
itself is correct; `test_server_roundtrip.py`-style socket tests cover the transport separately.

Fixture data is a small, deterministic, clearly-synthetic OHLC random walk -- CLOSED bars only, strictly
ascending epoch time, consistent OHLC ordering (`low <= open,close <= high`). It exists to exercise the
real `ve_tower.run_n3`/`run_n4` code paths end-to-end, not to assert a specific trading outcome -- these
tests check the RESPONSE IS WELL-FORMED and HONEST (whatever `ve_tower` itself decides), never that it
finds a particular zone or confirmation."""

from __future__ import annotations

import ve_tower  # type: ignore[import-untyped]  # the REAL installed artifact -- fails to collect if ever uninstalled

from ve_tower_worker.decision import real_decision
from ve_tower_worker.protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerRequest

_AS_OF = 1_700_000_000  # arbitrary fixed epoch anchor, deterministic across runs


def _synthetic_bars(*, count: int, step_seconds: int, as_of: int, start_price: float = 2000.0) -> tuple[dict[str, object], ...]:
    """Deterministic pseudo-random walk (LCG, no `random` module -- reproducible without seeding concerns),
    closing at `as_of`. `count` closed bars, strictly ascending, each `step_seconds` apart."""
    bars: list[dict[str, object]] = []
    price = start_price
    state = 12345
    first_time = as_of - (count - 1) * step_seconds
    for i in range(count):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        delta = ((state % 200) - 100) / 100.0  # in [-1.0, 1.0)
        open_ = price
        close = price + delta
        high = max(open_, close) + abs(delta) * 0.5 + 0.1
        low = min(open_, close) - abs(delta) * 0.5 - 0.1
        bars.append({
            "time": first_time + i * step_seconds,
            "open": round(open_, 2), "high": round(high, 2),
            "low": round(low, 2), "close": round(close, 2),
        })
        price = close
    return tuple(bars)


def _make_request(*, n2_bias_direction: str | object = "LONG", m15_count: int = 150, m5_count: int = 150) -> TowerRequest:
    m15_bars = _synthetic_bars(count=m15_count, step_seconds=900, as_of=_AS_OF)
    m5_bars = _synthetic_bars(count=m5_count, step_seconds=300, as_of=_AS_OF, start_price=2010.0)
    n2_output: dict[str, object] = {"available": True, "fingerprint": "n2fp-test"}
    if n2_bias_direction is not None:
        n2_output["bias_direction"] = n2_bias_direction
    return TowerRequest(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id="req-1", market_event_id="XAUUSD:15:1700000000", event_fingerprint="",
        data_identity="d1", node_input_fingerprint="n1",
        symbol="XAUUSD", as_of=str(_AS_OF),
        n1_output={"available": True, "fingerprint": "n1fp-test"},
        n2_output=n2_output,
        m15_closed_bars=m15_bars, m5_closed_bars=m5_bars,
        strategy_id="trend_pullback", strategy_version="1.0",
    )


def test_real_decision_calls_the_genuinely_installed_ve_tower() -> None:
    """Not a stub: proves the installed distribution's own version string comes back."""
    response = real_decision(_make_request())
    assert response.ok is True
    assert response.tower_version == ve_tower.VE_TOWER_VERSION == "0.3.0"


def test_real_decision_returns_well_formed_n3_output() -> None:
    response = real_decision(_make_request())
    assert response.n3_output is not None
    assert "market_map_available" in response.n3_output
    assert "levels_available" in response.n3_output
    assert isinstance(response.n3_output["market_map_available"], bool)


def test_real_decision_never_fabricates_confirmation_without_a_market_map() -> None:
    """If N3 found no map, N4 must never run -- `n4_output` stays `None`, not a fabricated confirmation."""
    response = real_decision(_make_request())
    if response.n3_output is not None and not response.n3_output["market_map_available"]:
        assert response.n4_output is None


def test_real_decision_skips_n4_when_bias_direction_absent() -> None:
    """No `bias_direction` -> no side to confirm -> N4 never called, regardless of what N3 found."""
    response = real_decision(_make_request(n2_bias_direction=None))
    assert response.n4_output is None


def test_real_decision_malformed_bias_direction_fails_closed() -> None:
    response = real_decision(_make_request(n2_bias_direction="SIDEWAYS"))
    assert response.ok is False
    assert response.n3_output is None
    assert response.n4_output is None
    assert any("bias_direction" in code for code in response.reason_codes)


def test_real_decision_malformed_bar_fails_closed() -> None:
    request = _make_request()
    bad_bar: dict[str, object] = {"time": 1, "open": 1.0, "high": 1.0, "low": 1.0}  # missing 'close'
    bad_bars = (bad_bar,) + request.m15_closed_bars[1:]
    import dataclasses
    request = dataclasses.replace(request, m15_closed_bars=bad_bars)
    response = real_decision(request)
    assert response.ok is False
    assert "MALFORMED_TOWER_REQUEST" in response.reason_codes


def test_real_decision_bad_as_of_fails_closed() -> None:
    import dataclasses
    request = dataclasses.replace(_make_request(), as_of="not-an-epoch")
    response = real_decision(request)
    assert response.ok is False
    assert "MALFORMED_TOWER_REQUEST" in response.reason_codes


def test_real_decision_is_deterministic_across_calls() -> None:
    """Same request in -> byte-identical response content out (aside from nothing session-related, since
    `real_decision` never touches session fields -- those are `server.py`'s job)."""
    r1 = real_decision(_make_request())
    r2 = real_decision(_make_request())
    assert r1.n3_output == r2.n3_output
    assert r1.n4_output == r2.n4_output
    assert r1.reason_codes == r2.reason_codes
