# STATISTICIAN — CITIREA GRILEI PE MĂSURĂTOAREA CORECTATĂ (OBDZ, 3 BRAȚE)

**Document ID:** STAT-OBDZ-THREE-ARM-GRID-READING-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit integral `code/obdz_three_arm_windows.py` (comitul `d869177`) — corespunde exact specificației mele (`v2.7.15`, `f705956`). `mypy --strict` curat. **Rulat direct** — toate cifrele citate reproduse exact: potrivire A↔C 275/223/156, zero nepotrivite, zero pullback nedefinit; MFE mediană la `[+2,+5]`: A=0,85/1,06/1,11, B=0,80/0,80/0,90, C=0,75/0,77/0,76 (bear/bull/corecție); agregat A=0,97/B=0,81/C=0,76; `[+2,+10]`: A=1,39, B=C=1,16; asimetria MAE/raport pe bear (A MAE=1,09 vs C=0,84, raport A=0,43 vs C=0,68) — toate confirmate exact.

**Verificare suplimentară, nu doar acceptarea premisei CEO:** am verificat direct polaritatea (long/demand vs short/supply) a celor 275/223/156 declanșatoare per regim, printr-un script temporar (necomis). **Rezultat: premisa CEO ("bear=100% supply, bull/corecție=100% demand") NU se confirmă** — toate cele trei regimuri sunt de fapt MIXTE: bear 57,8% demand/42,2% supply; bull 54,7% demand/45,3% supply; corecție 62,2% demand/37,8% supply. Aceasta rezolvă direct întrebarea de la Sarcina 2 — vezi acolo.

---

# SARCINA 1 — citirea grilei, plus întrebarea de domeniu asupra testului

## Citirea literală, pe pragurile deja pre-înregistrate

La fereastra principală `[+2,+5]`, aplicând pragurile mele proprii (15%/25%): **agregatul (A=0,97 vs C=0,76, +28%) și DOUĂ din trei regimuri (bull +38%, corecție +46%) depășesc clar pragul de 25% „zona adaugă peste retragere".** Bear (+13%) e SUB acel prag, deși în aceeași direcție. La `[+2,+10]`, agregatul (A=1,39 vs C=1,16, +19,8%) nu mai atinge clar 25% — efectul persistă în direcție, dar se atenuează.

**Nu e nici tiparul „închis definitiv" (nu e nul peste tot), nici perfect unanim (bear e mai slab). E un tipar consistent ca direcție, cu magnitudine variabilă pe regim — exact genul de rezultat pentru care am scris pragul de 25%, nu un caz clar de manual.**

## Testul — ESTE o întrebare de domeniu nouă, confirm, și block_bootstrap@v1 NU se aplică direct

**De acord: nu am mai pus întrebarea asta.** `block_bootstrap@v1` a fost calibrat pentru un obiect specific: o SINGURĂ serie de rezultate (`net_R` per tranzacție) cu dependență de suprapunere generată de ferestre de măsurare FIXE care împart șocuri viitoare comune — testul e „media seriei diferă de zero". **Comparația A versus C e alt obiect: o comparație PERECHE-CU-PERECHE** (fiecare declanșator A e potrivit 1-la-1 cu exact un partener C, prin construcția de potrivire pe `pullback_depth`) — nu o singură serie testată contra zero.

**Asta simplifică, nu complică:** potrivirea 1-la-1 înseamnă că întrebarea corectă e pe **diferența per-pereche** `d_i = MFE_A_i − MFE_C_i`, nu pe cele două distribuții separat. Un test PERECHE (Wilcoxon signed-rank, sau bootstrap pe diferența medie/mediană) e mai puternic și mai potrivit decât orice comparație ne-perecheată — controlează automat pentru orice factor comun perechii (același regim, aproximativ aceeași perioadă).

