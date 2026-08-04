"""`PolicyControl` tests."""

from __future__ import annotations

from pathlib import Path

from ai_trader.multi_policy_live.policy_control import PolicyControl
from ai_trader.persistent_state.store import SqliteStateStore


def test_defaults_to_disabled_when_never_set(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    try:
        control = PolicyControl(store)
        assert control.is_enabled("CAND-0009") is False
    finally:
        store.close()


def test_custom_default_is_respected_when_never_set(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    try:
        control = PolicyControl(store)
        assert control.is_enabled("CAND-0007", default=True) is True
    finally:
        store.close()


def test_set_enabled_true_then_read_back(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    try:
        control = PolicyControl(store)
        control.set_enabled("CAND-0007", True)
        assert control.is_enabled("CAND-0007") is True
    finally:
        store.close()


def test_set_enabled_false_overrides_a_default_of_true(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    try:
        control = PolicyControl(store)
        control.set_enabled("CAND-0009", False)
        assert control.is_enabled("CAND-0009", default=True) is False
    finally:
        store.close()


def test_persists_across_a_new_store_connection_to_the_same_file(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    store1 = SqliteStateStore(db_path)
    PolicyControl(store1).set_enabled("CAND-0019", True)
    store1.close()

    store2 = SqliteStateStore(db_path)
    try:
        assert PolicyControl(store2).is_enabled("CAND-0019") is True
    finally:
        store2.close()


def test_different_policies_are_independent(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    try:
        control = PolicyControl(store)
        control.set_enabled("CAND-0007", True)
        assert control.is_enabled("CAND-0007") is True
        assert control.is_enabled("CAND-0009") is False
    finally:
        store.close()
