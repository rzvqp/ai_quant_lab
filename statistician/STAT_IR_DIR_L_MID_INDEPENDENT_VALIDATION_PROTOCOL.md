# IR-DIR-L-mid — PREGĂTIREA VALIDĂRII INDEPENDENTE

**Divizia Statistician · `STAT-IR-DIR-L-MID-INDEPENDENT-VALIDATION-PREP-001` · 2026-08-21**

```
IR_DIR_L_MID_FRESH_VALIDATION_EVIDENCE_REQUIRED
```

**Protocolul NU e înghețat. Nicio validare executată.**

Dar evidența nu e principalul obstacol. **Testul de fidelitate a mecanismului cerut la §4 nu trece**, și
îl raportez ca verdict separat, în afara listei din §15, fiindcă lista nu prevedea acest rezultat:

```
IR_DIR_L_MID_DIRECTIONAL_ABLATION_NOT_LEGITIMATE
IR_DIR_L_MID_TAIL_CONCENTRATION_DISQUALIFYING
```

Toate cifrele raportate de Alpha **se reproduc exact**. Ce nu se susține este ce înseamnă ele.

---

## 1 — IDENTITATE: ★ CANDIDATUL NU EXISTĂ CA OBIECT DE COD

Prima constatare, înainte de orice măsurătoare. Am căutat `IR-DIR-L-mid` în tot repo-ul:

```
range_intra.REG  ->  IR-{bos|compexp|failcounter}-{L|S}-{mid|opp}     = 12 ID-uri
"IR-DIR-L-mid"   ->  apare EXCLUSIV in ALPHA_..._REPORT.md            = 0 ocurente in cod
```

Candidatul e **brațul A (coarse) al `range_intra.run(long=True, tp_mode="mid")`**, extras în
`deepen_intra.py` prin `IR.run("bos", True, "mid", …)["A"]`. Numele e un artefact de raport.

**★ Iar brațul A nu depinde de mecanism.** Ramura `A` din `run()` nu apelează niciodată `legfn`. Am
verificat empiric: `bos`, `compexp` și `failcounter` produc **exact aceleași 46 de tranzacții**
(`n=46 WR=0.435 avgR=0.523 PF=1.858`, identic la ultima zecimală). Deci nu sunt trei candidați — e
**unul singur**, iar alegerea `"bos"` din `deepen_intra` e arbitrară și fără efect.

### Identitatea înghețată

| element | valoare recuperată din cod |
|---|---|
| identitate canonică | `range_intra.run(mech=<orice>, long=True, tp_mode="mid")` → **brațul `A`** |
| amprente | `range_intra.py` `41fe6411efa4` · `range_m5.py` `bee2639f7178` · `deepen_intra.py` `5b475fdcee58` · `m5_data.py` `1339e74a5e05` |
| **container H1** | `rhi = rolling(24).max().shift(1)`, `rlo = rolling(24).min().shift(1)`, `rmid=(rhi+rlo)/2`, `width=rhi−rlo` |
| **gate `in_range`** | `abs(eff) < 0.35` **și** `40p ≤ width ≤ 600p` **și** `touch_hi ≥ 2` **și** `touch_lo ≥ 2` (atingere = în 10% din lățime) |
| locație | `loc = (entry_ref − rlo[i]) / width[i]`, `0` = range low |
| **gate de zonă** | **`loc ≤ 0.60`** ← definiția reală a candidatului |
| **confirmare direcțională** | **`h1c[i] > h1o[i]`** — o singură bară H1 cu închidere pozitivă |
| intrare | `m5o[j_ref]`, prima bară M5 după `h1ct[i]` (= deschiderea H1 următoare) |
| **SL** | `min(h1.low[i−2 … i]) − 0.10 × ATR14_H1` → **stopul e deținut de H1** (§10) |
| **TP** | `rmid[i]` — mijlocul containerului |
| gate de spațiu | `room = abs(rmid − entry_ref) ≥ 70 pips` **și** `rmid ≤ rhi` |
| hold maxim | 576 bare M5 (48 h) |
| serializare | `m5t[j_ref] > lastA`, `lastA` = timpul barei `j_ref + 576` |
| cost | `TICK 0.01`, `PIP 0.10`, STRESS round-trip **0.24**, BASE 0.05 |

