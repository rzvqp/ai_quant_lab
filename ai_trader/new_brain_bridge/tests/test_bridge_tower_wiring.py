"""`evaluate_bar`'s `tower=` wiring (CEO Phase 2 step 5, 2026-08-14; rewritten for the chain protocol by
RT-TOWER-0008, 2026-08-17) -- proves the three flags (`market_map_available`/`levels_available`/
`confirmation_available`) genuinely come from whatever `TowerClient.request_chain` returns, are queried
AT MOST ONCE per (bar, side) -- shared across every catalog strategy sharing that side -- and degrade to
all-`False` on every failure mode -- never fabricated `True`.

Uses a minimal in-process fake TCP worker (same pattern as `test_tower_client.py`'s own `_FakeServer`) so
these are genuine `TowerClient` instances speaking the real wire protocol -- not a duck-typed double that
would drift from what `bridge.py` actually calls."""

from __future__ import annotations

import json
import socket
import threading
from dataclasses import dataclass
from typing import Any

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.bridge import TowerDependencies, evaluate_bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import trend_up_regime_bars
from ai_trader.new_brain_bridge.tower_client import TowerClient, TowerClientConfig
from ai_trader.new_brain_bridge.tower_launcher import EstablishedSession
from ai_trader.new_brain_bridge.tower_protocol import WorkerIdentity, pack_frame, unpack_length_prefix

_SYMBOL = "XAUUSD"
_TIMEFRAME = "M15"

_FAKE_IDENTITY = WorkerIdentity(
    worker_package_version="0.3.0", worker_delivery_commit="abc123", protocol_version="3.0",
    ve_tower_package_version="0.5.0", package_build_commit="b128d8b", state_delivery_commit="26470f5",
    wheel_sha256="deadbeef" * 8, vendored_source_identity="vendored-digest",
    n3_contract_version="tower-n3-request-v2", n4_contract_version="tower-n4-request-v2",
    n2_contract_version="tower-n2-request-v1", chain_request_contract_version="tower-chain-request-v1",
    chain_response_contract_version="tower-chain-response-v1", tower_chain_binding_version="tower-chain-binding-v1",
    production_entrypoint="run_tower_chain",
)
_SESSION = EstablishedSession(
    session_id="sess-1", worker_identity=_FAKE_IDENTITY, worker_identity_fingerprint=_FAKE_IDENTITY.fingerprint(),
    host="127.0.0.1", port=0, pid=1234, process_start_identity="start-token",
)


@dataclass
class _RawRate:
    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: float = 100.0


class _FakeTimeframeAwareGateway:
    """Returns different bars for H1/M15/M5, keyed by `mt5_timeframe`."""

    def __init__(self, *, h1_rates: Any, m15_rates: Any, m5_rates: Any) -> None:
        self._rates_by_timeframe = {16385: h1_rates, 15: m15_rates, 5: m5_rates}
        self.copy_rates_from_calls: list[tuple[str, int, int, int]] = []

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any | None:
        self.copy_rates_from_calls.append((symbol, timeframe, date_from, count))
        return tuple(self._rates_by_timeframe.get(timeframe, ()))


def _closed_rates(*, count: int, step: int, now: int, start_price: float) -> tuple[_RawRate, ...]:
    price = start_price
    rates = []
    first_open = now - count * step
    for i in range(count):
        ts_open = first_open + i * step
        rates.append(_RawRate(time=ts_open, open=price, high=price + 0.5, low=price - 0.5, close=price + 0.1))
        price += 0.1
    return tuple(rates)


def _default_gateway(now: int = 10_000_000) -> _FakeTimeframeAwareGateway:
    return _FakeTimeframeAwareGateway(
        h1_rates=_closed_rates(count=150, step=3600, now=now, start_price=1990.0),
        m15_rates=_closed_rates(count=150, step=900, now=now, start_price=2000.0),
        m5_rates=_closed_rates(count=150, step=300, now=now, start_price=2010.0),
    )


