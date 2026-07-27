# D2 CLOSURE — EXECUTION LOG (WP-1…WP-4). WP-5′ NOT started.

**Document ID:** STAT-D2-EXEC-v1.0 · **Autor:** Research Lab · **Data:** 2026-07-26
**Autoritate:** CEO 2026-07-25 a autorizat WP-1..WP-4 (închiderea D2). WP-5′ (calibrare structurală) **NEAUTORIZAT — neînceput.**
**Constrângere absolută (CEO):** FDR-ul pe cele 412 ATR trebuie să rămână **neschimbat** — demonstrat numeric, nu afirmat. **Holdout SEALED.** Baseline (`results/FAMILY_RESULTS.parquet`) **neatins**; re-rularea scrie în `results/reproduction_d2/`.

---

## WP-1 — Cablare INVALID-EXECUTION (commit `00d2d26`)
Adăugat în `mstrat.simulate` ȘI `mstrat.simulate_ref` (identic, pentru paritate). Regula, operaționalizată din `MIN_STOP_FLOOR_PREREG.md`:
> o tranzacție **lărgită** (risk<min_exec → floor-uită) care se **rezolvă pe propria bară de intrare** (`xi==ei`) = gap-prin-stopul-floor-uit-la-intrare / same-bar cu fill ambiguu → **INVALID EXECUTION: exclusă, nu numărată** (cursorul de overlap avansează totuși).

Decizie de scope: INVALID e **scoped la tranzacțiile lărgite** — asta garantează prin construcție că regimul ATR (0 lărgite) e neschimbat, și e fidel intenției spec-ului (secțiunea e „R-normalization audit", despre stopuri mici). Toggle `cfg['mark_invalid']` (default True); `False` reproduce baseline-ul pre-D2. *(Variantă mai strictă — same-bar ambiguu inclusiv pe nelărgite — ar schimba ATR și nu e adoptată; e o decizie de Statistician.)*
Verificat: ATR identic ON vs OFF; `mark_invalid=False` reproduce exact FAMILY_RESULTS (S1: n=1259, exp=−0.2768).

## WP-2 — Paritate + smoke (PASS)
`run_lot.parity_and_smoke`: paritate `simulate`==`simulate_ref` **PASS** (regula INVALID adăugată identic în ambele); toate 20 familii smoke/lookahead/ledger **OK**.

## WP-3 — Re-rulare uniformă + DOVADA că cele 412 sunt neschimbate
Re-rulat `run_full_campaign.py` cu engine-ul cu D2 închis (mark_invalid=True) → `results/reproduction_d2/FAMILY_RESULTS.parquet` (baseline neatins). Comparație vs baseline (`code/d2_verify.py`):

| set | max\|diff\| numeric | flip-uri flag bool |
|---|---|---|
| **ATR toate (428)** | **0.000e+00** | 0 |
| **ATR valid FDR-412** | **0.000e+00** | 0 |

**`ATR_UNCHANGED = True` — constrângerea îndeplinită EXACT.** Cele 412 pe care s-a rulat FDR-ul sunt provabil identice → **rezultatul FDR rămâne valid, neschimbat**. (Dacă ar fi fost ≠0, m-aș fi oprit — nu e cazul.)

## WP-4 — Re-audit (ce s-a schimbat, în afara ATR)
Comparație completă 1972 (`results/reproduction_d2/d2_verify_summary.json`):
- **686/1972 ipoteze** cu schimbare numerică; **0 în ATR** (constrângerea ține); toate în struct/ema.
- **58.225 tranzacții eliminate** (INVALID), median 13/ipoteză, max 908. Familii: S1 (418 ipoteze), S2/S3 (48 fiecare), S8/S10/S12 (24), etc.
- Flip-uri de flag: **hist_prof 357 → 426** (+69), **research_worthy 130 → 138** (+8), **fragile 133 → 152** (+19).

**CONSTATARE NOTABILĂ (direcție opusă așteptării pre-declarate), consemnată nu concluzionată:** CEO se aștepta ca excluderea să „îndepărteze observații majoritar din ipoteze deja pierzătoare, curăță măsurătoarea, nu descoperă nimic." Măsurat: tranzacțiile INVALID eliminate erau **majoritar pierzătoare** (stop-out-uri pe stopuri mici floor-uite), deci eliminarea lor a **RIDICAT** profitabilitatea aparentă — **69 de ipoteze au trecut din pierzătoare în (marginal) profitabile** (hist_prof 357→426). Deci curățarea NU e cosmetică: schimbă care ipoteze sunt net-profitabile.
**Calificări (fără a concluziona):** (1) cele 69 sunt **structural-stop → integral în afara regimului validat** (matched_null@v1 nu le poate testa) → **nu sunt descoperiri**; (2) profitabilitatea lor e marginală (erau la graniță; eliminarea câtorva pierzători le-a trecut peste); (3) dacă profitabilitatea „curățată" e edge real sau artefact de eliminare selectivă a tranzacțiilor ne-executabile e **întrebare de Statistician**, nu a Research Lab. Direcția rămâne conservatoare pe axa concentrării (§8 diagnostic: floor-ul trunchiază coada), dar pe axa profitabilității cleaning-ul mută 69 peste prag.

### WP-4b — MECANISMUL (de ce 357→426 NU e eliminare selectivă / p-hacking)
Consemnat cu citare, ca să nu fie citit greșit peste șase luni. Bucla de ieșire din `mstrat.simulate` verifică **stopul ÎNAINTEA țintei**:
```
code/mstrat.py:68   if lo[j]<=stop: ex=stop;xi=j;break      # (long) STOP verificat primul
code/mstrat.py:69   if tgt is not None and ... hi[j]>=tgt: ex=tgt;xi=j;break   # ținta abia după
```
(identic short: liniile 71/72; și în `simulate_ref` 128/129, 131/132). Consecință: **pe orice bară unde ATÂT stopul CÂT ȘI ținta sunt atinse, stopul câștigă întotdeauna** — tranzacția e scorată drept pierdere. Aceasta e exact „worst-case model" pre-înregistrat în `docs/MIN_STOP_FLOOR_PREREG.md:31` („entry/exit inside the same bar with **ambiguous fill that the worst-case model cannot resolve**").

