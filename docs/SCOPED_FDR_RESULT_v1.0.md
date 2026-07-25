# SCOPED GLOBAL-FDR — RESULT (validated ATR-stop regime)

**Document ID:** STAT-SCOPED-FDR-RESULT-v1.0 · **Autor:** Statistician (Research Lab) · **Data:** 2026-07-25
**Pre-înregistrare:** `docs/SCOPED_FDR_PREREGISTRATION_v1.0.md` (comisă `ea36005`, ÎNAINTE de orice p).
**Artefacte:** `results/matched_null_validation/scoped_fdr_{summary.json,research.parquet,seeds.json,run.log}`.
**Sferă respectată:** holdout SEALED (niciodată încărcat); univers neschimbat după rezultate; nicio rulare pe familii cu stop structural; niciun prag ajustat; nicio re-rulare pentru alt număr.

---

## 1. HEADLINE — NU zero. UN supraviețuitor de research-FDR.

Contrar așteptării (zero), FDR-ul pe subsetul validat a produs **exact 1 supraviețuitor** la BH (α=0.05, m=412). Îl raportez **ca atare**, fără înmuiere și fără supraevaluare.

| | |
|---|---|
| Univers testat (m) | **412** (ATR-stop 1.5×ATR, n≥25) |
| Prag BH rang-1 (α/m) | **1.214e-4** |
| **Supraviețuitor BH** | **`ce76669a3b2a`** — S18 |
| Definiție ipoteză | **hour=13 UTC, side=down (short), stop=1.5×ATR, exit=time** |
| p research (MC-3 confirmat) | **6.80e-5**, CI95 [5.28e-5, 8.51e-5] — **întreg sub prag → NU UNRESOLVED** |
| p research (MC-1 → MC-2) | 1.00e-4 → 6.00e-5 (escaladare consistentă) |
| k research / obs_mean | 550 trades / **+0.0610 R/trade** |
| **p VALIDATION (OOS, SEPARAT)** | **0.0779** (k=183, obs +0.0226 R) — **NU confirmă la 0.05** |

BH: k*=1 (rang-2 ar cere p≤2.43e-4; al 2-lea cel mai mic p = 4.42e-4 > prag → neresins). Zero UNRESOLVED.

---

## 2. CÂȚI din 1972 au fost EXCLUȘI, și de ce (rezultatul care contează pentru decizia D2)

**1560 excluși · 412 testați.**
| categorie | count | motiv |
|---|---|---|
| Stop structural/level | **1532** | `structural/beyond_sweep/beyond_ext/beyond_level/bar/or_opp/prev_ext/ext/struct/level` — regimul D2, motor NECALIBRAT |
| `ema` (S7) | **12** | regim terț „distanță-de-indicator", ambiguu, nevalidat |
| ATR-stop dar n<25 | **16** | ineligibile (sub pragul înghețat), excluse din m, fără p fabricat |
| **Total exclus** | **1560** | |
| **Testat (m)** | **412** | ATR-stop valid |

S1 (1152 ipoteze) e **integral exclus** — nu are opțiune `atr`. Practic **79% din corp** (1560/1972) cade în afara domeniului validat al motorului. Aceasta e constatarea structurală: matched-null-ul, așa cum e validat azi, NU poate vorbi despre majoritatea corpului.

---

## 3. Cele mai mici 10 p de research (transparență)

| id | fam | ipoteză | k | obs_mean | p (MC-1) | notă |
|---|---|---|---|---|---|---|
| ce76669a3b2a | S18 | h13 down time | 550 | +0.061 | 1.0e-4 → **MC-3 6.8e-5** | **SUPRAVIEȚUITOR** |
| f1704085cbda | S18 | h14 down rr2 | 550 | −0.033 | 5.0e-4 → MC-3 4.42e-4 | neresins (rang-2 prag 2.4e-4) |
| 156071e50766 | S16 | pd_open reject rr2 | 451 | −0.018 | 8.5e-4 → MC-3 6.01e-4 | neresins |
| 9fcdbf1d8d13 | S5 | ny breakout opp_liq up | 1084 | −0.068 | 1.1e-3 | neresins |
| 42345e7a0115 | S18 | h14 down time | 550 | +0.006 | 1.25e-3 | neresins |
| 17488a6c88d7 | S5 | (dup) | 970 | −0.115 | 2.25e-3 | neresins |
| ba3e8d0cdb51 | S18 | h20 down/… | 550 | −0.071 | 3.65e-3 | neresins |
| 00d840de0b48 | S18 | h20 up rr2 | 534 | +0.107 | 4.30e-3 | neresins |

