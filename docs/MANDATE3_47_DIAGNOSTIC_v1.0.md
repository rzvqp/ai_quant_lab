# MANDATE 3 — pointed diagnostic of the 47 EXCLUSION-DEPENDENT hypotheses

**Document ID:** STAT-MANDATE3-v1.0 · **Autor:** Research Lab · **Data:** 2026-07-26
**Cerere:** Statisticianul — inferența lui (marcată explicit ca inferență): excluderea celor 47 vine mai probabil din **eșecuri de execuție degenerate** (gap peste podea, risc≤0 după floor) decât din **coin-flip genuin** pe bara ambiguă. Două măsurători ca s-o confirme sau infirme.
**Sferă:** măsurătoare. Artefacte existente din re-rularea D2 + replică instrumentată pe cele 47 (research). **Fără re-rularea campaniei. Fără holdout.** `results/reproduction_d2/mandate3_47.{parquet,summary.json}`.

---

## 1. Subtipul tranzacțiilor EXCLUSE (7371 excluse pe cele 47)
INVALID-EXECUTION acoperă trei cazuri. Descompunere, per tranzacție exclusă, pe bara de intrare:

| subtip | count | % | interpretare |
|---|---|---|---|
| **gap_stop** (stopul floor-uit atins pe bara de intrare, ținta NEatinsă) | **5816** | **78.9%** | eșec de execuție (stop minuscul floor-uit lovit imediat) |
| target_only (ținta atinsă pe bara de intrare, stopul neatins) | 949 | 12.9% | câștig same-bar (nu eșec, dar exclus fiindcă lărgit-same-bar) |
| **ambiguous** (ATÂT stop CÂT ȘI țintă atinse pe bara de intrare) | **606** | **8.2%** | coin-flip genuin (rezolvat stop-first prin convenție) |
| neg_risk (risc≤0 după floor) | 0 | 0.0% | nu apare (floor-ul garantează >0) |

**Subtipul dominant per ipoteză = `gap_stop` pentru TOATE cele 47.** Coin-flip-ul ambiguu = doar 8.2% agregat.

## 2. Fracția de excludere vs mediana corpului
| | excl_frac = excluse / n_baseline |
|---|---|
| corp (1972): median | **0.0000** |
| corp: p90 / max | 0.0521 / 0.3775 |
| **cele 47: median** | **0.0556** |
| cele 47: min / max | 0.0042 / 0.3043 |

Ipoteza mediană din corp are **zero** excluderi. Cele 47 au median 5.6% (≈ p90 al corpului), până la 30.4% (S8, S3). Toate 47 sunt peste mediana corpului (care e 0). *(Nota: „>5× mediană" e trivial adevărat fiindcă mediana=0; formularea relevantă e că cele 47 stau în coada superioară a corpului.)*

## 3. Ce spun cifrele (fără a concluziona — verdictul e al Statisticianului)
- **Inferența Statisticianului e susținută de descompunerea pe subtip:** 78.9% din tranzacțiile excluse ale celor 47 sunt **gap_stop (eșecuri de execuție)**, doar 8.2% coin-flip ambiguu. Prin acest criteriu, cele 47 **NU** sunt aproape de cele 22 (tie-break) — sunt dominate de eșecuri de execuție genuine.
- Profitabilitatea lor vine din eliminarea unei fracții **ne-triviale** a eșantionului (median 5.6%, până la 30%), aflată în coada superioară a corpului — nu o corecție marginală.
- Rezumat factual: statusul celor 47 nu se inversează pe tie-break (§bracket: worst==best==False), iar tranzacțiile eliminate care le fac profitabile sunt majoritar **stop-uri floor-uite lovite pe bara de intrare** (gap_stop), nu bare ambigue. Dacă „profitabilitatea rămasă după eliminarea eșecurilor de execuție" e edge real = **decizie de Statistician**. Research Lab a livrat cifrele.

Baseline + reproduction_d2 neatinse (în acest mandat). Holdout SEALED.
