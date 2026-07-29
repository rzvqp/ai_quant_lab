# STATISTICIAN — CORECȚIA CONSTANTEI DE COST, ORDER BLOCK, DEMANDZONE, IPOTEZA NOUĂ

**Document ID:** STAT-COST-CONSTANT-OB-DEMANDZONE-HYPOTHESIS-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

**Verificare de sursă:** confirmat direct `code/mstrat.py:10` (`TICK=0.1`), `:45` (`cost=(spread_ticks+slip_ticks)*TICK`), `:53` (`min_exec=max(2*spread_ticks*TICK, 5*TICK, 0.10*atr)`), și **CRITIC, linia care lipsea din citarea mea anterioară**: `:63` — `Rs.append((dirn*(ex-entry)-2*cost)/risk)`. Confirmat `DemandZone`/`is_mitigated`: zero apariții în `code/order_flow.py`; formarea OB rămâne `NotImplementedError`, docstring identic citat de tine. Confirmat `h1_trend_up`/`h4_trend_up` există în `code/mtf.py` (din `ema20>ema50`).

---

# PARTEA 1 — CONSTANTA DE COST, CORECTATĂ LA SURSĂ

## Valoarea corectă, derivată nu aleasă

**TICK = 0,01 dolari.** Sursa: specificația instrumentului, nu codul — cotare pe 2 zecimale, confirmat direct de contul tău real (`4033,84/4033,89`). Factor de eroare confirmat: **10×**.

**Descoperire critică, prin citirea liniei 63 (nu doar liniile 10/45/53):** `Rs.append((dirn*(ex-entry)-2*cost)/risk)` — codul aplică **`2*cost`**, nu `cost`. Deci costul round-trip REAL aplicat de motor nu e `cost` (variabila), ci `2×cost = 2×(spread_ticks+slip_ticks)×TICK`. La valorile vechi (spread_ticks=slip_ticks=1, TICK=0,10): `2×2×0,10=0,40` — cifra pe care am purtat-o corect ca „0,40" toată sesiunea. **Dar propria ta aritmetică din ordin — „cost=(spread_ticks+slip_ticks)×TICK = 2×0,1 = 0,40" — are ea însăși o eroare**: `2×0,1=0,20`, nu `0,40`. Cifra finală pe care ai folosit-o (0,40) e corectă, dar derivarea scrisă sare peste dublarea explicită din linia 63. A doua verificare-la-sursă din acest document, nu doar prima.

**Costul round-trip corectat, derivat din contul tău real:** spread tipic 5-15 ticks — folosesc **mediana intervalului (10 ticks)**, nu exemplul cel mai strâns (5 ticks, care e cel mai bun caz observat, nu tipic) — motivul: convenția deja aplicată toată sesiunea, alegerea conservatoare când există incertitudine, nu optimistă. Slippage = spread (convenția ta explicită). Cu structura EXISTENTĂ a codului (`2×(spread_ticks+slip_ticks)×TICK`) și **spread_ticks = slip_ticks = 5** (fiecare reprezentând jumătate din spread-ul complet de 10 ticks, păstrând convenția „per parte" deja din cod): 

```
cost_round_trip = 2 × (5+5) × 0,01 = 0,20 dolari
```

**Nu, slip_ticks=1 nu mai are sens.** La TICK corect, slip_ticks=1 ar însemna un slip de doar 1 cent per parte — mult sub orice slippage realist pe un cont OTC/CFD. Valoarea corectă e **5**, egală cu spread_ticks, exact convenția ta.

## De ce NU e o eroare de 10× pe R — auto-corecție, nu presupunere

Am verificat mecanic: `R_dolari = (deplasare_pips+2)×TICK`. Dar `deplasare_pips` însuși = `distanță_dolari/TICK` — deci **`R_dolari = distanță_dolari + 2×TICK`**. Termenul `distanță_dolari` (geometria reală, în dolari) e **complet independent de TICK** — nu se schimbă. DOAR bufferul de „2 pips" se schimbă în dolari: de la `2×0,10=0,20$` la `2×0,01=0,02$` — o corecție MICĂ, nu o explozie de 10×. **R-ul propriu-zis al fiecărei tranzacții scade cu o cantitate mică și fixă (0,18$), nu se prăbușește de 10 ori.**

## Ce se prăbușește, exhaustiv, pe DOUĂ canale distincte

**Canalul A — costul (0,40→0,20, un factor de 2×):**
- Toate verdictele „sub cost": E001/E002/E004 ca NEGATIVE_EXPECTANCY_UNDER_COST, SMC_S1 ca REJECTED_NET_OF_COST → CLOSED_DEFINITIVELY (rulat deja, pe costul greșit — **REDESCHIS, prioritate maximă**, un verdict „definitiv" a fost emis pe o constantă contaminată), cele 7 familii (S2/S3/S7/S11/S13/S16/S17) sub pragul de 40 de cenți.
- Pragurile de break-even `w*=(1+cost/S)/(RR+1)` — 0,440/0,3667 la stop 4,00; 0,550/0,367 la §9.4 — **REDESCHIS**.
- Pragul Liquidity Void: `3×0,40=1,20$` → **`3×0,20=0,60$`** — **REDESCHIS**.
- D2, componenta `2*spread_ticks*TICK` a podelei de execuție — afectată și de acest canal (spread_ticks) și de canalul B (TICK).

