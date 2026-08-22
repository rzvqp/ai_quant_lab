# ALPHA_STRUCTURAL_EVENT_MAP

Mandate `ALPHA-XAUUSD-HIERARCHICAL-MODE-STRUCTURAL-EVENT-DISCOVERY-001`. Architecture: H4 MARKET MODE + H1 context + M15 structural EVENT + POST-EVENT RESPONSE -> future path -> SPECIALIST strategy. Market modes frozen in `ALPHA_MARKET_OPERATING_MODE_V1_CONTRACT.md`. FIRST family only (§10, §30): LIQUIDITY EVENT -> RECLAIM/FAILURE -> DISPLACEMENT -> FUTURE PATH. Information-first; conditioned on the pre-frozen mode; L/S separate; event-deduped; DISC/CONF; cross-era WITHIN same mode (§17); structural stop; no clones.

## Status
- **Cycle 1 (checkpoint #39):** MARKET_OPERATING_MODE_V1 FROZEN (6 modes, price-only causal H4, two-scale primary-vs-immediate; separates PRIMARY_BEAR from BULL_CORRECTION). Population stable + sufficient N all 5 eras; transition matrix confirms sticky primary backbone (corrections return to primary, not flip). NEXT = liquidity-event family.

## Liquidity-event decomposition (mandatory, §18): MODE base -> +EVENT -> +RECLAIM -> +RECLAIM+DISPLACEMENT
## Direction separate (§15): sellside event -> possible LONG ; buyside event -> possible SHORT
## Winner-vs-loser (§14): event+reclaim vs event+no-reclaim ; reclaim+displacement vs reclaim-only
