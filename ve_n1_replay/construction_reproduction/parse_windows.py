"""
CEO_ASSISTED_SYNTHETIC_CONSTRUCTION_ONLY
CIRCULAR_LABEL_DERIVED_BARS
ZERO_VALIDATION_WEIGHT

Normalizeaza cele 48 de ferestre BLIND-001..048 dintr-un format JSON eterogen (doua scheme
observate empiric) intr-o reprezentare unica: o lista ordonata de "spans" per fereastra, fiecare
span fiind fie un REGIM (RANGE/CHANNEL_UP/CHANNEL_DOWN, cu lower/upper/mid optionale) fie un
BRIDGE (o tranzitie cu un eveniment asociat).

Nu se acceseaza NICIO bara OHLC reala -- sursa e EXCLUSIV fixtures/LEVEL_MAPPING.md +
fixtures/PART{1,2}_LOCKED_LABELS.json + fixtures/PART{3,4}_PROVISIONAL_LABELS.json +
fixtures/CORRECTION_ADDENDUM_046_048.md, copii comise byte-exact ale fisierelor deja publicate
(NEsigilate) pe `statistician-foundation` (v. fixtures/FIXTURE_PROVENANCE.md pt. commit-urile
sursa exacte) -- barele OHLC reale stau in escrow, in afara oricarui checkout Git, inaccesibile.

Aceasta componenta reproduce cifrele VE deja raportate (RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md).
NU valideaza detectorul -- corpusul e sintetizat MECANIC din aceleasi etichete cu care e comparat.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

FIXTURES = Path(__file__).resolve().parent / "fixtures"

# addendum-ul de corectie -- transcris manual din CORRECTION_ADDENDUM_046_048.md (proza -> structura),
# inlocuieste COMPLET etichetele PART3/4 pt. aceste 3 ferestre.
ADDENDUM_046_048: dict[str, dict[str, Any]] = {
    "BLIND-046": {
        "window_bars": 288,
        "spans": [
            {"kind": "regime", "start": 0, "end": 48, "class": "RANGE"},
            {"kind": "regime", "start": 48, "end": 96, "class": "RANGE"},
            {"kind": "regime", "start": 96, "end": 140, "class": "CHANNEL_DOWN"},
            {"kind": "bridge", "start": 140, "end": 148, "event": "BREAKOUT_DOWN"},
            {"kind": "regime", "start": 148, "end": 185, "class": "RANGE"},
            {"kind": "regime", "start": 185, "end": 235, "class": "CHANNEL_DOWN"},
            {"kind": "regime", "start": 235, "end": 280, "class": "RANGE"},
            {"kind": "bridge", "start": 280, "end": 288, "event": "BREAKOUT_DOWN"},
        ],
    },
    "BLIND-047": {
        "window_bars": 96,
        "spans": [
            {"kind": "bridge", "start": 0, "end": 6, "event": "BREAKOUT_UP"},
            {"kind": "regime", "start": 6, "end": 48, "class": "CHANNEL_UP"},
            {"kind": "regime", "start": 48, "end": 64, "class": "RANGE"},
            {"kind": "bridge", "start": 64, "end": 73, "event": "BREAKOUT_UP"},
            {"kind": "regime", "start": 73, "end": 84, "class": "RANGE"},
            {"kind": "regime", "start": 84, "end": 92, "class": "CHANNEL_DOWN"},
            {"kind": "regime", "start": 92, "end": 96, "class": "RANGE"},
        ],
    },
    "BLIND-048": {
        "window_bars": 480,
        "spans": [
            {"kind": "regime", "start": 0, "end": 35, "class": "CHANNEL_DOWN"},
            {"kind": "regime", "start": 35, "end": 105, "class": "RANGE"},
            {"kind": "bridge", "start": 105, "end": 125, "event": "BREAKOUT_DOWN"},
            {"kind": "regime", "start": 125, "end": 195, "class": "RANGE"},
            {"kind": "regime", "start": 195, "end": 235, "class": "CHANNEL_DOWN"},
            {"kind": "regime", "start": 235, "end": 330, "class": "CHANNEL_UP"},
            {"kind": "bridge", "start": 330, "end": 350, "event": "BREAKOUT_UP"},
            {"kind": "regime", "start": 350, "end": 410, "class": "RANGE"},
            {"kind": "regime", "start": 410, "end": 460, "class": "CHANNEL_UP"},
            {"kind": "regime", "start": 460, "end": 480, "class": "CHANNEL_DOWN"},
        ],
    },
}


def _class_span(seg: dict[str, Any]) -> dict[str, Any]:
    return {"kind": "regime", "start": seg["start"], "end": seg["end"], "class": seg["class"],
            "lower": seg.get("lower"), "upper": seg.get("upper"), "mid": seg.get("mid")}


def _bridge_span(seg: dict[str, Any]) -> dict[str, Any]:
    ev = seg.get("event") or seg.get("entry_event")
    if not ev and seg.get("events"):
        ev = seg["events"][0]
    return {"kind": "bridge", "start": seg["start"], "end": seg["end"], "event": ev}


def normalize_window(w: dict[str, Any]) -> tuple[int, list[dict[str, Any]], tuple[int, int] | None]:
    """Intoarce (window_bars, spans_ordonate_dupa_start, macro_envelope) folosind schema A
    (segments cu TRANSITION inline -- spans-urile SUNT scara L1/MACRO) sau schema B
    (internal_structures separat, mai fin-granular -- spans-urile astea sunt scara L2/INTERNAL,
    imbracate INTR-UN singur `segments[0]` care e chiar plicul L1/MACRO ce le contine pe toate;
    `macro_envelope` = (start,end) al acelui plic, sau None la schema A)."""
    window_bars = w["window_bars"]
    macro_envelope: tuple[int, int] | None = None
    src: list[dict[str, Any]]
    if w.get("internal_structures"):
        src = w["internal_structures"]
        top = w["segments"][0]
        macro_envelope = (top["start"], top["end"])
    else:
        src = w["segments"]
    spans = []
    for seg in src:
        if seg["class"] == "TRANSITION":
            spans.append(_bridge_span(seg))
        else:
            spans.append(_class_span(seg))
    spans.sort(key=lambda s: s["start"])
    return window_bars, spans, macro_envelope


def load_all_windows() -> dict[str, dict[str, Any]]:
    windows: dict[str, dict[str, Any]] = {}
    filenames = {
        "PART1": "PART1_LOCKED_LABELS.json", "PART2": "PART2_LOCKED_LABELS.json",
        "PART3": "PART3_PROVISIONAL_LABELS.json", "PART4": "PART4_PROVISIONAL_LABELS.json",
    }
    for part, fname in filenames.items():
        d = json.loads((FIXTURES / fname).read_text(encoding="utf-8"))
        for w in d["labels"]:
            windows[w["id"]] = {"raw": w, "part": part}
    for wid, override in ADDENDUM_046_048.items():
        windows[wid] = {"raw": {"id": wid, "window_bars": override["window_bars"],
                                "_addendum_spans": override["spans"]}, "part": "ADDENDUM"}
    assert len(windows) == 48, f"expected 48 windows, got {len(windows)}"
    return windows


def normalized(
    windows: dict[str, dict[str, Any]]
) -> dict[str, tuple[int, list[dict[str, Any]], tuple[int, int] | None]]:
    out: dict[str, tuple[int, list[dict[str, Any]], tuple[int, int] | None]] = {}
    for wid, entry in windows.items():
        raw = entry["raw"]
        if "_addendum_spans" in raw:
            out[wid] = (raw["window_bars"], sorted(raw["_addendum_spans"], key=lambda s: s["start"]), None)
        else:
            out[wid] = normalize_window(raw)
    return out


LEVEL_ROW = re.compile(
    r"\|\s*`(BLIND-\d+#L(\d)-(\d+))`\s*\|\s*`(BLIND-\d+)`\s*\|\s*(\d+)\s*\|\s*(B\d)\s*\|\s*"
    r"(\d+)-(\d+)\s*\|\s*([^|]+?)\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]*?)\s*\|"
)


def parse_level_mapping() -> list[dict[str, Any]]:
    """Parseaza tabelul din LEVEL_MAPPING.md -> lista de dict-uri
    {segment_id, blind, level(1/2), idx, block, start, end, label, level_assigned, parent}."""
    text = (FIXTURES / "LEVEL_MAPPING.md").read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        m = LEVEL_ROW.match(line.strip())
        if not m:
            continue
        seg_id, lvl, idx, blind, length, block, start, end, label, level_assigned, parent = m.groups()
        rows.append({
            "segment_id": seg_id, "blind": blind, "level": int(lvl), "idx": int(idx),
            "window_bars": int(length), "block": block, "start": int(start), "end": int(end),
            "label": label.strip(), "level_assigned": level_assigned.strip(),
            "parent": parent.strip() if parent.strip() != "-" else None,
        })
    return rows


if __name__ == "__main__":
    windows = load_all_windows()
    norm = normalized(windows)
    level_rows = parse_level_mapping()
    print(f"windows: {len(windows)}  level_mapping rows: {len(level_rows)}")
    macro_n = sum(1 for r in level_rows if r["level_assigned"] == "MACRO")
    unresolved_n = sum(1 for r in level_rows if r["level_assigned"] == "LEVEL_ASSIGNMENT_UNRESOLVED")
    internal_n = sum(1 for r in level_rows if r["level_assigned"] == "INTERNAL")
    print(f"MACRO={macro_n} UNRESOLVED={unresolved_n} INTERNAL={internal_n} (expect 88/26/12)")
