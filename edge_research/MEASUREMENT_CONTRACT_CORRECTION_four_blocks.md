# CORECȚIE — populația canonică = PATRU blocuri (nu trei). CEO 2026-08-13.

**Divizie:** Data Acquisition · corectează supra-îndreptarea M-4 din `MEASUREMENT_CONTRACT_R8_R9.md`.
Fix-ul anterior colapsase la **3** (cele 3 `discovery_range` din `segmentation_plan`) → arunca tacit ~3 ani (2022-12→2025-10), blocul cel mai recent și mai mare. A doua eroare, în direcția opusă. **Corectat la 4.**

---

## Ce am corectat

| # | Fișier | Schimbare |
|---|---|---|
| 1 | `_contract.py` | `canonical_discovery_blocks(manifest, tf)` NOU — sursa unică a celor **4** blocuri, din `context_derived_htf.m15_v2_discovery_blocks`. `official_blocks` + `dataset_identity` îl folosesc (nu `segmentation_plan`, care dă 3). |
| 2 | `_screen.derive_blocks` | întoarce acum **4** blocuri (via `official_blocks` stampat de loader), nu 3. |
| 3 | `_common.load` | livrează populația celor **4** blocuri: `in_disc` din `canonical_discovery_blocks` (nu `segmentation_plan`). `official_blocks_n` + `dataset_identity.n_discovery_segments` = 4. |

**Verificat live (M15_v2, cutoff 2025-10-23):**
- Livrare: **197.094 bari** (era 130.491), 2011-07-26 → **2025-10-12**. Include 2022-12→2025-10 ✓.
- `official_blocks` (4): `(0,52403) (52403,105254) (105254,130491) (130491,197094)`.
- Al 4-lea bloc: 2022-12-16 → 2025-10-12 (~66.600 bari, ~3 ani).
- `derive_blocks` → 4. Tripwire de tiling pasează (cele 4 tapetează frame-ul). mypy --strict clean.
- Cele 15 blocuri din goluri rămân INTERZISE (fallback doar pentru df ne-manifest, cu warning).

## Task 4 — al 4-lea bloc e sigilat pentru DISCOVERY? **NU.** (distincție scrisă explicit)

Sunt **două entități diferite** numite „a patra":
- **Al 4-lea REGIME_SEGMENT** = `bull_partial` (2022-10-31 → 2022-12-16). Prea scurt → **fără `discovery_range`**, sigilat pentru discovery. Corect exclus.
- **Al 4-lea BLOC DISCOVERY** = 2022-12-16 → 2025-10-12 (din `overlap_with_M15`, „inherits M15's discovery classification verbatim"). Este **DISCOVERY COMPLET** — listat explicit în `m15_v2_discovery_blocks`.

**Concluzie:** al 4-lea BLOC **nu** e sigilat pentru discovery — e populație pentru **AMBELE**: ferestrare/granițe **ȘI** selecție de ipoteze (e clasificarea discovery a M15, moștenită). Deci **nu** există un bloc „windowing-dar-nu-selecție" aici. Confuzia vine din omonimia „al 4-lea segment" (sigilat) vs „al 4-lea bloc" (discovery) — două lucruri distincte.

## ⚠ Inconsistență de manifest expusă (a Statisticianului)

Decizia CEO (4 blocuri) scoate la iveală o inconsistență INTERNĂ a manifestului:
- `segmentation_plan` (derivat din `regime_segments.discovery_range`) → **3** blocuri, tratează overlap-ul ca **sealed**.
- `context_derived_htf.m15_v2_discovery_blocks` → **4** blocuri, tratează overlap-ul ca **discovery**.

Fix-ul meu sursează din cele **4** (`m15_v2_discovery_blocks`), per decizia CEO. Asta creează o **divergență între `_common.load`/contract (4) și `segmentation_plan` (3)**. Reconcilierea DEFINITIVĂ e la nivel de manifest = **treaba Statisticianului** (nu ating manifestul): fie `regime_segments`/`segmentation_plan` se aliniază la 4, fie se documentează de ce coexistă. Am folosit `m15_v2_discovery_blocks` ca autoritate canonică fiindcă e lista pe care CEO a ratificat-o.

**Două teste loader pică** (encodează asumpția veche „overlap = sealed", acum răsturnată de CEO):
- `test_delivered_is_exactly_the_union_of_discovery_segments[M15_v2]` (asertează unirea celor 3).
- `test_m15_v2_three_fully_sealed_zones_never_appear` (asertează overlap-ul nelivrat).

Nu le ating (asertează semantică de manifest, a Statisticianului). Trebuie actualizate ODATĂ cu reconcilierea manifestului (segmentation_plan → 4). 26/28 restul trec (+ testul stale H1 pre-existent, deja semnalat) → efectiv 26 verzi din 27 relevante.

## Decizia 1 — spread = bid-ask COMPLET

BASE `spread_price` 0,05 → componenta R3 = **0,05**; STRESS 0,08 → **0,08**. NU 0,10/0,16.
**Verificat: NU am stampat nicăieri componente duble (0,10/0,16).** `verify_m1.py` folosește 0,20/0,30/0,50 = ilustrație cost/R pe M1 (context diferit, nu componenta R3). În schema R11, `cost_model` e marcat owner Statistician/VE (fără valori stampate de mine). Nimic de corectat.

## D-4 — se aplică separat la marginea dreaptă a FIECĂRUIA din cele patru

Populația celor 4 blocuri expune **patru margini drepte distincte**, unde D-4 (censurarea trade-urilor deschise la graniță) se aplică separat, nu una singură la capătul global:

| Bloc | index range | marginea dreaptă (ultima bară) |
|---|---|---|
| 1 (bear) | (0, 52403) | **2013-09-27** |
| 2 (bull) | (52403, 105254) | **2018-04-06** |
| 3 (correction) | (105254, 130491) | **2021-09-03** |
| 4 (overlap discovery) | (130491, 197094) | **2025-10-12** |

Contractul le expune ca 4 ranges în `official_blocks` → orice consumator (inclusiv logica D-4 a Statisticianului) vede 4 granițe drepte, nu una. *D-4 în sine (marcare CENSORED) e a Statisticianului; datoria mea e doar să expun corect cele 4 granițe — făcut.*

## Confirmare transmitere test stale H1 → Statistician

Testul `tests/test_loader_holdout_boundary.py::test_h1_from_m15_v2_awaits_path_reconciliation` (aserta că fișierul H1_from_M15_v2 NU există, dar a fost reconciliat la calea canonică în manifest v2.4.2/2.7.48) e **TRANSMIS** Statisticianului — semnalat în `edge_research/MEASUREMENT_CONTRACT_R8_R9.md` (commit `750bd58`, pushed) + acest raport. E al lui (asertează semantică de manifest); eu nu-l ating. Confirmat transmis.

## Reconfirmare mandate anterioare (neschimbate)
- **Census motoare:** două motoare de decizie cu populație proprie divergentă (Flow A `mtf.load_mtf` whole-file; `relevance12m_perstrategy.py` scratch) → Statistician.
- **Tripwire:** `assert_population_matches_manifest` apelat fail-closed pe FIECARE `_common.load` (acum verifică tiling-ul celor 4 blocuri).
- **R11:** 4/13 dimensiuni furnizate de Data Acquisition (data-side complet); 6/13 Statistician/VE; 3/13 Research Lab.
