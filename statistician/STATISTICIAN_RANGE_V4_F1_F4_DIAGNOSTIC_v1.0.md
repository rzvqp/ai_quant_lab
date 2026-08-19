# DIAGNOSTIC F1 + F4 ȘI PACHET DELTA

**Divizia Statistician · mandat 3.107 · 2026-08-20**

```
RANGE_V4_F1_INPUT_CONTRACT_DELTA_READY_FOR_RED_TEAM_STATIC_REVIEW
INTERNAL_SEMANTIC_CHANGE_NOT_JUSTIFIED
self_declared_pass = false · INDEPENDENT_SEMANTIC_BLIND = FALSE
BLIND_PASS_NOT_PERMITTED · VALIDATION_WEIGHT = ZERO
```

Pachet executabil: `ai_quant_lab-alpha-automation`, `alpha-automation-v1`, `f1_input_contract/`.
Amprentă `662b3bcad029cb815977c76036172098fbb18a48dd60c61fc18e4e531aa6decb`.

Toate cele 15 commituri citate există; `local = remote` pe cele patru oglinzi, în cele trei repo-uri.
Predicțiile înghețate re-hashate independent: `1754c86d…`, identic cu `46a9576`.

---

## 1 — F1: DIAGNOSTIC

Reprodus exact din corpusul canonic, fără a atinge runnerul: **13 din 13.824**.

| măsură | rezultat |
|---|---|
| bare afectate | **13 / 13.824** (0,094 ‰) |
| câmp | **`close` 13 · `open` 0** |
| direcție | peste `high` **9** · sub `low` **4** |
| magnitudine | **o singură valoare distinctă: 0,0005 USD** |
| ferestre atinse | **6 din 48** |
| pe lungime | 96: 1 · 288: 6 · 480: 6 |
| proveniență | corpusul canonic, nu eroare de extracție (reproduse din loaderul verificat) |

**Rafinare față de RT-RANGE-0010:** raportul descrie „close **sau** open"; măsurat, **toate 13 sunt pe
`close`, niciuna pe `open`**. `OPEN_OUTSIDE_HIGH_LOW` nu e declanșat de acest corpus.

### 1.1 Auditul tick-ului — `min_tick = 0,01` este deja normativ

Confirmat independent, nu acceptat pe cuvânt: `tick_size = 0.01` pentru XAUUSD e declarat în
`SymbolMeta` pe **patru** subsisteme AI Trader (`decision_comparison`, `decision_intelligence`,
`decision_intelligence_v2`, `edge_intelligence`) și a fost **ratificat de Red Team** în
`RT-AUDIT-MEAS-0001`, care a și corectat acolo o valoare greșită de 0,1. **Nu e o constantă introdusă
pentru F1.**

**Contradicție semnalată:** aceleași `SymbolMeta` declară `price_precision = 2`, dar corpusul M15 real
conține valori cu **până la 4 zecimale** (open/close: 31.560 valori la 4 zecimale; high/low: ~21.000).
Specificația de instrument (execuție) și precizia feedului (date) **nu sunt de acord**. Nu o rezolv
aici — o semnalez, fiindcă atinge alt domeniu decât RANGE.

**Corecție a unei cifre proprii publicate.** În `BARS_SHA256_SPEC.md` (`dc1d9ed`) am scris „un tick
XAUUSD este 0,001". **Greșit** — tickul normativ e 0,01. Concluzia de acolo nu se schimbă (devine chiar
mai tare: marjă de 10.000 de unități, nu 1.000), dar cifra era greșită și e corectată explicit, nu
tăcut. **A 14-a eroare proprie într-o cifră publicată.**

### 1.2 Regula de toleranță — comparație explicită între cele două candidate

| regulă | derivare | acceptă | verdict |
|---|---|---|---|
| **A: `min_tick / 2` = 0,005** | din tickul normativ ratificat | **13/13**, marjă 4,5·10⁻³ | **RECOMANDATĂ** |
| B: `10⁻³ / 2` = 0,0005 | jumătate de unitate în ultima poziție a câmpului cu precizia cea mai grosieră | **7/13** | **RESPINSĂ** |

**Motivul respingerii lui B este empiric, nu de gust.** Cele 13 abateri, în `float64`, sunt
`0,0004999999998744897` (×7) și `0,0005000000001018634` (×6). O toleranță fixată **exact** la
magnitudinea nominală a artefactului **respinge 6 din barele din care a fost derivată**. O regulă care
nu-și acceptă propriile date nu e mai strictă — e nefolosibilă.

