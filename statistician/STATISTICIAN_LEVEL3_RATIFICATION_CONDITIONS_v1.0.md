# STATISTICIAN — CELE TREI CONDIȚII DE APROBARE ALE NIVELULUI 3

**Document ID:** STAT-LEVEL3-RATIFICATION-CONDITIONS-v1.0
**Data:** 2026-08-11 · **Autor:** Statistician
**Închide:** ZM-L1, ZM-L2, ZM-U1 din APPROVED_WITH_LIMITATIONS, pe `zone_map.py` (`11ae360`).

**Verificare de sursă:** citit direct `code/zone_map.py`. **O măsurătoare nouă, proprie, P&L-oarbă, cu NUL.** **Constatarea Red Team se confirmă și e a mea ca eroare — dar remediul propus, măsurat, NU funcționează, și o raportez ca atare.**

---

# PARTEA 1 — ZM-L1: ACCEPT ACUZAȚIA. Dar remediul propus EȘUEAZĂ la măsurătoare.

## Eroarea, confirmată în cod, și e a mea

**`_near_level(prices, avail, ref, band, i_prev)` măsoară distanța fiecărei trăsături la `ref` — PREȚUL. Deci „confluența" era co-prezența a patru trăsături în jurul prețului, nu apropierea lor UNA DE ALTA.**

> **Două trăsături la 1×ATR de preț, pe laturi opuse, sunt la 2×ATR una de alta — deloc confluente — și totuși construcția le număra ca o confluență.** Am folosit o bandă de PROXIMITATE (cât de aproape e ceva ca să fie acționabil, corect ancorată la unitatea de risc) ca bandă de CONFLUENȚĂ (cât de aproape trebuie să fie două lucruri ca să fie același loc). **Sunt două întrebări diferite, iar eu le-am confundat.**

## Am corectat construcția și am măsurat-o contra unui NUL

**Construcție corectată: confluența se măsoară ÎNTRE trăsături, în jurul unui punct-ancoră, cu o bandă de confluență separată și mai îngustă. NUL: log-randamentele amestecate — aceeași scară de volatilitate, structura de nivel DISTRUSĂ.**

```
                     k=0     k=1     k=2     k=3   |  k>=2
REAL   1,00×ATR     0,26%   0,51%   9,28%  89,95%  | 99,23%
       0,50×ATR     0,26%   0,71%   9,32%  89,71%  | 99,03%
       0,25×ATR     0,26%   1,01%   9,43%  89,30%  | 98,73%
       0,10×ATR     0,26%   1,82%  10,47%  87,45%  | 97,92%
       0,05×ATR     0,26%   2,59%  12,81%  84,34%  | 97,15%

NUL    1,00×ATR     0,06%   0,28%   5,47%  94,19%  | 99,66%
       0,05×ATR     0,06%   1,00%   6,73%  92,21%  | 98,94%
```

## Două rezultate, iar al doilea e mai grav decât acuzația

```
1. ÎNGUSTAREA BENZII NU RESTABILEȘTE GRADIENTUL.
   De la 1,00 la 0,05×ATR — de 20 de ori mai îngustă — k>=2 scade doar de la 99,23% la 97,15%.
   Saturația supraviețuiește la ORICE bandă testată.

2. NULUL SATUREAZĂ MAI MULT DECÂT REALUL.
   La fiecare bandă, k=3 e mai frecvent pe date FĂRĂ structură decât pe cele reale.
   Diferența REAL − NUL pe k>=2 e NEGATIVĂ peste tot: −0,43 la 1,00×ATR, −1,79 la 0,05×ATR.
```

> **Deci contorul de confluență, așa cum e construit, nu e doar NEINFORMATIV — e ANTI-informativ față de nul. O serie fără nicio structură produce MAI MULTĂ „confluență" decât piața reală.**

**Remediul cerut la ZM-L1 — o bandă de confluență mai îngustă — e MĂSURAT ȘI RESPINS. Îl raportez ca eșec în loc să-l adopt, pentru că adoptat ar fi arătat ca o reparație și n-ar fi fost una.**

## Cauza reală, și ea indică alt remediu

**Nu banda e problema — e DENSITATEA fiecărei trăsături în parte.** Orice punct-ancoră are toate cele trei trăsături în apropiere, la orice bandă, pentru că fiecare tip de trăsătură e el însuși saturat. **Am măsurat asta deja de trei ori: 6.755 bazine ABOVE, 474 deasupra prețului la bara mediană; 89-188 niveluri persistente; 94,87% co-prezență la nivelul 3.**

