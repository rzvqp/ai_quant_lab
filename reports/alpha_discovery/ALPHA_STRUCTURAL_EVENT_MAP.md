# ALPHA_STRUCTURAL_EVENT_MAP

Mandate `ALPHA-XAUUSD-HIERARCHICAL-MODE-STRUCTURAL-EVENT-DISCOVERY-001`. Architecture: H4 MARKET MODE + H1 context + M15 structural EVENT + POST-EVENT RESPONSE -> future path -> SPECIALIST strategy. Market modes frozen in `ALPHA_MARKET_OPERATING_MODE_V1_CONTRACT.md`. FIRST family only (§10, §30): LIQUIDITY EVENT -> RECLAIM/FAILURE -> DISPLACEMENT -> FUTURE PATH. Information-first; conditioned on the pre-frozen mode; L/S separate; event-deduped; DISC/CONF; cross-era WITHIN same mode (§17); structural stop; no clones.

## Status
- **Cycle 1 (checkpoint #39):** MARKET_OPERATING_MODE_V1 FROZEN (6 modes, price-only causal H4, two-scale primary-vs-immediate; separates PRIMARY_BEAR from BULL_CORRECTION). Population stable + sufficient N all 5 eras; transition matrix confirms sticky primary backbone (corrections return to primary, not flip). NEXT = liquidity-event family.

## Liquidity-event decomposition (mandatory, §18): MODE base -> +EVENT -> +RECLAIM -> +RECLAIM+DISPLACEMENT
## Direction separate (§15): sellside event -> possible LONG ; buyside event -> possible SHORT
## Winner-vs-loser (§14): event+reclaim vs event+no-reclaim ; reclaim+displacement vs reclaim-only

## Liquidity-event decomposition — first cut (checkpoint #40)
`liquidity_event.py`. Mechanical M15 sweep (penetrate recent 20-bar swing) -> reclaim (close back inside) -> displacement (strong opposite body on reclaim bar). Decomposition MODE base -> +evt -> +rcl -> +disp, P(+70/-50) 8h, directed side, event-deduped, per era. Sources: b0/b1 hist, 2021/2022/2023 gated.
**Key finding (validates §13/§14):** the DISPLACEMENT component carries the information, NOT the raw sweep. +evt lifts small/inconsistent (~0); +disp adds the most (b0 BEAR_CORR sell +0.144, PRIMARY_BULL buy +0.070; 2021 PRIMARY_BEAR sell +0.144; 2023 PRIMARY_BEAR sell +0.075). The sweep alone is not the edge; the post-event displacement is.
**Two mode-conditional cross-era-consistent leads (b0+b1 same sign, disp-driven):**
| mode + event -> side | b0 +disp | b1 +disp | economic reading |
|---|---|---|---|
| BEAR_CORRECTION + sell-sweep+reclaim+disp -> L | +0.144 (n44) | +0.045 (n37) | bullish correction in bear: sweep lows + bull displacement -> corrective bounce continues up |
| BULL_CORRECTION + buy-sweep+reclaim+disp -> S | +0.064 (n37) | +0.046 (n31) | bearish pullback in bull: sweep highs + bear displacement -> pullback continues down |
Counter-trend cells (PRIMARY_BULL buy->S b0 +0.070 but 2023 -0.012) fail cross-era. b1 base rates low-vol-depressed (only relative lift comparable). Disp-level N small (31-44/era). LEADS not survivors.
**NEXT:** deepen the 2 correction leads — more eras (relaxed-N 2023), +100/-70 label, explicit winner-vs-loser (reclaim vs no-reclaim), event-N honesty (unique days/H4 episodes), then tradeability with structural stop.

## Two single-bar leads deepened — FAIL (checkpoint #41)
`liquidity_deepen.py`. §14 winner-loser + §18 labels/MFE-MAE + §20 event-N + §21-22 tradeability (structural stop = swept swing extreme).
| lead | b0 tradeable | b1 tradeable | freq | verdict |
|---|---|---|---|---|
| A: BEAR_CORRECTION sweep+reclaim+disp -> L | rr1.0 +0.136 (best10 +0.03) but SL only 23p (tight) | NEGATIVE (-0.10..-0.19) | ~2/mo | fails: b1 neg + tight stop + rare |
| B: BULL_CORRECTION sweep+reclaim+disp -> S | NEGATIVE (-0.21..-0.29) | marginal (rr2 +0.059) | ~2/mo | fails: b0 neg + rare |
**Problems:** (1) single-bar sweep+reclaim+displacement is RARE (~2 eff/mo; 6-23 raw events/yr gated); (2) structural stop = swept extreme is TOO TIGHT (16-30p med) when all 3 components on one M15 bar -> tight-stop fragility (§21); (3) NOT cross-era-robust within mode (A +b0/-b1, B -b0/+b1); winner-loser non-monotonic (reclaim-only often < base) = first-cut disp lift was small-N noise.
**Root cause = event FORMULATION, not necessarily the hypothesis:** the CEO sequence (sweep->reclaim->DISPLACEMENT->path) is inherently MULTI-BAR; collapsing onto one bar made it rare + tight-stopped. NEXT (one predeclared reformulation, §12-13, not mining): multi-bar liquidity SEQUENCE — sweep+reclaim on bar t, displacement over next K bars, entry after displacement confirms, structural stop at swept extreme (now with room), then re-test mode-conditional decomposition.

## Multi-bar sequence — REVERSAL branch NEGATIVE all modes cross-era (checkpoint #42)
`liquidity_seq.py`. Multi-bar sweep->reclaim->displacement (6-bar window), structural stop = swept extreme over sequence (healthy 20-41p), net STRESS per mode x side x era. Events plentiful (26-599). **Result: net-NEGATIVE in ALL 6 modes x both sides, cross-era.** Only positive cells = isolated single-era small-N outliers (BULL_CORR sell->L 2022 +0.45; TRANSITION short 2023 +0.08) that fail cross-era. The reversal reading of the liquidity mechanism carries NO tradeable edge. Multi-bar reformulation fixed frequency + stop-tightness but confirmed the reversal hypothesis is empirically false here (§14 "don't assume textbook"). NEXT (§14 mandatory): CONTINUATION/acceptance branch (sweep + NO reclaim + same-dir displacement -> continuation).
