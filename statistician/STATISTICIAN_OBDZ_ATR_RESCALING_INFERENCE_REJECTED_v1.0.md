# STATISTICIAN — REESCALAREA LA ATR-UL ACTUAL: INFERENȚĂ NEPERMISĂ, NU JUSTIFICARE INDEPENDENTĂ

**Document ID:** STAT-OBDZ-ATR-RESCALING-INFERENCE-REJECTED-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă, fără nicio măsurătoare nouă — doar citirea codului deja existent:** citit direct `code/partial_exit.py` (liniile 35, 58, 73) — confirmă mecanismul exact pe care se sprijină argumentul CTO: `R = abs(entry_price − sl_price)` (risc în DOLARI, fără multiplicator de lot — o poziție de 1 unitate implicit, prețul aurului fiind cotat direct în $), iar `net_R = 0,75×(r1 − cost/R) + 0,25×(r2 − cost/R)`, cu `cost=0,20$` FIX. **Aritmetica de bază a argumentului e corectă: costul-în-unități-de-R (`cost/R`) SCADE mecanic atunci când R (proporțional cu ATR) crește.** Verificată și aritmetica cifrelor citate: factor ATR = 7,40/1,98=3,74 (bear), 7,40/1,27=5,83 (bull), 7,40/2,19=3,38 (corecție) — confirmă intervalul "3,4x-5,8x"; edge scalat = 0,166×3,74=0,620; 0,050×5,83=0,292; 0,471×3,38=1,592 — toate reproduse.

---

## RĂSPUNS DIRECT: NU. Nu e o justificare independentă. E o inferență nepermisă.

Mecanismul pe care se sprijină (cost fix în $, R proporțional cu ATR, deci cost-în-R scade la ATR mare) e real și verificat direct în cod — asta nu se contestă. Ce se contestă e SALTUL de la acest mecanism corect la concluzia "deci edge-ul devine profitabil azi." Sunt trei motive independente, oricare suficient singur:

### Motivul 1 — testul statistic n-a stabilit că există un edge de rescalat

**H0 (mean(net_R)≤0) NU a fost respinsă în NICIUN regim** (p=0,637/0,861/0,288, Mandatul 3.38). Cifra de edge_brut pe care CTO o rescalează (0,166/0,050/0,471$) e un ESTIMATOR PUNCTUAL dintr-o distribuție pe care propriul nostru test n-a putut s-o distingă de zero (sau de negativ, în cazul bull). **Rescalarea unui număr nedemonstrat prin factorul de ATR nu produce dovadă nouă — produce ACELAȘI număr nedemonstrat, umflat algebric.** Dacă adevărata medie de populație a lui `net_R`/`edge_brut_R` e de fapt ≤0 (exact ipoteza pe care n-am putut s-o respingem), niciun factor de scalare n-o transformă în pozitivă — o face doar mai mare în dolari, la fel de aproape de zero (sau negativă) în termeni de R.

### Motivul 2 — datele PE CARE SE SPRIJINĂ argumentul deja resping premisa lui centrală

Argumentul presupune implicit că edge-ul în unități de R e o CONSTANTĂ STRUCTURALĂ, portabilă între regimuri de volatilitate — doar costul (în R) se schimbă cu ATR. **Dar chiar cele trei regimuri de descoperire deja CONTRAZIC portabilitatea asta:** `expectancy_R` = -0,0134 (bear) / **-0,0776 (bull)** / +0,0677 (corecție). Bull are cel mai NEGATIV edge în R, deși are cel mai MIC ATR median (1,27) dintre cele trei — dacă edge-ul ar fi determinat de nivelul de ATR (cum implică logica de rescalare), bull ar trebui să arate similar cu celelalte, ajustat doar de cost. Nu arată. **Edge-ul în R e determinat de condiții specifice regimului (bias, structură, volum), nu de nivelul absolut al ATR-ului — nu există un "edge de R" unic, stabil, de transplantat pe "azi."**

### Motivul 3 — extrapolare mult dincolo de domeniul testat, pe o presupunere suplimentară nesigură

Factorul de scalare (3,4x-5,8x) proiectează dincolo de ÎNTREGUL interval de ATR observat vreodată în datele de descoperire (1,27-2,19) — nu o interpolare, o extrapolare de câteva ori peste cel mai mare ATR văzut, pe o piață (aur ~4050$, față de 1000-2000$ istoric) care a trecut prin un deceniu+ de schimbări structurale (lichiditate, compoziție participanți, activitate algoritmică). **Argumentul presupune, suplimentar, că exact costul rămâne fix la 0,20$ în timp ce prețul/ATR cresc de 3-6 ori** — o presupunere cel puțin la fel de probabil greșită ca fiind corectă (spread-urile tind să se lărgească în perioade de volatilitate mai mare, empiric cunoscut, neverificat aici) și imposibil de confirmat fără date noi. **Exact genul de extrapolare dincolo de domeniul validat pe care acest proiect l-a respins consecvent** (AR(1) `INVALIDATED_FOR_THIS_SCALE`, diagnosticul SL/TP larg degenerat în măsurare de drift) — nu se schimbă regula acum doar pentru că rezultatul ar fi convenabil.

---

## Dacă ipoteza CTO ar fi validă condiționat — răspunsul rămâne același, motivul se schimbă

CTO a structurat corect logica CONDIȚIONALĂ ("dacă e validă, respingerea e a perioadei, nu a strategiei, și atunci..."). Dar condiționalul nu se împlinește — Motivul 1 e suficient singur să oprească lanțul: **nu putem spune "e respinsă doar perioada" atâta timp cât n-am demonstrat nici măcar că STRATEGIA are un edge real în vreo perioadă.** Întrebarea despre un prag de ATR derivabil din costul fix ar rezolva o problemă diferită (unde anume costul domină structural edge-ul), presupunând deja că edge-ul e real — presupunere pe care n-o avem dreptul s-o facem încă. **Nu merg mai departe pe acea întrebare — ar însemna să construiesc pe o premisă deja respinsă la Motivul 1.**

## Ce rămâne, totuși, un fir legitim — dar NU azi, NU fără date noi

Mecanismul verificat (cost fix, edge scalat cu ATR) e o observație REALĂ despre construcție, valabilă pentru orice ipoteză VIITOARE, testată direct pe date ACTUALE (nu re-scalată retroactiv pe date vechi). Dacă CEO dorește să investigheze acest lucru serios: singura cale legitimă e o ipoteză NOUĂ, cu familie proprie, testată pe date din perioada curentă (spread/cost verificat la sursă pentru condițiile de azi, nu presupus neschimbat), pre-înregistrată separat — nu o rescalare aritmetică a unui rezultat deja respins. **Asta ar necesita date și măsurători noi — exact ce acest mandat exclude explicit acum.**

---

## Verdict, fără ambiguitate

**NU e o justificare independentă pentru familia 3. E o inferență nepermisă — combină un mecanism real (verificat) cu un salt nejustificat peste o ipoteză nedemonstrată statistic, peste o portabilitate deja contrazisă de propriile date, și peste o extrapolare de piață neverificabilă.** Verdictul de la Mandatul 3.38 rămâne neschimbat: **linia OBDZ e închisă.**

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
