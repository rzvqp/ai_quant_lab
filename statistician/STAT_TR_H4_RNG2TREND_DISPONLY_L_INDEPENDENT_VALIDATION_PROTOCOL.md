# TR-H4-rng2trend_disponly-L — PREGĂTIREA VALIDĂRII INDEPENDENTE

**Divizia Statistician · `STAT-TR-H4-RNG2TREND-DISPONLY-L-INDEPENDENT-VALIDATION-PREP-001` · 2026-08-21**

```
TR_H4_RNG2TREND_DISPONLY_L_FRESH_VALIDATION_EVIDENCE_REQUIRED
TR_H4_RNG2TREND_DISPONLY_L_TRANSITION_SEMANTICS_NOT_SUPPORTED
```

**Protocolul NU e înghețat. Nicio validare executată.**

Cifrele se reproduc exact. Implementarea, cauzalitatea, cozile și testul de traiectorie **trec toate**.
Ce **nu** se susține este **numele**: obiectul nu e un mecanism `RANGE → TREND`, ci un
**breakout H4 filtrat prin displacement**. Iar afirmația de la §8 — displacement bate acceptance —
**se confirmă** pe o populație comună, ceea ce nu se întâmplase la `IR-DIR-L-mid`.

Nu emit `RESEARCH_AUDIT_FAIL` global: ar condamna un obiect care funcționează. Numesc exact ce cade.

---

## 1 — §2 IDENTITATEA, RECUPERATĂ MECANIC

**Candidatul e o RAMURĂ DE HARNESS**, ca și `MT-H4-efficiency-L`: instanțierea
`transition_campaign.evalc(tf="H4", mech="rng2trend_disponly", long=True, rr=1.5)`. Nu există obiect
izolat de strategie. ID-ul **există** în registru (`f"TR-{tf}-{m}-{'L'|'S'}"`).

| element | valoare din cod |
|---|---|
| amprente | `transition_campaign.py` blob `f0657ca73c06` @ `fd80040` · `m5_data.py` `1339e74a5e05` · motor `wp5b/code/mstrat.py` |
| TF primar / direcție | **H4** (agregat cauzal din M5 gated, `nsub ≥ 24` din 48) · **LONG** |
| **„RANGE" anterior** | **`abs(effic[i−2]) < 0.40`** — o singură valoare, decalată cu 2 bare |
| **„frontieră de range"** | `hi[i] = rolling(12).max().shift(1)` = **maximul ultimelor 12 bare H4 (2 zile), excluzând bara `i`** |
| **„tranziție"** | `close[i] > hi[i]` |
| **displacement** | **`close[i] − open[i] > 1.2 × ATR14_H4[i]`** |
| praguri | `0.40` (range) · `12` (frontieră) · `1.2` (displacement) · `20` (lookback eficiență) · `RR = 1.5` |
| timing semnal / intrare | închiderea barei `i` → intrare la **`open[i+1]`** |
| **SL** | `min(low[i−3 … i]) − 0.15 × ATR14_H4[i]` — swing de 4 bare pe TF-ul de edge |
| **TP** | `entry + 1.5 × risk` |
| hold maxim | **48 bare H4 = 8 zile**, apoi ieșire la închidere |
| podea de stop | `max(5·tick, 0.10·ATR_H4)` — **măsurat: se activează în 0,0%** |
| cost | `tick 0,01` · STRESS round-trip **0,24** |
| **serializare** | `mstrat.simulate`: `last = xi` (index de **ieșire**), `if ei <= last: continue` |
| dependențe de context | **niciuna** — fără regim, fără sesiune, fără TF superior |

---

## 2 — §5 REPRODUCEREA: **EXACTĂ**

| | Alpha | reprodus | |
|---|---|---|---|
| DEV `N` | 33 | **33** | ✓ |
| DEV `WR` | 45,5% | **0,455** | ✓ |
| DEV `avgR` | +0,443 | **+0,4431** | ✓ |
| DEV `PF` | 2,50 | **2,503** | ✓ |
| DEV `best-10%-rem` | +0,328 | **+0,3284** | ✓ |
| TP median | ~397 p | **396,6 p** | ✓ |
| CALIB `N` | 9 | **9** | ✓ |
| CALIB `WR` | 66,7% | **0,667** | ✓ |
| CALIB `avgR` | +0,658 | **+0,6583** | ✓ |

Cifrele complete cerute la §5:

