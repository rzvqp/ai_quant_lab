# STATISTICIAN — CIRCULARITATEA MIT/REJ, VERDICTELE REDESCHISE DE COST, IPOTEZA FORMALĂ

**Document ID:** STAT-MITREJ-CIRCULARITY-COST-VERDICTS-HYPOTHESIS-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

**Verificare de sursă, înainte de orice decizie:** citite integral `code/order_flow.py` (comiturile `3fad03e`, `74fd799`) și `code/partial_exit.py` (`4aa2b21`) în worktree-ul `ai_quant_lab-wp5b`; confirmate exact citările CEO. `mypy --strict` curat pe `order_flow.py`+`partial_exit.py`+`market_state.py`+`order_block_void.py` (4 module, 0 erori); 22/22 teste (`test_order_flow.py`+`test_partial_exit.py`) trec independent; suita completă a worktree-ului: 234 trecute, 4 eșecuri — **aceleași 4 pre-existente**, nimic nou. Am **rulat direct** `code/task1_atr_eligibility.py` și `code/task2_cost_rerun.py` — toate cifrele citate de CEO reproduse exact (89,75% global, per-regim 94,11/81,37/98,27%; S7 bear p=0,277, S11 bull p=0,364, S7 bear NOU b/sR=13,59, S17 corecție VECHI n=27/p=None, S17 corecție NOU b/sR=0,55, structura 3/24 și 6/24, familii S7/S11/S16/S17).

---

# BLOCUL 1 — Q1, circularitatea Mitigation/Rejection

## Confirmat, la sursă, și PRECIZAT dincolo de constatarea VE

`detect_order_blocks` fixează `formation_idx = i-1` (bara-ancoră înghițită), iar `_scan_reactions` scanează de la `range(ob.formation_idx + 1, stop)` — adică începe EXACT la bara `i`, bara de IMPULS. Prin condiția de înghițire `(i_lo<=p_lo și i_hi>=p_hi)`, corpul impulsului conține STRICT corpul zonei `[zl,zh]=[p_lo,p_hi]`, deci `low[i]<=i_lo<=zl` și `high[i]>=i_hi>=zh`.

**Am verificat că defectul nu se limitează la Mitigation, cum sugerează formularea VE — se aplică IDENTIC la Rejection.** Condiția de rejecție bullish, `low[i]<zl și close[i]>zl`: din înghițire, `low[i]<=zl`; iar pentru impuls bullish, `close[i]=i_hi>=zh`, și cum `zh>zl` (corp cu amplitudine nenulă, practic mereu adevărat pe date reale), rezultă `close[i]>zl`. **Deci bara de impuls produce o vizită-1 spurioasă garantată la AMBELE tipuri de eveniment, nu doar la Mitigation** — o precizare care întărește diagnosticul VE, nu îl slăbește.

## Decizie: RATIFIC propunerea VE — scanarea începe la `formation_idx + 2`

Motivul e identic cu E010: fereastra care pretinde să MĂSOARE prima re-vizitare a zonei conține, prin construcție, evenimentul care A CREAT zona. O „vizită" reprezintă întoarcerea INDEPENDENTĂ a pieței la o zonă deja formată — bara care tocmai a format-o nu e o întoarcere, e chiar actul de formare. Sărind bara de impuls (`formation_idx+2`) elimină exact acest artefact, fără să atingă nimic altceva din contract: fereastra de SELECȚIE rămâne funcție pură de bare `<=event_idx`, fereastra de MĂSURARE rămâne `[event_idx, event_idx+H)` — separarea anti-E010 deja specificată nu se schimbă, doar punctul de START al scanării.

**Nu propun altă convenție** — sărirea unei singure bare (cea responsabilă demonstrat pentru artefact) e minimală și suficientă; orice alternativă mai complexă (ex. un cooldown suplimentar de la formare) ar rezolva aceeași problemă cu mai multe grade de libertate nejustificate.

## Efect retroactiv: NU, verificat

