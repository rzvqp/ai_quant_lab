# AI TRADER Q3/Q4 OPERATING STANDARD V1

Installed by direct CEO mandate (real-time), immediately following the FINAL
`TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md`. **Prospective from Q3 onward only.** Does not alter,
rescore, renumber, or reinterpret any Q1/Q2 trade. Q2's 66 trades (17 structured-comparable) are
frozen as the historical learning baseline — see §1.

---

## 1. Q2 baseline freeze

```
Q2_BASELINE_FROZEN            = YES
Q2_TOTAL_TRADES                = 66
Q2_STRUCTURED_COMPARABLE_TRADES = 17
```

All 66 Q2 trades are preserved permanently in `TRADE_EVIDENCE_LOG.md`, `STRATEGY_EVIDENCE_DENOMINATOR.md`,
`2020_Q2_H4_LOG.md`, and `TRADER_KNOWLEDGE_CHECKPOINT_2020_Q2.md` (`STATUS: FINAL`) exactly as
finalized. Nothing in those files is edited by this mandate. The trader's accumulated experience
carries forward in full — this is a **performance-counter reset, not a knowledge reset**:

- `AI_TRADER_MARKET_READING_LIBRARY_V1.md` — carries forward unchanged.
- Recurring observations, trader lessons, trader mistakes, correct no-trades, missed
  opportunities — all carry forward (see `AI_TRADER_EXPERIENCE_LEDGER.md` and the Q1/Q2 checkpoint
  appendices).
- Playbooks A (retired), A-prime, B — carry forward as-is; Q3 evidence accumulates onto them
  going forward, it does not retroactively re-fit them against Q2 outcomes (§18 below).
- Regime knowledge (`AI_TRADER_REGIME_STRATEGY_MATRIX.md`), Multi-Timeframe Alignment knowledge,
  external-watchlist observations, developing strategy hypotheses — all carry forward unchanged.

## 2. Quarterly trade identities

Q3 trade counter starts at zero. Every new trade gets a `QUARTER_TRADE_ID` (`Q3-001`, `Q3-002`,
...) as primary, plus a `LIFETIME_TRADE_ID` (continuing from 67) for audit traceability only.
**Quarterly statistics use the quarterly cohort exclusively** — Q2 trades never enter Q3 totals,
Q3 trades never enter Q4 totals.

```
Q3_TRADE_COUNT   = 0
NEXT_TRADE_ID    = Q3-001
LIFETIME_NEXT_ID = 67
```

At Q4 authorization: `Q4_TRADE_COUNT = 0`, first trade `Q4-001`, lifetime numbering continues.

## 3. Purpose

Enable an honest Q2-vs-Q3(-vs-Q4) improvement audit, not defined by win rate alone. Minimum
tracked metrics per cohort: TRADE_COUNT, WINS, LOSSES, WIN_RATE, NET_PIPS, NET_R, AVG_R_PER_TRADE,
MEDIAN_R, PROFIT_FACTOR, MAX_DRAWDOWN, AVG_WIN_R, AVG_LOSS_R, AVG_PLANNED_RR, AVG_REALIZED_RR, MFE,
MAE, LONG_PERFORMANCE, SHORT_PERFORMANCE, REGIME_PERFORMANCE,
MULTITIMEFRAME_ALIGNMENT_PERFORMANCE, PLAYBOOK_PERFORMANCE, CORRECT_NO_TRADES,
MISSED_OPPORTUNITIES, PROCESS_ERRORS, STRATEGY_CANDIDATES_CREATED.

## 4. XAUUSD pip accounting standard V1

Primary distance/result unit from Q3 onward is **pips**, not raw points.

```
0.10 price movement = 1 pip
1.00 price movement = 10 pips
PIPS = ABS(PRICE_B - PRICE_A) * 10
LONG:  RESULT_PIPS = (EXIT - ENTRY) * 10
SHORT: RESULT_PIPS = (ENTRY - EXIT) * 10
```

