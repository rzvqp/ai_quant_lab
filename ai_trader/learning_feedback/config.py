"""Learning/Research Feedback configuration -- Phase D.

``LearningFeedbackConfig`` exists now purely as a TYPE: it carries no behavior and nothing in this
package (or anywhere else) reads it yet. It is the future opt-in switch Phase F will add as
``SimulationHarness``'s own additive ``learning_feedback_config: LearningFeedbackConfig | None = None``
constructor parameter -- default ``None`` means "feature disabled, byte-identical to today," matching
every prior touch's own convention (``health_eligible_ids``, `portfolio_architect_config`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.context_memory.contracts import SchemaVersion
from ai_trader.context_memory.validation import ContextMemoryValidationError

LEARNING_FEEDBACK_CONFIG_VERSION = SchemaVersion(namespace="learning_feedback_config", version="lfc-v1")


@dataclass(frozen=True)
class LearningFeedbackConfig:
    """Explicit, versioned, caller-constructed config -- never a hidden default (mirrors
    ``context_memory.evidence.EvidencePolicy``'s own established style). Carries no fields beyond its own
    version today; this phase defines the type only -- Phase F is where a real harness constructor
    parameter of this type activates any behavior."""

    config_version: SchemaVersion = field(default=LEARNING_FEEDBACK_CONFIG_VERSION)

    def __post_init__(self) -> None:
        if not isinstance(self.config_version, SchemaVersion):
            raise ContextMemoryValidationError(
                f"LearningFeedbackConfig.config_version must be a SchemaVersion, got {self.config_version!r}"
            )