```
CALEA CARE ARE PRECEDENT: se reduce densitatea LA SURSĂ, nu la banda de confluență.
  · bazine: DOAR neconsumate (`detect_sweeps`, D7) — precedentul de la nivelul 2 a dus
    6.755 → 212, iar fracția de bare fără bazin eligibil de la 5,1% la 72,78% CAUZAL;
  · niveluri: consumare D7 la prima atingere, deja convenție ratificată;
  · FVG: expirare/umplere, nu acumulare la nesfârșit.
CRITERIU DE ACCEPTARE, pre-declarat: distribuția lui k pe date REALE trebuie să difere
  MATERIAL de nul, ȘI ÎN DIRECȚIA CORECTĂ. Azi diferă în direcția GREȘITĂ.
```

## O delimitare pe care o păstrez

**Mi s-a cerut „valoarea all-4-versus-nu". Am măsurat versiunea DISTRIBUȚIONALĂ, oarbă la rezultate. NU am măsurat valoarea în sens de edge, și nu o voi face aici: aceea e estimare, deci nivelul 6 — iar făcută la nivelul 3 ar fi al doilea estimator ȘI o selecție pe rezultate.** Testul contra nulului răspunde la întrebarea care se poate răspunde fără să atingem outcome-ul: **contorul separă ceva, sau doar banda?** Răspunsul e: nu separă.

## Consecință pentru cablare, care corectează ce am scris eu la v2.7.57

**Am scris acolo: „îl includ ca și coordonată și las contracția să decidă, la cost zero". Rămâne adevărat că nu face rău — fiind cvasi-constant, aproape că nu împarte celule. Dar nu mai pot spune că e doar „neinformativ": e o coordonată a cărei CONSTRUCȚIE e defectă.**

```
Se cablează, dar cu eticheta: coordonata k e AȘTEPTATĂ să se contracte în părinte,
și NU se raportează niciodată ca „harta aduce informație" până când criteriul contra
nulului trece în direcția corectă.
```

---

# PARTEA 2 — ZM-L2: REGRESIA. Ambele părți se repară.

## Dezvăluirea: inspecție MECANICĂ, nu dicționar

**`REDUNDANT_WITH` e un dict hardcodat cu 17 muchii. Docstring-ul invocă „două tiere, L-R1" fără să le implementeze. Nivelul 2 avea inspecția reală și e în `code/bias_h1.py`.**

```
SE REUTILIZEAZĂ `redundancy_by_static_inspection` + `ratified_vocabulary` din `bias_h1.py`.
Ambele tiere, obligatorii (amendamentul L-R1):
  DIRECT    primitiva e apelată ÎN funcția de declanșator;
  INJECTAT  primitiva e apelată la nivel de MODUL și rezultatul e PASAT ca parametru.
Vocabularul se restrânge mecanic la FUNCȚIILE modulelor ratificate.
Un dicționar întreținut de mână se ÎNVECHEȘTE tăcut la fiecare candidat nou — exact
proprietatea pe care inspecția mecanică o are și el nu.
```

**Test de non-regresie, obligatoriu: maparea produsă de inspecție trebuie să CONȚINĂ toate cele 17 muchii hardcodate. Dacă nu le conține, una dintre cele două e greșită și se află care ÎNAINTE de a șterge dicționarul.** Nu înlocuiesc o listă cu un algoritm fără să verific că algoritmul o acoperă.

## Cascada: prin TIP, nu prin `if` pe booleeni de la apelant

**Cascada nivel 1/2 → 3 e azi un `if` pe booleeni pasați de apelant. Un apelant care uită să-i paseze obține tăcut o hartă „validă".**

```
Se aplică contractul din specificația de cablare (v2.7.57), fără excepție:
   LevelOutput[T] = Ok(value, as_of, valid_until, schema_hash) | Unavailable(reason, as_of)
Nivelul 3 PRIMEȘTE `LevelOutput[RegimeState]` și `LevelOutput[BiasState]` — nu booleeni.
Un `Unavailable` la intrare produce `Unavailable` la ieșire, cu motivul PROPAGAT.
`mypy --strict` face din ramura lipsă o EROARE DE TIP, nu o scăpare de review.
```

---

# PARTEA 3 — ZM-U1: A TREIA OARĂ, ȘI REGULA GENERALĂ SE APLICĂ IDENTIC

**`status=UNAVAILABLE` și mulțimea vidă VALIDĂ au amândouă `zones=()`. Consumatorul trebuie să verifice și status, și lungime — iar dacă uită, mulțimea vidă validă e citită ca „harta există".**

**Regula generatoare, deja enunțată: o stare „fără informație" nu are voie să fie REPREZENTABILĂ în același tip ca una informativă. Aici sunt TREI stări, nu două, și asta e miezul:**

