# STATISTICIAN — VERDICTUL FINAL OBDZ-002 ȘI ÎNCHIDEREA LINIEI OBDZ

**Document ID:** STAT-OBDZ002-FINAL-VERDICT-LINE-CLOSURE-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă, cifră cu cifră, înainte de verdict:** citit direct comitul `3ead80b` (`ai_quant_lab-wp5b`) și `reports/obdz002_run_results.json` — toate cifrele citate în mandat reproduse exact: `p_wp5` = 0,6367/0,8611/0,2884 (bear/bull/corecție); `expectancy_dollars` = -0,03434/-0,14994/+0,27109; `edge_brut_dollars` = +0,16566/+0,05006/+0,47109; `conv_TP1_TP2` = 0,62/0,658/0,685; polaritate bear demand=+0,16716/supply=-0,31053; polaritate corecție demand=+0,10888/supply=+0,53778. **Toate confirmate la a cincea zecimală, nu doar la rotunjirea citată.**

**O constatare aritmetică suplimentară, verificată direct, nemenționată în mandat dar centrală pentru verdict:** `edge_brut_dollars − expectancy_dollars` = exact **0,20** în TOATE cele trei regimuri (0,16566-(-0,03434)=0,2; 0,05006-(-0,14994)=0,2; 0,47109-0,27109=0,2). **Costul e o cifră FIXĂ, în dolari, identică în toate regimurile — NU proporțională cu ATR.** Aceasta e diagnoza structurală din spatele verdictului, nu doar o observație colaterală.

---

## ETICHETA, cu delimitare de scop explicită

**`REJECTED_AT_DECLARED_PARAMETRIZATION` — a doua oară, în aceeași familie de 2.**

Delimitare, exact ca la OBDZ-001 (Mandatul 3.26), acum reconfirmată pe a doua construcție distinctă: **RESPINSĂ e construcția asta EXACT** (declanșator compus direct, SL/TP1/TP2/podea = 1,0×/2,0×/3,0×/0,60×ATR14[t], fără confirmare) — NU semnalul de bază. Semnalul care justifică întreaga linie (zona depășește retragerea-fără-zonă pe MFE, +0,232×ATR agregat, semnificativ statistic, `STATISTICIAN_OBDZ_PAIRED_TEST_VERDICT_v1.0.md`, Mandatul 3.35) **rămâne exact cum a fost verificat — NEATINS de acest verdict.** Ce s-a respins e conversia acelui semnal, prin DOUĂ parametrizări de risc distincte și motivate (0,7×/1,4×/2,1× la OBDZ-001; 1,0×/2,0×/3,0× la OBDZ-002), într-un net_R comercial semnificativ statistic. Ambele au eșuat.

## Verdictul direct: LINIA OBDZ SE ÎNCHIDE

**Da, se închide. Nu propun o a treia parametrizare.** Motivele, fiecare verificat, nu presupus:

1. **H0 nerespinsă în TOATE cele trei regimuri, la a doua construcție consecutivă.** Nu e un rezultat marginal ratat — corecția, cel mai bun regim, are p=0,288, la ani-lumină de orice prag convențional. Bear și bull sunt și mai departe (0,637/0,861).

2. **Costul fix domină structural edge-ul scalat pe ATR, mai ales unde ATR e mic.** Cost=0,20$ constant peste tot; edge brut variază enorm (0,050$ în bull, unde ATR median la supraviețuitori e cel mai mic — 1,27, față de 1,98 în bear și 2,19 în corecție). Bull nu are nicio șansă structurală: 0,050$ brut nu poate niciodată acoperi 0,20$ cost fix, indiferent de câte iterații de reparametrizare am încerca pe SL/TP — problema nu e unde sunt pragurile SL/TP, e că mărimea absolută a mișcării așteptate în dolari, la acest nivel de ATR, e prea mică față de un cost care nu scalează cu ea.

