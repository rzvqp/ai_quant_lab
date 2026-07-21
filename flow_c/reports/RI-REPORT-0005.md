─────────────────────────────────────────────
FLOW C — RESEARCH REPORT
ID:              RI-REPORT-0005
Data:            2026-07-21
Autor:           Research Intelligence
Nivel epistemic: cunoaștere-observațională (descriptiv)
Încredere:       scăzută (C1 — Speculativ). 13 populații (familiile profitabile non-S1), completare
                 descriptivă, fără falsificare, fără mecanisme, fără explicații cross-familie.
                 Fidelitate descriptivă ridicată (corpus reprodus bit-exact).
─────────────────────────────────────────────
BAZA DE DOVEZI (Evidence base)
  • Sursă:      results/FAMILY_RESULTS.parquet, subseturile fam ∈ {S2,S3,S5,S6,S8,S9,S13,S14,S16,
                S17,S18,S19,S20} (620 rânduri). Reprodus bit-exact (comparison.json, diff 0.0).
                XAUUSD, grilă M15. Unități presupus R.
  • Fereastră:  years până la 4; months până la 27.
  • Completitudine: `val_exp` complet (0 lipsă) în toate cele 13 familii — confirmă corpus-wide că
    lipsa de val_exp e localizată exclusiv în S1.
  • NON-fabricare: fiecare cifră derivă din citirea directă a subseturilor.
─────────────────────────────────────────────
REGULI DE ÎNCADRARE:
  • Fiecare familie descrisă în sine; comparațiile cu corpul = baseline-uri descriptive etichetate.
  • Contribuția nouă: side split per-familie + amprentă temporală (months/pos_months/years) — celulele
    rămase pentru „normal legibil" (A.3.1). FĂRĂ explicații cross-familie, FĂRĂ mecanisme (🔒 P2/P4).
─────────────────────────────────────────────
CE AR FALSIFICA ACEST RAPORT:
  O re-citire a subseturilor care ar da alte distribuții (imposibil dacă fișierul e neschimbat).
PLAFON EPISTEMIC:
  Descriere. NU validează, NU explică, NU compară inferențial, NU recomandă.
─────────────────────────────────────────────

# 1. ÎNTREBAREA DE PLECARE

Care este side split-ul și amprenta temporală (months/pos_months/years) a celor 13 familii profitabile non-S1 — celulele descriptive rămase pentru a face „normalul" fiecăreia complet legibil?

*(Completare descriptivă. Orice relație = 🔒 P2.)*

---

# 2. CORPUL DE DOVEZI

620 de ipoteze pe 13 familii (toate familiile profitabile în afară de S1, deja tratat în RI-REPORT-0003). Împreună cu RI-REPORT-0001 (agregat) și 0002 (coloane robustețe), aici se închid ultimele celule per-familie: side și temporal.

---

# 3. OBSERVAȚII (side + temporal; comparații = baseline etichetat)

**Side:**
- **O1 — Toate cele 13 familii au side echilibrat long/short (nicio „both").** Totaluri: 310 long / 310 short / 0 both. *(Împreună cu RI-REPORT-0004: toate cele 104 „both" din corp sunt în familiile zero-profit. Relația side↔profitabilitate = 🔒 P2.)*

**Temporal (baseline corp: months med 27, pos_months med 8, years med 4):**
- **O2 — years median per familie variază:** 4 (S2,S3,S5,S6,S8,S13,S18), 3 (S9,S14,S16,S20), 2 (S17), **1 (S19)**.
- **O3 — pos_months median (luni pozitive) variază larg:** de la **2** (S3, S19) la **11** (S18); S2/S17 = 9, S9 = 10.
- **O4 — amprenta temporală scurtă co-apare descriptiv cu n mic:** S19 (n med 17, years 1, pos_months 2), S14 (n med 64), S17 (n med 172). *(marginal; relația n×temporal×outcome = 🔒 P2.)*

