"""Teste: contractul LevelOutput (Ok/Unavailable) + cheia opportunity_id (geometrie + două ceasuri + D7)."""

from __future__ import annotations

import os
import sys

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

from level_output import Ok, Unavailable, is_available, unwrap_or_none  # noqa: E402
from opportunity_id import OppState, Opportunity, OpportunityTracker  # noqa: E402


# ───────────────────────────── contractul ─────────────────────────────
def test_ok_carries_payload_unavailable_does_not() -> None:
    ok: Ok[int] = Ok(value=7, as_of=10, valid_until=12, schema_hash="h")
    un = Unavailable(reason="stale", as_of=10)
    assert unwrap_or_none(ok) == 7 and is_available(ok)
    assert unwrap_or_none(un) is None and not is_available(un)
    assert not hasattr(un, "value") and not hasattr(un, "schema_hash")   # absența e deliberată (mecanismul portant)


def test_unavailable_has_no_value_field() -> None:
    assert "value" not in Unavailable.__dataclass_fields__               # consumatorul nu poate atinge payload-ul
    assert set(Ok.__dataclass_fields__) == {"value", "as_of", "valid_until", "schema_hash"}


# ───────────────────────────── opportunity_id ─────────────────────────────
def test_new_id_not_a_function_of_bar_index() -> None:
    t = OpportunityTracker(w=3)
    o1 = t.step(100, close_prev=100.0, atr_prev=1.0, emitted=True)
    assert o1 is not None and o1.opportunity_id == "opp-00000001"        # contor surogat, NU „zone@100"
    assert o1.created_at == 100 and o1.state is OppState.DECIDED


def test_emission_in_band_refreshes_not_new_id_d7() -> None:
    t = OpportunityTracker(w=5)
    o1 = t.step(10, 100.0, 1.0, emitted=True)                            # anchor=100, band=1
    assert o1 is not None
    o2 = t.step(11, 100.4, 1.0, emitted=True)                            # în bandă (|100.4-100|<=1) → REFRESH
    assert o2 is None and t._counter == 1                                # NU un id nou (D7)
    assert t.open_opps[0].refresh_count == 1 and t.open_opps[0].last_seen == 11


def test_two_clocks_band_exit_economic_identity_survives() -> None:
    t = OpportunityTracker(w=5)                                          # identitate = created+6
    t.step(10, 100.0, 1.0, emitted=True)
    t.step(12, 103.0, 1.0, emitted=False)                               # |103-100|=3>1 → band_exit (economic)
    opp = t.open_opps[0]
    assert opp.band_exit_at == 12 and opp.state is not OppState.CLOSED   # ECONOMIC închis, IDENTITATEA supraviețuiește
    t.step(16, 103.0, 1.0, emitted=False)                               # j=16 >= deadline 10+5+1=16 → identity close
    assert t.open_opps == [] and t.closed_opps[0].close_reason == "expired_identity"


def test_frozen_band_does_not_widen_with_atr() -> None:
    t = OpportunityTracker(w=10)
    t.step(10, 100.0, 1.0, emitted=True)                                # band ÎNGHEȚAT = 1.0
    t.step(11, 101.5, 5.0, emitted=False)                              # ATR sare la 5, dar banda rămâne 1.0
    assert t.open_opps[0].band == 1.0 and t.open_opps[0].band_exit_at == 11   # |101.5-100|=1.5>1 → iese, nu se lărgește


def test_re_arm_beyond_w_reported_not_suppressed() -> None:
    t = OpportunityTracker(w=2)
    t.step(10, 100.0, 1.0, emitted=True)                                # deadline 13
    t.step(13, 100.0, 1.0, emitted=False)                              # identity close la 13
    o2 = t.step(15, 100.0, 1.0, emitted=True)                          # re-armare la aceeași ancoră, <=20 bare
    assert o2 is not None and t.re_arm_beyond_w == 1                    # id NOU, RAPORTAT (nu suprimat)
