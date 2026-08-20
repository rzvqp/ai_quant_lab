# RANGE V4 — F1-Only Remediation After RT-RANGE-0012 (mandat "RANGE V4 F1-ONLY REMEDIATION AFTER RT-RANGE-0012")

Status final: **`RANGE_V4_F1_ONLY_REMEDIATION_READY_FOR_RED_TEAM_AUDIT`**, `self_declared_pass=false`.

CEO a ales remedierea (b) din RT-RANGE-0012: **F1 SINGUR, F5 AMÂNAT COMPLET.** Acest livrabil e un
commit NOU (nu un amendament la `69af414`, care rămâne istoric neatins) ce (1) păstrează comportamentul
F1 validat de Red Team, (2) revine gardul de re-testare a frontierei MACRO la forma EXACTĂ pre-F5, (3)
păstrează MACRO congelat, (4) actualizează identitatea de implementare corect, (5) e pregătit pt.
re-audit îngust.

`MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED = FALSE` — doar Red Team poate elibera acest gate.

## 0 — Parent, sursă de autoritate, verificare

- **Părinte exact:** `82f27c0` (runner-ul reproductibil, F5-liber) → `69af414` (F1+F5, RESPINS) →
  **acest commit** (F1-only). Acest commit e copil direct al `69af414` în istoricul git (nu s-a făcut
  `git revert`/rebase — istoria rămâne intactă, cerută explicit de mandat).
- **Autoritate:** RT-RANGE-0012 (commit `892355f`, ledger E87) — verificat existent (`git cat-file -t`),
  citit integral la commit-ul exact citat (194 linii, `red_team/policy_reviews/
  RT-RANGE-0012_f1_f5_implementation_audit.md`). Trăiește pe branch-ul `statistician-foundation`
  (nu `discovery-mk-matrix-v1`) — verificat `git branch -a --contains 892355f`.
- **local=remote confirmat pe toate 4 remote-urile** (alpha1/discovery/lab/trader) ÎNAINTE de orice
  editare, pe branch-ul de lucru `discovery-mk-matrix-v1` (HEAD `69af414` pe toate patru, byte-identic).
- Toate commit-urile citate de mandat verificate existente: `892355f`, `46a9576`, `82f27c0`, `69af414`.

## 1 — Diff exact `82f27c0` → `69af414` (dovadă, nu presupunere)

```
 ve_n1_replay/blind_runner/inference.py             |  33 +-
 ve_n1_replay/blind_runner/schemas.py               | 129 +++++++-
 ve_n1_replay/blind_runner/scoring.py               |   6 +-
 ve_n1_replay/blind_runner/tests/test_f1_ohlc_tolerance.py   | 240 ++++++++++++++
 ve_n1_replay/blind_runner/tests/test_schemas.py    |   3 +-
 ve_n1_replay/tests/test_f5_tol_cluster_units.py    | 365 +++++++++++++++++++++
 ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py   |  36 +-
```

Decompus independent (nu pe cuvântul mandatului) în exact 6 categorii, verificate hunk-cu-hunk:

| Categorie | Fișier(e) | Acțiune în acest livrabil |
|---|---|---|
| F1 (validator complet) | `schemas.py` | **PĂSTRAT nemodificat** — 0 diff față de `69af414` |
| F1 (wiring input_quality_events, manifest) | `inference.py` | **PĂSTRAT** — doar identitatea (trio frozen) s-a schimbat |
| F5 comportamental (linia gardului, `× atr_ref`) | `range_semantic_v4_3.py` | **REVERTAT** la forma exactă `82f27c0` |
| fingerprint/snapshot (constantă + `snapshot_state`/`restore_state`) | `range_semantic_v4_3.py` | **PĂSTRAT mecanismul, SCHIMBATĂ valoarea** — mandatul interzice explicit revertarea oarbă |
| identitate scoring (2 literale) | `scoring.py` | **PĂSTRAT mecanismul, SCHIMBATĂ valoarea** — 0 schimbare de algoritm |
| teste | `test_f1_ohlc_tolerance.py`, `test_schemas.py`, `test_f5_tol_cluster_units.py` | primele 2 **PĂSTRATE**; al treilea **ȘTERS** (testa exclusiv comportamentul F5 revertat) + înlocuit cu `test_f1_only_macro_identity.py` nou |

