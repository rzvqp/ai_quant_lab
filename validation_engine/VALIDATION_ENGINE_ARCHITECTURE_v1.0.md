# VALIDATION ENGINE — ARHITECTURA v1.0
### Documentul de definire a interfețelor componentei de execuție a validării statistice

**Document ID:** VE-ARCH-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine (rol executiv)
**Statut:** **PROPUNERE — în așteptarea aprobării CEO.** Niciun cod nu a fost scris. Nicio componentă nu este operațională.
**Document guvernant:** `statistician/STATISTICIAN_VALIDATION_ENGINE_CONTRACT_v1.0.md` (STAT-VE-CONTRACT-v1.0, ratificat de CEO 2026-07-24)
**Context normativ secundar:** `statistician/STATISTICIAN_CONSTITUTION_v1.0.md` §4.7, §6, §8 · `docs/EMPIRICAL_PVALUE_SPEC.md` · `REPRODUCIBILITY_AUDIT.md`

> Acest document definește **exclusiv interfețele** Validation Engine: ce intră, ce iese, cum comunică, ce face, ce nu face niciodată. Nu definește algoritmi, nu definește structura internă a modulelor și nu autorizează nicio implementare. Construcția efectivă începe numai după aprobarea acestei arhitecturi, în faze mici, verificabile individual (§8).

---

## 0. Poziția în laborator

Pipeline-ul oficial al laboratorului rămâne neschimbat:

```
Alpha Discovery → Discovery Candidates → Red Team → STATISTICIAN → Knowledge Base → AI Trader
                                                         │
                                                         │  specificație completă
                                                         ▼
                                                 VALIDATION ENGINE
                                                         │
                                                         │  rezultate brute + manifest
                                                         ▼
                                                    STATISTICIAN
```

**Validation Engine nu este o etapă a pipeline-ului.** Este un **instrument subordonat Statisticianului**, plasat în interiorul etapei „Statistician", nu între ea și Knowledge Base. Consecințe directe:

- VE nu primește niciodată sarcini de la Alpha, Red Team, Flow C sau AI Trader.
- VE nu returnează niciodată rezultate către altcineva decât către Statistician.
- Nimic din ce produce VE nu avansează singur spre Knowledge Base. Traseul spre KB trece obligatoriu prin interpretarea și verdictul Statisticianului, apoi prin decizia CEO.
- VE nu are opinie asupra momentului în care rulează. Nu inițiază nimic.

Separarea fundamentală, din contract §0: **Statisticianul proiectează, interpretează și emite verdictul. Validation Engine execută și returnează.** Niciuna dintre părți nu poate prelua rolul celeilalte.

---

## 1. CE INTRĂ ÎN VALIDATION ENGINE

### 1.1 Intrări acceptate

| # | Intrare | Sursă | Format | Obligatorie |
|---|---|---|---|---|
| I1 | **Specificația de validare** | Statistician | fișier mașină (YAML/JSON), validat de schemă | DA — fără ea nu există rulare |
| I2 | **Datele de piață declarate în specificație** | `data/market/` (sau calea din `AI_QUANT_DATA_DIR`) | CSV/Parquet, read-only | DA |
| I3 | **Hash-urile declarate ale datelor** | din interiorul specificației (I1) | SHA-256 per fișier | DA |
| I4 | **Registrul de capabilități** | artefact propriu VE, versionat | JSON + document publicat | DA (intern) |
| I5 | **Token de autorizare CEO** | CEO, prin Statistician | token cu ID, resursă vizată, o singură utilizare | DOAR pentru resurse irepetabile (holdout sigilat) |
| I6 | **Modul de rulare** | invocare | `validate` \| `rehearse` \| `run` \| `verify` | DA |

Specificația (I1) trebuie să conțină, conform contract §1, toate cele șapte secțiuni: identificare, populație, variabile, teste în ordine cu parametri expliciți, criterii preînregistrate de succes/eșec cu metoda de corecție family-wise, formatul cerut la retur, clauza de oprire. **Lipsa oricăreia dintre ele oprește rularea înainte de orice atingere a datelor.**

### 1.2 Intrări refuzate categoric

VE **nu primește și nu citește niciodată**:

