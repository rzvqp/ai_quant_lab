"""Research Task Selector -- picks a concrete investigation WITHIN a given Perspective.

Distinct from the Perspective Generator (CEO refinement #3): the perspective sets the stance;
this selector turns that stance into a single precise, answerable research question bound to an
edge/topic and a window hint. It avoids re-asking a semantically-close question by normalizing
the filled question text and checking it against the set of already-asked questions from
research memory (transparent, auditable de-dup -- not a claim of semantic certainty).

The selector is pure and deterministic: given (perspective, pass_no, asked_norms, task_id) it
returns the same ResearchTask. IDs are allocated by the runner and passed in, so this module
performs no I/O.

Scientific boundary: questions are descriptive/observational ("does X behaviour occur", "how
does Y differ by regime"), never "is X profitable" or "what strategy should we trade".
"""

from __future__ import annotations

import re
from typing import Dict, List, Sequence

from . import seeds
from . import schemas

# Parameter pools shared across templates.
_SESSIONS = ["asia", "london", "ny", "late"]
_DOWS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
_HORIZONS = [3, 5, 10, 20]
_LEVELS = ["the prior-day high", "the prior-day low", "the session open", "the nearest round number"]
_MOVES = ["an isolated single-bar velocity outlier", "a sweep of a prior extreme",
          "a break of structure", "a failure to make a new extreme"]

# Each template: lens -> list of dicts. `t` uses {param} placeholders drawn from the pools below.
# tf/span/edge_ref/topic give the window hint and provenance link.
_BANK: Dict[str, List[dict]] = {
    "time": [
        {"t": "During the {session} session, does price movement behave measurably differently "
              "than in the other sessions over the sampled window?",
         "params": {"session": _SESSIONS}, "tf": "H1", "span": 400, "edge_ref": "E001", "topic": "session_timing"},
        {"t": "On {dow}s, is the distribution of bar ranges distinguishable from the rest of the "
              "week in the sampled window?",
         "params": {"dow": _DOWS}, "tf": "H1", "span": 500, "edge_ref": "E008", "topic": "day_of_week"},
    ],
    "behaviour": [
        {"t": "After {move}, how does price behave over the following {horizon} bars in the sampled window?",
         "params": {"move": _MOVES, "horizon": _HORIZONS}, "tf": "M15", "span": 600,
         "edge_ref": None, "topic": "post_event_behaviour"},
    ],
    "sequence": [
        {"t": "When {move} is immediately followed by {move2}, what is the observed continuation "
              "over the next {horizon} bars?",
         "params": {"move": _MOVES, "move2": _MOVES, "horizon": _HORIZONS}, "tf": "M15", "span": 600,
         "edge_ref": None, "topic": "event_sequence"},
    ],
    "structure": [
        {"t": "How often is {level} respected versus broken on first touch in the sampled window?",
         "params": {"level": _LEVELS}, "tf": "H1", "span": 500, "edge_ref": "E010", "topic": "level_interaction"},
    ],
    "volatility": [
        {"t": "Does the frequency of {move} differ between low- and high-volatility regimes in the "
              "sampled window?",
         "params": {"move": _MOVES}, "tf": "H1", "span": 500, "edge_ref": None, "topic": "vol_conditioning"},
    ],
    "cross_timeframe": [
        {"t": "When the higher timeframe shows {move}, how does the lower-timeframe reaction near "
              "{level} unfold over {horizon} bars?",
         "params": {"move": _MOVES, "level": _LEVELS, "horizon": _HORIZONS}, "tf": "H4", "span": 300,
         "edge_ref": None, "topic": "cross_tf"},
    ],
    "regime": [
        {"t": "Conditioned on a trending versus ranging regime, does the reaction to {level} differ "
              "in the sampled window?",
         "params": {"level": _LEVELS}, "tf": "H1", "span": 500, "edge_ref": None, "topic": "regime_conditioning"},
    ],
    "anomaly": [
        {"t": "Are there recurring outlier bars around {level} that stand out from the ambient "
              "distribution in the sampled window?",
         "params": {"level": _LEVELS}, "tf": "M15", "span": 600, "edge_ref": None, "topic": "anomaly_scan"},
    ],
    "falsification": [
        {"t": "Testing the tentative observation that {move} leads to continuation: does the pattern "
              "fail to appear where the observation predicts it should over {horizon} bars?",
         "params": {"move": _MOVES, "horizon": _HORIZONS}, "tf": "M15", "span": 600,
         "edge_ref": None, "topic": "falsification"},
    ],
}