**Garanția de siguranță a lui A:** `0,005 < 0,01 = 1 tick`. O abatere de **un tick întreg nu poate fi
tolerată niciodată**, deci toleranța nu poate masca o eroare reală de date la nivel de tick.

### 1.3 Contractul de input

`ohlc_input_contract_v1`. Ordine fail-closed: câmp lipsă → non-numeric → non-finit → `high >= low` →
`open`/`close` față de `[low − ε, high + ε]`.

★ **Comparația se face valoare-față-de-frontieră-deplasată** (`v <= high + ε`), **nu** diferență-față-de-
epsilon (`v − high <= ε`). Nu sunt echivalente în `float64`: o valoare construită exact ca `high + ε`
produce o diferență care depășește `ε` cu câțiva ULP, deci forma pe diferență ar respinge exact cazul
de egalitate pe care contractul îl declară **admis**. Prima mea implementare a folosit forma pe
diferență și **două teste au căzut** — corect. Forma normativă e cea din §7 al mandatului, și e exactă
prin construcție, fără nicio marjă inventată.

Eveniment de calitate: **`INPUT_OHLC_SUBTICK_TOLERATED`** — în afara celor 29 de reason codes
semantice (verificat mecanic: intersecție vidă, `|REASONS| = 29`). Un singur eveniment per bară; la
abateri pe ambele câmpuri se raportează cea cu magnitudinea mai mare, determinist. Contractul e
**fără stare**, deci determinismul, invarianța la fragmentare și restartul sunt proprietăți
structurale, nu comportamente testate accidental.

**Identitate (§8):** se schimbă numai validatorul de input, versiunea contractului de input, testele
și manifestul runnerului. Detectorul, `config_id`, setul semantic, formulele, frontierele, ATR,
stările, predicțiile, scorerul și etichetele — **neatinse**. Versiunea de runner care supersedează
`82f27c0` trebuie să poarte identitate nouă, fiindcă **contractul de input se schimbă**.

**Teste: 28, toate trec**, inclusiv cel decisiv — cele **13 bare reale acceptate cu valorile
byte-neschimbate** (testul verifică explicit că lista de bare e identică înainte și după validare).
`mypy --strict` curat.

> **Limită declarată:** nu pot demonstra aici că predicțiile produse prin CLI după patch sunt
> byte-identice cu `46a9576`, fiindcă §20 îmi interzice să modific runnerul, iar CLI-ul patchuit nu
> există. Ce demonstrez este condiția care o face necesară: contractul **nu modifică nicio valoare
> OHLC**, deci detectorul primește exact aceiași bytes. Testul CLI rămâne obligatoriu pentru VE.

---

## 2 — F4: DIAGNOSTIC

### 2.1 Cele 12 cazuri, fără goluri

Din predicțiile înghețate, cu ID-uri abstracte și indici relativi.

| # | caz | părinte MACRO viu | părinte CONFIRMAT | candidat INTERNAL | cauză principală |
|---|---|---|---|---|---|
| 1 | `BLIND-009[110,200)` | da | da | da | **7/8 touch insuficient** (`ESTABLISHING_FEW_SWINGS`, 39 bare) |
| 2 | `BLIND-009[270,288)` | da | **nu** | rest | **1 părinte indisponibil** |
| 3 | `BLIND-012[0,52)` | da | da | **niciunul** | **5 candidat negenerat** |
| 4 | `BLIND-012[88,96)` | da | **nu** | niciunul | **1 părinte indisponibil** |
| 5 | `BLIND-019[48,180)` | da | **nu** | niciunul | **1 părinte indisponibil** |
| 6 | `BLIND-019[468,480)` | da | **nu** | niciunul | **1 părinte indisponibil** |
| 7 | `BLIND-020[60,82)` | da | da | **niciunul** | **5 candidat negenerat** |
| 8 | `BLIND-022[155,190)` | da | da | da | **TRUE POSITIVE** (IoU 0,415) |
| 9 | `BLIND-034[360,410)` | da | da | **niciunul** | **5 candidat negenerat** |
| 10 | `BLIND-034[410,480)` | da | da | **niciunul** | **5 candidat negenerat** |
| 11 | `BLIND-037[24,50)` | da | **nu** | niciunul | **1 părinte indisponibil** |
| 12 | `BLIND-037[70,96)` | da | **nu** | niciunul | **1 părinte indisponibil** |

