# STATISTICIAN — DERIVAREA HTF LA MARGINEA LIVE. SPECIFICAȚIE + DECIZIA DE SEGMENTARE

**Document ID:** STAT-LIVE-HTF-DERIVATION-RULE-v1.0 · **Data:** 2026-08-11 · **Autor:** Statistician
**Verificare de sursă:** citit `context_derived_htf` integral din manifest (`mechanical_rule`, `m15_v2_discovery_blocks`, notele de graniță), plus `edge_research/_common.py`, `regime_classifier.py`, `bias_h1.py`.

**Diagnosticul Data Acquisition se confirmă. Nu e defect: e comportamentul corect al unei reguli corecte.**

---

# PARTEA 1 — DECIZIA 1: nu se poate extinde NIMIC. Și nu e nevoie.

## Ce am verificat, cu graniițele exacte

```
ultimul bloc discovery M15_v2      2022-12-16 10:45  →  2025-10-12 23:15
RESEARCH_HOLDOUT_CUTOFF_UTC                            2025-10-23 09:15
M15_v2 curent                                          2026-07-27
structura per segment, verbatim din manifest:  discovery_range → intra_segment_embargo → sealed_range
```

**Deci coada de 9 luni pe care ar trebui s-o acopere extinderea se împarte în exact două felii, și amândouă sunt indisponibile:**

```
2025-10-12 23:15 → 2025-10-23 09:15    BANDA DE EMBARGO intra-segment (~10,4 zile).
                                        Singurul ei rol e să împiedice scurgerea de dependență
                                        în zona sigilată. Consumarea ei o DESFIINȚEAZĂ.
2025-10-23 09:15 → 2026-07-27           SEALED_RANGE. Holdout-ul. Nediscutabil.
```

> **Răspunsul la „ce se poate extinde fără să rupi sigiliul" este: NIMIC. Nu există nicio felie liberă între 2025-10-12 și prezent. Prima e tamponul sigiliului, a doua e sigiliul.**

**Și argumentul de ce agregarea e un caz special de sever îl are manifestul deja, verbatim, scris de mine:**

> *„If even one constituent bar is sealed or in an embargo band, the aggregate's O/H/L/C/V values are mathematically a function of that sealed information — this is not a possible leak, it is a certain one (e.g. a D1 high is max() over its 96 M15 highs)."*

**O bară H4 construită peste graniță nu e „un pic contaminată". `max()` peste 16 componente din care una e sigilată ESTE o funcție de bara sigilată. Nu e un risc de scurgere; e o scurgere.**

## Dar întrebarea „trebuie extins?" are un răspuns mai bun decât „nu se poate"

**Fișierele H4/H1 offline există ca să servească DESCOPERIREA pe date istorice. Ele acoperă blocurile de descoperire complet. Că se opresc în 2025-10 nu e o lipsă — e exact ce cere regula.**

> **Cine are nevoie de H4/H1 până în 2026-07 e SHADOW LIVE. Iar Shadow nu citește fișierele offline. Are nevoie de agregatorul live — adică de Decizia 2. Extinderea offline ar rezolva o problemă pe care nimeni n-o are, cu prețul sigiliului.**

## Singura obiecție reală: warm-up-ul. Cuantificat, și rezolvat fără sigiliu.

**La pornirea Shadow, N1 și N2 au nevoie de istoric. Citit în cod:**

```
N1  regime_classifier.N_MIN_DEFAULT = 30 bare H4     →  30 × 4h  = 5 zile de tranzacționare
N2  bias_h1.N_MIN_BARS = WEEK_H1 = 115 bare H1        →  115 × 1h ≈ 4,8 zile de tranzacționare
```

> **Warm-up ≈ O SĂPTĂMÂNĂ de date ÎNAINTE. Nu e nevoie de nicio bară sigilată.**

**Iar în timpul warm-up-ului nu se construiește nimic nou: N1 și N2 emit `Unavailable`, regula mulțimii necesare face lanțul `NO_TRADE`, Shadow jurnalizează. Contractul AVAILABLE/UNAVAILABLE, deja specificat la v2.7.59, acoperă warm-up-ul integral. Tăcerea onorabilă a unei săptămâni e prețul, și e derizoriu.**

```
DECIZIA 1: NU se extinde niciun bloc discovery. Manifestul rămâne neschimbat.
           Motiv: nu există spațiu liber, iar nevoia reală e a lui Shadow, nu a offline-ului.
```

---

# PARTEA 2 — DECIZIA 2: regula live

## 2.1 Regula offline conține DOUĂ cerințe. Doar una supraviețuiește.

**Formularea Data Acq — „regula offline nu e regula live" — e corectă, dar motivul e mai precis decât „constrângerea n-are obiect". Regula offline împachetează două lucruri diferite într-o singură condiție:**