Mitigation și Rejection au fost implementate ACUM (comitul `3fad03e`), nicio ipoteză formalizată nu le consumă încă (confirmat: niciun fișier din `code/` sau `tests/` nu importă `detect_mitigations`/`detect_rejections` în afara propriei suite de teste), și niciun rezultat pe date reale nu există. **Nimic de corectat retroactiv.**

## Clasificare: BLOCARE REZOLVATĂ PRIN SPECIFICAȚIE

Nu mai e BLOCHEAZĂ PARTIAL — VE implementează `scan_start = formation_idx + 2` pentru ambele funcții, re-rulează testele anti-lookahead existente (trebuie să rămână verzi, fereastra de selecție tot nu citește viitorul), și pipeline-ul compus OB→Mit/Rej e deblocat.

---

# BLOCUL 2 — trei clarificări

## Q2 — intersecția DemandZone × OrderBlock: confirmat TRIVIALĂ cum implementat, RATIFIC interpretarea substanțială pentru compus

Verificat în `detect_demand_zones`: fiecare `DemandZone` se generează pe **aceeași bară-ancoră** ca OB-ul ei (`formation_idx=a` identic), doar lărgind corpul la fitil — deci geometric, `DemandZone ⊇ OrderBlock` pe ACEEAȘI bară, întotdeauna, prin construcție. VE a implementat corect primitivele SEPARAT și NU a inventat compusul — exact ce am cerut.

**Confirm: A=B (aceeași bară) e trivial** — nu adaugă nimic peste simplul OB, cum a spus VE precis.

**RATIFIC acum interpretarea A≠B ca operativă pentru ipoteza de la Blocul 4** (recomandarea mea din mandatul anterior, acum confirmată ca decizie, nu doar sugestie): intrarea cere un OrderBlock NEMITIGAT dintr-un eveniment de formare B, ȘI o DemandZone ACTIVĂ (persistentă, D4, niciodată nu expiră) dintr-un eveniment de formare A DIFERIT (bară-ancoră diferită), ale căror intervale geometrice se SUPRAPUN: `OB_B.zone_lower <= DemandZone_A.zone_upper ȘI OB_B.zone_upper >= DemandZone_A.zone_lower` (testul standard de suprapunere de intervale — nu containment complet, suprapunere parțială e suficientă). Evenimentul de intrare = bara la care OB_B își are propriul eveniment de Mitigation calificat (cf. Blocul 1, scanare de la `formation_idx+2`), CONDIȚIONAT ca la acea bară o DemandZone_A (A≠B) activă să se suprapună geometric. Fără această confirmare explicită, compusul ar fi rămas identic cu OB simplu — acum are conținut propriu: confluența a DOUĂ construcții formate în momente diferite.

## Q3 — bara ambiguă TP1↔stop: RATIFIC `stop_before_target=True`

Regula worst-case din `MIN_STOP_FLOOR_PREREG:31` a fost scrisă exact pentru situația "nu pot determina ordinea intrabar, presupun cazul mai defavorabil" — o regulă despre AMBIGUITATE de ordine, nu despre CARE nivel anume e vizat. TP1 și stopul sunt de-o parte și de alta a intrării; când ambele cad în aceeași bară, ordinea reală e la fel de necunoscută ca la ținta finală. Aceeași logică, aceeași concluzie: **stopul câștigă bara ambiguă**, consecvent cu disciplina worst-case aplicată peste tot în acest lab (podeaua D2, alegerea conservatoare a spread-ului la corecția de cost). Confirm.

## Q4 — TP1 și TP2 în aceeași bară: RATIFIC `tp1_tp2_same_bar=True`, cu o justificare mai tare decât un simplu default

Verificat în cod: `tp_hit(j,level) = high[j]>=level` (long). Cum TP2 e MEREU mai departe decât TP1 în direcția favorabilă (`tp2_price>tp1_price` pentru long), atingerea TP2 într-o bară IMPLICĂ logic atingerea TP1 în ACEEAȘI bară (extremul favorabil al barei a trecut prin ambele praguri, monoton). **Nu e o alegere sub incertitudine ca Q3 — e o consecință geometrică forțată de ordinea TP1<TP2.** Tratarea separată (execuție pe bare diferite) ar introduce o întârziere artificială acolo unde piața a trecut deja prin ambele niveluri, subraportând edge-ul real. Confirm `tp1_tp2_same_bar=True`, cu precizarea că nu e doar default declarat — e singura opțiune consecventă cu geometria.

