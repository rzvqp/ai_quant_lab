# V0 Operationalization Audit — Flow A (Statistician checklist, 2026-07-26)

**Why this exists.** Incoming unseen data (11yr M15 2011-2022, then 5yr M5) qualifies as a genuine unseen
set for the 40 V0 hypotheses *only if each hypothesis is operationalized BEFORE the data is touched*. A
narrative hypothesis "confirmed on unseen data" is not a confirmation — it is an operationalization chosen
after seeing the data. This audit checks, per the Statistician's exact 5-point checklist, whether each V0
already carries a pre-declared operationalization, **citing the line/parameter**. It does **NOT** fill any
gap in — a gap is marked, not completed (filling one in while auditing is the exact E015-V1 failure mode).

**Scope.** All 40 V0s except E010, E012, E015 (already verified directly in code by the Statistician). The
**24 UNSTUDIED are audited first** (they go to testing first); the 13 already-studied follow.

**Checklist (verbatim):** (1) explicit disclosed numeric detection/classification threshold; (2) fixed,
pre-declared outcome horizon (not "at some point"); (3) declared population/denominator — exact instance
rule; (4) declared reaction-classification threshold (continuation/reversal/stall), not subjective;
(5) no free parameter left to choose at confirmation time.

---

## PART 1 — 24 UNSTUDIED (priority). Verdict: ALL NARRATIVE — NOT OPERATIONALIZED.

No UNSTUDIED edge has an analysis script; the only artifact is its registry entry, which the registry
itself declares narrative by design ("written as a plain, literal statement ... not hedged or
pre-qualified, because the entire point ... is to discover the real conditions later, not assume them
now", registry l.54-58; "Measured outcome ... a definition to test against, not a pre-supposed result",
l.71-72). Consequently **criteria 1-5 are all MISSING for every UNSTUDIED edge.** Each row cites the
edge's own vaguest operative term as evidence; **each must be separately operationalized, in writing,
before the incoming data is touched.**

