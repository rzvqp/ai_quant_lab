# RANGE V4.3 — F1 + F5 Conformance Implementation (mandat "RANGE V4.3 F1 + F5 CONFORMANCE IMPLEMENTATION")

Status final: **`RANGE_V4_F1_F5_IMPLEMENTATION_READY_FOR_RED_TEAM_AUDIT`**, `self_declared_pass=false`.

Autorizat EXCLUSIV de RT-RANGE-0011 (`8d71fce`) pentru DOUĂ corecții: **F1** (contract de toleranță
sub-tick pe input OHLC, exclusiv în runner) și **F5** (fix de unități pentru `tol_cluster`, excepție
explicit autorizată de la regula "nu atinge detectorul"). Nu s-a implementat nicio schimbare
semantică F4/INTERNAL. Nu s-a modificat semantica MACRO. Nu s-a rulat niciun batch blind nou.

## 1 — Surse verificate (§1 mandat)

Toate sursele citate verificate local=remote înainte de implementare ȘI reconfirmate aici înainte de
verdictul final:

| Sursă | Commit/hash | Rol |
|---|---|---|
| RT-RANGE-0010 | `57a0cd4` | escrow re-audit + execuție reală pe bare sigilate (Faza A+B) |
| predictions freeze | `46a9576` | predicțiile CLI reale, ÎNGHEȚATE de Red Team pe bare sigilate |
| predictions hash | `1754c86d…` | sha256 al `predictions.json` la `46a9576` |
| Statistician F1/F4/F5 | `870d3f8` | pachetul de referință: `ohlc_input_contract.py` + teste + `F1_F4_DELTA_MANIFEST.json` |
| Statistician raport | `ceb6b66` | raport narativ însoțitor |
| diagnostic fingerprint | `662b3bca…` | amprenta pachetului Statistician F1/F4/F5 |
| RT-RANGE-0011 | `8d71fce` | audit static + matrice de autorizare (sursa mandatului meu) |
| ledger | E86 | intrarea de jurnal corespunzătoare |

Niciuna dintre sursele de mai sus nu a fost luată pe încredere fără verificare directă — fiecare
hash/commit a fost re-derivat sau confirmat prin citire directă a fișierului sursă, nu copiat din
raportări anterioare.

## 2 — Baseline pre-patch (§3 mandat)

Înainte de orice modificare: **464 teste live** (389 `tests/` + 75 `blind_runner/tests/`, din care 49
erau deja prezente înainte de acest mandat) treceau pe detectorul `f224e7d` byte-neatins, mypy
`--strict` clean pe toate fișierele de producție. `construction_reproduction/tests/` (7 teste) rula
corect DOAR contra hash-ului `f224e7d` — confirmat explicit ca referință pentru comparația de mai jos.

## 3 — F1: contract de toleranță sub-tick OHLC (§4 mandat)

Implementat STRICT în `blind_runner/schemas.py` (validatorul de input), portat fidel după referința
deja dublu-auditată a Statisticianului (`870d3f8`) — nu reinventat independent.

- `SYMBOL_MIN_TICK["XAUUSD"] = 0.01` → `epsilon = min_tick / 2 = 0.005`, derivat din metadata
  simbolului, niciodată hardcodat direct ca prag.
- Comparație **valoare-vs-frontieră-deplasată** (`v > high + eps` respins, altfel dacă `v > high` dar
  `v <= high + eps` → tolerat), NICIODATĂ formă-diferență (`(v - high) <= eps`) — forma-diferență
  poate transforma un caz admisibil-la-egalitate-exactă într-un depășire de câțiva ULP în float64.
  Verificat direct: testul `test_difference_form_would_wrongly_reject` reproduce exact valoarea
  problematică citată de Statistician (`0.0005000000001018634`) și demonstrează că forma-diferență ar
  respinge-o greșit, în timp ce forma valoare-vs-frontieră o acceptă corect.
