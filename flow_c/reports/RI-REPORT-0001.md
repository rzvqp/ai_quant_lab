─────────────────────────────────────────────
FLOW C — RESEARCH REPORT
ID:              RI-REPORT-0001
Data:            2026-07-21
Autor:           Research Intelligence
Nivel epistemic: cunoaștere-observațională (descriptiv)
Încredere:       scăzută (C1 — Speculativ). Justificare: un singur corpus, primă trecere,
                 fără pas de falsificare (Faza 1 = citire), fără mecanisme (interzis).
                 NOTĂ: fidelitatea descriptivă e ridicată (corpus reprodus bit-exact); maturitatea
                 interpretativă e scăzută. Vezi frecarea F1.
─────────────────────────────────────────────
BAZA DE DOVEZI (Evidence base)
  • Sursă:      results/FAMILY_RESULTS.parquet (motor mstrat v2, Alpha Discovery, S1–S20).
                Reprodus bit-exact: results/reproduction_v2/comparison.json — numeric_max_abs_diff = 0.0
                pe toate coloanele, id_set_identical=true, bool_mismatch_count=0.
                Provenanță instrument/TF (din docs lab): XAUUSD (tick 0.1) — docs/MIN_STOP_FLOOR_PREREG.md;
                grilă M15 (900 s) — docs/SYNTHETIC_PRICE_GENERATOR.md.
  • Fereastră:  years=4 pe hypotheză; activitate de tranzacționare până la months=27 (coloanele years/months).
                Fereastra calendaristică exactă nu e auto-descrisă în artefact — vezi frecarea F4.
  • NON-fabricare: fiecare cifră de mai jos derivă din citirea directă a parquet-ului de mai sus.
─────────────────────────────────────────────
CE AR FALSIFICA ACEST RAPORT:
  O re-citire a aceluiași parquet care ar da alte numărători de funnel / compoziție decât cele
  raportate (imposibil dacă fișierul e neschimbat — de aceea încrederea e despre INTERPRETARE, nu
  despre numărători). Interpretările descriptive (R1–R3) ar fi slăbite dacă un corpus viitor cu
  eșantionare echilibrată între familii nu ar reproduce concentrarea observată.
PLAFON EPISTEMIC:
  Acest document NU validează nimic. NU propune mecanisme. NU compară axe independente. NU recomandă
  implementare. Validarea aparține exclusiv Alpha Discovery.
─────────────────────────────────────────────

# 1. ÎNTREBAREA DE PLECARE

Care este **forma descriptivă** a populației complete de 1972 de ipoteze S1–S20 produse de Alpha Discovery — cum se distribuie profitabilitatea istorică și supraviețuirea la filtre, și ce structură are corpul (compoziție per familie, echilibru de side, fragilitate)?

*(Întrebare pur descriptivă, pe UN singur corpus. Orice corelație cross-axă e exclusă din format — vezi §6 și §7.)*

---

# 2. CORPUL DE DOVEZI

Un singur corpus: tabelul agregat de rezultate de familie, 1972 rânduri × 22 coloane, o linie per ipoteză. Coloane-cheie citite: `fam, id, n, exp, pf, dd, win, val_exp, months, pos_months, years, side, hist_prof, research_worthy, fragile`. 20 de familii (S1…S20). Corpus reprodus bit-exact (vezi Baza de dovezi).

Funnel headline (din reproduction_v2/comparison.json → headline_base):
`generated 1972 → valid 1800 → hist_profitable 357 → research_worthy 130`.

---

# 3. OBSERVAȚII (fapte brute, cu sursă)

