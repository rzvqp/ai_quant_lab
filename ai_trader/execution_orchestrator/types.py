"""Types owned by the Execution Orchestrator (Phase 9). Reuses every downstream engine's own types
unmodified -- only the genuinely missing coordination pieces (`CandidateSignal`, dependency bundle,
execution mode, result envelope) live here."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ai_trader.confidence_engine.types import ConfidenceAssessment, ConfidenceEngineConfig
from ai_trader.context_engine.types import MarketContextSnapshot
from ai_trader.context_memory import ContextMemoryRepository
from ai_trader.execution_engine.ledger import OrderLedger
from ai_trader.execution_engine.types import BrokerCapabilities
from ai_trader.order_manager.dry_run_adapter import DryRunBrokerAdapter
from ai_trader.order_manager.journal import OrderManagerAuditJournal
from ai_trader.order_manager.types import OrderExecutionResult, OrderManagerConfig
from ai_trader.portfolio_manager_live.types import PortfolioDailyState, PortfolioDecision, PortfolioManagerConfig
from ai_trader.recognition_engine.policy import SufficiencyPolicy
from ai_trader.recognition_engine_live.types import RecognitionResult
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import PortfolioState, RiskContext
from ai_trader.risk_manager_live.types import AccountState, InstrumentSpecification, LiveRiskDecision
from ai_trader.signal_engine.types import Direction
from ai_trader.telegram_notifier.types import TelegramCredentials


class ExecutionMode(str, Enum):
    """`LIVE` is refused unconditionally, at the very first check (CEO: "Nu activa tranzacționarea
    LIVE") -- structurally, not merely by convention. `DEMO` is functionally identical to `DRY_RUN`
    THIS phase: `order_manager.process_approved_intent` (Phase 3) is structurally dry-run-only, so no
    mode this phase can ever reach a real MT5 order (disclosed, `EXECUTION_ORCHESTRATOR_PHASE9_DESIGN.md`
    §7)."""

    DRY_RUN = "DRY_RUN"
    DEMO = "DEMO"
    LIVE = "LIVE"


@dataclass(frozen=True, slots=True)
class CandidateSignal:
    """The one new INPUT type this phase defines -- strategy signal generation (entry/stop/target) is
    ANOTHER module's job (`signal_engine`/`strategy_runtime`), never this orchestrator's own logic. The
    orchestrator RECEIVES this, it does not compute it."""

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
            raise ValueError("CandidateSignal.strategy_id must be non-empty")
        if not self.symbol:
            raise ValueError("CandidateSignal.symbol must be non-empty")
        if not self.session:
            raise ValueError("CandidateSignal.session must be non-empty")
        if not self.comment:
            raise ValueError("CandidateSignal.comment must be non-empty")
        if not isinstance(self.direction, Direction):
            raise TypeError(f"CandidateSignal.direction must be a Direction, got {self.direction!r}")


@dataclass(frozen=True, slots=True)
class OrchestratorConfig:
    max_staleness_seconds: int = 300
    #: `None` disables Recognition Engine entirely for this run (it is optional input to Confidence
    #: Engine, per Phase 8's own design) -- a caller may choose not to query it.
    recognition_pattern_id: str | None = "REC-SESSION-STRATEGY"
    recognition_policy: SufficiencyPolicy | None = None
    confidence_config: ConfidenceEngineConfig | None = None
    portfolio_config: PortfolioManagerConfig | None = None
    order_manager_config: OrderManagerConfig | None = None


@dataclass(frozen=True, slots=True)
class OrchestratorDependencies:
    """Every caller-supplied dependency this phase coordinates -- bundled, not 15 positional
    parameters, since this phase's own job is coordinating every prior phase at once. `ledger`/
    `order_journal` MUST be reused across calls (persistent, caller-owned) for idempotency to hold
    (`EXECUTION_ORCHESTRATOR_PHASE9_DESIGN.md` §4)."""

    account: AccountState
    portfolio: PortfolioState
    daily_state: PortfolioDailyState
    instrument: InstrumentSpecification
    risk_context: RiskContext
    risk_config: RiskConfig
    broker_caps: BrokerCapabilities
    ledger: OrderLedger
    order_journal: OrderManagerAuditJournal
    adapter: DryRunBrokerAdapter
    repository: ContextMemoryRepository | None = None
    telegram_credentials: TelegramCredentials | None = None
    strategy_library_path: Path | None = None


@dataclass(frozen=True, slots=True)
class CalculationTraceStep:
    """Same shape as the identical type already established in every prior live phase -- redeclared
    here (not imported) to avoid an arbitrary cross-package coupling choice among five equally-valid
    sources."""

    stage: str
    passed: bool
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    correlation_id: str
    strategy_id: str
    symbol: str
    as_of: int
    mode: ExecutionMode
    approved: bool
    context: MarketContextSnapshot | None
    recognition: RecognitionResult | None
    confidence: ConfidenceAssessment | None
    risk_decision: LiveRiskDecision | None
    portfolio_decision: PortfolioDecision | None
    order_result: OrderExecutionResult | None
    reason_codes: tuple[str, ...]
    calculation_trace: tuple[CalculationTraceStep, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.correlation_id:
            raise ValueError("OrchestrationResult.correlation_id must be non-empty")
        if not self.calculation_trace:
            raise ValueError("OrchestrationResult.calculation_trace must be non-empty -- every run is traced")
        if not self.approved and not self.reason_codes:
            raise ValueError("OrchestrationResult: a non-approved run must carry at least one reason code")
        if self.approved and self.order_result is None:
            raise ValueError("OrchestrationResult: an approved run must carry an order_result")
