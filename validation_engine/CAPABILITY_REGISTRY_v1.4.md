# CAPABILITY REGISTRY v1.4
### Vocabularul executabil al Validation Engine — catalogul publicat către Statistician

**Document ID:** VE-CAPREG-v1.4
**Data:** 2026-07-25 · **Autor:** Validation Engine · **Autoritate:** decizie CEO 2026-07-25 (G8 prin varianta V1)
**Înlocuiește:** `CAPABILITY_REGISTRY_v1.3.md` (păstrat ca istoric)
**Statut:** **PUBLICAT — NEEXECUTABIL.** Nicio metodă nu are statusul `VALIDATED`.
**Forma normativă:** `capabilities.json`

---

## 0. Ce s-a schimbat față de v1.3

Revizuirea acoperă **strict** golul G8 — familia de corecție cu apartenență dependentă de date, exprimată printr-o **regulă de eligibilitate declarativă limitată la câmpuri pre-rezultat** (varianta V1 din `REGISTRY_GAP_G8_DESIGN.md`).

| # | Schimbare |
|---|---|
| 1 | **Lista albă `member_eligibility_fields` = `[n, denominator, event_count]`** — singurele câmpuri pe care o regulă de eligibilitate le poate referi. `p_hat/observed/effect/statistic` sunt **deliberat absente** |
| 2 | `bonferroni@v1` și `benjamini_hochberg@v1` cer acum **`member_eligibility {field, op, value}`** |
| 3 | Patru reguli noi: lista albă (R3), regula declarată, oprirea pe familie vidă, eligibilitate obligatorie (fără omisiune) |

Nicio metodă adăugată/eliminată/promovată. Fără schemă nouă (regula stă în `multiple_testing.params`, obiect liber). `rules`: **15 → 19**.

---

## 1. `member_eligibility` — semantică și regula de aur

O familie de corecție poate avea membri candidați enumerați static, dar **eligibili doar dacă satisfac o condiție pe mărimea de eșantion**:

```json
"multiple_testing": {
  "members": [ ...cei 8 candidați... ],
  "method": "bonferroni@v1",
  "params": { "alpha": 0.05, "family_members": [...],
              "member_eligibility": { "field": "n", "op": ">=", "value": 25 } }
}
```

- **Familia realizată** = membrii candidați care satisfac regula; `m` = numărul lor; pragul corectat = `alpha / m`. Calculul se face la **execuție** (are nevoie de `n`, deci de date, F5+).
- **REGULA DE AUR R3 — independență de rezultat:** `field` provine **exclusiv** din lista albă `[n, denominator, event_count]`, toate pre-rezultat. `p_hat/observed/effect/statistic` **nu sunt în listă**, deci o regulă care le referă se oprește la validare (E2), înainte de orice date. **Apartenența la familie nu poate depinde sintactic de niciun rezultat** — garanția este de vocabular, nu de disciplină.
- **Declarată, nu dedusă:** regula `n≥25` este scrisă în specificație și înghețată în hash; motorul o aplică, niciodată nu o inventează.
- **Validatorul verifică doar structura și lista albă** (`{field, op, value}`, field ∈ listă, value numeric); **nu calculează familia**.
- **Familie eligibilă vidă → oprire explicită** la execuție (E6 PRECONDITION), niciodată corecție tăcută pe o familie goală.
- **„Fără filtrare" se declară explicit** (ex. `{field: n, op: >=, value: 1}`), niciodată prin omisiune — ca `none@v1` pentru corecție.

### 1.1 De ce lista albă este mecanismul, nu o convenție

Dacă `field` ar accepta orice șir, un autor ar putea scrie `{field: p_hat, op: <, value: 0.05}` — filtrare după rezultat, adică selecția circulară pe care G8 trebuie să o prevină. Lista albă închisă face acest lucru **imposibil de exprimat**: câmpul de rezultat nu există în vocabular, deci nu poate fi numit. Aceasta este forma cea mai tare a garanției — nu „verificăm că schimbarea lui p nu schimbă familia", ci „familia nu poate referi p deloc".

---

## 2. Restul catalogului

Neschimbat față de v1.3. 4 surse; graniță sigilată `2025-10-23T09:15:00Z`; 16 primitive de variabile (`indicator@v1`, `raw_series@v1`, …); 11 predicate de populație (`first_in_scope@v1`, …); 7 statistici; 12 metode de test + 3 corecții, toate `UNVALIDATED`; tipuri de referință rezolvate fail-closed (`variable_ref`, `test_ref`, `predicate_ref`, `eligibility_rule`).

Vezi `CAPABILITY_REGISTRY_v1.3.md` pentru detaliile neschimbate.

---

## 3. Impact generic

G8 nu este specific DC-0004. Aceeași regulă de eligibilitate se aplică la orice familie cu membri de suport variabil: DC-0008 + dependenți, teste stratificate cu celule subțiri, grile multiverse, și FDR-ul de portofoliu (unde `EMPIRICAL_PVALUE_SPEC.md` folosea deja informal „universul eligibil" — acum devine o proprietate declarată și auditabilă).

---

## 4. Goluri rămase deschise

| ID | Gol | Status |
|---|---|---|
| **G6** | agregare sub-bară / sursă M1-M5 (expunerea R a DC-0008) | `DESCHIS` (CEO: nerezolvat în această fază) |

---

**Statusul registrului la v1.4: PUBLICAT — NEEXECUTABIL. Toate metodele sunt `UNVALIDATED`.**