```
Unavailable(reason)      n-am putut calcula          ← FĂRĂ informație
Ok(zones = [])           am calculat, nimic nu se califică   ← CU informație. E un REZULTAT.
Ok(zones = [z1, z2, …])  am calculat, iată-le                ← CU informație
```

> **Mulțimea vidă NU e un eșec — am scris asta chiar în specificația nivelului 3 („mulțime vidă = rezultat valid, nu eroare"). Colapsarea la `zones=()` a distrus exact distincția pe care o cerusem.** Cu tipul-sumă, `Unavailable` nu e un `Ok`, deci `len(zones)` nici nu e accesibil pe el — **ambiguitatea dispare prin construcție, nu prin vigilența consumatorului.**

**A treia aplicare a aceleiași unelte: L-U2 la nivelul 1, Z4-L1 la nivelul 4, ZM-U1 aici. Aceeași regulă, același tip, aceeași impunere prin `mypy --strict`. O reutilizez, nu o reinventez.**

---

# PARTEA 4 — CONSTATAREA DE CONSEMNAT: „harta" supraestimează

**Accept integral, și o consemnez fără atenuare:**

```
CERUT      Zona A Confidence 93 · Zona B 81 · Zona C 72     — o ORDONARE
LIVRAT     prezent / absent                                  — un BOOLEAN
```

**Cu 4 trăsături și prag 4, gradientul k=1/2/3 e aruncat. Nivelul 6 primește da/nu, nu o ordonare. Cerința NU e satisfăcută în forma cerută.**

## Dar motivul pe care l-am dat era doar parțial corect, și îl corectez

**Am spus: gradientul nu se poate pondera, fiindcă ponderile ar cere potrivire pe rezultate, adică al doilea estimator. Asta rămâne adevărat — ȘI E IRELEVANT AICI.**

> **Gradientul nu s-a pierdut din lipsa ponderilor. S-a pierdut pentru că BANDA a aplatizat CONTORUL.** Un contor NEPONDERAT care chiar variază E o ordonare — exact ce cerea CEO, fără nicio pondere și fără un al doilea estimator.

**Deci ZM-L1 era, în principiu, calea de recuperare a gradientului — CEO are dreptate. Măsurătoarea din Partea 1 arată însă că îngustarea benzii nu o deschide: contorul rămâne saturat la 0,05×ATR, iar nulul saturează mai mult decât realul.**

```
CALEA RĂMASĂ, singura susținută de măsurătoare: reducerea densității LA SURSĂ (Partea 1).
Dacă trăsăturile devin rare, contorul variază, ordonarea revine — NEPONDERATĂ, deci
fără al doilea estimator. Până atunci, cerința rămâne NESATISFĂCUTĂ, și o spun așa.
```

---

## HANDOFF

**VE:** (1) `LevelOutput[T]` la intrările nivelului 3 — fără booleeni de la apelant; (2) tipul-sumă cu trei stări din Partea 3; (3) `redundancy_by_static_inspection` din `bias_h1.py`, cu testul de non-regresie contra celor 17 muchii ÎNAINTE de a șterge dicționarul; (4) criteriul contra nulului ca test permanent. **Banda de confluență NU se îngustează — măsurat, nu ajută.**
**Red Team, ținte:** dacă nulul cu log-randamente amestecate distruge într-adevăr structura de nivel sau doar o rearanjează; dacă „real mai puțin confluent decât nul" e un rezultat sau un artefact al construcției de ancoră; și dacă reducerea densității la sursă nu mută pur și simplu saturația în altă parte, cum am întrebat și la bazinele de la nivelul 2.
**CEO, patru lucruri:** **(1) acuzația e corectă și eroarea e a mea — am folosit o bandă de PROXIMITATE ca bandă de CONFLUENȚĂ, adică am măsurat distanța la PREȚ, nu între trăsături. (2) DAR remediul propus, măsurat, EȘUEAZĂ: de la 1,00 la 0,05×ATR, k≥2 scade doar de la 99,23% la 97,15% — iar NULUL saturează MAI MULT decât realul, deci contorul e anti-informativ, nu doar neinformativ. Îl raportez ca eșec în loc să-l adopt. (3) Cauza reală e densitatea FIECĂREI trăsături, nu banda; calea cu precedent e consumarea la sursă, care la nivelul 2 a dus 6.755 bazine la 212. (4) Consemnez că cerința ta nu e satisfăcută — ai cerut o ordonare, ai primit un boolean — și îmi corectez motivul: nu ponderile lipsesc, ci contorul e aplatizat de bandă; un contor neponderat care VARIAZĂ e deja ordonarea cerută.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.58 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
