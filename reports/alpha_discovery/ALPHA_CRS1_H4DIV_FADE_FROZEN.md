# CRS-1 — XAUUSD Current-Regime Cross-Scale H4-Divergence Fade (SHORT)

**Status: `STATISTICAL_VALIDATION_FAIL` (2026-08-23) — INVALIDATED, not a portfolio edge, not DEMO-eligible.**
⛔ The Statistician (STAT-CRS1-INDEPENDENT-REVIEW-FDR-001) + VE causality repair (commit 91b7415) found the entire evidence below was produced through a temporal LOOKAHEAD in `cur_screen.like_at` (M15 entry read a regime label from its own not-yet-closed H4 bucket; ≤240 min ahead, 100% of entries). **CAUSAL REPLAY collapses CRS-1 from avgR +0.4507 (p 3.2e-08) to +0.0669 (p 0.243)**, and it now FAILS the skepticism gate (worst min-partition over year-drops = −0.152). ~85% of the apparent edge was look-ahead. **CRS-1 FAIL is final for this frozen identity. CURRENT_REGIME_SURVIVOR = 0.** The definitions were NOT altered to recover performance (forbidden). All numbers below are TAINTED — retained for provenance only. S5 is unaffected. Any genuinely new post-repair result gets a fresh identity under normal governance.

Mandate: ALPHA-XAUUSD-CURRENT-REGIME-SPECIALIST-DISCOVERY-001. Price-only XAUUSD. Discovered 2026-08-23.

## Causal state machine
- **ACTIVATION (both required, causal/known at bar close):**
  1. `current-like` regime label ON (frozen CURRENT_XAUUSD_MARKET_SIGNATURE_V1 / CURRENT_LIKE_POPULATION_V1, backward-looking H4 descriptors — unchanged, not retuned).
  2. Known (last fully-closed) **H4 trend is UP**: H4 `ema20 > ema50` (causal EMAs; merge_asof-backward on H4 close_time — the forming H4 bar is excluded).
- **OFF-SWITCH (either):** `current-like` OFF, OR known H4 trend flips DOWN (`ema20 <= ema50`). When S5's structure returns (trend regime), this specialist is naturally OFF.

## Mechanism (economic)
Inside a high-vol post-blowoff DOWN-correction (current-like), a counter-trend **H4-up bounce** is faded by the dominant down-flow. The M15 short has **asymmetric payoff**: down-resumption (target 2R) is larger/more frequent than bounce-continuation (stop 1.5 ATR). It is a **cross-scale DIVERGENCE** (M15 short against a higher-TF counter-trend bounce), NOT a trend-follow — proven by the diagnostic (H4-DOWN version is negative). This is why it clears the ~0.54 directional ordering ceiling that closed CR-1..CR-12: the entry conditions on the higher-TF state, not on M15 direction.

## Rules (exact, as tested)
- Universe/entry: any M15 bar with ACTIVATION true; deduplicated ~1 per H4 bar (dedup spacing 16 M15 bars; robust to 8–48).
- Side: **SHORT**. Entry: next M15 bar (ratified `sb.simulate` next-bar entry, stop-wins-ties).
- Stop: **1.5 × ATR14(M15)**. Target: **rr = 2.0** (i.e., 3.0 ATR). Horizon: 96 M15 bars (24h) hard exit.
- Costs: STRESS round-turn 0.24 USD (ratified adverse scenario).

## Evidence (all skepticism-gate checks PASS)
- Primary (1.5ATR, rr2): **N=298, avgR=+0.451 R, PF 1.87, WR 0.507.**
- Per-year: 13/14 years positive (only 2011 −0.02).
- Tail (directional-gain gate): best-1%-removed **+0.440**, best-10%-removed **+0.286** → NOT crash-tail-concentrated.
- Partitions: DISC≤2021 **+0.425** (n193) / CONF 22-24 **+0.367** (n35) / OOS 25-26 **+0.565** (n70) → all positive, OOS strongest.
- Neighbor stability (stop,rr): (1.5,1)=+0.246 / (2.0,2)=+0.473 / (1.0,3)=+0.367 → all positive, all partitions positive.
- Entry-timing (dedup 8/16/24/32/48): avgR +0.34..+0.47, best-10%-removed all >0, all partitions >0 at every spacing (the axis that killed CR-6 — passes).
- Leave-one-year-out: worst-case avgR +0.411; worst min-partition over all year-drops +0.196 (>0).
- Effective N: 298 trades over **214 distinct H4-up episodes**.
- S5-independence: entry hours broad (all 12 2h-buckets 15–44); frac NY-open 13-14 UTC = 0.08; frac 12-16 = 0.21 (~uniform).
- Regime-specificity: same short NOT-current-like avgR **−0.123** (N=11785) — loses outside the regime.
- Mechanism-specificity: same short when H4-DOWN (closed trend short) avgR **−0.075** (N=2538) — loses; edge is the divergence.
- Cost robustness: 2× STRESS RT → avgR **+0.394**.

## Answer to the CEO research question
"WHEN does the downside payoff become causally capturable WITHOUT tail-dependence?" → **When conditioned on cross-scale divergence (current-like regime AND counter-trend H4-up bounce).** The fade of the higher-TF counter-trend resolves down with asymmetric payoff, tail-robustly (best-10%-removed +0.29) — escaping the M15 ordering ceiling by conditioning on higher-TF state rather than M15 direction.

## Reproduce
`cur_cr13.py` (info), `cur_cr13_trade.py` (tradeable + neighbor), `cur_cr13_verify.py` (full skepticism gate). Data: wp5b OANDA_XAUUSD_M15.csv through 2026-07-27.

## Label-dependency (robustness probe, cur_cr13_robust.py)
CRS-1's regime gate (current-like / SIGNATURE_V1) is LOAD-BEARING: one preregistered label-free proxy (H4 down-slope + elevated vol + bounce) is near-disjoint from current-like (12/254 overlap) and the entry LOSES on it (avgR -0.167). The entry is therefore SPECIFIC to the current-like structure (by design for a regime specialist), but the edge is demonstrated ONLY under the specific SIGNATURE_V1 label; a naive structural proxy does not substitute. Red Team: verify the global-percentile label for any leakage (descriptors are backward-looking -> argued no forward leak, independent check warranted). Not fished for a confirming proxy.

Provenance fingerprint (rule string): CRS1|curlike&H4up|SHORT|SL=1.5ATR|rr=2.0|H=96|STRESS0.24|dedup16
