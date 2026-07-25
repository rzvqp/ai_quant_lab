# TRANSFERABILITY DETERMINATION — `matched_null@v1` (VE / F6) → `mstrat.simulate`

**Document ID:** STAT-TRANSFER-DET-v1.0
**Data:** 2026-07-25 · **Autor:** Statistician (Research Lab)
**Autoritate:** CEO 2026-07-25 — reactivare pe Sarcina 1 (`NEXT_SESSION.md`), reformulată ca determinare de transferabilitate.
**Bază de analiză (pin):** `d453b27` (`statistician-foundation`). Notă: tip-ul remote a avansat la `6d8b634` în timpul sesiunii (push-uri concurente ale altor divizii); analiza e ancorată la pin, `6d8b634` nu schimbă niciuna dintre intrări.
**Sferă (strict):** determinare, atât. **FĂRĂ** global-FDR, **FĂRĂ** atingerea holdout-ului, **FĂRĂ** re-rularea campaniei. Nimic executat; efortul de la §5 este dimensionat, nu rulat.

---

## 1. VERDICT

**Rețeta se transferă. Implementarea și obiectul calibrat NU.** `matched_null@v1` nu poate fi „ridicat" pe `mstrat.simulate` fără o refacere substanțială, iar înainte de orice calibrare există un **blocaj dur: defectul D2** (explozia R din stop-uri minuscule) trebuie închis întâi — altfel calibrezi un null pe o statistică contaminată, adică validezi obiectul greșit.

Rezumat pe un rând: **PROTOCOLUL** F6 (serii de PREȚ sintetic la scală reală → aceeași cale → baterie null/putere/seed) este reutilizabil; **STATISTICA**, **NULUL** și **HARNESS-UL** sunt specifice VE și trebuie reconstruite pentru `mstrat`.

**Corecție acceptată (CEO 2026-07-25):** F6 **nu a deblocat campania**. A dovedit *rețeta*, nu *proprietatea*. F6 a validat `matched_null@v1` pentru pipeline-ul propriu al VE (celule eveniment sesiune×direcție), nu vreo proprietate a lui `mstrat.simulate`.

---

## 2. CE A VALIDAT F6, EXACT

- **Obiect VE:** `matched_null@v1` pe celule de eveniment (direcție × sesiune).
- **Statistică VE:** media *excess-ului forward-K6 în PREȚ* (excess = forward return − baseline de sesiune). Mărime **liniară**, în unități de preț.
- **Null VE** (`ve/methods/matched_null.py::_cell_p`): pentru fiecare celulă, B trageri care reeșantionează `len(ex)` valori **cu înlocuire** din `pool` (excess-ul tuturor barelor sesiunii); p = fracția de medii-null ≤ media observată. Pur **reeșantionaj la nivel de array** — fără motor, fără exit-uri, fără stop, fără R.
- **Calibrare F6:** serii de PREȚ random-walk la scala XAUUSD (σ₁ₕ=5.4$, wick 1.7$), aceeași cale (PDH/PDL→sesiuni→sweep-reject→forward K6→baseline→excess), fidelitate deterministă = reproduce exact numărătorile reale 135/34/42/114/40/47.
- **Verdict PASS:** KS D=0.060 p=0.765 (uniform); FPR=0.042 CI95 [0.018, 0.094] (conține 0.05); curbă de putere monotonă pe 5 magnitudini; reproducibil pe seed.

Ce a dovedit F6: **rețeta** (preț sintetic la scală reală + aceeași cale + baterie de calibrare) funcționează **pentru statistica și nulul VE**. F6 nu atinge, nu execută și nu spune nimic despre `mstrat.simulate`.

---

## 3. OBIECTUL-ȚINTĂ (`mstrat.simulate`) — DE CE E DIFERIT