```
DEV   n=33  GROSS +0.4488  BASE +0.4504  STRESS +0.4431   PF 2.503  maxDD 2.95 R
      med_R +0.328 · P25/P50/P75 = -1.006 / +0.328 / +1.490
      avg winner +1.107 (n=22) · avg loser -0.884 (n=11) · worst -1.016 · best +1.786
      mix iesiri: 14 tinta / 9 stop / 10 TIMP (30,3%)   hold median 30 bare H4 (5 zile), max 49
      medSL 264,4 p ($26,44) · medTP 396,6 p · medMAE 149,0 p · medMFE 351,2 p
      RR nominal = RR efectiv = 1,500 EXACT ; podea activata 0,0%
CALIB n= 9  GROSS +0.6667  BASE +0.6649  STRESS +0.6583   PF 2.955  maxDD 1.01 R
      med_R +1.491 · avg winner +1.492 (n=6) · avg loser -1.010 (n=3)
      mix iesiri: 6 tinta / 3 stop / 0 timp   medSL 275,6 p · medTP 413,4 p
```

**★ O singură discrepanță semantică, minoră:** `WR` din harness e proxy-ul `R ≥ rr − 0,05`, nu rata de
atingere a țintei. Pe DEV dau **0,455 (15/33)** vs **atingeri reale de țintă 14/33 = 0,424** — o ieșire
pe timp a depășit pragul. Diferența e mică, dar raportarea trebuie să spună „țintă / stop / timp",
mai ales fiindcă **30,3% din tranzacții ies pe timp**.

---

## 3 — ★★ §3 SEMANTICA DE TRANZIȚIE: **NU SE SUSȚINE**

Ai cerut să verific dacă e o tranziție reală sau un breakout generic deghizat. Am descompus mecanismul
în componentele lui și am măsurat contribuția fiecăreia.

### 3.1 Descompunerea

```
                                                SERIALIZAT (asa cum se tranzactioneaza)
                                                  n    WR      avgR     b10rem
(1) doar breakout        c>hi                     66  0.439   +0.2814   +0.1553
(2) breakout + DISPLACEMENT   (FARA poarta range) 40  0.450   +0.4199   +0.2923
(3) breakout + poarta RANGE   (FARA displacement) 57  0.474   +0.3169   +0.1981
(4) CANDIDATUL = brk + rng + disp                 33  0.455   +0.4431   +0.3284

                                                NESERIALIZAT (fiecare semnal eligibil)
(1) doar breakout                                203  0.330   +0.0147   -0.1486
(2) breakout + DISPLACEMENT                       69  0.391   +0.2600   +0.1378
(3) breakout + poarta RANGE                      151  0.338   +0.0167   -0.1482
(4) CANDIDATUL                                    50  0.400   +0.2690   +0.1265
```

**Displacement-ul face tot.** Neserializat: `+0,0147 → +0,2600`. **Poarta de „range" nu face aproape
nimic:** adăugată peste displacement, mută media cu **+0,009** (`+0,2600 → +0,2690`) eliminând 19
semnale; adăugată peste breakout singur, mută media cu **+0,002** (`+0,0147 → +0,0167`).

### 3.2 „Range"-ul anterior nu e un range

```
poarta |eff[i-2]| < 0.40 trece 2.029 / 2.592 = 78,3% din TOATE barele H4 din DEV
eff[i-2] pe cele 50 de semnale: min -0.345 · P25 -0.088 · mediana +0.078 · P75 +0.205 · max +0.392

  |eff[i-2]| < 0.20  (eticheta RANGE a proiectului) :  30/50 = 60,0%
  eff[i-2] > 0.20    (deja in urcare)               :  15/50 = 30,0%
  eff[i-2] in [0.30, 0.40)  (eticheta TREND_UP!)    :   9/50 = 18,0%
```

Proiectul definește `RANGE` ca `|effic| < 0.20` și `TREND_UP` ca `effic > 0.30`. Poarta candidatului,
`< 0.40`, **admite explicit stări pe care propriul proiect le numește TREND_UP** — 18% din semnale.
Nu există lățime minimă, nu există număr de atingeri, nu există structură de frontieră. E un singur
număr, permisiv.

### 3.3 „Inițiere de trend" — aceasta **se susține**

```
semnale la care bara i-1 inchisese DEJA peste propriul maxim anterior:  4/50 = 8,0%
```

