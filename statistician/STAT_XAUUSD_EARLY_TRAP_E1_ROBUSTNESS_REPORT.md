# XAUUSD — AUDIT DE ROBUSTEȚE AL SEMNALULUI `EARLY-TRAP-E1`

**Divizia Statistician · `STAT-XAUUSD-EARLY-TRAP-E1-ROBUSTNESS-001` · 2026-08-22**

```
EARLY_TRAP_E1_SIGNAL_SUPPORTED
EARLY_TRAP_E1_READY_FOR_EXECUTION_RESEARCH
```

**Primul verdict `SUPPORTED` pe care îl emit în această serie.** Toate cele patru condiții din §27 sunt
îndeplinite și le-am verificat pe rând. Nu proiectez execuție.

Emit verdictul **cu trei calificări pe care le consider obligatorii în orice citare a lui:**

```
1. Lift-ul e +0,105 dupa CONTROLUL pe distanta ramasa, NU +0,193 sau +0,302.
2. 2022 e compatibil cu zgomotul (CI contine rata de baza).
3. Valoarea regulii e SELECTIE, nu TIMING: testul pereche da +0,0085, CI contine zero.
```

`DEV-only. Zero CALIB, zero V1, zero 2025+. Nicio proiectare de execuție, niciun stop, nicio țintă.`

---

## 1 — §2 IDENTITATEA ARTEFACTULUI

| element | valoare |
|---|---|
| fișiere | `early_trap.py` blob `67d82be0536b` · `early_trap2.py` blob `b30bf8ec234a`, ambele @ `6a5d535` |
| lineage | **`session_trap` (`722a0e0`) NESCHIMBAT** — aceleași 329 de sweep-uri Asia-High, verificat |
| landmark | `landmark(r, k)` cu `k = 1` → bara `sweep+1`; referință `ref = close[sw+1]` |
| **outcome** | `low[j] ≤ asia_mid` pentru `j ∈ [sw+2, sw+25)`, **oprit la sfârșitul zilei UTC**; **FĂRĂ stop** |
| firewall | zero `read_csv`, zero N4, zero `shadow_driver`, zero 2025+ |

### ★ 1.1 Prima constatare: **`EARLY-TRAP-E1` nu are implementare în depozit**

Mandatul spune „implementarea din depozit e autoritativă" și „nu reconstrui din acest prompt". **Nu
există ce recupera.** Am căutat în tot depozitul: șirul `EARLY-TRAP-E1` și regula `R2` apar **exclusiv
în raportul `.md`**. `early_trap.py` calculează economia landmark-urilor și AUC-uri univariate;
`early_trap2.py` antrenează un model logistic cu 11 features. **Niciunul nu evaluează regula cu două
condiții.**

**Am implementat-o eu, literal după textul raportului** (§5, linia 57): *„la E1 (închiderea barei
sweep+1): dacă bara închide sub Asia High ȘI are corp bearish → TRAP"*:

```python
R2(r) :=  close[sw+1] < asia_hi   AND   close[sw+1] < open[sw+1]
```

### ★ 1.2 A doua constatare: un defect de implementare real

`prior_attacks(r)` numără barele din **aceeași zi UTC** anterioare sweep-ului cu `high ≥ asia_hi`. Dar
barele **Asia însele** definesc `asia_hi`, deci cel puțin una satisface condiția **prin construcție**:

```
prior_attacks: min = 1 · mediana = 1 · max = 5  |  episoade cu 0 atacuri anterioare: 0 / 329
```

**Analiza „first vs repeat attack" e vacuă** — output-ul tipărește doar linia `repeat`, fiindcă
categoria `first` e goală. Feature-ul e inclus în modelul cu 11 variabile; AUC-ul lui (`0,510` DISC /
`0,409` CONF) e zgomot, deci **impactul e nul**, dar defectul e real.

---

## 2 — §2 REPRODUCEREA: **EXACTĂ**

Am rulat `early_trap2.py` integral, apoi am implementat `R2` și am măsurat-o pe aceeași populație:

