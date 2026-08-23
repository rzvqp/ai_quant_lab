# STAT — CRS-1 INDEPENDENT STATISTICAL REVIEW + FDR GOVERNANCE

**Mandate ID:** `STAT-CRS1-INDEPENDENT-REVIEW-FDR-001`
**Division:** Statistician (independent statistical validation)
**Date:** 2026-08-23
**Candidate:** `CRS-1` / `CAND-CRS1` — status `FROZEN_PENDING_INDEPENDENT_VALIDATION_CURRENT_REGIME`
**Red Team input:** `57b2883` — `CRS1_INDEPENDENT_RED_TEAM_PASS`, ledger E101

**CRS-1 was not modified, optimized, repaired, filtered or re-regimed.**

---

## 0 — PRIMARY VERDICT

```
CRS1_STATISTICAL_VALIDATION_FAIL
```

**Decisive blocker — a second, independent causality defect, not the one Red Team found:**

> The `current-like` activation gate is looked up by flooring the M15 entry time to **its own H4 bucket
> start** (`cur_screen.like_at`: `h4 = (t // 14400) * 14400`). That bucket's label is computed from the
> bucket's **completed** descriptors — its close, ATR, efficiency, drawdown-from-high and 60-bar return.
> **100.0% of the 12,083 candidate entries (and all 298 trades) are gated on an H4 bar that had not yet
> closed at entry**, with a median lookahead of **135 minutes** and a maximum of **240 minutes**.

Correcting **only** that alignment — leaving every frozen constant, threshold, stop, target, horizon and
dedup untouched, and using the *identical* `merge_asof`-backward-on-`close_time` convention that CRS-1's own
H4-trend gate already uses — collapses the candidate:

| | frozen (as tested) | causal alignment (C1) |
|---|---|---|
| N | 298 | 267 |
| **avgR** | **+0.4507** | **+0.0669** |
| PF | 1.87 | 1.10 |
| WR | 0.507 | 0.378 |
| **best-10%-removed** | **+0.279** | **−0.148** |
| years positive | **13 / 14** | **7 / 14** |
| **raw one-sided p (episode-clustered)** | **3.17 × 10⁻⁸** | **0.243** |

**85% of the reported edge is produced by the lookahead**, and what remains is not significant *before* any
multiplicity adjustment.

This is a different and more damaging defect than the SIGNATURE_V1 normalization issue in §2 of the mandate.
It is mechanical, affects every trade, and is decisive on its own.

---

## 1 — INDEPENDENT RECONSTRUCTION (§1) — **identity reconstructed exactly**

| item | value | verified |
|---|---|---|
| Frozen card | `ALPHA_CRS1_H4DIV_FADE_FROZEN.md` | ✓ |
| Rule fingerprint | `CRS1\|curlike&H4up\|SHORT\|SL=1.5ATR\|rr=2.0\|H=96\|STRESS0.24\|dedup16` | ✓ |
| Signature | `ALPHA_CURRENT_MARKET_SIGNATURE_V1.md`, fingerprint `c8f5a8091e22aec1` | ✓ |
| Population | `CURRENT_LIKE_POPULATION_V1` — 3,030 H4 bars = 12.6% of history | ✓ reproduced |
| Implementation | `sig_build.py`, `cur_screen.py`, `cur_cr13_trade.py`, `cur_cr13_verify.py` | ✓ read |
| Discovery lineage | CR-13 (survivor), CR-14 / CR-15 characterization, checkpoints #63–64 | ✓ |
| Data | `OANDA_XAUUSD_M15.csv`, sha256 **`57f4ed9544993c8f…`** — matches the spec claim | ✓ |
| Alpha mirrors | alpha1 / discovery / lab / trader — **all four MATCH** at `8f1ae27` | ✓ |
| Red Team | `RT-CRS1-CURRENT-REGIME-INDEPENDENT-VALIDATION-001.md` @ `57b2883` | ✓ |

Identity is fully reconstructible. **No fail-closed condition on §1.**

---

