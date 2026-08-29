# AI Trader Market Apprenticeship — governance

Mandate: `AI_TRADER_MARKET_APPRENTICESHIP_V1` (CEO, 2026-08-24). Supersedes "find another statistical
edge" as AI Trader's primary objective. Alpha (repo `ai_quant_lab-alpha-automation` /
`alpha-automation-v1`, per `CANDIDATE_STATUS_REGISTER_v1.1.md` §0) remains the independent scientific
auditor and is a **separate division in a separate repo** — this alone satisfies the mandate's own
"AI Trader and Alpha do not communicate directly" requirement structurally, not just by convention.

## Two lanes (mandate §1)

- **Lane A — `HISTORICAL_MARKET_APPRENTICESHIP`**: chronological, candle-by-candle replay starting
  2020-01-01, TradingView Bar Replay primary. Files under `lane_a_historical/`.
- **Lane B — `CURRENT_MARKET_SHADOW_DEMO`**: parallel, independent read of the live chart. Files under
  `lane_b_current/`. Neither lane's data or conclusions may leak into the other (mandate §1, §27).

## Artifacts

- `AI_TRADER_EXPERIENCE_LEDGER.md` — durable, append-only. Market observations, frozen decisions,
  trades, missed opportunities, recurring lessons (mandate §14). Never retroactively edited (§12, §18).
- `checkpoints/TRADER_KNOWLEDGE_CHECKPOINT_<YYYY_QX>.md` — frozen quarterly knowledge version
  (mandate §17). `KNOWLEDGE_V<n>` referenced by later checkpoints; a changed interpretation creates a
  new version, never rewrites an old one (§18).
- `observation_candidates/TRADER_OBSERVATION_CANDIDATE_<ID>.md` — an unvalidated repeated-pattern
  belief the trader has formed, frozen per the mandate §19 template. Status `UNVALIDATED_TRADER_OBSERVATION`
  until a separate, CEO-authorized Alpha audit produces its own `ALPHA_VERDICT_<ID>` in Alpha's own repo.
- `AI_TRADER_MARKET_READING_LIBRARY_V1.md` — a structured OBSERVATION / INTERPRETATION library covering
  the canonical M01-M14 market-reading taxonomy plus the 3 frozen information assets (VOLTIME-1, DXY-NDX1,
  SF-3). Not a strategy library, not wired into any decision path, read-only and forward-only (does not
  retroactively apply to anything already logged). Per the 2026-08-25 coverage audit it references: 7
  modules RUNTIME-BACKED (M01, M03, M06, M07, M10, M13, M14), 4 PARTIAL (M02, M04, M05, M09), 3
  CONCEPTUAL_OBSERVATION_ONLY with no governed implementation anywhere (M08, M11, M12).

## Handoff mechanism (mandate §21)

No existing canonical AI-Trader-to-Alpha artifact handoff location was found (`KNOWLEDGE_REGISTRY.md`
and `CANDIDATE_STATUS_REGISTER_v1.1.md` are Alpha/CEO-owned statistical-claims registries, not raw
practitioner-observation intake — reusing them would misrepresent an unvalidated trader belief as
already-scoped statistical evidence). This directory is the new, clearly governed location, documented
once here per §21's own fallback instruction:

A handoff is: this repo's `docs/trader_apprenticeship/observation_candidates/TRADER_OBSERVATION_CANDIDATE_<ID>.md`,
committed to `ai-trader-implementation` with its own commit hash, referenced by CEO to Alpha for
independent audit. Alpha writes its own `ALPHA_VERDICT_<ID>` in Alpha's own repo — never in this one.
This repo's copy of a candidate is never edited after Alpha's verdict; if Alpha falsifies it, that fact
is recorded as a *new*, forward-only ledger/checkpoint entry (mandate §23), not a rewrite of the original.

## Frozen / out of scope

- S5 (`ai_trader/new_brain_live/strategy_platform/s5_opening_range_breakout.py` and its MT5 demo
  runtime) — read-only, untouched by this work (mandate §26).
- `ENTRY_READINESS_V1` — remains FAILED/FROZEN, not retuned (mandate §30).
- DXY-NDX1, VOLTIME-1, SF-3 — usable only as READ-ONLY context inputs to a `MARKET_ARMED`-style state,
  never as direct BUY/SELL signals (mandate §6), never retuned.
