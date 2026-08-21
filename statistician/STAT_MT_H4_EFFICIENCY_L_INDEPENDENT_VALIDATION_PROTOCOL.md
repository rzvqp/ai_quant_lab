# MT-H4-efficiency-L — PREGĂTIREA VALIDĂRII INDEPENDENTE

**Divizia Statistician · `STAT-MT-H4-EFFICIENCY-L-INDEPENDENT-VALIDATION-PREP-001` · 2026-08-21**

```
MT_H4_EFFICIENCY_L_FRESH_VALIDATION_EVIDENCE_REQUIRED
```

**Protocolul NU e înghețat. Nicio validare executată.**

Spre deosebire de cele două mandate precedente, **auditul de implementare TRECE**, iar două dintre
suspiciunile pe care le duceam cu mine din `IR-DIR-L-mid` **se infirmă la măsurătoare**. Le raportez ca
atare, fiindcă un rezultat negativ al unei căutări de defect contează la fel de mult ca unul pozitiv.

Ce blochează e altceva, și e mai simplu: **evidența nu e nouă, nu e suficientă, iar mecanismul este o
expunere de regim, nu un edge de eveniment.**

---

## 1 — §2 IDENTITATEA, RECUPERATĂ MECANIC

**`MT-H4-efficiency-L` EXISTĂ ca ID de registru** (`f"MT-{tf}-{mech}-{'L' if long else 'S'}"`), spre
deosebire de `IR-DIR-L-mid`. Dar, așa cum ai cerut să declar explicit:

> **Candidatul este o RAMURĂ DE HARNESS, nu o specificație izolată de strategie.** El este
> `multitf_campaign.eval_tf(tf="H4", mech="efficiency", long=True, rr=1.5, …)` — o instanțiere
> parametrică a unui evaluator generic partajat de toate cele 56 de ID-uri. Nu există fișier, funcție
> sau obiect care să conțină numai această strategie.

| element | valoare din cod |
|---|---|
| amprente | `multitf_campaign.py` blob `0989e1d4e6bc` @ `e1b08d8` · `m5_data.py` blob `1339e74a5e05` · motor `wp5b/code/mstrat.py` |
| TF de edge | **H4**, agregat cauzal din M5-ul gated (`m5_data.aggregate`, bucket `floor("4h")`, păstrat dacă `nsub ≥ 24` din 48) |
| direcție | **LONG-only** |
| **definiția eficienței** | `effic[i] = net / path`, `net = c[i] − c[i−20]`, `path = Σ abs(diff(c))` pe `[i−20, i−1]` (`.shift(1)`) |
| **prag** | **`effic[i] > 0.4`** — singura condiție de semnal |
| lookback | **20 bare H4** (≈3,3 zile); ATR14, EMA20/50 disponibile dar **neutilizate** de acest mecanism |
| context/regim | **niciun gate de regim** (`regime_gate=None` în campanie) |
| timing semnal | la închiderea barei H4 `i` |
| intrare | deschiderea barei H4 `i+1` (`o[i+1]`) |
| **SL structural** | `min(low[i−4 … i]) − 0.15 × ATR14_H4[i]` — swing de 5 bare **pe TF-ul de edge** |
| **TP** | `entry + 1.5 × risk` (`exit_kind="rr"`, `exit_param=1.5`) |
| hold maxim | **48 bare H4 = 8 zile**; la epuizare, ieșire la închidere |
| podea de stop | `max(2·spread·tick, 5·tick, 0.10·ATR_H4)` — **măsurat: nu se activează niciodată (0%)** |
| cost | `TICK = CFG['tick'] = **0,01**` · `2·cost = STRESS round-trip **0,24**` |
| **serializare** | `mstrat.simulate`: `last = xi` (**indexul de IEȘIRE**), `if ei <= last: continue` → o poziție o dată |
| filtre | niciunul în plus (`risk>0`, ordonare stop/entry) |

### ★ O verificare pe care o datoram: `mstrat.CFG['tick']`