## 2 — THE TWO CAUSALITY DEFECTS

### 2a — SIGNATURE_V1 normalization (the issue the mandate raised) — **CONFIRMED**

Read directly from `sig_build.py`:

```python
mu = np.nanmean(X[ok],0); sd = np.nanstd(X[ok],0)      # full corpus 2011-2026
curmask = dt >= dt.max() - 90d ; centroid = median(Z[curmask])   # 2026-derived centroid
thr = np.nanpercentile(dist[ok & ~curmask], 12.0)      # full-history distance percentile
```

All three future-dependent components confirmed. One refinement Red Team's summary did not state: the
threshold is taken over **non-current** history (`~curmask`), which narrows but does not remove the issue.
The **descriptors themselves are genuinely backward-looking** (ATR, ATR-MA, 20-bar efficiency,
`rolling(120).max().shift(1)`, `shift(60)`) — the leak is in the normalization/centroid/threshold only.

**Important qualification in Alpha's favour:** this leak carries **no outcome information**. The signature
was frozen before any candidate P&L re-screen, uses no future return, MFE or MAE, and was not fished for
profitability. For *forward* deployment the frozen constants are perfectly causal.

### 2b — ★ Label temporal alignment (NOT previously identified) — **CONFIRMED, DECISIVE**

The two activation gates of the same strategy use **different temporal conventions**:

```python
# H4 trend gate  (cur_cr13_trade.h4_up_map) -- CAUSAL
merge_asof(m15.time, h4.close_time, direction="backward")     # last CLOSED H4 bar

# current-like gate (cur_screen.like_at)    -- NOT CAUSAL
h4 = (m15_time // 14400) * 14400                              # the bar's OWN, still-forming bucket
```

The parquet is keyed on H4 **bucket start** (every key divisible by 14400, verified), and the label for
bucket *B* is a function of *B*'s close. Measured:

```
  entry time minus its label-bucket start : min 0min · median 105min · max 225min
  trades gated on a bucket that had NOT closed at entry : 12,083 / 12,083 = 100.0%
  lookahead among those : median 135 min · max 240 min
```

**Why this leaks outcome information, mechanically:** the descriptors that decide "current-like" include
`vol_norm = atr/close`, `ddfh = (close − 120-bar-high)/close` and `ret60`. A four-hour window that closes
with a sharp *down* move simultaneously (i) looks more high-vol and more drawdown-y, i.e. more current-like,
and (ii) is a window in which an M15 **short** profits. The label is partly reading the very move the trade
is trying to capture.

**The data confirm exactly that signature:**

```
  trades in BOTH labels                : n=194  avgR +0.259
  trades ONLY under the leaky label    : n=104  avgR +0.808   <- added by the lookahead
  trades ONLY under the causal label   : n= 73  avgR -0.444
```

The lookahead does not merely shift the population — it **selectively admits the most profitable trades**
(+0.808R versus +0.259R) and excludes losers. That is the fingerprint of outcome-correlated leakage, not of
a neutral labelling difference.

### 2c — Answer to the mandate's A / B / C question

**Neither A nor B nor C.** The mandate framed the choice on the assumption that the mechanism is supported
and only the identity's causality is at issue. **That assumption does not survive**: once the alignment is
corrected the mechanism itself is not statistically supported (avgR +0.067, p = 0.243, best-10%-removed
−0.148, 7/14 years positive). There is therefore no supported mechanism to re-freeze under a new causal
identity. The correct outcome is **FAIL**, not `REQUIRES_NEW_CAUSAL_IDENTITY`.

---

## 3 — REPRODUCTION OF THE ORIGINAL EVIDENCE (§3) — **EXACT**

