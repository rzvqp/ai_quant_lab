"""`DecisionAuthority`/`current_authority`/`set_authority` tests -- real `SqliteStateStore`, never
mocked, mirroring `test_policy_control.py`'s own established pattern for this exact persistence layer."""

from __future__ import annotations

from pathlib import Path

from ai_trader.new_brain_bridge.authority import DecisionAuthority, current_authority, set_authority
from ai_trader.persistent_state.store import SqliteStateStore


def test_defaults_to_legacy_when_never_set(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    try:
        assert current_authority(store) is DecisionAuthority.LEGACY
    finally:
        store.close()


def test_set_new_brain_then_read_back(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    try:
        set_authority(store, DecisionAuthority.NEW_BRAIN)
        assert current_authority(store) is DecisionAuthority.NEW_BRAIN
    finally:
        store.close()


def test_set_legacy_explicitly_after_new_brain_reverts(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    try:
        set_authority(store, DecisionAuthority.NEW_BRAIN)
        set_authority(store, DecisionAuthority.LEGACY)
        assert current_authority(store) is DecisionAuthority.LEGACY
    finally:
        store.close()


def test_a_fresh_store_handle_reads_the_same_persisted_value() -> None:
    """The actual cross-process property this mechanism depends on: a SEPARATE `SqliteStateStore`
    instance pointed at the same file sees the flip -- proving this is real persistence, not
    process-local in-memory state."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "shared_state.db"
        writer = SqliteStateStore(db_path)
        try:
            set_authority(writer, DecisionAuthority.NEW_BRAIN)
        finally:
            writer.close()

        reader = SqliteStateStore(db_path)
        try:
            assert current_authority(reader) is DecisionAuthority.NEW_BRAIN
        finally:
            reader.close()
