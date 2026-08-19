# STATISTICIAN — PROTOCOL PREÎNREGISTRAT: LOT BLIND INDEPENDENT `BLIND-001 … BLIND-048`

**Document ID:** STAT-RANGE-V3-BLIND-BATCH-02-PROTOCOL-v1.0 · **Data:** 2026-08-19 · **Autor:** Statistician
**Autorizat de:** Red Team `RT-RANGE-0005` @`10c2d46` — `RANGE_V3_PERFORMANCE_DELTA_PASS`, care autorizează **exclusiv** `NEW_INDEPENDENT_BLIND_LABEL_BATCH`.

> **★ SE COMITE ȘI SE ÎMPINGE ÎNAINTE DE A CITI ORICE BARĂ. Commit-ul lui e dovada de precedență. După acest commit, regula de selecție NU se modifică pe baza aspectului graficelor. Dacă apare un defect procedural: OPRIRE, publicarea defectului, cerere de decizie — niciodată corecție tăcută după ce am văzut OHLC.**

---

# 0 — VERIFICARE GIT ȘI O CONTRADICȚIE GĂSITĂ

```
STATISTICIAN V3   bf9f780   2026-08-18 23:43:07 +0300                                   ✔
MANIFEST v2.7.84  db098ed   2026-08-18 23:46:51 +0300                                   ✔
   fingerprint    cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233      ✔ recalculat
VE 0.4.1          f9af357 build · 7dc2ff9 delivery   2026-08-19 12:49                    ✔
   wheel SHA-256  39673910666e13708b1d4cb7266d1730bb1c9ceea4e0b021a1bf3cfa1f8281f4      ✔ extras si re-hash
                  (mandatul cita 39673910…81f4 — se potriveste exact)
RED TEAM          10c2d46   RT-RANGE-0005 (E80)      2026-08-19 13:11:47 +0300           ✔
lot anterior      RANGE_HUMAN_LABEL_BATCH_01 @2673227 + rezultate CEO_ASSISTED @bf9f780  ✔
```

## Contradicția, raportată înainte de orice selecție

> **`ve_n1_replay 0.3.1` și `ve_brain` rămăseseră INSTALATE în mediul de execuție din mandatul precedent, unde rularea detectorului era cerută pentru diagnostic. Acest mandat interzice rularea. Le-am DEZINSTALAT înainte de a scrie protocolul și am verificat: `find_spec` returnează `None` pentru ambele. `DETECTOR_NOT_RUN` nu e o declarație, ci o stare a mediului — și trebuie să fie adevărată prin construcție, nu prin bunăvoință.**

Testele VE 0.4.1 nu încarcă corpusul canonic; folosesc fixture-uri sintetice, între care `_hbl20_bars`, derivat din HBL-20. **Acoperit integral de excluderea întregului Batch 01.**

---

# 1 — POPULAȚIA ELIGIBILĂ ȘI EXCLUDERILE

```
simbol / TF   OANDA:XAUUSD / M15, bare CANONICE, loaderul pre-holdout (197.094 bare)
blocuri       cele PATRU oficiale:
                B1 2011-07-26 16:30 → 2013-09-27   B2 2016-01-11 09:00 → 2018-04-06
                B3 2020-08-11 06:45 → 2021-09-05   B4 2022-12-16 10:45 → 2025-10-12
exclus        tot ce e în afara celor patru blocuri; embargo; SEALED; OOS. FĂRĂ EXCEPȚIE.
```

## 1.1 Excluderi de independență, cu **marjă de 480 bare** de fiecare parte

```
E1  întinderile RANDATE ale tuturor celor 24 de ferestre HBL-01…HBL-24 din Batch 01
E2  intervalele canonice RC-01 … RC-08 (cele care au bare canonice: RC-03, RC-04, RC-05, RC-06)
E3  RC-CONSTRUCTION-CHANNEL-NEW-01, index canonic [192, 288)
E4  HBL-20 și fixture-ul sintetic derivat din el — acoperit de E1
E5  ferestrele folosite de VE în teste — verificat: NICIUNA, testele sunt sintetice
```

> **Marja e 480 de bare, adică o fereastră întreagă de lungime maximă, nu 96 ca la Batch 01. Motivul: independența cerută aici e mai tare decât non-suprapunerea. O fereastră nouă nu doar că nu împarte nicio bară cu materialul de construcție — e separată de el prin cel puțin o fereastră completă.**

## 1.2 Reguli tehnice (identice cu cele deja validate la Batch 01, v1.1)

