# SESSION_SPECIALIST_ATLAS_V1 — causal session structure census

SESSION_SPECIALIST_FACTORY_V1 §23 deliverable. Governed OANDA XAUUSD M15 (UTC), 2011-07 → 2026-07. DST-correct sessions via
`session_tz.py` (zoneinfo). Conservative same-bar ordering (`ob_exec.resolve`). Code: `sess_core.py`, `sess_scan.py`, `sess_diag.py`.

## 1. Session definitions (frozen, DST-correct, causal)
```
ASIA   = UTC 00:00–07:00 (Tokyo/Sydney; negligible DST)
LONDON = [london_open (08:00 Europe/London), nyse_open (09:30 America/New_York))   -> London-only pre-NY window
NY     = [nyse_open, nyse_open + 6.5h)
```
Session ranges (H/L/open/close) are FROZEN when the session completes; a decision uses ONLY completed sessions. Prior-day H/L/close are
yesterday's (causal). No future session H/L, no centered pivots, no completed-future HTF candle. Session-days: London 3,872 · NY 3,873.

## 2. Six mechanism families (dedup of 20 raw → 6 distinct; S5 NY-OR-breakout EXCLUDED)
| family | mechanism | decision | direction |
|---|---|---|---|
| **A** | Asia range → London expansion | first London close beyond Asia H/L → next-open | both |
| **B** | Asia false-break → London reversal | London sweeps Asia H/L then closes back inside → fade | both |
| **C** | London overextension → NY reversal | London range>1.5ATR & closed near extreme → fade at NY | both |
| **D** | London trend → NY continuation | London close-open >1ATR → continue at NY open | both |
| **E** | NY displacement → second leg | NY 1h displacement, pullback ≥40%, re-acceptance → next-open | both |
| **F** | late-NY continuation / exhaustion | day move >2ATR by late-NY → continue / fade | both |

`S5_MECHANISM_CLONED = NO` — no family is an NY opening-range breakout; A (the only OR-like family) uses the **Asia** range in the
**London** session, a distinct structure, and is not a survivor regardless.

## 3. First-pass baseline (next-open entry, 2R, conservative, price-cost)
| family | N | net-R | D | C | O | verdict |
|---|---|---|---|---|---|---|
| A Asia→London expansion | 3,293 | **+0.010** | +0.014 | −0.019 | +0.037 | break-even, era-mixed |
| B Asia false-break→London rev | 3,056 | −0.366 | −0.454 | −0.318 | −0.229 | FALSIFIED |
| C London overext→NY reversal | 1,748 | −0.279 | −0.272 | −0.276 | −0.297 | FALSIFIED |
| D London trend→NY continuation | 2,784 | −0.027 | −0.033 | −0.095 | +0.062 | break-even, O-only |
| E NY displacement→second leg | 989 | −0.171 | −0.258 | −0.137 | −0.030 | FALSIFIED |
| F late-NY continuation | 2,958 | neg | — | −0.191 | −0.054 | FALSIFIED |
| F late-NY exhaustion/fade | 2,958 | neg | — | −0.247 | −0.115 | FALSIFIED |

No family reaches a clearly positive baseline. B/C/E/F strongly negative; A and D break-even. The two break-even families are examined
against matched controls in the contrast report — where the key (and only interesting) finding emerges.