## 2 — A. F1 — păstrat exact

Zero modificări la `blind_runner/schemas.py` (`git diff` gol față de `69af414`). Comportamentul
RT-RANGE-0012-validat rămâne intact prin construcție (fișierul nu a fost atins), nu doar prin afirmație:
- `SYMBOL_MIN_TICK["XAUUSD"]=0.01` → `epsilon=0.005`
- comparație valoare-vs-frontieră-deplasată
- toleranță exactă la frontieră + respingere la +1 ULP dincolo de ambele frontiere
- eșec fail-closed pe simbol necunoscut
- `INPUT_OHLC_SUBTICK_TOLERATED` — canal separat de reason codes-urile semantice
- OHLC original complet nemodificat
- `input_quality_events` separat de predicțiile semantice

`blind_runner/tests/test_f1_ohlc_tolerance.py` (26 teste) — **26/26 PASS, nemodificat**.
`F1_OHLC_BYTE_IDENTITY` și `F1_ONLY_PATCHED_CLI_PREDICTIONS_MATCH_FREEZE` au fost deja stabilite
`TRUE` de Red Team direct (RT-RANGE-0012 §2, hash `62273c1e…`, 48/48) — VE nu are de ce să le
re-revendice, mecanismul care le-a produs (validatorul F1) e neatins.

## 3 — B. F5 — eliminat din candidat, `DEFERRED_RESEARCH_ONLY_NON_BLOCKING`

Linia comportamentală (fostă `range_semantic_v4_3.py` ~linia 774 în `69af414`) revertată EXACT:

```python
# 69af414 (RESPINS):
atr_ref = self._active_macro.atr_ref
if boundary is not None and atr_ref is not None and abs(price - boundary) <= self._cfg.tol_cluster * atr_ref:
    return

# acest commit (F1-only):
if boundary is not None and abs(price - boundary) <= self._cfg.tol_cluster:
    return
```

Verificat caracter-cu-caracter identic cu `82f27c0` (extras direct din blob-ul git, nu din memorie):
vezi §6 mai jos pt. dovada completă. Nu s-a: redesenat F5; introdus logică INTERNAL alternativă;
patch-uit comportamentul de promovare; modificat starea partajată pt. izolare; ajustat `tol_cluster`;
schimbat `d_internal`; schimbat semantica touch/retest; adăugat un al treilea nivel de ierarhie —
niciuna dintre acestea nu apare în diff (§8, scanare grep completă).

F5 e înregistrat explicit: **`DEFERRED_RESEARCH_ONLY_NON_BLOCKING`** — comentariul din cod (linia ~759)
citează RT-RANGE-0012/`892355f`/E87 și explică mecanismul leak-ului (contor de structure-id partajat,
promovare INTERNAL→MACRO, stare pending-swing partajată) pt. orice viitoare încercare de redesign.

## 4 — C. Identitate de implementare

Mandatul interzice explicit revertarea oarbă a infrastructurii de fingerprint. Aici:
- **Mecanismul** (`RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT` ca și constantă, participarea în
  `snapshot_state`/`restore_state`) **rămâne** — un fișier revertat orb la bytes-ul `f224e7d` ar fi lăsat
  un snapshot din pachetul RESPINS F1+F5 (sau un snapshot ȘI MAI vechi, pre-F1) restaurabil silențios
  aici, din moment ce `contract_version`+`config_id` nu s-au schimbat NICIODATĂ în niciuna dintre aceste
  variante.
- **Valoarea** s-a schimbat la `"f1-only-f5-deferred-2026-08-20"` — nu `f224e7d` gol (fișierul nu e
  byte-identic — vezi §6), nu `"f1-f5-conformance-2026-08-20"` (pachetul RESPINS).
- `FROZEN_PROTOTYPE_COMMIT` (`inference.py`): `"f224e7d+F1F5"` → **`"f224e7d+F1"`**.
- `FROZEN_HASHES["range_semantic_v4_3.py"]`: `70e30b3a…9999` (F1+F5) → **`098fa144…41fbc`** (F1-only,
  calculat DUPĂ finalizare+testare, disciplina de îngheț învățată din RT-RANGE-0007).
