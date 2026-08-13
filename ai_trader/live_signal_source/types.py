"""Types owned by `live_signal_source` (Phase 2A Step 5, #6): a live closed-bar feed, an
injected-recognition-rule signal producer, and an append-only observation journal.

Deliberately does NOT import `ai_trader.execution_orchestrator` -- not even `.types` for
`CandidateSignal`. `execution_orchestrator/types.py` itself imports the execution-capable broker-adapter
type from `ai_trader.execution_engine` and `ai_trader.order_manager.*` at module level (confirmed by
reading it before deciding, not assumed), so importing even its pure `CandidateSignal` type would
transitively pull those execution-capable modules into this package's own import graph -- exactly the
coupling the CEO's "the producer never receives the execution adapter, statically enforced" instruction
guards against, in its strongest form (not merely "never named," but "not even transitively reachable").
`LiveCandidate` below is this package's own, independently-owned equivalent -- same fields, same
direction-vs-stop invariant -- so a later, separately-authorized wiring step can convert it 1:1 into
`execution_orchestrator.types.CandidateSignal` without information loss or a schema rewrite.

Reuses `ai_trader.signal_engine.types.Direction` directly -- the same shared type both
`execution_orchestrator.types` and `shadow_evidence.types` already reuse rather than redefining their
own -- confirmed clean of any execution-capable transitive import before use (it depends only on
`market_scanner.types`/`strategy_manager.contract`, neither of which touches execution).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from ai_trader.signal_engine.types import Direction


@dataclass(frozen=True, slots=True)
class Bar:
    """One CLOSED live bar. Deliberately NOT `ai_trader.simulation.types.Bar` -- that type is
    documented as backtest-only ("as fed by the Replay Data Source"), and `ai_trader.simulation` is
    forbidden for this live path, matching every prior live package's own precedent
    (`mt5_pnl_source`/`mt5_account_bridge`). Structurally similar OHLCV shape by design, redeclared
    rather than imported -- the same convention `recognition_engine_live` already established for
    `CalculationTraceStep`."""

    symbol: str
    ts_open: int
    ts_close: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    is_backfilled: bool = False
    """CEO instruction, 2026-08-10: distinguishes a bar recovered from `LiveBarFeed`'s own gap-catch-up
    history query from one seen through normal steady-state polling. NOT "imputed" or "interpolated" --
    the OHLC values are the same real MT5 history either way (`GapRecord`'s own "gol se raporteaza, nu
    se umple" principle is about never FABRICATING a value, and backfill fetches real data, so it
    doesn't conflict with that rule); this flag only records HOW a genuine bar was learned about, which
    matters downstream for anything that depends on being present AT THE TIME the bar closed (a spread
    sample has no meaning read hours or days late -- see `spread_collection.observer.SpreadCollector`).
    Defaults to `False` so every existing call site constructing a `Bar` (tests, fakes) is unaffected."""

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("Bar.symbol must not be empty")
        if self.ts_close <= self.ts_open:
            raise ValueError(
                f"Bar.ts_close must be after ts_open, got ts_open={self.ts_open!r} ts_close={self.ts_close!r}"
            )


class BarFeedError(Exception):
    """Raised by `LiveBarFeed` when the gateway read itself fails (`copy_rates_from` returning `None`,
    MT5's own documented failure signal) or returns a record missing an expected OHLC field -- never
    silently skipped, never estimated. **Not** raised merely because no new closed bar exists yet -- an
    empty `poll()` result is the normal, expected outcome of polling mid-bar, not a failure."""


class StaleProbeError(BarFeedError):
    """Raised ONLY by `make_broker_offset`'s own staleness check (`_OFFSET_PROBE_MAX_STALE_LAG_SECONDS`)
    -- a distinct subtype from the base `BarFeedError`, added 2026-08-14 (CEO, after this exact condition
    killed all 5 live processes on a genuine 62-minute MT5 data gap): a stale probe means "the market
    appears closed right now," a fundamentally different, EXPECTED-to-eventually-happen condition from a
    genuinely broken gateway response (empty probe, missing field -- both still plain `BarFeedError`,
    still fatal, unchanged). `LiveBarFeed.poll()` catches this specific subtype to wait and retry instead
    of dying; it deliberately does NOT catch the base class, so a real gateway malfunction still crashes
    the process exactly as before -- only "the market looks closed" gets a second chance."""


@dataclass(frozen=True, slots=True)
class LiveCandidate:
    """This package's own equivalent of `execution_orchestrator.types.CandidateSignal` -- see this
    module's own docstring for why it is not imported directly. Same fields, and the same
    direction-vs-stop invariant enforced at the earliest possible point -- this repository's established
    defense-in-depth pattern (`CandidateSignal`, `TradeProposal`, and the risk gate each enforce it
    independently; Decision Logic Audit #2 / Phase 2A Step 2)."""

    strategy_id: str
    symbol: str
    direction: Direction
    entry: float
    stop: float
    target: float | None
    session: str
    magic_number: int
    comment: str
    as_of: int

    def __post_init__(self) -> None:
        if not self.strategy_id:
            raise ValueError("LiveCandidate.strategy_id must be non-empty")
        if not self.symbol:
            raise ValueError("LiveCandidate.symbol must be non-empty")
        if not self.session:
            raise ValueError("LiveCandidate.session must be non-empty")
        if not self.comment:
            raise ValueError("LiveCandidate.comment must be non-empty")
        if not isinstance(self.direction, Direction):
            raise TypeError(f"LiveCandidate.direction must be a Direction, got {self.direction!r}")
        if self.direction is Direction.LONG and self.stop >= self.entry:
            raise ValueError(
                f"LiveCandidate: LONG requires stop strictly below entry, got "
                f"stop={self.stop!r} entry={self.entry!r}"
            )
        if self.direction is Direction.SHORT and self.stop <= self.entry:
            raise ValueError(
                f"LiveCandidate: SHORT requires stop strictly above entry, got "
                f"stop={self.stop!r} entry={self.entry!r}"
            )


class RecognitionRule(Protocol):
    """The injected dependency Piesa 2 requires (CEO instruction, 2026-07-26: "regula de recunoastere e
    dependenta injectata"). Structurally typed -- no inheritance required, matching this codebase's own
    established convention for injected real/fake/null implementations."""

    def evaluate(self, bar: Bar) -> LiveCandidate | None: ...


class NullRecognitionRule:
    """The ONLY `RecognitionRule` this step ships -- returns `None` unconditionally, for every bar, no
    exceptions. No strategy logic anywhere in this class or file (CEO prohibition, 2026-07-26: "fara
    strategie scrisa in cod")."""

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        return None


@dataclass(frozen=True, slots=True)
class LiveSignalJournalEntry:
    """One append-only journal row -- one per bar the producer actually processed (Piesa 3), whether or
    not a candidate resulted. This is deliberately what gives the system its "eyes" even while
    `NullRecognitionRule` produces nothing (CEO, 2026-07-26: the system "poate vedea piata... si nu
    poate face nimic cu ce vede"): a row confirms a bar was observed, not merely that a trade was
    proposed.

    Does not reuse any of `shadow_evidence.types`'s six record dataclasses verbatim -- each is scoped to
    an already-scored, already-risk-decided shadow BACKTEST evaluation (`score_recommendation:
    Recommendation`, `shadow_risk_decision: "ALLOW"|"DENY"`, position-leg tracking), none of which exist
    at this pre-risk-evaluation live pipeline stage; confirmed by reading all six before deciding, not
    assumed. The reuse instead takes the concrete form both packages already establish: `Direction` (via
    `LiveCandidate.direction`), the same type `shadow_evidence.types` itself imports from
    `signal_engine.types` rather than redefining its own."""

    symbol: str
    as_of: int
    candidate: LiveCandidate | None
    is_backfilled: bool = False
    """Mirrors the `Bar.is_backfilled` this entry's own bar carried -- see that field's docstring.
    Defaults to `False`, matching `Bar`'s own default, for the same backward-compatibility reason."""

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("LiveSignalJournalEntry.symbol must not be empty")


class GapClassification(str, Enum):
    """CEO instruction, 2026-07-27: three categories, all visible, only one a problem -- "un consumator
    care citeste jurnalul peste sase luni nu poate distinge un shadow sanatos de unul cu pierderi" fara
    toate trei.

    **`EXTENDED_PAUSE`, added 2026-08-10** (CEO: "adauga o clasa: gol care depaseste durata maxima a
    unui weekend real"): a gap that spans a Saturday (so it would otherwise match `WEEKEND`) but whose
    duration exceeds what a real weekend closure has ever measured on this broker -- see
    `gap_classification.MAX_REAL_WEEKEND_SECONDS` for the empirical basis. Checked BEFORE `WEEKEND`, so
    it is the more specific classification for the same underlying condition, not a fourth independent
    category -- a gap can never be both."""

    MAINTENANCE = "MAINTENANCE"
    WEEKEND = "WEEKEND"
    EXTENDED_PAUSE = "EXTENDED_PAUSE"
    UNEXPECTED = "UNEXPECTED"


@dataclass(frozen=True, slots=True)
class GapRecord:
    """One detected continuity break in `LiveBarFeed`'s own emitted sequence -- reported, never filled
    (CEO: "golul se raporteaza, nu se umple. Fara imputare, fara interpolare"). `gap_start` is the last
    known-good bar's own `ts_open` (matching `code/gapfind.py`'s own `t0`, reused verbatim for
    classification -- see `gap_classification.py`); `gap_end` is the first bar seen after the gap
    (`t1`). `duration_seconds` is their literal difference, matching that script's own `mins` basis
    exactly (open-to-open, not close-to-open).

    **`bars_backfilled`/`backfill_capped`, added 2026-08-10**: this is still "the gap is reported, never
    filled" in the ORIGINAL sense -- nothing about the gap's own existence is ever hidden or estimated.
    What changed is a SEPARATE capability: `LiveBarFeed` can now fetch the real, already-existing MT5
    history for the missing window (not invent one), reported here as HOW MANY bars that recovered.
    `backfill_capped=True` means the gap exceeded `bar_feed.MAX_BACKFILL_SECONDS` (30 days) and was
    deliberately left unfilled -- reported, not filled, exactly per the original rule, for the specific
    case the CEO drew the line at."""

    symbol: str
    gap_start: int
    gap_end: int
    duration_seconds: int
    classification: GapClassification
    bars_backfilled: int = 0
    backfill_capped: bool = False

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("GapRecord.symbol must not be empty")
        if self.gap_end <= self.gap_start:
            raise ValueError(
                f"GapRecord.gap_end must be after gap_start, got "
                f"gap_start={self.gap_start!r} gap_end={self.gap_end!r}"
            )
        if self.duration_seconds != self.gap_end - self.gap_start:
            raise ValueError(
                f"GapRecord.duration_seconds must equal gap_end - gap_start, got "
                f"duration_seconds={self.duration_seconds!r}, "
                f"gap_end - gap_start={self.gap_end - self.gap_start!r}"
            )
