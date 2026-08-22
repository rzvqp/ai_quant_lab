# ALPHA_STATE_TRANSITION_MAP

State TRANSITIONS that alter forward path (§8). Stage-A univariate done; transition mapping is the next cycle.
Queued transitions to test (causal, pre-entry):
- extension-up -> vol-contraction (exhaustion + stalling) : does the SHORT path sharpen vs static extension?
- rising-vol -> falling-vol (expansion -> stabilization) in the trend direction.
- high-efficiency -> efficiency-drop (trend losing drive) : SHORT setup?
- neutral -> directional acceptance (effic crossing a stable region).
(None assumed to work; searched systematically, base-rate lift required.)

## Cycle note (post ST-TREND-EXH kill)
Static-state univariate winner (trend-extension) failed stability (DISC->CONF inversion; no cross-pop generalization). Transitions are now the priority family (§8). Next cycle: build a transition screen (state A at t-k -> state B at t) with the SAME first-passage path outcome + DISC/CONF + cross-population from the outset (skip straight to the stability test for any transition that shows univariate lift, to avoid another in-sample-only candidate).