| Dimensiune | VE `matched_null@v1` | `mstrat` matched-null (Test A, spec) |
|---|---|---|
| **Statistică** | media excess forward-K6, în **PREȚ** (liniar) | media **R/tranzacție**, R=pnl/risc (**raport**) |
| **Mecanism null** | reeșantionaj cu înlocuire dintr-un pool de sesiune (nivel array) | **timing de intrare aleator** prin `simulate()`, păstrând profilul **realizat** de risc/stop, exit-ul, costurile, overlap-ul 1-poziție |
| **Unitate de date** | celulă eveniment (dir, sesiune), n evenimente | serie de tranzacții per ipoteză, n≥25 tranzacții |
| **Univers** | câteva celule | **1.972** ipoteze / **m=1552** valide (FDR global) |
| **Transformare** | liniară (sumă de randamente) | **neliniară**: stop/target/trailing/time + stop-floor + costuri + overlap |
| **Contaminare** | niciuna (RW curat) | **D2 deschis**: explozia R din stop minuscul |

Miezul: uniformitatea VE se sprijină pe faptul că sub random-walk forward-returns sunt iid medie-zero → statistică **liniară** → p uniform **prin construcție**. Statistica `mstrat` e media R produsă de o mașinărie **neliniară** de exit + normalizare pe risc. Argumentul de uniformitate al VE **nu se propagă**.

---

## 4. DETERMINAREA — CE SE TRANSFERĂ / CE TREBUIE REFĂCUT

### 4.1 CE SE TRANSFERĂ (reutilizabil ca atare sau cu re-măsurare)

- **Protocolul de calibrare** (invariantul științific): generează serii de **PREȚ** sintetic la scală reală (măsurată) → injectează null + edge gradat → rulează **atât** statistica observată **cât și** nulul prin **aceeași cale** → baterie: ≥100 serii null → uniformitate KS + FPR cu CI Wilson; 3–5 magnitudini → curbă de putere monotonă; reproducibilitate pe seed.
- **Codul agnostic de metodă:** `run_battery`, `ks_uniform`, `wilson_ci` și designul generatorului `generate_price` (random-walk aditiv; **σ trebuie re-măsurat** pe contextul de date/feature al `mstrat`, dar arhitectura generatorului se transferă).
- **Disciplina „aceeași cale" (fidelitate deterministă):** cerința ca pipeline-ul sintetic să reproducă **exact** numărătorile reale (la VE: evenimente/celulă; la `mstrat`: numărătorile de setup-uri per familie) — se transferă ca cerință de proiectare.
- **Postura de guvernanță:** validează-înainte-de-promovare; nu ajusta metoda la eșec.

### 4.2 CE NU SE TRANSFERĂ (trebuie reconstruit)

**R1 — Domeniul statisticii.** Dovada de uniformitate a VE ține pentru un statistic **liniar** pe forward-returns iid. Statistica `mstrat` = media R (raport, prin exit neliniar + normalizare pe risc). Sub un null RW, distribuția lui R **nu** e distribuția randamentelor de preț; uniformitatea trebuie **re-stabilită empiric pentru R**, nu presupusă. **Dovada F6 nu se propagă.**

**R2 — Obiectul-null și harness-ul.** `ve/calibration/synthetic_matched_null.py` e legat de pipeline-ul de celule al VE (`_detect_events`, `pipeline_cells`, forward-K6, `matched_null.run` pe `ex`/`pool`). **Nimic din el nu conduce `mstrat.simulate`.** Nulul din spec (Test A: timing de intrare aleator păstrând profilul realizat de risc/stop, exit, costuri, overlap) trebuie implementat ca **harness NOU** care apelează `mstrat.simulate` (sau un provider de setup-uri sintetic fidel) cu intrări randomizate. **Reconstrucție, nu reutilizare.**

**R3 — Nulul existent din `mstrat` e sub-specificat.** `mstrat._pool` folosește un stop **fix 1.5×ATR**, nu riscul realizat per setup, și **nu** aplică stop-floor-ul. Deci nu e nici nulul „matched" din spec, nici consistent cu engine v2. Trebuie rescris să potrivească profilul realizat de risc **+** stop-floor înainte de a putea fi măcar o țintă de calibrare.

