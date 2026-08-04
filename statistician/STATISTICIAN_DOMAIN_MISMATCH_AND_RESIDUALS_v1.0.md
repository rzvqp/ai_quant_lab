# STATISTICIAN — NEPOTRIVIREA DE DOMENIU (RT-CODE-A-0006) ȘI CELE TREI REZIDUURI

**Document ID:** STAT-DOMAIN-MISMATCH-AND-RESIDUALS-v1.0
**Data:** 2026-08-04 · **Autor:** Statistician

**Verificare de sursă:** citit direct `PROJECT_AUDIT.md` (D2, D3), `code/wp5_battery.py`, `code/phase1_screening.py`, `docs/MATCHED_NULL_VALIDATION.md`. **Constatarea Red Team se confirmă VERBATIM.** Una dintre măsurători îmi contrazice propria ipoteză structurală și o consemnez ca atare.

---

# PARTEA 0 — CONFIRMARE, ȘI O A DOUA NEPOTRIVIRE PE CARE RAPORTUL NU O NUMEȘTE

**D3, caveat de scop (2026-07-25), citat exact: „validated regime = 1,5×ATR stops on generic signals; structural-stop families (the D2 sources) were never in the calibration battery → matched-null is NOT validated for them."** Iar **D2 e HIGH/OPEN și spune literal „gates any structural-stop use".** Red Team nu a găsit o interpretare — a găsit o poartă deja scrisă în audit și neînchisă.

## Mecanismul, nu doar eticheta „în afara domeniului"

**De ce contează tipul de stop pentru calibrarea unui NUL:**

```
stop STRUCTURAL → distanța de risc poate fi ~0 de la intrare → R = pnl/risc EXPLODEAZĂ
                  (D2, măsurat: S6 R până la +166; primele 5 tranzacții = 71% din profit)
                → statistica testată (media net_R) e dominată de câteva observații
                → eroarea de acoperire a bootstrap-ului crește cu ASIMETRIA și scade cu √n
```

**Nuanță pe care o adaug în apărarea motorului: un bootstrap E adaptativ la formă prin construcție** — reeșantionează rezultatele observate, deci nu are nevoie de o calibrare per formă de distribuție. **Deci nepotrivirea NU e automat fatală.** Ce nu se adaptează: termenul de eroare de acoperire, care crește cu asimetria. **Iar bateria nu conține niciun caz cu forma produsă de stopuri structurale, deci nimeni nu știe cât e acel termen aici.** Asta e diferența dintre „probabil e bine" și „calibrat".

**Și podeaua schimbă problema:** `min_executable_risk` (termenul 0,10×ATR domină la XAUUSD, verificat în `phase1_screening.py`) **mărginește explozia lui R.** Distribuția pe care o produce pipeline-ul real e cea PODITĂ — nu cea din D2. **Deci bateria trebuie re-rulată cu podeaua ACTIVĂ**, altfel calibrează o distribuție pe care nimeni nu o mai tranzacționează.

## A DOUA nepotrivire de domeniu, negăsită în raport: UNITATEA blocului

**`wp5_battery.py`, verbatim: „Șocurile = randamente REALE per-bară M15", iar `H=20` e „orizontul real de dependență finită" — în BARE. De acolo vine `L≥28`.**

**Dar statistica candidaților e o medie peste TRANZACȚII, nu peste bare.**

```
L = 28 justificat ca 28 BARE  (H=20 bare ≈ 5 ore de dependență)
L = 28 aplicat pe 28 TRANZACȚII → la ~1 tranzacție/zi înseamnă ~28 de ZILE
                                → de ~130 de ori mai lung decât orizontul care l-a justificat
```

> **Nu e o alegere conservatoare — e un transplant de unitate.** L a fost derivat într-o unitate și aplicat în alta, fără re-derivare. **Și de aici vine direct S-R2:** numărul de blocuri e n/28 în tranzacții, deci degenerează la n mic — la n=7, zero blocuri. Nu sunt două probleme, e una.

### Remediul, care le rezolvă pe ambele deodată

```
BLOC PE TIMP CALENDARISTIC, nu pe indexul tranzacției.
  bloc = O ZI de tranzacționare (~92 bare M15 = constanta empirică a laboratorului)
  o zi > 4 × H (20 bare) ⇒ blocul conține integral orizontul de dependență care a justificat L
  numărul de blocuri = zilele DISTINCTE cu tranzacții, NU n/28
```

**Corect ca unitate prin construcție, și imun la frecvența de tranzacționare.** Un candidat cu n=135 pe 8 ani are ~100+ zile distincte — deci ~100 de blocuri, nu 4,8.

---

# PARTEA 1 — RĂSPUNSUL LA CELE TREI OPȚIUNI: SE EXTINDE. Caveat-ul nu e disponibil.

## De ce opțiunea „se declară limitarea și verdictele poartă caveatul" NU e pe masă

**Un caveat e legitim când mărginește DOMENIUL unei afirmații.** Am folosit unul acum patru zile: „valabil pentru săptămâni complete, 94% din populație". Cititorul știe exact ce a cumpărat.

