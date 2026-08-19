# RANGE V4.3 — Raport de livrare al prototipului REAL (mandat "CONSTRUIRE PROTOTIP REAL")

**Autor:** VE · **Data:** 2026-08-19

```text
RANGE_V4_3_PROTOTYPE_RESULTS_READY_FOR_CEO_REVIEW
self_declared_pass = false
```

Acest document extinde `RANGE_V4_3_CONSTRUCTION_REPORT.md` și `RANGE_V4_3_PERFORMANCE_REPORT.md`
(deja livrate, commit `119a0cc`) cu rigoarea explicit cerută de acest mandat: matrice contract→cod→test,
matrice PASS/FAIL pe cele 19 iteme din §12, descompunerea exactă a celor 79 de teste ale harness-ului,
un test AST/structural nou, un defect real de orchestrare găsit-și-corectat DUPĂ prima livrare (v. §3),
și metricile extinse ale rulării de construcție (percentile IoU, întârziere confirm_ts, distribuția
completă a stărilor, funnel-ul complet al respingerilor, cele 6 exemple explicit cerute).

---

## 1 — Verificare obligatorie înainte de cod (§1 mandat)

| sursă citată | commit/hash | verificat | notă |
|---|---|---|---|
| pachet Statistician | `d6e599e` | ✔ exact, deja citit integral în mandatul anterior | |
| manifest v2.7.94 | `14d4c22` | ✔ | |
| fingerprint | `a5d69e2d…` | ✔ recalculat independent | |
| contract V4.2 anterior | `5a9d5ec` | ✔ există, **strămoș direct al lui `d6e599e`** (`git merge-base --is-ancestor` = YES) | deja inclus în pachetul final |
| fișa parametrilor V4.2 | `4684e66` | ✔ există, **strămoș direct al lui `d6e599e`** | idem |
| audit/config V4.2 | `b8cf2a7` | ✔ există, **strămoș direct al lui `d6e599e`** | idem |
| Red Team RT-RANGE-0006 | `2c113ef` | ✔, verdict `RANGE_V4_IMPLEMENTATION_PACKAGE_STATIC_PASS` confirmat | |
| harness | `range_v42_contract_harness.py` @`d6e599e` | ✔ SHA-256 recalculat, identic cu livrarea anterioară | |
| teste contractuale | `test_range_v42_adversarial.py` @`d6e599e` | ✔ rulat DIRECT încă o dată (nu doar citit) — 79 PASS / 0 FAIL | |
| mapping 114 segmente | `BLIND_BATCH_02_LEVEL_MAPPING.md` | ✔ 88 MACRO + 26 UNRESOLVED + 12 INTERNAL = 126 rânduri, parsate programatic | |
| local = remote, toate oglinzile | `alpha1`/`discovery`/`lab`/`trader` | ✔ toate 4 identice cu HEAD-ul local înainte de a începe | |

**Cele 3 surse noi citate în acest mandat (`5a9d5ec`/`4684e66`/`b8cf2a7`) sunt strămoși direcți ai
`d6e599e`** — deja incorporate integral în pachetul pe care implementarea existentă îl folosește ca
sursă normativă. Nicio contradicție reală găsită. **Nu s-a oprit implementarea.**

### Lista consolidată de blocante găsite (§1: "o singură listă, nu una câte una")

Niciun blocant real. O singură discrepanță de documentație, fără impact funcțional, raportată transparent:

