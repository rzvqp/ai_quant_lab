# ANALIZA GOLURILOR G3, G4 și G5
### Documentul de decizie care precedă registrul v1.2 și faza F3

**Document ID:** VE-GAPS-G3G4G5-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Statut:** **ANALIZĂ — în așteptarea deciziei CEO.** Registrul nu a fost modificat. Codul executabil nu a fost modificat. Nicio soluție nu a fost implementată.
**Descoperite în:** F2.1, la scrierea specificației de referință DC-0004 (`F2_1_REPORT.md` §4.3)

---

## 0. Rezultatul principal, înainte de detalii

**Niciunul dintre cele trei goluri nu cere o versiune nouă de schemă.** Toate se rezolvă prin gramatică + registru v1.2 + validator + teste. `SPEC_SCHEMA_v1.0.json` rămâne neatins, ca și la v1.1.

Al doilea rezultat, la întrebarea pusă explicit de CEO: **G3 nu este specific DC-0004.** Este o capacitate generică, cerută de constituția Statisticianului pentru o clasă largă de candidați viitori și necesară deja pentru 2 din cele 3 designuri livrate. Dovezile sunt în §1.

Al treilea: **G5 trebuie rezolvat înaintea sau împreună cu G3**, altfel G3 livrează o variabilă care poate fi numită dar nu verificată. Argumentul în §5.

---

## 1. Este G3 generic sau specific DC-0004?

Verificat pe toate cele trei designuri livrate de Statistician și pe documentele de guvernanță.

### 1.1 Dovezi din designurile existente

| Design | Ce cere testul de control | Are nevoie de indicator? |
|---|---|---|
| **DC-0004** §11 pas 3 | „regresia continuation-excess pe evenimentul sweep-reject, controlând explicit pentru profilul orar de volatilitate" | **DA** — expunerea este un eveniment (are loc / nu are loc) |
| **DC-0008** §12 | clasificarea rezultată din prag „prezice rezultatul post-M15 pre-definit, cu efect care supraviețuiește controlului pentru regimul de volatilitate" | **DA** — expunerea este apartenența la o clasă definită printr-un prag pe o variabilă continuă |
| **DC-0003** §11(a) | `outcome ~ scale_ratio + regim_lichiditate + scale_ratio:regim_lichiditate` | **NU** — expunerea (`scale_ratio`) este deja o variabilă continuă declarată |

Două din trei. Iar DC-0003, care nu are nevoie de indicator, are totuși nevoie de **G5**: `regression_control@v1.exposure_ref` este astăzi un simplu `string`, deci `scale_ratio` ar putea fi scris greșit fără ca validarea să observe.

### 1.2 Dovezi din guvernanță — de ce este generic, nu accidental

`STATISTICIAN_CONSTITUTION_v1.0.md` §6, primul control obligatoriu:

> „Control pentru regimul ambiental (volatilitate, lichiditate, profil orar) **ori de câte ori** candidatul implică o condiționare temporală sau o clasificare bazată pe volum/range — inclus ca **variabilă de control explicită, cu termen de interacțiune**, nu doar menționat textual."

`STATISTICIAN_PHASE1_SUMMARY.md` §4 punctul 1 repetă regula pentru **toate** Discovery Candidates viitoare. Iar §3 al aceleiași sinteze constată că primitivul Volatility este „de departe, cea mai ieftină și mai puternică ipoteză nulă disponibilă pentru orice candidat viitor din Grupul I sau din orice candidat condiționat de sesiune/oră".

Traducere operațională: **fiecare candidat care definește un eveniment discret va trebui să ruleze o regresie cu expunere-eveniment și control de regim.** Grupul I al portofoliului (11 din 18 candidați auditați) intră direct în această categorie.

### 1.3 Alte utilizări ale aceleiași primitive