La mandatul S5/S20 am impus ca validarea să **nu** folosească `mstrat.CFG` pentru cost sau podea,
fiindcă `tick = 0.1` fusese marcat de Red Team ca greșit de 10× (`RT-CODE-A-0007`). **Defectul a fost
remediat**: `mstrat.py:10` are acum `TICK = CFG['tick']` cu `CFG['tick'] = 0.01` și comentariul de
reconciliere. Măsurat în proces: `mstrat.TICK = 0.01`. **Constrângerea mea anterioară nu mai e
necesară pe această cale.** O consemnez fiindcă am fost cea care a impus-o.

---

## 2 — §3 REPRODUCEREA: **EXACTĂ**

| | Alpha | reprodus | |
|---|---|---|---|
| DEV STRESS | +0,380 | **+0,3798** | ✓ |
| DEV `best-10%-rem` | +0,267 | **+0,2668** | ✓ |
| DEV `WR` | ~43,5% | **0,435** (20 ținte / 46) | ✓ |
| CALIB | +0,357 | **+0,3569** | ✓ |
| CALIB `WR` | ~50% | **0,500** | ✓ |
| TP median | ~320 p | **320,5 p** | ✓ |
| **CALIB N** | „12–13" | **exact 12** | precizat |

**Zero dezacorduri aritmetice sau semantice cu Alpha.** Cifrele complete cerute la §3:

```
DEV   n=46  GROSS +0.3941  BASE +0.3912  STRESS +0.3798   PF 2.007   maxDD 6.12 R
      med_R +0.515 · P25/P50/P75 = -1.008 / +0.515 / +1.485
      avg winner +1.290 (n=27) · avg loser -0.913 (n=19) · worst -1.034 · best +1.786
      best1%rem +0.3486 · best2%rem +0.3486 · best5%rem +0.3226 · best10%rem +0.2668
      mix iesiri: 20 tinta / 16 stop / 10 timp (21,7%)
CALIB n=12  GROSS +0.3670  BASE +0.3649  STRESS +0.3569   PF 1.847   maxDD 2.02 R
      med_R +0.933 · avg winner +1.334 (n=7) · avg loser -1.011 (n=5)
      best1/5/10%rem toate +0.2533 (n prea mic pentru a le distinge)
```

---

## 3 — §4 AUDITUL DE COADĂ: **`BROAD_BASED_NOT_LOTTERY` ESTE JUSTIFICAT**

Acesta e primul candidat din serie la care afirmația se susține. Comparat direct cu cel care a picat:

```
                          MT-H4-efficiency-L      IR-DIR-L-mid
top 1 tranzactie                10,2%                25,1%
top 2                           18,8%                44,8%
top 3                           27,3%                62,4%
top 5 (10,9% din n)             44,4%                94,5%
mediana tranzactiei            +0,515               -1,041
cel mai mare castig            +1,786 R             +6,029 R
best10%rem                     +0,2668              +0,1211
```

**Mediana tranzacției este POZITIVĂ (+0,515)**, iar decăderea `best-1% → 5% → 10%`
(`+0,349 → +0,323 → +0,267`) e lină, nu abruptă.

### ★ Motivul structural, care e argumentul cel mai tare

`exit_kind="rr"` cu `rr=1.5` **plafonează R-ul per tranzacție prin construcție**: nicio tranzacție nu
poate fi un outlier de 6R. Maximul observat e `+1,786` (o ieșire pe timp peste țintă). `IR-DIR-L-mid`
avea țintă la `rmid`, cu `room/risk` variabil, deci structură de loterie posibilă — și realizată.

**Nu emit `TAIL_CONCENTRATION_DISQUALIFYING`.** Concentrarea de 44,4% în top 10,9% e ridicată față de
uniform, dar e limita naturală a unei distribuții mărginite cu 43,5% câștiguri la +1,49 și restul la
−1,0. Nu există aici structura pe care §24 al mandatului de descoperire o interzice.

*(Nuanță onestă: pe CALIB coada **este** concentrată — top 2 din 12 = 69,9%, top 3 = 104,7% — dar la
n=12 statisticile de coadă nu au conținut. Vezi §6.)*

---

## 4 — §5 AUDITUL DE SERIALIZARE: defectul EXISTĂ, dar candidatul **trece** testul care contează

Am căutat exact recurența defectului `IR-DIR-L-mid`. **Structura e prezentă:**

```
mstrat.simulate:  last = xi   (indexul de IESIRE)   ;   if ei <= last: continue

DEV  : 339 setup-uri brute  ->   46 luate (13,6%)
CALIB: 102 setup-uri brute  ->   12 luate (11,8%)
```

