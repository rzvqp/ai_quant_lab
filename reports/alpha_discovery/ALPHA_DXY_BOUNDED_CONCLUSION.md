# ALPHA_DXY_BOUNDED_CONCLUSION — CEO DECISION REQUESTED

**Mandate:** `ALPHA-XAUUSD-DXY-CAUSAL-INCREMENTAL-INFORMATION-001` (Decision A). Scope = whether causal DXY adds **material AND stable** incremental information about future XAUUSD path, above XAUUSD price-only state. §20 budget **complete**: aligner → univariate map → transitions → interactions → incremental test. Ratified ICE DXY H1 only; causal timestamp contract enforced; DXY-only (no yields/macro/proxy); price-only parent baseline; L/S separate; DISC/CONF; cross-era b0/b1/y2123; event-deduped; predeclared features/lags (no mining). Frozen objects untouched.

## What was tested (checkpoints #35–#38)
| stage | result |
|---|---|
| Foundation (#35) | causal aligner built + coverage verified == ratified report (97.4/97.8/99.9%); **past DXY return ~0 corr with XAUUSD forward return → the DXY↔gold inverse is CONTEMPORANEOUS, not predictive** |
| Stage A univariate (#36) | DXY impulse/accel/efficiency → XAUUSD path lifts small (≤0.04); persistent-DXY-direction inverse signal holds in b0/b1 but **REVERSES in 2021-2023**; lag curve decays from lag0 |
| X3 divergence (#37) | gold-not-reacting divergence flips sign b0 vs b1 → not stable |
| §7 incremental (#37, CRITICAL) | persistent DXY direction adds a **small POSITIVE increment over the XAUUSD parent regime in b0/b1 (+0.02..+0.06 → NON-redundant)** but **INVERTS in 2021-2023** |
| Transitions (#38) | USD impulse-exhaustion / reversal → no cross-era-stable XAUUSD path lift |

## Central finding
**DXY carries genuine, non-redundant incremental information about the XAUUSD path in the 2011-2018 eras** — it is *not* merely re-encoding XAUUSD trend/volatility (the §7 test confirms a real increment over the price-only parent state). **But that information is REGIME-CONDITIONAL and INVERTS in the 2021-2023 inflation/safe-haven regime** (the classic inverse DXY↔gold relationship flipped as gold and the dollar rose together on Fed hiking + risk-off demand). Univariate states, X3 divergence, and transitions all confirm: no DXY signal is cross-era-stable in sign.

**Therefore DXY does NOT provide MATERIAL + STABLE cross-era incremental information (§1/§15).** As a *stable, tradeable* edge: `DXY_INCREMENTAL_INFORMATION_NOT_SUPPORTED`. (This is NOT "DXY is uninformative" — it carries real contemporaneous and real historical incremental information; it is simply **non-stationary**, and the recent regime carries the *inverted* sign, so it cannot anchor a robust cross-era new strategy.)

## Why (mechanism, not curve-fit)
The DXY↔gold relationship is a *derived* correlation, not a primitive driver. Both instruments respond to a deeper variable — **real yields / monetary regime**. In the disinflation/ZIRP eras (2011-2018) the reduced-form inverse held; in the 2021-2023 inflation shock, gold's inflation-hedge/safe-haven demand and the dollar's rate-driven strength moved *together*, flipping the reduced-form sign. DXY alone cannot be cross-era-stable because it is one endogenous output of the regime, not the regime itself. **This is the exogenous-axis confirmation of the program-wide result: on XAUUSD, cross-era-stable directional expectancy is not available from any single endogenous feature (price-only OR DXY); the stable structure lives in the underlying macro-regime variable.**

## CEO DECISION REQUESTED (A / B / C / D)
- **A (recommended, paired with C) — Accept `DXY_INCREMENTAL_INFORMATION_NOT_SUPPORTED` as a stable edge** and close the DXY-alone frontier honestly.
- **C (recommended next axis) — Authorize the REAL-YIELDS / rates axis** (the mandate deferred it: "NO_YIELDS_YET … until we determine whether DXY itself contains incremental information" — now determined: DXY alone is regime-conditional, not stable). The 2021-2023 inversion is *precisely* a real-yield/inflation regime signature; real yields are the candidate stable driver that DXY only reflects. Same information-first, incremental, cross-era discipline; new Data Acquisition ratification required.
- **B — Regime-gated DXY:** deploy DXY info only inside a detected regime. Rejected as primary: regime detection is the unsolved problem, and the *recent* regime carries the inverted sign — high risk, no stable gate exists yet.
- **D — Return to price-only M15-trigger-under-HTF-edge** (the earlier Decision-C option) — execution-layer work on the proven frozen edges, deferring exogenous research.

**Recommendation: A + C.** DXY is now honestly characterized as real-but-non-stationary; the mechanism points to real yields as the deeper stable variable, and the mandate's own deferral condition for yields is satisfied. If real yields are not to be pursued, D (use M15 as a trigger under the frozen HTF edge) is the fallback. Awaiting CEO direction before committing the next axis.
