# OUTCOME-DISTRIBUTION MEASUREMENT — winrate × concentration over all 1972

**Document ID:** STAT-OUTCOME-DIST-v1.0 · **Autor:** Statistician (Research Lab) · **Data:** 2026-07-25
**Cerere:** CEO 2026-07-25 — măsoară distribuția comună winrate × concentrare (net1) pe **toți cei 1972**, defalcat pe tip de stop și regulă de ieșire; numără câți ar trece un screen alternativ și suprapunerea cu research_worthy.
**Sferă:** măsurătoare descriptivă. **Fără selecție de candidați. Fără screen nou propus. Fără matched-null. Fără holdout. Fără modificarea parquet-ului.** Motor observat determinist, segment research. Script `code/outcome_distribution.py`; date `results/matched_null_validation/outcome_distribution.parquet`. **Nu concluzionez, nu compar care e mai bun.**

`net1 = best/sumR` e definit doar unde `sumR > 0`. Din 1972: **357 au sumR>0** (net-profitabile pe research); celelalte 1615 (82%) sunt net-negative in-sample. research_worthy actual = 130.

---

## 1. Distribuția comună win × net1 (pe cele 357 cu sumR>0)
- **Pearson(win, net1) = −0.101 · Spearman = −0.080** (n=357) — corelație **slabă negativă**, nu o structură puternică.
- Mediană net1 pe benzi de winrate: **win<.30 → 0.771** · .30-.45 → 0.421 · .45-.60 → 0.433 · **≥.60 → 0.576**. Relație **ne-monotonă** (U-shaped): winrate foarte mic ȘI winrate mare au concentrare mai mare decât mijlocul.
- Cross-tab (rânduri=win, coloane=net1):

| win \ net1 | <.30 | .30-.50 | .50-1.0 | >1.0 |
|---|---|---|---|---|
| <.30 | 0 | 2 | 3 | 3 |
| .30-.45 | 63 | 32 | 16 | 62 |
| .45-.60 | 42 | 19 | 10 | 43 |
| ≥.60 | 2 | 13 | 46 | 1 |

Winrate mare (≥.60) NU merge cu concentrare mică: se aglomerează în net1 0.50-1.0 (46), nu în net1<.30 (doar 2). „win mare ⇒ net1 mic" **nu se susține** în aceste cifre.

## 2. Defalcare pe TIP DE STOP (win, net1)
| stop | n_hyp | net-profit rate | win median | net1 median (sumR>0) |
|---|---|---|---|---|
| **atr** | 428 | 61/428 = 14.3% | 0.316 | 0.467 (n=61) |
| **struct** | 1532 | 296/1532 = 19.3% | 0.376 | 0.550 (n=296) |
| **ema** | 12 | 0/12 = 0% | 0.248 | — (niciuna profitabilă) |

Stopurile **structurale** au winrate median mai mare (0.376 vs 0.316), rată net-profitabilă mai mare (19.3% vs 14.3%) și net1 median ușor mai mare (0.55 vs 0.47). Diferență **sistematică pe tip de stop**, nu doar coincidență de familie (S1 e integral structural, dar S9/S11/S13/S15/S20 au și atr și struct). `ema` = 0 profitabile.

## 3. Defalcare pe REGULĂ DE IEȘIRE (ipoteza CEO: time → concentrare mare + winrate mic; rr2 → invers)
| exit | n | win median | net1 median (sumR>0) | dd median |
|---|---|---|---|---|
| **time** | 484 | 0.353 | **0.628** | 46.6 |
| **rr2** | 580 | 0.371 | **0.387** | 60.6 |
| rr3 | 440 | 0.343 | 0.352 | 50.5 |
| opp_liq | 396 | 0.426 | 0.748 | 39.5 |
| **trailing** | 72 | 0.274 | — (0 profitabile) | **622.8** |

- **Axa concentrare CONFIRMĂ ipoteza:** `time` net1 median **0.628** > `rr2` net1 median **0.387** — regula de ieșire mută sistematic concentrarea (coincide cu §7.5 S18: aceleași intrări, best +15.88R pe time vs +1.97R pe rr2).
- **Axa winrate — slabă/neconfirmată:** time win 0.353 ≈ rr2 win 0.371 (time doar puțin mai mic, nu dramatic). opp_liq are cel mai mare winrate (0.426) DAR și net1 mare (0.748) → nu e un tradeoff curat concentrare↔winrate pe ieșiri.
- `trailing`: dd median **622.8R**, zero profitabile — catastrofal ca distribuție.

## 4. Screen alternativ (win≥0.50 & net1<0.30 & wo1>0) — NUMĂR + suprapunere cu research_worthy
- **Trec: 29** ipoteze. (Cifră descriptivă, NU un screen propus.)
- Suprapunere cu cele **130 research_worthy: 27**. alt-only (trec alt, NU rw): **2**. rw-only (rw, NU alt): **103**.
- Trecătorii alt pe familie: **S1=20**, S5=6, S19=2, S20=1. Pe tip de stop: **struct=27**, atr=2.
- Profil research_worthy actual: median win 0.442, median net1 0.275, median dd 12.9.

Observații factuale (fără concluzie):
- **27 din 29** trecători ai screen-ului alternativ sunt **deja research_worthy** → nu sunt „ascunși" de screen-ul actual; cele mai multe trec deja.
- **27 din 29** au **stop structural** → integral **în afara subsetului de 412** pe care s-a rulat FDR-ul validat. Adică ipotezele care se potrivesc cel mai bine criteriilor winrate+distribuție cad în regimul pe care matched-null-ul NU-l poate testa încă (structural = D2, exclus).
- Cele 103 research_worthy care NU trec alt au fie winrate <0.50, fie net1≥0.30, fie wo1≤0 — screen-ul actual (n≥25, exp>0, PF≥1.02, maxDD≤25R) nu conține criteriu de winrate sau distribuție, deci admite și profile concentrate.

---

## 5. Rezumat de cifre (fără concluzie, fără selecție)
| măsură | valoare |
|---|---|
| sumR>0 (net1 definit) din 1972 | 357 (82% sunt net-negative in-sample) |
| Corelație win↔net1 | Pearson −0.101 / Spearman −0.080 (slabă, ne-monotonă) |
| net1 median: time vs rr2 | 0.628 vs 0.387 (ieșirea mută concentrarea) |
| win median: struct vs atr | 0.376 vs 0.316 |
| trailing dd median / profitabile | 622.8R / 0 |
| alt-screen passers | 29 (27 deja research_worthy; 27 stop-structural) |

Măsurătoarea arată, în cifre, că **profilul de rezultat variază sistematic cu regula de ieșire (concentrare) și cu tipul de stop (winrate/profitabilitate)**. Nu concluzionez asupra implicației pentru metoda de căutare a laboratorului — o las la certificare/CEO. Nu am selectat candidați, nu am propus un screen nou, nu am modificat parquet-ul. Holdout SEALED.