### §5 — statutul M5

```
M5_SIGNAL_REQUIRED    = FALSE     (bratul A nu apeleaza niciun mecanism M5)
M5_EXECUTION_REQUIRED = TRUE      (pretul de fill = m5o[j_ref]; parcurgerea intrabar = walk() pe M5)
```

Formularea exactă contează: M5 **nu** e sursă de semnal, dar candidatul **nu poate fi executat fără
M5** — atât prețul de intrare cât și ordinea stop/țintă în interiorul barei vin din M5. Nu validez
nicio variantă M5 sub această identitate.

### ★ §12 — o narowing deja prezentă în raportul Alpha

Codul spune `loc ≤ 0.60`. Raportul Alpha, la §recomandare finală, descrie candidatul ca
**„lower-zone (0–25%)"**. Sunt două definiții diferite, iar a doua e **mai îngustă decât ce s-a
măsurat**. Îngheț definiția din **cod** (`≤ 0.60`). Orice variantă restrânsă la 0–25% sau 0–10% cere
**ID nou** și tratament de evidență nou, exact cum ai cerut.

*(În practică restricția e aproape inertă: 44 din 46 de tranzacții cad sub 25%, 0 peste 50% — v. §4.4.)*

---

## 2 — §3 REPRODUCEREA: **EXACTĂ**

Am reexecutat implementarea, fără retuning, prin poarta gated.

| | Alpha | reprodus | |
|---|---|---|---|
| DEV `n` | 46 | **46** | ✓ |
| DEV `WR` | 43,5% | **0,435** | ✓ |
| DEV `avgR` | +0,523 | **+0,5230** | ✓ |
| DEV `PF` | 1,86 | **1,858** | ✓ |
| DEV `best-10%-rem` | +0,121 | **+0,1211** | ✓ |
| CALIB `n` | 19 | **19** | ✓ |
| CALIB `WR` | 52,6% | **0,526** | ✓ |
| CALIB `avgR` | +0,612 | **+0,6121** | ✓ |
| CALIB `best-5%-rem` | +0,256 | **+0,2562** | ✓ |
| room median | ~92 p | **92,3 p** | ✓ |
| `%room ≥ 70` | 100% | **100%** | ✓ (v. §3.1) |
| `%room ≥ 80` | ~78% | **78,3%** | ✓ |

**Nicio corecție aritmetică.** Corecțiile de mai jos sunt semantice.

### 3.1 ★ „100% ≥ 70 pips" e o TAUTOLOGIE, nu un rezultat

```
range_intra.run():   if room < 70*PIP: continue
```

Spațiul de ≥70 pips e un **filtru de eligibilitate a setup-ului**, nu o proprietate descoperită.
`room.min() = 70,2 p` prin construcție. Cifra nu poate fi altceva decât 100% și nu susține nicio
concluzie. Informativ rămâne doar ce e **condiționat** de ea: `≥80 p = 78,3%`, `≥100 p = 34,8%`,
**`≥150 p = 4,3%`**.

### 3.2 ★ Mediana tranzacției e **−1,041 R**

```
avgR = +0,523   dar   med_R = -1,041
tinta atinsa 20 · stop atins 26 · iesire pe timp 0     (din 46)
```

Peste jumătate din tranzacții sunt **stop complet**. Media pozitivă vine integral din coada dreaptă.
Un lucru bun, pe care îl consemnez: **zero ieșiri pe timp** — paranteza e curat binară, spre deosebire
de `HR-TU-pb-L`.

### 3.3 Geometrie completă (§11/§23)