| | Alpha | **reprodus** | |
|---|---|---|---|
| DISC `n` | 68 | **68** | ✓ |
| DISC `P(mid)` | 0,794 | **0,794** | ✓ |
| DISC bază / lift | 0,594 / +0,200 | **0,594 / +0,200** | ✓ |
| DISC dist. rămasă | 20,7 p | **20,7 p** | ✓ |
| CONF `n` | 50 | **50** | ✓ |
| CONF `P(mid)` | 0,840 | **0,840** | ✓ |
| CONF bază / lift | 0,659 / +0,181 | **0,659 / +0,181** | ✓ |
| CONF dist. rămasă | 23,3 p | **23,3 p** | ✓ |
| logistic DISC/CONF AUC | 0,743 / 0,679 | **0,743 / 0,679** | ✓ |
| ablație `e1_close_above` | 0,673 | **0,673** | ✓ |

Nu emit `EARLY_TRAP_E1_REPRODUCTION_FAIL`. **Regula, deși nescrisă în cod, produce exact cifrele
raportate.** Corectez explicit o ipoteză de lucru pe care o avusesem: bănuisem că cifrele „R2" sunt de
fapt ale bucket-ului logistic, mislabelate. **Nu sunt.**

### ★ 2.1 „Economii identice" e o coincidență, nu identitate de mulțime

Raportul spune că forma logistică dă „economii identice, confirmând că R2 captează semnalul". Am
măsurat suprapunerea:

```
pe toate cele 329: logistic q0.6 n=129 | R2 n=118 | comune=96 | Jaccard 0,636
pe CONFIRMARE    : logistic n= 50 | R2 n= 50 | comune=37 | Jaccard 0,587
P(mid) CONF      : logistic 0,840 | R2 0,840
```

Ambele au `n = 50` și `P = 0,840` pe confirmare, **dar împart doar 37 din 50 de episoade**. E o
coincidență de mărime și de medie, **nu** aceeași mulțime. Nu invalidează nimic — dar formularea
„confirmând" e mai tare decât ce arată datele.

---

## 3 — §4 CRONOLOGIA SELECȚIEI

```
MODEL/PRAG:  CONFIRMATION_SELECTED
REGULA R2 :  DISCOVERY_JUSTIFIABLE, dar NEVERIFICABIL ca oarba
```

**Pragul logistic e selectat pe CONF.** `early_trap2.py` evaluează `q ∈ {0.0, 0.5, 0.6, 0.7}` — **toate
patru pe CONFIRMARE** — și raportul reține `q0.6`. Alegerea nu e predeclarată.

**Componentele lui R2 sunt însă justificabile pe DISCOVERY singură.** Tabelul univariat arată, pe DISC:
`e1_bear` **0,673** și `e1_close_above` **0,299** (adică `0,701` inversat) — cele două cele mai
puternice features E1. R2 folosește exact aceste două. **DISC singură ar fi selectat aceleași două
condiții.** Asta e exculpator și îl consemnez ca atare.

**Dar nu pot certifica orbirea**: artefactul tipărește DISC și CONF **una lângă alta**, nu există
pre-înregistrare, iar regula însăși nu e în cod (§1.1). Deci nu pot stabili *când* a fost înghețată.

## 4 — §5 MULTIPLICITATE

```
landmark-uri E0..E3 evaluate                       = 4
features univariate evaluate pe DISC SI CONF       = 13
model logistic (11 features) + ablatie             = 2
praguri de probabilitate evaluate pe CONF          = 4   (q0.0/0.5/0.6/0.7)
subgrupuri de sesiune                              = 2 x 2 split
first-vs-repeat                                    = 2   (DEGENERAT, v. §1.2)
```

Testele sunt puternic dependente (landmark-urile sunt imbricate, features corelate), deci **nu aplic
Bonferroni**. Evaluarea mea: pentru **prag** multiplicitatea e reală (4 celule pe CONF, s-a reținut
una); pentru **regula R2** e mult mai mică, fiindcă cele două componente sunt cele mai puternice și pe
DISC. Iar lift-ul supraviețuiește testării temporale independente (§8) și controlului pe distanță (§7),
care nu sunt afectate de selecția de prag.

---

## 5 — §6 UNITATEA DE OBSERVAȚIE ȘI §23 N EFECTIV

```
parinti eligibili la E1: 329            R2: 118 episoade = 118 ZILE UNICE  (1 pe zi)
CONF R2: 50 episoade = 50 ZILE UNICE    atinse 42 · neatinse 8
total R2: atinse 96 · neatinse 22
```

**Da — `n = 50` reprezintă într-adevăr ~50 de episoade zilnice independente.** Nu există rânduri
repetate per episod: lineage-ul păstrează un singur sweep pe zi. Iar orizontul de outcome se oprește la
sfârșitul zilei UTC, deci ferestrele **nu se suprapun între zile**. §23 = răspuns afirmativ.

