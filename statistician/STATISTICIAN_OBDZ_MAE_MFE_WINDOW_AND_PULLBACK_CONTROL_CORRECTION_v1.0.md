# STATISTICIAN — CORECȚIA FERESTREI DE MĂSURARE ȘI A BRAȚULUI DE CONTROL LIPSĂ (OBDZ)

**Document ID:** STAT-OBDZ-MAE-MFE-WINDOW-PULLBACK-CONTROL-CORRECTION-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

**Verificare de sursă:** citit integral `code/obdz_mae_mfe_control.py` (comitul `b233c83`) — implementarea corespunde exact specificației mele anterioare (`v2.7.14`, `47d742a`). `mypy --strict` curat. **Rulat direct** — cifrele CEO citate reproduse exact: `bar_MAE` mediană 35,0 (bear)/32,0 (bull)/41,0 (corecție); `bar_MFE` mediană 41,0 (bear)/45,0 (bull)/35,5 (corecție) — toate în intervalul „a doua zi", nu „reacție imediată". Zonă vs control aproape indistincte pe agregatul de 92 bare (MAE mediană 4,40 zonă vs 4,82 control; MFE mediană 4,67 zonă vs 4,46 control) — confirmat exact tiparul „comparație oarbă prin construcție".

**Ambele erori sunt ale mele, confirmate direct de propria verificare, nu doar acceptate pe cuvânt.**

---

# EROAREA 1 — fereastra de 92 bare măsura altceva decât reacția

## Confirmare aritmetică

92 de bare = ziua empirică (derivată la Mandatul 3.18/3.19, pentru compresia/fereastra de volatilitate — un scop COMPLET diferit). Verificat direct: medianele barelor de atingere (32-51 pentru MAE, 35-45 pentru MFE) cad toate în a doua parte a ferestrei — mișcări de „a doua zi", nu reacție la zonă. **Ai dreptate: MAE=4,4×ATR pe 92 de bare nu înseamnă „prețul merge 4,4 împotriva ta după ce intri" — înseamnă „în următoarele ~23 de ore, prețul oscilează cu 4,4×ATR", adevărat pentru orice punct.** Exact de-asta zona și controlul ies aproape identice — măsura nu conținea informație despre zonă, prin construcție, indiferent ce am fi comparat cu ea.

## Ferestre corectate, specificate mecanic

**Notație duală, pentru zero ambiguitate la implementare:** `t` = bara de atingere a zonei (Mitigation calificată); `entry = t+1` (convenția deja existentă în `obdz001.py`, neschimbată). Tabelul CEO (`bara 0`=atingere=`t`; `bara +1`=„încă în zonă"=`entry`; `bara +2`=„începe reacția"=`entry+1`) se traduce astfel:

```
notație CEO (relativ la t)   ==   indici absoluți (relativ la entry, convenția codului)
[t+2, t+3]                   ==   [entry+1, entry+2]      (2 bare)
[t+2, t+5]                   ==   [entry+1, entry+4]      (4 bare)
[t+2, t+10]                  ==   [entry+1, entry+9]       (9 bare)
[t+2, t+20]                  ==   [entry+1, entry+19]      (19 bare, orizontul real de tranzacționare)
```

**Prețul de referință pentru MAE/MFE rămâne `entry_price`** (prețul real de intrare) — se schimbă DOAR care bare se scanează pentru extreme (începând de la `entry+1`, sărind bara de intrare însăși, care încă reflectă atingerea zonei, nu reacția). ATR-ul normalizator rămâne `ATR14[t]`, neschimbat.

**Fereastra scurtă [+2,+5] e cea DECISIVĂ, cum ai spus explicit:** „dacă zona produce ceva, se vede la +2 până la +5; dacă nu se vede acolo, nu se vede nicăieri." Celelalte trei (+3, +10, +20) sunt context/confirmare, nu criteriul principal.

## Fereastra de 92 bare: PĂSTRATĂ, relabelată — decizia mea, cerută explicit