- documentul Discovery Candidate, Addenda sau `metadata_v1.json`;
- rapoartele sau review-urile Red Team;
- rapoartele Statisticianului (Phase 1, Stage S00x, sinteze);
- Knowledge Base, artefactele Alpha, registrul de observații, jurnalul de cercetare;
- conversații, chat-uri, istoricul niciunei divizii;
- instrucțiuni verbale, în proză, sau prin chat — o instrucțiune care nu este un câmp validat dintr-o specificație mașină nu există pentru VE;
- rezultatele unei rulări anterioare, ca intrare pentru o rulare nouă (fiecare rulare pornește de la zero din specificație + date).

Aceasta este proprietatea de **orbire la ipoteză**: VE nu știe ce testează. Vede numai populația, variabilele, testele și pragurile. Nu poate fi influențat, nici accidental, de narațiunea, de vechimea, de „promisiunea" sau de miza unui candidat, pentru că nu are acces la ele. ID-ul candidatului și hash-ul de îngheț intră doar ca **etichete de trasabilitate** în manifest — nu sunt citite de nicio componentă de calcul.

### 1.3 Regimul special al datelor sigilate

Constatare care determină designul: **holdout-ul nu este un fișier separat**. În `code/run_full_campaign.py:3` este ultimul segment al aceluiași `data/market/OANDA_XAUUSD_M15.csv` (16.831 bare din 84.152), iar pentru DC-0004 este fereastra post-2025-10-23 din `OANDA_XAUUSD_H1.csv`. Fișierele fizice conțin deja rândurile sigilate.

Prin urmare, **sigilarea se impune la nivel de fereastră temporală, nu de fișier**:

- un `SEALED_REGISTRY` declară perechi `(sursă, fereastră, status, autoritate)`;
- loader-ul trunchiază fizic seria la fereastra permisă înainte ca datele să ajungă la orice modul de calcul — rândurile sigilate nu sunt încărcate în memorie, nu doar ignorate;
- jurnalul de acces la date înregistrează timestamp-ul maxim efectiv citit din fiecare sursă, iar manifestul îl publică. Dovada că o rulare nu a atins holdout-ul devine **mecanică și verificabilă ulterior**, nu declarativă;
- fereastra sigilată se deschide numai cu token CEO valid (I5), o singură dată per resursă, și numai după o repetiție reușită pe fereastră nesigilată (§3.4).

---

## 2. CE IESE DIN VALIDATION ENGINE

### 2.1 Ieșiri produse

| # | Ieșire | Când | Destinatar |
|---|---|---|---|
| O1 | **Bundle de rezultate** (director write-once) | la fiecare rulare finalizată sau parțială | Statistician |
| O2 | **Manifest de execuție** | la fiecare rulare, inclusiv la cele oprite sau eșuate | Statistician + audit |
| O3 | **Cerere de clarificare** | la fiecare oprire fail-closed | Statistician |
| O4 | **Intrare în ledger-ul de rulări** (append-only) | la fiecare invocare, fără excepție | audit permanent |
| O5 | **Registrul de capabilități publicat** | la fiecare versiune a registrului | Statistician |
| O6 | **Raport de verificare (`verify`)** | la cerere, pe un bundle existent | Statistician + audit |

Bundle-ul (O1) conține obligatoriu, conform contract §1.6: **toate rezultatele brute — nu doar rezultatul „câștigător"** —, codul rulat, log-urile și toate semințele de randomizare. În concret: populația selectată, denominatorul (câți candidați au fost evaluați și respinși, per criteriu), distribuțiile nule complete, rândurile per instanță, coeficienții și reziduurile, avertizările, excepțiile, mediul de execuție și checksums.

### 2.2 Ieșiri care nu există niciodată

Din bundle, din manifest, din cererile de clarificare și din orice mesaj VE **lipsesc structural**:

- verdicte, concluzii, interpretări, rezumate narative;
- vocabularul de verdict: *semnificativ, confirmat, respins, robust, trece, eșuează, promițător, slab*;
- recomandări de orice fel — inclusiv recomandarea unei valori pentru un câmp lipsă;
- ordonarea rezultatelor după mărimea efectului sau a valorii p (ordinea este cea din specificație, întotdeauna);
- rezultate omise ca „nerelevante", „degenerate" sau „evident negative";
- rezultate parțiale comunicate informal, în afara bundle-ului.

Un test care nu a putut rula apare în rezultate cu status `HALTED` sau `ERROR` și cu traceback complet. **Absența unui rezultat este ea însăși un rezultat raportabil.**