**Dar rămâne o dependență reziduală de verificat:** declanșatoarele A apropiate în timp ar putea fi corelate între ele (condiții de piață comune), deci PERECHILE însele ar putea fi corelate secvențial — analog, nu identic, cu problema de suprapunere de la `net_R`. **Recomand: se reutilizează MECANICA de reeșantionare în blocuri a lui `block_bootstrap` (codul, nu calibrarea) aplicată pe seria de DIFERENȚE PERECHE `d_i`, ordonate temporal** (nu pe `net_R` — un obiect nou, o calibrare nouă) — rulată ALĂTURI de un bootstrap i.i.d. simplu (fără blocuri) ca linie de bază. **Dacă cele două converg apropiat, tiparul e robust la incertitudinea de dependență; dacă diverg semnificativ, aceea e informația relevantă** (aceeași disciplină ca la „r_variance_note" de la LM-001 — un instrument reutilizat, dar recalibrat pentru un obiect nou, nu presupus valid automat).

**Nu am rulat acest test.** Rezultatul de azi (+28%/+38%/+46% pe mediane) **e o OBSERVAȚIE, nu o dovadă**, exact cum ai anticipat la punctul 4 — necesită testul perechi (i.i.d. + blocuri, comparate) înainte de a fi tratat ca fapt stabilit. **Acesta rămâne diagnostic, nu testul formal al ipotezei** — nu consumă familia de corecție (la fel ca Măsurătoarea A' și tot ce a urmat), doar decide dacă merită specificată o ipoteză reală.

---

# SARCINA 2 — asimetria: REZOLVATĂ direct din date, fără a testa contra-trend

**Premisa ta ("bear=supply, bull/corecție=demand") nu se confirmă la verificare** — toate cele trei regimuri conțin AMBELE polarități în proporții substanțiale (37-46% clasa minoritară în fiecare). **Asta înseamnă că distincția polaritate-vs-regim SE POATE face direct pe datele existente, fără nicio colectare contra-trend** — exact opțiunea pe care ai lăsat-o deschisă ca posibilă, acum confirmată disponibilă.

**Specific: se re-stratifică ACELEAȘI evenimente A/C deja măsurate (nu o măsurătoare nouă de la zero) după POLARITATE (demand vs supply), agregat PESTE toate cele trei regimuri** (nu per regim) — la ferestrele `[+2,+5]`/`[+2,+10]`, MAE/MFE/raport, separat demand vs supply. **Citire:** dacă asimetria (raport prost pentru un grup, bun pentru altul) urmează POLARITATEA indiferent de regim → efect de polaritate, ipoteza următoare se restrânge la demand. Dacă asimetria urmează REGIMUL indiferent de polaritate (ex. toate tranzacțiile din bear ies prost, demand sau supply deopotrivă) → efect de regim/preț, se păstrează ambele. **Dacă niciun tipar clar nu apare** (asimetria nu urmează nici polaritatea, nici regimul curat) → rămâne deschis, se raportează onest, nu se forțează o concluzie.

---

# SARCINA 3 — ordinea, dacă testul perechi confirmă

**Nu formulez încă OBDZ-002 complet — exact cum ai cerut.** Ordinea:

1. **Testul perechi (i.i.d. + blocuri) pe `d_i=MFE_A−MFE_C`**, la `[+2,+5]`/`[+2,+10]`, agregat și per regim — GATEAZĂ tot ce urmează. Dacă nu arată o diferență robustă la zero, linia se reevaluează, nu se specifică o ipoteză nouă.
2. **Re-stratificarea pe polaritate** (Sarcina 2) — poate rula ÎN PARALEL cu #1 (întrebare diferită, aceleași date deja colectate) — decide scopul (demand-only vs ambele) al oricărei ipoteze următoare.
3. **DOAR dacă #1 confirmă:** SL/TP derivate din distribuția MAE la `[+1,+4]` (acum ai cifrele reale: mediană 0,88-1,09×ATR — mult mai strâns și mai informativ decât ancora veche de 0,7 SAU decât cifra oarbă de 4,4 de pe 92 de bare).
4. **Confirmarea (Varianta 3):** rămâne de măsurat SEPARAT — MAE/MFE de la bara de confirmare (nu de la atingerea brută `t`), nu presupun că se transferă automat cifrele de mai sus.
5. **Numărătoarea H1/H4:** rămâne REȚINUTĂ, neschimbat — devine relevantă abia după ce 1-4 arată că mecanismul de bază merită construit.

---

# RĂSPUNS DIRECT, CERUT EXPLICIT LA PUNCTUL 4

**Grila NU se citește nici clar pozitiv (fără test), nici negativ, nici amestecat în sens de semne contradictorii.** Se citește **consistent ca direcție (zona depășește retragerea în toate trei regimurile), cu magnitudine variabilă (13% la 46%) care NU a fost încă testată statistic.** E o observație descriptivă solidă, nu o dovadă — exact distincția pe care ai cerut-o. Nu autorizez formularea OBDZ-002 până nu rulează testul perechi de la Sarcina 1.

---

## Ce rămâne neatins

Numărătoarea H1/H4 rămâne REȚINUTĂ de VE, neautorizată. Sigilatul intact. Nimic executat în acest document dincolo de re-verificarea independentă a rezultatului deja livrat, plus verificarea suplimentară de polaritate.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.16 (commit `37b48ee`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
