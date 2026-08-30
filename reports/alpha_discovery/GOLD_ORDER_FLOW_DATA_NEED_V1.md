# GOLD_ORDER_FLOW_DATA_NEED_V1 — dataset specification (GOLD_ORDER_FLOW_DISCOVERY_V1 §4)

Produced because usable GC data does NOT exist (see `GOLD_GC_DATA_AUDIT_V1.md`: only a 2-week MBO sample, 1 period, 42 XAU break
events in overlap, already tested negative). Per §4 the deliverable is a specification, NOT an acquisition — **STOP after this, CEO decides.**

## A. What the research question actually requires
Discriminate structurally-similar XAU events (continue vs fail) using **exogenous COMEX Gold futures order-flow information** that is
(a) causally available before the XAU decision, and (b) tested for a *stable, cost-surviving, independent-period* discriminator — the
same gate every prior frontier used (STRESS 0.24R, cross-era D/C/O, best-trade-removed, independent periods §21.6). The binding
constraint is **temporal coverage across independent regimes**, because a single period cannot falsify.

## B. MINIMUM VIABLE dataset (smallest that could support a valid candidate)
```
INSTRUMENT      = COMEX Gold futures GC, front-month, continuous contract
VENUE           = CME GLOBEX (Databento GLBX.MDP3 or equivalent governed feed)
ROLL_LOGIC      = volume/OI-based roll, explicit & documented; roll-adjusted continuous series + raw per-contract kept
DATE_RANGE      = >= 6 years continuous, spanning >= 3 independent regimes (must overlap the XAU eras D<=2018 / C19-22 / O23+)
TIMESTAMP       = event-time, microsecond, UTC, single clock shared with (or deterministically mappable to) the XAU M15 clock
FIELDS          = OHLCV bars at <=15m, WITH real futures volume + trade count
RESOLUTION      = 15m bars minimum (to align 1:1 with XAU M15 decisions)
TIMEZONE        = UTC (DST handled via zoneinfo, per session_tz.py)
SESSION_CALENDAR= CME holiday/half-day calendar (governed), to avoid phantom bars
VOLUME          = real contract volume (NOT tick count as a volume proxy)
CAUSAL_ALIGN    = GC bar usable at XAU decision t only if its close <= t (merge_asof backward, same discipline as the DXY contract)
GOVERNANCE      = committed governed dataset with a data contract + integrity gate (file-sha + timeline-sha), NOT a temp scratchpad
```
This minimum supports **volume/participation** discriminators (volume expansion, trade-count surge, GC-vs-XAU relative volume) but
**NOT** true order flow (no aggressor/bid-ask) — see §D for what that costs.

## C. IDEAL dataset (full order-flow discovery)
Everything in B, plus:
```
BOOK            = MBP-10 (10-level bid/ask depth) OR full MBO (message-level, book reconstructable) — bit-exact validated
AGGRESSOR       = ground-truth trade side (buy/sell initiated) OR MBO-reconstructed + §17 sensitivity-tested
DERIVED FLOW    = signed volume / order-flow imbalance, depth imbalance, sweep detection, absorption, delta — all causal (bars<=t)
OPEN_INTEREST   = daily OI (positioning context; distinguishes new-money breaks from short-covering)
COT (secondary) = CFTC Commitments of Traders, weekly, lagged-and-causal (positioning regime)
DATE_RANGE      = same >= 6y / >= 3 regimes at message level (the expensive constraint — MBO is large)
```

## D. What can be tested with each tier (§4 required analysis)
- **GC OHLCV + real volume only (tier B):** volume-expansion / trade-count-surge as an ex-ante discriminator for XAU break
  continuation; GC-vs-XAU relative-volume divergence; GC volume-timing (a futures analogue of VOLTIME-1). This is a *participation*
  signal, not order flow. It could confirm/deny whether *futures volume* carries the discriminator that *spot price* lacks.
- **Requires TRUE order flow (tier C):** aggressor imbalance at the break (are breakouts bought or sold into?), depth-absorption
  (is the level defended?), sweep-vs-genuine-break separation, delta divergence. These are the mechanisms most likely to hold the
  ex-ante discriminator the Contrast Miner proved is *absent from price* (`ALPHA_CONTRAST_MINER_REPORT_V1.md`).
- **Value LOST without bid/ask (§4):** cannot distinguish aggressive vs passive execution, cannot measure absorption/defense, cannot
  separate a liquidity sweep from a real break — precisely the winner/loser distinction that price-derived features could not make.
  Volume alone shows *how much* traded, never *who initiated* — so a volume-only study can only partially answer the mandate.

## E. Causal-alignment requirement with XAU
GC and XAU must share (or map to) one UTC clock; the GC feature at XAU decision t uses only GC bars closed <= t (backward `merge_asof`,
identical to the ratified DXY aligner). Lead/lag claims are timestamp-artifact-prone (§16) and must be validated on the shared clock,
never asserted. Roll dates must be excluded or flagged (structural discontinuity, not signal).

## F. Recommendation ranking (for the CEO's acquisition decision)
1. **Tier B first (min viable, 6y+ GC 15m OHLCV+volume, governed)** — cheapest, answers "does futures *participation* carry the
   discriminator price lacks?" If NO, order-flow (tier C) is unlikely to help and the exogenous priority reverts to **real yields**
   (the standing #1 DATA_NEED from `ALPHA_DISCOVERY_FACTORY_V2_REPORT.md` §19).
2. **Tier C (MBO/MBP-10, 6y+)** — only if tier B shows participation signal, or if the CEO wants the definitive order-flow answer.
   Expensive (message-level, multi-year); scope a 2-3 regime slice first, not full history.
3. Cross-check against the already-higher-ranked **real-yields** need — GC order flow and real yields are competing exogenous
   candidates; real yields is cheaper (daily/H1) and has a stronger prior (DXY-NDX1 stability traced to the real-yield regime).

## G. STOP
No acquisition is started here (§4). The 2-week sample is insufficient and already tested negative. Return control to CEO for the
buy/scope decision. `NEXT_AUTHORIZED_ACTION = NONE`.