```
R1  întinderea RANDATĂ [s−C, s+L+C) stă INTEGRAL într-un singur bloc canonic, C = 24
R2  la cel puțin 96 de bare de ambele capete ale blocului
R3  nicio pauză internă peste 60h. Pragul stă în banda GOALĂ măsurată (53,25h — 73,00h):
    orice valoare din bandă dă aceeași mulțime eligibilă, deci nu am nicio libertate de reglaj.
    Weekendul normal (modal 49,25h) e ADMIS; sărbătorile și golurile de livrare NU.
R4  întinderea randată nu atinge nimic din §1.1, nici marja de 480 de bare
R5  întinderile randate ale ferestrelor selectate sunt disjuncte ȘI separate prin >= 96 bare
```

**Dacă populația nu mai permite lotul:** `RANGE_V3_BLIND_BATCH_BLOCKED_NO_INDEPENDENT_POPULATION`. **Nu se substituie SEALED/OOS. Nu se relaxează nicio regulă.**

---

# 2 — DIMENSIUNEA LOTULUI, DERIVATĂ ÎNAINTE DE SELECȚIE

**Nu aleg 24 fiindcă lotul anterior a avut 24.**

## 2.1 Ce se va estima ulterior

```
ESTIMAND   p = proporția segmentelor RANGE etichetate de om pe care detectorul le RECUNOAȘTE
           (recall pe segmente RANGE). Unitatea statistică e SEGMENTUL, nu fereastra.
```

Aleg recall-ul pe segmente fiindcă defectul dominant măsurat la v2.7.84 a fost **omisiunea** (37 din 66 de segmente), nu clasificarea greșită. Se estimează ce a eșuat.

## 2.2 Calculul, cu ipotezele declarate

```
IPOTEZA 1  interval Wald/Wilson la 95%, semilățime w:  n = z² p(1−p) / w²,  z = 1,96
IPOTEZA 2  p necunoscut ⇒ cazul cel mai defavorabil p = 0,5 (varianță maximă)
IPOTEZA 3  semilățime țintă w = 0,15
           Justificare: e o poartă semantică de PRIMĂ trecere, nu o estimare finală. O țintă mai
           fină ar cere o sarcină umană care riscă OBOSEALA DE ETICHETARE — ea însăși o sursă de
           bias, și una pe care nu o pot corecta ulterior.
IPOTEZA 4  rata de segmente RANGE pe fereastră, PRIOR SLAB din Batch 01 (CEO_ASSISTED):
              L = 96 → 0,875     L = 288 → 1,125     L = 480 → 1,375     (7 / 9 / 11 din 8+8+8)
           ★ Prior din etichete ASISTATE. Poate fi optimist. Sensibilitatea e declarată la §2.4.
IPOTEZA 5  segmentele sunt tratate ca observații independente pentru interval. Segmentele din
           ACEEAȘI fereastră nu sunt strict independente; consecința e un interval puțin
           prea îngust, declarat aici, nu descoperit ulterior.

REZULTAT   n_segmente = 1,96² × 0,25 / 0,15² = 42,7  →  43 segmente RANGE necesare
```

## 2.3 Din segmente în ferestre

```
STRATIFICARE   4 blocuri × 3 lungimi = 12 celule, k ferestre pe celulă
segmente RANGE așteptate = 4k × (0,875 + 1,125 + 1,375) = 13,5 k
   k = 3  →  36 ferestre  →  40,5 segmente   SUB pragul de 43   ✗
   k = 4  →  48 ferestre  →  54,0 segmente   PESTE prag         ✓

FIXAT ÎNAINTE DE EXTRAGERE:  N = 48 ferestre · 16 pe fiecare clasă de lungime · 12 pe bloc
```

## 2.4 Batch-uri secvențiale, toate fixate acum

```
4 batch-uri × 12 ferestre = 48.   Fiecare batch conține EXACT o fereastră din fiecare celulă
(4 blocuri × 3 lungimi), deci FIECARE BATCH E ECHILIBRAT DE UNUL SINGUR.
```

> **Proprietatea care contează: dacă CEO se oprește după batch-ul 2, datele parțiale rămân echilibrate pe blocuri și lungimi — doar intervalul e mai larg. Nu există o ordine în care oprirea să producă un eșantion strâmb.**

```
SENSIBILITATE, declarată: dacă rata reală de segmente e cu 25% sub priorul asistat (2,53 în loc
   de 3,375 pe triplet), cele 48 de ferestre dau 40,5 segmente ⇒ semilățime 0,155 în loc de 0,150.
   Consecință MINORĂ. Nu se compensează prin ferestre suplimentare.

CRITERII DE OPRIRE, fixate acum:
   Se oprește la 48. NU se continuă fiindcă „nu au ieșit destule RANGE-uri".
   NU se oprește mai devreme fiindcă „distribuția arată bine".
   Frecvența naturală observată SE ACCEPTĂ AȘA CUM E. Ea e o măsurătoare, nu un obstacol.
```