**R4 — Suprafața de fidelitate.** VE a reprodus 6 numărători de celulă. Generatorul sintetic `mstrat` trebuie să reproducă numărătorile de setup pe **20 de familii** cu feature-uri bogate (FVG, VWAP, opening range, compression, swings, PDH/PDL, context MTF H4/H1/D1). Ori construiești fidelitate sintetică full-feature, ori (decizie de proiectare) restrângi calibrarea la un **subset reprezentativ de familii**, documentat justificat.

**R5 — Rezoluția estimatorului.** VE a folosit B=2000/celulă. `mstrat` cere MC adaptiv (MC-1 B=20k → MC-2 ≥200k → MC-3 ≥1e6) la rezoluția pragului BH pentru m=1552 (α/m ≈ 3.2e-5). Bateria de calibrare trebuie rulată la o rezoluție adecvată verdictului — mult mai grea în calcul.

### 4.3 PRECONDIȚIE DURĂ — D2 (vezi §5)

Chiar cu R1–R5 rezolvate, calibrarea nu poate începe cât timp **D2 e deschis**: prețul sintetic curat al VE nu exercită niciodată patologia stop-ului minuscul, deci o baterie F6-style ar declara „calibrat" un estimator care în producție operează pe o statistică R contaminată. Detaliu și dimensionare mai jos.

---

## 5. D2 CA BLOCAJ DUR — CEA MAI IMPORTANTĂ CONSTATARE + DIMENSIONARE EFORT

### 5.1 De ce D2 domină determinarea

Statistica oficială `mstrat` este media R, R = pnl/risc_inițial. Când stopul de structură (`prev_ext` / `beyond_sweep` / `structural`) stă la ~0 față de intrare, R explodează pe o mișcare normală (audit S6: risc 0.19px, R până la +166; top-5 tranzacții = 71% din profit; scoate-le → suma R devine NEGATIVĂ). Stop-floor-ul v2 e activ în `simulate` (linia `min_exec`), dar **marcajul INVALID-EXECUTION NU e cablat** — deci statistica pe care ar sta orice null calibrat este încă un **artefact de normalizare**, nu alfa.

Consecință logică: **un null perfect calibrat pe o statistică contaminată e lipsit de sens.** Ordinea corectă este D2-întâi, calibrare-după. Aceasta răstoarnă ideea că F6 „aproape" a terminat treaba — F6 a validat rețeta pe un obiect curat; obiectul `mstrat` nu e încă curat.

### 5.2 Coroborare independentă (Flow C)

Flow C a măsurat **aceeași patologie**, independent, direct pe corp (`results/FAMILY_RESULTS.parquet`), verificat independent:
- **pf = ∞** în S1 (împărțire la pierdere zero → risc degenerat),
- **30,5%** dintre profitabili **colapsează** fără cea mai bună tranzacție,
- **top-5 ≈ 41%** din contribuție, win-rate median 0,443 printre câștigători.

Două metode independente — auditul meu de cod (D2) și caracterizarea descriptivă a lui Flow C — arată spre **același artefact de R-normalizare** în corp. Aceasta ridică D2 de la „defect suspectat" la **patologie măsurată de două ori**. Așteptarea CEO — „un p-engine valid va respinge majoritatea corpului, ăsta e rezultatul corect" — este exact predicția care rezultă din închiderea D2.

### 5.3 Dimensionarea efortului (per `docs/MIN_STOP_FLOOR_PREREG.md`) — NEEXECUTAT

Punct cheie de încadrare: **închiderea D2 este bine-specificată și mărginită, NU o problemă de cercetare deschisă.** Regula (floor + reguli INVALID-EXECUTION + politica de re-rulare) e deja pre-înregistrată integral în `MIN_STOP_FLOOR_PREREG.md`; lipsește *cablarea* + o *re-rulare uniformă* + un *re-audit*.

