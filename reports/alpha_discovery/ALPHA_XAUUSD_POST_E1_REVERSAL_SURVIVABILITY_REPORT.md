# ALPHA_XAUUSD_POST_E1_REVERSAL_SURVIVABILITY_REPORT

**Mandate:** `ALPHA-XAUUSD-POST-E1-REVERSAL-SURVIVABILITY-001` · **Date:** 2026-08-22.
**Lineage:** discovery `6a5d535` · audit `de35453` · freeze `edbc687` · execution `48a67d3`.
**Terminal status:** `POST_E1_SURVIVABILITY_DISCOVERY_COMPLETE` · **`POST_E1_SURVIVABILITY_SIGNAL_WEAK`**.
**Scope:** NEW signal identity on the FROZEN `EARLY-TRAP-E1 v1.0.0` parent (118 episodes, unchanged). Price-only, native-M5, DEV-only. NO execution research; NO EARLY-TRAP-E1 retuning; future path = label only. 0 signals promoted; 1 weak candidate for audit. No CALIB/V1/2025+/promotion; broker disabled.

---

## 0. Headline — answers to the §25 questions
1. **Can we predict at P1 whether the trade makes a new high first?** Partially — model AUC 0.64/0.66 at P1 (5 min, ~24p remaining): a modest early read.
2. **Does P2 materially improve discrimination?** **Yes** — AUC 0.786/0.774 (10 min, ~26p remaining).
3. **Does P3 materially improve?** **Yes** — AUC 0.802/0.898 (15 min) and **still ~25p remaining** (not late).
4. **Does P4 become too late?** P4 thins the undecided set to 56 and DISC drops to 0.710 — P3 is the sweet spot; P4 adds little.
5. **Is failed upward extension informative?** Yes — `dist_to_sweep` (how far below the sweep high price stayed) is the strongest single feature (P2 0.69/0.87).
6. **Is early downside progress informative?** **Yes — the core** (`net_prog` 0.74/0.74, `downside_prog` 0.69/0.68 at P2).
7. **Is adverse excursion already diagnostic?** Yes — proximity to the sweep high (invalidation) discriminates strongly.
8. **Does London differ from overlap?** Reported as context only (§11); **not used as a filter** (parent is London/overlap-dominated).
9. **Can a useful discriminator retain ≥20p to midpoint?** Population-level **yes** (~25p undecided at P2/P3); the high-confidence subset retains ~16p.
10. **Can we separate CLEAN from NEW_HIGH_FIRST with enough N?** Separation **yes** (AUC 0.77–0.90); **"enough N" is the weak point** (76–86 undecided; 6/year in 2021–2022).
11. **One simple frozen price-only rule worthy of audit?** **Yes** — `R1: net downside>0 AND bearish P2 body` (+0.22/+0.24 lift both splits).

## 1. Canonical parent identity (§1, §23)
Parent = frozen `EARLY-TRAP-E1 v1.0.0` (impl_fp `33bec449…`, verified `== edbc687`): 118 episodes, unchanged. No Asia/sweep/E1/rule modification.

## 2. Class construction (§2) — outcome labels only
Over the same-day forward path from E1: **A CLEAN_REVERSAL** (mid before any high > frozen sweep high) = 63 (53.4%); **B new-high-then-mid** = 36 (30.5%); **C new-high-never** = 19 (16.1%); **D none** = 0. Label = 1 for A. Future path never enters features (§22).

## 3. Landmarks P0–P4 (§4) — native M5
P0 = E1 close (signal known). P1–P4 = first four completed **native M5** bars after E1 (M5 firewall preserved; no synthetic bars). All 118 episodes have P1–P4.

## 4. Timeliness + undecided N (§8, §10) — no lateness trap
Discrimination is measured **only on episodes still UNDECIDED at Pk** (no new high yet, mid not yet reached) — the real decision point:
| landmark | undecided n | median % E1→mid consumed | median remaining |
|---|---|---|---|
| P1 (5 min) | 98 | 33% | 24.4p |
| P2 (10 min) | 86 | 31% | 25.6p |
| P3 (15 min) | 76 | 29% | 25.5p |
| P4 (20 min) | 56 | 28% | 28.0p |
**Room is preserved** — undecided episodes retain ~25p to the mid throughout, so a P2/P3 discriminator is genuinely early.

## 5. Univariate path diagnostics (§13) — stable dimensions (AUC DISC/CONF)
| feature | P1 | P2 | P3 | reading |
|---|---|---|---|---|
| **net_prog** (net downside by Pk) | 0.67/0.64 | 0.74/0.74 | 0.78/0.83 | early downside follow-through → clean |
| **dist_to_sweep** (room still below sweep) | 0.60/0.86 | 0.69/0.87 | 0.71/0.88 | stayed far below invalidation → clean |
| **downside_prog** | 0.64/0.56 | 0.69/0.68 | 0.67/0.84 | |
| **last_bear_body** | 0.67/0.64 | 0.73/0.70 | 0.68/0.75 | bearish Pk M5 body → clean |
| **ratio_dn_up** | 0.60/0.60 | 0.68/0.68 | 0.67/0.77 | |
| dist_to_e1hi | 0.58/0.77 | 0.66/0.76 | 0.71/0.79 | |
| consec_lower_high | 0.53/0.52 | 0.64/0.58 | 0.74/0.79 | (later) |
Non-informative / unstable: upside_retrace, last_close_loc, last_upper_wick, failed_extend (weak), consec_lower_close (P1).

