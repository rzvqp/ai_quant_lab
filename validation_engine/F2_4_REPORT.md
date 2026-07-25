# F2.4 — RAPORT DE LIVRARE
### G8 rezolvat (varianta V1) · Capability Registry v1.4 · DC-0004 replicare strictă completă

**Document ID:** VE-F24-REPORT-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Autoritate:** decizie CEO 2026-07-25 — implementarea G8 prin varianta V1 (eligibilitate declarativă pe listă albă pre-rezultat).
**Statut:** livrat, în așteptarea aprobării. **F3 NU a fost început. G6 NU a fost rezolvat. Nicio metodă statistică implementată. Nicio dată de piață citită.**

---

## 1. Cerințele CEO — respectate punct cu punct

| Cerință | Stare |
|---|---|
| `member_eligibility` doar din lista albă `n, denominator, event_count` | ✅ listă albă închisă în registru |
| Orice referire la p-value/statistică/efect respinsă fail-closed | ✅ câmpul de rezultat nu e în listă → E2 înainte de date (M79–M81) |
| Regula `n≥25` declarată în specificație, nu dedusă | ✅ `member_eligibility` e în specificația înghețată; motorul o aplică |
| Validatorul verifică doar structura și câmpurile permise, fără să calculeze familia | ✅ calculul familiei e execuție (F5+), nu validare |
| La execuție, membrii neeligibili sunt excluși conform regulii | ✅ specificat (rule `member_eligibility_declared`); execuția e F5+ |
| Familie eligibilă vidă → oprire explicită | ✅ specificat (rule `empty_eligible_family_halts`, E6 runtime) |
| Fără excepții specifice DC-0004 | ✅ mecanism generic; se aplică la Bonferroni și BH deopotrivă |
| Schema JSON neschimbată dacă se poate | ✅ regula stă în `multiple_testing.params`; schema neatinsă (hash identic) |
| Toate metodele `UNVALIDATED` | ✅ 15/15 |
| Registru `PUBLISHED_NOT_EXECUTABLE` | ✅ |
| F3 neînceput | ✅ |

---

## 2. Mecanismul G8 (varianta V1)

O familie de corecție are membri candidați enumerați static, dar **eligibili doar dacă satisfac o regulă pe mărimea de eșantion**:

```json
"multiple_testing": {
  "members": [ ...8 candidați... ],
  "method": "bonferroni@v1",
  "params": { "alpha": 0.05, "family_members": [...],
              "member_eligibility": { "field": "n", "op": ">=", "value": 25 } }
}
```

**Regula de aur R3, impusă prin vocabular, nu prin disciplină:** `field` provine exclusiv din lista albă `[n, denominator, event_count]`. Câmpurile de rezultat (`p_hat`, `observed`, `effect`, `statistic`) **nu există în vocabular**, deci o regulă care le-ar referi **nu poate fi nici măcar scrisă** fără a fi respinsă la validare. Aceasta este forma cea mai tare a garanției cerute de CEO: nu „verificăm că schimbarea lui p nu schimbă familia", ci **familia nu poate referi p deloc** (vezi §5).

---

## 3. Diferențele exacte v1.3 → v1.4

| | v1.3 | v1.4 |
|---|---|---|
| `registry_version` | 1.3 | 1.4 |
| `member_eligibility_fields` (listă albă) | — | **`[n, denominator, event_count]`** |
| `bonferroni@v1.required_params` | alpha, family_members | **+ member_eligibility** |
| `benjamini_hochberg@v1.required_params` | alpha, family_members, variant | **+ member_eligibility** |
| ieșiri Bonferroni/BH | … | **+ realized_family, dropped_members, m_realized** |
| `rules` | 15 | **19** (+whitelist, +declared, +empty-family-halt, +no-optional) |
| gramatică | — | **+`eligibility_rule`** (tip de referință) |
| schema JSON | neatinsă | **neatinsă** (hash `f1ba7009…`) |
| statusuri de calibrare | 15× UNVALIDATED | **identic** |

---

## 4. DC-0004 — replicare strictă COMPLETĂ

`tests/fixtures/reference_spec_dc0004.json` validează cu **4 × E3 (porți de calibrare), zero non-E3, zero accesări de date.**

**Substituentul nenormativ a fost eliminat.** Familia empirică e acum declarată direct:
```
family_id: "DC-0004-K6-session-direction-cells-eligible-n25"
member_eligibility: { field: "n", op: ">=", value: 25 }
```
Cei 8 candidați rămân enumerați; eligibilitatea `n≥25` îi filtrează la execuție, exact ca `obs0012`.

**Câmpul `_nonnormative` a dispărut complet.** Toate cele opt convenții Calea A sunt acum exprimate normativ:

| # | Convenție | Exprimare |
|---|---|---|
| 1 | graniță de zi 00:00 UTC | scope `day` (regula `day_scope_boundary`) |
| 2 | 4 sesiuni fixe UTC | `session_label@v1` cu 4 granițe |
| 3 | eveniment = prima depășire | `first_in_scope@v1` (G7) |
| 4 | **familie Bonferroni empirică n≥25** | **`member_eligibility` (G8)** ✅ |
| 5 | K6 decisiv | `T1_matched_null_k6` |
| 6 | baseline per sesiune | `baseline_forward_mean@v1` strata=[session] |
| 7 | one-sided | `tail: left` |
| 8 | seed | `derived_from_spec_hash` (politica decisă, înlocuiește seed=7 literal) |

> **Răspuns la întrebarea finală: DA, DC-0004 este acum complet exprimabil pentru replicare strictă.** Toate cele opt convenții sunt exprimate; nu mai există gol de vocabular, substituent sau câmp nenormativ. Singurele opriri rămase sunt cele patru porți de calibrare — care cad odată ce metodele trec bateriile din F5–F6.

