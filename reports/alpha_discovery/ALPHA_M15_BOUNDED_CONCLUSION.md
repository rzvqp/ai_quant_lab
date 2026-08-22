# ALPHA_M15_BOUNDED_CONCLUSION — CEO DECISION REQUESTED

**Mandate:** `ALPHA-XAUUSD-M15-CAUSAL-STATE-PATH-DISCOVERY-001`. Scope = the whole causal, price-only M15 state->path map. Method = information-first; first-passage P(+X before -Y); LONG/SHORT separate; event-deduped (2h cooldown); cross-era gate on three distinct eras (DEV 2021-2023 gated M15, b0 2011-2013, b1 2016-2018); STRESS cost (2.4 pips RT); no P&L-defined regimes; no threshold mining; no tight-stop forcing (§19). All frozen objects (S5, COMP-CONT-L-rr2, H4-bo-raw-S) untouched; DXY paused.

## Families systematically completed (§27)
1. **Unconditional baselines** (`state_path_m15.py`) — M15 path odds L/S near-symmetric; natural MFE/MAE ~31-52p; base rates era-dependent.
2. **Univariate states** (`state_m15_discover.py`, 16 states) — only volatility states are cross-era-stable; directional/displacement/pullback/position/path-cleanliness/body states are regime/era-transient or immaterial.
3. **Transitions** (`state_m15_transitions.py`, 10 causal A(t-8)->B(t)) — NO positive tradeable transition; only cross-stable = highvol->stabilization -> LONG-avoidance filter.
4. **Session-conditioned** (`state_m15_session.py`, §13) — session context adds cross-era-stable STRUCTURE (London/NY-open bilateral range-expansion; Off dead-zone avoidance filter) and ONE directional cross-era-stable candidate: NY-session high-vol -> SHORT.
5. **Decisive tradeability** of that candidate (`state_m15_ny_hvshort.py`) — NOT tradeable (below).

## Central finding
On causal price-only XAUUSD M15, **the ONLY cross-era-stable INFORMATION is volatility-structured**:
- high/rising vol -> a modest M15 SHORT (down) skew — cross-era-stable, and it survives the b1 gate ONLY when SESSION-conditioned (NY);
- London / NY-open -> bilateral range-expansion (both +/-70 targets reached more) = volatility-TIMING, not direction;
- Off (21-24 UTC) and high-vol->stabilization -> stable AVOIDANCE filters (targets under-reached).

**None of it converts to tradeable, net-positive, standalone directional alpha** under any honest geometry, after STRESS cost, event-deduped, cross-era:
| lead | result |
|---|---|
| univariate high-vol-short | not tradeable (no net-positive geometry) |
| DOWN-parent high-vol-short | regime-specific; **fails b1** (genuine-downtrend-era only) |
| **NY-session high-vol-short** (strongest; first INFO to survive b1) | **every geometry net-NEGATIVE on DEV+b0+b1** (best DEV avgR -0.034, losing 2022; b0 -0.021; b1 -0.088; best10 -0.15..-0.38 everywhere = carried by outliers) |
| transitions | only a stable avoidance filter |

## Interpretation (mechanism, not curve-fit)
The M15 volatility->direction relationship is **real information but too small** (P-lift ~+0.05-0.07) relative to (a) XAUUSD's adverse-first M15 path (price whipsaws through a sane stop before reaching the target) and (b) STRESS transaction cost. The robust, tradeable *directional* edges in this program live at HIGHER timeframes with an HTF state trigger — frozen **S5** and **COMP-CONT-L-rr2** (H4 QUIET->UP). M15 in isolation carries timing/volatility information but not exploitable standalone directional expectancy. This is consistent, not contradictory: it says **M15's proper role is a causal TRIGGER/timing layer under an HTF edge**, exactly the CEO economic-profile directive (HTF edge + M5/M15 causal-trigger entry), NOT a standalone directional decision timeframe.

## Program-wide consistency
Reinforces the standing finding: price-only XAUUSD alpha is **regime/era-conditional**; robust edges are HTF-state-specific and already frozen. Every SHORT-side lead across H1 and M15 fails cross-era or fails to convert. The M15 map adds precision: the *only* cross-era-stable M15 information is volatility, and it is a timing/filter signal, not standalone alpha.

## CEO DECISION REQUESTED
The M15 **standalone directional** frontier is bounded/exhausted (all families completed, no tradeable cross-era-stable non-redundant standalone M15 edge). Options:

- **A (recommended) — Pivot M15 to its evidenced role: causal TRIGGER under a frozen HTF edge.** Test whether NY-session high-vol / M15 volatility-timing / M15 compression-release improves the ENTRY (fill, adverse excursion, expectancy) of the frozen HTF LONG edge (COMP-CONT-L-rr2 / S5) — i.e., HTF edge + M15 causal trigger, the economic-profile A/B target. Uses the M15 information where the evidence says it has value.
- **B — Extend the M15 map to an untried axis** (multi-bar path-SHAPE/sequence features, or M15 explicitly conditioned on H4 causal state = a subset of A).
- **C — Accept the bounded M15 negative** and return the loop to the HTF/trigger-integration track directly.

**Recommendation: A.** The evidence is unambiguous that M15 carries information but not standalone directional expectancy; its value is as a trigger under an HTF edge, which is precisely the CEO economic-profile mandate. Awaiting CEO direction (A / B / C) before committing the next research arc.
