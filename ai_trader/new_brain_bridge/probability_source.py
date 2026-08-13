"""`load_probability_inputs` -- the honest gap in today's wiring, disclosed rather than papered over.

`ve_brain.ev_engine`'s own contract (its module docstring, quoted verbatim): "`probability_inputs`
... turatul NU produce conteo per-bara; conteoul vine din ISTORIC, cheiat pe regim/bias. Absent =>
NO_TRADE (nu se inventeaza)." That hierarchy -- validated, per-regime, empirical-Bayes outcome counts
(`ve_brain.OutcomeCell`: `n`, `n_target`, `n_horizon`, `sum_horizon_R`) for `ve_brain`'s canonical
strategy IDs (`trend_pullback`, `range_fade`, `trend_shadow`, `trend_experimental`) -- does not exist
anywhere in this repository. Building one would mean the AI Trader division ESTIMATING outcome
statistics itself, which is Alpha/Statistician research territory (see this session's own memory:
validated edges like CAND-0037 go through an independent statistical-validation gate before anyone
treats their outcome counts as real) -- not something this mandate authorizes inventing.

**Consequence, stated plainly**: every real live event that reaches `ve_brain.decide_n6` today returns
`NO_TRADE` / `MISSING_PROBABILITY_INPUTS` at the EV stage (or an earlier NO_TRADE if eligibility/regime
already refused first) -- never `TRADE` or `SHADOW_TRADE_CANDIDATE`. This is the CORRECT, EXPECTED
behavior of a SHADOW-only integration whose purpose is proving the WIRING is genuine, not producing
trades. When Alpha/Statistician research eventually produces a validated, ratified outcome-count table
for one of these strategy IDs, wiring it in here is an explicit, separate, reviewable change to this one
function -- not a silent, automatic pickup."""

from __future__ import annotations

import ve_brain  # type: ignore[import-untyped]  # external VE artifact, no py.typed marker -- never modified


def load_probability_inputs(strategy_id: str, strategy_version: str) -> ve_brain.ProbabilityInputs | None:
    """Always `None` today -- see module docstring. Takes `strategy_id`/`strategy_version` (not a
    regime/bias key) because that IS the granularity a real table would eventually be keyed at; the
    parameters exist now so callers don't need to change shape once a real source is wired in."""
    return None
