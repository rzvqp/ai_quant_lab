# knowledge/ — Official Lab Knowledge Base (S1–S51)

Consolidated, read-only record of what the lab has LEARNED from families S1–S51 on XAUUSD M15. It does NOT
modify or replace the source artifacts — it references them. Nothing here is validated alpha.

## Strategy vs Mechanism vs Primitive
- **Strategy / family (S1–S51):** a concrete backtested rule set (grammar of hypotheses). Lives in `code/`.
- **Mechanism:** the economic story a family tests (e.g., "opening-range momentum"). See `MECHANISM_REGISTRY.md`.
- **Primitive (this base):** an *observable market behavior* abstracted across families, with a proposed
  economic mechanism and traced evidence (e.g., P003 Opening-Range Momentum). See `BEHAVIOR_REGISTRY.md`.
  Primitives are the durable knowledge unit; strategies are disposable instances.

## Files (authoritative within knowledge/)
- `BEHAVIOR_REGISTRY.md` / `.jsonl` — all 19 primitives with status + evidence (machine-readable jsonl).
- `MECHANISM_REGISTRY.md` / `.parquet` — the 13 family-level mechanisms (copied from the project root).
- `STRATEGY_EVIDENCE_MAP.md` — strategy/family → mechanism → primitive → result chain.
- `NEGATIVE_EVIDENCE_REGISTRY.md` — every mechanism that failed (preserved, not deleted).
- `CONTRADICTION_REGISTRY.md` — important context-dependent contradictions.
- `VALIDATION_STATUS.md` — exactly what has and has NOT been validated.
- `primitives/PXXX_*.md` — one file per main primitive (13 files).

## Status vocabulary (never use "VALIDATED")
SUPPORTED EXPLORATORILY · MIXED · INCONCLUSIVE · REPEATEDLY NEGATIVE · TECHNICALLY INVALID · VALIDATION PENDING.

## How to add / update a conclusion
1. It must be traceable to an on-disk artifact (parquet/log/report). Conversations are not authoritative.
2. Write it as a **falsifiable, dataset/timeframe/regime-scoped** claim ("on XAUUSD M15 2022-25, …"), never a universal ("X works").
3. Add/adjust the primitive in `BEHAVIOR_REGISTRY.jsonl` (+ its file if a main primitive); update its status and confidence.
4. When a new family is built, map it in `STRATEGY_EVIDENCE_MAP.md`, attach it to a primitive (or create one only
   if it has sufficient evidence), and record any new contradiction.

## Handling contradictions
When two results conflict, record BOTH in `CONTRADICTION_REGISTRY.md` with the context difference and the test
that would separate them. Do not overwrite the negative result — context-dependence is itself knowledge.

## Avoiding over-strong claims
- Distinguish "historically profitable" and "OOS-positive" from "validated." Nothing here has passed matched-null
  over the full universe, global-FDR, walk-forward, Red Team, or the sealed holdout.
- Most positive primitives are long in a 2023-25 gold bull → the split between timing-alpha and gold beta is unresolved.

## What is authoritative
The parquet/log artifacts in `results/` and the family code in `code/` are the ground truth. This base is a
faithful, referenced synthesis of them — if they ever disagree, the artifacts win.
