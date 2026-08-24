# SESSION_LEDGER — SESSION_TIMING_LIQUIDITY_DISCOVERY_V1 (CEO 2026-08-24)

Do time-anchored session events create causal, repeatable, cost-surviving XAU opportunities price-only rules missed? Info-first;
DST-correct native-tz anchors (`session_tz.py`: London 08:00 Europe/London, US 08:30 & NYSE 09:30 America/New_York, LBMA 15:00
Europe/London — all DST-verified incl. UK/US offset-mismatch weeks). S5 frozen/read-only; DXY not used initially. cur_data M15 UTC.

## SF-1 ASIA→LONDON extreme interaction (`session_asia_london.py`) — NO directional information
Asia range frozen at London open (causal); first London-window interaction with an Asia extreme classified A(clean break/accept) vs
C(sweep+close-back) vs E(no interaction). 3,870 days, E=17%.
- **Continuation/reversal ~COINFLIP every type:** UPSIDE A-break P(cont)=0.494 / C-sweepback 0.503; DOWNSIDE A-break 0.505 / C-sweepback
  0.535. **Sweep+close-back does NOT add reversal info over a clean break** (upside rev 0.497 vs 0.506; downside C has LESS reversal,
  opposite the hypothesis). Deviations are single-era artifacts (downside C D=0.58 but C/O~0.49 — not stable).
- **MFE≈MAE (~3.0-3.5 ATR, symmetric), advFirst~0.49** — symmetric expansion, no directional edge (same pattern as price-only/VOLTIME).
- **VERDICT: Asia→London extreme interaction = no directional information; sweep refinement adds nothing; not cross-era-stable.**
  Consistent with the M05 session-extreme finding (extremes continue/coinflip, don't reverse). Next: US-participation families (08:30/
  09:30) where real catalysts live, and the London-lunch NO_TRADE / session-phase volatility structure (non-directional).

## SF-2 US 08:30 ET + NYSE 09:30 ET ORB (`session_us.py`) — no new directional edge
DST-correct macro/equity anchors (distinct from VOLTIME-4 fixed-UTC ORBs). 30-min OR breakout, 2R:1R, STRESS 0.24:
- US 08:30 ET: net −0.393 all eras (WR 0.282); RR3 −0.658. NYSE 09:30 ET: net −0.456 all eras (WR 0.261); RR3 −0.805. Tight OR whipsaws
  HARDER than the generic null (WR<0.33). Family-4: 08:30→09:30 move continues past 09:30 at P=0.510 (D0.52/C0.51/O0.50) = coinflip, no
  continuation info. **VERDICT: no tradeable directional edge at the US-participation anchors; S5's narrow NY-long config stays
  non-generalizable.** Consistent with VOLTIME-4. Next: family-5 session-phase opportunity structure (London-lunch NO_TRADE, non-directional).