Deși mecanismul **nu cere** ca bara precedentă să fie înăuntru (spre deosebire de `breakout_immediate`,
care cere `c[i−1] ≤ hi[i−1]`), în practică 92% din semnale sunt prima rupere. Punctul acesta e corect.

### 3.4 Verdictul semantic

```
Jaccard(candidat, breakout_immediate) = 0,311   dar   46 / 50 = 92% din semnalele candidatului
                                                       SUNT semnale breakout_immediate
Jaccard(candidat, breakout_retest)    = 0,249   si   50 / 50 = 100% sunt semnale breakout_retest
```

**Candidatul este o submulțime de 92-100% a familiei generice de breakout H4, selectată prin filtrul de
displacement.** Componenta „RANGE" e inertă. Deci:

```
TR_H4_RNG2TREND_DISPONLY_L_TRANSITION_SEMANTICS_NOT_SUPPORTED
mecanismul real = H4 BREAKOUT + DISPLACEMENT >= 1.2 ATR
```

Nu spun că obiectul e lipsit de valoare — spune-i pe nume și rămâne un lucru real (§4, §5). Spun că
**numele nu descrie ce face**, iar toată argumentația de „specialist de tranziție, complementar" se
sprijină pe acel nume.

---

## 4 — §6 AUDITUL DE COADĂ: **`BROAD_BASED_TRANSITION_ALPHA` justificat pe axa cozii**

```
top 1 (3,0% din n)  1,79 R = 12,2% din profit
top 2 (6,1%)        3,28 R = 22,4%
top 3 (9,1%)        4,77 R = 32,6%
top 4 (12,1%)       6,26 R = 42,8%
best1%rem +0.4012 · best2%rem +0.4012 · best5%rem +0.4012 · best10%rem +0.3284
P25 -1,006 · MEDIANA +0,328 · P75 +1,490
```

**Mediana tranzacției e pozitivă** și decăderea `best-k-removed` e lină. Același motiv structural ca la
`MT-H4-efficiency-L`: `rr` fix la 1,5 **plafonează R-ul per tranzacție** (max observat +1,786), deci
structura de loterie e imposibilă prin construcție. **Nu emit `TAIL_CONCENTRATION_DISQUALIFYING`.**

*(Pe CALIB coada e concentrată — top 2 din 9 = 50,5% — dar la n=9 statisticile de coadă nu au conținut.)*

## 5 — §7 SERIALIZARE ȘI SENSIBILITATE LA TRAIECTORIE: **PASS**

```
setup-uri brute 50  ->  33 luate (66,0%)     [la MT-H4-efficiency-L: 13,6%]
BLOCAT   n=33  avgR +0.4431  b10rem +0.3284
NEBLOCAT n=50  avgR +0.2690  b10rem +0.1265   <- ambele POZITIVE, spre deosebire de MT-H4
```

Testul decisiv, 36 de traiectorii alternative (aruncând primele `k` semnale):

```
avgR: min +0.4320 · P10 +0.4651 · MEDIANA +0.7206 · max +1.1201
traiectorii cu avgR <= 0 : 0,0%
traiectoria publicata (k=0) = +0.4431, la PERCENTILA 8,3  --  aproape de MINIMUL distributiei
```

**Publicată e printre cele mai slabe traiectorii posibile.** Nu e artefact de traiectorie; dacă ceva,
cifra raportată e conservatoare. Defectul `IR-DIR-L-mid` **nu se repetă**.

## 6 — ★ §8 DISPLACEMENT vs ACCEPTANCE: **concluzia lui Alpha SE CONFIRMĂ**

Aceasta era suspiciunea principală: două backtest-uri separate, fiecare cu propria populație endogenă.
Le-am rulat pe **populația-părinte comună** (`range gate ȘI breakout`), **neserializat**:

```
parinte (rng & breakout)          n=151  WR 0.338  avgR +0.0167  b10rem -0.1482
  subset DISPLACEMENT             n= 50  WR 0.400  avgR +0.2690  b10rem +0.1265
  subset ACCEPTANCE               n= 40  WR 0.225  avgR -0.0757  b10rem -0.2499
  complement NON-displacement     n=101  WR 0.307  avgR -0.1081  b10rem -0.2841
  complement NON-acceptance       n=111  WR 0.378  avgR +0.0501  b10rem -0.1116
suprapunerea celor doua subseturi: 4 bare, Jaccard 0,047 -> chiar sunt subseturi disjuncte ale aceluiasi parinte
```

