"""The one seam between the IPC boundary (`server.py`) and `ve_tower` itself.

**2026-08-14, `STAGED_INSTALL_AUTHORIZED` step 4 (Phase 2).** `ve_tower` 0.3.0 is now genuinely installed
in this venv (see `tower_worker/env/install_ve_tower.ps1`) -- this function now calls the REAL `run_n3`/
`run_n4` gates. Nothing below invents a market read: every unresolved path (bad request shape, `ve_tower`
absent, N3/N4 themselves reporting unavailable) returns an honest `ok=False`/`*_available=False` response
with a reason code, never a fabricated zone or confirmation.

**Wire-level sub-schema this function requires** (not enforced by `protocol.TowerRequest`'s own dataclass,
since its `n1_output`/`n2_output`/`*_closed_bars` fields are intentionally untyped `dict[str, object]` at
the transport layer -- this is the CONTENT contract layered on top, owned by this module alone):

- `n1_output` = `{"available": bool, "fingerprint": str}` -- N1 (regime) cascade gate + its own identity.
- `n2_output` = `{"available": bool, "fingerprint": str, "bias_direction": "LONG" | "SHORT" | None}` --
  N2 (bias) cascade gate + identity + the actual directional call. `bias_direction` is REQUIRED to select
  a side for N4 (see below) -- `n1_output` carries no analogous value because N3 never needs one.
- `m15_closed_bars` / `m5_closed_bars` = list of `{"time": int, "open": float, "high": float,
  "low": float, "close": float}` (epoch-seconds `time`, strictly ascending, all `<= as_of`; `open` is
  accepted but unused for M5/N4, which only reads high/low/close). Ordinary closed candle OHLCV -- the
  same shape `ai_trader.live_signal_source.types.Bar` already carries, deliberately NOT reusing that type
  directly so this module has zero import-time dependency on the rest of `ai_trader`.
- `as_of` = epoch seconds as a base-10 string (`TowerRequest.as_of` is `str` at the wire level to stay a
  JSON primitive with no ambiguity about units; this module is the one place it becomes `ve_tower`'s own
  `int`).

**N4's level/side selection is a genuine, disclosed policy call, not something `ve_tower` itself dictates**
(`ve_tower` only confirms a level/side it's TOLD -- it doesn't rank strategies): this module runs N4 against
N3's own **top-ranked zone** (`min(relative_rank)` -- `ve_tower`'s own ordering, not a new metric invented
here) in the direction `n2_output`'s `bias_direction` supplies. If N3 found no map, or `bias_direction` is
`None`/absent, N4 is never called and `n4_output` is `None` -- consistent with the real N3->N4 cascade
`ve_tower` itself enforces (`ZONE_UNAVAILABLE` when `n3_market_map_available=False`)."""

from __future__ import annotations

import importlib
from dataclasses import asdict
from typing import Any

from ve_tower_worker.protocol import TOWER_UNAVAILABLE, TowerRequest, TowerResponse

_MALFORMED_TOWER_REQUEST = "MALFORMED_TOWER_REQUEST"
_MISSING_BIAS_DIRECTION = "MISSING_BIAS_DIRECTION_N4_SKIPPED"


class _RequestShapeError(Exception):
    """Raised when `n1_output`/`n2_output`/bar-list content doesn't match this module's own sub-schema.
    Never a `ve_tower` error -- this is a client-side contract violation, caught before `ve_tower` is
    ever called."""


def _require_bars(raw_bars: tuple[dict[str, object], ...]) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...]]:
    opens: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    closes: list[float] = []
    times: list[int] = []
    for bar in raw_bars:
        try:
            opens.append(float(bar.get("open", 0.0)))  # type: ignore[arg-type]
            highs.append(float(bar["high"]))  # type: ignore[arg-type]
            lows.append(float(bar["low"]))  # type: ignore[arg-type]
            closes.append(float(bar["close"]))  # type: ignore[arg-type]
            times.append(int(bar["time"]))  # type: ignore[call-overload]
        except (KeyError, TypeError, ValueError) as exc:
            raise _RequestShapeError(f"malformed bar entry: {bar!r} ({exc})") from exc
    return tuple(opens), tuple(highs), tuple(lows), tuple(closes), tuple(times)


def _require_node_output(raw: dict[str, object], *, node: str) -> tuple[bool, str]:
    available = raw.get("available")
    fingerprint = raw.get("fingerprint")
    if not isinstance(available, bool) or not isinstance(fingerprint, str):
        raise _RequestShapeError(f"{node}_output missing/malformed 'available' (bool) or 'fingerprint' (str)")
    return available, fingerprint


def _bias_direction(n2_output: dict[str, object]) -> str | None:
    value = n2_output.get("bias_direction")
    if value is None:
        return None
    if value not in ("LONG", "SHORT"):
        raise _RequestShapeError(f"n2_output.bias_direction must be 'LONG', 'SHORT', or null; got {value!r}")
    return value


def _parse_as_of(raw: str) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise _RequestShapeError(f"as_of must be an epoch-seconds decimal string; got {raw!r}") from exc


