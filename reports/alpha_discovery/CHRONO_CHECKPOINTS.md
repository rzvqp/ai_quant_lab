# CHRONO_CHECKPOINTS — chronological market learning (walk-forward, forward-tested)

Each quarter: hypotheses from readings RESOLVED by quarter-end (no leakage); previous quarter's hypotheses FORWARD-TESTED here.


## HEADLINE — quarterly non-stationarity (walk-forward reader edge)
  quarters=27 mean_net=-0.246 std_net=0.185 %positive_quarters=15%
  lag-1 autocorr(net)=+0.11 (>0 => good quarter predicts next; ~0 => no persistence) sign-persistence=81%
  per-quarter net: 2020-Q1:+0.16 2020-Q2:-0.28 2020-Q3:+0.07 2020-Q4:-0.52 2021-Q1:-0.52 2021-Q2:-0.26 2021-Q3:-0.50 2021-Q4:-0.40 2022-Q1:-0.40 2022-Q2:-0.25 2022-Q3:-0.17 2022-Q4:-0.42 2023-Q1:-0.40 2023-Q2:-0.19 2023-Q3:-0.35 2023-Q4:-0.07 2024-Q1:-0.23 2024-Q2:-0.27 2024-Q3:-0.17 2024-Q4:-0.21 2025-Q1:-0.06 2025-Q2:-0.31 2025-Q3:-0.31 2025-Q4:+0.06 2026-Q1:+0.03 2026-Q2:-0.20 2026-Q3:-0.50

## Checkpoint 2020-Q1  (frozen readings in-quarter=195, resolved-by-Q=195, base P2R=0.467 net=+0.160)
  - regime P2R: up=0.52(n100) weak_up=0.45(n49) weak_down=0.40(n35)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BULLISH|up|nearZone=0.60(n72)_V[2020-Q1]; BULLISH|weak_up|nearZone=0.47(n38)_V[2020-Q1]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.50(n111) vs N1_weak P2R=0.43(n84)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2020-Q2  (frozen readings in-quarter=115, resolved-by-Q=112, base P2R=0.321 net=-0.276)
  - regime P2R: weak_up=0.35(n54) up=0.42(n36) weak_down=0.12(n16)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.36(n42) vs N1_weak P2R=0.30(n70)
  - FORWARD-TEST of previous checkpoint hyps: BULLISH|up|nearZone: prevP2R=0.60->fwdP2R=0.43(n23) HOLD; BULLISH|weak_up|nearZone: prevP2R=0.47->fwdP2R=0.33(n43) DECAY

## Checkpoint 2020-Q3  (frozen readings in-quarter=186, resolved-by-Q=181, base P2R=0.436 net=+0.069)
  - regime P2R: up=0.48(n81) weak_up=0.49(n57) weak_down=0.28(n43)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BULLISH|weak_up|nearZone=0.59(n41)_V[2020-Q3]; BULLISH|up|nearZone=0.48(n62)_V[2020-Q3]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.48(n81) vs N1_weak P2R=0.40(n100)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2020-Q4  (frozen readings in-quarter=126, resolved-by-Q=125, base P2R=0.240 net=-0.520)
  - regime P2R: weak_up=0.25(n53) up=0.08(n38) weak_down=0.12(n17) down=0.71(n17)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.27(n55) vs N1_weak P2R=0.21(n70)
  - FORWARD-TEST of previous checkpoint hyps: BULLISH|weak_up|nearZone: prevP2R=0.59->fwdP2R=0.20(n40) DECAY; BULLISH|up|nearZone: prevP2R=0.48->fwdP2R=0.10(n30) DECAY

