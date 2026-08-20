"""Diff-uiește proiecția MACRO din DOUĂ fișiere `predictions.json` produse de `run_inference()` pe
ACELAȘI input (mandat "RANGE V4 F1-ONLY REMEDIATION AFTER RT-RANGE-0012", secțiunea D).

De ce există: RT-RANGE-0012 (`892355f`/E87) a dovedit manual, o singură dată, că F5 schimbă proiecția
MACRO pe bare reale (12/48 ferestre, tabel §1). VE nu are acces la escrow (v. raportul de livrare) --
nu poate reproduce acea comparație direct. Acest script automatizează EXACT comparația din tabelul lor
§1, ca Red Team să o poată re-rula pe cerere, pe orice pereche de commit-uri, fără muncă manuală.

Utilizare (de către Red Team, cu acces la escrow):
  1. La commit-ul `82f27c0` (pre-F5, baseline înghețat): rulează `run_inference()` pe cele 48 ferestre
     reale -> salvează `predictions.json` ca `baseline.json`.
  2. La acest commit (F1-only, post-remediere): rulează `run_inference()` pe ACELEAȘI 48 ferestre reale
     -> salvează `predictions.json` ca `candidate.json`.
  3. `python verify_macro_identity_vs_baseline.py baseline.json candidate.json`

Ieșire: pt. fiecare fereastră, PASS dacă geometria MACRO (structuri + evenimente, excluzând
`structure_id` -- identic cu convenția RT-RANGE-0012) e identică; FAIL cu diff explicit altfel. Sumar
final replică exact rândurile tabelului RT-RANGE-0012 §1 (SWEEP_CONFIRMED/BREAKOUT_ACCEPTED/
LIQUIDITY_SWEEP_REVERSAL/IS_TREND_MACRO). Verdict global: `MACRO_IDENTICAL` doar dacă TOATE ferestrele
trec -- exit code 0 pe PASS, 1 pe orice FAIL (utilizabil direct în CI/scripting).

Nu citește escrow, nu cere acces la bare reale -- consumă DOAR fișiere `predictions.json` deja produse
de altcineva cu acces (Red Team). Determinist, fără stare, fără efecte laterale.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_MACRO_STRUCT_FIELDS = (
    "depth", "parent_structure_id", "start_ts", "confirm_ts", "end_ts", "end_reason",
    "boundary_upper", "boundary_lower", "role", "role_known_ts", "predecessor_id",
)
_MACRO_EVENT_KINDS_TRACKED = (
    "SWEEP_CONFIRMED", "BREAKOUT_ACCEPTED", "LIQUIDITY_SWEEP_REVERSAL", "IS_TREND_MACRO",
)


def _macro_structs(window_output: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {k: s.get(k) for k in _MACRO_STRUCT_FIELDS}
        for s in window_output.get("macro_structures", [])
    ]


def _macro_events(window_output: dict[str, Any]) -> list[tuple[int, str]]:
    out = []
    for rec in window_output.get("records", []):
        for e in rec.get("events", []):
            if e.get("depth") == "MACRO":
                out.append((rec["bar_index"], e["kind"]))
    return out


def _load(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {w["window_id"]: w for w in data["windows"]}


def compare(baseline_path: Path, candidate_path: Path) -> bool:
    baseline = _load(baseline_path)
    candidate = _load(candidate_path)

    baseline_ids, candidate_ids = set(baseline), set(candidate)
    if baseline_ids != candidate_ids:
        print(f"WINDOW SET MISMATCH: baseline-only={baseline_ids - candidate_ids} "
              f"candidate-only={candidate_ids - baseline_ids}")
        return False

    all_ok = True
    event_counts_baseline: dict[str, int] = {k: 0 for k in _MACRO_EVENT_KINDS_TRACKED}
    event_counts_candidate: dict[str, int] = {k: 0 for k in _MACRO_EVENT_KINDS_TRACKED}

    for wid in sorted(baseline_ids):
        b_structs = _macro_structs(baseline[wid])
        c_structs = _macro_structs(candidate[wid])
        b_events = _macro_events(baseline[wid])
        c_events = _macro_events(candidate[wid])

        for _bar, kind in b_events:
            if kind in event_counts_baseline:
                event_counts_baseline[kind] += 1
        for _bar, kind in c_events:
            if kind in event_counts_candidate:
                event_counts_candidate[kind] += 1

        geometry_ok = b_structs == c_structs
        events_ok = b_events == c_events
        window_ok = geometry_ok and events_ok
        all_ok = all_ok and window_ok

        status = "PASS" if window_ok else "FAIL"
        print(f"[{status}] {wid}")
        if not geometry_ok:
            print(f"    geometry differs: baseline={b_structs!r}")
            print(f"                      candidate={c_structs!r}")
        if not events_ok:
            print(f"    MACRO events differ: baseline={b_events!r}")
            print(f"                         candidate={c_events!r}")

    print()
    print("MACRO-depth event counts (baseline -> candidate):")
    for kind in _MACRO_EVENT_KINDS_TRACKED:
        b, c = event_counts_baseline[kind], event_counts_candidate[kind]
        marker = "OK" if b == c else "CHANGED"
        print(f"  {kind}: {b} -> {c}  [{marker}]")

    print()
    print("MACRO_IDENTICAL = TRUE" if all_ok else "MACRO_IDENTICAL = FALSE")
    return all_ok


def main() -> int:
    if len(sys.argv) != 3:
        print("utilizare: verify_macro_identity_vs_baseline.py <baseline_predictions.json> "
              "<candidate_predictions.json>", file=sys.stderr)
        return 2
    baseline_path, candidate_path = Path(sys.argv[1]), Path(sys.argv[2])
    ok = compare(baseline_path, candidate_path)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