## 6 — §7/§8 REPERUL CAUZAL ȘI CRONOLOGIA OUTCOME-ULUI

```
semnal cunoscut la  : INCHIDEREA barei sw+1
prima bara eligibila: sw+2                  (`for j in range(ei+1, ...)`)
semantica tintei    : atingere INTRABAR a mid-ului (low[j] <= mid), oprita la sfarsitul zilei UTC
```

**Nicio parte din lumânarea E1 nu contează ca progres viitor.** Verificat în cod. §7/§8 = **PASS**.

*(Observație: orizontul e `min(24 bare, sfârșitul zilei UTC)` — sweep-urile târzii primesc o fereastră
mai scurtă. E o constrângere reală, moștenită, pe care o consemnez fără a o modifica.)*

## 7 — ★★ §9/§10/§11 CONTROL PE PĂRINTE, COMPLEMENT ȘI — DECISIV — PE DISTANȚĂ

### 7.1 Aceeași populație-părinte

```
strat                                n     P(mid)     lift    medRemain
parinte la E1 (toti)               329      0.620    +0.000       39.1p
close-below SINGUR                 165      0.764    +0.144       24.9p
corp bearish SINGUR                158      0.741    +0.120       27.4p
R2 = close-below SI bearish        118      0.814    +0.193       21.6p
complement NOT-R2                  211      0.512    -0.108       49.3p
```

### 7.2 §19 — conjuncția adaugă peste fiecare componentă

```
close-below dar NU bearish          47      0.638    +0.018       30.7p
bearish dar NU close-below          40      0.525    -0.095       49.3p
nici una                           124      0.460    -0.160       54.9p
suprapunere: Jaccard(close-below, bearish) = 0,576
```

**Close-below fără corp bearish adaugă practic nimic (`+0,018`); corp bearish fără close-below e
NEGATIV (`−0,095`). Doar conjuncția funcționează.** Răspunsul la §19 e clar: **da, combinația adaugă
informație peste oricare componentă.**

### 7.3 ★★ Testul decisiv — supraviețuiește lift-ul controlului pe distanța rămasă?

R2 selectează episoade **deja mai aproape de țintă** (`21,6 p` vs `39,1 p` la părinte, `49,3 p` la
complement). E același confuz de poziție pe care l-am identificat la `ce4b634`. L-am controlat:

```
cvintila distantei ramase          n R2   P(mid|R2)   n nonR2   P(mid|nonR2)      dif
[-104.8,  20.7) p                    54      0.926        12          0.833     +0.093
[  20.7,  32.2) p                    33      0.727        33          0.606     +0.121
[  32.2,  46.6) p                    20      0.800        45          0.644     +0.156
[  46.6,  63.0) p                     6      0.333        60          0.500     -0.167
[  63.0, 241.4) p                     5      0.800        61          0.311     +0.489

diferenta MEDIE ponderata, controland pe distanta = +0.115     (necontrolat: +0.302)
control potrivit pe DECILA de distanta: 0.709 vs R2 0.814  ->  increment +0.105
```

**~65% din separarea brută e efect de poziție. ~35% e real: `+0,105`, pozitiv în 4 din 5 cvintile.**

Asta e diferența esențială față de mandatul precedent: acolo, după control, `S1` rămânea cu `+0,008`.
**Aici rămâne `+0,105`.**

### 7.4 §12 incertitudine la nivel de episod (bootstrap pe zile)

```
P(mid | R2) = 0.814   CI95 = [0.746 ; 0.881]   (n = 118 episoade-zi)
lift vs parinte     = +0.193   CI95 = [+0.130 ; +0.258]   nu contine 0
lift vs COMPLEMENT  = +0.302   CI95 = [+0.204 ; +0.399]   nu contine 0
```

---

## 8 — §13 EVALUARE TEMPORALĂ (regulă FIXĂ, 5 blocuri cronologice de zile)

```
blk  interval           parinte n    base   R2 n  P(mid|R2)     lift   medRem
1    2021-07..2021-11          65   0.554     20     0.800    +0.246    16.9p
2    2021-11..2022-12          66   0.636     24     0.792    +0.155    16.7p
3    2022-12..2023-04          66   0.591     24     0.792    +0.201    33.3p
4    2023-04..2023-08          66   0.712     25     0.840    +0.128    26.0p
5    2023-08..2023-12          66   0.606     25     0.840    +0.234    20.8p

lift: POZITIV IN 5/5 blocuri | medie +0.193 sd 0.051 -> t = 8.53
```

