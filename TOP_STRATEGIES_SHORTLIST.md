# TOP STRATEGIES SHORTLIST — workstream B (branch strategy-development, baseline 1bc0ffb)

Candidates for FUTURE matched-null (Test B) + global-FDR validation. **Nothing here is validated or
significant.** In-sample research metrics; OOS (validation segment) shown separately; holdout SEALED.
Long-book drift caveat applies throughout (see STRATEGY_DEVELOPMENT_REPORT §0).

## A. Two independent recommendations (Etapa 7)

### A1. Registry / mechanical recommendation (automated robustness_score — the "Codex-role" technical pass)
All 11 research-candidates, ranked by transparent robustness_score (stability + neighbour-robustness +
log n − top1 − dd − |OOS clip|):
1. S5/ny/up (2.14) 2. S9/any (1.76) 3. S9/align (1.51) 4. S20/breakout (1.34) 5. S17/pw_high/breakout (1.34)
6. S1/low/swing (1.26) 7. S1/low/pdh_pdl (1.22) 8. S2/low/pdh_pdl (1.18) 9. S6/london/fade/down (1.16)
10. S1/high/pdh_pdl SHORT (1.06) 11. S8/vwap/up (0.78).

### A2. Claude economic-verification recommendation (re-tiered on yearly stability, OOS, drift, redundancy)
- **TIER 1 — send to matched-null first (distinct mechanism, best evidence):**
  1. **S5 / ny / up** (opening-range momentum). n=287, exp .166, PF 1.48, DD 7.3R, positive EVERY year, OOS +0.179.
  2. **S2 / low / pdh_pdl** (failed-breakout FADE — mean reversion, not momentum). n=268, exp .060, OOS **+0.256** (best OOS).
  3. **S1 / high / pdh_pdl** (liquidity-sweep reversal, **SHORT** — the only short; the one resolved diversifier). n=241, OOS **+0.346**.
- **TIER 2 — test, but expect drift-beta / represents a cluster:**
  4. **S9 / c4h=up / any** — MTF-momentum, the single representative of the long-momentum cluster (see below). n=545, OOS +0.10.
  5. **S1 / low / pdh_pdl** (liquidity-sweep reversal, long). n=399, improving, OOS −0.06 (in-sample only).
- **TIER 3 — registry only / low priority (redundant, one-year, or OOS-negative):**
  S9/align & S20/breakout & S17/pw_high/breakout (redundant with S9/any, r 0.6–0.71 — do NOT test all four);
  S1/low/swing (yearly unstable, OOS≈0); S8/vwap (2022-only); S6/london/fade (entire edge in 2022).

## B. Agreements & disagreements
**Agree:** S5 is the top candidate; S2 (mean-reversion) is a genuine non-momentum bet; the S1 SHORT is a
valuable diversifier; the 6 fragile candidates are excluded.
**Disagree (Claude overrides the mechanical score):**
| candidate | mechanical | Claude | reason |
|---|---|---|---|
| S6/london/fade | shortlisted (1.16) | **drop** | entire edge is 2022 (1.86R); 2023-25 ≈ 0 |
| S8/vwap/up | shortlisted (0.78) | **drop** | 2022-only; negative 2023 & 2025 (top-year conc 1.97) |
| S9/align, S20, S17/pw_high | 3 distinct | **merge into S9/any** | correlate r 0.6–0.71 → one bet |
| S17/pw_high/breakout | rank 5 (1.34) | **demote** | high in-sample exp but OOS **−0.086** |
| S1/low/swing | rank 6 | **demote** | yearly −.73/.12/.08/−.08 unstable; OOS ≈ 0 |

**Note on Etapa 7:** the independent Codex live session (mcp__codex) **timed out (infra)** this session, so the
"mechanical" column above is the automated registry/robustness output (the technical role Codex was assigned,
executed by `stratdev_registry.py`) rather than a separate Codex opinion. **CEO decision: retry an independent
Codex review, or accept the automated-registry-vs-Claude dual view as sufficient.**

## C. Distinct economic mechanisms represented (the real answer)
After dedup (130→17) AND correlation-based cluster collapse, **~6–7 truly distinct economic bets** remain:
1. **Opening-range momentum** (S5) — intraday breakout of the session's first range.
2. **Failed-breakout fade / mean-reversion at prior-day levels** (S2) — contrarian.
3. **Liquidity-sweep reversal, LONG** (S1 low/pdh_pdl) — sweep prior-day low, reverse up.
4. **Liquidity-sweep reversal, SHORT** (S1 high/pdh_pdl) — sweep prior-day high, reverse down.
5. **MTF trend-continuation / momentum** (S9/any ≈ S20 ≈ S17-breakout cluster) — buy strength aligned with HTF trend.
6. **(probe) Extension mean-reversion vs VWAP** (S8) — fragile, keep as a low-priority MR probe.
(Opening-range and MTF-momentum are both "momentum" but at different horizons/triggers; kept separate.)

## D. Final answers to the CEO's 8 questions
1. **Duplicates among 130 RW:** 113 (87%).
2. **Distinct real strategies:** 17 by mechanism → **~6–7** after correlation de-redundancy.
3. **Top shortlist (11 registry / 5 Claude-prioritized):** see A1/A2; Tier-1+2 = S5, S2, S1-short, S9-momentum-rep, S1-long.
4. **Families represented:** S1, S2, S5, S6, S8, S9, S14, S17, S20 (9 with RW); exploratory S3/S13/S16/S18/S19.
5. **Distinct economic mechanisms:** the 6 in §C.
6. **Fragile strategies:** S1/high/swing, S1/low/session, S17/pw_low/reject, S17/pw_high/reject, S14/down,
   S6/ny/breakout (+ downgraded S6/london/fade, S8/vwap).
7. **Redundant strategies:** the long-momentum cluster S9/align + S20 + S17/pw_high ≈ S9/any; and all 113
   collapsed tuning duplicates.
8. **What to send to matched-null / global-FDR next:** the deduped, cluster-collapsed distinct set —
   **S5/ny/up, S2/low/pdh_pdl, S1/low/pdh_pdl (long), S1/high/pdh_pdl (short), S9/any (momentum rep)**, plus
   optionally the S8 MR probe. These form the eligible candidate set for Test B **once matched-null is
   validated** (other branch); then global-FDR over the frozen eligible universe. **Do not test the four
   correlated momentum variants separately.**

## E. Hard limits (unchanged)
No significance claimed. No parameters tuned. No holdout opened. No engine/screen change. Matched-null must be
validated first (separate branch, in progress). Portfolio Architect stays deferred (correlations too uncertain).
