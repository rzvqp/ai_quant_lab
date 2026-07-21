─────────────────────────────────────────────
FLOW C — RESEARCH REPORT
ID:              RI-REPORT-0004
Data:            2026-07-21
Autor:           Research Intelligence
Nivel epistemic: cunoaștere-observațională (descriptiv; cunoaștere NEGATIVĂ)
Încredere:       scăzută (C1 — Speculativ). Șase populații (familiile zero-profit), prima tratare
                 dedicată, fără falsificare, fără mecanisme, fără explicații cross-familie.
                 Fidelitate descriptivă ridicată (corpus reprodus bit-exact).
─────────────────────────────────────────────
BAZA DE DOVEZI (Evidence base)
  • Sursă:      results/FAMILY_RESULTS.parquet, subseturile fam ∈ {S4,S7,S10,S11,S12,S15} (200 rânduri).
                Reprodus bit-exact (comparison.json, diff 0.0). XAUUSD, grilă M15. Unități presupus R.
  • Fereastră:  years până la 4; months până la 27.
  • Completitudine: `val_exp` complet (0 lipsă) în toate cele 6 familii — confirmă că lipsa de val_exp
    din corp e localizată exclusiv în S1 (RI-REPORT-0003).
  • NON-fabricare: fiecare cifră derivă din citirea directă a subseturilor.
─────────────────────────────────────────────
REGULI DE ÎNCADRARE (mandat CEO):
  • Fiecare familie zero-profit e descrisă în sine (cunoaștere negativă, rigoare egală cu a câștigătorilor).
  • FĂRĂ explicații cross-familie (de ce o familie diferă de alta = 🔒 P2). FĂRĂ mecanisme (🔒 P4).
  • Relațiile (ex. side↔profitabilitate) = 🔒 P2. Întrebările relaționale doar logate, nu răspunse.
─────────────────────────────────────────────
CE AR FALSIFICA ACEST RAPORT:
  O re-citire a subseturilor care ar da alte distribuții (imposibil dacă fișierul e neschimbat).
PLAFON EPISTEMIC:
  Descriere a formei eșecului. NU validează, NU explică, NU compară inferențial, NU recomandă.
─────────────────────────────────────────────

# 1. ÎNTREBAREA DE PLECARE

Care este forma descriptivă a celor 6 familii care nu au produs nicio ipoteză istoric-profitabilă (S4, S7, S10, S11, S12, S15) — sunt uniform slabe sau near-miss, cum arată coada lor negativă, cu ce frecvență și drawdown?

*(Cunoaștere negativă — gardă anti-survivorship, A.4.2. Fiecare familie în sine; fără explicații cross-familie.)*

---

# 2. CORPUL DE DOVEZI

200 de ipoteze pe 6 familii, toate cu hist_prof = research_worthy = fragile = **0**. Reprezintă întreaga „cunoaștere negativă la nivel de familie" a corpului (celelalte 14 familii au ≥1 profitabil). `val_exp` complet în toate.

---

# 3. OBSERVAȚII (per familie + agregat)

**Agregat (200 ipoteze):** 0 profitabile. Cel mai bun exp din tot grupul = **−0,036** (S12); cel mai slab = **−0,611** (S7). Compoziție de side: S4/S7/S11/S15 integral „both"; S10/S12 long/short echilibrat. Colectiv, aceste 6 familii conțin **toate cele 104 ipoteze „both" din corp**. *(Relația side↔profitabilitate = 🔒 P2.)*

**Per familie (exp med | best | worst; pf med; win med; dd med; n med):**
- **O1 — S4** (32 hyp, both): exp −0,227 | −0,145 | −0,391; pf 0,738; win 0,255; dd 297; n 1228.
- **O2 — S7** (24 hyp, both): exp −0,400 | −0,099 | **−0,611**; pf **0,498**; win 0,287; dd **1188**; n **2803**; sumR med **−1185**.
- **O3 — S10** (48 hyp, long/short): exp −0,231 | −0,051 | −0,338; pf 0,720; win 0,299; dd 294; n 1515.
- **O4 — S11** (24 hyp, both): exp −0,120 | −0,053 | −0,246; pf 0,798; win 0,352; dd 100; n 700.
- **O5 — S12** (48 hyp, long/short): exp −0,155 | **−0,036** | −0,245; pf 0,783; win 0,346; dd 237; n 1534. *(4,2% din ipotezele S12 au exp > −0,05 — cele mai apropiate de breakeven din grup.)*
- **O6 — S15** (24 hyp, both): exp −0,117 | −0,050 | −0,284; pf 0,843; win 0,307; dd 175; n 1213.

**Comun tuturor:** median-trade puternic negativ (~−0,72 la −1,20); win median 0,25–0,35; toate `best exp` rămân negative.

---

# 4. INFORMAȚII (context, per familie / agregat)

