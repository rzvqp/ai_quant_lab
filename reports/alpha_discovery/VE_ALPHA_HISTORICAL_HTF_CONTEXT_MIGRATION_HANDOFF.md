# VE Alpha Historical HTF/PDH Context Migration — Handoff

**Mandate**: `VE-ALPHA-HISTORICAL-HTF-CONTEXT-MIGRATION-001`. **Date**: 2026-08-21. **Division**: Validation
Engine (VE). **Authorizing report**: `ALPHA_HISTORICAL_REREVIEW_WAVE1_REPORT.md` (commit `0a73877`).
**CEO Directive constraints honored**: `ENGINEERING_ONLY`, `NO_ALPHA_SCORING`, `NO_PROFITABILITY_TEST`,
`NO_VALIDATION_CONSUMPTION`, `NO_FUTURE_LEAKAGE`, `PRESERVE_HISTORICAL_SEMANTICS`, `ENABLE_DEVELOPMENT_REPLAY`,
`NO_AI_TRADER`, `NO_LIVE`.

This document is written for the Alpha Discovery department to consume the migrated fields without
re-deriving any of the engineering below. Structured against the mandate's own §11 (10 required items).

---

## 0 — Governance finding surfaced before anything else (read this first)

**Wave 1's own "DEVELOPMENT" population (`dt < 2018-05-01`, 160,888 bars, `hist_rereview.py`) was NOT
manifest-gated** — it reads the raw M15 CSV directly via `mstrat.load()` with no discovery-block filtering,
silently including **54,118 bars (~34% of that population) from an unratified gap** between the manifest's
discovery block 0 (ends 2013-09-27) and block 1 (starts 2016-01-11). A same-day sibling report
(`ALPHA_DISCOVERY_AUTONOMOUS_CAMPAIGN_REPORT.md`), using the project's properly-gated loader
(`edge_research._common.load()`), correctly restricts to **105,254 bars** for the equivalent window. Both
reports call their population "DEVELOPMENT."

This migration uses **only the manifest-ratified discovery blocks** (105,254 bars: block 0 2011-07-26→
2013-09-27 + block 1 2016-01-11→2018-04-06) as its DEVELOPMENT population, and its own gap-safety guard
(§0/§4 below) actively **excludes** the unratified gap rather than silently filling it. This is a deliberate,
disclosed choice, not an oversight: the discovery-block rule exists specifically to prevent leakage across
regime-segment/embargo boundaries (the manifest's own stated principle — "an HTF bar built from a sealed or
embargoed constituent is not a possible leak, it is a certain one"), and this mandate's `NO_FUTURE_LEAKAGE`/
`PRESERVE_HISTORICAL_SEMANTICS` constraints point the same direction. **If Wave 2 re-review uses the
160,888-bar (ungated) population instead, its results are not directly comparable to this migration's own
verified coverage figures below**, and ~34% of that population will show these context fields correctly absent
by construction (not a bug — see §4).

---

## 1 — Historical semantics (recovered from official repository artifacts, not approximated)

| Field | Historical definition | Recovered from |
|---|---|---|
| `h4_trend_up` | `EMA(20, close) > EMA(50, close)`, computed on the H4 series' **own** close prices (pandas `.ewm(span=X).mean()`, default `adjust=True`) | `code/mtf.py::_ind()` (frozen, reused unmodified) |
| `h1_trend_up` | Same formula, on the H1 series' own close prices | `code/mtf.py::_ind()` (frozen, reused unmodified) |
| `d1_trend_up` | Same formula, on the D1 series' own close prices | `code/mtf.py::_ind()` (frozen, reused unmodified) |
| `pdh` / `pdl` | High / low of the most recently **fully closed** D1 bar | `code/s1.py::load_s1()` (frozen, reused unmodified) |

**Source timeframe**: H4/H1/D1 bars, each timeframe's own OHLC series (NOT resampled per-M15-bar; a step
function that updates only at H4/H1/D1 close and holds until the next close).