```
lățime mediană container 268,5 p · SL median 37,4 p ($3,74) · room median 92,3 p ($9,23)
RR efectiv median 2,52 · loc median 0,141 · MAE median 29,7 p · MFE median 70,1 p
room: min 70,2 · P25 80,9 · P50 92,3 · P75 104,2 pips
maxDD 5,58 R · cea mai mare pierdere −1,174 R · cel mai mare câștig +6,029 R
```

---

## 3 — ★★ §4 TESTUL DE FIDELITATE A MECANISMULUI: **NU TRECE**

Ai cerut explicit să verific dacă ablația e o ablație cauzală legitimă sau e produsă de populații
diferite. **Este produsă de populații diferite.**

### 4.1 Defectul: serializarea nu e ținută fixă

`run()` actualizează `lastA` **numai când o tranzacție e efectiv luată**, adică numai când filtrul de
bară-up trece. `run_nofilter()` o actualizează la fiecare tranzacție — și ia mult mai multe. Blocajul
de 48 h se mută deci în alte locuri.

**Măsurat:**

```
|F| = 46 (cu filtru)     |N| = 79 (fara filtru)
tranzactii din F prezente in N:   11 / 46
tranzactii din F PIERDUTE de serializarea lui N:   35 / 46
```

**Doar 11 din cele 46 de tranzacții ale candidatului apar în setul de ablație.** N nu e o supermulțime
a lui F; sunt două eșantioane în mare parte **disjuncte**. Comparația `+0,523 vs −0,075` nu e o
ablație — e o comparație între două strategii diferite.

### 4.2 Ablația corectă, în trei forme

```
                                                    n     WR      avgR     b5rem     b10rem
F  filtru bara-up, serializat (CANDIDATUL)          46   0.435   +0.5230   +0.3018   +0.1211
N  fara filtru, serializat (ABLATIA ALPHA)          79   0.203   -0.0746   -0.5093   -0.7723
C  DOAR bare-down, serializat (complement adevarat) 74   0.176   -0.1095   -0.5763   -0.8630

--- serializare TINUTA FIXA (se imparte N insusi) ---
   N | bara H1 UP                                   12   0.500   +0.3897   +0.2102   +0.2102
   N | bara H1 DOWN                                 67   0.149   -0.1577   -0.6778   -0.9405

--- ★ serializare ELIMINATA (fiecare semnal eligibil) ---
   toate semnalele cu bara UP                      150   0.380   +0.1274   -0.1093   -0.2912
   toate semnalele cu bara DOWN                    303   0.201   +0.2810   -0.3696   -0.7173
   toate semnalele                                 453   0.260   +0.2301   -0.3177   -0.5957
```

### 4.3 ★ Ce arată: pe populația completă de semnale, filtrul direcțional **nu adaugă nimic — scade**

Când fiecare semnal eligibil e luat, **barele DOWN au media mai MARE decât barele UP: +0,2810 față de
+0,1274.** Filtrul direcțional, presupusul mecanism cauzal al candidatului, **nu poartă informație
direcțională** pe populația din care e extras. Semnul concluziei se **inversează**.

Iar fenomenul de bază — *zonă inferioară a containerului → mijloc* — are `+0,2301` pe **453** de
semnale, **indiferent de direcția barei H1**. Adică exact:

```
BUY_RANGE_LOW  ->  MIDPOINT
```

**pe care §4 al mandatului tău îl numește nominal ce candidatul nu are voie să fie.**

Formulez precis, ca să nu supra-interpretez în cealaltă direcție: pe populația neserializată,
`best-5%-removed` e **negativ în toate cele trei felii** (up −0,109 · down −0,370 · toate −0,318).
Deci nici fenomenul de bază nu e robust. Concluzia corectă nu e „reversia funcționează, filtrul nu" —
este: **ablația nu poate susține o afirmație cauzală în niciun sens, iar cifra `+0,523` e un produs
comun al (filtru × ordinea de serializare × coadă) pe 46 de tranzacții.**