Blocajul aruncă **86,4%** din semnale, iar durata lui depinde de **rezultatul** tranzacției precedente
(o tranzacție care merge până la limita de 48 de bare blochează mai mult decât una care atinge repede
ținta). Populația realizată este deci **endogenă și dependentă de traiectorie**.

Și diferența e mare:

```
DEV   BLOCAT   n= 46  avgR +0.3798   b10rem +0.2668
      NEBLOCAT n=339  avgR +0.0803   b10rem -0.0730   medR -1.004
CALIB BLOCAT   n= 12  avgR +0.3569
      NEBLOCAT n=102  avgR +0.6509   b10rem +0.5591   medR +1.481
```

### ★ 4.1 Testul de sensibilitate la traiectorie — și rezultatul **infirmă** suspiciunea

La `IR-DIR-L-mid`, decalajul dintre populația serializată și cea completă **inversa** concluzia. Aici am
făcut testul direct: am rulat **120 de traiectorii alternative**, aruncând primele `k` semnale
(`k = 0…119`) și lăsând blocajul să se reașeze de la zero.

```
avgR pe traiectorii:  min +0.2853 · P10 +0.3467 · P25 +0.3711 · MEDIANA +0.4153 · P75 +0.5238 · max +0.5953
n pe traiectorii   :  min 30 · mediana 40 · max 48
traiectorii cu avgR <= 0 :  0,0%
traiectoria publicata (k=0) : +0.3798, la PERCENTILA 41,7  --  sub mediana traiectoriilor
```

**Niciuna dintre cele 120 de traiectorii nu e negativă, iar cea publicată e ușor sub mediană.**
`+0,3798` **nu** e o traiectorie norocoasă.

### 4.2 Interpretarea corectă a decalajului 0,380 vs 0,080

Cele două numere estimează **lucruri diferite**, și niciunul nu e greșit:

- `+0,0803` = R-ul așteptat al unui **semnal ales la întâmplare** din cele 339;
- `+0,3798` = R-ul așteptat al **secvenței efectiv tranzacționabile**, o poziție o dată.

Cum `effic > 0.4` e o **stare persistentă** (§7), cele 339 de semnale sunt masiv suprapuse: aceeași
mișcare e numărată de zeci de ori. Blocajul nu selectează câștigători, ci **deduplică**. Iar regula e
implementabilă cauzal — la orice moment ai sau nu ai poziție. **Deci nu emit verdictul de defect pe
care l-am emis la `IR-DIR-L-mid`.**

### 4.3 ★ Ce rămâne totuși un defect — la nivel de CAMPANIE, nu de candidat

Cele 56 de ID-uri sunt comparate între ele, iar fiecare are propria populație endogenă: un mecanism cu
semnale dese e deduplicat agresiv, unul cu semnale rare aproape deloc. **Clasamentul de timeframe
`H4 > H1 >> M15 ~ M5` și ierarhia de mecanisme sunt deci comparații între populații diferit
serializate.** Nu invalidează candidatul, dar invalidează afirmația de ranking din commit. Îl semnalez
separat, ca să nu se contamineze verdictele.

---

## 5 — §6 CAUZALITATEA H4: **PASS**, cu o auto-corecție

```
semnal la inchiderea barei i  ->  intrare la deschiderea barei i+1     cauzal
stop = min(low[i-4..i]) - 0.15*ATR[i]                                   doar bare inchise
effic[i] = (c[i]-c[i-20]) / sum|diff(c)|[i-20..i-1]                     doar bare inchise
mers intrabar: STOP verificat INAINTE de tinta (conservator)
```

Nicio scurgere de lumânare H4 incompletă, niciun high/low viitor.

### ★ 5.1 O corecție a propriei mele măsurători

Prima trecere am numărat barele H4 aflate la ≤20 de bare după orice pauză `>24 h` și am obținut
**31/46 de tranzacții** — un număr alarmant. **Era greșit:** în FX/metale, pauza de weekend e normală și
apare de 115 ori în trei ani; orice feature rulant din orice backtest o traversează. Filtrând corect
pentru pauza reală — **golul de discovery de 258,6 zile** dintre segmentul S1 și S2 —:

