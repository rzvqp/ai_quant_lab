"""
CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY
CIRCULAR_LABEL_DERIVED_BARS
ZERO_VALIDATION_WEIGHT

Reproduce EXACT logica folosita pt. rularea de construcție deja raportată în
`RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md` (prototip înghețat `f224e7d`) -- comisă acum
pentru prima dată (Red Team RT-RANGE-0007 §16: rezultatele nu erau reproductibile fiindcă acest
fișier și `synth.py` trăiau doar local, necomise).

Nu modifică detectorul. Importă `ve_n1_replay.range_semantic_v4_3`/`range_engine_v4_3` NESCHIMBATE
și verifică explicit, înainte de orice rulare, că fișierele importate sunt byte-identice cu
fingerprint-urile citate în `f224e7d` -- dacă cineva a modificat detectorul de atunci, acest
script REFUZĂ să ruleze (fail-closed), nu produce tăcut numere dintr-un cod diferit.

Rulare: `python -m ve_n1_replay.construction_reproduction.run_construction` din `ve_n1_replay/`.
Scrie `construction_run_results.json` în acest director și verifică reproducerea cifrelor VE deja
raportate (§9 mandat) -- emite `HISTORICAL_SYNTHETIC_RESULT_REPRODUCED`/`ZERO_VALIDATION_WEIGHT`
sau `HISTORICAL_SYNTHETIC_RESULT_NOT_REPRODUCED`.
"""
from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))

from parse_windows import load_all_windows, normalized, parse_level_mapping  # noqa: E402
from synth import synthesize_window  # noqa: E402

# fingerprint-urile citate in RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md / RT-RANGE-0007, la
# commit-ul inghetat f224e7d -- verificate INAINTE de orice import al detectorului.
FROZEN_PROTOTYPE_COMMIT = "f224e7d"
FROZEN_HASHES = {
    "range_semantic_v4_3.py": "2aba333c413c484f8ff85c91180e29f852834475d982ab4f4a5c32120ccb238b",
    "range_engine_v4_3.py": "84dac346524591fdfe904cd0dde0f1d8888161cdffe62dcd7129cff6eea1c1f2",
}
FROZEN_CONFIG_ID = "24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da"

# cifrele VE deja raportate (RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md §7) -- toleranta stricta,
# nu se rotunjeste in avantajul reproducerii.
REPORTED = {
    "macro_matched": 57, "macro_gt": 88, "internal_matched": 2, "internal_gt": 12,
    "sweep_confirmed": 209, "breakout_accepted": 112, "liquidity_sweep_reversal": 21,
    "promo_count": 94, "funnel_total": 725, "funnel_macro_new": 151, "funnel_internal_new": 16,
    "funnel_partial_overlap": 558,
}


def _verify_frozen_detector() -> None:
    ve_n1_replay_dir = _HERE.parent / "ve_n1_replay"
    for fname, expected in FROZEN_HASHES.items():
        p = ve_n1_replay_dir / fname
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(
                f"FAIL-CLOSED: {fname} nu e byte-identic cu prototipul înghețat {FROZEN_PROTOTYPE_COMMIT}. "
                f"Așteptat {expected}, găsit {actual}. Acest mandat NU autorizează rularea pe un detector "
                f"modificat -- oprire."
            )


_verify_frozen_detector()

from ve_n1_replay.range_semantic_v4_3 import ConfigV43, RangeSemanticProducerV43  # noqa: E402

_cfg_check = ConfigV43()
if _cfg_check.config_id() != FROZEN_CONFIG_ID:
    raise RuntimeError(
        f"FAIL-CLOSED: config_id runtime ({_cfg_check.config_id()}) diferit de cel înghețat "
        f"({FROZEN_CONFIG_ID}) -- oprire."
    )


def iou(a: tuple[int, int], b: tuple[int, int]) -> float:
    s = max(a[0], b[0]); e = min(a[1], b[1])
    inter = max(0, e - s)
    union = (a[1] - a[0]) + (b[1] - b[0]) - inter
    return inter / union if union > 0 else 0.0