---

# BLOCUL 3 — verdictele redeschise de corecția de cost

## Distincția structurală a lui VE, confirmată și esențială pentru citirea corectă

`edge_brut_$` (media gross, independentă de cost ȘI de TICK) rămâne aceeași indiferent de costul aplicat — corecția 0,40→0,20 mută DOAR pragul de decizie și îmbunătățește netul cu 0,20$/tranzacție, NU creează edge nou. Fără această distincție, trecerea de la 3/24 la 6/24 celule „peste prag" s-ar fi citit greșit ca o îmbunătățire a semnalelor — de fapt e strict mecanică (același edge_brut, prag mai mic).

**Estimarea mea orientativă din mandatul anterior (6/8 familii ar trece) NU se reproduce — confirmat, 4/8 (S7, S11, S16, S17) au O SINGURĂ celulă peste prag, nu profitabilitate generală pe familie.** Notez asta explicit ca pe o predicție eronată a mea, nu doar ca pe o corectare a VE.

## Filtrul: NOU rămâne autoritar — dilutivitatea la S16 corecție e efect așteptat, nu eroare

Filtrul VECHI (`[1,01;6,50)$` = `[10,1;65)` pips @TICK 0,10) a fost derivat pe costul GREȘIT. Filtrul NOU (`[0,58;6,50)$` = `[58;650)` pips @TICK 0,01) e re-derivat din constantele CORECTE, cu aceeași metodologie (saturație 3×cost). **NOU e autoritar, necondiționat de care variantă arată mai bine pentru vreo celulă anume** — exact disciplina cerută de întregul acest exercițiu: nu se alege filtrul după cum arată rezultatul.

Inversiunea de semn la S16 corecție (+0,293 → −0,077, confirmată exact) e un efect MECANIC AȘTEPTAT, nu un semnal de eroare: podeaua nouă e mai mică ($0,58 vs $1,01), deci include MAI MULTE evenimente cu deplasare mică — evenimente mai zgomotoase, anterior excluse. Dilutivitatea e o consecință directă și corectă a coborârii podelei odată cu costul corectat, nu un artefact de filtrare greșită.

## SMC_S1 — RECHALIFICAT, eticheta se schimbă

**REJECTED_NET_OF_COST nu mai e corectă — de acord cu premisa întrebării.** Acea etichetă exista special pentru a distinge "niciun edge" de "edge brut real, mecanic demonstrat, dar sub costul de execuție". La costul corectat, edge_brut_$ pe cele trei regimuri e **−0,0007 / +0,0214 / −0,1128** (filtru VECHI) și **+0,0312 / −0,0072 / −0,0582** (filtru NOU) — practic zero și cu semn INCONSECVENT între regimuri, nu micul edge pozitiv monoton-descrescător raportat inițial la costul de 0,40. Povestea "mecanism real, doar nerentabil" nu mai are pe ce sta.

p_wp5 (H1: μ_netR>0) rămâne covârșitor de nesemnificativ în toate cele 6 celule (VECHI/NOU × 3 regimuri): 0,93/0,88, 0,98/1,0, 0,97/0,89 — nicăieri aproape de a respinge H0.

**Verdict: STATISTICALLY REJECTED** (nu mai un sub-label cu scop restrâns — costul fiind acum corect stabilit, iar edge-ul brut însuși inconsistent/aproape-zero pe toate regimurile, nu mai există distincția pe care REJECTED_NET_OF_COST o proteja). Delimitare de scop, păstrată: se respinge H1:μ_netR>0 la construcția Open-R actuală (direcție mecanică, orizont 20 bare, ieșire pe timp), pe ambele variante de filtru testate, pe cele trei regimuri M15_v2 discovery. NU se extinde la o construcție de risc diferită (ex. noua ipoteză ATR de la Blocul 4) sau la un mecanism de detecție diferit.

## S7 și S11 — TESTABLE BUT INSUFFICIENT EVIDENCE, nu REJECTED

