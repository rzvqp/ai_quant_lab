# Addendum contract de măsurare — census motoare + tripwire + R11 (proveniență)

**Divizie:** Data Acquisition · **Data:** 2026-08-13 · continuă `MEASUREMENT_CONTRACT_R8_R9.md`.
NU am atins M15_v2 / M5 / manifestul; NU am extins segmentarea.

---

## 1. Census EXHAUSTIV — orice motor cu populație proprie

Am căutat toate fișierele care citesc CSV-urile OANDA sau derivă structură din goluri.

**Motoare de DECIZIE cu populație divergentă de manifest (a doua sursă de adevăr):**
| Motor | Populație | Verdict |
|---|---|---|
| `code/mtf.load_mtf` → `mstrat`/`s1` (Flow A) | citește **tot CSV-ul raw** (fără manifest la nivel de motor; split-ul research/val/holdout doar în `wave1_harness`) | ⚠️ **a doua sursă** — raportat (mandatul precedent). Statisticianul. |
| `relevance12m_perstrategy.py` (root, **SCRATCH**) | citește `OANDA_XAUUSD_M15.csv` direct, fereastra 12 luni întreagă, fără manifest | ⚠️ **a doua sursă** (artefact scratch/audit, folosește `ai_trader.strategy_health`) — nou găsit. Semnalat. |

**Flow B (edge_research) — toate pe `_common.load` (manifest-EXCLUSIV):**
- Candidații care apelează `derive_blocks` (cand0001/0002/0004/0005/0006/0009/0027/0037/0038, cand_level_breakout, exp_stop_vs_period, exp_weekly_break_session, stop_profiler) → acum primesc **blocurile din manifest** (fix-ul R9). COVERED.
- `e029_weekly_gap_fill(.py/_clean)`: populația vine din `_common.load` (manifest); gap-ul `>20h` e DOAR detecție de feature (week-opens), **nu o a doua sursă de populație**. COVERED. *(Corectez o clasificare inițială: nu e populație divergentă.)*
- `e005`/`e006`: populație via `_common.load`; folosesc session UTC-oră (divergența R8 deja raportată).

**Utilitare Flow A (nu motoare de decizie):** `code/gapfind.py`, `diag_mm.py`, `quality_and_resample.py`, `resample_ny.py` (generatorul HTF ratificat 17:00-NY), `run_cycle.py` (citește un CSV efemer din Temp) — unelte de data-prep/diagnoză/generare, nu produc cifre de candidat. Semnalate ca atare, prioritate mică.

**ai_trader/**: NU citește CSV-urile OANDA pentru populație de backtest (folosește feed-ul MT5 live) — nicio a doua sursă acolo.

**Concluzie T1:** exact **două** motoare de decizie cu populație proprie divergentă (Flow A `mtf`, și `relevance12m` scratch). Ambele merg la Statistician — nu le ating.

## 2. Tripwire-ul — acum CHIAR apelat (fail-closed)

**Găsit:** `assert_population_matches_manifest` avea **ZERO call-site** (doar în docstring) → nu era fail-closed, exact cum ai bănuit.

**Impus:** `_common.load` **apelează acum** tripwire-ul pe FIECARE load (base ȘI context-derived). Verifică fail-closed că populația livrată egalează segmentarea discovery din manifest ȘI tapetează frame-ul fără gol/suprapunere/scurgere (invariant de tiling — prinde o bară non-discovery scursă sau o derivă a mapării loader-ului). Testat: pasează pe M15_v2 real (3 blocuri) și pe H4_from_M15_v2 (1 bloc); **RAISE** pe un candidat divergent. Contractul îmbogățit cu verificarea de tiling.

Notă: Flow B e acum protejat și prin CONSTRUCȚIE (`derive_blocks` ia din manifest → nu POATE emite populație divergentă), plus tripwire-ul la load. Pentru motoarele pe care nu le pot atinge (Flow A `mtf`, `relevance12m`), tripwire-ul e disponibil pentru a fi apelat de owner când adoptă contractul.

## 3. R11 — PROVENIENȚĂ. Ce lipsește și cine furnizează

Red Team: Testul 17 pică peste tot — niciun motor nu etichetează configurația. Am codificat cele **13 dimensiuni** în `_contract.PROVENANCE_R11` (owner + status). *(Nu am găsit spec-ul R11 în niciun repo accesibil — taxonomia de mai jos e raționată; recomand Statisticianul/Red Team să confirme cele 13 canonice.)*

**Furnizate de Data Acquisition — 4/13 (blocul DATA-SIDE, complet):**
1. `dataset_identity` — file_path + sha256 ✓
2. `dataset_version` — manifest_version + contract_version ✓
3. `instrument_source_tf` — symbol(XAUUSD) + source(OANDA) + tf + bar_seconds ✓ *(adăugat acum)*
4. `population_segmentation` — official_blocks + data_split_id + cutoff + holdout flag ✓

**Lipsă — blocul CONVENȚIE (6/13), owner Statistician/VE:**
5. `trading_day_timezone` — delimitatorul EXISTĂ (R8 `trading_day_index`, îl furnizez eu); lipsește **eticheta** — motoarele trebuie să STAMPUIASCĂ ce convenție au folosit.
6. `cost_model` — spread/slippage/comision (CFG evaluator canonic).
7. `execution_convention` — entry@next-open, intrabar stop-before-target, no-overlap, stop podit.
8. `evaluator_identity` — care evaluator + versiune (acum `mstrat.simulate` canonic, Step-6).
9. `metric_definitions` — R10: net-vs-gross, censurare, câmpul best_trade_share.
10. `random_seed` — CFG['seed'] pentru null-pools/subsampling.

**Lipsă — blocul ENGINE-RUN (3/13), owner Research Lab (motor/harness):**
11. `strategy_hypothesis_id` — PARȚIAL (familiile calculează un hid canonic, dar nu-l emit într-un stamp de proveniență).
12. `code_commit` — commit-ul git / snapshot-ul `RATIFIED_CODE_DIR` care a produs rezultatul.
13. `run_env_timestamp` — timestamp rulare + versiuni pandas/numpy/python + platformă.

**Arhitectura corectă:** fiecare rezultat trebuie să poarte un stamp = **DATA-SIDE (4, gata acum via `dataset_identity`) + CONVENȚIE (6, Statistician/VE) + ENGINE-RUN (3, Research Lab)**. Azi există doar blocul data-side → Testul 17 pică. Eu am închis partea mea; celelalte 9 sunt ale Statisticianului/VE (6) și ale motorului (3).

---

## Ce am impus vs raportat (acest addendum)
- **Impus:** tripwire-ul `assert_population_matches_manifest` acum apelat fail-closed în `_common.load` (+ invariant de tiling); `dataset_identity` extins la blocul data-side complet (4/13 R11); schema `PROVENANCE_R11` codificată.
- **Raportat (nu ating):** Flow A `mtf` (whole-file) și `relevance12m` scratch = a doua sursă de populație → Statistician; cele 9 dimensiuni R11 non-data → Statistician/VE (6) + Research Lab (3).