Displacement-ul separă net: `+0,269` față de complementul lui `−0,108`. Acceptance-ul e mai prost decât
părintele. **Concluzia se menține pe o populație comună, nu doar pe două backtest-uri separate.**

```
DISPLACEMENT_VS_ACCEPTANCE_CAUSAL_CLAIM = CONFIRMED_ON_COMMON_POPULATION
```

## 7 — §10 VALOAREA M5: `M5_REQUIRED = FALSE`, și testul lui Alpha era **deja corect**

Suspectam că brațul M5 e un subset al celui coarse (cum era la `HR-TU-pb-L`). **Nu este:**

```
semnale unde M5 nu a gasit declansator: 0 / 50
ALPHA (asa cum a rulat)  : A n=50 +0.2599 | B n=50 +0.2409 | dAvgR -0.0190
MATCHED (aceleasi semnale): n=50  A +0.2599 | B +0.2409 | dAvgR -0.0190   IDENTIC
```

Același SL H4, același TP H4, doar timing-ul diferă. **`M5_REQUIRED = FALSE` se îngheață.** Nu introduc
M5 în identitatea de validare.

*(Notă tehnică: aici `A` e +0,2599, față de +0,2690 în §3 — diferența vine din faptul că acest test
parcurge barele M5, iar §3 barele H4. Ambele sunt valide; rezoluția M5 e cea mai fină.)*

## 8 — §9 IMMEDIATE vs RETEST: **cifra lui Alpha e o CONȚINERE, nu un Jaccard**

```
immediate = 144 bare · retest = 201 bare · |cap| = 142
Jaccard REAL = 0,700          142/144 = 98,6% din immediate sunt si retest   <- de aici vine "0,978"
economie: immediate n=62 +0.2831 | retest n=65 +0.3012
```

Economic sunt ~echivalente, cum spune Alpha. Dar **nu sunt „aceleași tranzacții"**: `retest` are **57 de
semnale în plus** (40% mai multe). Iar condiția de retest, `low[i] ≤ hi[i]×1.001`, tolerează **0,1% din
preț ≈ 20 de pips** — adică nu cere un retest propriu-zis, doar ca minimul barei de rupere să fi rămas
aproape de nivel. Secundar per §21; nu consumă evidență.

## 9 — §11 GEOMETRIA ECONOMICĂ

```
RR nominal 1,5 = RR efectiv 1,500 EXACT (tinta derivata din ACELASI entry si ACELASI risc)
DEV : SL median 264,4 p ($26,44) · TP median 396,6 p ($39,66) · P25/P50/P75 TP = 324 / 397 / 520
      %TP >=80 = 100 · >=100 = 100 · >=150 = 100 · >=200 = 100 · >=300 = 84,8 · >=400 = 45,5
CALIB: SL 275,6 p · TP 413,4 p · >=300 = 100 · >=400 = 55,6
```

**Cele ~397 de pips se verifică (396,6).** E cel mai mare obiectiv economic din program. Procentele
**nu sunt tautologice** — nu există filtru de spațiu minim; ținta rezultă din stopul structural H4.

**Observație de dimensionare, nu defect:** un stop median de **$26,44** înseamnă 264 de pips de proiect
risc per tranzacție. E o strategie de swing pe 5 zile mediană (max 8).

## 10 — §12 ROBUSTEȚE TEMPORALĂ: **problema centrală**

```
2021: n= 9  avgR -0,143   2022: n= 6  avgR +0,291   2023: n=18  avgR +0,787
total R = 14,62 ; contributia lui 2023 = 18 x 0,787 = 14,17  ->  96,9% DIN PROFIT
```

**2021 e negativ**, 2022 se sprijină pe 6 tranzacții, iar **aproape tot profitul vine dintr-un singur
an**. E o concentrare temporală mai severă decât la `MT-H4-efficiency-L` (92,4%). Perioada slabă nu e
eliminată. Răspunsul la întrebarea ta: **candidatul depinde primar de mediul bullish târziu**, nu e un
mecanism general de tranziție.

## 11 — §13 ADECVAREA CALIBRĂRII

```
CALIB N = 9  (toate in 2024)
media +0,6583 · sd 1,251 · se 0,417 · t = 1,58 · IC 95% = [-0,159 ; +1,476]
```

**Intervalul include zero.**

```
CALIB_ADEQUACY = INSUFFICIENT
```

