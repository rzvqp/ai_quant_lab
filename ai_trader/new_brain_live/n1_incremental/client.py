"""`N1IncrementalClient` -- the ONLY file in the main AI Trader process/venv allowed to know about the
isolated N1 replay worker. Never imports `ve_n1_replay`; talks to it exclusively via `subprocess.run`
against `.ai_trader_n1_venv`'s own interpreter (AI-Trader-exclusive -- never `.alpha_n1_venv`, see
`artifact_pin.py`'s environment-split note), one call per invocation, JSON over stdin/stdout.
Reconstructs `ve_brain.RawAxes`/`ve_brain.EligibilityDecision` from the worker's JSON response using the
MAIN venv's own `ve_brain` (both venvs pin the identical 0.1.3 wheel, verified in `artifact_pin.py`'s
sibling identity checks) -- the exact same serialize/deserialize convention `dual_clock.upstream_
context.py` already established for the bounded hydration path, reused here rather than reinvented.
Every response's own `artifact` identity block is additionally checked per-call against the pin
(`artifact_pin.verify_artifact_identity`) -- fail-closed defense-in-depth against the environment
drifting DURING a long-running process's lifetime, not just at startup."""

from __future__ import annotations

import dataclasses
import json
import subprocess
from pathlib import Path
from typing import Any

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.no_console_window import NO_CONSOLE_WINDOW_CREATIONFLAGS
from ai_trader.new_brain_live.n1_incremental import artifact_pin
from ai_trader.new_brain_live.n1_incremental.artifact_pin import AI_TRADER_N1_VENV_PYTHON

_WORKER_SCRIPT = Path(__file__).resolve().parent / "worker_script.py"
DEFAULT_TIMEOUT_SECONDS = 60.0


class N1IncrementalWorkerError(Exception):
    """The worker process itself failed (non-zero exit, timeout, or malformed JSON) -- distinct from a
    normal, well-formed `rejected=True` response (identity mismatch / stale / future bar), which is not
    an error, just a fail-closed outcome the caller must handle as NO_TRADE."""


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class N1IncrementalResult:
    raw_axes: Any  # ve_brain.RawAxes
    applicable_regimes: frozenset[str]
    eligibility_decisions: tuple[Any, ...]  # tuple[ve_brain.EligibilityDecision, ...]
    n1_output_fingerprint: str
    router_output_fingerprint: str
    output_fingerprint: str
    input_data_identity: str
    reason_codes: tuple[str, ...]
    regime_axes_status: tuple[str, ...]
    availability_status: str
    last_closed_bar: Bar


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class N1IncrementalResponse:
    rejected: bool
    rejection_reason: str | None
    restored_from_snapshot: bool
    restore_rejected_reason: str | None
    bars_processed: int
    result: N1IncrementalResult | None
    snapshot_blob: str | None  # opaque -- persist verbatim, never parse
    identity_fingerprint: str | None


def _bar_to_dict(bar: Bar) -> dict[str, Any]:
    return {
        "symbol": bar.symbol, "ts_open": bar.ts_open, "ts_close": bar.ts_close, "open": bar.open,
        "high": bar.high, "low": bar.low, "close": bar.close, "volume": bar.volume,
        "is_backfilled": bar.is_backfilled,
    }


def _bar_from_dict(d: dict[str, Any]) -> Bar:
    return Bar(
        symbol=d["symbol"], ts_open=d["ts_open"], ts_close=d["ts_close"], open=d["open"], high=d["high"],
        low=d["low"], close=d["close"], volume=d.get("volume"), is_backfilled=d.get("is_backfilled", False),
    )


def _eligibility_from_dict(d: dict[str, Any]) -> Any:
    return ve_brain.EligibilityDecision(
        strategy_id=d["strategy_id"], strategy_version=d["strategy_version"],
        market_event_id=d["market_event_id"], regime_fingerprint=d["regime_fingerprint"],
        router_version=d["router_version"], eligible=d["eligible"], mode=ve_brain.RoutingMode(d["mode"]),
        matched_regimes=tuple(d["matched_regimes"]), reason_codes=tuple(d["reason_codes"]),
    )


