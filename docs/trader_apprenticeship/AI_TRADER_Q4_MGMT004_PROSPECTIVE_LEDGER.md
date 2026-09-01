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

## TRADE #4 — S5 LONG, bar 1256 (2020-10-20 15:45:00 UTC)

```
ENTRY                 1908.914
RISK (1R)              9.468
STRUCTURAL_TARGET      1937.318 (unchanged in both tracks)
+1.0R_TRIGGER_LEVEL     1918.382
```

**TRIGGER**: bar 1297 (2020-10-21 14:45:00 UTC), close 1919.326, +1.1046R. Shadow stop moved to
breakeven (1908.914); control stop (1899.446) and target (1937.318) unchanged in both tracks.

```
TRACK      EXIT_BAR   EXIT_REASON   EXIT_PRICE   R_MULTIPLE
CONTROL    1304        MAX_HOLD      1917.711     +0.929
SHADOW     1304        MAX_HOLD      1917.711     +0.929
```

**DELTA_R (SHADOW - CONTROL) = 0.000.** The first instance where MGMT-004 made literally no
difference: after triggering at +1.10R, price never pulled back anywhere near the breakeven shadow
stop (closest approach post-trigger: +6.26pt / +0.66R of headroom) — both tracks rode the same
48-bar hold to the same max-hold close.

```
MGMT004_TRIGGERS_TOTAL_AFTER_THIS_TRADE = 2
Q4_PROSPECTIVE_DELTA_R_RUNNING_TOTAL = -0.651 + 0.000 = -0.651
```

## TRADE #12 — S5 LONG, bar 2352 (2020-11-05 13:45:00 UTC)

*(Retroactive completeness fix: this trigger was already committed to the durable engine state and
disclosed as a documentation gap during the 2026-08-30 CEO learning audit -- see that audit's Section
11 -- but had never received its formal write-up here. No new judgment is applied; the figures below
are pulled directly from the already-frozen `TRADE_CONTRACT`/outcome record in
`AI_TRADER_Q4_TRADE_EVIDENCE_LOG.md`.)*

```
ENTRY                 1931.738
RISK (1R)              6.798
STRUCTURAL_TARGET      1952.132 (unchanged in both tracks)
+1.0R_TRIGGER_LEVEL     1938.536
```

**TRIGGER**: bar 2357 (2020-11-05 15:30:00 UTC), close 1942.109, +1.5256R -- first M15 close at or
beyond +1.0R. Shadow stop moved to breakeven (1931.738); control stop (1924.940) and target
(1952.132) unchanged in both tracks.

```
TRACK      EXIT_BAR   EXIT_REASON   EXIT_PRICE   R_MULTIPLE
CONTROL    2362        TARGET        1952.132     +3.000
SHADOW     2362        TARGET        1952.132     +3.000
```

**DELTA_R (SHADOW - CONTROL) = 0.000.** Price never pulled back toward the breakeven shadow stop after
triggering at +1.53R -- it ran impulsively straight through to target four bars later (bar 2358 high
1948.303 on volume 2325). Both tracks converge, as at TRADE #4.

```
MGMT004_TRIGGERS_TOTAL_AFTER_THIS_TRADE = 3
Q4_PROSPECTIVE_DELTA_R_RUNNING_TOTAL = -0.651 + 0.000 = -0.651
```

## TRADE #25 — S5 LONG, bar 4079 (2020-12-02 15:45:00 UTC)

```
ENTRY                 1826.580
RISK (1R)              10.074
STRUCTURAL_TARGET      1856.802 (unchanged in both tracks)
+1.0R_TRIGGER_LEVEL     1836.654
```

**TRIGGER**: bar 4122 (2020-12-03 03:30:00 UTC), close 1837.41, +1.0750R -- first M15 close at or
beyond +1.0R. Shadow stop moved to breakeven (1826.580); control stop (1816.506) and target
(1856.802) unchanged in both tracks.

```
TRACK      EXIT_BAR   EXIT_REASON   EXIT_PRICE   R_MULTIPLE
CONTROL    4127        MAX_HOLD      1836.136     +0.9486
SHADOW     4127        MAX_HOLD      1836.136     +0.9486
```

**DELTA_R (SHADOW - CONTROL) = 0.000.** After triggering at +1.08R (bar 4122's high-water close for
the trade, +0.13R above where it eventually exited), price eased slightly but never pulled back
anywhere near the breakeven shadow stop before the 5-bar-later MAX_HOLD exit -- both tracks ride the
same short remainder of the hold to the same close. Third consecutive MGMT-004 convergence (matching
TRADE #4 and TRADE #12); the first Q4 divergence remains TRADE #1's -0.651R.

```
MGMT004_TRIGGERS_TOTAL_AFTER_THIS_TRADE = 4
Q4_PROSPECTIVE_DELTA_R_RUNNING_TOTAL = -0.651 + 0.000 + 0.000 = -0.651
```

## TRADE #26 — S5 LONG, bar 4347 (2020-12-07 13:45:00 UTC)

```
ENTRY                 1839.422
RISK (1R)              9.151
STRUCTURAL_TARGET      1866.875 (unchanged in both tracks)
+1.0R_TRIGGER_LEVEL     1848.573
```

**TRIGGER**: bar 4351 (2020-12-07 14:45:00 UTC), close 1856.722, +1.8905R -- first M15 close at or
beyond +1.0R. Shadow stop moved to breakeven (1839.422); control stop (1830.271) and target
(1866.875) unchanged in both tracks.

```
TRACK      EXIT_BAR   EXIT_REASON   EXIT_PRICE   R_MULTIPLE
CONTROL    4355        TARGET        1866.875     +3.000
SHADOW     4355        TARGET        1866.875     +3.000
```

**DELTA_R (SHADOW - CONTROL) = 0.000.** After triggering at +1.89R, price ran impulsively straight
through to target four bars later (bar 4352 high 1863.894 on volume 2602) -- both tracks converge, as
at TRADE #4 and TRADE #12.

```
MGMT004_TRIGGERS_TOTAL_AFTER_THIS_TRADE = 5
Q4_PROSPECTIVE_DELTA_R_RUNNING_TOTAL = -0.651 + 0.000 + 0.000 + 0.000 = -0.651
```