| claim | claimed | reproduced | |
|---|---|---|---|
| N | 298 | **298** | MATCH |
| avgR | +0.4507 | **+0.4507** | MATCH |
| PF | 1.87 | **1.8718** | MATCH |
| WR | 0.507 | **0.5067** | MATCH |
| DISC ≤2021 | +0.425 (n193) | **+0.4246 (n193)** | MATCH |
| CONF 22-24 | +0.367 (n35) | **+0.3671 (n35)** | MATCH |
| OOS 25-26 | +0.565 (n70) | **+0.5647 (n70)** | MATCH |
| best-10%-removed | +0.286 | +0.2794 | minor definitional difference in removal count |
| years positive | 13/14 (only 2011 −0.02) | **13/14, 2011 −0.021** | MATCH |
| H4-DOWN diagnostic | −0.075 | **−0.0746 (N=2538)** | MATCH |
| outside current-like | −0.123 | **−0.1229 (N=11785)** | MATCH |

Also reproduced: median R +0.797, maxDD −8.14R, max loss −1.181R, best-1%-removed +0.435.

**Alpha's arithmetic is exact.** Nothing in this report questions the computation; the defect is in what was
computed.

---

## 4 — CAUSAL-NORMALIZATION ANALYSIS (§4)

**Two constructions were preregistered in writing before any scoring, and only these two were scored. No
normalization fishing.**

**C1 — LABEL-ALIGNMENT-CAUSAL.** Frozen mu/sd/centroid/threshold kept **exactly**; only the temporal
alignment changed to `merge_asof`-backward on `close_time`. Isolates alignment from normalization.

```
  labels differ on 177 of 12,083 candidate entries
  N=267  avgR +0.0669  PF 1.10  WR 0.378  best-10%-rem -0.1483
  DISC +0.0198 (n169) · CONF +0.0304 (n32) · OOS +0.2053 (n66)
  delta vs frozen: -0.3838 R  (85% of the edge)
```

**C2 — CAUSAL-FREEZE-2021.** Entire signature rebuilt on ≤ 2021-12-31 only (mu/sd from that period,
centroid = median z of its last 90 days, threshold = 12th pct of its non-current distances), then scored
**only** on 2022-01-01 → 2026-07-27. Cutoff is the lab's own pre-existing DISC/CONF boundary, not chosen by
me.

```
  2021 centroid z = [-0.40, -0.22, +0.07, +0.55, +0.25]
  2026 centroid z = [+1.09, -0.06, -0.33, -1.06, -0.92]   (frozen)
  Jaccard(C2, frozen population) = 0.0003        N=558  avgR -0.2397  PF 0.69
```

**I decline to use C2 as evidence against the mechanism, and I say so explicitly.** A causally-available
centroid describes *late-2021 gold* (a low-vol consolidation near highs), not *2026 gold* (a high-vol
drawdown). Jaccard 0.0003 shows the two populations are essentially disjoint — C2 tests a **different
regime**, therefore a different strategy. Its negative result is uninformative about CRS-1's mechanism.

**What C2 does establish, structurally:** the frozen CRS-1 regime label **cannot be historically
reconstructed causally at all**. Any causally-available centroid describes a different regime, hence a
different identity. Historical validation of *this exact* activation label is impossible in principle — which
is why the decisive evidence had to be C1, where the constants are held fixed and only the defect is removed.

*(Red Team reports Jaccard 0.883–0.890 for its own causal variant; that is consistent with a construction
which retains the 2026 centroid and re-normalizes, i.e. much closer to C1 than to C2. I could not reproduce
Red Team's exact construction from its report and do not treat its 0.363 figure as verified.)*

---

## 5 — MULTIPLE TESTING / FDR (§5) — my principal independent responsibility

Family reconstructed from the lab's own ledgers (`ALPHA_MULTIPLE_TESTING_LEDGER.md`,
`ALPHA_DISCOVERY_CHECKPOINTS.md`, `ALPHA_CURRENT_REGIME_RESCREEN_LEDGER.md`). Failed hypotheses are
**included**, not dropped:

| stratum | count |
|---|---|
| named strategy families S1–S51 | 51 |
| prior program (42 hypotheses / 19 frontiers) | 42 |
| broad-discovery v2 batches A–J + later frontiers | 60 |
| state-path method (~50 state/transition definitions × 2 sides) | 100 |
| radar hypotheses R1–R32 | 32 |
| current-regime frontiers CR-1 … CR-15 | 15 |
| **total enumerated hypothesis-level tests** | **300** |