- **O1 — Funnel.** 1972 generate → 1800 valide (172 invalide, 8,7%) → 357 istoric-profitabile (18,1% din generate; 19,8% din valide) → 130 research-worthy (6,6% din generate).
- **O2 — Compoziție puternic concentrată.** S1 = 1152 din 1972 de ipoteze (58,4% din tot corpul). Restul familiilor sunt mult mai mici (ex. S19 = 12, S14 = 16, S7 = 24). Eșantionarea per familie este puternic dezechilibrată.
- **O3 — Concentrarea se propagă în câștigători.** Din cele 357 istoric-profitabile, S1 aduce 261 (73,1%).
- **O4 — Side echilibrat prin design la generare.** 934 long / 934 short / 104 both — o simetrie construită.
- **O5 — (fapt joint, brut, ne-interpretat).** Printre cele 357 istoric-profitabile: 271 long / 86 short. *(Raportat ca numărătoare brută; NU îl interpretez ca relație — vezi §7.)*
- **O6 — Cunoaștere negativă.** 6 familii au produs ZERO ipoteze istoric-profitabile: S4, S7, S10, S11, S12, S15.
- **O7 — Fragilitate.** Flag-ul `fragile` apare de 133 de ori, și **toate** cele 133 sunt în interiorul setului istoric-profitabil → 133/357 = 37,3% dintre profitabile sunt marcate fragile.
- **O8 — Distribuția expectancy.** medie −0,115, mediană −0,116, doar 18,1% au exp>0, min −1,095, max 0,915. Populația e centrată negativ.
- **O9 — Extremele co-apar cu familii mici.** exp_max ridicat: S19 = 0,915 (n_hyp=12), S14 = 0,578 (16), S6 = 0,497 (32). S6 este cunoscut independent ca extremă tiny-stop/outlier (results/matched_null_validation/pilot_prereg.json: „known tiny-stop/outlier extreme, maxDD 89.8R").

---

# 4. INFORMAȚII (observațiile puse în context, în interiorul aceluiași corpus)

- **I1.** Rata hist_prof (18,1% din generate) ≈ ponderea exp>0 (18,1%). La nivel de populație, „istoric-profitabil" coincide aproape complet cu „expectancy in-sample pozitiv".
- **I2.** research_worthy (130) este un subset strict: doar 36% dintre cele 357 profitabile ajung research-worthy; ~64% din profitabile sunt filtrate înainte de a fi considerate demne de studiu.
- **I3.** Rata hist_prof per familie (numărător/total), pusă lângă mărimea familiei: S1 22,7% (261/1152), S5 20,8% (20/96), S9 37,5% (12/32), S14 37,5% (6/16), S17 25% (6/24). Familiile mici S9/S14 au rată mare de „hit" pe eșantion foarte mic → semnal de precauție la lățimea căutării (protocol §2, filtrul 4). *(Prezint ratele ca descriere stratificată; nu ca afirmație de relație cauzală.)*

---

# 5. REGULARITĂȚI GĂSITE (ce ține repetabil — cunoaștere observațională, C1)

- **R1 — Corpul e dominat de enumerare de o singură familie (S1), iar dominanța se propagă în fiecare numărătoare din aval.** Orice titlu de forma „câți câștigători avem" este, în proporție covârșitoare, o afirmație despre S1 (58% din corp, 73% din profitabile).
- **R2 — Expectancy-ul extrem la nivel de ipoteză individuală co-apare consecvent cu familii de eșantion mic** (S19/S14/S6). Forma e consistentă cu efecte de lățime-de-căutare / outlier; cazul S6 este deja cunoscut ca artefact tiny-stop. *(Formă descriptivă, nu afirmație validată.)*
- **R3 — Eticheta „profitabil" și eticheta „robust" diverg substanțial în același corpus:** o minoritate mare (37%) din setul profitabil este auto-marcată fragilă.

*Nivel de încredere pentru R1–R3: C1 (Speculativ) — un singur corpus, primă trecere, fără pas de falsificare, fără mecanism. Vezi §8 din protocol.*

---

# 6. CE NU EXPLICĂ RAPORTUL (limite, zone neatinse)

- Nu explică **DE CE** apare vreuna dintre regularități — mecanismele sunt interzise în această fază.
- Nu compară cross-axă (familie × outcome, side × outcome, backtest × live, TF × TF). În momentul în care aș face-o, documentul ar înceta să fie Research Report și ar deveni Meta Analysis (regula de graniță §1 din formate). O2/O3/O5/I3 ating pragul; le opresc la numărătoare brută.
- Nu spune dacă vreo ipoteză sau familie este „reală" — validarea e a lui Alpha Discovery.
- Nu a analizat coloana `val_exp` (posibil expectancy de validare/OOS) și nici `t1/t3/t5/wo1` (contribuția tranzacțiilor de vârf / expectancy fără cea mai bună) — rămân zone neatinse pentru un raport viitor.
- Nu a coborât la nivel de configurație/parametru intra-familie (nu e prezent în tabelul agregat; ar cere citirea configs).
- Fereastra calendaristică exactă nu e auto-descrisă în artefact (F4).

---

# 7. TRIMITERI (ce se naște de aici — DOAR întrebări, fără ipoteze)

*Constrângere Faza 1: „nu inventa ipoteze noi". Prin urmare emit doar Research Questions (întrebări) și indicații de Meta Analysis pentru faze viitoare — niciun mecanism, nicio ipoteză formulată.*

- **Candidat Research Question (RQ):** Populația hist_prof este puternic dezechilibrată spre long (271/86), deși generarea e simetrică (934/934). *Ce produce acest dezechilibru?* — întrebare deschisă; dezvoltarea ei ca relație este muncă de **Meta Analysis** (side × outcome), nu de Research Report.
- **Candidat RQ:** Co-apariția expectancy-extrem × familie-mică (R2) — este artefact de lățime-de-căutare sau semnal? Parțial pre-răspuns pentru S6 (artefact cunoscut); rămâne deschis ca clasă. Aparține unei **Meta Analysis** (mărime-familie × extreme).
- **Candidat RQ:** De ce 37% dintre profitabile sunt fragile — ce distinge cele 224 ne-fragile de cele 133 fragile în interiorul setului profitabil? Dezvoltarea = **Meta Analysis / Strategy Diagnostic**, nu RR.
- **Indicație de Meta Analysis (faza viitoare):** stratificarea outcome-ului pe side și familie ca *relații* (interzis în RR) este pasul natural următor pentru O2/O3/O5/I3.

*Stare: toate rămân OPEN. Niciuna nu se auto-promovează. Nicio ipoteză nu a fost formulată.*

─────────────────────────────────────────────
*Sfârșitul RI-REPORT-0001. Un singur raport, conform mandatului Fazei 1. Nu s-a început un al doilea.*
─────────────────────────────────────────────
