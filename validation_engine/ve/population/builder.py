"""Construirea populației (F4): include(∧) − exclude(∨) − cooldown, + denominator.

Raportează câte bare candidate a respins fiecare criteriu de includere (denominator
per criteriu). Fără nicio statistică.
"""

from __future__ import annotations

import pandas as pd

from . import predicates


def build(population: dict, values: dict, base: pd.DataFrame) -> dict:
    n_candidates = len(base)

    # include = conjuncție; denominator per criteriu
    include_masks = {}
    per_criterion = {}
    combined = pd.Series(True, index=base.index)
    for pred in population.get("include", []):
        m = predicates.evaluate(pred, values, base)
        include_masks[pred["id"]] = m
        per_criterion[pred["id"]] = {
            "passed": int(m.sum()),
            "rejected": int((~m).sum()),
        }
        combined &= m

    # exclude = orice potrivire scoate bara
    for pred in population.get("exclude", []):
        combined &= ~predicates.evaluate(pred, values, base)

    event_idx = list(base.index[combined])

    # cooldown pe bare consecutive (index de bară)
    min_gap = int(population.get("cooldown", {}).get("min_bars_between_events", 0))
    kept = []
    last = None
    for i in event_idx:
        if last is None or (i - last) >= min_gap:
            kept.append(i)
            last = i

    return {
        "n_candidates": n_candidates,
        "per_criterion_denominator": per_criterion,
        "n_after_include_exclude": len(event_idx),
        "n_after_cooldown": len(kept),
        "min_bars_between_events": min_gap,
        "event_indices": kept,
        "event_times": [int(base.loc[i, "time"]) for i in kept],
    }