```
(a) COMPLETITUDINE   toate cele N componente M15 ale ferestrei EXISTĂ.
                     Întrebare despre BINE-DEFINIRE. Se aplică LIVE, NESCHIMBATĂ.
(b) PROVENIENȚĂ      toate N aparțin ACELUIAȘI bloc discovery.
                     Întrebare despre CONTAMINARE. La marginea live nu există partiție
                     sigilat/nesigilat, deci nu are obiect.
```

## 2.2 Ce cere live și offline nu cerea

```
(c) FINALITATE     offline, datele sunt definitive. Live, o bară M15 poate fi revizuită.
                   O bară M15 e FINALĂ când fereastra ei s-a închis ȘI feed-ul a avansat
                   dincolo de ea. Nicio bară HTF nu se construiește din componente ne-finale.
(d) IMUABILITATE   o bară HTF emisă NU se rescrie NICIODATĂ. O corecție târzie NU rescrie
                   o bară deja emisă — se jurnalizează ca discrepanță.
                   Motiv: o bară rescrisă ar schimba retroactiv un context pe baza căruia
                   N6 a decis deja. E aceeași clasă cu „N4 modifică decizia", deja interzisă.
```

## 2.3 Ce NU se schimbă, și e cel mai important lucru din document

**Tentația e să faci regula live „mai bună": să emiți o bară H4 parțială la închiderea de vineri, să tolerezi o componentă lipsă, să acoperi sărbătorile. REFUZ, și nu din conservatorism:**

> **Regula live NU are voie să emită bare pe care regula offline NU le-ar fi emis. Dacă emite, Shadow rulează pe o distribuție de context pe care NICIUN backtest n-a văzut-o — iar orice comparație între Shadow și istoric devine o comparație între două obiecte diferite. FIDELITATEA BATE ACOPERIREA.**

**Concret: N rămâne FIX (H4: N=16, H1: N=4, D1: N=96). O fereastră de weekend pur și simplu nu emite — exact ca offline, unde e absentă din fișier. Nicio noțiune nouă de „număr așteptat de componente din calendar". Ar fi o îmbunătățire, și tocmai de aceea e interzisă.**

## 2.4 REGULA LIVE, completă

```
La închiderea ferestrei calendaristice [w_start, w_end) a unui timeframe HTF cu N componente:

  EMITE  Ok(bar, as_of=w_end, valid_until=w_end + perioada, schema_hash)
         dacă și numai dacă:
           (a) toate cele N bare M15 cu timestamp în [w_start, w_end) EXISTĂ
           (c) toate N sunt FINALE (fereastra închisă și feed-ul a avansat dincolo)
           (b') toate N provin din ACEEAȘI PARTIȚIE ADMISIBILĂ (vezi Partea 3)

  ALTFEL Unavailable(reason, as_of=w_end)
         reason ∈ {incomplete_window, not_final, partition_violation}
         NICIODATĂ o bară parțială. NICIODATĂ null-fill. NICIODATĂ present-but-flagged.

  O bară emisă e IMUABILĂ (d).
```

---

# PARTEA 3 — POT COEXISTA? Da — fiindcă e O SINGURĂ regulă, cu un parametru.

**Întrebarea din mandat e „coexistă sau una o înlocuiește". Răspunsul e a treia variantă, și e cea care contează:**

```
REGULA, unică:
    emite bara HTF ⟺ toate cele N componente există, sunt finale,
                      și aparțin ACELEIAȘI CELULE dintr-o PARTIȚIE dată.

    OFFLINE   partiția = {bloc₁, bloc₂, bloc₃, bloc₄, embargo…, sealed}   ⇒ condiția MUȘCĂ
    LIVE      partiția = { fluxul live }  — o singură celulă             ⇒ condiția e VID ADEVĂRATĂ
```

> **Nu sunt două reguli. E aceeași regulă, instanțiată cu două partiții. Diferența dintre offline și live e un PARAMETRU, nu un algoritm.**

**De ce insist, și de ce e o cerință de implementare, nu o eleganță:**

```
Două implementări separate ar DIVERGE. Iar dacă diverg, contextul H4 pe care rulează Shadow
nu e contextul H4 pe care s-a făcut fiecare backtest. Ar fi A DOUA SURSĂ DE ADEVĂR —
exact defectul semnalat de trei ori (`status: str`, dicționarul de redundanță, harnessul meu
paralel de la v2.7.60, care m-a costat o cifră publicată greșit).
CERINȚĂ: UN SINGUR agregator, un singur test, partiția ca argument.
```

---

# PARTEA 4 — CELE PATRU CEASURI. Corectez încadrarea: nu e nealiniere.

**Mandatul spune: „N1 și N2 dau context înghețat, N3 și N4 coadă proaspătă. Decizii greșite TACIT."**

