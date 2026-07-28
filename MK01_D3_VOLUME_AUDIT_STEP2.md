# MK-01 D3 VOLUME AUDIT — STEP 2 (Mandate 5.0)

**Autor:** Validation Engine · **Data:** 2026-07-28 · **Branch:** discovery-mk-matrix-v1
**Script:** `code/mk_d3_volume_audit.py` (rulabil, determinist).
**Rezultat: NICIUN bloc nu depășește 5% fereastră oarbă. Toate ≤ 0,04% → tier „ieftin" (≤1%). D3 se ratifică drept cost scăzut. LM-001 NU e blocat de D3.**

**Tensiune de guvernanță (repetată, nerezolvată):** am scris atât detectorul-de-test cât și scriptul de audit, și rulez măsurătoarea pe ele peste implementarea CEO. Statisticianul decide dacă CROSS-VERIFY-SPEC se aplică. Nu o rezolv.

**Conformitate cu interdicția:** audit de VOLUM GEOMETRIC. Se numără doar swing points (`detect_swings` + `label_structure`). ZERO interogare de preț pentru P&L, ZERO evaluare de performanță, ZERO apel LM-001, ZERO tranzacție. `detect_breaks` NU e folosit (deci Constatarea 2 din Step 1 nu atinge acest audit).

**Domeniu:** M15_v2, blocuri de descoperire din `config/split_manifest.json` v2.5.2 (`discovery_range` per regime_segment). **M5 EXCLUS prin D5** (mapare cross-rezoluție inexistentă) — exclus, nu omis. Segmentul 2022-2026 EXCLUS ca SAME-WINDOW-RESAMPLED. Toate blocurile auditate sunt 2011-2021 — cu mult înainte de granița sigilată 2025-10-23; auditul NU poate atinge holdout-ul.

---

## Rezultate per bloc

| Bloc | bare | (a) swings (high/low) | (b) UNCLASSIFIED (%) | (c) fereastră oarbă (bare / %) | tier |
|---|---|---|---|---|---|
| **bear** (2011-07→2013-09) | 52.404 | 14.220 (7.235 / 6.985) | 2 (0,0038%) | **16 bare / 0,0305%** | ≤1% ieftin |
| **bull** (2016-01→2018-04) | 52.851 | 14.468 (7.357 / 7.111) | 2 (0,0038%) | **9 bare / 0,0170%** | ≤1% ieftin |
| **correction** (2020-08→2021-09) | 25.237 | 6.744 (3.397 / 3.347) | 2 (0,0079%) | **10 bare / 0,0396%** | ≤1% ieftin |

**Total audit: 130.492 bare de descoperire.** Fereastra oarbă maximă pe orice bloc: **0,0396%** (correction) — de ~126× sub pragul de 5%, și sub pragul de 1%. Niciun bloc ascuns cu o cifră mare într-o medie mică: raportate individual, toate sunt neglijabile.

**Verdict pragului Statisticianului:** toate blocurile ≤ 1% → **D3 ratificat ca low-cost, fără condiții suplimentare de dezvăluire.**

---

## Constatări de verificat (raportate, nu presupuse)

1. **Numărul de blocuri: 3, nu 4.** Ratificarea (§13) vorbește de „8 structuri = 4 blocuri × 2 tipuri". Manifestul M15_v2 are `discovery_range` pentru DOAR 3 regime_segments (bear/bull/correction); al 4-lea (`bull_partial`, sliver 2022-10) **nu are `discovery_range`** și e sărit. Rezultă **6 UNCLASSIFIED (2 × 3 blocuri), nu 8.** Cifra „8/4-blocuri" din ratificare includea un bloc care nu e în setul de descoperire mascat de manifest (fie sliver-ul fără discovery_range, fie segmentul 2022-2026 exclus). Semnalez discrepanța; măsurătoarea reflectă manifestul, autoritatea de mascare.

2. **Bară-count: 130.492 vs 130.491 (CEO).** Diferență de 1 bară — convenție de graniță (am folosit `<= end_epoch` inclusiv la marginea unui segment) sau artefactul D10 (`wc` off-by-one, deja „proven benign"). Imaterial pentru verdict (ferestrele oarbe sunt ~0,03%, nu se schimbă cu 1 bară).

3. **UNCLASSIFIED = exact 2 per bloc** (primul high + primul low), confirmând că D3 funcționează cum e specificat (§43 al ratificării prezicea „exact 2 per bloc"). ✓

---

**Nu am atins holdout-ul, nu am rulat LM-001, nu am construit tranzacții. D3 = cost scăzut, LM-001 neblocat de fereastra oarbă. Continui la Pasul 3 (schelete MK-03/MK-04).**