Cuantificarea cerută: cu `n = 9`, eroarea standard e **0,417 R** — mai mare decât jumătate din media
estimată. Un singur rezultat basculat mută media cu ~0,28 R. `WR = 66,7%` înseamnă **6 din 9**; cu
un singur câștig în minus ar fi 55,6%, cu unul în plus 77,8%. **Nu interpretez `CALIB_PASS` drept
validare independentă**, iar la acest `n` nici măcar ca sprijin.

**Și DEV e la limită:** `n=33 · sd 1,088 · se 0,189 · t = 2,34 · IC [+0,072 ; +0,814]`. Limita de jos e
`+0,072`. Candidatul e **cel mai bun din 28 de ID-uri** testate pe același DEV; sub o corecție
elementară de multiplicitate (Bonferroni 28 ⇒ `t ≈ 3,0`), `t = 2,34` nu supraviețuiește.

## 12 — §4 CAUZALITATE: **PASS**

```
poarta de range foloseste eff[i-2]        -> strict bare <= i-2       (decalaj DELIBERAT si corect)
hi[i] = max(high[i-12 .. i-1])            -> EXCLUDE bara i           verificat programatic: True
displacement pe c[i]-o[i], ATR[i]         -> bara i inchisa la decizie
stop pe min(low[i-3..i])                  -> bare inchise
intrare la open[i+1]                      -> cauzal
semnale in cele 20 de bare de dupa golul de discovery de 258,6 zile:  0 / 50
bare H4 partiale (nsub<48): 17,0% global, dar doar 4,0% printre barele de semnal
```

Nicio scurgere. Decalajul `eff[i−2]` e o alegere de proiectare **corectă**: împiedică bara de
displacement să contamineze testul „a fost range". O consemnez ca punct pozitiv.

## 13 — §14/§15 REDUNDANȚĂ ȘI COMPLEMENTARITATE

```
la nivel de BARA-SEMNAL (DEV):
  vs MT-H4-efficiency-L   n=339  |cap|=20  acopera 40,0% din candidat  Jaccard 0,054
  vs MT-H4-dispaccept-L   n= 76  |cap|= 7  acopera 14,0%               Jaccard 0,059
  vs breakout_immediate   n=144  |cap|=46  acopera 92,0%               Jaccard 0,311
  vs breakout_retest      n=201  |cap|=50  acopera 100,0%              Jaccard 0,249

la nivel de TRANZACTIE (serializat) si de ZI:
  vs MT-H4-efficiency-L : trade Jaccard 0,174 · same-day Jaccard 0,230
  vs MT-H4-dispaccept-L : trade Jaccard 0,028 · same-day Jaccard 0,327
  semnal-ZI vs efficiency = 0,154   <- reproduce EXACT cifra lui Alpha
```

```
TR_H4_RNG2TREND_DISPONLY_L_MECHANISM_CLASS:
   fata de MT-H4-efficiency-L / MT-H4-dispaccept-L / H4-bo-raw-S  ->  RELATED_BUT_DISTINCT
   fata de familia de BREAKOUT H4 din propria campanie            ->  PARAMETRIC_VARIANT
                                                                      (breakout filtrat prin displacement)
```

**§15 — complementaritatea e reală, dar Alpha a citat cifra cea mai favorabilă.** `0,154` e Jaccard
**la nivel de zi-semnal**. La nivel de tranzacție e `0,174`, iar pe zile de tranzacție `0,230`. Toate
sunt mici; niciuna nu e greșită. Le raportez pe toate trei și păstrez eticheta cerută:

```
RESEARCH_LEVEL_COMPLEMENTARITY   (vs MT-H4-efficiency-L)
```

Nu o numesc validare independentă. Și semnalez că **față de `MT-H4-dispaccept-L` suprapunerea pe zile e
0,327** — semnificativ mai mare decât la nivel de tranzacție, deci expunerea zilnică e corelată.

## 14 — §16 AUDITUL DE NOUTATE

**`MECHANICAL_DATA_CONSUMPTION` — ABSENT**, verificat: poarta gated se oprește fizic la
`2024-06-20 00:40Z`; `N4 = 0`, `read_csv pe data/market = 0`, `2025+ = 0`, `shadow_driver = 0`.
Pragurile `0.40 / 12 / 1.2 / 20 / RR 1.5` sunt constante declarate în cod, fără grid, fără ajustare.

