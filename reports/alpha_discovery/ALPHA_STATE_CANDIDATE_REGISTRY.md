# ALPHA_STATE_CANDIDATE_REGISTRY

Causal STATES that survive the information-first gates (mandate `ALPHA-XAUUSD-CAUSAL-STATE-PATH-DISCOVERY-001`). A state advances only on MATERIAL base-rate lift (§12) + stability (§13) + DISC/CONF (§14). Strategy geometry is derived AFTER (Stage C), never imposed first (§3, §17).

| STATE_ID | definition (causal) | headline info (univariate, DEV) | status |
|---|---|---|---|
| ST-TREND-EXH | trend=(EMA20-EMA50)/ATR in the top decile (strongly extended up) on H1 | SHORT P(+100/-70)=0.472 vs base 0.391 (+0.081, +21pct, mono +0.50); LONG P drops to 0.313 (-0.105) | **INFO_UNSTABLE_KILLED** — fails stability: DISC +0.081 -> CONF -0.076 (inverts OOS); per-year 2021 +0.074/2022 +0.122/**2023 -0.029**; cross-pop b0 -0.001/b1 -0.032 (no generalization). A 2021-22 regime transient, not stable info. |
| ST-VOL-CONT | vol_ratio / vol_change high (rising volatility) on H1 | favors prevailing-trend continuation (LONG +, SHORT -) | INFO_NOTED — likely REDUNDANT with LONG trend-beta; test as a FILTER/interaction, not standalone |
| ST-EFFIC-SHORT-GATE | directional efficiency low/negative | monotone SHORT gate (high up-effic kills shorts) | INFO_NOTED — candidate SHORT filter (interaction), not standalone |

**Priority:** ST-TREND-EXH (a potential SHORT diversifier + LONG-avoidance filter) — the single highest-information causal state found. Independence vs frozen: it is COUNTER to LONG trend-beta (fires when extended, not on compression) -> not obviously redundant with COMP-CONT-L; overlap-check required at Stage C.

| ST-UPEFF-DROP-FILTER | up-efficiency (effic) high at t-6 then <0.1 at t (trend-drive fading) | LONG P(+100/-70) lift -0.069 STABLE (DISC -0.088/CONF -0.041; 2021 -0.054/2023 -0.099) | **STABLE_FILTER (LONG-avoidance)** — not a standalone trade (negative signal); re-encodes trend-drive presence (COMP-CONT-L territory); cannot apply to frozen strategies (§21/§24). Recorded, not promoted. |

**Transition family verdict:** no stable POSITIVE tradeable path-lift; the one stable signal is a LONG-avoidance filter. Both static-state and transition families now mapped -> next: path-history / multi-TF / session-conditioned states.

| ST-CLEAN-EXH-SHORT | clean recent advance near highs (realized-eff>0.3-0.5 & pullback<0.5 ATR) -> SHORT | DEV within-period STABLE +0.039 (all years + DISC/CONF); LONG-avoidance side -0.156 | **XPOP_UNSTABLE_KILLED** — cross-population INVERTS (b0/b1 SHORT lift -0.009 to -0.052). A 2021-2023 bid-market-regime property, not general. First stable-positive DEV signal, correctly killed by cross-population. |

**Meta-finding:** state->path relationships are REGIME-CONDITIONAL — within-period stability (per-year+DISC/CONF) is necessary but NOT sufficient; cross-population is the decisive gate. Three families mapped (static/transition/path-history); all within-period-stable signals fail cross-population.
## Status corrections (CEO mandate ALPHA-XAUUSD-REGIME-CONDITIONAL-STATE-PATH-DISCOVERY-001)
- **H4-bo-raw-S: INDEPENDENT_VALIDATION_BLOCKED** (PACKAGE_REPRODUCIBLE + NON_CAUSAL_LEGACY_D1_FILTER_CONFIRMED). NOT a validated/pending portfolio strategy; reference/overlap artifact only. Clean frozen objects = S5 (validated) + COMP-CONT-L-rr2 (pending).
- **Method shift:** generalization gate is now SAME-REGIME cross-era (not same-sign across different regimes). A regime-conditional edge is valid if the regime is causal+frozen+pre-entry and the edge is stable across distinct occurrences of that regime.

## M15 mandate candidates
- **ST-M15-HIGHVOL-SHORT** (univariate) — high/rising M15 vol -> SHORT. CROSS-ERA-STABLE INFO (+0.058 P(+70/-50)) but **STABLE_INFO_NOT_TRADEABLE**: no geometry net-positive cross-era (DEV neg, b1 neg, b0 marginal +0.03). The lift is real but sub-breakeven.
- **ST-M15-HIGHVOL-SHORT-DOWNPARENT** — high-vol M15 short in H1 DOWN parent regime. DEV +0.112 (2.0ATR rr1.0, best10 +0.015, 14.7tpm); b0 sign-confirmed (+0.03..+0.13, best10<0); **b1 CONTRADICTS (all neg)**. Status **REGIME_SPECIFIC_INFO_NOT_CROSS_ERA_STABLE** — fails same-regime cross-era (works in genuine-downtrend eras DEV/b0, fails in b1 uptrend-corrections). NOT frozen. Closest new-SHORT near-miss; a causal 'genuine-downtrend' regime def is a future direction (must not be P&L-fit).

## ST-M15-NY-HIGHVOL-SHORT (candidate — pending tradeability)
- **State:** M15 high/rising volatility (vr>1.3 OR vc>1.2) occurring in the NY session (13-21 UTC) -> SHORT.
- **Evidence:** P(+70/-50) 8h SHORT lift vs NY session base = +0.070 DEV, b0 +0.08, b1 +0.05 (all same-sign, all >=0.02, event-deduped). FIRST directional M15 signal to survive the b1 cross-era gate (DOWN-parent conditioning failed b1; session conditioning passes it).
- **Why it may be causal:** NY-session volatility bursts (US open + macro releases) carry a consistent short skew on XAUUSD across eras — a session/liquidity mechanism, not a regime-fitted one.
- **Status:** `INFO_CONFIRMED_CROSS_ERA_NOT_TRADEABLE` (`state_m15_ny_hvshort.py`). The +0.070 P(+70/-50) SHORT lift is REAL and cross-era-stable (survives b1), but NO geometry converts it to net-positive expectancy: all 4 fixed brackets + 9 structural ATR stops are net-NEGATIVE after STRESS cost on DEV AND b0 AND b1 (best DEV avgR -0.034 w/ losing 2022 -0.16; b0 -0.021; b1 -0.088), and best10 is -0.15..-0.38 everywhere -> the small edge is carried by outliers, not a robust core. Effect size (~+0.05-0.07 P-lift) too small vs adverse-first M15 path + cost. NOT frozen. Confirms: M15 volatility carries directional INFORMATION but not exploitable standalone directional expectancy.
