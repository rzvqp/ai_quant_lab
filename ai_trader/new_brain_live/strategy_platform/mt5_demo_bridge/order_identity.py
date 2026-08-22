"""Deterministic, idempotent S5 order identity (mandate section 21) -- a pure function of the canonical
event's own already-existing identity fields, never random, never time-of-submission-derived (either of
those would defeat idempotency by construction: the same canonical event, re-evaluated after a restart,
must re-derive the IDENTICAL id). Bound to: strategy identity, `TradeHypothesis.dedup_key` (strategy,
instrument, market_state_identity -- the signal/event identity, `trade_hypothesis.py`'s own definition),
the hypothesis's own `signal_timestamp` (the "trading day/event" the mandate names), and the EV
decision's `evidence_fingerprint` (binds the identity to the EXACT evidence that produced the decision --
a different evidence package, even for the same signal, is a genuinely different decision and must not
collide).

**Known, disclosed limitation this module deliberately avoids inheriting**: `mt5_demo_execution.
request_builder._magic_number_for` derives MT5's own `magic` field via Python's builtin `hash()`, which
is NOT stable across process restarts (string-hash randomization, `PYTHONHASHSEED`) -- unsuitable as a
cross-restart reconciliation key. This module's own `client_order_id` uses `hashlib.sha256` instead
(stable across restarts, interpreters, and machines) and is treated as the SOLE authoritative identity;
the broker-side `magic`/`comment` fields (still produced by the pre-existing, unmodified
`build_mt5_request` when this identity is submitted through `MT5DemoBrokerAdapter`) are non-authoritative
decoration only -- reconciliation never relies on them alone. See `reconciliation.py`'s own docstring for
the full consequence of this, and `AI_TRADER_S5_MT5_DEMO_EXECUTION_REPORT.md` section on order identity
for the disclosed reasoning in full."""

from __future__ import annotations

import hashlib

from ai_trader.new_brain_live.strategy_platform.ev_engine import EVDecision
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis

CLIENT_ORDER_ID_SCHEMA_VERSION = "s5-mt5-demo-client-order-id-v1"


def client_order_id_for(hypothesis: TradeHypothesis, decision: EVDecision) -> str:
    """`decision` MUST be the `EVDecision` produced FROM `hypothesis` (caller's own responsibility, same
    precondition discipline `risk_execution_adapter.evaluate_and_attempt` already establishes for
    `EVDecision.hypothesis`) -- not independently re-derivable from `decision` alone, since `EVDecision`
    only carries the fields it needs, not every field this identity binds to."""
    strategy_id, instrument, market_state_identity = hypothesis.dedup_key
    raw = "|".join((
        CLIENT_ORDER_ID_SCHEMA_VERSION, strategy_id, hypothesis.strategy_version, instrument,
        market_state_identity, str(hypothesis.signal_timestamp), decision.decision, decision.evidence_fingerprint,
    ))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"s5mt5-{digest}"


def decision_id_for(hypothesis: TradeHypothesis, decision: EVDecision) -> str:
    return f"{client_order_id_for(hypothesis, decision)}-dec"


def compact_comment_tag(hypothesis: TradeHypothesis, decision: EVDecision) -> str:
    """A best-effort, auditable, per-EVENT marker for MT5's own `comment` field (mandate section 22:
    "where broker comment length permits, include a compact auditable S5 marker"). Deliberately NOT the
    same scheme `mt5_demo_execution.request_builder._comment_for` uses (`f"{strategy_id}:{decision_id}"`)
    -- S5's own real `strategy_id` (`s5_c_2d587447_opening_range_breakout_long`, 44 chars) alone already
    exceeds that module's own empirically-confirmed 27-char broker limit
    (`FusionMarkets-Demo`/build 6090, re-verified live this mandate), so that scheme would silently
    truncate to a constant strategy_id-prefix, identical and non-distinguishing across every S5 order --
    disclosed here rather than silently accepted. This scheme instead uses a short, fixed `S5:` prefix
    plus a hash slice of THIS identity -- short enough to survive the same limit with margin, and unique
    per canonical event. Per section 22's own explicit allowance, this is a convenience marker only; the
    FULL identity mapping lives in `mt5_execution_ledger.py`, not in this string."""
    digest = hashlib.sha256(client_order_id_for(hypothesis, decision).encode("utf-8")).hexdigest()
    return f"S5:{digest[:20]}"
