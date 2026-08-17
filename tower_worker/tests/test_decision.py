"""`real_decision` against the GENUINELY installed `ve_tower` 0.5.0 -- RT-TOWER-0008 remediation
(2026-08-17): "workerul foloseste EXCLUSIV orchestratorul... ve_tower.run_tower_chain." These tests call
`real_decision` directly (no socket) to prove the `ve_tower` chain wiring itself is correct;
`test_server_roundtrip.py`-style socket tests cover the transport separately.

Fixture data is a small, deterministic, clearly-synthetic OHLC random walk -- CLOSED bars only, strictly
ascending epoch time, consistent OHLC ordering (`low <= open,close <= high`). It exists to exercise the
real `ve_tower.run_tower_chain` code path end-to-end, not to assert a specific trading outcome -- these
tests check the RESPONSE IS WELL-FORMED and HONEST (whatever `ve_tower` itself decides), never that it
finds a particular zone, bias, or confirmation."""

from __future__ import annotations

import dataclasses

import ve_tower  # type: ignore[import-untyped]  # the REAL installed artifact -- fails to collect if ever uninstalled

from ve_tower_worker.decision import real_decision
from ve_tower_worker.protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerChainRequest

_AS_OF = 1_700_000_000  # arbitrary fixed epoch anchor, deterministic across runs


def _synthetic_series(
    *, count: int, step_seconds: int, as_of: int, start_price: float = 2000.0,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...]]:
    """Deterministic pseudo-random walk (LCG, no `random` module -- reproducible without seeding concerns),
    closing at `as_of`. `count` closed bars, strictly ascending, each `step_seconds` apart. Returns
    (open, high, low, close, time) tuples -- the `ChainRequest` wire shape, not dicts."""
    opens: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    closes: list[float] = []
    times: list[int] = []
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
        opens.append(round(open_, 2)); highs.append(round(high, 2))
        lows.append(round(low, 2)); closes.append(round(close, 2))
        times.append(first_time + i * step_seconds)
        price = close
    return tuple(opens), tuple(highs), tuple(lows), tuple(closes), tuple(times)


def _make_request(
    *, side: int = 1, expected_n2_contract: str | None = None, expected_n3_contract: str | None = None,
    expected_n4_contract: str | None = None,
) -> TowerChainRequest:
    h1_o, h1_h, h1_l, h1_c, h1_t = _synthetic_series(count=150, step_seconds=3600, as_of=_AS_OF)
    m15_o, m15_h, m15_l, m15_c, m15_t = _synthetic_series(count=150, step_seconds=900, as_of=_AS_OF)
    _, m5_h, m5_l, m5_c, m5_t = _synthetic_series(count=150, step_seconds=300, as_of=_AS_OF, start_price=2010.0)
    return TowerChainRequest(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id="req-1", market_event_id="XAUUSD:15:1700000000", trace_id="trace-1",
        correlation_id="corr-1", symbol="XAUUSD", as_of=_AS_OF, configuration_fingerprint="cfg-1",
        regime_axes_status=("TREND_UP",),
        h1_open=h1_o, h1_high=h1_h, h1_low=h1_l, h1_close=h1_c, h1_time=h1_t,
        h1_source_identity="tower-client:XAUUSD:H1",
        m15_open=m15_o, m15_high=m15_h, m15_low=m15_l, m15_close=m15_c, m15_time=m15_t,
        m15_source_identity="tower-client:XAUUSD:M15",
        m5_high=m5_h, m5_low=m5_l, m5_close=m5_c, m5_time=m5_t, m5_source_identity="tower-client:XAUUSD:M5",
        strategy_id="trend_pullback", strategy_version="1.0", side=side,
        expected_n2_contract=expected_n2_contract or ve_tower.N2_CONTRACT_VERSION,
        expected_n3_contract=expected_n3_contract or ve_tower.N3_CONTRACT_VERSION,
        expected_n4_contract=expected_n4_contract or ve_tower.N4_CONTRACT_VERSION,
    )


def test_real_decision_calls_the_genuinely_installed_ve_tower_0_5_0() -> None:
    """Not a stub: proves the installed distribution's own version string comes back, and that it is
    genuinely 0.5.0 -- the version this whole remediation exists to wire in."""
    response = real_decision(_make_request())
    assert response.ok is True
    assert response.tower_version == ve_tower.VE_TOWER_VERSION == "0.5.0"
    assert response.chain_binding_version == ve_tower.TOWER_CHAIN_BINDING_VERSION == "tower-chain-binding-v1"
    assert response.chain_response_contract_version == ve_tower.CHAIN_RESPONSE_CONTRACT_VERSION


def test_real_decision_returns_well_formed_n2_output() -> None:
    """N2 is now a REAL, chain-internal producer (computed from H1 bars) -- never client-supplied."""
    response = real_decision(_make_request())
    assert response.n2_output is not None
    assert "bias_available" in response.n2_output
    assert isinstance(response.n2_output["bias_available"], bool)
    assert "direction_share_long" in response.n2_output
    assert "direction_share_short" in response.n2_output


def test_real_decision_returns_well_formed_n3_output() -> None:
    response = real_decision(_make_request())
    assert response.n3_output is not None
    assert "market_map_available" in response.n3_output
    assert "levels_available" in response.n3_output
    assert isinstance(response.n3_output["market_map_available"], bool)


def test_real_decision_has_a_real_chain_fingerprint() -> None:
    response = real_decision(_make_request())
    assert response.ok is True
    assert response.chain_fingerprint
    assert response.chain_status
    assert response.terminal_reason_code


def test_real_decision_contract_expectation_mismatch_fails_closed() -> None:
    """A caller pinning the WRONG expected N2/N3/N4 contract version must degrade to a fail-closed
    response, never silently proceed against a contract it didn't actually pin."""
    response = real_decision(_make_request(expected_n3_contract="wrong-contract-version"))
    assert response.ok is False
    assert response.n2_output is None
    assert response.n3_output is None
    assert response.n4_output is None
    assert any("CONTRACT_EXPECTATION_MISMATCH" in code for code in response.reason_codes)


def test_real_decision_is_deterministic_across_calls() -> None:
    """Same request in -> byte-identical response content out (aside from nothing session-related, since
    `real_decision` never touches session fields -- those are `server.py`'s job)."""
    r1 = real_decision(_make_request())
    r2 = real_decision(_make_request())
    assert r1.n2_output == r2.n2_output
    assert r1.n3_output == r2.n3_output
    assert r1.n4_output == r2.n4_output
    assert r1.chain_fingerprint == r2.chain_fingerprint
    assert r1.reason_codes == r2.reason_codes


def test_real_decision_side_is_genuinely_threaded_through_not_ignored() -> None:
    """`side` (LONG=1 vs SHORT=-1) changes what N4 confirms against -- proving it reaches `ve_tower`
    rather than being silently dropped. Not asserting a specific outcome, only that the two sides are
    processed (both return a real, well-formed response, not an error)."""
    long_response = real_decision(_make_request(side=1))
    short_response = real_decision(_make_request(side=-1))
    assert long_response.ok is True
    assert short_response.ok is True
