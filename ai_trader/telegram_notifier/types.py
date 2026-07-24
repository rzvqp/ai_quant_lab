"""Types owned by the Telegram Notification Service (Phase 5). Deliberately domain-free: nothing here
references any trading concept (`OrderRequest`, `RiskDecision`, ...) -- this module is a pure transport,
never a trading-domain dependent (`TELEGRAM_NOTIFIER_PHASE5_DESIGN.md` §2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ChatTarget(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    BOTH = "BOTH"


@dataclass(frozen=True, slots=True)
class TelegramCredentials:
    """`__repr__`/`__str__` NEVER include `bot_token` -- both are overridden to redact it
    unconditionally (same mandatory pattern as Phase 1's `BrokerCredentials`), so accidental logging,
    exception-message interpolation, or `repr()` in a debugger/traceback can never leak it."""

    bot_token: str
    primary_chat_id: str
    secondary_chat_id: str | None = None

    def __post_init__(self) -> None:
        if not self.bot_token:
            raise ValueError("TelegramCredentials.bot_token must be non-empty")
        if not self.primary_chat_id:
            raise ValueError("TelegramCredentials.primary_chat_id must be non-empty")

    def __repr__(self) -> str:
        return (
            f"TelegramCredentials(bot_token='***REDACTED***', primary_chat_id={self.primary_chat_id!r}, "
            f"secondary_chat_id={self.secondary_chat_id!r})"
        )

    __str__ = __repr__


@dataclass(frozen=True, slots=True)
class NotificationEvent:
    """Constructed by the CALLER from its own domain objects -- this module never constructs one
    itself from a trading type. `detail` is a flat `str->str` map (no nested trading objects) to keep
    the domain-free boundary honest, not merely conventional."""

    event_type: str
    summary: str
    correlation_id: str
    as_of: int
    detail: dict[str, str] = field(default_factory=dict)
    chat_target: ChatTarget = ChatTarget.PRIMARY

    def __post_init__(self) -> None:
        if not self.event_type:
            raise ValueError("NotificationEvent.event_type must be non-empty")
        if not self.summary:
            raise ValueError("NotificationEvent.summary must be non-empty")
        if not self.correlation_id:
            raise ValueError("NotificationEvent.correlation_id must be non-empty")

    def render_text(self) -> str:
        lines = [f"[{self.event_type}] {self.summary}", f"correlation_id={self.correlation_id}"]
        for key in sorted(self.detail):
            lines.append(f"{key}={self.detail[key]}")
        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Field-identical to `execution_engine.adapters.base.RetryPolicy` -- DUPLICATED, not imported,
    deliberately, to keep this cross-cutting service free of any dependency on the execution/broker
    layer (`TELEGRAM_NOTIFIER_PHASE5_DESIGN.md` §1)."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.1
    backoff_multiplier: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError(f"RetryPolicy.max_attempts must be >= 1, got {self.max_attempts!r}")
        if self.base_delay_seconds < 0:
            raise ValueError("RetryPolicy.base_delay_seconds must be >= 0")
        if self.backoff_multiplier < 1:
            raise ValueError("RetryPolicy.backoff_multiplier must be >= 1")


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    max_messages: int = 20
    per_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.max_messages < 1:
            raise ValueError("RateLimitPolicy.max_messages must be >= 1")
        if self.per_seconds <= 0:
            raise ValueError("RateLimitPolicy.per_seconds must be > 0")


@dataclass(frozen=True, slots=True)
class TelegramNotifierConfig:
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    rate_limit: RateLimitPolicy = field(default_factory=RateLimitPolicy)
    request_timeout_seconds: float = 5.0
    api_base_url: str = "https://api.telegram.org"


@dataclass(frozen=True, slots=True)
class SendResult:
    chat_id: str
    success: bool
    attempts: int
    http_status: int | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class NotificationOutcome:
    event_type: str
    correlation_id: str
    results: tuple[SendResult, ...]
    rate_limited: bool = False

    @property
    def overall_success(self) -> bool:
        return bool(self.results) and all(r.success for r in self.results)