- `range_engine_v4_3.py` — **confirmat neatins** (`84dac346…1c1f2`, identic pe tot parcursul, verificat
  din nou acum).
- `scoring.py`: cele două verificări literale actualizate la aceleași valori noi — **0 schimbare de
  algoritm/logică de scorare** (confirmat: diff-ul e strict 2 string-uri).
- Testat matricea completă de compatibilitate snapshot — vezi §7.

## 5 — Poarta `PATCHED_CLI_PREDICTIONS_MATCH_FREEZE` — deja stabilită TRUE de Red Team

Spre deosebire de mandatul F1+F5 anterior (unde am raportat `NOT_VERIFIABLE_HERE`), RT-RANGE-0012 §2 a
stabilit deja direct: **`F1_ONLY_PATCHED_CLI_PREDICTIONS_MATCH_FREEZE = TRUE`** — rulând validatorul F1
+ detectorul PRE-F5 pe barele reale, reproduce `46a9576` exact 48/48, hash `62273c1e…`. Acest livrabil
nu schimbă validatorul F1 și revine detectorul la forma pre-F5 exactă — deci mecanismul care a produs
acel rezultat rămâne intact prin construcție. Nu revendic din nou verificarea (tot nu am acces la
escrow — vezi §6), dar nici nu contrazic sau slăbesc dovada deja stabilită de Red Team.

## 6 — D. MACRO FREEZE — dovadă structurală + comportamentală ne-vacuă

**Escrow rămâne indisponibil pt. VE la acest mandat** — verificat explicit acum (nu presupus din
mandate anterioare): `ESCROW_DIR` nesetat; totuși un director cu formă de escrow EXISTĂ local
(`~/escrow_red_team/`, cu `escrow_key_v3.bin`/`escrow_tool.py`/`payload-b7e103a3d9b86f72.bin`) —
**deliberat necitit**. Rolul VE în acest proiect e definit structural să nu consume conținutul escrow,
indiferent de accesibilitate la nivel de sistem de fișiere; acest mandat nu schimbă acel rol (nu conține
nicio instrucțiune care acordă acces VE) — deci poarta pe bare reale rămâne **`NOT_VERIFIABLE_HERE`**,
raportată onest, nu fabricată. Nimic din reproducerea real-bar de mai jos a fost derivat din, sau
verificat contra, acel director.

În lipsa accesului, două dovezi INDEPENDENTE, ambele ne-vacue (spre deosebire de testul șters, care
rula EXCLUSIV la `atr=1,0`, exact punctul la care scalarea F5 devenea no-op):

### 6.1 — Dovadă STRUCTURALĂ (acoperire completă, nu eșantionată)

`git diff 82f27c0 -- ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py` (față de starea de LUCRU curentă,
nu față de `69af414`) arată EXACT trei categorii de diferență, NICIUNA executată în timpul `observe()`:

1. Constanta de fingerprint + docstring-ul ei + intrarea în `__all__` (citită NICIODATĂ în calea de
   procesare a barelor).
2. Un bloc de comentarii deasupra gardului (comentarii, zero diferență executabilă).
3. Două linii ADITIVE în `snapshot_state()`/`restore_state()` (afectează DOAR identitatea de
   serializare, niciodată calculul semantic din `observe()`).

Linia executabilă a gardului însăși (`if boundary is not None and abs(price - boundary) <=
self._cfg.tol_cluster: return`) **NU apare deloc în diff** — dovadă directă că e byte-identică cu
`82f27c0`. Verificat de două ori: (a) `git diff 82f27c0 -- <fișier>` (compară commit-ul cu working
tree, ține cont de normalizarea EOL a repo-ului) și (b) un test comis, permanent
(`test_boundary_retest_guard_is_byte_identical_to_pre_f5_82f27c0_source`), care verifică textul extras
o singură dată din blob-ul `82f27c0` ca substring exact în sursa curentă — dacă acest test trece,
NICIO valoare de ATR ar putea vreodată demonstra o diferență comportamentală în acest gard, pt. că nu
există cod diferit de rulat.