def run_all() -> dict[str, Any]:
    windows = load_all_windows()
    norm = normalized(windows)
    level_rows = parse_level_mapping()
    gt_by_window = collections.defaultdict(list)
    block_of = {}
    for r in level_rows:
        gt_by_window[r["blind"]].append(r)
        block_of[r["blind"]] = r["block"]

    per_window: dict[str, Any] = {}
    reason_code_counts: collections.Counter[str] = collections.Counter()
    event_kind_counts: collections.Counter[str] = collections.Counter()
    macro_state_bar_counts: collections.Counter[str | None] = collections.Counter()
    internal_state_bar_counts: collections.Counter[str | None] = collections.Counter()

    for wid, (wb, spans, env) in norm.items():
        bars = synthesize_window(wb, spans, macro_envelope=env)
        assert len(bars) == wb, f"{wid}: got {len(bars)} bars, expected {wb}"
        assert [b[0] for b in bars] == list(range(wb)), f"{wid}: bar index misalignment"

        cfg = ConfigV43()
        prod = RangeSemanticProducerV43(cfg)
        events_log = []
        final_res = None
        for idx, o, h, lo, c in bars:
            res, evs = prod.observe(ts_close=idx * 900, open_=o, high=h, low=lo, close=c, atr=1.0)
            final_res = res
            macro_state_bar_counts[res.macro_state] += 1
            internal_state_bar_counts[res.internal_state] += 1
            for e in evs:
                events_log.append({"bar": idx, "kind": e.kind, "depth": e.depth, "sid": e.structure_id})
                event_kind_counts[e.kind] += 1
        assert final_res is not None

        detected_macro = [
            {"start": h["start_ts"], "end": h["end_ts"], "confirmed": h["reached_confirmed"],
             "reason": h["end_reason"], "confirm_ts": h["confirm_ts"]}
            for h in prod.macro_history
        ]
        if prod._active_macro is not None:
            am = prod._active_macro
            detected_macro.append({"start": am.start_ts, "end": wb, "confirmed": am.reached_confirmed,
                                   "reason": None, "confirm_ts": am.confirm_ts})
        detected_internal = [
            {"start": h["start_ts"], "end": h["end_ts"], "confirmed": h["reached_confirmed"],
             "reason": h["end_reason"], "confirm_ts": h["confirm_ts"]}
            for h in prod.internal_history
        ]
        if prod._active_internal is not None:
            ai = prod._active_internal
            detected_internal.append({"start": ai.start_ts, "end": wb, "confirmed": ai.reached_confirmed,
                                      "reason": None, "confirm_ts": ai.confirm_ts})

        for h in prod.macro_history:
            if h["end_reason"]:
                reason_code_counts[h["end_reason"]] += 1
        for h in prod.internal_history:
            if h["end_reason"]:
                reason_code_counts[h["end_reason"]] += 1
        reason_code_counts[final_res.macro_reason] += 1
        if final_res.internal_reason:
            reason_code_counts[final_res.internal_reason] += 1

        per_window[wid] = {
            "window_bars": wb, "n_events": len(events_log),
            "detected_macro": detected_macro, "detected_internal": detected_internal,
            "final_macro_state": final_res.macro_state, "final_internal_state": final_res.internal_state,
        }

    counters = {
        "promo_count": event_kind_counts.get("IS_TREND_MACRO", 0),
        "sweep_confirmed": event_kind_counts.get("SWEEP_CONFIRMED", 0),
        "breakout_accepted": event_kind_counts.get("BREAKOUT_ACCEPTED", 0),
        "liquidity_sweep_reversal": event_kind_counts.get("LIQUIDITY_SWEEP_REVERSAL", 0),
    }

    macro_gt = [(r["blind"], r["start"], r["end"]) for r in level_rows if r["level_assigned"] == "MACRO"]
    internal_gt = [(r["blind"], r["start"], r["end"]) for r in level_rows if r["level_assigned"] == "INTERNAL"]
    unresolved_gt = [(r["blind"], r["start"], r["end"]) for r in level_rows
                     if r["level_assigned"] == "LEVEL_ASSIGNMENT_UNRESOLVED"]

    by_window_macro_gt = collections.defaultdict(list)
    for wid, s, e in macro_gt:
        by_window_macro_gt[wid].append((s, e))
    by_window_internal_gt = collections.defaultdict(list)
    for wid, s, e in internal_gt:
        by_window_internal_gt[wid].append((s, e))

    all_macro_matches: list[dict[str, Any]] = []
    all_internal_matches: list[dict[str, Any]] = []
    n_macro_new = 0
    n_internal_new = 0
    for wid, pw in per_window.items():
        det_macro_conf = [(d["start"], d["end"]) for d in pw["detected_macro"] if d["confirmed"]]
        det_internal_conf = [(d["start"], d["end"]) for d in pw["detected_internal"] if d["confirmed"]]
        n_macro_new += len(pw["detected_macro"])
        n_internal_new += len(pw["detected_internal"])
        gtm = by_window_macro_gt.get(wid, [])
        gti = by_window_internal_gt.get(wid, [])
        det_macro_ct = {(d["start"], d["end"]): d.get("confirm_ts") for d in pw["detected_macro"] if d["confirmed"]}
        det_internal_ct = {(d["start"], d["end"]): d.get("confirm_ts")
                           for d in pw["detected_internal"] if d["confirmed"]}
        for gt_segs, det_segs, ct_map, out_list in (
            (gtm, det_macro_conf, det_macro_ct, all_macro_matches),
            (gti, det_internal_conf, det_internal_ct, all_internal_matches),
        ):
            for g in gt_segs:
                best_iou, best_d = 0.0, None
                for d in det_segs:
                    v = iou(g, d)
                    if v > best_iou:
                        best_iou, best_d = v, d
                confirm_ts = ct_map.get(best_d) if best_d else None
                out_list.append({
                    "window": wid, "gt": g, "best_iou": best_iou, "det": best_d,
                    "det_confirm_ts": confirm_ts,
                    "confirm_delay": (confirm_ts - best_d[0]) if confirm_ts is not None and best_d else None,
                })

    n_refused = (event_kind_counts.get("PARTIAL_OVERLAP_NO_CONTAINMENT", 0)
                + event_kind_counts.get("DEPTH_LIMIT_EXCEEDED", 0)
                + event_kind_counts.get("LEVEL_ASSIGNMENT_UNRESOLVED", 0))
    funnel = {
        "total_attempts": n_macro_new + n_internal_new + n_refused,
        "macro_new": n_macro_new, "internal_new": n_internal_new,
        "refused_partial_overlap": event_kind_counts.get("PARTIAL_OVERLAP_NO_CONTAINMENT", 0),
        "refused_depth_limit": event_kind_counts.get("DEPTH_LIMIT_EXCEEDED", 0),
        "refused_unresolved": event_kind_counts.get("LEVEL_ASSIGNMENT_UNRESOLVED", 0),
    }

    return {
        "per_window": per_window, "reason_code_counts": dict(reason_code_counts),
        "event_kind_counts": dict(event_kind_counts), "counters": counters,
        "macro_state_bar_counts": {str(k): v for k, v in macro_state_bar_counts.items()},
        "internal_state_bar_counts": {str(k): v for k, v in internal_state_bar_counts.items()},
        "macro_matches": all_macro_matches, "internal_matches": all_internal_matches,
        "macro_gt_count": len(macro_gt), "internal_gt_count": len(internal_gt),
        "unresolved_gt_count": len(unresolved_gt), "funnel": funnel,
        "block_of": block_of,
        "frozen_prototype_commit": FROZEN_PROTOTYPE_COMMIT, "frozen_config_id": FROZEN_CONFIG_ID,
        "frozen_hashes": FROZEN_HASHES,
        "tags": ["CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY", "CIRCULAR_LABEL_DERIVED_BARS",
                "ZERO_VALIDATION_WEIGHT"],
    }


