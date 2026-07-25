# SPEC SCHEMA v1.0
### Formatul oficial al specificației predate de Statistician către Validation Engine

**Document ID:** VE-SPECSCHEMA-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Statut:** aprobat (F1, CEO 2026-07-24). **Revizuit redacțional 2026-07-24** pentru decizia JSON-only (A1) și pentru registrul v1.1 (G1/G2). **Fișierul de schemă `SPEC_SCHEMA_v1.0.json` nu a fost modificat** — extinderea vocabularului nu cere o versiune nouă de schemă.
**Forma normativă:** `SPEC_SCHEMA_v1.0.json` (JSON Schema draft 2020-12)
**Vocabular:** `capabilities.json` / `CAPABILITY_REGISTRY_v1.4.md`
**Documente guvernante:** contract §1.1–1.7 · `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md`

---

## 1. Scop

Contractul §1 enumeră șapte obligații ale specificației. Acest document le transformă într-o structură verificabilă mecanic, astfel încât „specificație completă" să nu mai fie o judecată, ci o proprietate testabilă.

**Specificația se scrie exclusiv în JSON** (decizie CEO 2026-07-24, punctul A1 din backlog). YAML nu este acceptat: un fișier `.yaml`/`.yml` nu este parsat tăcut, ci produce o oprire E3 explicită. **Documentul `.md` însoțitor este permis și încurajat pentru lizibilitate, dar nu este citit de VE** — sursa de adevăr este fișierul mașină.

### 1.1 Validarea în două etape

| Etapă | Instrument | Verifică | Eroare |
|---|---|---|---|
| 1 — **formă** | `SPEC_SCHEMA_v1.0.json` | secțiuni prezente, tipuri, structură, praguri numerice, ferestre complete | E1, E2 |
| 2 — **vocabular** | `capabilities.json` | ID-uri existente, parametri obligatorii prezenți, domenii respectate, status de calibrare, reguli de disponibilitate, suprapunere cu ferestre sigilate | E2, E3, E5 |

Metodele nu sunt duplicate în schemă. Registrul rămâne sursa unică de adevăr pentru ce se poate executa, iar o extindere de registru nu cere o versiune nouă de schemă.

---

## 2. Structura de nivel superior

Toate cele 17 câmpuri sunt obligatorii. Lipsa oricăruia oprește rularea **înainte de orice atingere a datelor**.

| Câmp | Contract | Rol |
|---|---|---|
| `spec_id`, `spec_version` | §1.1 | identificarea și versionarea specificației |
| `contract_version` | §1.1 | fixat la `STAT-VE-CONTRACT-v1.0` |
| `capability_registry_version` | §1.1 | versiunea de registru față de care s-a scris |
| `candidate.id`, `candidate.freeze_hash` | §1.1 | hash-ul de îngheț referit |
| `issued_by`, `issued_at` | §1.1 | emitentul (numai `Statistician`) și data |
| `mode` | — | `validate` \| `rehearse` \| `run` |
| `authorization` | — | token CEO pentru resurse irepetabile |
| `data` | §1.2 | sursele folosite + hash-urile așteptate |
| `population` | §1.2 | fereastra exactă și formula de includere/excludere |
| `variables` | §1.3 | formulele derivate + ordinea temporală permisă |
| `tests` | §1.4 | testele, în ordine, cu parametri expliciți |
| `multiple_testing` | §1.5 | familia și metoda de corecție |
| `criteria` | §1.5 | criteriile preînregistrate, cu praguri numerice |
| `return` | §1.6 | ce se cere înapoi |
| `on_missing_or_ambiguous` | §1.7 | clauza de oprire |

---

## 3. Secțiunile, pe rând

### 3.1 `candidate` — etichete, nu conținut

`id` și `freeze_hash` există exclusiv pentru trasabilitate în manifest. **Niciun modul de calcul nu le citește** (orbirea la ipoteză, arhitectură §1.2). VE nu deschide documentul candidatului și nu poate, în consecință, să fie influențat de ce testează.

### 3.2 `authorization` — resurse irepetabile

```yaml
authorization: {required: false, ceo_token_id: null, resource_class: null}
```

