"""Ledger-ul de rulări — append-only (arhitectură §3.5, §10 pct. 7).

Fiecare invocare — inclusiv cele oprite la prima fază — intră în ledger. Astfel,
selecția convenabilă a unei rulări dintre mai multe devine detectabilă fără a
depinde de onestitatea VE. Nimic nu se rescrie și nimic nu se șterge.

Două forme paralele: `run_ledger.jsonl` (mașină) și `RUN_LEDGER.md` (citibil).
"""

from __future__ import annotations

import json
from pathlib import Path

from .. import paths

JSONL = paths.VE_ROOT / "run_ledger.jsonl"
MD = paths.VE_ROOT / "RUN_LEDGER.md"

_MD_HEADER = (
    "# RUN LEDGER — Validation Engine\n\n"
    "Append-only. Fiecare rulare, inclusiv cele oprite. Nimic nu se rescrie.\n\n"
    "| run_id | moment | candidat | spec_sha256 | status | date atinse | external_writes |\n"
    "|---|---|---|---|---|---|---|\n"
)


def append(entry: dict, jsonl: Path | None = None, md: Path | None = None) -> None:
    jsonl = jsonl or JSONL
    md = md or MD
    with open(jsonl, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    if not md.exists():
        md.write_text(_MD_HEADER, encoding="utf-8")
    row = (
        f"| {entry.get('run_id')} | {entry.get('finished_at')} | "
        f"{entry.get('candidate_id')} | {str(entry.get('spec_sha256'))[:16]}… | "
        f"{entry.get('status')} | {entry.get('data_accesses', 0)} | "
        f"{entry.get('external_writes')} |\n"
    )
    with open(md, "a", encoding="utf-8") as fh:
        fh.write(row)


def read_all(jsonl: Path | None = None) -> list[dict]:
    jsonl = jsonl or JSONL
    if not Path(jsonl).exists():
        return []
    return [json.loads(line) for line in Path(jsonl).read_text(encoding="utf-8").splitlines() if line.strip()]