**Nicio degradare, niciun bloc negativ.** Al doilea rezultat temporal puternic din serie — și, spre
deosebire de coada probabilistică, aici lift-ul **nu se prăbușește** la evaluare pe blocuri.

## 9 — §14 AN CU AN, cu atenție specială pe 2022

```
2021: parinte n= 82 base=0.561 | R2 n=25 P=0.840 lift=+0.279 CI95(P)=[0.680,0.960] medRem=16.1p
2022: parinte n= 54 base=0.685 | R2 n=23 P=0.783 lift=+0.097 CI95(P)=[0.609,0.957] medRem=20.5p
2023: parinte n=193 base=0.627 | R2 n=70 P=0.814 lift=+0.187 CI95(P)=[0.714,0.900] medRem=25.0p
```

**★ Răspunsul cerut la §14: în 2022 lift-ul e compatibil cu zgomotul.** Intervalul de încredere al
`P(mid | R2)` este `[0,609 ; 0,957]` și **conține rata de bază `0,685`**. Cu `n = 23`, nu se poate
distinge `0,783` de `0,685`.

Nu cer magnitudini identice pe ani — dar **2022 nu susține independent semnalul**; el nu îl contrazice.
2021 și 2023 îl susțin, cu CI-uri care exclud propriile baze.

## 10 — §15/§16 SESIUNE

```
LONDON : parinte n=232 base=0.659 | R2 n=91 P=0.802 lift=+0.143 medRem=23.1p
OVERLAP: parinte n= 83 base=0.578 | R2 n=24 P=0.875 lift=+0.297 medRem=13.1p
NY     : parinte n= 14 base=0.214 | R2 n= 3 P=0.667 lift=+0.452 medRem=30.2p     <- n=3, fara continut

interactiune London-vs-Overlap: +0.143 - 0.297 = -0.154   CI95 = [-0.314 ; +0.004]   CONTINE ZERO
```

**Ambele sesiuni majore au lift pozitiv**, iar interacțiunea **nu e stabilită statistic** (CI conține
zero, la limită). Deci:

```
EARLY_TRAP_E1 = GENERAL_SESSION_SIGNAL   (cu heterogenitate sugerata, nedemonstrata)
```

Semnalez totuși că `OVERLAP` are `medRemain` de doar `13,1 p` — jumătate din London — deci acolo
semnalul e mai puternic **dar economic mai sărac. `NY` rămâne inutilizabil** (3 episoade).

## 11 — §17/§18 SUPRAVIEȚUIREA DRUMULUI (caracterizare, fără reguli de stop)

```
n=118   P(nou maxim peste sweep) = 0.466        (Alpha raporta ~0.50 pe setul logistic CONF)
MAE: mediana 24.1p · P75 56.8p · P90 99.6p
MFE spre mid: mediana 28.3p | excursie adversa INAINTE de mid: mediana 24.1p
```

**§18 — descompunerea în patru clase:**

```
A  mid FARA nou maxim        : 62  (52.5%)
B  nou maxim, APOI mid       : 34  (28.8%)
C  nou maxim, FARA mid       : 21  (17.8%)
D  nici nou maxim, nici mid  :  1  ( 0.8%)
```

**Peste jumătate din episoadele semnalate ajung la mijloc fără să mai facă un maxim nou** — asta e
partea încurajatoare, și e materialul brut pentru cercetarea de execuție. Dar `MAE P90 = 99,6 pips`
împotriva a `21,6 pips` de recompensă mediană e problema pe care acea cercetare trebuie s-o rezolve.
**Nu proiectez nimic aici** (§25/§26).

## 12 — ★ §21/§22 FRONTIERA INFORMAȚIE–ECONOMIE, pe un ENDPOINT COMUN

**Atenție metodologică, obligatorie pentru a nu părea că mă contrazic:** raportul `ce4b634` a folosit
endpoint-ul **cu stop încorporat** (`session_trap.outcome`), acesta folosește endpoint-ul **fără stop**
(`early_trap.landmark`). Cifrele nu sunt comparabile direct. Am recalculat **toate stările pe același
endpoint fără stop**:

