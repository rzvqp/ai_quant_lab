# DUPLICATE AUDIT — full 1972 grammar (+ 428 ATR)

**Document ID:** STAT-DUP-AUDIT-v1.0 · **Autor:** Research Lab · **Data:** 2026-07-28
**Cerere:** CEO. Furnizez cifrele; Statisticianul scrie specificația formală de dedublare.
**Criteriu:** două ID-uri sunt duplicate dacă produc **serii de tranzacții identice pe aceeași fereastră**.
**Metodă (fără re-rularea campaniei):** amprentă din metricile `FAMILY_RESULTS` existente (fereastra research) → clustere; fiecare cluster **confirmat prin hash pe seria R reconstituită** (motor canonic, doar ID-urile din clustere). Artefact: `results/reproduction_d2/duplicate_audit_summary.json`; cod `code/duplicate_audit.py`. Măsurătoare; holdout neatins.

## Cifre
| univers | ID-uri | ID-uri duplicate (în cluster >1) | clustere | strategii DISTINCTE | redundanță |
|---|---|---|---|---|---|
| **corp întreg 1972** | 1972 | **1040** | **508** | **1440** | **532 (27.0%)** |
| **428 ATR** | 428 | 136 | 68 | **360** | 68 (15.9%) |

Deci corpul „1972 de ipoteze" conține de fapt **1440 de strategii distincte**; 532 (27%) sunt copii redundante. Din cele 428 ATR, **360 distincte**, 68 redundante. (Sanity: perechea S2 `92481423c6b8`/`a53441048c3c` — confirmată în același cluster.)

## Ce parametri sunt inerți, și pentru ce valori ale altora
| param inert | # clustere | familii |
|---|---|---|
| **liq_lb** | 372 | S1 |
| **lb** | 72 | S2 (48), S3 (24) |
| mode | 48 | S5 |
| exit | 20 | S1 (12), S12 (8) |
| target | 8 | S12 |

- **Lookback-ul (`liq_lb`/`lb`) domină: 444/508 clustere (87%).** E inert **⟺ referința de lichiditate ≠ `swing`** (adică `pdh_pdl` sau `session`). Cauza e structurală în cod: setup-providerul folosește lookback-ul **doar** dacă `liq_ref=='swing'` (`lb = int(h['liq_lb']) if h['liq_ref']=='swing' else 20`). Când referința nu e swing, cele două valori de lookback (20/50) colapsează la setup-uri identice. Toate clusterele-eșantion confirmă (`liq_ref='pdh_pdl'`, `liq_lb` variază fără efect).
- **`exit` (rr2↔rr3)** colapsează când ținta RR nu e atinsă în fereastră (ambele ies pe time-out la aceeași bară) sau când un exit mai apropiat (opp_liq) declanșează primul — config-specific, adesea compus cu lookback-inert (clusterele S1 x4 = 2 lb × 2 exit, ambele inerte).
- `mode` (S5), `target` (S12): colapsuri mai mici, config-specifice.

## Inerția e sistematică sau accidentală?
**SISTEMATICĂ**, nu accidentală. **87% din clustere** provin dintr-un singur tipar structural: lookback-ul e activat printr-un condițional în grammar (`only if liq_ref=='swing'`), deci pentru celelalte valori ale referinței lookback-ul e mort și cele două valori ale lui produc aceeași strategie. Restul (`exit`/`mode`/`target`) sunt colapsuri config-specifice tot deterministe (parametru irelevant sub o anumită combinație), nu coincidențe. Duplicatele sunt un artefact al produsului cartezian al grammarului peste parametri conditional-inerți.

Nu concluzionez dincolo de cifre/tipar. Specificația formală de dedublare o scrie Statisticianul.

---

**CE NU FAC (consemnat):** M5 nu se rulează; contextul HTF aliniat pe M5 NU se generează (anulat de CTO) — blocajul raportat rămâne consemnat, **nerezolvat prin decizie, nu prin omisiune**. M5 rămâne în repository pentru DC-0008 și variabila R (blocantul G6) — nu-l dezafectez. Etichetele de arhivare ale celor 428 (367 ZERO_ALPHA_BASE_RATE / 58 REGIME_PERSISTENCE_FAILURE / 3 EXTREME_CONCENTRATION_FRAGILITY_wo1) le aplic **când le publică Statisticianul**, nu le inventez acum (mapează pe leaderboard: 0-regimuri / 1-2-regimuri=51+7 / cei 3). Fără WP-5′, fără linii noi. Holdout SEALED. **După acest audit: STANDBY.**
