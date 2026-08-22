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