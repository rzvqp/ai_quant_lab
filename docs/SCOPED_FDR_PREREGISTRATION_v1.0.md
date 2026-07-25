# SCOPED GLOBAL-FDR — PRE-REGISTRATION (committed BEFORE any p-value)

**Document ID:** STAT-SCOPED-FDR-PREREG-v1.0 · **Autor:** Statistician (Research Lab) · **Data:** 2026-07-25
**Autoritate:** CEO 2026-07-25 — rulează FDR global DOAR pe regimul în care motorul matched-null e validat.
**Statut la comitere:** ZERO valori p calculate. Enumerarea subsetului e derivată din câmpul `stop` al gramaticii + eligibilitatea înghețată n≥25; nicio statistică de test și niciun p nu au fost atinse.
**Bază de cod:** `code/matched_null.py` (Test B validat, unstratified + ATR-scaled), cherry-pick-uit pe `statistician-foundation` (D3 RESOLVED; original `28c35b6`→`aa5bee3`→`69747fd`).

---

## 0. De ce scopat, și de ce nu e selecție post-hoc

Motorul matched-null a fost validat (calibrare/putere/adversarial) **doar** pentru regimul de stop **1.5×ATR** pe semnale generice. Familiile cu stop **structural** (sursele D2) nu au fost niciodată în bateria de calibrare → pentru ele motorul nu e „calibrat pe date murdare", ci **NECALIBRAT**. Regula corectă a statisticii: **rulezi testul unde e validat, nu în afara domeniului lui.** Subsetul nu e ales pentru că trece; e ales pentru că e singurul domeniu în care un p are semnificație definită. Familiile cu stop structural rămân în afara domeniului până la închiderea D2.

---

## 1. Criteriul de apartenență la subset (derivat din câmpul `stop`, NU din rezultate)

Regula: **o ipoteză e IN-domain ⟺ `h['stop'] == 'atr'`.** Verificat în cod: în FIECARE familie care oferă opțiunea, `h['stop']=='atr'` produce exact `stop = o[ei] − dir·1.5·atr[·]` (mstrat.py liniile 211/236/255/275/297/318/336/359/380/396/410/424/439/452/467/480/493/506/523) — regimul de stop pe care `synth_price.py` l-a calibrat. Zero atr-stops cu alt multiplu.

**Excluse (în afara domeniului validat), cu motiv:**
- **Stopuri structurale/level (1532 ipoteze):** valorile `stop` = `structural, beyond_sweep, beyond_ext, beyond_level, bar, or_opp, prev_ext, ext, struct, level`. Toate plasează stopul la extrema/nivelul local (± 2 ticks) → pot sta ~0 de intrare → regimul D2. Motorul e NECALIBRAT aici.
- **`ema` (12 ipoteze, S7):** stop la nivelul unui EMA = regim terț „distanță-de-indicator", nici 1.5×ATR nici range-local. **Ambiguu → exclus** (nu a fost în nicio baterie de validare).
- **`atr`-stop dar n<25 (16 ipoteze):** IN-domain ca regim, dar INELIGIBILE (sub pragul înghețat n≥25) → excluse din `m`, fără p fabricat (conform EMPIRICAL_PVALUE_SPEC: invalizii = ineligibili, excluși din m, NU primesc p=1).

**Numărătoare (enumerare gramaticală, `results/matched_null_validation/subset_prereg_enumeration.json`):**
| categorie | count |
|---|---|
| Total gramatică | **1972** |
| ATR-stop (IN-domain, regim validat) | 428 |
| — din care valide (n≥25) = **UNIVERSUL TESTAT** | **412** |
| — ATR-stop dar n<25 (excluse, ineligibile) | 16 |
| Structural/level-stop (excluse, în afara domeniului = D2) | 1532 |
| `ema` (excluse, regim terț ambiguu) | 12 |
| **TOTAL EXCLUS din cei 1972** | **1560** |

S1 e **integral exclus** (toate cele 1152 sunt `beyond_sweep`/`structural` — S1 nu are opțiune `atr`).

---

## 2. `m` efectiv și pragul BH

- **m = 412** (ipoteze ATR-stop valide n≥25).
- **Prag BH rang-1** (Benjamini–Hochberg, α=0.05): α/m = 0.05/412 = **1.214e-4**.
- Procedura BH (step-up): sortează p crescător; respinge rangurile 1..k* unde k* = cel mai mare k cu p_(k) ≤ k·α/m. Pragul cel mai permisiv (rang m) = α = 0.05.
- **Notă de transparență privind „valid":** EMPIRICAL_PVALUE_SPEC citează un univers global „valid" m=1552 (mai strict decât n≥25=1800), cu o definiție nespecificată în artefactele mele. Folosesc eligibilitatea reproductibilă **n≥25** (frozen), care dă un `m` mai MARE → prag BH mai MIC → mai greu de declarat un supraviețuitor. Direcție conservatoare, aleasă înainte de rezultate.

