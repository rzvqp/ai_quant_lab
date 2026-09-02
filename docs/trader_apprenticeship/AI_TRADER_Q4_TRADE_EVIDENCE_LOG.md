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
EXIT_BAR      1030 (2020-10-16 04:15:00-04:30:00 UTC)
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
SIGNAL_BAR              1256 (2020-10-20 14:45:00-15:00:00 UTC, NY session bis=8)
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
EXIT_BAR (both)  1304 (2020-10-21 03:45:00-04:00:00 UTC)
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
SIGNAL_BAR              1345 (2020-10-21 14:00:00-14:15:00 UTC, NY session bis=5)
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
SIGNAL_BAR              1353 (2020-10-21 16:00:00-16:15:00 UTC, bis=13, SAME session as TRADE #5)
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
SIGNAL_BAR    1896 (2020-10-29 13:45:00-14:00:00 UTC, bis=4)
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

**OUTCOME:** MAX_HOLD exit at bar 1944 (2020-10-30 03:00:00 UTC), price 1874.655 (bar's own close).
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
SIGNAL_BAR    2085 (2020-11-02 16:00:00-16:15:00 UTC, bis=13)
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

**OUTCOME:** MAX_HOLD exit at bar 2133 (2020-11-03 05:15:00 UTC), price 1892.602 (bar's own close).
```
EXIT_BAR      2133
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1892.602
R_MULTIPLE     -0.2597
```
Another choppy, directionless hold -- highest close of the whole 48-bar hold was 1897.678 (bar
2120), only +0.44R, well short of MGMT-004 (+1.0R = 1901.769). Never came close to the stop either.
No P007 candidates fired at any point during this hold (price never crossed the causal H1 EMA50).
One MAINTENANCE gap (GAP-172, bar 2108->2109, 60min, now at the post-DST 22:00-23:00Z slot) inside
the hold. Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 10
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.3376 - 0.2597 = -2.5973
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #11 — S5 opening-range-breakout LONG (bar 2175)

```
SIGNAL_BAR    2175 (2020-11-03 15:30:00-15:45:00 UTC, bis=11)
ENTRY          1908.178
INITIAL_STOP    1899.309 (= or_low 1899.329 - 2*TICK)
STRUCTURAL_TARGET 1934.785 (= entry + 3R, R=8.869)
```

**THESIS (frozen before bar 2176 was revealed):** mechanically triggered, no discretionary override.
Close 1908.178 > or_high 1908.064 within the entry window. Preceded by a steady ~15pt climb from bar
2134 (close 1892.602) to bar 2170 (close 1906.626), no P007 candidates fired anywhere in this
stretch. Volume picked up sharply in the final 5 bars (2171-2175: 1734/1516/1401/1018/1091, well
above the quieter climb's baseline), with a wider-range, more volatile character (bar 2173's 7.7pt
range, bar 2174's dip to 1902.806) -- this window falls on 2020-11-03/04 (US election date),
consistent with genuine elevated market activity around that date, though this thesis rests only on
the visible price/volume pattern, not on any assumed cause.

**INVALIDATION:** a close at or below 1899.309 (STOP). MAX_HOLD 48 bars from entry (through bar
2223). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1917.047).

**OUTCOME:** STOP hit at bar 2209 (2020-11-04 01:15:00 UTC), price 1899.309.
```
EXIT_BAR      2209
EXIT_REASON    STOP
EXIT_PRICE     1899.309
R_MULTIPLE     -1.0000
```
Came genuinely close to MGMT-004 first: the trade reached a high close of 1915.593 (bar 2205,
+0.83R) -- just short of the +1.0R trigger (1917.047) -- before reversing hard: bar 2206 close
1911.452, bar 2207 close 1908.75, bar 2208 close 1899.934 (essentially at the stop already). Bar
2209 then wicked violently -- low 1882.212, a ~22pt intrabar stop-run well below the stop level --
on the heaviest single-bar volume of the entire Q4 replay to date (4229, exceeding even
Q4-P007-015's 4017 capitulation bar), before closing back up at 1904.193. The stop was triggered by
that low, not the close (control logic checks bar.low against control_stop). No P007 candidate
opened despite the extreme wick -- the bar's CLOSE (1904.193) stayed above the causal H1 EMA50
throughout, since P007 only evaluates closes, not intrabar wicks. This bar falls on 2020-11-03
(US election night); the extreme volume/range is consistent with genuine market activity around
that date, noted factually and not as a causal claim. GAP-173 (standard, 60min) sat inside the hold,
standard. MGMT-004 never fired (never reached +1.0R). Trade mechanics ran unconditionally on every
bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 11
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.5973 - 1.0000 = -3.5973
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #12 — S5 opening-range-breakout LONG (bar 2352)

```
SIGNAL_BAR    2352 (2020-11-05 13:45:00-14:00:00 UTC, bis=4)
ENTRY          1931.738
INITIAL_STOP    1924.940 (= or_low 1924.96 - 2*TICK)
STRUCTURAL_TARGET 1952.132 (= entry + 3R, R=6.798)
```

**THESIS (frozen before bar 2353 was revealed):** mechanically triggered, no discretionary override.
Close 1931.738 > or_high 1930.356 within the entry window. Preceded by a sustained ~30.8pt climb
from bar 2284 (close 1899.552) to bar 2351 (close 1930.356) over 67 bars, no P007 candidates fired
anywhere in this stretch. Volume built steadily through the back half of the climb (614 at bar 2340
up to 1557 at bar 2347), including a genuine impulsive push at bar 2347 (+6.4pt in one bar, volume
1557). GAP-174 (standard, 60min) sat inside this stretch.

**INVALIDATION:** a close at or below 1924.940 (STOP). MAX_HOLD 48 bars from entry (through bar
2400). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1938.536).

**OUTCOME:** TARGET hit at bar 2362 (2020-11-05 16:30:00 UTC), price 1952.132.
```
EXIT_BAR      2362
EXIT_REASON    TARGET
EXIT_PRICE     1952.132
R_MULTIPLE     +3.0000
```
Clean, strong trade -- the first TARGET hit in Q4. After a brief pullback (bars 2353-2354, low
1927.004), price ran hard higher: bar 2357 jumped to close 1942.109 on volume 2226, crossing MGMT-004
(+1.0R = 1938.536, fired that bar). Continued impulsively through bar 2358 (high 1948.303, volume
2325) and touched target on bar 2362's high (1952.786 >= 1952.132). Both CONTROL and SHADOW ledgers
agree (TARGET, same bar, same price) since price never came back down toward the breakeven stop
after MGMT-004 fired. No P007 candidates during the hold; no gaps.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 12
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -3.5973 + 3.0000 = -0.5973
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #13 — S5 opening-range-breakout LONG (bar 2363)

```
SIGNAL_BAR    2363 (2020-11-05 16:30:00-16:45:00 UTC, bis=15)
ENTRY          1947.384
INITIAL_STOP    1924.940 (= or_low 1924.96 - 2*TICK -- SAME or_low as TRADE #12)
STRUCTURAL_TARGET 2014.716 (= entry + 3R, R=22.444)
```

**THESIS (frozen before bar 2364 was revealed):** mechanically triggered, no discretionary override.
Close 1947.384 > or_high 1930.356 within the entry window. Reuses the SAME opening range as TRADE
#12 (bars 2352-2355) -- verified against the canonical `S5OpeningRangeBreakoutLong.evaluate()`
(`s5_opening_range_breakout.py`) that this is legitimate, not a control-flow bug: the strategy's
`evaluate()` carries no memory of whether a signal already fired this session, it is purely reactive
to each bar's own (session, OR, bis, close) state. TRADE #12 had already closed (TARGET, bar 2362)
before this new trigger, so no position conflict. Continuation of the same impulsive rally that
produced TRADE #12's target. Because the stop is anchored to the same or_low, risk is unusually wide
this time (22.444 vs TRADE #12's 6.798).

**INVALIDATION:** a close at or below 1924.940 (STOP). MAX_HOLD 48 bars from entry (through bar
2411). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1969.828).

**OUTCOME:** MAX_HOLD exit at bar 2411 (2020-11-06 05:45:00 UTC), price 1939.4 (bar's own close).
```
EXIT_BAR      2411
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1939.4
R_MULTIPLE     -0.3557
```
Choppy, directionless hold given the unusually wide stop distance -- highest close of the whole
48-bar hold was only 1952.492 (bar 2375, +0.23R), nowhere near MGMT-004 (+1.0R = 1969.828). No P007
candidates fired at any point (price never crossed the causal H1 EMA50). One MAINTENANCE gap
(GAP-175, bar 2384->2385, 60min) inside the hold. Trade mechanics ran unconditionally on every bar
throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 13
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -0.5973 - 0.3557 = -0.9530
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #14 — S5 opening-range-breakout LONG (bar 2445)

```
SIGNAL_BAR    2445 (2020-11-06 14:00:00-14:15:00 UTC, bis=5)
ENTRY          1960.285
INITIAL_STOP    1948.100 (= or_low 1948.12 - 2*TICK)
STRUCTURAL_TARGET 1996.840 (= entry + 3R, R=12.185)
```

**THESIS (frozen before bar 2446 was revealed):** mechanically triggered, no discretionary override.
Close 1960.285 > or_high 1959.552 within the entry window. Preceded by a steady climb from bar 2412
(close 1939.4) to bar 2440 (close 1949.658), no P007 candidates fired anywhere in this stretch. OR
itself (bars 2440-2443) formed during a volatile stretch -- bar 2443 alone printed a 10pt range
(1949.635-1959.552) on volume 3737, the heaviest single-bar volume since TRADE #13's own hold. Entry
followed 2 more bars of continuation.

**INVALIDATION:** a close at or below 1948.100 (STOP). MAX_HOLD 48 bars from entry (through bar
2493). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1972.470).

**OUTCOME:** STOP hit at bar 2447 (2020-11-06 14:45:00 UTC), price 1948.100.
```
EXIT_BAR      2447
EXIT_REASON    STOP
EXIT_PRICE     1948.100
R_MULTIPLE     -1.0000
```
Fast reversal -- only 2 bars from entry to stop. Bar 2446 immediately faded (close 1953.562, volume
2625, well off the entry high). Bar 2447 broke straight through the stop (low 1944.758), volume 3507
-- heavy participation on the reversal, the opposite of the entry's own volume signature. MGMT-004
never came close to triggering. No P007 candidate opened despite the reversal (bar 2447's close,
1946.847, stayed on the correct side of the causal H1 EMA50).

```
TRADES_TOTAL_AFTER_THIS_TRADE = 14
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -0.9530 - 1.0000 = -1.9530
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #15 — S5 opening-range-breakout LONG (bar 2633)

```
SIGNAL_BAR    2633 (2020-11-10 15:00:00-15:15:00 UTC, bis=9)
ENTRY          1883.906
INITIAL_STOP    1873.664 (= or_low 1873.684 - 2*TICK)
STRUCTURAL_TARGET 1914.632 (= entry + 3R, R=10.242)
```

**THESIS (frozen before bar 2634 was revealed):** mechanically triggered, no discretionary override.
Close 1883.906 > or_high 1883.566 within the entry window. Entry sits inside the still-open,
unresolved Q4-P007-024 episode -- by far the largest of the entire Q4 replay: bar 2529 alone printed
a 38pt intrabar range on 8812 volume, the heaviest single-bar volume of the entire replay, followed
by many more bars of extreme sustained volume declining to a new Q4-replay-low of 1850.53 (bar
2548), an ~88pt decline from bar 2528's open. Price has since stabilized and ground back up over the
following ~85 bars. This LONG entry rides that stabilization mechanically, not a discretionary read
of it. GAP-177 (standard, 60min) sat inside the episode.

**INVALIDATION:** a close at or below 1873.664 (STOP) -- would mean the recovery failed and the
episode's decline resumed. MAX_HOLD 48 bars from entry (through bar 2681). MGMT-004 breakeven
trigger at first M15 close >= +1.0R (>= 1894.148).

**OUTCOME:** STOP hit at bar 2656 (2020-11-10 21:00:00 UTC), price 1873.664.
```
EXIT_BAR      2656
EXIT_REASON    STOP
EXIT_PRICE     1873.664
R_MULTIPLE     -1.0000
```
The invalidation played out exactly as flagged: the recovery attempt failed. Highest close of the
hold was only 1884.606 (bar 2637, +0.07R), then price ground steadily lower through bars 2650-2656
(1877.19 -> 1872.839) and breached the stop. MGMT-004 never came close. Q4-P007-024's gate remains
open as of this exit -- the episode's decline has resumed, not yet reclaimed.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 15
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -1.9530 - 1.0000 = -2.9530
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #16 — S5 opening-range-breakout LONG (bar 2813)

```
SIGNAL_BAR    2813 (2020-11-12 14:00:00-14:15:00 UTC, bis=5)
ENTRY          1877.526
INITIAL_STOP    1867.594 (= or_low 1867.614 - 2*TICK)
STRUCTURAL_TARGET 1907.322 (= entry + 3R, R=9.932)
```

**THESIS (frozen before bar 2814 was revealed):** mechanically triggered, no discretionary override.
Close 1877.526 > or_high 1874.703 within the entry window. This is the deferred S5 signal that first
surfaced on bar 2812 (Q4-P007-024's own reclaim bar) -- per the durable control-flow ordering
invariant, P007 reasoning took priority for that bar's commit, and S5's own stateless evaluate()
correctly re-checked and re-fired here on bar 2813 with a fresh entry price, exactly as expected --
confirms the deferral mechanism works as designed, no signal was lost. This entry sits immediately
after Q4-P007-024's massive 284-bar episode resolved SUPPORT at bar 2812.

**INVALIDATION:** a close at or below 1867.594 (STOP). MAX_HOLD 48 bars from entry (through bar
2861). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1887.458).

**OUTCOME:** MAX_HOLD exit at bar 2861 (2020-11-13 03:15:00 UTC), price 1878.474 (bar's own close).
```
EXIT_BAR      2861
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1878.474
R_MULTIPLE     +0.0954
```
Choppy, directionless hold -- highest close of the whole 48-bar hold was only 1881 (bar 2854, +0.35R),
well short of MGMT-004 (+1.0R = 1887.458). Never came close to the stop either. Six P007 candidates
(Q4-P007-025 through -029, all REJECTED) opened and resolved during this hold, one Q4-P007-020-style
dead-chop regime throughout -- trade mechanics ran unconditionally on every bar.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 16
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.9530 + 0.0954 = -2.8576
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #17 — S5 opening-range-breakout LONG (bar 2904)

```
SIGNAL_BAR    2904 (2020-11-13 13:45:00-14:00:00 UTC, bis=4)
ENTRY          1894.85
INITIAL_STOP    1884.336 (= or_low 1884.356 - 2*TICK)
STRUCTURAL_TARGET 1926.392 (= entry + 3R, R=10.514)
```

**THESIS (frozen before bar 2905 was revealed):** mechanically triggered, no discretionary override.
Close 1894.85 > or_high 1893.22 within the entry window. Preceded by a steady climb from ~1878-1880
(bars 2888-2895) to ~1885-1895 (bars 2900-2904), no P007 candidates fired anywhere in this stretch.
Volume picked up notably in the final approach (1136/840/1152/1303 across bars 2901-2904), well
above the quieter 200-600 range earlier.

**INVALIDATION:** a close at or below 1884.336 (STOP). MAX_HOLD 48 bars from entry (through bar
2952). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1905.364).

**OUTCOME:** MAX_HOLD exit at bar 2952 (2020-11-16 03:00:00 UTC), price 1895.383 (bar's own close).
```
EXIT_BAR      2952
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1895.383
R_MULTIPLE     +0.0507
```
Choppy, directionless hold -- highest close of the whole 48-bar hold was only 1898.768 (bar 2949,
+0.37R), well short of MGMT-004 (+1.0R = 1905.364). Never came close to the stop either. No P007
candidates fired at any point during this hold. One GAP-180 (standard weekend, 49h) sat inside the
hold, standard.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 17
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.8576 + 0.0507 = -2.8069
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #18 — S5 opening-range-breakout LONG (bar 2997)

```
SIGNAL_BAR    2997 (2020-11-16 13:45:00-14:00:00 UTC, bis=5)
ENTRY          1888.266
INITIAL_STOP    1871.904 (= or_low 1871.924 - 2*TICK)
STRUCTURAL_TARGET 1937.352 (= entry + 3R, R=16.362)
```

**THESIS (frozen before bar 2998 was revealed):** mechanically triggered, no discretionary override.
Close 1888.266 > or_high 1885.443 within the entry window. This is the deferred S5 signal that first
surfaced on bar 2996 (Q4-P007-033's own reclaim bar) -- P007 took priority per the durable
control-flow ordering invariant, and S5's stateless evaluate() correctly re-fired here with a fresh
entry price, the same deferral mechanism already validated after -024 (TRADE #16). This entry sits
immediately after Q4-P007-033's 8-bar episode resolved SUPPORT -- the reclaim rally continued through
bar 2997 (volume 1288, still elevated).

**INVALIDATION:** a close at or below 1871.904 (STOP). MAX_HOLD 48 bars from entry (through bar
3045). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1904.628).

**OUTCOME:** MAX_HOLD exit at bar 3045 (2020-11-17 03:15:00 UTC), price 1891.682 (bar's own close).
```
EXIT_BAR      3045
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1891.682
R_MULTIPLE     +0.2088
```
Choppy hold -- highest close of the whole 48-bar hold was only 1895.323 (bar 3008, +0.43R), well
short of MGMT-004 (+1.0R = 1904.628). Never came close to the stop either. No P007 candidates fired
at any point during this hold. One GAP-182 (standard, 60min) sat inside the hold, standard.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 18
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.8069 + 0.2088 = -2.5981
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #19 — S5 opening-range-breakout LONG (bar 3088)

```
SIGNAL_BAR    3088 (2020-11-17 13:30:00-13:45:00 UTC, bis=4)
ENTRY          1891.303
INITIAL_STOP    1886.330 (= or_low 1886.35 - 2*TICK)
STRUCTURAL_TARGET 1906.222 (= entry + 3R, R=4.973)
```

**THESIS (frozen before bar 3089 was revealed):** mechanically triggered, no discretionary override.
Close 1891.303 > or_high 1890.205 within the entry window. Follows immediately after Q4-P007-036's
reclaim (bar 3085), with volume staying elevated throughout the climb into this breakout (547/1007/
962/1344/1117 across bars 3084-3088), well above the 196-444 baseline seen earlier in this same
dead-chop stretch (-032 through -036).

**INVALIDATION:** a close at or below 1886.330 (STOP). MAX_HOLD 48 bars from entry (through bar
3136). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1896.276).

**OUTCOME:** STOP hit at bar 3091 (2020-11-17 14:30:00 UTC), low 1886.297 <= stop 1886.330.
```
EXIT_BAR      3091
EXIT_REASON    STOP
EXIT_PRICE     1886.330
R_MULTIPLE     -1.0000
```
A fast, clean stop-out over just 3 bars. Bar 3089 (close 1889.334) and bar 3090 (close 1889.102,
low 1886.47) both held above the stop; bar 3091's low wicked to 1886.297, triggering the stop on
the low (control logic checks bar.low against control_stop), before closing back up at 1889.206.
Never came close to MGMT-004 (+1.0R = 1896.276) -- the trade's high close across its life was
1889.334 (bar 3089), only +0.398R. No P007 candidate fired during the hold. No gap fell inside the
hold. Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 19
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.5981 - 1.0000 = -3.5981
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #20 — S5 opening-range-breakout LONG (bar 3092)

```
SIGNAL_BAR    3092 (2020-11-17 14:45:00-15:00:00 UTC, bis=8)
ENTRY          1890.787
INITIAL_STOP    1886.330 (= or_low 1886.35 - 2*TICK)
STRUCTURAL_TARGET 1904.158 (= entry + 3R, R=4.457)
```

**THESIS (frozen before bar 3093 was revealed):** mechanically triggered, no discretionary override.
Close 1890.787 > or_high 1890.205 within the entry window. Same opening range as TRADE #19 (or_high
1890.205, or_low 1886.35) -- S5's `evaluate()` is stateless per bar and legitimately re-fires on the
same OR once price reclaims or_high, as already validated twice earlier in Q4. This re-fire comes
one bar after TRADE #19 stopped out on a wick to 1886.297 (bar 3091), which closed back up at
1889.206; bar 3092 then reclaimed the range on volume 1266, comparable to bar 3091's 1265. No P007
candidate is active.

**INVALIDATION:** a close at or below 1886.330 (STOP). MAX_HOLD 48 bars from entry (through bar
3140). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1895.244).

**OUTCOME:** STOP hit at bar 3095 (2020-11-17 15:30:00 UTC), low 1884.739 <= stop 1886.330.
```
EXIT_BAR      3095
EXIT_REASON    STOP
EXIT_PRICE     1886.330
R_MULTIPLE     -1.0000
```
A second consecutive fast stop-out on the same OR, 3 bars after re-entry. Bar 3093 (close 1888.132,
low 1887.27) and bar 3094 (close 1887.4, low 1886.482, coinciding with Q4-P007-037's gate origin)
both held above the stop; bar 3095's low wicked to 1884.739 -- a genuine fresh extreme, deeper than
any low seen in this stretch including bar 3091's 1886.297 -- triggering the stop on the low, before
closing back up at 1887.42. Never came close to MGMT-004 (+1.0R = 1895.244) -- the trade's high
close across its life was 1890.787 (its own entry bar), 0R. Q4-P007-037 remains open and unresolved
(bar 3095 did not naturally reclaim the causal H1 EMA50); this fresh-extreme low is directly relevant
context for that episode's eventual resolution and will be weighed there, not here. No gap fell
inside the hold. Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 20
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -3.5981 - 1.0000 = -4.5981
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #21 — S5 opening-range-breakout LONG (bar 3181)

```
SIGNAL_BAR    3181 (2020-11-18 14:00:00-14:15:00 UTC, bis=5)
ENTRY          1877.656
INITIAL_STOP    1869.032 (= or_low 1869.052 - 2*TICK)
STRUCTURAL_TARGET 1903.528 (= entry + 3R, R=8.624)
```

**THESIS (frozen before bar 3182 was revealed):** mechanically triggered, no discretionary override.
Close 1877.656 > or_high 1876.22 within the entry window. This OR (bars 3177-3180, NY session
2020-11-18 13:00 UTC) formed during a recovery bounce off a sharp intraday selloff -- price fell from
~1887 near bar 3098 to a low of 1863.772 (bar 3173) over roughly 75 bars, with notably elevated
volume around bars 3172-3173 (1842, 2554) and again at bar 3179 (1353). Q4-P007-038 (gate origin bar
3097) has remained open and unresolved this entire time -- 84 bars without a natural reclaim of the
causal H1 EMA50 -- a notably long, seemingly genuine sustained break, still unresolved as this trade
opens. This is meaningfully different context from most prior S5 entries, which mostly followed
already-resolved/reclaimed P007 episodes or flat chop. Noted honestly as context; S5 fires
mechanically regardless of P007 state by design, and no discretionary override is being applied.

**INVALIDATION:** a close at or below 1869.032 (STOP). MAX_HOLD 48 bars from entry (through bar
3229). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1886.280).

**OUTCOME:** STOP hit at bar 3218 (2020-11-19 00:15:00 UTC), low 1868.97 <= stop 1869.032.
```
EXIT_BAR      3218
EXIT_REASON    STOP
EXIT_PRICE     1869.032
R_MULTIPLE     -1.0000
```
A 37-bar hold, the longest since TRADE #12's target hit. Price never got close to the target or to
MGMT-004: the high-water mark was bar 3186's close of 1883.53 (+0.68R), reached right as Q4-P007-038
resolved SUPPORT (see pattern ledger) -- short of the +1.0R breakeven trigger (1886.280). From there
price ground down steadily over the next ~32 bars (Q4-P007-039 opened and remained unresolved
throughout this entire hold) until bar 3218's low wicked to 1868.97, triggering the stop, before
closing at 1869.096. GAP-183 (standard, 60min MAINTENANCE) sat inside the hold. Trade mechanics ran
unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 21
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -4.5981 - 1.0000 = -5.5981
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #22 — S5 opening-range-breakout LONG (bar 3366)

```
SIGNAL_BAR    3366 (2020-11-20 14:15:00-14:30:00 UTC, bis=6)
ENTRY          1877.502
INITIAL_STOP    1865.688 (= or_low 1865.708 - 2*TICK)
STRUCTURAL_TARGET 1912.944 (= entry + 3R, R=11.814)
```

**THESIS (frozen before bar 3367 was revealed):** mechanically triggered, no discretionary override.
Close 1877.502 > or_high 1868.78 within the entry window. This is the deferred re-fire of the S5
signal that coincided with Q4-P007-039's reclaim on bar 3365 (position was FLAT at the time; P007
took priority per governance, and as expected the S5 signal re-surfaced on the very next bar via S5's
stateless evaluate()). Q4-P007-039 (gate origin bar 3187, 179 bars) resolved SUPPORT the prior bar --
a genuine, high-conviction case: a deep fresh extreme (low 1852.792), an extended ~93-bar basing
period at the new lower level, and a decisive, well-participated reclaim (bar 3365, ~10pt move,
volume 1698). This entry sits at the start of that reclaim move. Noted honestly as context; S5 fires
mechanically regardless of P007 classification, and no discretionary override is being applied.

**INVALIDATION:** a close at or below 1865.688 (STOP). MAX_HOLD 48 bars from entry (through bar
3414). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1889.316).

**OUTCOME:** MAX_HOLD exit at bar 3414 (2020-11-23 03:15:00 UTC), price 1873.152 (bar's own close).
```
EXIT_BAR      3414
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1873.152 (bar's own close)
R_MULTIPLE     -0.3683
```
The full 48-bar hold, never threatening either stop or target. The reclaim move that produced this
entry stalled almost immediately: best close was bar 3370's 1879.0 (+0.13R), reached within 4 bars of
entry, then price drifted lower for the rest of the hold, closing as low as bar 3394's 1870.628
(-0.58R) before recovering slightly into the MAX_HOLD exit. Never came close to MGMT-004 (+1.0R =
1889.316). GAP-185 (standard weekend, ~49h) sat inside the hold, standard zero-price-gap. Trade
mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 22
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -5.5981 - 0.3683 = -5.9664
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #23 — S5 opening-range-breakout LONG (bar 3889)

```
SIGNAL_BAR    3889 (2020-11-30 14:15:00-14:30:00 UTC, bis=6)
ENTRY          1776.695
INITIAL_STOP    1765.594 (= or_low 1765.614 - 2*TICK)
STRUCTURAL_TARGET 1809.998 (= entry + 3R, R=11.101)
```

**THESIS (frozen before bar 3890 was revealed):** mechanically triggered, no discretionary override.
Close 1776.695 > or_high 1772.901 within the entry window. This OR forms during a recovery bounce off
a fresh low (1764.57, bar 3843) made WITHIN Q4-P007-041's own still-open episode (gate origin bar
3710, now spanning 179+ bars) -- this low is deeper than -040's own historic 1800.424, another
confirmed multi-month extreme in the same ongoing structural decline. Bar 3843's low printed on
elevated volume (1328, then 1408 the next bar). Price then based/recovered from there into this
breakout. Noted honestly as context: this entry sits inside an episode that has not yet resolved,
riding a bounce within a still-unfolding, very large bearish structure, not a confirmed reversal. S5
fires mechanically regardless of P007 state, and no discretionary override is applied.

**INVALIDATION:** a close at or below 1765.594 (STOP). MAX_HOLD 48 bars from entry (through bar
3937). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1787.796).

**OUTCOME:** MAX_HOLD exit at bar 3937 (2020-12-01 03:15:00 UTC), price 1785.355 (bar's own close).
```
EXIT_BAR      3937
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1785.355 (bar's own close)
R_MULTIPLE     +0.7801
```
The full 48-bar hold, never threatening the stop. Choppy start -- worst close was bar 3890's 1770.074
(-0.60R), one bar into the trade -- before a steady grind higher for the rest of the hold. The
MAX_HOLD exit itself was the single best close of the entire trade (+0.78R), just short of MGMT-004's
+1.0R trigger (1787.796) -- never fired. GAP-191 (standard, 60min MAINTENANCE) sat inside the hold.
Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 23
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -5.9664 + 0.7801 = -5.1863
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #24 — S5 opening-range-breakout LONG (bar 3979)

```
SIGNAL_BAR    3979 (2020-12-01 13:45:00-14:00:00 UTC, bis=4)
ENTRY          1812.914
INITIAL_STOP    1804.892 (= or_low 1804.912 - 2*TICK)
STRUCTURAL_TARGET 1836.980 (= entry + 3R, R=8.022)
```

**THESIS (frozen before bar 3980 was revealed):** mechanically triggered, no discretionary override.
Close 1812.914 > or_high 1811.046 within the entry window. Follows a steady 27-bar recovery climb
since Q4-P007-042's REJECTED resolution (bar 3952) -- price grinded from ~1791 to ~1811 without any
further P007 breaks, consistent with the "calmer chop / recovery continuation" read noted in that
resolution. Volume picked up into the breakout (624/903/1182/890/1150 across bars 3975-3979), above
the quieter climb's baseline.

**INVALIDATION:** a close at or below 1804.892 (STOP). MAX_HOLD 48 bars from entry (through bar
4027). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1820.936).

**OUTCOME:** MAX_HOLD exit at bar 4027 (2020-12-02 02:45:00 UTC), price 1809.042 (bar's own close).
```
EXIT_BAR      4027
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1809.042 (bar's own close)
R_MULTIPLE     -0.4827
```
The full 48-bar hold, never threatening the stop. Best close was bar 3998's 1816.092 (+0.40R), well
short of MGMT-004's +1.0R trigger (1820.936), reached fairly early in the hold; worst close was bar
3985's 1806.586 (-0.79R), close to the stop but never breaching it. The trade drifted without
sustained direction for the rest of the hold before the MAX_HOLD exit. GAP-192 (standard, 60min
MAINTENANCE) sat inside the hold. Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 24
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -5.1863 - 0.4827 = -5.6690
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #25 — S5 opening-range-breakout LONG (bar 4079)

```
SIGNAL_BAR    4079 (2020-12-02 15:45:00-16:00:00 UTC, bis=12)
ENTRY          1826.580
INITIAL_STOP    1816.506 (= or_low 1816.526 - 2*TICK)
STRUCTURAL_TARGET 1856.802 (= entry + 3R, R=10.074)
```

**THESIS (frozen before bar 4080 was revealed):** mechanically triggered, no discretionary override.
Close 1826.58 > or_high 1826.36 within the entry window. Follows a choppy but net-positive stretch
since TRADE #24's MAX_HOLD close (bar 4028-4060 climbed to ~1828, pulled back to ~1818 by bar 4070),
then a renewed climb on rising volume into this breakout (1603/1327/1068/1130/1210/767 across bars
4074-4079). No P007 candidates fired anywhere in this stretch.

**INVALIDATION:** a close at or below 1816.506 (STOP). MAX_HOLD 48 bars from entry (through bar
4127). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1836.654).

**OUTCOME:** MGMT-004 fired at bar 4122 (2020-12-03 03:30:00 UTC), close 1837.41, +1.0750R (see
`AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md` for the full dual-track write-up). MAX_HOLD exit at bar
4127 (2020-12-03 04:45:00 UTC), price 1836.136 (bar's own close), both CONTROL and SHADOW tracks
identical.
```
EXIT_BAR      4127
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1836.136 (bar's own close)
R_MULTIPLE     +0.9486 (CONTROL basis)
```
A steady, unremarkable climb -- worst close was bar 4087's 1826.058, essentially flat (-0.05R), never
threatening the stop. MGMT-004 fired at bar 4122's +1.08R high-water close; price eased slightly but
never came back near the breakeven shadow stop before the MAX_HOLD exit 5 bars later, so CONTROL and
SHADOW converge. GAP-193 (standard, 60min MAINTENANCE) sat inside the hold. Trade mechanics ran
unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 25
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -5.6690 + 0.9486 = -4.7204
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #26 — S5 opening-range-breakout LONG (bar 4347)

```
SIGNAL_BAR    4347 (2020-12-07 13:45:00-14:00:00 UTC, bis=4)
ENTRY          1839.422
INITIAL_STOP    1830.271 (= or_low 1830.291 - 2*TICK)
STRUCTURAL_TARGET 1866.875 (= entry + 3R, R=9.151)
```

**THESIS (frozen before bar 4348 was revealed):** mechanically triggered, no discretionary override.
Close 1839.422 > or_high 1838.805 within the entry window. This entry rides the very start of the
Q4-P007-045 reclaim move (resolved bar 4345), a genuine capitulation-and-recovery structure: deepest
low 1822.253 (bar 4326) coincided with the episode's heaviest volume (2494), the classic PATTERN-007
SUPPORT signature. Volume built into this breakout (773 at bar 4346, 877 at bar 4347).

**INVALIDATION:** a close at or below 1830.271 (STOP). MAX_HOLD 48 bars from entry (through bar
4395). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1848.573).

**OUTCOME:** MGMT-004 fired at bar 4351 (2020-12-07 14:45:00 UTC), close 1856.722, +1.8905R. TARGET
hit at bar 4355 (2020-12-07 15:45:00 UTC), price 1866.875, both CONTROL and SHADOW tracks identical
(see `AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md` for the full dual-track write-up).
```
EXIT_BAR      4355
EXIT_REASON    TARGET
EXIT_PRICE     1866.875
R_MULTIPLE     +3.0000
```
A strong, clean trade -- the second TARGET hit since TRADE #12. Price ran hard almost immediately:
bar 4350 jumped to close 1845.852 on volume 1373, then bar 4351 jumped further to 1856.722 on volume
2204, crossing MGMT-004 (+1.0R = 1848.573, fired that bar). Continued impulsively through bar 4352
(high 1863.894, volume 2602) and touched target on bar 4355's high (1867.188 >= 1866.875). Both
CONTROL and SHADOW ledgers agree since price never came back down toward the breakeven stop after
MGMT-004 fired. No P007 candidates during the hold; no gaps.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 26
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -4.7204 + 3.0000 = -1.7204
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #27 — S5 opening-range-breakout LONG (bar 4356)

```
SIGNAL_BAR    4356 (2020-12-07 16:00:00-16:15:00 UTC, bis=13)
ENTRY          1865.800
INITIAL_STOP    1830.271 (= or_low 1830.291 - 2*TICK)
STRUCTURAL_TARGET 1972.387 (= entry + 3R, R=35.529)
```

**THESIS (frozen before bar 4357 was revealed):** mechanically triggered, no discretionary override.
Close 1865.8 > or_high 1838.805 within the entry window. Same opening range as TRADE #26 (or_high
1838.805, or_low 1830.291) -- a legitimate re-fire on the same OR immediately after TRADE #26 closed
via TARGET (bar 4355), matching S5's established stateless-evaluate() re-fire behavior already
validated multiple times earlier in Q4. Noted honestly: because so much of the move already happened
before this bar (bis=13, deep in the entry window), the stop distance back to or_low is unusually
wide -- R=35.529, by far the largest of any Q4 trade so far (previous widest was TRADE #21/#23's
~9-11). This is a mechanical consequence of the OR re-fire rule interacting with a strong runup, not a
discretionary sizing choice; no override is being applied.

**INVALIDATION:** a close at or below 1830.271 (STOP). MAX_HOLD 48 bars from entry (through bar
4404). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1901.329).

**OUTCOME:** MAX_HOLD exit at bar 4404 (2020-12-08 04:30:00 UTC), price 1868.604 (bar's own close).
```
EXIT_BAR      4404
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1868.604 (bar's own close)
R_MULTIPLE     +0.0789
```
As anticipated given the unusually wide risk (R=35.529), this trade essentially chopped sideways for
its entire hold and never came close to either boundary: best close was bar 4402's 1870.962 (+0.15R),
worst was bar 4392's 1862.966 (-0.08R) -- neither MGMT-004 (+1.0R = 1901.329) nor the stop (1830.271)
was ever seriously threatened. No gaps, no P007 candidates during the hold. A clean illustration that
a same-OR re-fire landing deep in the entry window (bis=13) produces a trade whose R-multiple outcomes
are compressed toward zero by construction, regardless of the underlying move's direction.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 27
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -1.7204 + 0.0789 = -1.6415
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #28 — S5 opening-range-breakout LONG (bar 4443)

```
SIGNAL_BAR    4443 (2020-12-08 14:15:00-14:30:00 UTC, bis=6)
ENTRY          1871.138
INITIAL_STOP    1861.502 (= or_low 1861.522 - 2*TICK)
STRUCTURAL_TARGET 1900.046 (= entry + 3R, R=9.636)
```

**THESIS (frozen before bar 4444 was revealed):** mechanically triggered, no discretionary override.
Close 1871.138 > or_high 1870.393 within the entry window. Follows a quiet drift down from ~1870 to
~1860-1863 (bars 4405-4438), then a sudden volatile push (bars 4439-4443, volume
1316/1362/1288/1210/702, range 1861.522-1872.712) that formed this OR and broke through it. No P007
candidates fired anywhere in this stretch.

**INVALIDATION:** a close at or below 1861.502 (STOP). MAX_HOLD 48 bars from entry (through bar
4491). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1880.774).

**OUTCOME:** STOP hit at bar 4491 (2020-12-09 03:15:00 UTC), low 1861.434 <= stop 1861.502 -- the
same bar as the MAX_HOLD boundary; the stop check took priority.
```
EXIT_BAR      4491
EXIT_REASON    STOP
EXIT_PRICE     1861.502
R_MULTIPLE     -1.0000
```
Best close was bar 4444's 1874.329 (+0.33R), reached one bar into the trade, then price drifted lower
for the rest of the hold, closing right at the stop level (bar 4491, exactly on the max_hold boundary)
after a wick down to 1861.434. Never came close to MGMT-004 (+1.0R = 1880.774). GAP-198 (standard,
75min MAINTENANCE) sat inside the hold. Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 28
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -1.6415 - 1.0000 = -2.6415
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #29 — S5 opening-range-breakout LONG (bar 4629)

```
SIGNAL_BAR    4629 (2020-12-10 14:45:00-15:00:00 UTC, bis=8)
ENTRY          1847.771
INITIAL_STOP    1834.287 (= or_low 1834.307 - 2*TICK)
STRUCTURAL_TARGET 1888.223 (= entry + 3R, R=13.484)
```

**THESIS (frozen before bar 4630 was revealed):** mechanically triggered, no discretionary override.
Close 1847.771 > or_high 1845.896 within the entry window. This is the deferred re-fire of the S5
signal that coincided with Q4-P007-052's SUPPORT reclaim on bar 4628, re-surfacing exactly as expected
on the very next bar via S5's stateless evaluate(). Q4-P007-052 (gate origin bar 4533, 96 bars)
resolved SUPPORT the prior bar -- a genuine, high-conviction case: a dramatic new low (1825.579),
massive volume near the break (3220), and a partial ~64% retracement over a substantial 96-bar
structural process. This entry rides the start of that reclaim move.

**INVALIDATION:** a close at or below 1834.287 (STOP). MAX_HOLD 48 bars from entry (through bar
4677). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1861.255).

**OUTCOME:** STOP hit at bar 4633 (2020-12-10 15:45:00 UTC), low 1833.92 <= stop 1834.287.
```
EXIT_BAR      4633
EXIT_REASON    STOP
EXIT_PRICE     1834.287
R_MULTIPLE     -1.0000
```
A fast, clean 4-bar stop-out. Price declined steadily from entry (1847.771) through bars 4630-4633
(1844.904/1840.952/1840.0/1835.56) without ever threatening MGMT-004 (+1.0R = 1861.255) -- the trade's
best close was its own entry bar. Q4-P007-053 (gate origin bar 4630) remains open/locked through this
decline; bar 4633's low (1833.92) is now deeper than -053's own gate-origin low (1842.92), relevant
context for that episode's eventual resolution. No gap fell inside the hold. Trade mechanics ran
unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 29
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -2.6415 - 1.0000 = -3.6415
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #30 — S5 opening-range-breakout LONG (bar 4717)

```
SIGNAL_BAR    4717 (2020-12-11 13:45:00-14:00:00 UTC, bis=4)
ENTRY          1840.106
INITIAL_STOP    1831.794 (= or_low 1831.814 - 2*TICK)
STRUCTURAL_TARGET 1865.042 (= entry + 3R, R=8.312)
```

**THESIS (frozen before bar 4718 was revealed):** mechanically triggered, no discretionary override.
Close 1840.106 > or_high 1839.878 within the entry window. Follows a recovery from bar 4707's deep low
(1824.184, heavy volume 1208) within Q4-P007-053's still-open episode (gate origin bar 4630, now
spanning 87 bars). Volume built into this breakout (1139/1164/1381/915 across bars 4714-4717). Noted
honestly: this entry sits inside an episode that has not yet resolved -- P007-053 has not naturally
reclaimed as of this bar. S5 fires mechanically regardless of P007 state; no discretionary override
applied.

**INVALIDATION:** a close at or below 1831.794 (STOP). MAX_HOLD 48 bars from entry (through bar
4765). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1848.418).

**OUTCOME:** MAX_HOLD exit at bar 4765 (2020-12-14 02:45:00 UTC), price 1837.191 (bar's own close).
```
EXIT_BAR      4765
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1837.191 (bar's own close)
R_MULTIPLE     -0.3507
```
The full 48-bar hold, never threatening the stop. Best close was bar 4739's 1840.4 (+0.04R), just one
bar into the trade, and never came close to MGMT-004; worst close was bar 4761's 1835.416 (-0.56R).
Q4-P007-056 (gate origin bar 4738) remained open/locked through the whole hold. GAP-201 (standard
weekend) sat inside the hold. Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 30
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -3.6415 - 0.3507 = -3.9922
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #31 — S5 opening-range-breakout LONG (bar 4809)

```
SIGNAL_BAR    4809 (2020-12-14 13:45:00-14:00:00 UTC, bis=4)
ENTRY          1832.711
INITIAL_STOP    1822.309 (= or_low 1822.329 - 2*TICK)
STRUCTURAL_TARGET 1863.917 (= entry + 3R, R=10.402)
```

**THESIS (frozen before bar 4810 was revealed):** mechanically triggered, no discretionary override.
Close 1832.711 > or_high 1827.892 within the entry window. Follows a gradual decline within
Q4-P007-056's still-open episode (gate origin bar 4738, now spanning 71 bars) to a fresh deep low
(1819.418, bar 4795), a bounce on heavy volume (1398, bar 4796), extended consolidation (1822-1828
range), then a decisive breakout on building volume (1073/1545/948/1150 across bars 4806-4809). Noted
honestly: this entry sits inside an episode that has not yet naturally reclaimed as of this bar. S5
fires mechanically regardless of P007 state; no discretionary override applied.

**INVALIDATION:** a close at or below 1822.309 (STOP). MAX_HOLD 48 bars from entry (through bar
4857). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1843.113).

**OUTCOME:** STOP hit at bar 4820 (2020-12-14 16:30:00 UTC), low 1822.282 <= stop 1822.309.
```
EXIT_BAR      4820
EXIT_REASON    STOP
EXIT_PRICE     1822.309
R_MULTIPLE     -1.0000
```
A steady, clean 7-bar decline, never threatening MGMT-004. Price ground down consistently from entry
(1832.711) through bars 4814-4820 without a meaningful bounce. Bar 4820's low (1822.282) sits just
above -056's own record low (1819.418), not exceeding it. Q4-P007-057 (gate origin bar 4813) remains
open/locked through this decline. No gap fell inside the hold. Trade mechanics ran unconditionally on
every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 31
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -3.9922 - 1.0000 = -4.9922
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #32 — S5 opening-range-breakout LONG (bar 4823)

```
SIGNAL_BAR    4823 (2020-12-14 17:15:00-17:30:00 UTC, bis=18)
ENTRY          1828.520
INITIAL_STOP    1822.309 (= or_low 1822.329 - 2*TICK)
STRUCTURAL_TARGET 1847.153 (= entry + 3R, R=6.211)
```

**THESIS (frozen before bar 4824 was revealed):** mechanically triggered, no discretionary override.
Close 1828.52 > or_high 1827.892 within the entry window. Same opening range as TRADE #31 (or_high
1827.892, or_low 1822.329) -- a legitimate re-fire on the same OR following TRADE #31's stop-out (bar
4820), matching S5's established stateless-evaluate() re-fire behavior. This entry sits inside
Q4-P007-057's still-open episode (gate origin bar 4813), which has not naturally reclaimed as of this
bar. No discretionary override applied.

**INVALIDATION:** a close at or below 1822.309 (STOP). MAX_HOLD 48 bars from entry (through bar
4871). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1834.731).

**OUTCOME:** MGMT-004 fired at bar 4862 (2020-12-15 04:00:00 UTC), close 1834.784, +1.0085R (see
`AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md` for the full dual-track write-up). MAX_HOLD exit at bar
4871 (2020-12-15 06:15:00 UTC), price 1839.062 (bar's own close), both CONTROL and SHADOW tracks
identical.
```
EXIT_BAR      4871
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1839.062 (bar's own close)
R_MULTIPLE     +1.6973 (CONTROL basis)
```
A strong trade -- price continued climbing steadily after MGMT-004 fired, reaching a best close of
1839.408 (+1.75R, bar 4868) before easing slightly into the MAX_HOLD exit. Never came back near the
breakeven shadow stop, so CONTROL and SHADOW converge. No gaps, no P007 candidates during the hold.
Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 32
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -4.9922 + 1.6973 = -3.2949
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #33 — S5 opening-range-breakout LONG (bar 5085)

```
SIGNAL_BAR    5085 (2020-12-17 13:45:00-14:00:00 UTC, bis=4)
ENTRY          1887.960
INITIAL_STOP    1874.371 (= or_low 1874.391 - 2*TICK)
STRUCTURAL_TARGET 1928.727 (= entry + 3R, R=13.589)
```

**THESIS (frozen before bar 5086 was revealed):** mechanically triggered, no discretionary override.
Close 1887.96 > or_high 1887.094 within the entry window. Follows a steady 69-bar climb from ~1862 to
~1888 (bars 5017-5084), with no P007 candidates firing anywhere in the stretch -- a genuine, sustained
trend rather than a choppy grind. Volume built steadily into the breakout
(887/991/1342/1568/1870/1637 across bars 5080-5085).

**INVALIDATION:** a close at or below 1874.371 (STOP). MAX_HOLD 48 bars from entry (through bar
5133). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1901.549).

**OUTCOME:** MAX_HOLD exit at bar 5133 (2020-12-18 02:45:00 UTC), price 1880.172 (bar's own close).
```
EXIT_BAR      5133
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1880.172 (bar's own close)
R_MULTIPLE     -0.5731
```
The full 48-bar hold, never threatening the stop. Best close was bar 5090's 1893.974 (+0.44R), reached
early in the hold and well short of MGMT-004 (+1.0R = 1901.549); worst close was bar 5130's 1879.566
(-0.62R), close to but not breaching the stop. GAP-205 (standard, 60min MAINTENANCE) sat inside the
hold. Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 33
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -3.2949 - 0.5731 = -3.8680
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #34 — S5 opening-range-breakout LONG (bar 5362)

```
SIGNAL_BAR    5362 (2020-12-22 14:00:00-14:15:00 UTC, bis=5)
ENTRY          1880.196
INITIAL_STOP    1871.150 (= or_low 1871.170 - 2*TICK)
STRUCTURAL_TARGET 1907.334 (= entry + 3R, R=9.046)
```

**THESIS (frozen before bar 5363 was revealed):** mechanically triggered, no discretionary override.
Close 1880.196 > or_high 1878.913, within the entry window (bis=5). Bar 5361, the first entry-window
bar, closed 1878.88 -- just below or_high, no trigger -- so this is the very next bar's clean
breakout. Signal fires one bar after Q4-P007-064 resolved SUPPORT (reclaim bar 5361), which itself
capped a genuine 37-bar sustained decline to a fresh multi-week local low (1866.794, bar 5334) on
real break-leg volume (1565). Volume on the signal bar itself (863) is real, consistent with the
broader episode's elevated regime rather than the earlier post-Dec-21 quiet stretch.

**INVALIDATION:** a close at or below 1871.150 (STOP). MAX_HOLD 48 bars from entry (through bar
5410). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1889.242).

**OUTCOME:** STOP hit at bar 5366 (2020-12-22 15:00:00 UTC), price 1871.150 (exact stop level).
```
EXIT_BAR      5366
EXIT_REASON    STOP
EXIT_PRICE     1871.150
R_MULTIPLE     -1.0000
```
A clean, fast -1R stop-out just 4 bars after entry -- no bounce, no hesitation. Bar 5364 (close
1873.596, volume 1568) broke decisively below entry and continued straight through toward the stop;
bar 5365 (close 1874.475) offered a brief pause but never approached breakeven; bar 5366 (close
1870.594, volume 1657) closed through the stop, triggering the exit at the exact stop price. MGMT-004
never fired (best close never approached +1.0R = 1889.242 -- the trade was never in meaningful
profit at any point). Q4-P007-065 (gate origin bar 5363, still open/unresolved at trade-close) was
running concurrently and unaffected by this trade's resolution -- both subsystems processed
independently per the durable control-flow ordering invariant.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 34
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -3.8680 - 1.0000 = -4.8680
POSITION_AFTER_THIS_TRADE = FLAT
```

## TRADE #35 — S5 opening-range-breakout LONG (bar 5457)

```
SIGNAL_BAR    5457 (2020-12-23 14:45:00-15:00:00 UTC, bis=8)
ENTRY          1876.580
INITIAL_STOP    1860.711 (= or_low 1860.731 - 2*TICK)
STRUCTURAL_TARGET 1924.187 (= entry + 3R, R=15.869)
```

**THESIS (frozen before bar 5458 was revealed):** mechanically triggered, no discretionary override.
Close 1876.58 > or_high 1869.184, within the entry window (bis=8). This is the deferred re-fire of
the coincident S5 signal first seen at bar 5456 (Q4-P007-065's own reclaim bar) -- per standing
priority, the P007 resolution was handled first at bar 5456 and the S5 signal re-fired on the very
next bar, exactly as at Q4-P007-039->TRADE #26 and Q4-P007-052->TRADE #29. Signal fires immediately
on the heels of Q4-P007-065's own SUPPORT resolution (93-bar episode, fresh multi-week low
1857.132, 77% partial retracement). Volume on the signal bar (1518) is real.

**INVALIDATION:** a close at or below 1860.711 (STOP). MAX_HOLD 48 bars from entry (through bar
5505). MGMT-004 breakeven trigger at first M15 close >= +1.0R (>= 1892.449).

**OUTCOME:** MAX_HOLD exit at bar 5505 (2020-12-24 03:45:00 UTC), price 1876.370 (bar's own close).
```
EXIT_BAR      5505
EXIT_REASON    MAX_HOLD
EXIT_PRICE     1876.370
R_MULTIPLE     -0.0132
```
An essentially flat 48-bar hold -- never threatened the stop (worst close 1871.64 at bar 5488,
~-0.31R) and never approached MGMT-004 (best close 1879.022 at bar 5500, ~+0.15R, well short of
+1.0R = 1892.449). Price chopped in a tight ~1870-1879 range for the entire hold, never developing
real direction either way. One MAINTENANCE gap (GAP-209, bar 5485->5486) inside the hold, standard.
No P007 candidates during the hold. Trade mechanics ran unconditionally on every bar throughout.

```
TRADES_TOTAL_AFTER_THIS_TRADE = 35
Q4_NET_R_AFTER_THIS_TRADE (control basis) = -4.8680 - 0.0132 = -4.8812
POSITION_AFTER_THIS_TRADE = FLAT
```
