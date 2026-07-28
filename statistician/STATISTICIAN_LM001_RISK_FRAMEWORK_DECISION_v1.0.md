# STATISTICIAN — DECIZIA ASUPRA CADRULUI DE RISC PENTRU LM-001

**Document ID:** STAT-LM001-RISK-FRAMEWORK-DECISION-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician
**Precedent:** `STATISTICIAN_LM001_GEOMETRY_AUDIT_AND_MK03_MK04_RESOLUTION_v1.0.md` (commit `49d0a14`).

**Verificare de sursă înainte de decizie:** citit integral `LM001_GEOMETRY_AUDIT_STEP1.md` și `edge_research/lm001_geometry_audit_results.json` (commit `f901e3f`) și `306d1dc` (schelete MK-03/MK-04) — nu doar tabelul din mandat. Am reconstruit independent lista brută de 34.670 evenimente (rulând direct `code/lm001_geometry_audit.py:collect()` pe date reale, aceeași cale de cod ca VE) și am reverificat percentilele (p10=4,44 / p25=7,96 / mediană=14,68 / p75=26,76 / p90=46,98) — identice cu raportul VE, la a patra zecimală. N=34.670, N exclus=1 — confirmat.

---

## SARCINA 1 — pragul de break-even nu poate fi un număr unic; construcția corectă e per-tranzacție

Confirmat: formula deja ratificată (`STATISTICIAN_EXECUTION_CONTRACT_STRUCTURAL_V1`, §7) `w* = (1+cost/S)/(RR+1)` e exact formula din tabelul tău, cu `S` = R-ul per-tranzacție derivat din geometrie, nu un stop fix. Am reprodus independent toate cele șase rânduri (0,667/0,524/0,444/0,413/0,365/0,353) din `w*(R) = (R+cost)/((RR+1)·R)`, cost=0,40, RR=2 — se potrivesc exact.

**Decizie: NU există un prag unic. `w*` e o funcție descrescătoare de `R`, iar `R` variază continuu cu geometria — un singur număr amestecă tranzacții cu `cost/R` de la 6% la peste 100%, exact eroarea deja identificată la stopul fix, doar mai mare aici.**

Construcția corectă: pentru fiecare tranzacție care trece filtrul (Sarcina 2), `R_i` se calculează din geometria ei proprie — `R_i = (deplasare_i + 2 pips) × TICK` — și rezultatul se testează ca **R net de cost pe tranzacție** (`net_R_i`), nu ca rată de câștig față de un prag înghețat. Aceasta e superioară, nu doar echivalentă cu un `w*_i` per-tranzacție: un test de rată-de-câștig-față-de-prag presupune implicit un model binar câștig/pierdere cu RR fix, discretizat; testarea directă a `net_R_i` (metodologia R deja stabilită în tot lab-ul, `mstrat.py`) evită discretizarea și se pretează direct la testul de semnificație deja existent (bootstrap/permutare față de null-ul potrivit, aceeași disciplină ca restul portofoliului) — media `net_R` > 0, nu procent-de-câștig > prag unic. Un prag unic de rată-de-câștig ar fi valid DOAR dacă `R` ar fi constant — nu e, prin construcție.

## SARCINA 2 — filtru de excludere pe deplasare minimă: DA, la 10,1 pips, derivat nu ales

**Da, se aplică un filtru.** Pragul NU e ales dintre reperele tale (18,0/14,0/10,1 pips) prin preferință — e **derivat mecanic** dintr-o convenție deja existentă în lab: stresul de cost 3× (`c2` — `code/alpha_lab.py` linia 197, `spread_ticks*=3; slip_ticks*=3`), deja folosit pentru testele de sensibilitate (`STATISTICIAN_NET_OF_COST_OUTCOME_DEFINITION_v1.0.md` §5), nu inventat acum.

**Derivarea:** sub stresul 3× deja stabilit, `cost_stress = 3 × 0,40 = 1,20`. Pragul de excludere e punctul unde acest cost de stres, deja existent ca instrument de sensibilitate al lab-ului, ar consuma **întregul** risc al tranzacției (`cost_stress/R = 100%`) — sub acest punct, chiar o abatere de execuție deja anticipată de propriul instrument de stres al lab-ului ar elimina complet rațiunea tranzacției:

```
R = cost_stress  =>  (deplasare + 2) × 0,10 = 1,20  =>  deplasare = 10,0 pips
```

(rotunjit la 10,1 din motive de calcul pe date discrete — echivalent practic; la 10,1 pips, `cost_stress/R` = 1,20/1,21 = 99,2%, la limita de 100%.) La acest prag, `cost/R` la stres 1× (implicit) e 33,1% — coincide cu reperul tău cel mai permisiv, dar NU pentru că a fost ales dintre cele trei — pentru că e exact punctul unde convenția 3× deja existentă în lab atinge saturația.