| WP | Conținut | Natură | Mărime (estimare) |
|---|---|---|---|
| **WP-1** | Cablează marcajul **INVALID-EXECUTION** în `mstrat.simulate`: marchează invalid când (a) gap prin stopul floor-uit la intrare, (b) risc ≤0 după floor, (c) intrare/ieșire în aceeași bară cu fill ambiguu. Adaugă câmpuri de audit per tranzacție (stop tick-rotunjit, spread intrare+ieșire, slippage, gap-over-stop, modificare stop, break-even, exit-uri parțiale, ordonare intrabar, R-max-posibil vs. realizat). | Inginerie localizată în `simulate()` + o structură de audit; oglindește în `simulate_ref`. Atenție la lookahead-safety și la păstrarea parității înghețate. | **M** (1–2 sesiuni focalizate + review) |
| **WP-2** | Re-validează **paritatea** (`simulate` vs `simulate_ref`) + smoke, extinse să acopere INVALID-EXECUTION și să rămână PASS. | Test | **S–M** |
| **WP-3** | **Re-rulare uniformă S1–S20** pe v2+INVALID-EXECUTION → **nou** `FAMILY_RESULTS.parquet`, version-stamp; **NU** suprascrie baseline-ul (scrie în director nou, ca `results/reproduction_*`). | Calcul (ordinul a ~1,3M tranzacții); rulabil (reprodus deja o dată), în mare parte neasistat. | **L la calcul, S la efort uman** (ore de rulare) |
| **WP-4** | **Re-audit:** numărătorile se vor deplasa (357 hist-profitabile etc. se schimbă); re-verifică Screen V1, diff vs. baseline, documentează care candidați erau artefact de R-normalizare. | Analiză | **M** |
| **WP-5** | *Abia după* WP-1..4: construiește harness-ul matched-null `mstrat` (R2/R3), re-măsoară scala + fidelitatea sintetică (R4), rulează bateria F6-style la rezoluție adecvată (R1/R5). | Inginerie + calcul | **L** (determinare separată; nu parte din închiderea D2) |

**Incertitudine:** estimările sunt T-shirt, nu angajamente. Riscul dominant e la WP-1 (corectitudinea auditului intrabar, lookahead-safety) și la WP-5 (dacă statistica R refuză uniformitatea la R1 — atunci nulul, statistica sau ambele trebuie reproiectate). **Nimic din §5.3 nu a fost executat; este strict dimensionare.**

---

## 6. RECOMANDARE / SECVENȚIERE

1. **NU** calibra încă matched-null-ul `mstrat`.
2. Secvență: **închide D2** (WP-1..4) → **construiește harness-ul matched-null `mstrat`** conform spec (R2/R3) → **re-măsoară scala + fidelitatea** sintetică (R4) → **rulează bateria F6-style** la rezoluție adecvată (R1/R5) → abia atunci un p oficial validat pentru `mstrat`.
3. Holdout-ul rămâne **SIGILAT**; global-FDR rămâne **gated**; campania **nu** se re-rulează sub această determinare.
4. Registrul de metode (`capabilities.json`) rămâne `PUBLISHED_NOT_EXECUTABLE`; promovarea `matched_null@v1` la VALIDATED e amânată de CEO până după F6.1 și, oricum, **nu** conferă executabilitate nulului `mstrat`.

---

## 7. CONSTRÂNGERI RESPECTATE

| Cerință | Stare |
|---|---|
| Fără global-FDR | ✅ neatins |
| Fără atingerea holdout-ului | ✅ neatins |
| Fără re-rularea campaniei | ✅ neatins (§5.3 = dimensionare, neexecutată) |
| Livrabil = un singur document de determinare | ✅ acest fișier |
| Lucru pe clonă separată, nu în worktree-ul partajat | ✅ clonă pinuită la `d453b27` |
| Publicat pe `statistician-foundation`, hash confirmat | vezi commit + `git ls-remote` la închidere |

**Concluzie:** rețeta F6 se transferă; obiectul `mstrat` nu. Blocajul dur este D2, măsurat independent și de Flow C. D2 e mărginit și bine-specificat — cablare + re-rulare + re-audit, nu cercetare deschisă. Calibrarea matched-null `mstrat` este posibilă **numai după** D2.
