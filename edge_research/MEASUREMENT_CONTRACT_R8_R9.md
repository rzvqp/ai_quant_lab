# Contract canonic de măsurare — R8 (ziua de tranzacționare) + R9 (populația). Pasul 3.

**Divizie:** Data Acquisition · **Data:** 2026-08-13 · Contract v1.0-DRAFT (NOT RATIFIED; D-1/D-2 CEO-approved).
**NU am atins** M15_v2 / M5 / manifestul. **NU am extins** segmentarea. Verificat **în cod, per motor**.

---

## Implementat: `edge_research/_contract.py` (sursă unică, mypy --strict clean)

- **R8** `trading_day_index(time)` — ordinal de zi ancorat la **17:00 America/New_York, IANA, DST-aware**. Verificat **byte-identic** cu ancora D1 din `code/resample_ny.py` și cu `_screen.day_index_ny17`. Plus `trading_day_start_utc` (instantul de rollover) și constante.
- **R9** `dataset_identity(tf)` (id+versiune+hash+segmente, verificabil de orice motor), `official_blocks(df,tf)` (segmentele discovery din manifest ca index-ranges — SINGURA populație legitimă), `assert_population_matches_manifest(...)` (tripwire fail-closed pentru M-4).

---

## R9 — POPULAȚIA. Ce am găsit divergent, per motor

### Flow B (candidații `edge_research/` via `_common.load` → `_screen.derive_blocks`) — **M-4 CONFIRMAT LIVE**
Verificat pe M15_v2 real (130.491 bari discovery, manifest v2.7.62):
- `_common.load` livrează populația discovery din manifest = **3 segmente**: `(0,52403),(52403,105254),(105254,130491)`.
- `_screen.derive_blocks` re-derivă blocuri din goluri >72h = **15 blocuri**. Cele 12 granițe în plus sunt **închideri de sărbători** (Crăciun / Anul Nou / Paște–Good Friday, ~3 zile), **NU găuri de date**.
- **Populații diferite → cifre incomparabile** cu mstrat (exact M-4).

**IMPUS:**
- `_common.load` stampează `official_blocks` + `dataset_identity` în `meta` ȘI `df.attrs` (+ `official_blocks_n` pentru guard pe df nemodificat).
- `_screen.derive_blocks` întoarce acum **blocurile din manifest EXCLUSIV** când df-ul vine din `_common.load` (M-4 rezolvat). Golul >72h rămâne DOAR ca fallback pentru un df ne-manifest (frame ad-hoc/sintetic), cu warning zgomotos „NOT manifest-verified". Testat: df manifest → 3 blocuri + warning de override; df simplu → 15 + warning de fallback.
- Sigur: golurile de sărbători ~3 zile sunt tratate ca weekend-urile deja ținute în bloc (ferestrele pe număr de bare le tolerează) — nu introduce comportament nou de fereastră-peste-gol.
- **Consecință de semnalat:** ferestrarea candidaților trece 15→3 blocuri. Rezultatele lor se schimbă (spre populația CORECTĂ/comparabilă). **Statisticianul trebuie să re-ruleze candidații în cunoștință de cauză** — populația veche era incomparabilă.

### Flow A (`code/` — `mtf.load_mtf` / `s1.load_s1` / `mstrat.load`) — divergent, RAPORTAT (nerescris)
`mtf.load_mtf` (linia 34) citește **întreg CSV-ul raw** `OANDA_XAUUSD_M15.csv`, fără nicio segmentare din manifest la nivel de motor. Restrângerea la research/val/holdout se face abia în harness (`wave1_harness.load_segments`, split-ratios din manifest), NU în motor. Deci populația de bază a motorului = **tot fișierul**, divergentă de segmentarea discovery din manifest.
- **NU am rescris** — a răsturna asta schimbă FIECARE cifră istorică a Flow A și e decizie de ratificat (Statistician/CEO). Am furnizat contractul (`dataset_identity`/`official_blocks`) pentru adopție.

---

## R8 — ZIUA DE TRANZACȚIONARE. Cine o implementează diferit

| Calcul | Motor | Delimitare | Verdict |
|---|---|---|---|
| D1 / PDH / PDL / pd_open / pd_close | `s1.py`, `mstrat.py` (via `resample_ny` D1) | **17:00 NY DST** | ✅ consistent |
| day_index (levels) | `_screen.day_index_ny17` | **17:00 NY DST** | ✅ identic cu contractul |
| Ancora D1/H4 | `code/resample_ny.py` | **17:00 NY DST** | ✅ canonic |
| **session (asia/london/ny/late)** | `_common.load` L165 **ȘI** `mtf.load_mtf` L38 | **oră UTC** (`<8/<13/<21`) | ⚠️ **divergent** de 17:00-NY |

**IMPUS:** contractul `trading_day_index` = sursă unică 17:00-NY pentru ziua precedentă/PDH/PDL/daily range (partea daily e deja consistentă în ambele motoare).

**RAPORTAT (nerescris):** tagging-ul de **session** folosește bucket-uri de **oră UTC** în AMBELE flow-uri — **deliberat și documentat**, iar candidații ratificați depind de aceste granițe (e005 „London close 13:00 UTC", e006 „asia hour<8 UTC", e008 „ny/late hour>=13 UTC"). A-l răsturna la 17:00-NY schimbă rezultate ratificate → **decizie de ratificat (Statistician/CEO)**, nu o răstorn unilateral. Contractul oferă `trading_day_index`/`trading_day_start_utc` pentru adopție dacă se decide.

---

## Ce NU am făcut / de semnalat
- NU am atins M15_v2 / M5 / manifestul; NU am extins segmentarea.
- Test stale pre-existent (fără legătură cu R8/R9): `tests/test_loader_holdout_boundary.py::test_h1_from_m15_v2_awaits_path_reconciliation` aserta că fișierul H1_from_M15_v2 NU există, dar a fost reconciliat la calea canonică (mandatul H1, manifest v2.7.48). 28/28 restul trec. Semnalat Statisticianului — nu-l ating.

## Rezumat impus vs raportat
- **Impus:** contractul `_contract.py`; R9 la `_common.load` (official_blocks+identity) + `_screen.derive_blocks` (manifest EXCLUSIV, M-4 rezolvat); R8 delimitator canonic unic.
- **Raportat (necesită acțiunea owner-ului):** Flow A citește tot fișierul (populație); session UTC-oră în ambele flow-uri (R8) — ambele schimbă cifre ratificate, deci le ratifică Statisticianul/CEO.
