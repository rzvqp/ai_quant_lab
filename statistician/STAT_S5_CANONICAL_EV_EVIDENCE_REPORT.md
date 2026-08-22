# S5 — CONTRACTUL DE INTRARE AL EVIDENȚEI PENTRU MOTORUL REAL EV

**Divizia Statistician · `STAT-S5-CANONICAL-EV-EVIDENCE-001` · 2026-08-22**

```
S5_CANONICAL_EV_EVIDENCE_BLOCKED
S5_VALIDATED_LEDGER_REQUIRED_FOR_EV_INPUTS
```

**Blocajul e aritmetic, nu procedural, și îl pot demonstra fără să deschid escrow-ul.**

Contractul REAL EV nu consumă o rată de câștig și nici o expectanță. Consumă **patru contoare de
rezultat** dintr-o singură celulă empirical-Bayes. Din cele patru, artefactele statistice disponibile
susțin **unul singur**:

```
n              = 295          DIRECTLY_SUPPORTED
n_target       = ?            NOT_AVAILABLE   (pot demonstra doar bracketul [0, 54] -- deci NU e 162)
n_horizon      = ?            NOT_AVAILABLE   (pot demonstra doar bracketul [148, 196])
sum_horizon_R  = ?            NOT_AVAILABLE   (marime strict per-tranzactie)
```

**Nicio modificare de strategie, nicio revalidare, nicio modificare a AI Trader. Escrow-ul nu a fost
deschis.**

---

## 1 — §2 IDENTITATEA S5, RECUPERATĂ MECANIC

| element | valoare (din cod și artefacte, nu din proză) |
|---|---|
| candidat Alpha | **`C_2d587447`**, reprezentant **`7472f3d412f2`** |
| spec înghețat | **`S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}`** |
| direcție | **LONG-only** |
| `STRATEGY_ID` runtime | `s5_c_2d587447_opening_range_breakout_long` |
| `STRATEGY_VERSION` | `rep_7472f3d412f2` |
| `CONFIG_FINGERPRINT` | `S5-frozen-spec:session=ny,mode=breakout,side=up,stop=or_opp,exit=rr3;tick=0.01;or_bars=4;entry_window_bis=4-20;hold_bars=48;rr=3.0` |
| `IMPLEMENTATION_FINGERPRINT` | `s5_opening_range_breakout.py-impl-v1` |
| blob plugin @ `c30b056` | `fdacbf458537` |
| blob `real_ev_engine.py` @ `c30b056` | `77d353d67686` |
| **RR** | `RR_TARGET = 3.0` → `exit_specification = "rr:3.0"` |
| **hold maxim** | `MAX_HOLD_BARS = 48` |
| fereastră de intrare | `bar_in_session ∈ [4, 20]`, opening range = primele 4 bare M15 |
| sesiune | NY, `13:00–21:00 UTC` |
| SL | frontiera **opusă** a opening range (`stop=or_opp`) |
| tick | **`TICK = 0.01`** — override-ul ratificat, nu `mstrat.TICK = 0.1` (defectul `RT-CODE-A-0007`) |

**`S5_EV_EVIDENCE_IDENTITY_MISMATCH` nu se declanșează:** identitatea din plugin corespunde exact
identității din raportul de validare RT (§2 al acestuia) și din propriile mele artefacte de îngheț.

## 2 — PROVENIENȚA VALIDĂRII

```
validare independenta : RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001 (E97), commit ai_quant_lab 633bd5da
verdict               : INDEPENDENT_VALIDATION_PASS, portile A-H toate PASS
LEDGER INGHETAT       : S5_VALIDATION_TRADES_SHA256 = cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7
                        (295 tranzactii)  --  OFF-GIT / ESCROW
pregatire Statistician: STAT_S5_INDEPENDENT_VALIDATION_PROTOCOL.md + STAT_S5_S20_CLEAN_VALIDATION_FREEZE.md (ed49c2c)
```

