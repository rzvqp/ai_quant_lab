# STOP-FLOOR (D2) DIAGNOSTIC — is the body's concentration a floor artifact?

**Document ID:** STAT-STOPFLOOR-DIAG-v1.0 · **Autor:** Statistician (Research Lab) · **Data:** 2026-07-25
**Cerere:** CEO 2026-07-25 — cuantifică defectul D2 (stop-floor `mstrat.py:54` lărgește stopul prea mic în loc să-l excludă) și testează dacă concentrarea din `NET_CONCENTRATION_INVENTORY_v1.0.md` e artefact al podelei.
**Sferă:** măsurătoare. **Fără matched-null. Fără holdout. Fără metode noi. Fără modificarea parquet-ului.** Replică instrumentată fidelă a `mstrat.simulate` (linia 44-74), segment research (aceeași bază ca FAMILY_RESULTS). Script `code/stop_floor_diagnostic.py`; date `results/matched_null_validation/stop_floor_diagnostic.parquet`. **Nu concluzionez, nu propun remediere.**

**Bază VERIFICATĂ:** R-ul replicii == `MS.simulate` la **0.00e+00** pe toate cele 357; n match 357/357. Componente podea (CFG): `2×spread=0.2`, `5×tick=0.5`, `0.10×ATR` (variabil).

---

## 1. Frecvența lărgirii (tranzacții cu risk < min_exec, per ipoteză)
Distribuția `pct_widened` pe cele 357: p50 = **0%**, p75 = 0%, p90 = 2.4%, **max = 23.6%**.
- **293 / 357 ipoteze au ZERO tranzacții lărgite.** Nicio ipoteză nu are >50% lărgite.
- Lărgirea e concentrată în puține familii (medie pct_widened): **S6 4.5% · S17 3.9% · S14 1.3% · S1 0.6%**; toate celelalte (S2/S3/S5/S8/S9/S13/S16/S18/S19/S20) = **0%**. (S1 = 261 ipoteze structurale, dar doar 0.6% lărgire — stopurile structurale nu sunt la fel de mici ca scenariul-cel-mai-rău S6.)

## 2. Cât de departe de podea erau tranzacțiile lărgite (req_risk / min_exec)
1144 tranzacții lărgite în tot corpul. Raport `req/floor`: p10 = 0.09, **p50 = 0.542**, p90 = 0.879.
- req < 10% din podea (un ordin de mărime sub): **10.8%** din cele lărgite.
- req < 50% din podea: 45.9%. req în [50%, 100%): 54.1%.
- Deci majoritatea celor lărgite erau doar **modest** sub podea (~jumătate), nu ordine de mărime.

## 3. Corelația lărgire ↔ concentrare pe net (best/sumR)
- **Pearson(pct_widened, net1) = 0.023 · Spearman = 0.073** (n=357) — practic **zero**.
- Medie net1 | ipoteze cu 0% lărgite: **1.568** (n=293); cu >0% lărgite: **2.728** (n=64). (Grupul cu lărgire are net1 mediu mai mare, dar corelația continuă e ~0 — semnal confundat de familiile S6/S17, nu o relație monotonă.)

## 4. ÎNTREBAREA DECISIVĂ — cea mai bună tranzacție (care dă concentrarea) a fost lărgită?
- **Ipoteze a căror best-trade a fost lărgită: 13 / 357.**
- Dintre cele 250 cu net1 > 30%: best-trade lărgit la **13**.
- Dintre cele 184 cu net1 > 50%: best-trade lărgit la **12** (deci **172 din 184** au best-trade **NELĂRGIT**).
- Motiv mecanic (cifră, nu concluzie): lărgirea mărește riscul → R = pnl/risc **scade** → o tranzacție lărgită e mai puțin probabil să fie „cea mai bună". Tranzacțiile care produc concentrarea sunt sistematic **NELĂRGITE**.

## 5. Componenta activă a min_exec pentru tranzacțiile lărgite
Din 1144 lărgite: **tick (5×TICK=0.5) = 93.4%** (1068) · **ATR (0.10×ATR) = 6.6%** (76) · spread = 0%.
- Componenta ATR **NU** domină (6.6%). Podeaua celor lărgite e dominată de constanta **tick (0.5)**, nu de volatilitate — lărgirile apar în contexte cu ATR < 5 (0.10×ATR < 0.5), adică perioade liniștite unde stopul structural e foarte strâns.

## 6. Cazurile specifice (supraviețuitor + doi h20-long)
| ipoteză | n | pct_widened | best_widened | net1 |
|---|---|---|---|---|
| supraviețuitor h13-short time (`ce76669a3b2a`) | 550 | **0.0%** | **False** | 0.474 |
| h20-long time (`2341cf9911de`) | 534 | **0.0%** | **False** | 0.102 |
| h20-long rr2 (`00d840de0b48`) | 534 | **0.0%** | **False** | 0.039 |

Toate trei sunt **atr-stop (1.5×ATR)** → riscul cerut (1.5×ATR) e mult peste podea (0.10×ATR) → **niciodată lărgite**. Concentrarea supraviețuitorului (net1=0.474) provine dintr-o tranzacție de +15.88R pe risc **nelărgit** (cerut de strategie), nu din podea.

---

## 7. Rezumat de cifre (fără concluzie)
| măsură | valoare |
|---|---|
| Ipoteze cu 0% tranzacții lărgite | 293 / 357 |
| Max pct_widened (orice ipoteză) | 23.6% |
| Corelație pct_widened ↔ net1 | Pearson 0.023 / Spearman 0.073 |
| Ipoteze cu best-trade lărgit | 13 / 357 |
| Din cele 184 cu net1>50%, best-trade NELĂRGIT | 172 / 184 |
| Componentă podea dominantă (lărgite) | tick 93.4% (nu ATR) |
| Supraviețuitor / h20-long lărgite | 0% (atr-stop) |

Măsurătoarea răspunde la întrebarea decisivă (#4) în cifre: tranzacțiile care produc concentrarea nu sunt cele lărgite. **Nu concluzionez**; cifrele merg la certificare împreună cu inventarul de concentrare. D2 rămâne HIGH/DESCHIS (necuantificat ca remediere — doar măsurat aici). Holdout SEALED.

## 8. NOTĂ — direcția efectului D2 (adăugată la review-ul CEO 2026-07-25)
Podeaua **TRUNCHIAZĂ** coada, nu o creează. Dacă o strategie cere stop 0.05 și primește 0.50, o mișcare care ar fi dat 100R dă 10R. Deci D2, în măsura în care acționează, face corpul să arate **MAI PUȚIN concentrat decât e în realitate**, nu mai mult — riscul impus e mai MARE decât cel cerut, deci R e mai MIC, deci coada e comprimată. **Direcție sigură** pentru concluzia „concentrarea e reală" (subestimarea, nu supraestimarea, ar fi biasul). Consecință de guvernanță: D2 nu inflaționează niciun rezultat de concentrare/edge — deci prioritizarea lui NU e urgentă pentru integritatea rezultatelor actuale; contează doar pentru a debloca cele 1560 de ipoteze excluse din regimul validat (deblocare, nu corecție de bias). Măsurat: lărgirea atinge 0.6% din tranzacții pe familia S1, corelație ~0 cu concentrarea.
