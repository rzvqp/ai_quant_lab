# AI_TRADER_Q4_TRADE_EVIDENCE_LOG

Paper/research-only Q4 apprenticeship trades. Every trade frozen under the full contract required
by `AI_TRADER_Q4_APPRENTICESHIP_V1` §8 BEFORE the next outcome bar. Entry logic is independent of
MGMT-004 (§9) — MGMT-004's shadow ledger is tracked separately in
`AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md`, never influencing whether/how a trade is taken.

---

## TRADE #1 — S5 opening-range-breakout LONG (bar 608)

```
STRATEGY               s5_c_2d587447_opening_range_breakout_long (rep_7472f3d412f2)
SIGNAL_BAR              608 (2020-10-09 13:45:00-13:59:59 UTC, NY session bis=4, first entry-window bar)
DIRECTION               LONG
ENTRY                   1923.31 (signal bar's own close, per TradeHypothesis.eligible_entry_timestamp
                        convention -- effectively fills at bar 609's open)
INITIAL_STOP             1916.671 (= or_low 1916.691 - 2*TICK, TICK=0.01, ratified RT-CODE-A-0007 value)
STRUCTURAL_TARGET         1943.227 (= entry + 3R, R=risk=6.639)
RISK (R)                 6.639
BASELINE_MANAGEMENT       hold to stop/target/max-hold per S5's own frozen exit spec (exit=rr3,
                          max_hold=48 M15 bars from the signal bar = bar 656); MGMT-004 tracked
                          separately, never influencing entry
INVALIDATION              1916.671 (= initial stop)
```

**THESIS (frozen before bar 609 was revealed):** mechanically triggered per the frozen S5 spec, no
discretionary override. Opening range formed bars 604-607 (or_high 1923.055, or_low 1916.691); bar
608 closed 1923.31, above or_high, in the entry window (bis=4). Descriptive context (not an input to
the signal): this bar sits within a strong, sustained rally following the Q4-P007-003 reclaim at bar
487 -- 74 consecutive bars closed above the causal H1 EMA50 by this point (one brief ~7-bar pullback
around bars 516-522 did not invalidate the reclaim), price climbing roughly 1892->1923 as the EMA
itself rose from 1891.7 to 1901.0. No new Q4 price/volume record set on this bar or in the preceding
stretch.

**OUTCOME (CONTROL — original stop/target, no management):**
```
EXIT_BAR      656 (2020-10-12 02:45:00-02:59:59 UTC)
EXIT_REASON    MAX_HOLD (neither stop nor target hit within 48 bars of the signal bar)
EXIT_PRICE     1927.632 (bar 656's own close, per the frozen force-close-at-max-hold rule)
R_MULTIPLE     +0.651
```
Full 48-bar path: price pushed as high as 1933.292 intrabar (bar 642, +1.50R) -- just over half
(50.1%) of the way to the +3R target (1943.227) -- but never closed or wicked far enough to trigger
it, then chopped in a 1920-1933 range for the remainder of the hold, closing the window at 1927.632.
Stop (1916.671) was never approached (closest low: bar 617's 1919.622, +2.95pt / +0.44R of stop
headroom at its narrowest). One weekend gap (GAP-157, bar 636->637) occurred inside the hold; per the frozen
max-hold convention (counted in M15 bars, not elapsed calendar time) this neither shortened nor
extended the effective window, and the gap's own zero-price-gap property meant it carried no
directional information either way.

**OUTCOME (MGMT-004 SHADOW — see `AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md` for the full
dual-track record):** MGMT-004 triggered at bar 636 (close 1930.521, +1.05R, first M15 close at or
beyond +1.0R); shadow stop moved to breakeven (1923.31); shadow stopped out at breakeven (R=0.0) at
bar 648 on a pullback low of 1922.4. MGMT-004 underperformed the control path on this instance
(0.0R vs. +0.651R) -- one data point, not by itself evidence for or against the candidate; see the
MGMT-004 ledger for the full, disclosed comparison.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 1
POSITION_AFTER_THIS_TRADE = FLAT (both control and shadow paths closed)
```

## TRADE #2 — S5 opening-range-breakout LONG (bar 884)

```
STRATEGY               s5_c_2d587447_opening_range_breakout_long (rep_7472f3d412f2)
SIGNAL_BAR              884 (2020-10-14 13:45:00-13:59:59 UTC, NY session bis=4)
DIRECTION               LONG
ENTRY                   1912.356
INITIAL_STOP             1904.96 (= or_low 1904.98 - 2*TICK)
STRUCTURAL_TARGET         1934.544 (= entry + 3R, R=7.396)
RISK (R)                 7.396
BASELINE_MANAGEMENT       hold to stop/target/max-hold per S5's frozen exit spec; MGMT-004 tracked
                          separately, never influencing entry
