"""Learning/Research Feedback -- Flow B roadmap step 3/6.

Phase D: pure, deterministic, isolated adapters that convert existing Shadow Evidence / real-portfolio /
Risk Manager records into Context Memory's own ``Outcome``/``OperationalMetadata`` contracts. Nothing in
this package is wired into any orchestration path yet (Phase E, ``capture.py``, does not exist) or into
``harness.py`` (Phase F) -- this package is unreachable from any production code today.
"""

from __future__ import annotations

from ai_trader.learning_feedback.adapters import (
    ALL_DENIAL_CODES,
    LEARNING_FEEDBACK_OUTCOME_DEFINITION_VERSION,
    REJECTION_STAGE_BY_DENIAL_CODE,
    UnmappedDenialCodeError,
    build_operational_metadata,
    build_portfolio_outcome,
    build_strategy_outcome,
    canonical_cost_model_ref,
    rejection_stage_for,
)
from ai_trader.learning_feedback.config import LEARNING_FEEDBACK_CONFIG_VERSION, LearningFeedbackConfig

__all__ = [
    "LearningFeedbackConfig",
    "LEARNING_FEEDBACK_CONFIG_VERSION",
    "LEARNING_FEEDBACK_OUTCOME_DEFINITION_VERSION",
    "build_strategy_outcome",
    "build_portfolio_outcome",
    "build_operational_metadata",
    "canonical_cost_model_ref",
    "rejection_stage_for",
    "REJECTION_STAGE_BY_DENIAL_CODE",
    "ALL_DENIAL_CODES",
    "UnmappedDenialCodeError",
]