- **Test placebo/control negativ** (constituție §6): un nivel placebo produce un al doilea eveniment, deci un al doilea indicator, comparabil cu primul.
- **Denominator și rată de expunere** (golul universal al portofoliului): cu un indicator explicit, „câte evenimente din câte candidate eligibile" devine o mărime raportabilă, nu o reconstrucție.
- **Stratificare** pe apartenența la clasă (`stratifier`), fără a fi nevoie de o celulă separată per test.

### 1.4 Concluzia asupra genericității

> G3 nu este o gaură lăsată de DC-0004. Este primitiva care lipsește pentru **întreaga familie de protocoale regresie-cu-control** pe care laboratorul le-a declarat obligatorii. Recomandarea din §3 este construită pe acest rol generic, nu pe specificația de referință.

### 1.5 O verificare colaterală: lanțul de rezultate între teste NU este un gol

Designul DC-0008 derivă pragul din date (§11(b): bootstrap pe Otsu/intersecție GMM) și abia apoi clasifică. S-ar putea crede că specificația trebuie să poată folosi ieșirea unui test ca intrare a altuia.

Nu trebuie — și nu ar avea voie. Constituția §8.2 interzice explicit: *„niciun prag nu se alege pentru a maximiza separarea observată pe același set pe care va fi testat efectul."* Derivarea și testarea sunt două specificații preînregistrate distincte, cu hash-uri distincte. **Absența lanțului între teste nu este o limitare, ci aplicarea unei reguli de preînregistrare.** Nu propun nicio schimbare aici.

---

## 2. G3 — nu există primitivă care să transforme un predicat într-o variabilă

### 2.1 Cauza exactă

Registrul separă net două lumi: **predicatele** selectează rânduri (populația), **variabilele** poartă valori (intrările testelor). Nu există punte între ele. Un predicat nu poate deveni o valoare.

Cauza de fond este aceeași ca la G1 și G2 — o presupunere nescrisă. Registrul v1.0 a fost construit pentru testele care *compară grupuri deja separate* (matched-null pe evenimente), nu pentru testele care *modelează contrastul* între expuși și neexpuși în același model. Prima familie are nevoie doar de selecție; a doua are nevoie de expunere ca variabilă.

### 2.2 Impactul asupra contractului

`regression_control@v1` cere `exposure_ref`. Dacă expunerea este un eveniment, nu există nicio variabilă care să o reprezinte. La execuție, motorul ar avea două ieșiri posibile: să se oprească, sau să **construiască singur indicatorul** din predicatele populației. A doua este o alegere de proiectare făcută de executant — interzisă de contract §1.7 și §2.9, exact ca la G2.

Există și o a doua încălcare, mai subtilă: fără indicator, populația trebuie să conțină doar evenimente, deci regresia nu are grup de comparație. Motorul ar trebui să deducă de unde vine grupul de referință. Aceeași categorie de deducție interzisă.

### 2.3 Impactul asupra execuției

Blocant pentru F5+ pentru orice candidat cu expunere-eveniment: **DC-0004 și DC-0008 astăzi, plus Grupul I în întregime**. Nu blochează matched-null, dip test, GMM, changepoint, placebo, multiverse sau power simulation.

### 2.4 Variantele și riscurile lor

