# ALPHA_XAUUSD_FRANKFURT_LONDON_FALSE_DRIVE_SHORT_REPORT

**Mandate:** `ALPHA-XAUUSD-FRANKFURT-LONDON-FALSE-DRIVE-SHORT-001` (+ CEO 4-class addendum) · **Date:** 2026-08-22.
**Terminal statuses:** `FRANKFURT_FALSE_DRIVE_DISCOVERY_COMPLETE` · **`NO_ROBUST_FRANKFURT_SHORT_SIGNAL_FOUND`** ; `LONDON_FALSE_DRIVE_DISCOVERY_COMPLETE` · **`LONDON_SHORT_SIGNAL_WEAK`**.
**Scope:** NEW independent SHORT family; price-only XAUUSD; native-M5 primary; DST-aware; DEV-only; no CALIB/V1/2025+/N4/execution. Two families kept **separate**. ≤16 signal IDs (3 sub-populations + ladder + anatomy), 0 promoted, 1 WEAK candidate for audit. No promotion; broker disabled.

---

## 0. Headline
- **Liquidity-level is the decisive variable (§35.Q3):** sweeping the **Pre-London-High** during London open produces a **clean bearish reversal (class A) 3× more often than sweeping Asia High** — P(A) 0.368 vs 0.106 (Frankfurt) / 0.119 (London/Asia-High) — and it is **stable across all three years** (0.41/0.38/0.34).
- **But the "false-drive → clean short" narrative is falsified for Asia-High:** the Frankfurt and London Asia-High families are dominated by **B (new-high-first) + C (continuation)** — the *right-direction-bad-path* case the CEO warned about. Frankfurt: A 0.11 / B 0.47 / C 0.42.
- **The Pre-London-High edge is a LEVEL finding, not a path-clean solution:** P(A) 0.37 still means 63% are non-clean (B 0.28, C 0.35), ~22p room, and **no early E1/E2 anatomy discriminator generalizes** to raise it (small undecided-N, DISC↔CONF sign-flips). Hence **WEAK, not READY**.

## 1. Artifact lineage + firewall (§2)
Independent of EARLY-TRAP-E1 / POST-E1-CLEAN-P2 / S2 / S4 (all frozen, untouched). Native M5 (121,949 DEV bars, 2021-07-27→2023-12-29). Asia levels from canonical M15 (00:00–07:00 UTC). No synthetic M5, no N4, no CALIB/V1/2025+.

## 2. Timezone + DST verification (§3, §30) — passed
DST-aware via `tz_convert`. Audit across EU transitions: Berlin = London + 1h **year-round**; London +1:00 summer / 0:00 winter; Berlin +2:00 / +1:00; verified on 2022-03-27 (spring), 2022-10-30 (fall), winter, summer. No fixed-offset leak. **Asia-complete gate (`utc_hour ≥ 7`) enforced** so no European sweep uses an incomplete Asia range — this trims summer early-Frankfurt (where London 07:00 = 06:00 UTC), documented rather than hidden.

## 3. Session windows (frozen before outcomes, §5)
| family | window (local) | UTC behavior | Asia-complete gate |
|---|---|---|---|
| **F** Frankfurt/early-Europe | London 07:00–08:00 (Berlin 08:00–09:00) | 07–08 UTC winter / 06–07 UTC summer | `utc≥7` (summer-trimmed) |
| **L** London open | London 08:00–10:00 | 08–10 UTC winter / 07–09 UTC summer | `utc≥7` |
Windows disjoint (London 07–08 vs 08–10) → **deterministic event ownership** (§29), no double-count. L/Asia-High and L/Pre-London-High are **separate identities** on the same window (§19).

## 4. Level construction (§6, §7)
- **Asia High/Low/mid:** canonical M15, 00:00–07:00 UTC, ≥12 bars, complete at 07:00 UTC.
- **Pre-London-High:** max native-M5 high over London 07:00–08:00 (Frankfurt hour), same day — causal, known before London open (08:00). No future bars.

## 5. Parent sweeps (§8) — first M5 `high > L` (strict) in window
| sub-population | parent N | unique days |
|---|---|---|
| F / Asia-High | 66 | 66 |
| L / Asia-High | 176 | 176 |
| L / Pre-London-High | 133 | 133 |

