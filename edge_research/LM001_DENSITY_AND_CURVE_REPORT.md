# LM-001 — DENSITATE TEMPORALĂ + COMPLETAREA CURBEI S8 (Mandat 5.5, Sarcina 1)

**Autor:** Validation Engine · **Data:** 2026-07-28 · **Branch:** discovery-mk-matrix-v1
**Livrez DOUĂ măsurători, fără concluzie. Maparea densitate→φ o face Statisticianul (sau declară că nu se poate → WP-5'). NU declar metoda utilizabilă sau nu.**

Circularitatea (ai nevoie de autocorelația net_R ca să știi dacă metoda e sigură; ai nevoie de prețuri ca s-o calculezi) e ocolită geometric: suprapunerea ferestrelor de 20 bare produce autocorelație și se numără pe indici, fără P&L.

---

## A. Auditul de densitate temporală (`code/lm001_density_audit.py`)

Populație: **21.054** wick-sweep-uri filtrate [10,1 ; 65,0] pips. Din care **6** au orizontul c+20 ieșind din segment (disclosed) → **21.048** = exact `combined_population.n` din manifest. Suprapunere = `|c_i − c_j| < 20` în același segment. Doar geometrie de indici; zero prețuri pentru performanță.

| Celulă | N | evenimente concurente (medie) | % care se suprapun | grad (medie / p90 / max) |
|---|---|---|---|---|
| **AGREGAT** | 21.054 | **8,64** | **99,1%** | 7,64 / 13 / 26 |
| bear | 9.254 | 8,95 | 99,4% | 7,95 / 13 / 24 |
| bull | 7.186 | 8,09 | 98,3% | 7,09 / 12 / 26 |
| correction | 4.614 | 8,87 | 99,6% | 7,87 / 12 / 22 |
| asia | 5.915 | 6,92 | 98,0% | 5,92 / 10 / 18 |
| london | 5.635 | 9,85 | 99,7% | 8,85 / 14 / 24 |
| ny | 8.386 | 9,36 | 99,6% | 8,36 / 13 / 26 |
| late | 1.118 | 6,27 | 97,7% | 5,27 / 9 / 16 |

**Distribuția gradului (nu doar media)** — un eveniment cu 15 suprapuneri ≠ unul cu una singură:
grad 0: 191 · 1: 436 · 2: 835 · 3: 1243 · 4: 1597 · 5: 2055 · 6: 2221 · 7: 2388 · 8: 2185 · 9: 1974 · 10: 1600 · 11: 1273 · 12: 943 · 13: 639 · 14: 467 · 15: 312 · 16: 254 · 17: 143 · 18: 130 · 19: 75 · 20: 36 · 21: 21 · 22: 19 · 23: 9 · 24: 7 · 26: 1.

**Fapt (nu concluzie):** doar 0,9% din evenimente sunt izolate temporal; masa e la 5–10 suprapuneri, coadă până la 26. london/ny cele mai dense (~9,4–9,9), asia/late cele mai rare (~6,3–6,9).

## B. Completarea curbei S8 la n=21.048 (`edge_research/lm001_s8/complete_curve.py`)

Aceeași baterie, aceiași parametri (B=10.000, L=28, n_series=300, α=0,05), două puncte noi în golul unde cade pragul propus de 0,45:

| φ | FPR@0,05 | CI95 | |
|---|---|---|---|
| 0,40 | 0,0500 | [0,031 ; 0,081] | nominal (măsurat anterior) |
| **0,45** | **0,0433** | [0,026 ; 0,073] | **nominal** |
| **0,50** | **0,0467** | [0,028 ; 0,077] | **nominal** |
| 0,60 | 0,0767 | [0,052 ; 0,112] | anti-conservator (măsurat anterior) |

**Fapt (nu concluzie):** granița nominal↔anti-conservator la n=21.048 e **între φ=0,50 (0,0467, nominal) și φ=0,60 (0,0767)** — traversează banda ~0,06 în jurul lui **φ≈0,55**. Pragul de 0,45, propus în ordin, cade **confortabil în regiunea nominală** (0,0433), nu la graniță. Acum granița e **derivată din măsurători**, nu aleasă.

---

**Ce NU fac:** nu leg densitatea (procent/grad de suprapunere) de un φ AR(1) — nu există o funcție densitate→φ, iar derivarea nu e a mea. Nu declar LM-001 testabilă sau nu. Livrez ambele măsurători; decizia (mapare densitate→φ, sau WP-5' structural) e a Statisticianului. Zero prețuri pentru P&L, holdout neatins, module MK neatinse aici.
