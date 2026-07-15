"""``SimulationContext`` -- the immutable run spec (``SIMULATION_CONTEXT.md`` §A) -- plus every
numeric/policy default the frozen docs name without fixing a value. Every such gap is filled here with
an explicit, documented, conservative default and marked IMPLEMENTATION CHOICE, exactly the discipline
every prior module's own ``config.py`` followed. See ``IMPLEMENTATION_CHOICES.md`` for the full
rationale behind each default (frozen before any run, before any profitability inspection).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.simulation.exceptions import InvalidContextError
from ai_trader.simulation.types import (
    CloseAtEndPolicy,
    EntryTiming,
    IntrabarRule,
    LatencyModelType,
    PartialFillPolicy,
    SlippageModelType,
)

SIMULATION_FRAMEWORK_VERSION = "1.0.0"
SIMULATION_SCHEMA_VERSION = "1.0.0"
FILL_MODEL_VERSION = "1.0.0"
COST_MODEL_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class DateRange:
    """``SIMULATION_CONTEXT.md`` §A.1. UTC epoch seconds, ``start < end``."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start >= self.end:
            raise InvalidContextError(f"DateRange.start ({self.start}) must be < end ({self.end})")


@dataclass(frozen=True, slots=True)
class CostModel:
    """``SIMULATION_CONTEXT.md`` §A.3 / ``EXECUTION_SIMULATOR.md`` §4. ``spread_ticks``/
    ``commission_per_lot`` are the default v1 numeric knobs behind the named ``spread_model``/
    ``commission_model`` strings -- IMPLEMENTATION CHOICE, conservative placeholders (never tuned
    against results, ``IMPLEMENTATION_CHOICES.md`` intro)."""

    spread_model: str = "fixed_ticks"
    spread_ticks: float = 1.0
    commission_model: str = "per_lot"
    commission_per_lot: float = 0.0
    cost_model_version: str = COST_MODEL_VERSION


@dataclass(frozen=True, slots=True)
class SlippageModel:
    """``SIMULATION_CONTEXT.md`` §A.3. ``seed_key`` names the stable per-order key
    (``client_order_id`` + ``as_of``) the harness hashes with ``run_seed`` -- never a global RNG."""

    type: SlippageModelType = SlippageModelType.FIXED
    fixed_ticks: float = 1.0
    atr_fraction: float = 0.1
    max_slippage_ticks: float = 5.0


@dataclass(frozen=True, slots=True)
class FillModel:
    """``SIMULATION_CONTEXT.md`` §A.3 / ``EXECUTION_SIMULATOR.md`` §§3,5,7."""

    entry_timing: EntryTiming = EntryTiming.NEXT_OPEN
    intrabar: IntrabarRule = IntrabarRule.STOP_BEFORE_TARGET
    partial_fill_policy: PartialFillPolicy = PartialFillPolicy.FULL_FILL
    partial_fill_fraction: float = 1.0
    limit_touch_rule: str = "range_touch"
    slippage_model: SlippageModel = field(default_factory=SlippageModel)
    latency_model: LatencyModelType = LatencyModelType.NONE
    fill_model_version: str = FILL_MODEL_VERSION

    def __post_init__(self) -> None:
        if not (0.0 < self.partial_fill_fraction <= 1.0):
            raise InvalidContextError("FillModel.partial_fill_fraction must be in (0, 1]")


@dataclass(frozen=True, slots=True)
class MarginModel:
    """``SIMULATION_CONTEXT.md`` §A.2. Conservative placeholder defaults, ``IMPLEMENTATION_CHOICES.md``
    §5 -- never tuned against performance results."""

    initial_margin_pct: float = 0.01
    maintenance_margin_pct: float = 0.005
    leverage_max: float = 100.0
    halt_on_liquidation: bool = True

    def __post_init__(self) -> None:
        if not (0.0 < self.maintenance_margin_pct < self.initial_margin_pct):
            raise InvalidContextError(
                "MarginModel requires 0 < maintenance_margin_pct < initial_margin_pct"
            )
        if self.leverage_max <= 0:
            raise InvalidContextError("MarginModel.leverage_max must be > 0")


@dataclass(frozen=True, slots=True)
class RecordConfig:
    """``SIMULATION_CONTEXT.md`` §A.6 -- what the Simulation Ledger persists."""

    trade_history: bool = True
    execution_log: bool = True
    equity_curve: bool = True
    risk_events: bool = True
    per_bar_snapshots: bool = False


@dataclass(frozen=True, slots=True)
class StatsRollups:
    """``SIMULATION_CONTEXT.md`` §A.6."""

    session: bool = True
    daily: bool = True
    monthly: bool = True


@dataclass(frozen=True, slots=True)
class SimulationContext:
    """The immutable specification of ONE simulation run (``SIMULATION_CONTEXT.md`` §A). A run is
    fully determined by this object + the historical data + the composed module versions -- nothing
    outside it may influence results (the determinism law, ``deterministic`` is hard-pinned ``True``).
    """

    run_id: str
    date_range: DateRange
    symbols: tuple[str, ...]
    timeframes: tuple[str, ...]
    starting_balance: float
    run_seed: int
    base_currency: str = "USD"
    data_source: str = "replay"
    warmup_bars: int = 200
    margin_model: MarginModel = field(default_factory=MarginModel)
    cost_model: CostModel = field(default_factory=CostModel)
    fill_model: FillModel = field(default_factory=FillModel)
    strategy_set: tuple[str, ...] | str = "all_activatable"
    strategy_library_path: str | None = None
    capital_allocation: dict[str, float] | None = None
    record: RecordConfig = field(default_factory=RecordConfig)
    stats_rollups: StatsRollups = field(default_factory=StatsRollups)
    close_at_end_policy: CloseAtEndPolicy = CloseAtEndPolicy.CLOSE_AT_LAST
    base_timeframe: str = "M15"
    batch_id: str | None = None
    #: ``deterministic`` is const=true in the schema itself -- there is no "off" switch (v1 always).
    deterministic: bool = True

    def __post_init__(self) -> None:
        if not self.run_id:
            raise InvalidContextError("SimulationContext.run_id must be non-empty")
        if not self.symbols:
            raise InvalidContextError("SimulationContext.symbols must be non-empty")
        if not self.timeframes:
            raise InvalidContextError("SimulationContext.timeframes must be non-empty")
        if self.base_timeframe not in self.timeframes:
            raise InvalidContextError(
                f"SimulationContext.base_timeframe {self.base_timeframe!r} must be in timeframes {self.timeframes!r}"
            )
        if self.starting_balance <= 0:
            raise InvalidContextError("SimulationContext.starting_balance must be > 0")
        if self.warmup_bars < 0:
            raise InvalidContextError("SimulationContext.warmup_bars must be >= 0")
        if not self.deterministic:
            raise InvalidContextError("SimulationContext.deterministic must be True in v1 (no 'off' switch)")

    def seed_for(self, stable_key: str) -> int:
        """Deterministic sub-seed derivation for any stochastic model (``SIMULATION_CONTEXT.md`` §A.5:
        ``hash(run_seed, stable_key)``). Uses a fixed, versioned, non-cryptographic mix (Python's
        built-in ``hash()`` is salted per-process and therefore explicitly NOT reproducible across
        runs/processes -- using it here would silently break the determinism law) so identical
        ``(run_seed, stable_key)`` always produce the identical sub-seed, in this or any future
        process."""
        import hashlib
        digest = hashlib.sha256(f"{self.run_seed}:{stable_key}".encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big", signed=False)