Aplic regula Constituției (CEO, 2026-07-24): REJECTED e rezervat strict pentru dovezi care DEZMINT activ ipoteza — nu pentru informație insuficientă. Aici estimatul punctual e **pozitiv** (S7 bear net$[.20]=+144, edge_brut +0,31/+0,25; S11 bull net$[.20]=+255, edge_brut +0,31/+0,17), doar nesemnificativ (p=0,277–0,455 pentru S7 bear; p=0,364–0,915 pentru S11 bull) — o situație calitativ diferită de SMC_S1 (unde estimatul era negativ ȘI nesemnificativ în sens opus). Nesemnificația singură nu dezminte — cere **TESTABLE BUT INSUFFICIENT EVIDENCE**.

**Dar S7 bear poartă un steag de fragilitate obligatoriu, cf. disciplinei NET_CONCENTRATION_INVENTORY:** b/sR=13,59 la filtrul NOU înseamnă o singură tranzacție echivalează cu **13,6× întreaga sumă netă** — eliminarea ei ar duce suma la puternic negativ (wo1R=−39, față de un net_sumR total mic). Semnalul "pozitiv" din această celulă e, demonstrat mecanic, un artefact de o tranzacție, nu un fenomen repetabil. Celelalte regimuri S7 (bull, corecție) sunt net-negative în ambele filtre. **Tabloul familiei S7, per total: fragil, nu robust — TESTABLE BUT INSUFFICIENT EVIDENCE, cu steagul de concentrare pe bear ca o condiție PERMANENTĂ a acestei clasificări** (orice re-testare viitoare pe alte date trebuie să verifice explicit dacă edge-ul supraviețuiește eliminarea celei mai bune tranzacții, nu doar p-value).

S11: bull cu p=0,364/0,915 (filtru VECHI/NOU) — nesemnificativ, celelalte regimuri net-negative. **TESTABLE BUT INSUFFICIENT EVIDENCE**, fără steagul de concentrare specific (nu verificat ca fiind dominat de o singură tranzacție, dar nici confirmat robust).

S2, S3, S13 — verificate, menționate pentru completitudine deși CEO nu a întrebat explicit: net negativ în toate cele 3 regimuri, ambele filtre, fără nicio celulă pozitivă notabilă. Nu ridică nicio întrebare vie — rămân TESTABLE BUT INSUFFICIENT EVIDENCE prin absența oricărui semnal, nu prin dovadă activă de respingere.

## S16 și S17 — NOT TESTABLE (oracol necalibrat), independent de orice p-value

**Oracolul `block_bootstrap@v1` a fost validat STRICT pentru L>=H=20** (Mandatul 3.20, `4c9c20f`) — regimul de dependență finit-memorabilă acoperă corect blocul DOAR când lungimea blocului L conține în întregime fereastra reală de dependență H. S16 (H=92) și S17 (H=460) rulează cu **același L=28 fix**, aplicat MECANIC din contractul Open-R comun (grupa A folosește L=28 la H=20) — dar la H=92 și H=460, **L=28 < H**, exact condiția care făcea metoda invalidă în regimul AR(1) original (Mandatul 3.17) și pe care validarea de la 3.20 o excludea explicit prin L>=H.

**Concluzie: orice `p_wp5` raportat pentru S16/S17 în această rulare e NEVALIDAT — nu se poate folosi pentru nicio concluzie, favorabilă sau nefavorabilă.** Asta include, explicit, cele două p-value aparent "semnificative" ale lui S17 (bear NOU p=0,0265, corecție NOU p=0,0190) — **NU sunt dovadă**, exact pentru că metoda care le-a produs nu e calibrată în acest regim; un p mic dintr-un estimator necalibrat nu e un semnal, e o capcană clasică pe care disciplina acestui lab există s-o prevină. Le semnalez explicit ca NEUTILIZABILE, nu ca fiind promițătoare.

**Suplimentar, S17 corecție la filtrul VECHI: n=27, sub orice prag rezonabil** (chiar sub cerința strictă `nt>L=28` din cod, motiv pentru care p=None a fost corect returnat — nu o eroare, un refuz corect al testului de a rula sub-putere).

