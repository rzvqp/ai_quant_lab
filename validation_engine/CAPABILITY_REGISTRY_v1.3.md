# CAPABILITY REGISTRY v1.3
### Vocabularul executabil al Validation Engine — catalogul publicat către Statistician

**Document ID:** VE-CAPREG-v1.3
**Data:** 2026-07-24 · **Autor:** Validation Engine · **Autoritate:** decizie CEO 2026-07-24 (DC-0004 = Calea A, replicare strictă; rezolvă G7)
**Înlocuiește:** `CAPABILITY_REGISTRY_v1.2.md` (păstrat ca istoric)
**Statut:** **PUBLICAT — NEEXECUTABIL.** Nicio metodă nu are statusul `VALIDATED`.
**Forma normativă:** `capabilities.json`

---

## 0. Ce s-a schimbat față de v1.2

Revizuirea acoperă **strict** golul G7, necesar pentru a exprima evenimentul in-sample al DC-0004 sub Calea A.

| # | Schimbare | Motiv |
|---|---|---|
| 1 | Predicat nou: **`first_in_scope@v1 {scope, predicate}`** — adevărat doar pe **prima** bară dintr-un domeniu (`day`/`session`/`week`) care satisface predicatul intern; lookahead-safe | G7 — evenimentul „prima bară a zilei care depășește nivelul" |
| 2 | Regulă nouă: **`day_scope_boundary`** — granița scope-ului `day` este **00:00 UTC** (Calea A), identică cu scripturile in-sample (`df["dt"].dt.date`) | fixarea convenției oficiale de zi |

Nicio metodă de test/corecție adăugată, eliminată sau promovată. Nicio schemă nouă (tipul `predicate` din gramatică era deja disponibil). `population_predicates`: **10 → 11**; `rules`: **14 → 15**; `variable_primitives` neschimbat (16).

---

## 1. `first_in_scope@v1` — semantică

```json
{
  "id": "ev_first_up_breach",
  "predicate": "first_in_scope@v1",
  "params": {"scope": "day",
             "predicate": {"id": "ev_up_breach", "predicate": "compare@v1",
                           "params": {"left": "bar_high", "op": ">", "right": "pdh"}}}
}
```

- **Adevărat doar pe prima bară** din domeniu unde predicatul intern e adevărat; fals pe toate celelalte, inclusiv pe barele ulterioare care ar satisface și ele condiția.
- **Lookahead-safe:** determinarea „prima" folosește doar bare până la și inclusiv bara curentă din domeniu.
- **Compunere:** evenimentul in-sample „prima bară care depășește PDH, apoi respinge" = `and(first_in_scope(day, high>PDH), close<PDH)`. Dacă prima depășire nu respinge, evenimentul nu se declanșează în acea zi — chiar dacă o bară ulterioară ar respinge. Replică exact `next(i for i in idx if high>ph)` + verificarea `close<ph` din `obs0003/0008/0012/0013`.
- **Domeniu `day` = 00:00 UTC** (regula `day_scope_boundary`). Un domeniu ancorat local (direcția `OPERATIONAL_DEFINITIONS` a Statisticianului) ar cere un scope separat, explicit versionat, și un protocol separat.
- Predicatul intern intră sub aceleași reguli ca orice predicat: id unic pe întreaga specificație, variabile rezolvate, garda de leakage pe variabilele folosite.

---

## 2. Restul catalogului

Neschimbat față de v1.2. 4 surse de date; graniță sigilată `2025-10-23T09:15:00Z`; 16 primitive de variabile (inclusiv `indicator@v1`, `raw_series@v1`); **11** predicate de populație (adăugat `first_in_scope@v1`); 7 statistici; 12 metode de test + 3 corecții, toate `UNVALIDATED`; tipurile de referință `variable_ref`/`test_ref`/`predicate_ref` rezolvate fail-closed.

Vezi `CAPABILITY_REGISTRY_v1.2.md` pentru detaliile neschimbate.

---

## 3. Goluri rămase deschise (consemnate în backlog, NEREZOLVATE)

| ID | Gol | De ce nu e rezolvat aici |
|---|---|---|
| **G6** | agregare sub-bară / sursă M1-M5 (expunerea R a DC-0008) | CEO: „Nu rezolva G6 în acest pas" |
| **G8** | familia Bonferroni **empirică** (celule cu n≥25) — apartenența depinde de date; modelul cere enumerare statică | descoperit la exprimarea Căii A; nu a fost autorizată rezolvarea; blochează caracterul complet al specificației DC-0004 |
| **seed** | `seed=7` literal — schema fixează `seed_policy` la `derived_from_spec_hash` (anti-seed-shopping) | tensiune între replicarea strictă și modelul de reproductibilitate; cere decizie CEO |

---

**Statusul registrului la v1.3: PUBLICAT — NEEXECUTABIL. Toate metodele sunt `UNVALIDATED`.**
