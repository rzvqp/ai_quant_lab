# RED TEAM — RANGE V4.3 REAL-BAR EXECUTION · TERMINAL VERDICT
### RT-RANGE-0009 · `REAL_BAR_SEALED_CONSTRUCTION_REVALIDATION`
**Date:** 2026-08-19 · **Auditor:** Red Team · **Battery:** RT-RANGE-0009

---

## 0 — VERDICT

```
RANGE_V4_3_REAL_BAR_EXECUTION_BLOCKED_ESCROW
RANGE_V4_3_REAL_BAR_METRICS_INVALID          (no run performed — no metrics produced)
INDEPENDENT_SEMANTIC_BLIND = FALSE
BLIND_PASS_NOT_PERMITTED
```

**The escrow's sealed OHLC bar-content could not be independently verified. Per mandate §4 I stopped
fail-closed BEFORE reading any label, BEFORE running the detector, and WITHOUT substituting any other
data.** No inference executed. No labels accessed. No SEALED/OOS/PnL/broker/LIVE_SHADOW touched.

This is a blocking-integrity result about the **escrow reproducibility**, not a semantic judgement of the
detector. It says nothing about whether V4.3 recognizes the CEO-assisted structures — that question remains
open and can only be answered once the escrow is made reproducible (minimal fix in §7).

---

## 1 — What the mandate required before a run (§4)

Before any inference the mandate requires escrow verification, including verbatim: *"each window's extracted
OHLC SHA-256 = the published hash in `BLIND_LABEL_BATCH_02_HASHES.md`"*, and: *"Dacă payload-ul sau mapping-ul
nu poate fi verificat, oprește-te cu `RANGE_V4_3_REAL_BAR_EXECUTION_BLOCKED_ESCROW`. Nu substitui alte date."*

The `bars_sha256` published per window in the sealed mapping (and mirrored in `BLIND_LABEL_BATCH_02_HASHES.md`,
column *"SHA-256 bare OHLC"*) is the cryptographic anchor that binds the bars I would feed the detector to the
bars the Statistician sealed **before** labelling. Confirming it is a hard precondition, not a formality: it is
the only defence against silently running the frozen detector on the wrong OHLC.

## 2 — What VERIFIED (escrow integrity — all pass)

Pre-run protocol committed and pushed BEFORE any sealed read (commit `38daf9b`,
`RT-RANGE-0009_real_bar_execution_PROTOCOL_PRECOMMIT.md`, `local = remote` on all 4 mirrors,
`REAL_BAR_EXECUTION_PROTOCOL_PRECOMMITTED` declared). Then, on the sealed payload:

| Check (§4) | Result |
|---|---|
| Payload exists; SHA-256 = content-addressed filename | **PASS** (`payload-b7e103a3d9b86f72.bin`, 20 906 B) |
| Correct key opens (HMAC tag valid) | **PASS** (`escrow_key_v3.bin`) |
| Wrong key refused / 1-bit change refused (encrypt-then-MAC) | **PASS** (both raise `TAG INVALID`) |
| Exactly 48 window IDs, no duplicate ID | **PASS** |
| Lengths 16×96 + 16×288 + 16×480 = 13 824 bars | **PASS** |
| Corrected lengths BLIND-046 = 288 · 047 = 96 · 048 = 480 | **PASS** (mapping matches the CORRECTION ADDENDUM, not the stale attached JSONs) |
| Instrument XAUUSD, timeframe M15 | **PASS** (per-window timestamps land on the canonical M15 calendar, 15-min spacing) |
| Each window's start_utc/end_utc lands on a real canonical bar | **PASS** (e.g. BLIND-001 `2024-12-24 02:30 → 2024-12-30 08:30`, unix `1735007400`, present in the canonical corpus) |
| **Each window's extracted OHLC SHA-256 = published `bars_sha256`** | **FAIL — CANNOT REPRODUCE** (see §3) |

Everything about the escrow *container* is sound (tamper-evident, correctly keyed, right population, right
lengths, timestamps on the real calendar). The **content anchor is the single unverifiable item**, and it is
the one the mandate makes blocking.

## 3 — Why `bars_sha256` cannot be reproduced (the blocking obstacle)

Two committed/available artifacts are missing, both necessary to recompute the anchor:

1. **The canonical-index source corpus is not materialized.** The mapping indexes each window into a
   **197 094-bar** discovery corpus (BLIND-001 `canonical_index_start = 178230`; `independence_proof.of_total =
   197094`). No CSV of ~197 094 rows exists anywhere under `ai_quant_lab-wp5b/data`, `ai_quant_lab/data`, or the
   escrow folder. The M15 corpora that DO exist are **355 696** rows (wp5b full history) and **84 152** rows
   (`__SUPERSEDED_v1`). Index 178 230 fits neither: it overflows 84 152 and is offset differently from 355 696
   (the sealed timestamp `1735007400` sits at index 318 264 in the 355 696 corpus, not 178 230). The 197 094-bar
   corpus is a reconstruction (the 4 discovery blocks concatenated) that has never been committed as a file.

