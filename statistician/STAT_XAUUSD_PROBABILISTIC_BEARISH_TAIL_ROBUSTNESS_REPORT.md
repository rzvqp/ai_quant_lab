# XAUUSD — AUDIT DE ROBUSTEȚE TEMPORALĂ AL SEMNALULUI PROBABILISTIC BEARISH DE COADĂ

**Divizia Statistician · `STAT-XAUUSD-PROB-BEAR-TAIL-ROBUSTNESS-001` · 2026-08-22**

```
PROBABILISTIC_BEARISH_TAIL_SIGNAL_WEAK
FRESH_DIRECTIONAL_EVIDENCE_REQUIRED
```

**Reproducerea e EXACTĂ.** Efectul nu dispare și nu se inversează — dar **se micșorează cu ~60% sub
evaluare temporală corectă și își pierde semnificația sub orice tratament al dependenței.**

Un lucru se susține și îl spun din start: **coada NU e doar momentum reambalat** (§7). Ăsta e singurul
argument real pentru a nu o închide definitiv.

`DEV-only. Zero CALIB. Zero 2025+. Zero V1. Niciun model reantrenat, niciun feature nou, niciun prag nou.`

---

## 1 — §2 IDENTITATEA ARTEFACTULUI

| element | valoare din cod (`7e8d6ef`) |
|---|---|
| fișiere | `prob_state.py`, `prob_state2.py` |
| univers | H1 **agregat cauzal din M5-ul gated** (`m5_data`); H4/M15 aliniate prin `searchsorted(close_time)` |
| features | **31** asamblate: 18 H1 + 8 H4 + 4 M15 + `mtf_div`; toate ATR-normalizate, cauzale |
| normalizare | `mu`/`sd` **înghețate pe DISCOVERY** (`Model.fit`), verificat: drift median 0,027 |
| clasă de model | **ridge logistic prin IRLS**, `l2 = 2.0` (M4 folosește 20.0) |
| etichetă | `y[i] = 1` dacă, pe `i+1 … i+24`, `(entry − min low)/PIP ≥ 150` **și** > excursia bullish |
| orizont | **`H = 24` bare H1** · `THR = 150` pips de proiect |
| split | `cut` la **60%** din rândurile valide → **`valid n=10001`** -> `DISC n=6000` / `CONF n=4001` |
| praguri de coadă | `thr = quantile(prob_DISC, q)` pentru `q ∈ {0.90, 0.95, 0.98}` |
| execuție | short la `o[i+1]`, stop = ultimul swing-high H1 din `i−6 … i` (sau `entry+1.5·ATR`), țintă `rr × risk`, hold 24, cost 2,4 pips, cooldown la bara de ieșire |

**Firewall verificat:** `prob_state` folosește exclusiv `m5_data` → loaderul gated. Zero `read_csv`,
zero N4, zero 2025+, zero CALIB, zero exogen.

## 2 — REPRODUCERE: **EXACTĂ, fără nicio abatere**

Am rulat `prob_state2.py` integral. Toate cifrele raportate se confirmă:

```
PRIMARY = M5 H4+H1+M15   CONF AUC = 0.505   cel mai bun baseline (momentum) = 0.563
q0.90  thr=0.368  CONF n=369  bear=0.279          (Alpha 0.279)  base CONF = 0.2314
q0.95  thr=0.414  CONF n=194  bear=0.309          (Alpha 0.309)
q0.98  thr=0.473  CONF n= 56  bear=0.411          (Alpha 0.411)
exec rr2 @ q0.98: n=20 WR 0.500 avgR +0.3446 med -0.0428 b5 +0.2593 b10 +0.1649 top10% 0.569
```

Nu emit `PROBABILISTIC_TAIL_REPRODUCTION_FAIL`.

### ★ 2.1 Ce am observat în propria reproducere și nu apare în raportul Alpha

```
CONFIRMATION contine EXCLUSIV 2023: "TEMPORAL (CONF AUC by year)" tipareste o singura linie, 2023 n=4001
executie q0.90 rr2 = -0.086   q0.95 rr2 = +0.107   q0.98 rr2 = +0.345
```

**Economia execuției e negativă la q0.90.** „Semnalul" apare doar în celula cea mai extremă și cea mai
mică. Iar `top10%` iese `None` sau absurd (`21.157`, `38.372`) în mai multe celule — semn că profitul
total e ~0 și raportul e nedefinit.