**Canalul B — TICK ca divizor de pips (0,10→0,01, un factor de 10×):**
- Eticheta în PIPS a oricărei distanțe geometrice — distanța reală în dolari NU se schimbă, dar numărul de „pips" raportat pentru ACEEAȘI distanță devine 10× mai mare. **Orice cifră în pips citată până acum trebuie relabelată sau reprodusă cu TICK corect, nu doar recalculată aritmetic pe hârtie.**
- D2, componenta `5*TICK` a podelei — de la 0,50$ la 0,05$ — **REDESCHIS, prioritate înaltă**: cele 58.225 tranzacții INVALID, cele 7.371 analizate, cele 47 respinse au fost măsurate contra unei podele de zece ori prea mari. Care componentă din `max(2*spread_ticks*TICK, 5*TICK, 0,10*atr)` DOMINĂ se poate schimba complet la scara corectă (la ATR-uri istorice mici, `0,10*atr` ar putea deveni dominantă, unde înainte `5*TICK` domina orbește).

**Canalul A+B combinate (compus, cel mai afectat):**
- **Filtrul `[10,1;65,0)` pips (LM-001/SMC_S1-S20):** podeaua era derivată din cost (canal A) ȘI exprimată în pips (canal B) — **AMBELE greșite simultan**. Recalculat corect: podea nouă = `(3×0,20 − 2×0,01)/0,01 = 58` pips (în dolari reali: $0,58, față de vechiul $1,00 implicit — o ÎNGUSTARE reală modestă a podelei, nu o explozie). Plafonul (65 pips, din percentila empirică p90 — NU derivat din cost) reprezintă o distanță reală de `65×0,10=6,50$` — **relabelat** la TICK corect: `6,50/0,01=650` pips (aceeași distanță reală, altă etichetă). **Rezultat: banda corectă e [58, 650) pips, NU [10,1;65,0)** — o bandă mult mai largă în etichetă, dar geometric aproape identică în dolari cu cea veche, doar corect exprimată. **REDESCHIS — filtrul trebuie re-derivat și, ideal, re-rulat pe geometrie brută (nu doar relabelare manuală a rapoartelor vechi, ca să nu se strecoare o eroare ascunsă).**

## Ce NU depinde de cost — rămâne neschimbat, verificat explicit