# Fallback templates if a lens somehow has no bank entry.
_FALLBACK = _BANK["behaviour"]


def normalize_question(q: str) -> str:
    """Canonicalize a filled question for de-dup: lowercase, strip punctuation, collapse spaces."""
    q = q.lower()
    q = re.sub(r"[^a-z0-9\s]", " ", q)
    q = re.sub(r"\s+", " ", q).strip()
    return q


def _enumerate_candidates(templates: List[dict]) -> List[dict]:
    """Expand every (template, param-combination) into a candidate spec. Deterministic order."""
    out: List[dict] = []
    for ti, tmpl in enumerate(templates):
        names = list(tmpl["params"].keys())
        pools = [tmpl["params"][n] for n in names]
        # cartesian product without itertools import noise
        combos: List[List] = [[]]
        for pool in pools:
            combos = [c + [v] for c in combos for v in pool]
        for combo in combos:
            mapping = dict(zip(names, combo))
            # {move2} reuses the {move} pool under a distinct key
            fill = dict(mapping)
            if "move2" in tmpl["t"] and "move2" not in fill and "move" in fill:
                fill["move2"] = fill["move"]
            out.append({"tmpl_idx": ti, "tmpl": tmpl, "fill": fill})
    return out


class ResearchTaskSelector:
    def __init__(self, master_seed: int):
        self.master_seed = int(master_seed)

    def select(
        self,
        perspective: dict,
        pass_no: int,
        asked_norms: Sequence[str],
        task_id: str,
    ) -> dict:
        lens = perspective["lens"]
        templates = _BANK.get(lens, _FALLBACK)
        candidates = _enumerate_candidates(templates)

        rng = seeds.rng_labelled(self.master_seed, pass_no, "task")
        rng.shuffle(candidates)

        asked = set(asked_norms)
        chosen = None
        for cand in candidates:
            q = _fill(cand["tmpl"]["t"], cand["fill"])
            if normalize_question(q) not in asked:
                chosen = (cand, q)
                break
        exhausted = chosen is None
        if exhausted:
            cand = candidates[0]
            q = _fill(cand["tmpl"]["t"], cand["fill"])
            chosen = (cand, q)

        cand, question = chosen
        tmpl = cand["tmpl"]
        task = {
            "task_id": task_id,
            "perspective_id": perspective["perspective_id"],
            "lens": lens,
            "edge_ref": tmpl.get("edge_ref"),
            "topic": tmpl.get("topic", "general"),
            "question": question,
            "question_norm": normalize_question(question),
            "selection_reason": (
                f"Within a {lens}/{perspective['framing']} perspective, chose an unasked "
                f"question on '{tmpl.get('topic')}'."
                if not exhausted else
                f"Question space for lens '{lens}' exhausted vs memory; reusing oldest candidate."
            ),
            "window_hint": {
                "timeframe": tmpl.get("tf", "H1"),
                "span_bars": int(tmpl.get("span", 400)),
                "prefer_regime": perspective.get("regime_bias", "any"),
            },
        }
        errs = schemas.validate(task, schemas.load_schema("research_task"))
        if errs:  # pragma: no cover - internal invariant
            raise AssertionError(f"generated invalid task: {errs}")
        return task


def _fill(template: str, mapping: dict) -> str:
    out = template
    for k, v in mapping.items():
        out = out.replace("{" + k + "}", str(v))
    return out