2. **No seal/hash recipe is committed.** `BLIND_LABEL_BATCH_02_HASHES.md` asserts *"Toate recalculabile"* but
   publishes no serialization spec, and a repository-wide search for `bars_sha256` across the escrow folder and
   the entire `statistician/` tree returns **zero** scripts. The seal-creation tool that defines the exact OHLC
   byte layout lives off-git.

Because the exact source corpus at the canonical index is absent AND the serialization format is undocumented,
`bars_sha256` is not independently recomputable. I extracted BLIND-001's 288 bars by timestamp from the
355 696-row canonical corpus (timestamps match exactly) and tried the anchor against **~24 serialization
conventions** — CSV lines; ISO-time and unix-time; OHLC and OHLCV; JSON dict/list forms (compact and spaced);
1/2/3/5-decimal rounding; pipe/semicolon/tab separators; the L=288 canonical window and the 336-bar render
window (`render_start..render_end`); and raw little-endian float32/float64 byte packing. **None** reproduce the
target `7546a8d1f415d6ee…`. Timestamp-match is strong evidence I located the correct *window*, but it does NOT
confirm the OHLC *values* are byte-identical to the sealed reference (a re-pull of the discovery corpus could
differ in precision/rounding), and byte-identity is exactly what the anchor exists to prove.

Substituting the 355 696-corpus bars and running anyway is explicitly forbidden (*"Nu substitui alte date"*)
and would defeat the escrow's purpose — the same class of pre-run-integrity failure this division flagged in
RT-RANGE-0007 (`PRE_RUN_FREEZE_PROTOCOL = FAIL`). Fail-closed is the correct action.

## 4 — Finding (reproducible, non-invented)

**`ESCROW-UNREPRODUCIBLE-ANCHOR` — the sealed batch publishes a per-window OHLC verification hash whose
reproduction recipe is not committed, so no independent party can complete the §4 bar-content check.** An
unreproducible verification hash cannot serve its verification purpose. Concretely: (a) the 197 094-bar
canonical-index corpus is absent from all repos and disk; (b) no committed script or spec defines the
`bars_sha256` serialization. This is not a detector defect and not an invented defect — it is a gap in the
escrow-publication protocol that blocks the mandated pre-run verification.

## 5 — Discipline confirmations

- **No labels read.** Env B / scoring never constructed; `LEVEL_MAPPING`/`LOCKED_LABELS`/fixtures never opened.
- **No inference run.** `RUN_ATTEMPT` never reached 1; the frozen detector (`f224e7d`, config_id `24f72a60…`,
  detector hashes `2aba333c…`/`84dac346…`) was never executed on sealed bars.
- **No prohibited surfaces.** Zero SEALED/OOS access, zero PnL, zero broker, zero LIVE_SHADOW, zero Alpha,
  zero Strategy Catalog, no wheel, no 6-hour regression. VE / Statistician / AI Trader code untouched; all
  changes confined to `red_team/`.
- **No sealed data published.** This report contains only opaque IDs, a single already-published timestamp,
  hashes, and aggregate structure — no bar values, no ID→timestamp mapping, no key, no local paths.
- The decrypted mapping was handled only in an off-git scratch location and is not committed; it is deleted at
  delivery.

## 6 — Disposition

Forbidden verdicts (`BLIND_PASS`, `SEMANTIC_PASS`, `FINAL_VALIDATION_PASS`, `STRATEGY_CATALOG_READY`,
`ALPHA_AUTHORIZED`) are not emitted. `RANGE_V4_3_REAL_BAR_EXECUTION_BLOCKED_ESCROW` authorizes **nothing
downstream** — not a blind batch, not a diagnostic on real metrics (none exist), not the wheel/Strategy
Catalog/Alpha/AI Trader/LIVE_SHADOW/broker/trades/6h-regression. It authorizes exactly one thing: a
**re-attempt of RT-RANGE-0009 after the escrow is made reproducible** per the minimal fix.

## 7 — Minimal fix (stated, NOT implemented by Red Team)

The Statistician must commit to a Git-tracked location, sufficient to recompute the anchor deterministically:

1. **The exact canonical-index source corpus** used to seal the batch — either the 197 094-bar discovery corpus
   itself, or a content hash of it plus a committed, deterministic build recipe (the 4 discovery blocks +
   concatenation order) that reproduces exactly 197 094 rows and resolves `canonical_index_start` unambiguously.
2. **The seal/serialization spec or script** that defines, byte-for-byte, how `bars_sha256` is computed from a
   window's OHLC (field order, decimal formatting, row/field separators, time representation, inclusive/exclusive
   bounds, and whether the L-window or the render-window is hashed).

With (1) and (2) committed, Red Team can complete §4 (`extracted OHLC SHA-256 == published`) and re-run
RT-RANGE-0009's two-stage isolated execution. Nothing about the frozen detector, contract, or config changes.

---

**TERMINAL:** `RANGE_V4_3_REAL_BAR_EXECUTION_BLOCKED_ESCROW` · `INDEPENDENT_SEMANTIC_BLIND = FALSE` ·
`BLIND_PASS_NOT_PERMITTED`. Ledger entry **E84** (prev_hash E83).