### 4.4 Ce am căutat și NU am găsit — lookahead pe prețul de fill

Gate-urile (`loc ≤ 0.60`, `room ≥ 70p`, ordonarea stop/entry/target) sunt evaluate pe `entry_ref =
m5o[j_ref]`, **adică chiar prețul la care se face fill-ul**. Am recalculat totul cu gate-urile evaluate
pe `h1c[i]` (strict cunoscut înainte de decizie), păstrând fill-ul la `m5o[j_ref]`:

```
gate pe pretul de fill (Alpha) : DEV n=46 avgR +0.5230 | CALIB n=19 avgR +0.6121
gate pe inchiderea H1 (strict) : DEV n=46 avgR +0.5230 | CALIB n=19 avgR +0.6121
```

**Identic.** Nu există efect. Îl raportez fiindcă am căutat un defect specific și nu e acolo — asta
contează la fel de mult ca defectele găsite.

### 4.5 Detaliu de distribuție a zonei (§7 al mandatului Alpha, §12 al tău)

```
loc  0-10%   n=15   avgR +0.994
loc 10-25%   n=29   avgR +0.215
loc 25-50%   n= 2   avgR +1.461      <- doua tranzactii
loc 50-60%   n= 0   avgR  --
```

Gate-ul nominal e `≤0.60`, dar **44/46 sunt sub 25%** și **niciuna peste 50%**. Cea mai mare medie
pe zonă e în celula cu **n=2**. Defalcarea e dominată de zgomot și **nu poate fi convertită** într-o
definiție de candidat.

---

## 4 — ★★ §24 CONCENTRAREA COZII: DISCALIFICANTĂ DUPĂ PROPRIUL TĂU CRITERIU

Raportul Alpha scrie: *„edge-ul supraviețuiește eliminării a 10% din tranzacții → **nu sunt câteva
range-uri care au scăpat în trenduri**"*. Am măsurat afirmația direct:

```
total DEV = 24,06 R pe 46 de tranzactii

top 1 tranzactie (2,2% din n)  =  6,03 R  =  25,1% din TOT profitul
top 2                          = 10,78 R  =  44,8%
top 3                          = 15,01 R  =  62,4%
top 5 (10,9% din n)            = 22,73 R  =  94,5%   <<<

scoate top 1 -> avgR +0,4006 · top 2 -> +0,3018 · top 4 -> +0,1211
```

**Cinci tranzacții din 46 produc 94,5% din profit.** `best-10%-removed = +0,121` nu contrazice asta —
o *exprimă*: după scoaterea a 4 tranzacții rămân 5,09 R pe 42 de tranzacții. §24 al mandatului tău
cere literal să nu accepți o strategie al cărei edge e de fapt câteva range-uri care au scăpat în
trenduri. **Aceasta este acea strategie**, iar mediana de −1,041 R o confirmă din cealaltă direcție.