---

# 3 — STRATIFICARE: NUMAI CE E INDEPENDENT DE PREȚ

```
PERMIS      bloc canonic · lungimea ferestrei (96 / 288 / 480) · poziția în indexul eligibil ·
            regulile calendaristice preînregistrate
INTERZIS    trend · range · volatilitate · ATR · pantă · swings · breakout · detector · PnL ·
            orice etichetă istorică
```

---

# 4 — SEED ȘI ALGORITM

```
SEED = SHA256( "RANGE_V3_BLIND_LABEL_BATCH_02|10c2d46|f9af357|N48" )      șir ASCII EXACT
flux  bloc_k = SHA256( SEED ‖ uint64_be(k) ), citit în felii de 8 octeți, u_j = uint64_be(felia j)
candidat  s = ELIGIBLE[ u_j mod len(ELIGIBLE) ],  ELIGIBLE = lista SORTATĂ CRESCĂTOR
```

## Ordinea de extragere — singura sursă a numerotării interne

```
pentru batch in (1, 2, 3, 4):
    pentru bloc in (B1, B2, B3, B4):
        pentru L in (96, 288, 480):
            extrage un candidat; dacă încalcă R1-R5 → REFUZĂ, consemnează motivul,
               consumă URMĂTOAREA valoare din flux, repetă
            altfel → ACCEPTĂ

plafon de siguranță: 20.000 de extrageri ⇒ RANGE_V3_BLIND_BATCH_BLOCKED_DRAW_CEILING
   Nu se relaxează nicio regulă. Nu se schimbă seed-ul. NICIODATĂ după vizualizare.
```

```
zero redraw pentru aspectul prețului · zero intervenție manuală · zero detector ·
zero acces la rezultate viitoare · refuzurile procedurale se consemnează integral
```

> **Scriptul de selecție citește EXCLUSIV coloana `time`. `open/high/low/close` nu sunt atinse până când lista completă a celor 48 de ferestre e fixată ȘI hash-uită. Dovada: hash-ul listei se calculează înainte de orice citire OHLC și se publică.**

---

# 5 — ID-URI OPACE ȘI AMESTECARE DETERMINISTĂ

```
ID afișat    BLIND-001 … BLIND-048.  NU conțin blocul, perioada, lungimea sau ordinea extragerii.
AMESTECARE   permutare Fisher-Yates deterministă, condusă de ACELAȘI flux, continuat după
             ultima extragere de selecție. Ordinea de prezentare NU e ordinea extragerii.
MAPARE       ID → (bloc, lungime, index, timestamp) stă EXCLUSIV în escrow, niciodată în PDF.
```

---

# 6 — RANDAREA

```
o pagină per fereastră · fundal negru · bullish turcoaz · bearish alb · același raport de aspect
fereastra centrală clar delimitată prin linii verticale · context 24+24 ESTOMPAT și etichetat CONTEXT
numărul de bare centrale afișat · lumânări lizibile

★ AXA TIMPULUI = INDEX DE BARĂ RELATIV (0 … N), FĂRĂ NICIO DATĂ CALENDARISTICĂ.
  Formularul cere granițele de segment ca `start_bar_approx` / `end_bar_approx`, deci indexul e
  exact unitatea în care CEO va răspunde. Data nu e necesară pentru sarcină, deci nu se afișează.

ZERO output de detector · ZERO etichete RANGE/TREND/CHANNEL · ZERO reason codes · ZERO PnL ·
ZERO swings marcați · ZERO ATR · ZERO limite automate · ZERO evenimente · ZERO sugestii
```

> **Scurgere reziduală, declarată acum și nu descoperită ulterior: axa PREȚULUI rămâne reală, fiindcă formularul cere limitele aproximative ale range-ului. Nivelul absolut al aurului trădează aproximativ epoca. Nu îl ascund, fiindcă un preț normalizat ar face răspunsurile CEO greu de dat și greu de recuperat. Epoca nu spune însă nimic despre etichetă, iar blindul care contează aici e față de DETECTOR.**

---

# 7 — FORMULARUL: ETICHETARE PE SEGMENTE

CEO **nu** e obligat să aleagă o singură clasă pentru o fereastră. Pentru fiecare fereastră, oricâte segmente ordonate.

