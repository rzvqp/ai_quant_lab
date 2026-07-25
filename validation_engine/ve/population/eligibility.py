"""Aplicarea eligibility → familia realizată (F4).

Numără `n` per celulă (evenimente ce satisfac predicatele celulei) și aplică regula
`member_eligibility {field, op, value}` — DOAR pe câmpuri pre-rezultat. Rezultatul e
familia realizată (celule eligibile + m). NU e o corecție statistică (pragul e F5).
"""

from __future__ import annotations

import pandas as pd

from . import predicates

_OPS = {
    "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b, "!=": lambda a, b: a != b,
}

#: Câmpuri pre-rezultat calculabile la F4 (subsetul din lista albă a registrului).
_PRE_OUTCOME = {"n", "event_count"}


def realized_family(multiple_testing: dict, tests: list[dict], event_idx: list,
                    values: dict, base: pd.DataFrame) -> dict:
    """Familia realizată pentru testul referit de membri, aplicând member_eligibility."""
    elig = multiple_testing.get("params", {}).get("member_eligibility")
    members = multiple_testing.get("members", [])

    # grupăm membrii pe test
    test_by_id = {t["test_id"]: t for t in tests}
    event_set = set(event_idx)

    per_cell = {}
    for m in members:
        tid, cell_id = m["test_id"], m["cell"]
        test = test_by_id.get(tid)
        if test is None:
            continue
        cell = next((c for c in test.get("cells", []) if c["id"] == cell_id), None)
        if cell is None:
            continue
        # n = evenimente care satisfac predicatele celulei (conjuncție)
        mask = pd.Series(True, index=base.index)
        for pred in cell.get("predicates", []):
            mask &= predicates.evaluate(pred, values, base)
        cell_events = [i for i in event_idx if bool(mask.loc[i])]
        per_cell[f"{tid}::{cell_id}"] = {"n": len(cell_events), "event_count": len(cell_events)}

    # aplicăm eligibilitatea (doar câmp pre-rezultat)
    eligible = []
    dropped = []
    if elig and elig.get("field") in _PRE_OUTCOME:
        field, op, value = elig["field"], elig["op"], elig["value"]
        for key, stats in per_cell.items():
            if _OPS[op](stats[field], value):
                eligible.append(key)
            else:
                dropped.append({"cell": key, field: stats[field]})
    else:
        eligible = list(per_cell)

    return {
        "eligibility_rule": elig,
        "per_cell": per_cell,
        "eligible_cells": eligible,
        "dropped_cells": dropped,
        "m_realized": len(eligible),
        "note": "Familia realizată prin numărare de populație. Pragul de corecție este F5.",
    }