Când `required: true`, `ceo_token_id` și `resource_class` devin obligatoriu neveline. Etapa 2 verifică suplimentar situația inversă și mai periculoasă: **dacă fereastra populației se suprapune peste o fereastră sigilată iar `required` este `false`, rularea se oprește (E5).** O specificație nu poate atinge holdout-ul din neatenție.

### 3.3 `data` — hash-uri declarate

Fiecare sursă folosită se declară cu hash-ul SHA-256 pe care Statisticianul îl așteaptă. Nepotrivirea oprește rularea (E4) — nu se continuă cu o notă de avertizare. Hash-urile curente sunt publicate în `CAPABILITY_REGISTRY_v1.4.md` §2.

### 3.4 `population` — populația și denominatorul

```yaml
population:
  source_id: OANDA_XAUUSD_H1@v1
  window: {start: "...Z", end: "...Z", bounds: "[)"}
  timezone: UTC
  include: [ {id: ..., predicate: ..., params: {...}}, ... ]
  exclude: [ ... ]
  cooldown: {min_bars_between_events: 0}
  min_n: 15
  report_denominator: true
```

Patru decizii structurale:

- **`bounds` este obligatoriu.** O fereastră fără inclusivitate declarată este ambiguă la capete, iar la n mic un singur eveniment de graniță poate schimba rezultatul.
- **Fiecare predicat are `id`.** Denominatorul raportează câte bare candidate a respins *fiecare criteriu în parte*, nu doar totalul. Este exact golul semnalat ca universal în `STATISTICIAN_PHASE1_SUMMARY.md` §1.
- **`cooldown` este obligatoriu.** „Câte evenimente distincte există" este o decizie de proiectare. Fără deduplicare declarată, ar deveni o alegere a VE. Zero se declară explicit.
- **`min_n` este obligatoriu.** Sub prag, VE **se oprește**; nu rulează și nu comentează dimensiunea eșantionului. Interpretarea unui eșantion insuficient aparține Statisticianului (constituție §6 „analiză de putere înaintea interpretării").

### 3.5 `variables` — formule și ordine temporală

```json
{
  "id": "vol_regime_hour",
  "primitive": "hour_of_day_volatility_profile@v1",
  "params": {"source_id": "OANDA_XAUUSD_H1@v1", "estimator": "parkinson",
             "lookback_days": 60, "normalization": "divide_by_daily_mean",
             "min_observations_per_hour": 20},
  "availability": {"anchor": "event_time", "offset_bars": -1, "source_id": "OANDA_XAUUSD_H1@v1"},
  "role": "control"
}
```

Începând cu registrul v1.1, o serie brută se declară tot ca variabilă, nu ca nume magic de coloană:

```json
{
  "id": "bar_high",
  "primitive": "raw_series@v1",
  "params": {"source_id": "OANDA_XAUUSD_H1@v1", "field": "high"},
  "availability": {"anchor": "event_time", "offset_bars": 0, "source_id": "OANDA_XAUUSD_H1@v1"},
  "role": "exposure"
}
```

Pentru `raw_series@v1`, `offset_bars` selectează bara a cărei valoare se ia. Consecința importantă: seria brută rămâne **sub garda de leakage**, exact ca orice altă variabilă.

Începând cu registrul v1.2, un eveniment discret se declară ca variabilă de expunere prin `indicator@v1`, care transformă un predicat într-o serie 0/1 (G3). Disponibilitatea indicatorului nu poate fi mai devreme decât a oricărei variabile folosite de predicatul lui — verificat recursiv, iar ciclurile de referință sunt respinse:

```json
{
  "id": "sweep_event",
  "primitive": "indicator@v1",
  "params": {"predicate": {"id": "ev_reject", "predicate": "compare@v1",
             "params": {"left": "bar_high", "op": ">", "right": "pdh"}}},
  "availability": {"anchor": "event_time", "offset_bars": 0, "source_id": "OANDA_XAUUSD_H1@v1"},
  "role": "exposure"
}
```

Tot din v1.2, parametrii de referință ai testelor (`exposure_ref`, `outcome_ref`, `base_test_ref`, `predicate_ref` etc.) sunt rezolvați fail-closed la validare — o referință inexistentă oprește cu E2 înainte de orice acces la date (G5).

Din registrul v1.3, un eveniment de tip „prima bară a domeniului care satisface o condiție" se declară prin predicatul `first_in_scope@v1` (G7). Scope-ul `day` are granița la 00:00 UTC (regula `day_scope_boundary`, Calea A). Evenimentul in-sample al DC-0004 — „prima bară a zilei care depășește PDH, apoi respinge" — se scrie `and(first_in_scope(day, high>pdh), close<pdh)`:

```json
{
  "id": "ev_up",
  "predicate": "and@v1",
  "params": {"operands": [
    {"id": "ev_up_first", "predicate": "first_in_scope@v1",
     "params": {"scope": "day", "predicate": {"id": "ev_up_breach", "predicate": "compare@v1",
                "params": {"left": "bar_high", "op": ">", "right": "pdh"}}}},
    {"id": "ev_up_rej", "predicate": "compare@v1", "params": {"left": "bar_close", "op": "<", "right": "pdh"}}
  ]}
}
```

`availability` este mecanismul prin care contractul §1.3 („ordinea temporală permisă, pentru a preveni leakage") devine executabil. Garda **verifică declarația, nu deduce intenția**: rolurile `exposure`/`control`/`stratifier` cer `offset_bars ≤ 0`; `outcome` permite offset pozitiv, dar fereastra de rezultat trebuie să fie disjunctă de fereastra de clasificare. Suprapunerea oprește rularea (E6).

### 3.6 `tests` — ordine și celule

```json
{
  "order": 1,
  "test_id": "T1_matched_null",
  "method": "matched_null@v1",
  "params": {
    "statistic": {"id": "s_mean_excess_k6", "statistic": "mean@v1",
                  "params": {"variable_ref": "cont_excess_k6"}},
    "tail": "two_sided", "B": 200000,
    "preserve": ["session", "calendar_period", "event_count"],
    "resample_unit": "event", "min_n": 15
  },
  "cells": [{"id": "ny_up", "predicates": []}, {"id": "asia_up", "predicates": []}],
  "seed_policy": "derived_from_spec_hash"
}
```

Începând cu registrul v1.1, statistica se declară parametrizat — `{id, statistic, params}`, exact forma predicatelor. Fără această formă, motorul ar fi trebuit să deducă la execuție cărei variabile i se aplică media, ceea ce contractul interzice.

- Testele se execută **strict în ordinea `order`**, niciodată reordonate.
- `cells` este obligatoriu și enumerat explicit. Un test nestratificat declară exact o celulă cu listă goală de predicate. Nu există stratificare automată — VE nu descoperă singur că un test „ar trebui" rulat pe șase celule.
- `seed_policy` are o singură valoare admisă: sămânța se derivă determinist din hash-ul specificației. Statisticianul nu alege semințe, iar VE nu le generează aleator. Aceeași specificație produce aceleași semințe pe orice mașină.

### 3.7 `multiple_testing` — familia se enumeră, nu se deduce

```yaml
multiple_testing:
  family_id: DC-XXXX-holdout-6cells
  members: [ {test_id: T1_matched_null, cell: ny_up, output: p_hat}, ... ]
  method: bonferroni@v1
  params: {alpha: 0.05, family_members: [...]}
```

VE nu descoperă că un test face parte dintr-o familie mai mare și nu propune o corecție. „Fără corecție" se declară explicit prin `none@v1`; **omiterea secțiunii este o specificație incompletă, nu o declarație**.

### 3.8 `criteria` — praguri numerice, ținte structurate

```yaml
criteria:
  - {id: C1, target: {test_id: T1_matched_null, cell: ny_up, output: p_adjusted}, comparator: "<", threshold: 0.05}
```

Două proprietăți deliberate:

- **`threshold` este `number`.** Un prag descriptiv („volatilitate ridicată", „suficient de rar") nu poate fi exprimat în schemă. Interdicția din contract §1.2 („praguri numerice explicite, niciodată descriptive") devine imposibil de încălcat, nu doar interzisă.
- **`target` este o referință structurată, nu o expresie.** VE nu conține și nu va conține un interpretor de expresii — un mini-limbaj în specificație ar readuce, pe ușa din dos, capacitatea de a calcula lucruri nespecificate.

### 3.9 `return` și clauza de oprire

`return` acoperă contractul §1.6. Câmpul `criteria_evaluation` **este deliberat absent în v1.0** și va fi respins de schemă (`additionalProperties: false`) până la ratificarea punctului deschis P1 — dacă VE evaluează mecanic criteriile sau returnează doar numerele.

`on_missing_or_ambiguous` are o singură valoare admisă. **Nu există mod permisiv configurabil.**

---

## 4. Cele cinci mecanisme care fac schema fail-closed prin construcție

| # | Mecanism | Ce previne |
|---|---|---|
| 1 | `additionalProperties: false` peste tot | câmpuri inventate, extensii tăcute, parametri strecurați |
| 2 | `threshold: number` | praguri descriptive |
| 3 | `window` cu ambele capete și `bounds` | ferestre deschise sau ambigue la graniță |
| 4 | `const` pe `on_missing_or_ambiguous` și `seed_policy` | dezactivarea clauzei de oprire; semințe alese ad-hoc |
| 5 | zero apariții ale cuvântului-cheie `default` în schemă | ca VE să completeze tăcut o valoare lipsă |

Mecanismul 5 este cel mai important și cel mai ușor de pierdut: un singur `default` în schemă ar reintroduce exact comportamentul pe care contractul §1.7 îl interzice.

---

## 5. Ce nu poate fi exprimat în această schemă, deliberat

- un prag descriptiv sau condiționat de inspecție vizuală;
- o fereastră deschisă la un capăt sau relativă („ultimele 6 luni");
- un parametru opțional sau cu valoare implicită;
- o instrucțiune de tip „alege cea mai bună variantă", „optimizează", „dacă nu merge, încearcă";
- o corecție implicită sau absentă fără declarație;
- un mod permisiv care să continue peste un câmp lipsă;
- o expresie calculabilă liber;
- evaluarea criteriilor de către VE (rezervat până la P1).

---

## 6. Ciclul de corectare

O specificație respinsă **nu se editează în loc**. VE emite `CLARIFICATION_REQUEST.md` cu patru câmpuri (cod, cale exactă a câmpului, motiv, ce există în registru — fără valoare recomandată), iar Statisticianul emite o versiune nouă, cu `spec_version` incrementat și hash nou.

Istoricul complet al versiunilor rămâne vizibil. Combinat cu ledger-ul append-only al rulărilor, aceasta face detectabilă orice succesiune de re-specificări făcute după ce s-a văzut un rezultat parțial — fără a depinde de onestitatea niciunei părți.

---

## 7. Maparea erorilor

| Cod | Declanșat de | Etapă | Date atinse |
|---|---|---|---|
| **E1** | câmp obligatoriu absent | 1 | nu |
| **E2** | tip greșit, prag ne-numeric, fereastră incompletă, familie neenumerată, parametru obligatoriu lipsă | 1–2 | nu |
| **E3** | `source_id`/`primitive`/`predicate`/`method` inexistent în registru, sau metodă care nu este `VALIDATED` | 2 | nu |
| **E4** | hash de date nepotrivit, sursă absentă, fereastră neacoperită | preflight | doar hash |
| **E5** | suprapunere cu fereastră sigilată fără autorizare, token invalid sau consumat, repetiție prealabilă absentă | 2 / preflight | nu |
| **E6** | `n < min_n`, populație vidă, tripwire de leakage | execuție | da (nesigilate) |

---

## 8. Fișiere însoțitoare

| Fișier | Rol |
|---|---|
| `SPEC_TEMPLATE_v1.4.json` | șablon oficial, cu structura completă și valorile purtătoare de decizie marcate ca substituenți `<<...>>`. **Nu este o specificație validă și nu poate fi executat**; există pentru a fi copiat, nu rulat |
| `tests/fixtures/reference_spec_dc0004.json` | specificația de referință — transcrierea unui design real în vocabularul aprobat. Artefact de inginerie, **nu** o specificație oficială a Statisticianului |

Șablonul YAML din F1 a fost retras odată cu decizia JSON-only; adnotările lui sunt preluate integral în §3 din acest document.

---

**Nu s-a scris niciun cod. Nu s-a executat nicio validare. Nu s-a modificat niciun artefact al laboratorului în afara directorului `validation_engine/`.**