**Notă de citire critică:** multe p mici au **obs_mean NEGATIV** (ex. −0.033, −0.068). Matched-null e one-sided pe TIMING: p mic = observatul depășește nulul de timing-aleator cu ACELAȘI profil de risc/cost/exit. Nulul acestor ipoteze e puternic negativ (costuri + structura exit/RR pierd sub timing aleator); observatul doar „pierde mai puțin". **Testul măsoară abilitate de timing relativă, NU profitabilitate absolută.** Supraviețuitorul are obs POZITIV (+0.061) și depășește nulul — dar tot în acest cadru de timing.

---

## 4. Interpretarea Statistician-ului asupra supraviețuitorului (asumă-l fals, încearcă să-l distrugi)

Supraviețuitorul NU e o alfa nouă validată. Trei probleme concrete, raportate separat:

1. **[RETRAS 2026-07-25 — vezi §7.1]** ~~Alternativă neexclusă = primitiva Volatility (profil oră-din-zi) + asimetria direcțională.~~ Explicația inițială (supraviețuitorul = re-detecția primitivei Volatility + asimetria direcțională Flow C) **NU se susține** și e retrasă: supraviețuitorul e **short** într-o fereastră în care aurul a crescut ~131%, iar Flow C a măsurat hit-rate long 29.0% vs short 9.2% — deci driftul și asimetria direcțională lucrează **împotriva** lui, nu îl explică. Detaliu în §7.1.