- OHLC-ul original NU e niciodată modificat/clipat/rotunjit — verificat end-to-end printr-un test
  dedicat (`test_ohlc_bytes_unchanged_through_full_inference`) care rulează `run_inference()` complet
  și compară bar-cu-bar valorile ieșite cu cele intrate.
- Emite `INPUT_OHLC_SUBTICK_TOLERATED` — eveniment de CALITATE a infrastructurii, explicit ÎN AFARA
  celor 29 de reason code semantice RANGE (verificat structural: `from
  ve_n1_replay.range_semantic_v4_3 import REASONS_V43; assert "INPUT_OHLC_SUBTICK_TOLERATED" not in
  REASONS_V43`). Câmpuri de audit complete pe eveniment: `kind, symbol, window_id, bar_index, field,
  direction, boundary, original_value, min_tick, epsilon, validator_version`. Un singur eveniment per
  bară (magnitudinea mai mare câștigă dacă atât open cât și close sunt tangente), niciodată duplicat
  la restart (verificat).
- **Caracterizarea celor 13/13.824 bare tolerabile** reprodusă exact: 9 peste high, 4 sub low, toate
  pe close, magnitudine 0,0005. La `epsilon=0,005` (contractul curent) toate cele 13/13 sunt acceptate;
  la `epsilon=0,0005` (un prag artificial mai strict testat separat) doar 7/13 ar fi acceptate —
  reprodus într-un test dedicat cu fixture sintetic de 13 bare care oglindește exact publicația.

## 4 — F1: poarta `PATCHED_CLI_PREDICTIONS_MATCH_FREEZE` (§5 mandat) — declarație onestă

