# ALPHA_CAUSAL_MORPHOLOGY_CONTRACT (+ feature dictionary + multiplicity ledger)

Mandate `ALPHA-XAUUSD-CAUSAL-MORPHOLOGY-DISCOVERY-001`: discover recurring event archetypes from CAUSAL price morphology (no future/P&L in discovery), freeze, THEN measure forward path. Move from hand-authored hypotheses to discovered events.

## Method (firewall-respecting; §1/§4/§8/§10)
1. **Causal features** (`morph_features.py`, event-time, ATR-normalized, NO future info): 10-D bounded dictionary (below).
2. **Fit z-norm + KMeans (K=12, reproducible seed 7)** on the **DISC era = b0+b1 (2011-2018)** only.
3. **FREEZE** centroids + normalization; assign ALL eras to the frozen archetypes (`morph_discover.py`, `morph_space_htf.py`).
4. **Stability BEFORE outcome** (§6): occupancy per era → STRUCTURALLY_RECURRENT vs ERA_SPECIFIC.
5. **Novelty gate** (§7): interpret each centroid → KNOWN_MECHANISM / GENUINELY_NEW / UNCLEAR vs S1-S51 + A-J + Radar + S5 + RANGE.
6. **THEN forward path** (§9): P(+X/-Y) L/S first-passage (`state_path_m15`), asym70 = P(+70/-50 L)−P(+70/-50 S), cross-era.
7. **Promotion**: RECURRENT + material (|asym|≥0.05) + cross-era same-sign (all eras N≥40) + NOVEL → freeze + S5-independence + strategy conversion (STRESS cost). No RR/stop mining.

## Feature dictionary (10-D, causal, interpretable — §16 no feature soup), lookback K=8 bars
| feature | definition (causal) | class |
|---|---|---|
| disp | (c − c[−K]) / atr | net displacement |
| effic | (c − c[−K]) / Σ\|Δc\| over K | directional efficiency (persist vs alternate) |
| pathlen | Σ\|Δc\| over K / atr | distance travelled |
| hi_pos | argmax(high) position in window /(K−1) | extreme location/ordering |
| lo_pos | argmin(low) position /(K−1) | extreme location/ordering |
| rng_trend | mean range recent-half / older-half | expansion vs contraction |
| body_frac | mean\|c−o\| / mean range over K | body vs wick |
| alternation | fraction of return sign-changes over K | alternation vs persistence |
| retr | (window extreme − c)/atr in disp direction | retracement depth |
| vol_state | atr / atr_ma | volatility regime |

## Temporal scales searched (§3) — separate morphology spaces
- **Space A** = M15 short structure (K=8 bars=2h), forward 48 bars (12h).
- **Space B** = H1 short structure (K=8=8h), forward 24 bars (1 day).
- **Space C** = H4 short structure (K=8=32h), forward 12 bars (2 days).
Multi-day/session unsupervised morphology = future spaces if warranted (hand-authored versions already bounded: Batch D/E/J).

## Multiplicity ledger (morphology)
- Spaces run: A(M15), B(H1), C(H4) bar-structure (K=12 each) + D(session-geometry, K=10). 1 clustering fit per space (DISC=b0+b1). Total 46 archetypes examined. Fixed seed(7), fixed K, fixed feature set, DISC-only fit — all preserved. 0 promoted to strategy.
- No re-fit after seeing forward paths (no post-hoc redesign; §10). Any future re-fit = new identity + new ledger entry.

## Governance
Price-only XAUUSD; authorized frames only (hist_m15_data/hist_data b0/b1 2011-2018 + swing_base gated DEV/CAL 2021-2024); no 2025+, no exogenous, no legacy D1 features, no protected/sealed. RANGE vNext / Market Mode = optional descriptors only (not used in Space A/B/C base run; both frozen).
