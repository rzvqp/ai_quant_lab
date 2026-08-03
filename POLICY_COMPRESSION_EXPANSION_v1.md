# POLICY — Compression-to-Expansion Breakout — canonical schema

**candidate_id: `CAND-0002`.** Design artifact only. No execution, no data touched, no numeric parameter
chosen, no optimization, no variants, no SL method constructed. A **distinct family** from CAND-0001
(PDH/PDL reference-level reaction): this is a **volatility-state transition** — a low-volatility
compression resolving into a displacement/expansion breakout.

> **Two independent parts, not conflated.** **PART A (entry mechanism)** is built on **ratified,
> lookahead-safe primitives** (`market_state.py`, ratified Statistician v2.6.1 `2fb948f`) and is **fully
> DEFINED**. **PART B (risk management)** has **no ratified structural source** and is **UNSPECIFIED**.
> The market mechanism is present; only the risk-management *specification* is absent.

Grounded in ratified primitives `market_state.compression`, `market_state.expansion`, `market_state.atr14`
(verified before citing; `market_structure.py` MK-01 and `liquidity_mechanics.py` MK-02 are DRAFTS and are
NOT used). Ratified constants: `DISP_MULT=1.5`, `BODY_FRAC=0.5`, `ATR_WINDOW=14`, `COMPRESSION_WINDOW=460`,
`COMPRESSION_PCTL=10` (log-range Parkinson, E000).

| Field | Value |
|---|---|
| **policy_id** | `COMPRESSION-EXPANSION-BREAKOUT` |
| **version** | `1.1` (W10: cross-repo primitive-source references added; no mechanism change) |
| **family** | `volatility_state_transition` (market_state, MK Mandate 5.8) |

## Primitive source references — W10 (cross-repo grounding, verifiable without co-location)

The cited primitives live on a **different branch** than this policy (which is on `alpha-automation-v1`).
Pinned so a consumer can verify grounding without the files being co-located.

- **source_repository:** `github.com/rzvqp/ai_quant_lab-alpha-automation.git`
- **source_branch:** `discovery-mk-matrix-v1`
- **source_commit:** `8edbf9900b761b774b901a13a5b325be578468e6` (full)

| source_file | primitive(s) | source_hash (sha256 of file @ commit) |
|---|---|---|
| `code/market_state.py` | `compression`, `expansion`, `atr14`; constants `DISP_MULT=1.5`, `BODY_FRAC=0.5`, `ATR_WINDOW=14`, `COMPRESSION_WINDOW=460`, `COMPRESSION_PCTL=10.0` (ratified, Statistician v2.6.1 `2fb948f`) | `823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f` |

*Verify:* `git show 8edbf9900b761b774b901a13a5b325be578468e6:code/market_state.py | sha256sum`
against `alpha1/discovery-mk-matrix-v1`.

---

## PART A — ENTRY MECHANISM (ratified primitives) — **FULLY DEFINED, lookahead-safe**

