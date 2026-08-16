"""`evaluate_bar`'s `tower=` wiring (CEO Phase 2 step 5, 2026-08-14) -- proves the three flags
(`market_map_available`/`levels_available`/`confirmation_available`) genuinely come from whatever
`TowerClient.request_n3_n4` returns, are queried AT MOST ONCE per bar (shared across the whole catalog),
and degrade to all-`False` on every failure mode -- never fabricated `True`.

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
    worker_package_version="0.2.0", worker_delivery_commit="abc123", protocol_version="2.0",
    ve_tower_package_version="0.3.0", package_build_commit="6daf2aa", state_delivery_commit="0207ffa",
    wheel_sha256="deadbeef" * 8, vendored_source_identity="vendored-digest", n3_contract_version="1.0",
    n4_contract_version="1.0",
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
    """Returns different bars for M15 vs M5, keyed by `mt5_timeframe` -- unlike
    `live_signal_source/tests/_fixtures.py`'s `FakeMT5Gateway` (single-timeframe by design), this fake
    exists specifically to prove `tower_bar_source.fetch_tower_bar_windows` fetches BOTH windows."""

    def __init__(self, *, m15_rates: Any, m5_rates: Any) -> None:
        self._rates_by_timeframe = {15: m15_rates, 5: m5_rates}
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


class _FakeWorker:
    """Accepts exactly one connection, replies with a fixed N3/N4 payload -- built directly from
    `tower_protocol`'s own framing, mirroring `test_tower_client.py`'s `_FakeServer`."""

    def __init__(self, *, n3_output: dict[str, object] | None, n4_output: dict[str, object] | None) -> None:
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
                    "type": "n3n4_response", "protocol_version": "2.0", "schema_version": "2.0",
                    "request_id": request["request_id"], "market_event_id": request["market_event_id"],
                    "event_fingerprint": "worker-computed-fp", "tower_version": "0.3.0", "ok": True,
                    "n3_output": self._n3_output, "n4_output": self._n4_output,
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


_N3_DATA_IDENTITY = {"symbol": _SYMBOL, "timeframe": "M15", "bar_count": 150, "bars_content_hash": "n3-hash"}
_N4_DATA_IDENTITY = {"symbol": _SYMBOL, "timeframe": "M5", "bar_count": 150, "bars_content_hash": "n4-hash"}


def test_tower_true_result_flows_into_the_decision_request() -> None:
    """`n3_output`/`n4_output` now carry the SAME identity fields the real worker actually returns
    (contract_version/event_fingerprint/node_input_fingerprint/data_identity -- empirically confirmed
    against the real installed `ve_tower` 0.3.0, RT-MANDATE2-0002) -- a minimal payload missing these is
    correctly treated as `TOWER_IDENTITY_UNAVAILABLE` (see the dedicated test below), not as a bug here."""
    worker = _FakeWorker(
        n3_output={
            "market_map_available": True, "levels_available": True, "contract_version": "tower-n3-request-v2",
            "n3_version": "level3-v2.0-reanchored", "event_fingerprint": "shared-event-fp",
            "node_input_fingerprint": "n3-node-input-fp", "data_identity": _N3_DATA_IDENTITY,
        },
        n4_output={
            "confirmation_available": True, "contract_version": "tower-n4-request-v2",
            "n4_version": "level4-v2.0-w3", "event_fingerprint": "shared-event-fp",
            "node_input_fingerprint": "n4-node-input-fp", "data_identity": _N4_DATA_IDENTITY,
        },
    )
    try:
        gateway = _FakeTimeframeAwareGateway(
            m15_rates=_closed_rates(count=150, step=900, now=10_000_000, start_price=2000.0),
            m5_rates=_closed_rates(count=150, step=300, now=10_000_000, start_price=2010.0),
        )
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
        n3_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN3")
        n4_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN4")
        assert n3_trace.component_version == "tower-n3-request-v2"
        assert n4_trace.component_version == "tower-n4-request-v2"
        assert n3_trace.input_fingerprint == "n3-node-input-fp"
        assert n4_trace.input_fingerprint == "n4-node-input-fp"
        assert n3_trace.input_fingerprint != n4_trace.input_fingerprint  # distinct per node, per the CEO's own rule
        # N4->N3 response linkage: TowerN4's own output is a fingerprint OVER n3's event_fingerprint --
        # changing n3's event_fingerprint (see the mismatch test below) provably changes n4_trace.output too.
        from ai_trader.new_brain_bridge.bridge import _fp
        assert n4_trace.output == _fp(str(True), "shared-event-fp", "shared-event-fp")
        assert outcome.event_identity.n3_data_identity != outcome.event_identity.n4_data_identity
        assert outcome.event_identity.n3_event_fingerprint == outcome.event_identity.n4_event_fingerprint == "shared-event-fp"
        assert outcome.event_identity.worker_session_id == _SESSION.session_id
        assert outcome.event_identity.worker_identity_fingerprint == _SESSION.worker_identity_fingerprint
        assert gateway.copy_rates_from_calls, "expected the tower path to actually fetch bars"
    finally:
        worker.stop()


def test_tower_response_missing_identity_fields_degrades_to_identity_unavailable() -> None:
    """The pre-remediation minimal payload (booleans only, no identity fields) must now be treated as
    `TOWER_IDENTITY_UNAVAILABLE`, fail-closed -- never silently accepted as available with no identity."""
    worker = _FakeWorker(
        n3_output={"market_map_available": True, "levels_available": True},
        n4_output={"confirmation_available": True},
    )
    try:
        gateway = _FakeTimeframeAwareGateway(
            m15_rates=_closed_rates(count=150, step=900, now=10_000_000, start_price=2000.0),
            m5_rates=_closed_rates(count=150, step=300, now=10_000_000, start_price=2010.0),
        )
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        outcome = next(o for o in outcomes if o.strategy_id == "trend_pullback")
        assert outcome.decision is not None
        assert outcome.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
        n3_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN3")
        assert "TOWER_IDENTITY_UNAVAILABLE" in n3_trace.reason_codes
        assert outcome.event_identity.n3_data_identity is None  # never a fabricated substitute
    finally:
        worker.stop()


def test_tower_n3_n4_event_fingerprint_disagreement_degrades_to_identity_mismatch() -> None:
    """A worker reply where N3 and N4 disagree on `event_fingerprint` (same event, different node
    identity) must degrade to `TOWER_IDENTITY_MISMATCH`, fail-closed -- this can never happen from the
    real worker (both come from the SAME request/event), but a corrupted or impostor reply must still be
    caught here, not trusted."""
    worker = _FakeWorker(
        n3_output={
            "market_map_available": True, "levels_available": True, "contract_version": "tower-n3-request-v2",
            "n3_version": "level3-v2.0-reanchored", "event_fingerprint": "event-fp-A",
            "node_input_fingerprint": "n3-node-input-fp", "data_identity": _N3_DATA_IDENTITY,
        },
        n4_output={
            "confirmation_available": True, "contract_version": "tower-n4-request-v2",
            "n4_version": "level4-v2.0-w3", "event_fingerprint": "event-fp-B",
            "node_input_fingerprint": "n4-node-input-fp", "data_identity": _N4_DATA_IDENTITY,
        },
    )
    try:
        gateway = _FakeTimeframeAwareGateway(
            m15_rates=_closed_rates(count=150, step=900, now=10_000_000, start_price=2000.0),
            m5_rates=_closed_rates(count=150, step=300, now=10_000_000, start_price=2010.0),
        )
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        outcome = next(o for o in outcomes if o.strategy_id == "trend_pullback")
        assert outcome.decision is not None
        assert outcome.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
        n3_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN3")
        assert "TOWER_IDENTITY_MISMATCH" in n3_trace.reason_codes
    finally:
        worker.stop()


def test_tower_unavailable_result_keeps_all_three_flags_false() -> None:
    """Worker refuses (`ok=False` via a malformed n3/n4 pair -- here simulated by the worker returning a
    session_id that doesn't match, forcing `TowerUnavailableResult`) -- must degrade exactly like
    `tower=None`, never crash, never fabricate `True`."""
    worker = _FakeWorker(n3_output=None, n4_output=None)
    try:
        gateway = _FakeTimeframeAwareGateway(
            m15_rates=_closed_rates(count=150, step=900, now=10_000_000, start_price=2000.0),
            m5_rates=_closed_rates(count=150, step=300, now=10_000_000, start_price=2010.0),
        )
        # No established session at all -- HANDSHAKE_NOT_ESTABLISHED, the simplest genuine failure mode.
        client = TowerClient(TowerClientConfig(host=worker.host, port=worker.port), session=None)
        tower = TowerDependencies(client=client, gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        outcome = next(o for o in outcomes if o.strategy_id == "trend_pullback")
        assert outcome.decision is not None
        assert outcome.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
        n3_trace = next(t for t in outcome.node_traces if t.node_name == "TowerN3")
        assert n3_trace.reason_codes == ("HANDSHAKE_NOT_ESTABLISHED",)
        assert outcome.event_identity.worker_session_id is None  # no session -- never a fabricated one
    finally:
        worker.stop()


def test_tower_is_queried_at_most_once_per_bar_shared_across_catalog() -> None:
    worker = _FakeWorker(
        n3_output={"market_map_available": True, "levels_available": True},
        n4_output={"confirmation_available": False},
    )
    try:
        gateway = _FakeTimeframeAwareGateway(
            m15_rates=_closed_rates(count=150, step=900, now=10_000_000, start_price=2000.0),
            m5_rates=_closed_rates(count=150, step=300, now=10_000_000, start_price=2010.0),
        )
        tower = TowerDependencies(client=_client_for(worker), gateway=gateway, now=10_000_000)  # type: ignore[arg-type]

        builder = RawAxesBuilder(_SYMBOL)
        last_bar = _last_bar(builder)
        outcomes = evaluate_bar(last_bar, timeframe=_TIMEFRAME, axes_builder=builder, tower=tower)

        assert len(outcomes) == len(ve_brain.CANONICAL_STRATEGIES)
        assert worker.connection_count == 1, (
            f"expected exactly one tower connection shared across the whole catalog, got "
            f"{worker.connection_count}"
        )
    finally:
        worker.stop()


def test_tower_never_queried_when_no_strategy_reaches_geometry() -> None:
    """ATR history insufficient (too few bars) -- the tower must never be called at all: `_get_tower_
    result` is lazy, and no strategy this bar ever reaches the point that needs it."""
    worker = _FakeWorker(n3_output=None, n4_output=None)
    try:
        gateway = _FakeTimeframeAwareGateway(m15_rates=(), m5_rates=())
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
