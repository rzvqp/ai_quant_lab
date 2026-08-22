from __future__ import annotations

import dataclasses

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.order_identity import (
    client_order_id_for,
    compact_comment_tag,
    decision_id_for,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.tests._fixtures import (
    make_s5_hypothesis,
    make_trade_decision,
)


def test_deterministic_same_inputs_same_id() -> None:
    hyp = make_s5_hypothesis()
    dec = make_trade_decision(hyp)
    a = client_order_id_for(hyp, dec)
    b = client_order_id_for(hyp, dec)
    assert a == b


def test_different_market_state_produces_different_id() -> None:
    hyp1 = make_s5_hypothesis(market_state_identity="ms-1")
    hyp2 = make_s5_hypothesis(market_state_identity="ms-2")
    assert client_order_id_for(hyp1, make_trade_decision(hyp1)) != client_order_id_for(hyp2, make_trade_decision(hyp2))


def test_different_evidence_fingerprint_produces_different_id() -> None:
    hyp = make_s5_hypothesis()
    dec = make_trade_decision(hyp)
    dec2 = dataclasses.replace(dec, evidence_fingerprint="different-fingerprint")
    assert client_order_id_for(hyp, dec) != client_order_id_for(hyp, dec2)


def test_decision_id_derived_from_and_distinct_from_client_order_id() -> None:
    hyp = make_s5_hypothesis()
    dec = make_trade_decision(hyp)
    cid = client_order_id_for(hyp, dec)
    did = decision_id_for(hyp, dec)
    assert did != cid
    assert cid in did


def test_comment_tag_fits_the_broker_comment_limit_with_margin() -> None:
    hyp = make_s5_hypothesis()
    dec = make_trade_decision(hyp)
    tag = compact_comment_tag(hyp, dec)
    # empirically-confirmed working limit for this project's own tested broker/terminal is 27-28 chars
    # (mt5_demo_execution/request_builder.py) -- stay comfortably under it.
    assert len(tag) <= 25


def test_comment_tag_deterministic_and_distinguishes_events() -> None:
    hyp1 = make_s5_hypothesis(market_state_identity="ms-1")
    hyp2 = make_s5_hypothesis(market_state_identity="ms-2")
    assert compact_comment_tag(hyp1, make_trade_decision(hyp1)) == compact_comment_tag(hyp1, make_trade_decision(hyp1))
    assert compact_comment_tag(hyp1, make_trade_decision(hyp1)) != compact_comment_tag(hyp2, make_trade_decision(hyp2))
