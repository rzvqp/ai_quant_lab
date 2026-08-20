"""Etapa 1 — INFERENCE. Bare reale -> detector înghețat (`f224e7d`) -> predicții brute -> hash și
sigilare.

**Acest modul NU importă și nu poate primi**: etichete CEO, mapping MACRO/INTERNAL, intervale de
segmente, fișiere de scoring, output PnL. Verificat structural de
`tests/test_anti_leakage_ast.py` (parsare `ast`, nu doar convenție).

Nu modifică detectorul (`ve_n1_replay.range_semantic_v4_3`/`range_engine_v4_3`, NESCHIMBATE, importate
ca-atare) și verifică fail-closed, înainte de orice rulare, că fișierele lor sunt byte-identice cu
prototipul înghețat `f224e7d`."""
from __future__ import annotations

import dataclasses as dc
import hashlib
import json
import os
import stat
import sys
import time
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

# Baza istorică rămâne `f224e7d` (RT-RANGE-0007/0010/0011). `69af414` a livrat F1+F5 -- Red Team
# (RT-RANGE-0012, `892355f`/E87) a găsit F5 material-defect (MACRO leak pe bare reale, 62/88->58/88) și
# CEO a ales remedierea (b): F1 SINGUR, F5 amânat complet (DEFERRED_RESEARCH_ONLY_NON_BLOCKING). Acest
# fișier reflectă acum implementarea F1-only: `range_semantic_v4_3.py` e revenit byte-comportamental la
# forma pre-F5 (linia de gard rămâne NESCALATĂ prin ATR), dar NU byte-identic cu `f224e7d` la nivel de
# fișier (infrastructura de fingerprint rămâne, deliberat nereverta -- v. comentariul din
# `range_semantic_v4_3.py`). `range_engine_v4_3.py` rămâne NEATINS (verificat separat mai jos, hash
# identic cu f224e7d pe tot parcursul). `FROZEN_HASHES`/`FROZEN_IMPLEMENTATION_FINGERPRINT` actualizate
# la amprenta post-remediere (calculată DUPĂ finalizare+testare, nu invers).
FROZEN_PROTOTYPE_COMMIT = "f224e7d+F1"
FROZEN_HASHES = {
    "range_semantic_v4_3.py": "098fa1445521e5183ab5ddd94caac88fe010159ee283f2f33eca22f701241fbc",
    "range_engine_v4_3.py": "84dac346524591fdfe904cd0dde0f1d8888161cdffe62dcd7129cff6eea1c1f2",
}
FROZEN_CONFIG_ID = "24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da"
FROZEN_IMPLEMENTATION_FINGERPRINT = "f1-only-f5-deferred-2026-08-20"


