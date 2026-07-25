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

1. **Alternativă neexclusă = primitiva Volatility (profil oră-din-zi) + asimetria direcțională.** Supraviețuitorul e o ipoteză **oră-din-zi cu bias short** (h13 UTC = deschidere NY). Clusterul S18 la p mic (h13/h14/h20, majoritatea **short**) arată o structură sistematică oră-din-zi-direcțională. Laboratorul are deja **Volatility ca primitivă promovată cu profil oră-din-zi**, iar Flow C a ridicat asimetria direcțională (RI-META-0004, „drift is a hypothesis"). Matched-null-ul randomizează timing-ul peste TOATE barele eligibile → va marca orice strategie oră-concentrată ori de câte ori anumite ore sunt sistematic direcționale — exact ce afirmă primitiva Volatility. Deci supraviețuitorul e **plauzibil o re-detecție a cunoașterii deja existente**, nu un factor independent nou. Este exact alternativa pe care rapoartele mele de Fază 1 au semnalat-o de fiecare dată.

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

**Verdict:** 1 supraviețuitor de research-FDR în regimul validat (`ce76669a3b2a`, S18 oră-13-short), MC-3-confirmat sub prag, dar **fără confirmare OOS** și **cel mai probabil re-detecția primitivei Volatility oră-din-zi**, **ortogonal** regimului D2. 1560 din 1972 ipoteze (79%) sunt în afara domeniului validat. Decizia D2 revine CEO; condiția pre-declarată e îndeplinită, dar motivul concret e slab și nu vizează regimul structural.
