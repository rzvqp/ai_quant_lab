# TRANSFERABILITY DETERMINATION — ADDENDUM v1.1

**Document ID:** STAT-TRANSFER-DET-v1.1 · **Extinde:** `docs/TRANSFERABILITY_DETERMINATION_v1.0.md`
**Data:** 2026-07-25 · **Autor:** Statistician (Research Lab)
**Declanșator:** CEO a semnalat trei commit-uri nemerge-uite pe `flow-c-foundation` (`28c35b6` WIP, `aa5bee3` VALIDATED, `69747fd` Verdict A) care conțin o reconstrucție matched-null din 2026-07-13 — exact obiectul R2 pe care determinarea v1.0 îl marcase „reconstrucție, nu reutilizare".
**Metodă:** citit din blob-urile git pe `origin/flow-c-foundation`. **Fără merge, fără execuție.** Toate cifrele sunt citite din artefactele comise (`results/matched_null_validation/*.json`), nu re-rulate.
**Constrângere de framing (CEO):** NU emit verdict asupra cărei validări e „superioară" (a mea, F6, sau cea din 2026-07-13). Întrebările sunt: **ce cod e refolosibil** și **dacă ordinea D2-întâi se menține**.

---

## 0. Ce este reconstrucția din 2026-07-13 (factual)