Notă onestă asupra seed (§8): convenția in-sample era `seed=7` literal; politica de reproductibilitate a laboratorului (decizie CEO) o înlocuiește cu `derived_from_spec_hash`. Aceasta este singura convenție Calea A care **nu** este o copie literală a scriptului — dar este o decizie de guvernanță asumată, nu un gol. Pentru holdout (alt eșantion) seed-ul literal era oricum imaterial.

---

## 5. Confirmarea că p-value-urile nu pot schimba apartenența la familie

Cerută explicit de CEO. Confirmată în forma cea mai tare posibilă — **structural, nu doar empiric:**

- `member_eligibility.field` acceptă **exclusiv** valori din lista albă `[n, denominator, event_count]`.
- `p_hat`, `p_adjusted`, `observed`, `effect`, `statistic` **nu sunt în listă**, deci o regulă care le referă se oprește la validare (E2), **înainte de orice acces la date**.
- Test dedicat `test_g8_result_fields_are_rejected_fail_closed`: pentru fiecare dintre cele cinci câmpuri de rezultat, regula e respinsă, `data_accesses == []`, iar motivul menționează explicit interdicția.
- Mutațiile M79 (p_hat), M80 (observed), M81 (statistic): toate opresc fail-closed.

**Concluzie:** apartenența la familie nu poate depinde **sintactic** de niciun rezultat. Nu este nevoie de un test runtime „schimbăm p și verificăm că familia nu se schimbă" — familia nu poate referi p în primul rând. Garanția e de vocabular, imposibil de ocolit.

---

## 6. Bateria de mutații

**87 de mutații** (F2.3: 78, +M79–M87 pentru G8). Toate opresc; niciuna nu atinge date.

| ID | Mutație | Cod |
|---|---|---|
| M79 | R3: eligibilitate după p-value (INTERZIS) | E2 |
| M80 | R3: eligibilitate după efect observat (INTERZIS) | E2 |
| M81 | R3: eligibilitate după statistică (INTERZIS) | E2 |
| M82 | câmp de eligibilitate inexistent (`sharpe`) | E2 |
| M83 | `value` ne-numeric | E2 |
| M84 | regulă malformată (chei lipsă) | E2 |
| M85 | `member_eligibility` absent (obligatoriu la Bonferroni) | E2 |
| M86 | eligibilitate validă pe `denominator` (se oprește doar pe calibrare) | E3 |
| M87 | eligibilitate validă pe `event_count` (se oprește doar pe calibrare) | E3 |

Distribuție totală: E1:18, E2:55, E3:12, E5:2.

---

## 7. Fișiere create, modificate, șterse

**Create (3):** `CAPABILITY_REGISTRY_v1.4.md`, `SPEC_TEMPLATE_v1.4.json`, `F2_4_REPORT.md`.
**Modificate (8):** `capabilities.json` (v1.4), `ve/spec/domains.py` (+`eligibility_rule`), `ve/spec/registry_validator.py` (rezolvarea `eligibility_rule` + R3), `tests/fixtures/reference_spec_dc0004.json` (familie empirică, `_nonnormative` eliminat), `tests/fixtures/{fixture_baseline_spec,reference_spec_dc0008}.json` (registru 1.4 + `member_eligibility` — compatibilitate, fără schimbare de design DC-0008), `tests/mutations.py` (+M79–M87), `tests/test_reference_spec.py` + `tests/test_schema_and_registry.py`, `SPEC_SCHEMA_v1.0.md`, `VE_BACKLOG.md`.
**Șters (1):** `SPEC_TEMPLATE_v1.3.json` (înlocuit de v1.4).

**Nemodificat, verificat prin hash:** `SPEC_SCHEMA_v1.0.json` (`f1ba7009…`), `ve/spec/{schema_validator,validate,loader}.py`, `ve/errors.py`, `ve/audit/access_audit.py`, `ve/clarification.py`, `ve/cli.py`, `CAPABILITY_REGISTRY_v1.0–1.3.md`, arhitectura, contractul, constituția.

---

## 8. Teste și integritate

```
../venv/Scripts/python.exe -m pytest tests -q
360 passed in 1.39s
```

- **Bateria de mutații:** 87. Toate opresc; niciuna nu atinge date.
- **Zero accesări de date** pe toate mutațiile și toate erorile; hash-urile celor 4 surse identice cu F1.
- **DC-0004** validează 4×E3; **DC-0008** 8×E3; **baseline** 2×E3 — toate zero non-E3, zero accesări.
- **`ve capabilities`:** 0 metode executabile; `PUBLISHED_NOT_EXECUTABLE`; 15/15 `UNVALIDATED`.
- **Integritate repo:** nimic modificat în afara `validation_engine/`.

---

## 9. Confirmări finale

| Cerință | Stare |
|---|---|
| G8 rezolvat prin V1, listă albă pre-rezultat | ✅ |
| Filtrarea după rezultat imposibilă (structural) | ✅ §5 |
| Substituentul nenormativ eliminat din DC-0004 | ✅ |
| DC-0004 complet exprimabil pentru replicare strictă | ✅ §4 |
| G6 nerezolvat | ✅ neatins |
| F3 neînceput | ✅ |
| Toate metodele UNVALIDATED, registru PUBLISHED_NOT_EXECUTABLE | ✅ |
| Schema JSON neschimbată | ✅ hash identic |
| Date de piață neatinse | ✅ hash-uri identice |

---

**Validation Engine se oprește aici. G8 este rezolvat generic; DC-0004 este complet exprimabil pentru replicare strictă, blocat doar de porțile de calibrare (F5–F6). Aștept aprobarea.**