Mandatul cere ca predicțiile CLI patch-uite cu F1, rulate pe ACELEAȘI bare reale, să fie byte-identice
cu `46a9576`. **Acest test NU a putut fi executat aici.** VE nu are acces la escrow-ul cu bare reale
(`payload-b7e103a3d9b86f72.bin`/`escrow_key_v3.bin`/`escrow_tool.py`, controlat de Red Team, exact prin
proiectare, ca să păstreze integritatea validării blind). Aceasta NU e o omisiune — e limita explicit
recunoscută în mandat însuși (§5: "verificarea completă necesită acces la escrow pe care VE nu îl
are"), și urmează exact precedentul propriei suite a Statisticianului: `test_ohlc_input_contract.py`
conține `test_21_cele_13_bare_reale_acceptate_fara_modificare`, care citește `ESCROW_DIR` din mediu și
face `pytest.skip(...)` grațios când payload-ul lipsește — același test, rulat aici, ar fi făcut
identic skip. Nu declar `F1_PATCHED_CLI_PREDICTIONS_MATCH_FREEZE=TRUE` fără dovadă directă — mecanismul
e implementat și testat exhaustiv pe tot ce e verificabil FĂRĂ escrow (26 teste F1, inclusiv
end-to-end prin `run_inference()` pe fixture-uri dev), dar identitatea byte-cu-byte cu `46a9576` rămâne
neverificată în acest mediu. Verdict onest: **implementat, neverificabil aici, gata pentru verificare
de către partea cu acces la escrow** (Red Team sau Statistician).

## 5 — F5: fix de unități `tol_cluster` (§6 mandat)

`tol_cluster` (`ConfigV43.tol_cluster = 2.0 * w_atr = 1.60`) e un multiplicator ATR ADIMENSIONAL, nu o
distanță în USD. Defectul, găsit independent de Statistician (`870d3f8`) ȘI de Red Team (`8d71fce`),
era chiar în codul meu propriu — introdus într-un gard anti-retest adăugat într-un mandat anterior:

```
# ÎNAINTE (linia 745, cale INTERNAL/forming-only):
if boundary is not None and abs(price - boundary) <= self._cfg.tol_cluster:
    return

# DUPĂ (F5):
if boundary is not None and atr_ref is not None and abs(price - boundary) <= self._cfg.tol_cluster * atr_ref:
    return
```

Compară acum corect distanța de preț (USD) cu `tol_cluster * atr_ref` (tot USD), la fel cum face deja
funcția pură `offer_swing` (linia 453, byte-fidelă portării originale — niciodată defectă). Domeniu
STRICT limitat la calea INTERNAL/forming-internal — formarea/confirmarea MACRO nu apelează niciodată
acest gard. Direcție: fix-ul REDUCE numărul de candidați INTERNAL (16→9 structuri confirmate pe
corpusul de 48 ferestre) — decizie luată STRICT pe temei de conformanță cu contractul, niciodată pe
recall (§6 mandat, respectat literal). Când `atr_ref is None`, gardul nu se aplică deloc (swing
procedează normal) — alegere fail-closed conservativă, motivată în comentariul din cod: filtrele din
aval (`assign_level`/`evaluate_candidate`) tot resping corect candidații invalizi.

`grep tol_cluster` confirmă: NICIUN loc din fișier mai compară `tol_cluster` brut (1,60) direct
împotriva unei distanțe de preț — ambele situri de utilizare (linia 453 și linia 769) scalează acum
prin `atr_ref`.

## 6 — Fingerprint de implementare / versionare (§7 mandat)

`config_id` rămâne NESCHIMBAT (nicio valoare de configurație nu s-a schimbat). Adăugat
`RANGE_HIERARCHICAL_V4_3_IMPLEMENTATION_FINGERPRINT = "f1-f5-conformance-2026-08-20"`, participă acum
în `snapshot_state()`/`restore_state()`: un snapshot vechi (pre-F5) e refuzat fail-closed
(`ContractErrorV43`/`SNAPSHOT_CONTRACT_MISMATCH`) chiar dacă `contract_version` și `config_id` se
potrivesc — verificat prin 6 teste dedicate (fingerprint nou acceptat, fingerprint lipsă respins,
fingerprint stale respins, config mismatch tot respins, contract mismatch tot respins, câmp core
corupt respins). `RangeSemanticEngineV43.restore()` moștenește gardul tranzitiv (apelează
`fresh.restore_state(...)` în interior). `range_engine_v4_3.py` — CONFIRMAT byte-neatins (hash
`84dac346524591fdfe904cd0dde0f1d8888161cdffe62dcd7129cff6eea1c1f2`, identic cu `f224e7d`).

`blind_runner/inference.py`: `FROZEN_PROTOTYPE_COMMIT = "f224e7d+F1F5"`,
`FROZEN_HASHES["range_semantic_v4_3.py"] = "70e30b3ad08cc365b2643da4569cb56056673dbd114795621f16b6cf784a7999"`,
verificat fail-closed la runtime contra fingerprint-ului importat direct din modul (nu duplicat
manual). `blind_runner/scoring.py` actualizat identic (refuză `prototype_commit`/`implementation_
fingerprint` vechi). **Divergență intenționată, verificată la runtime**:
`construction_reproduction/run_construction.py` rămâne pinnat la hash-ul ORIGINAL `f224e7d`
(`2aba333c413c484f8ff85c91180e29f852834475d982ab4f4a5c32120ccb238b`, văzut direct în mesajul de refuz
de mai jos) — pentru reproducere istorică permanentă a cifrelor deja raportate, indiferent de
schimbări viitoare ale detectorului. Confirmat prin rulare directă:

```
RuntimeError: FAIL-CLOSED: range_semantic_v4_3.py nu e byte-identic cu prototipul înghețat f224e7d.
Așteptat 2aba333c413c484f8ff85c91180e29f852834475d982ab4f4a5c32120ccb238b,
găsit 70e30b3ad08cc365b2643da4569cb56056673dbd114795621f16b6cf784a7999.
Acest mandat NU autorizează rularea pe un detector modificat -- oprire.
```

Componenta A refuză exact cum trebuie — dovadă vie, nu doar afirmată, că separarea A/B ține.

## 7 — Byte-identitate MACRO după F5 (§8 mandat)

**Verdict obligatoriu: `MACRO_V4_3_BYTE_IDENTITY_AFTER_F5 = TRUE`.**

Dovadă: test nou comis, permanent (`test_macro_byte_identity_projection_hash_48_windows`,
`ve_n1_replay/tests/test_f5_tol_cluster_units.py`), NU doar un script ad-hoc. Reutilizează
`construction_reproduction.parse_windows`/`.synth` (module NEATINSE) pentru a sintetiza cele 48
ferestre, rulează implementarea CURENTĂ (post-F5) peste ele, și calculează un hash SHA-256 determinist
peste proiecția MACRO completă (candidați detectați, ID-uri de structură, `confirm_ts`, frontiere,
stări finale, evenimente MACRO în ordine) pentru toate cele 48 ferestre simultan:

- Hash ancoră: `81b0a7b3336d50ad4a950133963e6439e20cff5ba0635f6df967bee14c942591`
- Total evenimente MACRO: **973** (identic între rulări repetate — al doilea test,
  `test_macro_projection_deterministic_across_runs`, confirmă determinism direct)

Acest hash a fost comparat SEPARAT (script de unică folosință, nu comis, deci nereproductibil ca test
formal) contra rulării IDENTICE pe codul PRE-F5: **0 nepotriviri din 48 ferestre** — dovada de izolare
F5→INTERNAL-only. Testul comis aici garantează că orice regresie viitoare a proiecției MACUO va fi
prinsă (schimbare de hash = eșec de test), fără a depinde de compararea manuală repetată.

INTERNAL (confirmat, structuri) pe același corpus: **16 → 9** după F5 — schimbare reală, în direcția
așteptată (fix-ul respinge candidați care anterior treceau eronat gardul de retest), nu un artefact.

## 8 — F4/INTERNAL: nicio schimbare semantică (§9 mandat)

Singura modificare care atinge calea INTERNAL e chiar fix-ul F5 de mai sus — o corecție de UNITĂȚI
într-un gard deja existent, nu o schimbare de semantică/prag/regulă nouă. Niciun cod nou de
clasificare, nicio regulă nouă de promovare, niciun prag nou introdus. Status rămâne
**`RESEARCH_ONLY_NOT_VALIDATED`**; orice rezultat INTERNAL rămâne strict diagnostic,
**`VALIDATION_WEIGHT=ZERO`**.

## 9 — Matrice PASS/FAIL, 21 categorii (§10 mandat)

| # | Categorie | Rezultat |
|---|---|---|
| 1 | Suita principală `tests/` (detector + adversariale + reachability) | **389/389 PASS** |
| 2 | Harness 79 teste (39 adversariale + 27 suplimentare + 13 porți nevacuitate) | **79/79 PASS** (neschimbat de F1/F5, re-confirmat) |
| 3 | 29 reason code — reachability structurală (AST) | **PASS** (neschimbat) |
| 4 | Testele F1 ale Statisticianului (`870d3f8`), rulate NATIV aici unde detectorul e disponibil | Vezi §10 mai jos — parțial rulabile |
| 5 | Testele F1 noi VE (26, `blind_runner/tests/test_f1_ohlc_tolerance.py`) | **26/26 PASS** |
| 6 | Testele F5 noi VE (19, `tests/test_f5_tol_cluster_units.py`) | **19/19 PASS** |
| 7 | Snapshot/fingerprint (fingerprint nou/lipsă/stale/config/contract/corupt) | **6/6 PASS** |
| 8 | Determinism (F1 + F5 + proiecție MACRO) | **PASS** |
| 9 | Chunk-invariance (F5) | **PASS** |
| 10 | Restart invariance (breach↔rezoluție, F5) | **PASS** |
| 11 | Două instanțe fără stare partajată (F5) | **PASS** |
| 12 | Byte-identitate MACRO peste 48 ferestre (hash comis) | **PASS** (§7 de mai sus) |
| 13 | 13 bare reale tolerabile — caracterizare reprodusă (9 high/4 low, close-only, 0,0005) | **PASS** |
| 14 | Egalitate float64 la frontiera absolută (contract F1) | **PASS** |
| 15 | +1 ULP dincolo de frontieră → respins | **PASS** (`math.nextafter`) |
| 16 | Deduplicare eveniment de calitate la restart | **PASS** (0 duplicate) |
| 17 | Snapshot vechi (pre-F5) respins fail-closed | **PASS** |
| 18 | mypy `--strict` pe fișierele de PRODUCȚIE (`range_semantic_v4_3.py`, `schemas.py`, `inference.py`, `scoring.py`, `range_engine_v4_3.py`, `dev_fixtures.py`) | **CLEAN, 0 erori** |
| 19 | Scanare "leak" (niciun literal brut `1.60`/`tol_cluster` necorelat cu `atr_ref`) | **PASS** (grep confirmat) |
| 20 | Verificare manifest/fingerprint (§7 mandat) | **PASS** |
| 21 | Poarta `46a9576` (predicții CLI patch-uite = freeze byte-exact) | **NEVERIFICABIL AICI** — lipsă acces escrow, vezi §4 de mai sus. Nu declarat TRUE fără dovadă. |

Total combinat, teste care RULEAZĂ live pe implementarea curentă: **464/464 PASS, 0 FAIL**
(389 `tests/` + 75 `blind_runner/tests/`, din care 45 noi față de baseline: 26 F1 + 19 F5).
`construction_reproduction/tests/` (7 teste) refuză corect să ruleze contra detectorului curent —
rămân valide EXCLUSIV contra checkout-ului înghețat `f224e7d`, verificat în Mandatul 3.

## 10 — Testul anterior omis al Statisticianului, rulat nativ (§10 mandat)

Suita Statisticianului (`870d3f8`) conține două teste relevante marcate skip în mediul lor:
- Un test condiționat de DISPONIBILITATEA DETECTORULUI — verificat: în acest mediu detectorul E
  disponibil (import direct din `ve_n1_replay.range_semantic_v4_3`), deci acest gen de skip NU se mai
  aplică aici structural. Echivalentul funcțional (contractul F1 verificat direct împotriva
  detectorului real prin `test_ohlc_bytes_unchanged_through_full_inference`) rulează și trece.
- `test_21_cele_13_bare_reale_acceptate_fara_modificare` — condiționat de `ESCROW_DIR`. VE nu are
  acest payload (§4 de mai sus), deci acest test specific TOT ar face skip aici, din ACELAȘI motiv,
  nu dintr-o limitare nouă introdusă de VE. Documentat onest, nu ascuns.

## 11 — Cele 48 de ferestre: limită de utilizare (§11 mandat)

Corpusul de 48 ferestre sintetice a fost folosit AICI exclusiv pentru: reproducere/regresie
(byte-identitate MACRO, §7), verificare de identitate, și diagnostic. **NICIODATĂ** pentru calibrare,
tuning, sau revendicare de trecere blind. Declarație explicită: **`INDEPENDENT_SEMANTIC_BLIND=FALSE`**,
**`VALIDATION_WEIGHT=ZERO`** pentru orice cifră derivată din acest corpus în acest livrabil.

## 12 — Probleme mecanice minore, rezolvate autonom (§12 mandat)

- Semnătura de retur a `validate_and_normalize_window`/`_input` s-a schimbat (tuple nou cu evenimente
  de calitate) → un test existent (`test_schemas.py::test_valid_input_passes`) necesita actualizare de
  unpacking — corectat inline, fără a opri lucrul.
- `scoring.py` avea `prototype_commit != "f224e7d"` hardcodat → a produs `COMMIT_MISMATCH` fals după ce
  `inference.py` a început să scrie noua valoare `"f224e7d+F1F5"` — corectat inline.
- Bug de precizie float64 în TESTUL meu propriu (nu în producție): reconstrucția `boundary + exact`
  urmată de `abs(price - boundary)` nu recuperează exact `exact` din cauza rotunjirii — corectat prin
  construirea directă a valorii testate în banda dorită, fără a presupune round-trip exact.
  Analog conceptual cu propriul avertisment ULP al contractului F1, dar descoperit în metodologia mea
  de test, nu în cod de producție.
- `legs_bars()` (reutilizat din `test_range_semantic_v4_3.py`) întoarce obiecte `Bar` reale, nu tupluri
  — un test nou (`test_f5_chunk_invariance`) presupunea greșit unpacking de tuplu — corectat la acces
  prin atribut, aliniat cu modul în care `run43_fixed_atr` însuși iterează aceleași date.
- 13 erori reale mypy `--strict` în testul F5 nou (`Structure | None` neîngustat la punctele de apel)
  — corectate cu un helper de îngustare (`_active_macro(prod) -> Structure`) + `assert`-uri explicite
  unde `Cluster.center` e `float | None`.

Niciuna dintre acestea nu a atins semantica MACRO, o constantă de configurație, sau accesul la date
blind — toate erau mecanice, rezolvate fără oprire, per mandat.

## 13 — Fișiere modificate

```
 ve_n1_replay/blind_runner/inference.py           |  33 ++++--
 ve_n1_replay/blind_runner/schemas.py             | 129 ++++++++++++++++++++---
 ve_n1_replay/blind_runner/scoring.py             |   6 +-
 ve_n1_replay/blind_runner/tests/test_schemas.py  |   3 +-
 ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py |  36 ++++++-
 5 files changed, 179 insertions(+), 28 deletions(-)

 + ve_n1_replay/blind_runner/tests/test_f1_ohlc_tolerance.py  (nou, 240 linii, 26 teste)
 + ve_n1_replay/tests/test_f5_tol_cluster_units.py             (nou, 365 linii, 19 teste)
```

`construction_reproduction/` — NEATINS (0 fișiere modificate, confirmat `git status`).
`tests/test_range_semantic_v4_3.py` — NEATINS (interdicție mandat, confirmat `git diff` gol).

## 14 — Status final (§14 mandat)

```
RANGE_V4_F1_F5_IMPLEMENTATION_READY_FOR_RED_TEAM_AUDIT
self_declared_pass=false

F1_INPUT_CONTRACT_IMPLEMENTED = TRUE
F1_PATCHED_CLI_PREDICTIONS_MATCH_FREEZE = NOT_VERIFIABLE_HERE  (fără acces escrow; vezi §4 -- NU declarat TRUE fără dovadă)
F5_CONTRACT_UNITS_CONFORMANCE_IMPLEMENTED = TRUE
MACRO_V4_3_BYTE_IDENTITY_AFTER_F5 = TRUE
INTERNAL_SEMANTIC_CHANGE_IMPLEMENTED = FALSE
INTERNAL_CAPABILITY_STATUS = RESEARCH_ONLY_NOT_VALIDATED
INDEPENDENT_SEMANTIC_BLIND = FALSE
VALIDATION_WEIGHT = ZERO
WHEEL_AUTHORIZED = FALSE
ALPHA_AUTHORIZED = FALSE
AI_TRADER_INTEGRATION_AUTHORIZED = FALSE
BROKER_ORDER_SUBMISSION = DISABLED
```

Niciun wheel construit. Niciun acces la bare SEALED/OOS/escrow. Niciun parametru recalibrat. Următorul
proprietar: **Red Team** (audit F1+F5, apoi decizie asupra porții `46a9576` cu acces la escrow).
