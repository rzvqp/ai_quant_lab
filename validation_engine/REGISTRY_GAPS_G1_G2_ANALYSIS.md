# ANALIZA GOLURILOR DE REGISTRU G1 și G2
### Documentul de decizie care precedă orice modificare a Capability Registry

**Document ID:** VE-GAPS-G1G2-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Statut:** **ANALIZĂ — în așteptarea deciziei CEO.** Registrul nu a fost modificat. Nicio implementare nu a început.
**Descoperite în:** faza F2 (`F2_REPORT.md` §7)
**Documente atinse de decizie:** `capabilities.json`, `CAPABILITY_REGISTRY_v1.0.md`, eventual `ve/spec/domains.py`

---

## 1. Enunțul celor două goluri

**G1 — nu există primitivă pentru seria brută OHLCV.** Registrul conține numai mărimi derivate (`atr@v1`, `parkinson_volatility@v1`, `forward_return@v1`, …). Nu există nicio cale de a referi direct `open`, `high`, `low`, `close`, `volume`.

**G2 — statisticile nu își pot primi parametrii.** Metodele primesc statistica prin descriptorul `statistic_id`, adică un simplu identificator. Dar 6 din cele 7 statistici din registru au parametri obligatorii proprii (`mean@v1` cere `variable_ref`, `trimmed_mean@v1` cere și `trim_pct`, `difference_in_means@v1` cere patru). Nu există unde să fie transmiși.

---

## 2. De ce au apărut

### 2.1 G1 — omisiunea presupusului

Registrul v1.0 a fost construit prin enumerarea a ceea ce cereau explicit designurile deja livrate (rapoartele Phase 1 pentru DC-0008, DC-0003, DC-0004). Acele documente numesc testele și mărimile derivate, dar nu numesc niciodată prețul brut — pentru un cititor uman, „prima bară a zilei cu high > prior-day high și close < prior-day high" nu are nevoie de nicio primitivă: `high` *este* bara.

Cauza de fond este însă taxonomică, nu redacțională. Categoria s-a numit `variable_primitives` și a fost gândită ca **listă de calcule**. Prețul brut nu este un calcul, este intrarea. Nu exista o categorie pentru „mărime observată direct din sursă", iar `variable_primitives` a confundat „variabilă derivată" cu „orice mărime referibilă".

Un catalog construit din ce a scris cineva conține exact ce a scris. Nu conține ce a presupus.

### 2.2 G2 — regula aplicată în interiorul catalogului, nu la granița dintre cataloage

Registrul are o regulă centrală: *niciun parametru opțional, totul explicit*. Regula a fost aplicată riguros **în interiorul** fiecărei categorii. Nu a fost aplicată **compoziției** dintre categorii: momentul în care o entitate de catalog este folosită ca argument al altei entități de catalog.

Diagnosticul precis, verificat pe registrul actual:

> **Statisticile sunt singura categorie de entități cu parametri obligatorii care nu are un loc de declarare în specificație.**

Toate celelalte referințe încrucișate trimit la obiecte care se declară undeva, cu parametrii lor: `variable_ref` → secțiunea `variables`; `base_test_ref` → secțiunea `tests`; `predicate_ref`, `baseline_ref` → obiecte declarate. Predicatele, deși folosite inline, au și ele loc de declarare — schema le cere forma `{id, predicate, params}`. Doar statistica este invocată printr-un identificator gol.

---

## 3. Impactul asupra arhitecturii

**Rezultatul principal: niciunul dintre cele două goluri nu atinge arhitectura aprobată.** Contractul, `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md` și fluxul de execuție rămân neschimbate. Ambele sunt conținute în stratul de vocabular.

Aceasta este exact plata deciziei luate la F1 — *schema validează forma, registrul validează vocabularul, registrul este sursa unică de adevăr* — care permite extinderea vocabularului fără o versiune nouă de schemă.

| Dimensiune | G1 | G2 |
|---|---|---|
| Contract §1–§4 | neatins | neatins |
| Arhitectură (straturi, flux, interfețe) | neatinsă | neatinsă |
| `SPEC_SCHEMA_v1.0.json` | neatinsă | neatinsă *(depinde de opțiune — vezi §5)* |
| `capabilities.json` | + intrări noi | + descriptor nou |
| `ve/spec/domains.py` | neatins | + o formă de gramatică |
| Validare (F2) | trece deja | trece deja |
| **Execuție (F5+)** | **blocată** | **blocată** |

### 3.1 Impactul real al G1

