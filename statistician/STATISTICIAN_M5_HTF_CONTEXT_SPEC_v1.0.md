# STATISTICIAN — CONTEXT HTF DERIVAT DIN M5, CE SE PIERDE, ȘI ÎNTREBAREA DE COST

**Document ID:** STAT-M5-HTF-CONTEXT-SPEC-v1.0
**Data:** 2026-08-04 · **Autor:** Statistician

**Verificare de sursă:** citit direct `config/split_manifest.json` (intrarea M5, `context_derived_htf`) și `acquisition_staging/generate_htf_context.py`. **O măsurătoare nouă, proprie, P&L-oarbă** pe M5 (354.656 bare) și M15 (două ferestre). **Măsurătoarea de cost răspunde altfel decât sugerează întrebarea, și corectează o afirmație din codul de screening.**

---

# PARTEA 1 — DERIVAREA H1 ȘI H4 DIN M5

**Se oglindește `generate_htf_context.py` verbatim. Nu inventez nicio convenție; enumăr ce se transferă și ce se schimbă.**

## Regula, identică

```
ANCORARE      H1 = floor pe ora UTC.
              H4 = ancora 17:00 America/New_York (DST-aware), floor 4h, apoi +17h, retur UTC.
              Identic cu code/resample_ny.py. Zero convenție paralelă.

EXISTENȚĂ     o bară HTF există DOAR DACĂ fereastra ei calendaristică FIXĂ cade integral
              într-un SINGUR bloc de descoperire M5:
                 s <= w_start   ȘI   w_end <= e   ȘI   max_comp < e
              Fără straddling, fără trunchiere, fără bare parțiale sau marcate.

GRANIȚE       semi-deschise: fereastra e [w_start, w_start + bar_seconds).
              H1 bar_seconds = 3600 ; H4 = 14400.

IEȘIRE        formatul nativ cu 7 coloane: time,open,high,low,close,volume,sub
              open=first, high=max, low=min, close=last, volume=sum, sub=COUNT componente.
```

## Invariantul de contabilitate — cu cifrele de așteptat pe M5

```
n_fără_filtru − n_cu_filtru  =  straddle + outside,   defalcat pe fiecare graniță de bloc.
sub AȘTEPTAT:   H1 = 12 bare M5   (pe M15_v2 era 4)
                H4 = 48 bare M5   (pe M15_v2 era 16)
⇒ orice bară cu `sub` diferit de valoarea nominală semnalează un gol de piață, nu un defect
  al derivării — se raportează, nu se completează.
```

**Verificarea hash-ului sursă rămâne prima instrucțiune, ca în script:** `sha256(OANDA_XAUUSD_M5.csv)` trebuie să dea `cbb6eebe…3814` (statusul e deja `CONFIRMED_BY_STATISTICIAN`) înainte ca orice să fie generat.

## Două diferențe reale față de M15_v2, care nu se pot copia

```
1. BLOCURILE SUNT ALTELE. M5 are trei segmente proprii (Partea 2), nu cele patru ale lui M15_v2.
   ⇒ `m5_discovery_blocks` trebuie ADĂUGAT în manifest ca secțiune proprie, NU refolosit
     din `m15_v2_discovery_blocks`. Reutilizarea ar produce bare tăcut greșite.

2. COADA post-hartă e `TOO_SHORT_FULLY_SEALED` (2026-06-30 → 2026-07-27, 16,34 zile).
   ⇒ se EXCLUDE explicit; nu e bloc de descoperire și nu produce bare HTF.
   Segmentul trei fiind scurt (~4 luni), rata de eliminare H4 la marginile lui va fi
   proporțional mai mare decât pe M15_v2. Se raportează, nu se corectează.
```

---

# PARTEA 2 — CE SE PIERDE. Nu e „trei regimuri devin două".

**Segmentele M5, citite din manifest:**

```
1. 2021-07 → 2022-10   correction   ← „M5 catches only the TAIL" (eticheta din manifest)
2. 2022-10 → 2026-02   bull         ← integral
3. 2026-02 → 2026-06   correction   ← integral, dar SCURT (~4 luni)
BEAR: ABSENT integral. Bear-ul laboratorului e 2011-2015, cu ~6 ani înainte ca M5 să existe.
```

