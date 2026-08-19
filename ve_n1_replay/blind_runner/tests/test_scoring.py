"""Teste scoring -- mandat §11 iteme 5/18/20."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dev_fixtures import make_dev_input  # noqa: E402
from inference import run_inference  # noqa: E402
from scoring import load_frozen_predictions, score  # noqa: E402


@pytest.fixture()
def frozen_predictions(tmp_path: Path) -> tuple[Path, dict]:
    inp = tmp_path / "input.json"
    inp.write_text(json.dumps(make_dev_input(n_windows=1, bars_per_window=200)), encoding="utf-8")
    out_dir = tmp_path / "out"
    run_inference(inp, out_dir)
    return out_dir, load_frozen_predictions(out_dir)


def test_matching_label_yields_full_recall(frozen_predictions) -> None:
    out_dir, preds = frozen_predictions
    # fixture-ul de 200 bare confirma MACRO id=1 la start_ts=3, deschis pana la finalul ferestrei --
    # o eticheta care acopera aproape acelasi interval trebuie sa se potriveasca (IoU mare, recall=1).
    labels = {"segments": [{"window_id": "DEV-000", "level": "MACRO", "start": 3, "end": 200,
                            "window_bars": 200, "block": "B1"}]}
    result = score(preds, labels)
    assert result["macro"]["recall"] == 1.0
    assert result["macro"]["gt_count"] == 1
    assert result["macro"]["matched_count"] == 1
    assert result["macro"]["iou_median"] is not None and result["macro"]["iou_median"] > 0.9


def test_nonmatching_label_yields_zero_recall_and_reports_missed(frozen_predictions) -> None:
    out_dir, preds = frozen_predictions
    # o eticheta intr-o zona a ferestrei complet nesuprapusa cu structura reala (id=1, [3,200))
    # nu se poate cere de fapt in interiorul acelorasi 200 de bare -- simuleaza in schimb o eticheta
    # pt. o fereastra care NU exista deloc in predictii (acoperire zero prin constructie).
    labels = {"segments": [{"window_id": "DEV-999-NONEXISTENT", "level": "MACRO", "start": 0, "end": 50,
                            "window_bars": 50, "block": "B1"}]}
    result = score(preds, labels)
    assert result["macro"]["recall"] == 0.0
    assert len(result["macro"]["missed_segments"]) == 1


def test_internal_denominator_is_separate_from_macro() -> None:
    """Mandat §8: INTERNAL nu e dublu numărat -- denominator propriu."""
    preds = {"windows": [{"window_id": "W", "n_bars": 10, "records": [],
                          "macro_structures": [], "internal_structures": []}]}
    labels = {"segments": [
        {"window_id": "W", "level": "MACRO", "start": 0, "end": 10, "window_bars": 10, "block": "B1"},
        {"window_id": "W", "level": "INTERNAL", "start": 2, "end": 8, "window_bars": 10, "block": "B1"},
        {"window_id": "W", "level": "UNRESOLVED", "start": 0, "end": 5, "window_bars": 10, "block": "B1"},
    ]}
    result = score(preds, labels)
    assert result["population"]["macro_gt"] == 1
    assert result["population"]["internal_gt"] == 1
    assert result["population"]["unresolved_gt"] == 1
    assert result["population"]["macro_plus_unresolved"] == 2


def test_unresolved_never_enters_macro_recall_denominator() -> None:
    preds = {"windows": [{"window_id": "W", "n_bars": 10, "records": [],
                          "macro_structures": [], "internal_structures": []}]}
    labels = {"segments": [
        {"window_id": "W", "level": "UNRESOLVED", "start": 0, "end": 5, "window_bars": 10, "block": "B1"},
        {"window_id": "W", "level": "UNRESOLVED", "start": 5, "end": 10, "window_bars": 10, "block": "B1"},
    ]}
    result = score(preds, labels)
    assert result["macro"]["gt_count"] == 0
    assert result["macro"]["recall"] is None   # niciun GT MACRO -- recall nedefinit, NU zero fals


def test_load_frozen_predictions_refuses_commit_mismatch(tmp_path: Path, frozen_predictions) -> None:
    out_dir, _ = frozen_predictions
    pred_path = out_dir / "predictions.json"
    import os, stat
    os.chmod(pred_path, stat.S_IWRITE | stat.S_IREAD)
    data = json.loads(pred_path.read_text(encoding="utf-8"))
    data["prototype_commit"] = "deadbeef"
    new_bytes = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
    pred_path.write_bytes(new_bytes)
    import hashlib
    (out_dir / "predictions.sha256").write_text(
        f"{hashlib.sha256(new_bytes).hexdigest()}  predictions.json\n", encoding="utf-8")
    from scoring import ScoringRefusedError
    with pytest.raises(ScoringRefusedError) as exc_info:
        load_frozen_predictions(out_dir)
    assert exc_info.value.code == "COMMIT_MISMATCH"
