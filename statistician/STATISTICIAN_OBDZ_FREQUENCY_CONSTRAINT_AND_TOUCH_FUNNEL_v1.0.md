# STATISTICIAN — CONSTRÂNGEREA DE FRECVENȚĂ ȘI PÂLNIA ÎN ATINGERI (OBDZ, ADĂUGARE)

**Document ID:** STAT-OBDZ-FREQUENCY-CONSTRAINT-TOUCH-FUNNEL-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** confirmat direct duratele blocurilor de descoperire în manifest — bear 794,0 zile (2,174 ani), bull 816,1 zile (2,234 ani), corecție 390,2 zile (1,068 ani), total 2000,4 zile (5,477 ani). Recalculat frecvențele: bear 261/2,174=120,1/an=2,31/săpt; bull 194/2,234=86,8/an=1,67/săpt; corecție 154/1,068=144,2/an=2,77/săpt (ușor sub cei „3,0" citați — durata reală e 1,068 ani, nu exact 1,0 — o precizare mică, nu o corectare substanțială); agregat 609/5,477=111,2/an=2,14/săpt. **Cifrele tale se confirmă, cu o rafinare minoră la corecție (2,77, nu 3,0).** Concluzia rămâne neschimbată: aproximativ jumătate din ținta de 5/săptămână.

**Confirmată auto-corecția ta despre pâlnie — verificat aritmetic, nu doar acceptat:** treapta 1 (90.306 = 35.454+37.707+17.145) e în BARE; treapta 2 (5.560 = 2.275+2.107+1.178) e în ZONE; treapta 3 (654 = 275+223+156) e în DECLANȘATOARE (evenimente de atingere OB, nu zone). **Corect: nu se poate calcula o rată de supraviețuire între unități diferite** — o zonă poate fi atinsă de zero, o dată sau de zece ori, deci raportul 654/5.560 nu spune nimic despre „câte zone supraviețuiesc". Nu era eticheta mea — nu am scris niciodată acea propoziție (verificat direct în toate documentele proprii) — dar confirm corecția ta ca fiind exactă.

---

## Pâlnia în ATINGERI, într-o singură unitate consistentă — SPECIFICATĂ ACUM, cerută de mine

**Nu relaxez nimic — asta e pură numărătoare descriptivă, read-only, care nu atinge nicio regulă de intrare/ieșire.** Se poate rula ÎN PARALEL cu testul pereche de la mandatul anterior (nu se blochează reciproc), tocmai pentru că, până se citește verdictul, să existe deja datele care spun UNDE se întâmplă colapsul.

**Toate cele trei trepte, în ACEEAȘI unitate — nivel de ZONĂ, nu bară, nu eveniment:**

```
T1  câte DemandZone (din cele 5.560/2.275+2.107+1.178) sunt ATINSE cel puțin o dată
    (prețul re-intră în [zone_lower, zone_upper] la orice moment după formare, în ACELAȘI bloc)
    -> raportat ca număr de ZONE (nu evenimente de atingere), la PRIMA atingere per zonă

T2  dintre cele atinse (T1), câte au un OB nemitigat cross-candle suprapus la momentul primei atingeri
    (exact mecanica Deciziei 3, deja ratificată — polaritate identică, formare diferită, ≤460 bare,
    suprapunere de interval)

T3  dintre acelea (T2), câte au bias (H1+H4) aliniat la bara atingerii
```

**Raportat separat pe polaritate (demand vs supply)**, nu doar pe regim — se leagă direct de re-stratificarea de polaritate deja specificată la mandatul anterior, și de asimetria semnalată în context (bear/supply cu raport MFE/MAE mai prost).

**De ce contează unde e colapsul, nu doar cât de mare e:** dacă majoritatea zonelor nu sunt NICIODATĂ atinse (colaps la T1), problema e de DISPONIBILITATE — pârghia potrivită e alt tip de zonă sau o construcție diferită de zonă, nu relaxarea condiției compuse. Dacă zonele sunt atinse des dar rar au OB suprapus (colaps la T2), confluența însăși e rară — pârghia potrivită ar putea fi alte tipuri de zonă (Pârghia 2) sau reconsiderarea ferestrei de suprapunere. Dacă atingerea+confluența sunt frecvente dar bias-ul elimină majoritatea (colaps la T3), Pârghia 1 (H4 singur) devine cea mai relevantă de testat prima.

---

## Cele trei pârghii — NU se aleg acum, se SPECIFICĂ ce ar trebui măsurat pentru fiecare

**Niciuna nu se rulează înainte de verdict.** Dacă grila (testul pereche, mandatul anterior) iese zgomot, nicio pârghie nu contează — de acord integral, frecvența nu salvează un semnal absent. Specific aici DOAR metodologia de măsurare pentru fiecare pârghie, ca să fie gata de rulat imediat ce verdictul confirmă semnal — nu aleg încă niciuna.

**Pârghia 1 — bias doar pe H4:** se redefinește condiția de bias (doar `h4_trend_up`, fără cerința H1) și se re-rulează ACEEAȘI construcție de declanșator compus (zonă cross-candle × OB nemitigat), apoi ACELEAȘI trei brațe (A/B/C) pe ACELEAȘI ferestre principale (`[+2,+5]`/`[+2,+10]`). **Întrebarea nu e „crește frecvența" (aproape sigur da) — e „supraviețuiește efectul de +28%".** Dacă efectul se păstrează aproximativ, alinierea dublă era doar un filtru de frecvență. Dacă efectul se subțiază sau dispare, alinierea H1 era parte din MECANISM (posibil filtrând exact barele unde H4 e adevărat dar tendința locală deja se întoarce) — nu doar o rată de eșantionare.

**Pârghia 2 — tipuri de zonă suplimentare (FVG, Breaker, PDH/PDL):** **fiecare tip se măsoară SEPARAT, nu în grămadă**, exact cum ai cerut — pentru fiecare, se construiește propriul declanșator compus (zonă cross-candle × [tip]-nemitigat, aceeași logică de suprapunere, adaptată la propria stare de „nemitigat" a fiecărei primitive), apoi ACELEAȘI trei brațe pe ACELEAȘI ferestre. **Diluează sau păstrează?** — necunoscut fără măsurătoare, per tip; combinarea (uniune de tipuri calificate) e o întrebare SEPARATĂ, ulterioară, condiționată de rezultatele individuale, nu presupusă acum.

**Pârghia 3 — zone pe M15 în loc de HTF:** semnalez explicit — asta **inversează o alegere de proiectare deliberată**, nu e o pârghie neutră printre celelalte două. Mandatul original a cerut EXPLICIT zone H1/H4 cu intrare M15, tocmai pentru zone mai mari/mai rare, mai de încredere. Revenirea la zone M15-native ar fi un pas înapoi spre construcția OBDZ-001 originală (deja respinsă la parametrizarea declarată) — nu o simplă relaxare de frecvență. Dacă se ia în calcul, trebuie tratată ca o schimbare de fond a ipotezei, nu ca o ajustare marginală.

---

## Răspuns direct, cerut explicit

**Frecvența NU se decide acum.** Rămâne exact unde ai pus-o: „nu se discută până nu se citește grila". Pâlnia de atingeri (mai sus) se cere ACUM, în paralel cu testul pereche, pentru că e read-only și nu relaxează nimic. Cele trei pârghii rămân SPECIFICATE, nu alese — gata de rulat imediat ce verdictul iese pozitiv, fiecare cu propria măsurătoare, nu presupuse valide.

**Dacă, după măsurătorile de mai sus, niciuna nu crește frecvența fără să erodeze efectul — asta e un răspuns legitim, nu un eșec.** 2,2/săptămână (sau chiar mai puțin, dacă pârghiile nu ajută) rămâne un edge, dacă testul pereche îl confirmă ca atare — o strategie discreționară rară nu e mai puțin validă decât una frecventă, doar mai puțin convenabilă operațional.

---

## Notă asupra asimetriei din context — deja acoperită, nu o întrebare nouă

Asimetria semnalată (bear/supply cu raport MFE/MAE 0,43 vs 0,68 la retragere, MAE cu 30% mai mare) e exact motivul pentru care re-stratificarea pe polaritate (specificată la mandatul anterior) rămâne necesară — pâlnia de atingeri de mai sus, raportată și ea pe polaritate, va ajuta la aceeași citire. Nu e o întrebare separată — se rezolvă în același pas cu testul pereche și re-stratificarea deja cerute.

---

**Nimic relaxat, nimic rulat pe mecanismul de intrare/ieșire în acest document — doar pâlnia de atingeri cerută, read-only. Sigilatul intact. Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.17 (commit `81eeb7b`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
