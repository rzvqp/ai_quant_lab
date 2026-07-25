# F6.1 — RAPORT: CALIBRARE SUB STRUCTURĂ DE VOLATILITATE REALISTĂ
### Testul decisiv al nulului principal al laboratorului pentru `matched_null@v1`

**Document ID:** VE-F61-REPORT-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Autoritate:** CEO 2026-07-25 — F6.1, precondiție pentru promovarea `matched_null@v1`.
**Statut:** baterie rulată, **verdict PASS**. **Nimic promovat — registrul rămâne `PUBLISHED_NOT_EXECUTABLE`. Holdout neatins.**

---

## 0. ⚠️ Documente referite care NU au putut fi găsite

CEO a cerut: „Citește `CANDIDATE_STATUS_REGISTER_v1.0.md` înainte" și „Execută F6.1 conform specificației deja transmise".

**Am căutat exhaustiv** (toate fișierele din `ai_quant_lab` și worktree-urile `alpha-automation`/`research-main`, plus întregul istoric git pe toate branch-urile): **niciunul dintre cele două artefacte nu există** — nici `CANDIDATE_STATUS_REGISTER_v1.0.md`, nici o specificație F6.1 dedicată. Nu pot citi ce nu există și nu inventez conținut (contract §1.7, principiul fail-closed aplicat consecvent).

**Ce am executat:** testul decisiv este specificat neambiguu chiar în mesajul CEO — „serii în care sesiunea NY are volatilitate mai mare fără niciun efect real de nivel; metoda trebuie să nu respingă" — plus motivul (σ constantă normală ⇒ fără cozi grele, fără vol pe sesiune). Am executat exact acest test, care este sigur (100% sintetic, fără promovare, fără holdout). **Dacă documentele lipsă conțin cerințe suplimentare F6.1, acelea NU sunt acoperite** și le voi executa la primirea lor.

---

## 1. De ce F6 nu era suficient

Generatorul F6 folosea `rng.normal(0, σ_constant)`: randamente iid, σ identică pe toate sesiunile, fără cozi grele. Consecință (semnalată de CEO): **nulul principal al laboratorului — profilul de volatilitate pe sesiune (primitivul Volatility promovat) — nu putea fi testat** într-o lume unde toate sesiunile se comportă identic. Riscul real: un test care confundă o simplă diferență de volatilitate cu un efect de nivel ar respinge fals.

## 2. Designul F6.1

Generator extins, cu **medie zero peste tot** (niciun efect de nivel — doar structură de volatilitate):
- **Volatilitate diferențiată pe sesiune:** `session_vol={"ny": 2.5}` → σ_NY = 2.5 × σ_bază; restul sesiunilor la bază (mimează primitivul Volatility).
- **Cozi grele:** randamente Student-t (df=4), standardizate la varianță unitară, apoi scalate la σ-ul sesiunii.

Observație realistă confirmată empiric: vol NY mai mare **mută breach-urile prior-day-high în NY** (mișcările mari NY sparg PDH), producând suficiente evenimente NY (n≥25) — exact motivul pentru care datele reale au evenimente NY, absente sub σ constantă.

## 3. Testul decisiv — PASS

120 serii null per regim, celula țintă NY (up/ny), B=2000. Înregistrare: `F6_1_CALIBRATION_RECORD.json`.

| Regim (medie zero, doar structură de vol) | Țintă | FPR | CI95 | KS_p | Verdict |
|---|---|---|---|---|---|
| **DECISIV: NY vol 2.5×, fără efect de nivel** | up/ny | **0.050** | [0.023, 0.105] | 0.186 | ✅ **NU RESPINGE** |
| Cozi grele Student-t(4) | up/asia | 0.058 | [0.029, 0.116] | 0.820 | ✅ nu respinge |
| NY vol 2.5× + cozi grele t(4) | up/ny | 0.033 | [0.013, 0.083] | 0.759 | ✅ nu respinge |

În toate regimele, distribuția p rămâne **uniformă** și FPR ≈ **5%** (CI conține 0.05). **Metoda NU respinge când singura structură este volatilitatea** — exact ce cere nulul principal al laboratorului.

