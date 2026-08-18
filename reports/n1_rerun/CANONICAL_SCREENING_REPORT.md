# ALPHA CANONICAL SCREENING — N1/Router rerun of the 355 hypotheses

**Status:** `ALPHA_CANONICAL_SCREENING_COMPLETE_PENDING_REVIEW`
**Authorization:** RT-N1-0001 `N1_HANDOFF_PASS` (Red Team `5352570`) + RT-N1-0002 `N1_INCREMENTAL_PASS` (`6230ee5`).
**Date:** 2026-08-18. **No RATIFIED / PROMOTED / LIVE declared. Statistician + Red Team review required next.**

---

## 1. Install + ledger (Steps 1–3)
| item | value |
|---|---|
| artifact | `ve_n1_replay 0.1.0→0.1.1`, wheel SHA-256 `2cff7e7be1f9401c10753f751a1189a512f5be39946dfada4260b9c5e1cd29ab` (exact ✓), delivery `e118c33` |
| ve_brain | `0.1.3`, wheel `edd208ad…` (exact ✓), N1 contract `n1-additive-raw-axes-v1`, router `router-v1`, detector `61cbd58` |
| install | isolated venv `.alpha_n1_venv`; `ve_tower` NOT importable; hermetic vendored `_ai` (no live AI Trader import) |
| smoke parity | PASS (TREND_UP/DOWN/UNCERTAIN/BOS, live==replay, snapshot/restore, duplicate-idempotent, out-of-order rejected) |
| **ledger** | **355,696 bars in 1121.9 s (18.7 min, 3.15 ms/bar, O(n))**; `ledger_key=0ca1ad1f940ebab8`, `evaluation_identity_fingerprint=64414829e2ea080b`, `history_horizon=460` |
| ledger verify | **zero-lookahead = OK** (prefix stability @1k, 20k); **snapshot/restore unbounded-structure = OK** |
| regime bar counts (full history) | TREND_UP 181,795 · TREND_DOWN 173,442 · COMPRESSION 37,047 · **BREAKOUT_TRANSITION 0** · UNCERTAIN 459 |

**Key canonical fact:** the canonical N1 producer **never emits `BREAKOUT_TRANSITION`** on this instrument
(the RawAxesBuilder maps confirmed breaks to `structure ∈ {weak,strong}`, never `"range"`, which
BREAKOUT_TRANSITION requires). All breakout/bos hypotheses are therefore **canonically ineligible**.

## 2. Rerun identity (Step 5) — invariants held
- **m_total = 357 unchanged**; hypothesis count 355; 16 duplicate tombstones intact.
- `hypothesis_semantic_fingerprint` **preserved** (e.g. G0037 `88da9894aeb1`); a **new** `evaluation_run_hash`
  (e.g. G0037 `04bbc6511f98aa78`) binds: hsf, ve_n1_replay 0.1.1 + wheel SHA, ve_brain 0.1.3 + wheel SHA, N1
  contract, router version, detector submodule commit, ledger key + snapshot schema + history horizon,
  data identity, evaluator (`mstrat.simulate@wp5b_reconciled TICK=0.01 RT-CODE-A-0007`), eligibility contract,
  regime-episode definition, exit policy, and the full cost-model identity.
- Old results marked **`SUPERSEDED_NONCANONICAL_N1`** (preserved, never deleted or silently compared).

## 3. Methodology (Steps 4, 7)
- **Canonical eligibility:** a signal counts only where the hypothesis regime ∈ `applicable_regimes` (N1
  ledger) at the signal bar. Entry triggers unchanged (pullback/momentum/continuation/bos/comp_break);
  **only the regime gate became canonical**, isolating the regime effect.
- **Episode-primary** (regime episode = unit): RECENT_PRIMARY (2022-12→2025-10) is the estimand;
  HISTORICAL_REGIME_TRANSFER (2011→2021, same regime) secondary; COMBINED diagnostic only. NOT_APPLICABLE for
  no-regime periods. `position_at_regime_end = HOLD_UNTIL_STRATEGY_EXIT`.
- **Official cost (Step 6):** `AI_TRADER_SHADOW_COST_MODEL_v1`, calibration **RATIFIED**, config-fp
  `b7bb9a9aed17a1c8`, content_hash `1341f228…`, SE **UNAVAILABLE**, IQR 0.04, provenance = 4-day set, 175 obs.
  Applied via the reconciled evaluator (`TICK=0.01`): BASE round-trip **0.05**, STRESS **0.24**, mapped as
  `slip_ticks=round_trip/(2·TICK)`, `spread_ticks=0`, so the executable-stop floor `max(0.05,0.10·atr)` is
  **identical** across gross/BASE/STRESS (only the cost term changes). GROSS/NET_BASE/NET_STRESS all reported.
