# AI_TRADER_CONTEXT_V1 -- Governance / Versioning Record

```
SCRIPT_NAME     = AI_TRADER_CONTEXT_V1
SCRIPT_VERSION  = 1.0
PINE_VERSION    = 6 (//@version=6)
CREATED_FOR     = Q3 2020 apprenticeship (AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1)
SOURCE_FILE     = pine_scripts/AI_TRADER_CONTEXT_V1.pine
SHA256          = c0b053aa900bc463327b694ab9f60c8e35bcd585e7746f584c8a4c03f64900fc
```

Installed by direct CEO mandate, real-time, following the indicator utility review
(3 approved diagnostics: H1 EMA(50) confirmed-only, causal session VWAP, M15 ATR(14)).

**Governance rule**: this file records the exact V1.0 source and its SHA256 fingerprint at
creation. Any future modification to the script's logic creates a new file/version
(`AI_TRADER_CONTEXT_V2.pine` etc.) with its own governance record -- `AI_TRADER_CONTEXT_V1.pine`
is never silently edited once Q3 evidence has begun accumulating against it. If the fingerprint
recorded here ever fails to match the live file, that is itself evidence of an undisclosed
modification and must be investigated before further use.

## Scope / what this script is NOT

- Not a signal generator. No BUY/SELL/LONG/SHORT logic exists anywhere in the script.
- Not a replacement for H4/H1/M15 structural reasoning -- strictly secondary context, consulted
  after structure, per the standing decision hierarchy (`AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md`).
- Not a scoring system, not a "N confirmations = trade" mechanism, not a traffic light.
- Contains exactly the three CEO-approved components -- no EMA20/100/200, RSI, MACD, Stochastic,
  Bollinger Bands, Supertrend, or any other indicator.

## Session-boundary sourcing (do-not-invent requirement)

The CEO mandate required recovering the AI Trader's *existing* session definitions rather than
inventing new ones. A dedicated search (Explore agent, this session) found:

- The only coded, RUNTIME-BACKED session definition that `AI_TRADER_MARKET_READING_LIBRARY_V1.md`
  module M07 actually cites is `ai_trader/market_scanner/session.py`'s `session_name_for_hour()` --
  fixed UTC-hour thresholds, no DST adjustment: **ASIA 00:00-08:00, LONDON 08:00-13:00,
  NY 13:00-21:00, LATE 21:00-24:00** (identical across all repo copies checked).
- A separate, unrelated Alpha-division artifact (`session_tz.py`/`session_phase.py`, a 6-phase
  DST-aware taxonomy tied to London/NY market opens) exists but is explicitly a different team's
  unwired research asset (the "SF-3" information source), not the SessionEngine, and not what M07
  cites as authoritative.
- The narrative `ASIA/LONDON/PRE_US/NY_US_CASH/LATE_US` labels used in `TRADE_EVIDENCE_LOG.md` and
  `EVIDENCE_UPGRADE_METHODOLOGY_V1.md` have **no coded boundary definition anywhere** in the
  codebase -- they are a manual tagging convention only, never given exact numeric cutoffs.

**Decision**: this script uses the actual coded `SessionEngine` boundaries (ASIA/LONDON/NY/LATE,
fixed UTC hours) since that is the one definition explicitly described in this codebase as
RUNTIME-BACKED and authoritative. It does not use the narrative 5-label convention, since no coded
definition for `PRE_US`/`NY_US_CASH`/`LATE_US` exists to recover.

## Causality / non-repaint design

- **H1 EMA(50)**: `request.security(..., ta.ema(close,50)[1], lookahead=barmerge.lookahead_off)`.
  The `[1]` offset guarantees every M15 bar only ever reads the last *fully closed* H1 bar's EMA
  value -- the currently-forming H1 bar (whose eventual close is unknown at the M15 replay
  timestamp) is never referenced, satisfying the "confirmed/closed H1 only" requirement exactly.
  `lookahead=barmerge.lookahead_off` additionally prevents any future-bar leakage during
  historical/replay evaluation (the repainting failure mode this parameter exists to prevent).
- **Session VWAP**: built from `ta.vwap(hlc3, anchor)`, a native Pine cumulative accumulator that
  resets whenever `anchor` (a session-boundary-crossing boolean, computed from `ta.change()` on the
  current session index) is true. It sums only current-and-past bar price*volume from the most
  recent reset forward -- there is no `request.security` call and no reference to any bar that has
  not yet occurred, so it is non-repainting/causal by construction, not merely by empirical test.
- **ATR(14)**: `ta.atr(14)`, Pine's standard non-repainting ATR built-in, computed on the chart's
  own (M15) resolution with no higher-timeframe request involved.

## Installation record

See the CEO validation report delivered in-session for the exact PASS/FAIL results of: Pine
compile, chart attachment, per-component display verification, and the replay-integrity checks
(pointer unchanged during install, no already-processed Q3 bar reinterpreted).

`INDICATOR_CONTEXT_V1_EFFECTIVE_FROM` is recorded in that same report -- everything before that
timestamp remains `PRE_INDICATOR_CONTEXT` and is never retroactively reinterpreted using this
script's output.
