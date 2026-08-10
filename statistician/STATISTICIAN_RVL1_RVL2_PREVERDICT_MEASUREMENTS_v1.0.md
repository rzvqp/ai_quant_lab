# STATISTICIAN — RV-L1 ȘI RV-L2: MĂSURĂTORILE DINAINTEA PRIMULUI VERDICT

**Document ID:** STAT-RVL1-RVL2-PREVERDICT-MEASUREMENTS-v1.0
**Data:** 2026-08-10 · **Autor:** Statistician
**Închide:** RV-L1 și RV-L2 din RT-CODE-A-0013 (`651c491`). **Tratează RV-L3 și reziduul de seed.**

**Verificare de sursă:** citit direct `reports/restante_validation_results.json`, `code/restante_validation.py`, `reports/phase1_screening_results.json`. **Două măsurători noi, proprii.** **Niciun verdict nu se emite aici — se raportează ce iese, cum s-a cerut.**

---

# PARTEA 1 — RV-L1: AUTOCORELAȚIA CROSS-ZI, MĂSURATĂ

## Observația care face întrebarea mai gravă decât pare

**Din `restante_validation_results.json`: CAND-0001 are 1.225 tranzacții în 1.093 de zile distincte. CAND-0007, 373 în 352. CAND-0002, 1.061 în 738.**

> **La 1,06-1,44 tranzacții pe zi, blocul-zi nu agregă aproape nimic — e cvasi-identic cu un bootstrap i.i.d. pe tranzacții. Deci la trei din patru piloți, ÎNTREAGA tratare a dependenței se sprijină pe independența cross-zi. Exact presupunerea nemăsurată.**

## Măsurătoarea: autocorelația seriei ZILNICE agregate, și factorul de inflație a varianței

```
cand        n_tr   zile  tr/zi     rho1     rho2     rho3     rho5     VIF   SE×
CAND-0001   1225   1093   1,12   −0,007   −0,002   −0,009   −0,002   0,840   0,916
CAND-0002   1061    738   1,44   −0,019   +0,007   −0,038   −0,003   0,909   0,954
CAND-0003   6326   1400   4,52   +0,263   +0,138   +0,138   +0,125   4,763   2,182
CAND-0007    373    352   1,06   −0,005   −0,013   −0,001   +0,003   0,852   0,923
```

**VIF = 1 + 2·Σ(pondere Bartlett × ρ), L=20 zile. E cantitatea care contează: cu cât e SUBESTIMATĂ eroarea standard.**

## Verdictul pe fiecare pilot

```
CAND-0001, 0002, 0007   VIF < 1  ⇒ dependența cross-zi e ușor NEGATIVĂ.
                        Blocul-zi e, dacă ceva, CONSERVATOR. RV-L1 se ÎNCHIDE pentru ei.
CAND-0003               VIF = 4,76  ⇒  eroarea standard adevărată e de 2,18× cea presupusă.
                        NU se închide.
```

**Predicția Red Team era că 0002, 0003 și 0007 sunt „mai expuși". Măsurat, doar 0003 e. Jumătate din grupare se confirmă, jumătate nu — și o spun, pentru că gruparea ar fi dus la o corecție inutilă pe doi candidați.**

## Ce înseamnă concret pentru p-value-ul lui CAND-0003

```
p nominal 0,01  →  z 2,326 / 2,182 = 1,066  →  p REAL ≈ 0,14
p nominal 0,05  →  z 1,645 / 2,182 = 0,754  →  p REAL ≈ 0,23
```

**Dar direcția contează, și e în favoarea verdictului:**

> **O eroare standard subestimată face RESPINGEREA prea ușoară, nu invers. CAND-0003 are E_R = −0,615 și e ARHIVAT-NEGATIV pe criteriul meu (0/8 ani, 0/3 regimuri). Nu va respinge H0 în direcția pozitivă. Deci inflația NU poate fabrica un fals pozitiv acolo — iar o NE-respingere devine, sub SE corect, și mai fermă.**

```
CLEARANCE CONDIȚIONATĂ, declarată: verdictul pentru CAND-0003 poate fi emis DOAR dacă e o
NE-RESPINGERE. Dacă testul ar respinge, p-value-ul lui e INVALID și verdictul se blochează.
```

## Remediul, pentru oricine RESPINGE

**Nu e o corecție unică — e o regulă permanentă:**

