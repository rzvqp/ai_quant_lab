# ALPHA_DXY_NDX1 — first cross-era-STABLE incremental DXY signal (NON-DIRECTIONAL)

Mandate `DXY_INCREMENTAL_INFORMATION_DISCOVERY_V1` (CEO 2026-08-24). The prior DXY frontier (`...INFORMATION-001`) found DXY→XAU
DIRECTION carries real but REGIME-INVERTING info (NOT_SUPPORTED as stable). This finding is on the NEW axis the prior work did not
test: **NON-DIRECTIONAL** (magnitude/timing) incremental info on the XAU compression→expansion state (VOLTIME-1). Direction-free →
no sign to invert → the reason it is stable where direction was not.

## Preregistered hypothesis (economic rationale, no mining)
**H-NDX1:** XAU and DXY both respond to macro shocks (rate surprises, risk events). A causal DXY IMPULSE (`d_imp` = 4h DXY move / DXY
ATR, from the last-closed DXY H1 bar per the ratified aligner) signals a macro event underway that AMPLIFIES XAU's forward expansion —
regardless of XAU direction. Test: within XAU-compressed bars, does DXY-impulse-HIGH raise P(2R within 8h)/forward-range ABOVE the XAU
price-only baseline, CONTROLLING for XAU's own volatility, deduped, and SIGN-STABLE across all research blocks?

## Result (`dxy_voltime.py`, `dxy_incremental.py`) — MATERIAL + STABLE + NON-REDUNDANT + DEDUP-ROBUST
Blocks b0(2011-13)/b1(2016-18)/y2123(2021-07..2023-12) — all ≤2023-12-29; **2024+ PROTECTED, never loaded**. Causal DXY lag0 (contract
enforced, 100% causal, coverage 97.4/97.8/99.9%).
- **Residual DXY-impulse dP2R (controlled for XAU-own vol-ratio tercile, EVENT-DEDUPED to non-overlapping windows): +0.076 / +0.086 /
  +0.107 (b0/b1/y2123)** — material (all >0.03), SIGN-STABLE across all 3 blocks including the inflation regime that inverted every
  DIRECTIONAL DXY signal. Positive in every vol-tercile of every block (+0.015..+0.155). Dedup n = 809/795/397 independent events.
- Univariate (dxy_voltime): DXY-impulse-high → larger XAU forward range + P2R (dP2R +0.04/+0.03/+0.06 raw); DXY-vol-ratio-high → SMALLER
  forward range (vol mean-reversion, largely redundant with XAU vol) — the IMPULSE effect, not the vol-level effect, is the genuine one.
- **H-DIR1 (direction) NEGATIVE/decaying:** P(XAU down | DXY up) = 0.535/0.514/0.505 — barely above coinflip and fading; DXY does NOT
  resolve XAU expansion DIRECTION (confirms the prior directional NOT_SUPPORTED).

## Status & honest caveat
**FROZEN as DXY-NDX1 information finding** (`ALPHA_DXY_INFORMATION_MAP.md` lineage). This is the FIRST cross-era-stable incremental
signal in the whole campaign — but it is **INFORMATION (how-large/how-fast), NOT yet a tradeable EDGE.** The expansion magnitude is
amplified by DXY-impulse, but DIRECTION remains unresolved (H-DIR1 null). Per VOLTIME, a bigger *symmetric* expansion still whipsaws.
**Tradeability is UNPROVEN and is the next test:** does DXY-impulse make the expansion more DIRECTIONAL (less whipsaw) so a breakout /
S5-style entry survives costs — or merely bigger-symmetric (still untradeable)? MECHANIZE only if a DXY-impulse-conditioned entry beats
its unconditioned baseline after full costs cross-block. No strategy, no P&L claim yet. S5 frozen/untouched. No parameter mining
(median splits, predeclared features). No protected data.