Șase module în `code/` (`matched_null.py`, `synth_price.py`, `mn_calibration.py`, `mn_power.py`, `mn_adversarial.py`, `run_matched_null_pilot.py`) + `docs/MATCHED_NULL_{SPEC,VALIDATION}.md`. `PROJECT_AUDIT.md` de pe acel branch marchează **D3 = RESOLVED** („Rebuilt on synthetic PRICE series routed through mstrat.simulate … VALIDATED (Verdict A), unstratified config. Not yet merged"). Pe linia principală D3 e încă deschis fiindcă commit-urile nu au fost merge-uite. **D2 rămâne HIGH/deschis și pe `flow-c-foundation`** (INVALID-EXECUTION tot necablat).

---

## 1. Q1 — Cât din R1–R5 e deja acoperit? Re-dimensionare WP-5

| Element (v1.0) | Stare în codul din 2026-07-13 | Dovadă în cod |
|---|---|---|
| **R1** — re-stabilirea empirică a uniformității pentru statistica R | **ACOPERIT metodologic** (empiric, dar pe semnale generice + engine cu D2 deschis) | `mn_calibration.py`: 120 serii null → KS p=0.113, FPR(0.05)=0.025 CI[0.009,0.071], `CALIBRATED=true` |
| **R2** — harness nou care conduce `mstrat.simulate` cu null Test-A | **ACOPERIT INTEGRAL** — cea mai mare bucată din WP-5, deja construită | `matched_null.py`: `observed_profile`/`_null_mean`/`matched_null_p`, `import mstrat as MS`, `r = MS.simulate(...)` |
| **R3** — nulul `_pool` sub-specificat (stop fix 1.5×ATR) | **REZOLVAT / SUPERSEDAT** — nulul nou păstrează profilul realizat risc/ATR, nu 1.5×ATR fix; nu folosește deloc `_pool` | `_null_mean`: `risk = risk_over_atr[j] * atr[i]` |
| **R4** — fidelitate pe cele 20 de familii | **NEACOPERIT** — bateriile folosesc semnale generice, nu providerii de familii | `synth_price.py`: `exo/breakout/sweep/timeofday_signals` + `make_setups`; zero apeluri la gramatica S1–S20 |
| **R5** — rezoluția estimatorului (MC adaptiv la m=1552) | **PARȚIAL** — mașinăria MC adaptiv există (20k→200k); FDR global la ≥1e6 nerulat (gated, în afara sferei) | `run_matched_null_pilot.py`: `B_TRIAGE=20000; B_REFINE=200000` |

**Re-dimensionare WP-5: de la „L" la „S–M" pentru partea de inginerie.** Harness-ul (R2), fix-ul de nul (R3), mașinăria de baterie (R1) și MC-ul adaptiv (R5) sunt **deja scrise și refolosibile ca atare**. Ce rămâne nu e reconstrucție, ci: **(a)** R4 — fidelitatea la providerii de familii (design real, ~M, sau justificarea că semnalele generice transferă); **(b)** o **re-rulare obligatorie** a calibrării/puterii/adversarialului **după închiderea D2** (vezi §5–§6), ieftină uman, mărginită la calcul. Codul nu se aruncă — se refolosește; validarea trebuie re-stabilită pe engine-ul curat.

---

## 2. Q2 — Rula efectiv prin `mstrat.simulate`, sau printr-un proxy? (verificat în cod)

**Prin `mstrat.simulate`, nu proxy.** `matched_null.py` liniile 7, 19, 91: `import mstrat as MS`; observatul e executat de `MS.simulate(d, setups, cfg)`; fiecare replică null e executată de `r = MS.simulate(d, setups, cfg)['R'].values`. Cele trei baterii importă `matched_null as MN` și `synth_price as SP` și apelează `MN.matched_null_p(...)` → deci **trec efectiv prin engine-ul v2 real**, cu stop-floor-ul lui activ. Paritatea (`test_matched_null_parity.py`, raportată în doc §6) confirmă R observat = R din `MS` la <1e-12. Documentația și codul coincid aici.

## 3. Q3 — `synth_price.py` rezolvă R4 (fidelitatea)? Pe câte familii?

**Nu.** `synth_price.py` **nu reproduce niciuna** dintre cele 20 de familii. Are propriile 4 template-uri generice de semnal (`exo_signals` = bare aleatoare price-independent, `breakout_signals`, `sweep_signals`, `timeofday_signals`) și construiește setup-uri direct cu `make_setups` (intrare la next-open, stop ATR sau structural). Calibrarea/puterea/adversarialul rulează pe aceste semnale generice — **nu** pe gramatica S1–S20 cu feature-urile ei (FVG, VWAP, opening range, compression, swings, PDH/PDL, context MTF). Fidelitatea de tip F6 („reproduce exact numărătorile reale") **nu e stabilită** pentru suprafața de familii. Singurul loc care atinge familiile reale e **pilotul** (`run_matched_null_pilot.py`, `MS.setups(res, h)`), dar el rulează pe **date reale** → fără adevăr-teren, deci nu poate măsura FPR/putere acolo. **R4 rămâne deschis.**

## 4. Q4 — Nulul e Test A din spec, sau `_pool`-ul sub-specificat cu 1.5×ATR fix?

**Test A autentic — NU `_pool`-ul.** `_null_mean` bootstrapează profilul realizat (direcție, exit, și **risc ca raport risc/ATR**) al tranzacțiilor observate executate, alege **timing de intrare aleator** dintr-un pool eligibil (opțional stratificat), **rescalează riscul la ATR-ul local** la bara de intrare contrafactuală, și rulează prin `MS.simulate`. Păstrează direcția, numărul de tranzacții executate, regula de exit, costurile și overlap-ul (prin engine), randomizând doar timing-ul — exact definiția Test A. Nu apelează `_pool` și nu folosește 1.5×ATR fix. **Aceasta este o îmbunătățire reală față de defectul din R3.**

## 5. Q5 — Verdictul asupra ipotezei „D2-ca-drift": susținut, contrazis, sau netestabil?

**Forma tare a ipotezei — „FPR=0.975 ESTE D2 manifestat ca sensibilitate la drift, cele două constatări sunt aceeași" — este CONTRAZISĂ de cod.** Lanțul probator, direct din artefacte:

1. `git diff 28c35b6 aa5bee3 -- code/matched_null.py` arată că **singura schimbare** WIP→VALIDATED este trecerea de la bootstrap de **risc absolut** la **risc/ATR rescalat la ATR-ul local**.
2. `MATCHED_NULL_VALIDATION.md §2` declară explicit: pre-fix `drift_long FPR=0.975, trend_short=0.925, regime_shift=0.25`; post-fix `0.00 / 0.00 / 0.00`. Cauza diagnosticată: „risc absolut eșantionat de la o bară târzie cu ATR mare, aplicat la o bară timpurie cu ATR mic → nepotrivire de volatilitate locală → nulul nu captează drift-ul, deci observatul câștigă mereu."
3. `adversarial_summary.json` comis confirmă starea finală: `drift_long fpr05=0.0` (mean_p 0.53), `trend_short fpr05=0.0` (mean_p 0.55), `struct_stops fpr05=0.0`, `ALL_SCENARIOS_CALIBRATED=true`.
4. **Fix-ul nu atinge D2:** INVALID-EXECUTION rămâne necablat, D2 rămâne HIGH/deschis pe același branch.

**Logica decisivă:** dacă D2 (explozia R din stop minuscul) ar fi fost motorul FPR-ului de 0.975, o corecție care lasă mecanismul de explozie R intact **nu ar fi putut** readuce calibrarea la 0.00. Faptul că o corecție pur de **potrivire risc-la-volatilitate** a rezolvat drift-FPR-ul, cu D2 neatins, arată că **cele două defecte sunt separabile**: drift-FPR-ul a fost un artefact de **construcție a nulului**, distinct de D2. Ipoteza de unificare nu e susținută.

**Reziduul care rămâne netestabil fără execuție** (și pe care îl declar cinstit, nu îl închid):
- Bateria **sub-exercită** cazul-cel-mai-rău al D2. Stopul „structural" sintetic (`make_setups`: `l[t]−2·TICK` / `h[t]+2·TICK`) e mărginit de range-ul barei de semnal; stopurile reale `prev_ext`/`beyond_sweep` pot sta la ~0.05 ATR de intrare (mult mai mici). Deci `struct_stops fpr05=0.0` **nu** certifică faptul că D2 e inofensiv pe setup-urile reale cu stop structural.
- Grosul validării folosește `risk_kind='atr'` (1.5×ATR) — stopuri **care nu declanșează D2**. Regimul D2 e practic **neatins** de baterie.
- Rescalarea risc→ATR-local modulează și magnitudinea exploziei R (risc mai mare în vol mare = R mai mic), deci fix-ul **întâmplător** atenuează parțial D2 — cele două sunt entangled în implementare, chiar dacă direcția diagnosticului (diluția capturii de drift) e un efect de nivel, nu de explozie.

**Verdict Q5:** forma tare **contrazisă de cod**; un reziduu slab (D2 ar putea totuși contamina statistica pe familiile reale cu stop structural) **rămâne netestabil fără execuție** pe engine-ul cu D2 închis.

## 6. Q6 — Se schimbă secvențierea? Rămâne D2-întâi?

**Rămâne D2-întâi — și argumentul se ÎNTĂREȘTE, dintr-un motiv mai ascuțit decât în v1.0.** Validarea din 2026-07-13 a stabilit Test B pentru setup-uri **cu stop ATR / bine-comportate**, pe semnale generice. Prin propria ei sferă, ea **exclude regimul D2**: familiile cu stop structural (`beyond_sweep`/`prev_ext` — exact S1/S6, sursele D2) sunt tocmai cele pe care calibrarea validată **nu** a fost stabilită. Închiderea D2 (cablarea INVALID-EXECUTION) **schimbă statistica R** exact pentru acele setup-uri → calibrarea trebuie **re-stabilită pe engine-ul cu D2 închis**, în special pentru setup-urile cu stop structural.

Deci secvența din §6 v1.0 se menține, rafinată:
1. **Închide D2** (WP-1..4 din v1.0) — neschimbat.
2. **Refolosește harness-ul din 2026-07-13** (R2/R3 gata) — nu-l reconstrui.
3. **Re-rulează calibrarea/puterea/adversarialul pe engine-ul cu D2 închis**, cu accent pe stopuri structurale la scala reală (acoperă R4 + reziduul Q5 într-un singur pas).
4. Abia atunci Test B validat intră în FDR global (gated, holdout sigilat).

Nota de convergență: pilotul (`§7`) și limitarea sa `§9.3` spun explicit că sub FDR-ul global (m=1552, prag BH ≈3.2e-5) **niciuna** dintre cele 10 ipoteze reale nu ar fi semnificativă — coerent cu așteptarea „un p-engine valid respinge majoritatea corpului = rezultat corect", și cu D2/D6 măsurate de Flow C.

---

## 7. Corecții aduse determinării v1.0 (audit-trail)

- **R2 nu mai e „reconstrucție de la zero".** Un harness Test-A care conduce `mstrat.simulate` **există deja** (2026-07-13, `matched_null.py`), nemerge-uit. v1.0 l-a marcat inexistent pentru că a fost făcută de pe `statistician-foundation`, unde commit-urile nu apar. Corectat.
- **R3 e deja rezolvat** în acel cod (risc/ATR realizat, nu 1.5×ATR fix).
- **Ce NU se schimbă din v1.0:** blocajul dur D2 (§5 v1.0) rămâne constatarea centrală — de fapt întărită: acea validare a fost făcută cu D2 deschis și cu regimul D2 practic neatins de baterie, deci nu îl neutralizează. Secvențierea D2-întâi se menține.
- **Fără ierarhizare de validări**, per instrucția CEO: nu afirm care validare e superioară; afirm doar ce cod e refolosibil (R2/R3/R1/R5 machinery) și că D2-întâi rezistă.

---

## 8. Constrângeri respectate

| Cerință | Stare |
|---|---|
| Fără merge | ✅ citit din blob `origin/flow-c-foundation` |
| Fără execuție | ✅ toate cifrele citite din artefactele comise |
| Fără global-FDR / holdout / re-rularea campaniei | ✅ neatins |
| Verificare în cod, nu în documentație (Q2/Q3/Q4) | ✅ diff + citire modul, nu doar `MATCHED_NULL_VALIDATION.md` |
| Fără verdict „cine avea dreptate" | ✅ doar refolosibilitate + secvențiere |
| Clonă separată, protocol de rebase | vezi commit + `git ls-remote` la închidere |