Verificat: hash-ul ledger-ului **este** citat în raportul RT — deci **identitatea** ledger-ului e publică
chiar dacă **conținutul** lui nu e. Asta contează pentru §12 (fail-closed pe amprentă).

---

## 3 — ★★ §3 CONTRACTUL DE INTRARE AL MOTORULUI REAL EV, RECUPERAT DIN COD

Lanțul e: `RealEVDecisionEngine.decide` → `_decode_probability_inputs(hypothesis.expected_edge)` →
`ve_brain.ProbabilityInputs(hierarchy=(HierarchyLevel(cell=OutcomeCell(...)),), credibility)` →
`ve_brain.run_ev` → `ve_brain._ev_core.decide`.

### 3.1 Câmpurile cerute de `expected_edge`

| câmp | tip | obligatoriu | constrângere validată în cod | semnificație (din `ve_brain.OutcomeCell`) |
|---|---|---|---|---|
| `edge_schema` | `str` | **DA** | trebuie `== "real-ev-expected-edge-v1"` | versiunea schemei; orice altceva ⇒ `None` ⇒ `MISSING_PROBABILITY_INPUTS` |
| `n` | `int` | **DA** | `≥ 0`; iar `_ev_core` cere `n > 0`, altfel `_fail("global_rate")` | numărul total de tranzacții în celulă |
| `n_target` | `int` | **DA** | `≥ 0` | **ieșiri la ȚINTĂ** |
| `n_horizon` | `int` | **DA** | `≥ 0` | **ieșiri pe ORIZONT (time-stop)** |
| `sum_horizon_r` | `float` | **DA** | finit | **suma cu semn a R pe ieșirile de orizont**; `E[X|h] = sum / n_horizon` |
| `credibility` | `float` | opțional, implicit **`0.80`** | `0 < credibility < 1` | nivelul de credibilitate; `q_lcb = 1 − credibility` |

**Unități:** `n`, `n_target`, `n_horizon` sunt **contoare**; `sum_horizon_R` e în **unități R**
(adimensional, raportat la riscul fiecărei tranzacții). Ieșirile la stop nu se transmit — sunt
**implicite**: `n_stop = n − n_target − n_horizon`.

### 3.2 Ce face motorul cu ele — §8 e determinat de contract, nu de mine

```
p_t_hat = _shrink_proportion(hierarchy, c -> c.n_target)        proportia (shrink-uita) a iesirilor la tinta
p_h_hat = _shrink_proportion(hierarchy, c -> c.n_horizon)       proportia iesirilor pe orizont
p_t_lcb = _beta_ppf(1 - credibility, alpha_t, beta_t)           LIMITA INFERIOARA Beta a lui p_target
e_x_h   = _shrink_mean_horizon(...)                             media R pe iesirile de orizont
          !! daca lipseste -> e_x_h = -1.0  (cel mai RAU caz, NU zero)
ev_lcb  = ev_from_terms(p_t_lcb, p_h_hat, e_x_h, rr, cost/r)
enter   = ev_lcb > 0.0     (STRICT; egalitate -> NO_TRADE)
feasibility: rr > cost/r    altfel NO_TRADE_FEASIBILITY
```

**★ Răspunsul la §8:** motorul **NU** consumă o probabilitate punctuală, nici o expectanță, nici un CI
furnizat din afară. Consumă **contoare brute** și își **construiește singur** limita inferioară
(`p_t_lcb`, un LCB Beta unilateral la `1 − credibility`). Deci:

```
NU se furnizeaza: win rate, expected R, BASE/STRESS expectancy, PF, CI, EV lower bound
SE furnizeaza   : n, n_target, n_horizon, sum_horizon_R  (+ credibility, care e POLITICA, nu evidenta)
```

`credibility = 0.80` este **valoarea implicită ratificată** din `ve_brain`. Nu proiectez o filosofie
nouă de risc: se declară explicit în artefact, cu valoarea ratificată.

---

## 4 — §4 CARTOGRAFIEREA EVIDENȚĂ → CÂMPURI EV

