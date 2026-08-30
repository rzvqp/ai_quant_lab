"""Mandate section 6: an open P007 forces reasoning-dependent/ATOMIC handling, P007 resolution
clears the lock, P007 remains TRADEABLE=NO and does not alter S5 eligibility, restart preserves any
open P007 state. Uses the REAL, already-consumed bars 786-787 (safe, far below 1305) for the full
integration proof -- the strongest available test, not a synthetic stand-in, wherever the real
long source file is present on this machine; synthetic-only tests cover the rest.
"""

from __future__ import annotations

import dataclasses
import shutil
from pathlib import Path

import pytest

from ai_trader.csv_causal_replay.engine import CSVCausalReplayEngine
from ai_trader.csv_causal_replay.errors import HybridModeLockedError
from ai_trader.csv_causal_replay.fixtures.autonomous_extend import bind_extended_fixture, extend_next_bar
from ai_trader.csv_causal_replay.identity import SourceIdentity
from ai_trader.csv_causal_replay.p007_gate import apply_p007_gate
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.types import DurableState

REAL_DATA_DIR = Path(__file__).parent.parent / "fixtures" / "data"
REAL_786 = REAL_DATA_DIR / "Q4_SEALED_1_786.csv"
REAL_786_MANIFEST = REAL_DATA_DIR / "Q4_SEALED_1_786_MANIFEST.json"

_LONG_SOURCE_CANDIDATES = [
    Path("/c/Users/MEDION GAMING/ai_quant_lab-alpha-automation/data/market/OANDA_XAUUSD_M15.csv"),
    Path("C:/Users/MEDION GAMING/ai_quant_lab-alpha-automation/data/market/OANDA_XAUUSD_M15.csv"),
]


def _find_long_source() -> Path | None:
    for c in _LONG_SOURCE_CANDIDATES:
        if c.exists():
            return c
    return None


def _seed_at_786(tmp_path) -> tuple[Path, DurablePointerStore]:
    import json
    output_dir = tmp_path / "data"
    output_dir.mkdir()
    shutil.copy(REAL_786, output_dir / REAL_786.name)
    shutil.copy(REAL_786_MANIFEST, output_dir / REAL_786_MANIFEST.name)
    manifest = json.loads((output_dir / REAL_786_MANIFEST.name).read_text(encoding="utf-8"))
    identity = SourceIdentity(
        source_file_name=manifest["source_file_name"], content_hash=manifest["content_hash"],
        symbol=manifest["symbol"], timeframe=manifest["timeframe"],
        bar_interval_seconds=manifest["bar_interval_seconds"], first_bar_ts_open=manifest["first_bar_ts_open"],
        sealed_through_bar_index=manifest["sealed_through_bar_index"], adapter_version=manifest["adapter_version"],
    )
    state = DurableState(
        source_identity=identity, session_id="test", last_committed_bar=manifest["last_bar_ts_open"],
        last_committed_timestamp=manifest["last_bar_ts_open"], next_bar=787, pending_decision=None,
        open_event_state_reference=None, adapter_version=manifest["adapter_version"],
    )
    store = DurablePointerStore(tmp_path / "state.json")
    store.save(state)
    return output_dir, store


