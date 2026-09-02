# RED TEAM — S14 RESCUE INDEPENDENT RETEST V1 · STRATEGY #2 CANDIDATE FALSIFICATION
### RT-S14-RESCUE-INDEPENDENT-RETEST-V1 · Auditor: Red Team · 2026-09-02

Independent falsification of Alpha Discovery's frozen top-ranked ATTRIBUTION_V2 rescue hypothesis (S14
mean-reversion conditional rescue at the previous-session-extreme condition). Bind → freeze → reproduce →
find untouched data → retest. NO optimization. The frozen spec was bound verbatim from the V2 artifacts and
reproduced exactly; the retest cannot run because **no genuinely untouched data exists** — the entire
governed record was consumed by discovery and attribution and the last research holdout was permanently
exposed.

---

## 0 — VERDICT

```
S14_RESCUE_INDEPENDENT_RETEST_V1_COMPLETE = YES
S14_RESCUE_SPEC_HASH = 7a4ef8036b77eeaea5cc829daf168aba2540d5102372dec37e69593f19984f2d

DISCOVERY_RESULT_REPRODUCED   = YES (exact, independently re-derived from the committed trade ledger)
DISCOVERY_SUBSET_N            = 65 (over 56 distinct UTC days)
DISCOVERY_SUBSET_EXPECTANCY   = +0.492592 R
DISCOVERY_REMAINDER_EXPECTANCY= -0.188098 R

UNTOUCHED_TEST_DATA_AVAILABLE = NO
UNTOUCHED_TEST_RANGE          = NONE (no genuinely untouched chronological period exists in the governed repo)

TEST_RESCUE_N / EXPECTANCY / PF / WR   = N/A — DATA_BLOCKED
TEST_REMAINDER_EXPECTANCY / LIFT       = N/A — DATA_BLOCKED
BASE_RESULT / STRESS_RESULT            = N/A — DATA_BLOCKED
CONCENTRATION_STATUS (discovery)       = drop-best-5% +0.394 > 0 (not tail-carried) BUT episode-clustered
STABILITY_STATUS (discovery)           = chrono thirds 2/3 positive (middle third negative)

S14_RESCUE_RETEST_STATUS = DATA_BLOCKED
VERDICT                  = S14_RESCUE_DATA_BLOCKED
READY_FOR_STRATEGY2_PROMOTION_REVIEW = NO
NEXT_AUTHORIZED_ACTION   = NONE — CEO DECISION REQUIRED
```

## 1 — IDENTITY FREEZE (§1, §2) — bound verbatim, hashed

The exact frozen hypothesis is object **`S14::25e44853ad0f`** (SHORT representative of family S14, mechanism
`M08_EXTENSION_MEAN_REVERSION`, variant spec `{"exit":"rr2","roc_k":0.004,"side":"down","stop":"atr"}`), with
rescue condition **blinded `f028` = `dist_prev_sess_high_atr` == bin `0.0`** (price at/through the
previous-session high, ATR-normalized nearest bin of 5). The full specification — identity, the original
`mstrat.py` strategy rule (3-bar-ROC exhaustion SHORT, next-open entry, 1.5·ATR stop, RR2 target, 48-bar
timeout, BASE 0.40 round-trip cost), the exact bin, and all discovery statistics — is frozen in
`red_team/policy_reviews/S14_RESCUE_FROZEN_SPEC_V1.md`. **S14_RESCUE_SPEC_HASH =
`7a4ef8036b77eeaea5cc829daf168aba2540d5102372dec37e69593f19984f2d`** (sha256 of that file). No threshold
moved, no neighboring bin, no session adjustment, no retuning. All fields verified at source in the frozen V2
artifacts (`ATTRIBUTION_V2_PER_FAMILY_AUTOPSY.csv`, `ATTRIBUTION_V2_FULL_FAMILY_MATRIX.csv`,
`ATTRIBUTION_V2_FINAL83_BLIND_RESULTS.csv`, `attribution_v2/EXECUTION_UNIVERSE` + `REPRESENTATIVE_VARIANT_MAP`).

## 2 — REPRODUCE THE ORIGINAL FINDING (§3) — reproduced exactly (replication, not validation)

