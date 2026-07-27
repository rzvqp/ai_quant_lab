# FOUR-REGIME DISCOVERY-HALF RUN — STATUS (PREPARED, NOT STARTED)

**Document ID:** STAT-4REGIME-STATUS-v1.0 · **Autor:** Research Lab · **Data:** 2026-07-26
**Mandat:** CEO 2026-07-25 — re-rulează campania pe patru regimuri macro, DESCRIPTIV, pe jumătatea de descoperire. **Poartă dură: nu se începe** până Data Acquisition confirmă loader-ul + enforcement holdout pe M15 v2, ȘI Statisticianul livrează împărțirea pre-înregistrată.

## Reconstrucția mandatului (ce voi rula când poarta se deschide)
- **Domeniu STRICT: cele 428 de ipoteze ATR.** Cele **1544 STRUCTURAL-R-UNVALIDATED NU se rulează** (R nu e statistica potrivită acolo; date fine nu rezolvă — Statistician). Cei **16 atr-n<25 rămân ineligibili**. `428 + 16 + 1544 = 1972`.
- **Motor:** canonic `reproduction_d2` (D2 închis); `mark_invalid` și `target_first` la **default**.
- **Date:** M15 v2 în directoarele canonice; **doar jumătatea de descoperire**, conform împărțirii pre-înregistrate de Statistician (50/50 stratificată pe segmente de regim, carantină 1000 bare M15 la fiecare graniță internă). **Jumătatea sigilată nu se atinge. Holdout SEALED.**
- **Raportare per regim macro, separat, nu agregat:**

  | regim | tip | mișcare |
  |---|---|---|
  | 2011-2015 | bear | −42% |
  | 2015-2020 | bull | +86% |
  | 2020-2022 | corecție | −17% |
  | 2022-2026 | bull | +223% |

  Pentru fiecare din cele 428, pe fiecare regim: **expectancy, winrate, profit factor, drawdown, nr. tranzacții**, și **concentrarea pe NET** (best/sumR, top-3, top-5, wo1). **NU t1/t3/t5** (brut, subestimează sistematic fragilitatea).
- **Măsurătoarea centrală:** din cele 428, câte sunt profitabile în **TOATE cele 4** regimuri / 3 / 2 / 1 / 0. (Fereastra veche era exclusiv bull; o ipoteză care ține în toate patru e altceva decât una de bull market.)
- **Interdicții:** fără FDR, fără corecție de testare multiplă (măsurătoare descriptivă, nu test de ipoteză — Statisticianul decide corecția după ce vede structura); fără selecție de candidați; fără screen; fără concluzie.

## Starea porții — NEÎNDEPLINITĂ (verificat 2026-07-26)
| precondiție | stare | dovadă |
|---|---|---|
| **P1** Loader oficial citește M15 v2 acoperind 2011-2026 + enforcement holdout confirmat | ❌ | loader-ul citește acum M15 care acoperă doar **2022-12 → 2026-07** (ani 2022-2026); niciun set M5/v2 în `data/market/` |
| **P2** Împărțirea pre-înregistrată a Statisticianului (mask descoperire + granițe regim + carantină 1000) | ❌ | niciun `docs/M5_SPLIT_PREREGISTRATION.json` prezent |

## Pregătire (fără a începe)
- Harness gata: `code/four_regime_measure.py` — **guard-uit să ABORTEZE** până ambele preconditii sunt îndeplinite (testat: abortează curat cu P1=False, P2=False). Encodează exact spec-ul de metrici (net-concentrare, NU t1/t3/t5) + numărătoarea 4/3/2/1/0. Granițele de regim și masca de descoperire sunt **parametri de intrare** din spec-ul Statisticianului (contract: `docs/M5_SPLIT_PREREGISTRATION.json`), NU hardcodate/ghicite.

## Ce aștept
1. **Data Acquisition:** confirmarea că loader-ul oficial citește M15 v2 (2011-2026) în directoarele canonice ȘI că enforcement-ul de holdout funcționează pe ele.
2. **Statistician:** `M5_SPLIT_PREREGISTRATION.json` — 50/50 stratificat pe segmente de regim, carantină 1000 bare M15, mască de descoperire + granițe de regim exacte + criteriul de profitabilitate/min-n per regim.

Până atunci: **NU încep. Jumătatea sigilată neatinsă. Holdout SEALED. WP-5′ neînceput. STANDBY.**
