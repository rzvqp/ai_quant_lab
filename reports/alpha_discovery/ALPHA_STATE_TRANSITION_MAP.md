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

## Transition screen results (2021-2023 H1 DEV, headline P(+100/-70) H48, stability built-in)
9 transitions x 2 sides screened with per-year + DISC/CONF stability IN the screen (`state_transitions.py`).
| transition | side | lift | DISC | CONF | per-year | verdict |
|---|---|---|---|---|---|---|
| T3 upEff->drop | L | -0.069 | -0.088 | -0.041 | 2021 -0.054 / 2023 -0.099 | **STABLE (LONG-avoidance filter)** |
| T3 upEff->drop | S | +0.048 | -0.004 | +0.115 | 2021 -0.065 / 2023 +0.135 | UNSTABLE (2023-only, DISC~0) |
| T9 trend_weaken | S | +0.029 | +0.091 | **-0.075** | 2021-22 +, 2023 ~0 | UNSTABLE (DISC->CONF inversion; 2021-22 transient) |
| T5 accept_up | L | +0.050 | -0.010 | +0.146 | 2021 -0.072 / 2023 +0.135 | UNSTABLE (2023-only, DISC neg) |
| T8 flip_up->dn | S | +0.059 | +0.078 | +0.030 | only 2023 has N | INSUFFICIENT (N=91, single-year) |
| T1/T2/T4/T6/T7 | L/S | <\|0.06\| | mixed | mixed | mixed | not stable |
**Conclusion:** the ONLY stable transition signal is `T3 up-efficiency->drop` = a LONG-AVOIDANCE filter (stable -0.069), NOT a standalone positive edge; and it re-encodes "trend-drive presence" (which COMP-CONT-L already exploits). No stable POSITIVE tradeable path-lift from the transition family. Every apparent positive is a 2021-22 or 2023-only regime transient (same failure mode as ST-TREND-EXH). PIVOT to the next state family: PATH-HISTORY states (MFE/MAE-so-far before decision) + multi-TF / session-conditioned states.
