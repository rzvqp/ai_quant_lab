"""Recognition Engine -- Phase 1A: single-dimension conditional statistics.

`RECOGNITION_ENGINE_PHASE1_DESIGN.md` (CEO verdict CONDITIONAL GO) authorized exactly this narrow scope:
read-only, purely descriptive conditional statistics over the official Learning Feedback dataset
(`LEARNING_FEEDBACK_DATASET_AUDIT.md`, verdict READY), one context dimension at a time, strictly isolated
per `strategy_id`/`outcome_kind`. NOT authorized in this phase: embeddings, clustering, prototypes, ML
models, classifiers, multi-dimensional context matching, automatic optimization, or any trading/decision/
execution output of any kind.
"""

from __future__ import annotations

from ai_trader.recognition_engine.engine import compute_conditional_statistics
from ai_trader.recognition_engine.policy import SufficiencyPolicy
from ai_trader.recognition_engine.types import ConditionalStatistics, ContextDimension, Sufficiency

__all__ = [
    "compute_conditional_statistics",
    "SufficiencyPolicy",
    "ConditionalStatistics",
    "ContextDimension",
    "Sufficiency",
]