```
per SEGMENT   start_bar_approx · end_bar_approx
              clasa ∈ {RANGE · CHANNEL_UP · CHANNEL_DOWN · TREND_UP · TREND_DOWN ·
                       TRANSITION · AMBIGUOUS · UNAVAILABLE}
              confidence ∈ {HIGH · MEDIUM · LOW}
per EVENIMENT SWEEP_UP · SWEEP_DOWN · BREAKOUT_UP · BREAKOUT_DOWN ·
              FAILED_BREAKOUT_UP · FAILED_BREAKOUT_DOWN · NONE · AMBIGUOUS
dacă RANGE    lower aprox · upper aprox · mid opțional · acumulare/distribuție dacă se observă ·
              episodul CONTINUĂ sau S-A TERMINAT
```

**Secvențe de tipul `RANGE → SWEEP_DOWN → MARKUP_UP → RANGE` sunt explicit permise. Etichetele CEO NU se convertesc automat în taxonomia detectorului** — conversia, dacă va fi vreodată necesară, e un pas separat, versionat și vizibil.

---

# 8 — REGULA DE INTERACȚIUNE, TIPĂRITĂ ÎN INSTRUCȚIUNI

```
1  CEO spune PRIMUL ce vede.
2  Asistentul NU oferă clasificare, sugestie sau corecție înainte de răspuns.
3  Asistentul poate cere DOAR clarificări neutre („la ce bară se termină?"), niciodată sugestive.
4  După confirmare, eticheta se BLOCHEAZĂ.
5  NU se revine la o fereastră după vizualizarea vreunui output de detector.
6  AMBIGUOUS e legitim. Incertitudinea NU se forțează.
7  Asistentul doar TRANSCRIE verdictul CEO.
```

```
proveniența în fișierul final:  CEO_INDEPENDENT_BLIND_LABEL      — niciodată CEO_ASSISTED
```

---

# 9 — BLOCAREA ETICHETELOR ȘI ESCROW

```
la final   fișier CSV machine-readable cu răspunsurile EXACTE · SHA-256 · timestamp ·
           publicare doar a ce e permis · sigilarea mapării ID→timestamp ·
           confirmarea că detectorul NU a fost încă rulat · etichetele NU se mai modifică
corecții   orice corecție de transcriere ulterioară e VERSIONATĂ, explicată, și făcută
           FĂRĂ acces la outputul detectorului
escrow     mapping ID→(bloc, lungime, index, timestamp) + lista ferestrelor, content-addressed
           și cifrat, ÎN AFARA checkout-urilor Git, ca la RT-BLIND-ESCROW-RANGE-V2-001
```

---

# 10 — CE NU FACE ACEST MANDAT

```
NU se instalează și NU se rulează 0.4.1 (sau orice versiune) pe aceste ferestre
NU se compară etichetele cu detectorul · NU se calculează accuracy/recall · NU se aleg parametri
NU se modifică SPEC V3 · NU Strategy Catalog · NU Alpha · NU AI Trader · NU LIVE_SHADOW · NU broker
```

**Mandatul se încheie imediat după livrarea PDF-ului și a formularului către CEO.** Comparația cu detectorul e un mandat Red Team SEPARAT, după blocarea etichetelor.

**Verdicte permise:** `RANGE_V3_BLIND_LABEL_BATCH_READY_FOR_CEO` sau `RANGE_V3_BLIND_BATCH_BLOCKED_<motiv>`.
**Interzise:** `RANGE_V3_BLIND_PASS` · `RANGE_V3_SEMANTIC_PASS` · `STRATEGY_CATALOG_READY` · `ALPHA_AUTHORIZED`.

---

# 11 — INVARIANTE

```
n_generated_total = 363 · m_inference = 26 · tombstones · registrul Alpha · verdictele existente
F1-F6 BLOCKED_PENDING_RANGE_SEMANTIC_FIX · F7 SAFETY_GUARD
BLIND_OUTPUT_NOT_ACCESSED · DETECTOR_NOT_RUN · SEALED/OOS_ACCESS = 0
zero PnL · zero strategie · zero broker · zero LIVE_SHADOW · zero Alpha run
```

---

# 12 — ORDINEA DE EXECUȚIE

```
1. ACEST document se comite și se împinge; hash local = remote se verifică.   ← precedență
2. Abia apoi se citesc timestamp-urile și se execută selecția (§1-§4).
3. Lista celor 48 de ferestre se HASH-UIEȘTE și se publică ÎNAINTE de orice citire OHLC.
4. Abia apoi se citesc OHLC-urile și se randează (§6).
5. Rezultatul într-un commit SEPARAT, care îl citează pe acesta.
```

**Următorul proprietar după READY: CEO, pentru etichetare independentă.**
