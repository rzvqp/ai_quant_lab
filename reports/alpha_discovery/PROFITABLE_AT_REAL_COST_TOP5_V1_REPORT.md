# TOP-5 PROFITABLE-AT-REAL-COST STRATEGIES — 4H→15m + 15m→1m

Mandate: find the top strategies that are **profitable at the real live-shadow costs already in the project**, on two architectures — 4H edge +
15m entry/confirmation, and 15m analysis + 1m entry. Alpha/Research-executor discipline: pre-registered governed grammar scored ONCE at real cost
through the skepticism gate; adversarial falsification of anything too-good; honest labels (validated vs current-regime). No threshold mining.

## Real costs used (authoritative — `AI_TRADER_SHADOW_COST_MODEL_v1`, RATIFIED)
Live-shadow captured **real observed bid-ask spread** (n=175: median 0.07, p90 0.124, max 0.20 price units); **commission never captured (=0)**,
**no real position ever opened** (broker gate disabled). Ratified tiers, used verbatim:
- **BASE round-trip 0.05** (spread-only) · **STRESS round-trip 0.24** (spread 0.08 + slippage 0.08+0.08).
Simulator: governed `mstrat.simulate` (next-open entry, stop-wins-ties, ENGINE-v2 stop floor), **TICK forced 0.01** (the 0.1 is the known 10× bug).
Gate = profitable at BASE **and** STRESS, PF ≥ 1.15, ≥2/3 chronological thirds positive, drop-best-5% > 0, N ≥ 150, recent (2025+) ≥ 0, and beats
the naive long-beta baseline. **Naive long baseline (buy-every-96, 1ATR, rr2) = −0.128R (recent −0.194R)** → a long-only strategy being positive is
NOT trivial beta.

