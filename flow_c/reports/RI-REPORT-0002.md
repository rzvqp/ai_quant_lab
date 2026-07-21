─────────────────────────────────────────────
FLOW C — RESEARCH REPORT
ID:              RI-REPORT-0002
Data:            2026-07-21
Autor:           Research Intelligence
Nivel epistemic: cunoaștere-observațională (descriptiv, marginal)
Încredere:       scăzută (C1 — Speculativ). Un singur corpus, prima tratare a acestor coloane,
                 fără falsificare, fără mecanisme, fără corelații. Fidelitate descriptivă ridicată
                 (corpus reprodus bit-exact).
─────────────────────────────────────────────
BAZA DE DOVEZI (Evidence base)
  • Sursă:      results/FAMILY_RESULTS.parquet (motor mstrat v2, Alpha Discovery, S1–S20).
                Reprodus bit-exact (results/reproduction_v2/comparison.json, diff 0.0).
                Instrument/TF: XAUUSD, grilă M15 (per docs lab). Unități presupus în R.
  • Fereastră:  aceeași ca RI-REPORT-0001 (years=4; activitate până la months=27).
  • Completitudine: val_exp are 176 valori lipsă (n=1796/1972); trim5 are 16 lipsă (n=1956).
                Restul coloanelor: n=1972 complet.
  • NON-fabricare: fiecare cifră derivă din citirea directă a coloanelor parquet-ului.
─────────────────────────────────────────────
CE AR FALSIFICA ACEST RAPORT:
  O re-citire a acelorași coloane care ar da alte distribuții marginale (imposibil dacă fișierul e
  neschimbat). Interpretările (R1–R4) sunt descriptive-marginale și rămân la C1.
PLAFON EPISTEMIC:
  Descriere MARGINALĂ per coloană. NU corelează coloane între ele (ex. val_exp vs exp, concentrare vs
  fragile) — acele RELAȚII sunt 🔒 P2. NU explică (🔒 P4). NU validează. NU recomandă implementare.
─────────────────────────────────────────────

# 1. ÎNTREBAREA DE PLECARE

Care este **forma descriptivă marginală** a coloanelor de robustețe și concentrare rămase neatinse de RI-REPORT-0001 — `val_exp, t1, t3, t5, wo1, dd, win, sumR, median, trim5` — la nivelul întregului corp și în stratul profitabil (hist_prof)?

*(Coloană cu coloană, marginal. Orice relație între ele = 🔒 P2.)*

---

# 2. CORPUL DE DOVEZI

Același corpus (1972 ipoteze, S1–S20), coloanele de calitate/robustețe. Semantică (citită din valori, de confirmat definitiv de Alpha):
- `val_exp` — a doua măsură de expectancy (probabil validare/OOS).
- `t1/t3/t5` — contribuția fracțională a celor mai bune 1/3/5 tranzacții (concentrare).
- `wo1` — expectancy cu cea mai bună tranzacție eliminată (robustețe la un singur trade).
- `dd` — max drawdown (R). `win` — rată de câștig. `sumR` — sumă R. `median` — R median per trade. `trim5` — medie trunchiată 5%.

---

# 3. OBSERVAȚII (marginal, cu cifre)

**Corp întreg (n=1972 dacă nu se specifică altfel):**
- **O1 — val_exp:** mediană −0,042, medie −0,051, interval [−1,106; +1,260]; 34,2% > 0. (n=1796; 176 lipsă.)
- **O2 — concentrare t1/t3/t5:** mediane 0,024 / 0,065 / 0,103; medii 0,070 / 0,145 / 0,187; max = 1,0 la toate trei (există ipoteze unde 1/3/5 trade-uri = 100% din rezultat). Minime negative extreme la t3/t5 (−2,55 / −4,78).
- **O3 — wo1:** mediană −0,140, medie −0,145; doar **12,6% > 0** pe tot corpul.
- **O4 — dd:** mediană 53,4, medie 139,2, p95 558,3, max **2000,8**; 98,2% > 0. Distribuție puternic asimetrică la dreapta.
- **O5 — win:** mediană 0,363, interval [0; 1].
- **O6 — sumR:** mediană −32,0; p75 = −5,1 (peste 75% din corp are sumR negativ).
- **O7 — median (R median per trade):** mediană −1,04 — tranzacția **tipică** pierde ~1R.
- **O8 — trim5:** mediană −0,233.

**Stratul profitabil (hist_prof, n=357):**
- **O9 — val_exp:** mediană +0,095, 69% > 0 (n=247; **110 din cei 357 profitabili nu au val_exp**).
- **O10 — concentrare:** mediane t1 0,081 / t3 0,180 / t5 0,255; medii 0,192 / 0,357 / **0,414** — în setul profitabil, top-5 trade-uri contribuie în medie ~41%.
- **O11 — wo1:** mediană +0,030, 69,5% > 0 → **30,5% dintre profitabili au wo1 ≤ 0** (eliminarea celui mai bun trade îi face ne-pozitivi).
- **O12 — dd:** mediană 12,9, max 139,8 (mult sub corpul întreg).
- **O13 — win:** mediană 0,443 — **sub 50% chiar în setul profitabil**.
- **O14 — median per trade:** mediană −0,231 — tranzacția tipică rămâne negativă chiar printre profitabili.
- **O15 — trim5:** mediană −0,027 (aproape de zero).