---

## 3. CUM COMUNICĂ CU STATISTICIANUL

Comunicarea este **asincronă, prin artefacte pe disc, unidirecțională pe fiecare sens**. Nu există dialog, negociere sau schimb informal. Există exact patru tipuri de mesaje.

### 3.1 Tipurile de mesaj

| Tip | Direcție | Artefact | Semnificație |
|---|---|---|---|
| M1 **Specificație** | Statistician → VE | fișier în `validation_engine/specs/` | „Execută exact acest protocol." |
| M2 **Bundle de rezultate** | VE → Statistician | director în `validation_engine/runs/` | „Am executat. Iată tot ce a rezultat." |
| M3 **Cerere de clarificare** | VE → Statistician | `CLARIFICATION_REQUEST.md` în bundle | „Nu pot executa. Iată exact ce lipsește." |
| M4 **Registru de capabilități** | VE → Statistician | `CAPABILITY_REGISTRY_vX.md` | „Acesta este vocabularul executabil." |

### 3.2 Bucla normală

```
Statistician  ──M1 specificație──►  VE
                                     │  faze de validare (schemă, completitudine, capabilități)
                                     │  faze de execuție (populație, variabile, teste, corecții)
Statistician  ◄──M2 bundle────────  VE
                                     │
                                    VE se oprește. Nu urmărește ce se întâmplă cu rezultatele.
```

VE nu află niciodată ce verdict a emis Statisticianul, nici dacă rezultatele au fost folosite. Nu are memorie între rulări, în afara ledger-ului de audit.

### 3.3 Bucla de oprire (clauza §1.7 din contract)

```
Statistician  ──M1 specificație──►  VE
                                     │  detectează câmp lipsă / ambiguu / metodă inexistentă
Statistician  ◄──M3 clarificare───  VE   (zero date atinse pentru erorile de tip spec)
              ──M1' specificație v2──►  VE
```

Cererea de clarificare (M3) conține **exact patru câmpuri**, în această ordine:

1. codul erorii;
2. calea exactă a câmpului problematic în specificație;
3. motivul pentru care nu poate fi executat ca atare;
4. ce există în registrul de capabilități, ca informație factuală.

**Nu conține o valoare recomandată, un default propus sau o reformulare a specificației.** Contractul §1.7 interzice explicit alegerea unei valori implicite de către VE; o sugestie este o alegere deghizată și ar transfera tacit proiectarea dinspre Statistician spre executant.

Specificația corectată primește o versiune nouă și un hash nou. Nu se editează niciodată în loc — istoricul versiunilor de specificație rămâne integral vizibil.

### 3.4 Protocolul pentru resurse irepetabile

Pentru orice resursă declarată sigilată (holdout OOS), comunicarea are două etape obligatorii, în această ordine:

```
1. REHEARSAL   Statistician ──M1 (rehearse)──► VE ──M2 bundle NON-OFFICIAL──► Statistician
               Aceeași specificație, executată pe fereastra nesigilată declarată în spec.
               Fereastra sigilată nu este încărcată; jurnalul de acces o dovedește.

2. SEALED RUN  Statistician ──M1 + token CEO──► VE ──M2 bundle OFFICIAL──► Statistician
               Se acceptă numai dacă: hash-ul specificației este identic cu cel din rehearsal,
               rehearsal-ul s-a încheiat fără oprire, iar token-ul este valid și neconsumat.
               VE marchează resursa consumată. Orice a doua încercare este refuzată,
               indiferent de autorizare.
```

Aceasta transformă în mecanism regulile deja existente: constituția Statisticianului §8.7 („resursele irepetabile se cheltuiesc o singură dată, cu designul complet blocat înainte de execuție — niciodată în încercări repetate până la un rezultat convenabil") și `NEXT_SESSION.md` („Do not open the terminal holdout (CEO gate)").

### 3.5 Reguli de comunicare

- VE nu negociază conținutul unei specificații și nu propune modificări.
- VE nu raportează progres parțial, rezultate intermediare sau „primele impresii". Un rezultat există numai în bundle, complet.
- VE nu comunică niciodată cu Alpha, Red Team, Flow C sau AI Trader, în niciun sens.
- Fiecare invocare — inclusiv cele oprite la prima fază — intră în ledger. Statisticianul vede istoricul complet al rulărilor per hash de specificație. **Selecția convenabilă a unei rulări dintre mai multe devine detectabilă fără a depinde de onestitatea VE.**

