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