Această dovadă e STRICT mai puternică decât orice test comportamental eșantionat: acoperă fiecare
intrare posibilă, nu un set ales.

### 6.2 — Dovadă COMPORTAMENTALĂ, ne-vacuă (defense-in-depth, răspunde direct §2 din RT-RANGE-0012)

`tests/test_f1_only_macro_identity.py` (nou, înlocuiește fișierul șters):
- `test_retest_guard_outcome_identical_across_five_distinct_atr_values` +
  `test_retest_guard_filters_within_raw_tol_cluster_across_five_distinct_atr_values`: gardul exercitat
  DIRECT la cinci valori ATR distincte (0,65/1,0/1,85/3,2/10,0 — sub/în jurul/mult peste mediana ATR14
  reală XAUUSD M15 ~1,87), demonstrând că rezultatul accept/respins nu mai depinde deloc de ATR.
- `test_macro_projection_hash_at_non_unit_atr` (parametrizat pe aceleași 5 valori): proiecția MACRO
  completă peste cele 48 ferestre sintetice de construcție (reutilizate STRICT pt. diversitate
  structurală de regresie, NU reproducere istorică — acel rol rămâne al `construction_reproduction/`,
  pinnat separat la `f224e7d`), hash SHA-256 ancorat PER valoare ATR:

  | ATR | hash proiecție MACRO | evenimente MACRO |
  |---|---|---|
  | 0.65 | `4ec40a81b2f1…069e91` | 801 |
  | 1.0 | `81b0a7b3336d…c942591` | 973 |
  | 1.85 | `9d80775db970…c8baa0` | 940 |
  | 3.2 | `ef443e311ff1…ca00a7` | 973 |
  | 10.0 | `439da0c11316…f04e327f` | 1231 |

  Notă importantă: ancora la `atr=1,0` COINCIDE exact cu cea calculată în mandatul F1+F5 (dovadă
  independentă că `atr=1,0` nu poate distinge "F5 prezent" de "F5 absent" — motivul exact al vacuității
  găsite de Red Team). Celelalte patru valori NU au fost niciodată calculate pe pachetul F1+F5 și sunt
  dovada nouă, ne-vacuă.
- 24/24 teste noi PASS (inclusiv matricea de snapshot §7 de mai jos).

**Ce NU demonstrează §6.2 (declarat onest):** ATR afectează legitim MULTE alte căi din detector
(degeneracy checks, praguri `evaluate_candidate` etc.) — de aceea hash-urile la ATR diferite NU sunt
identice între ele (801/973/940/973/1231 evenimente), doar fiecare identic cu SINE ÎNSUȘI, determinist,
peste rulări repetate. Afirmația "F5 nu mai afectează MACRO" e susținută de §6.1 (structural, complet),
NU de faptul că schimbarea ATR-ului nu schimbă rezultatul — ar fi greșit și nu s-a revendicat asta.

### 6.3 — Script determinist pt. Red Team (bare reale)

`blind_runner/verify_macro_identity_vs_baseline.py` (nou) — consumă DOI `predictions.json` deja produși
(nu citește escrow, nu are nevoie de acces): Red Team rulează `run_inference()` neschimbat o dată la
`82f27c0` (baseline îngheț) și o dată la acest commit (candidat), pe ACELEAȘI 48 ferestre reale, apoi
`python verify_macro_identity_vs_baseline.py baseline.json candidate.json` — reproduce automat exact
tabelul RT-RANGE-0012 §1 (geometrie MACRO per fereastră excluzând `structure_id`, evenimente MACRO,
contoare SWEEP_CONFIRMED/BREAKOUT_ACCEPTED/LIQUIDITY_SWEEP_REVERSAL/IS_TREND_MACRO), verdict
`MACRO_IDENTICAL=TRUE/FALSE`, exit code 0/1. Smoke-testat pe fixture-uri dev: auto-comparație =
`MACRO_IDENTICAL=TRUE`; o mutație de test (frontieră modificată) → corect detectată `FALSE` cu diff
explicit. mypy `--strict` clean.

