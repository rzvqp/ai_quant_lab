"""Real-portfolio position identity registry -- Learning/Research Feedback Phase F, Architectural
Decision Package Decision 1 (Option D: read-only, per-bar snapshot diff), recommended over adding a
``position_id`` field to :class:`~ai_trader.simulation.portfolio_simulator.Position` itself (Option A --
crosses the ownership boundary into a frozen, independently-tested production module for a single
downstream consumer's own need) and over an event-replay external registry (Option B -- duplicates
open/scale-in/reduce/flip CLASSIFICATION logic that would have to stay in permanent lockstep with
``portfolio_simulator.py``'s own).

This module NEVER re-derives ``Position.size``/quantity bookkeeping -- it only diffs the ALREADY-
AUTHORITATIVE ``Position`` snapshot (``portfolio_simulator.account.positions``, keyed by ``symbol``,
Lifecycle Specification §3A/I3) bar over bar, using exactly two already-existing, already-correct facts:
whether a symbol key is present, and whether its ``opened_as_of`` changed. Nothing here imports or calls
anything from ``portfolio_simulator.py`` beyond reading its own already-public ``Position`` dataclass for
type hints -- ``portfolio_simulator.py`` itself is never modified.

**Disclosed, accepted limitation** (Architectural Decision Package Decision 1): a same-bar
open-then-close-then-reopen sequence at one symbol is invisible to this registry -- only the END-of-bar
state is ever observed. This is a deliberate trade-off: the alternative (Option B) would have required
duplicating Portfolio Simulator's own fill-classification logic to see intra-bar transitions, a larger,
ongoing maintenance-coupling risk this design explicitly avoids.

**``strategy_id`` is never part of the position key** (Lifecycle Specification I3: ``Position.strategy_id``
can be reassigned to a different strategy's own fill on a flip, and is not even part of
``portfolio_simulator.py``'s own dict key) -- it is carried on :class:`PositionKeyInfo` purely as
informational attribution, current as of the bar the info was produced, never as part of the key string.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.portfolio_simulator import Position


def make_position_key(run_id: str, symbol: str, opened_as_of: int, direction: Direction) -> str:
    """The one, pure, canonical position-key formula (Architectural Decision Package Decision 1) --
    unique within a run, stable while the same economic position remains open, and produces a fresh key
    whenever a flat-to-open transition or a flip occurs (proven against every required property in the
    Architectural Decision Package)."""
    return f"{run_id}:{symbol}:{opened_as_of}:{direction.value}"


@dataclass(frozen=True)
class PositionKeyInfo:
    """Everything known about one real-portfolio position identity at the moment it was last observed."""

    position_key: str
    symbol: str
    strategy_id: str
    direction: Direction
    opened_as_of: int


@dataclass(frozen=True)
class RegistryDiff:
    """One bar's worth of position-identity transitions, produced by :meth:`RealPositionRegistry.observe`.

    ``deaths`` includes BOTH plain closes (a symbol simply disappears) AND the closing half of a flip
    (the same symbol reappears this same bar under a NEW ``opened_as_of``) -- callers that need to
    distinguish the two use :attr:`plain_deaths`/:attr:`flips` rather than re-deriving the distinction
    themselves."""

    births: tuple[PositionKeyInfo, ...]
    deaths: tuple[PositionKeyInfo, ...]
    flips: tuple[tuple[PositionKeyInfo, PositionKeyInfo], ...]

    @property
    def plain_deaths(self) -> tuple[PositionKeyInfo, ...]:
        """Deaths that are NOT the closing half of a flip -- the position closed to flat and nothing
        reopened at that symbol this same bar."""
        flipped_symbols = {old.symbol for old, _ in self.flips}
        return tuple(d for d in self.deaths if d.symbol not in flipped_symbols)


class RealPositionRegistry:
    """Run-scoped, read-only tracker of the real Portfolio Simulator's own already-authoritative
    ``Position`` state. Bound to one ``run_id`` at construction (mirrors :class:`~ai_trader.
    learning_feedback.capture.CorrelationMap`'s own convention). :meth:`observe` must be called at most
    once per bar, strictly AFTER ``portfolio_simulator.apply(fills, bar_index)`` has fully processed every
    fill for that bar -- never mid-bar."""

    def __init__(self, run_id: str) -> None:
        self._run_id = run_id
        self._current: dict[str, PositionKeyInfo] = {}

    @property
    def run_id(self) -> str:
        return self._run_id

    def current_key(self, symbol: str) -> PositionKeyInfo | None:
        return self._current.get(symbol)

    def observe(self, positions: dict[str, Position]) -> RegistryDiff:
        """Diff ``positions`` (``portfolio_simulator.account.positions``, read-only) against this
        registry's own last-observed state. Never mutates ``positions`` itself."""
        previous = self._current
        next_state: dict[str, PositionKeyInfo] = {}
        births: list[PositionKeyInfo] = []
        flips: list[tuple[PositionKeyInfo, PositionKeyInfo]] = []

        for symbol, pos in positions.items():
            prior = previous.get(symbol)
            if prior is None or prior.opened_as_of != pos.opened_as_of:
                new_info = PositionKeyInfo(
                    position_key=make_position_key(self._run_id, symbol, pos.opened_as_of, pos.direction),
                    symbol=symbol, strategy_id=pos.strategy_id, direction=pos.direction,
                    opened_as_of=pos.opened_as_of,
                )
                next_state[symbol] = new_info
                if prior is not None:
                    flips.append((prior, new_info))
                else:
                    births.append(new_info)
            else:
                next_state[symbol] = prior

        disappeared = tuple(prior for symbol, prior in previous.items() if symbol not in positions)
        flip_deaths = tuple(old for old, _ in flips)
        deaths = disappeared + flip_deaths

        self._current = next_state
        return RegistryDiff(births=tuple(births), deaths=deaths, flips=tuple(flips))

    def drain(self) -> tuple[PositionKeyInfo, ...]:
        """Every position_key still open, for end-of-run (``HOLD_AND_MARK``) disposition -- Architectural
        Decision Package Decision 3: never fabricates a terminal Outcome for these, only reports which
        keys are being abandoned, still open, at the end of this run."""
        return tuple(self._current.values())
