# STATISTICIAN — VERDICTUL PE A', CONTROLUL ALEATORIU, MĂSURĂTOAREA MAE/MFE ȘI CADRUL DE CONFIRMARE OBDZ-002

**Document ID:** STAT-OBDZ-MAE-MFE-CONTROL-CONFIRMATION-SPEC-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

**Verificare de sursă:** citit integral `code/obdz_sltp_diagnostic.py` (comitul `465eb38`) — implementarea corespunde exact specificației (`v2.7.13`, `44477f3`). `mypy --strict` curat. **Rulat direct** — toate cifrele citate reproduse exact: MAE agregat p50=4,399 (≈4,4×ATR, raport la 0,7 = 6,29×); fracții de timeout la p75/p90: 0,956/0,96/0,962 și 0,989/0,978/0,987 (interval 0,96-0,99 confirmat); conversie TP1→TP2 la p75/p90: 0,0 sau `None` (reach_TP1≈0) peste tot; best/sumR la p90 corecție = 9,643 (≈9,64); verdictul mecanic literal = MERITĂ IPOTEZĂ NOUĂ. Verificat direct în cod: `detect_rejections` (D6 wick-sweep-reject la zona corp) NU e geometrie pinbar (close în treimea superioară, fitil≥60% range) — confirmat diferit de Varianta 1. Căutare exhaustivă: zero apariții `inside_bar`/`pinbar` în `code/` — Variantele 1 și 2 cer primitive noi, confirmat. Căutare exhaustivă: `detect_order_blocks`/`detect_demand_zones` sunt apelate DOAR pe bare M15 (`obdz001.py`, `task_obdz_population.py`, `obdz_sltp_diagnostic.py`, teste sintetice) — NICIODATĂ pe `H1_from_M15_v2`/`H4_from_M15_v2` — golul de cablare confirmat real, nu doar semnalat.

---

# SARCINA 1 — verdictul pe Diagnosticul A'

## Pragul mecanic s-a declanșat, dar pe celule care nu mai testează raportul SL/TP — NU accept „MERITĂ IPOTEZĂ NOUĂ" ca răspuns valid la întrebarea pusă

**Diagnosticul, așa cum a fost specificat, nu a anticipat acest mod de degenerare — e un gol în PROPRIA mea specificație, nu o eroare de execuție a VE.** La p75/p90 (SL=8,56×/13,61×ATR), TP1 (17-27×ATR) e practic de neatins (`reach_TP1`≈0-3 din 156-275), iar 95,6-98,9% din tranzacții expiră pe plasa de 20 de bare fără să atingă nici stopul, nici ținta. Ce se măsoară acolo nu mai e „intră, SL la k×ATR, TP la 2k/3k×ATR" — e „intră, ține 20 de bare, ieși la orice preț se întâmplă să fie" — exact observația ta. Rezultatul pozitiv de acolo (drift rezidual normalizat la un R enorm) nu e dovadă că raportul SL/TP ajută; e dovadă că un R suficient de mare face APROAPE ORICE rezultat mic să pară „pozitiv" în unități normalizate, fără legătură cu mecanismul de risc testat.

**Chiar și candidatul care ÎNCĂ testează ceva structural apropiat de întrebarea pusă (p25, SL=1,965×ATR) nu trece pragul:** timeout scade la 0,356-0,444 (mult mai rezonabil), dar expectancy_$ e negativă în bear (−85,5$) și bull (−39,7$), pozitivă doar în corecție (+9,7$) — **1 din 3 regimuri, nu 2+, cerut de pragul pre-înregistrat.**

