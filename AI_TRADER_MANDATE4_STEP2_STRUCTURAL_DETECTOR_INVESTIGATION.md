# AI Trader — Mandate 4, Step 2: Structural Detector Investigation — Report

**Nature of this document**: investigation only, per explicit instruction ("RAPORTEAZA ce ai gasit, nu
repara singur"). No code touched. Every claim below is traced to a specific line in the seven named
modules (read directly, not assumed), plus their direct dependencies.

## Finding 0 (found while investigating, not anticipated): these modules live in a DIFFERENT repository

Before anything else: `market_structure.py`, `liquidity_mechanics.py`, `imbalance_mechanics.py`,
`institutional_levels.py`, `order_flow.py`, `market_state.py`, `interactions.py` do **not exist anywhere
in `ai_quant_lab-research-main`** — confirmed by a repo-wide search, zero matches. They exist in
`ai_quant_lab-wp5b/code/`, a **separate git repository**. `ai_trader` (this repo) has no dependency on
`ai_quant_lab-wp5b` today — no path reference, no vendored copy, no package install.

This is a real precondition for Step 3 that "connect the detectors to the journal" does not, by itself,
resolve: wiring requires deciding HOW `ai_trader` reaches this code — vendor a copy in, add the other
repo to the Python path, or package it installably — each with different implications for staying
byte-for-byte faithful to code you've described as frozen and independently audited. I have not made
this decision; noted here as Finding 0, alongside the block-boundary questions you asked for by name.

## The block-boundary question, per module

Every module's own docstring already documents WHY block-boundary resets exist: `code/` was written for
**offline discovery** over historical data, where blocks are contiguous windows separated by real gaps
and quarantine bands, and state must not leak across a quarantine boundary (that would let structure from
before a sealed region "leak" into it, contaminating the discovery result). Live has no such quarantine —
it is one continuous, real-time series, arriving strictly in order, nothing sealed, nothing to protect
from contamination.

**Confirmed conclusion, consistent across every module that uses `Block`**: for live, the correct mapping
is **ONE single, ever-growing `Block`** — not per-day, not per-restart, not any other segmentation. State
should flow continuously, exactly as you hypothesized. This is not just a technical workaround: it is
also the economically correct reading — a liquidity pool or an FVG does not stop being real just because
time passes; it stays valid until price actually consumes it. The block-reset in `code/` exists to
protect a RESEARCH methodology, not because the underlying market structure has a real boundary there.

Per module:

- **`market_structure.py` (D3)**: `detect_swings`/`label_structure`/`detect_breaks` all partition by
  `Block` and reset (`last_high`/`last_low` dicts keyed by `block_index`) at each new block. Single
  continuous block → no resets, exactly your hypothesis. **Separate, disclosed limitation**: these
  functions are stateless, pure, RECOMPUTE-FROM-SCRATCH over the whole array on every call — not an
  incremental streaming detector. A months-long live run needs a windowing/truncation strategy so this
  doesn't mean re-scanning an ever-growing array on every bar close forever; not a correctness question,
  a performance one, and not yet decided.
- **`liquidity_mechanics.py` (D4)**: `detect_sweeps` filters `active` pools to `p.block_index == b_i` per
  block loop — a pool from block 0 is invisible in block 1's loop by construction. Single continuous
  block → pools persist until consumed, matching real SMC semantics. **Blocking, separate from D4**: D5
  (M5→M15 HTF alignment for INTERNAL pools) is explicitly unresolved in the module's own docstring — "the
  cross-timeframe M5→M15 mapping is NOT implemented here; it requires an alignment artifact that does not
  exist in the manifest." Internal pools cannot be built. EXTERNAL pools depend on HTF (H4/D1) bars, which
  circle back to Finding 3 below — also blocked, transitively.
- **`imbalance_mechanics.py` (Q2, "analog D4")**: same block-confinement pattern, CLOSED status ("all
  questions resolved"), most mature of the seven. Single continuous block → FVGs persist until touched/
  filled/inverted. No other blocking dependency found — this module is self-contained (needs only
  high/low/close arrays).
- **`institutional_levels.py` (D3_bis)**: same block-reset pattern for PDH/PDL/Weekly memory. Single
  continuous block applies the same way. **Blocking, separate from D3_bis**: see Finding 3 below —
  `day_index`/`week_index` have no live-callable derivation.
- **`order_flow.py`**: uses a scalar `block_end`, not a `Block` list, so D3/D4 don't directly apply to its
  own signature — but see Finding 1 below, which blocks it entirely regardless.
- **`market_state.py`**: does not use `Block` at all — `expansion()`/`compression()`/`sessions()` operate
  on flat arrays with no block partitioning or quarantine concept anywhere. The block-boundary question
  does not apply to this module; it was never partitioned that way.
- **`interactions.py`**: pure, generic, stateless mask/confluence utility — no `Block`, no history
  dependency, no boundary question. See Finding 4 below for why it is deliberately not wired regardless.

## Finding 1 (blocking, found while reading, not anticipated): Order Block formation is unimplemented

`order_flow.py::detect_order_blocks` raises `NotImplementedError` outright — its own docstring: "the
FORMATION criterion for an OB (which candle BECOMES an OB) remains DESCHIS (open) per the Statistician's
decision — no formalized family requires it." `order_block_void.py` (the frozen type `order_flow.py`
imports) says the same thing independently: "BLOCKS autonomous OB detection; does NOT block the zone/
windows." Breaker/Mitigation/Rejection all take an already-existing `OrderBlock` as their INPUT — nothing
in the pipeline produces one. **This is not a block-boundary question — `order_flow.py` cannot produce
any output in live, or in research, until a formation criterion is ratified.** Wiring it as an observer
now would record nothing, forever, by construction.

## Finding 2 (blocking, found while reading, not anticipated): compression() is a disclosed, provisional definition

`market_state.py`'s own docstring, verbatim: "Compression is the ONLY primitive (together with the OB
formation criterion) genuinely UN-ANCHORED — no SMC_S* family requires it... remains a definition choice,
not an anchoring to a consumer," further disclosing that window size (460), percentile (10), and `<=` vs
`<` are "one of ten plausible variants," not a settled definition. Recording it as pure observation (never
evaluating it) does not itself require the definition to be final — but I flag this because the CEO's own
"regimul de stare — compresie" request would be recording a value the research division itself has not
ratified. Not blocking in the sense the other findings are; disclosed so the choice to record it anyway is
made knowingly, not by omission.

