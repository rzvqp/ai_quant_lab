from __future__ import annotations

import pytest

from ai_trader.telegram_notifier.credentials import MissingTelegramCredentialsError, load_credentials_from_env


def test_loads_credentials_from_provided_env_mapping() -> None:
    env = {"TELEGRAM_BOT_TOKEN": "TOK", "TELEGRAM_CHAT_ID_PRIMARY": "111", "TELEGRAM_CHAT_ID_SECONDARY": "222"}
    credentials = load_credentials_from_env(env)
    assert credentials.bot_token == "TOK"
    assert credentials.primary_chat_id == "111"
    assert credentials.secondary_chat_id == "222"


def test_secondary_chat_id_is_optional() -> None:
    env = {"TELEGRAM_BOT_TOKEN": "TOK", "TELEGRAM_CHAT_ID_PRIMARY": "111"}
    credentials = load_credentials_from_env(env)
    assert credentials.secondary_chat_id is None


def test_missing_bot_token_raises() -> None:
    env = {"TELEGRAM_CHAT_ID_PRIMARY": "111"}
    with pytest.raises(MissingTelegramCredentialsError):
        load_credentials_from_env(env)


def test_missing_primary_chat_id_raises() -> None:
    env = {"TELEGRAM_BOT_TOKEN": "TOK"}
    with pytest.raises(MissingTelegramCredentialsError):
        load_credentials_from_env(env)


def test_falls_back_to_legacy_chat_id_when_primary_is_unset() -> None:
    env = {"TELEGRAM_BOT_TOKEN": "TOK", "TELEGRAM_CHAT_ID": "999"}
    credentials = load_credentials_from_env(env)
    assert credentials.primary_chat_id == "999"


def test_primary_chat_id_takes_priority_over_legacy_when_both_are_set() -> None:
    env = {"TELEGRAM_BOT_TOKEN": "TOK", "TELEGRAM_CHAT_ID_PRIMARY": "111", "TELEGRAM_CHAT_ID": "999"}
    credentials = load_credentials_from_env(env)
    assert credentials.primary_chat_id == "111"


def test_missing_both_primary_and_legacy_chat_id_raises() -> None:
    env = {"TELEGRAM_BOT_TOKEN": "TOK"}
    with pytest.raises(MissingTelegramCredentialsError):
        load_credentials_from_env(env)
