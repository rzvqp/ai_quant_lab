# SESSION_SPECIALIST_CONTRAST_REPORT_V1 — does the SESSION CONDITION add information? (§14)

The central §14 test: for the two break-even families (A, D), does the session condition beat a matched unconditional/beta control?
Control = same-direction entry at the same session decision, WITHOUT the session condition. Code: `sess_diag.py`.

## 1. Direction split + matched control
```
                                 net-R     D        C        O       yrs+   vs CONTROL
A.LONG  (break Asia high)        +0.010   -0.052   -0.029   +0.165   7/16
A.CONTROL uncond London LONG     -0.135   -0.223   -0.068   -0.029   5/16   -> A.LONG beats control +0.145
A.SHORT (break Asia low)         +0.010   +0.070   -0.009   -0.129   8/16
A.CONTROL uncond London SHORT    -0.121   -0.074   -0.194   -0.136   4/16   -> A.SHORT beats control +0.131
D.LONG  (London up -> NY long)   -0.010   -0.102   -0.024   +0.172   4/16
D.CONTROL uncond NY LONG         -0.120   -0.164   -0.096   -0.055   2/16   -> D.LONG beats control +0.110
D.SHORT (London down -> NY short)-0.043   +0.029   -0.174   -0.072   7/16
D.CONTROL uncond NY SHORT        -0.091   -0.037   -0.160   -0.124   2/16   -> D.SHORT beats control +0.048
```

## 2. §14 / §21 answer
**SESSION_INCREMENTAL_INFORMATION_FOUND = YES.** Session conditions consistently beat their unconditional/beta controls by +0.05 to
+0.15R (the Asia-range-break and London-trend states carry ex-ante information relative to blind session-open exposure).

**But it does NOT monetize.** No conditioned family reaches positive cross-era net expectancy:
- Absolute net-R is ~0 at best (A ±0.010; D ≤0).
- The positive era cells are **directional beta to the prevailing era-trend**: long-families positive only in the O bull (A.LONG O+0.165,
  D.LONG O+0.172), short-families positive only in the D bear (A.SHORT D+0.070, D.SHORT D+0.029). This is the R20 signature, not a stable
  session edge — it sign-flips by era and direction.
- Year robustness fails: best family (A) is positive in 7-8/16 years only.

## 3. This is the same pattern as the OB cycle
Two independent structural conditions — the **order-block level** (OB cycle) and now **session state** — each carry confirmed incremental
information over matched controls, yet neither monetizes into positive cross-era net expectancy. The information is real; direction-
efficiency and execution frictions consume it. XAU price-only structure is **informative but not directionally monetizable** beyond S5.

## 4. Verdict
No family survives §21 (positive NET_R + cross-era + year-robust + beats control + outlier/cost-robust). **SURVIVED = 0.**
`SESSION_INCREMENTAL_INFORMATION_FOUND = YES` (knowledge), `CROSS_ERA_STABLE_SURVIVOR = NO`, `NEW_STRATEGY_CANDIDATES = 0`.
