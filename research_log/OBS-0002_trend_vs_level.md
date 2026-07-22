# OBS-0002 — Prior-day break-hold: level effect or trend-conditioning?
Type: Observation Record. **NOT a Discovery Candidate.** Date 2026-07-22 · XAUUSD H1 · replay_pre_cutoff / loader · 16,623 bars 2023-01→2025-10-23 · resolves OBS-0001 residue (NRQ-3).

**Q:** Is the prior-day break-and-hold "continuation" a LEVEL effect (holds in any regime) or TREND-conditioning (only when the break aligns with the EMA200 trend)?
**Pre-reg:** continuation-excess = s·(fwdK−driftK), s=+1 up/−1 down; level⇒>0 in all regimes incl. against-trend; trend⇒>0 only aligned. Falsify level if against-trend cells not >0.

**Result (bootstrap CI95):** At K=6 all four (dir×regime) cells have continuation-excess CI spanning 0 (means −0.75…+0.22). At K=12 means are positive but 7/8 CIs include 0 (only down-break/up-trend barely excludes, n=64, noisy). No cell robustly positive; alignment does not order the effect.

**Verdict: NEGATIVE — and it dissolves OBS-0001's residue.** The apparent break-hold "continuation" is neither a clean level effect nor cleanly trend-conditioned; it is drift+noise once split by regime with CIs. Prior-day-extreme break-hold has no robust H1 continuation mechanism.
**Residue:** none new. Strengthens confidence that prior-day-extreme *break* interactions carry little descriptive edge; attention shifts to *reject* interactions (OBS-0003) and non-level structure.
