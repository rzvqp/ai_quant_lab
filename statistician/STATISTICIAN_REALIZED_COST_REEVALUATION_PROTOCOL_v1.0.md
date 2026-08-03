# STATISTICIAN — COSTUL REALIZAT: CE AR FI NEVOIE CA SĂ REDESCHID VERDICTELE

**Document ID:** STAT-REALIZED-COST-REEVALUATION-PROTOCOL-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**NU redeschid nimic aici.** O observație nu stabilește nimic — de acord, integral. Specific ce ar fi nevoie.

**Verificare de sursă, la provenieța constantei:** citit direct manifestul — `cost_round_trip=0,20` NU e o măsurătoare. E o construcție: `2×(spread_ticks + slip_ticks)×TICK = 2×(5+5)×0,01`, unde `spread_ticks=5` vine din „mijlocul intervalului de 5-15 ticks declarat de CEO", iar `slip_ticks=5` din **convenția CEO „slip = spread"** — nu dintr-o observație. **Asta schimbă complet forma întrebării.**

---

# PARTEA 0 — Cei 4× NU sunt o eroare. Sunt DOUĂ erori cu statut probatoriu diferit.

```
componentă        MODELAT              OBSERVAT (1 tranzacție)     statut probatoriu
spread            0,10  (2×5×0,01)     0,05                        măsurabil pasiv, direct
slippage          0,10  (2×5×0,01)     0,00                        NEmăsurabil pasiv
                  ─────                ─────
total             0,20                 0,05
```

**Consecința centrală, și e cea care decide Partea 4:** jumătatea de *spread* a modelului e supraestimată cu ~2× și se poate corecta prin observare pasivă. **Jumătatea de *slippage* nu are NICIO bază empirică** (e o convenție declarată), **și nu poate fi măsurată prin observarea spread-ului — deloc.** Slippage-ul apare la volum, pe bare volatile și pe goluri — exact condițiile în care declanșează aceste strategii. Un singur fill, la dimensiune minimă, într-un moment calm, cu slippage 0, **nu spune aproape nimic** despre slippage-ul acestor strategii.

**Observație de consistență, în favoarea prudenței:** spread-ul observat (0,05 = 5 ticks) se află la **limita de JOS a intervalului de 5-15 ticks pe care CEO însuși l-a declarat inițial**, nu la mijloc. Exact ce ai aștepta de la un eșantion prins într-un moment calm. Asta nu infirmă măsurătoarea — o *încadrează*: e o observație validă a capătului liniștit al distribuției.

**Verificare obligatorie înainte de orice altceva:** un spread de 0,05 pe XAUUSD indică un cont **raw/ECN**, care de regulă taxează **comision separat**. Dacă e cazul, costul round-trip real e `0,05 + comision`, iar cifra citată nu e costul complet. **De verificat la sursă (specificația contului), nu de presupus** — aceeași disciplină ca la verificarea TICK-ului la Mandatul 3.22.

---

# PARTEA 1 — Câte observații, și cum se eșantionează

## Estimandul: NU media spread-ului. Media costului CONDIȚIONAT de declanșare.

Costul intră liniar în expectanță (`E[net] = E[gross] − E[cost]`), deci estimandul e **media**, nu mediana — derivat, nu ales. Dar media *peste ce populație*?

**Tranzacțiile nu apar la momente aleatorii.** Apar când strategia declanșează — pe bare de expansiune, atingeri de nivel, goluri. **Spread-ul se lărgește exact atunci.** Deci:

```
E[cost | declanșare]  >  E[cost | moment calendaristic aleatoriu]
```

**Eșantionarea la intervale fixe de 30 de secunde produce o estimare SISTEMATIC PREA MICĂ** a costului pe care aceste strategii îl plătesc efectiv. Răspunsul la „aleatoriu sau stratificat" e deci: **niciunul singur** — colectare continuă (ieftină), dar **estimare REPONDERATĂ către distribuția de declanșare**, nu cea calendaristică. Reponderarea e posibilă doar dacă se înregistrează etichetele de stratificare (Partea 4).

## Celulele de stratificare — deja existente ca primitive ratificate, nu inventate

