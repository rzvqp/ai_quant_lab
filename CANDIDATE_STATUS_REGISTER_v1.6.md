# REGISTRU CONSOLIDAT — DIVIZII ȘI CANDIDAȚI
### Singura sursă de adevăr pentru structura laboratorului și stadiul fiecărui candidat

**Document ID:** CEO-REGISTER-v1.6
**Data:** 2026-07-25 · **Autor:** CEO (aplicat de Validation Engine sub directivă CEO explicită 2026-07-25)
**Înlocuiește:** v1.5 (aceeași zi)
**Statut:** operațional

**Modificări față de v1.5:** `bonferroni@v1` PROMOVAT la `VALIDATED` prin suita **deterministă S7** (decizie CEO 2026-07-25); metode validate `1/15` → `2/15` (status rămâne `PARTIALLY_EXECUTABLE`); §B.3 nou (S7 + de ce nu F6); §C decizia 9 nouă. Registrul distinge tipurile de metode prin `acceptance_suites` — bonferroni poartă exclusiv S7, disjunctă de suitele stocastice.

**Istoric v1.5 (păstrat):** `matched_null@v1` PROMOVAT la `VALIDATED`; mașinăria trece de la `PUBLISHED_NOT_EXECUTABLE` la `PARTIALLY_EXECUTABLE`; §C decizia 6 RATIFICATĂ; §B cu cele 4 caveat-uri + raționamentul (φ condițional + KS).

---

## De ce există acest document

Regulile de independență interzic fiecărei divizii să scrie în arborele alteia. Consecința: `lifecycle status` din `DISCOVERY_CANDIDATE_INDEX.md` arată `FROZEN` pentru toți cei 28 de candidați, deși Red Team a evaluat 28, Statistician a analizat 3, iar Validation Engine a executat oficial pe 1.

În sesiunea din 2026-07-25, lucrul dintr-un inventar incomplet a produs **patru** erori factuale distincte, fiecare comisă de o parte competentă:

1. RT-FINAL-0001 a omis DC-0025, DC-0026 și AP2-DC-0002 (inventar de 25 în loc de 28).
2. Corecția F2 a fost scrisă cu 180,53pt; valoarea corectă (514,165pt) exista deja depusă în DC-0024 Addendum D.
3. Arhitectul Șef a afirmat că recordurile de 514,165pt și 53.154 nu erau înregistrate; ambele erau depuse corect ca addenda.
4. Registrul v1.0 a numărat 6 divizii; sunt 8.

Doar CEO modifică acest document.

---

## §0 — Harta diviziilor

| # | Divizie | Repo / branch | Stare | Ultimul artefact | Publicat |
|---|---|---|---|---|---|
| 1 | **AI Trader** | `ai_quant_lab-research-main` / `ai-trader-implementation` | ACTIV | `40e9e48` — Decision Logic Audit | ✅ |
| 2 | **Alpha 1** | `ai_quant_lab-alpha-automation` / `alpha-automation-v1` | **ÎNCHIS** | `a9088b7` — închideri + inventar | ✅ |
| 3 | **Alpha 2** | `ai_quant_lab` / `statistician-foundation` | **ÎNCHIS** | `d453b27` — șablon testabilitate | ✅ |
| 4 | **Red Team** | `ai_quant_lab` / `statistician-foundation` | STANDBY | `de919c2` — RT-FINAL-0002 | ✅ |
| 5 | **Statistician** | `ai_quant_lab` / `statistician-foundation` | ACTIV | `4c458a7` — verdict holdout DC-0004 | ✅ |
| 6 | **Validation Engine** | `ai_quant_lab` / `statistician-foundation` | ACTIV | registru v1.6 — `matched_null@v1` + `bonferroni@v1` **VALIDATED** (2/15) | ✅ |
| 7 | **Flow C** | `ai_quant_lab` / **`flow-c-foundation`** | ACTIV | `083c69e` — RI-REPORT-0003 | ❌ **NEPUBLICAT** |
| 8 | **Research Lab** | `ai_quant_lab` / `statistician-foundation` | **REACTIVAT 07-25** | dormant din 2026-07-13 | ✅ |