**Decizie asupra recalibrării:** NU comand o recalibrare WP-5' la L>=92 și L>=460 în acest document — ar fi un efort de validare de aceeași magnitudine ca recalibrarea originală (Mandatul 3.19-3.20: generator de nul potrivit mecanismului real, baterie FPR dedicată, prag de acceptare pre-înregistrat), un task VE nou și substanțial, nu o simplă re-etichetare. **S16 și S17 rămân marcate NOT TESTABLE (oracol necalibrat pentru aceste orizonturi)** până când o asemenea recalibrare dedicată e comandată separat și executată — nu inventez un rezultat provizoriu pe un instrument nevalidat.

## Corecția de testare multiplă: familia = 8, urmând convenția deja stabilită la S1

Verific precedentul propriu: verdictul ORIGINAL al lui S1 (Mandatul 3.20) a fost definit ca „family of 1" cu testul aplicat pe **counturi POOLED peste regimurile eligibile** — NU trei teste separate per regim. Extind ACEEAȘI convenție, pentru consecvență, la toate cele 8 familii acum testate ÎMPREUNĂ în aceeași trecere (`task2_cost_rerun.py`): **familia de corecție = 8** (un test POOLED per familie, peste cele 3 regimuri combinate ca observații ale ACELUIAȘI construct, nu 24 de teste separate pe celulă).

**Acest test POOLED per familie NU a fost încă calculat de VE** — cifrele din această rulare sunt per-celulă (per regim). Pentru S1, nu e nevoie de el ca să închid verdictul: toate cele 3 regimuri sunt independent negative ȘI covârșitor nesemnificative (p 0,88-1,0) — punerea lor laolaltă nu poate produce semnificație pozitivă din trei rezultate individual puternic non-pozitive. **Pentru S7/S11, cer explicit acest test pooled de la VE înainte de un verdict final** — clasificarea TESTABLE BUT INSUFFICIENT EVIDENCE de mai sus e interimară, bazată pe dovada per-celulă disponibilă acum.

La pragul BH-FDR α=0,05/8=0,00625 (cel mai strict rang), NICIUNA din valorile p per-celulă disponibile (minim 0,0190 la S17 corecție NOU — deja exclusă independent pe motiv de oracol) nu s-ar apropia de prag chiar dacă am aplica-o direct — confirmă calitativ concluziile de mai sus, fără să le înlocuiască cu testul pooled formal cerut.

---

# BLOCUL 4 — ipoteza formală (ATR/DemandZone/OB, partial-exit)

## Auto-corecție necesară: eroarea mea de unitate la podeaua ATR, retrasă explicit

**VE a găsit corect problema, iar CEO a confirmat-o direct: „îngrijorarea despre populație goală venea dintr-o nepotrivire de unitati."** Retrag explicit constatarea "hypothesis-threatening" din mandatul anterior. Eroarea, precis: am calculat corect podeaua nouă (`ATR_min≈0,857$≈86 pips @TICK 0,01`), dar am comparat-o direct cu „74 pips" — cifra pe care CEO o citase în mandatul ORIGINAL (câteva mandate în urmă), înainte de corecția de TICK, când convenția de „pip" folosită în TOATĂ sesiunea era încă `TICK=0,10` (adică 74 pips vechi = 7,40$, NU 0,74$). Am comparat 86 din sistemul NOU (=0,857$) cu 74 din sistemul VECHI (=7,40$) ca și cum ar fi aceeași unitate — exact capcana pip-vs-tick pe care întreaga corecție de cost există s-o prevină. Am făcut-o eu însumi, la o săptămână după ce am cerut altora s-o evite.

**Verificat direct, rulând `code/task1_atr_eligibility.py` eu însumi:** podeaua $0,857 e depășită de 89,75% din barele de descoperire (bear 94,11%, bull 81,37%, corecție 98,27%; mediana ATR pe regim $1,99/$1,23/$2,16 — toate cu mult peste podea). **Populația eligibilă NU e goală și nici aproape de goală — e majoritară.** Ratific: filtrul de eligibilitate ATR (`ATR_min≈0,857$`, derivat din saturația 3×cost/0,7, RATIFICAT în mandatul anterior) rămâne AȘA CUM A FOST DERIVAT, acum confirmat fezabil pe date reale, nu doar pe hârtie.