| Opțiune | Descriere | Riscuri |
|---|---|---|
| **G3-a** | nicio acțiune | Controlul declarat **obligatoriu** de constituția §6 rămâne inexecutabil pentru toată familia de candidați cu expunere-eveniment. La prima rulare, motorul ar fi pus să deducă. Risc maxim |
| **G3-b** | primitivă `indicator@v1 {predicate}` — evaluează un predicat declarat inline și produce o variabilă 0/1, cu `availability` și `role` ca orice altă variabilă | Indicatorul poate fi declarat cu o disponibilitate mai devreme decât a variabilelor pe care predicatul le folosește → **gaură de leakage**. Se închide printr-o verificare de consistență (§2.6). Al doilea risc: distincția cohortă/expuși devine responsabilitatea autorului specificației |
| **G3-c** | populații per test (`tests[].population`) | **Cere schemă nouă.** Multiplică semantica denominatorului și a lui `min_n` (câte una per test). Face ca „populația" să nu mai fie un obiect unic auditabil |
| **G3-d** | bloc dedicat cohortă + expunere în `population` (`{kind: none}` / `{kind: predicate}`) | **Cere schemă nouă.** Cel mai curat semantic (cohortă + expunere, ca în epidemiologie), dar impune ceremonie și în specificațiile fără expunere, și cere migrarea tuturor fixturilor |
| **G3-e** | `regression_control@v1` primește direct `event_predicate_ref` | Indicatorul ar exista doar în interiorul unei metode, invizibil pentru placebo sau stratificare. Ar fi o mărime **fără `availability` declarată** — exact obiecția pentru care au fost respinse numele magice de coloană la G1 |
| **G3-f** | inferență din structura populației („expunerea = ce selectează populația") | Deducție a motorului. De respins fără discuție |

### 2.5 Recomandare: **G3-b**

Argumentele, în ordinea greutății:

1. **Un singur mecanism.** Indicatorul este o variabilă obișnuită: se declară în `variables`, cu `params`, `availability` și `role`. Nimic nou de învățat pentru Statistician, nimic nou de validat pentru motor.
2. **Zero modificări de schemă și zero modificări de gramatică.** Tipul de referință `predicate` există deja în gramatică (`ve/spec/domains.py`), iar validatorul îl rezolvă deja recursiv — este mecanismul folosit de `and@v1`/`or@v1` pentru operanzii lor. `indicator@v1` reutilizează exact acea cale.
3. **Rămâne sub garda de leakage**, cu condiția verificării din §2.6.
4. **Deblochează, cu o singură intrare, toată familia de protocoale** din §1.2, nu doar DC-0004.
5. Față de G3-d, care este mai curat semantic: costul unei scheme noi și al migrării tuturor fixturilor nu se justifică atâta timp cât aceeași separare cohortă/expunere se exprimă declarativ prin `population.include` (eligibilitate) + variabila indicator (expunere). Dacă practica arată că autorii confundă cele două, G3-d rămâne calea de escaladare, iar migrarea G3-b → G3-d este mecanică.

### 2.6 Modificările necesare

| Componentă | Modificare |
|---|---|
| **Gramatică** (`ve/spec/domains.py`) | **niciuna** — tipul `predicate` există deja |
| **Registru** (v1.2) | o intrare: `indicator@v1 {required_params: {predicate: "predicate"}}`, cu notă despre semantica 0/1 și despre regula de disponibilitate |
| **Validator** (`registry_validator.py`) | **o verificare nouă, obligatorie**: disponibilitatea indicatorului nu poate fi mai devreme decât a oricărei variabile folosite în predicatul lui — `offset_bars(indicator) ≥ max(offset_bars(variabile referite))`. Fără ea, un indicator declarat la offset −1 peste o variabilă de la offset 0 ar fi o gaură de leakage curată |
| **Registru — regulă** | notă că `population.include` definește **cohorta eligibilă**, iar indicatorul definește **expunerea**; denominatorul raportează ambele |
| **Teste** | ~7: indicator valid; indicator cu predicat inexistent (E3); indicator cu variabilă nedeclarată în predicat (E2); indicator cu disponibilitate anterioară intrărilor (E2, tripwire nou); indicator folosit ca `exposure_ref` într-o regresie; specificația de referință DC-0004 completată la 15/15; predicatul indicatorului validat recursiv |
| **Schemă** | **nu este necesară versiune nouă** |

---

## 3. G4 — semantica listelor de predicate nu este definită

### 3.1 Cauza exactă

`population.include`, `population.exclude` și `cells[].predicates` sunt liste. Nicăieri — nici în schemă, nici în registru, nici în documentul de schemă — nu este scris cum se combină elementele. Conjuncția a fost presupusă de toată lumea, inclusiv de mine când am scris specificația de referință.

Cauza: lista a fost aleasă pentru un motiv **operațional** (fiecare predicat are un `id`, ca denominatorul să raporteze respingerile per criteriu), iar acel motiv a ascuns întrebarea semantică. O structură aleasă pentru raportare a ajuns să poarte, tăcut, un operator logic.

### 3.2 Impactul asupra contractului

Astăzi, niciunul — validarea nu evaluează predicate. Dar la F4, constructorul de populație trebuie să implementeze *ceva*. Dacă acel ceva nu este scris în prealabil, motorul va fi ales o semantică pe cont propriu. Este forma cea mai insidioasă de decizie a executantului: nu apare ca o alegere, apare ca o implementare.

Riscul simetric este mai probabil: Statisticianul scrie o listă crezând că exprimă altceva decât ce implementează motorul, iar rezultatul este o populație greșită care nu semnalează nimic.

### 3.3 Impactul asupra execuției

Nu blochează nimic. Devine periculos exact la F4.

### 3.4 Variantele și riscurile lor

| Opțiune | Descriere | Riscuri |
|---|---|---|
| **G4-a** | nicio acțiune | Semantica se fixează implicit prin prima implementare. Risc de divergență tăcută între intenție și execuție |
| **G4-b** | un singur predicat-rădăcină în loc de listă | **Cere schemă nouă** și, mai grav, **distruge denominatorul per criteriu** — fără id-uri per criteriu, nu se mai poate raporta câte bare a respins fiecare condiție, adică exact golul universal al portofoliului. De respins |
| **G4-c** | câmp explicit `combine: "and" \| "or"` per listă | **Cere schemă nouă.** Un `or` la nivel de `include` ar face denominatorul per criteriu neinterpretabil (o bară respinsă de un criteriu poate fi totuși inclusă) |
| **G4-d** | **documentare normativă în registru**: listele sunt conjuncții; `exclude` exclude la potrivirea *oricărui* element; logica ne-conjunctivă se exprimă explicit prin `and@v1`/`or@v1`/`not@v1`; + teste de conformitate la F4 | Documentația nu este execuție: regula nu devine obligatorie decât când constructorul de populație există. Se acoperă prin fixturi de conformitate la F4 |

### 3.5 Recomandare: **G4-d**

Este singura variantă care fixează semantica fără să sacrifice denominatorul per criteriu — mărimea pe care întreaga structură de listă a fost proiectată să o producă. Costul este zero cod acum și o suită de fixturi la F4.

De consemnat, în aceeași regulă, două cazuri-limită pe care documentul actual nu le acoperă: `exclude: []` înseamnă „nicio excludere" (declarat explicit, nu presupus), iar `cells[].predicates: []` înseamnă „toată populația" — folosit deja în specificația de referință pentru testele nestratificate.

### 3.6 Modificările necesare

| Componentă | Modificare |
|---|---|
| **Gramatică** | niciuna |
| **Registru** (v1.2) | 3 reguli noi în blocul `rules`: conjuncția listelor, semantica `exclude`, semantica listelor goale |
| **Validator** | niciuna acum |
| **Teste** | 3 teste de invariant care verifică prezența regulilor în registru; suita de conformitate a semanticii se scrie la F4, odată cu constructorul de populație |
| **Schemă** | **nu este necesară versiune nouă** |

---

## 4. G5 — referințe tipizate ca `string`

### 4.1 Cauza exactă

Aceeași cauză de fond ca G2, în alte locuri: descriptorii de domeniu au fost scriși parametru cu parametru, manual, iar caracterul de *referință* nu a fost aplicat sistematic. Unde autorul s-a gândit „acesta trimite la o variabilă" a scris `variable_ref`; unde s-a gândit „acesta e un nume", a scris `string`. Aceeași noțiune, două tipizări, după cum a picat.

Inventar exact, măsurat pe registrul v1.1 — **13 parametri** în 3 categorii de referință:

| Referă o **variabilă** | Referă un **test** | Referă un **predicat** |
|---|---|---|
| `lag@v1.variable_ref` | `placebo_control@v1.base_test_ref` | `proportion@v1.predicate_ref` |
| `forward_excess@v1.forward_return_ref` | `multiverse@v1.base_test_ref` | |
| `forward_excess@v1.baseline_ref` | | |
| `rolling_quantile@v1.variable_ref` | | |
| `dip_test@v1.variable_ref` | | |
| `gaussian_mixture@v1.variable_ref` | | |
| `changepoint@v1.variable_ref` | | |
| `regression_control@v1.outcome_ref` | | |
| `regression_control@v1.exposure_ref` | | |
| `descriptive_measurement@v1.variable_ref` | | |

### 4.2 Impactul asupra contractului

Identic cu G2 înainte de corectare: o referință inexistentă trece validarea și devine problemă abia la execuție, unde motorul ar fi pus fie să se oprească (corect, dar târziu — după ce specificația a fost declarată validă), fie să deducă la ce s-a referit autorul (interzis).

Cazul cel mai grav este `regression_control@v1.exposure_ref`, pentru că este exact parametrul pe care G3 urmează să îl alimenteze cu indicatorul nou.

### 4.3 Impactul asupra execuției

Nu blochează astăzi nicio metodă, dar slăbește garanția centrală a etapei 2: „o specificație validată este executabilă fără decizii suplimentare".

### 4.4 Variantele și riscurile lor

| Opțiune | Descriere | Riscuri |
|---|---|---|
| **G5-a** | nicio acțiune | Menține o clasă de defecte deja identificată și deja corectată în altă parte. Incoerență internă a registrului |
| **G5-b** | retipizare completă: cei 10 parametri de variabilă → `variable_ref`; două tipuri de referință noi în gramatică, `test_ref` și `predicate_ref`, pentru ceilalți 3 | Muncă de gramatică + validator (două ramuri noi de rezolvare). `predicate_ref` cere ca predicatele declarate în populație să fie referibile după `id`, ceea ce înseamnă că id-urile de predicat devin parte din interfața publică a specificației |
| **G5-c** | doar referințele de variabilă acum; `test_ref` și `predicate_ref` amânate | Lasă aceeași clasă pe jumătate deschisă și impune două migrări în loc de una. Riscul practic: a doua migrare se amână la infinit |
| **G5-d** | verificare euristică: orice parametru cu sufixul `_ref` se rezolvă automat | **Inferență după numele parametrului.** Motorul ar ghici semantica dintr-o convenție de denumire. De respins — este exact tiparul pe care arhitectura îl interzice |

### 4.5 Recomandare: **G5-b**

Retipizare completă, într-o singură revizuire. Motivul pentru care nu recomand G5-c: golul a fost descoperit tocmai pentru că fusese lăsat pe jumătate rezolvat la G2, iar a doua jumătate a ieșit la iveală printr-o mutație de test, nu prin recitire. O clasă de defecte identificată se închide integral sau se redeschide.

Observație de proiectare pentru `predicate_ref`: `id`-urile predicatelor devin referibile, deci trebuie să fie unice **în întreaga specificație**, nu doar la nivelul listei `include` — validatorul actual verifică unicitatea numai în `include`/`exclude`. Verificarea trebuie extinsă la predicatele imbricate și la cele din celule.

### 4.6 Modificările necesare

| Componentă | Modificare |
|---|---|
| **Gramatică** (`ve/spec/domains.py`) | 2 tipuri noi în `REFERENCE_TYPES`: `test_ref`, `predicate_ref` |
| **Registru** (v1.2) | 13 descriptori retipizați (10 × `variable_ref`, 2 × `test_ref`, 1 × `predicate_ref`) |
| **Validator** | 2 ramuri noi în rezolvator; extinderea verificării de unicitate a id-urilor de predicat la întreaga specificație |
| **Teste** | ~10: câte o mutație de referință inexistentă pentru fiecare categorie; un test de inventar care verifică mecanic că **niciun** parametru cu semantică de referință nu mai are domeniul `string`; unicitatea globală a id-urilor de predicat |
| **Schemă** | **nu este necesară versiune nouă** |

---

## 5. Ordinea recomandată de rezolvare

```
1. G5   gramatică (test_ref, predicate_ref) → registru → validator → teste
2. G3   registru (indicator@v1) → validator (verificarea de disponibilitate) → teste
3. G4   reguli în registru (fără cod) → teste de invariant
        [semantica se impune executabil la F4, cu fixturi de conformitate]
```

**G5 înaintea lui G3, obligatoriu.** Motivul: indicatorul produs de G3 este destinat parametrului `regression_control@v1.exposure_ref`, care astăzi este `string`. Dacă G3 se livrează primul, rezultatul este o variabilă care poate fi numită dar nu verificată — adică fix defectul pe care G3 îl repară, mutat cu un pas mai departe. G3 fără G5 nu închide nimic.

G4 poate merge oricând; nu are dependențe și nu are cod.

**Ordinea internă a fiecărui pas rămâne cea impusă de auto-verificarea fail-closed:** gramatica înaintea registrului. Un registru care folosește `test_ref` înainte ca gramatica să îl cunoască oprește complet motorul.

### 5.1 Poarta de acceptare propusă pentru registrul v1.2

1. Specificația de referință DC-0004 exprimă **15 din 15** elemente ale designului, inclusiv regresia de control obligatorie.
2. **O a doua specificație de referință, pentru designul DC-0008** — formă complet diferită (dip test, GMM, changepoint, prag derivat din date, clasificare) care exercită `indicator@v1` în cealaltă variantă a lui, cea de apartenență la clasă. Prima aplicare a porții de publicare a produs trei goluri dintr-un singur design; a doua formă de design merită tratată la fel.
3. Testul de inventar din §4.6 trece: niciun parametru cu semantică de referință nu mai este `string`.
4. Toate metodele rămân `UNVALIDATED`.

---

## 6. Rezumatul deciziilor cerute

| Gol | Recomandare | Schemă nouă? | Registru | Gramatică | Validator | Teste |
|---|---|---|---|---|---|---|
| **G3** | `indicator@v1 {predicate}` | **nu** | +1 intrare, +1 regulă | — | +1 verificare de disponibilitate | ~7 |
| **G4** | documentare normativă a semanticii | **nu** | +3 reguli | — | — | 3 (+ conformitate la F4) |
| **G5** | retipizare completă, 13 parametri | **nu** | 13 descriptori | +2 tipuri de referință | +2 ramuri, unicitate globală de id-uri | ~10 |

**Niciunul nu cere versiune nouă de schemă. Toate trei încap într-un singur registru v1.2.**

---

## 7. Ce NU recomand

- Rezolvarea lui G3 prin inferență din structura populației sau prin expunere ascunsă în interiorul unei metode — ar recrea gaura de disponibilitate pentru care au fost respinse numele magice de coloană la G1.
- Rezolvarea lui G4 prin eliminarea listelor — ar distruge denominatorul per criteriu.
- Rezolvarea lui G5 prin euristică pe sufixul `_ref` — ghicit după numele parametrului.
- Adăugarea altor metode „cât tot deschidem registrul". Fiecare intrare nouă cere propria baterie de calibrare.
- Introducerea lanțului de rezultate între teste (§1.5) — absența lui aplică regula de preînregistrare din constituție §8.2.

---

**Registrul nu a fost modificat. Codul executabil nu a fost modificat. Nicio soluție nu a fost implementată. Nicio dată de piață nu a fost citită în afara numărătorilor factuale din §1 și din cererea de clarificare însoțitoare.**

**Validation Engine se oprește aici și așteaptă decizia CEO asupra §5 și §6.**