INVALIDATION              1904.96
```

**THESIS (frozen before bar 885 was revealed):** mechanically triggered, no discretionary override.
OR formed bars 880-883 (or_high 1909.755, or_low 1904.98); bar 884 closed 1912.356, above or_high, in
the entry window (bis=4). Descriptive context: this bar sits 6 bars after the Q4-P007-004 reclaim
(bar 878) -- itself the resolution of a 91-bar below-EMA pullback (bars 787-877, real/heavy peak
volume 4134 at bar 791) that had pulled back roughly 40pt off the bar-786 local high. No new Q4
price/volume record on this bar or the preceding stretch.

**OUTCOME:** stopped out at bar 892 (2020-10-14 15:45:00 UTC), low 1902.764 <= stop 1904.96.
```
EXIT_BAR      892
EXIT_REASON    STOP
EXIT_PRICE     1904.96
R_MULTIPLE     -1.000
```
A fast, clean loss -- 8 bars from entry to stop, price never closed back above the entry level after
bar 890's brief 1911-1912 push (high 1912.214, +0.05R short of the entry itself), then reversed
sharply on bar 892 (open 1909.212, low 1902.764, a 6.4pt intrabar range on real volume 1247) straight
through the stop. MGMT-004 never triggered (price never closed at or beyond +1.0R = 1919.752 at any
point in the hold) -- no shadow track to report.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 2
Q4_NET_R_AFTER_THIS_TRADE (control basis) = +0.651 + (-1.000) = -0.349
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #3 — S5 opening-range-breakout LONG (bar 982)

```
STRATEGY               s5_c_2d587447_opening_range_breakout_long (rep_7472f3d412f2)
SIGNAL_BAR              982 (2020-10-15 15:15:00-15:29:59 UTC, NY session bis=10 -- not the first
                        entry-window bar; OR was not broken until several bars into the session)
DIRECTION               LONG
ENTRY                   1904.62
INITIAL_STOP             1891.748 (= or_low 1891.768 - 2*TICK)
STRUCTURAL_TARGET         1943.236 (= entry + 3R, R=12.872)
RISK (R)                 12.872
INVALIDATION              1891.748
```

**THESIS (frozen before bar 983 was revealed):** mechanically triggered, no discretionary override.
Close 1904.62 > or_high 1900.22 within the bis 4-20 entry window (bis=10). Descriptive context: this
trigger follows TRADE #2's stop-out (bar 892, -1.0R) and a further below-EMA stretch that reclaimed
without reaching the batch runner's heavy-volume-crossing threshold. No new Q4 price/volume record.

**OUTCOME:** ran the full 48-bar hold, never threatening either stop or target.
```
EXIT_BAR      1030 (2020-10-16 15:15:00-15:29:59 UTC)
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1904.56
R_MULTIPLE     -0.005 (essentially flat)
```
Tight range throughout: max favorable excursion +0.46R (bar 1017, high 1910.574), max adverse
excursion -0.21R (bar 987, low 1901.862, +10.1pt / +0.79R of stop headroom at its narrowest). One
MAINTENANCE gap (GAP-160, bar 1004->1005) inside the hold, no directional information (zero-price-gap).
MGMT-004 never triggered (never reached +1.0R = 1917.492).

```
TRADES_TOTAL_AFTER_THIS_TRADE = 3
Q4_NET_R_AFTER_THIS_TRADE (control basis) = +0.651 - 1.000 - 0.005 = -0.354
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #4 — S5 opening-range-breakout LONG (bar 1256)

```
STRATEGY               s5_c_2d587447_opening_range_breakout_long (rep_7472f3d412f2)
SIGNAL_BAR              1256 (2020-10-20 15:45:00-15:59:59 UTC, NY session bis=8)
DIRECTION               LONG
ENTRY                   1908.914
INITIAL_STOP             1899.446 (= or_low 1899.466 - 2*TICK)
STRUCTURAL_TARGET         1937.318 (= entry + 3R, R=9.468)
RISK (R)                 9.468
INVALIDATION              1899.446
```