def _n3_response_to_dict(n3_resp: Any) -> dict[str, object]:
    d = asdict(n3_resp)
    if n3_resp.data_identity is not None:
        d["data_identity"] = n3_resp.data_identity.to_dict()
    return d


def _n4_response_to_dict(n4_resp: Any) -> dict[str, object]:
    d = asdict(n4_resp)
    if n4_resp.data_identity is not None:
        d["data_identity"] = n4_resp.data_identity.to_dict()
    return d


def _unavailable(request: TowerRequest, tower_version: str, reason_codes: tuple[str, ...]) -> TowerResponse:
    return TowerResponse(
        protocol_version=request.protocol_version,
        schema_version=request.schema_version,
        request_id=request.request_id,
        market_event_id=request.market_event_id,
        event_fingerprint=request.event_fingerprint,
        tower_version=tower_version,
        ok=False,
        n3_output=None,
        n4_output=None,
        session_id="",  # overwritten unconditionally by server.py's own _stamp_session
        worker_identity_fingerprint="",
        reason_codes=reason_codes,
    )


def real_decision(request: TowerRequest) -> TowerResponse:
    """Fail-closed at every seam: `ve_tower` absence, malformed request content, and `ve_tower`'s own
    N3/N4 unavailability all produce an honest response -- never invented N3/N4 output."""
    try:
        ve_tower = importlib.import_module("ve_tower")
    except ImportError:
        return _unavailable(request, "UNAVAILABLE", (TOWER_UNAVAILABLE,))

    try:
        m15_open, m15_high, m15_low, m15_close, m15_time = _require_bars(request.m15_closed_bars)
        m5_open, m5_high, m5_low, m5_close, m5_time = _require_bars(request.m5_closed_bars)
        as_of = _parse_as_of(request.as_of)
        n1_available, n1_fp = _require_node_output(request.n1_output, node="n1")
        n2_available, n2_fp = _require_node_output(request.n2_output, node="n2")
        bias_direction = _bias_direction(request.n2_output)
    except _RequestShapeError as exc:
        return _unavailable(request, ve_tower.VE_TOWER_VERSION, (_MALFORMED_TOWER_REQUEST, str(exc)))

    n3_req = ve_tower.N3Request(
        contract_version=ve_tower.N3_CONTRACT_VERSION,
        market_event_id=request.market_event_id,
        symbol=request.symbol,
        timeframe="M15",
        source_identity=f"tower-client:{request.symbol}:M15",
        open=m15_open, high=m15_high, low=m15_low, close=m15_close, time=m15_time,
        as_of=as_of, regime_available=n1_available, bias_available=n2_available,
        n1_fingerprint=n1_fp, n2_fingerprint=n2_fp, max_staleness_s=request.max_staleness_s,
    )
    n3_resp = ve_tower.run_n3(n3_req)

    n4_resp = None
    if n3_resp.market_map_available and n3_resp.market_map and bias_direction is not None:
        level = min(n3_resp.market_map, key=lambda z: z.relative_rank)
        side = 1 if bias_direction == "LONG" else -1
        n4_req = ve_tower.N4Request(
            contract_version=ve_tower.N4_CONTRACT_VERSION,
            market_event_id=request.market_event_id,
            symbol=request.symbol,
            timeframe="M5",
            source_identity=f"tower-client:{request.symbol}:M5",
            high=m5_high, low=m5_low, close=m5_close, time=m5_time,
            level=level.price_anchor, side=side, as_of=as_of,
            strategy_id=request.strategy_id, strategy_version=request.strategy_version,
            regime_available=n1_available, bias_available=n2_available,
            n1_fingerprint=n1_fp, n2_fingerprint=n2_fp,
            n3_market_event_id=n3_resp.market_event_id,
            n3_event_fingerprint=n3_resp.event_fingerprint,
            n3_node_input_fingerprint=n3_resp.node_input_fingerprint or "",
            n3_market_map_available=n3_resp.market_map_available,
            n3_level_zone_id=level.zone_id,
            n3_level_provenance=tuple((p.family, p.instance_count) for p in level.provenance),
            max_staleness_s=request.max_staleness_s,
        )
        n4_resp = ve_tower.run_n4(n4_req)

    reason_codes: tuple[str, ...] = tuple(n3_resp.reason_codes)
    if n3_resp.market_map_available and bias_direction is None:
        reason_codes = reason_codes + (_MISSING_BIAS_DIRECTION,)
    if n4_resp is not None:
        reason_codes = reason_codes + tuple(n4_resp.reason_codes)

    return TowerResponse(
        protocol_version=request.protocol_version,
        schema_version=request.schema_version,
        request_id=request.request_id,
        market_event_id=request.market_event_id,
        event_fingerprint=n3_resp.event_fingerprint,
        tower_version=ve_tower.VE_TOWER_VERSION,
        ok=True,
        n3_output=_n3_response_to_dict(n3_resp),
        n4_output=_n4_response_to_dict(n4_resp) if n4_resp is not None else None,
        session_id="",  # overwritten unconditionally by server.py's own _stamp_session
        worker_identity_fingerprint="",
        reason_codes=reason_codes,
    )
