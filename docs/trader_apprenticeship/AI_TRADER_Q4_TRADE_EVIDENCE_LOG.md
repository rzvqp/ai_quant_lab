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
