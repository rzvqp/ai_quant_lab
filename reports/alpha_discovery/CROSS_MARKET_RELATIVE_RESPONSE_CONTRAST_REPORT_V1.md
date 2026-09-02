# CROSS_MARKET_RELATIVE_RESPONSE_CONTRAST_REPORT_V1 — does the RELATIVE RESPONSE add information? (§14)

The central §14 test: does the relative-response residual beat matched controls — above all the **simple DXY impulse** (§4 forbids
re-selling the impulse; we must show the residual adds something the raw impulse does not). Code: `cm_scan.py`.

## 1. Relative-response families vs simple-impulse control
```
                              net-R     D(b0+b1)   O(y2123)
A catch-up                    -0.084    +0.031     -0.359
B relative-strength           -0.240    -0.333     -0.013
C overshoot-fade              -0.125    -0.162     +0.043
E session-resolution          -0.058    -0.047     -0.087
CONTROL simple-DXY-impulse    -0.069    -0.020     -0.188
```

## 2. §14 / §23 answer — CROSS_MARKET_INCREMENTAL_INFORMATION_FOUND = NO
- **A catch-up (−0.084) is WORSE than the simple impulse (−0.069)** — conditioning on XAU under-reaction does not improve on "DXY moved."
- **B (−0.240) and C (−0.125) are far worse** than the control.
- **E (−0.058) ≈ control (−0.069)** — no meaningful improvement, and both negative on tiny N.

So the relative-response residual **does not add incremental information** over the raw DXY impulse — which is itself already negative
(consistent with the prior DXY-NDX1 finding: DXY→gold is regime-conditional / information-only, not a directional edge). This is a
**stronger** negative than the OB-level and session-state cycles, where the structural condition at least beat its control; here the new
cross-market residual beats nothing.

## 3. Cross-era instability (§15)
No family is sign-stable across the three governed blocks: A is +0.093 in b1 but −0.359 in y2123; C is −0.19 in b0 but +0.04 in y2123. The
few positive slice-cells are isolated and small — no prospectively-identifiable regime, just noise across a 3-block, DXY-only sample.

## 4. Verdict
`CROSS_MARKET_INCREMENTAL_INFORMATION_FOUND = NO` · `CROSS_ERA_STABLE_SURVIVOR = NO` · `SURVIVED = 0`. Within the available governed data
(DXY-only, H1, 3 blocks, no 2024+, no risk proxy), the XAU-vs-DXY relative-response mechanism carries no monetizable directional
information and does not beat the simple impulse. A definitive cross-market answer would require a governed risk-market series (e.g., NDX)
and 2024+ DXY — neither exists in-project.
