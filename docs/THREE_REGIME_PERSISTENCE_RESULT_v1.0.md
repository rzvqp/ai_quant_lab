# THREE-REGIME PERSISTENCE — RESULT (M15_v2 discovery, 428 ATR)

**Document ID:** STAT-3REGIME-RESULT-v1.0 · **Autor:** Research Lab · **Data:** 2026-07-28
**Mandat:** CEO 1.1. Domeniu STRICT: cele **428 ATR**. 1544 STRUCTURAL-R-UNVALIDATED **nu rulate**; 16 atr-n<25 flag ineligibil. Motor canonic `reproduction_d2` (D2 închis), `mark_invalid`/`target_first` la default. **Măsurătoare descriptivă**, nu test de ipoteză: fără FDR, fără corecție de testare multiplă, fără selecție, fără screen, fără concluzie. Jumătatea sigilată neatinsă. Holdout SEALED.
**Artefacte:** `results/reproduction_d2/four_regime_{all,persisters}.parquet`, `four_regime_summary.json`, `four_regime_{bear,bull,correction}.parquet`; harness `code/run_four_regime.py`.

## Poarta + invariante (verificate)
- **Stability gate PASS:** cele 3 fișiere de context (H1/H4/D1_from_M15_v2) — READ A==READ B, ambele == manifest v2.4.2 ratificat (`524977d0`/`f8f23f6e`/`dad51764`), content_hash `3b309c79` OK.
- **Invariant de contabilitate a barelor PASS (assert în cod):** discovery M15_v2 = **bear 52.403 + bull 52.851 + correction 25.237 = 130.491** — exact cifrele CEO.
- **TREI regimuri, nu patru** (corectat; manifestul `changelog_v2_4` confirmă independent: 2022-2026 exclus ca SAME-WINDOW-RESAMPLED). Eroarea de numărătoare (CEO) — consemnată.
- Fiecare bloc rulat **izolat** (dir de date propriu, doar barele lui de discovery) → fără lookback cross-bloc/sealed; contextul HTF derivat e block-local prin construcție. Context non-null ~99.97%.

## Metrici (NET, nu brut)
Per regim, per ipoteză: exp, win, pf, dd, n, și concentrare pe **NET** — best/sumR (net1), top-3, top-5, wo1. **NU t1/t3/t5** (brut; subestimează fragilitatea).

## Agregat per regim (din cele 428)
| regim | profitabile | n median | win median | net1 median (profitabile) | din care o-singură-tranzacție (wo1≤0) |
|---|---|---|---|---|---|
| bear (−42.0%) | 39/428 | 769 | 0.316 | 0.568 | 11/39 |
| bull (+86.3%) | 9/428 | 748 | 0.322 | 0.644 | 2/9 |
| correction (−17.4%) | 26/428 | 382 | 0.321 | **1.721** | **17/26** |

„Profitabilă într-un regim" = n≥25 & sumR>0 & exp>0 & pf>1.00 în acel regim. Din cele 74 de rânduri profitabile (peste regimuri), **30 (41%) sunt o-singură-tranzacție** (wo1≤0). În corecție, mediana net1 a profitabilelor = 1.72 (cea mai bună tranzacție = 172% din net → fără ea, net-negativ).

## LEADERBOARD DE PERSISTENȚĂ (măsurătoarea centrală)
Câte din cele 428 sunt profitabile în:
| în N din 3 regimuri | 428 (toate) | 412 (eligibile) |
|---|---|---|
| **TOATE 3** | **3** | 3 |
| 2 | 7 | 7 |
| 1 | 51 | 51 |
| **0** | **367** | 351 |

**367/428 (86%) sunt profitabile în ZERO regimuri.** Doar **3** persistă în toate trei.

## Cei 3 persistenți — wo1 și best/sumR PE FIECARE REGIM (nu agregat)
| id | fam | ipoteză | regim | n | exp | pf | net1 | wo1 |
|---|---|---|---|---|---|---|---|---|
| 92481423c6b8 | S2 | pdh_pdl failed-breakout long, exit=time | bear | 281 | +0.096 | 1.14 | 0.655 | +0.033 |
| | | | bull | 337 | +0.093 | 1.13 | 0.644 | +0.033 |
| | | | correction | 153 | +0.017 | 1.03 | **2.797** | **−0.031** |
| a53441048c3c | S2 | (DUPLICAT al celui de sus — `lb` inert pentru `pdh_pdl`) | — | — | — | — | identic | identic |
| f5afb9813f83 | S17 | pw_high reject, exit=time | bear | 155 | +0.095 | 1.14 | 0.381 | +0.059 |
| | | | bull | 194 | +0.009 | 1.01 | **4.962** | **−0.037** |
| | | | correction | 125 | +0.003 | 1.004 | **23.869** | **−0.064** |

**Constatare factuală (cifre, fără concluzie), pe distincția CEO distribuit-vs-o-tranzacție:**
- Cei doi S2 sunt **duplicate** (diferă doar prin `lb`, inert pentru `pdh_pdl`) → **2 strategii distincte** persistă, nu 3: **un S2** (pdh_pdl) + **un S17** (pw_high). Ambele cu **exit=time**.
- **NICIUNA nu persistă distribuit.** Fiecare are ≥1 regim în care profitabilitatea e **integral o singură tranzacție** (wo1≤0): S2 în **correction** (net1 2.80, wo1 −0.031); S17 în **bull** (net1 4.96, wo1 −0.037) ȘI **correction** (net1 23.9, wo1 −0.064 — cea mai bună tranzacție = 2390% din net). Doar S17-bear (wo1 +0.059) și S2-bear/bull (wo1 +0.033) sunt „supraviețuiesc scoaterii celei mai bune", și acolo net1 e tot 0.38–0.66 (38–66% dintr-o tranzacție).

Nu concluzionez. Corecția de testare multiplă (dacă/care) o decide Statisticianul după ce vede structura.

---

## M5 — AL 4-LEA BLOCAJ (nu rulez; raportez, per instrucțiunea CEO)
M5 trebuie rulat SEPARAT. **Blocaj:** nu există context HTF **aliniat pe M5**. Intrările derivate din manifest sunt doar `H4/H1/D1_from_M15_v2` (`source_timeframe: M15_v2`), **block-local pe blocurile de discovery M15_v2** — nu pe cele M5. Verificat: ferestrele de discovery M5 NU-s acoperite de HTF-ul derivat din M15_v2:
| segment discovery M5 | bare derived-H4 în fereastră |
|---|---|
| correction 2021-07→2022-02 | 169 (M15_v2 correction-discovery se termină 2021-09) |
| bull 2022-11→2024-06 | 2325 (parțial; M15_v2 inherited-discovery începe 2022-12) |
| correction 2026-03→2026-04 | **0** (necuprins) |

Familiile cu context HTF (S7/S9/S11/S15/S20) ar rula pe context NaN/lipsă pe M5 → **corupt**. Un `H*_from_M5` (derivat din M5, block-local pe blocurile M5) **nu există** în manifest. **Rezoluție = Data Acquisition/Statistician:** generarea + validarea unui context HTF derivat din M5, aliniat pe blocurile de discovery M5 (aceeași regulă block-local ca la M15_v2). Până atunci, rularea M5 a familiilor cu context nu e leakage-safe. Rularea M15_v2 (de mai sus) e completă și neafectată.

**Sealed neatins. Holdout SEALED. WP-5′ neînceput. M15_v2 livrat; M5 blocat pe context HTF M5-aliniat.**
