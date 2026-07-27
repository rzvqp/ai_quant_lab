# CANONICAL TRANSITION — pre-D2 baseline → D2-closed (FAMILY_RESULTS)

**Document ID:** STAT-CANON-TRANS-v1.0 · **Autor:** Research Lab · **Data:** 2026-07-26
**Autoritate:** Statistician + CEO 2026-07-25 — decizia de măsurare (excluderea INVALID) e corectă **independent** de soarta celor 69; promovează `reproduction_d2` la canonic.
**Acțiune:** `results/reproduction_d2/FAMILY_RESULTS.parquet` → `results/FAMILY_RESULTS.parquet` (canonic). **Baseline PĂSTRAT** (nu șters) la `results/FAMILY_RESULTS_pre_d2_baseline.parquet`.

## Proveniență
- Canonic nou = engine v2 + INVALID-EXECUTION (mark_invalid=True). Regimul **ATR provabil identic** (max|diff|=0.000e+00 pe toate 428 și pe cele 412 din FDR — `d2_verify.py`). Schimbări confinate la struct/ema. Mecanism §WP-4b (stop-first worst-case → excluderile erau părtinite pesimist).
- Reproducerea unei cifre de baseline: folosește `FAMILY_RESULTS_pre_d2_baseline.parquet` sau engine cu `cfg['mark_invalid']=False`.

## Mapare vechi → nou (cifre citate)
| cifră | vechi (baseline) | nou (canonic D2) |
|---|---|---|
| hist_prof | 357 | **426** |
| research_worthy | 130 | **138** |
| fragile | 133 | **152** |
| sumR>0 (net1 definit) | 357 | **426** |
| net1 single-best median | 0.538 | **0.477** |
| fragile=False & net1>30% | 117 | **129** |
| fragile=False & net1>50% | 51 | **57** |
| best>net „colaps" | 109 (30.5%) | **128 (30.0%)** |
| net1 median exit=time | 0.628 | 0.628 (neschimbat) |
| net1 median exit=rr2 | 0.387 | **0.318** |

## Impact pe fiecare document
- **`SCOPED_FDR_{PREREGISTRATION,RESULT}` (412 ATR, supraviețuitor S18, excluși 1560):** **NESCHIMBAT** — regim ATR provabil identic (0.000e+00). Supraviețuitorul, pragul BH, cei 412 rămân exact.
- **`SCOPED_FDR_RESULT §7.5` + certificarea S18:** **NESCHIMBAT** — S18 e atr-stop.
- **`BRACKET_69` + `MANDATE3_47`:** definite ca diff baseline→nou; rămân valabile ca înregistrare a tranziției (22 convention-artifact, 47 execution-failure-dominated).
- **`NET_CONCENTRATION_INVENTORY`:** calculat pe baseline (357). Echivalent nou în tabelul de mai sus (426; net1 median 0.538→0.477; 117→129 / 51→57; colaps 30.5%→30.0%). Documentul descrie baseline-ul (păstrat).
- **`OUTCOME_DISTRIBUTION`:** parțial schimbat (ATR neschimbat; struct schimbat). sumR>0 357→426; net1 median rr2 0.387→0.318; time 0.628 neschimbat.
- **`STOP_FLOOR_DIAGNOSTIC`:** a măsurat engine-ul PRE-excludere ca să testeze dacă concentrarea e artefact de podea; concluzia (nu e) stă. Tranzacțiile „lărgite" pe care le-a numărat sunt acum excluse în canonic.
- **`STRUCTURAL_R_UNVALIDATED` (1544):** eticheta **neschimbată** — D2 curăță statistica, nu potrivirea lui R.
- **Rapoarte Flow C (nu ale mele):** ancorele de re-mapare = hist_prof 357→426, colaps 30.5%→30.0% (stabil), t1/t3/t5 sunt pe BRUT (neschimbate ca definiție; valorile per-ipoteză structurală se mișcă). Re-derivarea cifrelor Flow C pe noul canonic e a diviziei Flow C; ancorele sunt aici.

## Guvernanță
- Baseline **păstrat**, nu șters. Documentele descriptive anterioare rămân valide ca instantanee-baseline; orice cifră e reproductibilă din baseline-ul păstrat sau `mark_invalid=False`.
- Promovarea e **independentă** de verdictul celor 69 (22 respinse, 47 în evaluare de Statistician post-Mandat 3). Holdout SEALED.
