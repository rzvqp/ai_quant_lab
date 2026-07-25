# F2.3 — RAPORT DE LIVRARE
### DC-0004 Calea A (replicare strictă) · rezolvarea G7 · Capability Registry v1.3

**Document ID:** VE-F23-REPORT-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Autoritate:** decizie CEO 2026-07-24 — DC-0004 = Calea A (replicare strictă in-sample); rezolvă G7 strict cât e necesar.
**Statut:** livrat, în așteptarea aprobării. **F3 NU a fost început. G6 NU a fost rezolvat. DC-0008 NU a fost modificat (design). Nicio metodă statistică implementată. Nicio dată de piață citită.**

---

## 1. Ce s-a cerut și ce s-a livrat

| Pas cerut | Livrat |
|---|---|
| 1. actualizează specificația DC-0004 cu convențiile Calea A | `tests/fixtures/reference_spec_dc0004.json` rescrisă complet |
| 2. rezolvă G7 strict cât e necesar pentru evenimentul original | `first_in_scope@v1` (registru v1.3) + recursie în validator |
| 3. actualizează testele și documentația | +7 teste DC-0004 Calea A, +4 mutații G7, +2 invarianți v1.3; registru v1.3 md; schema md; șablon v1.3 |
| 4. raportează dacă specificația devine completă și executabilă structural | §7 — **structural validă, dar NU completă**: blocată de G8 + tensiunea seed |

---

## 2. Convențiile Calea A blocate în specificația DC-0004

Toate replicate din `obs0003/0008/0012/0013` (verificate direct în cod):

| # | Convenție | Cum e exprimată |
|---|---|---|
| 1 | **graniță de zi 00:00 UTC** | scope `day` (regula `day_scope_boundary`, registru v1.3) |
| 2 | **4 sesiuni fixe UTC** (asia 00-08, london 08-13, ny 13-21, late 21-24) | `session_label@v1` cu 4 granițe UTC |
| 3 | **eveniment = prima bară care depășește nivelul**, verificând doar acea bară | `and(first_in_scope@v1(day, high>pdh), close<pdh)` + simetric pe PDL |
| 4 | **K6 orizont decisiv** (K12 secundar) | `T1_matched_null_k6` decisiv; `T2_matched_null_k12` diagnostic |
| 5 | **baseline per sesiune** | `baseline_forward_mean@v1` cu `strata: [session]` |
| 6 | **test one-sided** (coada stângă = reversie) | `matched_null@v1.tail: left` |
| 7 | **familie Bonferroni empirică n≥25** | ⚠️ **NEEXPRIMABILĂ — G8** (vezi §5) |
| 8 | **seed = 7** | ⚠️ **NEEXPRIMABIL — tensiune** (vezi §6) |

Șase din opt sunt exprimate fidel. Două (7, 8) nu sunt exprimabile în vocabularul/schema curente și sunt raportate ca blocaje, nu substituite tăcut.

---

## 3. Rezolvarea G7 — `first_in_scope@v1`

**Minimal, exact cât cere evenimentul original.** Un singur predicat de populație:

```
first_in_scope@v1 {scope: [day|session|week], predicate: <predicat intern>}
```

- adevărat **doar pe prima bară** din domeniu care satisface predicatul intern; lookahead-safe (folosește doar bare până la și inclusiv bara curentă din domeniu);
- replică exact `next(i for i in idx if high>ph)` din scripturi: dacă prima depășire nu respinge, evenimentul nu se declanșează în acea zi, chiar dacă o bară ulterioară ar respinge;
- scope `day` = 00:00 UTC (regula nouă `day_scope_boundary`), identic cu `df["dt"].dt.date` din in-sample.

**Fără schemă nouă și fără tip nou de gramatică:** tipul de referință `predicate` exista deja. Singura modificare de cod în validator: `_iter_predicates` recursează acum și în parametrul-predicat singular (`first_in_scope.predicate`), pentru ca id-urile interne să intre în unicitatea globală și variabilele interne în graful de dependențe.

---

## 4. Diferențele exacte v1.2 → v1.3

| | v1.2 | v1.3 |
|---|---|---|
| `registry_version` | 1.2 | 1.3 |
| `population_predicates` | 10 | **11** (`+first_in_scope@v1`) |
| `rules` | 14 | **15** (`+day_scope_boundary`) |
| `variable_primitives` | 16 | 16 (neschimbat) |
| metode test / corecții / statusuri | 12 / 3 / toate UNVALIDATED | **identic** |
| schema JSON | neatinsă | **neatinsă** (hash `f1ba7009…`) |

---

## 5. G8 — familia Bonferroni empirică (gol nou, NEREZOLVAT)

`obs0012` calculează familia din date: `cells = [(d,s) if len(rej)≥25]`, apoi `thr = 0.05/len(cells)`. Mărimea familiei depinde de câte celule (din 4 sesiuni × 2 direcții) ating n≥25 — potențial inclusiv „late".

Modelul VE cere `multiple_testing.members` **enumerați static**, iar motorul nu deduce apartenența la familie. O familie a cărei mărime depinde de date **nu poate fi enumerată în avans**.