## Checkpoint 2021-Q1  (frozen readings in-quarter=96, resolved-by-Q=96, base P2R=0.240 net=-0.521)
  - regime P2R: weak_down=0.30(n53) up=0.25(n20) weak_up=0.06(n17)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.23(n26) vs N1_weak P2R=0.24(n70)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2021-Q2  (frozen readings in-quarter=168, resolved-by-Q=168, base P2R=0.327 net=-0.258)
  - regime P2R: up=0.39(n67) weak_up=0.31(n48) down=0.19(n27) weak_down=0.35(n26)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.33(n94) vs N1_weak P2R=0.32(n74)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2021-Q3  (frozen readings in-quarter=97, resolved-by-Q=97, base P2R=0.247 net=-0.498)
  - regime P2R: weak_up=0.37(n43) weak_down=0.09(n35)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.26(n19) vs N1_weak P2R=0.24(n78)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2021-Q4  (frozen readings in-quarter=150, resolved-by-Q=147, base P2R=0.279 net=-0.403)
  - regime P2R: weak_up=0.28(n75) weak_down=0.30(n33) up=0.27(n30)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.26(n39) vs N1_weak P2R=0.29(n108)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2022-Q1  (frozen readings in-quarter=164, resolved-by-Q=164, base P2R=0.280 net=-0.399)
  - regime P2R: up=0.35(n69) weak_up=0.25(n56) weak_down=0.21(n39)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.35(n69) vs N1_weak P2R=0.23(n95)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2022-Q2  (frozen readings in-quarter=157, resolved-by-Q=157, base P2R=0.331 net=-0.246)
  - regime P2R: weak_down=0.31(n64) down=0.48(n42) weak_up=0.11(n28) up=0.39(n23)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BEARISH|down|nearZone=0.45(n33)_V[2022-Q2]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.45(n65) vs N1_weak P2R=0.25(n92)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2022-Q3  (frozen readings in-quarter=218, resolved-by-Q=216, base P2R=0.356 net=-0.171)
  - regime P2R: down=0.27(n77) weak_up=0.27(n74) weak_down=0.55(n65)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BEARISH|weak_down|nearZone=0.59(n51)_V[2022-Q3]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.27(n77) vs N1_weak P2R=0.40(n139)
  - FORWARD-TEST of previous checkpoint hyps: BEARISH|down|nearZone: prevP2R=0.45->fwdP2R=0.25(n55) DECAY

## Checkpoint 2022-Q4  (frozen readings in-quarter=129, resolved-by-Q=124, base P2R=0.274 net=-0.417)
  - regime P2R: weak_up=0.30(n61) weak_down=0.24(n37) up=0.27(n26)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.27(n26) vs N1_weak P2R=0.28(n98)
  - FORWARD-TEST of previous checkpoint hyps: BEARISH|weak_down|nearZone: prevP2R=0.59->fwdP2R=0.23(n31) DECAY

## Checkpoint 2023-Q1  (frozen readings in-quarter=193, resolved-by-Q=193, base P2R=0.280 net=-0.401)
  - regime P2R: weak_up=0.28(n109) weak_down=0.20(n44) up=0.50(n28)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.38(n40) vs N1_weak P2R=0.25(n153)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2023-Q2  (frozen readings in-quarter=117, resolved-by-Q=117, base P2R=0.350 net=-0.189)
  - regime P2R: weak_down=0.38(n58) weak_up=0.36(n45)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.21(n14) vs N1_weak P2R=0.37(n103)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2023-Q3  (frozen readings in-quarter=146, resolved-by-Q=142, base P2R=0.296 net=-0.353)
  - regime P2R: weak_down=0.35(n69) down=0.26(n39) weak_up=0.21(n28)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.27(n45) vs N1_weak P2R=0.31(n97)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2023-Q4  (frozen readings in-quarter=174, resolved-by-Q=174, base P2R=0.391 net=-0.068)
  - regime P2R: weak_up=0.42(n103) weak_down=0.35(n48)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.35(n23) vs N1_weak P2R=0.40(n151)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2024-Q1  (frozen readings in-quarter=114, resolved-by-Q=110, base P2R=0.336 net=-0.231)
  - regime P2R: up=0.33(n60) weak_up=0.36(n42)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.32(n68) vs N1_weak P2R=0.36(n42)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2024-Q2  (frozen readings in-quarter=176, resolved-by-Q=176, base P2R=0.324 net=-0.268)
  - regime P2R: weak_up=0.41(n93) up=0.18(n49) weak_down=0.29(n34)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BULLISH|weak_up|nearZone=0.46(n65)_V[2024-Q2]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.18(n49) vs N1_weak P2R=0.38(n127)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2024-Q3  (frozen readings in-quarter=191, resolved-by-Q=188, base P2R=0.356 net=-0.171)
  - regime P2R: weak_up=0.49(n105) up=0.19(n57)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BULLISH|weak_up|nearZone=0.49(n82)_V[2024-Q3]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.20(n69) vs N1_weak P2R=0.45(n119)
  - FORWARD-TEST of previous checkpoint hyps: BULLISH|weak_up|nearZone: prevP2R=0.46->fwdP2R=0.49(n82) HOLD

