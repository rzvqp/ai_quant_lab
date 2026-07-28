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

## UPDATE v1.1 (2026-07-28) — poarta parțial deschisă; guard redirectat; UN blocaj rămas (P3)

**Corecția de guard (cerută de CEO):** spec-ul NU e `M5_SPLIT_PREREGISTRATION.json` (nu a existat niciodată). E **`config/split_manifest.json` v2.2.0** (commit `4e1f550`, alpha-automation-v1). Guard-ul redirectat acolo (env `AQ_SPLIT_MANIFEST`), verifică: manifest prezent + **content_hash** + M15_v2 **status==VALIDATED** + **data_file_sha256** vs fișierul fizic; eșuează devreme și explicit dacă lipsește.

**Reconcilierea hărții de regim (nu e contradicție blocantă):** cele „4 regimuri" din mandat = segmentele autoritare ale manifestului. Manifestul „superseded" DOAR convenția de graniță (pro-forma Jan-1 → monthly-close real 15%), nu numărul de regimuri. Procentele se potrivesc **exact**:
| mandat (year-level, superseded) | manifest M15_v2 (monthly-close, autoritar) |
|---|---|
| 2011-2015 bear −42% | 2011-08→2015-12 bear **−42.0%** · discovery 2011-07-26→2013-09-27 |
| 2015-2020 bull +86% | 2015-12→2020-07 bull **+86.3%** · discovery 2016-01-11→2018-04-06 |
| 2020-2022 corecție −17% | 2020-07→2022-10 correction **−17.4%** · discovery 2020-08-11→2021-09-05 |
| 2022-2026 bull +223% | 2022-12→2026-07 bull **+223.3%** (moștenit din split-ul M15, cutoff 2025-10-23) |
Al 5-lea „segment" = sliver 2022-10→12 (182 bare, **TOO_SHORT_FULLY_SEALED**). Voi folosi granițele de discovery autoritare din manifest.

**Starea porții (verificat 2026-07-28):**
| precondiție | stare | dovadă |
|---|---|---|
| **P1** M15_v2 acoperă 2011-2026 | ✅ | fișier 355.696 bare, 2011-07 → 2026-07 |
| **P2** Manifest VALIDATED + content_hash + data_sha256 | ✅ | M15_v2 SHA `57f4ed95…` = manifest; status VALIDATED; content_hash OK |
| **P3** Context HTF (H4/H1/D1) acoperă 2011.. | ❌ | H4/H1/D1 acoperă doar **2023-01 → 2026-07** |