Evidența autoritară disponibilă (raport RT `633bd5da`, secțiunile 4/5/10/11):

```
n=295 · WR 0.549 · avg R BASE 0.210 · median R 0.125 · avg winner +1.009 · avg loser -0.763
PF 1.609 · gross/BASE/STRESS 0.214/0.210/0.193 · maxDD -6.44R · maxLoss -1.03R
holding median 49 bare (P25 30.5 / P75 49) · MAE/MFE median $6.83/$10.42 · long fraction 1.00
TP median $37.32 (373.2 pips), P25/P50/P75 = 27.20/37.32/51.44 · %TP>=100p = 99.0%
temporal treimi [0.273, 0.153, 0.201] · best-1%-removed 0.1907 · delay+1 0.1581
```

| câmp EV | clasificare | justificare |
|---|---|---|
| `edge_schema` | **DIRECTLY_SUPPORTED** | constantă de schemă, `"real-ev-expected-edge-v1"` |
| **`n`** | **DIRECTLY_SUPPORTED** | `295`, citat explicit în RT §4 și în poarta A |
| **`n_target`** | **NOT_AVAILABLE** | v. §5 — `WR` **nu** e rata de atingere a țintei; demonstrat aritmetic |
| **`n_horizon`** | **NOT_AVAILABLE** | v. §5 — se poate mărgini inferior, nu determina |
| **`sum_horizon_R`** | **NOT_AVAILABLE** | mărime strict per-tranzacție; niciun agregat publicat nu o determină |
| `credibility` | **DIRECTLY_SUPPORTED** (ca politică) | implicit ratificat `0.80` din `ve_brain` |

**Niciun câmp nu e `DERIVABLE_WITHOUT_NEW_STATISTICAL_ASSUMPTION` în afară de `n`.**

---

## 5 — ★★ DEMONSTRAȚIA ARITMETICĂ: DE CE `WR` NU POATE FURNIZA `n_target`

Aceasta e partea decisivă, și se face **exclusiv din cifrele publicate**, fără escrow.

### 5.1 Consistența internă a metricilor RT (verificată)

```
castigatori W = round(0.549 x 295) = 162        perdanti L = 133        162/295 = 0.5492 ✓ (raportat 0.549)
suma R = 162 x (+1.009) + 133 x (-0.763) = +61.979     ->  media = 0.2101   ✓ (raportat 0.210)
PF = 163.458 / 101.479 = 1.6108                                            ✓ (raportat 1.609)
```

Metricile RT sunt **mutual consistente**. Le pot folosi ca sistem de ecuații.

### 5.2 Limita superioară pe `n_target`

`S5` are `exit = rr3`, deci **o ieșire la țintă returnează ≈ +3,0 R** (minus costul BASE de `$0,05`
raportat la un risc median de `$12,44`, adică `−0,004 R` — neglijabil).

Profitul brut total al câștigătorilor este `162 × 1,009 = 163,458 R`. Dacă ar exista `T` ieșiri la
țintă, ele singure ar contribui `≈ 3,0·T`, iar restul câștigătorilor contribuie strict pozitiv. Deci:

```
3.0 x T  <=  163.458    =>    T <= 54.5    =>    n_target <= 54
```

```
rata de atingere a tintei  <=  54/295 = 0.183      fata de   win rate = 0.549
                                                   ->  WR SUPRAESTIMEAZA n_target de cel putin 3.0x
```