## Checkpoint 2024-Q4  (frozen readings in-quarter=160, resolved-by-Q=160, base P2R=0.344 net=-0.209)
  - regime P2R: up=0.24(n74) weak_up=0.64(n33) weak_down=0.35(n31) down=0.23(n22)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.24(n96) vs N1_weak P2R=0.50(n64)
  - FORWARD-TEST of previous checkpoint hyps: BULLISH|weak_up|nearZone: prevP2R=0.49->fwdP2R=0.60(n25) HOLD

## Checkpoint 2025-Q1  (frozen readings in-quarter=183, resolved-by-Q=180, base P2R=0.394 net=-0.057)
  - regime P2R: weak_up=0.46(n123) up=0.24(n37) weak_down=0.27(n15)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BULLISH|weak_up|noZone=0.57(n30)_V[2025-Q1]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.26(n42) vs N1_weak P2R=0.43(n138)
  - FORWARD-TEST: (no previous checkpoint)

## Checkpoint 2025-Q2  (frozen readings in-quarter=158, resolved-by-Q=158, base P2R=0.310 net=-0.310)
  - regime P2R: weak_up=0.30(n73) weak_down=0.41(n46) up=0.24(n25)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BEARISH|weak_down|nearZone=0.45(n33)_V[2025-Q2]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.21(n39) vs N1_weak P2R=0.34(n119)
  - FORWARD-TEST of previous checkpoint hyps: BULLISH|weak_up|noZone: prevP2R=0.57->fwdP2R=0.39(n18) HOLD

## Checkpoint 2025-Q3  (frozen readings in-quarter=215, resolved-by-Q=212, base P2R=0.311 net=-0.306)
  - regime P2R: weak_up=0.32(n111) up=0.45(n65) weak_down=0.00(n30)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BULLISH|up|nearZone=0.46(n56)_V[2025-Q3]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.44(n71) vs N1_weak P2R=0.25(n141)
  - FORWARD-TEST of previous checkpoint hyps: BEARISH|weak_down|nearZone: prevP2R=0.45->fwdP2R=0.00(n26) DECAY

## Checkpoint 2025-Q4  (frozen readings in-quarter=224, resolved-by-Q=224, base P2R=0.433 net=+0.059)
  - regime P2R: weak_up=0.56(n104) up=0.30(n69) weak_down=0.35(n51)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BULLISH|weak_up|nearZone=0.61(n74)_V[2025-Q4]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.30(n69) vs N1_weak P2R=0.49(n155)
  - FORWARD-TEST of previous checkpoint hyps: BULLISH|up|nearZone: prevP2R=0.46->fwdP2R=0.26(n53) DECAY

## Checkpoint 2026-Q1  (frozen readings in-quarter=202, resolved-by-Q=198, base P2R=0.424 net=+0.033)
  - regime P2R: weak_up=0.42(n100) weak_down=0.48(n44) up=0.33(n39) down=0.53(n15)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): BULLISH|weak_up|nearZone=0.49(n70)_V[2026-Q1]; BEARISH|weak_down|nearZone=0.49(n39)_V[2026-Q1]
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.39(n54) vs N1_weak P2R=0.44(n144)
  - FORWARD-TEST of previous checkpoint hyps: BULLISH|weak_up|nearZone: prevP2R=0.61->fwdP2R=0.49(n71) HOLD

## Checkpoint 2026-Q2  (frozen readings in-quarter=124, resolved-by-Q=124, base P2R=0.347 net=-0.200)
  - regime P2R: weak_down=0.42(n73) weak_up=0.23(n26) down=0.19(n21)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.24(n25) vs N1_weak P2R=0.37(n99)
  - FORWARD-TEST of previous checkpoint hyps: BULLISH|weak_up|nearZone: prevP2R=0.49->fwdP2R=0.29(n21) DECAY; BEARISH|weak_down|nearZone: prevP2R=0.49->fwdP2R=0.38(n53) HOLD

