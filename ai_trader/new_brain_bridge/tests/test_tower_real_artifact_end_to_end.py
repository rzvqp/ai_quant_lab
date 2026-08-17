"""The definitive real-artifact proof -- CEO Phase 2, steps 3-4 (2026-08-14); re-verified against
`ve_tower` 0.5.0's real chain orchestrator by RT-TOWER-0008 (2026-08-17). This test spawns the worker with
**no test-identity override**, against the genuinely installed `ve_tower` 0.5.0
(`N2_HANDOFF_PASS`/`N2_CHAIN_BINDING_PASS`, `tower_worker/env/install_ve_tower.ps1`). A real handshake, a
real identity pin match (including the 5 new chain-binding fields), and a real chain fixture answered by
`ve_tower.run_tower_chain` itself -- not a stub anywhere in the chain.

Skips cleanly if the isolated tower venv isn't present on this machine (same convention as
`test_tower_launcher.py`'s real-subprocess tests)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.new_brain_bridge.tower_client import TowerChainResult, TowerClient, TowerClientConfig
from ai_trader.new_brain_bridge.tower_identity_pin import (
    EXPECTED_N2_CONTRACT_VERSION,
    EXPECTED_N3_CONTRACT_VERSION,
    EXPECTED_N4_CONTRACT_VERSION,
    EXPECTED_PACKAGE_BUILD_COMMIT,
    EXPECTED_VE_TOWER_PACKAGE_VERSION,
)
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession, TowerWorkerLauncher
from ai_trader.new_brain_bridge.tower_protocol import PROTOCOL_VERSION, REQUEST_SCHEMA_VERSION, TowerChainRequest

_TOWER_VENV = Path("C:/Users/MEDION GAMING/ve_tower_venv")
_TOWER_PYTHON = _TOWER_VENV / "Scripts" / "python.exe"

pytestmark_real = pytest.mark.skipif(
    not _TOWER_PYTHON.is_file(), reason="isolated tower venv not present on this machine"
)

_AS_OF = 1_700_000_000


def _synthetic_series(
    *, count: int, step_seconds: int, as_of: int, start_price: float,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...]]:
    """Same deterministic generator as `tower_worker/tests/test_decision.py` -- duplicated rather than
    imported, since this test runs in the MAIN venv and must never import anything from `ve_tower_worker`
    (that package is only ever installed in the isolated tower venv). Returns (open, high, low, close,
    time) tuples -- the `ChainRequest` wire shape, not dicts."""
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
        delta = ((state % 200) - 100) / 100.0
        open_ = price
        close = price + delta
        high = max(open_, close) + abs(delta) * 0.5 + 0.1
        low = min(open_, close) - abs(delta) * 0.5 - 0.1
        opens.append(round(open_, 2)); highs.append(round(high, 2))
        lows.append(round(low, 2)); closes.append(round(close, 2))
        times.append(first_time + i * step_seconds)
        price = close
    return tuple(opens), tuple(highs), tuple(lows), tuple(closes), tuple(times)


def _fixture_request() -> TowerChainRequest:
    h1_o, h1_h, h1_l, h1_c, h1_t = _synthetic_series(count=150, step_seconds=3600, as_of=_AS_OF, start_price=2000.0)
    m15_o, m15_h, m15_l, m15_c, m15_t = _synthetic_series(count=150, step_seconds=900, as_of=_AS_OF, start_price=2000.0)
    _, m5_h, m5_l, m5_c, m5_t = _synthetic_series(count=150, step_seconds=300, as_of=_AS_OF, start_price=2010.0)
    return TowerChainRequest(
        protocol_version=PROTOCOL_VERSION, schema_version=REQUEST_SCHEMA_VERSION,
        request_id="real-e2e-req-1", market_event_id="XAUUSD:15:1700000000", trace_id="real-e2e-trace-1",
        correlation_id="XAUUSD:15:1700000000", symbol="XAUUSD", as_of=_AS_OF,
        configuration_fingerprint="real-e2e-cfg-1", regime_axes_status=("TREND_UP",),
        h1_open=h1_o, h1_high=h1_h, h1_low=h1_l, h1_close=h1_c, h1_time=h1_t,
        h1_source_identity="tower-client:XAUUSD:H1",
        m15_open=m15_o, m15_high=m15_h, m15_low=m15_l, m15_close=m15_c, m15_time=m15_t,
        m15_source_identity="tower-client:XAUUSD:M15",
        m5_high=m5_h, m5_low=m5_l, m5_close=m5_c, m5_time=m5_t, m5_source_identity="tower-client:XAUUSD:M5",
        strategy_id="trend_pullback", strategy_version="1.0", side=1,
        expected_n2_contract=EXPECTED_N2_CONTRACT_VERSION, expected_n3_contract=EXPECTED_N3_CONTRACT_VERSION,
        expected_n4_contract=EXPECTED_N4_CONTRACT_VERSION,
    )


@pytestmark_real
def test_real_worker_handshake_is_accepted_with_no_test_identity_override(tmp_path: Path) -> None:
    """The literal task-273 completion criterion, re-verified for 0.5.0: a genuine `EstablishedSession`,
    not a `HandshakeFailure` -- no stub, no monkeypatch, the real pin against the real artifact."""
    launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, run_dir=tmp_path)
    try:
        result = launcher.launch_and_handshake()
        assert isinstance(result, EstablishedSession), f"expected EstablishedSession, got {result!r}"
        assert result.worker_identity.ve_tower_package_version == EXPECTED_VE_TOWER_PACKAGE_VERSION
        assert result.worker_identity.package_build_commit == EXPECTED_PACKAGE_BUILD_COMMIT
        assert result.worker_identity.production_entrypoint == "run_tower_chain"
        assert result.worker_identity.n2_contract_version == EXPECTED_N2_CONTRACT_VERSION
    finally:
        launcher.stop()


@pytestmark_real
def test_real_worker_answers_a_real_chain_fixture_over_real_ipc(tmp_path: Path) -> None:
    """Full round trip: real handshake -> real `TowerClient` -> real socket -> real
    `ve_tower.run_tower_chain` -> real response, session-and-identity-verified on the way back."""
    launcher = TowerWorkerLauncher(tower_python=_TOWER_PYTHON, run_dir=tmp_path)
    try:
        session = launcher.launch_and_handshake()
        assert isinstance(session, EstablishedSession), f"expected EstablishedSession, got {session!r}"

        client = TowerClient(
            TowerClientConfig(host=session.host, port=session.port, timeout_seconds=10.0), session=session,
        )
        result = client.request_chain(_fixture_request())

        assert isinstance(result, TowerChainResult), f"expected TowerChainResult, got {result!r}"
        assert result.tower_version == EXPECTED_VE_TOWER_PACKAGE_VERSION
        assert result.chain_binding_version == "tower-chain-binding-v1"
        assert result.n2_output is not None
        assert "bias_available" in result.n2_output
        assert result.n3_output is not None
        assert "market_map_available" in result.n3_output
        assert isinstance(result.n3_output["market_map_available"], bool)
        # n4_output is present iff N3 found a map -- never asserting a specific TRUE/FALSE outcome, only
        # that the wiring itself produced an honest, well-formed answer from the real artifact.
        if result.n3_output["market_map_available"]:
            assert result.n4_output is not None
            assert "confirmation_available" in result.n4_output
    finally:
        launcher.stop()
