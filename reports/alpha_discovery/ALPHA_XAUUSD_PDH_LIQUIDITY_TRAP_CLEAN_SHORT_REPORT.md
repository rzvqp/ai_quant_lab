# ALPHA_XAUUSD_PDH_LIQUIDITY_TRAP_CLEAN_SHORT_REPORT

**Mandate:** `ALPHA-XAUUSD-PDH-LIQUIDITY-TRAP-CLEAN-SHORT-001` · **Date:** 2026-08-22.
**Terminal statuses:** `PDH_LONDON_DISCOVERY_COMPLETE` · **`NO_ROBUST_PDH_LONDON_SHORT_SIGNAL_FOUND`** ; `PDH_NY_DISCOVERY_COMPLETE` · **`NO_ROBUST_PDH_NY_SHORT_SIGNAL_FOUND`**.
**Scope:** NEW independent SHORT family (PDH sweep + time + early response + clean-path). London & NY **separate**. Price-only, native-M5, DST-aware, DEV-only. Primary objective = **≥80 project-pip bearish move BEFORE any new high** (4-class A/B/C/D). No CALIB/V1/2025+/N4/execution. Independent of EARLY-TRAP-E1 / POST-E1-CLEAN-P2 / Pre-London-High (§44). ≤16 IDs; 0 candidates. No promotion; broker disabled.

---

## 0. Headline
- **The demanding 80p clean-path bar exposes the right-direction-bad-path wall starkly:** PDH sweeps produce a **clean 80p short only 8–11% of the time** — L P(A) 0.108, N P(A) 0.080. The 80p downside *does* occur (MFE≥80p 56% L / 42% N) but overwhelmingly **after a new high (class B) or with bullish continuation (class C)** — B+C = 0.89 (L) / 0.88 (N).
- **No robust clean-path signal in either session.** Same-parent failed-acceptance lifts P(A) only to ~0.139. Early net-downside anatomy discriminates A-vs-B (NY net_prog AUC 0.76/0.84) — the **same mechanism as POST-E1-CLEAN-P2** — but the actionable bucket is **2023-concentrated, DISC↔CONF-inconsistent, and n=6–18**, failing multi-year robustness (§40) and sample honesty (§39).
- Neither family qualifies even as WEAK: raw P(A) is far too low and the discriminating subset does not generalize across years.

## 1. Lineage + firewall (§1, §2)
Independent new module. Native M5 (121,949 DEV bars, 2021-07-27→2023-12-29). Sanctioned loader only; no synthetic/interpolated M5; no N4/CALIB/V1/2025+.

## 2. PDH definition + day identity + DST (§4, §5, §8) — frozen convention
No canonical repo PDH existed → **one frozen versioned convention** (declared before outcomes): **trading day = UTC calendar day; PDH(D) = max native-M5 high of the immediately preceding day with ≥100 M5 bars (weekend/holiday → last day with data); no current/future bars.** DST-free (UTC boundary). 678 PDH days defined. Session windows via DST-aware `tz_convert` (verified Berlin/London/NY offsets, transitions). **FAMILY L = London-local 08:00–10:00; FAMILY N = New-York-local 08:00–11:00** — disjoint in UTC → deterministic event ownership (§9), no double-count. First sweep per window per day.

## 3. Parent sweep population (§6, §9)
| family | parent N | unique days | median sweep excursion above PDH |
|---|---|---|---|
| L (London) | 93 | 93 | 19.8p |
| N (New York) | 175 | 175 | 23.1p |

## 4. Four-class construction (§10, §11) + primary 80p endpoint
Frozen sweep_hi = high[E0]; reference = close[E0]; **CLEAN objective = reach `ref − 80p` before any high > sweep_hi**; horizon 96 M5 bars (8h), same UTC day.
| family | N | **A clean 80p** | **B newhi-first** | C continuation | D stalled | P(reach 80p ever) |
|---|---|---|---|---|---|---|
| **L (London)** | 93 | **0.108** | 0.452 | 0.441 | 0.000 | 0.559 |
| **N (New York)** | 175 | **0.080** | 0.343 | 0.537 | 0.040 | 0.423 |
**A is rare; B+C dominate.** The clean-path fraction is 8–11%, versus a 42–56% chance the 80p move happens *at all* (mostly as B).

