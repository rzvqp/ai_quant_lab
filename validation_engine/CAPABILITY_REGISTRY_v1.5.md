# CAPABILITY REGISTRY v1.5
### Vocabularul executabil al Validation Engine — catalogul publicat către Statistician

**Document ID:** VE-CAPREG-v1.5
**Data:** 2026-07-25 · **Autor:** Validation Engine · **Autoritate:** decizie CEO 2026-07-25 (promovarea `matched_null@v1`)
**Înlocuiește:** `CAPABILITY_REGISTRY_v1.4.md` (păstrat ca istoric)
**Statut:** **PARȚIAL EXECUTABIL — 1 din 15 metode `VALIDATED`.**
**Forma normativă:** `capabilities.json`

---

## 0. Ce s-a schimbat față de v1.4

O singură metodă a fost promovată. Nimic altceva nu s-a atins.

| # | Schimbare |
|---|---|
| 1 | **`matched_null@v1`: `UNVALIDATED` → `VALIDATED`** (decizie CEO 2026-07-25) |
| 2 | **`status`: `PUBLISHED_NOT_EXECUTABLE` → `PARTIALLY_EXECUTABLE`** (1/15 metode validate) |
| 3 | `matched_null@v1` primește un obiect `validation` cu **patru câmpuri de caveat obligatorii** (câmpuri, nu note de subsol) |
| 4 | Celelalte 14 metode rămân `UNVALIDATED` și **nu pot fi referite** de o specificație oficială (regula `unvalidated_not_executable`) |

Nicio metodă adăugată/eliminată. Nicio schemă nouă. Niciun alt status de calibrare schimbat.

---

## 1. `matched_null@v1` — VALIDATED, cu domeniu de validitate explicit

Promovarea se bazează pe F6 (uniformitate/FPR/putere/reproducibilitate) + F6.1 (vol pe sesiune + cozi grele) + F6.2 (drift real) + F6.3 (reversie AR1 / FPR multi-prag / placebo pe nivel arbitrar), toate la condițiile reale ale datelor, plus măsurătoarea φ AR(1) **condițional pe populația reală de evenimente NY-up**.

**Cele patru caveat-uri sunt câmpuri de prim rang în `capabilities.json`, nu note de subsol:**

1. **Domeniu de validare — forward K6 EXCLUSIV.** Punctul de rupere la reversie a fost măsurat pe curba K6. **K12 NU este acoperit:** φ condițional la K12 = −0.058 (~3× globalul −0.018), iar pragul de rupere la K12 nu a fost măsurat deloc. Orice utilizare la K12 sau alt orizont cere validare separată.
2. **Celula NY-up:** n ≈ 37–42, la granița calibrării. KS p=0.003 pe corpul distribuției (direcție conservatoare). Cozile nominale la 0.01 / 0.05 / 0.10.
3. **Vulnerabilitate confirmată la reversie** φ ≤ −0.10 (5.5× reala −0.018). φ condițional măsurat pe populația reală de evenimente: −0.018 la K6, cu CI [−0.228, +0.212] care **NU exclude** pragul. Estimarea punctuală confirmă marja; precizia nu o poate confirma la n=42. Imprecizia este un risc **specific DC-0004** (tipar de reversie), nu un risc al metodei.
4. **Configurație:** unstratified; stratificat pe **SESIUNE**; ATR-scaled. Stratificarea pe volatilitate **NU există și NU e validată.**

---

## 2. Restul catalogului

Neschimbat față de v1.4. 4 surse (M15/H1/H4/D1); graniță sigilată `2025-10-23T09:15:00Z`; 16 primitive de variabile; 11 predicate de populație; 7 statistici; **14 metode de test rămase `UNVALIDATED`** + 3 corecții `UNVALIDATED`; tipuri de referință rezolvate fail-closed. Regula `unvalidated_not_executable` rămâne activă: o specificație oficială **nu poate referi** nicio metodă care nu e `VALIDATED`.

Vezi `CAPABILITY_REGISTRY_v1.4.md` pentru detaliile neschimbate.

---

## 3. Goluri rămase deschise

| ID | Gol | Status |
|---|---|---|
| **G6** | agregare sub-bară / sursă M1-M5 (expunerea R a DC-0008) | `DESCHIS` (CEO: nerezolvat în această fază) — **rămâne blocantul structural al DC-0008 Phase 2** |

---

**Statusul registrului la v1.5: PARȚIAL EXECUTABIL. `matched_null@v1` = `VALIDATED` (1/15), cu domeniu K6. Restul de 14 metode: `UNVALIDATED`.**
