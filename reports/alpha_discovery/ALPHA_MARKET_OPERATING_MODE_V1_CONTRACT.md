# ALPHA_MARKET_OPERATING_MODE_V1_CONTRACT (FROZEN)

**Mandate:** `ALPHA-XAUUSD-HIERARCHICAL-MODE-STRUCTURAL-EVENT-DISCOVERY-001`, §3-8. Price-only, causal, H4-primary. Frozen from **price behavior only** — no P&L, no future-path labels, no optimization against Alpha outcomes. Implementation: `market_mode.py` `mode(h4frame)`. D1 not used (§6); NEUTRAL_ROTATION is research-local, NOT canonical RANGE (§7).

## Purpose (§4)
Separate economically distinct environments the old UP/DOWN/CHOP/QUIET/TRANSITION labels conflated — in particular a genuine **PRIMARY BEAR** from a **bearish CORRECTION inside a bull** (and mirror). Achieved by a two-scale H4 view: a PRIMARY backbone vs the IMMEDIATE direction.

## Frozen definitions (causal — all inputs known at H4 bar close)
- `pdisp` = (close − close[−P]) / ATR, **P=30** H4 bars (~5 trading days) — primary backbone displacement.
- `idisp` = (close − close[−I]) / ATR, **I=6** H4 bars (~1 day) — immediate displacement.
- `eff` = H4 directional efficiency(20). `vr` = ATR/ATR_ma (volatility tag). `ext` = (close−EMA20)/ATR (extension tag).
- **Frozen thresholds** (price-structure reasoning, not fit): PRIM_T=1.0 ATR, IMM_T=0.3 ATR, EFF_T=0.25.
- `prim` = +1 if pdisp>1.0 / −1 if pdisp<−1.0 / 0 else. `imm` = +1 if idisp>0.3 / −1 if idisp<−0.3 / 0 else.

## Modes (precedence by construction; mutually exclusive)
| mode | rule |
|---|---|
| **PRIMARY_BULL_IMPULSE** | prim=+1 & imm≥0 (bull backbone, advancing/pausing) |
| **BULL_CORRECTION** | prim=+1 & imm=−1 (bearish pullback INSIDE bull) |
| **PRIMARY_BEAR_IMPULSE** | prim=−1 & imm≤0 (genuine bear trend) |
| **BEAR_CORRECTION** | prim=−1 & imm=+1 (bullish pullback inside bear) |
| **NEUTRAL_ROTATION** | prim=0 & |eff|<0.25 (research-local; NOT canonical RANGE) |
| **TRANSITION** | prim=0 & |eff|≥0.25 (directional move without established backbone = emerging) |

Volatility (vr→HIGH/NORMAL/LOW) and extension (ext) are ATTRIBUTE tags, NOT separate modes (§5 avoid combinatorial explosion).

## Hierarchy & timestamps
H4 = primary mode authority. H1 = structural context/refinement (added at event stage). M15 owns the decision timestamp. All HTF context causal/last-closed (align by close_time ≤ decision). No D1.

## Population report (RAW bars / episodes / unique days / avg duration) — per era
| mode | b0 % | b1 % | 2021 % | 2022 % | 2023 % | avg dur |
|---|---|---|---|---|---|---|
| PRIMARY_BULL_IMPULSE | 29.8 | 32.7 | 33.7 | 38.3 | 31.5 | 21-25h |
| BULL_CORRECTION | 10.6 | 11.3 | 10.9 | 13.7 | 12.2 | 9-12h |
| PRIMARY_BEAR_IMPULSE | 27.8 | 28.8 | 23.7 | 19.6 | 29.8 | 16-27h |
| BEAR_CORRECTION | 12.3 | 10.1 | 8.5 | 8.3 | 8.4 | 10-14h |
| NEUTRAL_ROTATION | 14.4 | 13.5 | 15.4 | 14.0 | 14.6 | 9-11h |
| TRANSITION | 4.3 | 3.6 | 3.3 | 6.1 | 3.6 | 6-8h |
Source: b0/b1 = hist H4 (_from_M15_v2); 2021/2022/2023 = gated sb H4. Every mode has sufficient N/episodes in every era → cross-era gate viable for all modes. Corrections are SHORTER-duration than primary impulses (economically coherent — pullbacks resolve faster).

## Transition matrix (b0, episode-level; economically coherent)
Dominant cycles: PRIMARY_BULL_IMPULSE⇄BULL_CORRECTION (101/78), PRIMARY_BEAR_IMPULSE⇄BEAR_CORRECTION (96/78). Cross-direction flips RARE (bull→bear ≈5) — the primary backbone is STICKY; a correction transitions BACK to its primary, not into the opposite trend. NEUTRAL_ROTATION/TRANSITION are the connectors between primary regimes. => BULL_CORRECTION is genuinely NOT PRIMARY_BEAR (§4 solved).

## Config identity
`market_mode.py` mode(): P=30, I=6, PRIM_T=1.0, IMM_T=0.3, EFF_T=0.25. FROZEN before any structural-event outcome. Any taxonomy revision requires a new mandate + new identity + economic reason independent of P&L (§29).

**Frozen. Next (§10):** FIRST structural-event family — LIQUIDITY EVENT → RECLAIM/FAILURE → DISPLACEMENT → FUTURE PATH — conditioned on these frozen modes, information-first.