**Păstrez rezultatul de 92 bare, cu domeniul corectat explicit: „profil de VOLATILITATE GENERALĂ pe ~1 zi de tranzacționare după punctul de intrare (zonă vs control aliniat pe bias), NU o măsură de reacție imediată."** Nu-l retrag — nu e greșit, e greșit ETICHETAT în specificația mea inițială. Ca rezultat corect scopat, spune ceva legitim (deși mai puțin interesant): OBDZ nu arată o volatilitate neobișnuită pe orizont de o zi față de un control aliniat pe bias. Marcat acum explicit ca să nu fie recitit peste șase luni ca „reacție la zonă".

---

# EROAREA 2 — brațul C, retragere fără zonă, specificat mecanic

## Confirmare a problemei

De acord: brațul B (aliniat pe bias) izolează corect contribuția DEMANDZONE×OB față de simpla aliniere de bias — dar NU izolează efectul „intrarea e, prin construcție, la o RETRAGERE" (Mitigation = atingerea unei zone situate contra direcției mișcării recente). B include orice bară aliniată pe bias, inclusiv la maxime locale (zero retragere). **Comparația A vs B confundă două lucruri: contribuția zonei ȘI faptul că A e mereu la o retragere.** Dacă retragerile în trend se comportă structural mai prost decât intrările la întâmplare (plauzibil — cumperi în timp ce prețul cade), „zonă ≈ aleatoriu" ar putea ascunde de fapt „zonă > retragere simplă". Designul actual nu poate distinge asta — corect diagnosticat.

## Adâncimea de retragere, definită mecanic — reutilizează primitiva deja stabilită