- **I1 — Textură de eșec heterogenă:** unele familii sunt near-miss (S12 best −0,036; S10/S11/S15 best în [−0,05; −0,053]), altele clar slabe (S4 best −0,145; S7 best −0,099 dar median −0,400). Eșecul nu e uniform. *(descriptiv; „de ce" = 🔒 P4.)*
- **I2 — S7 e o extremă de badness în grup:** cea mai slabă exp mediană (−0,400), cel mai mic pf (0,498), cel mai mare dd (1188), cel mai mare n (2803), sumR −1185. *(comparație descriptivă etichetată; explicația inter-familie = 🔒 P2.)*
- **I3 — Frecvență ridicată:** toate cele 6 familii au n median mult peste S1 (209) — de la 700 (S11) la 2803 (S7). Populații descriptiv de frecvență înaltă.
- **I4 — Coada negativă:** cea mai slabă ipoteză din grup atinge exp −0,611 (S7) și sumR până la −1185 median.
- **I5 — Completitudine:** `val_exp` complet aici, spre deosebire de S1.

---

# 5. REGULARITĂȚI GĂSITE (C1 — Speculativ, în interiorul grupului zero-profit)

- **R1 — Eșec heterogen, nu uniform:** familiile zero-profit se întind de la near-breakeven (best −0,036) la sever (median −0,400).
- **R2 — Semnătură comună descriptivă:** win median sub 0,36, median-trade puternic negativ, toate best-exp negative, frecvență de tranzacționare înaltă.
- **R3 — S7 = valoare extremă a grupului** pe exp, pf, dd, n, sumR simultan.

*Încredere R1–R3: C1. Șase populații, descriptiv, fără falsificare, fără explicații cross-familie.*

---

# 6. CE NU EXPLICĂ RAPORTUL

- **DE CE** o familie eșuează, sau de ce S7 e mai slabă decât S12 — mecanisme / explicații cross-familie, 🔒 P4 / P2.
- Relația **side↔profitabilitate** (toate „both" sunt aici) — 🔒 P2.
- Dacă near-miss-ul S12 e semnal sau zgomot — 🔒 P2 (necesită test).
- Semantica exactă a coloanelor; decompoziția „valid" per-familie.

---

# 7. TRIMITERI (doar întrebări, fără ipoteze)

- **Candidat RQ:** Toate cele 104 ipoteze „both" din corp sunt în familii zero-profit — există o relație side↔profitabilitate? → **Meta Analysis**, 🔒 P2.
- **Candidat RQ:** Near-miss-ul S12 (best −0,036; 4,2% > −0,05) e semnal exploatabil sau artefact de coadă? → 🔒 P2 (test).
- **Candidat RQ:** S7 diferă de restul grupului pe toate axele simultan — ce distinge configurația ei? → comparație inter-familie, 🔒 P2.
- **Indicație Meta (P2):** frecvența înaltă (n) a familiilor zero-profit vs S1 — juxtapunere relațională pentru P2.

*Stare: toate OPEN. Nicio ipoteză formulată. Adăugate în coada relațională P2 fără a reordona planul (§7.3).*

---

# 8. FAMILY IDENTITY (standard de prezentare — doar câmpuri descriptive)

*Introdus prin decizie CEO; secțiune de prezentare, nu analitică. Un card descriptiv per familie.*

| Câmp | S4 | S7 | S10 | S11 | S12 | S15 |
|---|---|---|---|---|---|---|
| Nr. ipoteze | 32 | 24 | 48 | 24 | 48 | 24 |
| Cotă din corp | 1,6% | 1,2% | 2,4% | 1,2% | 2,4% | 1,2% |
| Side | both | both | long/short | both | long/short | both |
| hist_prof / rw / fragile | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| Status profitabilitate | zero-profit | zero-profit | zero-profit | zero-profit | zero-profit | zero-profit |
| exp median | −0,227 | −0,400 | −0,231 | −0,120 | −0,155 | −0,117 |
| exp best / worst | −0,145 / −0,391 | −0,099 / −0,611 | −0,051 / −0,338 | −0,053 / −0,246 | −0,036 / −0,245 | −0,050 / −0,284 |
| pf median | 0,738 | 0,498 | 0,720 | 0,798 | 0,783 | 0,843 |
| win median | 0,255 | 0,287 | 0,299 | 0,352 | 0,346 | 0,307 |
| dd median | 297 | 1188 | 294 | 100 | 237 | 175 |
| n median (trades) | 1228 | 2803 | 1515 | 700 | 1534 | 1213 |
| val_exp lipsă | 0 | 0 | 0 | 0 | 0 | 0 |
| Extremă notabilă | — | dd/n/sumR extreme ale grupului | — | cel mai mic dd | cel mai aproape de breakeven | cel mai mare pf |

─────────────────────────────────────────────
CONTRIBUȚIE LA ACOPERIRE (per P1_COVERAGE_PLAN):
  Celule completate: 2a rândul zero-profit (6/6 familii ca cunoaștere negativă → A.3.2);
  gardă anti-survivorship (A.4.2) satisfăcută pentru familiile de eșec.
  Coverage Confidence: rămâne Medium (în urcare) — RI-REPORT-0005 (side/temporal per-familie non-S1)
  rămâne deschis. Fără upgrade formal acum.
─────────────────────────────────────────────
*Sfârșitul RI-REPORT-0004. Doar acest raport, conform mandatului. Nu s-a început RI-REPORT-0005.*
─────────────────────────────────────────────
