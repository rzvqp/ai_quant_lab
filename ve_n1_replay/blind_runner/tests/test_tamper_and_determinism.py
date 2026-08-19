"""Teste determinism + tamper detection -- mandat §10, §11 iteme 8-16."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dev_fixtures import make_dev_input  # noqa: E402
from inference import run_inference  # noqa: E402
from scoring import ScoringRefusedError, load_frozen_predictions, score  # noqa: E402


def _write_input(tmp_path: Path, name: str = "input.json", **kw) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(make_dev_input(**kw)), encoding="utf-8")
    return p


def test_same_input_byte_identical_output(tmp_path: Path) -> None:
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=50)
    r1 = run_inference(inp, tmp_path / "out1")
    r2 = run_inference(inp, tmp_path / "out2")
    assert r1["predictions_path"].read_bytes() == r2["predictions_path"].read_bytes()
    assert r1["predictions_hash"] == r2["predictions_hash"]


def test_window_order_independent_per_window_result(tmp_path: Path) -> None:
    """Fiecare fereastră își păstrează propriul rezultat indiferent de ordinea celorlalte."""
    d1 = make_dev_input(n_windows=2, bars_per_window=40)
    d2 = {"windows": list(reversed(d1["windows"]))}
    p1 = tmp_path / "in1.json"; p1.write_text(json.dumps(d1), encoding="utf-8")
    p2 = tmp_path / "in2.json"; p2.write_text(json.dumps(d2), encoding="utf-8")
    r1 = run_inference(p1, tmp_path / "o1")
    r2 = run_inference(p2, tmp_path / "o2")
    preds1 = json.loads(r1["predictions_path"].read_text(encoding="utf-8"))
    preds2 = json.loads(r2["predictions_path"].read_text(encoding="utf-8"))
    by_id_1 = {w["window_id"]: w["records"] for w in preds1["windows"]}
    by_id_2 = {w["window_id"]: w["records"] for w in preds2["windows"]}
    assert by_id_1.keys() == by_id_2.keys()
    for wid in by_id_1:
        assert by_id_1[wid] == by_id_2[wid], f"{wid}: rezultat diferit după reordonarea ferestrelor"


def test_one_bit_input_change_changes_hash(tmp_path: Path) -> None:
    d = make_dev_input(n_windows=1, bars_per_window=30)
    p1 = tmp_path / "a.json"; p1.write_text(json.dumps(d), encoding="utf-8")
    d["windows"][0]["bars"][0]["close"] += 0.0001
    p2 = tmp_path / "b.json"; p2.write_text(json.dumps(d), encoding="utf-8")
    r1 = run_inference(p1, tmp_path / "o1")
    r2 = run_inference(p2, tmp_path / "o2")
    assert r1["manifest"]["input_bytes_hash"] != r2["manifest"]["input_bytes_hash"]
    assert r1["predictions_hash"] != r2["predictions_hash"]


def test_one_bit_prediction_change_blocks_scorer(tmp_path: Path) -> None:
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=30)
    result = run_inference(inp, tmp_path / "out")
    pred_path = result["predictions_path"]
    os.chmod(pred_path, stat.S_IWRITE | stat.S_IREAD)
    raw = bytearray(pred_path.read_bytes())
    raw[50] = (raw[50] + 1) % 256
    pred_path.write_bytes(bytes(raw))
    with pytest.raises(ScoringRefusedError) as exc_info:
        load_frozen_predictions(tmp_path / "out")
    assert exc_info.value.code == "TAMPER_DETECTED"


def test_missing_predictions_refused(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(ScoringRefusedError) as exc_info:
        load_frozen_predictions(empty_dir)
    assert exc_info.value.code == "MISSING_PREDICTIONS"


def test_two_processes_no_shared_state(tmp_path: Path) -> None:
    """Rulează inference de două ori, în directoare complet separate, cu bare identice dar
    ferestre cu ID-uri diferite -- rezultatul per-bară trebuie identic (nicio stare globală
    scursă între "procese")."""
    d1 = make_dev_input(n_windows=1, bars_per_window=40)
    d1["windows"][0]["window_id"] = "PROC-A"
    d2 = make_dev_input(n_windows=1, bars_per_window=40)
    d2["windows"][0]["window_id"] = "PROC-B"
    p1 = tmp_path / "p1.json"; p1.write_text(json.dumps(d1), encoding="utf-8")
    p2 = tmp_path / "p2.json"; p2.write_text(json.dumps(d2), encoding="utf-8")
    r1 = run_inference(p1, tmp_path / "o1")
    r2 = run_inference(p2, tmp_path / "o2")
    preds1 = json.loads(r1["predictions_path"].read_text(encoding="utf-8"))
    preds2 = json.loads(r2["predictions_path"].read_text(encoding="utf-8"))
    recs1 = preds1["windows"][0]["records"]
    recs2 = preds2["windows"][0]["records"]
    for a, b in zip(recs1, recs2):
        assert a["macro"] == b["macro"]
        assert a["internal"] == b["internal"]


def test_python_version_documented() -> None:
    """Mandat §10: versiunea Python suportată e documentată -- verificată direct din pyproject.toml
    (`requires-python`), nu doar afirmată în proză."""
    pyproject = (Path(__file__).resolve().parent.parent.parent / "pyproject.toml").read_text(encoding="utf-8")
    assert "requires-python" in pyproject


def test_chunk_invariance_bar_by_bar_matches_single_batch() -> None:
    """Mandat §11 item 14 -- aceeași intrare în chunk-uri diferite -> rezultat semantic identic.
    Exercitat prin exact tiparul de utilizare al lui `inference.py` (motor nou per fereastră,
    `Bar` real), nu doar prin API-ul intern al detectorului (deja acoperit exhaustiv în
    `tests/test_range_semantic_v4_3.py` -- aici se verifică DOAR că runnerul îl folosește corect)."""
    import sys as _s
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from ve_n1_replay import Bar
    from ve_n1_replay.range_semantic_v4_3 import ConfigV43
    from ve_n1_replay.range_engine_v4_3 import RangeSemanticEngineV43
    from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT

    raw_bars = make_dev_input(n_windows=1, bars_per_window=80)["windows"][0]["bars"]
    bars = [Bar(symbol="XAUUSD", ts_open=b["ts_open"], ts_close=b["ts_close"], open=b["open"],
               high=b["high"], low=b["low"], close=b["close"], volume=b["volume"],
               is_backfilled=b["is_backfilled"]) for b in raw_bars]

    def _new_engine() -> "RangeSemanticEngineV43":
        return RangeSemanticEngineV43(
            symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
            implementation_commit=RAW_AXES_BUILDER_IMPL_COMMIT,
            range_config=ConfigV43(), acknowledge_construction_only=True)

    single = _new_engine()
    single_results = [single.observe_closed_bar(b)[1] for b in bars]

    chunked = _new_engine()
    split = 37
    chunked_results = [chunked.observe_closed_bar(b)[1] for b in bars[:split]]
    snap = chunked.snapshot()
    restored = _new_engine()
    restored.restore(snap)
    chunked_results += [restored.observe_closed_bar(b)[1] for b in bars[split:]]

    for i, (a, b) in enumerate(zip(single_results, chunked_results)):
        assert a.macro_id == b.macro_id, f"bar {i}: macro_id diferă între rulare unică și chunk-uită"
        assert a.macro_reason == b.macro_reason, f"bar {i}: macro_reason diferă"
        assert a.macro_boundary_upper == b.macro_boundary_upper
        assert a.internal_id == b.internal_id


def test_snapshot_restart_mid_window_identical_continuation() -> None:
    """Mandat §11 item 15 -- snapshot/restart produce continuare identică (caz separat de chunk
    invariance: aici verificăm explicit că `restore()` pe un motor PROASPĂT, nu doar pe cel
    original, reproduce exact starea)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from ve_n1_replay import Bar
    from ve_n1_replay.range_semantic_v4_3 import ConfigV43
    from ve_n1_replay.range_engine_v4_3 import RangeSemanticEngineV43
    from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT

    raw_bars = make_dev_input(n_windows=1, bars_per_window=60)["windows"][0]["bars"]
    bars = [Bar(symbol="XAUUSD", ts_open=b["ts_open"], ts_close=b["ts_close"], open=b["open"],
               high=b["high"], low=b["low"], close=b["close"], volume=b["volume"],
               is_backfilled=b["is_backfilled"]) for b in raw_bars]

    def _new_engine() -> "RangeSemanticEngineV43":
        return RangeSemanticEngineV43(
            symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
            implementation_commit=RAW_AXES_BUILDER_IMPL_COMMIT,
            range_config=ConfigV43(), acknowledge_construction_only=True)

    engine_a = _new_engine()
    for b in bars[:33]:
        engine_a.observe_closed_bar(b)
    snap = engine_a.snapshot()

    engine_b = _new_engine()   # motor complet NOU, nu cel care a produs snapshot-ul
    engine_b.restore(snap)

    res_a = [engine_a.observe_closed_bar(b)[1] for b in bars[33:]]
    res_b = [engine_b.observe_closed_bar(b)[1] for b in bars[33:]]
    for ra, rb in zip(res_a, res_b):
        assert ra.macro_id == rb.macro_id
        assert ra.macro_boundary_upper == rb.macro_boundary_upper
        assert ra.internal_state == rb.internal_state


