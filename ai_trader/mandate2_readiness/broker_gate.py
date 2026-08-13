"""`BrokerOrderSubmissionGate` -- CEO Mandate 2 prep, 2026-08-14: "BROKER_ORDER_SUBMISSION = DISABLED.
Aparat prin COD, CONFIGURATIE si TEST. Nu doar prin promisiune operationala."

A freestanding, NOT-YET-WIRED safety primitive. Prepared and fully tested NOW, ahead of VE's own
artifact handoff and Red Team's ratification (`VE_HANDOFF_PASS`), so the mandatory choke point already
exists, already defaults closed, and is already proven correct in isolation -- before a single line of
new order-producing code exists for it to guard.

**Not wired into the 5 currently-running live processes.** CAND-0001/CAND-0007/CAND-0009/CAND-0019 all
keep submitting DEMO orders through their own existing, CEO-approved `send_after_dry_run_gate` path
(`mt5_demo_execution/gating.py`), completely unchanged -- "Cele cinci procese... Neschimbate." This gate
exists for the NEW integration surface Mandate 2's own future step will build; wiring it into anything
(existing or new) is itself a separately-authorized future action, not taken here.

**Why a dataclass with no setter, not a mutable flag or an env-var lookup**: the accidental-activation
failure mode this exists to rule out is exactly the kind a mutable global or a missing/misspelled
environment variable defaulting to "on" would produce. `enabled` can only ever be set at construction,
explicitly, as a keyword-visible `True` -- there is no code path (setter, `os.environ.get(..., "true")`,
a truthy-string parse) anywhere in this file that could silently produce an enabled gate. The only way to
get one is to write `BrokerOrderSubmissionGate(enabled=True, reason="...")` in a caller's own source,
where it is `git blame`-able and grep-able forever.
"""

from __future__ import annotations

from dataclasses import dataclass


class BrokerOrderSubmissionDisabledError(Exception):
    """Raised by `BrokerOrderSubmissionGate.authorize()` whenever submission is not explicitly enabled --
    the ONLY way code downstream of this gate can ever reach a real broker order call. Never caught and
    silently ignored by this module itself -- a caller that wants "no order this time" behavior gets that
    from `authorize()` raising, same as this project's own established fail-closed convention
    (`BarFeedError`, `StaleProbeError`) rather than a boolean return a caller could forget to check."""


@dataclass(frozen=True, slots=True, kw_only=True)
class BrokerOrderSubmissionGate:
    """`enabled` defaults to `False` -- constructing `BrokerOrderSubmissionGate()` with no arguments at
    all is, by construction, the disabled state. `frozen=True` means there is no setter: once
    constructed, a gate's `enabled` value cannot change -- re-authorizing requires constructing a NEW
    gate, explicitly, which is the audit trail (test 22 in `tests/test_e2e_readiness.py`: enabling is
    never a silent flip).

    **`kw_only=True`, added after this module's own test 19 caught the gap**: without it, a plain
    dataclass accepts positional arguments too -- `BrokerOrderSubmissionGate(True)` would have silently
    enabled it via a bare positional `True`, with no `enabled=` keyword anywhere in the caller's own
    source to `grep` for. `kw_only=True` makes that a `TypeError` instead: the ONLY way to construct an
    enabled gate is the explicit, source-visible `enabled=True` keyword this module's whole design
    depends on."""

    enabled: bool = False
    reason: str = "Mandate 2 integration not yet ratified by Red Team -- default-closed"

    def authorize(self) -> None:
        """Call immediately before any order-producing call reaches the broker. Raises
        `BrokerOrderSubmissionDisabledError` unless `enabled=True` was passed explicitly at
        construction. Exactly two outcomes: proceed (returns `None`) or raise -- no third,
        silently-ignorable path (e.g. a boolean a caller could forget to check)."""
        if not self.enabled:
            raise BrokerOrderSubmissionDisabledError(
                f"BrokerOrderSubmissionGate: order submission is DISABLED -- {self.reason}"
            )