## 5. Secondary structural diagnostics (§12) — the room exists
Downside MFE from reference: **L** ≥30p 0.83, ≥50p 0.70, ≥80p 0.56, ≥100p 0.43, ≥150p 0.18, ≥200p 0.10 · **N** ≥30p 0.78, ≥50p 0.63, ≥80p 0.42, ≥100p 0.32, ≥150p 0.18, ≥200p 0.08. Large downside is physically available; **the constraint is the PATH (new-high-first), not target availability** — the exact right-direction-bad-path problem.

## 6. E0–E4 anatomy + clean-path discriminator (§15–§20, §34) — insufficient
Undecided-conditioned (no new high & 80p not yet reached), predicting eventual class A, DISC/CONF AUC of the best stable feature:
| landmark | L undecided n (AUC) | N undecided n (AUC best=net_prog) | remaining to 80p |
|---|---|---|---|
| E1 | 48 (failed_ext 0.66/0.69) | 78 (downside 0.77/0.62) | ~66–73p |
| E2 | 36 (downside 0.59/0.67) | 67 (net_prog **0.76/0.84**) | ~62–69p |
| E3 | 29 (failed_ext 0.69/0.67) | 55 (net_prog 0.62/0.81) | ~53–58p |
| E4 | 27 (last_bear 0.60/0.81) | 43 (net_prog 0.72/0.91) | ~46–57p |
**Early net-downside progress carries real A-vs-B rank information in NY (AUC stable), retaining ~50–62p room** — but the actionable bucket does not generalize (next).

## 7. High-confidence bucket (frozen DISC median net-downside, E2) — fails robustness
| family | DISC bucket P(A) (base) | CONF bucket P(A) (base) | CONF P(B) | 2021 / 2022 / 2023 P(A) |
|---|---|---|---|---|
| **N (NY)** | 0.167 (0.111), n18 | **0.462** (0.290), n13 | **0.000** | 0.143 / 0.167 / 0.389 |
| **L (London)** | 0.364 (0.318), n11 | 0.333 (0.214), n6 | **0.455** | 0.000 / — / 0.556 |
NY's clean bucket reaches P(A) 0.46 / P(B) 0.00 on CONF — **but DISC lifts barely (0.11→0.17), it is 2023-concentrated (2021/22 ~0.15), and n=13.** London's high-net-downside subset **keeps P(B)=0.455** (bad path persists) with per-year 0.00/0.56 noise. **Neither clears §40 (no one-year dependence) or §39 (small-N honesty).**

## 8. Failed acceptance (§19) + failed extension + velocity + marginal progress (§22, §23)
Same-parent failed-acceptance (close < PDH by E2) vs sustained: **L +0.051 (0.139 vs 0.088), N +0.100 (0.139 vs 0.039)** — real but small; even failed-acceptance P(A) only 0.139. Failed-extension nominally stable in London (AUC ~0.67) but on a 0.11 base. Attack-velocity / marginal-upside-progress not advanced (parent families already negative).

## 9. First-vs-repeat (§21) + previous-day + day-of-week (§25, §26) — no stable structure
First-vs-repeat PDH attack (counted correctly, only after PDH frozen — **no `prior_attacks()` defect**): L first 0.048 / repeat 0.125; N first 0.132 / repeat 0.047 — **opposite directions → noise.** Day-of-week (correct units): L Mo 0.14/Tu 0.15/We 0.13/Th 0.09/Fr 0.05; N Mo 0.04/Tu 0.10/We 0.00/Th 0.09/Fr 0.15 — **no stable DOW effect**; no DOW logic built (§26).