**`ANALYST_KNOWLEDGE_CONSUMPTION` — PREZENT**, și pentru **exact** familiile pe care le-ai enumerat:
`≥17` studii de edge Flow A committed au `date_range 2022-12-16 → 2025-10-23`, iar cinci merg la
`2026-07-13`. Flow A **este** Alpha Discovery Laboratory. Relevante direct aici: **`E014` inside-bar
false breakout**, **`E006` Asia range expansion failure**, **`E017` equal highs/lows**, `E011` failed
3-drive, `E026` ADR exhaustion — adică **breakout de range, expansiune de volatilitate și eșec de
rupere**, exact familia acestui candidat. `2025-10-23 → 2026-07-13` rămâne **CONSUMAT** prin breach-ul
holdout-ului terminal (`PROJECT_STATE_v2 §8.23`).

## 15 — ★ §17 EXPUNEREA LA ETICHETAREA DE RANGE: prezentă, dar **relevanță ATENUATĂ**

Ai cerut explicit să nu clasific automat asta drept contaminare, ci să determin relevanța reală.

**Faptul:** 11 din cele 124 de ferestre blind de etichetare RANGE cad integral în calendarul `V1`
(`BLIND-001/032/033/047`, `MB3-011/035/047`, `FB14-012/013/014`, `F441-014`), dintre care **9 randate
și etichetate semantic de CEO**, iar `FB14`/`F441` sunt chiar validările blind ale V4.4/V4.4.1.

**Relevanța reală, măsurată:**

| canal | verdict |
|---|---|
| import / dependență de cod de la V4.4 | **ZERO** |
| praguri partajate cu configul V4.4 (`d_macro 29`, `n_touch 2`, `tol_cluster 1,60`, `w_atr 0,80`) | **NICIUNUL** — candidatul folosește `\|eff[i−2]\|<0.40` și `rolling(12)` |
| ponderea componentei „range" în edge | **~0** — contribuie `+0,009` din `+0,269` (§3.1) |

**Concluzie:** expunerea la etichetarea RANGE există, dar e **mai puțin relevantă pentru acest candidat
decât pentru `IR-DIR-L-mid`** — tocmai fiindcă partea de „range" e inertă. Paradoxal, ceea ce salvează
candidatul de contaminarea RANGE e chiar ce îi invalidează numele (§3).

**Ceea ce contează în schimb** e §14: familia `breakout / expansiune de volatilitate / eșec de rupere`
a fost studiată de aceeași divizie pe exact calendarul `V1`. **Aceea e expunerea materială.**

## 16 — §18 INVENTARUL EVIDENȚEI ȘI §19 SUFICIENȚA

Frecvență măsurată, fără a inspecta niciun rezultat protejat: **33 tranzacții / 2.652 bare H4 DEV =
1 la 80,4** (CALIB: 9/725 = 1 la 80,6 — coerență excelentă). Numărătoarea barelor e făcută **exclusiv
pe coloana `time`**.

| regiune | interval | bare M5 | bare H4 | **N așteptat** | status |
|---|---|---|---|---|---|
| **V1** | `2024-07-10 → 2025-10-23` | 91.445 | 1.988 | **~25** | `PARTIALLY_CONSUMED` |
| **V2** | `2025-10-23 → 2026-02-17` | 22.229 | 482 | ~6 | `CONSUMED` |
| **V3** | `2026-03-10 → 2026-06-20` | 19.950 | 434 | ~5 | `CONSUMED` |
| **V4** | `2026-07-13 → 2026-07-27` | 2.904 | 64 | **~1** | `CLEAN` |

*(Amprentele `ohlc_sha256` ale celor patru regiuni sunt înghețate la `6d4430a` §6.)*

```
N >= 30  : NU se atinge NICAIERI, nici macar in V1 (~25)     necesar ~2.411 bare H4 = ~1,1 ani de M5 nou
N >= 50  : necesar ~4.018 bare H4 = ~1,8 ani
N >= 100 : necesar ~8.036 bare H4 = ~3,7 ani
```

**★ Acesta e primul candidat la care `V1` nu atinge nici măcar pragul minim de 30.** Prin urmare:

```
CLEAN si SUFFICIENT NU COEXISTA -- si, in plus, SUFFICIENT nu e atins NICI in regiunea contaminata.
```

Asta simplifică decizia: nu există niciun argument pentru a cheltui `V1` pe acest candidat, fiindcă
nici măcar cheltuindu-l nu se obține un test interpretabil.