---

## 4. CUM COMUNICĂ CU REPOSITORY-UL

### 4.1 Zone de acces

| Zonă | Acces | Observații |
|---|---|---|
| `validation_engine/specs/**` | **citire** | specificațiile primite, imutabile după recepție |
| `data/market/**` | **citire**, trunchiat la fereastra permisă | hash verificat față de cel declarat în spec |
| fereastra sigilată din sursele de date | **fără acces**, exceptând sealed run autorizat | impus în loader, nu prin convenție |
| `validation_engine/capabilities.json` | **citire** | registrul propriu |
| `validation_engine/runs/**` | **scriere, write-once** | singura zonă în care VE creează fișiere de rezultat |
| `validation_engine/RUN_LEDGER` | **adăugare (append-only)** | niciodată rescris, niciodată curățat |
| `validation_engine/clarifications/**` | **scriere** | cererile de clarificare |
| **restul repository-ului** | **fără acces** | vezi 4.2 |

„Fără acces" este mai strict decât „read-only" și este intenționat: `discovery_candidates/`, `red_team/`, `statistician/reviews/`, `docs/`, `results/`, `alpha_instance_2/`, `flow_c/`, `code/` nu sunt citite de VE. Orbirea la ipoteză (§1.2) este garantată de topologia accesului, nu de disciplină.

### 4.2 Interdicții de scriere

VE **nu scrie, nu modifică, nu șterge și nu redenumește niciodată** nimic în afara celor trei zone de scriere de mai sus. În particular, nu atinge: Discovery Candidates, Addenda, rapoartele Red Team, rapoartele Statisticianului, Knowledge Base, artefactele Alpha, `data/`, `results/`, `code/`.

Verificarea este mecanică, nu declarativă: **hash al arborelui de repository înainte și după fiecare rulare**, publicat în manifest ca `repo_integrity.external_writes`. O valoare diferită de zero invalidează bundle-ul.

### 4.3 Integritatea intrărilor

- Fiecare fișier de date primește SHA-256 la încărcare, comparat cu hash-ul declarat în specificație. Nepotrivire → oprire, înainte de orice calcul.
- Datele nu sunt niciodată rescrise, normalizate în loc, corectate sau completate de VE. O anomalie de date (duplicat, gap, OHLC invalid) se raportează, nu se repară.

### 4.4 Trasabilitatea codului

- Modul `official` cere arbore git curat și înregistrează commit-ul exact. Arbore murdar → rulare refuzată în mod oficial.
- Modul `rehearse` permite arbore murdar, dar înregistrează diff-ul în manifest și marchează bundle-ul `NON-OFFICIAL`.
- Manifestul publică versiunile exacte de Python și biblioteci, sistemul de operare și mașina — standardul deja atins de laborator în `REPRODUCIBILITY_AUDIT.md` (reproducere exactă pe un stack pandas/numpy mai nou).

### 4.5 Imutabilitatea ieșirilor

- Un bundle este **write-once**: după sigilare, niciun fișier din el nu se mai modifică.
- O re-rulare primește un `run_id` nou. Nimic nu se suprascrie niciodată — convenția `results/reproduction_v2/` deja practicată în laborator.
- Comanda `verify` re-execută un bundle și compară cu toleranțele deja convenite: `atol = rtol = 1e-9`, `NaN == NaN`, `inf == inf`. Ieșire: `EXACT` / `WITHIN_TOLERANCE` / `MISMATCH`.

---

## 5. RESPONSABILITĂȚILE VALIDATION ENGINE