class _FakeWorker:
    """Accepts exactly one connection, replies with a fixed chain payload -- built directly from
    `tower_protocol`'s own framing, mirroring `test_tower_client.py`'s `_FakeServer`."""

    def __init__(
        self, *, n2_output: dict[str, object] | None, n3_output: dict[str, object] | None,
        n4_output: dict[str, object] | None,
    ) -> None:
        self._n2_output = n2_output
        self._n3_output = n3_output
        self._n4_output = n4_output
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(5)
        self.host, self.port = self._sock.getsockname()
        self.connection_count = 0
        self._stop = False
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> None:
        while not self._stop:
            self._sock.settimeout(0.2)
            try:
                conn, _ = self._sock.accept()
            except OSError:
                continue
            self.connection_count += 1
            try:
                prefix = b""
                while len(prefix) < 4:
                    prefix += conn.recv(4 - len(prefix))
                length = unpack_length_prefix(prefix)
                body = b""
                while len(body) < length:
                    body += conn.recv(length - len(body))
                request = json.loads(body.decode("utf-8"))
                response = {
                    "type": "chain_response", "protocol_version": "3.0", "schema_version": "2.0",
                    "request_id": request["request_id"], "market_event_id": request["market_event_id"],
                    "correlation_id": request["correlation_id"],
                    "configuration_fingerprint": request["configuration_fingerprint"],
                    "tower_version": "0.5.0", "chain_binding_version": "tower-chain-binding-v1",
                    "chain_response_contract_version": "tower-chain-response-v1",
                    "chain_fingerprint": "fake-chain-fp", "chain_status": "fake_status",
                    "terminal_reason_code": "fake_reason", "ok": True,
                    "n2_output": self._n2_output, "n3_output": self._n3_output, "n4_output": self._n4_output,
                    "session_id": _SESSION.session_id,
                    "worker_identity_fingerprint": _SESSION.worker_identity_fingerprint,
                    "reason_codes": [],
                }
                conn.sendall(pack_frame(json.dumps(response).encode("utf-8")))
            finally:
                conn.close()

    def stop(self) -> None:
        self._stop = True
        self._sock.close()
        self._thread.join(timeout=2.0)


def _client_for(worker: _FakeWorker) -> TowerClient:
    return TowerClient(
        TowerClientConfig(host=worker.host, port=worker.port, timeout_seconds=2.0), session=_SESSION,
    )


