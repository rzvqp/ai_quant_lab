# LM-001 — S8 EXTENSION la n≈21.000 (Mandat 5.4)

**Autor:** Validation Engine · **Data:** 2026-07-28 · **Branch:** discovery-mk-matrix-v1
**Spec:** manifest v2.5.5 (`1d03e4f`) `lm_001_preregistration.bootstrap_method`.
**Verdict: REGIM-DEPENDENT. Testul pre-înregistrat (φ=0,4) TRECE; regimul φ=0,6 NU — anti-conservator la n=21.048 și NU converge. Nu am ajustat implementarea.**

**Provenance / conformitate:** bateria S8 EXISTENTĂ reutilizată, **cu LOGICA neschimbată** (`block_bootstrap.py` = metoda VE; `synthetic_block_bootstrap.py` = harness-ul S8; copiate din `validation_engine/ve/`). Singurele modificări: importul local + **adnotări de tip pentru `mypy --strict`** — NEUTRE COMPORTAMENTAL (metadata; nu ating logica de reeșantionare/FPR, reproducerea numerică confirmată). Distribuții sintetice în memorie, **zero prețuri reale**, fără `.load()`, fără backtest. **B = 10.000** (Mandat 5.4), α = 0,05. Lungime bloc `L = round(n^(1/3))` — rata principială Politis-White, fixată înainte de rezultat; reproduce punctele deja calibrate (n=1.000 → L=10, exact ca în recordul care a picat). n_series = 300/punct.

---

## Curba FPR@0,05 pe null AR(1) (edge=0)

| n | L | φ=0,4 FPR@0,05 (CI95) | φ=0,6 FPR@0,05 (CI95) |
|---|---|---|---|
| 1.000 | 10 | 0,0567 [0,036–0,089] | 0,0600 [0,038–0,093] |
| 2.000 | 13 | 0,0500 [0,031–0,081] | **0,0733** [0,049–0,109] |
| 5.000 | 17 | 0,0600 [0,038–0,093] | **0,0733** [0,049–0,109] |
| 10.000 | 22 | 0,0367 [0,021–0,065] | 0,0600 [0,038–0,093] |
| **21.048** | **28** | **0,0500** [0,031–0,081] | **0,0767** [0,052–0,112] |

## Interpretare (fapt, nu decizie de verdict — verdictul e al Statisticianului)

**φ=0,4 (autocorelație moderată) — TRECE testul pre-înregistrat.** La n=21.048, FPR@0,05 = **0,0500**, în banda nominală (≤~0,055–0,06). Curba stă în nominal pe tot intervalul (0,037–0,060), fără deriva. Exact „comparabil cu φ=0,4 la n=1.000–2.000", cum a fixat Statisticianul.

**φ=0,6 (autocorelație mai puternică) — NU trece, și e o constatare, nu zgomot de n mic.** La n=21.048, FPR@0,05 = **0,0767**, peste bandă. Și critic: curba **NU se curăță monoton** — 0,060 → 0,073 → 0,073 → 0,060 → **0,077**; punctul cel mai mare (n=21.048) e cel mai anti-conservator. Anti-conservatorismul la φ=0,6 **persistă la 10× cel mai mare punct calibrat** — NU e un efect de eșantion finit care dispare cu n. 

**Aceasta validează refuzul Statisticianului de a extrapola:** dacă s-ar fi presupus „e sigur la n mare pentru că e consistent asimptotic", presupunerea ar fi fost **falsă la φ=0,6**. Metoda nu converge uniform la nominal — convergența depinde de regimul de autocorelație.

## Ce înseamnă pentru LM-001

Calibrarea la n=21.048 e **condiționată de autocorelația seriei net_R a LM-001**, care e NECUNOSCUTĂ a priori și pe care NU o pot măsura fără a atinge prețuri reale (interzis). 
- Dacă autocorelația net_R ≤ ~0,4–0,5: `block_bootstrap@v1` e nominal → utilizabil.
- Dacă e ~0,6 sau mai mult: rămâne anti-conservator chiar la acest n → **NU** utilizabil.

Nu declar o trecere necondiționată (ar ascunde constatarea φ=0,6), nici un eșec total (testul pre-înregistrat la φ=0,4 trece). **Decizia — dacă regimul LM-001 e sub pragul de siguranță, sau dacă regim-dependența declanșează WP-5' structural — e a Statisticianului.** Reamintesc: fallback-ul specificat NU e `matched_null@v1` (scop greșit), ci **WP-5'** structural, deja identificat.

**Nu am ajustat implementarea ca să treacă. Nu am atins prețuri reale, holdout-ul, market_structure.py sau liquidity_mechanics.py. Mă opresc aici.**