**Worktree-uri care NU sunt divizii:** `ai_quant_lab-alpha-discovery` (strămoș depășit, *do not use*), `ai_quant_lab-families`, `ai_quant_lab-stratdev`.

**Neinventariat:** `tradingview-mcp` — tooling-ul de replay pe care se bazează întreaga metodă Alpha, în afara tuturor repo-urilor oficiale.

### Fluxul real

```
Alpha 1 (închis) ─┐
Alpha 2 (închis) ─┴─→ Red Team ─→ Statistician ─→ Validation Engine ─→ AI Trader
                                                                          │
Research Lab ──→ FAMILY_RESULTS.parquet ←── Flow C                        └─ 0 primite
   (reactivat)          (același obiect)      (descriere)
```

---

## §1 — Alpha #1: 26 candidați

| ID | Alpha | Red Team | Statistician | Valid. Engine | Stare reală | Flags |
|---|---|---|---|---|---|---|
| DC-0001 | FROZEN 07-21 | 🟡 | — | — | În așteptare | W2 |
| DC-0002 | FROZEN 07-22 | 🟡 | — | — | În așteptare | |
| DC-0003 | FROZEN 07-22 | 🟢 | Phase 1 complet | — | **→ Phase 2 autorizat** | |
| DC-0004 | FROZEN 07-22 | 🟢 *(flag)* | Phase 1 + verdict holdout | **F5 executat** | **Plafonat — §A** | W1 |
| DC-0005 | FROZEN 07-22 | 🟡 | — | — | În așteptare | |
| DC-0006 | FROZEN 07-22 | 🔴 | — | — | **ARHIVAT** | |
| DC-0007 | FROZEN 07-22 | 🟡 | — | — | În așteptare | |
| DC-0008 | FROZEN 07-22 | 🟢 | Phase 1 complet | — | **→ Phase 2, PRIORITATE** | |
| DC-0009 | FROZEN 07-22 | 🟡 | — | — | În așteptare | |
| DC-0010 | FROZEN 07-22 | 🔴 | — | — | **ARHIVAT** | |
| DC-0011 | FROZEN 07-22 | 🟡 | — | — | În așteptare | |
| DC-0012 | FROZEN 07-22 | 🟡 | — | — | În așteptare | |
| DC-0013 | FROZEN 07-23 | 🟡 | — | — | Container familie (~12 instanțe) | |
| DC-0014 | FROZEN 07-23 | 🟡 | — | — | În așteptare | |
| DC-0015 | FROZEN 07-23 | 🔴 | — | — | **ARHIVAT** | |
| DC-0016 | FROZEN 07-23 | 🟡 | — | — | În așteptare | |
| DC-0017 | FROZEN 07-23 | 🔴 | — | — | **ARHIVAT** | |
| DC-0018 | FROZEN 07-23 | 🟡 | — | — | În așteptare | |
| DC-0019 | FROZEN 07-24 | 🟡 | — | — | În așteptare | W5 |
| DC-0020 | FROZEN 07-24 | 🟡 | — | — | În așteptare | W5 |
| DC-0021 | FROZEN 07-24 | 🟡 | — | — | În așteptare | W5 |
| DC-0022 | FROZEN 07-24 | 🔴 | — | — | **ARHIVAT** | W3, W5 |
| DC-0023 | FROZEN 07-24 | 🟡 | — | — | În așteptare | W5 |
| DC-0024 | FROZEN 07-24 | 🔴 | — | — | **ARHIVAT** | W3, W5 |
| DC-0025 | FROZEN 07-25 | 🔴 | — | — | **ARHIVAT** | W3, W4, W5 |
| DC-0026 | FROZEN 07-25 | 🟡 | — | — | Cel mai solid din lotul nou | W4, W5 |

## §2 — Alpha #2: 2 candidați

