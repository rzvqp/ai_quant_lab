"""`SlippageObservation`/`SlippageLog` tests -- serialize/deserialize round-trip, in-memory vs.
persisted-store behavior, matching the established `SpreadObservationLog`/`PdhPdlAuditJournal` test
pattern."""

from __future__ import annotations

from pathlib import Path

from ai_trader.pdh_pdl_demo.slippage import SlippageLeg, SlippageLog, SlippageObservation
from ai_trader.persistent_state.store import SqliteStateStore

SYMBOL = "XAUUSD"


def _entry_observation() -> SlippageObservation:
    return SlippageObservation(
        symbol=SYMBOL, magic_number=100_001, client_order_id="CID-1", leg=SlippageLeg.ENTRY,
        as_of=1_705_356_000, direction=-1, requested_price=108.0, realized_price=108.05,
        signed_slippage=0.05, close_reason=None,
    )


def _exit_observation() -> SlippageObservation:
    return SlippageObservation(
        symbol=SYMBOL, magic_number=100_001, client_order_id="CID-1", leg=SlippageLeg.EXIT,
        as_of=1_705_356_900, direction=-1, requested_price=111.0, realized_price=111.08,
        signed_slippage=0.08, close_reason="BROKER_SLTP",
    )


def test_record_without_a_store_is_in_memory_only() -> None:
    log = SlippageLog()
    log.record(_entry_observation())

    assert len(log.entries) == 1
    assert log.entries[0].leg is SlippageLeg.ENTRY
    assert log.entries[0].signed_slippage == 0.05


def test_record_persists_through_a_state_store(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    log = SlippageLog(store)
    log.record(_entry_observation())
    log.record(_exit_observation())

    assert len(log.entries) == 2
    store.close()


def test_entries_survive_a_reload_from_the_same_store(tmp_path: Path) -> None:
    store1 = SqliteStateStore(tmp_path / "state.db")
    SlippageLog(store1).record(_entry_observation())
    store1.close()

    store2 = SqliteStateStore(tmp_path / "state.db")
    log2 = SlippageLog(store2)

    assert len(log2.entries) == 1
    reloaded = log2.entries[0]
    assert reloaded.symbol == SYMBOL
    assert reloaded.magic_number == 100_001
    assert reloaded.client_order_id == "CID-1"
    assert reloaded.leg is SlippageLeg.ENTRY
    assert reloaded.as_of == 1_705_356_000
    assert reloaded.direction == -1
    assert reloaded.requested_price == 108.0
    assert reloaded.realized_price == 108.05
    assert reloaded.signed_slippage == 0.05
    assert reloaded.close_reason is None
    store2.close()


def test_exit_leg_close_reason_survives_a_reload(tmp_path: Path) -> None:
    store = SqliteStateStore(tmp_path / "state.db")
    SlippageLog(store).record(_exit_observation())
    store.close()

    store2 = SqliteStateStore(tmp_path / "state.db")
    reloaded = SlippageLog(store2).entries[0]

    assert reloaded.leg is SlippageLeg.EXIT
    assert reloaded.close_reason == "BROKER_SLTP"
    assert reloaded.signed_slippage == 0.08
    store2.close()


def test_signed_slippage_is_not_abs_and_can_be_negative() -> None:
    """A favorable fill (realized price better than requested) must be recorded as negative, not
    clamped -- this module deliberately does NOT `abs()` (see its own module docstring); that decision
    belongs to whoever consumes the log."""
    favorable = SlippageObservation(
        symbol=SYMBOL, magic_number=100_001, client_order_id="CID-2", leg=SlippageLeg.ENTRY,
        as_of=1_705_356_000, direction=1, requested_price=100.0, realized_price=99.95,
        signed_slippage=-0.05, close_reason=None,
    )
    log = SlippageLog()
    log.record(favorable)

    assert log.entries[0].signed_slippage == -0.05


def test_two_policies_sharing_one_log_are_distinguished_by_magic_number(tmp_path: Path) -> None:
    """Matches `multi_policy_live`'s own wiring: one shared `SlippageLog` per process, filterable by
    `magic_number` per policy."""
    store = SqliteStateStore(tmp_path / "state.db")
    log = SlippageLog(store)
    log.record(_entry_observation())  # magic_number=100_001
    other_policy = SlippageObservation(
        symbol=SYMBOL, magic_number=100_002, client_order_id="CID-3", leg=SlippageLeg.ENTRY,
        as_of=1_705_356_000, direction=1, requested_price=50.0, realized_price=50.02,
        signed_slippage=0.02, close_reason=None,
    )
    log.record(other_policy)

    magic_numbers = {e.magic_number for e in log.entries}
    assert magic_numbers == {100_001, 100_002}
    store.close()