**Scor înghețat de referință** (NU recalculat aici, doar citat din RT-RANGE-0012 pt. context — Red Team
îl re-verifică independent cu §6.3 de mai sus): MACRO = 62/88, recall = 0,705. F1-only NU trebuie să
reproducă rezultatul RESPINS post-F5 (58/88, 0,659) — pe baza §6.1 (dovadă structurală completă) nu are
CUM să-l reproducă, din moment ce codul executat e byte-identic cu `82f27c0`, care ESTE baseline-ul
62/88.

## 7 — F. Matrice de compatibilitate snapshot

| Snapshot sursă | Restaurare aici | Test |
|---|---|---|
| F1-only (acest commit) | **ACCEPTAT** | `test_snapshot_new_fingerprint_accepted` |
| `f224e7d`/`82f27c0` (fără câmp `implementation_fingerprint`) | **REFUZAT fail-closed** | `test_snapshot_missing_fingerprint_refused_simulates_bare_f224e7d` |
| `69af414` RESPINS (F1+F5, fingerprint `f1-f5-conformance-2026-08-20`) | **REFUZAT fail-closed** | `test_snapshot_rejected_f1_f5_fingerprint_refused` |
| fingerprint necunoscut/corupt | **REFUZAT fail-closed** | `test_snapshot_stale_or_corrupt_fingerprint_value_refused` |
| `config_id` greșit | **REFUZAT fail-closed** (neschimbat) | `test_snapshot_config_mismatch_still_refused` |
| `contract_version` greșit | **REFUZAT fail-closed** (neschimbat) | `test_snapshot_contract_mismatch_still_refused` |
| câmp core lipsă (corupt) | **REFUZAT** (`KeyError`/`ContractErrorV43`) | `test_snapshot_corrupted_missing_core_field_refused` |
| restore refuzat → stare țintă | **NEMODIFICATĂ** (atomic) | `test_restore_is_atomic_on_refusal` |
| restart determinist | **PASS** | `test_restart_between_breach_and_resolution_identical`, `test_chunk_invariance` |

`construction_reproduction/` (Componenta A, pinnată permanent la `f224e7d`) — verificat prin rulare
DIRECTĂ (nu doar afirmat) că REFUZĂ fail-closed acest commit nou, cu noul hash corect în mesajul de
eroare (`Așteptat 2aba333c…238b, găsit 098fa144…41fbc`) — dovadă vie că pin-ul Componentei A ține
indiferent de câte remedieri urmează.

## 8 — G. Teste / verificări statice

| Suită | Rezultat |
|---|---|
| `tests/` (detector + F1-only nou + adversariale + reachability) | **394/394 PASS** |
| `blind_runner/tests/` (F1 26 + restul 49, neschimbate) | **75/75 PASS** |
| `construction_reproduction/tests/` | Refuză fail-closed corect (Componenta A, prin design — nu e o eroare) |
| **Total live** | **469/469 PASS, 0 FAIL** |
| mypy `--strict` (`range_semantic_v4_3.py`, `schemas.py`, `inference.py`, `scoring.py`, `range_engine_v4_3.py`, `dev_fixtures.py`, `verify_macro_identity_vs_baseline.py`) | **CLEAN, 0 erori — 7 fișiere** |
| Scanare "leak" (`grep tol_cluster`) | **PASS** — un singur sit fără scalare (gardul revertat, intenționat), un sit cu scalare (`offer_swing`, neatins de F5 vreodată) |
| `tests/test_range_semantic_v4_3.py` | **NEATINS** (`git diff` gol) |
| `construction_reproduction/` | **NEATINS** (`git status` gol) |

Un defect mecanic găsit ȘI corectat autonom în timpul scrierii testelor noi (per mandat §12 al
mandatului anterior, aceeași disciplină aplicată aici): testul inițial `test_atr_unavailable_…`,
portat mecanic din suita ștearsă, presupunea greșit că `atr_ref=None` mai dezactivează un filtru —
premisă validă DOAR sub F5 (care citea `atr_ref`). Eșuat imediat la prima rulare (semnal clar, nu
tăcut), corectat la `test_atr_ref_none_has_zero_effect_guard_never_reads_it`, care verifică explicit
noua realitate: `atr_ref` nu mai are NICIUN efect asupra gardului. Chiar acest eșec e o confirmare
suplimentară că revertul e complet — nici măcar ramura fail-closed specifică F5 nu a supraviețuit.