| ID | Alpha | Red Team | Statistician | Valid. Engine | Stare reală | Flags |
|---|---|---|---|---|---|---|
| AP2-DC-0001 | FROZEN 07-24 | 🟡 *(RT-DS-0001: VARIANT OF DC-0018)* | — | — | Replicare independentă | W6, W7 |
| AP2-DC-0002 | FROZEN 07-25 | 🟡 *(RT-DS-0002: VARIANT OF DC-0023)* | — | — | În așteptare | W6, W8 |

**Legendă:** 🟢 SURVIVED · 🟡 NEEDS MORE EVIDENCE · 🔴 REJECTED *(arhivat, ID rezervat permanent, nu șters)*

---

## §3 — Sinteză

| | Nr. |
|---|---|
| Total candidați | **28** |
| Evaluați de Red Team | 28 |
| Analizați de Statistician | 3 |
| Executați de Validation Engine | 1 |
| **Promovați în Knowledge Base** | **0** |
| Ajunși la AI Trader | 0 |
| Arhivați (REJECTED) | 7 |

---

## §A — DC-0004: de ce e plafonat

Singurul candidat care a traversat trei divizii.

- **Semnal real:** matched-null p = 0,021 (celula NY-up), sign-stable pe ambele jumătăți
- **Dar:** pică Bonferroni; selecție post-hoc dintre ~12 celule
- **Și:** holdout-ul rezervat post `2025-10-23T09:15Z` a fost consumat prin observație discreționară (Alpha a parcurs până la `2026-05-15 20:59:59 UTC`)
- **Coada necontaminată:** `2026-05-15` → `2026-07-13`, ~2,4–2,6 evenimente proiectate vs prag de putere 15–20

**Verdict:** Ramura 1 indisponibilă. Plafon = `TESTABLE BUT INSUFFICIENT EVIDENCE`. Ramura 2 (extensie de robustețe in-sample, etichetată explicit) e calea operativă.

**Notă:** DC-0004 pica Bonferroni *înainte* de contaminare. Holdout-ul ars a costat testul decisiv, nu rezultatul de fond.

---

## §B — Mașinăria de validare

| Element | Stare |
|---|---|
| Metode `VALIDATED` | **2 / 15** |
| Registru de capabilități | `PARTIALLY_EXECUTABLE` (`VE-CAPREG-v1.6`) |
| `matched_null@v1` | **VALIDATED** (CEO 2026-07-25) — suite S1/S3/S4, domeniu K6, 4 caveat-uri (§B.1) |
| `bonferroni@v1` | **VALIDATED** (CEO 2026-07-25) — suite **S7 deterministă** (§B.3) |
| Celelalte 13 metode | `UNVALIDATED` — nereferabile de o specificație oficială |
| Holdout la nivel VE | Neatins |
| Teste | 436 |

Traseul de promovare: F6 (uniformitate/FPR/putere/reproducibilitate) → F6.1 (vol pe sesiune + cozi grele) → F6.2 (drift real, fără eșec clar) → F6.3 (reversie AR1 / FPR multi-prag / placebo nivel arbitrar), toate la condițiile reale ale datelor → măsurătoarea finală φ AR(1) condițional pe populația reală de evenimente NY-up.

### §B.1 — Cele 4 caveat-uri obligatorii ale `matched_null@v1` (câmpuri, nu note de subsol)

1. **Domeniu de validare — forward K6.** Punctul de rupere la reversie a fost măsurat pe curba K6. **K12 NU ESTE ACOPERIT** — φ condițional acolo = −0.058 (~3× globalul), iar pragul de rupere la K12 nu a fost măsurat deloc. Orice utilizare la K12 sau alt orizont cere validare separată.
2. **Celula NY-up:** n ≈ 37–42, la granița calibrării. KS p=0.003 pe corpul distribuției, conservator. Cozile nominale la 0.01 / 0.05 / 0.10.
3. **Vulnerabilitate confirmată la reversie** φ ≤ −0.10, adică 5.5× cea reală. φ condițional măsurat pe populația reală de evenimente: **−0.018 la K6, cu CI [−0.228, +0.212]** care **NU exclude** pragul. Estimarea punctuală confirmă marja; precizia nu o poate confirma la n=42.
4. **Configurație:** unstratified, stratificat pe **SESIUNE**, ATR-scaled. Stratificarea pe volatilitate **NU există și NU e validată.**