## Pragurile 0,7/1,4/2,1: reconfirmate ca alegere de proiectare a CEO, nu derivate

Neschimbat față de mandatul anterior — structura 0,7×{1,2,3} rămâne o observație, nu o derivare. Accept ca pre-înregistrate, declarat explicit.

## Filtrul de eligibilitate: RATIFICAT ca podea de ATR (nu mai „de rederivat" — rederivat deja, acum confirmat fezabil)

Vechiul filtru `[10,1;65,0)` pips (presupune stop structural) rămâne ELIMINAT pentru această ipoteză, cf. mandatului anterior. Podeaua de ATR e singurul filtru de eligibilitate operativ.

## Orizontul variabil: cum se măsoară rezultatul

`net_R` (deja specificat, Piesa 3) e o variabilă per-tranzacție bine definită indiferent de câte bare a durat efectiv fiecare tranzacție — testul statistic (medie/bootstrap pe seria `net_R`) nu cere un orizont uniform, tratează fiecare tranzacție ca o observație, oricare ar fi motivul ei de ieșire (TP1/TP2/stop/breakeven/timeout). Ce TREBUIE raportat, obligatoriu: distribuția orizonturilor realizate (deja cerut în mandatul anterior), ca diagnostic, nu ca parte a testului.

**Punct tehnic nou, rezolvat acum:** orizontul MĂSURAT variază, dar e MĂRGINIT SUPERIOR de 20 de bare (`min(entry+20, EOD)` — niciodată mai mult de 20). Pentru acoperirea oracolului (L>=H), asta înseamnă H de referință rămâne **20** (cazul cel mai defavorabil/lung posibil), identic cu LM-001 — orizontul variabil NU strică validarea L>=H=20 deja stabilită, pentru că adevărata fereastră de dependență nu poate depăși niciodată acest maxim. **Oracolul acoperă corect această ipoteză la L>=28, ca la S1-S13.**

## Familia de corecție: SEPARATĂ, family=1

Construcția (DemandZone/OB compus, risc ATR, ieșire parțială) e structural distinctă de grammatica Open-R (S1-S20) — nu o variantă apropiată a vreunei familii existente (spre deosebire de SMC_S1_v2, care justifica family-of-2 CU S1 tocmai pentru că reutiliza aceeași descoperire pentru o ipoteză aproape identică). **Family=1, separată de familia-24 a Blocului 3.**

## Pre-înregistrare formală, cele cinci criterii

1. **Prag numeric:** `H0: μ_netR<=0` vs `H1: μ_netR>0`, unilateral, BH-FDR α=0,05, family=1.
2. **Orizont ca bare:** VARIABIL, `min(entry+20, EOD)` — H de referință pentru oracol = 20 (marginea superioară), consecvent cu L>=28.
3. **Populație:** confirmată NEGOALĂ — 89,75% din cele 130.491 bare de descoperire M15_v2 depășesc podeaua ATR de $0,857 (pe lângă condiția de intrare compusă DemandZone×OB, care va reduce populația efectivă în continuare — numărul exact de tranzacții eligibile rămâne de măsurat la execuție, nu presupun o cifră).
4. **Prag de clasificare:** α=0,05, family=1, separat de familia-24.
5. **Zero parametri liberi:** toate elementele fixate sau declarate explicit ca alegere (0,7/1,4/2,1 ATR), inclusiv Blocul 1 (scanare de la formation_idx+2) și Blocul 2 (Q2/Q3/Q4) acum rezolvate — nimic rămas nedecis care ar afecta execuția.

**AWAITING VALIDATION_ENGINE_CODE.** Nu execut, nu rulez ipoteza — doar specific complet.

---

**Nimic re-rulat suplimentar în acest document dincolo de re-verificarea independentă a cifrelor deja livrate de VE. Publicat pe `statistician-foundation`; manifestul se incrementează.**