```
pauze > 7 zile in cadrul H4: 1  (258,6 zile)
semnale DEV in cele 20 de bare de dupa ea:   0 / 339
tranzactii DEV luate in acea banda:          0 / 46
```

**Zero contaminare.** Publicasem un pericol care nu există; îl corectez înainte, nu după.

### 5.2 Semantica de agregare, înghețată

```
bucket = dt.floor("4h") ; pastrat daca nsub >= 24 din 48 ; time = primul epoch M5 ; close_time = ultimul
nsub: min 24 · P10 36 · mediana 48 · medie 45,5 · max 48
bare H4 PARTIALE (< 48 sub-bare): 17,0%   dintre care 24-35 sub-bare: 4,0%
```

**17% din „barele H4" nu sunt bare de patru ore.** High/low-ul lor subestimează amplitudinea reală,
ceea ce afectează atât swing-ul de stop, cât și detectarea atingerilor în `walk`. Nu e lookahead, dar e
o infidelitate de specificație care trebuie reprodusă identic la validare — sau corectată printr-un
`nsub` mai strict, caz în care candidatul se schimbă și cere ID nou.

---

## 6 — §7 GEOMETRIA DE EXECUȚIE: **RR nominal = RR efectiv, exact**

```
tinta = entry + 1.5 * risk,   cu  risk = abs(entry - stop)  si  ACELASI `entry` = o[i+1]
->  RR EFECTIV = 1,500 EXACT, pe toate tranzactiile
->  podeaua de stop se activeaza in 0,0% din cazuri (risc pre-podea = risc post-podea)
->  ZERO slippage de intrare fata de referinta structurala: nu exista referinta separata
```

**Eroarea de la `HR-TU-pb-L` nu se repetă.** Acolo SL/TP erau ancorate într-un preț de referință diferit
de cel al fill-ului, iar RR-ul executat era 1,68 în loc de 2,0. Aici ținta derivă din **același** preț
de intrare și **același** risc, deci nu există decalaj nominal/efectiv. **PASS.**

## 7 — §8 GEOMETRIA ECONOMICĂ

```
DEV  : SL median 213,6 p ($21,36) · TP median 320,5 p ($32,05)
       P25 / P50 / P75 TP = 177 / 320 / 483 pips
       %TP >=70 = 97,8 · >=80 = 97,8 · >=100 = 97,8 · >=150 = 89,1 · >=200 = 69,6 · >=300 = 56,5
CALIB: SL median 286,2 p ($28,62) · TP median 429,3 p · >=300 = 75,0%
```

**Afirmația de ~320 de pips se verifică (320,5).** E de departe cel mai „economic" candidat al
programului — 56,5% din ținte trec de 300 de pips. Spre deosebire de `IR-DIR-L-mid`, procentele **nu
sunt tautologice**: nu există filtru de spațiu minim în acest candidat; ținta rezultă din mărimea
stopului structural H4.

**Consemnez ca observație de dimensionare, nu ca defect:** un stop median de **$21,36** (CALIB $28,62)
e foarte mare. La convenția proiectului, riscul median per tranzacție e de **214 pips de proiect**.
Aceasta e o strategie de swing, nu una de intraday, iar dimensionarea trebuie să reflecte asta.

---

## 8 — §9 ROBUSTEȚE TEMPORALĂ: **problema principală a candidatului**

```
2021: n= 7  avgR -0,2490  medR -1,008  WR 0,143  PF 0,573  maxDD 4,08 R  total  -1,74 R
2022: n=10  avgR +0,3080  medR +0,480  WR 0,300  PF 1,756  maxDD 1,03 R  total  +3,08 R
2023: n=29  avgR +0,5564  medR +1,476  WR 0,552  PF 2,755  maxDD 2,04 R  total +16,14 R
```

**2021 e NEGATIV** — nu doar „slab", cum îl descrie Alpha: PF sub 1, un singur câștig din șapte.
Și, mai grav: **din cei 17,47 R totali, 16,14 R (92,4%) vin din 2023 singur**, cu 63% din tranzacții.
Perioada nu se elimină și nu e eliminată.

Concentrarea temporală e aici **mai severă decât concentrarea de coadă**, și cele două nu se compensează:
un candidat cu o coadă sănătoasă, dar al cărui profit e produs într-un singur an, e tot un candidat
dependent de un singur regim.