| # | Responsabilitate | Sursă |
|---|---|---|
| **R1** | **Recepția și validarea de completitudine** a specificației — verifică structura, prezența tuturor celor șapte secțiuni, caracterul numeric (nu descriptiv) al fiecărui prag, capetele explicite ale fiecărei ferestre, existența tuturor parametrilor fiecărui test | contract §1.1–1.6 |
| **R2** | **Execuția literală** a protocolului — populație, variabile, teste în ordinea dată, corecție family-wise pe familia enumerată explicit; exact ce s-a specificat, nimic în plus, nimic în minus | contract §1.2–1.5, §2.9 |
| **R3** | **Returnarea integrală** a rezultatelor brute — toate testele, toate celulele, toate variantele, indiferent dacă susțin sau infirmă ipoteza; plus codul, log-urile și semințele | contract §1.6, §2.9 |
| **R4** | **Generarea manifestului de execuție** la fiecare rulare: versiunea codului, hash-ul datelor, hash-ul specificației, data și ora, durata, orice avertizare sau excepție — astfel încât orice execuție să poată fi reprodusă și verificată ulterior | contract §2.8 |
| **R5** | **Oprirea fail-closed cu cerere de clarificare** ori de câte ori un parametru lipsește sau este ambiguu — niciodată alegerea unei valori implicite | contract §1.7 |
| **R6** | **Protecția resurselor irepetabile** — impunerea mecanică a sigiliului, a repetiției prealabile și a consumului unic | constituție §8.7, `NEXT_SESSION.md` |
| **R7** | **Menținerea ledger-ului append-only** al tuturor rulărilor, ca bază de audit împotriva raportării selective | derivat din §8 preînregistrare |
| **R8** | **Publicarea și menținerea registrului de capabilități**, inclusiv statusul de calibrare al fiecărei metode, astfel încât Statisticianul să scrie numai specificații executabile | derivat din §1.4 + §2.9 |