```
cauza 1  părinte MACRO neconfirmat în span      6 / 12   (50%)   ← poarta DOMINANTĂ
cauza 5  candidat INTERNAL negenerat            4 / 12   (33%)
cauza 7/8 touch insuficient                     1 / 12
TP                                              1 / 12
                                               ------
                                               12 / 12
```

### 2.2 Funnelul INTERNAL, global

```
13.824 bare
 └─ 12.736 (92,1%) fără niciun candidat viu        BETWEEN_EPISODES
 └─    112 candidați creați
        └─ 96 uciși înainte de confirmare         ZONES_DEGENERATE 73 · ZONES_INVERTED 23
        └─ 25 confirmați                          OK_RANGE_INTERNAL
              └─ 1 potrivit cu GT
TOO_SHORT_INTERNAL: 31 bare din 13.824
```

★ **`d_internal = 12` NU este cauza.** Mandatul a cerut să nu presupun asta; măsurat, poarta de durată
atinge 31 de bare din 13.824 și **niciunul** dintre cele 12 cazuri nu eșuează pe ea.

### 2.3 O ipoteză proprie, respinsă înainte de publicare

Am presupus că `w_atr` fiind partajat între niveluri, segmentele INTERNAL sunt structural prea înguste
și cad pe degenerare. **Măsurat: fals.** Lățimea span-ului raportată la `ATR14` — INTERNAL mediană
**5,48**, MACRO **5,62**; **0 din 12** sub pragul de degenerare 1,60. Segmentele etichetate INTERNAL
sunt la fel de late ca cele MACRO. Cei 96 de candidați uciși sunt candidați **spurioși**, nu segmentele
etichetate. Ipoteza era plauzibilă și greșită; o consemnez fiindcă era la un pas de a fi publicată ca
mecanism.

### 2.4 Detector sau scorer — tranșat (§12)

Am recalculat potrivirea INTERNAL **independent, fără să import scorerul**, direct din predicțiile
înghețate și din etichete:

```
prag IoU 0,5 → 0/12      prag 0,3 → 1/12      prag 0,2 → 1/12      prag 0,1 → 1/12
IoU maxim per caz: 11 din 12 au EXACT 0,000; singurul nenul e BLIND-022 la 0,415
```

**Reproduc exact `1/12` al scorerului înghețat, iar 11 din 12 cazuri au suprapunere exact zero.**
Nu sunt rateuri la limită și nu e o chestiune de prag. **F4 este pe partea detectorului** —
generarea candidatului și disponibilitatea părintelui — **nu pe scorer, nu pe schema predicției, nu
pe etichete.** Scorerul nu se modifică.

### 2.5 De ce nu justific o schimbare semantică

§15 cere o cauză unică sau clar dominantă. **Nu există.** Cauza dominantă (6/12) este **absența unui
părinte MACRO confirmat** — adică ratarea MACRO propagată în jos. MACRO are recall 0,705, deci 26 din
88 sunt ratate; INTERNAL moștenește acele ratări. **Jumătate din eșecurile INTERNAL nu sunt reparabile
la nivel INTERNAL fără a atinge MACRO, iar §3 interzice asta** — corect, fiindcă MACRO e baza înghețată.

A doua cauză (4/12) e reală și localizată la generarea candidatului, dar **n = 4**. §14 cere
leave-one-out, sensibilitate și bootstrap; cu patru cazuri, orice regulă derivată din ele ar fi
memorare, nu generalizare. Nu raportez robustețe pe care eșantionul nu o susține.

Prin urmare: **`INTERNAL_SEMANTIC_CHANGE_NOT_JUSTIFIED`**. Nu inventez o corecție.

---

## 3 — F5: CONSTATARE NOUĂ (a mea) — neconformitate de unități în detector

`range_semantic_v4_3.py`, calea de generare a candidatului INTERNAL:

```
linia 442   cl.offer(price, cfg.tol_cluster * st.atr_ref)          ← scalat cu ATR
linia 745   abs(price - boundary) <= self._cfg.tol_cluster          ← NEscalat
```

