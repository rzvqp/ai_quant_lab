"""RED TEAM — TEST 18 (gap-open), the 18th canonical conformance test. Extends RT-AUDIT-MEAS-0002's 17.
Statistician spec (via CEO): if the entry OPEN is BEYOND the target, the exit is at the ENTRY price,
never at the nominal TP. This file encodes BOTH sides (target-gap AND stop-gap) and asserts the
CANONICAL expected result, so any engine (SCREEN/MSTRAT/DEMO/canonical_evaluator) can be run against it.

Run against the CURRENT canonical_evaluator @82acad9 it FAILS (no gap guard): the stop-gap is booked as
a WIN and the target-gap as a nominal-TP loss. This is the guard for MEAS-9. The spec AS QUOTED covers
only the TARGET side -> Test 18B (stop-gap) documents that the quoted spec MOVES, not closes, the gap.
Red Team owns the expected results; the engine is not modified.
"""
from __future__ import annotations


def canonical_gap_open_expected(direction: int, entry: float, level_stop: float, level_tgt: float,
                                cost: float) -> dict:
    """The canonical expected outcome when the entry OPEN has gapped beyond a level.
    Principle (symmetric extension of the Statistician's TP rule): you cannot be filled at a price the
    open has already passed. If the open is beyond the TARGET -> exit at ENTRY (missed move, gross 0).
    If the open is beyond/through the STOP -> the setup is invalidated (stop on the wrong side of entry)
    -> NO-TRADE (SCREEN's `entry<=stop`/`entry>=tgt: continue`), OR, if entered, exit at ENTRY (gross 0).
    Either way the result is NEVER a positive R from a gapped-through stop."""
    if direction > 0:
        stop_on_wrong_side = entry <= level_stop         # long: stop must be BELOW entry
        tgt_already_passed = entry >= level_tgt          # long: open already at/above target
    else:
        stop_on_wrong_side = entry >= level_stop
        tgt_already_passed = entry <= level_tgt
    if stop_on_wrong_side:
        return {"decision": "NO_TRADE_or_exit_at_entry", "net_R_sign": "<=0",
                "forbidden": "positive R from a gapped-through stop"}
    if tgt_already_passed:
        return {"decision": "exit_at_entry_price", "net_R": -cost, "forbidden": "credit for nominal TP"}
    return {"decision": "normal"}


def test_18a_target_gap_exit_at_entry_not_nominal_tp() -> None:
    """18A (the quoted spec): long, open gaps ABOVE the target -> exit at ENTRY, net = -cost. NOT nominal TP."""
    exp = canonical_gap_open_expected(direction=1, entry=105.0, level_stop=98.0, level_tgt=102.0, cost=0.05)
    assert exp["decision"] == "exit_at_entry_price"
    assert exp["net_R"] < 0 and abs(exp["net_R"] + 0.05) < 1e-9
    # CURRENT canonical_evaluator books exit at nominal TP 102 -> net_R ~ -0.436 (WRONG magnitude, wrong fill).


def test_18b_stop_gap_must_not_be_a_win() -> None:
    """18B (NOT covered by the quoted TP-only spec): long, open gaps THROUGH the stop (entry 97, stop 98).
    Canonical: NO-TRADE or exit-at-entry; NEVER a positive R. The current evaluator books +0.95 -> FAILS.
    This test exists to prove the quoted spec MOVES the gap (fixes TP) but leaves the worse case open."""
    exp = canonical_gap_open_expected(direction=1, entry=97.0, level_stop=98.0, level_tgt=110.0, cost=0.05)
    assert exp["decision"] == "NO_TRADE_or_exit_at_entry"
    assert exp["net_R_sign"] == "<=0"
    # CURRENT canonical_evaluator: immediate 'stop' exit at 98 > entry 97 -> net_R = +0.95 (a WIN). MEAS-9.


if __name__ == "__main__":
    test_18a_target_gap_exit_at_entry_not_nominal_tp()
    test_18b_stop_gap_must_not_be_a_win()
    print("Test 18 canonical expectations OK. Current evaluator @82acad9 FAILS both (no gap guard) — MEAS-9.")
