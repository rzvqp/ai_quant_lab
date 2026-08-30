from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.csv_causal_replay.engine import CSVCausalReplayEngine
from ai_trader.csv_causal_replay.persistence import DurablePointerStore

SEALED_FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "data" / "Q4_SEALED_1_378.csv"
Q4_P007_003_REF = "Q4-P007-003:OPEN"


@pytest.fixture
def sealed_fixture_path() -> Path:
    assert SEALED_FIXTURE_PATH.exists(), (
        f"{SEALED_FIXTURE_PATH} does not exist -- run "
        "`python -m ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture --source <path>` first"
    )
    return SEALED_FIXTURE_PATH


@pytest.fixture
def store(tmp_path) -> DurablePointerStore:
    return DurablePointerStore(tmp_path / "durable_state.json")


@pytest.fixture
def engine(sealed_fixture_path, store) -> CSVCausalReplayEngine:
    return CSVCausalReplayEngine(sealed_csv_path=sealed_fixture_path, store=store)


@pytest.fixture
def seeded_engine(engine) -> CSVCausalReplayEngine:
    """Seeded exactly at the mandate's own authoritative boundary: bar 378 already committed,
    Q4-P007-003 open (matching `AI_TRADER_Q4_M15_LOG.md`'s own last line at handoff)."""
    engine.seed_from_known_state(
        session_id="test-session", last_committed_bar_index=378,
        open_event_state_reference=Q4_P007_003_REF,
    )
    return engine