Raw price displacement retained as secondary audit info only. All Q3+ trade evidence and
checkpoint reports lead with pips.

## 5. Project pip value standard (reporting only)

```
1 pip @ 1.00 lot = $10
1 pip @ 0.10 lot = $1
1 pip @ 0.01 lot = $0.10
RESULT_USD = RESULT_PIPS * 10 * LOT_SIZE
```

This is the AI Quant Lab **reporting** convention only. Real broker execution/risk sizing (if ever
involved — it is not, in this apprenticeship) must respect the actual MT5 contract spec; this
convention never silently substitutes for real broker economics.

## 6. Required trade reporting fields (Q3+)

`QUARTER_TRADE_ID`, `LIFETIME_TRADE_ID`, `DIRECTION`, `ENTRY_PRICE`, `INITIAL_STOP_PRICE`,
`INITIAL_RISK_PIPS`, `STRUCTURAL_TARGET_1/2/3` (as applicable), `EXECUTABLE_TP1/2/3`,
`TP1/2/3_DISTANCE_PIPS`, `TP1/2/3_RR`, `MFE_PIPS`, `MAE_PIPS`, `RESULT_PIPS`, `RESULT_R`, and
modeled `RESULT_USD` when a lot size is defined.

## 7. Structural-first target selection

Order of reasoning is always **MARKET STRUCTURE → TARGET → RR CALCULATION → TRADE QUALITY
DECISION**, never the reverse. Valid target anchors: swing high/low, support/resistance,
liquidity pool, session high/low, range boundary, H1 structure, M15 structure, next clear
opposing reaction zone, price-discovery objective where justified. Never invent structure to hit
a desired RR.

## 8–9. TP Execution Buffer V1 (unchanged mechanism, now pip-denominated; TP only, never SL)

```
TP_EXECUTION_BUFFER = 10 pips = 1.00 price point
SHORT: EXECUTABLE_TP = STRUCTURAL_TARGET + 10 pips
LONG:  EXECUTABLE_TP = STRUCTURAL_TARGET - 10 pips
```

The structural target is retained separately for research. SL is never adjusted by this buffer —
SL remains genuine structural invalidation only. **Not applied retrospectively to Q2 or Trade
#66** (unchanged from the Q2-era version of this rule).

## 10. Minimum acceptable TP1

`EXECUTABLE_TP1_RR >= 1.50R`, after the 10-pip buffer, or the trade is `NO_TRADE`. Never move TP
farther away artificially to manufacture 1.50R — if the market doesn't genuinely offer the room,
decline the trade.

## 11–13. Multi-target system V1

TP1 = first structural objective clearing 1.50R after the buffer (mandatory floor). TP2 = next
genuine structural objective beyond TP1 (guidance only, commonly ~2.25–2.50R+ when the market
provides it — never forced). TP3 = larger/final structural objective from the entry thesis (can
be 3R/4R/5R+ for genuine large opportunities — never capped at a conventional number, and never
fabricated to fill a slot). `TARGET_MODE` = `TP1_ONLY` / `TP1_TP2` / `TP1_TP2_TP3`, set honestly
per trade. Default position split for a genuine 3-target trade: **TP1 40% / TP2 30% / TP3 30%**,
frozen before entry; if only TP1/TP2 exist, the actual chosen split is frozen explicitly instead
(never silently invent a TP3).

## 14. Trailing management

May coexist with multi-target exits, but the full management plan (`TRAILING_MODE`,
`TRAILING_ACTIVATION_CONDITION`, `STOP_ADJUSTMENT_RULE`, `TP1/2/3_BEHAVIOR`) must be frozen before
entry. Never: widen SL after entry, move a TP farther after entry, invent a new rule because a
trade is losing, change the frozen plan based on outcome, or auto-move to breakeven on TP1 unless
that was part of the frozen plan.

## 15. Partial exit accounting

