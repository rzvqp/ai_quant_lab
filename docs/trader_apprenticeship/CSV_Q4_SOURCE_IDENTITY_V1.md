# CSV_Q4_SOURCE_IDENTITY_V1

Mandate section 3: locate the exact historical source corresponding to the Q4 2020 M15 replay AI
Trader actually consumed, mechanically, not invented.

## What was checked

`OANDA_XAUUSD_M15.csv` exists under `data/market/` in eleven different repo checkouts on this
machine. **Hashing all of them revealed they are NOT one canonical file** — three distinct
contents share this filename:

| SHA-256 (short) | Repos | Date range |
|---|---|---|
| `57f4ed95...` | `ai_quant_lab-alpha-automation`, `ai_quant_lab-data-acq`, `ai_quant_lab-wp5b` | 2011-07-26 → 2026-07-xx (355,696 rows) |
| `8f865b87...` | `ai_quant_lab-alpha-discovery`, `ai_quant_lab-families`, `ai_quant_lab-research-main`, `ai_quant_lab-research-main-strategies`, `ai_quant_lab-stratdev`, `aql_stat_clone` | 2022-12-16 → 2026-07-xx (84,152 rows) |
| `c777cb9c...` | `ai_quant_lab` (standalone) | 2022-12-16 → 2026-07-xx |

Per mandate section 3 ("If more than one plausible source exists: STOP and report ambiguity — do
not choose silently"): this is disclosed, not hidden. It is **not**, however, an unresolvable
ambiguity — two of the three variants (`8f865b87...`, `c777cb9c...`) start in December 2022 and
mechanically cannot contain any Q4 2020 row at all (confirmed: `awk` scan for any row in the epoch
range 1601510400–1601520000 found zero matches in either). Only `57f4ed95...` covers Q4 2020. This
is a real data-hygiene finding worth separate attention (the *same filename* meaning three different
things across a dozen checkouts is a latent footgun for any future script that assumes it), flagged
here rather than silently worked around, but it does not block this mandate: the correct source is
determined by mechanical fact (date coverage), not preference.

## AUTHORITATIVE_SOURCE

```
SOURCE_FILE   = data/market/OANDA_XAUUSD_M15.csv
                (identical copies in ai_quant_lab-alpha-automation, ai_quant_lab-data-acq,
                 ai_quant_lab-wp5b — canonical reference used: ai_quant_lab-data-acq, the
                 Data Acquisition division's own repo)
SOURCE_HASH   = 57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37  (SHA-256, full file)
INSTRUMENT    = XAUUSD (OANDA CFD feed)
TIMEFRAME     = M15 (900s bars)
TIMEZONE      = UTC (unix epoch seconds, column `time`)
DATE_RANGE    = 2011-07-26T06:30:00Z .. (2026, still-growing)
FIELDS        = time,open,high,low,close,volume
Q4_START_MAPPING  = epoch 1601510400 = 2020-10-01T00:00:00 UTC (bar open)
BAR_378_MAPPING   = epoch 1602036900 = 2020-10-07T02:15:00 UTC (bar open) /
                     2020-10-07T02:29:59 UTC (TradingView's own close-label convention, matching
                     AI_TRADER_Q4_M15_LOG.md's "BAR 378 (02:29:59)" verbatim)
TIMESTAMP_BAR_378 = 1602036900
```

## Mechanical verification this is genuinely the right file (not merely the right shape)

`REPLAY_DATA_GAP_LEDGER.md` cites the Q4 apprenticeship's own replay source as `OANDA:XAUUSD,
TradingView Bar Replay` — the same instrument this file's own name and price level independently
confirm. Beyond matching by name, three independent numeric checks against
`AI_TRADER_Q4_M15_LOG.md` (a document this mandate did not generate) all passed exactly:

1. **Bar 378's own OHLC**: `AI_TRADER_Q4_M15_LOG.md`: *"BAR 378 (02:29:59): close 1880.434, vol
   523."* The source file's row at epoch 1602036900: `close=1880.434, volume=523` — exact match to
   three decimal places and an exact integer volume match.
2. **Bars 375–378's closes**: the log's own `COMPACT BLOCK 370-377` CLOSES list gives bars 375-377
   as `1875.888 / 1879.648 / 1879.44`; the source file's three preceding rows (epochs 1602034200,
   1602035100, 1602036000) give exactly those three values, in order.
3. **All four Q4 gaps in range 1-378, by exact bar index**: `REPLAY_DATA_GAP_LEDGER.md` documents
   GAP-151 (Q4 bar 85, 75min), GAP-152 (Q4 bar 177, 49.25h weekend), GAP-153 (Q4 bar 269, 75min),
   GAP-154 (Q4 bar 361, 75min). The source file's own gap positions, found independently by scanning
   for any timestamp delta ≠ 900s: bar 85 (4500s), bar 177 (177300s = exactly 49.25h), bar 269
   (4500s), bar 361 (4500s) — **four gaps, four exact index matches, four exact duration-class
   matches**, against a document this mandate's own code never read while computing them.

Four independent close-price matches, one volume match, and four independent gap-position matches
— all against a pre-existing, independently-authored ledger — is not treated as coincidental.

`Q4_START_MAPPING` is independently corroborated a second way: `AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md`
section 20 states the first Q4 bar is *"2020-10-01 00:00:00 UTC"* — exactly epoch 1601510400, the
source file's own first Q4-range row.