**Funnel/rezultat (rezumat; detaliu în Family Identity §8):**
- **O5 — research_worthy neuniform:** prezent la S2,S5,S6,S8,S9,S14,S17,S20; **absent (0) deși există profitabili** la S3,S13,S16,S18,S19.
- **O6 — extreme de exp cu n mic:** S19 best +0,915 / worst −1,095 (n=12); S14 best +0,579 (n=16); S6 best +0,497 (n=32); S17 best +0,424 (n=24). *(descriptiv; „artefact vs semnal" = 🔒 P2, S6 deja cunoscut ca tiny-stop.)*

**Completitudine:**
- **O7 — `val_exp` complet** în toate cele 13 familii.

---

# 4. INFORMAȚII (context, per familie)

- **I1.** Compoziția de side e uniformă (long/short echilibrat) în toate familiile profitabile non-S1; „both" apare exclusiv în familiile zero-profit (RI-REPORT-0004). *(descriptiv; relația = 🔒 P2.)*
- **I2.** Amprenta temporală e heterogenă: unele familii sunt active pe tot orizontul cu multe luni pozitive (S18 pos_months 11, S9 10, S2 9), altele scurte (S19 years 1, pos_months 2).
- **I3.** Familiile cu exp-max mari sunt și cele cu n mic și/sau amprentă temporală scurtă (O4/O6) — co-apariție descriptivă, în linia observației de corp din RI-REPORT-0001. *(relația = 🔒 P2.)*
- **I4.** `val_exp` complet aici → localizarea în S1 se confirmă la nivelul întregului corp.

---

# 5. REGULARITĂȚI GĂSITE (C1 — Speculativ)

- **R1 — Toate familiile profitabile non-S1 sunt side-balanced (long/short, fără both).**
- **R2 — Amprentă temporală heterogenă:** years median 1–4, pos_months median 2–11.
- **R3 — exp-max mare co-apare cu n mic / temporal scurt** (S19/S14/S17/S6) — marginal; relația = 🔒 P2.

*Încredere R1–R3: C1. 13 populații, descriptiv, fără falsificare, fără corelații.*

---

# 6. CE NU EXPLICĂ RAPORTUL

- **DE CE** variază amprenta temporală sau de ce apar exp-max mari la n mic — mecanisme, 🔒 P4.
- Relațiile **side↔profitabilitate**, **n×exp-max**, **temporal×outcome** — 🔒 P2.
- Dacă research_worthy absent la S3/S13/S16/S18/S19 e semnal — 🔒 P2.
- Semantica coloanelor; decompoziția „valid" per-familie.

---

# 7. TRIMITERI (doar întrebări, fără ipoteze)

- **Candidat RQ:** Side-ul „both" apare exclusiv în familii zero-profit, iar long/short exclusiv altundeva — relație reală sau artefact de design? → **Meta Analysis**, 🔒 P2.
- **Candidat RQ:** exp-max mari la n mic (S19/S14) sunt semnal sau artefact de eșantion mic? → 🔒 P2 (test), S6 deja artefact.
- **Candidat RQ:** de ce unele familii cu profitabili nu au niciun research_worthy (S3/S13/S16/S18/S19)? → 🔒 P2.
- **Indicație Meta (P2):** amprenta temporală × profitabilitate ca relație — juxtapunere pentru P2.

*Stare: toate OPEN. Nicio ipoteză formulată. Adăugate în coada relațională P2 fără a reordona planul (§7.3).*

---

# 8. FAMILY IDENTITY (standard de prezentare — doar câmpuri descriptive)

*Un rând descriptiv per familie. Non-analitic.*

| Familie | n | Side | hp/rw/fr | exp med | exp best/worst | pf med | win med | dd med | n med | pos_m med(max) | years med | val_exp lipsă | Extremă notabilă |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S2 | 144 | 72/72 | 18/6/11 | −0,095 | +0,075/−0,407 | 0,866 | 0,321 | 125 | 893 | 9(17) | 4 | 0 | cea mai numeroasă non-S1 |
| S3 | 96 | 48/48 | 2/0/0 | −0,269 | +0,063/−0,417 | 0,670 | 0,381 | 405 | 1614 | 2(15) | 4 | 0 | 0 research-worthy |
| S5 | 96 | 48/48 | 20/12/2 | −0,104 | +0,166/−0,391 | 0,783 | 0,377 | 60 | 410 | 7(19) | 4 | 0 | cei mai mulți rw non-S1 |
| S6 | 32 | 16/16 | 7/3/3 | −0,289 | +0,497/−0,801 | 0,686 | 0,289 | 84 | 315 | 8(13) | 4 | 0 | tiny-stop cunoscut |
| S8 | 48 | 24/24 | 4/2/0 | −0,235 | +0,029/−0,753 | 0,736 | 0,298 | 202 | 663 | 7(16) | 4 | 0 | — |
| S9 | 32 | 16/16 | 12/6/1 | −0,077 | +0,068/−0,308 | 0,872 | 0,352 | 54 | 540 | 10(17) | 3 | 0 | rată hp mare pe n mic |
| S13 | 24 | 12/12 | 5/0/0 | −0,153 | +0,041/−0,359 | 0,769 | 0,329 | 305 | 2020 | 6(18) | 4 | 0 | frecvență înaltă |
| S14 | 16 | 8/8 | 6/1/5 | −0,069 | +0,579/−0,689 | 0,889 | 0,364 | 10 | 64 | 5(11) | 3 | 0 | 5/6 profitabili fragili |
| S16 | 40 | 20/20 | 1/0/0 | −0,250 | +0,032/−0,622 | 0,726 | 0,304 | 220 | 631 | 6(14) | 3 | 0 | 1 singur profitabil |
| S17 | 24 | 12/12 | 6/5/0 | −0,203 | +0,424/−0,553 | 0,785 | 0,309 | 45 | 172 | 9(18) | 2 | 0 | exp-max mare, dd mic |
| S18 | 24 | 12/12 | 5/0/1 | −0,076 | +0,177/−0,471 | 0,899 | 0,302 | 73 | 550 | 11(20) | 4 | 0 | cel mai mare pos_months |
| S19 | 12 | 6/6 | 4/0/1 | −0,203 | +0,915/−1,095 | 0,709 | 0,342 | 7 | 17 | 2(6) | 1 | 0 | cel mai mic n, cel mai mare spread exp |
| S20 | 32 | 16/16 | 6/5/0 | −0,167 | +0,099/−0,386 | 0,776 | 0,333 | 84 | 523 | 7(16) | 3 | 0 | — |

─────────────────────────────────────────────
CONTRIBUȚIE LA ACOPERIRE (per P1_COVERAGE_PLAN):
  Celule completate: 2a — side per-familie + temporal pentru cele 13 familii profitabile non-S1
  → închide A.3.1 (20/20 „normal" legibil incl. side). Coloana temporală (pos_months) tratată.
  Coverage Confidence: RĂMÂNE Medium — NU declar re-rating. Auditul A.5 se pregătește separat;
  re-rating-ul spre High e rezervat review-ului CEO (upgrade cu review, §2.1 Lifecycle).
─────────────────────────────────────────────
*Sfârșitul RI-REPORT-0005. Ultimul raport din secvența planificată. NU încep P2, NU încep alt raport.*
─────────────────────────────────────────────