**Verdict corectat: diagnosticul NU oferă dovadă utilizabilă că un raport SL/TP mai lat ajută.** Aplicarea literală a pragului („MERITĂ IPOTEZĂ NOUĂ") se declară **INVALIDĂ ca răspuns la întrebarea „contează raportul"** — pragul s-a declanșat pe un artefact de construcție (candidați unde SL/TP au încetat să fie mecanismul activ), nu pe un semnal real. Reclasific: pentru întrebarea „raportul SL/TP", rezultatul e **TESTABLE BUT INSUFFICIENT EVIDENCE** — cu precizarea că „insuficient" aici înseamnă „construcția testată la extremele late nu mai testează raportul", nu „ar trebui mai multe date". **Nu se formulează OBDZ-002 pe baza acestui prag literal.**

## MAE=4,4×ATR ca fapt de sine stătător — necesită controlul cerut, specificat mai jos (Sarcina 2)

De acord complet: fără un control, nu putem spune dacă 4,4×ATR e o proprietate a ZONEI (declanșatorul compus prezice o excursie adversă specifică) sau a PIEȚEI (orice punct aleator pe aceeași fereastră de 92 de bare arată la fel). Exact paralela cu controlul E004 (85% bază, 71% pentru gap-urile specifice — sub bază, nu peste). Specificat integral la Sarcina 2.

---

# SARCINA 2 — Măsurătoarea MAE + MFE, cu bara de atingere, plus controlul aleatoriu

## Controlul aleatoriu — specificat mecanic

**Eșantion de control: bare M15 alese ALEATORIU din populația „bias aliniat" a fiecărui regim** (pasul 1 din numărătoarea de populație — 35.454/37.707/17.145 bare, deja calculată), **fără înlocuire, potrivit ca NUMĂR exact cu declanșatoarele brute reale** (275/223/156), **cu direcția = direcția bias-ului la acea bară** (aceeași convenție ca declanșatoarele OBDZ — long dacă bias sus, short dacă bias jos) — izolează contribuția SPECIFICĂ a intersecției compuse (DemandZone×OB nemitigat) FAȚĂ DE simpla aliniere de bias, nu față de „orice bară aleatoare din tot regimul". **Fără podeaua de ATR** (aceeași convenție ca Măsurătoarea A', comparație curată brut-la-brut). **Sămânță fixă** (reutilizez `20260729`, aceeași convenție ca WP-5', pentru reproductibilitate).

**Aceeași măsurătoare MAE (92 bare, multipli ATR14 la bara aleasă)** se aplică identic pe control. **Raportare: percentilele p25/p50/p75/p90 ale MAE-control, alături de MAE-declanșatoare, pe același tabel** — comparație directă, nu un test formal separat (consecvent cu natura diagnostică, nu de tip verdict-cu-prag, a acestei măsurători — la fel ca la E004, unde comparația era „cade rata în banda pre-înregistrată", nu un test statistic complet nou).

**Citire, scrisă acum:** dacă MAE-control ≈ MAE-declanșatoare (percentile apropiate) → zona NU adaugă nimic față de simpla aliniere de bias; 4,4×ATR e o proprietate a volatilității pieței pe 92 de bare, nu a construcției compuse. Dacă MAE-control e MATERIAL mai mic → declanșatoarele compuse sunt sistematic mai expuse la excursie adversă decât un punct aliniat-la-bias oarecare — susține direct teoria ta (zona identifică momente structural expuse, nu protejate). Dacă MAE-control e MATERIAL mai mare → declanșatoarele compuse sunt relativ protejate față de un punct aleator — ar submina motivația pentru orice confirmare suplimentară.

## Măsurătoarea MFE + bara de atingere, pentru AMBELE populații (declanșatoare ȘI control)

**Definiție simetrică cu MAE:** pentru fiecare eveniment (declanșator SAU control), pe aceeași fereastră `[entry+1, entry+1+92]`, **MFE = excursia favorabilă maximă, în multipli ATR14[entry]** (long: `max(high)−entry_price`; short: `entry_price−min(low)`).

**Bara de atingere, pentru ambele extreme:** `bar_MAE` = indexul barei (relativ la intrare) unde e atins PRIMA DATĂ punctul de excursie adversă maximă; `bar_MFE` = analog pentru excursia favorabilă maximă.

**Raportare obligatorie, pe fiecare populație (declanșatoare, per regim + agregat; control, per regim + agregat):**
- distribuția MAE (deja specificată) și distribuția MFE (percentile p25/p50/p75/p90), separat
- distribuția raportului MFE/MAE per eveniment (percentile) — cât de mare e mișcarea favorabilă relativ la cea adversă, per eveniment individual, nu doar în agregat
- fracția evenimentelor unde `bar_MAE < bar_MFE` (adversul vine primul) vs `bar_MAE > bar_MFE` (favorabilul vine primul) vs egalitate
- distribuția `bar_MAE` și `bar_MFE` separat (percentile, ca număr de bare de la intrare)

**Citirea, EXACT grila ta, aplicată la ce arată tabelul — nu un prag numeric nou inventat acum:**
```
bar_MAE tipic devreme, bar_MFE tipic mai târziu, ȘI MFE nu e sistematic mic vs MAE
  -> intrare prea devreme, ideea directă corectă (susține confirmarea de moment)

MAE mare, MFE sistematic mic (raport MFE/MAE mic la majoritatea percentilelor)
  -> zona nu prezice o reversare reală, nu doar un moment nepotrivit

bar_MAE ≈ bar_MFE, ambele devreme, magnitudini comparabile
  -> se măsoară doar volatilitate generică, nu un tipar direcțional
```
**Aceeași măsurătoare pe control** decide dacă tiparul de secvențiere (nu doar magnitudinea) e specific zonei sau general pieței — dacă și controlul arată „advers devreme, favorabil târziu" în aceeași proporție, chiar și un rezultat „adversul vine primul" la declanșatoare nu ar sprijini confirmarea (ar fi doar cum se comportă orice bară aliniată la bias).

---

# SARCINA 3 — cadrul pentru ipoteza cu confirmare (Varianta 3), NU specificată numeric acum

**Confirmat, la sursă:** Varianta 3 (înghițire de corp + magnitudine) există complet — e EXACT criteriul de formare OB deja ratificat (`detect_order_blocks`: impuls E010 `range>1,5×ATR14[i-1]` ȘI `corp≥0,5×range`, plus înghițire completă a corpului barei opuse). Zero primitive noi. Variantele 1 (pinbar) și 2 (inside bar) cer geometrie nouă, confirmat prin căutare — **de acord cu recomandarea ta: se țin pe loc până se vede dacă Varianta 3 reduce MAE.** A construi 1 și 2 acum, înainte de a ști dacă mecanismul de confirmare (nu geometria specifică) chiar ajută, ar însemna primitive construite pentru o întrebare la care încă nu avem răspuns — de acord integral, nu le construiesc.

## Mecanica Variantei 3, specificată STRUCTURAL (nu numeric)

Declanșatorul compus rămâne cel deja definit (bias + intersecție cross-candle DemandZone×OB), la bara `t` (prima Mitigation calificată). **Intrarea NU se mai face la `t+1`** — se așteaptă o bară de CONFIRMARE `j>=t`, prima bară unde apare un nou impuls (aceeași pereche de condiții ca formarea OB: `range[j]>1,5×ATR14[j-1]` ȘI `corp[j]≥0,5×range[j]`) **în direcția bias-ului** (impuls bullish pentru un setup long). Intrarea devine `j+1` (next-open după confirmare). Dacă nicio confirmare nu apare într-o fereastră rezonabilă, declanșatorul se marchează NECONFIRMAT (fără intrare) — fereastra exactă de așteptare rămâne de derivat (vezi mai jos), nu aleasă acum.

## Ce rămâne DE DERIVAT, condiționat de Sarcinile 1-2 — NU specificat aici

- **Stopul:** se re-rulează Măsurătoarea A' (MAE) pornind de la bara de CONFIRMARE `j` (nu de la `t`), pe populația OBDZ-002 (confirmată). Dacă MAE-confirmat scade material față de 4,4×ATR, susține direct teoria confirmării; dacă nu scade, confirmarea nu rezolvă problema de moment, indiferent de câte primitive am adăuga. Candidații SL rămân percentilele acestei NOI distribuții — nu inventez o cifră acum.
- **Țintele:** rămân 2×/3× stopul derivat (aceeași progresie 1×/2×/3×), CU EXCEPȚIA cazului în care distribuția MFE (Sarcina 2, pe populația confirmată) arată un raport MFE/MAE sistematic diferit de 2:1/3:1 — decizie de luat DUPĂ ce se vede acea distribuție, nu acum.
- **Orizontul:** diagnosticul A' a arătat că 20 de bare devine insuficient la stopuri late (chiar înainte de confirmare). Se derivă din distribuția REALĂ a barei de rezoluție (SL sau TP) sub parametrii candidați ai populației confirmate — un orizont care lasă majoritatea tranzacțiilor să se rezolve, nu unul ales din intuiție. Nu aleg o cifră acum.
- **Populația pe H1/H4 — pas OBLIGATORIU ÎNAINTEA oricărei implementări de mașină de stare noi:**

## Golul de cablare H1/H4 — confirmat real, pas de numărare ÎNAINTE de construcție

Confirmat prin căutare: `detect_order_blocks`/`detect_demand_zones` nu au rulat NICIODATĂ pe bare H1/H4 — doar M15. Nu e o primitivă lipsă (aceleași funcții se aplică oricărui OHLC), e o recablare: (1) rulează detectoarele pe `H1_from_M15_v2`/`H4_from_M15_v2` direct (context-derived, discovery-safe — NU calea nativă sigilată), (2) mapează zonele rezultate (H1/H4) înapoi pe linia de timp M15 printr-un merge forward-safe identic convenției deja folosite pentru bias (`avail=time_HTF+period`, `merge_asof` backward) — o zonă H1/H4 devine „cunoscută" pe M15 abia după ce bara ei proprie s-a ÎNCHIS.

**Înainte de a construi mecanica completă de intrare pe zone H1/H4, cer un SCRIPT DE NUMĂRARE READ-ONLY** (analog `task_obdz_population.py`), care rulează EXACT aceleași criterii de formare (deja ratificate, zero primitive noi) pe `H1_from_M15_v2` (49.580 bare) și `H4_from_M15_v2` (12.832 bare), raportând câte zone/OB-uri se formează per regim, ÎNAINTE de orice efort de implementare a mașinii compuse. Motiv: pe M15 (130.491 bare), condiția compusă completă a dat doar 275/223/156 declanșatoare brute (~0,2-0,3% rată) — pe H4 (12.832 bare TOTAL pe toată perioada), aceeași rată ar da o mână de evenimente, posibil sub pragul INSUFFICIENT_N chiar înainte de orice alt filtru. **Regula INSUFFICIENT_N (n≥25/regim) se aplică la acest pas de numărare, nu abia la sfârșit** — dacă populația H1/H4 e deja insuficientă, se raportează și ne oprim, fără să construim restul mecanicii degeaba.

---

# SARCINA 4 — familia de corecție: CONFIRM family=2, schimbarea de mecanism NU scutește de regulă

**Nu se separă.** Motivul nu e cât de diferit e mecanismul (intrare la confirmare vs la prima atingere) — e că justificarea ÎNTREGII schimbări (constatarea MAE=4,4×ATR) vine DIRECT din diagnosticul rulat pe ACEEAȘI descoperire M15_v2. Exact situația epistemică de la SMC_S1/SMC_S1_v2: o a DOUA proiectare informată de o PRIVIRE anterioară asupra acelorași date, nu o ipoteză independentă, pre-înregistrată orb. **Cu cât schimbarea de mecanism e mai substanțială, cu atât motivul pentru family=2 e mai puternic, nu mai slab** — o schimbare mare informată de aceleași date merită la fel de multă precauție ca una mică, nu mai puțină. **OBDZ-002 (confirmare + posibil H1/H4) intră în familie de 2 cu OBDZ-001, pragul de semnificație se îngustează corespunzător, declarat explicit înainte de orice test.**

---

## Ordinea confirmată

Verdictul pe A' (Sarcina 1) — ÎNCHIS, corectat. Măsurătoarea MAE/MFE+control (Sarcina 2) — SPECIFICATĂ, de rulat următoarea. Numărătoarea de populație H1/H4 (Sarcina 3, parte) — SPECIFICATĂ, de rulat în paralel/după. **Ipoteza OBDZ-002 NU se specifică numeric în acest document** — se formulează DUPĂ ce Sarcinile 2 și 3 raportează, exact cum ai cerut.

---

**Nimic rulat suplimentar în acest document dincolo de re-verificarea independentă a diagnosticului A' deja livrat. Publicat pe `statistician-foundation`; manifestul se incrementează.**