## TRADEABILITY VERDICT (`dxy_tradeable.py`) — INFORMATION-ONLY, NOT tradeable
Compression-breakout on the DXY-aligned XAU-H1 blocks (STRESS 0.24): BASELINE all breakouts net −0.309/−0.307/−0.333 (b0/b1/y2123,
confirms H1 breakout ≈ M15 VOLTIME-2 null-negative). **DXY-IMP-FILTER net −0.348/−0.346/−0.468 (WORSE than baseline)** — the DXY-impulse-
amplified expansion is bigger but DIRECTIONALLY SYMMETRIC, so the wider move whipsaws MORE, not less. DXY-DIR-CONFLUENCE (break agrees
with DXY-inverse) net −0.502/−0.328/−0.300 (also all-negative; direction weak + era-inverting). **NONE tradeable.**
**VERDICT: DXY-NDX1 = genuine, cross-era-stable, non-redundant NON-DIRECTIONAL INFORMATION (first stable incremental signal in the
campaign) but NOT a tradeable edge — magnitude/timing is amplified, DIRECTION remains unresolved, and a bigger symmetric expansion does
not monetize (whipsaw persists/worsens).** This refines (does not overturn) the prior `DXY_INCREMENTAL_INFORMATION_NOT_SUPPORTED`:
DXY carries STABLE non-directional info (new) but still no tradeable directional edge (confirmed). Answers the CEO question:
WHEN/HOW-LARGE/HOW-FAST → DXY helps (stable info); WHICH-WAY → no; TRADEABLE → no. Frozen as an information finding; not mechanized.

## JOINT compression/convergence (`dxy_joint.py`) — negative; DXY frontier V1 CONCLUSION
Last distinct DXY mechanism: XAU breakout gated on DXY-also-compressed + DXY-inverse-impulse at the break (shared-catalyst coordinated
direction). All variants net-negative every block: baseline −0.309/−0.307/−0.333; +DXY-compressed −0.307/−0.254/−0.376; +DXY-inverse-
impulse −0.424/−0.264/−0.373. The DXY coordination does not rescue the breakout — whipsaw dominates.

## DXY_INCREMENTAL_INFORMATION_DISCOVERY_V1 — FRONTIER CONCLUSION
Comprehensively answered the CEO question "can DXY help resolve WHEN/HOW-LARGE/HOW-FAST/WHICH-WAY the predictable XAU expansion?":
- **WHEN / HOW-LARGE / HOW-FAST → YES (genuine, first stable incremental signal): DXY-NDX1** — a causal DXY impulse amplifies XAU
  expansion magnitude/timing (dP2R +0.08/+0.09/+0.11), cross-era-stable, non-redundant (survives XAU-own-vol control), dedup-robust.
- **WHICH-WAY → NO:** DXY direction is weak + regime-conditional (inverse in disinflation b0/b1, flips in the 2021-23 inflation regime);
  H-DIR1, dir-confluence, and joint-convergence all confirm no stable direction resolution.
- **TRADEABLE → NO:** the stable DXY info is NON-DIRECTIONAL (magnitude), and a bigger symmetric expansion is not monetizable (all DXY-
  conditioned breakouts net-negative, some worse than baseline). No cross-era-stable tradeable DXY edge.
- **Refines (not overturns) the prior `DXY_INCREMENTAL_INFORMATION_NOT_SUPPORTED`:** DXY carries a STABLE non-directional incremental
  component (NDX1, new positive) plus real-but-regime-conditional directional info (prior); neither yields a tradeable edge.
- **Mechanism / next axis:** DXY↔gold direction is a reduced-form of the real-yield / monetary regime; DXY alone (an endogenous output)
  cannot be a cross-era-stable direction resolver. The prior work's recommendation stands and is now doubly-confirmed: the deeper STABLE
  driver is REAL YIELDS (which DXY only reflects) — a DIFFERENT exogenous axis requiring separate CEO authorization + governed data.
  2024+ DXY never accessed; causal contract enforced; S5 frozen; no mining. **GOVERNANCE GATE: DXY-only frontier concluded.**