- **Oracolul WP-5' (block_bootstrap@v1 VALIDATED pentru mecanismul de suprapunere)** — despre STRUCTURA de dependență/autocorelație, zero constante de dolari implicate. **NESCHIMBAT.**
- Deciziile D1-D7 (market_structure), bug-ul de re-armare și fix-ul lui — geometrie pură de preț, fără cost. **NESCHIMBAT.**
- Regula de graniță semi-deschisă `[start,end)`, convenția de sesiuni (asia/london/ny/late), orizonturile derivate din durata sesiunii sau din zi/săptămână empirică (20/32/92/460 bare) — toate bazate pe TIMP, nu preț. **NESCHIMBATE.**
- Regula de îngheț D-BPR (toleranțe 0,00/0,10/0,25) — bazată pe granularitatea de preț (2 zecimale = 0,01$), **de fapt ÎNTĂRITĂ, nu contrazisă**, de descoperirea TICK=0,01 din acest document.
- Reclasificarea S18, recompunerea Range/MTF-Trend (S12/S9/S20), criteriul de expansiune OB (reutilizat din E010, bazat pe ATR nu pe cost) — structurale, fără cost. **NESCHIMBATE.**
- Controlul E004 (fill 0,7148 vs 0,85, z=8,8) — o proporție, nu un cost. **NESCHIMBAT.**
- Regula permanentă asupra heteroschedasticității R (Mandatul anterior) — despre proprietăți statistice, nu valori de dolari. **NESCHIMBATĂ.**

## Ordinea de re-rulare

1. **Confirmă constantele** (acest document) — TICK=0,01, cost_round_trip=0,20, spread_ticks=slip_ticks=5.
2. **D2 — re-diagnostichează podeaua de execuție** la constantele corecte, pe TOATĂ gama istorică de ATR (componenta dominantă se poate schimba).
3. **Re-rulează geometria brută** (auditul de deplasare, nu doar relabelare manuală) cu TICK corect → noul filtru `[58,650)` (sau orice rezultă din re-rulare, nu din calculul meu de mai sus, care e orientativ).
4. **Re-rulează SMC_S1 și cele 7 familii** cu costul corect (0,20) — inclusiv verdictul CLOSED_DEFINITIVELY, care se REDESCHIDE explicit.
5. **Abia apoi** — Măsurătoarea A / harta de sensibilitate (SMC_S1_v2), rămasă blocată de la mandatul anterior, acum ȘI de costul greșit.

**Regula propusă de tine, ratificată explicit:** orice constantă de model care intră într-o derivare se verifică la sursă — specificația instrumentului/contul real, nu codul care o folosește. Adaug: **inclusiv liniile de cod ADIACENTE celei citate** (linia 63, nu doar 10/45/53) — o constantă poate fi corectă izolat și totuși greșit APLICATĂ o linie mai jos.

---

# PARTEA 2 — CRITERIUL DE FORMARE ORDER BLOCK

**Verificat, confirmat exact ca tine:** `DemandZone`/`is_mitigated` nu există în cod; formarea OB rămâne `NotImplementedError`. Descrierea „citată" era reconstrucție, nu citire.

**RATIFIC propunerea, cu o combinare explicită necesară:** lumânarea de impuls înghite complet corpul `[Close,Open]` al barei inverse precedente (de culoare/direcție OPUSĂ) — **fără filtru de volum**, aceeași motivație ca la Mandatul 3.21 (proveniență neconfirmată, propagare tăcută într-o primitivă persistentă).

**Piesă lipsă din propunerea citată, completată acum:** ce face o lumânare „de impuls"? Reutilizez **exact criteriul deja ratificat la Mandatul 3.21** pentru expansiune (E010): `range[i]>1,5×ATR14[i-1]` ȘI `corp≥0,5×range[i]`. Formarea OB completă = (a) lumânarea calificată ca impuls prin criteriul E010 deja ratificat, ȘI (b) corpul ei înghite complet corpul barei opuse precedente. Zona OB rezultată = corpul barei ÎNGHIȚITE (ancora), nu al impulsului — neschimbat față de Mandatul 3.20.