@pytest.mark.skipif(not (REAL_786.exists() and _find_long_source()), reason="real bar-786 fixture or long source not present")
def test_full_real_integration_gate_engages_hybrid_lock_and_resolution_clears_it(tmp_path):
    output_dir, store = _seed_at_786(tmp_path)
    source_path = _find_long_source()

    # Extend + bind bar 787 (the real, already-known trigger bar) via the REAL, already-tested
    # E104/identity-handoff mechanisms -- not simulated.
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    bind_extended_fixture(store=store, output_dir=output_dir)

    # Apply the gate BEFORE step() -- the earliest point bar 787's data is legitimately bound.
    gated = apply_p007_gate(store=store, output_dir=output_dir)
    assert gated.open_event_state_reference is not None
    assert "bar_787" in gated.open_event_state_reference

    # HYBRID must now be refused.
    engine = CSVCausalReplayEngine(sealed_csv_path=output_dir / gated.source_identity.source_file_name, store=store)
    with pytest.raises(HybridModeLockedError):
        engine.run_until_gate(expected_pointer_before=gated.last_committed_timestamp, max_bars=8)

    # ATOMIC (step()) must still work normally while P007 is open.
    revealed = engine.step(expected_pointer_before=gated.last_committed_timestamp)
    assert revealed.bar_index == 787
    engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
    assert engine.status().open_event_state_reference is not None  # still open -- ROUTINE commit does not clear it

    # Bar 788 needs its own extend+bind first (the fixture is only sealed through 787 so far) --
    # same real E104/identity-handoff mechanism as bar 787 above.
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    bind_extended_fixture(store=store, output_dir=output_dir)

    # An explicit P007_RESOLUTION commit clears the lock -- the EXISTING engine.py mechanism,
    # unchanged. This proves the MECHANISM only (committing P007_RESOLUTION at whichever bar is
    # next, here 788) -- the historically-exact resolution bar (878) is separately, rigorously
    # reproduced by test_p007_detector.py's own dedicated test against the real ledger record.
    engine2 = CSVCausalReplayEngine(sealed_csv_path=output_dir / engine.status().source_identity.source_file_name, store=store)
    revealed2 = engine2.step(expected_pointer_before=revealed.bar.ts_open)
    engine2.commit_decision(
        bar_id=revealed2.bar.ts_open, decision_type="P007_RESOLUTION",
        decision_record={"trigger_bar_id": revealed.bar.ts_open, "resolution": "SUPPORT"},
    )
    assert engine2.status().open_event_state_reference is None

    # HYBRID must be available again now that the lock is cleared -- extend one more real bar first
    # so the call has genuine room to succeed (the fixture is otherwise sealed right at the bar just
    # committed, which would refuse for the unrelated reason of hitting that boundary, not proving
    # anything about the lock itself). Each extension needs its own step+commit before the NEXT
    # extension is allowed (ONE_BAR_UNLOCK_ENFORCED, mandate E104) -- extend/bind/step/commit for
    # bar 789, then extend/bind again for 790 to give run_until_gate one real bar of room.
    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    bind_extended_fixture(store=store, output_dir=output_dir)
    engine3 = CSVCausalReplayEngine(sealed_csv_path=output_dir / store.load().source_identity.source_file_name, store=store)
    revealed3 = engine3.step(expected_pointer_before=revealed2.bar.ts_open)
    engine3.commit_decision(bar_id=revealed3.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})

    extend_next_bar(store=store, source_path=source_path, output_dir=output_dir)
    bind_extended_fixture(store=store, output_dir=output_dir)
    state_after = store.load()
    engine4 = CSVCausalReplayEngine(sealed_csv_path=output_dir / state_after.source_identity.source_file_name, store=store)
    # max_bars=1: only one bar (790) has actually been extended/bound above -- asking for more would
    # correctly hit SealedBoundaryError on the next bar, which is a fixture-availability limit this
    # test deliberately didn't extend further for, not a HYBRID-lock question. One successful bar is
    # sufficient to prove the lock itself is cleared.
    result = engine4.run_until_gate(expected_pointer_before=state_after.last_committed_timestamp, max_bars=1)
    assert result is not None
    assert len(result.bars_processed) == 1


# ── synthetic-only: no-op / idempotency / field isolation / restart ────────────────────────────

def _minimal_state(sealed_through: int, *, open_ref: str | None) -> tuple[SourceIdentity, DurableState]:
    identity = SourceIdentity(
        source_file_name=f"Q4_SEALED_1_{sealed_through}.csv", content_hash="0" * 64, symbol="OANDA:XAUUSD",
        timeframe="M15", bar_interval_seconds=900, first_bar_ts_open=1_601_000_000,
        sealed_through_bar_index=sealed_through, adapter_version="1.0.0",
    )
    state = DurableState(
        source_identity=identity, session_id="t", last_committed_bar=1_601_000_000 + sealed_through * 900,
        last_committed_timestamp=1_601_000_000 + sealed_through * 900, next_bar=sealed_through + 1,
        pending_decision=None, open_event_state_reference=open_ref, adapter_version="1.0.0",
    )
    return identity, state


