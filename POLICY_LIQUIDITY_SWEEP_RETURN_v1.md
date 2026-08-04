# POLICY — Liquidity Sweep + Return — **v1.0 (Part A + Part B, screening)**

# 🟡 SCREENING_BASELINE · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED

**CAND-0020.** First candidate on the newly-ratified MK-02 (`liquidity_mechanics.py`). Mean-reversion
away from swept liquidity. Part A entry + one frozen, executable, family-native structural Part B —
single variant, composed from ratified primitives + raw OHLC, chosen BEFORE any result; no invention,
no lookahead, no optimization.

> **MK-01/MK-02 ratification note (Flow A flag, not a repair).** The CEO declares MK-01/MK-02 RATIFIED
> (fidelity 7/7 Statistician, 12/12 VE, three Red Team attacks, cascade semantics corrected + measured
> at v2.7.38). The git history at `000022555…` corroborates this exactly (`0000225` = "MK-01 cascade
> break semantics v2.7.38 + cascade-frequency measurement"; `f4f8fab`/`f9f910b` = Red Team F2/F3).
> **However, the module header at this commit STILL carries the boilerplate line "DRAFT DE REFERINȚĂ.
> Nu e cod verificat. Necesită… ratificare de o divizie."** I treat the CEO's directive + the
> corroborating verification history as authoritative and cite `0000225` with a freshly-computed hash;
> the stale DRAFT header should be updated at source. Flagged, not circumvented.

## PART A — ENTRY MECHANISM — **DEFINED**

Mechanism: institutional stop-hunt reversal. A liquidity pool (resting stops beyond a confirmed swing)
is **swept** — price penetrates the pool intrabar and **closes back inside** the range (the wick-sweep
signature). The sweep exhausts the liquidity that was fuelling continuation; price reverses AWAY from
the swept side.

| field | value · reason |
|---|---|
| **family** | `liquidity_sweep_reversal` (MK-02, `detect_sweeps` wick-sweep) |
| **timeframes_used** | single-TF (discovery TF); no MTF dependency |
| **activation** | a `LiquidityPool` is **available** — `build_pools` from a **confirmed labeled swing** (HH/LH→ABOVE, HL/LL→BELOW); `pool.available_idx = swing.confirmed_idx` (D1 lookahead-safe). |
| **trigger** | `detect_sweeps(..., require_close_back_inside=True)` fires a `SweepEvent` at bar `c`: for a BELOW pool `p` — `low[c] < p AND close[c] > p`; for an ABOVE pool — `high[c] > p AND close[c] < p`. **D6: both conditions on bar `c`, no lookahead.** `close_back_inside=True` is the wick-sweep signature. |
| **entry** | `next-open` after `c`. Direction = **reversal off the swept side**: BELOW-pool sweep (sell-stops taken, close back up) → **LONG**; ABOVE-pool sweep → **SHORT**. |
| **invalidation** | the sweep bar's own extreme is breached (see Part B stop). |
| **no_trade_rules** | pool consumed once (D7); a pool active only within its block from `available_idx` (D4). No trade if `next-open` already beyond stop or target. |
| **expiry** | the `SweepEvent` is the event; entry is the immediately-following bar or the signal lapses. |

**D2 population restriction (permanent, NOT circumvented):** `build_pools` ignores UNCLASSIFIED swings,
and MK-01's strict-inequality tie-break (D2) means **equal highs / equal lows never become swings** →
`build_pools` can never emit a pool on an equal-high/equal-low. This removes exactly the equal-highs /
equal-lows that are the archetypal liquidity structures — the measured selective cost is 24.8%–59.7% of
swings. **This is a permanent interpretive restriction on the candidate's population; I do not compensate
for it.** The tested population is "sweeps of strict-fractal swing pools," not "all liquidity sweeps."

**No F4 exposure:** the mechanism uses `detect_sweeps` only; it does **not** read CHoCH direction.

## PART B — RISK MANAGEMENT — **COMPLETED (screening, single structural variant)**

Family = liquidity-sweep reversal. The sweep's own geometry supplies the risk; the opposite pool supplies
the target.

| field | method · reason |
|---|---|
| **stop_loss** | **Beyond the sweep bar's swept extreme:** long → `low[c]` (the sweep low); short → `high[c]`. **Reason:** the wick-sweep's extreme IS the invalidation — a reversal that returns beyond the swept wick has failed. Raw OHLC at `c`, known at entry. |
| **exit** | **The nearest OPPOSITE-side liquidity pool**, from the same ratified `build_pools` set, available at entry (`available_idx ≤ c`): long → nearest ABOVE pool price above entry; short → nearest BELOW pool price below entry. **Reason:** swept liquidity is sought toward the opposite resting liquidity. **Backstop:** if no opposite pool is available → **20-bar `GROUP_A_HORIZON` live time-stop** (short-horizon reversal; the same live-valid constant used across CAND-0011/0013/0014). |
| **management** | **DECLARED ABSENT** — screening minimalism. |
| **sizing** | **Fixed 1R**, risk-normalized; no equity-%. |
| **min_trades** | **Deferred to the Statistician.** |

**Validity guard:** no trade if `next-open` is already beyond the sweep extreme (stop) or beyond the
opposite pool (target). All coords known at entry → **no lookahead**. **FAIL-CLOSED check:** stop = raw
OHLC extreme (ratified `SweepEvent.idx`); target = ratified pool price; time-stop = live-valid constant.
Composable — **method stands**.

## W10 CROSS-REPO REFERENCE BLOCK

| field | value |
|---|---|
| source_repository | `github.com/rzvqp/ai_quant_lab-alpha-automation.git` (remote `alpha1`) |
| source_branch | `discovery-mk-matrix-v1` |
| source_commit | `000022555e7344ccc89862dbb2091795ccbad25a` |

| primitive | source_file | source_hash (sha256 @ commit) |
|---|---|---|
| `detect_swings`, `label_structure` | `code/market_structure.py` | `f3dee97bbb619820d1d07ef288be4c2fd74c76d3f6d4101e0402bff53bf95623` |
| `build_pools`, `detect_sweeps` | `code/liquidity_mechanics.py` | `1531cffa7498c09b0e663062de874573bb1da13a092845686d261ae636fa32e3` |

*Verify the hash, don't assume it — `git show <commit>:<file> | sha256sum`.*

## Verdict — **DEFINED (SCREENING_BASELINE)** · NOT STATISTICALLY VALIDATED · NOT PRODUCTION APPROVED