| Edge | Cited narrative anchor (registry line) | 1 thr | 2 horizon | 3 pop | 4 react | 5 free | Data on incoming M15+M5 XAUUSD? |
|---|---|---|---|---|---|---|---|
| E001 London Open Liquidity Hunt | "traded in a range … within a **defined** post-sweep window" (l.85-94) | ✗ | ✗ | ✗ | ✗ | ✗ | **Yes** (needs M5; no external data) |
| E002 Frankfurt Pre-Market Trap | "**Aggressive** price moves … reverse once London opens" (l.100-101) | ✗ | ✗ | ✗ | ✗ | ✗ | **Yes** (M5) |
| E003 NY Silver Fix Momentum | "momentum and correlation effects" (l.114-115) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs XAGUSD + verified Silver-Fix timestamp (l.116-117) |
| E004 US Open First FVG | "**statistically meaningful** predictive value … in a fixed post-open window" (l.129-136) | ✗ | ✗ | ✗ | ✗ | ✗ | **Yes** (M5; needs exact US-open ts) |
| E007 Central Bank Whisper | "Detectable algorithmic drift … in a **fixed** pre-release window" (l.176-183) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs economic calendar + M1/tick (l.177-178) |
| E013 Mitigation Block Sniping | "**precise** entry zone … Rate and magnitude of a directional reaction" (l.285-292) | ✗ | ✗ | ✗ | ✗ | ✗ | **Yes** (M5/M15) |
| E016 Propulsion Block Entry | "last opposing candle before a **strong impulsive** move … reliable continuation" (l.340-347) | ✗ | ✗ | ✗ | ✗ | ✗ | **Yes** (M5/M15) |
| E018 B-Book Stop Hunt | Registry itself flags it needs reformulation into an observable proxy "before this can even enter Discovery" (l.376-388) | ✗ | ✗ | ✗ | ✗ | ✗ | Partial (M5) **only after reformulation** |
| E019 Volume Climax Exhaustion | "A **volume spike** … signals exhaustion" (l.394) | ✗ | ✗ | ✗ | ✗ | ✗ | **Conditional** — needs verified volume (l.395-397) |
| E020 Delta Divergence | "cumulative volume **delta** (buy/sell pressure)" (l.409-412) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs bid/ask-side flow, absent (l.411-412) |
| E021 Iceberg Order Absorption | "**absorption** … visible as stalling despite volume" (l.422-425) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs tick/order-book (l.424-425) |
| E022 VWAP Touch And Go | "touching the session VWAP from a **trending** state" (l.436-437) | ✗ | ✗ | ✗ | ✗ | ✗ | **Conditional** — needs volume for VWAP (l.438) |
| E023 High Rel-Volume Breakout | "volume **significantly above** its recent average" (l.449) | ✗ | ✗ | ✗ | ✗ | ✗ | **Conditional** — needs volume (l.451) |
| E024 SP500/Gold Delta Shift | "a **shift** in their rolling correlation" (l.462-463) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs SPX (l.464-465) |
| E030 Tick Speed Acceleration | "**sudden acceleration** in tick/quote frequency" (l.576-577) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs tick data (l.578-579) |
| E031 3-SD VWAP | "**3rd standard-deviation band**" is a numeric anchor (l.589) but SD-window/session/reversion-horizon/threshold all absent (l.594-595) | ~partial | ✗ | ✗ | ✗ | ✗ | **Conditional** — needs volume for VWAP (l.591) |
| E033 DXY Lead | "**measurable** lag" (l.623-624) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs DXY (l.625-626) |
| E034 US10Y Lead | "**measurable** lag" (l.637-638) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs US10Y (l.639) |
| E035 Silver Leading Indicator | "Silver … **lead** gold moves" (l.650-651) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs XAGUSD (l.652) |
| E036 USDJPY Inversion | "inverse/lead relationship … during **specific regimes**" (l.663-664) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs USDJPY (l.665-666) |
| E037 NFP First Wave | "**frequently** a liquidity overshoot … within a fixed post-release window" (l.680-689) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs calendar + tick/M1 (l.682-683) |
| E038 CPI Initial Reversal | "**frequently** reverses within a **short** window" (l.695-704) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs calendar + tick/M1 (l.697-698) |
| E039 FOMC Slingshot | "reverses **sharply** … within a fixed post-statement window" (l.710-719) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs calendar + tick/M1 (l.712-713) |
| E040 Flash PMI Sentiment Flip | "**frequently** reversed once the full report is digested" (l.725-734) | ✗ | ✗ | ✗ | ✗ | ✗ | **No** — needs calendar + tick/M1 (l.727-728) |

**UNSTUDIED verdict:** 24 / 24 **NOT OPERATIONALIZED**. None may go to confirmation on the incoming data
until each is separately operationalized, in writing, before the data is touched. Of these, only
**E001, E002, E004, E013, E016** are even data-eligible for XAUUSD M15+M5 alone (E018 after reformulation;
E019/E022/E023/E031 conditional on volume); the remaining 13 need tick, intermarket, or calendar data that
is **not** part of the incoming acquisition and therefore cannot be tested on it regardless of wording.

---

## PART 2 — 13 already-studied (excl. E010/E012/E015). Verdict: OPERATIONALIZED (committed script).

Each has a frozen, committed Discovery script pinning a PRIMARY configuration (criteria 1-3, 5) and, for
the profile edges, the shared reaction-classification threshold `_profile.REACTION_THRESHOLD = 1.0×ATR`
(`_profile.py` l.13) with fixed horizons `_profile.HORIZONS = (1,3,5,10,20,50)` (l.11) (criterion 4).
Citations are to each edge's script.

