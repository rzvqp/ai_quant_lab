─────────────────────────────────────────────
FLOW C — RESEARCH REPORT
ID:              RI-REPORT-0003
Data:            2026-07-21
Autor:           Research Intelligence
Nivel epistemic: cunoaștere-observațională (descriptiv)
Încredere:       scăzută (C1 — Speculativ). O singură populație (S1), prima tratare dedicată,
                 fără falsificare, fără mecanisme, fără corelații. Fidelitate descriptivă ridicată
                 (corpus reprodus bit-exact).
─────────────────────────────────────────────
BAZA DE DOVEZI (Evidence base)
  • Sursă:      results/FAMILY_RESULTS.parquet, subsetul fam=="S1" (1152 rânduri).
                Reprodus bit-exact (comparison.json, diff 0.0). XAUUSD, grilă M15. Unități presupus R.
  • Fereastră:  years până la 4; months până la 27.
  • Completitudine: în S1, `val_exp` lipsește pentru 176 rânduri; `trim5` pentru 16.
  • NON-fabricare: fiecare cifră derivă din citirea directă a subsetului S1.
─────────────────────────────────────────────
REGULI DE ÎNCADRARE (mandat CEO pentru acest raport):
  • S1 e tratat ca POPULAȚIE ÎN SINE, cu propriul „normal".
  • Comparațiile cu corpul sunt EXCLUSIV baseline-uri descriptive ETICHETATE — NU afirmații de
    superioritate. Corpul-baseline INCLUDE S1 (58% din el), deci NU e o referință independentă;
    comparațiile sunt descriptive, nu inferențiale.
  • NU explic de ce S1 domină (🔒). NU infer că S1 e mai bun / mai robust / privilegiat (🔒 — necesită
    analiză relațională autorizată separat, P2). Relațiile cross-axă și mecanismele: 🔒 P2 / P4.
─────────────────────────────────────────────
CE AR FALSIFICA ACEST RAPORT:
  O re-citire a subsetului S1 care ar da alte distribuții (imposibil dacă fișierul e neschimbat).
PLAFON EPISTEMIC:
  Descriere a populației S1. NU validează, NU explică, NU compară inferențial, NU recomandă.
─────────────────────────────────────────────

# 1. ÎNTREBAREA DE PLECARE

Care este „normalul" descriptiv al familiei S1, tratată ca populație de sine stătătoare — mărime, funnel, distribuții de rezultat, side, marginale de robustețe, completitudine, extreme și concentrare internă?

---

# 2. CORPUL DE DOVEZI

Subsetul S1: 1152 ipoteze (58,4% din corpul de 1972). Familia cea mai numeroasă. Aceleași ~22 coloane. `val_exp` lipsă în 176 rânduri — de notat că acestea reprezintă **întreaga lipsă de `val_exp` din corp** (176 din 176 sunt în S1).

---

# 3. OBSERVAȚII (cu cifre; comparațiile = baseline descriptiv etichetat)

