# Mandat 5.7 — Pasul 2: bateria WP-5' (block_bootstrap contra nulului STRUCTURAL)

**Rol:** Validation Engine (executiv). Am rulat bateria pre-înregistrată; raportez rezultatul contra
predicției pre-înregistrate. NU ajustez generatorul, NU emit verdicte dincolo de banda de acceptare.

Cod: `code/wp5_null_generator.py` (Pas 1, `96d31ad`) + `code/wp5_battery.py` (harness).
Rezultate brute: `edge_research/wp5_battery_results.json`.

## Configurație
- `n_events = 21.048` (populația LM-001: filtrată [10.1, 65] pips, ferestre de margine `c+H≥n` excluse — Q2)
- `H = 20` bare (orizontul real de dependență finită), `B = 2000` bootstrap, `N_SERIES = 200` realizări de null
- Șocuri = randamente REALE per-bară M15 (close-to-close), bootstrap-reeșantionate per segment (Q5)
- Null = sume pe orizont `[c, c+H]` pe POZIȚIILE EMPIRICE EXACTE (Q1 forma tare), stratificat pe sesiune (Q3)

## Rezultat: FPR@0.05 (banda nominală ≤ 0.06)

| L | regim | FPR agregat | asia | london | ny | late | verdict |
|---|---|---|---|---|---|---|---|
| 10 | L < H | 0.0450 | 0.015 | 0.030 | 0.075 | 0.055 | NOMINAL |
| 20 | L ≥ H | **0.0400** | 0.015 | 0.030 | 0.060 | 0.045 | NOMINAL |
| 28 | L ≥ H | **0.0400** | 0.015 | 0.025 | 0.055 | 0.045 | NOMINAL |
| 40 | L ≥ H | **0.0400** | 0.015 | 0.030 | 0.050 | 0.045 | NOMINAL |

## Predicția pre-înregistrată — CONFIRMATĂ

> „La L ≥ H, blocul conține integral dependența finită → FPR ar trebui să coboare stabil în banda nominală."

- La **L ≥ 28**: FPR@0.05 = **0.0400**, stabil, în banda nominală (per-sesiune toate ≤ 0.060). **CONFIRMAT.**
- La L = 20 (= H): identic 0.0400 nominal.
- Sub H (L = 10): 0.0450 — tot nominal (ny = 0.075 e singura celulă peste 0.06, dar doar per-sesiune la L<H;
  agregatul e nominal).

**Conform criteriului pre-înregistrat de Statistician/CEO:** predicția se confirmă → `block_bootstrap@v1`
devine validat **SPECIFIC pentru mecanismul de suprapunere (LM-001)**, la scara n = 21.048, la L ≥ H.

### Domeniu STRICT al concluziei (nu extrapolez)
- Aceasta NU anulează `INVALIDATED_FOR_THIS_SCALE` din bateria S8 AR(1): acolo metoda era anti-conservatoare
  la φ = 0.6 (memorie INFINITĂ, decadere geometrică). Cele două regimuri sunt diferite: nulul WP-5' are
  memorie FINITĂ (autocorelație → 0 dincolo de lag ~H), pe care un bloc L ≥ H o conține integral.
- Validarea e scopată la: nulul de suprapunere finită-memorie al LM-001, n = 21.048, L ≥ H = 20, FPR@0.05.
- Observație onestă (nu extrapolez din ea): și L = 10 (< H) iese nominal aici — deci pentru ACEST mecanism
  cu memorie finită, sensibilitatea la L e mică; contrastul dur față de S8 vine din MECANISM (finit vs
  infinit), nu din L per se. Nu trag concluzii dincolo de banda măsurată.
- NU am mutat registrul (`capabilities.json`). Statusul scopat (ex. `VALIDATED_FOR_OVERLAP_MECHANISM` cu
  suita S-WP5') e decizia Statisticianului; eu raportez doar că banda de acceptare pre-înregistrată e atinsă.

## Q4 — „69% orizont partajat" ca CONSECINȚĂ DERIVATĂ (nu invariant impus)

Generatorul condiționează pe POZIȚIILE EMPIRICE EXACTE (Q1) → NU impune nicio spațiere; orice structură de
suprapunere reală e reprodusă exact. Verificarea derivată (post-generare):

- **BUG de raportare în printout/JSON:** `shared_horizon = 0.809` din log e MISCOMPUTAT (a poolat indicii
  LOCALI de segment și i-a sortat între segmente). **FPR-urile NU sunt afectate** — ele folosesc pozițiile
  per-segment corect în `generate_null_series`.
- **Valoare CORECTATĂ per-segment:** `mean_spacing = 8.52` bare → `shared_horizon = (H−spacing)/H = 0.574`;
  spacing median = 5.0 bare; 89.7% dintre gap-urile consecutive < H (ferestre suprapuse).
- **Divergență față de 0.69 referit în manifest:** 0.574 vs 0.69 — atribuibilă definiției metricii de
  spațiere + populației (filtrată [10.1,65]+edge-excluse vs populația la care s-a citat 7.64). Fiindcă
  generatorul folosește pozițiile EXACTE, orice ar fi adevărata suprapunere e reprodusă exact — deci NU e un
  defect de generator, ci o diferență de METRICĂ. **Raportez faptul; nu reconciliez definiția metricii
  (rol de Statistician).**

## Tensiune de guvernanță (semnalată explicit)
- Mandatul cerea „sintetic în memorie, zero prețuri reale". Q5 cere ca șocurile să fie randamente EMPIRICE
  M15 (close-to-close) reeșantionate bootstrap. Reconciliere: se citește DISTRIBUȚIA DE RANDAMENTE ca
  INTRARE DE CALIBRARE (nu P&L, nu backtest, nu direcție/outcome LM-001) — aceeași permisiune ca auditurile
  de densitate/geometrie. Seriile-null în sine sunt sintetice în memorie. Semnalez tensiunea, nu o rezolv
  unilateral.
- Aceasta DEBLOCHEAZĂ LM-001 (per mandat), sub domeniul strict de mai sus.
