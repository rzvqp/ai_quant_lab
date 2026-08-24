# ALPHA_M15_SESSION_MAP

Mandate `ALPHA-XAUUSD-M15-CAUSAL-STATE-PATH-DISCOVERY-001`, §13 (last untested family). Session-conditioned M15, P(+70/-50) 8h, measured vs SESSION base, event-deduped, cross-era b0/b1 (`state_m15_session.py`). Sessions UTC: Asia 0-7, London 7-13, NY 13-21, Off 21-24. DEV global base L 0.276 / S 0.265.

## (1) Session structural bias (vs global base)
| session | N | L lift (b0/b1) | S lift (b0/b1) | read |
|---|---|---|---|---|
| Asia | 1552 | -0.006 (−.01/−.02) | -0.006 (+.01/−.04) | flat |
| **London** | 1331 | **+0.086 (+.07/+.06)** | **+0.126 (+.09/+.09)** | **BILATERAL range-expansion, cross-era-stable; small consistent SHORT tilt (~+0.04)** |
| NY | 1764 | -0.045 (−.02/−.02) | -0.068 (−.06/−.02) | mild bilateral depress |
| **Off (21-24)** | 435 | **-0.058 (−.07/−.05)** | **-0.088 (−.06/−.06)** | **stable AVOIDANCE filter (dead-zone, ±70 rarely reached)** |

## (2) Session-open first hour (vs that session's base)
| session | N | L lift (b0/b1) | S lift (b0/b1) | read |
|---|---|---|---|---|
| **NY open** | 220 | **+0.173 (+.05/+.02)** | **+0.162 (+.12/+.10)** | **strong BILATERAL burst, cross-era = volatility-TIMING signal (biggest ±70 reach)** |
| London open | 220 | +0.061 | -0.069 | mild, not cross-stable |
| Asia/Off open | 223/95 | neg | neg | quiet opens |

## (3) high/rising-vol -> SHORT concentration (vs that session's SHORT base)
| session | N | short lift (b0/b1) | verdict |
|---|---|---|---|
| Asia | 720 | -0.003 (−.00/+.01) | none |
| London | 920 | +0.027 (+.02/−.00) | marginal, b1 fails |
| **NY** | 938 | **+0.070 (+.08/+.05)** | **S_CROSS_STABLE — the ONE directional signal that survives b1** |
| Off | 38 | thin | — |

**Central finding:** session context DOES add cross-era-stable STRUCTURE to M15 path odds — but the structural findings (London/NY-open bilateral lift) are RANGE-EXPANSION / volatility-TIMING (both sides reach ±70 more), not directional alpha by themselves; the Off dead-zone is a stable avoidance filter. The ONE directional cross-era-stable candidate is **NY-session high-vol -> M15 SHORT** (+0.070, b0 +0.08 / b1 +0.05) — the first time the high-vol-short information survives the b1 gate, because SESSION conditioning (NY volatility bursts) captures the mechanism where DOWN-PARENT conditioning did not. => earns a tradeability characterization (next).