| stare | n | P(mid) | dist. rămasă | % consumat | lag (bare) | P(nou maxim) |
|---|---|---|---|---|---|---|
| S0 (bara de sweep) | 329 | 0,617 | 39,1 p | −1,4% | 0 | 0,769 |
| E1 părinte (`sw+1`) | 329 | 0,620 | 39,1 p | 0,2% | 1 | 0,669 |
| **EARLY-TRAP-E1 (R2)** | **118** | **0,814** | **21,6 p** | **35,0%** | **1** | **0,466** |
| NOT-R2 | 211 | 0,512 | 49,3 p | −22,9% | 1 | 0,782 |
| S1 return-inside | 255 | 0,729 | 26,1 p | 27,5% | 1 | 0,482 |
| S2 bearish displacement | 140 | 0,829 | 10,3 p | 72,9% | 4 | 0,214 |
| S4 structure break | 92 | 0,946 | −4,8 p | 111,9% | 6 | 0,054 |

**★ Răspunsul la §21: DA, `EARLY-TRAP-E1` rezolvă material problema de întârziere identificată la
`ce4b634`.** La aceeași probabilitate practic (`0,814` vs `0,829`), oferă **de 2,1× mai multă distanță
rămasă** (`21,6 p` vs `10,3 p`) și sosește **cu 3 bare mai devreme** (lag 1 vs 4). Iar față de `S4`
diferența e categorică: `S4` nu mai are ce oferi.

## 13 — ★★ CE ANUME FACE REGULA: SELECȚIE, NU TIMING

Am rulat și testul pereche care a demontat `S1` la mandatul precedent — pe **aceleași 118 episoade R2**,
`P(mid)` măsurat de la `sw+1` față de `P(mid)` măsurat de la **propriul lor sweep**:

```
de la E1 = 0.814     de la propriul sweep = 0.805     lift pereche = +0.0085   CI95 = [+0.000 ; +0.025]
```

**Interpretarea corectă, și e importantă:** regula **nu crește** probabilitatea pentru episoadele pe
care le semnalează — acelea aveau oricum `0,805` de la bara de sweep. Ce face regula e să **identifice
CARE episoade sunt acelea** (`0,814` vs `0,512` la complement).

Cele două teste răspund la întrebări diferite și ambele sunt adevărate:

```
PEREChE (aceleasi episoade, alt reper)  -> +0.008   reperul NU adauga valoare de TIMING
SECTIUNE (R2 vs complement, acelasi reper) -> +0.302 brut, +0.105 controlat pe distanta   -> SELECTIE REALA
```

**Pentru cercetarea de execuție contează selecția**, fiindcă la bara de sweep nu știi în care grup ești.
De aceea răspunsul la §1 este: regula **identifică** o subpopulație cu probabilitate material mai mare;
nu **mărește** probabilitatea episoadelor pe care le selectează.

---

## 14 — §27 VERDICT

```
EARLY_TRAP_E1_SIGNAL_SUPPORTED
```

Verificat punct cu punct față de definiția din mandat:

| condiția din §27 | verificare |
|---|---|
| regula fixă **se reproduce** | **DA** — exact, 8/8 cifre (deși a trebuit s-o implementez eu, §1.1) |
| rămâne pozitivă sub testare **temporală** | **DA** — 5/5 blocuri, medie `+0,193`, `t = 8,53` |
| rămâne pozitivă sub testare **conștientă de dependență** | **DA** — bootstrap pe episoade-zi, lift `+0,193` CI `[+0,130 ; +0,258]`; `n = 118` sunt 118 zile reale |
| lift **semnificativ peste controale pe același părinte** | **DA** — vs complement `+0,302`; **după controlul pe distanță `+0,105`**, pozitiv în 4/5 cvintile |
| păstrează **material mai multă distanță economică decât S2** | **DA** — `21,6 p` vs `10,3 p` (2,1×), la `P(mid)` practic egal, 3 bare mai devreme |

## 15 — §28 ELIGIBILITATE

```
EARLY_TRAP_E1_READY_FOR_EXECUTION_RESEARCH
```

**Nu proiectez execuție** (§25/§26). Predau cercetării de execuție următoarele **caracterizări**, nu
reguli:

