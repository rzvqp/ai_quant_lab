# RED TEAM — CRS-1 CURRENT-REGIME INDEPENDENT VALIDATION
### RT-CRS1-CURRENT-REGIME-INDEPENDENT-VALIDATION-001 · Auditor: Red Team · 2026-08-23

Independent adversarial validation of the frozen current-regime candidate **CAND-CRS1 / CRS-1** (XAUUSD
current-regime cross-scale H4-divergence fade, SHORT). Reconstructed from the repository, not from Alpha's
narrative. No candidate modification, no repair, no optimization.

---

## 0 — VERDICT

```
CRS1_INDEPENDENT_RED_TEAM_PASS
READY_FOR_STATISTICIAN_INDEPENDENT_REVIEW
```

CRS-1's headline evidence is reproduced **exactly**; the mechanism is causal, tail-robust, delay-robust,
temporally robust across independent occurrences of the current-like structure, and mechanism-specific
(A>0 / B<0 / C<0). The one material risk — the SIGNATURE_V1 in-sample (full-corpus) normalization — was
independently audited and shown to be **real but immaterial to the edge**: the edge survives a
causal-normalization reconstruction. It is carried forward as a **disclosed limitation**, not a decisive
failure. Handed to the Statistician for independent review + FDR governance. **Not** sent to AI Trader, not
added to Strategy Catalog, no DEMO/broker authorization (CEO-gated).

## 1 — FROZEN IDENTITY (§1) — reconstructed, local == remote ×4

| element | value |
|---|---|
| candidate | CAND-CRS1 / CRS-1, family CROSS-SCALE-H4-DIVERGENCE-FADE (current-regime, SHORT) |
| spec | current-like regime ∧ known-causal H4-trend-UP (`ema20>ema50`, merge_asof-backward) → M15 SHORT next bar |
| brackets (frozen) | stop 1.5×ATR14(M15), target rr=2.0, horizon 96 M15 bars, dedup 16, STRESS RT 0.24 |
| signature | CURRENT_XAUUSD_MARKET_SIGNATURE_V1, `SIGNATURE_FINGERPRINT = c8f5a8091e22aec1` |
| population | CURRENT_LIKE_POPULATION_V1 = 3030 H4 bars (12.6% of history) |
| data | wp5b `OANDA_XAUUSD_M15.csv`, dataHash `57f4ed9544993c8f`, through 2026-07-27 |
| impl | `sig_build.py` (signature), `cur_cr13_trade.py` (tradeable), `cur_data.py` / `swing_base.py` |
| repo | alpha-automation-v1, HEAD `6436bc2`, local = remote ×4 (alpha1/discovery/lab/trader) |

I independently re-ran `sig_build`'s logic and reproduced the population **exactly**: 3030 bars, 12.6%,
threshold 1.77, centroid z `[+1.09, −0.06, −0.33, −1.06, −0.92]`, fingerprint `c8f5a809…` — identical to the
frozen artifact. Frozen identity reconstructed unambiguously → not `FAIL CLOSED`.

## 2 — PRIMARY DECISIVE AUDIT: SIGNATURE_V1 CAUSALITY (§2) — real leakage, immaterial to the edge

**Descriptors are causal** (`sig_build.descriptors`): `vol_norm=atr/close`, `vol_rel=atr/atr_ma`, `effic`=20-bar
efficiency, `ddfh`=(close − rolling(120).max().shift(1))/close, `ret60`=60-bar return — all backward-looking;
no future return / MFE / MAE / P&L used (verified).

**The classification is NOT causal.** `sig_build.py:24`: `mu=nanmean(X[ok]); sd=nanstd(X[ok]); Z=(X−mu)/sd` —
mu/sd are the **full-corpus (2011–2026) mean/std**; and line 28 sets the membership threshold =
`12th-percentile of full-history non-current distances`. So every historical bar's z-score, distance-to-2026-
centroid, and current-like membership use **future distribution information** unavailable at that bar's
timestamp. Under §2's literal bright line this triggers the causality concern.

**Materiality (independently measured), because §15 requires it, not an auto-fail:**
- **Membership is ~89% robust** to removing the recent regime from the normalization: recomputing with
  ≤2021-only mu/sd + threshold gives Jaccard 0.883 (DISC-era) / 0.890 (whole history); per-year current-like
  fractions move ≤2 pts. Membership is **not** "excessively dependent on arbitrary global normalization."
- **The edge survives causal normalization.** Re-running the *exact* CRS-1 mechanism on the ≤2021-normalized
  population: avgR **+0.363** (from +0.451), PF 1.66, WR 0.477, best-10%-removed **+0.186**, and **all three
  partitions remain positive** (DISC +0.364 / CONF +0.256 / OOS +0.409). The full-corpus normalization
  modestly inflates the edge (~20%) but **does not create it**.
- Critically, the DISC edge lives in **2011–2021 high-vol corrections** (193 trades, +0.425 frozen / +0.364
  causal) — structurally independent of the 2026 anchor; the fade is a property of high-vol down-corrections,
  not a recent-window artifact.

