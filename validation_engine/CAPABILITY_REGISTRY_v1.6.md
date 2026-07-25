# CAPABILITY REGISTRY v1.6
### Vocabularul executabil al Validation Engine — catalogul publicat către Statistician

**Document ID:** VE-CAPREG-v1.6
**Data:** 2026-07-25 · **Autor:** Validation Engine · **Autoritate:** decizie CEO 2026-07-25 (promovarea `bonferroni@v1` prin suita S7)
**Înlocuiește:** `CAPABILITY_REGISTRY_v1.5.md` (păstrat ca istoric)
**Statut:** **PARȚIAL EXECUTABIL — 2 din 15 metode `VALIDATED`.**
**Forma normativă:** `capabilities.json`

---

## 0. Ce s-a schimbat față de v1.5

O singură metodă promovată, printr-o suită **deterministă**. Nimic stocastic.

| # | Schimbare |
|---|---|
| 1 | **`bonferroni@v1`: `UNVALIDATED` → `VALIDATED`** prin suita **S7** (decizie CEO 2026-07-25) |
| 2 | **`status`: rămâne `PARTIALLY_EXECUTABLE`; metode validate `1/15` → `2/15`** |
| 3 | Implementat contractul de ieșiri al lui `bonferroni@v1` în `ve/methods/bonferroni.py` (funcție pură) |
| 4 | `bonferroni@v1` primește un obiect `validation` (suită S7, determinist, cele șase verificări) |
| 5 | Celelalte 13 metode rămân `UNVALIDATED` |

---

## 1. De ce S7 (determinist), nu o baterie F6 (stocastică)

Registrul **distinge tipurile de metode prin câmpul `acceptance_suites`**, per-metodă. `bonferroni@v1`, `benjamini_hochberg@v1` și `none@v1` poartă **exclusiv S7** — disjunctă de suitele stocastice `S1/S3/S4` purtate de `matched_null@v1`, `permutation_test@v1`, `block_bootstrap@v1` etc.

Bonferroni este `p × m`. Garanția FWER ≤ α este **inegalitatea Boole — o teoremă**, nu o proprietate empirică. Nu are distribuție null, putere, FPR sau seed de calibrat. Calibrarea p-values-urilor de intrare este responsabilitatea metodei din **amonte** (S1/S3/S4 pe ea), nu a corecției. Deci suita corectă e deterministă.

Taxonomia se închide curat: corecția family-wise **stocastică** (max-T prin permutare, cerută de DC-0008 §4.8) **nu e** `bonferroni@v1`, ci `permutation_test@v1`, care poartă S1/S3/S4.

## 2. Suita S7 — cele șase verificări executate (`tests/test_s7_bonferroni.py`)

1. **Aritmetică** pe fixturi cu răspuns cunoscut: `threshold_per_test = α/m`, `p_adjusted = min(1, p×m)`, plafonare la 1, `m=1` = fără efect.
2. **Contabilitatea familiei realizate**: `member_eligibility` pe câmpuri pre-rezultat → `eligible_cells`, `dropped_members`, `m_realized` exacte.
3. **Familie eligibilă vidă** → oprire **E6 PRECONDITION** (`empty_eligible_family_halts`), niciodată corecție tăcută pe `m=0`.
4. **Independență de rezultat (R3)** la stratul de execuție: o regulă care referă `p_hat/observed/effect/statistic` e respinsă `E2` înainte de date.
5. **„Fără filtrare" declarat explicit**: regula trivial-adevărată (`n≥1`) păstrează familia întreagă; `member_eligibility` e parametru obligatoriu.
6. **Determinism / idempotență**: aceleași intrări → aceeași familie, aceleași praguri, aceiași p ajustați. Fără RNG, fără seed.

Zero serii sintetice, zero curbă de putere, zero FPR, zero baterie adversarială.

## 3. Restul catalogului

Neschimbat față de v1.5. 4 surse (M15/H1/H4/D1); graniță sigilată `2025-10-23T09:15:00Z`; 16 primitive; 11 predicate; 7 statistici; **13 metode rămase `UNVALIDATED`**. Regula `unvalidated_not_executable` rămâne activă. Vezi `CAPABILITY_REGISTRY_v1.5.md` / `v1.4.md` pentru detaliile neschimbate.

## 4. Goluri rămase deschise

| ID | Gol | Status |
|---|---|---|
| **G6** | agregare sub-bară / sursă M1-M5 (expunerea R a DC-0008) | `DESCHIS` — blocantul structural al DC-0008 Phase 2 |

---

**Statusul registrului la v1.6: PARȚIAL EXECUTABIL. `matched_null@v1` (S1/S3/S4) + `bonferroni@v1` (S7) = `VALIDATED` (2/15). Restul de 13: `UNVALIDATED`.**