**BLOCAJ (P3) — context HTF lipsă pentru 2011-2022.** `mstrat` încarcă contextul H4/H1/D1 din **fișiere separate** (nu resample din M15). Aceste fișiere acoperă doar 2023-2026. Pentru barele M15_v2 din regimurile **bear/bull/correction (2011-2022)**, coloanele de context (h4_trend_up, h1_trend_up, features D1) ar fi **NaN** → familiile dependente de context (S7, S9, S11, S15, S20) ar produce **zero tranzacții** acolo → **matricea de persistență ar fi CORUPTĂ** (o strategie HTF ar apărea „neprofitabilă în 3 regimuri" fiindcă n-a avut context, nu fiindcă a eșuat). Manifestul validează doar M15_v2 + M5; **H1 = AWAITING_REGIME_MAP (100% sigilat)**; nu există H4/D1 v2.

**Rezoluția e decizie de Statistician (NU o iau eu):**
- (A) Data Acquisition livrează + validează H4/H1/D1 extins (2011-2026) — dar manifestul nu le cere (doar H1, care e AWAITING_REGIME_MAP).
- (B) Resample H4/H1/D1 din M15_v2 (pipeline-ul original resampla din M15; leakage-safe în banda de embargo de 1000 bare) — introduce un produs de context derivat care nu e în manifest → cere ratificare.
- (C) Restrânge rularea la familiile fără context HTF (subset al celor 428) — schimbă domeniul → cere aprobare.

Data Acquisition mută activ fișiere în directoarele canonice (M15_v2 a apărut/dispărut între citiri; SHA se potrivește acum) — a doua confirmare că nu totul e așezat.

## Ce aștept (P3)
1. **Statistician/CEO:** decizia de sursă a contextului HTF 2011-2026 (A/B/C de mai sus).
2. Dacă (B): ratificarea resample-ului din M15_v2 (și, ideal, o intrare de manifest pentru contextul derivat).

Până atunci: **NU încep** — o rulare acum ar coruptă matricea de persistență pentru familiile HTF. Jumătatea sigilată neatinsă. Holdout SEALED. WP-5′ neînceput. STANDBY pe P3.

## UPDATE v1.2 (2026-07-28) — manifest v2.4.1 (`ab0e823`); scop = 3 regimuri; blocaj NOU pe H1 context

**Scop corectat la TREI regimuri (confirmat de manifest, nu doar de CEO).** Manifestul `changelog_v2_4`: „bear/bull/correction, 2011-2021; **the 2022-2026 regime is excluded as SAME-WINDOW-RESAMPLED, Statistician's own earlier 4-regime mandate was in error, corrected here**." Descoperirea M15_v2 = bear 52.403 + bull 52.851 + correction 25.237 = **130.491 bare** (cifre CEO; le voi verifica drept invariant de contabilitate la rulare). Leaderboard-ul de persistență = pe **3 regimuri** (3/2/1/0). Eroarea de numărătoare (a CEO, în mandate anterioare) — consemnată.

**Loader v6 = al Flow A**, `edge_research/_common.py`: „never imports the frozen Research Lab engine or any ai_trader package." Deci NU alimentează mstrat; Research Lab încarcă contextul singur (M15_v2 + HTF derivat), filtrat pe intervalele de discovery din manifest, per-bloc (leakage-safe), verificând numărătorile de discovery vs. cifrele CEO.

**BLOCAJ NOU (P3-bis) — contextul H1 derivat NU e livrat în `data/market`, iar manifestul se contrazice intern:**
- CEO: „H1 … promovat la CONTEXT_DERIVED_VALIDATED."
- Manifest `changelog_v2_4_htf_ratification`: H1_from_M15_v2 „is **NOT registered here** … stays in **acquisition_staging/, unregistered**, pending a future decision."
- Intrarea H1: `file_path = "acquisition_staging/OANDA_XAUUSD_H1_from_M15_v2_UNREGISTERED.csv"` (staging, `_UNREGISTERED`, NU în `data/market/`).
- `changelog_v2_4_1` pretinde „Registers H1_from_M15_v2" → **contradicție internă a manifestului**.
- mstrat are nevoie de `h1_trend_up` (S9/S11/S15). Fără H1 în `data/market`, acele familii rulează pe H1 NaN în 2011-2021 → **persistență coruptă**.

**BLOCAJ (flux) — directorul canonic încă se scrie:** `H4_from_M15_v2`/`D1_from_M15_v2` au apărut apoi au dispărut între două citiri consecutive (prezente în bash, absente în Python secunde mai târziu). Fără snapshot stabil verificabil prin hash, nu rulez.

**Ce cer (Data Acquisition / Statistician), ca să pornesc:**
1. Livrarea `OANDA_XAUUSD_H1_from_M15_v2.csv` în **`data/market/`** (nu staging/`_UNREGISTERED`) + reconcilierea contradicției interne a manifestului privind înregistrarea H1.
2. Confirmarea că directorul canonic **s-a așezat** (fișierele nu mai apar/dispar) — ca să pot face un snapshot stabil, verificat prin content_hash + data_file_sha256.

Guard actualizat corespunzător (P3 va verifica și H1_from_M15_v2 în `data/market`). **NU încep. Sealed neatins. Holdout SEALED. WP-5′ neînceput. STANDBY.**