**THESIS (frozen before bar 1257 was revealed):** mechanically triggered, no discretionary override.
Close 1908.914 > or_high 1907.422 within the entry window (bis=8). Follows a quiet 226-bar
consolidation (bars 1031-1255, GAP-161 weekend + GAP-162 daily, no heavy-volume EMA crossing) after
TRADE #2/#3. No new Q4 price/volume record.

**OUTCOME (CONTROL and SHADOW converged):**
```
EXIT_BAR (both)  1304 (2020-10-21 15:45:00-15:59:59 UTC)
EXIT_REASON       MAX_HOLD (both tracks)
EXIT_PRICE        1917.711 (both tracks)
R_MULTIPLE        +0.929 (both tracks)
```
MGMT-004 triggered at bar 1297 (close 1919.326, +1.10R); shadow stop moved to breakeven (1908.914).
Price reached a maximum of +1.22R intrabar (bar 1298, high 1920.483 -- 40.7% of the way to target)
immediately after the trigger, then pulled back but never came close to testing the breakeven shadow
stop (closest approach after the trigger: bar low 1915.177, +6.26pt / +0.66R of headroom) -- **the
first instance where MGMT-004 made literally no difference to the outcome**, since the shadow stop
was never at risk of being touched. Both tracks closed identically at max-hold, +0.929R.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 4
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -0.354 + 0.929 = +0.575
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #5 — S5 opening-range-breakout LONG (bar 1345)

**METHODOLOGY NOTE:** the first trade evaluated under the new canonical
`reveal_next_bar_with_p007_gate()` path (CEO mandate, Red Team E110/`a2db277`) -- every bar leading
up to and monitoring this trade ran through the P007 gate as a structural part of the reveal, not a
separately-remembered step.

```
STRATEGY               s5_c_2d587447_opening_range_breakout_long (rep_7472f3d412f2)
SIGNAL_BAR              1345 (2020-10-23 15:30:00-15:44:59 UTC, NY session bis=5)
DIRECTION               LONG
ENTRY                   1928.046
INITIAL_STOP             1921.947 (= or_low 1921.967 - 2*TICK)
STRUCTURAL_TARGET         1946.343 (= entry + 3R, R=6.099)
RISK (R)                 6.099
INVALIDATION              1921.947
```

**THESIS (frozen before bar 1346 was revealed):** mechanically triggered, no discretionary override.
Close 1928.046 > or_high 1926.384 within the entry window (bis=5). P007 gate flagged no candidate in
bars 1310-1345. No new Q4 price/volume record.

**OUTCOME:** stopped out at bar 1350 (2020-10-21 15:15:00 UTC), low 1920.214 <= stop 1921.947.
```
EXIT_BAR      1350
EXIT_REASON    STOP
EXIT_PRICE     1921.947
R_MULTIPLE     -1.000
```
Fast loss -- 5 bars from entry to stop. Brief push to 1931.401 (bar 1347, +0.55R) before reversing
hard through bars 1348-1350 (real volume 1005/1500/1629) straight through the stop. MGMT-004 never
triggered (never reached +1.0R = 1934.145).