## 9 — §10 ADECVAREA CALIBRĂRII

```
CALIB N = 12 (exact)     toate in 2024
media +0,3569 · sd 1,246 · se 0,360 · t = 0,99 · IC 95% = [-0,348 ; +1,062]
```

**Intervalul de încredere include zero.**

```
CALIB_ADEQUACY = INSUFFICIENT
```

Nu `SUPPORTIVE_BUT_THIN`: un `t` de 0,99 nu susține nimic — e compatibil cu expectanță zero și chiar cu
expectanță negativă. Nu echivalez expectanța CALIB pozitivă cu validare independentă.

**Pentru comparație, și DEV e la limită:** `n=46 · sd 1,156 · se 0,170 · t = 2,23 · IC [+0,046 ; +0,714]`.
Limita inferioară e **+0,046** — abia peste zero — și asta **înainte** de a lua în calcul că e cel mai
bun din **56 de ID-uri** testate pe același DEV. Sub o corecție de multiplicitate elementară (Bonferroni
56 ⇒ prag `t ≈ 3,2`), `t = 2,23` nu supraviețuiește.

---

## 10 — §11 REDUNDANȚA DE MECANISM: **`HIGHLY_RELATED_MECHANISM`**

### ★ Constatarea centrală: `effic > 0.4` nu e un eveniment, e o STARE

Mecanismul nu are declanșator. Nu există bară de semnal, rupere, respingere sau secvență. Condiția e
adevărată pe **orice** bară H4 în care eficiența direcțională pe 20 de bare depășește 0,4 — deci pe
blocuri contigue de bare.

```
bare de semnal efficiency-L pe DEV : 339 din 2.652 bare H4 (12,8%)
   dintre ele in regimul H4 TREND_UP : 305 (90,0%)
   bare TREND_UP in DEV               : 491
   -> efficiency fireaza pe 62,1% din TOATE barele TREND_UP
```

Iar eticheta `TREND_UP` a proiectului este ea însăși `ema20 > ema50 ȘI effic > 0.30`. Deci
`MT-H4-efficiency-L` este, în esență:

> **„fii long cât timp H4 e într-un uptrend puternic"**

O expunere de regim, nu un edge de eveniment. Asta explică fără rest profilul temporal: 2021 (topping)
**−0,249**, 2023 (bull puternic) **+0,556**, CALIB 2024 (bull) **+0,357**.

### Suprapunerea de condiție-semnal cu celelalte mecanisme H4 LONG

```
vs breakout     Jaccard 0,223   acopera 26,5% din barele efficiency
vs momentum     Jaccard 0,162   26,8%
vs structure    Jaccard 0,105   15,6%
vs dispaccept   Jaccard 0,078    8,8%
vs pullback     Jaccard 0,010    2,1%
vs compression  Jaccard 0,011    1,2%
```

Nu e `DUPLICATE` și nu e `PARAMETRIC_VARIANT` al niciunuia. Dar nu e nici `NEW_MECHANISM`:

```
MT_H4_EFFICIENCY_L_MECHANISM_CLASS = HIGHLY_RELATED_MECHANISM
   (relatat cu FILTRUL DE REGIM al proiectului, nu cu un alt candidat)
```

## 11 — §12 SUPRAPUNERE LA NIVEL DE CERCETARE

**vs `MT-H4-dispaccept-L`** (candidatul secundar, măsurat pe aceeași populație):

```
suprapunere de bare-tranzactie: 3 din 46 vs 41   Jaccard 0,036
suprapunere pe aceeasi ZI      : 12 zile         Jaccard(zile) 0,169
```

Nu sunt duplicate la nivel de tranzacție, dar **12 zile comune** și ambele fiind specialiste H4 LONG de
trend înseamnă **expunere corelată**, nu independență. §17 respectat: nu consum evidență pentru el.

