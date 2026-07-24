"""Control 9 (no-write control): Recognition Engine must never modify Context Memory, Learning Feedback,
strategies, portfolio, or execution -- CEO's own explicit Phase 1A requirement."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from ai_trader.context_memory.enums import OutcomeKind
from ai_trader.context_memory.repository import ContextMemoryRepository
from ai_trader.recognition_engine import engine as engine_module
from ai_trader.recognition_engine.engine import compute_conditional_statistics
from ai_trader.recognition_engine.types import ContextDimension
from ai_trader.recognition_engine.tests._fixtures import build_repository

_WRITE_METHOD_NAMES = (
    "append", "append_context_snapshot", "append_context_snapshots", "append_observation",
    "append_observations", "append_outcome", "append_outcomes", "append_operational_metadata",
    "append_operational_metadatas", "append_interim_realization", "append_position_outcome",
)


class _WriteForbiddingRepository(ContextMemoryRepository):
    """Wraps a real repository; any write call raises immediately, proving the code under test never
    attempts one -- not merely that it happens not to today."""

    def __getattribute__(self, name: str) -> object:
        if name in _WRITE_METHOD_NAMES:
            raise AssertionError(f"Recognition Engine attempted a write call: {name}()")
        return super().__getattribute__(name)


def test_static_no_repository_write_call_anywhere_in_engine_source() -> None:
    """Structural proof: the module's own source text never references any repository write method name
    (deliberately NOT a bare "append" substring check -- `results.append(...)` is a legitimate, ordinary
    Python list append inside `compute_conditional_statistics`, unrelated to repository writes)."""
    source = inspect.getsource(engine_module)
    # "append" (bare) deliberately excluded -- `results.append(...)` inside compute_conditional_statistics
    # is an ordinary Python list append, unrelated to any repository write; every OTHER name here is
    # unambiguous (no legitimate non-repository reason for e.g. "append_position_outcome" to appear).
    checked_names = tuple(name for name in _WRITE_METHOD_NAMES if name != "append")
    hits = {name for name in checked_names if name in source}
    assert not hits, f"engine.py references repository write method(s): {hits}"


def test_runtime_no_write_call_during_computation(tmp_path: Path) -> None:
    records = [
        {"strategy_id": "S1", "outcome_kind": OutcomeKind.STRATEGY, "result": 1.0,
         "snapshot_overrides": {"session_state": "ny"}}
        for _ in range(30)
    ]
    real_repo = build_repository(tmp_path, records)
    forbidding_repo = _WriteForbiddingRepository(real_repo.root_path)
    # Must complete normally -- no write method was ever called, so nothing raises.
    stats = compute_conditional_statistics(forbidding_repo, "S1", OutcomeKind.STRATEGY, ContextDimension.SESSION)
    assert stats[0].n == 30


def test_write_forbidding_wrapper_actually_detects_a_write_attempt(tmp_path: Path) -> None:
    """Sanity-check the control itself: confirm `_WriteForbiddingRepository` genuinely raises on a real
    write attempt (else the runtime no-write test above would be vacuous)."""
    repo = _WriteForbiddingRepository(tmp_path / "repo2")
    from ai_trader.recognition_engine.tests._fixtures import make_observation

    with pytest.raises(AssertionError, match="attempted a write call"):
        repo.append_observation(make_observation())