| Edge | 1 detection threshold | 2 horizon | 3 population | 4 reaction | 5 free params |
|---|---|---|---|---|---|
| E005 | `MIN_COMPLETENESS_FRAC=0.75`, `PRE/POST_WINDOW_HOURS=2` (e005 l.48-50) | POST 2h + `P.HORIZONS` | session-boundary events (l.83) | 1.0×ATR (_profile) | pinned |
| E006 | `MIN_SESSION_COMPLETENESS_FRAC=0.875` (e006 l.66); breakout beyond Asia range | `FAILURE_HORIZON_HOURS=16` (l.65) | Asia-range breakouts | primary = binary return-inside-range (l.38) | pinned + disclosed variants |
| E008 | calendar rule: afternoon = `session∈{ny,late}`, UTC hr≥13 (e008 l.11) | afternoon window | Friday vs pooled Mon-Thu afternoons (l.31-32) | efficiency ratio + volatility, Mann-Whitney (l.16-22) | pinned (seed=42) |
| E009 | `PRIMARY_K=5` (e009 l.56) | `PRIMARY_HORIZON=480` (l.53) | CHoCH vs BOS swings | retest/continuation/failure rates (l.248) | pinned; `K_SWEEP`/`HORIZONS` disclosed |
| E011 | `FRACTAL_K_PRIMARY=3` (e011 l.65) | 50 bars = max `P.HORIZONS` (l.40) | failed-3rd-leg swing events | 1.0×ATR `movement_profile` (l.140) | pinned; k-variants disclosed |
| E014 | `NO_BREAKOUT_WINDOW_BARS=200`, `MAX_ATTEMPT_BUCKET=2` (e014 l.65-66) | `RESPONSE_HORIZON_BARS=50` (l.64) | inside-bar false-breakout attempts | fade = `-direction`, 1.0×ATR (l.152) | pinned |
| E017 | `K=5`, `PRIMARY_TOL=0.15` (e017 l.41-43) | `PRIMARY_HORIZON=480`, `REACTION_N=16` (l.45-46) | equal vs isolated swing pairs | reach + reaction magnitude (l.90) | pinned; `TOLS`/`HORIZONS` disclosed |
| E025 | `GRANS=[10,50,100]`, `COOLDOWN=8` (e025_clean l.21-23) | `NS=[4,16]` bars (l.22) | round-level approaches vs matched control | reaction rate at level | pinned |
| E026 | `THRESH=[0.3,0.5,0.7,0.9,1.1,1.3]` ADR fractions (e026_clean l.20) | remainder-of-session | %-ADR-consumed events | continuation-rate change | pinned |
| E027 | `DEPARTURE_THRESHOLD_ATR=0.25` (e027 l.54) | revisit + `P.HORIZONS` | midnight-open revisits vs random-matched | 1.0×ATR away-direction (l.109) | pinned |
| E028 | `K=5`; zone bins `[.382,.618,.79,1.0]` (e028_clean l.79-80) | leg-continuation | fractal-zigzag legs by retracement zone | `continued = cont_mag>0` (l.74) | pinned |
| E029 | gap definition; `HORIZON_BARS=480` (e029_clean l.18) | `HORIZON_BARS=480` (l.18) | Fri-close→Mon-open gaps | fill = binary touch (l.34) | pinned |
| E032 | equilibrium 50%; `STEP=16`, `NS=[16,64]` (e032_clean l.19-20) | move toward/away | above/below-equilibrium bars, 2 range defs | rate toward vs away | pinned |

**Two mandatory caveats on Part 2 (not to be dropped):**
1. **Operationalized ≠ valid.** These scripts satisfy the *existence* checklist, not correctness. The
   same was true of E010-D1/E012-D1 (circular) and E015-V1 (dependence) — all had committed
   operationalizations and still failed. A pre-registered operationalization is necessary, not
   sufficient.
2. **The five TERMINAL-HOLDOUT-BREACHED edges (E025/E026/E028/E029/E032) are burned for Set B ONLY**
   (RULE 2B-1, Set B = 2025-10→2026-07). The incoming 2011-2022 / M5 data is a *different, never-seen*
   set; the Set-B burn does not disqualify them from it. Their Set-A operationalization above is the
   pre-registered contract for that new-data test.

---

## Summary

| | Count |
|---|---|
| UNSTUDIED audited | 24 |
| — NOT OPERATIONALIZED | **24 / 24** |
| — data-eligible on incoming M15+M5 XAUUSD (after operationalization) | 5 clear (E001/E002/E004/E013/E016) + 5 conditional/reformulation |
| Studied audited (excl E010/E012/E015) | 13 |
| — OPERATIONALIZED (committed script) | **13 / 13** (operationalized ≠ validated) |
| Excluded (already code-verified by Statistician) | E010, E012, E015 |

**Bottom line for the data gate:** every one of the 24 UNSTUDIED must be operationalized in writing
before the incoming data is touched; nothing here has been operationalized in the process of auditing it.