Blochează exact clasa de evenimente **comparație preț ↔ nivel**. Exemplul cel mai bine documentat este evenimentul central al DC-0004 (`high > PDH` și `close < PDH`, citat verbatim în raportul Phase 1): nivelul există în registru (`prior_period_extreme@v1`), dar mărimea cu care este comparat nu.

Predicatele de populație operează pe `variable_ref | number`. Fără serie brută, niciun predicat nu poate referi prețul. Populațiile exprimabile astăzi sunt doar cele definite integral prin praguri pe mărimi derivate.

### 3.2 Impactul real al G2 — mai grav decât pare

La validare, G2 este invizibil: `statistic: "mean@v1"` trece etapa 2 fără reproș. La execuție însă, motorul ar primi o metodă căreia îi lipsește informația despre *ce* măsoară.

În acel punct există exact două comportamente posibile: fie motorul se oprește, fie **deduce** variabila (de exemplu „singura variabilă cu rol `outcome`"). A doua variantă este o alegere făcută de Validation Engine în locul Statisticianului — adică fix ce interzice contractul §1.7 și §2.9.

> G2 nu este o inconveniență de sintaxă. Este o încălcare de contract programată să se producă la prima rulare reală, dacă nu este rezolvată înainte de F5.

---

## 4. Variantele de rezolvare pentru G1

| Opțiune | Descriere | Evaluare |
|---|---|---|
| **G1-a** *(nicio acțiune)* | Statisticianul rutează totul prin mărimi derivate | Respinge de la sine: evenimentele de tip comparație cu nivel sunt nucleul portofoliului. Ar bloca DC-0004, candidatul cel mai bine specificat din portofoliu |
| **G1-b** | O primitivă unică `raw_series@v1 {source_id, field}`, `field ∈ {open, high, low, close, volume, sub}`, validată față de coloanele declarate ale sursei | Un singur mecanism; variabila brută se declară exact ca oricare alta, cu `availability` și `role`; garda de leakage se aplică nemodificată |
| **G1-c** | Nume magice de coloană direct în predicate (`left: "close"`) | Creează un al doilea spațiu de nume, nedeclarat. Variabila nu ar mai avea `availability`, deci **garda de leakage nu ar avea ce verifica**. De respins |
| **G1-d** | Operand de tip „câmp" adăugat în `compare@v1` | Aceeași problemă ca G1-c, localizată în predicate. De respins |
| **G1-e** | Cinci primitive separate (`bar_open@v1`, `bar_high@v1`, …) | Echivalent funcțional cu G1-b, dar cu cinci intrări în loc de una și fără niciun câștig |
| **G1-f** | O primitivă generală `series_expression@v1` cu aritmetică pe câmpuri | Reintroduce un interpretor de expresii, refuzat explicit în `SPEC_SCHEMA_v1.0.md` §3.8. De respins |
| **G1-g** | Categorie nouă în registru, `source_fields`, separată de `variable_primitives` | Corect taxonomic, dar creează un al doilea mecanism de declarare pentru zero câștig operațional |

## 5. Variantele de rezolvare pentru G2

| Opțiune | Descriere | Evaluare |
|---|---|---|
| **G2-a** *(nicio acțiune)* | — | Inacceptabil: forțează motorul să deducă la execuție (§3.2) |
| **G2-b** | Referință parametrizată: `statistic: {id: "...", statistic: "mean@v1", params: {...}}`, **exact forma predicatelor** | Fără modificare de schemă (`tests[].params` este obiect liber, validat în etapa 2). Un singur mecanism nou de gramatică. Reutilizează un tipar deja existent și aprobat |
| **G2-c** | Secțiune nouă de nivel superior `statistics: [...]`, simetrică cu `variables`; metodele referă un id declarat | Cea mai curată simetrie („orice are parametri are loc de declarare"), dar cere **schemă v1.1** și mai multă ceremonie. Beneficiul — statistici partajate între teste sau referite din `criteria` — nu are astăzi niciun caz de folosință: țintele din `criteria` referă ieșiri de metodă, nu statistici |
| **G2-d** | Parametrul statisticii absorbit în metodă (`statistic` + `statistic_variable_ref`) | Se rupe la statisticile cu mai mulți parametri (`trimmed_mean`, `difference_in_means` cu patru). Ar umfla listele de parametri ale fiecărei metode |
| **G2-e** | Convenție de legare implicită („statistica se aplică variabilei cu rol `outcome`") | Deducție făcută de motor. De respins fără discuție |
| **G2-f** | Eliminarea catalogului de statistici; fiecare metodă declară statistica inline ca enum + variabilă | Pierde reutilizarea și mută aceeași problemă în fiecare metodă |

---

## 6. Recomandare

### 6.1 Pentru G1 — opțiunea **G1-b**

O singură primitivă `raw_series@v1`, cu `field` validat față de coloanele declarate ale sursei în registru. Argumente:

1. **Un singur mecanism.** Variabila brută se declară ca orice altă variabilă: cu `params`, `availability` și `role`. Nu apare niciun spațiu de nume paralel.
2. **Garda de leakage rămâne funcțională.** G1-c și G1-d ar produce mărimi fără `availability`, adică exact punctul orb pe care garda a fost construită să-l acopere.
3. **Validarea devine mai strictă, nu mai laxă.** Registrul declară deja coloanele fiecărei surse, iar M15 nu are coloana `sub` pe care H1/H4/D1 o au — deci o specificație care cere `sub` pe M15 se oprește cu E2, verificat mecanic.
4. **Nu deschide nicio ușă închisă deliberat.** Regulile de disponibilitate se aplică nemodificat, deci accesul brut nu permite folosirea barelor viitoare.

Sub-decizie de semnalat: pentru `raw_series@v1`, `availability.offset_bars` **selectează bara** a cărei valoare se ia (spre deosebire de `atr@v1`, unde offsetul înseamnă „calculat pe date până la"). Recomand ca această semantică să fie scrisă explicit în registru, nu lăsată la intuiție.

### 6.2 Pentru G2 — opțiunea **G2-b**, în forma predicatelor

Recomand referința parametrizată, cu **exact aceeași formă pe care schema o cere deja predicatelor**: `{id, statistic, params}`.

Argumentul decisiv nu este economia, ci consistența. Cauza de fond a lui G2 este că o entitate cu parametri nu avea loc de declarare. G2-b nu ocolește această cauză — o rezolvă, adăugând locul de declarare acolo unde entitatea este folosită, exact cum face schema pentru predicate. Rezultatul nu este „două mecanisme", ci același mecanism aplicat unde lipsea.

Față de G2-c, care este teoretic mai simetric:

- G2-c cere o schemă v1.1, iar schema este artefactul cel mai scump de revizuit — fiecare modificare consumă un ciclu de aprobare;
- beneficiul lui G2-c (statistici partajate, referibile din `criteria`) **nu are astăzi niciun caz de folosință**, verificat: țintele din `criteria` referă ieșiri de metodă;
- dacă acel caz apare, migrarea G2-b → G2-c este mecanică: declarațiile inline se ridică într-o secțiune, referințele devin id-uri.

Recomand ca `id` să fie obligatoriu și în declarația statisticii, pentru simetrie cu predicatele și pentru ca rezultatele să poată eticheta ce anume s-a măsurat.

### 6.3 Ordinea impusă de design

Extinderea registrului introduce descriptorul de domeniu `statistic_call`, neacoperit de gramatica actuală. Auto-verificarea fail-closed implementată la F2 (`registry_domains_are_parseable`) **refuză să valideze orice specificație** dacă registrul conține un descriptor neparsabil.

Consecință: ordinea nu este opțională.

```
1. extinderea gramaticii (ve/spec/domains.py) + teste
2. publicarea registrului v1.1
3. actualizarea specificației de referință și a bateriei
```

Un registru v1.1 publicat înaintea gramaticii ar opri complet motorul — comportament corect, dar evitabil dacă ordinea se respectă.

### 6.4 O recomandare de proces

Ambele goluri au ieșit la suprafață dintr-un singur motiv: specificația de referință a fost scrisă **strict în vocabularul aprobat, fără improvizații**. Un catalog nu se poate audita citindu-l; se auditează încercând să scrii cu el.

Recomand ca poartă de acceptare pentru orice versiune viitoare de registru: **scrierea unei specificații de referință complete pentru cel puțin un design real de candidat**, înainte de publicare. Costul este de ordinul zecilor de minute; ambele goluri de acum ar fi fost prinse așa, înainte de a fi publicate.

---

## 7. Ce NU recomand

- Modificarea registrului înainte de decizie (nu a fost făcută).
- Rezolvarea lui G1 prin nume magice sau operanzi speciali în predicate — ar dezactiva tăcut garda de leakage.
- Rezolvarea lui G2 prin orice formă de legare implicită — ar muta o decizie statistică în motor.
- Adăugarea, cu ocazia acestei revizuiri, a altor metode „cât tot deschidem registrul". Fiecare intrare nouă are nevoie de propria baterie de calibrare; un registru umflat înainte de F5 mută costul, nu îl elimină.

---

**Registrul nu a fost modificat. Nicio implementare nu a început. Nu s-a atins niciun artefact al laboratorului în afara `validation_engine/`.**

**Validation Engine se oprește aici și așteaptă decizia CEO asupra opțiunilor din §6.**