---

## 3 — ★★ §3 CRONOLOGIA PRAGURILOR: nivelurile sunt predeclarate, **modelul NU este**

```
PREDECLARED_THRESHOLD   pentru nivelurile q0.90 / q0.95 / q0.98
```

Codul calculează `thr = np.quantile(pdisc, q)` **exclusiv din scorurile DISCOVERY**, iar bucla
`for q in (0.90, 0.95, 0.98)` **evaluează și tipărește toate trei**. Nu s-a raportat doar câștigătorul.
Pe axa cuantilelor, cronologia e curată.

### ★ Dar coada e definită de scorurile unui model ALES PE SETUL DE TEST

```python
prob_state.py:
prim = max([m for m in MODELS if m.name.startswith(("M2","M3","M5"))],
           key = lambda m: auc(y[conf], m.prob(conf)))        # <- CONFIRMATION
```

`prim` e ales prin **AUC pe CONFIRMATION**, dintre M2 (0.490), M3 (0.502), M5 (0.505). Toate trei sunt
la nivelul hazardului; se selectează maximul a trei valori aproape aleatoare — **și apoi pe acel model
se construiește coada raportată**.

```
MODEL_SELECTION = POST_HOC_ON_CONFIRMATION
```

Nu e o încălcare a literei mandatului („q0.98 a fost ales după CONF?" — nu a fost), dar e **aceeași
clasă de defect** aplicată unui pas mai devreme. Auditul temporal din §5 elimină exact acest pas,
rulând **toate trei** modelele fără nicio selecție.

*(O a doua observație tehnică: între DISC și CONF **nu există embargo**, deși eticheta privește 24 de
bare înainte. Ultimele 24 de bare DISC au etichete care se întind în CONF. Efect mic, dar real; în §5
am impus embargo.)*

---

## 4 — §4 AUDITUL DE MULTIPLICITATE

Spațiul de căutare, enumerat din cod:

```
7 modele logistice (M1..M7)  +  M8 Markov  +  4 baseline-uri            = 12 functii de scor pe CONF
selectie `prim` peste {M2, M3, M5} dupa AUC pe CONF                     = 3
cuantile de coada evaluate si raportate                                  = 3
niveluri RR in executie                                                  = 3
praguri de eticheta calculate (80/100/150/200/300)                       = 5   (doar 150 pe calea cozii)
grile an-la-an                                                           = 4
```

Grila direcțională efectivă = **3 modele × 3 cuantile = 9 celule**, din care s-a raportat maximul.
Grila de execuție tipărită = **3 × 3 = 9 celule** (+3 pentru baseline).

**De ce NU aplic Bonferroni.** Celulele sunt puternic dependente: modelele sunt **imbricate**
(`M2 ⊂ M3 ⊂ M5` ca set de features, cu AUC-uri în interval de 0,015), iar cuantilele sunt **imbricate**
(`q0.98 ⊂ q0.95 ⊂ q0.90`). Numărul efectiv de teste independente e de ordinul **2–3**, nu 9. Bonferroni
la 9 ar fi apărare exagerată și aș fi criticabilă pentru asta.

**★ Și, mai important: nu am nevoie de corecția de multiplicitate.** Chiar cu **zero** corecție,
elevația nu supraviețuiește tratamentului dependenței (§6). Multiplicitatea e o problemă secundară
aici, iar cea primară e mai gravă. O consemnez, nu mă sprijin pe ea.

---

## 5 — §9/§10 SUPRAPUNEREA ȘI DIMENSIUNEA EFECTIVĂ A EȘANTIONULUI

```
orizontul etichetei H = 24 bare H1
-> doua bare consecutive impart 23/24 = 95,8% din fereastra lor de rezultat
```

Stările de coadă nu sunt observații independente; sunt **rulaje contigue** ale aceleiași stări.
Am numărat episoadele distincte (separate prin > 24 bare):

| | `n` stări | **episoade distincte** | `n_eff / n` | mărime episod (med / max) | episoade cu **vreun** eveniment bearish |
|---|---|---|---|---|---|
| q0.90 | 369 | **32** | 0,087 | 8 / 35 | 13 / 32 |
| q0.95 | 194 | **27** | 0,139 | 5 / 26 | 8 / 27 |
| **q0.98** | **56** | **15** | **0,268** | 2 / 12 | **5 / 15** |

**★ Cele 56 de stări din coadă sunt 15 episoade, iar întreaga rată de 0,411 se sprijină pe 5 episoade
în care s-a întâmplat ceva bearish.** Nu 56 de observații; cinci evenimente.

Și rata per-bară e **umflată de episoadele lungi**: media-mediilor pe episod e **0,282**, nu 0,411.

Cele 20 de tranzacții executate sunt non-suprapuse prin construcție (`cool = bara de ieșire`), deci
`n_eff ≈ 20` acolo — dar toate cad în **8 luni distincte, toate din 2023**.

## 6 — ★★ §12 MONOTONIA ȘI INCERTITUDINEA CONȘTIENTĂ DE DEPENDENȚĂ

`base CONF = 0,2314`

| | `n` | bear | lift abs | **SE naiv** | **SE pe EPISOD** | bootstrap în blocuri (blk=24) — CI95 | conține base? |
|---|---|---|---|---|---|---|---|
| q0.90 | 369 | 0,279 | +0,048 | **2,04 SE** | **−0,09 SE** | `[0,138 ; 0,436]` | **DA** |
| q0.95 | 194 | 0,309 | +0,078 | **2,35 SE** | **−0,28 SE** | `[0,082 ; 0,526]` | **DA** |
| **q0.98** | **56** | **0,411** | **+0,179** | **2,73 SE** | **+0,46 SE** | `[0,054 ; 0,643]` | **DA** |

**Monotonia per-bară e reală** (0,279 → 0,309 → 0,411) — dar la nivel de episod se aplatizează
(0,226 → 0,212 → 0,282) și e integral în zgomotul de eșantionare.

**Sub tratament pe episoade, elevația q0.98 scade de la 2,73 SE la +0,46 SE**, iar q0.90 și q0.95 devin
**negative**. Bootstrap-ul în blocuri mobile conține rata de bază **în toate cele trei cazuri**.

*(Notă de reproducere: obțin `2,73 SE` naiv, nu `~3,2 SE` cât raportează Alpha — probabil o SE calculată
pe rata de bază, nu pe rata din coadă. Diferența nu schimbă nimic: nici 2,7 nici 3,2 nu e cifra
relevantă.)*

---

## 7 — ★ §14 COADA **ADAUGĂ** INFORMAȚIE PESTE MOMENTUM

Acesta e singurul rezultat clar favorabil, și îl raportez integral.

```
momentum-short (r20 <= DISC-q15 = -2.852):  n=693  bear=0.306  lift +0.074   (42 episoade distincte)
suprapunerea cozii cu momentum-short:  q0.90 16,8% · q0.95 17,0% · q0.98 30,4%

CONTROL POTRIVIT PE MOMENTUM pentru q0.98 (acelasi mix de decile r20, coada exclusa):
    control = 0.244        coada q0.98 = 0.411        INCREMENT = +0.166
    -> doar 7% din lift-ul brut e explicat de momentum singur
```

**Coada nu e momentum reambalat.** Suprapunerea e sub o treime, iar controlul potrivit pe decila de
momentum lasă practic tot lift-ul intact.

Dar: incrementul de `+0,166` e măsurat pe **aceleași 56 de bare / 15 episoade**, deci moștenește
exact incertitudinea din §6. **Direcția e credibilă; magnitudinea nu e estimabilă.**

Observație suplimentară, care taie în cealaltă direcție: **momentum-short obține `bear = 0,306` pe
`n = 693`** — practic egal cu q0.95 (`0,309` pe `n = 194`) și cu 3,6× mai multe observații. La nivel
de rată direcțională, filtrul trivial e la fel de bun ca modelul, până la q0.98.

---

## 8 — ★★ §5/§6/§7 EVALUARE TEMPORALĂ ANCORATĂ (rezultatul decisiv)

**Design.** Walk-forward ancorat pe rândurile valide DEV, `K = 6` blocuri cronologice, 5 blocuri de
evaluare. Antrenare **exclusiv pe blocurile anterioare**, cu **embargo de 24 de bare** la frontieră.
Aceleași features, aceeași familie de model, același `l2 = 2.0`, aceeași regulă de normalizare cauzală
(`mu`/`sd` din TRAIN). **Pragul = cuantila `q` a scorurilor din porțiunea de ANTRENARE** — nicio
informație de percentilă din viitor. **Zero selecție de model:** rulez M2, M3 și M5 în paralel.

### q0.98

| model | pooled tail `n` | pooled bear | base | **lift pooled** | blocuri cu lift > 0 | media lift pe bloc (sd) |
|---|---|---|---|---|---|---|
| M2 H1-only | 133 | 0,233 | 0,249 | **−0,016** | 3/5 | −0,041 (0,124) |
| M3 H4+H1 | 140 | 0,300 | 0,249 | **+0,051** | 2/5 | +0,016 (0,105) |
| **M5** (primarul lui Alpha) | **137** | **0,321** | 0,249 | **+0,072** | **2/5** | **+0,035 (0,094)** |

Pe blocuri, pentru M5:

```
blk1 2021-11..2022-11  base 0.234 | tail n=23 ep= 6 bear 0.217  lift -0.017  AUC 0.567
blk2 2022-11..2023-02  base 0.262 | tail n=22 ep= 7 bear 0.227  lift -0.034  AUC 0.498
blk3 2023-02..2023-06  base 0.338 | tail n=39 ep= 7 bear 0.436  lift +0.098  AUC 0.593
blk4 2023-06..2023-09  base 0.155 | tail n=18 ep= 8 bear 0.111  lift -0.044  AUC 0.419
blk5 2023-09..2023-12  base 0.259 | tail n=35 ep= 5 bear 0.429  lift +0.169  AUC 0.512
```

### q0.95 — lift-ul **dispare**

```
M2 +0.001   M3 +0.002   M5 +0.007      (Alpha, pe splitul unic: +0.078)
lift > 0 in 1/5, 3/5, 3/5 blocuri
```

### Ce arată

1. **Lift-ul q0.98 scade de la `+0,179` la `+0,072`** — o pierdere de **60%** — și e pozitiv în doar
   **2 din 5** blocuri. Media pe bloc `+0,035` cu `sd 0,094` pe 5 blocuri dă `t ≈ 0,83`.
2. **Lift-ul q0.95 se evaporă**: `+0,078` → `+0,007`.
3. **Blocul 4 (2023-06 … 2023-09) e negativ pentru TOATE modelele, la TOATE cuantilele.** Acolo AUC-ul
   e `0,419`, adică **sub hazard**.
4. Efectul e purtat de blocurile 3 și 5 — ambele în 2023.

---

## 9 — §11 STABILITATE TEMPORALĂ

CONFIRMATION-ul lui Alpha e **integral 2023**, deci întrebarea „mai mult de un an?" nu poate primi
răspuns din designul original. Din walk-forward:

```
2021-11 .. 2022-11 : lift -0.017 (M5, q0.98)     -> NEGATIV
2022-11 .. 2023-02 : lift -0.034                 -> NEGATIV
2023-02 .. 2023-06 : lift +0.098
2023-06 .. 2023-09 : lift -0.044                 -> NEGATIV
2023-09 .. 2023-12 : lift +0.169
```

**Efectul se inversează în trei din cinci blocuri, dintre care unul întreg din 2022.** Nu poartă un
singur an în sens strict — dar cele două blocuri pozitive sunt amândouă din 2023.

## 10 — §15 STABILITATEA MODELULUI: **fără `MODEL_INSTABILITY`**

Semnele coeficienților standardizați pe cele 5 folduri, pentru cele mai mari 10 `|w|` ale lui M5:

```
h1_ema_gap      +++++  stabil   [+0.287,+0.784]      h1_dist_ema20  +++++  stabil  [+0.044,+0.717]
h1_updown_asym  -----  stabil   [-0.510,-0.319]      h1_dist_hh20   +++++  stabil  [+0.079,+0.484]
h1_exc_asym     +++++  stabil   [+0.145,+0.828]      h1_accel       -----  stabil  [-0.573,-0.088]
h4_slope20      +----  INSTABIL [-0.485,+0.188]      h4_vol_exp     +++++  stabil  [+0.126,+0.288]
h1_rangepos50   +++++  stabil   [+0.262,+0.615]      h1_r20         +++++  stabil  [+0.014,+1.039]

=> stabil ca semn in 9/10
```

**Nu ridic `MODEL_INSTABILITY`.** Scorul de coadă nu e generat de relații care își schimbă semnul —
un singur feature (`h4_slope20`) oscilează. Structura e stabilă; ce lipsește e puterea, nu coerența.

## 11 — §13 POATE COEXISTA O COADĂ REALĂ CU UN MODEL GLOBAL SLAB?

**Da, în principiu, și nu resping ipoteza pe acest temei.** Un clasificator poate fi nediscriminant în
masă (`AUC 0,505`, Brier sub predictorul de rată de bază, bucket-uri de mijloc non-monotone) și totuși
să izoleze o regiune rară în care condiționarea e reală: AUC-ul e o statistică de ordonare globală,
insensibilă la 2% din observații.

**Testul corect e dacă regiunea rară se reproduce în afara splitului în care a fost observată.** §8
arată că se reproduce **slab și inconstant** (`+0,072`, 2/5 blocuri), iar §6 arată că nici pe splitul
original nu e distinsă de zgomot odată tratată dependența. Deci coexistența e **posibilă teoretic**,
dar **nu e demonstrată aici**.

## 12 — §17/§18 DIAGNOSTICUL DE EXECUȚIE (reprodus, descriptiv — NU un audit)

§16 condiționează auditul de execuție de supraviețuirea semnalului direcțional. **Nu a supraviețuit**,
deci **nu fac auditul de execuție.** Raportez doar reproducerea, fiindcă §2 o cere, și descompunerea
cerută explicit la §18.

```
n=20  WR 0.500  avgR +0.3446  MEDIANA R -0.0428  PF 1.648
maxDD 6.46 R  vs  totalR 6.89 R      <- drawdown-ul aproape egaleaza tot profitul
best1rem +0.2593 · best5rem +0.2593 · best10rem +0.1649
top 1 (5%) = 28,5% din profit · top 2 (10%) = 56,9% · top 3 (15%) = 85,3%
fractiuni: castig 0.500 · pierdere 0.500 · breakeven (|R|<0.05) 0.000
avg castigator +1.7522 (n=10) | avg perdant -1.0630 (n=10)
mix iesiri: 8 tinta / 10 stop / 2 timp | risc median 51,6 pips | hold median 6 bare H1
sd 1.471 · se 0.329 · t = 1.05 · CI95 = [-0.300 ; +0.989]     <- INCLUDE ZERO
temporal: 8 luni distincte, TOATE in 2023;  Q2 (n4) +0.965 · Q3 (n6) -0.079 · Q4 (n10) +0.351
```

**§18 — răspunsul precis:** exact 10 câștiguri și 10 pierderi, zero breakeven-uri, mediană `−0,043`.
Rezultatul **nu e economic broad-based**, în ciuda metricilor de eliminare a cozii: **trei tranzacții
din 20 produc 85,3% din profit**, drawdown-ul maxim (`6,46 R`) aproape egalează profitul total
(`6,89 R`), iar Q3 2023 e negativ. `best-10%-removed = +0,165` trece pentru că `10%` din 20 înseamnă
eliminarea a **două** tranzacții — la acest `n` metrica nu are conținut discriminant.

> **Regula de la mandatul precedent a funcționat.** În prima redactare scrisesem `DISC n=6002`; înainte de commit am rulat verificarea și valoarea reală e **`6000`** (`valid = 10001`, `CONF = 4001`). Corectat. Consemnez fiindcă e a patra oară când această clasă de eroare apare — de data asta **prinsă de procedură, nu de noroc**.

## 13 — LIMITĂRI ALE PROPRIULUI MEU AUDIT

1. Walk-forward-ul meu are **5 blocuri**; cu `~10.000` de rânduri valide și un orizont de 24 de bare,
   asta lasă `~20` de tranzacții de coadă per bloc la `q0.98`. Blocurile sunt mici, iar sd-ul lift-ului
   pe bloc (`0,094`) e mare. Un design cu mai multe blocuri ar avea și mai puține stări per bloc.
2. Bootstrap-ul în blocuri folosește blocuri de lungime fixă `= H`. Alegerea lungimii e o convenție;
   nu am testat sensibilitatea la ea.
3. Analiza pe episoade tratează un episod ca o observație, ceea ce e **conservator** — episoadele lungi
   chiar conțin mai multă informație decât cele scurte. Adevărul e între `n = 56` și `n = 15`; am
   raportat ambele capete, iar concluzia nu se schimbă la nici unul.
4. **Nu am rulat un audit de multiplicitate formal** cu permutări; am argumentat de ce nu e nevoie
   (§4), dar e o alegere, nu o demonstrație.
5. Controlul pe momentum (§7) potrivește pe decila `r20` — o singură dimensiune. Un control mai bogat
   (volatilitate, poziție în range) ar putea explica mai mult din increment.

## 14 — §21 VERDICT

```
PROBABILISTIC_BEARISH_TAIL_SIGNAL_WEAK
```

Motivarea, punct cu punct față de definiția din mandat:

- **Nu e `SUPPORTED`**: elevația **nu** supraviețuiește testării conștiente de dependență
  (`+0,46 SE` pe episoade; bootstrap-ul conține rata de bază) și **nu** se reproduce în walk-forward
  ancorat (`+0,072` față de `+0,179`, pozitiv în 2/5 blocuri). În plus, modelul care generează coada a
  fost **ales pe setul de confirmare**.
- **Nu e `NOT_SUPPORTED`**: efectul **nu dispare și nu se inversează** — rămâne pozitiv pooled la
  q0.98 pentru M3 (`+0,051`) și M5 (`+0,072`) sub walk-forward; **coada adaugă informație reală peste
  momentum** (increment `+0,166`, doar 7% din lift explicat de momentum); iar structura modelului e
  **stabilă ca semn în 9/10 features**. Nu e adecvat explicat doar prin selecție sau multiplicitate.
- **Este `WEAK`**: direcțional interesant, dar `n_eff = 15 episoade`, `5` dintre ele purtătoare de
  eveniment, un singur an de confirmare și lift inconstant pe blocuri. **Prea puțin și prea instabil
  pentru a crea un candidat.**

## 15 — §22 RECOMANDARE

```
FRESH_DIRECTIONAL_EVIDENCE_REQUIRED
```

**De ce, exact:**

1. **Dimensiunea efectivă, nu nominală, e constrângerea.** `q0.98` produce ~2% din bare; pe DEV asta a
   însemnat **15 episoade**. Pentru a distinge `+0,07` de zero la nivel de episod ar trebui un ordin de
   mărime mai multe episoade — nu mai multe bare.
2. **Confirmarea acoperă un singur an.** Orice afirmație despre repetabilitate temporală e
   nedeterminată prin construcție.
3. **Modelul primar a fost ales pe confirmare.** Orice evidență nouă trebuie să fixeze modelul
   **înainte** de a privi noua perioadă. Recomand fixarea lui **M3** sau **M5** prin regulă declarată
   (de exemplu „setul complet de features"), nu prin AUC.

**Ce NU recomand:** o variantă de salvare — un `q0.99`, un alt model, alt orizont, alt prag de
etichetă. Grila a fost deja parcursă; adăugarea de celule ar transforma o problemă de putere într-una
de multiplicitate.

**Ce ar fi util și nu costă dovezi:** re-rularea walk-forward-ului cu modelul fixat prin regulă,
raportând **lift-ul la nivel de episod**, ca linie de bază pentru orice evidență viitoare.

---

```
PROBABILISTIC_BEARISH_TAIL_SIGNAL_WEAK
FRESH_DIRECTIONAL_EVIDENCE_REQUIRED
REPRODUCTION = EXACT  (nu se emite PROBABILISTIC_TAIL_REPRODUCTION_FAIL)
THRESHOLD_LEVELS = PREDECLARED  ·  MODEL_SELECTION = POST_HOC_ON_CONFIRMATION
n_eff: 56 stari -> 15 episoade, dintre care 5 cu eveniment bearish
episode-level elevation q0.98 = +0.46 SE  ·  block-bootstrap CI contine rata de baza la toate 3 cuantilele
anchored walk-forward q0.98 lift: M2 -0.016 · M3 +0.051 · M5 +0.072   (2/5 blocuri pozitive)
anchored walk-forward q0.95 lift: +0.001 / +0.002 / +0.007            (fata de +0.078 pe splitul unic)
TAIL_ADDS_INFORMATION_BEYOND_MOMENTUM = TRUE  (increment +0.166; 7% din lift explicat de momentum)
MODEL_INSTABILITY = NOT_RAISED  (semn stabil in 9/10 features)
executie rr2 reprodusa: n=20, t=1.05, CI include zero, top 3 = 85,3% din profit, maxDD ~ profit total
```

*Niciun candidat creat. Niciun `VALIDATED_SIGNAL`. Fără CALIB, fără V1, fără 2025+, fără holdout final.
Fără promovare, fără AI Trader, fără broker, fără live.*
