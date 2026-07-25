"""New reason codes for the live Risk Manager -- additive, never colliding with the existing, frozen
`ai_trader/risk_manager/` vocabulary (`guards.py`/`limits.py`/`filters.py`/`sizing.py`'s own codes are
reused verbatim, unmodified, when the underlying function returns them)."""

from __future__ import annotations

PROPOSAL_DATA_INCOMPLETE = "PROPOSAL_DATA_INCOMPLETE"
RISK_NOT_CALCULABLE = "RISK_NOT_CALCULABLE"
VOLUME_STEP_ROUNDING_BELOW_MIN = "VOLUME_STEP_ROUNDING_BELOW_MIN"
INSUFFICIENT_FREE_MARGIN = "INSUFFICIENT_FREE_MARGIN"

#: Circuit-breaker reason codes (Risk Audit #1 fix, 2026-07-25). Loss/drawdown-triggered suspensions
#: reuse guards.py's own DeniedReason codes verbatim (LOSS_DAILY/LOSS_WEEKLY/DRAWDOWN_MAX) -- only the
#: manual-override code is new.
CIRCUIT_EMERGENCY_STOP_REQUESTED = "CIRCUIT_EMERGENCY_STOP_REQUESTED"
CIRCUIT_SUSPENDED = "CIRCUIT_SUSPENDED"