Significance uses a **one-sided episode-clustered** standard error (episodes = trade runs separated by more
than 4 H4 bars), because trades cluster inside H4-up episodes.

| label | N | clusters | avgR | clustered SE | z | **raw p** |
|---|---|---|---|---|---|---|
| frozen (non-causal) | 298 | 139 | +0.4507 | 0.0833 | +5.41 | **3.17 × 10⁻⁸** |
| **causal C1** | 267 | 134 | +0.0669 | 0.0960 | +0.70 | **0.243** |

| family definition | m | frozen: BH q | causal C1: BH q |
|---|---|---|---|
| CR-1 … CR-15 only | 15 | 4.75 × 10⁻⁷ **sig** | 1.00 **not sig** |
| current-regime + radar | 47 | 1.49 × 10⁻⁶ **sig** | 1.00 **not sig** |
| full enumerated program | 300 | 9.50 × 10⁻⁶ **sig** | 1.00 **not sig** |

**The frozen result survives multiplicity at every family definition — even m = 300. The causal result fails
at m = 1.** Multiplicity is therefore *not* the binding constraint on CRS-1, and I decline to reject it on
those grounds. **Causality is the binding constraint.** I record this deliberately: had the alignment been
correct, CRS-1 would have cleared the FDR gate convincingly.

---

## 6 — TEMPORAL ROBUSTNESS (§6)

| | frozen | causal C1 |
|---|---|---|
| years positive | **13 / 14** | **7 / 14** |
| leave-one-year-out worst | +0.4110 (drop 2025) | +0.0182 (drop 2025) |
| DISC ≤2021 | +0.4246 (n193) | +0.0198 (n169) |
| CONF 2022-24 | +0.3671 (n35) | +0.0304 (n32) |
| OOS 2025-26 | +0.5647 (n70) | +0.2053 (n66) |
| min partition | +0.3671 | +0.0198 |

Under C1, half the years are negative (2011 −0.407, 2013 −0.072, 2015 −0.359, 2016 −0.276, 2019 −0.122,
2021 −0.070, 2023 −0.470), and the whole result becomes dependent on 2025 and 2020. The CONF sample Red Team
flagged as thin is n=32 under C1 at +0.030 — indistinguishable from zero.

---

## 7 — TAIL ROBUSTNESS (§7) — the causal candidate **is** a tail strategy

| | frozen | **causal C1** |
|---|---|---|
| best-1%-removed | +0.4351 | +0.0451 |
| best-5%-removed | +0.3694 | **−0.0391** |
| best-10%-removed | +0.2794 | **−0.1483** |
| largest single winner, share of total | 1.5% | **11.1%** |
| top-5 share | 7.4% | **55.6%** |
| top-10 share | 14.8% | **111.1%** |
| largest winning year share | 2020: 28.6% | 2020: **75.4%** |
| removing largest winning year → avgR | +0.4119 | **+0.0215** |

The mandate states "CRS-1 must not be another crash-tail strategy". Under the frozen label it is not.
**Under causal alignment it is precisely that**: the top 10 of 267 trades account for more than the entire
net result, and one year supplies three-quarters of it.

---

## 8 — EFFECTIVE SAMPLE SIZE (§8) — the 214-episode claim is **overstated**

```
  frozen : N=298  unique days=126  distinct H4-up episodes (Alpha's own >64-M15-bar rule) = 94
           trades/episode 3.17 · lag-1 autocorrelation +0.058
  causal : N=267  unique days=118  episodes = 91 · trades/episode 2.93
```

Alpha and Red Team report "**298 trades over 214 distinct H4-up episodes**". Applying **Alpha's own
clustering rule to the 298 trades** gives **94** episodes. The 214 figure comes from
`cur_cr13_verify.py` lines 61–63, which count episodes in the **pre-filter candidate index set** — before
the `current-like` restriction — and not in the trades. **Effective N is ~94 independent clusters, not 214**
— a 2.3× overstatement of independent evidence. All p-values in §5 use the clustered SE and are unaffected.