## Finding 3 (blocking, found while reading, not anticipated): day/week boundary derivation is a batch script, not a live function

`institutional_levels.py` requires the caller to supply `day_index`/`week_index`, explicitly NOT derived
inside the module: "day_index comes from the 17:00 New York DST-aware anchor (`code/resample_ny.py`)."
I read that file: it is a standalone, offline, pandas-based script that reads a FULL HISTORICAL CSV,
resamples the whole thing with `tz_convert('America/New_York')`/floor-to-day/shift-back-to-UTC, and writes
new CSVs — it operates on complete historical arrays, not per-bar, and is not something a live loop can
call bar-by-bar. A live-usable equivalent (same DST-aware algorithm, different execution shape:
incremental, one new bar at a time) would need to be freshly WRITTEN, not merely imported. The algorithm
itself is well-specified and could presumably be reused faithfully — but writing a new implementation of
a currently-frozen, audited module's boundary logic is exactly the kind of decision this report is meant
to surface, not make. **This also transitively blocks `liquidity_mechanics.py`'s EXTERNAL pools**, since
external pools derive from HH/LL on HTF (H4/D1) context, and those HTF bars are themselves built by the
same 17:00 NY resampling this finding describes. One possible way around it — sourcing H4/D1 directly
from MT5's own native timeframe codes instead of resampling M15 — is untested; I have not verified MT5's
native H4/D1 boundaries actually match the 17:00 NY anchor the research modules assume, and did not build
toward this path without that verification.

## Finding 4: `interactions.py` deliberately not wired, even though nothing blocks it technically

Its own docstring: the module is a generic confluence LOCATOR, explicitly built so that COMBINING
conditions (e.g. "an OB inside an active external pool during London/NY") is a HYPOTHESIS, requiring full
pre-registration — the Statistician's own ruling explicitly REJECTED the example combination given in the
original order as "a complete hypothesis, not a primitive." Since your mandate for this observer is
explicit — "Nu produce semnale. Nu evalueaza. INREGISTREAZA" — using `interactions.py` to combine any of
the other modules' outputs would risk crossing exactly the line you drew. Not wired; each detector's own
raw output is recorded standalone, never combined.

## Summary: what is safe to wire without a further decision, and what needs one

| Module | Function(s) | Live-safe under single-continuous-block? | Additional blocker |
|---|---|---|---|
| `market_structure.py` | swings, HH/HL/LH/LL, BOS/CHoCH | Yes | None found |
| `imbalance_mechanics.py` | FVG, CE-50 reactions, IFVG | Yes | None found |
| `market_state.py` | expansion, sessions | Yes (no block concept at all) | None found |
| `market_state.py` | compression | Yes | Disclosed provisional definition (Finding 2) |
| `liquidity_mechanics.py` | external pools, sweeps | N/A | Finding 3 (HTF day-boundary) |
| `liquidity_mechanics.py` | internal pools | N/A | D5, explicit manifest gap |
| `institutional_levels.py` | PDH/PDL, Weekly | N/A | Finding 3 (day/week-boundary) |
| `order_flow.py` | OB/Breaker/Mitigation/Rejection | N/A | Finding 1 (formation unimplemented) |
| `interactions.py` | confluence | N/A | Finding 4 (hypothesis territory, by design) |

Four of the seven modules (`market_structure`, `imbalance_mechanics`, `market_state`, and `interactions`
as a deliberate non-use) have no blocker beyond Finding 0 (the cross-repo location, which applies to all
seven equally). Three (`liquidity_mechanics`, `institutional_levels`, `order_flow`) each need a specific,
named decision before they can be wired.

**Not building Step 3 yet.** Awaiting direction on Finding 0 (how `ai_trader` reaches this code) before
wiring anything — even the four unblocked ones need that question answered first.
