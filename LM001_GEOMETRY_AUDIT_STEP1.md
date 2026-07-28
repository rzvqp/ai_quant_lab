# LM-001 GEOMETRY AUDIT — STEP 1 (Mandate 5.1)

**Autor:** Validation Engine · **Data:** 2026-07-28 · **Branch:** discovery-mk-matrix-v1
**Spec:** STAT-LM001-GEOMETRY-MK03-MK04-v1.0 (commit 49d0a14), citită integral din commit înainte de rulare.
**Script:** `code/lm001_geometry_audit.py` · **Record:** `edge_research/lm001_geometry_audit_results.json`

**Conformitate cu interdicțiile (spec §F):** audit de geometrie pură. `detect_breaks` NU e apelat — cale de cod izolată (bug-ul de re-armare rămâne izolat, cum a verificat Statisticianul). Fără P&L, fără tranzacții, fără optimizare, fără prag înghețat. Auditul NU derivă și NU recomandă o podea/plafon — doar măsoară.

**Tensiune de guvernanță (repetată, nerezolvată):** am scris scriptul de audit + detectorul-de-test și rulez măsurătoarea pe ele peste implementarea CEO. Statisticianul decide dacă CROSS-VERIFY-SPEC se aplică modulelor de cod.

**Setup verificat:** 130.491 bare de descoperire M15_v2 (52.403/52.851/25.237, convenție semi-deschisă `[start,end)`, coordonate verbatim din manifest via `edge_research/split_manifest.py` — nu recalculat; cifra ta corectă reprodusă exact). TICK=0,10 (`mstrat.py:10`, `alpha_lab.py:11`). Sesiuni din `mtf.py:37-38`, atribuite după ora UTC a barei-eveniment `c`. **N valid = 34.670 · N exclus (fără next-open în același `discovery_range`) = 1.**

---

## Matricea de percentile — deplasare în pips (intrare next-open → extremul fitilului)

| Celulă | N | min | p10 | p25 | mediană | p75 | p90 | max |
|---|---|---|---|---|---|---|---|---|
| **AGREGAT** | 34.670 | −3,6 | 4,4 | 8,0 | **14,7** | 26,8 | 47,0 | 607,5 |
| bear | 13.863 | −3,6 | 5,4 | 9,9 | 17,9 | 32,7 | 56,2 | 321,5 |
| bull | 14.190 | 0,1 | 3,5 | 6,2 | 10,7 | 18,3 | 31,2 | 220,7 |
| correction | 6.617 | 0,3 | 5,9 | 10,7 | 19,2 | 33,1 | 56,0 | 607,5 |
| asia | 11.219 | 0,1 | 3,6 | 6,4 | 11,2 | 19,3 | 31,8 | 304,6 |
| london | 8.796 | 0,1 | 5,1 | 8,7 | 15,6 | 28,0 | 47,3 | 303,3 |
| ny | 12.228 | −3,6 | 5,9 | 10,6 | 19,4 | 35,4 | 60,2 | 321,5 |
| late | 2.427 | 0,2 | 2,9 | 5,3 | 10,0 | 17,8 | 34,8 | 607,5 |

(min negativ = gap peste extrem; raportat ca atare, netrunchiat, per spec §E. Toate celulele n≫25.)

## Fracțiile — podeaua 40 / plafonul 65 pips (SCOPUL auditului; N explicit per celulă)

| Celulă | N | <40 pips | [40,65) | ≥65 |
|---|---|---|---|---|
| **AGREGAT** | 34.670 | **30.043 (86,7%)** | 2.788 (8,0%) | 1.839 (5,3%) |
| bear | 13.863 | 11.309 (81,6%) | 1.503 (10,8%) | 1.051 (7,6%) |
| bull | 14.190 | 13.341 (94,0%) | 526 (3,7%) | 323 (2,3%) |
| correction | 6.617 | 5.393 (81,5%) | 759 (11,5%) | 465 (7,0%) |
| asia | 11.219 | 10.527 (93,8%) | 453 (4,0%) | 239 (2,1%) |
| london | 8.796 | 7.601 (86,4%) | 708 (8,0%) | 487 (5,5%) |
| ny | 12.228 | 9.679 (79,2%) | 1.523 (12,5%) | 1.026 (8,4%) |
| late | 2.427 | 2.236 (92,1%) | 104 (4,3%) | 87 (3,6%) |

---

## Ce arată măsurătoarea (fapte, nu recomandare de prag)

**86,7% din deplasări cad sub 40 pips.** Exact scenariul semnalat: o podea de 40 de pips ar sta DEASUPRA geometriei de manipulare pentru marea majoritate a evenimentelor — ar **impune** riscul în loc să-l **derive** din extremul fitilului. Aceeași mecanică pe care ai numit-o D2. Chiar și în sesiunea/regimul cu cele mai mari deplasări (ny: 79,2% sub 40; bear/correction ~81,5%), majoritatea rămâne sub 40. Plafonul de 65 exclude 5,3% pe agregat (2,1%–8,4% pe celule).

**Referință de context (corectat de tine):** ATR-ul M15 pe descoperire e ~16–17 pips, nu 24. Mediana deplasării (14,7 pips agregat) e ~0,9× ATR — deplasarea tipică e sub un ATR, consecvent cu majoritatea sub 40.

**Structură:** bull cel mai strâns (mediană 10,7), bear/correction cele mai largi (17,9/19,2); ny cea mai largă sesiune (19,4), late/asia cele mai strânse (~10–11). Toate celulele au n≫25 — nicio celulă sub prag.

**Decizia podea/plafon NU e a mea** (spec §F) — e a Statisticianului, DUPĂ ce distribuția există. Aici e distribuția. Nu am atins holdout-ul, nu am rulat LM-001 ca ipoteză, nu am construit tranzacții.