---

## 9 / 10 — EXECUTION AND NEIGHBOUR ROBUSTNESS (§9, §10) — reported without selection

| variant | frozen N / avgR | causal N / avgR |
|---|---|---|
| dedup 8 | 591 / +0.3379 | 519 / +0.0135 |
| **dedup 16 (frozen)** | **298 / +0.4507** | **267 / +0.0669** |
| dedup 24 | 205 / +0.3371 | 173 / +0.0711 |
| dedup 32 | 152 / +0.4707 | 137 / +0.0693 |
| dedup 48 | 104 / +0.3562 | 88 / **−0.0061** |
| stop 1.0 / rr 3 | 298 / +0.3674 | 267 / **−0.0328** |
| stop 2.0 / rr 2 | 298 / +0.4728 | 267 / +0.2151 |
| stop 1.5 / rr 1 | 298 / +0.2455 | 267 / +0.0224 |

Execution semantics themselves are correct: `sb.simulate` uses next-M15-bar entry, stop-wins-same-bar-ties,
a single round-turn cost, and a hard 96-bar horizon; the H4→M15 trend alignment is causal. **The neighbour
grid is robust under the frozen label and is not under causal alignment** — two of eight variants go
negative and only one is materially positive. No neighbour was selected; the frozen identity remains the
only candidate assessed.

---

## 11 — MECHANISM SPECIFICITY (§11)

| arm | frozen label | causal C1 |
|---|---|---|
| **A** current-like & H4-**UP** → SHORT (CRS-1) | N=298, **+0.4507**, best10 +0.279 | N=267, **+0.0669**, best10 −0.148 |
| **B** current-like & H4-**DOWN** → SHORT | N=2538, −0.0746 | N=2559, −0.0680 |
| **C** outside current-like & H4-UP → SHORT | N=11785, −0.1229 | N=11816, −0.1128 |
| **A − B** | **+0.5253** | **+0.1349** |
| **A − C** | **+0.5737** | **+0.1797** |

The cross-scale-divergence claim rests on A being economically distinct from B and C. Under the frozen label
it clearly is. **Under causal alignment the spread collapses by ~75%**, and A itself is +0.067 with a
negative best-10%-removed — no longer economically distinct in any usable sense.

---

## 12 — S5 / PORTFOLIO INDEPENDENCE (§12)

CRS-1 is a **SHORT**; S5 is a **LONG** — directionally orthogonal. Entry times are broadly spread:
fraction in the S5 NY-open window (13–14 UTC) = **0.077** frozen / 0.067 causal; fraction 12–16 UTC = 0.215 /
0.176. **Structurally independent of S5.** Trade-level overlap and return correlation are **NOT COMPUTABLE**
— S5's ledger is sealed in `escrow_red_team/` and its validated population (2023-07 → 2025-10) barely
overlaps CRS-1's. Independence is not in question and is not the reason for this verdict.

---

## 13 — H1 CONFLUENCE / FREEZE PROTECTION (§13) — **PASS**

I verified mechanically that **no H1 condition entered the frozen candidate**: the activation is exactly
`current-like AND H4 ema20>ema50`, and no H1 series is read anywhere in `cur_cr13_trade.py` /
`cur_cr13_verify.py`. The CR-15 "H1-UP & H4-UP" subset was **not analysed, not scored and not promoted** in
this review. It remains post-selection information requiring a new identity.

---

## 14 — CURRENT-REGIME STATUS (§14)

I judged CRS-1 as a `CURRENT_REGIME_SPECIALIST`, not a universal strategy: its negative performance outside
the regime (−0.123) is treated as **supporting specialization**, not as a fault, and I did not require
out-of-regime profitability.