Aceeași constantă, **două unități diferite, în același fișier**. `tol_cluster = 1,60` este un
**multiplu de ATR**, folosit la linia 745 ca distanță absolută de **1,60 USD**. Comentariul de
deasupra afirmă explicit că e „ACEEAȘI toleranță normativă folosită de `Cluster.offer`, nicio valoare
inventată" — **afirmă o identitate pe care codul nu o implementează**.

**Măsurat:** pragul contractual `1,60 × ATR14` are mediana **2,990 USD**, față de **1,600 USD**
implementat; contractual e mai larg pe **87,2%** din bare.

★ **Direcția contează și e contraintuitivă:** filtrul implementat respinge **mai puține** swing-uri
decât cere contractul, deci **nu** e cauza candidaților lipsă — iar **repararea lui ar produce și mai
puțini candidați INTERNAL**, adică recall mai mic. De aceea trebuie decis **pe temei de conformitate,
nu pe recall**. Îl raportez ca defect de conformitate, cu efectul declarat, și nu propun să fie
reparat ca soluție la F4.

E strict pe calea `forming_internal`, deci **MACRO nu e afectat**.

---

## 4 — MATRICE PASS/FAIL

| § | cerință | rezultat |
|---|---|---|
| 1 | commituri verificate, `local=remote` ×4 | **PASS** |
| 2 | stare înghețată nereinterpretată | **PASS** |
| 3 | MACRO nemodificat | **PASS** — nicio propunere nu atinge MACRO |
| 4 | date folosite doar pentru diagnostic | **PASS** — zero lot blind nou |
| 5 | F1 reprodus cu distribuții complete | **PASS** |
| 6 | audit tick + regulă derivată + comparație | **PASS** — A vs B comparate explicit |
| 7 | contract F1 fără ambiguitate | **PASS** |
| 8 | identitate F1 limitată la input | **PASS** |
| 9 | teste F1 pozitive + negative | **PASS** — 28/28 |
| 9 | CLI patched = predicții înghețate | **NEDEMONSTRAT** — §20 interzice modificarea runnerului; condiția necesară (zero modificare OHLC) e demonstrată |
| 10 | tabel 12/12 fără goluri | **PASS** |
| 11 | funnel complet + poartă dominantă | **PASS** |
| 12 | detector vs scorer tranșat | **PASS** — detector; 1/12 reprodus fără scorer |
| 13 | analiza candidaților de corecție | **N/A** — nicio corecție justificată |
| 14 | control overfit | **PASS** — declarat insuficient la n=12/n=4 |
| 15 | condiții pentru schimbare semantică | **NEÎNDEPLINITE** → `INTERNAL_SEMANTIC_CHANGE_NOT_JUSTIFIED` |
| 16 | versionare | **N/A** — fără schimbare semantică, `range-hierarchical-v4.3` rămâne; se versionează doar contractul de input |
| 19 | invarianțe | **PASS** — vezi §5 |
| 21 | verdicte permise | **PASS** |

---

## 5 — INVARIANȚE

Detectorul `f224e7d` **byte-identic** (identitate de blob Git față de `82f27c0`, verificată în
mandatul precedent și neatinsă aici). Runnerul `82f27c0` **nemodificat** — pachetul F1 e un contract
nou, separat, nu un patch aplicat. Cele 29 de reason codes rămân închise; evenimentul de calitate e
**în afara** setului (intersecție vidă, verificată mecanic). `DEPTH_LIMIT_EXCEEDED` activ, două
niveluri, MICRO nereprezentabil, al treilea nivel refuzat, frontiere înghețate, fără lookahead,
ATR cauzal, snapshot fail-closed, determinism și invarianță la fragmentare — toate structurale în
contractul de input, care e **fără stare**.

---

## 6 — DOMENIU

Autorizează **exclusiv** revizuirea statică Red Team a contractului de input F1. Nu autorizează și nu
afirmă nimic despre: PASS semantic, BLIND PASS, rularea detectorului, wheel, Strategy Catalog, Alpha,
AI Trader, LIVE_SHADOW, broker, tranzacții. Rezultatele pe cele 48 de ferestre sunt
`POST_DIAGNOSTIC_CONSTRUCTION_ONLY` cu `VALIDATION_WEIGHT = ZERO`.

*Divizia Statistician · detector NErulat · scorer NErulat · lot blind nou NEatins · `SEALED/OOS_ACCESS = 0`*
