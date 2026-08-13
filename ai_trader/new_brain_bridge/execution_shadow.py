"""`attempt_shadow_execution` -- Mandate 2 continuation, section 3 (CEO, 2026-08-14): "Un candidat
COMPLET APROBAT upstream trebuie sa ajunga pana la bariera brokerului si sa fie BLOCAT acolo. Nu e
suficient sa demonstrezi ca NO_TRADE nu trimite ordine."

This function's ENTIRE job is that one property: given a candidate `risk_gate.submit_new_brain_candidate`
has already APPROVED, actually reach `mandate2_readiness.broker_gate.BrokerOrderSubmissionGate.authorize()`
and observe what happens -- never short-circuit before the gate, never assume the outcome.

**Never modifies `BrokerOrderSubmissionGate` itself, never constructs one with `enabled=True` except in
this module's own tests (an explicit, source-visible fault-injection scenario proving the function
genuinely calls `authorize()` rather than hardcoding "always blocked").** The default parameter is a
fresh, production default-closed gate -- a caller reaching this function from any real entrypoint gets
the real gate, not a mock. (`BrokerOrderSubmissionGate` is a frozen, side-effect-free dataclass, so a
literal default-constructed instance here carries none of the usual "mutable default argument" risk --
every call still observes the same default-`False` state, by construction, not by convention.)"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionDisabledError, BrokerOrderSubmissionGate
from ai_trader.mandate2_readiness.event_identity import NodeTrace
from ai_trader.risk_manager_live.types import LiveRiskDecision

RISK_MANAGER_DENIED = "RISK_MANAGER_DENIED"
_COMPONENT_VERSION = "broker_gate_v1"


@dataclass(frozen=True, slots=True, kw_only=True)
class ShadowExecutionResult:
    """`reached_broker_gate=False` means Risk Manager itself already denied -- there was never a
    complete, approved candidate to test the barrier with, so `authorize()` was never even called (a
    RISK_MANAGER_DENIED candidate proves nothing about the barrier's own behavior). `reached_broker_gate
    =True, blocked=True` is the property the CEO's section 3 requires: a COMPLETE, APPROVED candidate
    that reached the barrier and was refused there."""

    reached_broker_gate: bool
    blocked: bool
    reason: str


def attempt_shadow_execution(
    risk_decision: LiveRiskDecision, *, gate: BrokerOrderSubmissionGate = BrokerOrderSubmissionGate(),
) -> ShadowExecutionResult:
    """Called ONLY after `risk_gate.submit_new_brain_candidate` has run -- this function trusts
    `risk_decision.approved` as its sole precondition, re-checking nothing about provenance or sizing
    (that already happened). `gate` is a keyword-only override, exclusively for this module's own
    fault-injection tests -- every real caller uses the default."""
    if not risk_decision.approved:
        return ShadowExecutionResult(reached_broker_gate=False, blocked=True, reason=RISK_MANAGER_DENIED)

    try:
        gate.authorize()
    except BrokerOrderSubmissionDisabledError as exc:
        return ShadowExecutionResult(reached_broker_gate=True, blocked=True, reason=str(exc))

    # Unreachable under the production default-DISABLED gate. Reached only if a caller explicitly
    # constructed `gate=BrokerOrderSubmissionGate(enabled=True, reason=...)` -- a visible, grep-able,
    # deliberate act, never a silent flip.
    return ShadowExecutionResult(reached_broker_gate=True, blocked=False, reason="AUTHORIZED")


def build_execution_adapter_trace(trace_id: str, result: ShadowExecutionResult) -> NodeTrace:
    """A `NodeTrace(node_name="ExecutionAdapter")` for `telemetry.NewBrainTelemetryLog.record_outcome`'s
    `extra_traces` -- kept separate from `attempt_shadow_execution` itself so that function's own return
    type never changes."""
    input_fp = hashlib.sha256(trace_id.encode("utf-8")).hexdigest()[:16]
    output_fp = hashlib.sha256(
        f"{result.reached_broker_gate}|{result.blocked}".encode("utf-8")
    ).hexdigest()[:16]
    reason_codes = () if result.blocked is False else (result.reason,)
    return NodeTrace(
        trace_id=trace_id, node_name="ExecutionAdapter", input_fingerprint=input_fp, output=output_fp,
        reason_codes=reason_codes, latency_seconds=0.0, component_version=_COMPONENT_VERSION,
    )
