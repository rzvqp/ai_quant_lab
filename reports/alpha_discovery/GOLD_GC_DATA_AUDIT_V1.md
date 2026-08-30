# GOLD_GC_DATA_AUDIT_V1 — GC futures data availability (GOLD_ORDER_FLOW_DISCOVERY_V1 §3)

First action per mandate: inspect only authoritative existing assets; classify GC data availability. **No proxies, no fabricating
order flow from OHLC.**

## What exists
The ONLY GC futures data on disk is a **2-week Databento GLBX.MDP3 MBO SAMPLE** from a PRIOR session's temporary scratchpad
(`...344b31d3.../scratchpad/phaseb/`), built by `code/build_gc_bars.py`:
- Raw: 11 files `glbx-mdp3-2026{0629..0710}.mbo.dbn.zst` (MBO trade-level, GCQ6 front-month iid=42011464).
- Built: `gc_15m.csv` = 896 fifteen-minute bars, 11 sessions **2026-06-29 → 2026-07-10**, fields {ts, open, high, low, close, volume
  (real futures volume), ntrades}. **No bid/ask columns** in the built file (MBP-10 was in the acquisition spec but not in the working
  sample; aggressor side is *inferable* from raw MBO + reconstructed book per the Phase-B validation, not present as ground truth).
- Provenance: Phase-B validated the reconstruction engine (MBP-10 bit-exact 100% on the 2 gate days, legacy normalization). Two prior
  DISCOVERY runs (MBO trajectory-divergence, 122k anchors on this exact sample) → **NEGATIVE**: no stable pre-price signal; features flip
  sign day-to-day, 0 replicate across days. See memory `comex-gc-microstructure-infra`.

## Required audit fields
```
GC_DATA_AVAILABLE = SAMPLE-ONLY (not a governed research dataset)
GC_SYMBOL = GCQ6 (COMEX Gold front-month outright, iid 42011464)
SOURCE = Databento GLBX.MDP3 MBO (prior-session temp scratchpad, NOT a committed governed dataset)
DATE_RANGE = 2026-06-29 .. 2026-07-10 (11 sessions, ~2 weeks)
RESOLUTION = MBO trade-level (raw) → 896 × 15-min bars (built)
FIELDS = ts, OHLC, volume(real futures), ntrades ; (raw MBO: price/size/ts/action, book reconstructable)
TIMEZONE = UTC
ACTUAL_FUTURES_VOLUME = YES
BID_ASK_AVAILABLE = NO (in working sample; MBP-10 not carried into the 15m build)
AGGRESSOR_SIDE_AVAILABLE = INFERABLE-ONLY (from raw MBO + reconstructed book; not ground-truth; §17 sensitivity untested here)
OPEN_INTEREST_AVAILABLE = NO
CONTINUOUS_CONTRACT_METHOD = none (single front-month outright, no roll stitching; only 2 weeks so roll not encountered)
KNOWN_ROLL_ISSUES = n/a (window too short to cross a roll)
KNOWN_DATA_GAPS = only 11 sessions exist; everything outside 2026-06-29..07-10 is MISSING
```

## Tier classification
- **In-kind:** TIER_A (trade-level MBO, real volume, book reconstructable, aggressor inferable).
- **For the mandate's research question:** effectively **TIER_C** — a 2-week single-period sample is NOT a governed dataset "suitable for
  the research." Concretely: XAU structural-break events in the entire GC overlap = **42** (vs ~16,000 across full history), in **1**
  contiguous period. This **cannot** satisfy the candidate gate's independent-period (§21.6) or cross-era (§15) requirements, and any
  discriminator on N=42 single-period events would be noise — exactly the over-fitting §16/§18/§22 forbid promoting.

## Decision (§4)
Usable GC data for GOLD_ORDER_FLOW_DISCOVERY_V1 does **NOT** currently exist. Per §4/§22, **no discovery is run** (running a contrast on
42 single-period events and reporting it as discovery is explicitly forbidden). Deliverable = this audit + `GOLD_ORDER_FLOW_DATA_NEED_V1.md`.
The relevant existing empirical evidence (the 2 prior MBO-divergence runs on this sample) is already NEGATIVE. **STOP; CEO decision required.**