## 10. DISCOVERY/CONFIRMATION + temporal (§29, §40) — 2023-dependent
Chronological split applied. The raw clean rate is stable-but-low across years (L 0.08/0.12/0.12); the *discriminated* NY bucket is 2023-driven (0.14/0.17/0.39). No candidate shows same-direction strength across partial-2021, 2022, and 2023.

## 11. Candidate ranking (§41) + graveyard (§45)
**No candidate ranks.** Best-of-a-bad-field = NY early-net-downside bucket (P(A) 0.46 CONF / P(B) 0.00) — **rejected** for 2023-concentration + DISC↔CONF inconsistency + n=13. Graveyard: London & NY raw PDH clean-80p (bad-path dominated); all E0–E4 anatomy buckets; failed-acceptance/extension; first-vs-repeat; day-of-week. Recorded in `pdh_short.py` / `pdh_short2.py`.

## 12. Answers to §45 (compact)
1 L 93 days (~14%) · 2 N 175 days (~26%) · **3 clean 80p: L 0.108 / N 0.080** · **4 new-high-first: L 0.452 / N 0.343** · 5 continuation: L 0.441 / N 0.537 · 6 return-below marginal (+0.05/+0.10 same-parent) · 7–8 anatomy not robust · 9–10 velocity/marginal not advanced · 11–13 E1→E4 net-downside AUC rises (NY 0.62→0.91) but 2023-driven/small-N · 14 E4 ~46p remaining (not too late physically) · 15 first-vs-repeat = noise · 16 NY has the net-downside AUC signal, London noisier; **neither robust** · 17 ≥80p room exists (MFE 42–56%) but as class B · **18 does NOT work in partial-2021/2022 (clean ~0)** · 19 P(new-high-first) reduced only in a tiny 2023 NY bucket · **20 NO standalone clean-path signal for audit.**

## 13. Limitations (§39)
Parent N modest (L 93 / N 175); undecided sub-buckets 6–18; native-M5 partial-2021 (from 2021-07, dated). The 80p objective makes clean events intrinsically rare (base 0.08–0.11), so even a stable rank-discriminator yields tiny actionable subsets. Single frozen PDH convention (UTC-day) — a different daily boundary was **not** searched (§4 forbids selection).

## 14. CEO recommendation
1. **`NO_ROBUST_PDH_LONDON_SHORT_SIGNAL_FOUND`** and **`NO_ROBUST_PDH_NY_SHORT_SIGNAL_FOUND`.** At the economically-meaningful 80p clean bar, a PDH sweep cleanly reverses only 8–11% of the time; the dominant outcomes are new-high-first (B) and bullish continuation (C). The large downside genuinely available (MFE≥80p 42–56%) is **not tradeable as a clean path** because it overwhelmingly follows a new high.
2. **The one real sub-finding is not a signal:** early net-downside progress discriminates clean-vs-bad-path in NY (AUC 0.76–0.84, stable) — but this is the **same mechanism already surfaced by POST-E1-CLEAN-P2**, and on the PDH parent it is 2023-concentrated, DISC↔CONF-inconsistent, and n=13. It does not clear the mandate's multi-year and sample-size bars. Recorded as a lead, **not** advanced (and, per §44, deliberately not combined with POST-E1-CLEAN-P2).
3. **Consistent program picture:** across Asia-High, Pre-London-High, and now PDH, *which level is swept* modulates the clean-reversal rate (Pre-London-High was best at ~0.37 to the mid), but **no price-only sweep family produces a robust CLEAN 80p short** — the adverse-path (new-high-first) wall persists, and the only helping discriminator (early downside follow-through) is N-limited on every parent tested.
4. **No promotion; no execution research (§43); broker disabled; DEV-only; no CALIB.** EARLY-TRAP-E1 and all frozen strategies untouched; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal statuses:** `PDH_LONDON_DISCOVERY_COMPLETE` · `NO_ROBUST_PDH_LONDON_SHORT_SIGNAL_FOUND` ; `PDH_NY_DISCOVERY_COMPLETE` · `NO_ROBUST_PDH_NY_SHORT_SIGNAL_FOUND`. **STOP.**