## 17 — §20 PORȚI PRE-ÎNREGISTRATE (contingent, NU protocol înghețat)

Fixate acum, fără să fi văzut niciun rezultat în `V1–V4`.

```
TR_H4_RNG2TREND_DISPONLY_L_GATES_PREREGISTERED_CONTINGENT
```

| # | poartă | prag |
|---|---|---|
| A | fidelitate de specificație | `\|eff[i−2]\|<0.40` · `c[i]>max(high[i−12..i−1])` · `c[i]−o[i]>1.2·ATR` · SL swing 4 bare `−0.15·ATR` · TP `entry+1.5·risk` · hold 48 · `nsub≥24` · blocaj o-poziție-o-dată. Orice abatere ⇒ **STOP** |
| B | N minim | `n ≥ 30` → altfel `INCONCLUSIVE`. `n < 100` ⇒ etichetă permanentă `LOW_POWER` |
| C | BASE | `> 0` la round-trip `0,05` |
| D | STRESS | `> 0` la round-trip **`0,24`** |
| E | robustețe cronologică | treimi fixate pe **bare H4**: ≥2/3 pozitive, niciuna sub `−0,10` |
| F | `best-1%-removed` | `> 0` (valid la `n ≥ 100`; sub, se raportează fără verdict) |
| G | `best-5%-removed` | `> 0` |
| H | `best-10%-removed` | `> 0` |
| I | concentrarea profitului | **top 10% din tranzacții ≤ 60% din profitul total** (DEV: ~36%) |
| J | maxDD | `≤ 9 R` (DEV 2,95 R) |
| K | pierdere individuală maximă | `≤ 1,5 R` (DEV −1,016 R) |
| L | fidelitate RR efectiv | `1,500 ± 0,01` pe **fiecare** tranzacție |
| M | geometrie economică TP | `%TP ≥ 300` să rămână `≥ 60%` (DEV 84,8%) |
| **N** | **★ fidelitate semantică de tranziție** | **`avgR(candidat) > avgR(breakout+displacement FĂRĂ poarta de range)`, pe aceeași fereastră.** Formulată exact ca să testeze ce §3 a găsit că lipsește. Dacă pică, obiectul trebuie **redenumit**, nu respins |
| **O** | **★ invarianță la traiectorie** | ≥50 traiectorii de serializare, **≥90% pozitive**, iar cea publicată între P10 și P90 |

Niciun prag nu se mișcă după rezultate.

## 18 — RĂSPUNSURI LA §1

| | |
|---|---|
| reproductibil mecanic | **DA**, exact |
| tranziție `RANGE→TREND` autentică | **NU** — e `breakout H4 + displacement`; poarta de range contribuie `+0,009` și admite `TREND_UP` în 18% din cazuri |
| tail robust | **DA** — top 10% ≈ 36% din profit, mediană `+0,328`, motiv structural |
| implementat cauzal | **DA** — verificat, inclusiv decalajul deliberat `eff[i−2]` |
| distinct de candidații H4 existenți | **PARȚIAL** — `RELATED_BUT_DISTINCT` față de ei, dar **`PARAMETRIC_VARIANT`** al propriei familii de breakout (92–100% subset) |
| eligibil pentru validare independentă | **NU** |
| dovezi curate ȘI suficiente | **NU** — și, unic până acum, **nici măcar `V1` nu atinge `n ≥ 30`** |

## 19 — CE AR DEBLOCA

1. **Redenumire și re-identificare.** Dacă vrei să păstrezi obiectul — și există un obiect real —
   trebuie să primească **ID nou** ca `H4-breakout-displacement-L`, iar cadrul „specialist de tranziție,
   complementar" retras. Costă zero dovezi.
2. **Poarta N, rulată acum pe DEV.** `breakout + displacement` fără poarta de range dă `+0,4199`
   serializat pe `n=40` — **mai multe tranzacții** decât candidatul. Dacă versiunea fără poartă e egală
   sau mai bună, ea e candidatul mai bun, cu frecvență mai mare, ceea ce atacă direct problema de
   suficiență de la §16.
3. **Un regim advers.** DEV conține unul: 2021, `−0,143`. Testarea deliberată pe perioade non-bull
   spune mai mult decât ~25 de tranzacții dintr-un bull.
4. **Acumulare prospectivă**: `n ≥ 50` cere ~1,8 ani de M5 nou.

