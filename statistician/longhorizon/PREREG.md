# MULTI_SESSION_LONG_HORIZON_ALPHA_SCOUT_V1 — PRE-REGISTRATION

Written and committed **before any hypothesis was scored**. Scout V2 ended with a self-disclosed budget
breach (60 declared, 80 scored). This time the budget is enforced programmatically: the scoring function
raises on hypothesis 61.

## Data

- Base series: `OANDA_XAUUSD_M15.csv`, sha256 `57f4ed9544993c8fbba28d9c1e3319f2…`, 355,696 bars,
  2011-07-26 → 2026-07-27. Native M15; **no M5 synthesis, no new acquisition**.
- **Holdout firewall respected:** all analysis truncated at the program constant
  `RESEARCH_HOLDOUT_CUTOFF_UTC = 2025-10-23T09:15:00Z` (`edge_research/_common.py:43`).
  17,792 bars after the cutoff are NOT consumed.
- Usable window: **2011-07-26 → 2025-10-23**, 337,904 bars, **14.2 years** (native M5 gives 5.0).
- 1 project pip = 0.10 USD.

## Independence rule (mandate §3) — declared first, as instructed

**Every anchor is at a single fixed clock time.** This is the core design decision: it makes time-of-day
identical between the conditional and baseline groups *by construction*, which is precisely the
composition confound that closed V2-4.

- Branches A, B, C, E, F: **one anchor per trading day at 22:00 UTC** (daily close).
- Branch D: **one anchor per trading day at 08:00 UTC** (start of the European phase), state measured on
  the preceding 00:00–08:00 window.
- Non-overlap enforced by anchor stride: horizons 6h/12h/24h use stride 1 day; **48h uses stride 2 days**.
- Anchors whose forward window spans a weekend/holiday are **dropped** (wall-clock span must be
  ≤ 1.25 × horizon), so a "next 24h" is always a real next 24h.
- **Primary N = INDEPENDENT_EPISODES** (anchors). Raw-bar N is reported secondarily only.
- Uncertainty: **calendar-month-clustered** standard errors on the conditional group.
- No phenomenon may qualify on raw-bar z.

## Splits

- **DEV** = anchors before 2019-01-01 (7.4 y). **OOS** = 2019-01-01 → 2025-10-23 (6.8 y).
- All 60 hypotheses scored on DEV only. Top 5 frozen **in writing** before OOS is inspected once.
- Era blocks for §17: 2011–2013, 2013–2016, 2016–2019, 2019–2021, 2021–2023, 2023–2025.
- `PRE_2021` = anchors < 2021-01-01; `POST_2021` = 2021-01-01 → 2025-10-23.
- Because DEV is entirely pre-2019, **a DEV discovery is by construction a pre-2021 discovery** — the
  opposite failure mode to native-M5 work.

## Search budget — 60 effective hypotheses, declared by branch

| branch | topic | budget |
|---|---|---|
| A | multi-hour trend persistence | **12** |
| B | multi-hour compression / expansion | **10** |
| C | path / inventory state | **12** |
| D | multi-session transitions | **8** |
| E | daily state transitions | **12** |
| F | tail / positive-skew states | **6** |
| | **TOTAL** | **60** |

One hypothesis = one (state, horizon, target) triple scored on DEV. Multiplicity assessed at **m = 60**
(Bonferroni two-sided α .05 → |z| > 3.02).

Positive controls (**3, declared separately, not part of the 60**) plus one SE-calibration run.

## Targets

`fwd_ret`, `|fwd_ret|`, sign-aligned `fwd_ret` (continuation), MFE, MAE, largest excursion,
`P(MFE ≥ X)` / `P(MAE ≥ X)` for X ∈ {100, 200, 300, 500} pips, time-to-first-±100p.
Horizons: **6h, 12h, 24h, 48h** only. No horizon grid search.

## Direction vs magnitude (mandate §12)

Every state is scored separately for DIRECTION (sign-aligned return) and MAGNITUDE (|return|, excursion,
expansion). A state that moves magnitude but not direction is `INFORMATION_ONLY` unless a second causal
event reveals direction. No direction will be manufactured.

## Excluded by mandate §22

L1, P2, V2-4, scheduled events, Family E, S5. Branch B does not reuse V2-4's M5 48-bar range/ATR
percentile: compression here is defined on **48h range ÷ 20-day ATR** and on **5-day ÷ 20-day realized
vol**, at daily anchors — different timeframe, different lookback, different anchor.