Per multi-target trade, independently record `TP1/2/3_HIT`, `TP1/2/3_EXIT_PRICE`,
`TP1/2/3_REALIZED_PIPS`, `TP1/2/3_REALIZED_R`, then compute `WEIGHTED_RESULT_PIPS` /
`WEIGHTED_RESULT_R` from the frozen allocation (e.g. 40/30/30) using **actual realized exits**,
never nominal targets, in final performance statistics.

## 16. Target efficiency research

Track `STRUCTURAL_TARGET_REACHED` vs `EXECUTABLE_TARGET_REACHED` on every trade going forward, to
learn prospectively whether the buffer prevents near-miss reversals, improves realized
expectancy, or sacrifices favorable excursion. Do not recalibrate the buffer after one or two
examples — accumulate evidence first.

## 17. Q3 playbook / strategy discovery

Unchanged permanent path: `OBSERVATION → RECURRING_OBSERVATION → REPEATED_LESSON →
DEVELOPING_PLAYBOOK → TRADER_STRATEGY_CANDIDATE → CEO REVIEW → ALPHA FALSIFICATION`. No universal
strategy required — regime specialists preferred, via the existing Regime Strategy Matrix. A
candidate must specify at minimum: REGIME, MARKET_MECHANISM, TIMEFRAMES, DIRECTION, CONTEXT,
LOCATION, ENTRY, CONFIRMATION, INVALIDATION, STOP, TP1/TP2/TP3 logic, MANAGEMENT, NO_TRADE
conditions, FAILURE conditions, SUPPORTING_EXAMPLES, COUNTEREXAMPLES, LIMITATIONS. Remains
UNVALIDATED until independently tested by Alpha.

## 18. Q2 knowledge may inform Q3 — Q2 results may not

Legitimate lessons from Q2 (mechanism-level understanding, e.g. "trailing underperformed static
baselines," "FULLY_ALIGNED setups underperformed this window") may inform Q3 reasoning
prospectively. Q2's specific trade *outcomes* must never be peeked at to re-fit a rule each time a
similar setup appears in Q3 — that would be exactly the retrospective-optimization governance
this apprenticeship has refused throughout. Q2 remains historical learning; Q3 is the new forward
cohort.

## 19. Q3 performance cohort

Period: **2020-07-01 through 2020-09-30**. Starts at the first unseen M15 bar, 2020-07-01
00:00:00 UTC. All standing causal apprenticeship rules remain active: H4 context → H1 active
structure/phase → M15 primary executable reasoning → M5 only if available/useful;
ONE-STEP-ONE-READ; NO FUTURE LEAKAGE; FREEZE BEFORE REVEAL; Multi-Timeframe Alignment V1; Evidence
Upgrade V1; ZERO VOLUNTARY IDLE; source-native gap handling; visible market thesis; forward-only
learning.

## 20. Q3 end / Q4 reset

Final M15 Q3 bar: **2020-09-30 23:45:00 UTC**. Do not consume the first Q4 bar
(2020-10-01 00:00:00 UTC) as part of Q3. At that boundary: finalize
`TRADER_KNOWLEDGE_CHECKPOINT_2020_Q3.md` including a direct Q2-vs-Q3 improvement audit, then STOP
for CEO review — do not automatically begin Q4 replay. The Q4 operating rule (§2) is
pre-installed and activates only on explicit CEO authorization.

## 21. Q4 comparison (when reached)

Final Q4-close comparison must show Q2 / Q3 / Q4 independently across: selectivity, win rate,
expectancy, drawdown, target quality, target capture, management, MFE retention, false entries,
missed trades, regime identification, Multi-Timeframe Alignment, playbook specialization,
strategy-candidate creation.

## 22. Governance (unchanged, restated)

Never touch S5, Strategy Catalog production status, live broker permissions, or Alpha validation
evidence. The apprenticeship remains fully separate. No apprenticeship playbook becomes a
validated/live strategy without CEO review → Alpha falsification → independent validation →
explicit promotion authorization.