**vs `H4-bo-raw-S`:** suprapunerea de tranzacții **nu e calculabilă legitim** și nu o fabric.
`H4-bo-raw-S` trăiește pe o populație complet diferită — H4 derivat din **M15 canonic**, plafonat la
blocurile b0/b1/calib (`≤ 2021-09`) — în timp ce acest candidat trăiește pe H4 derivat din **M5 gated**
(`2021-07 → 2024-06`). Nu împart nici bare, nici ani. Conceptual însă: `H4-bo-raw-S` e o continuare de
trend H4, aliniată la trendul D1, **SHORT**. Adică **oglinda aceleiași familii**. Iar mandatul tău spune
corect că LONG vs SHORT nu e dovadă de independență — o susțin: sunt același mecanism de continuare,
pe direcții și epoci diferite.

**vs `HR-TU-pb-L` și `S5`:** ambele pe alte populații sau alte TF-uri; nu consum rezultate protejate
pentru o comparație descriptivă.

---

## 12 — §13 AUDITUL DE NOUTATE SPECIFIC CANDIDATULUI

### 12.1 `MECHANICAL_DATA_CONSUMPTION` — **ABSENT**, verificat

```
poarta gated: 155.258 bare, se opreste fizic la 2024-06-20 00:40Z
N4 = 0 · read_csv pe data/market = 0 · 2025+ = 0 · shadow_driver = 0
pragul 0.4 si lookback-ul 20: constante declarate in cod, fara grid, fara ajustare pe date
`effic` e definit in m5_data.add_features, exclusiv din date gated
```

### 12.2 `ANALYST_KNOWLEDGE_CONSUMPTION` — **PREZENT**

Se transferă integral de la auditurile precedente: `≥17` studii de edge Flow A committed au
`date_range 2022-12-16 → 2025-10-23`, iar cinci merg la `2026-07-13`; Flow A **este** Alpha Discovery
Laboratory. Familiile relevante aici sunt explicit de continuare: `E028 Fibonacci OTE` („intrare de
**continuare** favorabilă statistic"), `E011 failed 3-drive`, `E026 ADR exhaustion` (persistență /
epuizare a mișcării). `2025-10-23 → 2026-07-13` rămâne **CONSUMAT** prin breach-ul holdout-ului terminal.

### 12.3 ★ Ce e specific ACESTUI candidat și e mai grav decât la ceilalți doi

Din §10: candidatul este, în esență, **long pe trendul H4**. Iar manifestul ratificat etichetează el
însuși regiunea propusă:

> `"2022-10 -> 2026-02 bull (+223.3%)"`

`V1` și `V2` sunt **integral** înăuntru. La `HR-TU-pb-L` am numit asta un test *aliniat*. Aici e mai
mult decât aliniat: un candidat a cărui condiție de semnal este *„trendul e puternic în sus"*, testat
exclusiv într-un segment declarat `+223,3%` bull, **măsoară beta pe acel trend**, nu alpha. Singurul
segment care l-ar testa advers — `S3`, `"2026-02 → 2026-06 correction (−24,1%)"` — e integral în
fereastra invalidată. Iar DEV-ul ne spune deja ce se întâmplă într-un regim advers: **2021, −0,249**.

```
MT_H4_EFFICIENCY_L_VALIDATION_EVIDENCE = PARTIALLY_CONSUMED (V1) · CONSUMED (V2, V3) · CLEAN (V4)
```

---

## 13 — §14/§15 REGIUNI DISPONIBILE ȘI SUFICIENȚĂ

Rata măsurată: `46 / 2.652 bare H4 DEV` = **1 tranzacție la 57,7 bare H4** (CALIB: 1 la 60,4 — coerent).
Numărătoarea de bare e făcută **exclusiv pe coloana `time`**, fără a inspecta niciun rezultat.

| regiune | interval | bare M5 | bare H4 | tranzacții est. | status |
|---|---|---|---|---|---|
| **V1** | `2024-07-10 → 2025-10-23` | 91.445 | 1.988 | **~34** | `PARTIALLY_CONSUMED` |
| **V2** | `2025-10-23 → 2026-02-17` | 22.229 | 482 | ~8 | `CONSUMED` |
| **V3** | `2026-03-10 → 2026-06-20` | 19.950 | 434 | ~8 | `CONSUMED` |
| **V4** | `2026-07-13 → 2026-07-27` | 2.904 | 64 | **~1** | `CLEAN` |

*(Amprentele `ohlc_sha256` ale celor patru regiuni sunt înghețate la `6d4430a` §6 și rămân valabile.)*