**Aici limitarea nu e pe domeniu — e pe RATA DE EROARE însăși.**

> **Un p-value a cărui FPR e necunoscută nu e un p-value cu un caveat. Nu e un p-value.** Singurul lucru pe care numărul îl afirmă e o rată de eroare; un caveat care spune „rata de eroare poate fi deplasată cu o cantitate necunoscută, într-o direcție necunoscută" nu îngustează afirmația — o anulează. **Caveat-ele pot mărgini scopul; nu pot mărgini miscalibrarea.**

## „Altceva" — și e mai bun decât extinderea cerută

**„Stopuri structurale" NU e o unitate de domeniu validă.** Candidații curenți folosesc: extrema barei de touch, fitilul sweep-ului, podeaua OB, marginea FVG, minimul ambelor structuri. **Acestea produc distribuții de R DIFERITE între ele** — un stop la extrema barei de touch e strâns (rată mare de stop-out, câștiguri mari în R), unul la podeaua OB e larg (opusul). Măsurat pe screening: winrate 0,208 la CAND-0029 vs 0,470 la CAND-0031 vs 0,377 la CAND-0011. **A calibra o singură baterie „pentru stopuri structurale" ar reproduce exact eroarea pe care o reparăm, doar cu o cutie mai mare.**

```
DECIZIA: CALIBRARE PER CANDIDAT, ca PRECONDIȚIE EXECUTABILĂ.

Pentru fiecare candidat, ÎNAINTE de testul lui:
  1. se ia distribuția lui PROPRIE de net_R per tranzacție din screening (podită, cu costuri) —
     artefact care EXISTĂ DEJA, nu date noi;
  2. se centrează la medie zero ⇒ nul cu adevăr cunoscut, păstrând forma, asimetria și
     masa punctuală de la podea;
  3. se generează >=1.000 serii sintetice pe grila calendaristică a candidatului;
  4. se măsoară FPR@0,05 a oracolului cu bloc-zi;
  5. POARTĂ: limita superioară a CI pe FPR <= 0,07. Peste ⇒ candidatul NU primește p-value.
```

**Costul: calcul pe artefacte existente. Nu date noi, nu luni.** Bateria nu se extinde o dată pentru o clasă — devine un pas al fiecărui protocol, ca podeaua S2.

---

# PARTEA 2 — CE ÎNSEAMNĂ PENTRU CANDIDAȚII CARE AȘTEAPTĂ

```
STATUS       neschimbat. Niciun candidat nu se retrogradează, niciunul nu se rearanjează.
PROTOCOALE   toate cele 16 din familie primesc precondiția din Partea 1, inserată înaintea
             pasului de p-value. Protocoalele deja scrise NU se rescriu — se prefixează.
BLOCAJ       REAL și îl spun direct: NICIUN candidat nu poate primi un verdict formal până
             când precondiția lui rulează. Inclusiv cei patru piloți.
             Durata: zile de calcul, nu luni de colectare.
DEMO         NEAFECTAT. Am stabilit la v2.7.34 că DEMO nu rulează niciun test și nu produce
             niciun p-value ⇒ nu are domeniu de depășit. Linia DEMO continuă neîntreruptă.
ORDINEA      precondiția rulează în ACEEAȘI trecere VE ca testul, imediat înainte. Nu e o fază
             separată de așteptat.
```

**Consecință care merită spusă limpede: separarea DEMO/validare, pe care am impus-o din alt motiv, e exact ce împiedică defectul ăsta să oprească tot programul.** Piloții continuă să adune cost realizat și verificări de execuție; doar afirmațiile statistice așteaptă.

---

# PARTEA 3 — REZIDUURILE

## S-R2 — oracol validat la un singur n, degenerează la n mic

**Corect, și e aceeași problemă cu transplantul de unitate (Partea 0).** Rezolvat de blocul calendaristic. Plus un prag, care lipsea:

```
PRAG FIXAT:  >=10 blocuri (zile distincte cu tranzacții) MINIM;  >=20 preferat.
             Sub 10 ⇒ bloc-bootstrap INDISPONIBIL, candidatul nu primește p-value pe această cale.
```

**Verificare de consistență cu criteriul de triaj: orice candidat care trece N_MIN=25 într-un regim are, practic, >=10 zile distincte cu tranzacții. CAND-0023 (n=7) eșuează aici la fel cum a eșuat la triaj — două instrumente independente, aceeași concluzie.** Nu e o coincidență: ambele măsoară aceeași sărăcie de informație.

## S-R3 — garduri lejere, „CALIBRATED" supraevaluează

**Red Team are dreptate pe ETICHETĂ. Dar cifra măsurată e pe partea sigură, și distincția contează:**

```
măsurat (120 serii nule):  FPR(0,05) = 0,025   CI [0,009 ; 0,071]   ⇒ CONSERVATOR, nu lejer
adversarial (50 serii):    FPR(0,05) <= 0,075 în FIECARE scenariu
```