```
4 sesiuni (asia/london/ny/late — market_state.session_of, ratificat)
      ×
3 stări de volatilitate (comprimat / normal / expansiune — market_state.compression+expansion,
      ratificate; exact partiția în 3 stări pe care am specificat-o deja la v2.7.30)
= 12 celule
```

## n-ul care contează: ZILE, nu tick-uri

**Punctul tehnic decisiv.** Observațiile la 30 de secunde sunt masiv autocorelate — două observații la 30s distanță sunt cvasi-identice. **2880 de observații pe zi NU sunt 2880 de observații independente.** A raporta un interval de încredere pe n=tick-uri ar produce un CI absurd de îngust și o falsă certitudine.

```
Unitatea de eșantionare = (zi × sesiune), nu tick-ul.
Estimarea mediei + CI se face prin bootstrap pe BLOCURI/clustere de zile —
   reutilizând mecanica block_bootstrap deja ratificată în acest laborator
   (aceeași distincție iid-vs-bloc pe care am aplicat-o la testul pereche OBDZ).
Prag: n >= 25 ZILE DISTINCTE per celulă (convenția N_MIN=25, aplicată la unitatea corectă).
```

**Consecință practică onestă:** 12 celule × 25 de zile distincte înseamnă **săptămâni-luni de colectare**, nu ore — și celulele rare (ex. expansiune în sesiunea asia) vor fi ultimele care se umplu. **Asta e costul real al unui răspuns solid**, și e mai bine spus acum decât descoperit după.

## Regula de oprire — un criteriu decidabil, nu un prag inventat

**Nu inventez o țintă de precizie.** Criteriul: **întregul CI 95% (bootstrap pe clustere, reponderat la declanșare) trebuie să se afle SUB 0,20** pentru ca modelul să fie demonstrat greșit. Dacă CI-ul încalecă 0,20, colectarea continuă. E un criteriu natural, derivat din întrebarea însăși, nu o cifră aleasă.

---

# PARTEA 2 — Ce se redeschide, ce nu

## Mai întâi: o corecție la motivul pe care l-ai dat pentru non-recalculare

**Ai spus: „edge_brut a fost derivat scăzând costul din expectancy, deci poartă eroarea în el." Verificat direct — nu e așa, și motivul real e mai important.**

La Mandatul 3.38 am verificat eu însumi: `edge_brut_dollars − expectancy_dollars = exact 0,20` în toate cele trei regimuri. Deci `edge_brut = expectancy + cost_presupus`, iar `expectancy = brut_simulat − cost_presupus`. **Cele două se anulează: `edge_brut = brut_simulat`, care e independent de valoarea costului.** Aditiv, edge_brut e curat.

**Motivul REAL pentru care nu se poate recalcula e altul, și e mai serios — costul nu intră doar aditiv:**

```
cost → podeaua de eligibilitate ATR (derivată ca 3×cost/SL_mult; 0,60 la cost 0,20)
cost → min_executable_risk (k_spread × effective_spread = 2 × spread)
```

