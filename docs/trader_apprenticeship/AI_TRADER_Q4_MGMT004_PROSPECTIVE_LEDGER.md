# AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER

Dual-track (CONTROL vs. MGMT-004 SHADOW) outcome ledger for every MGMT-004-eligible Q4 trade, per
`AI_TRADER_Q4_APPRENTICESHIP_V1` §10-12. **MGMT-004 is used exactly as frozen in
`AI_TRADER_Q4_MANAGEMENT_PROSPECTIVE_PROTOCOL_V1.md`** — trigger = first M15 close at or beyond
+1.0R favorable excursion; action = move stop to breakeven (entry price); no threshold adjustment,
no session/direction/volatility variation, no post-outcome exception, for any trade, for any reason.

Frozen protocol re-stated here for reference (not redefined):
```
TRIGGER      = first M15 close >= +1.0R favorable excursion from entry
STOP_CHANGE  = move stop to exactly entry price (0R)
TARGET_RULE  = unchanged from the original trade's own structural target
COST_MODEL   = no incremental transaction (single stop-level change)
```

---

## TRADE #1 — S5 LONG, bar 608 (2020-10-09 13:45:00 UTC)

```
ENTRY                 1923.31
RISK (1R)              6.639
STRUCTURAL_TARGET      1943.227 (unchanged in both tracks, per frozen TARGET_RULE)
+1.0R_TRIGGER_LEVEL     1929.949
```

**MGMT-004 eligibility**: YES (a real trade exists; frozen protocol applies automatically, entry
logic was frozen before any MGMT-004 consideration — see `AI_TRADER_Q4_TRADE_EVIDENCE_LOG.md`).

**TRIGGER**: bar 636 (2020-10-09 20:45:00 UTC), close 1930.521, +1.0546R — first M15 close at or
beyond +1.0R. Committed via `commit_decision(decision_type="MGMT004_TRIGGER", trade_bar_id=608,
r_multiple_reached=1.0546)`. Shadow stop moved to breakeven (1923.31) at this bar; control stop
(1916.671) and structural target (1943.227) unchanged in both tracks per the frozen rule.

```
TRACK      EXIT_BAR   EXIT_REASON   EXIT_PRICE   R_MULTIPLE
CONTROL    656         MAX_HOLD      1927.632     +0.651
SHADOW     648         STOP          1923.31      0.000
```

**DELTA_R (SHADOW - CONTROL) = -0.651.** MGMT-004 underperformed the control on this instance: after
triggering at +1.05R, price pulled back to touch the breakeven shadow stop at bar 648 (low 1922.4,
8 bars after the trigger), while the control path — never having moved its stop — rode out that same
pullback (which never reached the original 1916.671 stop, closest approach bar 617's 1919.622,
+0.44R of headroom) and the subsequent chop, closing the 48-bar hold at +0.651R via max-hold. The
same price path that stopped the shadow at breakeven never threatened the control's wider stop.

**Not treated as evidence for or against MGMT-004 on its own** — this is a single prospective data
point (n=1 in Q4, joining the n=4 Q1-Q3 discovery-stage evidence per
`AI_TRADER_MANAGEMENT_EXIT_RESEARCH_V1.md`). No threshold, session, or protocol adjustment was made
in response to this outcome, per the frozen protocol's own "no post-outcome exception" clause.

```
MGMT004_TRIGGERS_TOTAL_AFTER_THIS_TRADE = 1
Q4_PROSPECTIVE_DELTA_R_RUNNING_TOTAL = -0.651
```