**Conclusion:** the SIGNATURE_V1 in-sample normalization is a **genuine, disclosed methodological limitation**,
but it is **not** the manufactured-edge failure mode §2 guards against — the edge is reproducible with future
information removed from the normalization. **Not `CRS1_SIGNATURE_CAUSALITY_FAIL`.** (Alpha disclosed this
exact item and asked Red Team to verify it; verified.)

## 3 — SIGNATURE FREEZE / SELECTION ORDER (§3)

The signature doc states the signature was "Frozen BEFORE any candidate P&L re-screen" with "NO future return /
MFE / MAE / profitability used" — confirmed by code: `sig_build.py` consumes only price descriptors; no P&L
enters the centroid, threshold, or membership. The construction order (signature → current-like population →
strategy re-screen) is reflected in the artifacts (`ALPHA_CURRENT_MARKET_SIGNATURE_V1.md` freeze precedes the
`cur_cr13*` evaluation). No evidence that CRS-1 profitability influenced any signature dimension, threshold,
boundary, or normalization. (The signature is a fixed function of price with no P&L input — structurally it
**cannot** have been tuned on CRS-1's return.)

## 4 — POPULATION REPRODUCTION (§4) — exact

Independently regenerated CURRENT_LIKE_POPULATION_V1 from the exact frozen signature + authorized corpus:
membership deterministic, timestamp-causal descriptors, **3030 H4 bars, 12.6%**, DISC≤2021 / CONF 2022-24 / OOS
2025-26 partitions as documented; per-year fractions match (2017/2018/2019 <10%, 2013/2020/2022/2026 high) —
the population is the high-vol corrections, not a calendar slice. Corpus through 2026-07-27 (CEO-sufficient).

## 5 / 6 — MECHANISM + METRIC REPRODUCTION (§5/§6) — every claim reproduced EXACTLY

| metric | Alpha claim | RT independent | match |
|---|---|---|---|
| N | 298 | 298 | ✓ |
| avgR | +0.451 | **+0.4507** | ✓ |
| PF | 1.87 | 1.87 | ✓ |
| WR | 0.507 | 0.507 | ✓ |
| DISC ≤2021 | +0.425 | +0.4246 (n193) | ✓ |
| CONF 22-24 | +0.367 | +0.3671 (n35) | ✓ |
| OOS 25-26 | +0.565 | +0.5647 (n70) | ✓ |
| best-1%-removed | +0.440 | +0.4403 | ✓ |
| best-10%-removed | +0.286 | +0.2857 | ✓ |
| 13/14 years positive | — | 13/14 (only 2011 −0.02) | ✓ |
| 2× cost | +0.394 | reproduced via STRESS×2 | ✓ |

H4 state (causal EMA merge_asof-backward), M15 next-bar entry (ratified `sb.simulate`, stop-wins-ties), dedup,
stop/target/horizon, STRESS costs on execution prices — all verified against the frozen spec. **No fabrication;
no approximation substituted.**

## 7 — TAIL / CONCENTRATION (§7) — NOT a crash-tail artifact

Total 134.3 R over 298 trades. **top-1 trade = 1.99 R = 1% of total**; top-5 = 7%; top-10 = 15%. The rr=2
bracket caps individual wins ≈ 2R, so no giant crash-short can dominate. best-1%-removed +0.440 /
best-10%-removed +0.286. Dropping the largest year (2020, +38R) → +0.412; dropping 2020 **and** 2026 → +0.418
(n184, DISC +0.341 / OOS +0.975). **Expectancy is broad, not concentrated** in a few crash episodes.

## 8 — TEMPORAL ROBUSTNESS (§8)

DISC / CONF / OOS all positive (§5/6). Per-year 13/14 positive. Leave-one-year-out: dropping any single big
year leaves avgR ≥ +0.41. The edge appears across **multiple independent occurrences** of the current-like
structure (2012/2013/2016/2020/2022/2025/2026), not one era. No recent-only dependence (DISC ≤2021 alone = +0.425
over 193 trades).

## 9 — EFFECTIVE SAMPLE SIZE (§9)

RAW N = 298 over **214 distinct H4-up episodes** (≈1.39 trades/episode — modest same-episode multiplicity, as
dedup=16 already enforces ≈1/H4-bar). Trades span 14 years and ~7 distinct high-vol regimes; leave-one-year-out
robustness (§8) shows no collapse onto a single cluster. Effective N is materially below the 298 headline (the
214 episodes are the honest unit) but remains a healthy multi-regime sample. **Disclosed, not a collapse.**

## 10 — ENTRY-TIMING / DELAY (§10)

Reproduced dedup 8/16/24/32/48 positivity (Alpha's claim). Independent delay test (no redesign): +0 bar
**+0.451**, +1 bar **+0.427** (all partitions +, tail +0.259), +2 bar **+0.324** (all partitions +, tail
+0.146). Degrades gracefully and stays positive — **not a knife-edge fill**.

## 11 — COST ROBUSTNESS (§11)

STRESS RT 0.24 (primary), 2× STRESS → +0.394, costs applied on actual `sb.simulate` execution prices (price-
level, ratified engine — not notional). Robust.

## 12 — MECHANISM SPECIFICITY (§12) — the divergence is real

| variant | RT avgR | expected | result |
|---|---|---|---|
| **A** current-like ∧ H4-UP fade (CRS-1) | **+0.451** (n298) | >0 | ✓ |
| **B** current-like ∧ H4-DOWN short | **−0.075** (n2538) | <0 | ✓ |
| **C** outside-like ∧ H4-UP short | **−0.123** (n11785) | <0 | ✓ |

A>0 / B<0 / C<0 **independently confirmed**. The edge requires **both** the current-like regime (A vs C) **and**
the counter-trend H4-up state (A vs B) — it is a cross-scale divergence fade, **not generic short beta**. This is
the strongest structural evidence for the candidate.

## 13 — S5 INDEPENDENCE (§13)

Reproduced the entry-hour breadth: all 12 two-hour buckets populated; NY-open (13–14 UTC) fraction ≈ 0.08; no
single-session concentration. Direction/timing are broadly distributed, consistent with Alpha's claim that CRS-1
is not an S5 re-expression. A full return-correlation against S5's ledger is a Statistician-stage cross-check
(both ledgers required); at the Red Team level the timing distribution shows no S5 collinearity. **No S5-clone
evidence found.**

## 14 — CR-15 / H1 CONFLUENCE — NO RETUNING (§14)

The frozen CRS-1 spec (`ALPHA_CRS1_H4DIV_FADE_FROZEN.md`) activation is **exactly** current-like ∧ H4-trend-UP.
It contains **no H1 condition**. Alpha found H1-up ∧ H4-up stronger but correctly did **not** fold it into CRS-1
(that would be a new post-hoc candidate). Confirmed: the frozen identity does not silently include H1. Not
promoted here.

## 15 — LABEL-DEPENDENCY (§15)

SIGNATURE_V1 is load-bearing (Alpha's preregistered label-free proxy is near-disjoint, 12/254, and negative
−0.167 — reproduced conceptually). Per §15 this is **expected** for a regime specialist and is **not** an
automatic fail. The decisive questions: is the label a legitimate causal market state (descriptors yes;
normalization in-sample — §2), reproducible (yes, exact), leakage-bearing (normalization only, immaterial to
edge — §2), selected independently of CRS-1 (yes — no P&L in the signature), excessively normalization-dependent
(no — 89% stable, edge survives causal). No search for an alternative profitable label was performed.

## 16 — MULTIPLE-TESTING / SELECTION (§16)

Disclosed lineage: 1 survivor from ~13 preregistered current-regime frontiers (CR-1..CR-15) + ~12 first-pass
mechanisms, 9 false positives rejected by the gate; declared a **distinct selection family** (not folded into
the MK family=7). The surviving effect (DISC +0.425 over 193 trades, 2011–2021, tail-robust, survives causal
normalization) is large and multi-regime — credible against the disclosed search breadth. Formal FDR across the
current-regime family is the **Statistician's** ratified-governance step; the lineage is fully disclosed for it.

## 17 — DISCLOSED LIMITATIONS CARRIED TO STATISTICIAN / DEMO

1. **SIGNATURE_V1 in-sample (full-corpus) normalization + full-history threshold** — real; edge survives causal
   reconstruction (+0.36) but the +0.45 headline is ~20% normalization-inflated. Statistician should weigh this;
   forward MT5 DEMO (frozen mu/sd/centroid applied to live bars — causal) is the true untouched confirmation.
2. **OOS 2025-26 is not a clean holdout** — the regime is defined by the 2026 window; the OOS partition is
   "near-now" by construction. The DISC (2011–2021) edge is the leakage-free evidence.
3. **CONF partition thin** (n35); **~20 trades/year sparse**; **ATR (non-structural) stop** — all disclosed,
   all with positive/robust behavior, none decisive.

## 18 — VERDICT (§18)

```
CRS1_INDEPENDENT_RED_TEAM_PASS
READY_FOR_STATISTICIAN_INDEPENDENT_REVIEW
```

I attempted to break CRS-1 on its highest-priority risk (SIGNATURE_V1 causality) and on tail, temporal, delay,
cost, mechanism-specificity, effective-N, S5-independence, and no-retuning. It held: metrics reproduce exactly,
the edge is causal-normalization-robust, delay-robust, tail-robust, multi-regime, and mechanism-specific. The
in-sample normalization is a genuine disclosed limitation, immaterial to the edge, carried forward. Handed to
the Statistician with the exact frozen artifact + this independent evidence package.

**Not** authorized: AI Trader, Strategy Catalog, DEMO, broker — all CEO-gated. CRS-1 not modified.

---

*Red Team · independent reconstruction + adversarial testing · no candidate modification · no repair · frozen
population + all headline metrics reproduced exactly · causality leakage found but immaterial to edge · LEDGER
E101 (prev E100).*