def test_dev_fixtures_reference_no_sealed_or_escrow_paths() -> None:
    """Mandat §11 item 24 -- zero acces SEALED/OOS în testele de dezvoltare, verificat structural."""
    import ast
    src_path = Path(__file__).resolve().parent.parent / "dev_fixtures.py"
    tree = ast.parse(src_path.read_text(encoding="utf-8"))
    forbidden = ("SEALED", "escrow", "OOS", "BLIND-0", "statistician")
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for f in forbidden:
                assert f not in node.value, f"dev_fixtures.py conține literalul suspect {f!r}"
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not (imported & {"construction_reproduction", "parse_windows", "synth"}), (
        "dev_fixtures.py nu trebuie să depindă de componenta A (izolare completă)"
    )


def test_config_mismatch_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inp = _write_input(tmp_path, n_windows=1, bars_per_window=20)
    result = run_inference(inp, tmp_path / "out")
    pred_path = result["predictions_path"]
    os.chmod(pred_path, stat.S_IWRITE | stat.S_IREAD)
    data = json.loads(pred_path.read_text(encoding="utf-8"))
    data["config_id"] = "0" * 64
    new_bytes = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
    pred_path.write_bytes(new_bytes)
    (tmp_path / "out" / "predictions.sha256").write_text(
        f"{hashlib.sha256(new_bytes).hexdigest()}  predictions.json\n", encoding="utf-8")
    with pytest.raises(ScoringRefusedError) as exc_info:
        load_frozen_predictions(tmp_path / "out")
    assert exc_info.value.code == "CONFIG_MISMATCH"