```
n >= 30  : atins MARGINAL, doar in V1 (~34)  -- si V1 nu e curat
n >= 50  : NICAIERI
n >= 100 : NICAIERI, nici macar V1+V2+V3 cumulat (~50)
```

**Nu există nicio regiune simultan `CLEAN` și `SUFFICIENT`.** Singura regiune curată, `V4`, produce
aproximativ **o** tranzacție. Iar la un candidat al cărui IC pe DEV e deja `[+0,046 ; +0,714]`, un
eșantion de 34 nu poate distinge `+0,38` de `0`.

---

## 14 — §16 PORȚI PRE-ÎNREGISTRATE (contingent, NU protocol înghețat)

Fixate acum, **fără să fi văzut niciun rezultat în V1–V4**.

```
MT_H4_EFFICIENCY_L_GATES_PREREGISTERED_CONTINGENT
```

| # | poartă | prag |
|---|---|---|
| A | fidelitate de specificație | `effic>0.4` pe 20 bare H4, SL = swing 5 bare `−0.15·ATR`, TP = `entry+1.5·risk`, hold 48, `nsub≥24`, blocaj o-poziție-o-dată. Orice abatere ⇒ **STOP**, nu FAIL |
| B | N minim | `n ≥ 30` → altfel `INCONCLUSIVE`. `n < 100` ⇒ etichetă permanentă `LOW_POWER` |
| C | expectanță BASE | `> 0` la round-trip `0,05` |
| D | expectanță STRESS | `> 0` la round-trip **`0,24`** |
| E | robustețe temporală | treimi cronologice fixate pe **bare H4**: ≥2/3 pozitive, niciuna sub `−0,10` |
| F | `best-1%-removed` | `> 0` (valid la `n ≥ 100`; sub, se raportează fără verdict) |
| G | `best-5%-removed` | `> 0` |
| H | concentrarea profitului | **top 10% din tranzacții ≤ 60% din profitul total** (DEV a dat 44,4% ⇒ poarta e trecută pe DEV și nu e retro-croită) |
| I | maxDD | `≤ 12 R` (DEV 6,12 R) |
| J | pierdere individuală maximă | `≤ 1,5 R` (DEV −1,034 R) |
| K | fidelitate RR efectiv | `RR_efectiv = 1,500 ± 0,01` pe **fiecare** tranzacție |
| L | geometrie economică TP | `%TP ≥ 150` să rămână `≥ 70%` (DEV 89,1%; CALIB 91,7%) |
| **M** | **★ referință de regim** | **`avgR` al candidatului > `avgR` al aceleiași geometrii de intrare/stop/țintă declanșate pe TOATE barele H4 din fereastră (fără condiția `effic>0.4`), cu același blocaj.** Adăugată de mine: pentru o strategie care e expunere de regim (§10), singurul test care separă alpha de beta este un control care ia trendul fără condiție. Fără această poartă, un bull de +223% garantează un PASS |
| **N** | **★ invarianță la traiectorie** | pe ≥50 de traiectorii alternative de serializare, **≥90% pozitive**, iar traiectoria publicată între P10 și P90. Formalizează testul care a exonerat candidatul aici (§4.1) |

Niciun prag nu se mișcă după rezultate.

---

## 15 — RĂSPUNSURILE LA §1

| | |
|---|---|
| **A. reproductibil mecanic** | **DA** — exact, toate cifrele |
| **B. semantic valid** | **DA cu rezervă** — arhitectura e coerentă și RR-ul nominal = efectiv; dar mecanismul e o **stare de regim**, nu un eveniment |
| **C. autentic tail-robust** | **DA** — `BROAD_BASED_NOT_LOTTERY` justificat, cu motiv structural |
| **D. suficient specificat** | **PARȚIAL** — e o ramură de harness, nu o spec izolată; `nsub≥24` (17% bare parțiale) și blocajul de serializare trebuie să facă parte explicit din spec |
| **E. eligibil pentru validare independentă** | **NU** — nicio regiune nu e simultan curată și suficientă |
| **F. dovezi proaspete specifice** | **NU** — `V1` `PARTIALLY_CONSUMED` și, mai important, aliniat la regimul candidatului |

## 16 — CE AR DEBLOCA