Sub §21 al mandatului Alpha („kill când … tail dependence catastrophic … sau semnalul e o versiune
deghizată a mean-reversion-ului de frontieră"), candidatul ar fi trebuit ucis la sursă.

---

## 5 — §25 ROBUSTEȚE TEMPORALĂ

```
2021: n= 8   avgR +1,126
2022: n= 9   avgR -0,006      <- plat, dezvaluit corect de Alpha
2023: n=29   avgR +0,521
```

**63% din tranzacții sunt în 2023.** Anul cel mai puternic are 8 tranzacții. Nu depinde *integral* de
un an, dar concentrarea e severă și se combină multiplicativ cu §4: cele 5 tranzacții care fac 94,5%
din profit sunt distribuite pe un eșantion deja concentrat într-un an.

---

## 6 — §6 PROVENIENȚA EVIDENȚEI: **VERIFICATĂ**

Lanțul `range_intra` → `range_m5` → `m5_data` → `edge_research._common.load`. Reexecutat de mine:

```
M5 gated 155.258 bare  2021-07-27 15:45Z .. 2024-06-20 00:40Z
H1 agregat 12.946      DEV 10.168 · CALIB 2.778
bare H1 „in_range": DEV 4.352 / 10.168 (42,8%) · CALIB 1.204
DEV 121.949 bare (ohlc b30912e1...) · CALIB 33.309 (ohlc 3c170953...)  = cele inghetate la b8d0447
```

| cerință | rezultat |
|---|---|
| acces 2025+ pentru ACEASTĂ campanie | **0** |
| utilizare N4 | **0** — zero referințe în `range_intra` / `range_m5` / `deepen_intra` |
| `read_csv` pe `data/market` | **0** |
| evidență protejată | **0** |

---

## 7 — ★ §7/§8 AUDITUL DE NOUTATE, SPECIFIC ACESTUI CANDIDAT

Regiunile candidate sunt aceleași derivate mecanic la `6d4430a` din splitul M5 ratificat
(`50_50_stratified_by_regime_segment`, întrețesut, embargo 3.000):

| regiune | interval | bare | `ohlc_sha256` (32) |
|---|---|---|---|
| **V1** | `2024-07-10 20:45Z → 2025-10-23 09:15Z` | 91.445 | `a2ca328f40101954b42c08b9f9512ac2` |
| **V2** | `2025-10-23 09:15Z → 2026-02-17 11:45Z` | 22.229 | `c4d32d911eab0212ebd4b8f783283dc5` |
| **V3** | `2026-03-10 07:45Z → 2026-06-20 13:45Z` | 19.950 | `1496b35eafc59ac10fcfd4295aa39e15` |
| **V4** | `2026-07-13 06:00Z → 2026-07-27 17:55Z` | 2.904 | `a130b9a9ce2f812d9d175b08cd432a5a` |

### 7.1 Ce se transferă de la auditul precedent

`V2` și `V3` sunt **CONSUMATE** prin breach-ul holdout-ului terminal (`PROJECT_STATE_v2 §8.23`, verdict
CEO). `≥17` studii de edge Flow A committed au `date_range 2022-12-16 → 2025-10-23`, acoperind integral
`V1`; Flow A **este** Alpha Discovery Laboratory.

### 7.2 ★ Ce e NOU și e specific acestui candidat: cercetarea de RANGE a consumat `V1`

Ai cerut explicit să verific dacă regiunea propusă a influențat *range research, range boundaries,
intra-range hypotheses*. Am măsurat, folosind coordonatele non-semantice din propriile mele artefacte
de selecție (loturile blind 02, MB3, FB14, F441):

```
124 ferestre blind randate in total ->  11 cad INTEGRAL in calendarul V1 (2024-07-10 .. 2025-10-23):

  lotul 02   BLIND-001, BLIND-032, BLIND-033, BLIND-047     ETICHETATE DE CEO
  MB3        MB3-011                                        ETICHETATA DE CEO
             MB3-035, MB3-047                               randate, SEALED, neetichetate
  FB14       FB14-012, FB14-013, FB14-014                   ETICHETATE DE CEO
  F441       F441-014                                       ETICHETATA DE CEO

  ->  9 din 11 au fost randate SI etichetate semantic de CEO; 2 randate si sigilate.
```

Acelea sunt ferestre pe care **le-ai privit și le-ai etichetat personal** ca `RANGE` / `TREND` /
`TRANSITION`, la rezoluție M15, în exact calendarul propus ca dovadă independentă — pentru un candidat
al cărui **container este un range**. Și nu e material periferic: `FB14` și `F441` **sunt** validările
blind proaspete ale lui V4.4 și V4.4.1, iar lotul 02 a stat la baza specificației semantice V3. Deci
semantica de RANGE a laboratorului (V3 → V4.4, praguri, ratificare, verdicte de generalizare) e
parțial derivată din structura de piață din `V1`.

**Legătura mecanică e ABSENTĂ**, și o spun clar: `range_m5.in_range` e o definiție locală
(`rolling-24 hi/lo + |eff|<0.35 + width + touch≥2`), **nu** detectorul V4.4; nu există import.
Semnalez o singură coincidență numerică — `touch ≥ 2` vs `n_touch = 2` din configul V4.4 ratificat —
dar valoarea e generică (minimul natural pentru „două atingeri pe fiecare parte) și **nu afirm
transplant**.

### 7.3 §8 — separarea cerută

| canal | verdict |
|---|---|
| **A. folosire mecanică a datelor viitoare** | **ABSENTĂ.** Poarta gated se oprește fizic la `2024-06-20`; 0 bare 2025+; 0 `read_csv`; 0 N4. Verificat, nu presupus. |
| **B. cunoaștere de laborator / studii înrudite** | **PREZENTĂ și, aici, mai puternică decât la `HR-TU-pb-L`.** Nu doar familii de mecanism adiacente (E0xx), ci **etichete semantice de RANGE produse chiar de CEO pe 11 ferestre din V1**, iar containerul candidatului *este* un range. |

```
IR_DIR_L_MID_VALIDATION_EVIDENCE = PARTIALLY_CONSUMED   (V1)
                                 = CONSUMED             (V2, V3)
                                 = CLEAN                (V4, 2.904 bare)
```

**Nu supra-declar independența:** canalul B nu poate fi cuantificat și nu poate fi exclus. Blochează
afirmația „validare independentă"; nu blochează o evaluare out-of-sample declarată ca atare.

---

## 8 — §9 SUFICIENȚA EȘANTIONULUI

Frecvență măsurată, fără a citi niciun rezultat în regiunile protejate — doar rata din DEV/CALIB
aplicată numărului de bare (recensământ pe coloana `time`):

```
DEV   : 46 / 121.949 = 1 la 2.651 bare M5
CALIB : 19 /  33.309 = 1 la 1.753 bare M5
combinat: 65 / 155.258 = 1 la 2.389 bare M5

V1    91.445 bare  ->  ~38 tranzactii
V1+V2 113.674      ->  ~48
V3     19.950      ->   ~8
V4      2.904      ->   ~1
```

**★ Dar aici pragul de suficiență e mult mai sus decât de obicei**, tocmai din cauza §4: dacă 10,9% din
tranzacții produc 94,5% din profit, atunci un eșantion de 38 de tranzacții e determinat aproape integral
de **dacă 1–2 valori extreme se întâmplă să apară**. Un asemenea test nu poate nici confirma, nici
infirma. Pentru ca media să nu fie dominată de coadă ar trebui un ordin de mărime mai mult — orientativ
`n ≈ 200`, adică ~478.000 de bare M5 ≈ **4,5 ani de date noi**.

```
IR_DIR_L_MID_EVIDENCE = NEITHER CLEAN NOR SUFFICIENT
```

---

## 9 — §13 INDEPENDENȚA FAȚĂ DE `HR-TU-pb-L`: **VERIFICATĂ**, cu o corecție

Am recalculat ambele seturi de tranzacții pe aceeași populație DEV:

```
IR-DIR-L-mid : 46 tranzactii pe 46 zile distincte
HR-TU-pb-L   : 51 tranzactii pe 51 zile distincte
suprapunere pe aceeasi zi = 0        Jaccard = 0,0000     CONFIRMAT
bare de semnal IR aflate in regim TREND_UP (regimul lui HR) = 0 / 46
```

Disjuncția e **structurală**, nu norocoasă: `HR` cere `TREND_UP`, iar `IR` cere `in_range`. Clasific,
cum ai cerut, drept **complementaritate de nivel-cercetare**.

### ★ Corecție la caracterizarea „primul Alpha de regim RANGE"

Regimurile H1 ale celor 46 de semnale IR, după **clasificatorul de regim al proiectului**:

```
TREND_DOWN 17 (37%) · REGIME_INDEPENDENT 13 (28%) · RANGE 11 (24%) · TRANSITION 5 (11%)
```

**Doar 11 din 46 sunt în regimul `RANGE`.** Cel mai mare grup e `TREND_DOWN`. Cauza: coexistă **două
definiții diferite de range** în același cod — `range_m5.in_range` (`|eff| < 0.35`) și
`m5_data.regime_label` (`RANGE` la `|effic| < 0.20`) — și nu sunt de acord. Deci afirmația *„fires
exactly when the trend strategy is inactive (in ranges)"* e corectă doar în prima jumătate: fireează
când strategia de **trend ascendent** e inactivă, dar **37% din tranzacții sunt long-uri contra unui
TREND_DOWN**.

O nuanță suplimentară: disjuncția e **doar pe aceeași zi**. Pentru 20 din 46 de tranzacții IR există o
tranzacție `HR` la **≤3 zile** distanță (mediana 3,6 zile). Jaccard pe zile e o măsură slabă de
independență; nu susține o afirmație de necorelare a randamentelor.

**Față de `S5` și `H4-bo-raw-S`:** nu am comparat cantitativ. Ar cere executarea acelor strategii, iar
`S5` rulează pe altă populație (M15 canonic), a cărei regiune de validare curată e deja sigilată și
predată Red Team. Nu consum evidență protejată pentru o comparație descriptivă.

---

## 10 — §10 PORȚI PRE-ÎNREGISTRATE (contingent, NU protocol înghețat)

Le fixez acum, **fără să fi văzut niciun rezultat în V1–V4**, ca să nu poată fi ajustate ulterior.

```
IR_DIR_L_MID_GATES_PREREGISTERED_CONTINGENT
```

| # | poartă | prag |
|---|---|---|
| A | N minim | `n ≥ 30` → altfel `INCONCLUSIVE`, niciodată PASS/FAIL. `n < 150` ⇒ etichetă permanentă `TAIL_UNDERDETERMINED` (justificare: §4) |
| B | expectanță BASE | `> 0` la round-trip `0,05` |
| C | expectanță STRESS | `> 0` la round-trip **`0,24`** |
| D | robustețe temporală | treimi cronologice fixate pe **bare**: ≥2/3 pozitive, niciuna sub `−0,10` |
| E | `best-1%-removed` | `> 0` |
| F | `best-5%-removed` | `> 0` |
| G | maxDD | `≤ 12 R` (DEV 5,58 R) |
| H | pierdere individuală maximă | `≤ 1,5 R` (DEV −1,174 R) |
| I | fidelitate de specificație | container `rolling-24 + eff<0.35 + touch≥2`, zonă `loc ≤ 0.60` **neschimbată**, filtru `h1c>h1o`, SL = swing 3 bare H1, TP = `rmid`. Orice restrângere de zonă ⇒ **STOP**, nu FAIL |
| J | geometrie economică | `room ≥ 70p` rămâne **filtru de setup**; se raportează `≥80 / ≥100 / ≥150` ca rezultate |
| **K** | **★ concentrarea cozii** | **top 10% din tranzacții ≤ 60% din profitul total.** Adăugată de mine: fără ea, porțile E/F pot trece iar §24 al mandatului tău să fie totuși încălcat — exact ce s-a întâmplat pe DEV (94,5%) |
| **L** | **★ non-degenerarea mecanismului** | pe populația **neserializată** de semnale, `avgR(bară UP) > avgR(bară DOWN)`. Fără ea, „confirmare direcțională" nu înseamnă nimic |

Niciun prag nu se mișcă după rezultate.

## 11 — §11 SPECIFICAȚIA DE RAPORTARE

```
WR (= rata de atingere a tintei) + descompunere tinta / stop / iesire-pe-timp
RR efectiv (mediana per-tranzactie) · PF · avg R BASE · avg R STRESS · maxDD · pierdere maxima
mediana R  (pe DEV a fost -1,041 -- se raporteaza intotdeauna langa medie)
SL median in pips si USD · room/TP median in pips si USD · P25/P50/P75
%TP >=70 (declarat ca FILTRU) · >=80 · >=100 · >=150
percentila de intrare in containerul H1 + defalcare pe zone (DIAGNOSTIC, nu definitie)
concentrarea cozii: top 1/2/5/10% din profit         (10 pips = 1,00 USD)
```

## 12 — CE AR DEBLOCA

1. **Repararea ablației înainte de orice altceva.** Ablația trebuie refăcută pe populația de semnale
   ținând sampling-ul fix. Dacă `avgR(UP) > avgR(DOWN)` nu se restabilește, candidatul **este**
   `BUY_RANGE_LOW_MEAN_REVERSION` deghizat, iar ramura respectivă e deja închisă cu
   `NO_ROBUST_RANGE_M5_ALPHA_FOUND`. Asta nu costă nicio dovadă nouă și se face pe DEV.
2. **Un mecanism direcțional real**, în locul unei singure bare H1 pozitive — mandatul tău enumera
   secvențe HL, BOS, displacement, acceptare. `h1c > h1o` nu e niciunul dintre ele. ID nou.
3. **Acumulare prospectivă de M5** — singura cale către evidență curată *și* suficientă, dar aici
   pragul e ~4,5 ani, nu ~17 luni, din cauza cozii.
4. **Dacă totuși vrei un verdict rapid:** `V1` folosit explicit ca `OUT_OF_SAMPLE_SAME_DIVISION`, cu
   etichetele `TAIL_UNDERDETERMINED` și `RANGE_SEMANTICS_PARTIALLY_CONSUMED`. Cumpără foarte puțin.

**Recomand (1).** E gratuit, se face pe date deja consumate, și determină dacă mai există ceva de
validat. Nu recomand să se cheltuie `V1` pe un candidat al cărui mecanism declarat nu a fost încă
demonstrat.

---

## 13 — PREDARE CĂTRE RED TEAM

Gata de atacat: identitatea (§1), reproducerea exactă (§2), ablația și cele trei forme corective (§3),
concentrarea cozii (§4), auditul de noutate cu numărătoarea ferestrelor blind (§7), porțile contingente
inclusiv K și L (§10).

Ținta pe care o formulez împotriva mea: **secțiunea 4.3 depinde de alegerea „fără serializare" ca
referință.** Un adversar poate susține că tranzacționarea reală *este* serializată, deci comparația
relevantă e F vs C (`+0,523` vs `−0,110`), care sprijină Alpha. Contraargumentul meu: întrebarea de la
§4 e dacă filtrul poartă **informație direcțională**, iar asta se răspunde pe populația de semnale, nu
pe un subeșantion selectat de o regulă de blocare care nu are legătură cu direcția. Ambele lecturi sunt
în raport, cu cifrele lor; nu am ascuns-o pe cea care mă contrazice.

A doua țintă: **§7.2 e o inferență.** Am numărat 11 ferestre blind în calendarul `V1` și am arătat că
nu există legătură mecanică. Nu am demonstrat că etichetarea acelor ferestre a influențat definiția
containerului din `range_m5.py`.

---

```
IR_DIR_L_MID_FRESH_VALIDATION_EVIDENCE_REQUIRED
IR_DIR_L_MID_CANDIDATE_IDENTITY_FROZEN
IR_DIR_L_MID_RESEARCH_RESULTS_REPRODUCED_EXACTLY
IR_DIR_L_MID_DIRECTIONAL_ABLATION_NOT_LEGITIMATE
IR_DIR_L_MID_TAIL_CONCENTRATION_DISQUALIFYING
M5_SIGNAL_REQUIRED = FALSE · M5_EXECUTION_REQUIRED = TRUE
IR_DIR_L_MID_GATES_PREREGISTERED_CONTINGENT
```

*Fără execuție de validare. Fără modificarea Alpha. Fără AI Trader, Catalog, broker, live.*