| Field | Definition |
|---|---|
| **regimes_permitted** | *Numeric/selection decision reserved to the Statistician — not chosen.* |
| **timeframes_used** | **M15** for both compression and expansion (execution bars). No fixed-ATR *distance* is used as a signal (ATR enters only the ratified expansion criterion). |
| **activation** | A bar `i` is in a **valid compression state**: `is_valid[i]` (a full 460-bar trailing window exists, `i>=459`) **AND** `is_compressed[i]` = `ln(high[i]/low[i]) <= P10` over the trailing `[i-459, i]` (`market_state.compression`). **Strictly causal — zero lookahead** (module-verified: no bar `>i` enters the classification of `i`). |
| **trigger** | The **first expansion (displacement) bar immediately following a compressed bar**: `expansion[i]==True` **AND** `is_compressed[i-1]==True`. `expansion` = E010 criterion `range[i] > 1.5×ATR14[i-1]` AND `|close[i]-open[i]| >= 0.5×range[i]` (`market_state.expansion`) — lookahead-safe (prior-bar ATR + current bar only). |
| **entry** | **type:** breakout / continuation in the expansion direction. **direction:** `sign(close[i]-open[i])` of the expansion bar — bullish displacement → **long**, bearish → **short**. **moment:** `entry@next-open` (open of bar `i+1`; lookahead-safe). **reference price:** the expansion bar (`open[i]`/`close[i]`). |
| **invalidation** | Void before entry if the bar immediately after a compressed bar is **not** an expansion — the setup lapses; a subsequent compressed bar re-arms. *(1-bar adjacency; no numeric wait-window is chosen. Widening the compression→expansion wait window is a numeric parameter deferred to the Statistician.)* |
| **no_trade_rules** | No trade while `is_valid[i]`=False (the first 460 bars / any incomplete trailing window). No trade on an expansion bar **not** immediately preceded by a compressed bar (that is a plain displacement, not a compression breakout). **One entry per compression→expansion episode** — only the first qualifying expansion bar fires; no re-entry on consecutive expansion bars of the same episode until a new compressed bar re-arms. |
| **expiry** | The setup (a compressed bar) is evaluated only on the immediately following bar; if that bar is not an expansion, the setup expires (1 bar). No fixed multi-bar window is chosen. |
| **min_trades** (per policy & per regime) | *Numeric floor reserved to the Statistician — not chosen.* |

**PART A status: complete.** All mechanism fields defined and lookahead-safe. `regimes_permitted` /
`min_trades` are numeric parameters for the Statistician — the mechanism is fully specified around them.

### ⚠ Disclosed risk on the compression primitive (surfaced, not hidden — Red Team relevant)
`market_state.py` itself flags that **compression is the only genuinely un-anchored ratified primitive** —
no SMC family requires it; the definition (measure granularity, percentile level, `<=` vs `<`, window=460)
is "a definition choice, not an anchoring to a consumer," and the "ten-plausible-variants" risk is
**reduced (derived window) but not eliminated**. The parameters are ratified and the primitive is
lookahead-safe, so the mechanism is DEFINED — but Red Team should weigh this abstract-definition risk
explicitly. (`expansion` carries no such flag — it is anchored verbatim to E010.)

---

## PART B — RISK MANAGEMENT — **UNSPECIFIED (declared, stopped — no method constructed)**

Same standing gap as CAND-0001: fixed-ATR/RR risk is disqualified (identical 0.378–0.385 winrate across 6
mechanisms — structure dominated signal), and **no ratified structural stop/exit primitive exists** in the
repo (the cited v8.5 M_031–M_034 is confirmed nonexistent).

| Field | Declaration (method required · why absent) |
|---|---|
| **stop_loss** | **UNSPECIFIED.** Required: a ratified **structural** stop method for a volatility-breakout (e.g. anchored to the compression range's opposite extreme, or to the expansion bar's structural invalidation), as a **method not a value**, not fixed-ATR. Absent: no ratified structural-SL primitive exists. **Not constructed.** |
| **exit** | **UNSPECIFIED.** Same requirement / same gap — a ratified structural exit method. **Not constructed.** |
| **management** (partials / breakeven / trailing) | **UNSPECIFIED.** Fully dependent on the structural stop/exit above. **Not constructed.** |

**PART B status: blocked at the source** — a risk-layer specification gap, not a market-mechanism gap
(Part A is complete).

---

## Verdict — **PARTIALLY DEFINED**

Entry mechanism (Part A) complete and lookahead-safe (with the compression-anchoring risk disclosed); risk
management (Part B) unspecified for lack of a ratified structural source. The two are separate.

## Handoff
- **Part A → Red Team, phase A** (weigh the disclosed compression-definition risk explicitly).
- **Part B → Statistician, as a specification request**: a ratified structural stop/exit/management method,
  plus the numeric parameters (`regimes_permitted`, `min_trades`, any compression→expansion wait-window).

**Stop here — no execution, no promotion.** Next candidate produced when ready.