1. **Poarta M, măsurată acum pe DEV, gratis.** Dacă `effic > 0.4` nu bate controlul „intră pe fiecare
   bară H4 cu aceeași geometrie", candidatul nu e alpha, e beta pe trend. Nu costă nicio dovadă nouă și
   e testul cel mai informativ care se poate face astăzi.
2. **Un regim advers.** DEV conține deja unul — 2021, cu **−0,249** pe 7 tranzacții. Extinderea
   deliberată a evaluării către perioade non-bull (alt instrument, altă epocă) spune mai mult decât
   încă 34 de tranzacții dintr-un bull.
3. **Acumulare prospectivă de M5**, pentru `n ≥ 100`: la 1 la 57,7 bare H4, ~5.770 bare H4 ≈
   **2,6 ani** de date noi. Mai puțin decât la ceilalți doi candidați, fiindcă H4 e mai productiv.
4. **Reducerea multiplicității**: cel mai bun din 56, cu `t = 2,23`. O corecție explicită de
   multiplicitate pe DEV ar spune dacă mai rămâne ceva de validat.

**Recomand (1), apoi (2).** Nu recomand cheltuirea lui `V1`: ~34 de tranzacții dintr-un bull de +223%,
pentru un candidat care este long pe trend, nu poate produce un verdict interpretabil.

## 17 — PREDARE CĂTRE RED TEAM

Gata de atacat: identitatea și declarația de ramură-de-harness (§1), reproducerea exactă (§2), auditul
de coadă cu argumentul structural (§3), testul de 120 de traiectorii (§4.1), auto-corecția pe golul de
date (§5.1), fidelitatea RR (§6), statistica de adecvare (§9), caracterizarea mecanismului ca stare de
regim (§10), porțile M și N (§14).

**Auto-atac 1:** §4.1 testează sensibilitatea la traiectorie doar prin *decalarea începutului*. Un
adversar poate cere perturbări mai agresive (eliminare aleatoare de semnale, deplasarea limitei de
hold). Nu le-am rulat.

**Auto-atac 2:** §10 leagă `efficiency` de `TREND_UP` prin suprapunere de bare (90%), nu printr-o
demonstrație că expunerea la trend explică *întregul* rezultat. Poarta M e propusă tocmai fiindcă
măsurătoarea care ar decide lipsește; nu pretind că am făcut-o.

**Auto-corecție 2, prinsă înainte de commit:** în prima redactare a înghețat amprenta `multitf_campaign.py` ca `f4832ee2` — un număr pe care **nu îl calculasem**. Blobul real la `e1b08d8` este **`0989e1d4e6bc`**; l-am verificat și l-am corectat înainte de publicare. O amprentă scrisă fără a fi măsurată este exact clasa de eroare pe care o urmăresc la alții.

**Auto-corecție consemnată:** am publicat intern un „31/46 tranzacții contaminate de golul de date",
apoi am descoperit că numărasem weekendurile. Cifra corectă e **0/46**. Corecția e în §5.1.

---

```
MT_H4_EFFICIENCY_L_FRESH_VALIDATION_EVIDENCE_REQUIRED
MT_H4_EFFICIENCY_L_IMPLEMENTATION_AUDIT_PASS
MT_H4_EFFICIENCY_L_RESEARCH_RESULTS_REPRODUCED_EXACTLY
MT_H4_EFFICIENCY_L_TAIL_CLAIM_JUSTIFIED  (BROAD_BASED_NOT_LOTTERY confirmat)
MT_H4_EFFICIENCY_L_SERIALIZATION_PATH_ROBUST  (120/120 traiectorii pozitive)
MT_H4_EFFICIENCY_L_EFFECTIVE_RR_FIDELITY_PASS  (1,500 exact)
MT_H4_EFFICIENCY_L_CALIB_ADEQUACY = INSUFFICIENT  (n=12, t=0,99, IC include zero)
MT_H4_EFFICIENCY_L_MECHANISM_CLASS = HIGHLY_RELATED_MECHANISM  (expunere de regim)
MT_H4_EFFICIENCY_L_GATES_PREREGISTERED_CONTINGENT  (A-N)
MT_H4_dispaccept_L = SECONDARY_RESEARCH_CANDIDATE  (neatins)
```

*Fără execuție de validare. Fără retuning Alpha. Fără al doilea candidat. Fără AI Trader, Catalog,
broker, live.*