Nota la R8: registrul marchează fiecare metodă cu `VALIDATED` / `UNVALIDATED` / `QUARANTINED`, iar o metodă necalibrată nu poate fi referită de nicio specificație oficială. Motivul este documentat în laborator: `docs/EMPIRICAL_PVALUE_SPEC.md` consemnează că implementarea matched-null existentă este necalibrată („fails synthetic-null; MUST be fixed+re-validated before official use"). Mecanismul de status există tocmai pentru ca o metodă în această stare să nu poată reintra accidental în uz oficial.

---

## 6. CE NU VA FACE NICIODATĂ

Din contract §2.9, plus consecințele operaționale necesare pentru a-l face executabil:

**Asupra protocolului**
1. Nu schimbă niciun parametru primit — nici pentru convergență, nici pentru viteză, nici pentru că valoarea dată produce eroare.
2. Nu optimizează și nu derivă praguri. Pragul vine din specificație sau rularea se oprește.
3. Nu ignoră teste și nu adaugă teste suplimentare — nici măcar teste evident utile pe care Statisticianul le-a omis.
4. Nu elimină rezultate considerate „nerelevante", degenerate sau neinteresante.
5. Nu alege semințe, ferestre, orizonturi, numere de reeșantionări sau metode. Ce lipsește oprește rularea.
6. Nu reordonează testele și nu le execută selectiv.

**Asupra interpretării**
7. Nu emite interpretări, concluzii sau verdicte.
8. Nu folosește vocabularul de verdict în niciun artefact.
9. Nu agregă rezultatele într-o judecată sintetică de niciun fel.
10. Nu recomandă pasul următor și nu evaluează dacă un rezultat este bun sau rău.
11. Nu sugerează valori atunci când cere clarificare.

**Asupra rolului**
12. Nu proiectează experimente, nu formulează H0/H1, nu identifică confounduri, nu alege controale.
13. Nu observă piața, nu colectează date noi, nu construiește serii noi.
14. Nu creează, nu evaluează și nu clasifică Discovery Candidates.
15. Nu face Red Team, nu face triaj de portofoliu, nu compară candidați între ei.
16. Nu decide când rulează și nu inițiază nicio rulare din proprie inițiativă.

**Asupra datelor și artefactelor**
17. Nu modifică niciun artefact al laboratorului în afara propriului director de rulare.
18. Nu rescrie, nu corectează și nu completează datele de piață.
19. Nu atinge o fereastră sigilată fără token CEO valid, repetiție prealabilă reușită și resursă neconsumată.
20. Nu suprascrie un bundle existent și nu șterge o intrare din ledger.

**Asupra propriei execuții**
21. Nu re-rulează cu semințe diferite până la un rezultat convenabil.
22. Nu reutilizează rezultatul unei rulări anterioare pentru a scurta o rulare nouă.
23. Nu raportează rezultate parțiale informal, în afara bundle-ului complet.
24. Nu comunică cu nicio altă divizie în afară de Statistician.

---

## 7. Ipoteze de lucru și puncte rămase în decizia CEO

Arhitectura de mai sus este completă și autoconsistentă sub următoarele ipoteze. Cele marcate **PROVIZORIU** trebuie ratificate înainte de faza de implementare care le atinge.

| # | Punct | Ipoteza asumată în acest document | Status |
|---|---|---|---|
| P1 | Evaluarea mecanică a criteriilor preînregistrate | VE produce un tabel `(valoare, comparator, prag, met: true/false)` într-un fișier separat, fără agregare și fără mapare la verdict | **PROVIZORIU** — afectează §2.1 |
| P2 | Reutilizarea nucleului statistic existent | VE implementează independent metodele statistice; reutilizează din `code/` exclusiv convenția de localizare a datelor (`AI_QUANT_DATA_DIR`, `code/mtf.py:11`) | **PROVIZORIU** — motivat de matched-null-ul necalibrat |
| P3 | Domeniul registrului de capabilități v1.0 | Numai metodele cerute de cele trei design-uri deja livrate (DC-0008, DC-0003, DC-0004) | **PROVIZORIU** |
| P4 | Deținerea sigiliului holdout | CEO emite token-ul; VE îl impune mecanic și îl marchează consumat | **PROVIZORIU** — afectează §1.3, §3.4 |
| P5 | Limba artefactelor | Chei mașină și rezultate în engleză (consistent cu `code/`); guvernanță și cereri de clarificare în română (consistent cu `statistician/`) | asumat, reversibil |

---

## 8. Fazele de construcție propuse

Construcție incrementală, fiecare fază verificabilă independent și oprită înainte de următoarea. Nicio fază nu atinge date reale înainte de faza F6.

| Fază | Livrabil | Criteriu de acceptare | Atinge date reale |
|---|---|---|---|
| **F0** | Acest document, aprobat | aprobare CEO | nu |
| **F1** | Schema de specificație + registrul de capabilități publicat | Statisticianul poate scrie o specificație validă fără să ghicească nimic | nu |
| **F2** | Validatorul de specificație + taxonomia de erori + cererea de clarificare | bateria de mutații: fiecare câmp obligatoriu lipsă/ambiguu produce oprirea corectă, cu **zero** accesări de date | nu |
| **F3** | Manifest, checksums, ledger, integritatea repository-ului | o rulare goală produce un manifest complet și dovedește `external_writes = 0` | nu |
| **F4** | Stratul de date + sigilarea pe fereastră + jurnalul de acces | fereastra sigilată nu poate fi încărcată nici măcar accidental; dovadă în jurnal | doar hash + fereastră nesigilată |
| **F5** | Prima metodă statistică + bateria sintetică de calibrare | distribuția p uniformă sub null, curbă de putere monotonă, reproducere bit-exactă | nu (serii sintetice) |
| **F6** | Restul metodelor din registru, una câte una, fiecare cu propria calibrare | fiecare metodă trece individual înainte de a primi `VALIDATED` | nu (serii sintetice) |
| **F7** | Prima execuție pe date reale, pe fereastră nesigilată | bundle complet, `verify` = `EXACT` | da |
| **F8** | Protocolul de resursă sigilată | refuz corect în toate scenariile neautorizate; consum unic | numai cu token CEO |

Ordinea este deliberată: **capacitatea de a se opri corect (F2) se construiește înaintea capacității de a calcula ceva (F5)**, iar capacitatea de a proteja holdout-ul (F4) se construiește înaintea oricărei atingeri de date reale (F7). Un motor care calculează corect dar nu se oprește corect este mai periculos decât unul care nu calculează deloc.

---

## 9. Versionare

Acest document devine arhitectura oficială a Validation Engine în momentul aprobării CEO. Orice modificare ulterioară a interfețelor definite aici cere o versiune nouă explicită (v1.1+) și o notă de decizie. Modificarea contractului `STAT-VE-CONTRACT-v1.0` obligă la revizuirea acestui document.

---

**Nu s-a scris niciun cod. Nu s-a executat nicio validare. Nu s-a modificat niciun Discovery Candidate, Addendum, raport Red Team, raport Statistician, Knowledge Base sau artefact Alpha. Datele de piață și holdout-ul sigilat nu au fost atinse.**

**Validation Engine se oprește aici și așteaptă aprobarea arhitecturii înainte de faza F1.**