def _result_from_dict(d: dict[str, Any]) -> N1IncrementalResult:
    axes_d = d["raw_axes"]
    axes = ve_brain.RawAxes(
        is_compressed=axes_d["is_compressed"], is_displacement=axes_d["is_displacement"],
        direction=axes_d["direction"], structure=axes_d["structure"],
        volatility_state=axes_d["volatility_state"], n1_contract_version=axes_d["n1_contract_version"],
        raw_axis_schema_version=axes_d["raw_axis_schema_version"],
    )
    return N1IncrementalResult(
        raw_axes=axes, applicable_regimes=frozenset(d["applicable_regimes"]),
        eligibility_decisions=tuple(_eligibility_from_dict(e) for e in d["eligibility_decisions"]),
        n1_output_fingerprint=d["n1_output_fingerprint"], router_output_fingerprint=d["router_output_fingerprint"],
        output_fingerprint=d["output_fingerprint"], input_data_identity=d["input_data_identity"],
        reason_codes=tuple(d["reason_codes"]), regime_axes_status=tuple(d["regime_axes_status"]),
        availability_status=d["availability_status"], last_closed_bar=_bar_from_dict(d["last_closed_bar"]),
    )


class N1IncrementalClient:
    def __init__(
        self, *, symbol: str, timeframe: str, bar_interval_seconds: int, implementation_commit: str,
        venv_python: Path = AI_TRADER_N1_VENV_PYTHON, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_staleness_seconds: float | None = None,
    ) -> None:
        self._symbol = symbol
        self._timeframe = timeframe
        self._bar_interval_seconds = bar_interval_seconds
        self._implementation_commit = implementation_commit
        self._venv_python = venv_python
        self._timeout_seconds = timeout_seconds
        self._max_staleness_seconds = max_staleness_seconds
        """Passed fresh into a NEW engine every call (the isolated worker never persists an engine
        instance across calls) -- staleness is judged against `wall_clock_now`, itself read fresh by the
        caller every time (`IncrementalContextRefreshLoop`'s own `wall_clock` callable), never a value
        cached at client-construction time. This is the same request-scoped-time discipline `TowerDependencies
        .wall_clock_provider` (RT-TIME-0001 section A) already established for the tower path."""

    def observe(
        self, *, bars: tuple[Bar, ...], restore_snapshot_blob: str | None, wall_clock_now: float,
    ) -> N1IncrementalResponse:
        request = {
            "symbol": self._symbol, "timeframe": self._timeframe,
            "bar_interval_seconds": self._bar_interval_seconds,
            "implementation_commit": self._implementation_commit,
            "restore_snapshot_blob": restore_snapshot_blob,
            "bars": [_bar_to_dict(b) for b in bars], "wall_clock_now": wall_clock_now,
            "max_staleness_seconds": self._max_staleness_seconds,
        }
        try:
            proc = subprocess.run(
                [str(self._venv_python), str(_WORKER_SCRIPT)], input=json.dumps(request),
                capture_output=True, text=True, timeout=self._timeout_seconds,
                creationflags=NO_CONSOLE_WINDOW_CREATIONFLAGS,
            )
        except subprocess.TimeoutExpired as exc:
            raise N1IncrementalWorkerError(f"worker timed out after {self._timeout_seconds}s") from exc

        if proc.returncode != 0:
            raise N1IncrementalWorkerError(
                f"worker exited {proc.returncode}, stderr={proc.stderr[-2000:]!r}"
            )
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise N1IncrementalWorkerError(f"worker produced non-JSON stdout: {proc.stdout[:2000]!r}") from exc

        if not data.get("ok", False):
            raise N1IncrementalWorkerError(f"worker reported an internal error: {data.get('error')}")

        artifact = data.get("artifact")
        identity_ok, identity_reason = (
            (False, "worker response carries no 'artifact' identity block")
            if artifact is None
            else artifact_pin.verify_artifact_identity(
                ve_n1_replay_version=artifact.get("ve_n1_replay_version", ""),
                ai_source_commit=artifact.get("ai_source_commit", ""),
                detector_submodule_commit=artifact.get("detector_submodule_commit", ""),
            )
        )
        if not identity_ok:
            # Per-call, fail-closed defense-in-depth (RT-N1-ENV-SPLIT-0001): a venv mutated DURING a
            # long-running process's lifetime is caught here, not just at startup by verify_pin(). Never
            # surfaces `result` on a mismatch, regardless of what the worker otherwise computed.
            return N1IncrementalResponse(
                rejected=True, rejection_reason=f"ARTIFACT_VERSION_MISMATCH: {identity_reason}",
                restored_from_snapshot=False, restore_rejected_reason=None, bars_processed=0,
                result=None, snapshot_blob=None, identity_fingerprint=None,
            )

        result_data = data.get("last_result")
        return N1IncrementalResponse(
            rejected=data["rejected"], rejection_reason=data.get("rejection_reason"),
            restored_from_snapshot=data["restored_from_snapshot"],
            restore_rejected_reason=data.get("restore_rejected_reason"),
            bars_processed=data["bars_processed"],
            result=None if result_data is None else _result_from_dict(result_data),
            snapshot_blob=data.get("snapshot_blob"),
            identity_fingerprint=None if data.get("identity") is None else data["identity"]["fingerprint"],
        )