**Causal timestamp**: `avail = time.shift(-1)` per bar (the bar becomes usable once the *next* bar of that
timeframe starts, i.e. once it is fully closed); the last bar in each file gets `avail = last_time + period`
(no next row to shift from). Joined onto M15 via `pandas.merge_asof(direction='backward')`.

**Warmup**: `EMA(span=X, adjust=True)` has **no warmup gate** in the inherited formula — the first bar of any
series produces *some* trend_up value immediately (this is `mtf.py`'s own existing behavior, not something
this migration added or should "fix"; fixing it would be redefining a frozen formula, out of scope). By
contrast `atr`/`rsi`/`volrank` (computed alongside `trend_up` by the same `_ind()` call but not part of this
migration's required fields) genuinely need 14/14/60 bars respectively before producing a value — verified
directly (`tests/test_htf_context_historical.py::test_atr_and_rsi_do_have_a_real_warmup_gate...`).

**Session/day boundary**: H4 and D1 anchor to **17:00 America/New_York, DST-aware** (`code/resample_ny.py`,
independently confirmed against the raw `D1_from_M15_v2.csv` bars themselves: every single D1 bar opens at NY
wall-clock hour 17 regardless of season — 22:00 UTC in winter/EST, 21:00 UTC in summer/EDT).
**H1 uses plain UTC-hour flooring** — explicitly *not* NY-anchored (confirmed: every H1 bar's epoch is an exact
multiple of 3600). `pdh`/`pdl` inherit the D1 (NY-17:00) day boundary, since they are read directly off the
D1 series.

**Lookback**: none beyond the bar's own EMA/rolling state — no additional history window is consulted per
M15 bar beyond what the causal join already resolves.

**Missing-data behavior**: where a required prior bar doesn't exist (before any data starts, inside the
unratified gap, or right at a discovery-block edge with insufficient lookback), the field is `NaN` — never
approximated, never forward-filled across a gap (see §4, the new safety guard this migration adds).

---

## 2 — Migrated feature identities

| Field | Needed by | Notes |
|---|---|---|
| `h4_trend_up` | S9 (both variants), S20 | S20 has **no** `h1_trend_up` dependency (confirmed by direct code reading of `s20_setups` — the report's loose "h4/h1 unpopulated" phrasing over-states S20's actual dependency) |
| `h1_trend_up` | S9 `conf1h='align'` variant only (`C_d008e0a4`) | S9 `conf1h='any'` variant (`C_0bb5095b`) does not read it |
| `d1_trend_up` | not required by S9/S20/S1 | included for completeness/parity with `mstrat.load()`'s own schema |
| `pdh` / `pdl` | S1-PDH/PDL (both variants: `C_dca5629f`, `C_9214b37b`) | S1-PDH/PDL has **no** `h4_trend_up`/`h1_trend_up` dependency at all (confirmed by direct code reading of `s1_setups`) |
| `pd_open`/`pd_close`/`pd_mid`/`pw_high`/`pw_low` | not required by S9/S20/S1 | provided only for full `mstrat.load()` schema parity via `load_mstrat_historical()` (§9) |

---

## 3 — Source paths

| What | Path |
|---|---|
| New module (additive, `mtf.py`/`s1.py`/`mstrat.py` byte-untouched) | `code/htf_context_historical.py` |
| Tests | `tests/test_htf_context_historical.py` |
| Underlying resampled HTF bars (already existed, Data Acquisition Mandate 2.7, `generate_htf_context.py`) | `data/market/OANDA_XAUUSD_{H1,H4,D1}_from_M15_v2.csv` |
| Governance/ratification record | `config/split_manifest.json` → `context_derived_htf` |
| M15 source (unmodified, already covers 2011-07-26 onward) | `data/market/OANDA_XAUUSD_M15.csv` |

---

## 4 — Causal timing, and the new safety guard this migration adds

The causal-availability convention (`avail = time.shift(-1)`, `merge_asof(direction='backward')`) is reused
byte-for-byte from `mtf.py`/`s1.py` — see §1.