**★ Deci `n_target = round(WR × n) = 162` ar fi o falsificare de cel puțin trei ori.** `avg winner
= +1,009` la o geometrie `RR3` spune direct că **majoritatea „câștigătorilor" nu sunt ieșiri la țintă**,
ci ieșiri pe orizont cu R pozitiv. Aceasta e exact capcana pe care §5 al mandatului o interzice
(„luarea WR dintr-un raport și inserarea manuală").

### 5.3 Limita inferioară pe `n_horizon`

`MAX_HOLD_BARS = 48`. În `mstrat.simulate`, bucla acoperă `j ∈ [ei, ei+47]`; dacă nu se atinge nici
stopul nici ținta, `xi = ei + 48`, deci **holding-ul `xi − ei + 1 = 49` apare EXCLUSIV la ieșirile pe
orizont**. RT raportează:

```
holding median = 49 bare   (P25 30.5 / P75 49)
```

Mediana celor 295 de valori e a **148-a**. Dacă a 148-a valoare este `49`, atunci **cel puțin 148 de
tranzacții au holding 49**, adică sunt ieșiri pe orizont:

```
n_horizon >= 148        (>= 50.2% din esantion)
```

### 5.4 O a treia margine, din `avg loser` — și bracketul complet

`avg loser = −0,763`, deci pierderea brută este `133 × (−0,763) = −101,479 R`. O ieșire la **stop**
returnează `−1 − cost/risc`; RT raportează `maxLoss = −1,03 R`, deci fiecare stop pierde **între 1,004
și 1,03 R**. O ieșire pe orizont negativă nu poate fi mai rea decât stopul (altfel stopul s-ar fi
declanșat primul). Deci:

```
n_stop x 1.03  >= 101.479   =>   n_stop >= 99     (marginea CONSERVATOARE)
n_stop x 1.004 >= 101.479   =>   n_stop >= 102    (marginea stransa)
```

**★ Bracketul complet derivabil fără escrow (varianta conservatoare):**

```
n_target   in [  0,  54]     din avg winner = +1.009 la geometrie RR3
n_horizon  in [148, 196]     inferior din holding median = 49 = plafon ; superior din n_stop >= 99
n_stop     in [ 99, 147]     din avg loser = -0.763 si maxLoss = -1.03
                                              n_target + n_horizon + n_stop = 295
```

**Și totuși rămâne nedeterminat**: trei necunoscute, trei inegalități, nicio ecuație. Iar
**`sum_horizon_R` nu are nicio margine utilă** — e suma cu semn a R-urilor pe ieșirile de orizont, iar
`avg R` global nu o separă de contribuția țintelor și a stopurilor. Bracketul de mai sus e util ca
**test de acceptare** pentru cifrele care vor veni (§13), nu ca substitut pentru ele.

**Observație care confirmă independent povestea:** dacă toți cei 133 de perdanți ar fi stopuri,
`avg loser` ar fi `≈ −1,004`. Este `−0,763`. Deci **și o parte din perdanți sunt ieșiri pe orizont**,
cu R negativ dar mai blând decât stopul — exact ce prezice un `MAX_HOLD_BARS = 48` care se activează
pe peste jumătate din eșantion.

**Iar `e_x_h` este exact termenul cu cea mai severă consecință**: dacă lipsește, `_ev_core` îl setează
la **`−1.0`**, cel mai rău caz. Un `n_horizon` sau un `sum_horizon_R` inventat ar muta direct `ev_lcb`,
adică decizia însăși.

---

## 6 — §6 DEPENDENȚA DE LEDGER

```
S5_VALIDATED_LEDGER_REQUIRED_FOR_EV_INPUTS
```

Cele trei câmpuri lipsă (`n_target`, `n_horizon`, `sum_horizon_R`) sunt **statistici de partiție a
ieșirilor și de sumă per-tranzacție**. Ele nu sunt funcții ale niciunei combinații de
`{N, WR, avg R, median R, avg winner, avg loser, PF, maxDD, maxLoss, holding, MAE/MFE, TP}` publicate.

**Escrow-ul NU a fost deschis și nu trebuie deschis de mine.** Ce lipsește nu e „acces la ledger" ca
scop în sine — e **un artefact statistic derivat, cu trei numere**, pe care deținătorul autorizat al
ledger-ului îl poate produce fără a expune tranzacții individuale:

```
n_target, n_horizon, sum_horizon_R      (trei scalari, plus hash-ul ledger-ului din care provin)
```

**Asta e tot ce lipsește.** Nu tranzacțiile, nu prețurile, nu datele — trei contoare agregate.

## 7 — §7 REPRODUCEREA METRICILOR

**Nu am reprodus metricile prin re-execuție**, și nu trebuie: §13/§14 interzic revalidarea, iar ledgerul
e sigilat. Ce am făcut e **verificarea de consistență internă** din §5.1, care e mai relevantă aici:
metricile publicate formează un sistem coerent (`W`, `L`, `avg`, `PF` se reconstruiesc reciproc la
`±0,002`).

**Discrepanțe față de valorile de referință din mandat:** niciuna materială.

```
mandat: N=295 · WR 54.9% · BASE +0.210 · STRESS +0.193 · PF 1.61 · maxDD -6.44R · RR 1:3
RT    : N=295 · WR 0.549 · BASE  0.210 · STRESS  0.193 · PF 1.609 · maxDD -6.44R · rr3
```

Singura precizare: RT raportează `BASE 0.2098` la poarta B și `0.210` la profilul realizat — aceeași
valoare, rotunjită diferit. Nu e discrepanță.

## 8 — §9 IDENTITATEA COSTULUI

**Economia validării:**

```
TICK = 0.01 (override ratificat RT-CODE-A-0007; mstrat.TICK = 0.1 NU a fost folosit)
BASE round-trip   = $0.05      STRESS round-trip = $0.24     (AI_TRADER_SHADOW_COST_MODEL_v1.json)
podea de stop     = max(2*spread, 0.05, 0.10*ATR) -> max(0.05, 0.10*ATR)   activata in 0% din tranzactii
spread pliat in slippage (spread_ticks = 0, slip_ticks = RT/(2*TICK))
intrare           = deschiderea barei URMATOARE (next-bar open)
R                 = (directie*(iesire - intrare) - round_trip) / risc      risc in unitati de PRET
```

**Economia runtime**, din `ve_brain.ev_engine._rr_r_cost`:

```
r    = |entry_price - stop_price|                                  (pret)
cost = full_spread_price + entry_slippage_price + exit_slippage_price   (pret, SUMA celor trei)
```

**★ Constrângerea exactă de identitate de cost:**

```
CostModel.full_spread_price + entry_slippage_price + exit_slippage_price  ==  0.24   (STRESS)
                                                                          ==  0.05   (BASE)
```

Validarea a **pliat spread-ul în slippage**, deci **descompunerea nu e identificată** — numai **suma**
e validată. Orice triplet care însumează `0,24` e identic economic cu validarea; orice sumă diferită
declanșează `S5_EV_COST_IDENTITY_FAIL`.

**Verificare de fezabilitate:** `rr = 3.0` vs `cost/r`. Cu risc median `= TP/3 = 373,2/3 = 124,4` pips
`= $12,44`, avem `cost/r = 0,24/12,44 = 0,0193`. `3,0 ≫ 0,0193` ⇒ poarta de fezabilitate nu se
activează niciodată la geometria S5. Consemnat, nu presupus.

**Nu emit `S5_EV_COST_IDENTITY_FAIL`** — dar identitatea e **condiționată**, nu constatată: nu am
inspectat `CostModel`-ul cu care pipeline-ul e asamblat în producție (§15 interzice modificarea AI
Trader; nu l-am nici citit ca fiind cel operativ). Constrângerea de mai sus e obligatorie la ambalare.

## 9 — §10 IDENTITATEA POPULAȚIEI

```
populatie de validare independenta : 52.572 bare M15, 2023-07-24 10:30Z -> 2025-10-12 23:00Z
pop_ohlc_sha256   = bac65b1a...        timeline_sha256 = 4c9ce7b7...
sursa             = corpus M15_v2 manifest-gated, fisier sha 57f4ed95...
inghetata la      = ed49c2c (STAT_S5_S20_CLEAN_VALIDATION_FREEZE.md)
FINAL_HOLDOUT_ACCESS_COUNT = 0
```

**Aceasta e singura populație care poate susține evidența EV.** Interzis explicit în artefact:

```
DEV S1-S20 · CALIB · felia istorica CONSUMATA (2022-12-01 -> 2023-07-24, 15.086 bare) ·
holdout final (>= 2025-10-23) · V1 · 2025+ M5 · orice amestec al acestora
```

**Provenienta nu se pierde la runtime:** artefactul trebuie să poarte `pop_ohlc_sha256` și
`timeline_sha256`, iar motorul trebuie să le verifice — v. §11/§12.

---

## 10 — §11 SCHEMA CANONICĂ A ARTEFACTULUI DE EVIDENȚĂ

Definesc obiectul; **nu îl implementez și nu ating AI Trader** (§15). Câmpurile marcate `<<LIPSA>>` sunt
exact cele blocate.

```yaml
artifact_id:            S5_EV_EVIDENCE
artifact_version:       s5-ev-evidence-v1
artifact_sha256:        <sha256 al continutului canonicalizat, exclusiv acest camp>

# ── identitate strategie (fail-closed pe fiecare) ──
strategy_id:            s5_c_2d587447_opening_range_breakout_long
strategy_version:       rep_7472f3d412f2
config_fingerprint:     "S5-frozen-spec:session=ny,mode=breakout,side=up,stop=or_opp,exit=rr3;
                         tick=0.01;or_bars=4;entry_window_bis=4-20;hold_bars=48;rr=3.0"
implementation_fingerprint: s5_opening_range_breakout.py-impl-v1
alpha_candidate:        C_2d587447
representative:         7472f3d412f2

# ── identitate validare ──
validation_mandate:     RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001
validation_commit:      633bd5da
validation_verdict:     INDEPENDENT_VALIDATION_PASS
validation_ledger_sha256: cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7
validation_ledger_n:    295

# ── identitate populatie ──
population_id:          S5_S20_CLEAN_VALIDATION_POPULATION
population_ohlc_sha256: bac65b1a...
population_timeline_sha256: 4c9ce7b7...
population_start_utc:   2023-07-24T10:30:00Z
population_end_utc:     2025-10-12T23:00:00Z
population_bars:        52572
final_holdout_access_count: 0

# ── identitate cost ──
cost_model_id:          AI_TRADER_SHADOW_COST_MODEL_v1
cost_scenario:          STRESS                  # sau BASE; se declara, nu se presupune
round_trip_price:       0.24                    # BASE = 0.05
min_tick:               0.01
stop_floor_rule:        "max(0.05, 0.10*ATR)"
entry_convention:       next_bar_open

# ── INTRARILE EV (singurele consumate de real_ev_engine) ──
edge_schema:            real-ev-expected-edge-v1
n:                      295
n_target:               <<LIPSA -- necesita ledgerul>>
n_horizon:              <<LIPSA -- necesita ledgerul>>
sum_horizon_r:          <<LIPSA -- necesita ledgerul>>
credibility:            0.80                    # POLITICA (implicitul ratificat ve_brain), nu evidenta

# ── metadate de incertitudine (declarative) ──
uncertainty_semantics:  "motorul deriva singur p_t_lcb = Beta_ppf(1-credibility) din contoare;
                         artefactul NU furnizeaza probabilitati, CI-uri sau expectante"
derivation_policy:      RAW_COUNTS_ONLY_NO_ESTIMATION
```

**Ce NU are voie să conțină artefactul:** `win_rate`, `expected_edge` scalar, `avg_R`, `PF`, `maxDD`,
orice CI, orice valoare implicită pentru cele trei câmpuri lipsă.

## 11 — §12 MATRICEA FAIL-CLOSED

| condiție | comportament cerut | unde e deja aplicată |
|---|---|---|
| `strategy_id` necunoscut în catalog | `NO_TRADE` / `UNKNOWN_STRATEGY` | `real_ev_engine.decide` pas 1 ✓ |
| strategie dezactivată | `NO_TRADE` / `STRATEGY_DISABLED` | pas 1 ✓ |
| `config_fingerprint` ≠ cel din catalog | `NO_TRADE` / `STRATEGY_POLICY_MISMATCH` | pas 1 ✓ |
| status ≠ `VALIDATED` | `NO_TRADE` / `NO_ELIGIBLE_STRATEGY` | pas 1 ✓ |
| `validation_provenance` absentă | `NO_TRADE` / `STRATEGY_POLICY_MISMATCH` | pas 1 ✓ |
| `implementation_fingerprint` ≠ artefact | **NOU — de adăugat la ambalare** | — |
| identitate de validare ≠ artefact | **NOU** | — |
| `cost_model_id` / sumă round-trip ≠ validare | **NOU** ⇒ `S5_EV_COST_IDENTITY_FAIL` | — |
| amprentă de populație ≠ artefact | **NOU** | — |
| `edge_schema` greșită sau absentă | `MISSING_PROBABILITY_INPUTS` | `_decode_probability_inputs` ✓ |
| oricare din `n/n_target/n_horizon/sum_horizon_r` absent | `MISSING_PROBABILITY_INPUTS` | ✓ (`KeyError` → `None`) |
| tip greșit / neconvertibil | `MISSING_PROBABILITY_INPUTS` | ✓ (`TypeError/ValueError`) |
| `n < 0` sau `n_target < 0` sau `n_horizon < 0` | `MISSING_PROBABILITY_INPUTS` | ✓ |
| `credibility ∉ (0,1)` | `MISSING_PROBABILITY_INPUTS` | ✓ |
| `n == 0` | `_fail("global_rate")` → `NO_TRADE` | `_ev_core.decide` ✓ |
| `NaN` / `inf` în `sum_horizon_r` | **LACUNĂ** — `float("nan")` trece de `_decode`; `_ev_core` verifică `rr/r/cost/credibility`, **nu** `sum_horizon_R` | **de adăugat la ambalare** |
| `n_target + n_horizon > n` | **LACUNĂ** — nicio verificare | **de adăugat la ambalare** |
| artefact modificat (tampering) | verificare `artifact_sha256` | **NOU** |
| derivare nesuportată (WR → `n_target`) | interzisă prin `derivation_policy` | **NOU** |

**★ Două lacune reale găsite în contractul existent**, ambele nemateriale azi (fiindcă `expected_edge`
e `None`) dar obligatorii înainte de ambalare: **`sum_horizon_r = NaN` nu e respins**, și
**`n_target + n_horizon > n` nu e respins**. Le semnalez ca cerințe de ambalare, nu le implementez.

## 12 — §16 VERDICT

```
S5_CANONICAL_EV_EVIDENCE_BLOCKED
```

**Ce lipsește, exact:**

```
n_target        (ieșiri la ȚINTĂ, contor)          -- demonstrat <= 54, deci NU 162; valoarea exacta lipseste
n_horizon       (ieșiri pe ORIZONT, contor)        -- demonstrat >= 148; valoarea exacta lipseste
sum_horizon_R   (suma cu semn a R pe orizont)      -- fara nicio margine derivabila
```

**De unde poate veni:** exclusiv din ledgerul înghețat `cd4e8d4a…` (295 tranzacții), prin deținătorul
lui autorizat. **Trei scalari**, nu tranzacții.

**Comportamentul actual e CORECT și trebuie păstrat până atunci:** `expected_edge = None` →
`_decode_probability_inputs` → `None` → `MISSING_PROBABILITY_INPUTS` → `NO_TRADE`. **Fail-closed
funcționează exact cum trebuie.** Nu recomand nicio soluție intermediară.

**Interzis explicit, și repet fiindcă e tentant:**

```
n_target := round(WR x n) = 162        FALSIFICARE  (demonstrat: n_target <= 54)
n_horizon := 0                          FALSIFICARE  (demonstrat: n_horizon >= 148); si ar scoate
                                        termenul de orizont din EV, adica ar schimba decizia
sum_horizon_R := 0                      FALSIFICARE  ("neutru" nu e absent; absenta da e_x_h = -1.0)
orice valoare din DEV/CALIB             populatie gresita -> pierdere de provenienta
orice fixture sintetic                  nu e evidenta
```

## 13 — §17 PREDAREA CĂTRE URMĂTORUL MANDAT

**Un singur lucru e de obținut**, și e mic:

> Deținătorul autorizat al ledgerului `cd4e8d4aae0104cd…` produce **trei contoare agregate** —
> `n_target`, `n_horizon`, `sum_horizon_R` — calculate pe **cele 295 de tranzacții**, partiționate după
> tipul de ieșire (`țintă` / `orizont la 48 bare` / `stop`), în **scenariul de cost declarat**, împreună
> cu hash-ul ledgerului din care provin. **Nicio tranzacție individuală nu trebuie expusă.**

**Verificări de consistență pe care le pot face fără escrow, imediat ce cifrele sosesc:**

```
1.  n_target + n_horizon <= 295            partitie valida (n_stop = 295 - n_target - n_horizon >= 0)
2.  n_target  in [  0,  54]                §5.2   din avg winner +1.009 la RR3
3.  n_horizon in [148, 196]                §5.3 / §5.4
4.  n_stop    in [ 99, 147]                §5.4   din avg loser -0.763 si maxLoss -1.03
5.  RECONSTRUCTIE, cu c = round_trip/risc per tranzactie (~0.004 la BASE, risc median $12.44):
       n_target*(3.0 - c)  +  sum_horizon_R  +  n_stop*(-1.0 - c)   ~=   295 * 0.210  =  61.95 R
```

**Verificarea 5 e testul cel mai tare**: dacă cele trei contoare nu reconstituie `avg R = 0,210` din
raportul RT (în toleranța dată de variația lui `c` per tranzacție), artefactul e inconsistent cu
validarea și trebuie respins. **Nu pot fabrica cifrele, dar
pot verifica riguros cifrele pe care le primesc** — și asta e exact rolul meu.

**Nu autorizez ambalarea până când:** (a) cele trei contoare sosesc cu hash-ul ledgerului; (b) trec
verificările 1–4; (c) `CostModel`-ul operativ e verificat împotriva constrângerii din §8; (d) cele două
lacune fail-closed din §11 sunt închise.

---

```
S5_CANONICAL_EV_EVIDENCE_BLOCKED
S5_VALIDATED_LEDGER_REQUIRED_FOR_EV_INPUTS
S5_EV_EVIDENCE_IDENTITY_MISMATCH   : NU se declanseaza (identitate verificata)
S5_EV_COST_IDENTITY_FAIL           : NU se declanseaza, dar identitatea e CONDITIONATA
                                     (suma celor trei campuri de cost trebuie sa fie 0.24 STRESS / 0.05 BASE)
contract EV recuperat: edge_schema · n · n_target · n_horizon · sum_horizon_r · credibility(0.80)
motorul deriva SINGUR p_t_lcb (Beta LCB unilateral); NU se furnizeaza WR, expectanta, PF sau CI
n = 295 DIRECTLY_SUPPORTED · celelalte trei NOT_AVAILABLE
demonstrat fara escrow: n_target in [0,54] (WR o supraestimeaza de >=3x) · n_horizon in [148,196] · n_stop in [99,147]
e_x_h lipsa -> -1.0 (cel mai rau caz, NU zero) -> orice contor inventat schimba direct decizia
comportamentul actual (expected_edge=None -> MISSING_PROBABILITY_INPUTS -> NO_TRADE) e CORECT
doua lacune fail-closed gasite: sum_horizon_r=NaN neblocat · n_target+n_horizon>n neverificat
```

*Escrow-ul nu a fost deschis. Nicio modificare a S5, a Alpha, a AI Trader. Nicio revalidare. Fără
holdout, CALIB, V1 sau 2025+. Fără broker, fără live.*