## 4. Puterea se păstrează sub volatilitate mare

Edge real (reversie) injectat în NY, peste vol 2.5×:

| δ ($) | Respingere |
|---|---|
| 0.0 | 0.05 (FPR) |
| 4.0 | 0.23 |
| 8.0 | 0.47 |
| 12.0 | 0.79 |

Monotonă crescătoare — metoda **detectează efecte reale** chiar și sub volatilitate mare. Puterea e mai mică decât în F6 (vol constantă) la același δ, ceea ce e **corect**: vol NY mai mare = pool mai lat = raport semnal/zgomot mai mic pentru un δ fix. Comportament științific corect, nu eșec.

## 5. De ce metoda este robustă (mecanismul)

`matched_null@v1` folosește **pooling per-sesiune** (`preserve=session`): evenimentele NY sunt comparate cu pool-ul NY (ambele vol mare), iar baseline-ul per-sesiune elimină media sesiunii. Reeșantionarea este **neparametrică** (nulul se construiește din pool-ul real, cu aceleași cozi grele). Prin urmare, o diferență de volatilitate între sesiuni nu poate produce o respingere falsă — comparația este mereu în interiorul aceleiași sesiuni. F6.1 **confirmă** această proprietate de design, care nu putuse fi testată sub σ constantă.

## 6. Verdict și promovare

**Verdict F6.1: PASS.** Combinat cu F6 (uniform sub null simplu, curbă de putere, reproducibilitate), `matched_null@v1` este acum calibrat și **sub structura de volatilitate realistă a laboratorului**.

**Registrul poate ieși din `PUBLISHED_NOT_EXECUTABLE` pentru `matched_null@v1`.** Schimbarea propusă (neaplicată, în așteptarea ordinului):
```
- test_methods["matched_null@v1"].calibration_status: "UNVALIDATED" -> "VALIDATED"
+ calibration_record: {F6: F6_CALIBRATION_RECORD.json, F6.1: F6_1_CALIBRATION_RECORD.json, verdict: PASS}
- status: "PUBLISHED_NOT_EXECUTABLE" -> "PUBLISHED_PARTIALLY_EXECUTABLE (1/15 VALIDATED)"
```
**Nu am aplicat-o autonom** — promovarea la VALIDATED rămâne ratificarea CEO. Restul de 14 metode rămân UNVALIDATED; DC-0004 tot nu devine executabil oficial (bonferroni/multiverse UNVALIDATED).

**Notă de guvernanță:** înainte de promovare recomand furnizarea documentelor lipsă (`CANDIDATE_STATUS_REGISTER_v1.0.md` + specificația F6.1), în caz că impun criterii suplimentare pe care nu le-am putut vedea.

---

## 7. Constrângeri respectate

| Cerință | Stare |
|---|---|
| Serii cu vol diferențiată pe sesiune + cozi grele | ✅ NY 2.5×, Student-t(4), medie zero |
| Test decisiv: NY vol mare fără efect de nivel → nu respinge | ✅ FPR=0.050, uniform |
| Holdout neatins | ✅ 100% sintetic; date reale doar pentru fidelitate (fereastra deschisă) |
| Nimic promovat; registru NOT_EXECUTABLE | ✅ neatins |
| Dacă pică → raportează, nu ajusta | N/A — a trecut din prima |

## 8. Fișiere

**Create:** `F6_1_CALIBRATION_RECORD.json`, `tests/test_f6_1_regime.py`, `F6_1_REPORT.md`.
**Modificate:** `ve/calibration/synthetic_matched_null.py` (+vol pe sesiune, +cozi grele, +`run_f61`).
**Neatins:** registrul, schema, DC-0004, motorul, cele 4 surse de date. **Teste: 410 passed.**

---

**Verdict F6.1: PASS.** `matched_null@v1` calibrează sub structura de volatilitate realistă și nu respinge fals când singura structură e volatilitatea. Promovarea la VALIDATED este gata și recomandată, dar **neaplicată** — aștept ordinul CEO și, ideal, documentele referite lipsă.

**Validation Engine se oprește și așteaptă decizia.**
