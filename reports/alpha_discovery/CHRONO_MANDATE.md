# CHRONOLOGICAL_MARKET_LEARNING — primary campaign (CEO mandate 2026-08-24)

PRIMARY discovery is now a strict walk-forward in time (random blinds = SECONDARY AUDIT ONLY; the random-blind corpus
reading_ledger_b2.jsonl / Batch-1/2 stay FROZEN). Learn XAUUSD as it evolves, not just search for a strategy.

- **chrono_engine.py** — walk M15 STRICTLY chronologically from 2020-01-01 to latest authorized bar, candle-by-candle, top-down
  N1(H4)->N2(H1)->N3(M15)->N4(M5 2021-07-27+ only, else UNAVAILABLE, never synthesized)->N6 BUY/SELL/NO_TRADE+readiness->freeze->
  reveal one candle. NO future access, NO outcome in the walk. Readings tagged by QUARTER. Output reading_chrono.jsonl.
- **chrono_checkpoint.py** — every quarter: form hypotheses from readings RESOLVED by quarter-end (no leakage), version them, and
  FORWARD-TEST the previous quarter's frozen hypotheses on this quarter (Q1 discovers V1 -> Q2 tests V1 -> V2 after Q2 -> Q3 tests V2).
  Track which knowledge survives multiple future quarters. 12-item checkpoints. NO retrospective editing. Output CHRONO_CHECKPOINTS.md
  + chrono_hypotheses.json (lineage).

Objective: what structures persist vs decay, high-prob BUY/SELL conditions, when NO_TRADE is optimal, which mechanisms are
regime-specific, and which knowledge survives multiple forward quarters. Continuous through the latest authorized data.