```
TRADES_TOTAL_AFTER_THIS_TRADE = 5
Q4_NET_R_AFTER_THIS_TRADE (control basis) = +0.575 - 1.000 = -0.425
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #6 — S5 opening-range-breakout LONG (bar 1353)

```
STRATEGY               s5_c_2d587447_opening_range_breakout_long (rep_7472f3d412f2)
SIGNAL_BAR              1353 (2020-10-21 15:45:00-15:59:59 UTC, bis=13, SAME session as TRADE #5)
DIRECTION               LONG
ENTRY                   1927.102
INITIAL_STOP             1921.947 (= or_low 1921.967 - 2*TICK, same OR as TRADE #5)
STRUCTURAL_TARGET         1942.567 (= entry + 3R, R=5.155)
INVALIDATION              1921.947
```

**THESIS (frozen before bar 1354 was revealed):** mechanically triggered, no discretionary override
-- a fresh, independent re-trigger of the same session's opening range (TRADE #5 had already closed
by bar 1350; the frozen S5 spec does not prohibit a second signal within the same bis 4-20 window).
No new Q4 price/volume record.

**OUTCOME:** stopped out at bar 1365, low 1921.814 <= stop 1921.947.
```
EXIT_BAR      1365
EXIT_REASON    STOP
EXIT_PRICE     1921.947
R_MULTIPLE     -1.000
```
Max favorable excursion +0.44R (bar 1354, high 1929.393) immediately after entry, then a slow,
grinding decline over 11 bars straight through the stop -- no gaps, no dramatic single-bar move,
just sustained real selling. MGMT-004 never triggered (never reached +1.0R = 1932.257).

```
TRADES_TOTAL_AFTER_THIS_TRADE = 6
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -0.425 - 1.000 = -1.425
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #7 — S5 opening-range-breakout LONG (bar 1621)

```
SIGNAL_BAR    1621 (2020-10-26 14:00:00-14:14:59 UTC, bis=5)
ENTRY          1905.948
INITIAL_STOP    1900.046 (= or_low 1900.066 - 2*TICK)
STRUCTURAL_TARGET 1923.654 (= entry + 3R, R=5.902)
```

**THESIS (frozen before bar 1622 was revealed):** mechanically triggered, no discretionary override.
Close 1905.948 > or_high 1905.344 within the entry window. Preceded by an extended choppy stretch
(bars ~1509-1620) with many individually-reasoned P007 candidates, none affecting S5 eligibility.

**OUTCOME:** stopped out at bar 1625 (2020-10-26 15:00:00 UTC), low 1898.962 <= stop 1900.046.
```
EXIT_BAR      1625
EXIT_REASON    STOP
EXIT_PRICE     1900.046
R_MULTIPLE     -1.000
```
Fast loss -- 4 bars from entry to stop, price never closed back above entry after the signal bar,
declining steadily through bars 1622-1625 (real volume throughout, 1040-1759) straight through the
stop. MGMT-004 never triggered. Note: bar 1624 (inside this trade's hold) also carried a P007
candidate (gap -0.23pt, vol 1125, REJECTED) -- the trade's own stop/target were manually verified
safe for that bar before the P007 decision was committed (see `AI_TRADER_Q4_M15_LOG.md`), since the
runner's control flow evaluates P007 signals before its trade-monitoring block.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 7
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -1.425 - 1.000 = -2.425
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #8 — S5 opening-range-breakout LONG (bar 1718)

**Opened via the durable control flow (`ai_trader/csv_causal_replay/q4_control_flow.py`, commit
`44aee88`) for the first time in production.**

```
SIGNAL_BAR    1718 (2020-10-27 15:15:00-15:29:59 UTC, bis=10)
ENTRY          1908.268
INITIAL_STOP    1902.110 (= or_low 1902.13 - 2*TICK)
STRUCTURAL_TARGET 1926.742 (= entry + 3R, R=6.158)
```

**THESIS (frozen before bar 1719 was revealed):** mechanically triggered, no discretionary override.
Close 1908.268 > or_high 1907.636 within the entry window. OR formed by bars 1708-1711 -- the exact
same 4 bars as Q4-P007-010's reclaim (bar 1708) and Q4-P007-011's full episode (bars 1710-1711);
or_low 1902.13 is bar 1711's own intrabar low, printed during -011's brief dip-and-reverse. Entry
window bars 1712-1717 stayed below or_high (max close 1906.822 at bar 1713) before bar 1718 broke
out on moderate volume (545, in line with the session's 500-900 baseline).

**INVALIDATION:** a close at or below 1902.110 (STOP). MAX_HOLD 48 bars from entry (through bar
1766) if neither stop nor target is hit first. MGMT-004 breakeven trigger at first M15 close >=
+1.0R (>= 1914.426).

**OUTCOME:** MAX_HOLD exit at bar 1766 (2020-10-28 04:15:00 UTC), price 1907.376 (bar's own close).
```
EXIT_BAR      1766
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1907.376
R_MULTIPLE     -0.1449
```
Choppy, directionless hold -- price never closed within 1R of target (highest close of the whole
48-bar hold was 1910.802 at bar 1727, only +0.42R) and MGMT-004 never triggered. Never came within
0.403pt of the stop either (closest approach: bar 1749's low 1902.513, part of Q4-P007-013's episode,
itself REJECTED as a spike/reversal). Four P007 candidates opened and resolved during this hold
(Q4-P007-012 through -014 REJECTED; -013 tested the stop closely but never touched it) -- trade
mechanics ran unconditionally on every bar throughout, confirmed via `open_trade_state.json` staying
untouched (mgmt004_fired/control_closed both false) until the MAX_HOLD exit itself.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 8
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.425 - 0.1449 = -2.5699
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #9 — S5 opening-range-breakout LONG (bar 1896)

```
SIGNAL_BAR    1896 (2020-10-29 01:00:00-01:14:59 UTC, bis=4)
ENTRY          1871.904
INITIAL_STOP    1860.060 (= or_low 1860.08 - 2*TICK)
STRUCTURAL_TARGET 1907.436 (= entry + 3R, R=11.844)
```

**THESIS (frozen before bar 1897 was revealed):** mechanically triggered, no discretionary override.
Close 1871.904 > or_high 1871.519 within the entry window. This entry sits at the tail of the
single largest directional move of Q4 so far: price fell from ~1902.7 (bar 1782, the same bar that
opened the still-unresolved Q4-P007-015 gate) to a new Q4-replay-low of 1860.08 (bar 1893) -- a
~42.6pt decline over 111 bars, punctuated by a fast ~20pt leg in the first 18 bars, an ~80-bar
consolidation around 1877-1882, then a final capitulation leg (bars 1890-1893, volume 1594-1817) to
the low. Bars 1894-1896 then reversed sharply on the heaviest volume of the whole Q4 replay to date
(1306/4017/3396) -- the OR itself (bars 1892-1895) spans the capitulation low and the first violent
bounce bar.

**INVALIDATION:** a close at or below 1860.060 (STOP) -- would mean the reversal failed and the
capitulation low was retested/broken. MAX_HOLD 48 bars from entry (through bar 1944). MGMT-004
breakeven trigger at first M15 close >= +1.0R (>= 1883.748).

**NOTE:** Q4-P007-015 (gate-origin bar 1782, the same bar this decline began) remains open and
unresolved as of TRADE #9's entry -- price has never closed back above the causal H1 EMA50 since.
Both subsystems are being tracked independently per the durable control-flow ordering invariant; see
`AI_TRADER_Q4_PATTERN_LEDGER.md`.

**OUTCOME:** MAX_HOLD exit at bar 1944 (2020-10-30 09:00:00 UTC), price 1874.655 (bar's own close).
```
EXIT_BAR      1944
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1874.655
R_MULTIPLE     +0.2323
```
The violent reversal (bars 1894-1896) fizzled into a tight range -- price oscillated between
~1866 and ~1876 for the entire 48-bar hold, never closing more than +0.38R above entry (max close
1876.396, bar 1899) and never coming close to MGMT-004 (+1.0R = 1883.748) or the stop (1860.06,
never within ~6pt after entry). Q4-P007-015 remained open throughout this entire hold too -- price
never closed back above the causal H1 EMA50 at any point across TRADE #9's 48 bars. One MAINTENANCE
gap (GAP-170, bar 1924->1925, 60min) inside the hold. Trade mechanics ran unconditionally on every
bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 9
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.5699 + 0.2323 = -2.3376
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #10 — S5 opening-range-breakout LONG (bar 2085)

```
SIGNAL_BAR    2085 (2020-11-02 15:15:00-15:29:59 UTC, bis=13)
ENTRY          1894.492
INITIAL_STOP    1887.215 (= or_low 1887.235 - 2*TICK)
STRUCTURAL_TARGET 1916.323 (= entry + 3R, R=7.277)
```

**THESIS (frozen before bar 2086 was revealed):** mechanically triggered, no discretionary override.
Close 1894.492 > or_high 1893.136 within the entry window. Preceded by a steady, unremarkable
~58-bar grind higher from bar 2027's reclaim (close ~1879.5) to ~1890 (bars 2060-2084) -- no P007
candidates fired anywhere in this stretch, price stayed comfortably above the causal H1 EMA50
throughout. Volume picked up notably in the final approach (bars 2080-2085: 1189/1332/941/1021/622/
826), consistent with a genuine breakout rather than a random poke through the range.

**INVALIDATION:** a close at or below 1887.215 (STOP). MAX_HOLD 48 bars from entry (through bar
2133). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1901.769).