But the mandate's own condition is that the activation regime must be *"causal, reproducible, statistically
defensible, defined independently of candidate profitability."* It is reproducible and it was defined
independently of profitability (no P&L in the signature — creditable). **It is not causal as applied**: the
label is read from an unclosed bar for 100% of trades, and that non-causality is worth 85% of the measured
edge.

---

## 15 — LIMITATIONS

1. C1 changes the label's temporal alignment only. I did **not** search for any alignment that would improve
   CRS-1, and I scored exactly the two constructions I preregistered.
2. C2 is reported for completeness and explicitly **not** used as evidence against the mechanism (§4).
3. Red Team's specific causal variant could not be reproduced from its report; its +0.363 figure is
   **not verified** here, neither confirmed nor contradicted.
4. S5 trade-level overlap not computable (escrow).
5. **Nothing was modified, repaired, retuned or filtered.**

---

## 16 — VERDICT AND DISPOSITION

```
CRS1_STATISTICAL_VALIDATION_FAIL
```

**What is genuinely creditable, and should not be lost:** Alpha's arithmetic reproduces exactly on every
headline figure; the signature was frozen before any P&L re-screen and contains no outcome information; the
candidate was routed to independent validation rather than self-promoted; the H4-trend gate *is* causal; no
H1 confluence leaked into the freeze; and Alpha itself flagged the label as load-bearing and explicitly
asked Red Team to check it for leakage (`ALPHA_CRS1_H4DIV_FADE_FROZEN.md`, label-dependency section). That
request was correct — the leak is real, and it is in the alignment rather than the percentile.

**The decisive failure:** the `current-like` gate reads an H4 bar that has not yet closed, for **every**
trade, with a median 135-minute lookahead. The trades this admits average **+0.808R** against **+0.259R**
for trades both labels agree on. Removing the lookahead — and nothing else — takes avgR from **+0.451 to
+0.067**, best-10%-removed from **+0.279 to −0.148**, years-positive from **13/14 to 7/14**, and the raw
one-sided p from **3 × 10⁻⁸ to 0.243**. Multiplicity is not the binding constraint; causality is.

**Per §17, no repair was attempted.** Any corrected construction — including simply re-aligning the label —
is a **new candidate identity** owned by Alpha under a new mandate, and would have to re-enter discovery,
freeze and validation from the start. It should not inherit CRS-1's evidence.

**Not `CRS1_READY_FOR_CEO_DEMO_DECISION`.** Not integrated, Strategy Catalog untouched, not sent to AI
Trader, no DEMO orders. `CURRENT_REGIME_SURVIVOR` count returns to **0**.

**Recommended CEO actions (decisions are yours, not mine):**
1. Record `CRS-1 = STATISTICAL_VALIDATION_FAIL — NON_CAUSAL_ACTIVATION_LABEL_ALIGNMENT`.
2. Treat `cur_screen.like_at` as a **program-level defect**: every current-regime re-screen result that used
   it (the CR-1 … CR-15 series and the A/B/C bucket screen) inherits the same lookahead and should be
   re-derived before any of it is cited.
3. If the mechanism is still of interest, commission a **new** Alpha identity with a causally-aligned label
   from the outset — noting that under correct alignment the present evidence does **not** support it.

---

## 17 — ARTIFACTS

`statistician/crs1/` — `run1.py` (reproduction + both causality audits, with the preregistration block),
`run2.py` (materiality, mechanism, effective N, tail, neighbours), `run3.py` (FDR + temporal + S5), and the
JSON outputs.

**Environment:** Python 3.14 · data `OANDA_XAUUSD_M15.csv` sha256 `57f4ed9544993c8f…` (355,696 M15 / 23,990
H4 bars, 2011-07-26 → 2026-07-27) · Alpha `8f1ae27` (4 mirrors MATCH) · Red Team `57b2883` ·
signature fingerprint `c8f5a8091e22aec1` · cost STRESS round-turn 0.24 USD.

---

*Statistician division — independent statistical validation. Verdicts are scoped strictly to the evidence
examined and are not transferable to adjacent claims.*