- **MDE:** `(z_.05 + z_.80)·sd(net_R_BASE)/√n` per hypothesis. COST_BASE_FALSIFIED requires RATIFIED ∧
  `estimate_BASE ≤ 0` ∧ `|estimate_BASE| ≥ MDE`; `|estimate_BASE| < MDE ⇒ ARCHIVE_INSUFFICIENT`.
- **Data (Step 8):** official loader, pre-holdout only (197,094 bars, 2011-07→2025-10-12). **SEALED 2025-11+
  never loaded; OOS access count = 0.**

## 4. NET verdict distribution (355)
| count | verdict |
|---|---|
| 133 | ARCHIVE_INSUFFICIENT (incl. low-power `|EV|<MDE`) |
| 119 | NET_STRUCTURALLY_NEGATIVE_GROSS (gross EV ≤ 0 canonically — not a cost effect) |
| 41 | RECENT_REGIME_NET_PROVISIONAL (net BASE > 0, historical transfer weak) |
| **31** | **CANONICAL_PROVISIONAL_SURVIVOR** (net BASE > 0 robust + historical same-regime transfer > 0) |
| 17 | NET_FAT_TAIL_DEPENDENT |
| 14 | RERUN_BLOCKED_UNRESOLVED_SPEC (compact records not exactly reconstructable — reported, not guessed) |

**Eliminations:** survive BASE = **72**; of those, **6 die under STRESS**. COST_BASE_FALSIFIED are absorbed
into ARCHIVE_INSUFFICIENT/NET_STRUCTURALLY_NEGATIVE per the ladder above. No RATIFIED/PROMOTED/LIVE.

## 5. Shortlist — canonical distinct mechanisms (≤5, ≥2 surviving variants)
Under canonical N1 eligibility **only 3 economically-distinct mechanisms survive, all TREND_UP long**:

| # | mechanism | rep | NET BASE EV | NET STRESS EV | trimmed BASE | surv/variants | walk-forward | maxDD (R) | hist transfer |
|---|---|---|---|---|---|---|---|---|---|
| 1 | TREND_UP \| pullback | CAND-G0037 | **+0.271** | **+0.238** | +0.192 | 34/57 | [0.162, 0.481, 0.161] all+ | −17.9 | +0.017 |
| 2 | TREND_UP \| continuation | CAND-G0184 | +0.129 | +0.094 | +0.099 | 22/35 | [0.061, 0.126, 0.196] all+ | −31.8 | +0.000 |
| 3 | TREND_UP \| momentum | CAND-G0059 | +0.116 | +0.078 | +0.086 | 16/35 | [−0.019, 0.162, 0.204] | −35.4 | −0.022 |

- **TREND_DOWN, COMPRESSION, BREAKOUT** produce **no** robust (≥2-survivor, net-positive, non-fat-tail)
  cluster canonically — a real tightening vs the noncanonical 4-mechanism shortlist.
- **G0037 remains the lead** and is the strongest edge: recent NET BASE +0.271 (STRESS +0.238) on n=643 trades,
  1,638 episodes / 667 with trades, best-episode-share 0.069, **MDE 0.174 ≪ EV 0.271**, walk-forward all positive.

## 6. Differences vs the old gross/noncanonical results
- Old gross survivors (AWAITING_COST) = **62** → **44 still canonical survivors, 18 lost**.
- Canonical regime **falsified** many old gross survivors and **also promoted** some old
  GROSS_STRUCTURALLY_FALSIFIED (24 → survivor/provisional) because the canonical regime changed their
  eligibility. Full crosstab in `CANONICAL_RERUN_SUMMARY.json`. Notable rows:
  - `GROSS_STRUCTURALLY_FALSIFIED → NET_STRUCTURALLY_NEGATIVE_GROSS`: 117
  - `GROSS_STRUCTURALLY_FALSIFIED → ARCHIVE_INSUFFICIENT`: 113
  - `GROSS_EPISODE_SURVIVOR_AWAITING_COST → CANONICAL_PROVISIONAL_SURVIVOR`: 14
  - `RECENT_GROSS_SIGNAL_AWAITING_COST → RECENT_REGIME_NET_PROVISIONAL`: 16

## 7. Next
Statistician verifies the results; Red Team verifies the pipeline + integrity; only then may accepted
strategies feed LIVE_SHADOW. Alpha did **not** provide probability_inputs to AI Trader, did **not** touch the
broker gate or LIVE_SHADOW, and declares nothing profitable or validated. Artifacts:
`CANONICAL_RERUN_RECORDS.json` (per-hypothesis), `CANONICAL_RERUN_SUMMARY.json`, `N1_LEDGER_META.json`,
`canonical_rerun.py`, `build_n1_ledger.py`, `postprocess.py`.
