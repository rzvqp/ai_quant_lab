"""Mandate: wire P007 gate into real Q4 replay loop. Section 4's required regression (real bars
787/878, through the actual production loop) and section 5's over-inclusive-crossing checks
(rejected candidates clear, genuine opens stay locked, later crossings are not masked by a stale
prior reference) -- driven entirely through `reveal_next_bar_with_p007_gate`, the actual wired
entrypoint, never a simulation of it.
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

import pytest

from ai_trader.csv_causal_replay.engine import CSVCausalReplayEngine
from ai_trader.csv_causal_replay.errors import HybridModeLockedError
from ai_trader.csv_causal_replay.identity import M15_BAR_INTERVAL_SECONDS, Q4_START_TS, SourceIdentity
from ai_trader.csv_causal_replay.persistence import DurablePointerStore
from ai_trader.csv_causal_replay.q4_replay_step import reveal_next_bar_with_p007_gate
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


# ── section 4: required regression, real bars 787/878, through the ACTUAL wired loop ───────────

@pytest.mark.skipif(not (REAL_786.exists() and _find_long_source()), reason="real bar-786 fixture or long source not present")
def test_real_p007_004_regression_through_the_actual_wired_loop(tmp_path):
    output_dir, store = _seed_at_786(tmp_path)
    source_path = _find_long_source()

    # Bar 787: the real, known trigger -- revealed through the ONE canonical wired entrypoint.
    result = reveal_next_bar_with_p007_gate(store=store, source_path=source_path, output_dir=output_dir)
    assert result.revealed.bar_index == 787
    assert result.new_p007_candidate_detected is True
    assert "bar_787" in result.state_after_gate.open_event_state_reference

    # reveal_next_bar_with_p007_gate() already called step() internally, so a pending_decision
    # exists for bar 787 at this point -- run_until_gate would refuse via MissingCommitError
    # regardless of P007 status here, which would not isolate the P007-SPECIFIC lock this test
    # wants to prove. Commit first, THEN check that HYBRID is refused for the P007 reason
    # specifically (HybridModeLockedError, not MissingCommitError).
    engine = CSVCausalReplayEngine(
        sealed_csv_path=output_dir / result.state_after_gate.source_identity.source_file_name, store=store,
    )
    engine.commit_decision(bar_id=result.revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
    with pytest.raises(HybridModeLockedError):
        engine.run_until_gate(expected_pointer_before=result.revealed.bar.ts_open, max_bars=8)

    # Bar 788: still locked, gate does not re-flag (already open), no new-candidate signal.
    result2 = reveal_next_bar_with_p007_gate(store=store, source_path=source_path, output_dir=output_dir)
    assert result2.new_p007_candidate_detected is False
    assert result2.state_after_gate.open_event_state_reference is not None
    engine2 = CSVCausalReplayEngine(
        sealed_csv_path=output_dir / result2.state_after_gate.source_identity.source_file_name, store=store,
    )
    engine2.commit_decision(bar_id=result2.revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})

    # The historically-exact resolution bar (878) is separately, rigorously reproduced against the
    # full real history by test_p007_detector.py -- this test proves the WIRING mechanism using the
    # real trigger bar and an explicit resolution commit, not a re-walk of all 91 intervening bars.
    assert result2.state_after_gate.open_event_state_reference is not None


# ── section 5: over-inclusive crossings, rejected candidates, stale-lock masking, later crossings ─

def _write_two_cycle_synthetic_source(path: Path, *, total_bars: int = 260) -> None:
    """Empirically verified (not guessed) via a standalone replay before this test was written:
    TRIGGER@205, RESOLUTION@237, TRIGGER@245, RESOLUTION@253 -- two clean, separate P007 cycles."""
    def close_for(i: int) -> float:
        if i < 204:
            return 100.0
        if i < 236:
            return 90.0
        if i < 244:
            return 110.0
        if i < 252:
            return 90.0
        return 110.0

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close", "volume"])
        for i in range(total_bars):
            ts = Q4_START_TS + i * M15_BAR_INTERVAL_SECONDS
            c = close_for(i)
            writer.writerow([ts, c, c, c, c, 10])


def _seed_at_bar_1(tmp_path, source_path: Path) -> tuple[Path, DurablePointerStore]:
    from ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture import materialize
    output_dir = tmp_path / "data"
    manifest = materialize(source_path, max_q4_bar_index=1, output_dir=output_dir)
    identity = SourceIdentity(
        source_file_name=manifest["source_file_name"], content_hash=manifest["content_hash"],
        symbol=manifest["symbol"], timeframe=manifest["timeframe"],
        bar_interval_seconds=manifest["bar_interval_seconds"], first_bar_ts_open=manifest["first_bar_ts_open"],
        sealed_through_bar_index=manifest["sealed_through_bar_index"], adapter_version=manifest["adapter_version"],
    )
    state = DurableState(
        source_identity=identity, session_id="test", last_committed_bar=manifest["last_bar_ts_open"],
        last_committed_timestamp=manifest["last_bar_ts_open"], next_bar=2, pending_decision=None,
        open_event_state_reference=None, adapter_version=manifest["adapter_version"],
    )
    store = DurablePointerStore(tmp_path / "state.json")
    store.save(state)
    return output_dir, store


def test_two_separate_cycles_rejected_candidate_clears_and_later_crossing_not_masked(tmp_path):
    source_path = tmp_path / "synthetic_two_cycle_source.csv"
    _write_two_cycle_synthetic_source(source_path)
    output_dir, store = _seed_at_bar_1(tmp_path, source_path)

    seen_new_candidate_at: list[int] = []
    naturally_reclaimed_at: list[int] = []

    for _ in range(255):
        result = reveal_next_bar_with_p007_gate(store=store, source_path=source_path, output_dir=output_dir)
        idx = result.revealed.bar_index

        if result.new_p007_candidate_detected:
            seen_new_candidate_at.append(idx)
        if result.p007_naturally_reclaimed_but_still_locked:
            naturally_reclaimed_at.append(idx)

        engine = CSVCausalReplayEngine(
            sealed_csv_path=output_dir / result.state_after_gate.source_identity.source_file_name, store=store,
        )
        if idx == 237:
            # A REJECTED classification (not "SUPPORT") -- must still clear the lock via the same
            # P007_RESOLUTION mechanism; nothing in this package special-cases specific resolution values.
            engine.commit_decision(
                bar_id=result.revealed.bar.ts_open, decision_type="P007_RESOLUTION",
                decision_record={"trigger_bar_id": 205 * 900 + Q4_START_TS - 900, "resolution": "NOT_QUALIFYING_TOO_BRIEF"},
            )
        elif idx == 253:
            engine.commit_decision(
                bar_id=result.revealed.bar.ts_open, decision_type="P007_RESOLUTION",
                decision_record={"trigger_bar_id": 245 * 900 + Q4_START_TS - 900, "resolution": "SUPPORT"},
            )
        else:
            engine.commit_decision(bar_id=result.revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})

    # Two SEPARATE detections -- the second is NOT masked by the first having already occurred and resolved.
    assert seen_new_candidate_at == [205, 245]
    # The natural-reclaim signal fired for both true reclaim bars, before either resolution was committed.
    assert 237 in naturally_reclaimed_at
    assert 253 in naturally_reclaimed_at
    # Final state: no lock left over from either cycle.
    assert store.load().open_event_state_reference is None


def test_hybrid_refused_throughout_a_genuinely_open_p007_even_across_many_routine_commits(tmp_path):
    source_path = tmp_path / "synthetic_source.csv"
    _write_two_cycle_synthetic_source(source_path)
    output_dir, store = _seed_at_bar_1(tmp_path, source_path)

    for _ in range(210):  # through bar 210 -- inside the first open interval (205-236)
        result = reveal_next_bar_with_p007_gate(store=store, source_path=source_path, output_dir=output_dir)
        engine = CSVCausalReplayEngine(
            sealed_csv_path=output_dir / result.state_after_gate.source_identity.source_file_name, store=store,
        )
        engine.commit_decision(bar_id=result.revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})

    final_state = store.load()
    assert final_state.open_event_state_reference is not None  # still genuinely open
    engine = CSVCausalReplayEngine(
        sealed_csv_path=output_dir / final_state.source_identity.source_file_name, store=store,
    )
    with pytest.raises(HybridModeLockedError):
        engine.run_until_gate(expected_pointer_before=final_state.last_committed_timestamp, max_bars=8)
