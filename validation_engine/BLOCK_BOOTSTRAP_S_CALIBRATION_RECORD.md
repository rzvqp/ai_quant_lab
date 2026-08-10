# block_bootstrap@v1 — RAPORT DE CALIBRARE S1/S3/S4/S8

**Document ID:** VE-BB-CALIB-v1.0 · **Data:** 2026-07-25 · **Autor:** Validation Engine
**Verdict: NU TRECE.** Metoda e **anti-conservatoare (liberală)** în regimul ei de utilizare (n mic + autocorelație) — direcția NESIGURĂ. `block_bootstrap@v1` rămâne `UNVALIDATED`. Implementarea NU a fost ajustată.

**Implementare testată:** `ve/methods/block_bootstrap.py` (moving-block, centrare la 0, coadă dreaptă, `p_hat=(k+1)/(B+1)`). Harness: `ve/calibration/synthetic_block_bootstrap.py`.
**Fidelitate:** reproduce cele două controale din `MONTE_CARLO_AUDIT.md`: null(medie~0)→p≈0.57, edge curat(.25)→p≈5e-5 (audit: 0.42 / 4e-4; diferența = altă tragere/B). Implementarea e fidelă codului vechi; anti-conservatorismul e o proprietate reală, nu un defect de implementare.

## Ce acoperă cele două controale existente vs. bateria completă
Cele 2 controale = **un punct de null + un punct de putere**. Nu pot estima o RATĂ de FPR (au nevoie de multe trageri), nu dau o curbă de putere, și nu ating S8 (autocorelația). Exact golul semnalat de `PROJECT_AUDIT.md` l.23: *"needs full battery"*.

## S1 — contract + reproducibilitate — **PASS**
Determinist pe seed (identic la re-rulare); `p_hat=(k+1)/(B+1)`, `p>0` imposibil; ieșiri complete (n, observed, k, B, p_hat, p_mc_ci95, mc_resolution, seed).

## S4 — putere — **PASS**
Curbă monotonă, rejection@0.05 (n=250, L=15, n_series=300): edge 0.0→0.09, 0.1→0.54, 0.2→0.94, 0.3→1.00.

## S3 — calibrare sub null (iid) — **MARGINAL**
FPR@0.05 (n_series=1000): n=250 L=1 → **0.054** [0.042,0.070] (nominal); n=250 L=5 → **0.062** [0.049,0.079] (la limită); n=1000 L=5 → 0.044; n=2000 L=5 → 0.048 (nominale). Referință t-test pe aceleași serii: 0.051 / 0.042 (harness sănătos). Ușor liberal la n mic + bloc lung; se curăță cu n.

## S8 — null AUTOCORELAT (motivul metodei) — **FAIL la n realist**
FPR@0.05 (n_series=1000, L potrivit blocului):

| φ | n | L | FPR@0.05 | CI95 | |
|---|---|---|---|---|---|
| 0.4 | **250** | 8 | **0.077** | [0.062, 0.095] | ANTI-CONSERVATOR |
| 0.4 | 1000 | 10 | 0.049 | [0.037, 0.064] | nominal |
| 0.4 | 2000 | 12 | 0.055 | [0.042, 0.071] | nominal |
| 0.6 | **250** | 8 | **0.093** | [0.077, 0.113] | ANTI-CONSERVATOR |
| 0.6 | 1000 | 10 | 0.061 | [0.048, 0.078] | ~limită |
| 0.6 | 2000 | 12 | 0.066 | [0.052, 0.083] | ușor anti-conservator |

Pe date IID cu bloc lung, iid (L=1) pe date autocorelate = 0.175 (foarte inflat) — blocul e mai bun decât iid, dar tot NU nominal la n mic.

## Interpretare
Anti-conservatorismul e o proprietate de **eșantion finit** a moving-block bootstrap (subestimează varianța pe termen lung când numărul de blocuri n/L e mic și autocorelația e prezentă). Dispare la n≥~1000. **DAR** seriile-R de tranzacții reale sunt exact în regimul mic (S6: n=244; S1 rep: ~200). În acel regim, un p chiar sub 0.05 corespunde unei rate reale de eroare ~0.08–0.09 — adică **supra-declară semnificația**, direcția periculoasă.

Un "domeniu n≥1000" ar valida metoda exact acolo unde NU e folosită. Nu e o validare utilă, și e liberală acolo unde e folosită.

## Verdict
`block_bootstrap@v1` **NU trece** S3/S8 în regimul de utilizare (n≈250 + autocorelație): anti-conservator, direcția nesigură. **Rămâne `UNVALIDATED`.** Nu am ajustat implementarea. O metodă calibrată ar cere o construcție diferită (bootstrap studentizat, bloc cu taper/Politis-White, sau selecție de lungime de bloc) — dar aceea e o metodă NOUĂ / o re-specificație, decizia Statisticianului, nu o reparație pe care o fac eu ca să treacă.