---

# 4. INFORMAȚII (context, în interiorul aceluiași corpus)

- **I1.** La nivel de populație, `val_exp` e mai puțin negativ decât `exp` (mediane −0,042 vs −0,116). *(Două marginale prezentate alături; divergența per-ipoteză = 🔒 P2.)*
- **I2.** În setul profitabil coexistă: rată de câștig sub 50% (O13), tranzacție mediană negativă (O14), și concentrare mare în top-5 trade-uri (O10). Profitabilitatea NU vine dintr-o tranzacție tipică pozitivă. *(Fapt descriptiv; „de ce" = 🔒 P4.)*
- **I3.** Robustețea la un singur trade e fragilă chiar în vârful setului: ~31% dintre profitabili devin ne-pozitivi fără cel mai bun trade (O11).
- **I4.** Completitudinea datelor nu e uniformă: `val_exp` lipsește pentru 176 de ipoteze (și pentru 110 din cei 357 profitabili) — o limitare de acoperire, nu doar un detaliu.

---

# 5. REGULARITĂȚI GĂSITE (C1 — Speculativ)

- **R1 — Concentrare ridicată în setul profitabil:** top-5 trade-uri ~41% din contribuție (medie), cu cazuri de 100% la 1 trade. Distribuția de concentrare e mult mai grea în stratul profitabil decât în corpul întreg.
- **R2 — Profitabilitatea coexistă cu win-rate sub-50% și tranzacție mediană negativă** (O13/O14). Semnătură descriptivă consecventă în tot stratul profitabil.
- **R3 — Robustețe la-un-singur-trade slabă în vârf:** ~31% dintre profitabili au wo1 ≤ 0 (R4-legat de flag-ul `fragile`, dar corelația explicită = 🔒 P2).
- **R4 — `val_exp` e sistematic mai puțin negativ decât `exp` la nivel de marginale populaționale**, dar cu completitudine lacunară (176 lipsă). *(Marginal; relația per-ipoteză = 🔒 P2.)*

*Încredere R1–R4: C1. Un singur corpus, marginale, fără falsificare, fără corelații.*

---

# 6. CE NU EXPLICĂ RAPORTUL

- **DE CE** apare concentrarea / win-rate-ul sub 50% / fragilitatea la un trade — mecanisme, 🔒 P4.
- Orice **relație între coloane** — 🔒 P2: `val_exp` vs `exp` (divergență per-ipoteză), concentrare (t1/t3/t5) vs flag `fragile`, `wo1` vs `exp`, `dd` vs familie/side.
- Semantica definitivă a `val_exp` (validare/OOS?) — de confirmat de Alpha.
- Cauza celor 176 de valori `val_exp` lipsă.

---

# 7. TRIMITERI (doar întrebări, fără ipoteze)

- **Candidat RQ:** De ce ~31% dintre profitabili colapsează fără un singur trade (wo1 ≤ 0)? — dezvoltarea ca relație wo1×fragile = **Meta Analysis / Strategy Diagnostic**, 🔒 P2/P3.
- **Candidat RQ:** Ce înseamnă exact `val_exp` și de ce lipsește pentru 110 din 357 de profitabili? — întrebare de acoperire + semantică, deschisă.
- **Indicație Meta (P2):** divergența marginală `val_exp` (−0,042) vs `exp` (−0,116) sugerează o suprafață relațională de examinat *ca relație per-ipoteză* — strict P2.
- **Indicație Meta (P2):** concentrarea (t1/t3/t5) vs flag-ul `fragile` (37% din profitabili) — juxtapunerea lor e coada relațională naturală.

*Stare: toate OPEN. Nicio ipoteză formulată. Adăugate în coada relațională P2 (fără a reordona planul — Plan Revision Rules §7.3).*

─────────────────────────────────────────────
CONTRIBUȚIE LA ACOPERIRE (per P1_COVERAGE_PLAN):
  Celule completate: 2b — val_exp, t1, t3, t5, wo1, dd, win, sumR, median, trim5 (marginal);
  2c — regiunea „fragili (formă)" descrisă marginal.
  Coverage Confidence: rămâne Medium (în urcare) per estimarea planului §5 — S1 dedicat,
  familiile de eșec și side-per-familie rămân deschise. Re-rating formal doar la gate-ul de review.
─────────────────────────────────────────────
*Sfârșitul RI-REPORT-0002. Doar acest raport, conform mandatului. Nu s-a început RI-REPORT-0003.*
─────────────────────────────────────────────
