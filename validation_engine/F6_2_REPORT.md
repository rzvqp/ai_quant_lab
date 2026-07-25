# F6.2 — RAPORT: CALIBRARE SUB DRIFT REAL (acoperire, nu poartă)
### `matched_null@v1` sub driftul dominant al XAUUSD

**Document ID:** VE-F62-REPORT-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Statut:** finalizat. **Verdict: NICIUN EȘEC CLAR DE DRIFT.** Reîncadrat de CEO din poartă în acoperire.

---

## 0. Reîncadrare (corecție CEO)

CEO a corectat premisa: FPR=0.975 sub drift_long **NU** era rezultatul bateriei adversariale finale Flow C, ci un **defect al PRIMEI versiuni a unui motor DIFERIT** (bootstrap pe risc absolut, nepotrivire de scală ATR), reparat imediat (post-fix: 0.00). Controlul de drift a fost construit special de ei pentru strategii long-biased. Deci F6.2 nu mai e o poartă de promovare — rămâne valabil ca **acoperire** pe implementarea mea (diferită: celule de eveniment, nu backtesturi).

## 1. Driftul măsurat (nu ales)

Din `data/market/OANDA_XAUUSD_M15.csv` (fereastra deschisă): 0.03472 $/bară M15 × 4 = **0.13889 $/bară H1** (aurul +131% pe fereastra de cercetare — driftul e regimul dominant, nu marginal).

## 2. Rezultat — niciun eșec clar

Regimuri: drift ascendent, descendent, schimbare de regim la mijloc; combinate cu vol NY 2.5× + cozi grele t(4); celule up/ny și up/asia; ~1000 serii inițial + confirmare la n mare.

| Caz (up/ny) | n | FPR | CI95 | |
|---|---|---|---|---|
| fără drift (control) | 400 | 0.062 | [0.043, 0.091] | include 0.05 |
| drift descendent (control) | 400 | 0.062 | [0.043, 0.091] | include 0.05 |
| **drift ascendent** | 600 | 0.067 | [0.049, 0.090] | include 0.05 |
| **schimbare de regim** | 600 | 0.050 | [0.035, 0.070] | include 0.05 |

up/asia: 0.024–0.041 în toate regimurile (OK).

**Semnalul inițial** (n=170: up/ny up-drift 0.088, regime-shift 0.094, CI excludeau marginal 0.05) **nu s-a replicat la n=400–600** — a fost zgomot de eșantion mic. Toate CI-urile la n mare includ 0.05.

## 3. Interpretare

`matched_null@v1` **nu respinge fals sub drift real**. Există o înclinare ușoară (~0.06 vs 0.05) în celula up/ny, prezentă **și fără drift** (n~37 evenimente) — o proprietate de eșantion mic al celulei, nu specifică driftului, în CI de 0.05. Consistent cu design-ul: baseline-ul per-sesiune (excess) elimină drift-beta **structural** — analogul fix-ului Flow C (raport risk/ATR, nu absolut).

## 4. Fișiere

`F6_2_CALIBRATION_RECORD.json`, `F6_2_REPORT.md`, `tests/test_f6_2_drift.py`; `ve/calibration/synthetic_matched_null.py` (+drift, +regime_shift). Holdout neatins. Nimic promovat.

---

**Verdict F6.2: niciun eșec clar de drift.** Vezi `MATCHED_NULL_BATTERY_GAP_ANALYSIS.md` pentru scenariile Flow C încă netestate (G-AR1 reversie, G-FPR praguri, G-PLACEBO) recomandate înainte de promovare.
