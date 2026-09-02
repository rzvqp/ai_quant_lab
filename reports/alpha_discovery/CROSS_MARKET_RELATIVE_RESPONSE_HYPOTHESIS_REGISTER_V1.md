# CROSS_MARKET_RELATIVE_RESPONSE_HYPOTHESIS_REGISTER_V1 — 20 raw → dedup 5 → tested → 0 survived

§6 deliverable. New variable = relative-response residual (XAU actual − DXY-implied), NOT the falsified simple DXY impulse (§4).
Screened against `ALPHA_NEGATIVE_KNOWLEDGE_BASE_V1` (DXY impulse alone / DXY up→gold down are Negative Knowledge).

## 20 raw → dedup
| ID | concept | dedup |
|---|---|---|
| X01 | DXY implied XAU move, XAU under-reacts → catch-up (long) | KEEP → **A** |
| X02 | mirror short | → A |
| X03 | XAU under-reacts → catch-up over next session | REJECT — = A horizon variant |
| X04 | DXY strong, XAU refuses to fall → XAU up continuation | KEEP → **B** |
| X05 | DXY weak, XAU refuses to rise → XAU down continuation | → B |
| X06 | XAU relative strength percentile → continuation | REJECT — = B normalization variant |
| X07 | XAU over-reacts vs DXY → fade | KEEP → **C** |
| X08 | XAU over-reacts → fade to expected | REJECT — = C |
| X09 | DXY displacement → XAU delayed repricing (lead-lag) | KEEP → **D** |
| X10 | fixed 1h/2h/4h lag repricing | REJECT — = D horizon variant |
| X11 | dislocation before London → London resolves | KEEP → **E** |
| X12 | dislocation before NY → NY resolves | → E |
| X13 | DXY+risk agree, XAU diverges (dual-confirm) | REJECT — **F, NO risk-market data** |
| X14 | DXY+risk conflict → XAU follows one | REJECT — F, no data |
| X15 | simple DXY impulse → implied dir | REJECT — Negative Knowledge (§4); used only as CONTROL |
| X16 | same-bar DXY/XAU correlation | REJECT — Negative Knowledge (§4) |
| X17 | DXY trend + XAU trend alignment | REJECT — = directional beta (R20) |
| X18 | rolling-beta regime switch | REJECT — parameter/regime mining |
| X19 | residual momentum (residual autocorrelation) | REJECT — folded into B |
| X20 | residual + XAU local structure confluence | REJECT — reintroduces price-only structure (mandate §0) |

20 raw → **5 distinct** (A catch-up, B relative-strength, C overshoot, D lead-lag, E session-resolution). F excluded (no risk-market data).

## Results
| family | net-R | vs impulse control | verdict |
|---|---|---|---|
| A catch-up | −0.084 | worse (control −0.069) | FALSIFIED |
| B relative-strength | −0.240 | far worse | FALSIFIED |
| C overshoot-fade | −0.125 | worse | FALSIFIED |
| D lead-lag | ≈ impulse control (−0.069), tested via t+1 entry + impulse ref | FALSIFIED |
| E session-resolution | −0.058 | ≈ control, both neg | FALSIFIED |

RAW=20 · DEDUPED=5 · TESTED=5 · FALSIFIED=5 · **SURVIVED=0.** `CROSS_MARKET_INCREMENTAL_INFORMATION_FOUND=NO` — the relative-response
residual does not beat the (already-negative) simple DXY impulse. Falsified subfamilies added to the Negative Knowledge Base.