Deci cele 58.225 de tranzacții INVALID eliminate erau majoritar pierzătoare **PRIN CONSTRUCȚIE**: bara ambiguă a fost mereu rezolvată în **defavoarea** strategiei (stop-first). **Excluderea lor NU introduce o părtinire optimistă — elimină una PESIMISTĂ care era deja acolo.** Mișcarea hist_prof 357→426 nu vine dintr-o selecție favorabilă, ci din retragerea unei penalizări pe cazuri intrabar nerezolvabile pe care spec-ul le marchează ca ne-măsurabile. (Notă tehnică: regula mea exclude toate cele lărgite-same-bar, nu doar cele stop-first-ambigue; contrastul stop-first e mecanismul dominant de ce eliminatele erau pierzătoare.)

**Ce rămâne DESCHIS (întrebare de Statistician, NU a Research Lab):** că părtinirea era pesimistă **nu** implică automat că **excluderea totală** e remediul corect. Alternativa e **raportarea separată** — tranzacții rezolvabile vs. ambigue — în loc de eliminare. Iar cele 69 nou-profitabile pot fi reale **sau** doar mai puțin penalizate. Se transmite Statisticianului împreună cu întrebarea despre potrivirea lui R.

---

## Guvernanță / stare (decizie CEO 2026-07-25)
- Baseline `results/FAMILY_RESULTS.parquet` **neatins**. Re-rularea D2-închis trăiește în `results/reproduction_d2/` (version-stamped). **Se păstrează AMBELE.**
- **`reproduction_d2` NU se promovează la canonic ACUM.** Motiv (CEO): FAMILY_RESULTS actual e baza pentru inventarul de concentrare, diagnosticul de stop-floor, măsurătoarea de distribuție, certificarea S18 și toate rapoartele Flow C — înlocuirea azi ar face fiecare cifră citată în ele nereproductibilă fără notă. `reproduction_d2` devine canonic **doar după ce Statisticianul se pronunță asupra excluderii**, și atunci **cu un document de tranziție** care mapează cifrele vechi la cele noi.
- Documentele descriptive deja comise rămân valide pe baseline; nu sunt invalidate.
- **WP-5′ (calibrare structurală separată) NEAUTORIZAT — neînceput.** Închiderea D2 e NECESARĂ dar NU SUFICIENTĂ pentru testarea structurală.
- **Consecință de dimensiune a problemei (semnalată de CEO):** regimul structural are acum **426** ipoteze profitabile (nu 357) și rămâne **netestabil**; poarta e în continuare calibrarea structurală, care depinde de întrebarea despre R.

## STANDBY — se așteaptă Statisticianul la DOUĂ întrebări
1. **Potrivirea lui `R = pnl/risc`** ca variabilă de rezultat pentru regimul structural (varianță explozivă la risc→0 e proprietate a statisticii, nu a rezoluției; date fine măsoară mai bine numitorul, nu-l fac mai mare). — `D2_CLOSURE_SIZING_v1.0.md`.
2. **Tratamentul corect al tranzacțiilor ambigue:** excludere totală (implementat acum) vs. raportare separată rezolvabile/ambigue. — §WP-4b de mai sus.

Până la răspunsuri: **NU** încep WP-5′, **NU** promovez nimic la canonic, **NU** re-rulez nimic.

**WP-1..4 executate. Cele 412 provabil neschimbate (0.000e+00). Holdout SEALED. WP-5′ neînceput. STANDBY.**