def check_historical_reproduction(result: dict[str, Any]) -> tuple[bool, list[str]]:
    """§9 mandat: reproduce sau explica diferenta pt. cifrele VE deja raportate."""
    mismatches = []
    macro_matched = sum(1 for m in result["macro_matches"] if m["best_iou"] > 0)
    internal_matched = sum(1 for m in result["internal_matches"] if m["best_iou"] > 0)
    checks = [
        ("macro_matched", macro_matched, REPORTED["macro_matched"]),
        ("macro_gt", result["macro_gt_count"], REPORTED["macro_gt"]),
        ("internal_matched", internal_matched, REPORTED["internal_matched"]),
        ("internal_gt", result["internal_gt_count"], REPORTED["internal_gt"]),
        ("sweep_confirmed", result["counters"]["sweep_confirmed"], REPORTED["sweep_confirmed"]),
        ("breakout_accepted", result["counters"]["breakout_accepted"], REPORTED["breakout_accepted"]),
        ("liquidity_sweep_reversal", result["counters"]["liquidity_sweep_reversal"],
         REPORTED["liquidity_sweep_reversal"]),
        ("promo_count", result["counters"]["promo_count"], REPORTED["promo_count"]),
        ("funnel_total", result["funnel"]["total_attempts"], REPORTED["funnel_total"]),
        ("funnel_macro_new", result["funnel"]["macro_new"], REPORTED["funnel_macro_new"]),
        ("funnel_internal_new", result["funnel"]["internal_new"], REPORTED["funnel_internal_new"]),
        ("funnel_partial_overlap", result["funnel"]["refused_partial_overlap"],
         REPORTED["funnel_partial_overlap"]),
    ]
    for name, actual, expected in checks:
        if actual != expected:
            mismatches.append(f"{name}: reprodus={actual} raportat_anterior={expected}")
    return (not mismatches), mismatches


if __name__ == "__main__":
    result = run_all()
    reproduced, mismatches = check_historical_reproduction(result)

    print(f"windows processed: {len(result['per_window'])}")
    print(f"MACRO: GT={result['macro_gt_count']} matched="
         f"{sum(1 for m in result['macro_matches'] if m['best_iou'] > 0)}")
    print(f"INTERNAL: GT={result['internal_gt_count']} matched="
         f"{sum(1 for m in result['internal_matches'] if m['best_iou'] > 0)}")
    print(f"counters: {result['counters']}")
    print(f"funnel: {result['funnel']}")

    if reproduced:
        print("\nHISTORICAL_SYNTHETIC_RESULT_REPRODUCED")
        print("ZERO_VALIDATION_WEIGHT")
    else:
        print("\nHISTORICAL_SYNTHETIC_RESULT_NOT_REPRODUCED")
        for m in mismatches:
            print("  ", m)

    result["historical_reproduction"] = {
        "status": "HISTORICAL_SYNTHETIC_RESULT_REPRODUCED" if reproduced
                 else "HISTORICAL_SYNTHETIC_RESULT_NOT_REPRODUCED",
        "mismatches": mismatches,
    }
    out_path = _HERE / "construction_run_results.json"
    out_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out_path}")