```
Pentru orice candidat care RESPINGE H0: se măsoară VIF pe seria zilnică ÎNAINTE de a raporta p.
  VIF <= 1,2  ⇒ blocul-zi e suficient.
  VIF > 1,2   ⇒ lungimea blocului se RE-DERIVĂ per candidat din autocorelația măsurată,
                nu se fixează la o zi. Aceeași lecție ca L=28: constanta se derivă în unitatea
                și pe populația în care se aplică, nu se transplantează.
```

**La CAND-0003 autocorelația persistă la lag 5 (+0,125), deci nici o săptămână n-ar fi de ajuns — dependența se întinde pe săptămâni. E FVG-CE50 cu 4,5 tranzacții/zi: reacțiile la FVG se aglomerează în zile consecutive, ceea ce explică mecanismul.**

---

# PARTEA 2 — RV-L2: PIVOTUL DE PARTIȚIE

## Ipoteza „cel mai lung overlap" e INFIRMATĂ. Suspiciunea de artefact e CONFIRMATĂ, prin alt mecanism.

```
cand        n_tr   luni cu tranzacții   median tr/lună   luni cu O SINGURĂ tranzacție
CAND-0016    108           56                 2,0                   22
CAND-0022  18168           69               276,0                    0
CAND-0024  18852           69               285,0                    0
CAND-0036   2602           69                41,0                    0
```

> **CAND-0016 nu are cel mai LUNG overlap — are cel mai SCURT (56 de luni față de 69) și de departe cel mai SĂRAC. Mediana lui e 2 tranzacții pe lună, iar 22 din 56 de luni conțin o SINGURĂ tranzacție.**

**Într-o lună cu o singură tranzacție, „valoarea lunară" ESTE rezultatul acelei tranzacții. Seria lunară a lui CAND-0016 nu e o agregare — e o succesiune de rezultate individuale, corelată cu serii agregate din sute de tranzacții. Estimările ies instabile prin construcție.**

**Deci: ipoteza specifică a Red Team e greșită, concluzia lui e corectă. Consemnez ambele.**

## Dar întrebarea e VOIDĂ, și ăsta e răspunsul care contează

**Am verificat statusul de triaj al tuturor celor patru candidați din cele trei perechi:**

```
CAND-0016   ARHIVAT-INSUFICIENT   (min pe regim 19 < 25)
CAND-0022   ARHIVAT-NEGATIV       (0/8 ani, 0/3 regimuri)
CAND-0024   ARHIVAT-NEGATIV       (0/8, 0/3)
CAND-0036   ARHIVAT-NEGATIV       (0/8, 0/3)
```

> **Niciuna dintre cele trei perechi nu conține un singur candidat care va fi testat. PRDS e o condiție pe distribuția comună a STATISTICILOR CALCULATE. Un candidat arhivat nu produce p-value și nu produce respingere, deci dependența lui cu orice altceva nu poate afecta FDR. Nu e nevoie de nicio partiție — nu pentru că am verificat-o și e curată, ci pentru că obiectul ei nu există.**

## Eroarea de specificație din spate

**`task3_monthly_matrix` a fost calculată peste 32 de candidați, nu peste FAMILIE. De aceea toate negativele materiale au venit din arhivați.**

```
REGULĂ, fixată: verificarea PRDS se face peste MULȚIMEA TESTATĂ, nu peste tot ce s-a screenat.
Și distincția care trebuie păstrată:
  m (numărul din prag)      = 16, MONOTON, include arhivații admiși — face corecția mai strictă.
  mulțimea pentru PRDS      = doar candidații care produc efectiv o statistică = 15.
Două mulțimi, două scopuri. Nu se amestecă.
```

## Verificarea restrânsă la mulțimea testată — și rezultatul licențiază BH

```
105 perechi, toate rezolvabile.  media r +0,079   min −0,212   max +0,933
perechi negative: 38 din 105.   MATERIAL negative (r < −0,30): ZERO.
singura sub −0,20: CAND-0002 ~ CAND-0031, r = −0,212, 67 de luni, o singură lună subțire.
```

> **Zero perechi material-negative în interiorul mulțimii testate. BH e valid fără nicio partiție. RV-L2 se ÎNCHIDE.**

---

# PARTEA 3 — CELE DOUĂ REZIDUURI

## RV-L3 — PRDS verificat doar pentru perechi ≥48 luni