- **§2 al acestui mandat cere extragerea și folosirea a patru câmpuri de identitate suplimentare —
  `schema_version`, `snapshot_version`, `config_version`, `reason_code_set_version`.** Căutare
  exhaustivă (harness, pachetul de implementare, manifest) confirmă că **niciunul dintre aceste patru
  nume nu există ca literal distinct în sursele normative deja verificate** — singurele câmpuri de
  identitate REAL folosite de contract pentru fail-closed matching la `snapshot`/`restore` sunt
  `contract_version` și `config_id` (verificat direct în textul pachetului: *"`snapshot`/`restore`
  refuză fail-closed la nepotrivire de `contract_version` **sau** `config_id`"*). Conform interdicției
  explicite a acestui mandat ("Nu inventa și nu deduce alte versiuni"), **nu s-au inventat valori
  pentru cele patru câmpuri absente**. Implementarea folosește exact cele două câmpuri normative
  existente, deja verificate byte-exact (`config_id` = `24f72a60…3826da`).

---

## 2 — Identitate normativă (§2 mandat)

| câmp cerut | valoare | sursă |
|---|---|---|
| `contract_version` | `"range-hierarchical-v4.3"` | normativ, folosit ca-atare |
| `config_id` | `24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da` | recalculat de `ConfigV43.config_id()`, byte-identic cu normativul |
| `schema_version` / `snapshot_version` / `config_version` / `reason_code_set_version` | **inexistente în sursa normativă** | v. §1 — nu s-au inventat |
| fingerprint manifest | `a5d69e2d0150d7ca2cf750df49f65cfc55b91fa89d13568fa42f81a48f4ee565` | verificat |

V4.3 supersedează V4.2 (`5a9d5ec`) prin cele 17 corecții C1-C17 din pachetul `d6e599e` — toate
incluse; niciun modul nou nu poartă `v42` în nume (`range_semantic_v4_3.py`/`range_engine_v4_3.py`).

---

## 3 — Defect nou găsit ȘI CORECTAT în această trecere (înainte de îngheț)

**`LIQUIDITY_SWEEP_REVERSAL` (corecția C13) era portată fidel ca funcție pură
(`sweep_reversal_confirmed`) și testată DIRECT, dar nu era apelată NICĂIERI din bucla per-bară a
producătorului** (`RangeSemanticProducerV43.observe`/`_step_depth`). Verificat abia acum, prin
căutarea explicită a apelurilor reale ale funcției (nu doar a apariției numelui constantei în sursă —
testul AST din §5b NU putea singur prinde acest defect, fiindcă funcția pură însăși referențiază
constanta corect; doar nimeni nu o mai chema). Consecință: `LIQUIDITY_SWEEP_REVERSAL` nu putea fi
emis NICIODATĂ prin observare reală bară-cu-bară, doar prin apel manual al funcției — o formă mai
slabă de "reachability" decât cere mandatul.

**Fix** (`range_semantic_v4_3.py`, aditiv, izolat): un "reversal watch" nou (`_macro_reversal_watch`/
`_internal_reversal_watch`), populat la exact momentul `SWEEP_CONFIRMED` (separat de slot-ul de
excursie activă, care trebuie golit ca o excursie nouă să poată deschide), verificat în fiecare bară
ulterioară prin `_check_reversal_watch` — apelând EXACT funcția pură deja portată și testată, fără
nicio modificare a semanticii ei. `episode_end_ts` se verifică dinamic (nu memorat static la creare):
`None` cât timp structura e activă, `end_ts` real dacă s-a închis între timp, fail-closed (tratat ca
deja expirat) dacă structura a fost evacuată din istoricul mărginit (`maxlen=64`) înainte ca
reversal-ul să se rezolve — caz extrem de improbabil, dar tratat explicit. Persistat integral în
`snapshot_state`/`restore_state`.

**Verificare end-to-end**: fixture-ul HBL-20 deja validat (nu unul nou, izolat) produce acum
`LIQUIDITY_SWEEP_REVERSAL` prin `observe()` la bara 75 — test nou dedicat
`test_hbl20_liquidity_sweep_reversal_reachable_via_observe`. Re-rulat pe corpusul de construcție
(48 ferestre): **21 emiteri** de `LIQUIDITY_SWEEP_REVERSAL`, de la 0 înainte de fix. Recall/precision/
IoU pe segmente MACRO/INTERNAL **neschimbate** (fix-ul adaugă un eveniment nou, nu modifică formarea/
confirmarea structurilor). mypy `--strict` clean, 370/370 teste (368 anterior + 2 noi), 0 regresii.

Această corecție s-a produs **înainte** de declararea `PROTOTYPE_PRE_RUN_FROZEN` (§8 mai jos) — deci
respectă disciplina §14 a mandatului anterior (fix real de orchestrare, nu reacție post-îngheț la
rezultate).

---

## 4 — Matrice contract → cod → test

| clauză contract | implementare | test(e) |
|---|---|---|
| §2 (V4.3, nu V4.2) | `RANGE_HIERARCHICAL_V4_3_CONTRACT_VERSION`, module `*_v4_3.py` | config identity tests |
| §4 config CEO-fixată | `ConfigV43` (frozen dataclass) | `test_config_id_matches_normative`, bounds tests |
| §5 MACRO/INTERNAL, MICRO nereprezentabil | `Depth` enum (2 valori), `assign_level` R1/R2/R3 + C14 | 3rd-level-refused tests (direct + via producer) |
| §6 frontiere înghețate | `Cluster.frozen`, `zones()` gate pe `reached_confirmed` | zone-freeze fixture tests |
| §7 sweep/breakout/promovare | `Excursion`, `evaluate_candidate`, `promotion_check` | items 12-17 |
| §8 promovare | `_maybe_promote`, `_promo_fired` | bullish/bearish promotion tests |
| §9 roluri retrospective | `Structure.assign_role`, `_resolve_role_if_watched` | HBL-20 + role-timing tests |
| §10 conjuncție + priorități | `evaluate_candidate_with_n_touch` | non-vacuity gates (13) |
| §11 snapshot/restore | `snapshot_state`/`restore_state`, fail-closed pe `contract_version`+`config_id` | snapshot-in-every-state (5 fracții) + legacy/corrupted refusal |
| §12 teste | v. §5-6 mai jos | |
| §13 complexitate O(n) | `_RunningMedian`, `_UnboundedSlope` (fără evicție, fără re-scanare) | `RANGE_V4_3_PERFORMANCE_REPORT.md` |
| §15 run corpus | `run_construction.py` + `synth.py` | v. §7 mai jos |

---

## 5 — Descompunerea exactă a celor 79 de teste ale harness-ului (§12 iteme 3-6)

Re-rulat DIRECT (nu doar citit) în această trecere, prin execuție instrumentată a fișierului sursă
(nu comparație de liste hardcodate):

| grup | interval nume | count | rezultat |
|---|---|---:|---|
| cazuri adversariale (§E, itemele 1-16 din harness) | `1a`…`16b` | **39** | 39 PASS |
| grupe suplimentare (itemele 17-20: C13/C14/C15-17/acoperire coduri) | `17a`…`20c` | **27** | 27 PASS |
| porți de nevacuitate (§D) | `nevacuu: *` | **13** | 13 PASS |
| **TOTAL** | | **79** | **79 PASS / 0 FAIL** |

Fiecare din cele 13 porți de nevacuitate verifică ATÂT trecerea CÂT ȘI eșecul (dicționar `gates` cu
tuple `(pass_case, fail_case)`, o singură buclă `check()` per poartă — 13 chei exacte, confirmate
prin citirea directă a sursei: durata MACRO, durata INTERNAL, degenerare zone, inversare zone, sweep,
breakout acceptat, apartenență cluster, nivel INTERNAL, nivel UNRESOLVED, clasificare canal, rol
retrospectiv, reversal după sweep, limită de adâncime).

---

## 5b — Testul AST/structural (§12, cerință nouă)

`test_reason_codes_ast_structural_reachability` (nou, `tests/test_range_semantic_v4_3.py`): parsează
`range_semantic_v4_3.py` cu `ast`, verifică fiecare din cele 29 de constante de reason code e
referențiată (`ast.Name`, context Load) cel puțin O DATĂ în afara propriei declarații și a tuplului
`REASONS_V43` — adică folosită efectiv într-o comparație/return/append/raise reală. Contorizare directă
per cod: minim 2 referințe (`SWING_OUTSIDE_CLUSTER`, cele 4 `PROMOTION_REFUSED_PRECONDITION_P*`, etc.),
maxim 11 (`BREAKOUT_ACCEPTED`). **Notă onestă despre limita acestui test**: el demonstrează că un
cod NU e complet izolat sintactic, dar NU demonstrează că funcția care-l conține e ea însăși apelată
de motorul per-bară — exact clasa de defect găsită și corectată la §3 (funcția pură referenția corect
constanta; nimeni n-o mai chema). Cele două verificări sunt complementare, nu una o înlocuiește pe
cealaltă.

---

## 6 — Matrice PASS/FAIL pe cele 19 iteme din §12

| # | item | rezultat | dovadă |
|---:|---|---|---|
| 1 | toate testele istorice `ve_n1_replay` | PASS | 320/320 baseline, 0.4.1 byte-neatins |
| 2 | mypy `--strict` pe fișiere noi | PASS | `range_semantic_v4_3.py`, `range_engine_v4_3.py`, `test_range_semantic_v4_3.py` — 0 erori |
| 3 | 79 teste harness | PASS | §5, 79/79 |
| 4 | 16 cazuri adversariale | PASS | §5, 39 check-uri (16 grupe) |
| 5 | 4 grupe suplimentare | PASS | §5, 27 check-uri (grupele 17-20) |
| 6 | 13 porți de nevacuitate | PASS | §5, 13/13 |
| 7 | reachability dinamic 29 coduri | PASS | `test_all_29_reason_codes_reachable_via_public_api` + §5b AST |
| 8 | determinism | PASS | `run43_fixed_atr` repetabil bit-identic pe fixture-uri calibrate |
| 9 | chunk invariance | PASS | parametrizat, 5 fracții |
| 10 | două instanțe fără stare comună | PASS | test dedicat |
| 11 | zero lookahead | PASS | test dedicat |
| 12 | snapshot/restart bit-identic | PASS | 5 fracții pe HBL-20 |
| 13 | granițele rămân înghețate | PASS | fixture zone-freeze + §3 audit |
| 14 | INTERNAL nu omoară MACRO | PASS | `1c`/`2b` harness + 8 ferestre din corpus (§7) cu internal+macro confirmate simultan |
| 15 | al treilea nivel refuzat | PASS | direct + via producer |
| 16 | breakout nu șterge episodul anterior | PASS | `macro_history` păstrează toate episoadele închise |
| 17 | roluri retrospective nu apar înainte de `role_known_ts` | PASS | `assign_role` refuză explicit |
| 18 | HBL-20 | PASS | narativ complet + acum și reversal (§3) |
| 19 | complexitate/memorie | PASS | `RANGE_V4_3_PERFORMANCE_REPORT.md`, 355.696 bare, cost/bară plat |

**19/19 PASS.** Niciun item marcat FAIL sau SKIP.

---

## 7 — Rulare pe corpusul de construcție CEO_ASSISTED (§15, extins)

Corpus: 48 ferestre `BLIND-001…048`, XAUUSD M15, 16 pe fiecare lungime (96/288/480) = **13.824 bare
total** (corectat față de o cifră greșită menționată doar conversațional în livrarea anterioară —
niciun fișier livrat conținea cifra greșită, verificat). 114 segmente RANGE nivel 1 (88 MACRO + 26
UNRESOLVED) + 12 INTERNAL nivel 2, conform `BLIND_BATCH_02_LEVEL_MAPPING.md`. **Nu e corpus blind,
nu e OOS** — exact cum specifică acest mandat (§15) — provenența etichetelor e `CEO_ASSISTED`/
`CEO_INDEPENDENT_BLIND_LABEL_WITH_POST_LOCK_ASSISTANT_REVIEW` (vezi `labeling_provenance` din JSON).
Sintetizat MECANIC din etichetele deja publicate (nu bare reale — verificat separat, §0 din
`RANGE_V4_3_CONSTRUCTION_REPORT.md`, că barele reale rămân inaccesibile VE).

### Structuri detectate

| nivel | GT | detectate (confirmate+neconfirmate) | confirmate | potrivite (IoU>0) cu GT |
|---|---:|---:|---:|---:|
| MACRO | 88 | 151 | 119 | 57 |
| INTERNAL | 12 | 16 | 9 | 2 |

### Recall / Precision / IoU

| | recall | precision | IoU mediu | IoU p25 | IoU mediană | IoU p75 | IoU max |
|---|---:|---:|---:|---:|---:|---:|---:|
| MACRO | 0,648 | 0,445 | 0,641 | 0,390 | **0,770** | 0,881 | 0,990 |
| INTERNAL | 0,167 | 0,111 | 0,249 | 0,154 | 0,249 | 0,345 | 0,440 |

Mediana MACRO (0,770) e semnificativ mai bună decât media (0,641) — media e trasă în jos de câteva
potriviri slabe; majoritatea potrivirilor sunt de fapt destul de bune.

### Eroare start/end și întârziere confirm_ts

| | eroare start medie (bare) | eroare end medie (bare) | confirm_ts delay: medie | mediană | min | max |
|---|---:|---:|---:|---:|---:|---:|
| MACRO | 17,6 | 22,6 | 38,5 | **29,0** | 29 | 134 |
| INTERNAL | 23,0 | 23,0 | 15,0 | 15,0 | 15 | 15 |

Mediana întârzierii de confirmare MACRO e **exact `d_macro=29`** — poarta de durată e constrângerea
dominantă, nu o eroare de detecție; motorul confirmă cât de repede permite contractul.

**Eroare boundary în unități ATR — NECALCULABILĂ din datele disponibile**: etichetele publicate
(`LEVEL_MAPPING.md`, `PART1-4.json`) conțin bare-index și clasă, NU niveluri de preț reale (cu excepția
câtorva adnotări aproximative `lower`/`upper`, prezente doar pe o minoritate de segmente și folosite
deja ca ancoră de sintetizare — comparația ar fi circulară). Aceeași limitare structurală ca la
absența barelor reale (§0): nu s-a inventat o valoare.

### Distribuție pe lungime și bloc (MACRO, potrivite/GT)

| 96 bare | 288 bare | 480 bare |
|---:|---:|---:|
| 12/25 (48%) | 28/33 (85%) | 17/30 (57%) |

| B1 | B2 | B3 | B4 |
|---:|---:|---:|---:|
| 14/24 | 18/22 | 15/19 | 10/23 |

### Confuzie RANGE/CHANNEL/TREND

Corpusul nu conține nicio etichetă TREND (verificat exhaustiv pe toate cele 276 de segmente brute).
Matrice completă imposibilă din acest lot — v. `RANGE_V4_3_CONSTRUCTION_REPORT.md` §4 pt. proxy-ul
raportat deja (46/57 MACRO-uri potrivite s-au închis prin `BREAKOUT_ACCEPTED`).

### Sweep-uri, breakout-uri, reversal, promovări

| eveniment | nr. |
|---|---:|
| `SWEEP_CONFIRMED` | 209 |
| `BREAKOUT_ACCEPTED` | 112 |
| `LIQUIDITY_SWEEP_REVERSAL` | **21** (0 înainte de fix-ul §3) |
| `IS_TREND_MACRO` (promovări) | 94 |
| `ZONES_DEGENERATE` | 2 |

Failed breakout: nu există cod separat `FAILED_BREAKOUT` în contract — conceptul din §7 e implementat
prin `SWEEP_CONFIRMED` (excursie rezolvată prin reintrare, fără acceptarea breakout-ului).

### Funnel complet al formării de candidați (`assign_level`)

| | nr. |
|---|---:|
| încercări totale | 725 |
| → MACRO create | 151 |
| → INTERNAL create | 16 |
| → refuzate `PARTIAL_OVERLAP_NO_CONTAINMENT` | 558 |
| → refuzate `DEPTH_LIMIT_EXCEEDED` | 0 |
| → refuzate `LEVEL_ASSIGNMENT_UNRESOLVED` | 0 |
| **rată de succes formare** | **23,0%** |

Ambele coduri de refuz `DEPTH_LIMIT_EXCEEDED`/`LEVEL_ASSIGNMENT_UNRESOLVED` sunt implementate și
demonstrate reachable prin teste unitare directe (§6, item 15/harness item 18) — pur și simplu nu s-au
declanșat în ACEST corpus sintetic particular (0 apariții e o observație, nu o eroare).

### Distribuția completă a stărilor (bare, 13.824 total pe MACRO)

| stare | bare | % |
|---|---:|---:|
| `RANGE_FORMING` | 7303 | 52,8% |
| `RANGE_CONFIRMED` | 4450 | 32,2% |
| `BOUNDARY_EXCURSION` | 433 | 3,1% |
| `SWEEP_CONFIRMED` | 203 | 1,5% |
| `TREND_DOWN` | 239 | 1,7% |
| `TREND_UP` | 175 | 1,3% |
| `EPISODE_CLOSED` | 53 | 0,4% |
| (niciun candidat) | 968 | 7,0% |

INTERNAL: 92,9% din bare fără candidat activ (`None`), restul dominat de `INT_CHANNEL_UP` (501),
`INT_BALANCE` (196), `INT_CHANNEL_DOWN` (192), `INT_SUBRANGE` (23).

### Segmente pierdute + motiv, cazuri UNRESOLVED

Detaliu complet, per-fereastră, în `RANGE_V4_3_CONSTRUCTION_REPORT.md` §6/§6b/§7 (31 MACRO + 10
INTERNAL nepotrivite, cu motiv structural per caz; 26 UNRESOLVED în 8 ferestre, raportate separat,
niciodată scorate).

### Cele 6 exemple explicit cerute (§15, ultimul paragraf)

| exemplu cerut | verificat | dovadă |
|---|---|---|
| RANGE MACRO cu channel intern (up/down) | ✔ | `BLIND-034`: `RANGE_CONFIRMED` (MACRO) simultan cu `INT_CHANNEL_DOWN` (internal) la finalul ferestrei; + teste unitare dedicate `test_e2e_macro_with_channel_up/down_internal` |
| RANGE cu sub-range intern | ✔ | 23 bare `INT_SUBRANGE` observate în corpus (agregat, nicio fereastră nu s-a ÎNCHEIAT în această stare) + test unitar dedicat `test_e2e_macro_with_subrange_internal` (confirmare completă, nu doar tranzitorie) |
| sweep de lichiditate + mișcare agresivă opusă | ✔ | 21 emiteri `LIQUIDITY_SWEEP_REVERSAL` în corpus (§3, fix nou) + `test_hbl20_liquidity_sweep_reversal_reachable_via_observe` |
| acumulare → manipulare → distribuție/markup | ✔ | HBL-20 complet: `BALANCE → SWEEP_DOWN → REENTRY_CONFIRMED → BULLISH_STRUCTURE_BREAK → MARKUP → ACCUMULATION_CONFIRMED`, `test_hbl20_full_narrative_accumulation` |
| breakout urmat de nou RANGE | ✔ | `BLIND-001` `macro_history`: `[(1,3,32,55,BREAKOUT_ACCEPTED),(2,51,80,137,BREAKOUT_ACCEPTED),(3,137,166,200,...),...]` — episoade succesive legate prin `predecessor_id`, niciodată suprapuse |
| INTERNAL nu distruge RANGE MACRO | ✔ | 8 ferestre (`BLIND-004/008/028/030/032/037/040/047`) cu INTERNAL și MACRO confirmate SIMULTAN; harness `1c`/`2b` (macro.end_ts rămâne None) |

**Rezultatul NU e BLIND PASS** — sintetizat din aceleași etichete cu care e comparat.

---

## 8 — Îngheț (§14 mandat)

```text
cod fingerprint (SHA-256):
  range_semantic_v4_3.py  2aba333c413c484f8ff85c91180e29f852834475d982ab4f4a5c32120ccb238b
  range_engine_v4_3.py    84dac346524591fdfe904cd0dde0f1d8888161cdffe62dcd7129cff6eea1c1f2
config_id: 24f72a60fcde42746d44f098558a745fac0f20b0141865bdbe0359f9cc3826da (byte-identic normativ)
contract_version: range-hierarchical-v4.3
```

**`PROTOTYPE_PRE_RUN_FROZEN`** declarat la commit-ul acestei livrări (v. §9). Nicio modificare de
semantică/parametri după acest punct. Corecția din §3 s-a produs ÎNAINTE de acest îngheț (parte din
finalizarea implementării, nu reacție post-run) — rularea de construcție raportată la §7 folosește
codul deja fixat.

---

## 9 — Livrare (§17)

- Fișiere noi: `range_semantic_v4_3.py`, `range_engine_v4_3.py`, `tests/test_range_semantic_v4_3.py`,
  `RANGE_V4_3_CONSTRUCTION_REPORT.md`, `RANGE_V4_3_PERFORMANCE_REPORT.md`,
  `RANGE_V4_3_REAL_PROTOTYPE_DELIVERY_REPORT.md` (acest fișier).
- Fișiere modificate ADITIV: `__init__.py`, `version.py` (0 ștergeri, verificat `git diff`).
- Dovadă generații anterioare byte-identice: 0.4.1 rămâne neatins; rollback verificat prin `git stash`
  + rulare izolată 320/320 pe arborele fără V4.3 (livrarea anterioară, neschimbat aici).
- Toate rezultatele testelor: §5/§5b/§6 de mai sus (370/370 total, 0 regresii).
- Benchmark: `RANGE_V4_3_PERFORMANCE_REPORT.md` (neschimbat, fix-ul din §3 nu adaugă cost per-bară
  material — un dicționar nou verificat O(1), o funcție pură deja O(1)).
- Output brut + tabele run construction: §7 de mai sus + `construction_run_results.json` (artefact
  local, nu comis — derivabil determinist din codul comis + etichetele deja comise).
- Fingerprint cod/config: §8.
- Commit pre-run înghețat + commit rezultat: v. istoricul git (acest commit conține AMBELE — fix-ul
  §3 și metricile extinse §7 împreună, fiindcă rularea corpusului s-a făcut DUPĂ fix, ÎNAINTE de commit).
- Push pe toate oglinzile + hash local=remote: verificat după commit (v. mesaj de livrare).
- Actualizare `PROJECT_STATE.md`/memory: v. bullet nou, prepend, `ve_n1_replay 0.4.1` neatins.
- Notificare Telegram: obligatorie, trimisă după push (v. confirmare HTTP).

## 10 — Interpretare (§16)

Nu se declară `BLIND_PASS`, `SEMANTIC_PASS`, `STRATEGY_CATALOG_READY`, `ALPHA_AUTHORIZED`,
`AI_TRADER_INTEGRATION_READY`, `LIVE_SHADOW_READY`. Implementarea și testele sunt complete:

```text
RANGE_V4_3_PROTOTYPE_RESULTS_READY_FOR_CEO_REVIEW
self_declared_pass = false
```

Niciun wheel construit. Niciun parametru modificat pt. a crește artificial numărul de range-uri
(config identic celui livrat prima dată, `config_id` neschimbat). Următorul proprietar: Red Team,
pentru auditul implementării reale.
