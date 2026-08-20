"""Etapa 2 — SCORING. Predicții deja înghețate + etichete -> metrici.

**Acest modul NU importă detectorul** (`ve_n1_replay.range_semantic_v4_3`/`range_engine_v4_3` NU
apar nicăieri în acest fișier -- verificat structural de `tests/test_anti_leakage_ast.py`), nu
poate re-rula inference-ul, nu modifică predicțiile, nu recalculează limitele, nu modifică
configurația, nu selectează ferestre după rezultate.

Refuză fail-closed orice fișier de predicții al cărui hash nu se potrivește cu
`predictions.sha256` -- un singur bit modificat blochează scorarea (mandat §7/§10)."""
from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Any


class ScoringRefusedError(Exception):
    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        super().__init__(f"{code}: {detail}")


def load_frozen_predictions(predictions_dir: Path) -> dict[str, Any]:
    """Verifică hash-ul ÎNAINTE de a interpreta conținutul -- orice nepotrivire refuză fail-closed,
    nu doar avertizează."""
    pred_path = predictions_dir / "predictions.json"
    sha_path = predictions_dir / "predictions.sha256"
    if not pred_path.exists() or not sha_path.exists():
        raise ScoringRefusedError("MISSING_PREDICTIONS", f"lipsesc predictions.json/.sha256 din {predictions_dir}")
    raw_bytes = pred_path.read_bytes()
    actual_hash = hashlib.sha256(raw_bytes).hexdigest()
    declared_line = sha_path.read_text(encoding="utf-8").strip().split()[0]
    if actual_hash != declared_line:
        raise ScoringRefusedError(
            "TAMPER_DETECTED",
            f"hash-ul predictions.json ({actual_hash}) nu se potrivește cu predictions.sha256 "
            f"({declared_line}) -- predicțiile au fost modificate după sigilare, refuz să scorez."
        )
    predictions: dict[str, Any] = json.loads(raw_bytes)
    if predictions.get("config_id") != "24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da":
        raise ScoringRefusedError("CONFIG_MISMATCH", f"config_id neașteptat: {predictions.get('config_id')}")
    if predictions.get("prototype_commit") != "f224e7d+F1":
        raise ScoringRefusedError("COMMIT_MISMATCH", f"prototype_commit neașteptat: {predictions.get('prototype_commit')}")
    if predictions.get("implementation_fingerprint") != "f1-only-f5-deferred-2026-08-20":
        raise ScoringRefusedError(
            "IMPLEMENTATION_FINGERPRINT_MISMATCH",
            f"implementation_fingerprint neașteptat: {predictions.get('implementation_fingerprint')}")
    return predictions


def _iou(a: tuple[int, int], b: tuple[int, int]) -> float:
    s = max(a[0], b[0]); e = min(a[1], b[1])
    inter = max(0, e - s)
    union = (a[1] - a[0]) + (b[1] - b[0]) - inter
    return inter / union if union > 0 else 0.0