## 6. Failed-extension (§7) + downside-progress (§9) + adverse-excursion (§8)
- **Failed upward extension:** captured continuously by `dist_to_sweep` — the further below the sweep high price stays, the more likely a clean reversal (P2 CONF AUC 0.87). The binary `failed_extend` alone is weak; the continuous distance is the signal.
- **Early downside progress:** `net_prog`/`downside_prog` are the primary discriminators (§9 hypothesis supported).
- **Adverse excursion:** proximity to the sweep high (small `dist_to_sweep`) is an early tell of eventual new-high-first.

## 7. Small interpretable model (§14) + simple rule (§15)
**P2 model** (8 features: net_prog, dist_to_sweep, downside_prog, ratio_dn_up, last_bear_body, consec_lower_close, dist_to_e1hi, failed_extend; frozen DISC): **DISC AUC 0.786 → CONF AUC 0.774.** High-confidence clean bucket (p ≥ DISC-q0.6): CONF n=20, **P(clean) 0.650** (base 0.410, +0.24), ~17p remaining. Per-landmark model: P3 reaches DISC 0.80 / CONF 0.90 (still ~25p remaining).

**Simple rule (§15):**
| rule | DISC | CONF |
|---|---|---|
| **R1: net downside>0 AND bearish P2 body** | n17 P(clean) 0.706 (+0.217), 17p | n17 P(clean) 0.647 (+0.237), 16p |
| R2: net downside>0 AND dist_to_sweep≥17p | n13 0.769 (+0.280) | **n4** 1.000 (too small) |
| R3: net downside>0 alone | n21 0.667 (+0.177) | n21 0.571 (+0.161) |
**R1 is the transparent frozen proxy** — stable +0.22/+0.24 both splits, ~16p remaining.

## 8. Discovery/confirmation (§16, §19) — MEETS the primary criterion
Chronological split of the 118 episodes (DISC 70 / CONF 48; undecided-at-P2 DISC 47 / CONF 39). The discriminator **improves prediction of CLEAN_REVERSAL on BOTH DISCOVERY and CONFIRMATION while ~25p remains** (§19 primary success criterion met): model 0.786/0.774; R1 +0.217/+0.237.

## 9. Temporal blocks (§21) — consistent direction, thin per-year N
High-confidence model P(clean) by year (base_clean in parens): 2021 n6 **0.667** (0.43) · 2022 n6 **0.667** (0.44) · 2023 n27 **0.704** (0.46). Positive lift in all three years — but **2021/2022 rest on n=6 each.**

## 10. Remaining-distance (§20) + session/timing (§11, §12)
Undecided-at-P2/P3 retain ~25p median; high-confidence subset ~16p. **No PnL/stop/entry** computed (§24). Session/Frankfurt-London timing reported as **context only** — no session or time filter added (that would be a further new signal component).

## 11. Candidate ranking + graveyard (§18)
- **Candidate `POST-E1-CLEAN-P2` (WEAK)** — NEW signal identity: EARLY-TRAP-E1 parent + at P2, R1 (`net downside>0 AND bearish P2 M5 body`) or the 8-feature P2 logistic → predict CLEAN_REVERSAL. Generalizes (DISC/CONF), timely (~16–25p remaining), positive all 3 years.
- Graveyard: upside_retrace, last_close_loc, last_upper_wick, failed_extend-binary, R2 (CONF n=4 — insufficient). Recorded in `post_e1_survive.py` / `post_e1_survive2.py`.

## 12. Limitations (§17) — why WEAK, not READY
- **Effective N small:** 118 parent → 76–86 undecided at P2/P3; CONF undecided 39; R1 CONF n=17; **per-year high-confidence n=6 (2021), 6 (2022), 27 (2023).** §17 mandates WEAK when candidate N is this small.
- **Reduces, does not eliminate:** flagged episodes still ~30–35% new-high-first (P(clean) ~0.65–0.71, not ~0.9).
- **Discrimination/room tradeoff:** the highest-confidence subset retains ~16p (less than the ~25p population).
- **Single-year OOS depth:** CONF is 2023-heavy; the 2021/2022 support is directional but tiny.
- **Not execution-tested** (§24): whether the improved survivability converts to expectancy is a separate future mandate.

## 13. CEO recommendation
1. **`POST_E1_SURVIVABILITY_SIGNAL_WEAK`.** A **genuine, DISC→CONF-stable, economically-timely** early discriminator EXISTS: at P2/P3 (10–15 min after E1, ~29–31% of the path consumed, ~25p still to the mid), **early downside progress + staying far below the sweep high + a bearish P2 M5 body** predict CLEAN_REVERSAL out-of-sample (model CONF AUC 0.77–0.90; rule R1 +0.24), directionally positive in all three years. This is the first evidence that the post-E1 adverse-path problem (`48a67d3`) is *partially* predictable from price alone.
2. **It is WEAK, not READY, on sample grounds (§17):** 76–86 undecided episodes and 6/year in 2021–2022 are too thin to declare robust. **Recommend independent Statistician audit** of `POST-E1-CLEAN-P2` (rule R1 + the P2 model) — the same gate EARLY-TRAP-E1 itself passed — to rule on effective N and robustness before any canonical freeze or execution mandate.
3. **Frozen definition handed forward, nothing promoted.** EARLY-TRAP-E1 (`edbc687`) untouched; session/timing/width observations remain diagnostic (§11/§33-discipline — adding them = yet another new signal). No execution research performed (§24). No promotion; broker disabled; DEV-only; no CALIB. The 9 frozen strategies are unaltered; portfolio SHORT still only frozen `H4-bo-raw-S`.

**Terminal status:** `POST_E1_SURVIVABILITY_DISCOVERY_COMPLETE` · `POST_E1_SURVIVABILITY_SIGNAL_WEAK`. **STOP.**
