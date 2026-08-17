"""`safe_evaluate_bar` -- Mandate 2, section 5 (CEO, 2026-08-14): "Brain indisponibil -> NO_TRADE,
BRAIN_UNAVAILABLE. FARA fallback legacy." This is the wrapper an entrypoint calls once `DecisionAuthority
.NEW_BRAIN` is active -- ANY failure inside `bridge.evaluate_bar` (an unexpected exception from `ve_brain`
itself, a `RawAxesBuilder`/vendor-detector failure, anything) becomes an explicit `BrainUnavailableOutcome`
here, never an unhandled exception that could crash the caller's loop, and never a call back into any
legacy recognition/submission code -- there IS no such call in this function; the "no fallback" guarantee
is structural (the legacy path is simply absent from this function's body), not a runtime check that
could be bypassed.

**`tower` parameter (RT-TOWER LIVE_SHADOW activation, 2026-08-17)**: additive, optional, defaults to
`None` -- every pre-existing call site is unaffected. When supplied, forwarded verbatim to `evaluate_bar`;
a tower-side failure (worker crash, IPC failure, `ve_tower` itself reporting the chain unavailable) is
ALREADY fail-closed inside `bridge._query_tower_chain` (returns all-`False` availability flags, a real
`NO_TRADE` reason code from `ve_brain.decide_n6` -- never a fabricated result, never raised as an
exception this wrapper would need to catch). A total inability to even reach the worker process (never
launched, or the launcher's own handshake failed) is a caller-level precondition, not something this
function papers over -- callers construct `tower` from an already-established `TowerClient` session and
refuse to start their own loop if that session was never established (see `new_brain_live/entrypoint.py`'s
own preflight)."""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome, TowerDependencies, evaluate_bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder

BRAIN_UNAVAILABLE = "BRAIN_UNAVAILABLE"


@dataclass(frozen=True, slots=True, kw_only=True)
class BrainUnavailableOutcome:
    """Distinct from `NewBrainOutcome` on purpose -- a brain failure is a fact about the WHOLE
    evaluation for this bar, not about any one catalog strategy, so it is never forced into the
    per-strategy shape. `error` is the exception's own `str()`, for the audit journal only -- never
    parsed, never used for control flow."""

    symbol: str
    timeframe: str
    bar_ts_close: int
    reason: str
    error: str


def safe_evaluate_bar(
    bar: Bar, *, timeframe: str, axes_builder: RawAxesBuilder, tower: TowerDependencies | None = None,
) -> tuple[NewBrainOutcome, ...] | BrainUnavailableOutcome:
    """Same signature as `bridge.evaluate_bar` for the common-path arguments -- callers that already
    have a `RawAxesBuilder` wired need no other change to route through the fail-safe wrapper. `tower`
    is additive (see module docstring) -- omitting it preserves the exact pre-existing tower-less
    behavior."""
    try:
        return evaluate_bar(bar, timeframe=timeframe, axes_builder=axes_builder, tower=tower)
    except Exception as exc:  # noqa: BLE001 -- deliberately broad: ANY failure here means BRAIN_UNAVAILABLE,
        # never a silent crash and never a fallback to legacy (there is no legacy call in this function).
        return BrainUnavailableOutcome(
            symbol=bar.symbol, timeframe=timeframe, bar_ts_close=bar.ts_close, reason=BRAIN_UNAVAILABLE,
            error=str(exc),
        )