## 9 — Fișiere modificate

```
 M ve_n1_replay/blind_runner/inference.py           (identitate: trio frozen actualizat, F1 neatins)
 M ve_n1_replay/blind_runner/scoring.py              (identitate: 2 literale, 0 schimbare de logică)
 D ve_n1_replay/tests/test_f5_tol_cluster_units.py    (șters — testa exclusiv comportamentul F5 revertat)
 M ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py  (F5 revertat + fingerprint redenumit)
 + ve_n1_replay/blind_runner/verify_macro_identity_vs_baseline.py   (nou, script Red Team, 130 linii)
 + ve_n1_replay/tests/test_f1_only_macro_identity.py                (nou, 24 teste, 359 linii)
```

`blind_runner/schemas.py`, `blind_runner/tests/test_f1_ohlc_tolerance.py`,
`blind_runner/tests/test_schemas.py`, `ve_n1_replay/range_engine_v4_3.py` — **0 modificări** față de
`69af414`. `RANGE_V4_3_F1_F5_CONFORMANCE_DELIVERY_REPORT.md` (raportul mandatului RESPINS) —
**neatins, nu amendat** (istoric păstrat, per mandat).

## 10 — Itemi `NOT_VERIFIABLE_HERE` (declarați explicit, nu ascunși)

1. **MACRO pe bare reale, ATR real** (§D, mandat) — VE nu are acces la escrow pt. acest mandat.
   Compensat prin §6.1 (dovadă structurală completă) + §6.2 (sweep comportamental ne-vacuu pe 5 valori
   ATR) + §6.3 (script determinist livrat pt. Red Team).
2. Scorul înghețat 62/88 / recall 0,705 pe bare reale — citat din RT-RANGE-0012, NU recalculat aici
   (aceeași limitare de acces).

Niciun item de mai sus a fost fabricat sau presupus adevărat fără dovadă.

## 11 — Status final

```
RANGE_V4_F1_ONLY_REMEDIATION_READY_FOR_RED_TEAM_AUDIT
self_declared_pass=false

F1_RETAINED_UNCHANGED = TRUE
F5_BEHAVIORAL_CHANGE_REVERTED = TRUE
F5_STATUS = DEFERRED_RESEARCH_ONLY_NON_BLOCKING
INTERNAL_CAPABILITY_STATUS = RESEARCH_ONLY_NOT_VALIDATED (NON_BLOCKING)
IMPLEMENTATION_IDENTITY_CORRECTLY_LABELED = TRUE  (nu f224e7d gol, nu f1-f5-conformance)
SNAPSHOT_FAIL_CLOSED_AGAINST_ALL_INCOMPATIBLE_STATES = TRUE
MACRO_STRUCTURAL_IDENTITY_VS_82f27c0 = TRUE  (diff complet, acoperire totală)
MACRO_BEHAVIORAL_IDENTITY_ON_REAL_BARS_REAL_ATR = NOT_VERIFIABLE_HERE  (fără acces escrow)
CONSTRUCTION_REPRODUCTION_PIN_INTACT = TRUE  (verificat prin refuz live)
SCORING_LOGIC_UNCHANGED = TRUE
MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED = FALSE
WHEEL_AUTHORIZED = FALSE
ALPHA_AUTHORIZED = FALSE
AI_TRADER_INTEGRATION_AUTHORIZED = FALSE
BROKER_ORDER_SUBMISSION = DISABLED
```

Niciun wheel construit. Niciun acces la bare SEALED/OOS/escrow (verificat, nu doar presupus). Niciun
parametru RANGE/CEO recalibrat. Nicio atingere la Strategy Catalog/Alpha Discovery/ve_brain
registry/AI Trader/LIVE_SHADOW/broker. Următorul proprietar: **Red Team** — singurul care poate elibera
`MACRO_INDEPENDENT_BLIND_PREPARATION_AUTHORIZED`.
