# Census EXHAUSTIV al populației — v2. Găsit tiparul M-4 nedescoperit: `_setb.py`

**Divizie:** Data Acquisition · **Data:** 2026-08-13 · extinde census-ul din `MEASUREMENT_CONTRACT_ADDENDUM_engines_tripwire_R11.md`.
Căutare exhaustivă a TUTUROR `read_csv`/loader-elor/definițiilor de populație (nu doar cele din M-4). NU am atins manifestul / M15_v2 / M5.

---

## ★ FINDING NOU (semnificativ): `edge_research/_setb.py` — a doua sursă de adevăr asupra populației Set B

`load_setb(tf, ...)` livrează **"Set B"** = fereastra de confirmare/unseen `[SETB_START, SETB_END]`, cu bounds **HARDCODATE în cod**:
- `SETB_START_EPOCH = 1761210900` = **2025-10-23T09:15Z**
- `SETB_END_EPOCH = 1783922400` = **2026-07-13T06:00Z**
- `SETB_EXPECTED_BARS = {M15:16831, H1:4209, H4:1100, D1:183}` (counts frozen)
- `SETB_SPLIT_ID = "setB_confirmation_...v1"`, `SETB_LOADER_VERSION` frozen 2026-07-25.

**Manifestul definește ACEEAȘI fereastră:** ambele epoch-uri (`1761210900`, `1783922400`) și ISO-urile (`2025-10-23T09`, `2026-07-13T06`) sunt prezente în `config/split_manifest.json`. Deci fereastra Set B e definită în **DOUĂ locuri**: manifest + constante hardcodate în `_setb.py`.

**Riscul = exact tiparul M-4:** `_setb.py` **NU citește manifestul** — hardcodează. Cele două coincid ASTĂZI, dar nimic nu le ține sincronizate; dacă Statisticianul schimbă fereastra Set B în manifest, `_setb.py` rămâne pe valorile vechi → **două populații divergente pentru același Set B, tăcut**. E aceeași clasă de defect ca M-4 (o a doua sursă de adevăr asupra populației), nedescoperită până acum.

**Folosit LIVE:** `e015_setb_dependence.py`, `e_setb_confirm.py` (nu e cod mort).

**Atenuant existent:** `_setb.py` are enforcement fail-closed puternic — count exact (`SETB_EXPECTED_BARS`) + bare de bracketing la fiecare graniță → o schimbare de date sau o graniță mutată **trip-uie** (nu poate servi o fereastră trunchiată/deplasată). DAR verifică față de **propriile constante hardcodate**, NU față de manifest — deci un manifest schimbat NU e prins.

**PROPUNERE (Statisticianul decide; e cod ratificat, nu-l rescriu unilateral):**
- `_setb.py` să **sursseze** `SETB_START/END` (și ideal `SETB_EXPECTED_BARS`) din manifest — sursă unică, la fel ca fix-ul R9 pentru discovery; SAU
- minim: să **aserteze** constantele hardcodate față de definiția Set B din manifest la load (fail-closed via contractul `assert_population_matches_manifest` sau echivalent) — astfel un drift manifest↔cod devine zgomotos.
- Pot implementa oricare variantă la aprobare.

## Finding minor: `code/run_prod.py`

Batch de producție experimental: `files=glob.glob(DATADIR+"\\*.csv")` peste un **DATADIR Temp efemer** (`...344b31d3.../scratchpad/phaseb/alpha/data` — cale moartă), whole-file, multi-simbol, `touch_holdout=True`. Scratch/experiment mort (ca `run_cycle.py`), nu motor de discovery live. Semnalat ca scratch — nu e o sursă de populație activă asupra XAUUSD.

---

## Census complet (toate sursele de populație, clasificate)

| Sursă | Tip | Populație | Verdict |
|---|---|---|---|
| `edge_research/_common.load` | loader canonic | manifest-EXCLUSIV (acum **4 blocuri**) | ✅ sub contract R9 |
| **`edge_research/_setb.load_setb`** | loader Set B | **bounds HARDCODATE** (dubl. cu manifest) | ⚠️ **a 2-a sursă (Set B) — tiparul M-4** |
| `code/mtf.load_mtf` / `s1` / `mstrat` | Flow A | tot fișierul raw, fără manifest | ⚠️ raportat (mandat anterior) |
| `relevance12m_perstrategy.py` | scratch (root) | fereastra 12 luni, fără manifest | ⚠️ raportat (scratch) |
| `code/run_prod.py` | scratch producție | glob Temp efemer, whole-file, touch_holdout | ⚠️ scratch/mort (nou) |
| `resample_ny` / `quality_and_resample` / `generate_htf_context` / `gapfind` / `diag_mm` / `run_cycle` | data-prep/diag | citesc raw pt. generare/diagnoză | ℹ️ unelte, nu motoare de decizie |
| `ai_trader/*` | runtime live | feed MT5, NU citește CSV pt. populație de backtest | ✅ fără a 2-a sursă |

**Concluzie:** census-ul e acum exhaustiv. Singura sursă de populație **activă, ratificată, cu autoritate în afara manifestului** e **`_setb.py`** (Set B) — tiparul M-4 nedescoperit pe care l-ai anticipat. Restul sunt fie sub contract (`_common.load`), fie scratch/data-prep. Toate merg la Statistician; nu ating cod ratificat fără aprobare.

## Stare operațională
Fereastra neagră: rezolvată (ambele task-uri pe `pythonw.exe`; news `LastResult=0x0`, log crește la 300s). Desigilare: NU (Opțiunea B, CEO); manifest neatins; propunerea de split păstrată ca document.