def _last_bar(builder: RawAxesBuilder) -> Bar:
    bars = trend_up_regime_bars(_SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    return bars[-1]


_N2_DATA_IDENTITY = {"symbol": _SYMBOL, "timeframe": "H1", "bar_count": 150, "bars_content_hash": "n2-hash"}
_N3_DATA_IDENTITY = {"symbol": _SYMBOL, "timeframe": "M15", "bar_count": 150, "bars_content_hash": "n3-hash"}
_N4_DATA_IDENTITY = {"symbol": _SYMBOL, "timeframe": "M5", "bar_count": 150, "bars_content_hash": "n4-hash"}

_COMPLETE_N2_OUTPUT = {
    "bias_available": True, "contract_version": "tower-n2-request-v1", "n2_code_version": "level2-v1.0",
    "event_fingerprint": "shared-event-fp", "node_input_fingerprint": "n2-node-input-fp",
    "data_identity": _N2_DATA_IDENTITY, "output_fingerprint": "n2-output-fp",
}
_COMPLETE_N3_OUTPUT = {
    "market_map_available": True, "levels_available": True, "contract_version": "tower-n3-request-v2",
    "n3_version": "level3-v2.0-reanchored", "event_fingerprint": "shared-event-fp",
    "node_input_fingerprint": "n3-node-input-fp", "data_identity": _N3_DATA_IDENTITY,
}
_COMPLETE_N4_OUTPUT = {
    "confirmation_available": True, "contract_version": "tower-n4-request-v2",
    "n4_version": "level4-v2.0-w3", "event_fingerprint": "shared-event-fp",
    "node_input_fingerprint": "n4-node-input-fp", "data_identity": _N4_DATA_IDENTITY,
}


def test_tower_chain_true_result_flows_into_the_decision_request() -> None:
    """`n2_output`/`n3_output`/`n4_output` now carry the SAME identity fields the real worker actually
    returns (empirically confirmed against the real installed `ve_tower` 0.5.0, RT-TOWER-0008) -- a
    minimal payload missing these is correctly treated as `TOWER_IDENTITY_UNAVAILABLE` (see the dedicated
    test below), not as a bug here."""
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        gateway = _default_gateway()
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        reached_n6 = [o for o in outcomes if o.strategy_id == "trend_pullback"]
        assert reached_n6, "expected trend_pullback to reach N6"
        outcome = reached_n6[0]
        assert outcome.decision is not None
        # MISSING_LEVEL_INPUT must be GONE now that all three flags are True -- whatever N6 decides
        # instead is real ve_brain logic (EV/probability gates), not asserted here; only that the tower
        # gap itself no longer fires.
        assert ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value not in outcome.decision.reason_codes
        n2_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN2")
        n3_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN3")
        n4_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN4")
        assert n2_trace.component_version == "tower-n2-request-v1"
        assert n3_trace.component_version == "tower-n3-request-v2"
        assert n4_trace.component_version == "tower-n4-request-v2"
        assert n2_trace.input_fingerprint == "n2-node-input-fp"
        assert n3_trace.input_fingerprint == "n3-node-input-fp"
        assert n4_trace.input_fingerprint == "n4-node-input-fp"
        # distinct per node, per the CEO's own rule (N2 answers on H1, N3 on M15, N4 on M5)
        assert len({n2_trace.input_fingerprint, n3_trace.input_fingerprint, n4_trace.input_fingerprint}) == 3
        assert outcome.event_identity.n2_data_identity != outcome.event_identity.n3_data_identity
        assert outcome.event_identity.n3_data_identity != outcome.event_identity.n4_data_identity
        assert (
            outcome.event_identity.n2_event_fingerprint
            == outcome.event_identity.n3_event_fingerprint
            == outcome.event_identity.n4_event_fingerprint
            == "shared-event-fp"
        )
        assert outcome.event_identity.worker_session_id == _SESSION.session_id
        assert outcome.event_identity.worker_identity_fingerprint == _SESSION.worker_identity_fingerprint
        assert outcome.event_identity.chain_fingerprint == "fake-chain-fp"
        assert gateway.copy_rates_from_calls, "expected the tower path to actually fetch bars"
    finally:
        worker.stop()


def test_tower_chain_response_missing_identity_fields_degrades_to_identity_unavailable() -> None:
    """A minimal payload (booleans only, no identity fields) must be treated as `TOWER_IDENTITY_
    UNAVAILABLE`, fail-closed -- never silently accepted as available with no identity."""
    worker = _FakeWorker(
        n2_output={"bias_available": True}, n3_output={"market_map_available": True, "levels_available": True},
        n4_output={"confirmation_available": True},
    )
    try:
        gateway = _default_gateway()
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        outcome = next(o for o in outcomes if o.strategy_id == "trend_pullback")
        assert outcome.decision is not None
        assert outcome.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
        n2_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN2")
        assert "TOWER_IDENTITY_UNAVAILABLE" in n2_trace.reason_codes
        assert outcome.event_identity.n2_data_identity is None  # never a fabricated substitute
        assert outcome.event_identity.n3_data_identity is None
    finally:
        worker.stop()


def test_tower_chain_node_event_fingerprint_disagreement_degrades_to_identity_mismatch() -> None:
    """A worker reply where N2/N3/N4 disagree on `event_fingerprint` (same event, different node
    identity) must degrade to `CHAIN_IDENTITY_MISMATCH`, fail-closed -- this can never happen from the
    real worker (all three come from the SAME request/event), but a corrupted or impostor reply must
    still be caught here, not trusted."""
    worker = _FakeWorker(
        n2_output={**_COMPLETE_N2_OUTPUT, "event_fingerprint": "event-fp-N2"},
        n3_output={**_COMPLETE_N3_OUTPUT, "event_fingerprint": "event-fp-N3"},
        n4_output={**_COMPLETE_N4_OUTPUT, "event_fingerprint": "event-fp-N4"},
    )
    try:
        gateway = _default_gateway()
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        outcome = next(o for o in outcomes if o.strategy_id == "trend_pullback")
        assert outcome.decision is not None
        assert outcome.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
        n2_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN2")
        assert "CHAIN_IDENTITY_MISMATCH" in n2_trace.reason_codes
    finally:
        worker.stop()


def test_tower_unavailable_result_keeps_all_flags_false() -> None:
    """Worker unreachable (no established session, the simplest genuine failure mode) -- must degrade
    exactly like `tower=None`, never crash, never fabricate `True`."""
    worker = _FakeWorker(n2_output=None, n3_output=None, n4_output=None)
    try:
        gateway = _default_gateway()
        # No established session at all -- HANDSHAKE_NOT_ESTABLISHED.
        client = TowerClient(TowerClientConfig(host=worker.host, port=worker.port), session=None)
        tower = TowerDependencies(client=client, gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        outcome = next(o for o in outcomes if o.strategy_id == "trend_pullback")
        assert outcome.decision is not None
        assert outcome.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
        n2_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN2")
        assert n2_trace.reason_codes == ("HANDSHAKE_NOT_ESTABLISHED",)
        assert outcome.event_identity.worker_session_id is None  # no session -- never a fabricated one
    finally:
        worker.stop()


def test_tower_is_queried_at_most_once_per_side_shared_across_catalog() -> None:
    """Every entry in `ve_brain.CANONICAL_STRATEGIES` today is `allowed_directions=("LONG",)`, so `side`
    is the SAME (1) for every eligible strategy this bar -- confirming ONE chain call, memoized by side,
    not one call per bar regardless of strategy identity and not one call per strategy."""
    worker = _FakeWorker(
        n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT,
        n4_output={**_COMPLETE_N4_OUTPUT, "confirmation_available": False},
    )
    try:
        gateway = _default_gateway()
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        assert len(outcomes) == len(ve_brain.CANONICAL_STRATEGIES)
        assert worker.connection_count == 1, (
            f"expected exactly one tower connection shared across every strategy sharing the same side, "
            f"got {worker.connection_count}"
        )
    finally:
        worker.stop()


def test_tower_never_queried_when_no_strategy_reaches_geometry() -> None:
    """ATR history insufficient (too few bars) -- the tower must never be called at all: `_get_chain_
    result` is lazy, and no strategy this bar ever reaches the point that needs it."""
    worker = _FakeWorker(n2_output=None, n3_output=None, n4_output=None)
    try:
        gateway = _FakeTimeframeAwareGateway(h1_rates=(), m15_rates=(), m5_rates=())
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        price = 2400.0
        last_bar = None
        for i in range(3):
            last_bar = Bar(symbol=_SYMBOL, ts_open=i * 900, ts_close=(i + 1) * 900, open=price,
                            high=price + 0.5, low=price - 0.5, close=price + 0.1, volume=100.0)
            builder.observe(last_bar)
        assert last_bar is not None

        evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        assert worker.connection_count == 0, "the tower must never be contacted when no strategy needs it"
        assert not gateway.copy_rates_from_calls, "bar history must never be fetched when the tower is never queried"
    finally:
        worker.stop()


def test_side_is_derived_from_the_strategy_contract_never_a_default() -> None:
    """CEO section 3 (2026-08-17): `side` must come from the eligible strategy's own contracted
    `allowed_directions`, never a bridge.py-level default. Every catalog strategy today is LONG-only, so
    this proves `side=1` reaches the wire, and the trace discloses ITS OWN provenance string."""
    worker = _FakeWorker(n2_output=_COMPLETE_N2_OUTPUT, n3_output=_COMPLETE_N3_OUTPUT, n4_output=_COMPLETE_N4_OUTPUT)
    try:
        gateway = _default_gateway()
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        outcome = next(o for o in outcomes if o.strategy_id == "trend_pullback")
        n2_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN2")

        from ai_trader.new_brain_bridge.bridge import _fp, _side_provenance

        canon = next(c for c in ve_brain.CANONICAL_STRATEGIES if c.strategy_id == "trend_pullback")
        assert canon.allowed_directions[0] == "LONG"  # the real, current catalog fact this test relies on
        expected_provenance = _side_provenance(canon)
        assert "trend_pullback" in expected_provenance and "LONG" in expected_provenance
        # decisive proof: the TowerN2 trace's own output is a fingerprint OVER this exact provenance
        # string -- recomputing it independently proves `side` genuinely reached the trace, sourced from
        # the strategy contract, not a bridge.py-level default.
        assert n2_trace.output == _fp(
            str(_COMPLETE_N2_OUTPUT["bias_available"] is True), "n2-output-fp", "1", expected_provenance,
        )
        assert outcome.decision is not None
    finally:
        worker.stop()