**Recomand (1) + (2), imediat și gratuit.** Nu recomand cheltuirea lui `V1`: la ~25 de tranzacții
așteptate nu se poate produce un verdict interpretabil, indiferent de curățenie.

## 20 — PREDARE CĂTRE RED TEAM

Gata de atacat: identitatea și declarația de ramură-de-harness (§1), reproducerea exactă (§2),
**descompunerea semantică în trei componente (§3)**, auditul de coadă (§4), testul de 36 de traiectorii
(§5), **testul displacement-vs-acceptance pe populația-părinte comună (§6)**, corecția
Jaccard-vs-conținere la immediate/retest (§8), statistica de adecvare (§11), redundanța la trei niveluri
(§13), relevanța atenuată a expunerii RANGE (§15), porțile N și O (§17).

**★ AUTO-CORECȚIE, A DOUA OARĂ CONSECUTIV — clasă de eroare, nu accident.** În prima redactare am înghețat amprenta `transition_campaign.py` ca `e6e4b3a53a25` — **un număr pe care nu îl calculasem**. Blobul real la `fd80040` este **`f0657ca73c06`**; verificat și corectat înainte de publicare. Exact aceeași eroare am prins-o și la `MT-H4-efficiency-L` (`32e69ab`). Două ocurențe consecutive înseamnă tipar, deci îmi impun regula: **nicio amprentă nu intră într-un document înainte ca `git rev-parse` care o produce să fi rulat.** E aceeași disciplină pe care o cer altora — nu scrie un număr fără să îl măsori.

**Auto-atac 1:** §3.1 folosește populația **neserializată** ca arbitru pentru contribuția componentelor.
Un adversar poate susține că serializat poarta de range contribuie mai mult (`+0,4199 → +0,4431`,
adică `+0,023`). Ambele cifre sunt în raport. Argumentul meu: contribuția unei *condiții* se măsoară pe
populația de semnale, nu pe un subeșantion selectat de o regulă de blocare fără legătură cu condiția.

**Auto-atac 2:** §6 confirmă displacement peste acceptance pe părintele comun, dar **neserializat**.
Nu am rulat o versiune serializată cu populație-părinte comună; e posibil ca ordinea de blocare să
schimbe magnitudinile (nu, cred, semnul, dat fiind `+0,269` vs `−0,076`).

**Auto-atac 3:** clasificarea `PARAMETRIC_VARIANT` se bazează pe conținerea semnalelor (92–100%), nu pe
o demonstrație că filtrul de displacement e „doar un parametru". Un adversar poate susține că un filtru
care mută media de la `+0,015` la `+0,260` e mai mult decât un parametru. Cifrele sunt în §3.1.

---

```
TR_H4_RNG2TREND_DISPONLY_L_FRESH_VALIDATION_EVIDENCE_REQUIRED
TR_H4_RNG2TREND_DISPONLY_L_FRESH_EVIDENCE_ACCUMULATION_REQUIRED   (se aplica INDEPENDENT: V1 ~25 < 30)
TR_H4_RNG2TREND_DISPONLY_L_TRANSITION_SEMANTICS_NOT_SUPPORTED
TR_H4_RNG2TREND_DISPONLY_L_IMPLEMENTATION_AUDIT_PASS
TR_H4_RNG2TREND_DISPONLY_L_CAUSALITY_PASS
TR_H4_RNG2TREND_DISPONLY_L_TAIL_CLAIM_JUSTIFIED
TR_H4_RNG2TREND_DISPONLY_L_SERIALIZATION_PATH_ROBUST
DISPLACEMENT_VS_ACCEPTANCE_CAUSAL_CLAIM = CONFIRMED_ON_COMMON_POPULATION
M5_REQUIRED = FALSE  (confirmat, si testul lui Alpha era deja corect matchuit)
CALIB_ADEQUACY = INSUFFICIENT  (n=9, t=1,58, IC include zero)
MECHANISM_CLASS = RELATED_BUT_DISTINCT / PARAMETRIC_VARIANT al familiei de breakout H4
RESEARCH_LEVEL_COMPLEMENTARITY  (vs MT-H4-efficiency-L)
GATES_PREREGISTERED_CONTINGENT  (A-O)
```

*Fără execuție de validare. Fără retuning Alpha. Fără candidați secundari (`TR-H4-breakout-L`,
`breakout_immediate`, `breakout_retest` rămân research-only, §21). Fără AI Trader, Catalog, broker, live.*
