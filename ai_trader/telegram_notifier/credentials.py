"""Environment-variable credential loading -- no hardcoded credentials, no invented registry mechanism
(none exists in this repo's own conventions, `TELEGRAM_NOTIFIER_PHASE5_DESIGN.md` §4).

`PRIMARY_CHAT_ID_ENV_VAR` (`TELEGRAM_CHAT_ID_PRIMARY`) is the canonical name. `LEGACY_CHAT_ID_ENV_VAR`
(`TELEGRAM_CHAT_ID`, no suffix) is accepted as a fallback ONLY when the canonical name is unset --
`TELEGRAM_CHAT_ID` predates this package (set by an earlier ad-hoc PowerShell notification mechanism)
and is what several machines already have persisted in their User-scope environment. Accepting it here,
in code, means no machine-specific `setx` step is required for the official package to work: a fresh
machine that only carries the old variable still works today, and one that's been migrated to the
canonical name takes priority automatically without any code change."""

from __future__ import annotations

import os

from ai_trader.telegram_notifier.types import TelegramCredentials

BOT_TOKEN_ENV_VAR = "TELEGRAM_BOT_TOKEN"
PRIMARY_CHAT_ID_ENV_VAR = "TELEGRAM_CHAT_ID_PRIMARY"
LEGACY_CHAT_ID_ENV_VAR = "TELEGRAM_CHAT_ID"
SECONDARY_CHAT_ID_ENV_VAR = "TELEGRAM_CHAT_ID_SECONDARY"


class MissingTelegramCredentialsError(Exception):
    """Raised only by `load_credentials_from_env` itself (a startup-time, explicit failure) -- never by
    `notify()`, which is fail-closed and never raises."""


def load_credentials_from_env(env: dict[str, str] | None = None) -> TelegramCredentials:
    resolved_env = env if env is not None else os.environ
    bot_token = resolved_env.get(BOT_TOKEN_ENV_VAR)
    primary_chat_id = resolved_env.get(PRIMARY_CHAT_ID_ENV_VAR) or resolved_env.get(LEGACY_CHAT_ID_ENV_VAR)
    if not bot_token or not primary_chat_id:
        raise MissingTelegramCredentialsError(
            f"{BOT_TOKEN_ENV_VAR} and one of ({PRIMARY_CHAT_ID_ENV_VAR}, {LEGACY_CHAT_ID_ENV_VAR}) must be set"
        )
    secondary_chat_id = resolved_env.get(SECONDARY_CHAT_ID_ENV_VAR) or None
    return TelegramCredentials(
        bot_token=bot_token, primary_chat_id=primary_chat_id, secondary_chat_id=secondary_chat_id,
    )