**Prima parte e adevărată și e CORECTĂ. A doua nu decurge din ea.**

> **Un regim H4 calculat la 12:00 și folosit la 15:55 NU e învechit — e cea mai recentă observație COMPLETĂ. Un sistem pe bare nu are altceva, iar alternativa (o bară H4 neînchisă) ar fi LOOKAHEAD. Am hotărât asta la v2.7.57 și rămâne.**

**Cele patru timeframe-uri NU POT avansa împreună — au perioade diferite. A cere asta ar cere bare neînchise. Pericolul real e altul, și e deja rezolvat:**

```
PERICOLUL              carry-forward NEMĂRGINIT — o valoare purtată dincolo de valabilitatea ei.
MECANISMUL, existent   fiecare nivel emite `as_of` și `valid_until`.
                       N6, la `decision_ts`:   as_of <= decision_ts < valid_until  ⇒ `Ok` se folosește
                                               altfel                              ⇒ `Unavailable("stale")`
DE CE NU E TACIT       sub contract, un context expirat NU e o valoare veche folosită în tăcere —
                       e `Unavailable`, deci mulțimea necesară taie lanțul, deci NO_TRADE jurnalizat.
                       Nu există cale silențioasă. Asta ERA problema; e închisă din v2.7.57.
```

> **Deci nu e nimic de construit pentru „alinierea ceasurilor". Singura cerință nouă e ca AGREGATORUL să emită corect `as_of` și `valid_until` — `as_of = w_end`, `valid_until = w_end + perioada`. Două câmpuri, nu o componentă.**

---

# PARTEA 5 — ÎMPĂRȚIREA MUNCII: confirm două din trei, corectez a treia

```
✅ eu specific regula live                    — acest document
✅ Data Acq construiește agregatorul          — cu cerința de la Partea 3: UN SINGUR agregator,
                                                partiția ca argument, care servește ȘI offline-ul
❌ „runtime-ul Shadow aliniază cele patru ceasuri"
```

**Corecția: nu există „aliniere de ceasuri" de construit, iar construirea ei ar fi activ dăunătoare.**

```
Ar fi machinery NOUĂ — interzisă de constrângerea de scop.
Și, mai rău, ar fi AL DOILEA LOC în care se decide ce e învechit. Regula de valabilitate
trăiește în N6, pe contract. Un al doilea arbitru în runtime ar putea contrazice primul.
CE FACE RUNTIME-UL, exact: transmite `decision_ts` și respectă `Ok` / `Unavailable`. Atât.
```

---

# PARTEA 6 — MINIMUL, ȘI CE RĂMÂNE DESCHIS

**Verificarea de scop, pe fiecare element: e necesar pentru milestone?**

```
regula live (a)(c)(b')     DA — fără ea Shadow n-are context H4/H1 deloc
imuabilitatea (d)          DA — altfel o corecție rescrie un context pe care s-a decis deja
as_of / valid_until        DA — două câmpuri; fără ele regula de vechime n-are intrări
un singur agregator        DA — a doua implementare rupe comparabilitatea cu backtest-urile
număr de componente        NU — N rămâne FIX. Interzis, ca să nu diveargă de offline.
   din calendar
aliniere de ceasuri        NU — nu există. Contractul o face deja.
extinderea blocurilor      NU — și e imposibilă. Vezi Partea 1.
```

```
BLOCKING      niciunul. Regula e specificabilă și implementabilă acum.
MATERIAL      finalitatea (c) depinde de semantica feed-ului brokerului. Definiția minimă —
              „fereastra închisă și feed-ul a avansat dincolo" — e suficientă pentru milestone,
              dar e o ASUMPȚIE despre feed. Se declară, ca la polaritatea lichidității.
MATERIAL      warm-up ~1 săptămână la pornirea Shadow, cu N1/N2 `Unavailable`. Pre-declarat,
              nu descoperit. Nu se scurtează cu bare sigilate.
LIMITATION    H4/H1/D1 offline rămân oprite în 2025-10. E CORECT, nu o lipsă. Orice raport
              care le citește trebuie să spună că acoperă descoperirea, nu prezentul.
LIMITATION    ferestrele HTF de weekend/sărbătoare nu emit niciodată, live ca și offline.
              Identic cu backtest-urile — deliberat.
NON-MATERIAL  discrepanțele de revizuire se jurnalizează; nicio acțiune automată.
```

**Nu cere: gate nou, framework nou, primitivă nouă, nivel nou, componentă de runtime nouă. Regula live e regula existentă cu partiția schimbată, plus două câmpuri și o interdicție de rescriere.**

---

**Manifest:** `config/split_manifest.json` v2.7.63, secțiunea `live_htf_derivation_rule_v2_7_63`.