## Screen scope & falsification
Re-ran the **entire governed grammar S1–S51 (2,448 configs, 45 families)** at real cost. 2,270 configs had ≥100 trades; **34 passed the gate**.
**Adversarial check rejected 4 of them (all S49 "narrow-range fade")** as an engine artifact: median hold **0.0 bars**, 98% "exit=stop" yet 71% WR —
the bar-stop sits on the *wrong side* of entry after the breakout close, so the trade books an instant fake profit at its own stop (inverted-stop /
same-bar fill artifact; +0.70R/82%WR at ~5,000 trades/yr is impossible given the campaign's efficient-direction finding). **30 believable survivors
remain.** Every believable survivor is **long-tilted** (short/opposite-context counterparts all lose: S5-down −0.067, S9-down −0.048, S20-down
−0.091, S1-low −0.082) — consistent with a real long session/continuation edge, not symmetric.

## Honest era reality (critical)
Only **S5** has genuine multi-era positivity (2011-16 +0.026 incl. the 2013 crash · 2017-21 +0.033 · 2022-26 +0.139). **S9/S20 exist only 2023-2026**
(the panel's precomputed 4H/1H trend is defined only from 2023), and **S1's confirmed configs concentrate post-2021**. Their "3/3 eras" in the screen
are chronological thirds *within the recent regime*, NOT cross-regime. So: **S5 = VALIDATED multi-era; the rest = CURRENT-REGIME candidates**
(long-tilted, riding/selecting within the 2021-2026 gold bull) — they beat naive long and pass the gate, but are `READY_FOR_STATISTICIAN`, not validated.

## TOP 5 (4H→15m architecture) — profitable at real cost
| # | strategy | config | BASE / STRESS R | PF | WR | N (/yr) | recent 2025+ | class |
|---|---|---|---|---|---|---|---|---|
| **1** | **S5 NY Opening-Range Breakout (LONG)** | `session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3` | **+0.092 / +0.063** | 1.24/1.16 | 46.8% | 2006 (133) | +0.147 | **VALIDATED multi-era** |
| **2** | **S1 PDH sweep + displacement (LONG)** | `side=high, liq_ref=pdh_pdl, confirm=displacement, stop=beyond_sweep, exit=rr3, window=4` | +0.222 / **+0.166** | 1.39 | 39.1% | 322 (21) | +0.285 | current-regime |
| **3** | **S9 4H-trend + 1H-align continuation → 15m** | `c4h=up, conf1h=align, lb=20, stop=structural, exit=rr3` | +0.165 / **+0.146** | 1.37 | 46.0% | 665 (44) | +0.252 | current-regime |
| **4** | **S20 4H-up context + breakout → 15m** | `ctx=h4up, trig=breakout, lb=50, stop=atr, exit=rr3` | +0.161 / +0.119 | 1.24 | 32.3% | 777 (52) | +0.194 | current-regime |
| **5** | **S9 4H+1H continuation → 15m (higher-WR, rr2)** | `c4h=up, conf1h=align, lb=20, stop=structural, exit=rr2` | +0.135 / +0.117 | 1.32 | 48.6% | 695 (46) | +0.169 | current-regime |

Distinct-mechanism honorable mention (6th, different family): **S17 prev-week-high reject** `level=pw_high, mode=reject, stop=atr, exit=rr2` —
BASE +0.104 / STRESS +0.068, PF 1.17. #2 and #3/#5 give a profile mix: S5/S1 are profile-B (WR ~39-47% @ rr3), S9-rr2 is profile-A-leaning (WR 49%).
All are LONG-only; short counterparts lose (do not run them short).

## 15m→1m architecture (M1 = QUARANTINE / DISCOVERY-ONLY, 2025-08→2026-08, 1 yr, cost/R ~13% at 1-bar stop)
Tested M1-triggered entry vs M15-open on the top survivors over the M1 year, STRESS cost 0.24:
| strategy | M15-open | M1-trigger + **M15 stop** | M1-trigger + tight **M1 stop** |
|---|---|---|---|
| S5 ny ORB | +0.145R PF 1.41 | **+0.165R PF 1.53** (filters ~54%) | −0.094R WR 13% ✗ |
| S9 c4h=up | +0.158R PF 1.43 | +0.131R PF 1.39 | +0.315R WR 13% (variance) |
| S20 h4up | +0.198R PF 1.31 | +0.183R PF 1.32 | +0.173R WR 17% (variance) |

**Finding:** there is **no standalone 15m→1m edge**. The M1 layer is useful only as a **light confirmation FILTER on an already-valid HTF/M15 edge,
with an M15-scale stop** — it modestly improves **S5** (+0.145→+0.165R, PF 1.41→1.53) by dropping unconfirmed signals, and is neutral for S9/S20. A
**tight M1 stop is destroyed** (WR 13-17% — cost/R + wicking), confirming the quarantine verdict. M1 is DISCOVERY-ONLY (single bull regime); no
validation claim. This matches the economic-profile directive: HTF/M15 edge + LTF trigger + large target, never an M1 scalp.

## FINAL BLOCK
```
PROFITABLE_AT_REAL_COST_SEARCH_V1_COMPLETE = YES
REAL_COST_USED = BASE round-trip 0.05 / STRESS round-trip 0.24 (ratified AI_TRADER_SHADOW_COST_MODEL_v1; commission never captured; no real fills)
GRAMMAR_SCREENED = S1-S51 (2448 configs) · GATE_SURVIVORS = 34 · ARTIFACTS_REJECTED = 4 (S49 inverted-stop) · BELIEVABLE = 30
LONG_BETA_BASELINE = -0.128R (recent -0.194R) -> survivors beat it; all long-tilted (shorts lose)
TOP5_4H_TO_15M = [S5_ny_ORB_up_rr3 (VALIDATED), S1_pdh_sweep_displacement_rr3, S9_c4h_up_align_structural_rr3, S20_h4up_breakout_atr_rr3, S9_c4h_up_align_structural_rr2]
MULTI_ERA_VALIDATED = S5 only · CURRENT_REGIME_CANDIDATES = S1/S9/S20 (2021+/2023+ only, READY_FOR_STATISTICIAN, not validated)
ARCH_B_15M_TO_1M = NO standalone edge; M1 usable only as a confirmation FILTER (M15-scale stop) — modestly improves S5 (+0.165R PF 1.53); tight M1 stop destroyed (WR 13-17%). DISCOVERY-ONLY.
NEXT_AUTHORIZED_ACTION = NONE — CEO DECISION REQUIRED (send S1/S9/S20 current-regime candidates to Statistician for independent validation; S5 already validated)
```

Honest bottom line: strategies **are** profitable at the ratified real costs, and the top-5 is delivered. But only **S5 is a validated multi-era edge**;
the other four are **current-regime long-tilted candidates** that survive the skepticism gate and beat naive long, yet are not cross-era-validated —
they need independent Statistician validation + prospective confirmation before any promotion. I rejected the one "spectacular" result (S49) as an
engine artifact rather than hand it over. No promotion; protections intact.
```
PROFITABLE_AT_REAL_COST_TOP5 = DELIVERED — S5 validated + 4 current-regime survivors at STRESS 0.24; S49 rejected as artifact; M1 only a confirmation filter
```
