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

## SF-3 SESSION-PHASE opportunity structure (`session_phase.py`) — cross-era-stable NON-DIRECTIONAL finding (valid NO_TRADE map)
Session-relative phases (DST-correct), forward K=8b=2h non-directional metrics, per era. ALL phases cross-era-STABLE (D/C/O nearly identical).
- **Whipsaw (both ±1ATR within 2h = chop) varies ~5x by phase, stable:** US_SESSION post-09:30 = **0.088 (cleanest/most trending)**;
  London-AM 0.161; LATE 0.136; **pre-US/London-lunch 0.424 and US-MACRO 0.383 (choppiest)**. fwdRange/P(move): macro-window high
  (5.1/0.93 — but forward-window leaks into the 08:30 explosion) vs US-session low (2.36/0.51 — clean but quiet).
- **Reading:** the pre-US/macro window is HIGH-expansion but HIGH-whipsaw (breakout NO_TRADE zone — explains why 08:30/09:30 ORB failed);
  the US cash session is LOW-whipsaw/clean (where S5 lives) but low expansion; London-AM has the best clean-expansion ratio (0.71 P(move)
  at 0.16 whipsaw). **This is a valid cross-era-stable NON-DIRECTIONAL session-timing discovery (a whipsaw/NO_TRADE map)** — useful as
  CONTEXT/filter, NOT a standalone tradeable edge (direction still the binding constraint; the underlying directional mechanisms fail).
  Consistent with the campaign: session-TIMING supplies real non-directional structure (like VOLTIME, DXY-NDX1) but no standalone
  directional edge beyond S5's narrow config. Next: LBMA PM benchmark (family-6) + synthesis.
