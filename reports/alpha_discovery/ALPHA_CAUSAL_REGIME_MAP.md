# ALPHA_CAUSAL_REGIME_MAP

Mandate `ALPHA-XAUUSD-REGIME-CONDITIONAL-STATE-PATH-DISCOVERY-001`. A small, interpretable, CAUSAL, price-only regime taxonomy — FROZEN before any path outcome (§3, §28). NOT P&L-defined; NOT canonical RANGE (§6 — `QUIET` is a research-local low-vol-neutral label, distinct from canonical RANGE). Regime known at each H1 bar close.

## Frozen taxonomy (`state_regime.py::regime`, priority QUIET>UP>DOWN>CHOP>TRANSITION)
Features (all causal): `eff`=directional efficiency(20); `trend`=(EMA20-EMA50)/ATR; `vr`=ATR/ATR_ma(30).
- **UP**: eff>0.35 AND trend>0.2 (persistent directional up)
- **DOWN**: eff<-0.35 AND trend<-0.2 (persistent directional down)
- **QUIET**: vr<0.9 AND |eff|<0.25 (low-vol neutral; research-local, NOT canonical RANGE)
- **CHOP**: |eff|<0.25 and not QUIET (neutral, normal/high vol)
- **TRANSITION**: everything else (directional separation w/o efficiency, or efficiency w/o separation, or high-vol mixed)

## Reproducibility (§8) — the regimes RECUR near-identically across all eras (NOT "year 2022")
| regime | DEV 2021-23 | 2021 | 2022 | 2023 | b0 2011-13 | b1 2016-18 |
|---|---|---|---|---|---|---|
| UP | 13.3% | 12.7 | 15.0 | 13.0 | 12.1 | 13.3 |
| DOWN | 9.9% | 8.4 | 9.4 | 10.7 | 11.9 | 11.6 |
| QUIET | 24.6% | 23.7 | 24.0 | 25.2 | 24.4 | 23.2 |
| CHOP | 32.4% | 34.2 | 29.4 | 32.5 | 29.0 | 31.3 |
| TRANSITION | 19.6% | 20.3 | 22.2 | 18.6 | 22.4 | 20.6 |
**Every regime occurs 8-34% in EVERY era** — a genuinely reproducible, contemporaneous, causal taxonomy. Crucially **DOWN recurs in all eras (b0 11.9% / b1 11.6%)**, enabling same-regime cross-era SHORT validation. Episodes are frequent (hundreds per era) -> adequate independent occurrences.