**Nu mușcă la verdictul curent: în mulțimea testată, TOATE cele 105 perechi sunt rezolvabile.** Reziduul e real pentru viitor, nu pentru acum.

```
ACCEPTAT, cu regulă obligatorie: un candidat verdict-eligibil cu istoric sub pragul de rezolvare
NU merge pe BH pe tăcute. Are două căi: verificare la propria lui rezoluție (grilă mai fină,
cu SE(r) raportat), sau BY declarat pentru el. Alegerea se face ÎNAINTE de test, nu după.
Costul BY e deja cuantificat: 4,06× la m=32; la m=16, Σ(1/i) = 3,38×.
```

## Seed = index de enumerare

**Nu îl accept — se repară, e ieftin.**

```
Reproductibil azi, dar leagă rezultatul de ORDINEA listei. O reordonare — un candidat arhivat,
unul adăugat — schimbă toate seed-urile din aval, deci toate rulările devin ne-comparabile,
fără ca nimic material să se fi schimbat.
REMEDIU: seed derivat dintr-o CHEIE STABILĂ (hash-ul id-ului candidatului), nu din poziție.
Reproductibilitatea devine invariantă la ordine. Cost: o linie.
```

---

# PARTEA 4 — CE IESE, ÎNAINTE DE VERDICT

```
RV-L2   ÎNCHISĂ.  Nicio partiție necesară; obiectul ei e în afara familiei. BH valid pe cei 15.
RV-L1   ÎNCHISĂ pentru CAND-0001, CAND-0002, CAND-0007 (VIF < 1 ⇒ conservator).
        CONDIȚIONATĂ pentru CAND-0003: verdict admisibil DOAR ca ne-respingere.
RV-L3   ACCEPTAT cu regulă; nu blochează verdictul curent.
SEED    se repară înainte de rulare; nu blochează, dar nu se lasă așa.
```

**Un lucru care trebuie spus înainte de a numi asta „primul verdict formal": dintre cei patru piloți, CAND-0003 e ARHIVAT-NEGATIV pe criteriul meu (0/8 ani, 0/3 regimuri, E_R −0,615).** Verdictul lui e practic predeterminat, iar clearance-ul de la RV-L1 e condiționat exact pe asta. **Verdictul formal are conținut informativ real pentru CAND-0001, 0002 și 0007.**

**Și limita de scop, ca să nu fie citită greșit: măsurătorile de aici validează MAȘINĂRIA — calibrarea, blocul, corecția de multiplicitate. Ele nu spun nimic despre dacă vreun candidat are edge. Aceea e întrebarea pe care verdictul o va răspunde, iar eu nu o anticipez.**

---

## HANDOFF

**VE:** repară seed-ul pe cheie stabilă; recalculează matricea PRDS peste cei 15 TESTAȚI, nu peste 32; măsoară VIF pentru orice candidat care respinge, înainte de a raporta p.
**Red Team, ținte:** dacă fereastra Bartlett de 20 de zile e suficientă pentru CAND-0003, dat fiind că ρ e încă +0,125 la lag 5; și dacă argumentul de direcție („SE subestimat nu poate fabrica un fals pozitiv într-o ne-respingere") se ține și pentru testul incremental, nu doar pentru cel contra zero.
**CEO, patru lucruri:** **(1) RV-L2 e închisă, dar nu prin confirmarea partiției — prin faptul că toți cei patru candidați din perechile negative sunt ÎN AFARA familiei, deci obiectul partiției nu există; restrâns la cei 15 testați, ZERO perechi material-negative, deci BH e valid fără partiție. (2) Ipoteza „cel mai lung overlap" e infirmată: CAND-0016 are cel mai SCURT overlap și 22 din 56 de luni cu o singură tranzacție — artefactul e de SĂRĂCIE, nu de lungime. Suspiciunea Red Team era corectă, mecanismul nu. (3) RV-L1 se închide pentru trei piloți din patru; la CAND-0003 eroarea standard e subestimată de 2,18×, dar direcția e în favoarea verdictului, deci îl clearez CONDIȚIONAT — admisibil doar ca ne-respingere. (4) Eroarea de fond era că matricea s-a calculat peste 32 de candidați în loc de familie; regula e fixată acum, iar m=16 și mulțimea-PRDS=15 sunt două lucruri diferite care nu se amestecă.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.55 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