- **Impact:** blochează caracterul complet al specificației oficiale DC-0004 (convenția #4 din lista CEO).
- **În fixtură:** cele 8 celule K6 sunt enumerate static ca **substituent nenormativ**, marcat explicit (`family_id` conține `STATIC-PLACEHOLDER-for-empirical-n25`, câmp `_nonnormative`).
- **Posibilă rezolvare (nepropusă spre implementare acum):** un parametru declarat `min_member_n` la `bonferroni@v1` — un prag **declarat** de Statistician, nu inferat de motor, deci compatibil cu principiul „motorul nu decide familia". Necesită autorizare separată.

Conform instrucțiunii permanente, G8 este **înregistrat și nerezolvat**.

---

## 6. Tensiunea seed=7 (NEREZOLVATĂ, decizie CEO)

Scripturile in-sample folosesc `seed=7` fix. Schema VE fixează `seed_policy` la singura valoare `derived_from_spec_hash` — seed determinist derivat din hash-ul specificației, **tocmai pentru a împiedica alegerea unei semințe** (arhitectură §10, anti-seed-shopping).

- **Un `seed=7` literal nu este exprimabil** fără o excepție de schemă/arhitectură.
- **Pentru holdout, seed-ul literal este imaterial pentru replicare:** holdout-ul e alt eșantion, deci seed=7 nu reproduce numerele in-sample oricum; ce contează pentru replicarea *metodei* este estimatorul (același B, aceeași reeșantionare pe sesiune, aceeași coadă), iar `derived_from_spec_hash` asigură reproductibilitatea rulării pe holdout.
- **Decizie CEO necesară:** (a) se acceptă seed-ul derivat determinist ca fiind „replicarea" (recomandarea implicită a designului de reproductibilitate), sau (b) se autorizează o excepție de schemă pentru un seed literal. Nu am ales — fixtura folosește `derived_from_spec_hash` și marchează punctul.

---

## 7. Este specificația completă și executabilă structural?

**Structural validă: DA.** `reference_spec_dc0004.json` (Calea A) validează cu **4 × E3 (porți de calibrare: `matched_null` ×2, `multiverse`, `bonferroni`), zero erori non-E3, zero accesări de date.** Evenimentul „prima depășire", cele 4 sesiuni UTC, cele 8 celule, baseline-ul per sesiune, testul one-sided — toate se exprimă fără gol de vocabular.

**Completă pentru replicare strictă: NU.** Două dintre cele opt convenții Calea A nu sunt exprimabile:
- **G8** — familia Bonferroni empirică n≥25 (blocaj de vocabular; substituent static în fixtură);
- **seed=7** — literal (blocaj de schemă/politică; derived în fixtură).

Prin urmare specificația **nu poate fi încă blocată ca normă oficială executabilă**. Devine completă după: (1) o decizie asupra G8 (ex. autorizarea unui `min_member_n` declarat), și (2) o decizie asupra seed (acceptăm derived, sau excepție de schemă). Ambele sunt decizii CEO; niciuna nu e o alegere a Validation Engine.

Restul (Q1/Q3) este acum **decis**: convențiile Calea A sunt oficiale pentru DC-0004, iar acele părți ale fixturii nu mai sunt nenormative — doar G8 și seed rămân marcate.

---

## 8. Fișiere create, modificate, șterse

**Create (3):** `CAPABILITY_REGISTRY_v1.3.md`, `SPEC_TEMPLATE_v1.3.json`, `F2_3_REPORT.md`.
**Modificate (7):** `capabilities.json` (v1.3), `ve/spec/registry_validator.py` (recursie + `first_in_scope`), `tests/fixtures/reference_spec_dc0004.json` (Calea A, rescrisă), `tests/fixtures/{fixture_baseline_spec,reference_spec_dc0008}.json` (**doar câmpul `capability_registry_version` → 1.3; DC-0008 fără schimbare de design**), `tests/mutations.py` (+M75–M78), `tests/test_reference_spec.py` + `tests/test_schema_and_registry.py`, `SPEC_SCHEMA_v1.0.md`, `VE_BACKLOG.md`.
**Șters (1):** `SPEC_TEMPLATE_v1.2.json` (înlocuit de v1.3).

**Nemodificat, verificat prin hash:** `SPEC_SCHEMA_v1.0.json` (`f1ba7009…`), `ve/spec/{schema_validator,validate,loader,domains}.py`, `ve/errors.py`, `ve/audit/access_audit.py`, `ve/clarification.py`, `ve/cli.py`, `CAPABILITY_REGISTRY_v1.0/1.1/1.2.md`, arhitectura, contractul, constituția. `reference_spec_dc0008.json` — design neatins (doar tag de versiune).

---

## 9. Teste și integritate

```
../venv/Scripts/python.exe -m pytest tests -q
326 passed in 1.25s
```

- **Bateria de mutații:** 78 (F2.2: 74, +M75–M78 pentru G7). Toate opresc; niciuna nu atinge date.
- **Zero accesări de date** pe toate mutațiile și toate erorile; hash-urile celor 4 surse identice cu F1.
- **`ve capabilities`:** 0 metode executabile; `status = PUBLISHED_NOT_EXECUTABLE`; 15/15 `UNVALIDATED`.
- **Integritate repo:** nimic modificat în afara `validation_engine/`.

---

## 10. Confirmări finale

| Cerință | Stare |
|---|---|
| G6 nerezolvat | ✅ neatins |
| DC-0008 nemodificat (design) | ✅ doar tag de versiune 1.2→1.3, fără schimbare de conținut |
| F3 neînceput | ✅ |
| Toate metodele UNVALIDATED | ✅ 15/15 |
| Registru PUBLISHED_NOT_EXECUTABLE | ✅ |
| Schema JSON neschimbată | ✅ hash identic |
| Date de piață neatinse | ✅ hash-uri identice |

---

**Validation Engine se oprește aici. Specificația oficială DC-0004 (Calea A) este structural validă, dar necesită două decizii CEO (G8 și seed) înainte de a putea fi completă și blocată ca normă executabilă. Aștept aprobarea.**
