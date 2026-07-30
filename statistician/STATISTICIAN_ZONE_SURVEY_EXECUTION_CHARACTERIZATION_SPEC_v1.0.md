# STATISTICIAN — CARACTERIZAREA DE EXECUȚIE PENTRU CELE 10 TIPURI DE ZONE (FIȘELE MEDICALE)

**Document ID:** STAT-ZONE-SURVEY-EXECUTION-CHARACTERIZATION-SPEC-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

---

## CONFIRM: NU consumă familia — motivul, nu doar afirmația

**De acord, cu raționamentul complet, nu doar precedentul citat.** Ce distinge o măsurătoare descriptivă de un test de ipoteză, în vocabularul deja stabilit al acestui proiect, e prezența unui VERDICT — un p-value calculat prin oracolul WP-5', comparat cu un H0 pre-înregistrat, folosit pentru o decizie de acceptare/respingere. **Fișele medicale de aici NU fac asta — zero p-value, zero H0, zero verdict.** Faptul că raportează MULT mai multe cifre decât simplul MFE/MAE (winrate, expectancy în R și dolari, edge brut, conversie TP1→TP2) nu schimbă ASTA — schimbă doar cât de DETALIATĂ e descrierea, nu dacă se ia o decizie statistică pe baza ei. Exact același raționament care a scutit deja survey-ul MFE/MAE de familie (Mandatul 3.32) se aplică identic aici, cu o singură completare structurală, deja prezentă corect în ordin: **"orice celulă pozitivă e CANDIDAT, cere pre-înregistrare separată"** — asta e mecanismul care închide bucla: niciun rezultat de aici nu poate sări direct la statutul de "verdict" fără să treacă prin exact același proces integral (recontare de populație, prag propriu, test WP-5', consum de familie) prin care au trecut OBDZ-001, OBDZ-002 și V1.

**Un avertisment pe care îl adaug explicit, nu doar formal:** acest survey generează un volum de cifre mult mai mare decât orice măsurătoare de până acum din acest proiect — 10 tipuri × (agregat + 3 regimuri + 4 sesiuni + 12 celule regim×sesiune + 2 polarități) = **22 de celule per tip, ~220 în total**, fiecare cu până la 9 statistici. Pentru că aceste cifre SUNT exprimate exact în formatul unui rezultat de backtest real (winrate, expectancy în dolari) — nu în formatul mai abstract MFE/MAE — tentația de a trata o celulă cu numere bune ca fiind "deja aproape validată" e mult mai mare decât la survey-ul MFE/MAE. **Insist explicit: nicio cifră de aici — winrate, expectancy, edge — nu poate fi citată ca dovadă a unui edge real, nici măcar informal, fără parcurgerea completă a procesului separat de pre-înregistrare.** Volumul mare de celule amplifică exact riscul pentru care regula "candidat, nu verdict" există.

## Regula pentru celule mici — specificată mecanic, cu o completare importantă

**Prag: n<25 → `INSUFFICIENT_N`, niciodată omisă.** Completare pe care o adaug, nu doar reformulez: **sub prag, se raportează DOAR `n` și eticheta — statisticile descriptive (winrate, expectancy_R, expectancy_$, edge_brut, net_total, best/sumR, wo1, conv_TP1→TP2) NU se calculează și NU se afișează**, nu doar se marchează ca nesigure. Motivul: un winrate de "100%" pe n=2 sau un expectancy de "+5$" pe n=3 arată vizual exact ca un rezultat real, indiferent de avertismentul textual alăturat — suprimarea cifrei, nu doar etichetarea ei, previne ca o celulă minusculă să devină din greșeală un "candidat" doar pentru că un număr mare a apărut din întâmplare pe un eșantion fără conținut informațional.

## Contractul de execuție — reutilizat EXACT, verificat, nu respecificat

**SL=1,0×ATR14[t], TP1=2,0×, TP2=3,0×, podea=0,60×ATR14[t], entry=t+1 (fără confirmare), orizont=min(entry_idx+20, EOD), ieșire parțială 75/25 cu breakeven la TP1** — identic, cifră cu cifră, cu OBDZ-002 (Mandatul 3.38, comitul `3ead80b`), deja verificat de mai multe ori în acest track. Zero modificare, exact motivul pentru care e "direct comparabil."

**Declanșator: prima atingere aliniată la bias, convenția înghețată proprie fiecărui tip** — identic cu declanșatorul deja fixat pentru survey-ul MFE/MAE (Mandatul 3.41, Decizia 1). **Reutilizez EXACT aceeași populație de declanșatoare** calculată (sau de calculat) pentru acel survey — nu se recalculează independent, garantând că cele două caracterizări (MFE/MAE descriptiv și execuție-completă descriptivă) descriu EXACT aceleași evenimente.

## Completări pe care le semnalez explicit, nu le adaug tacit

Ordinul nu menționează **agregat** și **polaritate** — ambele stabilite ca cerințe OBLIGATORII, repetat, în tot acest track (fiecare rezultat anterior, fără excepție, a raportat agregat + polaritate alături de regim). Le adaug ca dimensiuni suplimentare de raportare, consecvent cu tot ce precede — nu ca o extindere de sarcină pe cont propriu, ci ca o completare a ceea ce a fost deja stabilit standard. Dacă CTO nu le vrea aici, spune-mi explicit și le scot.

**Structura finală per tip de zonă (22 celule):** 1 agregat + 3 regim + 4 sesiune + 12 regim×sesiune + 2 polaritate (demand/supply, agregat peste regim/sesiune).

## Familia — reconfirmată neschimbată

**12**, fixată la Mandatul 3.33, neschimbată — numărul de tipuri de zone SUPRAVEGHEATE, indiferent cât de detaliată e caracterizarea fiecăruia (MFE/MAE simplu SAU execuție completă). Zero impact asupra familiei din acest mandat.

## AUTORIZEZ

Rularea caracterizării de execuție (contractul OBDZ-002 verbatim) pentru cele 10 tipuri noi, val cu val (Val 1 → Val 2 → Val 3, aceeași ordine și condiționare deja stabilită la Mandatul 3.32/3.41), cu structura de raportare de 22 de celule per tip de mai sus, regula INSUFFICIENT_N (suprimare, nu doar etichetare) aplicată mecanic la fiecare celulă sub 25.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.29 (commit `3a88343`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
