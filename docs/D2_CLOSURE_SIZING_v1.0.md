# D2 CLOSURE — SIZING (re-scope of WP-1…WP-4). NOT executed.

**Document ID:** STAT-D2-SIZING-v1.0 · **Autor:** Statistician (Research Lab) · **Data:** 2026-07-25
**Extinde:** `docs/TRANSFERABILITY_ADDENDUM_v1.1.md` (WP-1..WP-5). **Cerere:** CEO 2026-07-25 — dimensionează închiderea D2, răspunzând precis la 4 întrebări. **Nimic executat, nicio re-rulare pornită.** Cifrele de afectare sunt măsurate pe motorul observat (segment research); regula e citată din `docs/MIN_STOP_FLOOR_PREREG.md`.

**Cifre de afectare (măsurate, ALL 1972, research):** 1.300.740 tranzacții total; **77.851 lărgite (5.99%)**, TOATE în struct (65.350) + ema (12.501), **ZERO în atr**; **725/1972 ipoteze** au ≥1 tranzacție lărgită. Proxy INVALID (entry/exit în aceeași bară printre cele lărgite): ~48.968 tranzacții, 672/1972 ipoteze. Pe corpul profitabil (357 hist_prof): doar **1.144 lărgite, 64/357 ipoteze, best-trade aproape niciodată lărgit** (13/357).

---

## Q1 — Ce înseamnă exact WP-1 (INVALID-EXECUTION), per specificația pre-înregistrată

Specificația (`MIN_STOP_FLOOR_PREREG.md`) distinge DOUĂ lucruri pe care nu trebuie să le confundăm:
1. **FLOORING (deja implementat, `mstrat.py:54`):** „Any trade whose strategy_stop_distance < min_executable_risk is FLOORED … **it is still a trade** but at the executable risk." Deci tranzacțiile lărgite **RĂMÂN în rezultat**, la riscul-podea. NU se exclud, NU se raportează separat.
2. **INVALID-EXECUTION (necablat = WP-1):** „marked INVALID EXECUTION (**excluded, not counted**) **only if it cannot be executed at all**: gap through the floored stop at entry, zero/negative risk after flooring, or entry/exit inside the same bar with ambiguous fill." Plus un **audit per tranzacție** (stop tick-rotunjit, spread intrare+ieșire, slippage, gap-over-stop, modificare stop, break-even, exit-uri parțiale, ordonare intrabar, R-max-posibil vs realizat).

**Răspuns:** tranzacțiile care ating podeaua **NU se exclud** — se lărgesc și rămân numărate (deja e cazul). Se **EXCLUD** (nu se raportează separat) DOAR cele genuin ne-executabile (gap prin stopul floor-uit la intrare / risc≤0 după floor — imposibil, floor-ul garantează >0 / aceeași-bară ambiguu). WP-1 = cablarea acestei excluderi înguste + câmpurile de audit. NU e „exclude toate cele lărgite".

## Q2 — Campanie întreagă sau doar familiile structurale? Câte ipoteze afectate?

- Flooring-ul e deja **uniform** în engine-ul comun; INVALID-EXECUTION e un audit per-tranzacție adăugat în `simulate` partajat → toate familiile trec prin el. Spec-ul **MANDATEAZĂ** re-rulare uniformă: „re-run ALL families S1–S20 uniformly on v2." Deci re-rulare completă (guvernanță), NU doar structurale.
- **DAR impactul de rezultat e localizat:** lărgirea = **ZERO în regimul atr** (428 ipoteze, inclusiv cele 412 pe care s-a rulat FDR-ul). Deci **rezultatul FDR pe subsetul ATR rămâne valid, neschimbat** — nu are nevoie de re-rulare pentru corectitudine. Schimbările reale sunt în struct+ema.
- **Ipoteze efectiv afectate:** 725/1972 au ≥1 lărgită (≈37%), toate struct/ema. Proxy INVALID: 672/1972. Pe corpul PROFITABIL doar 64/357, iar best-trade-urile lor sunt nelărgite → metricile candidaților interesanți se mișcă neglijabil; grosul excluderilor cade pe ipotezele structurale **pierzătoare** (deja respinse).
- **Compute:** mărginit — campania se reproduce (1.300.740 tranzacții, ~ore neasistate).

## Q3 — DECISIV: după cablare, matched_null@v1 devine aplicabil regimului structural?

**NU — rămâne validat doar pe ATR-scaled. Cablarea D2 NU deblochează testarea structurală.**