> **Deci nu sunt „două regimuri" — e UN bull complet, o corecție scurtă și o coadă de corecție.** Iar cele trei sunt faze ale UNEI SINGURE epoci de piață (2021-2026), nu trei epoci independente. **Axa de regim și axa de epocă se suprapun.**

## Consecința care contează cel mai mult, și nu e pierderea bear-ului

**Fereastra M5 (2021-07 → 2026-07) se suprapune peste segmentele TÂRZII ale lui M15_v2 — aceeași perioadă de piață, la rezoluție mai fină.**

> **M5 nu e informație NOUĂ despre piață. E rezoluție mai mare pe o traiectorie de preț deja folosită parțial.** O „confirmare pe M5" a unui tipar descoperit pe M15 în același interval calendaristic **nu e o confirmare independentă — e aceeași traiectorie reeșantionată.**

**Consecință de guvernanță, pe care o fixez acum ca să nu fie citită greșit mai târziu:**

```
O variantă M5 a unui candidat existent NU e o ipoteză nouă independentă.
E ACELAȘI candidat la rezoluție mai fină ⇒ dacă e testat formal, CONSUMĂ UN SLOT DE FAMILIE,
și NU poate fi raportat ca a doua confirmare a celui pe M15.
```

## Ce etichetă de scop poartă un verdict pe M5 — și de ce ASTA e un caveat legitim

**Un verdict pe M5 nu poate revendica persistență de regim în sensul definit de laborator.** Poate revendica **consistență între faze, în interiorul unei singure epoci (2021-2026)**.

**Și e important că acest caveat E disponibil, spre deosebire de cel refuzat acum o oră la nepotrivirea de domeniu: acolo limitarea era pe RATA DE EROARE, aici e pe DOMENIU.** Cititorul știe exact ce a cumpărat: un rezultat valid pe o epocă, netestat pe bear. **Caveat-ele mărginesc scopul; nu mărginesc miscalibrarea.** Aceeași regulă, aplicată de data asta în favoarea propunerii.

**Utilizarea legitimă a lui M5 e deci cea pe care o cere CEO — mecanica de INTRARE și CONFIRMARE, nu validare independentă.** Zone pe M15/H1, declanșare pe M5: M5 aduce rezoluție de execuție, nu grade de libertate statistice.

---

# PARTEA 3 — COSTUL. Măsurat, și răspunsul nu e cel sugerat de întrebare.

**Premisa din mandat — „pe M5 mișcările sunt mai mici decât pe M15, deci cost/R crește" — e corectă ca mecanică și incompletă ca aritmetică, pentru că aurul s-a triplat între epoca de descoperire și fereastra M5.**

```
                                              ATR14 median   cost/R la R = 1×ATR
M5    2021-07 → 2026-07 (toată fereastra)         1,471           13,60%
M15   ACEEAȘI fereastră 2021-07 → 2026-07         2,681            7,46%
M15   epoca de DESCOPERIRE (până în 2020-07)      1,382           14,47%   ← toți candidații actuali
```

## Două afirmații adevărate simultan, și amândouă trebuie spuse

```
1. M5 NU e o capcană NOUĂ. La 13,60%, e MAI IEFTIN decât regimul în care au fost produse
   TOATE rezultatele curente (14,47%). Fiecare arhivare, fiecare candidat marginal din
   coadă vine dintr-un cost/R mai PROST decât cel pe care l-ar avea M5 azi.

2. DAR alternativa reală nu e M15-de-atunci, e M15-de-acum. Față de ea, M5 costă 1,82× mai mult
   pe R (13,60% vs 7,46%). Ăsta e prețul deciziei, și e real.
```

**Deci: „aceeași capcană?" — DA, exact aceeași, la aceeași magnitudine cu cea în care lucrăm deja. Nu e un risc nou; e riscul cunoscut, plătit încă o dată, când există o alternativă la jumătate de preț.**

## Constatarea mai gravă, găsită căutând altceva: PODEAUA

**`phase1_screening.py` afirmă în comentariu: „Termenul 0,10×ATR domină podeaua pt. XAUUSD." Măsurat, e fals la median:**

