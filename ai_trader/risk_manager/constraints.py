"""The Constraint Builder (``RISK_MANAGER_ARCHITECTURE.md`` §4/§5 stage 8) -- runs only after Sizing
returns a valid size. Carries the validated entry/stop/target through and sets ``max_hold_bars``/
``valid_until``/``max_slippage``/``allowed_session`` from the versioned config
(:class:`~ai_trader.risk_manager.config.ConstraintDefaults`). Never executes anything -- the
Execution Engine performs whatever this constraint object describes (``POSITION_SIZING.md`` §8: "the
Risk Manager specifies the plan ...; the Execution Engine performs").
"""

from __future__ import annotations

from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import Constraints
from ai_trader.scoring_engine.types import OpportunityScore


def build_constraints(opportunity: OpportunityScore, config: RiskConfig) -> Constraints:
    tc = opportunity.trade_context
    entry = tc.entry if tc is not None else None
    stop = tc.stop if tc is not None else None
    target = tc.target if tc is not None else None
    cd = config.constraints
    max_slippage = entry * cd.max_slippage_pct if entry is not None else None
    return Constraints(
        entry=entry, stop=stop, target=target,
        max_hold_bars=cd.max_hold_bars, valid_until=cd.valid_for_bars,
        max_slippage=max_slippage, allowed_session=None, reduce_only=False,
    )