**Deci nu există un eșec observat — există o GARANȚIE care nu poate fi susținută la 120 de serii.** Reziduul real e limita superioară: **0,071 e de 1,42× nominalul și nu poate fi exclusă.** La m=16 asta se propagă direct în FDR.

```
REMEDIU PRIMAR    >=1.000 replicări. La 0,025 observat, limita superioară scade la ~0,037.
                  Calcul pur, fără date noi.
REMEDIU INTERIMAR dacă se testează înainte: se operează la α implicat de CI,
                  α' = 0,05 × (0,05/0,071) ≈ 0,035. Conservator, disponibil imediat.
ETICHETA          se elimină. „CALIBRATED = True" se înlocuiește cu INTERVALUL măsurat.
```

> **Regulă generală de consemnat: un cuvânt de status ascunde o cantitate. Acolo unde există un număr, se raportează numărul și incertitudinea lui, niciodată o etichetă binară.** Aceeași disciplină ca „suprimă, nu eticheta" la N_MIN.

## S-R6 — BH presupune PRDS, neverificat

**Am rulat un ECRAN, nu o verificare, și spun care e diferența.** Corelații perechi ale seriei anuale `net_R` între cei 14 candidați de categoria C:

```
66 perechi   media r = +0,275   mediana +0,250   min −0,594   max +0,904
pozitive 48/66 (73%)   material negative (r < −0,3): 4
```

**Predominant pozitiv, deci compatibil cu PRDS — dar la 7-8 observații anuale, SE(r) ≈ 0,4, deci cele 4 negative sunt în zgomot și ecranul NU poate stabili nimic.** Îl raportez ca ecran.

### Mi-am testat propria ipoteză structurală, și NU se confirmă

**Așteptam ca CAND-0009 — singurul candidat pe direcția de RUPERE, restul fiind fade — să fie negativ dependent cu ÎNTREAGA clasă fade, nu doar cu CAND-0001. Măsurat: media +0,203, pozitiv la 9 din 11.**

**Explicația, și e una care îmi întărește decizia veche în loc să o slăbească: opoziția e LOCALĂ, pe barele comune, iar barele comune sunt o minoritate din populația fiecăruia.** Agregatul anual e dominat de barele necomune, unde ambii beneficiază de aceleași condiții. **De aceea partiția de la v2.7.35 a fost corect ȚINTITĂ pe barele suprapuse, nu pe relația întreagă.** Dacă aș fi partiționat relația global, aș fi corectat ceva ce nu există.

### Verdict pe S-R6: NU acceptat prin presupunere — verificarea se PROGRAMEAZĂ

```
VERIFICAREA   matricea de corelații pe grilă LUNARĂ (nu anuală), calculată din propria trecere
              VE ca produs secundar. La ~90-100 de luni, SE(r) ≈ 0,10 — resolubil.
              Evaluată ÎNAINTE de pasul BH, nu după.
REGULA, pre-declarată:
  toate perechile r >= 0            ⇒ dependență pozitivă susținută empiric, BH se aplică
  o pereche material negativă       ⇒ acea pereche se partiționează (procedeul CAND-0009),
                                      restul familiei rămâne pe BH
  negativitate difuză, nepartiționabilă ⇒ FAMILIA TRECE PE BY
COSTUL FALLBACK-ULUI, cuantificat acum: BY = BH × Σ(1/i), i=1..16 = 3,38×.
              (La m=7 era 2,59×; creșterea familiei scumpește fallback-ul, nu BH-ul.)
```

**Nu e „acceptat pentru că probabil e în regulă". E o verificare programată la rezoluția la care e posibilă, cu regula și prețul alternativei fixate înainte de a vedea rezultatul.**

---

## HANDOFF

**VE, ordinea e obligatorie:**
1. **re-derivă blocul pe TIMP CALENDARISTIC** (bloc = zi de tranzacționare) și retrage `L=28` aplicat pe indexul tranzacției — e o eroare de unitate, nu o setare;
2. **precondiția de calibrare per candidat** (Partea 1, ≥1.000 replicări, poartă CI ≤ 0,07), rulată imediat înaintea fiecărui test, pe distribuția proprie de screening;
3. **matricea de corelații lunară** înaintea pasului BH, cu regula din S-R6;
4. abia apoi p-value. **Niciun verdict formal înainte de (1)-(3).**

**Red Team:** două ținte explicite — dacă blocul-zi conține într-adevăr întreaga dependență a rezultatelor de tranzacție (nu doar pe cea a barelor), și dacă centrarea la medie zero păstrează suficient din formă ca nulul per candidat să fie legitim.
**Alpha:** nimic de făcut; niciun candidat nu se schimbă.
**CEO:** un blocaj real, cu o durată — **niciun verdict formal până rulează precondiția, inclusiv pentru cei patru piloți; costul e zile de calcul pe artefacte existente, nu colectare nouă. Linia DEMO nu e atinsă**, pentru că DEMO nu produce p-value.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.45 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