**New guard, not present in `mtf.py`/`s1.py` (never needed there, since the native 2023+ files have no
internal gaps)**: the `_from_M15_v2` files are built under Statistician's single-discovery-block rule — an
HTF bar exists only if entirely within one ratified `m15_v2_discovery_block` — but that rule protects only the
*bar itself*. A plain `merge_asof(direction='backward')` join can still silently **bridge across** the gap
between two non-adjacent blocks: an M15 bar from, say, 2015 (inside the 2013→2016 gap) would otherwise match
the stale H4 bar from ~2013-09 (the last one before the gap), producing a value up to ~2.3 years out of date.
**Measured directly**: without this guard, **158,676 of 355,696 M15 bars (~45%)** would have received a
silently-stale `h4_trend_up` value. This migration adds an explicit same-discovery-block check on every join
(`code/htf_context_historical.py::_merge_gapsafe`): a value is used only if the M15 row's own timestamp and
the matched HTF bar's own bar-start timestamp fall in the *same* ratified block; otherwise `NaN`. Proven via a
dedicated mutation test (`test_mutation_disabling_the_block_guard_reintroduces_stale_bridging`) that the guard
is load-bearing, not incidental.

---

## 5 — DEVELOPMENT coverage (measured directly against the real data, not estimated)

Population: the two ratified discovery blocks inside the mandate's 2011–2018 target (§0).

| | Block 0 (2011-07-26 → 2013-09-27, 52,403 bars) | Block 1 (2016-01-11 → 2018-04-06, 52,851 bars) | Combined (105,254 bars) |
|---|---:|---:|---:|
| `h4_trend_up` | 99.9657% | 99.9622% | 99.9639% |
| `h1_trend_up` | 99.9886% | 99.9924% | 99.9905% |
| `d1_trend_up` | 99.7863% | 99.7275% | 99.7568% |
| `pdh` / `pdl` | 99.7863% | 99.7275% | 99.7568% |

First/last valid timestamp per field, per block:

| | Block 0 first valid | Block 0 last valid | Block 1 first valid | Block 1 last valid |
|---|---|---|---|---|
| `h4_trend_up` | 2011-07-26 21:00 UTC | 2013-09-27 16:30 UTC | 2016-01-11 14:00 UTC | 2018-04-06 11:45 UTC |
| `h1_trend_up` | 2011-07-26 18:00 UTC | 2013-09-27 16:30 UTC | 2016-01-11 10:00 UTC | 2018-04-06 11:45 UTC |
| `pdh`/`pdl` | 2011-07-27 21:00 UTC | 2013-09-27 16:30 UTC | 2016-01-12 23:00 UTC | 2018-04-06 11:45 UTC |

**Missing interval / source gap**: 2013-09-27 16:45 UTC → 2016-01-11 09:00 UTC (54,118 M15 bars, all context
fields correctly `NaN` — this is the manifest's unratified gap, not a data-availability gap; the raw M15
prices themselves are continuous through this period, confirmed directly, ~23,801 bars in calendar-2014 alone).
**Warmup loss**: sub-0.3% per block, concentrated at each block's own opening edge (the first HTF bar of a
fresh block needs one bar-period to become "available").

**On the Wave1 report's own 160,888-bar (ungated) population**, for direct comparison: `h4_trend_up` coverage
is 65.40%, `h1_trend_up` 65.41%, `pdh`/`pdl` 65.26% — i.e. exactly the ~35% the unratified gap represents,
correctly absent, not a defect (§0).

---

## 6 — Tests