**Populație & funnel:**
- **O1 — Mărime:** 1152 ipoteze (58,4% din corp).
- **O2 — Funnel S1:** 1152 generate → hist_prof **261** (22,7%) → research_worthy **90** (7,8%); fragile **109**. *(„valid" e o metrică headline la nivel de corp, nedecompozabilă per-familie din acest artefact — limitare de acoperire.)*
- **O3 — Baseline descriptiv (NU superioritate):** rata hist_prof S1 = 22,7% | baseline corp = 18,1%. Rata research_worthy S1 = 7,8% | baseline corp = 6,6%. *(Corpul include S1; comparație descriptivă, nu inferențială.)*
- **O4 — Fragilitate:** toate cele 109 fragile din S1 sunt printre cei 261 profitabili → **41,8% dintre profitabilii S1 sunt fragili**.

**Side:**
- **O5 — Side S1:** 576 long / 576 short / **0 both** (perfect echilibrat prin design; cele 104 „both" din corp sunt în alte familii).

**Distribuții de rezultat (S1 med | baseline corp med):**
- **O6 — exp:** −0,089 | −0,116; interval S1 [−0,470; +0,391].
- **O7 — pf:** 0,815 | 0,787; **pf max = ∞** în S1 (ipoteze cu pierdere brută zero — extremă de date).
- **O8 — dd:** 30,7 | 53,4; S1 p95 = 213,8; **S1 max = 440,5**.
- **O9 — win:** 0,384 | 0,363; interval [0; 1].
- **O10 — sumR:** −16,3 | −32,0; interval S1 [−437,7; +91,7].
- **O11 — median (R median/trade):** −0,712 | −1,039.
- **O12 — trim5:** −0,201 | −0,233.
- **O13 — n (nr. trade-uri):** median 209 | baseline corp 379; interval S1 [2; 2065].

**Marginale de robustețe/concentrare în S1 (S1 med | baseline corp med):**
- **O14 — val_exp:** −0,025 | −0,042 (n=976 în S1 din cauza lipsei).
- **O15 — concentrare t1/t3/t5:** 0,041 / 0,112 / 0,174 | 0,024 / 0,065 / 0,103. La profitabilii S1: t5 median = **0,408**.
- **O16 — wo1:** −0,121 | −0,140. La profitabilii S1: **32,6% au wo1 ≤ 0** (85 din 261).
- **O17 — profitabili S1:** win median = 0,50; median-trade = −0,024.

**Extreme interne:** exp max +0,391 / min −0,470; dd max 440,5; pf max ∞; t5 max 1,0 (concentrare de 100% pe ≤5 trade-uri în unele ipoteze).

**Temporal:** months până la 27, years până la 4; pos_months median 9 (baseline corp 8).

---

# 4. INFORMAȚII (context, în interiorul S1)

- **I1.** ~42% dintre profitabilii S1 sunt fragili (O4) — proporția de fragilitate în vârful S1 e substanțială.
- **I2.** Semnătura descriptivă a stratului profitabil S1: win median exact 0,50, tranzacție mediană ușor negativă (−0,024), concentrare t5 ~41% (O15/O17). Profitabilitatea S1 nu vine dintr-o tranzacție tipică pozitivă. *(descriptiv; „de ce" = 🔒 P4.)*
- **I3.** ~33% dintre profitabilii S1 au wo1 ≤ 0 (O16) — dependență critică de cel mai bun trade, în linie descriptivă cu observația de corp din RI-REPORT-0002 (~31%).
- **I4.** Ipotezele S1 au median 209 trade-uri, sub baseline-ul de corp de 379 (O13) — populație descriptiv diferită ca frecvență de tranzacționare. *(baseline etichetat, nu inferență.)*
- **I5.** Întreaga lipsă de `val_exp` din corp (176) e localizată în S1 — un fapt de completitudine, nu de performanță.

---

# 5. REGULARITĂȚI GĂSITE (C1 — Speculativ, intern S1)

- **R1 — Fragilitate substanțială în vârf:** ~42% dintre profitabilii S1 fragili; ~33% cu wo1 ≤ 0.
- **R2 — Profitabilitatea S1 coexistă cu win-rate ~0,50 și tranzacție mediană negativă**, cu concentrare mare în top-5 trade-uri.
- **R3 — S1 poartă extreme de date proprii:** pf = ∞, dd până la 440,5, concentrare până la 100%.
- **R4 — Completitudine lacunară localizată:** toată lipsa de `val_exp` din corp e în S1.

*Încredere R1–R4: C1. O populație, marginale, fără falsificare, fără corelații, fără inferență de superioritate.*

---

# 6. CE NU EXPLICĂ RAPORTUL

- **DE CE domină S1** (58% din corp) — 🔒 neexplicat, prin mandat.
- Dacă S1 e „mai bun / mai robust / privilegiat" — 🔒 NEINFERAT; rata hist_prof mai mare (O3) e un baseline descriptiv într-un corp care include S1, nu o afirmație de superioritate. Necesită analiză relațională autorizată (P2).
- Orice **relație între coloane / între S1 și restul** — 🔒 P2.
- **Mecanismele** (concentrare, fragilitate, val_exp lipsă) — 🔒 P4.
- Decompoziția „valid" per-familie și semantica `val_exp` — negăsibile în artefact.

---

# 7. TRIMITERI (doar întrebări, fără ipoteze)

- **Candidat RQ:** Rata hist_prof mai mare a S1 (22,7% vs baseline 18,1%) este un efect real sau un artefact de enumerare (S1 = 1152 extrageri)? — strict relațional/statistic, 🔒 P2.
- **Candidat RQ:** De ce e localizată în S1 întreaga lipsă de `val_exp`? — întrebare de acoperire + proveniență, deschisă.
- **Candidat RQ:** Fragilitatea vârfului S1 (42% fragil, 33% wo1≤0) diferă de a altor familii? — comparație inter-familii = **Meta Analysis**, 🔒 P2.
- **Indicație Meta (P2):** „S1 vs restul corpului" ca relație — natural next, dar interzis în P1.

*Stare: toate OPEN. Nicio ipoteză formulată. Adăugate în coada relațională P2 fără a reordona planul (§7.3).*

─────────────────────────────────────────────
CONTRIBUȚIE LA ACOPERIRE (per P1_COVERAGE_PLAN):
  Celule completate: 2a rândul S1 (profitabilitate, interval exp/pf, side, temporal, distribuție
  internă, robustețe) → satisface A.3.5 (S1 dedicat).
  Coverage Confidence: rămâne Medium (în urcare) — familiile de eșec (RI-REPORT-0004) și
  side/temporal per-familie non-S1 (RI-REPORT-0005) rămân deschise. Fără upgrade formal acum.
─────────────────────────────────────────────
*Sfârșitul RI-REPORT-0003. Doar acest raport, conform mandatului. Nu s-a început RI-REPORT-0004.*
─────────────────────────────────────────────