### §B.2 — Raționamentul deciziei de promovare (CEO, 2026-07-25)

Regula inițială („φ condițional clar peste −0.10") era prost formulată și corectată explicit de CEO: la n=42 niciun orizont nu poate oferi un CI care să excludă pragul — o certitudine pe care datele nu o pot produce.

**Imprecizia lui φ este un risc SPECIFIC DC-0004, nu al metodei.** DC-0004 e singurul dintre cele trei pachete care e un tipar de reversie; DC-0008 e un test de bimodalitate pe rapoarte de concentrare, DC-0003 e alt mecanism — reversia nu îi atinge. În plus, DC-0004 este deja plafonat la `TESTABLE BUT INSUFFICIENT EVIDENCE` (holdout consumat, pică Bonferroni — §A): un p eventual fabricat de reversie nu poate produce un fals pozitiv pe care cineva să acționeze.

**Analiza KS (p=0.003) acceptată:** cozile sunt calibrate direct (FPR nominal la 0.01/0.05/0.10); non-uniformitatea vine din corp (medie 0.542, conservator). Deplasarea corpului spre conservator nu poate coborî rata de respingere din coadă, doar s-o ridice, iar FPR-ul măsurat o arată nominală — direcția erorii e cea sigură. Caveat documentat (câmp 2), nu blocant.

### §B.3 — `bonferroni@v1` VALIDATED prin S7 (determinist), NU prin F6

Registrul **distinge tipurile de metode prin `acceptance_suites`**. `bonferroni@v1` poartă **exclusiv S7**, disjunctă de suitele stocastice `S1/S3/S4` ale metodelor cu reeșantionare. Bonferroni e `p × m`: garanția FWER ≤ α e **inegalitatea Boole (o teoremă)**, nu o proprietate empirică — nu are distribuție null, putere, FPR sau seed de calibrat. Deci NU i se aplică bateria F6.

**Cele șase verificări deterministe** (`tests/test_s7_bonferroni.py`, implementare `ve/methods/bonferroni.py`): (1) aritmetică pe fixturi cu răspuns cunoscut (`α/m`, `min(1,p×m)`); (2) contabilitatea familiei realizate; (3) oprire E6 la familie eligibilă vidă; (4) independență de rezultat R3 la execuție; (5) „fără filtrare" declarat explicit; (6) determinism/idempotență. **Toate trec.** Taxonomia se închide: corecția family-wise stocastică (max-T, DC-0008 §4.8) e `permutation_test@v1` (S1/S3/S4), nu bonferroni.

**Milestone lateral:** specificația de referință a bateriei de mutații (`matched_null@v1` + `bonferroni@v1`, ambele acum VALIDATED) **trece integral validarea** — prima specificație cu vocabular de metode complet executabil. (Validare ≠ execuție; nu atinge date.)

---

## §E — Corpul S1–S51: constatări Flow C, verificate independent

RI-REPORT-0002 și 0003 verificate direct în `results/FAMILY_RESULTS.parquet` (1.972 rânduri). Toate cifrele se confirmă.

| Constatare | Valoare verificată |
|---|---|
| Top-5 tranzacții din contribuție (medie, profitabili) | **41,4%** |
| Win-rate median printre profitabili | **0,443** |
| Tranzacție mediană printre profitabili | **−0,231 R** |
| Profitabili care colapsează fără cea mai bună tranzacție | **30,5%** |
| `val_exp` lipsă | 176 — **toate în S1** |
| S1 ca fracție din gramatică | 1.152 / 1.972 = **58,4%** |
| S1 `pf` maxim | **∞** (defect D2 materializat) |
| S1 `dd` maxim | 440,5 R |

**Consecință strategică:** obiectivul declarat al laboratorului e un sistem cu winrate ridicat și RR mic. Corpul arată exact configurația opusă — profitabilitate purtată de câteva tranzacții mari, cu rată de câștig sub 50%.

**Observație de acoperire, NU o constatare:** filtrând cei 130 research-worthy pe `win ≥ 0,50` ∧ `wo1 > 0` ∧ `n ≥ 50` rămân **21 de ipoteze**. Această filtrare a fost făcută post-hoc, după vizualizarea datelor, pe criterii nepre-înregistrate. Nu are valoare probatorie. Poate deveni ipoteză doar prin pre-înregistrare completă, p-engine validat și model de cost.

---

## §C — Decizii ratificate (Arhitect Șef, sub delegare CEO, 2026-07-25)

| # | Decizie | Stare |
|---|---|---|
| 1 | Inventar = 28 candidați | ✅ RATIFICAT |
| 2 | RT-AUDIT-0001 (Alpha #2) | ✅ ACCEPTAT |
| 3 | RT-AUDIT-0002 (Alpha #1) | ✅ ACCEPTAT |
| 4 | Cei 7 REJECTED → arhivați, nu șterși | ✅ RATIFICAT |
| 5 | DC-0003 și DC-0008 → Statistician Phase 2 | ✅ AUTORIZAT |
| 6 | Promovare `matched_null@v1` → `VALIDATED` | ✅ RATIFICAT (CEO 2026-07-25, registru v1.5, cu 4 caveat-uri — §B.1) |
| 9 | Promovare `bonferroni@v1` → `VALIDATED` prin S7 (determinist) | ✅ RATIFICAT (CEO 2026-07-25, registru v1.6, 2/15 — §B.3) |
| 7 | RT-DS-0001 → consemnat aici, nu scris în arborele Alpha | ✅ RATIFICAT |
| 8 | `flow_c/` | ✅ REZOLVAT — e divizia 7, nu reziduu |

**Rezervat CEO:** ștergerea permanentă a celor 7 arhivați. Arhivarea e reversibilă; ștergerea nu.

---

## §D — Reguli permanente

1. **Publicat = oficial.** O livrare necomisă și nepublicată pe branch-ul oficial nu există. Nicio divizie nu raportează „livrat" înainte de push confirmat prin `git ls-remote`.

2. **Fapte comune, opinii izolate.** Izolarea epistemică se păstrează — nicio divizie nu vede verdictul alteia înainte de a-l forma pe al său. Izolarea factuală se elimină — acest registru e lectură obligatorie pentru toate cele 8 divizii, înainte de orice sarcină.

3. **Pe branch comun, cine împinge ultimul publică munca tuturor.** Verifică ce urcă odată cu tine.

4. **Registrul se actualizează la fiecare tranziție de status**, înainte de a da următoarea directivă.

---

## Anexă — Registrul de integritate W1–W8

| ID | Constatare | Afectați |
|---|---|---|
| W1 | Holdout consumat — contaminează testul decisiv al DC-0004 | DC-0004 |
| W2 | Hash-ul de conținut al DC-0001 nu se reproduce (17/18 se reproduc) | DC-0001 |
| W3 | Contabilitatea recordurilor e inconsistentă intern | DC-0022, DC-0024, DC-0025 |
| W4 | Lipsește `metadata_v1.json` | DC-0025, DC-0026 |
| W5 | Pragul de 42,7% construcție organică se sprijină pe o singură ancoră | DC-0019 … DC-0026 |
| W6 | Calibrarea de confidence a Alpha #2 diferă de a Alpha #1 la n=1 | AP2-DC-0001, AP2-DC-0002 |
| W7 | Proveniența feed-ului — volum posibil mixt OANDA / FusionMarkets | AP2-DC-0001 |
| W8 | Discrepanță de inventar 28 vs 27 | portofoliu |

---

## Surse

- `ai_quant_lab` @ `d453b27` — `red_team/RED_TEAM_FINAL_EVALUATION_v2.md`, `statistician/`, `validation_engine/F6_REPORT.md`, `results/FAMILY_RESULTS.parquet`
- `ai_quant_lab` @ `flow-c-foundation` `083c69e` — `flow_c/reports/` *(nepublicat la data acestui document)*
- `ai_quant_lab-alpha-automation` @ `a9088b7`
- `ai_quant_lab-research-main` @ `40e9e48`