**Ambele determină CARE tranzacții intră în eșantion.** Un cost mai mic ⇒ podea mai mică ⇒ **o populație DIFERITĂ de tranzacții** ⇒ un `edge_brut` diferit, pe alt set de evenimente. **Canalul e populațional, nu aritmetic** — de aceea recalcularea pe hârtie e imposibilă și e nevoie de o re-rulare completă. Concluzia ta („nu recalcula") e corectă; motivul e altul, și contează pentru că arată că nici măcar `edge_brut` nu e reutilizabil ca atare.

## CONSTRÂNGEREA DECISIVĂ: măsurătoarea e din PREZENT, verdictele sunt pe 2011-2022

**Aceasta e obiecția care guvernează tot restul, și mi-o aplic mie însumi înainte de a o aplica ție.**

La Mandatul 3.39 am respins argumentul de reescalare la ATR-ul actual, pe trei motive, dintre care al treilea a fost: **extrapolare în afara domeniului măsurat — o cifră din piața de azi proiectată pe date istorice cu structură diferită.** Costul măsurat azi, pe FusionMarkets, la aur ~4050$, **e exact aceeași categorie de inferență**, doar în direcție favorabilă.

**Nu pot respinge o extrapolare când e nefavorabilă și s-o accept când e favorabilă.** Deci:

> **O măsurătoare de cost din prezent stabilește costul PREZENT. Nu stabilește costul din 2011-2022, și deci NU redeschide, prin ea însăși, niciun verdict pe backtest istoric.**

**Diferența reală, pe care o recunosc onest:** un cost e o constantă *mecanică*, direct verificabilă, spre deosebire de un edge, care e o proprietate *comportamentală*. Ca tip de dovadă, aceasta e **mai puternică** decât argumentul ATR. Dar puterea probatorie nu rezolvă problema temporală — o măsurătoare bună a lucrului greșit rămâne o măsurătoare a lucrului greșit.

## Taxonomia — după MOTIVUL DECISIV al fiecărui verdict

```
A. RESPINSE PENTRU CĂ COSTUL A DEPĂȘIT EDGE-UL BRUT  →  candidate la redeschidere
   OBDZ-002 REJECTED_AT_DECLARED_PARAMETRIZATION — DA, sensibil la cost.
     Motiv: brut era POZITIV peste tot (+0,166/+0,050/+0,471) și costul l-a mâncat în bear/bull.
     Un cost mai mic deplasează întreaga distribuție net_R în sus ⇒ p-urile se mișcă material.
     Eticheta pe care am ales-o („la parametrizarea DECLARATĂ") anticipa deja revizuibilitatea.
   S3/S2/S7/S13/S16/S17/S11 — aceeași categorie, prin construcție.

B. RESPINSE PE ALT MOTIV DECÂT COSTUL  →  NU se redeschid pe acest argument
   SMC_S1 STATISTICALLY REJECTED (Mandatul 3.23) — NU se redeschide.
     Motivul verdictului a fost că edge-ul BRUT era cvasi-zero și cu SEMN INCONSISTENT
     între regimuri. Un cost mai mic NU salvează un brut care nu e fiabil pozitiv —
     scade ce se scade, nu creează ce nu există.
     Rezervă onestă: canalul podea→populație (mai sus) înseamnă că populația ar fi fost
     alta, deci strict vorbind ar cere o re-rulare — dar aceea e un TEST NOU, care
     CONSUMĂ familie, nu o „redeschidere" gratuită.

C. VERDICTE FĂRĂ NICIO DEPENDENȚĂ DE COST  →  NEATINSE, în ambele sensuri
   Semnalul MFE zonă-vs-retragere (Mandatul 3.35, +0,232×ATR, n=654) — măsurat pe excursii
     de preț BRUTE, fără niciun cost. Rămâne exact cât de valid era. Nici nu se
     întărește, nici nu slăbește.
   Ratificările D1-D7, revizia de fidelitate MK-01/MK-02, calibrarea block_bootstrap,
     respingerea reescalării ATR — niciuna nu atinge costul.
```

**Observația care leagă totul:** singura constatare POZITIVĂ a acestei linii (semnalul MFE) n-a depins niciodată de cost. Toate eșecurile au fost în *conversia* lui în profit net-de-cost. **Dacă acel cost e într-adevăr de câteva ori mai mic, problema de conversie se micșorează — dar asta rămâne o ipoteză de testat, nu o concluzie**, și numai pentru perioada în care costul a fost efectiv măsurat.

## Cele TREI condiții cumulative pentru redeschidere

```
1. CI 95% (cluster-bootstrap, reponderat la declanșare) integral sub 0,20 — Partea 1.
2. Problema TEMPORALĂ adresată: fie date de spread din perioada 2011-2022, fie o
   re-încadrare explicită a verdictelor ca fiind despre PERFORMANȚA FORWARD (nu
   despre backtestul istoric) — o schimbare de obiect, declarată, nu tăcută.
3. Componenta de SLIPPAGE măsurată pe fill-uri REALE (Partea 0) — nu prin observare pasivă.
```

**Toate trei, nu prima singură.** Condiția 2 e cea care va fi cel mai greu de îndeplinit și cea mai ușor de sărit tăcut.

---

# PARTEA 3 — Constant sau variabil? Întrebare EMPIRICĂ, cu propriul meu rezultat pus în joc

**Nu decid a priori. Colectarea o decide** — și specific analiza discriminantă acum, înainte de date:

```
Se estimează elasticitatea spread-ului față de volatilitate: regresie/binning al spread-ului
observat pe ATR14 contemporan (și pe sesiune), raportând panta pe scară log-log.

elasticitate ≈ 0  →  costul E o constantă în dolari; se păstrează forma actuală, cu
                     valoarea corectată. Constatarea mea de la Mandatul 3.38 rămâne validă.
elasticitate ≈ 1  →  costul scalează cu ATR ⇒ cost/R e ~CONSTANT ⇒ avantajul regimurilor
                     de ATR mare DISPARE.
```

**Consecință pe care o declar explicit împotriva mea:** la Mandatul 3.38 am explicat eșecul OBDZ structural — *cost fix vs. edge scalat cu ATR*, motiv pentru care bull (cel mai mic ATR) nu putea niciodată acoperi costul. **Dacă elasticitatea iese ≈1, acea explicație a mea e greșită și trebuie revizuită** — iar respingerea reescalării ATR de la Mandatul 3.39 câștigă un al patrulea motiv (costul ar crește odată cu ATR-ul, anulând câștigul presupus).

**Îmi pun propria concluzie în joc, cu criteriul scris înainte de a vedea datele.** Asta e singura formă onestă de a pune întrebarea.

---

# PARTEA 4 — Ce se colectează

## Observare pasivă (AI Trader, cadența de 30s existentă) — corectează DOAR jumătatea de spread

```
per observație:  timestamp UTC · bid · ask · spread=(ask−bid) · mid
etichete OBLIGATORII (fără ele reponderarea din Partea 1 e imposibilă):
    sesiune (market_state.session_of — ratificat)
    stare de volatilitate (compression/expansion — ratificate)
    ATR14 M15 contemporan  ← indispensabil pentru Partea 3
    zi (pentru clusterizarea din Partea 1)
```

Fără ordine, fără cost — corect, e pură observare.

## Ce observarea pasivă NU poate da — și de ce e jumătatea mai importantă

**Slippage-ul și comisionul nu se văd în bid/ask.** Se văd doar în fill-uri reale. Deci, separat și obligatoriu:

```
per ORDIN REAL pe DEMO (oricând apare unul):
    preț cerut vs. preț umplut, pe AMBELE picioare · slippage realizat per picior
    comision perceput (dacă există) · dimensiunea ordinului
    aceleași etichete (sesiune, stare de volatilitate, ATR) ca mai sus
```

**Și, explicit:** slippage-ul observat în condiții calme și la dimensiune minimă **nu se extrapolează** la condițiile de declanșare ale acestor strategii. Fill-urile care contează sunt cele pe bare de expansiune și pe goluri. **Până când există fill-uri reale ÎN acele condiții, jumătatea de slippage a modelului rămâne neverificată — și e jumătatea fără nicio bază empirică.**

## Legătura directă cu gardurile DEMO deja fixate

`min_executable_risk` folosește `k_spread × effective_spread`. Am impus deja (v2.7.34/v2.7.36) ca `effective_spread` să fie cel **REALIZAT**, nu presupus. **Această colectare e exact ce alimentează acel câmp** — deci nu e o măsurătoare paralelă, ci sursa unei valori pe care am cerut-o deja. Un spread real de 0,05 în loc de 0,40 presupus **schimbă podeaua**, deci schimbă câte tranzacții sunt podite la CAND-0003 — legat direct de consecința pe care am derivat-o la Mandatul 3.49.

---

## Ce NU se schimbă, indiferent de rezultat

Holdout-ul rămâne sigilat. Familia rămâne 7. Nicio re-rulare nu e „gratuită": o re-rulare sub un cost corectat e un **TEST NOU pe aceleași date**, deci consumă familie — nu o redeschidere fără preț. **Asta trebuie spus acum**, altfel un cost corectat devine o poartă de re-testare nelimitată a tot ce a eșuat.

## HANDOFF

**AI Trader** — colectarea pasivă (câmpurile de mai sus, cu etichete). **Validation Engine** — captura fill-urilor reale + verificarea comisionului la sursa contului. **Statistician** — reia când n≥25 zile distincte/celulă e atins, sau mai devreme dacă verificarea comisionului schimbă cifra de bază.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.37 (commit `cd169ab`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
