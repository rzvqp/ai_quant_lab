"""Teste inference -- mandat §11 iteme 4/7/8/17/21-24."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dev_fixtures import make_dev_input  # noqa: E402
from inference import FROZEN_CONFIG_ID, FROZEN_PROTOTYPE_COMMIT, run_inference  # noqa: E402


def _write_input(tmp_path: Path, **kw) -> Path:
    p = tmp_path / "input.json"
    p.write_text(json.dumps(make_dev_input(**kw)), encoding="utf-8")
    return p


def test_still_open_structure_at_window_end_is_included(tmp_path: Path) -> None:
    """**Găsit, remediat**: `ledger.macro_history`/`internal_history` conțin DOAR structurile
    ÎNCHISE -- o structură confirmată dar încă deschisă la finalul ferestrei (cazul obișnuit,
    range-ul nu apucă să spargă înainte de capăt) lipsea complet din `macro_structures` deși
    `records` arăta clar `OK_RANGE_MACRO`/`RANGE_CONFIRMED`. Descoperit prin exercitarea directă
    a inference-ului pe un fixture de 200 de bare (nu prin code review)."""
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=200)
    result = run_inference(inp, tmp_path / "out")
    preds = json.loads(result["predictions_path"].read_text(encoding="utf-8"))
    w = preds["windows"][0]
    last_rec = w["records"][-1]
    assert last_rec["macro"]["reason"] == "OK_RANGE_MACRO"
    assert len(w["macro_structures"]) >= 1, "structura MACRO încă deschisă lipsește din macro_structures"
    open_struct = w["macro_structures"][-1]
    assert open_struct["end_ts"] is None
    assert open_struct["confirm_ts"] is not None
    assert open_struct["boundary_upper"] is not None and open_struct["boundary_lower"] is not None
    assert open_struct["depth"] == "MACRO"


def test_inference_produces_three_artifacts(tmp_path: Path) -> None:
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=40)
    out_dir = tmp_path / "out"
    result = run_inference(inp, out_dir)
    assert result["predictions_path"].exists()
    assert result["manifest_path"].exists()
    assert result["sha_path"].exists()


def test_output_schema_has_required_fields(tmp_path: Path) -> None:
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=40)
    result = run_inference(inp, tmp_path / "out")
    preds = json.loads(result["predictions_path"].read_text(encoding="utf-8"))
    for f in ("prototype_commit", "contract_version", "config_id", "code_fingerprint",
             "config_fingerprint", "input_bytes_hash", "normalized_bars_hash", "windows",
             "snapshot_restore_markers"):
        assert f in preds, f"câmp lipsă din output: {f}"
    assert preds["prototype_commit"] == FROZEN_PROTOTYPE_COMMIT
    assert preds["config_id"] == FROZEN_CONFIG_ID
    w = preds["windows"][0]
    assert "window_id" in w and "records" in w and "macro_structures" in w and "internal_structures" in w
    rec = w["records"][0]
    for f in ("bar_index", "macro", "internal", "events"):
        assert f in rec
    for f in ("structure_id", "state", "boundary_upper", "boundary_lower", "confirm_ts", "role", "reason"):
        assert f in rec["macro"]


def test_zero_real_calendar_timestamp_in_output(tmp_path: Path) -> None:
    """Mandat §6: nu se publică timestamp-uri calendaristice reale în output pt. evaluare."""
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=30)
    result = run_inference(inp, tmp_path / "out")
    text = result["predictions_path"].read_text(encoding="utf-8")
    assert "ts_close" not in text and "ts_open" not in text
    # ts_open-ul de dezvoltare a fost 1_700_000_000 -- confirmă că nu apare literal in output
    assert "1700000000" not in text.replace("_", "")


def test_zero_local_paths_zero_secrets_in_output(tmp_path: Path) -> None:
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=20)
    result = run_inference(inp, tmp_path / "out")
    text = result["predictions_path"].read_text(encoding="utf-8")
    assert "C:\\" not in text and "/home/" not in text and "TELEGRAM" not in text.upper()


def test_two_windows_produce_independent_results_no_shared_state(tmp_path: Path) -> None:
    """Mandat §10: două instanțe (aici, două ferestre procesate în aceeași rulare) nu împart stare."""
    inp = _write_input(tmp_path, n_windows=2, bars_per_window=40)
    result = run_inference(inp, tmp_path / "out")
    preds = json.loads(result["predictions_path"].read_text(encoding="utf-8"))
    w0, w1 = preds["windows"]
    assert w0["window_id"] != w1["window_id"]
    # ambele incep la bar_index=0 -- confirma ca fiecare fereastra a pornit de la o instanta noua
    assert w0["records"][0]["bar_index"] == 0
    assert w1["records"][0]["bar_index"] == 0


def test_manifest_declares_zero_labels_access(tmp_path: Path) -> None:
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=20)
    result = run_inference(inp, tmp_path / "out")
    manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
    assert manifest["zero_labels_access"] is True
    assert manifest["input_bytes_hash"] and manifest["output_hash"]
    assert manifest["prototype_commit"] == FROZEN_PROTOTYPE_COMMIT


def test_predictions_file_is_read_only_after_write(tmp_path: Path) -> None:
    import os
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=10)
    result = run_inference(inp, tmp_path / "out")
    mode = os.stat(result["predictions_path"]).st_mode
    assert not (mode & 0o222), "predictions.json trebuie să fie read-only după sigilare"


def test_no_pnl_no_broker_no_network_keywords_in_predictions(tmp_path: Path) -> None:
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=20)
    result = run_inference(inp, tmp_path / "out")
    text = result["predictions_path"].read_text(encoding="utf-8").lower()
    for forbidden in ("pnl", "broker", "order_send", "mt5", "http://", "https://"):
        assert forbidden not in text, f"cuvânt interzis găsit în output: {forbidden}"
