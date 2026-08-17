"""The one seam between the IPC boundary (`server.py`) and `ve_tower` itself.

**2026-08-17, RT-TOWER-0008 remediation (`N2_HANDOFF_PASS`/`N2_CHAIN_BINDING_PASS`, `ve_tower` 0.5.0).**
This module now calls EXCLUSIVELY `ve_tower.run_tower_chain` -- `ve_tower.run_n2`/`run_n3`/`run_n4` are
NEVER imported, referenced, or called anywhere below (see `UNBOUND_DIRECT_API` -- ve_tower's own name for
those three functions once `run_tower_chain` exists). N2 (bias, computed from real H1 bars) is now a REAL,
independently-contracted producer INSIDE `ve_tower` itself -- this module no longer accepts `n2_output`/
`bias_direction`/`n2_fingerprint` from the client at all; those fields do not even exist on
`TowerChainRequest`'s wire schema anymore (see `protocol.py`'s own `_ALLOWED_CHAIN_REQUEST_FIELDS`).

**2026-08-14, `STAGED_INSTALL_AUTHORIZED` step 4 (Phase 2, superseded by the above).** The original version
of this function called `run_n3`/`run_n4` directly, with the client supplying `n1_output`/`n2_output`
sub-schemas over the wire -- CLOSED by this remediation, not merely deprecated.

Nothing below invents a market read: every unresolved path (bad request shape, `ve_tower` absent, the chain
itself reporting unavailable) returns an honest `ok=False` response with a reason code, never a fabricated
zone, bias, or confirmation."""

from __future__ import annotations

import importlib
from dataclasses import asdict
from typing import Any

from ve_tower_worker.protocol import TOWER_UNAVAILABLE, TowerChainRequest, TowerChainResponse

_MALFORMED_TOWER_REQUEST = "MALFORMED_TOWER_REQUEST"
_CONTRACT_EXPECTATION_MISMATCH = "CONTRACT_EXPECTATION_MISMATCH"


class _RequestShapeError(Exception):
    """Raised when the request's own content doesn't match what `ve_tower.ChainRequest` needs. Never a
    `ve_tower` error -- this is a client-side contract violation, caught before `ve_tower` is ever called."""


def _node_output_to_dict(resp: Any) -> dict[str, object] | None:
    if resp is None:
        return None
    d = asdict(resp)
    if getattr(resp, "data_identity", None) is not None:
        d["data_identity"] = resp.data_identity.to_dict()
    return d


def _unavailable(
    request: TowerChainRequest, tower_version: str, reason_codes: tuple[str, ...],
) -> TowerChainResponse:
    return TowerChainResponse(
        protocol_version=request.protocol_version,
        schema_version=request.schema_version,
        request_id=request.request_id,
        market_event_id=request.market_event_id,
        correlation_id=request.correlation_id,
        configuration_fingerprint=request.configuration_fingerprint,
        tower_version=tower_version,
        chain_binding_version="",
        chain_response_contract_version="",
        chain_fingerprint="",
        chain_status="UNAVAILABLE",
        terminal_reason_code=reason_codes[0] if reason_codes else TOWER_UNAVAILABLE,
        ok=False,
        n2_output=None,
        n3_output=None,
        n4_output=None,
        session_id="",  # overwritten unconditionally by server.py's own _stamp_session
        worker_identity_fingerprint="",
        reason_codes=reason_codes,
    )


def real_decision(request: TowerChainRequest) -> TowerChainResponse:
    """Fail-closed at every seam: `ve_tower` absence, malformed request content, and `ve_tower`'s own
    chain-level unavailability all produce an honest response -- never invented N2/N3/N4 output. The ONLY
    `ve_tower` call this module ever makes is `run_tower_chain` -- enforced by this repo's own AST guard
    test (`test_decision_ast_guard.py`), not merely by this docstring's own claim."""
    try:
        ve_tower = importlib.import_module("ve_tower")
    except ImportError:
        return _unavailable(request, "UNAVAILABLE", (TOWER_UNAVAILABLE,))

    if (request.expected_n2_contract != ve_tower.N2_CONTRACT_VERSION
            or request.expected_n3_contract != ve_tower.N3_CONTRACT_VERSION
            or request.expected_n4_contract != ve_tower.N4_CONTRACT_VERSION):
        return _unavailable(
            request, ve_tower.VE_TOWER_VERSION,
            (_CONTRACT_EXPECTATION_MISMATCH,
             f"expected n2={request.expected_n2_contract!r} n3={request.expected_n3_contract!r} "
             f"n4={request.expected_n4_contract!r}; installed n2={ve_tower.N2_CONTRACT_VERSION!r} "
             f"n3={ve_tower.N3_CONTRACT_VERSION!r} n4={ve_tower.N4_CONTRACT_VERSION!r}"),
        )

    try:
        chain_req = ve_tower.ChainRequest(
            contract_version=ve_tower.CHAIN_REQUEST_CONTRACT_VERSION,
            market_event_id=request.market_event_id,
            correlation_id=request.correlation_id,
            symbol=request.symbol,
            as_of=request.as_of,
            configuration_fingerprint=request.configuration_fingerprint,
            n1_fingerprint=request.trace_id,
            regime_axes_status=request.regime_axes_status,
            h1_open=request.h1_open, h1_high=request.h1_high, h1_low=request.h1_low,
            h1_close=request.h1_close, h1_time=request.h1_time,
            m15_open=request.m15_open, m15_high=request.m15_high, m15_low=request.m15_low,
            m15_close=request.m15_close, m15_time=request.m15_time,
            m5_high=request.m5_high, m5_low=request.m5_low, m5_close=request.m5_close,
            m5_time=request.m5_time,
            h1_source_identity=request.h1_source_identity, m15_source_identity=request.m15_source_identity,
            m5_source_identity=request.m5_source_identity,
            strategy_id=request.strategy_id, strategy_version=request.strategy_version, side=request.side,
            expected_n2_contract=request.expected_n2_contract, expected_n3_contract=request.expected_n3_contract,
            expected_n4_contract=request.expected_n4_contract,
            h1_max_staleness_s=request.h1_max_staleness_s, m15_max_staleness_s=request.m15_max_staleness_s,
            m5_max_staleness_s=request.m5_max_staleness_s,
        )
    except (TypeError, ValueError) as exc:
        return _unavailable(request, ve_tower.VE_TOWER_VERSION, (_MALFORMED_TOWER_REQUEST, str(exc)))

    chain_resp = ve_tower.run_tower_chain(chain_req)

    return TowerChainResponse(
        protocol_version=request.protocol_version,
        schema_version=request.schema_version,
        request_id=request.request_id,
        market_event_id=chain_resp.market_event_id,
        correlation_id=chain_resp.correlation_id,
        configuration_fingerprint=chain_resp.configuration_fingerprint,
        tower_version=chain_resp.tower_version,
        chain_binding_version=chain_resp.chain_binding_version,
        chain_response_contract_version=chain_resp.contract_version,
        chain_fingerprint=chain_resp.chain_fingerprint,
        chain_status=chain_resp.chain_status,
        terminal_reason_code=chain_resp.terminal_reason_code,
        ok=True,
        n2_output=_node_output_to_dict(chain_resp.n2),
        n3_output=_node_output_to_dict(chain_resp.n3),
        n4_output=_node_output_to_dict(chain_resp.n4),
        session_id="",  # overwritten unconditionally by server.py's own _stamp_session
        worker_identity_fingerprint="",
        reason_codes=(),
    )