## Checkpoint 2026-Q3  (frozen readings in-quarter=53, resolved-by-Q=53, base P2R=0.245 net=-0.504)
  - regime P2R: weak_down=0.15(n20) down=0.20(n15)
  - BUY cells (top): none n>=20
  - SELL cells (top): none n>=20
  - promising hypotheses (P2R>=0.45, n>=30): NONE
  - failed cells (P2R<=~null, n>=30): none
  - readiness proxy: N1_strong P2R=0.14(n22) vs N1_weak P2R=0.32(n31)
  - FORWARD-TEST: (no previous checkpoint)

## Multi-quarter survival (forward-quarters a hypothesis held above base)
  BULLISH|weak_up|nearZone: held 3 forward-quarter(s); lineage [('2020-Q1', np.float64(0.474), 38), ('2020-Q3', np.float64(0.585), 41), ('2024-Q2', np.float64(0.462), 65), ('2024-Q3', np.float64(0.488), 82), ('2025-Q4', np.float64(0.608), 74), ('2026-Q1', np.float64(0.486), 70)]
  BULLISH|up|nearZone: held 1 forward-quarter(s); lineage [('2020-Q1', np.float64(0.597), 72), ('2020-Q3', np.float64(0.484), 62), ('2025-Q3', np.float64(0.464), 56)]
  BEARISH|weak_down|nearZone: held 1 forward-quarter(s); lineage [('2022-Q3', np.float64(0.588), 51), ('2025-Q2', np.float64(0.455), 33), ('2026-Q1', np.float64(0.487), 39)]
  BULLISH|weak_up|noZone: held 1 forward-quarter(s); lineage [('2025-Q1', np.float64(0.567), 30)]
  BEARISH|down|nearZone: held 0 forward-quarter(s); lineage [('2022-Q2', np.float64(0.455), 33)]
## WUZ-1 MECHANIZE + FALSIFY (2026-08-24) — the one forward-surviving cell, CLEAN NEGATIVE
`chrono_wuz1.py`: BULLISH|{up,weak_up}|nearZone LONG (buy uptrend-regime pullback to a demand zone). Full-history 3,728 signals:
P2R=0.358, gross +0.073R, **net −0.167R** (STRESS 0.24). FAIL all gate dims: DISC/CONF/OOS net −0.250/−0.143/−0.073 (negative every era;
OOS gross +0.167 but costs erase it); tail −0.167; 2×cost −0.407; per-year net>0 3/16; LOYO worst −0.186; entry-delay −0.172; neighbors
negative. **VERDICT: FAIL (cost-rejected). CLOSED.** Even the single best chronologically forward-surviving cell has no edge after costs.

## CHRONOLOGICAL CAMPAIGN VERDICT (first full pass, 2020-Q1 → 2026-Q3)
- Top-down N-node zone-reaction reader: **net-negative in 23/27 quarters** (mean −0.246R/trade); quarterly edge non-persistent
  (lag-1 autocorr +0.11). The occasional positive quarter does not carry forward.
- Walk-forward forward-testing (no leakage, versioned lineage): only `BULLISH|weak_up|nearZone` held ≥3 forward quarters; mechanized
  as WUZ-1 → FAILS the full quant gate under costs.
- **Conclusion:** across quant screens (56 branches), predefined SMC, canonical top-down reading (random + chronological), broadened
  structural observation, and 2 preregistered candidates (ASREJ-1, WUZ-1) both fully falsified — **no robust directional edge exists at
  M15 beyond S5.** S5 (NY opening-range breakout, direction self-supplied) remains the ONLY validated edge. Costs are the consistent
  killer of thin gross tendencies. This is a strong, honest negative, established by five independent methods.

## REGIME-CONDITIONAL (pooled 4,231 chrono readings) — NO PROFITABLE REGIME
Net R/trade by regime state (STRESS 0.24 cost): EVERY cell negative. Best = BULLISH×high_choppy −0.044 (n657, closest to breakeven);
BULLISH×high_directional −0.130; BEARISH×high_choppy −0.374 (worst). By vol alone: high_choppy −0.163 … low −0.284 (all neg). By
decision: BUY −0.15 beats SELL −0.28 (era-trend), both negative; SELL×nearZone worst (−0.336). Overall −0.204. **No volatility state, no
regime direction, no zone condition, and neither trade side is net-positive.** The top-down zone-reaction reader has no edge in ANY
regime — the strongest possible negative, consistent across chronological, pooled, and per-regime views. Mandate item "which mechanisms
are regime-specific": answer = none, for this reading. S5 remains the ONLY validated edge.