## 6. Addendum 4-class distribution (§4, §12) — the primary result
Frozen sweep_hi = high[E0]; objective = Asia mid; horizon 48 M5 (4h), same-day; classes mutually exclusive, labels only.
| sub-population | N | **A clean** | **B newhi-first** | C continuation | D stalled | P(mid) | P(Asia low) | med remaining |
|---|---|---|---|---|---|---|---|---|
| **F / Asia-High** | 66 | **0.106** | 0.470 | 0.424 | 0.000 | 0.576 | 0.197 | 32p |
| **L / Asia-High** | 176 | **0.119** | 0.295 | 0.568 | 0.017 | 0.415 | 0.108 | 37p |
| **L / Pre-London-High** | 133 | **0.368** | 0.278 | 0.346 | 0.008 | 0.647 | 0.271 | 22p |
*(P(new-high full-horizon) ≈ 0.90 for all — but that counts new highs made **after** the objective is reached; the A/B/C/D classes use new-high-**before**-objective, the correct path metric. A short that reaches the mid first (A) is unaffected by a later high.)*

## 7. Sweep anatomy / failed acceptance / bearish response (§8–§13) — same-parent controls
**Failed-acceptance (close back below L by E2) vs sustained-acceptance, P(A clean):**
| sub-population | failed-accept n / P(A) | sustained n / P(A) | same-parent incr |
|---|---|---|---|
| F/Asia-High | 51 / 0.137 | 15 / 0.000 | +0.137 |
| L/Asia-High | 126 / 0.167 | 50 / 0.000 | +0.167 |
| L/Pre-London-High | 94 / **0.404** | 39 / 0.282 | +0.122 |
Failed-acceptance adds same-parent information (sustained-acceptance → P(A)≈0 for Asia-High: if price holds above, it never cleanly reverses). **Bearish E1/E2 response and failed-extension do NOT robustly discriminate** (§8, next).

## 8. Early anatomy discrimination (§9, §23) — does NOT generalize (why WEAK)
On the best family (L/Pre-London-High), predicting class A among **undecided-at-E1** (n=39; DISC 21 / CONF 18; ~34p remaining): candidate features **sign-flip between DISC and CONF** — net_prog 0.31/0.85, last_bear 0.31/0.85, failed_ext 0.70/0.25 (E2 last_bear 0.95/0.48). The undecided subset is too small to learn a stable A-vs-not-A anatomy. Simple rule (net downside>0 AND close-below-PLH): DISC P(A) 0.167 (**−0.119**), CONF 0.286 (+0.008) — **no generalizing lift.** Unlike POST-E1-CLEAN-P2 (n=86 undecided, stable AUC 0.77), here N is insufficient.

## 9. Attack velocity, first-vs-repeat (§13, §14)
Velocity/acceleration and first-vs-repeat (counted correctly — only attacks **after** the level is frozen, avoiding the `prior_attacks()` defect) were characterized but not advanced: the parent families are already path-dominated (F/L-AsiaHigh) or lack a generalizing sub-discriminator (L-PLH). No robust incremental information.

## 10. DISCOVERY/CONFIRMATION + temporal (§21, §26, §27) — the stable finding
The **level effect is temporally robust**: L/Pre-London-High P(A) = 2021 0.407 (n27) / 2022 0.383 (n47) / 2023 0.339 (n59) — consistent ~0.34–0.41 across all authorized years (partial-2021 from 2021-07). Asia-High families are uniformly weak across years (F 0.07/0.14/0.10; L 0.11/0.15/0.11). No single year dominates the level finding.