```
fracția barelor unde 0,10×ATR e SUB podeaua absolută (2×spread = 0,20):
   M5, fereastra proprie        64,1%
   M15, epoca de descoperire    73,1%
   M15, fereastra M5            33,6%
```

**Pe majoritatea barelor, termenul care mușcă e cel ABSOLUT, nu cel scalat cu ATR.** Codul calculează corect `max(...)`; comentariul descrie greșit care termen câștigă. **Nu se schimbă niciun rezultat — se schimbă interpretarea: podeaua NU e adaptativă la volatilitate în practică, e o podea FIXĂ de 0,20 pe două treimi din bare.**

### Și de aici iese consecința care contează operațional

```
podea = max(2 × effective_spread, ...)   ȘI   cost_round_trip = 2 × effective_spread
⇒ când podeaua mușcă prin termenul absolut,  cost/R = 0,20 / 0,20 = 100%  PRIN CONSTRUCȚIE.
```

> **O tranzacție a cărei distanță de risc e podită plătește un R întreg în cost. Nu are edge redus — are, la o țintă de 1R, imposibilitate structurală de break-even.** Podeaua garantează executabilitatea exact la pragul unde profitabilitatea dispare.

**Asta întărește ce am cerut la criteriile DEMO (v2.7.34/36): fracția podită nu e un diagnostic, e o populație care nu poate fi profitabilă la 1R.** Nu proiectez politica — e a lui Alpha — dar consemnez faptul statistic și îl rutez.

## Verdictul pe „merită?", cu poarta fixată înainte

**Pericolul lui M5 nu e cost/R median. E că stopurile STRUCTURALE pe M5 sunt mai mici în valoare absolută, deci o fracție mai MARE dintre ele va atinge podeaua — unde cost/R e 100%.**

```
POARTA, pre-declarată, măsurabilă ÎNAINTE de a construi orice candidat M5:
  se aplică regula de stop a candidatului pe barele M5 și se raportează
  FRACȚIA PODITĂ, per regim, ÎNAINTE de orice cifră de performanță.

  fracția podită <= 10%   ⇒ M5 e admisibil pentru acel candidat
  10% – 25%               ⇒ admisibil DOAR cu fracția raportată lângă fiecare rezultat
  > 25%                   ⇒ candidatul nu se construiește pe M5; stopul lui e sub rezoluția
                            economică a timeframe-ului
```

**Aceeași disciplină ca „numărul de declanșări înainte de performanță" de la primitiva B: cantitatea care poate invalida rezultatul se raportează înaintea rezultatului.**

**Recomandarea mea, delimitată:** **DA pentru rolul cerut** — zone pe M15/H1, confirmare și intrare pe M5 — pentru că acolo M5 aduce rezoluție de execuție, iar costul lui e cel cu care laboratorul lucrează deja. **NU ca substitut de validare** și **NU fără poarta de fracție podită**, pentru că acolo M5 plătește dublu față de alternativa vie fără a aduce date independente.

---

## HANDOFF

**Data Acquisition / VE:** generează H1 și H4 din M5 pe regula din Partea 1; **adaugă `m5_discovery_blocks` ca secțiune proprie de manifest — NU reutiliza blocurile M15_v2**; exclude explicit coada `TOO_SHORT_FULLY_SEALED`; raportează invariantul (`n_fără − n_cu = straddle + outside`, per graniță) și distribuția lui `sub` față de nominalul 12/48.
**Alpha:** poate construi variantele cu confirmare pe M5 DUPĂ ce poarta de fracție podită trece; fiecare variantă M5 a unui candidat existent consumă un slot de familie și nu se raportează ca a doua confirmare.
**Red Team:** ținte explicite — dacă suprapunerea calendaristică M5/M15 face o „confirmare pe M5" circulară, și dacă poarta de 10%/25% e derivată sau aleasă.
**CEO:** trei cifre — **M5 costă 13,60% din R, mai puțin decât cei 14,47% în care au fost produse toate rezultatele actuale, dar 1,82× mai mult decât M15 azi (7,46%). Bear-ul lipsește integral, și cele trei segmente sunt faze ale unei singure epoci, nu trei epoci.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.46 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