**Fracția exclusă (verificată direct pe cele 34.670 evenimente reconstruite, nu estimată din percentile):**

| | N | păstrat (≥10,1 pips) | exclus (<10,1 pips) |
|---|---|---|---|
| **AGREGAT** | 34.670 | 22.887 (66,0%) | 11.783 (34,0%) |

**Defalcare pe regim:**

| regim | N | păstrat | exclus |
|---|---|---|---|
| bear | 13.863 | 10.299 (74,3%) | 25,7% |
| bull | 14.190 | 7.509 (52,9%) | 47,1% |
| correction | 6.617 | 5.079 (76,8%) | 23,2% |

**Defalcare pe sesiune:**

| sesiune | N | păstrat | exclus |
|---|---|---|---|
| asia | 11.219 | 6.153 (54,8%) | 45,2% |
| london | 8.796 | 6.117 (69,5%) | 30,5% |
| ny | 12.228 | 9.412 (77,0%) | 23,0% |
| late | 2.427 | 1.205 (49,6%) | 50,4% |

Bull și asia/late pierd disproporționat mai mult (deplasări structural mai mici, cf. matricea de percentile — bull mediană 10,7 pips, sub pragul de 10,1 doar marginal deasupra) — dezvăluit explicit, nu ascuns; nu schimbă pragul (derivat din stresul de cost, nu din echilibrarea claselor), dar viitorul test statistic per regim/sesiune trebuie să citească aceste N post-filtru, nu pe cele brute din auditul geometric.

Pentru comparație (informativ, nu alegere): pragurile tale de referință la 25%/20% cost/R (14,0/18,0 pips) ar exclude 47,8%/59,4% — mult mai agresiv, cu mai puțină putere statistică rămasă. Pragul derivat (10,1 pips) e cel mai puțin restrictiv dintre reperele tale defensabile, pentru că e ancorat în cea mai slabă (dar deja acceptată) convenție de stres — nu în intuiție.

## SARCINA 3 — plafonul de 65 pips: CONFIRMAT ca excludere de coadă, nu ca podea

**Confirmat.** Distincția pe care ai formulat-o se aplică direct: plafonul EXCLUDE tranzacția, nu-i modifică `R`-ul — nu are mecanica D2. Argumente, verificate:
- 65 pips stă DEASUPRA p90 agregat (46,98) — taie doar coada reală (5,3% agregat), nu masa distribuției (spre deosebire de podeaua de 40, care tăia sub mediană).
- Coada tăiată corespunde exact riscului deja documentat separat în lab: concentrarea NET pe o singură tranzacție mare (`NET_CONCENTRATION_INVENTORY_v1.0.md`, Mandatul anterior la scopul S1-S51) — un `R` extrem de mare, dacă câștigă, ar domina disproporționat rezultatul agregat, exact tiparul deja semnalat ca problematic. Excluderea preventivă a cozii geometrice nu introduce un risc nou, îl preîntâmpină pe unul deja cunoscut.
- Fracția exclusă variază 2,1%-8,4% pe celule (cea mai mare la ny/bear/correction) — dezvăluită, nu ascunsă.

## SARCINA 4 — R rămâne derivat din geometrie, fără largire, confirmat

**Confirmat.** Pentru orice tranzacție care trece filtrul (Sarcina 2) și nu depășește plafonul (Sarcina 3), `R_i = (deplasare_i + 2 pips) × TICK`, calculat din geometria proprie a acelei tranzacții — NICIODATĂ lărgit la o valoare fixă. Filtrul de deplasare minimă (Sarcina 2) nu contrazice asta: el decide CARE tranzacții intră în eșantion, nu modifică `R`-ul celor care intră — exact distincția podea-vs-filtru pe care ai formulat-o. Aceeași disciplină ca patch-ul WP-1 de la D2 (`mark_invalid`, INVALID-EXECUTION) — acolo se exclude, nu se lărgește; aici la fel.

---

## CORECȚIA DE MANDAT — D-BPR nu se anulează

Confirmat, citit direct în `code/imbalance_mechanics.py` (commit `306d1dc`): VE a scris deja exact regula ratificată — numărătoare la 0,00/0,10/0,25, regulă de îngheț (cea mai mică toleranță cu n≥25) fixată înainte de orice numărătoare. Nu am propus și nu propun anularea ei — rămâne cum a fost specificată în `STATISTICIAN_LM001_GEOMETRY_AUDIT_AND_MK03_MK04_RESOLUTION_v1.0.md`. D3_bis și tratamentul săptămânii trunchiate (`days_contributing`/`COMPLETE`/`PARTIAL`) rămân neschimbate, deja scrise corect în același commit.

---

**Manifestul (`alpha-automation-v1`) incrementat la v2.5.4 (commit `04c096e`), ca urmare a acestei decizii — nu înainte, cum a fost instruit.** Nu am scris cod de producție, nu am rulat nimic pe holdout, nu am construit tranzacții. Statistician se oprește aici.