2. **Eșuează OOS.** Validation p = 0.078 > 0.05. Nu se confirmă out-of-sample (consistent cu tiparul „edge-urile de research pică OOS").

3. **E ortogonal regimului D2.** Supraviețuitorul folosește stop 1.5×ATR — nu are nicio legătură cu stopurile structurale (sursele D2). Prin urmare **NU** e o dovadă că *regimul structural (D2) ascunde un edge*; ar fi supraviețuit indiferent de D2. E un efect oră-din-zi ortogonal.

**Avertisment metodologic:** configurația validată folosește o sămânță comună (0xA11CE) pe toate ipotezele → tragerile null sunt corelate între ipoteze (BH sub dependență pozitivă rămâne valid, dar robustețea la per-hyp-seed nu e testată). Un singur supraviețuitor lângă prag e consistent și cu coada rară de fals-pozitivi sub FDR 5%.

---

## 5. Implicația pentru decizia D2 (regula pre-declarată a CEO)

Regula CEO, pre-declarată: „dacă ceva supraviețuiește în subset, D2 devine obligatoriu, pentru că avem un motiv concret să credem că mai e ceva de găsit." **Formal, condiția s-a declanșat: există 1 supraviețuitor.** Îl raportez ca atare — nu îl reduc la „practic zero".

Dar, ca Statistician, ponderez cinstit **cât de concret** e motivul, și e **SLAB**, din trei motive independente (§4): supraviețuitorul (a) e cel mai probabil re-detecția primitivei Volatility/asimetriei direcționale, nu un factor nou; (b) eșuează OOS; (c) e **ortogonal** regimului structural — nu spune nimic despre ce ascunde regimul D2. Argumentul original al CEO era „dacă regimul curat produce ceva, crește probabilitatea ca regimul murdar să ascundă un edge real". Acel argument NU e susținut aici, fiindcă singurul supraviețuitor e un efect oră-din-zi care nu are nicio legătură cu stopurile structurale.

**Recomandarea mea (decizia rămâne a CEO):** condiția pre-declarată e îndeplinită, deci decizia despre WP-1..4 se poate lua acum pe dovezi — dar dovada nu e „un edge în regimul curat care sugerează mai mult în cel murdar". E „un efect oră-din-zi, deja explicabil prin primitiva Volatility, care nici măcar nu confirmă OOS". Dacă motivul pentru D2 e *speranța unui edge structural ascuns*, acest rezultat **nu îl susține**. Dacă D2 se închide, se justifică mai degrabă pe integritatea metodologică (a debloca cei 1560 de excluși pentru orice test viitor) decât pe acest supraviețuitor.

---

## 6. Ce s-a livrat / respectat

| cerință pre-înregistrată | stare |
|---|---|
| Criteriu subset din câmpul `stop`, nu din rezultate | ✅ `h['stop']=='atr'` |
| m + prag BH pre-declarate | ✅ m=412, 1.214e-4 |
| Config unstratified + ATR-scaled (singura validată) | ✅ strata=None |
| MC adaptiv 20k/200k/1e6, p=(k+1)/(B+1), seminte+contoare | ✅ salvate în seeds.json / research.parquet |
| Oprire secvențială never-BH-rejected (p>0.05) | ✅ reproductibilitate verificată = `matched_null_p` la 1e-12 |
| Regula UNRESOLVED | ✅ 0 unresolved (CI supraviețuitor sub prag) |
| Research și validation raportate SEPARAT | ✅ niciodată combinate |
| Raportare indiferent de semn + numărul de excluși | ✅ 1 supraviețuitor, 1560 excluși |
| Holdout SEALED, fără extindere/ajustare/re-rulare | ✅ |

**Verdict:** 1 supraviețuitor de research-FDR în regimul validat (`ce76669a3b2a`, S18 oră-13-short), MC-3-confirmat sub prag, **fără confirmare OOS** (val_p=0.078) și **ortogonal** regimului D2. 1560 din 1972 ipoteze (79%) sunt în afara domeniului validat. **Vezi §7 (corecții la review-ul CEO 2026-07-25):** explicația „re-detecție Volatility" e RETRASĂ (supraviețuitorul e short într-o piață în urcare de 131% — driftul/asimetria lucrează împotriva lui); profilul de fragilitate al supraviețuitorului e neobișnuit de bun (nu poate fi respins prin argumentul de concentrare); și există o contradicție de criterii a laboratorului (a trecut FDR global, dar research_worthy=False fiindcă dd=33.4R > pragul 25R). D2 NU se închide pe baza acestui supraviețuitor (premisa regulii — edge curat ⇒ edge murdar — nu se aplică unui efect oră-din-zi ortogonal). Rezultatul merge la certificare (contract v1.1 §5); nu se interpretează mai departe. Holdout SEALED.

---

## 7. CORECȚII LA REVIEW-UL CEO (2026-07-25) + verificarea clusterului

### 7.1 RETRAGERE — explicația #1 (Volatility + asimetrie direcțională) NU se susține
Am atribuit supraviețuitorul primitivei Volatility (profil oră-din-zi) + asimetriei direcționale (Flow C RI-META-0004). **Retras.** Supraviețuitorul e **SHORT** (h13 UTC), într-o fereastră în care aurul a crescut **~131%**. Flow C a măsurat hit-rate **long 29.0% vs short 9.2%**. Deci driftul și asimetria direcțională lucrează **AMÂNDOUĂ ÎMPOTRIVA** unui short — nu îl pot explica. Profilul orar poate explica de ce există *un efect* la h13, dar **nu** de ce e short și **nu** de ce supraviețuiește unui null care **păstrează direcția** (matched-null randomizează doar timing-ul, ținând direcția short fixă). Concluzia: supraviețuitorul e un efect **h13-short specific de timing**, NE-explicat de cunoașterea existentă (Volatility e direcție-agnostică; drift/asimetrie se opun shorturilor). **Punctele §4.2 (eșec OOS) și §4.3 (ortogonal D2) rămân valabile.**

### 7.2 Profil de fragilitate neobișnuit de bun (corectează argumentul de concentrare)
Supraviețuitorul (FAMILY_RESULTS rând 1919): **t5 = 0.141** (vs mediană profitabili 0.255 — sub jumătate), **wo1 = +0.032** (supraviețuiește scoaterii celei mai bune tranzacții), **fragile = False**, 550 tranzacții / 27 luni / 14 luni pozitive / 4 ani. Concentrarea = ~14% vs 41% la nivel de corp (Flow C). **Nu îl validează**, dar înseamnă că **nu poate fi respins prin argumentul de concentrare** care se aplică restului corpului. Îmi corectez implicit ponderarea din §4: supraviețuitorul e mai greu de respins decât am sugerat.

### 7.3 FINDING DE INTEGRITATE (al laboratorului, nu al analizei) — criterii oficiale în contradicție
Supraviețuitorul a trecut **FDR-ul global** (Test B validat, p sub prag BH), dar **`research_worthy = False`** — cauza: **dd = 33.4R > pragul 25R** din Discovery Screen V1. **Două criterii oficiale ale laboratorului dau verdicte opuse pe același obiect:** unul îl declară supraviețuitor statistic, celălalt îl respinge la screening. Consemnat ca finding de integritate; **NU îl rezolv** (nu e în mandatul acestei analize).

### 7.4 VERIFICAREA CLUSTERULUI S18 (cifre, fără concluzie)
Întrebare: clusterul S18 la p mic (orele 13/14/20, majoritatea short) conține și alte ipoteze cu profil similar supraviețuitorului (t5<0.20 & wo1>0 & fragile=False)?

Cele 6 ipoteze S18 cu p_research < 0.02, sortate după p:
| id | oră | dir | exit | n | exp | dd | t5 | wo1 | fragile | p | profil-bun? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ce76669a3b2a | 13 | down | time | 550 | +0.061 | 33.4 | 0.141 | +0.032 | False | 1.0e-4 | **DA (supraviețuitor)** |
| f1704085cbda | 14 | down | rr2 | 550 | −0.033 | 37.7 | 0.030 | −0.036 | False | 5.0e-4 | nu (wo1<0) |
| 42345e7a0115 | 14 | down | time | 550 | +0.006 | 51.0 | 0.116 | −0.015 | **True** | 1.25e-3 | nu (fragile) |
| ba3e8d0cdb51 | 13 | down | rr2 | 550 | −0.071 | 64.7 | 0.028 | −0.075 | False | 3.65e-3 | nu (wo1<0) |
| 00d840de0b48 | 20 | up | rr2 | 534 | +0.107 | 31.6 | 0.025 | +0.103 | False | 4.30e-3 | **DA** |
| 2341cf9911de | 20 | up | time | 534 | +0.177 | 26.2 | 0.090 | +0.159 | False | 1.26e-2 | **DA** |

**Cifre (fără concluzie):**
- S18 cu p<0.005: **5** ipoteze, din care cu profil-bun (t5<0.20 & wo1>0 & fragile=False): **2** (ce76669a3b2a, 00d840de0b48).
- S18 cu p<0.02: **6** ipoteze, din care profil-bun: **3** (+ 2341cf9911de).
- Deci **supraviețuitorul NU e singurul** cu profil-bun (2 alți), dar **nu tot clusterul** îl are (3 din 6).
- Observație factuală: cele 3 cu profil-bun sunt supraviețuitorul (**h13 short**) + două **h20 long** (00d840de0b48, 2341cf9911de); shorturile low-p rămase (h14 down, h13 down) au wo1 **negativ**. Cei doi h20-long au p mai mare (0.004, 0.013 — nu trec FDR), dar unul (2341cf9911de) are exp +0.177 și dd 26.2 (chiar peste pragul de 25R).

Nu concluzionez. Cifrele merg la certificare împreună cu supraviețuitorul.
