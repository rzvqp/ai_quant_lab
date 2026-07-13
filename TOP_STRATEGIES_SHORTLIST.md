# TOP_STRATEGIES_SHORTLIST — distinct candidates for FUTURE validation (NOT validated)

Deduplicated from 139 Research-Worthy → 22 distinct → this shortlist. Ranking uses **Codex's inline scoring
formula (TASK 3)** — expectancy weighted only 8%; penalties for negative-OOS, top-1 dependence, small-n,
cluster-redundancy, and long-only beta; hard exclusions fragile / n<20 / top1≥80% — reconciled with **Claude
methodology** and **Codex's TASK-5 final critique**. Nothing here is alpha; matched-null + global-FDR are CEO-gated.

## A. FACTS — Codex-formula score ranking (top 12 of 22)
| score | strategy | family | side | n | exp | PF | maxDD | OOS | top1 | cluster |
|---|---|---|---|---|---|---|---|---|---|---|
| 88.4 | S5 opening-range (ny/up) | S5 | long | 287 | .166 | 1.48 | 7.3R | +.18 | .02 | mom |
| 84.9 | S1 sweep long (low/swing) | S1 | long | 43 | .240 | 1.80 | 1.8R | +.29 | .09 | — |
| 80.8 | S29 Friday-up | S29 | long | 109 | .307 | 1.39 | 21R | +.20 | .06 | — |
| 78.8 | S1 sweep short (high/swing) | S1 | short | 47 | .021 | 1.68 | 1.1R | NA | .18 | — |
| 78.2 | S20 MTF-momentum breakout | S20 | long | 313 | .097 | 1.24 | 8.4R | +.17 | .01 | mom |
| 77.7 | S22 round-number $100 momentum | S22 | both | 223 | .082 | 1.12 | 22.5R | +.15 | .02 | — |
| 77.7 | S17 weekly pw_low reject | S17 | short | 137 | .142 | 1.21 | 18.9R | +.08 | .14 | — |
| 72.9 | S1 sweep long (low/pdh) | S1 | long | 316 | .057 | 1.10 | 11.2R | +.01 | .01 | — |
| 70.6 | S9 MTF align | S9 | long | 414 | .059 | 1.13 | 14.9R | +.20 | .01 | mom |
| 70.5 | S1 sweep short (high/pdh) | S1 | short | 241 | .017 | 1.03 | 22.8R | +.35 | .02 | — |
| 70.0 | S9 MTF any | S9 | long | 545 | .068 | 1.15 | 16.2R | +.10 | .01 | mom |
| 69.0 | S2 failed-breakout fade (low/pdh) | S2 | long | 268 | .060 | 1.08 | 23.9R | +.26 | .06 | — |

Full machine table: `kb_shortlist_scored.json`. "mom" = long-momentum correlation cluster (monthly-corr .6–.88, CI excludes 0).

## B. CLAUDE INTERPRETATION — reconciled shortlist (with Codex TASK-5 adjustments)
The raw score is corrected for two things it can't see per-candidate: **family-wise selection** (calendar) and
**cluster redundancy** (validate one momentum representative first). Applying that + Codex's TASK-5 calls:

**SHORTLIST (send to matched-null → global-FDR later), ~8 distinct economic bets:**
1. **S5 opening-range momentum (ny/up)** — top; exp .166, +OOS .18, positive every year, low DD. Distinct mechanism M03.
2. **S2 failed-breakout fade (low/pdh)** — distinct mean-reversion M04; +OOS .26.
3. **S1 liquidity-sweep SHORT (high/pdh)** — the only short; +OOS .35 (resolves one diversifier). M01.
4. **S1 liquidity-sweep long (low/swing)** — provisional/high-uncertainty (**n=43**); exp .24, +OOS .29. M01.
5. **Momentum-cluster representative — ONE of {S20, S9-any/align, S17-pwhigh-break, S39}** — pick MECHANICALLY
   (simplicity + effective-n + cost robustness), not by best score. Default: **S20 breakout** (n=313, dd 8R, +OOS .17). M05.
6. **S22 round-number $100 momentum** — distinct M06; +OOS .15.
7. **S1 liquidity-sweep long (low/pdh)** — *demoted to reserve per Codex* (OOS +.01 ≈ null). Include only if beta-adjusted.
8. **S17 weekly pw_low reject (short)** — *reserve* (OOS +.08 alone insufficient; keep for the short/level diversity).

**EXPLORATORY-ONLY (NOT shortlisted):**
- **S29 (Friday-up), S31 (month-start-short)** — calendar; high raw score is a **family-wise-selection artifact**
  (S29 tested 10 weekday×side combos; S31 OOS −.44). Do NOT validate as edges.
- **S39 efficiency continuation** — weak (+.02), variant-dependent (folded into the momentum-cluster question).
- **S6 session-transition, S8 VWAP-MR** — near-zero expectancy / mostly-negative family.
- **S1 high/swing** (n=47, OOS=NA), **S1 low/session** (fragile, excluded), **S14** (excluded, OOS −.14).

## C. CODEX INLINE REVIEW (TASK 5 verbatim positions)
- Agrees with the 8-shortlist shape and the calendar exclusion (family-wise selection invalidates candidate-level OOS).
- **DROP S1 low/pdh** (OOS +.01 ≈ null). **DEMOTE S17 pw_low** to reserve. **Keep S1 low/swing as exploratory/high-uncertainty** (n=43).
- Select the momentum representative **mechanically**, not by best score.
- Codex's stricter shortlist: **S5, S2, S1-short, S1-low/swing (provisional), one momentum rep, S22** (S17 reserve).

## D. CODEX FILESYSTEM REVIEW — PENDING (stale sandbox; could not read Tier-B files).

## Per-shortlist next-required-test
Every shortlisted strategy's next test is identical and singular (Codex TASK 5 + Claude): a **frozen,
direction/regime/time-of-day-matched null on untouched data, with ALL candidates and their variants in ONE
dependence-aware global-multiplicity (FDR) procedure, reporting beta-adjusted expectancy net of realistic costs.**
Until a strategy beats its matched gold-beta/null net of costs, it is NOT alpha. (CEO-gated.)
