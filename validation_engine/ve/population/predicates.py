"""Evaluarea predicatelor de populație pe barele sursei (F4).

Fiecare predicat devine o mască booleană pandas. Semantica listelor este
CONJUNCȚIE (G4). `first_in_scope(day, …)` = prima bară a zilei UTC unde predicatul
intern e adevărat.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..data import calendar


class PredicateError(RuntimeError):
    """Predicat neimplementat sau operand nerezolvabil la runtime."""


def _resolve_operand(operand, values: dict, base: pd.DataFrame):
    """Un operand este un id de variabilă sau o constantă numerică."""
    if isinstance(operand, (int, float)) and not isinstance(operand, bool):
        return operand
    if isinstance(operand, str):
        if operand in values:
            return values[operand]
        raise PredicateError(f"operand nerezolvabil: '{operand}'")
    raise PredicateError(f"operand invalid: {operand!r}")


_OPS = {
    "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b, "!=": lambda a, b: a != b,
}


def evaluate(pred: dict, values: dict, base: pd.DataFrame) -> pd.Series:
    """Întoarce o mască booleană aliniată la `base`."""
    kind = pred["predicate"]
    p = pred.get("params", {})

    if kind == "compare@v1":
        left = _resolve_operand(p["left"], values, base)
        right = _resolve_operand(p["right"], values, base)
        mask = _OPS[p["op"]](left, right)
        return pd.Series(mask, index=base.index).fillna(False).astype(bool)

    if kind == "and@v1":
        out = pd.Series(True, index=base.index)
        for op in p["operands"]:
            out &= evaluate(op, values, base)
        return out

    if kind == "or@v1":
        out = pd.Series(False, index=base.index)
        for op in p["operands"]:
            out |= evaluate(op, values, base)
        return out

    if kind == "not@v1":
        return ~evaluate(p["operands"][0], values, base)

    if kind == "in_session@v1":
        sess = values[p["session_ref"]]
        return sess.isin(set(p["names"])).fillna(False).astype(bool)

    if kind == "bar_position@v1":
        scope = p["scope"]
        idx = p["index"]
        frm = p["from"]
        if scope != "day":
            raise PredicateError(f"bar_position scope neimplementat în F4: {scope}")
        grp = base.groupby("day")
        pos = grp.cumcount() if frm == "start" else grp.cumcount(ascending=False)
        return (pos == idx)

    if kind == "first_in_scope@v1":
        scope = p["scope"]
        if scope != "day":
            raise PredicateError(f"first_in_scope scope neimplementat în F4: {scope}")
        inner = evaluate(p["predicate"], values, base)
        # prima bară a fiecărei zile UTC unde inner e True
        df = pd.DataFrame({"day": base["day"].values, "inner": inner.values}, index=base.index)
        first = pd.Series(False, index=base.index)
        # index-ul primului True per zi
        true_rows = df[df["inner"]]
        firsts = true_rows.groupby("day").head(1).index
        first.loc[firsts] = True
        return first

    raise PredicateError(f"predicat neimplementat în F4: {kind}")