**Tensiunea semnalată (IFVG „NOT single-bar body-engulfment" vs regula citată) — NU e o contradicție, explic de ce:** IFVG răspunde la o întrebare diferită — CÂND se INVERSEAZĂ o zonă DEJA EXISTENTĂ (răspuns: prima închidere ulterioară dincolo de margine, posibil după multe bare) — pe când formarea OB răspunde la CARE lumânare DEVINE o zonă, de la bun început (un eveniment de o singură bară, prin construcție). Sunt întrebări diferite, cu răspunsuri diferite, legitim — nu o inconsecvență de proiectare.

---

# PARTEA 3 — DEMANDZONE, PRIMITIVĂ NOUĂ

**Granițe: `[High, Low]`** (interval complet, fitil inclus) — NU `[Close,Open]`. Derivat direct din propria ta relație de subset: `OrderBlock` (corp) e ÎNTOTDEAUNA o submulțime geometrică a `[High,Low]` pentru orice lumânare, prin definiție (`High≥max(O,C)`, `Low≤min(O,C)`). Dacă DemandZone ar fi și ea `[Close,Open]`, ar fi IDENTICĂ cu OrderBlock, nu un „subset strict" — relația de subset pe care o ceri e adevărată DOAR dacă DemandZone=`[High,Low]`.

**Consumare: DemandZone NU se consumă — OrderBlock (imbricat) SE consumă prin D7, neschimbat.** Nu e o inconsecvență — sunt concepte diferite pe aceeași geometrie: DemandZone e reperul MACRO, persistent (ca un nivel S/R clasic, re-testabil), OrderBlock e afirmația mai ÎNGUSTĂ, specifică („exact acest corp, ca origine a impulsului, e valabil o singură dată"). Declar explicit intenționat, nu scăpare.

**Intersecția, specificată mecanic, nu descriptiv:** intrare la next-open dacă `preț ∈ [DemandZone_low, DemandZone_high]` PENTRU UN eveniment de formare A, ȘI `preț ∈ [OB_close, OB_open]` pentru un OrderBlock NEMITIGAT dintr-un eveniment de formare B — **A și B pot fi ACELAȘI eveniment (caz trivial, colapsat automat de subset — nu adaugă informație) SAU evenimente DIFERITE (caz substanțial — o DemandZone mai veche/nouă oferă context suplimentar dincolo de propriul OB îngust).** **Semnalez explicit:** dacă intenția ta e cazul trivial (A=B mereu), condiția compusă nu adaugă nimic față de simplul OB — recomand interpretarea A≠B ca fiind cea care dă sens conceptului de „intersecție", dar cere confirmare înainte de implementare, exact disciplina aplicată la „swing-ul major" din mandatul anterior.

**Separarea anti-E010 aplicată compusului:** fereastra de valabilitate a DemandZone = de la formare până la finalul blocului (D4, niciodată nu expiră altfel, fiind non-consumabilă); fereastra de MĂSURARE (a ipotezei compuse) începe DOAR la bara unde condiția compusă (DemandZone activă + OB nemitigat) devine adevărată pentru prima dată — niciodată la formarea vreuneia din cele două, separat.

---

# PARTEA 4 — IPOTEZA URMĂTOARE

## Verificat

`h1_trend_up`/`h4_trend_up` există (`code/mtf.py`, din `ema20>ema50`) — confirmat.

## Pragurile ATR: ALESE, nu derivate — declarat explicit

**0,7/1,4/2,1 × ATR** — nu le derivez, le accept ca alegere de proiectare DECLARATĂ, nu ca prag statistic. Observație structurală, nu derivare: cele trei formează progresia `0,7×{1,2,3}` — SL, 2×SL, 3×SL. Nu-i o coincidență fără sens, dar nici o derivare — o consemnez ca atare.

## O CORECȚIE, verificată, nu doar confirmată: RR ponderat NU e 1,58

**Aritmetica ta tratează 1,4 și 2,1 direct ca multipli de R — greșit, pentru că R = 0,7×ATR, nu 1×ATR.** În unități de R: `TP1 = 1,4×ATR / 0,7×ATR = 2,0 R` (nu 1,4R). `TP2 = 2,1/0,7 = 3,0 R` (nu 2,1R). **RR ponderat corect: `0,75×2,0 + 0,25×3,0 = 2,25 R`, nu 1,58 R.** O corecție favorabilă — potențialul de câștig e mai mare decât credeai, nu mai mic.

**Rata de câștig necesară** (`w*=(1+cost/R)/(RR_eficient+1)`, RR_eficient=2,25): `w*=(1+cost/R)/3,25`. **Nu e un singur număr** — R variază cu ATR-ul curent (lecția deja stabilită la Mandatul 3.13, retrapică identic aici).

## Breakeven după TP1: intrarea EXACT, nu intrare+cost

Costul e deja scăzut O SINGURĂ DATĂ, agregat, din `net_R` final — mutarea stopului la intrare+cost ar fi o a doua contabilizare a aceluiași cost. **Stopul de breakeven = prețul de intrare exact.**

## Conflictul limită-20/închidere-zilnică: rezolvat ca MINIM, orizont devine VARIABIL

**Nu e o prioritate de ales — e un minim mecanic:** ieșire la `min(intrare+20 bare, ultima bară a zilei)`. **Consecință declarată explicit:** orizontul NU mai e un număr fix de bare — devine VARIABIL, dependent de ora intrării. Se raportează ca DISTRIBUȚIE (nu un singur N), o abatere explicită de la criteriul „orizont ca număr de bare" pe care îl impun de obicei — consemnată, nu ascunsă.

## Ieșirea parțială — piesă nouă, specificată complet

```
net_R = 0,75 × (R_TP1_sau_final − cost_frac_leg1) + 0,25 × (R_leg2_final − cost_frac_leg2)
```
Cost TOTAL rămâne 0,20$ agregat (proporțional pe cele două tranșe, NU dublat pentru a doua ieșire) — cont zero-comision, costul e proporțional cu noționalul tranzacționat, nu cu numărul de bilete de ieșire. Declarat ca alegere de model, nu ca fapt dat.

## Filtrul de eligibilitate: eliminat, ÎNLOCUIT cu o podea ATR — CONSTATARE CRITICĂ

Filtrul vechi `[10,1;65,0)` pici **se elimină** — derivat pe cost greșit ȘI presupune stop structural, nu ATR. **Nou, derivat prin ACEEAȘI logică de saturație 3×cost** aplicată la `R=0,7×ATR`: prag de saturație unde `3×cost=R` → `3×0,20=0,7×ATR_min` → **`ATR_min ≈ 0,857$ ≈ 86 pips`**.

**Constatare care amenință testabilitatea ipotezei:** ATR-ul de AZI (cel mai mare din tabelul tău, ~74 pips) e **SUB** acest prag de 86 pips. Media istorică pe descoperire (17-18 pips) e cu mult sub. **Populația eligibilă pe M15_v2 descoperire ar putea fi aproape goală, sau chiar goală, la costul corectat de 0,20$.** Nu presupun rezultatul — semnalez ca prag de verificat ÎNAINTE de orice execuție, nu ca o concluzie. Dacă populația e prea mică, opțiuni: cost mai mic (extremitatea joasă a intervalului tău, 0,05 spread → cost≈0,10$, prag≈43 pips, tot aproape de limita superioară istorică), sau acceptarea unei populații foarte mici cu regula deja stabilită `n≥25`.

## Cele cinci criterii, aplicate

1. **Prag numeric:** `H0: μ_netR≤0`, neschimbat conceptual.
2. **Orizont ca bare:** VARIABIL (min 20 bare / bare-până-la-EOD) — abatere explicită, raportată ca distribuție.
3. **Populație:** de derivat/verificat — podeaua ATR de mai sus decide dacă există populație testabilă.
4. **Prag de clasificare:** `alpha=0,05`, familie de 1 (ipoteză nouă, distinctă structural de SMC_S1-S20).
5. **Zero parametri liberi:** toate elementele de mai sus fixate — pragurile ATR declarate ca alese (nu ascunse ca derivate), restul derivat sau specificat mecanic.

---

**Nimic re-rulat în acest document. Publicat pe `statistician-foundation`; manifestul se incrementează. Holdout SEALED.**