## 11. Remaining-distance economics (§17, §31)
L/Pre-London-High median remaining to mid ~22p (closer level → less room than Asia-High's 32–37p). Downside MFE: ≥20p 0.65, ≥30p 0.54, ≥50p 0.33, ≥80p 0.17, ≥100p 0.05, ≥150p 0.02 — natural move is **small session mean-reversion**, not large continuation. Asia Low reached 0.271.

## 12. Candidate table (addendum §12)
| candidate | N | P(mid) | **P(A clean)** | **P(B newhi-first)** | P(C) | P(D) | med remaining | med dist-to-sweep | DISC/CONF (P(A)) | 2021/22/23 P(A) |
|---|---|---|---|---|---|---|---|---|---|---|
| **`LONDON-PREMARKET-HIGH-FALSE-DRIVE` (WEAK)** | 133 (94 failed-accept) | 0.647 | 0.368 (0.404) | 0.278 | 0.346 | 0.008 | 22p | — | stable (~0.37 both) | 0.41/0.38/0.34 |
| F/Asia-High (graveyard) | 66 | 0.576 | 0.106 | 0.470 | 0.424 | 0.000 | 32p | — | weak | 0.07/0.14/0.10 |
| L/Asia-High (graveyard) | 176 | 0.415 | 0.119 | 0.295 | 0.568 | 0.017 | 37p | — | weak | 0.11/0.15/0.11 |

## 13. Family F answers (§34) — brief
1 ~66 days sweep Asia-High in the Frankfurt hour · 2 77% return below · 3 return-below adds +0.137 same-parent · 4–6 bearish/extension/velocity anatomy **not** robust · 8 P(mid) 0.576 · 9 P(low) 0.197 · 10 **89% make a new high before mid-or-never (B+C)** · 11 ~32p remaining · **12 NO robust Frankfurt SHORT (P(A) 0.11).**

## 14. Family L answers (§35) — brief
1 176 Asia-High sweeps · 2 133 Pre-London-High sweeps · **3 Pre-London-High far more informative (P(A) 0.37 vs 0.12)** · 4 failed-acceptance matters (+0.12 same-parent) · 5–7 bearish/velocity/extension **not** robust (small-N sign-flip) · 8 London/PLH ≠ Frankfurt/AH; London/AH ≈ Frankfurt/AH · 9 natural target = **Asia-mid session mean-reversion** (P(mid) 0.65; large continuation rare) · **10 WEAK London Pre-London-High false-drive signal.**

## 15. Comparison (§36)
L/Pre-London-High **> both Asia-High families** on P(A clean) and temporal stability, with adequate parent N (133). Chosen on generalization + N, not headline WR. But its P(B) 0.28 and ~22p room mean it is a **modestly-better level, not a path-clean edge.**

## 16. Graveyard + limitations (§28)
- **Graveyard:** Frankfurt/Asia-High and London/Asia-High false-drives (bad-path-dominated); all early E1/E2 anatomy discriminators for L/PLH (DISC↔CONF sign-flips); the net-downside+close-below rule (no lift). Recorded in `frank_london.py` / `frank_london2.py`.
- **Limitations:** the WEAK candidate rests on a **level** effect (Pre-London-High) with P(A) 0.37 (63% non-clean), ~22p room, no surviving anatomy refiner; undecided sub-N tiny (39). Native-M5 starts mid-2021 (partial-2021, dated). No execution tested (§32).

## 17. CEO recommendation
1. **`NO_ROBUST_FRANKFURT_SHORT_SIGNAL_FOUND`** — the Frankfurt/early-Europe Asia-High raid is overwhelmingly *right-direction-bad-path* (A 0.11 / B 0.47 / C 0.42); it does not contain a clean-reversal short.
2. **`LONDON_SHORT_SIGNAL_WEAK`** — the one genuine, price-only, temporally-stable finding is the **liquidity-LEVEL** result: a London-open sweep of the causal **Pre-London-High** cleanly reverses (class A) 0.37–0.40 of the time — **3× the Asia-High families** and consistent across 2021/2022/2023. Candidate `LONDON-PREMARKET-HIGH-FALSE-DRIVE`. **But it is WEAK, not READY:** it reduces the new-high-first problem versus Asia-High yet does not solve it (P(B) 0.28), retains only ~22p room, and **no early anatomy discriminator generalizes** to sharpen it. **Recommend independent Statistician audit of the Pre-London-High level effect** (the same gate EARLY-TRAP-E1 passed) before any deeper work.
3. **The most defensible reading:** *which liquidity level is swept* matters more than *how* it is swept — Pre-London-High (a fresh, session-local level) carries more clean-reversal information than Asia-High. The path-anatomy layer that would convert this to a tradeable clean-path signal is **not** learnable at this sample size — the same N-wall seen in POST-E1 survivability.
4. **No promotion; no execution research (§32); broker disabled; DEV-only; no CALIB.** EARLY-TRAP-E1 and all frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`. Session/time observations remain diagnostic.

**Terminal statuses:** `FRANKFURT_FALSE_DRIVE_DISCOVERY_COMPLETE` · `NO_ROBUST_FRANKFURT_SHORT_SIGNAL_FOUND` ; `LONDON_FALSE_DRIVE_DISCOVERY_COMPLETE` · `LONDON_SHORT_SIGNAL_WEAK`. **STOP.**