def _pct(vals: list[float], p: float) -> float | None:
    if not vals:
        return None
    s = sorted(vals)
    k = (len(s) - 1) * p
    f, c = int(k), min(int(k) + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def _confirmed_structures(window_pred: dict[str, Any], depth: str) -> list[dict[str, Any]]:
    key = "macro_structures" if depth == "MACRO" else "internal_structures"
    return [s for s in window_pred[key] if s["confirm_ts"] is not None]


def _match_segments(gt_segments: list[dict[str, Any]], detected: list[dict[str, Any]],
                    window_n_bars: dict[str, int]) -> list[dict[str, Any]]:
    matches = []
    for g in gt_segments:
        g_span = (g["start"], g["end"])
        best_iou, best_d = 0.0, None
        for d in detected:
            # o structură ÎNCĂ deschisă (end_ts=None) se întinde până la finalul observat al
            # ferestrei, NU are lungime zero -- găsit+corectat (folosirea lui start_ts ca fallback
            # pt. end producea IoU=0 garantat pt. orice structură confirmată dar niciodată închisă
            # înainte de capătul ferestrei, cazul cel mai OBIȘNUIT, nu unul marginal).
            d_end = d["end_ts"] if d["end_ts"] is not None else window_n_bars.get(g["window_id"], d["start_ts"])
            d_span = (d["start_ts"], d_end)
            v = _iou(g_span, d_span)
            if v > best_iou:
                best_iou, best_d = v, d
        confirm_delay = (best_d["confirm_ts"] - best_d["start_ts"]) if best_d else None
        boundary_err_atr = None
        if best_d is not None and g.get("boundary_upper") is not None and g.get("atr_ref"):
            errs = []
            if best_d.get("boundary_upper") is not None:
                errs.append(abs(best_d["boundary_upper"] - g["boundary_upper"]) / g["atr_ref"])
            if best_d.get("boundary_lower") is not None and g.get("boundary_lower") is not None:
                errs.append(abs(best_d["boundary_lower"] - g["boundary_lower"]) / g["atr_ref"])
            if errs:
                boundary_err_atr = sum(errs) / len(errs)
        matches.append({
            "window_id": g["window_id"], "gt": g_span, "best_iou": best_iou,
            "det": (best_d["start_ts"], best_d["end_ts"]) if best_d else None,
            "confirm_delay": confirm_delay, "boundary_err_atr": boundary_err_atr,
        })
    return matches


def score(predictions: dict[str, Any], labels: dict[str, Any]) -> dict[str, Any]:
    """`labels`: {"segments": [{"window_id","level"("MACRO"/"INTERNAL"/"UNRESOLVED"),"start","end",
    "window_bars","block", "boundary_upper"?,"boundary_lower"?,"atr_ref"?}, ...]}."""
    pred_by_window = {w["window_id"]: w for w in predictions["windows"]}
    macro_gt = [s for s in labels["segments"] if s["level"] == "MACRO"]
    internal_gt = [s for s in labels["segments"] if s["level"] == "INTERNAL"]
    unresolved_gt = [s for s in labels["segments"] if s["level"] == "UNRESOLVED"]

    n_windows = len(pred_by_window)
    n_bars_total = sum(w["n_bars"] for w in pred_by_window.values())
    window_n_bars = {wid: w["n_bars"] for wid, w in pred_by_window.items()}

    macro_matches: list[dict[str, Any]] = []
    internal_matches: list[dict[str, Any]] = []
    for gt_list, out_list, depth in ((macro_gt, macro_matches, "MACRO"), (internal_gt, internal_matches, "INTERNAL")):
        by_window: dict[str, list[dict[str, Any]]] = {}
        for g in gt_list:
            by_window.setdefault(g["window_id"], []).append(g)
        for wid, segs in by_window.items():
            wp = pred_by_window.get(wid)
            detected = _confirmed_structures(wp, depth) if wp is not None else []
            out_list.extend(_match_segments(segs, detected, window_n_bars))

    def _recall_precision(matches: list[dict[str, Any]], gt_count: int, det_count: int) -> dict[str, Any]:
        matched = [m for m in matches if m["best_iou"] > 0]
        ious = [m["best_iou"] for m in matched]
        delays = [m["confirm_delay"] for m in matched if m["confirm_delay"] is not None]
        b_errs = [m["boundary_err_atr"] for m in matched if m["boundary_err_atr"] is not None]
        return {
            "gt_count": gt_count, "matched_count": len(matched), "detected_count": det_count,
            "recall": len(matched) / gt_count if gt_count else None,
            "precision": len(matched) / det_count if det_count else None,
            "iou_p25": _pct(ious, 0.25), "iou_median": _pct(ious, 0.50), "iou_p75": _pct(ious, 0.75),
            "iou_max": max(ious) if ious else None,
            "confirm_delay_mean": statistics.mean(delays) if delays else None,
            "confirm_delay_median": _pct([float(d) for d in delays], 0.5) if delays else None,
            "boundary_error_atr_mean": statistics.mean(b_errs) if b_errs else None,
            "missed_segments": [m["gt"] for m in matches if m["best_iou"] == 0],
        }

    macro_det_count = sum(len(_confirmed_structures(w, "MACRO")) for w in pred_by_window.values())
    internal_det_count = sum(len(_confirmed_structures(w, "INTERNAL")) for w in pred_by_window.values())
    macro_scores = _recall_precision(macro_matches, len(macro_gt), macro_det_count)
    internal_scores = _recall_precision(internal_matches, len(internal_gt), internal_det_count)

    # false positives = structuri detectate care nu au potrivit NICIUN GT (best_iou>0 pt. ORICE gt)
    matched_det_spans = {(m["window_id"], m["det"]) for m in macro_matches if m["best_iou"] > 0 and m["det"]}
    false_positives_macro = macro_det_count - len(matched_det_spans)

    event_kind_counts: dict[str, int] = {}
    reason_code_counts: dict[str, int] = {}
    macro_state_counts: dict[str, int] = {}
    internal_state_counts: dict[str, int] = {}
    for w in pred_by_window.values():
        for rec in w["records"]:
            macro_state_counts[str(rec["macro"]["state"])] = macro_state_counts.get(str(rec["macro"]["state"]), 0) + 1
            internal_state_counts[str(rec["internal"]["state"])] = (
                internal_state_counts.get(str(rec["internal"]["state"]), 0) + 1)
            reason_code_counts[rec["macro"]["reason"]] = reason_code_counts.get(rec["macro"]["reason"], 0) + 1
            if rec["internal"]["reason"]:
                reason_code_counts[rec["internal"]["reason"]] = reason_code_counts.get(rec["internal"]["reason"], 0) + 1
            for ev in rec["events"]:
                event_kind_counts[ev["kind"]] = event_kind_counts.get(ev["kind"], 0) + 1

    n_refused = (event_kind_counts.get("PARTIAL_OVERLAP_NO_CONTAINMENT", 0)
                + event_kind_counts.get("DEPTH_LIMIT_EXCEEDED", 0)
                + event_kind_counts.get("LEVEL_ASSIGNMENT_UNRESOLVED", 0))
    funnel = {
        "total_attempts": macro_det_count + internal_det_count + n_refused,
        "macro_new": macro_det_count, "internal_new": internal_det_count,
        "refused_partial_overlap": event_kind_counts.get("PARTIAL_OVERLAP_NO_CONTAINMENT", 0),
        "refused_depth_limit": event_kind_counts.get("DEPTH_LIMIT_EXCEEDED", 0),
        "refused_unresolved": event_kind_counts.get("LEVEL_ASSIGNMENT_UNRESOLVED", 0),
    }

    by_length: dict[int, dict[str, int]] = {}
    by_block: dict[str, dict[str, int]] = {}
    length_of = {s["window_id"]: s["window_bars"] for s in labels["segments"]}
    block_of = {s["window_id"]: s.get("block") for s in labels["segments"]}
    for m in macro_matches:
        wb = length_of.get(m["window_id"])
        blk = block_of.get(m["window_id"])
        if wb is not None:
            by_length.setdefault(wb, {"matched": 0, "total": 0})
            by_length[wb]["total"] += 1
            if m["best_iou"] > 0:
                by_length[wb]["matched"] += 1
        if blk is not None:
            by_block.setdefault(blk, {"matched": 0, "total": 0})
            by_block[blk]["total"] += 1
            if m["best_iou"] > 0:
                by_block[blk]["matched"] += 1

    return {
        "population": {"n_windows": n_windows, "n_bars_total": n_bars_total,
                       "macro_gt": len(macro_gt), "internal_gt": len(internal_gt),
                       "unresolved_gt": len(unresolved_gt),
                       "macro_plus_unresolved": len(macro_gt) + len(unresolved_gt)},
        "macro": macro_scores, "internal": internal_scores,
        "false_positives_macro": false_positives_macro,
        "events": {
            "sweep_confirmed": event_kind_counts.get("SWEEP_CONFIRMED", 0),
            "breakout_accepted": event_kind_counts.get("BREAKOUT_ACCEPTED", 0),
            "liquidity_sweep_reversal": event_kind_counts.get("LIQUIDITY_SWEEP_REVERSAL", 0),
            "promotions": event_kind_counts.get("IS_TREND_MACRO", 0),
        },
        "event_kind_counts": event_kind_counts, "reason_code_counts": reason_code_counts,
        "macro_state_counts": macro_state_counts, "internal_state_counts": internal_state_counts,
        "by_length": by_length, "by_block": by_block, "funnel": funnel,
        "unresolved_note": "cele 26 UNRESOLVED (in lotul de 48 ferestre) sunt raportate separat, "
                           "niciodata introduse in denominatorul recall MACRO",
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Etapa 2: scoring pe predicții deja sigilate")
    ap.add_argument("--predictions-dir", required=True, type=Path)
    ap.add_argument("--labels", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    try:
        preds = load_frozen_predictions(args.predictions_dir)
    except ScoringRefusedError as exc:
        import sys
        print(f"REFUZAT (fail-closed): {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    labels_data = json.loads(args.labels.read_text(encoding="utf-8"))
    result = score(preds, labels_data)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {args.out}")
    print(json.dumps({"macro_recall": result["macro"]["recall"],
                      "internal_recall": result["internal"]["recall"]}, indent=2))