def test_p007_gate_module_never_references_s5_trades_or_mgmt004():
    """Structural, not merely behavioral: p007_gate.py's own source contains no reference to any of
    the concepts mandate section 4 forbids it from touching."""
    source = Path(__file__).parent.parent.joinpath("p007_gate.py").read_text(encoding="utf-8")
    forbidden = ["S5", "MGMT004", "MGMT-004", "TRADE_CONTRACT", "trade_evidence"]
    for term in forbidden:
        assert term not in source, f"p007_gate.py unexpectedly references {term!r}"


def test_apply_p007_gate_is_a_noop_when_no_candidate_is_open(tmp_path):
    """A flat synthetic series (no EMA crossing possible) sealed at bar 60 -- the gate must leave
    open_event_state_reference untouched (None stays None)."""
    import csv as csv_module

    from ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture import materialize
    from ai_trader.csv_causal_replay.identity import M15_BAR_INTERVAL_SECONDS, Q4_START_TS

    source_path = tmp_path / "flat_source.csv"
    with source_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv_module.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close", "volume"])
        for i in range(120):
            ts = Q4_START_TS + i * M15_BAR_INTERVAL_SECONDS
            writer.writerow([ts, 100.0, 100.0, 100.0, 100.0, 10])
    output_dir = tmp_path / "data"
    manifest = materialize(source_path, max_q4_bar_index=60, output_dir=output_dir)
    identity = SourceIdentity(
        source_file_name=manifest["source_file_name"], content_hash=manifest["content_hash"],
        symbol=manifest["symbol"], timeframe=manifest["timeframe"],
        bar_interval_seconds=manifest["bar_interval_seconds"], first_bar_ts_open=manifest["first_bar_ts_open"],
        sealed_through_bar_index=manifest["sealed_through_bar_index"], adapter_version=manifest["adapter_version"],
    )
    state = DurableState(
        source_identity=identity, session_id="t", last_committed_bar=manifest["last_bar_ts_open"],
        last_committed_timestamp=manifest["last_bar_ts_open"], next_bar=61, pending_decision=None,
        open_event_state_reference=None, adapter_version=manifest["adapter_version"],
    )
    store = DurablePointerStore(tmp_path / "state.json")
    store.save(state)

    result = apply_p007_gate(store=store, output_dir=output_dir)
    assert result.open_event_state_reference is None
    assert result == state


def test_apply_p007_gate_never_overwrites_an_already_open_reference(tmp_path):
    identity, state = _minimal_state(10, open_ref="Q4-P007-CANDIDATE:OPEN@bar_3")
    store = DurablePointerStore(tmp_path / "state.json")
    store.save(state)
    output_dir = tmp_path / "data"
    output_dir.mkdir()
    # No fixture file needs to exist for THIS test: an already-open reference short-circuits before
    # the gate ever tries to read one (see p007_gate.py's own idempotent-no-op ordering).
    result = apply_p007_gate(store=store, output_dir=output_dir)
    assert result.open_event_state_reference == "Q4-P007-CANDIDATE:OPEN@bar_3"


def test_restart_preserves_open_p007_state(tmp_path):
    store_path = tmp_path / "state.json"
    _, state = _minimal_state(10, open_ref="Q4-P007-CANDIDATE:OPEN@bar_10")
    DurablePointerStore(store_path).save(state)

    reloaded = DurablePointerStore(store_path).load()  # simulated restart: fresh store instance
    assert reloaded.open_event_state_reference == "Q4-P007-CANDIDATE:OPEN@bar_10"
    assert reloaded.next_bar == state.next_bar
    assert reloaded.last_committed_bar == state.last_committed_bar