---

## 3. Configurație (singura validată)

- **Matched-null unstratified + ATR-scaled** (`strata=None`), exact configurația care a trecut calibrare/putere/adversarial. **Nulurile stratificate session×vol NU sunt validate → NU se folosesc.**
- Statistica = media R/tranzacție a tranzacțiilor executate; H0: mean_R ≤ 0, one-sided; p = coada dreaptă (fracția de medii-null ≥ observat), p=(k_ge+1)/(B+1).
- Nulul executat prin `mstrat.simulate` (engine v2, stop-floor activ) — profil realizat risc/ATR, timing de intrare aleator, direcție/exit/costuri/overlap păstrate.
- **Segment de calcul:** RESEARCH (primele 60%, `d[:0.6n]`). Holdout SEALED, niciodată încărcat. Validation (20%) = OOS separat (§5).

---

## 4. Monte-Carlo adaptiv + regula de nedecis

- **MC-1 TRIAGE** B=20.000. **MC-2 REFINEMENT** B≥200.000 cu CI Wilson. **MC-3 CONFIRMATION** B≥1.000.000. p=(k_ge+1)/(B+1). Seminte și contoare (k_ge, B) salvate per ipoteză.
- **Oprire secvențială (pre-autorizată de EMPIRICAL_PVALUE_SPEC §"sequential MC / stopping bounds"):** la MC-1, o ipoteză se oprește imediat ce `k_ge` garantează p>0.05, fiindcă o ipoteză cu p>0.05 **nu poate fi respinsă de BH la niciun rang** (pragul BH maxim = α = 0.05). La B=20.000, bound = `k_ge > 1000`. Oprirea NU schimbă p pentru ipotezele care ar putea fi respinse (acelea rulează la B plin cu ACEEAȘI secvență RNG). Reproducibilitate păstrată.
- **Escaladare:** orice ipoteză care NU e eliminată la MC-1 (candidat la respingere BH) → MC-2 → MC-3.
- **Regula UNRESOLVED:** dacă CI-ul Wilson al lui p intersectează pragul BH aplicabil ipotezei → status **UNRESOLVED — MORE SIMULATIONS REQUIRED** (nu se forțează un verdict).

## 5. Research și validare — RAPORTATE SEPARAT, NICIODATĂ COMBINATE

- FDR-ul primar se aplică pe p-urile de **RESEARCH** (m=412). Decizia de supraviețuire = BH pe research.
- Pentru ORICE supraviețuitor BH de research, p-ul de **VALIDATION** (segment OOS 20%, B=10.000, sămânță separată) se raportează **separat**, ca a doua probă independentă. Cele două p nu se agregă niciodată într-un singur număr.

## 6. Criterii de succes / eșec (scrise ÎNAINTE de rezultate)

- **SUPRAVIEȚUITOR** ⟺ p-ul de research trece BH (α=0.05, m=412) ȘI, dacă a fost nevoie de escaladare, MC-3 confirmă cu CI sub pragul BH al ipotezei (nu UNRESOLVED).
- **ZERO SUPRAVIEȚUITORI** = rezultat VALID și așteptat (pilotul 2026-07-13: cel mai bun p research = 0.0049 ≫ prag). Dacă iese așa, se scrie **ca atare** — fără înmuiere, fără prag alternativ, fără căutarea unui sub-subset care trece, fără re-rulare pentru alt număr.
- **≥1 SUPRAVIEȚUITOR** → se raportează cu p-ul de validation separat; devine un motiv concret că un edge poate exista în regimul curat → susține închiderea D2 (WP-1..4).
- **UNRESOLVED** → dacă vreun candidat rămâne cu CI peste prag după MC-3.

## 7. Interdicții (pre-înregistrate)

Holdout SEALED indiferent de rezultat. NU se extinde universul după vederea rezultatelor. NU se rulează pe familii cu stop structural (în afara domeniului). NU se ajustează praguri. NU se re-rulează pentru alt număr. Raportare indiferent de semn, cu numărul exact de excluși (1560) și de ce.

---

**Fișiere de rezultat (se scriu DUPĂ această comitere):** `results/matched_null_validation/scoped_fdr_{prereg_ids.json,research.parquet,summary.json,seeds.json}` + `docs/SCOPED_FDR_RESULT_v1.0.md`.