def _verify_frozen_detector() -> None:
    ve_dir = _HERE.parent / "ve_n1_replay"
    for fname, expected in FROZEN_HASHES.items():
        actual = hashlib.sha256((ve_dir / fname).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(
                f"FAIL-CLOSED: {fname} nu e byte-identic cu implementarea înghețată "
                f"{FROZEN_PROTOTYPE_COMMIT}. Așteptat {expected}, găsit {actual}. Oprire -- inference nu "
                f"rulează pe un detector modificat/nepatch-uit."
            )


_verify_frozen_detector()

from schemas import InputValidationError, InputWindow, validate_and_normalize_input  # noqa: E402
from ve_n1_replay import Bar  # noqa: E402
from ve_n1_replay.range_semantic_v4_3 import (  # noqa: E402
    RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT as IMPLEMENTATION_FINGERPRINT, ConfigV43,
)
from ve_n1_replay.range_engine_v4_3 import RangeSemanticEngineV43  # noqa: E402
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT  # noqa: E402

if ConfigV43().config_id() != FROZEN_CONFIG_ID:
    raise RuntimeError("FAIL-CLOSED: config_id runtime diferit de cel înghețat -- oprire.")
if IMPLEMENTATION_FINGERPRINT != FROZEN_IMPLEMENTATION_FINGERPRINT:
    raise RuntimeError("FAIL-CLOSED: implementation_fingerprint runtime diferit de cel înghețat -- oprire.")


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(p: Path) -> str:
    return _sha256_bytes(p.read_bytes())


def _run_one_window(window: InputWindow) -> dict[str, Any]:
    """O instanță de motor NOUĂ per fereastră -- nicio stare comună între ferestre (mandat §10)."""
    cfg = ConfigV43()
    engine = RangeSemanticEngineV43(
        symbol=window.symbol, timeframe=window.timeframe,
        bar_interval_seconds=window.bar_interval_seconds,
        implementation_commit=RAW_AXES_BUILDER_IMPL_COMMIT,
        range_config=cfg, acknowledge_construction_only=True)
    bars = tuple(
        Bar(symbol=window.symbol, ts_open=b.ts_open, ts_close=b.ts_close, open=b.open, high=b.high,
           low=b.low, close=b.close, volume=b.volume, is_backfilled=b.is_backfilled)
        for b in window.bars
    )
    ledger = engine.replay_batch(bars)

    records = []
    for rec in ledger.records:
        events = [
            {"kind": e["kind"], "depth": e["depth"], "applies_to_structure_id": e["structure_id"],
             "reason_codes": list(e["reason_codes"])}
            for e in rec.events
        ]
        records.append({
            "bar_index": rec.bar_index,   # index RELATIV in fereastra, NU ts_close real
            "macro": {
                "structure_id": rec.macro_id, "state": rec.macro_state, "reason": rec.macro_reason,
                "boundary_upper": rec.macro_boundary_upper, "boundary_lower": rec.macro_boundary_lower,
                "confirm_ts": rec.macro_confirm_ts,   # deja index de bara relativ (identitate producator)
                "role": rec.macro_role,
            },
            "internal": {
                "structure_id": rec.internal_id, "state": rec.internal_state, "reason": rec.internal_reason,
                "boundary_upper": rec.internal_boundary_upper, "boundary_lower": rec.internal_boundary_lower,
                "role": rec.internal_role,
            },
            "regime": rec.regime,
            "events": events,
        })

    def _median(members: list[float]) -> float | None:
        if not members:
            return None
        import statistics
        return statistics.median(members)

    def _structure_dict(s: dict[str, Any]) -> dict[str, Any]:
        # `boundary_upper`/`boundary_lower` nu sunt câmpuri stocate în `Structure.snapshot()` (sunt
        # @property calculate pe obiectul viu din `up.center`/`dn.center`) -- recalculate aici cu
        # `statistics.median` pe `up_members`/`dn_members`, deja incluse în snapshot: aceeași valoare
        # matematică, nu o aproximare (mediana e o funcție bine-definită, indiferent de algoritmul
        # O(log m) al `_RunningMedian` folosit pe calea fierbinte a detectorului vs. `statistics.median`
        # folosit aici -- niciun recalcul de LIMITĂ contractuală, doar citirea aceleiași valori).
        return {"structure_id": s["structure_id"], "depth": "MACRO" if s["depth"] == 0 else "INTERNAL",
               "parent_structure_id": s["parent_structure_id"], "start_ts": s["start_ts"],
               "confirm_ts": s["confirm_ts"], "end_ts": s["end_ts"], "end_reason": s["end_reason"],
               "boundary_upper": _median(s["up_members"]), "boundary_lower": _median(s["dn_members"]),
               "role": s["role"], "role_known_ts": s["role_known_ts"], "predecessor_id": s["predecessor_id"]}

    def _structures(history: tuple[dict[str, Any], ...], active: Any) -> list[dict[str, Any]]:
        # `history` (macro_history/internal_history) conține DOAR structurile ÎNCHISE -- cea încă
        # activă la finalul ferestrei (cazul obișnuit: range-ul nu apucă să spargă înainte de capăt)
        # nu e niciodată mutată acolo. Găsit prin exercitarea directă cu un fixture de dezvoltare
        # (macro_structures ieșea gol deși OK_RANGE_MACRO se confirmase clar în records) -- accesul la
        # `engine._range._active_macro`/`_active_internal` (privat) e singura cale, fiindcă motorul
        # nu expune public o structură încă-deschisă (nu se modifică detectorul pt. a adăuga una).
        out = [_structure_dict(s) for s in history]
        if active is not None:
            out.append(_structure_dict(active.snapshot()))
        return out

    return {
        "window_id": window.window_id, "n_bars": len(window.bars),
        "records": records,
        "macro_structures": _structures(ledger.macro_history, engine._range._active_macro),
        "internal_structures": _structures(ledger.internal_history, engine._range._active_internal),
        "run_hash": ledger.run_hash,
    }


def run_inference(input_path: Path, output_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    input_bytes = input_path.read_bytes()
    input_bytes_hash = _sha256_bytes(input_bytes)
    try:
        raw = json.loads(input_bytes)
    except json.JSONDecodeError as exc:
        raise InputValidationError("CORRUPT_FILE", f"input nu e JSON valid: {exc}") from exc

    windows, quality_events = validate_and_normalize_input(raw)

    # hash-ul barelor NORMALIZATE (dupa validare, nu bytes-ul brut) -- schimbarea unui singur bit
    # in orice bara normalizata schimba acest hash (mandat §10).
    normalized_repr = json.dumps(
        [
            {"window_id": w.window_id, "symbol": w.symbol, "timeframe": w.timeframe,
             "bar_interval_seconds": w.bar_interval_seconds,
             "bars": [dc.asdict(b) for b in w.bars]}
            for w in windows
        ],
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    normalized_bars_hash = _sha256_bytes(normalized_repr)

    window_outputs = [_run_one_window(w) for w in windows]

    # F1 (mandat §4.4): evenimentele de calitate a inputului -- infrastructură, NU reason codes
    # semantice RANGE (v. verificarea mecanică în tests/test_f1_ohlc_tolerance.py). `bar_index` e deja
    # relativ (schemas.py), deci sigur de inclus în output-ul pt. evaluare -- zero timestamp real.
    input_quality_events = [dc.asdict(ev) for ev in quality_events]

    total_bars = sum(w["n_bars"] for w in window_outputs)
    predictions: dict[str, Any] = {
        "prototype_commit": FROZEN_PROTOTYPE_COMMIT,
        "contract_version": "range-hierarchical-v4.3",
        "config_id": FROZEN_CONFIG_ID,
        "code_fingerprint": dict(FROZEN_HASHES),
        "config_fingerprint": FROZEN_CONFIG_ID,
        "implementation_fingerprint": FROZEN_IMPLEMENTATION_FINGERPRINT,
        "input_bytes_hash": input_bytes_hash,
        "normalized_bars_hash": normalized_bars_hash,
        "n_windows": len(window_outputs),
        "n_bars_total": total_bars,
        "windows": window_outputs,
        "input_quality_events": input_quality_events,
        "snapshot_restore_markers": [],   # rulare completa, fara fragmentare -- gol dar prezent
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = output_dir / "predictions.json"
    predictions_bytes = json.dumps(predictions, indent=2, sort_keys=True).encode("utf-8")
    predictions_path.write_bytes(predictions_bytes)
    predictions_hash = _sha256_bytes(predictions_bytes)

    manifest = {
        "prototype_commit": FROZEN_PROTOTYPE_COMMIT,
        "config_id": FROZEN_CONFIG_ID,
        "input_bytes_hash": input_bytes_hash,
        "output_hash": predictions_hash,
        "n_windows": len(window_outputs),
        "n_bars_total": total_bars,
        "run_time_seconds": round(time.time() - t0, 6),
        "exit_status": "ok",
        "runner": "blind_runner.inference",
        "zero_labels_access": True,
        "zero_sealed_access_in_dev_tests": True,
        "python_version": sys.version.split()[0],
        "f1_bars_tolerated": len(input_quality_events),
        "implementation_fingerprint": IMPLEMENTATION_FINGERPRINT,
    }
    manifest_path = output_dir / "predictions.manifest.json"
    manifest_path.write_bytes(json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8"))

    sha_path = output_dir / "predictions.sha256"
    sha_path.write_text(f"{predictions_hash}  predictions.json\n", encoding="utf-8")

    # predicțiile devin read-only dupa emiterea hash-ului (mandat §7) -- best-effort cross-platform
    try:
        os.chmod(predictions_path, stat.S_IREAD)
    except OSError:
        pass

    return {"predictions_path": predictions_path, "manifest_path": manifest_path,
           "sha_path": sha_path, "predictions_hash": predictions_hash, "manifest": manifest}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Etapa 1: inference pe bare reale (fara labels)")
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    try:
        result = run_inference(args.input, args.output_dir)
    except InputValidationError as exc:
        print(f"REFUZAT (fail-closed): {exc}", file=sys.stderr)
        sys.exit(2)
    print(f"predictions: {result['predictions_path']}")
    print(f"hash: {result['predictions_hash']}")
    print(f"manifest: {result['manifest']}")
