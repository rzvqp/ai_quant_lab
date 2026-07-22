"""Learning/Research Feedback -- Flow B roadmap step 3/6.

Phase D: pure, deterministic, isolated adapters that convert existing Shadow Evidence / real-portfolio /
Risk Manager records into Context Memory's own ``Outcome``/``OperationalMetadata`` contracts.

Phase E: ``capture.py`` -- decision-time/resolution-time orchestration and the run-scoped
``client_order_id`` correlation map, consuming Phase D's adapters. Still UNWIRED: nothing in this
package is called from ``harness.py`` (Phase F) -- unreachable from any production code today.
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
from ai_trader.learning_feedback.capture import (
    CorrelationError,
    CorrelationMap,
    CorrelationRunMismatchError,
    DuplicateDecisionCaptureError,
    PendingCapture,
    capture_decision_observation,
    capture_operational_metadata,
    capture_portfolio_resolution,
    capture_strategy_resolution,
    register_pending_correlation,
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
    "CorrelationMap",
    "PendingCapture",
    "CorrelationError",
    "CorrelationRunMismatchError",
    "DuplicateDecisionCaptureError",
    "capture_decision_observation",
    "capture_operational_metadata",
    "register_pending_correlation",
    "capture_strategy_resolution",
    "capture_portfolio_resolution",
]