```
recompensa mediana ramasa   21,6 p ($2,16)   P25 13,9p · P75 33,6p · P90 45,2p
                            >=20p in 57,6% · >=30p in 33,9% · >=40p in 17,8% · >=50p in 6,8%
excursie adversa            MAE mediana 24,1p · P75 56,8p · P90 99,6p
P(nou maxim peste sweep)    0,466        clasa C (nou maxim, fara mid) = 17,8%
clasa A (mid fara nou maxim) = 52,5%     -> peste jumatate ajung la tinta fara sa mai atace maximul
```

**Întrebarea deschisă, formulată neutru:** cu `MAE P90 ≈ 100 p` împotriva a `≈ 22 p` de recompensă
mediană, geometria stopului e problema centrală. **Nu o rezolv și nu sugerez o soluție.**

**Trei condiții pe care le atașez verdictului:**

1. **Orice citare a lui `+0,181` sau `+0,193` trebuie însoțită de `+0,105`** — lift-ul după controlul
   pe distanță. Prima cifră include efectul de poziție.
2. **`R2` trebuie implementată în cod** și comisă, cu numerele de mai sus ca test de regresie. Un semnal
   înghețat care există doar în proză nu e înghețat.
3. **2022 trebuie declarat ca an care nu susține independent semnalul** (CI conține baza).

## 16 — LIMITĂRI ALE PROPRIULUI MEU AUDIT

1. **Am implementat eu `R2`** din textul raportului. Reproduce toate cele opt cifre, ceea ce e o
   verificare puternică, dar dacă Alpha a folosit o variantă subtil diferită care întâmplător dă
   aceleași opt numere, nu aș putea distinge.
2. Controlul pe distanță (§7.3) folosește cvintile/decile pe **o singură dimensiune**. Un control mai
   bogat (volatilitate, oră, lățimea Asia) ar putea explica mai mult din `+0,105`.
3. Cvintila 4 a distanței dă `−0,167` pe `n = 6` R2 — contrazice tendința, dar la un `n` fără conținut.
4. Endpoint-ul nu are stop și se oprește la sfârșitul zilei UTC; ambele sunt moștenite și le-am păstrat,
   dar înseamnă că `P(mid)` **nu** e o probabilitate de tranzacție.
5. Blocurile temporale sunt egale ca număr de zile, nu ca durată; blocul 2 acoperă 13 luni.
6. Nu am testat stabilitatea regulii la perturbări (de exemplu prag de corp bearish nenul); §3 interzice.

---

```
EARLY_TRAP_E1_SIGNAL_SUPPORTED  ·  EARLY_TRAP_E1_READY_FOR_EXECUTION_RESEARCH
REPRODUCTION = EXACT (8/8 cifre)  --  dar regula NU e implementata in depozit, am scris-o eu
SELECTION_CHRONOLOGY: prag logistic = CONFIRMATION_SELECTED (grila de 4 evaluata pe CONF)
                      regula R2      = DISCOVERY_JUSTIFIABLE, NEVERIFICABIL ca oarba
EPISODE_N: 118 R2 = 118 zile unice · CONF 50 = 50 zile unice (42 atinse / 8 neatinse)
lift vs complement +0.302 -> DUPA CONTROLUL PE DISTANTA +0.105 (pozitiv in 4/5 cvintile)
bootstrap pe episoade: P(mid|R2)=0.814 CI [0.746,0.881] · lift CI [+0.130,+0.258]
temporal: 5/5 blocuri pozitive, medie +0.193, t=8.53
2022: CI [0.609,0.957] CONTINE baza 0.685 -> nu sustine independent
sesiuni: LONDON +0.143 · OVERLAP +0.297 · interactiune CI contine zero -> GENERAL_SESSION_SIGNAL
conjunctia adauga: close-below singur +0.018 · bearish singur -0.095 · ambele +0.193
frontiera (endpoint comun): R2 0.814 @ 21.6p lag1  vs  S2 0.829 @ 10.3p lag4  vs  S4 0.946 @ -4.8p lag6
   -> LATENESS_MATERIALLY_RESOLVED (2,1x distanta, 3 bare mai devreme)
test pereche +0.0085 (CI contine 0) -> valoarea e SELECTIE, nu TIMING
defect: prior_attacks contaminat de barele Asia -> analiza 'first vs repeat' e VACUA (0/329 'first')
```

*Niciun candidat de strategie creat. Nicio proiectare de execuție, niciun stop, nicio țintă, niciun RR.
Fără CALIB, V1, 2025+ sau holdout final. Fără promovare, fără AI Trader, fără broker, fără live.*