Raționament:
- WP-1 curăță **STATISTICA** (R) pentru ipotezele structurale (exclude tranzacțiile ne-executabile, elimină contaminarea de R-normalizare). Nu atinge **CALIBRAREA** metodei.
- Calibrarea `matched_null@v1` (p uniform sub null, FPR≈5%, curbă de putere) a fost stabilită **exclusiv pe regimul ATR-scaled cu semnale generice**. Scenariul `struct_stops` din bateria F6 folosea stopuri structurale sintetice **mărginite** de range-ul barei (±2 ticks), NU stopurile reale `prev_ext`/`beyond_sweep` care pot sta la ~0.05 ATR. Regimul structural real **nu a fost niciodată în baterie** (constatarea R4 din Addendum v1.1).
- Deci, pentru a testa ipotezele structurale, e nevoie de o **calibrare separată pe regimul structural**: baterie F6-style cu setup-uri structural-stop **fidele** (reproducând numărătorile reale), rulată **pe engine-ul cu D2 închis**, verificând p uniform / FPR / putere.
- **Dependență dură de ordine:** acea calibrare trebuie să ruleze **DUPĂ** WP-1..4 (altfel calibrează pe statistica contaminată — punctul R1). Ordine: WP-1..4 (închide D2) → **calibrare structurală separată** → FDR structural.
- **Semnal de risc (poate face calibrarea să eșueze):** exact argumentul CEO de la retragerea asimetriei — la risc→0, R are **varianță explozivă în ambele brațe**; varianța mare **distruge puterea**. După excluderea INVALID, unele ipoteze structurale scad sub n≥25 → ineligibile. Deci calibrarea structurală poate arăta **putere scăzută** pe M15 → motiv concret pentru achiziția de date mai fine (tick/1M), care ar micșora varianța R prin măsurarea precisă a stopurilor mici.

**Concluzia pentru decizie:** închiderea D2 este **NECESARĂ dar NU SUFICIENTĂ** pentru testarea structurală. Poarta reală e calibrarea structurală separată, iar ea poate lovi zidul de putere. Deci întrebarea „acum vs după achiziția de date" se reduce la: **dacă ne așteptăm ca bateria structurală să treacă pe M15, închidem D2 acum și calibrăm; dacă ne așteptăm la putere scăzută (probabil, dat fiind varianța R la stopuri mici), achiziția de date fine ar trebui să preceadă calibrarea** — D2 se poate închide oricum acum (e ieftin și sigur, §8 din diagnostic: nu inflaționează nimic), dar deblocarea efectivă a testării depinde de calibrare, nu de D2.

## Q4 — Efort (scala S/M/L) și ce s-a schimbat față de estimarea inițială

| WP | conținut | mărime | schimbare vs Addendum v1.1 |
|---|---|---|---|
| **WP-1** | Cablare INVALID-EXECUTION (excludere îngustă genuin-ne-executabile) + audit per-tranzacție | **M** | neschimbat ca mărime; scope mai clar (flooring deja făcut, doar excluderea îngustă + audit); auditul trebuie să trateze corect ~49k candidați same-bar/gap |
| **WP-2** | Re-validare paritate + smoke, acoperind INVALID-EXECUTION | **S–M** | neschimbat |
| **WP-3** | Re-rulare uniformă S1–S20 pe engine-ul cu INVALID; results version-stamp, NU suprascrie baseline | **L (calcul) / S (uman)** | neschimbat; NOU: regimul ATR provabil neschimbat → FDR-ul pe 412 rămâne valid, se poate verifica prin diff |
| **WP-4** | Re-audit: ce ipoteze se mișcă; diff vs baseline | **S–M** | ↓ de la M — set afectat caracterizat (struct/ema, majoritatea pierzătoare; ATR neatins) |
| **WP-5′** | **Calibrare structurală separată** a matched-null (baterie F6-style pe engine-ul cu D2 închis, setup-uri structural-stop fidele) | **M–L** | **NOU explicit și PURTĂTOR** — asta deblochează testarea structurală, NU WP-1..4; era implicit în R4/WP-5. Risc: poate eșua / putere scăzută |

**Ce s-a schimbat, esențial:** închiderea D2 (WP-1..4) e **mai ieftină și mai sigură** decât părea (afectare zero pe ATR, best-trade-uri nelărgite, §8: trunchiază coada = nu poate inflaționa niciun rezultat). **DAR** „a închide D2" ≠ „a debloca testarea structurală". Addendum-ul inițial sub-pondera calibrarea structurală separată (WP-5′), care e acum piesa decisivă și purtătoare de risc. Punctul 3 e cel care decide: D2 se poate închide acum (sigur, ieftin, prerechizit), dar go/no-go pentru testarea celor 79% depinde de calibrarea structurală, care poate cere mai întâi date mai fine.

---

**Nimic executat. Nicio re-rulare pornită. Holdout SEALED. Dimensionare livrată pentru decizia CEO.**