`tests/test_htf_context_historical.py`, 25 tests, all passing, covering exactly the mandate's §9 list:
hash/ratification gate (incl. a tampered-hash mutation check), H4/H1/PDH/PDL causality (both a hand-built
3-bar boundary check and a full-dataset no-lookahead proof), session-boundary DST-awareness, the EMA
no-warmup-gate (documented as intentionally inherited, contrasted against ATR/RSI's genuine gate),
discovery-block gap exclusion plus a dedicated mutation test proving the guard is load-bearing (not
incidental — disabling it via monkeypatch measurably reintroduces stale bridging), restart/determinism, and
two exhaustive (not sampled) global no-future-leakage proofs. Full repo regression (`pytest tests/ -q`):
166 passed / 3 failed, all 3 failures independently confirmed pre-existing (reproduced identically with this
migration's files completely removed) and unrelated to this work.

---

## 7 — Fingerprints

| File | sha256 |
|---|---|
| `code/htf_context_historical.py` | `752a7f5c44ad6b2cf44a3f486b2544a8bbc6e0725918569b079cd10aa6c88714` |
| `tests/test_htf_context_historical.py` | `9cf320dddbf044a1a495bccb7897b549ae78049f3ef9305b1041943c88f49f5c` |

`code/mtf.py`/`code/s1.py`/`code/mstrat.py`/`code/alpha_lab.py`: byte-untouched (`git diff` = 0 lines — see
delivery commit).

---

## 8 — Known limitations

- **The unratified 2013-2016 gap** (§0/§5) — real, not fixable by this mandate (extending discovery blocks is
  Statistician's exclusive domain, not Data Acquisition's or VE's, per `config/split_manifest.json`'s own
  `who_does_what`).
- **`h4_trend_up`/`h1_trend_up` disagree with the native (2023+) pipeline in ~0.16%/0.04% of the overlapping
  period** — traced precisely (not hand-waved): `pandas.ewm(adjust=True)` is a weighted average over *all*
  prior history with slowly-decaying weights (especially at `span=50`), so a computation with a genuinely
  longer warmup (this migration, sourced from the long `_from_M15_v2` history) will not be bit-identical to
  one with a short/zero warmup (the native pipeline, which starts cold at 2023-01-02) even far downstream —
  this is expected numerical behavior, not a bug, and if anything this migration's values are the more
  historically-faithful ones (longer real warmup) at those disagreement points.
- **`pdh`/`pdl` match the native pipeline 100.000% exactly** on the full overlap (65,638 bars) — no warmup
  ambiguity for a mechanical prior-day lookup, so this is a clean equivalence proof with zero caveats.
- **The known `TICK=0.1` bug** (should be `0.01` — fixed on `wp5b` via commit `38e7165`/RT-CODE-A-0007, but
  NOT present on this repo's `alpha-automation-v1` branch, and this is the copy `hist_rereview.py`'s own
  `sys.path` order actually resolves to at runtime, despite naming `wp5b` first) does **not** affect any field
  in this migration (`h4_trend_up`/`h1_trend_up`/`d1_trend_up`/`pdh`/`pdl` have zero dependency on `TICK` —
  it only enters cost/stop-distance calculations downstream, in `simulate()`). Flagged here because any Wave 2
  economic evaluation built on top of this migration will inherit it unless separately fixed — out of this
  mandate's scope (`NO_PROFITABILITY_TEST`) to correct.
- **`hist_rereview.py` as currently committed cannot reproduce its own `hist_rereview_records.json`** — the
  script's only path that could emit `"HISTORICAL_CANDIDATE_IMPLEMENTATION_MIGRATION_REQUIRED"` is a generic
  6-key exception handler, but the actual JSON records have the 13-key shape of the *success* path. The
  underlying finding (all 5 target candidates produce 0 setups pre-migration, because `h4_trend_up`/
  `h1_trend_up`/`pdh`/`pdl` are genuinely `NaN` before 2023-01-03) was independently re-verified directly
  against the raw data and the real `mstrat.py` signal functions (§9) and is **true** — but whatever script
  literally produced that JSON's polished diagnostic text is not the version currently in git. Also, `hist_
  rereview.py`'s own `n1_ledger.npz` sidecar dependency is missing from the repo entirely (would need
  rebuilding via `reports/n1_rerun/build_n1_ledger.py` before that specific script could run fresh end-to-end)
  — unrelated to HTF/PDH context, flagged for completeness since Wave 2 will likely want to reuse the same
  harness shape.
- `pw_high`/`pw_low` (not required by S9/S20/S1) use a slightly looser gap-guard approximation (the weekly
  aggregate's own end-of-week timestamp, not a per-constituent-day check) — acceptable for a non-required
  bonus field, disclosed rather than silently accepted.

---

## 9 — Exact Alpha replay instructions

```python
import sys
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\code")
import htf_context_historical as H

# Full mstrat.load()-schema drop-in (54 columns, verified identical to native mstrat.load()'s own schema):
d = H.load_mstrat_historical()

# Restrict to the PROPERLY-GATED DEVELOPMENT population (105,254 bars -- see SS0 for why, not the
# ungated 160,888-bar `dt < 2018-05-01` population hist_rereview.py currently uses):
blocks = H.discovery_blocks()
dev = d[((d["time"] >= blocks[0][0]) & (d["time"] < blocks[0][1])) |
        ((d["time"] >= blocks[1][0]) & (d["time"] < blocks[1][1]))].reset_index(drop=True)

# Feed directly into the UNCHANGED, frozen signal functions -- no adapter needed, schema matches exactly:
import mstrat
setups_s9  = mstrat.s9_setups(dev, {"c4h": "up", "conf1h": "any", "lb": 20, "stop": "structural", "exit": "rr2"})
setups_s20 = mstrat.s20_setups(dev, {"ctx": "h4up", "exit": "rr3", "lb": 50, "stop": "atr", "trig": "breakout"})
setups_s1  = mstrat.s1_setups(dev, {"side": "low", "liq_ref": "pdh_pdl", "liq_lb": 20, "confirm": "consecutive2",
                                    "imb": "none", "stop": "beyond_sweep", "exit": "rr2", "window": 8})
```

If instead only the isolated context columns are wanted (e.g. to merge onto an existing dataset):
`H.load_mtf_historical()` returns M15 + `h4_trend_up`/`h1_trend_up`/`d1_trend_up` (+ `m_*`/`session`);
`H.load_s1_historical()` adds `pdh`/`pdl` + the M15-only S1 columns (`rmax`/`rmin`/`fvg`/`disp`/etc., all
already fully available back to 2011, untouched by this migration).

**Do not** call `mtf.load_mtf()`/`s1.load_s1()`/`mstrat.load()` (native) expecting DEVELOPMENT coverage — those
remain byte-unchanged and still only cover 2023-01-03 onward for these 4 fields, exactly as before this
migration.

---

## 10 — Candidates enabled

All 5 previously-`MIGRATION_REQUIRED` candidates now produce real signals on the properly-gated DEVELOPMENT
population (verified directly against the real, unmodified `mstrat.py` signal functions — **counts only,
no profitability/return evaluation performed, per `NO_PROFITABILITY_TEST`**):

| Candidate | Setups on DEVELOPMENT (105,254 bars) |
|---|---:|
| S9 `C_0bb5095b` (`c4h=up,conf1h=any,exit=rr2,lb=20,stop=structural`) | 3,252 |
| S9 `C_d008e0a4` (`c4h=up,conf1h=align,exit=rr3,lb=10,stop=structural`) | 3,189 |
| S20 `C_09d2245b` (`ctx=h4up,exit=rr3,lb=50,stop=atr,trig=breakout`) | 1,200 |
| S1-PDH `C_dca5629f` (low, `confirm=consecutive2,exit=rr2`) | 1,652 |
| S1-PDH `C_9214b37b` (high, `confirm=displacement,exit=rr3`) | 603 |

(S1-swing `C_954698b1`, already fully DEVELOPMENT-replayable pre-migration and already scored `FAIL` in Wave
1, is unaffected by this migration and not re-tested here.)

---

## Final status

```
HISTORICAL_HTF_CONTEXT_MIGRATION_READY
S9_S20_S1_PDH_DEVELOPMENT_REPLAY_ENABLED
READY_FOR_ALPHA_REREVIEW_WAVE2
```

Caveat carried forward explicitly (not a blocking condition, per mandate §12's own "if all required fields are
faithfully available" — they are, over the ratified population): Wave 2 should use the 105,254-bar
manifest-gated DEVELOPMENT population (§0), not Wave 1's own 160,888-bar ungated one, for results to be
correctly comparable to the coverage figures in this handoff. No Alpha hypothesis, strategy design, backtest
P&L, or profitability judgment was produced by VE — economic evaluation is Alpha Discovery's own next step.
