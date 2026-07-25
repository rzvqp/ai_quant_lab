# NET vs GROSS PROFIT-CONCENTRATION INVENTORY — full hist_prof body (357)

**Document ID:** STAT-NET-CONC-INV-v1.0 · **Autor:** Statistician (Research Lab) · **Data:** 2026-07-25
**Cerere:** CEO 2026-07-25 — recalculează concentrarea pe **NET** pentru întreg corpul și compară cu metricile existente (t1/t3/t5, care sunt pe **BRUT**).
**Sferă:** măsurătoare/inventar. **Fără matched-null. Fără holdout. Fără modificarea parquet-ului.** Motor observat determinist (`MS.setups`+`MS.simulate`, segment research), aceeași bază ca FAMILY_RESULTS. Script: `code/net_concentration_inventory.py`; date: `results/matched_null_validation/net_concentration_inventory.parquet`. **Nu concluzionez și nu propun o metrică nouă.**

---

## 1. Baza — VERIFICATĂ (comparația e validă)
Reconstituit pe research pentru toate cele 357 hist_prof: **n match 357/357**, `max|exp − sumR/n| = 5e-16` (zgomot float). Rațiile pe brut reconstituite **coincid exact** cu `t1/t3/t5` din parquet: `max|g1−t1| = max|g3−t3| = max|g5−t5| = 0.0000`. Deci FAMILY_RESULTS calculează t1/t3/t5 pe **profitul BRUT** (Σ R pozitivi), iar rațiile mele pe NET (Σ tot R) sunt direct comparabile.

Definiții: **BRUT** `g_k = topk_R / Σ(R>0)` (= t_k). **NET** `net_k = topk_R / sumR`, unde `sumR` = profitul net (Σ tot R). Întotdeauna `net_k ≥ g_k` fiindcă `sumR ≤ Σ(R>0)`.

## 2. Distribuția — cota unei singure tranzacții (cea mai bună) din profit

| cuantilă | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|
| **BRUT (t1)** | 0.081 | 0.411 | 0.546 | 0.656 | 0.828 |
| **NET (best/sumR)** | **0.538** | 1.295 | 2.374 | 3.780 | 83.67 |
| **raport NET/BRUT** | **6.0×** | 21.9× | 49.8× | 97.1× | 2212× |

Ipoteza **mediană** hist_prof ia **54% din profitul NET dintr-o singură tranzacție** — față de **8%** cât raportează t1 (brut). Raportul median net/brut = **6×**.

## 3. Distribuția — top-3 și top-5

| | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|
| **NET top3/sumR** | 1.025 | 3.004 | 5.411 | 9.318 | 212.8 |
| **NET top5/sumR** | **1.462** | 3.704 | 7.764 | 13.354 | 317.8 |
| **BRUT t5** | 0.255 | 0.845 | 1.000 | 1.000 | 1.000 |

Mediana top-5 pe NET = **146% din profitul net** (adică fără top-5, ipoteza mediană e net-negativă), vs **25.5%** cât raportează t5 pe brut.

## 4. Numărătorile cerute — fragile=False cu concentrare NET mare pe o singură tranzacție

357 hist_prof · **224 fragile=False** · 133 fragile=True.

| prag (best/sumR NET) | toate hist_prof | din care **fragile=False** |
|---|---|---|
| **> 30%** | 250 / 357 | **117** |
| **> 50%** | 184 / 357 | **51** |

Context suplimentar (cifre, fără concluzie):
- `best/sumR > 100%` (cea mai bună depășește netul → fără ea, restul e net-negativ): **109 / 357 = 30.5%**.
- `top5/sumR > 50%`: **311 / 357**; `> 80%`: **290 / 357**.

## 5. Observație factuală privind Flow C (fără concluzie)
Flow C (RI-REPORT-0002) raportează „30.5% colapsează fără cea mai bună tranzacție" și „top-5 = 41% din contribuție". Cifra de colaps **coincide numeric** cu `best/sumR > 100%` măsurat aici = **109/357 = 30.5%** (aceeași definiție: fără cea mai bună, netul devine negativ). Cifra „top-5 = 41%" e de ordinul medianei pe **BRUT** (t5 p50 = 25.5%, media mai sus); pe **NET**, mediana top-5 e **146%**. Nu concluzionez asupra cărei baze folosește fiecare cifră Flow C — o consemnez pentru reconciliere.

## 6. Poziția supraviețuitorului scoped-FDR (referință)
`ce76669a3b2a`: **net1 = 0.474** (47.4% din net dintr-o tranzacție) vs **t1 = 0.035** (3.5% brut); net5 = 1.926 (top-5 = 193% din net); t5 = 0.141; **fragile = False**. Este una dintre cele 117 (fragile=False & net1>30%), sub pragul de 50%.

Comparativ, `2341cf9911de` (h20-long time, neselectat de test): 9.65/94.54 = **10.2% din net** — de ~4.6× mai puțin concentrat decât supraviețuitorul.

---

**Livrat ca inventar pentru certificare (contract v1.1 §5). Nu concluzionez, nu propun metrică nouă, nu am modificat parquet-ul. Holdout SEALED.**