**Nu invenez o fereastră rulantă nouă — reutilizez `market_structure.py` Swing/StructureLabel**, EXACT primitiva deja folosită la Măsurătoarea A de la SMC_S1_v2 („swing-ul major precedent"). Definiție: pentru o bară `j` cu bias BULLISH, `pullback_depth(j) = (preț_swing_HIGH_clasificat_precedent − preț[j]) / ATR14[j]`, unde swing-ul e cel mai apropiat swing HIGH CLASIFICAT (orice `StructureLabel`, nu doar HH/LH), strict anterior lui `j`, în ACELAȘI bloc de descoperire (D4). Simetric pentru bias BEARISH (swing LOW precedent, `pullback_depth=(preț[j]−preț_swing_LOW)/ATR14[j]`).

**Caz de margine, tratat explicit, nu ascuns:** dacă nu există niciun swing clasificat de tipul corect în bloc înainte de `j`, `pullback_depth` e NEDEFINIT — bara respectivă e EXCLUSĂ din construcția brațului C (și din comparația A-vs-C, vezi mai jos), numărul exclus raportat separat, nu tratat ca zero.

## Brațul C — construcție mecanică

**Populația-sursă:** ACEEAȘI colecție „aliniat pe bias" folosită la brațul B (35.454/37.707/17.145 bare/regim), MINUS cele 275/223/156 bare care sunt ele însele declanșatoare de zonă (excludere directă, nu doar o rază de siguranță).

**Potrivire, per declanșator de zonă cu `pullback_depth_A` definit:** candidați = barele din populația-sursă (excluzând declanșatoarele) cu `pullback_depth` în banda `[pullback_depth_A − max(0,25×pullback_depth_A, 0,5×ATR), pullback_depth_A + max(0,25×pullback_depth_A, 0,5×ATR)]` — tolerantă relativă de 25% SAU absolută de 0,5×ATR, oricare e mai LATĂ (convenție declarată, nu derivată — analogă altor praguri pragmatice din acest lab, ex. `n≥25`). **Dacă nicio candidată nu cade în bandă, se lărgește progresiv** (dublând banda) până la un plafon dur (±100%/±2×ATR) — declanșatoarele rămase nepotrivite la plafon se raportează EXPLICIT ca „nepotrivite", nu se elimină tăcut și nu se forțează o potrivire artificială.

**Selecție:** o candidată aleasă ALEATORIU (fără înlocuire în cadrul regimului, sămânță `20260729+regim_index` — aceeași convenție deja folosită la brațul B) dintre cele calificate, per declanșator.

**Mecanica de intrare pentru brațul C, identică cu A/B:** `entry = bara_aleasă+1`, `direcție = bias`, `ATR = ATR14[bara_aleasă]`, `preț_intrare = open[entry]` — se schimbă DOAR criteriul de selecție, nu mecanica de măsurare.

## Comparația A-vs-C: pe subsetul cu `pullback_depth` definit, declarat explicit

**Brațul A, pentru comparația cu C, se restrânge la subsetul de declanșatoare cu `pullback_depth_A` definit** (poate exclude câteva, cf. cazului de margine de mai sus) — comparație curată pe ACEEAȘI populație de bază. **Brațul A „complet" (toate cele 275/223/156, deja măsurat)** rămâne valabil neschimbat pentru comparația A-vs-B (nu depinde de `pullback_depth`). Ambele „A" se raportează, etichetate distinct („A_full" vs „A_subset_matched"), ca să nu se confunde.

---

# GRILA DE INTERPRETARE — pre-înregistrată, pe MFE median la ferestrele [+2,+5]/[+2,+10] ca prag principal

```
A_subset ≈ C, ambele > B_matched         (diferență mediană MFE < 15% între A și C, ȘI
                                           A și C fiecare > B cu >25%)
  -> RETRAGEREA contează, ZONA nu adaugă nimic dincolo de ea. Se închide unghiul specific
     zonei (DemandZone×OB) — ideea de „retragere simplă, fără zonă" rămâne o direcție
     posibilă, distinctă, NEdecisă aici.

A_subset > C                              (A > C cu >25% în MFE median)
  -> ZONA adaugă ceva peste retragere. Confirmarea (Varianta 3) merită investigată mai
     departe.

A_subset ≈ C ≈ B                          (toate trei în bandă de 15% unele de altele)
  -> NICI retragerea, NICI zona nu contează la ferestrele scurte. Linia OBDZ se închide
     integral, nu doar unghiul zonei.

Orice alt tipar                          -> TESTABLE BUT INSUFFICIENT EVIDENCE, nicio
                                             concluzie prematură.
```

**Pragurile (15%/25%) sunt convenții declarate, nu derivate** — analog altor praguri pragmatice deja acceptate în acest lab. **Citirea principală se face pe ferestrele [+2,+5] și [+2,+10]** (cele mai informative pentru „apare o reacție devreme"); [+2,+3] și [+2,+20] se raportează ca context, nu ca prag de decizie.

---

# RĂSPUNSURI DIRECTE

**1. Specificația corectată** — de mai sus: trei brațe (A, B, C), patru ferestre noi de la +2, plus fereastra de 92 păstrată/relabelată.

**2. Verdictul OBDZ rămâne AMÂNAT.** Rezultatul de azi (zonă≈control pe 92 de bare) răspunde la o întrebare mai îngustă decât cea care conta — „zona bate o intrare oarecare aliniată pe bias, pe volatilitatea de o zi" — răspuns nu, dar nu e întrebarea centrală. Nu știm încă dacă zona bate o retragere simplă, și n-am măsurat deloc reacția imediată (+2 până la +20). Nicio concluzie de viabilitate până la corectate.

**3. Grila de mai sus** — scrisă acum, înainte de orice cifră din rularea corectată.

**4. Fereastra de 92: PĂSTRATĂ, relabelată** — decizia mea, cf. secțiunii dedicate de mai sus.

---

## Ce NU se schimbă

VE a executat exact ce am specificat — erorile sunt ale mele. Corect că a reținut Sarcina 2 (numărătoarea H1/H4) în loc s-o ruleze pe un semnal a cărui capacitate predictivă nu era stabilită — **rămâne reținută, condiționată de rezultatul măsurătorii corectate, neschimbat.**

---

**Nimic rulat suplimentar în acest document dincolo de re-verificarea independentă a rezultatului deja livrat. Publicat pe `statistician-foundation`; manifestul se incrementează.**