Independently re-derived from the committed exposed-history ledger `ATTRIBUTION_V2_TRADE_FEATURES.parquet`
(505,794 trades; the S14 object's own 1,239 trades, 2011-08-02 → 2026-07-26), recomputing the subset from
scratch:

```
ORIGINAL_FULL_POPULATION_N = 1239   ORIGINAL_FULL_EXPECTANCY = -0.152388 R   (exact)
RESCUE_SUBSET_N = 65   RESCUE_SUBSET_EXPECTANCY = +0.492592 R                 (exact)
REMAINDER_N = 1174     REMAINDER_EXPECTANCY = -0.188098 R                     (exact)
EXPECTANCY_LIFT = +0.680691 R                                                (exact)
FDR_STATUS = fdr_sig True (BH-FDR q=0.05 @ m=5175; omni_p 0.000511 < bh_thresh 0.002357)
CHRONOLOGICAL_STABILITY = thirds [+0.9032, -0.0695, +0.6513] -> 2/3 positive (PROFITABLE_RESCUE gate met)
CONCENTRATION_STATUS = drop-best-5% (drop 4/65) = +0.3941 > 0 (gate met); drop-best-1 = +0.4691;
                       top-1% share of gross winners = 3.2%; WR 0.538; median R +0.4331; PF 2.083
```

The discovery result reproduces to the digit. **DISCOVERY_RESULT_REPRODUCED = YES.** (Replication of the
reported finding on exposed history — it does not confer validity, per the mandate.)

**Diagnostic disclosure (does not rescue anything).** The subset, while passing the V2 gates, is **thin and
episode-concentrated**: 65 trades over ~15 years (~4.3/yr), clustered in 2011 (12), 2020 (12), 2025 (9),
2026 (20) = 53/65 (82%) in four years, with **zero** in 2014, 2016–2018, 2022–2023, and a **negative middle
chronological third**. Its per-cell placebo false-positive load is ~13% and it was selected on
MATERIALLY_EXPOSED history. So even before the data question, this is a fragile, sparse, explicitly
hypothesis-only candidate.

## 3 — TRULY UNTOUCHED DATA (§4) — none exists

```
DISCOVERY_DATA_END            = 2026-07-27 16:15 UTC (the entire governed XAU M15 record end)
S14 ledger last decision      = 2026-07-26 22:15 UTC
UNTOUCHED_TEST_DATA_AVAILABLE = NO
UNTOUCHED_TEST_START / END    = NONE
```

Established from the frozen artifacts and the governed data directly (not inferred):
- **The attribution consumed the entire governed record.** `STRATEGY_ATTRIBUTION_V2_PROTOCOL_FREEZE.md`:
  `ATTRIBUTION_DISCOVERY_RANGE = 2011-07-26 .. 2026-07-27 (the entire governed XAU M15 record)`;
  `HISTORICAL_REUSE_STATUS = MATERIALLY_EXPOSED — no clean OOS exists; V2 output is HYPOTHESIS_GENERATION
  ONLY`.
- **The last research holdout is permanently burned.** The protocol freeze states `RESEARCH_HOLDOUT_CUTOFF_UTC
  = 2025-10-23 has been consumed`, and `ALPHA_CURRENT_DATA_REBASE_AUDIT.md` records that the authorized
  CURRENT_DATA_REBASE **exposed everything after 2024-06-20 through 2026-07-27, including "any 2025-10-23+
  holdout that overlapped"**, which "permanently lose untouched-validation status and must NEVER later be
  represented as independent OOS." The audit's own designation: "forward MT5 DEMO becomes the true untouched
  confirmation."
- **The data simply ends.** Governed XAUUSD M15 (canonical sha `57f4ed95`) runs 2011-07-26 16:30 → 2026-07-27
  16:15 UTC (355,696 bars); native M5 ends 2026-07-27 17:55 UTC — both fully inside the exposed range. There
  is no chronological period after the discovery end, and no reserved-and-untouched slice within it.

Relabeling any exposed slice as OOS is explicitly forbidden (§4) and would violate the lab's own frozen
governance. **No genuinely untouched data exists.**

## 4 — DATA_BLOCKED (§5) — retest not run; minimum prospective dataset specified

Per §5 I do **not** recycle exposed history and do **not** manufacture a holdout. `S14_RESCUE_RETEST_STATUS =
DATA_BLOCKED`. Sections 6–13 (the actual retest, metrics, cost stress, diagnostics, top-tail) are **not
executed** — there is no untouched data to run them on, and no post-hoc rescue is permitted (§10).

**Minimum prospective dataset required to test S14_RESCUE_FROZEN_SPEC_V1:**
```
TIMEFRAME        = XAUUSD M15-native (S14 decision + entry are M15; dist_prev_sess_high_atr is a session
                   aggregate derived from the same M15 stream)
REQUIRED_COLUMNS = UTC epoch timestamp, open, high, low, close, tick_volume (M15 bars; enough to compute
                   3-bar ROC, ATR, next-open entry, 1.5*ATR stop, RR2 target, 48-bar timeout, AND the
                   previous-session high -> dist_prev_sess_high_atr bin-0 condition)
MINIMUM_CHRONOLOGY = strictly AFTER 2026-07-27 16:15 UTC, collected prospectively and NEVER used by any
                   discovery / variant selection / V2 attribution / condition selection / parameter tuning
                   (e.g. forward MT5 DEMO or a fresh vendor pull post-cutoff, exactly as the rebase audit
                   itself designates the true untouched confirmation)
TARGET_TRADES    = >= 50-100 INDEPENDENT rescue-condition (f028 bin-0) trades for a day-clustered,
                   dependence-aware expectancy test with a usable 95% interval, PLUS enough full-S14 trades
                   (family fires ~83/yr) for the remainder/lift baseline
COST_REQUIREMENTS = lab frozen conventions, BOTH: BASE = 0.40 price round-trip (spread 1 + slip 1 tick,
                   TICK 0.1, as used in discovery) AND STRESS = x3 spread+slip (alpha_lab.red_team()); no
                   favorable fills, no discovery-era cost simplifications weaker than the current standard
```

**★ Feasibility caveat (decision-relevant).** The frozen rescue condition is extremely rare — 65 bin-0
trades in ~15 years (~4.3/yr). At that historical rate, accumulating the minimum 50–100 independent
rescue-condition trades needs **~12–23 years** of forward data. So a prospective test of THIS frozen
condition is not merely data-blocked today; it is effectively **infeasible on any near-term horizon** without
either a far longer forward window or a broader condition — and broadening the condition would void the
frozen spec (a NEW hypothesis, forbidden here). This rarity is itself the strongest practical argument
against treating S14 as a near-term Strategy #2 candidate.

## 5 — FALSIFICATION VERDICT (§13, §14)

`VERDICT = S14_RESCUE_DATA_BLOCKED`. A PASS requires genuinely untouched data with positive net expectancy on
an economically meaningful sample; none of that is reachable. This is neither a PASS nor a FAIL of the
economics — it is a data-availability block: the candidate cannot be independently falsified or confirmed
because the discovery process already consumed every governed observation. `READY_FOR_STRATEGY2_PROMOTION_
REVIEW = NO`. No promotion, no StrategyCatalog change, no live/demo execution, no optimization (§14, §15).

## 6 — PROTECTIONS (§15) — intact

Read-only audit. Did not modify S5, AI Trader, P007, MGMT-004, MT5, or StrategyCatalog; did not touch the
Statistician's active P007 prospective-discriminator work; did not open the offline BLIND_KEY / secret
feature map (the unblinded name `dist_prev_sess_high_atr` was read only from in-repo materialized artifacts).
No exposed history was relabeled as OOS; no holdout was manufactured; the frozen S14 condition was not
altered. All changes are confined to `red_team/` (the frozen spec + this report + LEDGER).

## 7 — CONCLUSION

Alpha's frozen top rescue hypothesis (S14 SHORT mean-reversion at the previous-session-high bin,
`f028==0`) was bound verbatim and hashed, and its discovery result reproduces exactly on the exposed
ledger (subset +0.492592R / N65 vs remainder −0.188098R, FDR-significant, 2/3 chronological thirds,
concentration-robust). But it cannot be independently retested: the V2 attribution and S14 discovery
consumed the entire governed XAUUSD record (2011-07-26 → 2026-07-27), the last research holdout (2025-10-23+)
was permanently exposed by the authorized data rebase, and the lab's own frozen protocol already declares the
history MATERIALLY_EXPOSED / HYPOTHESIS_GENERATION_ONLY with no clean OOS. Relabeling exposed data as OOS or
fabricating a holdout is forbidden, so the retest is **DATA_BLOCKED**. The only valid path is genuinely
prospective post-2026-07-27 data (per the spec in §4) — and given the ~4.3 rescue-trades/year rate, even a
minimum-sample prospective test would take well over a decade. The candidate remains a fragile,
episode-concentrated, hypothesis-only sliver; it is **not** ready for Strategy #2 promotion review.

```
VERDICT = S14_RESCUE_DATA_BLOCKED
READY_FOR_STRATEGY2_PROMOTION_REVIEW = NO
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED
```

Frozen spec bound + hashed; discovery result reproduced exactly; no untouched data exists; no post-hoc
rescue; protections intact. Control returned to CEO.

---

*Red Team · S14 rescue independent retest · spec hash 7a4ef803 · discovery reproduced exact (65 / +0.492592R
vs −0.188098R, FDR True, 2/3 thirds, drop-5% +0.394) · governed record consumed 2011→2026-07-27, holdout
2025-10-23+ permanently exposed, MATERIALLY_EXPOSED · DATA_BLOCKED · rescue rate ~4.3/yr => prospective test
~12-23 yrs · no promotion · LEDGER E112 (prev E111).*