3. **Chiar și corecția — singurul regim cu net pozitiv — nu atinge pragul convenției proprii a acestui proiect.** Podeaua de eligibilitate (0,60×ATR) a fost ea însăși derivată din regula deja stabilită "3×cost" (3×0,20/1,0=0,60) — aplicată la RISC (R), nu la EDGE. Aplicând ACEEAȘI regulă la edge brut (nu doar la risc): 3×cost=0,60$. Corecția (0,471$) nu atinge nici măcar acest prag propriu — e la ~2,35× cost, nu 3×. **Dacă am aplica consecvent aceeași marjă de siguranță pe care o cerem deja de la risc, și la edge, NICIUN regim n-ar trece — inclusiv cel mai bun.**

4. **Familia (2, OBDZ-001+OBDZ-002) e epuizată.** Amândouă informate de aceeași descoperire, amândouă testate cu rigoare egală, amândouă respinse la propria lor parametrizare declarată. O a treia încercare (OBDZ-003) ar necesita o familie nouă (3), o justificare nouă, independentă de "poate cu alte cifre merge" — exact tiparul "ghici-și-verifică" pe care acest proiect l-a respins explicit de mai multe ori (Mandatul 3.26: "recomandă o cale de diagnostic-întâi, nu ghici-și-verifică").

## Ce NU propun ca "singura modificare" — și de ce, explicit, nu doar prin tăcere

**Tentația vizibilă în date: împărțirea pe polaritate arată o combinație care ar "câștiga" — demand în bear (+0,167) + supply în corecție (+0,538), excluzând supply-bear (-0,311) și demand-corecție (+0,109, mai slab).** NU propun asta. Motivul: selectarea POST-HOC a combinației polaritate×regim care arată cel mai bine DUPĂ ce am văzut rezultatele e exact capcana de selecție împotriva căreia întreaga disciplină de familie fixată din acest proiect există — genul de "1972 de ipoteze" care a colapsat pragul de semnificație la 0,000032. O combinație aleasă pentru că arată bine acum nu e o "modificare derivată" — e supra-potrivire pe zgomot, indiferent cât de tentantă arată aritmetica. **Stratificarea pe polaritate rămâne ce a fost dintotdeauna: un diagnostic obligatoriu de raportat, nu un meniu din care se alege după fapt.**

**Nu propun nici recalibrarea costului** — cifra de 0,20$ a fost verificată direct la sursă (specificația instrumentului) de mai multe ori în acest proiect (Mandatul 3.22) și nu există niciun motiv NOU, apărut din acest rezultat, s-o repunem în discuție; a face asta acum ar fi o rundă de măsurare, nu o derivare.

**Nu propun mărirea podelei de ATR la o valoare specifică** — ar necesita o distribuție nouă (edge brut pe intervale de ATR), o măsurătoare pe care mandatul o interzice explicit acum.

**Concluzie: nu există o singură modificare derivabilă din datele deja în mână, care să nu fie fie o rundă de măsurare deghizată, fie o potrivire post-hoc pe zgomot. De aceea răspunsul e închiderea, nu o a treia încercare.**

---

## Ce rămâne valid, explicit, necontrazis de această închidere

- **Semnalul MFE zonă-vs-retragere** (Mandatul 3.35, agregat n=654, semnificativ statistic pe medie ȘI mediană, robust la două metode de bootstrap) — rămâne o constatare descriptivă validă despre comportamentul prețului. Nu a fost respins — a fost doar demonstrat, de două ori, că nu se traduce direct într-o construcție comercială profitabilă la acest orizont/cost.
- **Contractul de confluență (Decizia 3, v2.7.10)** — rămâne corect, folosit fidel în ambele runde.
- **Toată infrastructura** (12 primitive, oracolul WP-5', datele de 15 ani) — rămâne validă, reutilizabilă pentru orice ipoteză VIITOARE, independentă, pre-înregistrată separat — nu pentru o a treia iterație pe ACEEAȘI idee.

## Ce se închide, mecanic

- Linia OBDZ (OBDZ-001, OBDZ-002) — CLOSED, familia 2 epuizată.
- Cele douăsprezece tipuri de zone, palnia, Session Open — rămân ÎN AȘTEPTARE, dar depindeau de OBDZ ca dovadă de concept pentru ideea compusă zonă×OB — acea dovadă de concept nu s-a materializat comercial. Orice continuare pe aceste teme ar necesita o justificare NOUĂ, nu moștenirea automată a motivației OBDZ.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.24 (commit `a18bd02`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
