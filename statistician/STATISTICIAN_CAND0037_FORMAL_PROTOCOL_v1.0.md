# STATISTICIAN — PROTOCOL FORMAL: CAND-0037 (WEEKLY-LEVEL BREAKOUT)

**Document ID:** STAT-CAND0037-FORMAL-PROTOCOL-v1.0 · **Data:** 2026-08-11 · **Autor:** Statistician
**Verificare de sursă:** citit `dfadc04` integral, `CANDIDATE_QUEUE.md` liniile 63/91/120-133, și propriile mele hotărâri de la v2.7.45 (domeniul oracolului) și v2.7.48 (familia monotonă).

**Cifrele din mandat se confirmă VERBATIM** (n=246, win 50,8%, avg_R +0,062, median +0,013, PF 1,302, best-share 17%, trimmed +0,043 / PF 1,21, 7/8 ani). **Nu am găsit nicio discrepanță.**

> **Dar am găsit TREI lucruri care nu sunt în mandat, iar două dintre ele BLOCHEAZĂ verdictul formal. Le pun înaintea protocolului, fiindcă protocolul nu se poate executa fără ele.**

---

# PARTEA 1 — ÎNTREBAREA 1: se aplică oracolul? Da, dar întrebarea e pusă pe axa greșită.

**Mandatul spune: „CAND-0037 folosește stopul cel mai structural dintre toate — o gamă săptămânală. Verifică dacă oracolul se aplică." Îmi corectez propriul limbaj din v2.7.45, care a produs această citire: am scris „stopuri structurale" ca și cum ar fi un domeniu. Nu e. Tot acolo am și demonstrat de ce:**

```
v2.7.45, verbatim: „«stopuri structurale» NU e o unitate de domeniu validă. Extrema barei de
atingere, fitilul de sweep, podeaua OB și marginea FVG produc distribuții R DIFERITE."
```

**Axa care contează e MECANISMUL, pe care l-am documentat tot acolo:**

```
stop structural → distanța de risc poate fi ~0 → R = pnl/risc EXPLODEAZĂ → statistica e
dominată de câteva observații → eroarea de acoperire a bootstrap-ului crește cu ASIMETRIA.
```

> **Deci nu „cât de structural" e stopul, ci **cât de MIC** poate deveni. Stopul lui CAND-0037 e gama săptămânală ÎNTREAGĂ — distanța de risc MAXIMĂ posibilă din tot proiectul, deci mecanismul de explozie a lui R e ABSENT prin construcție. Cifrele o confirmă independent: best-share 17% (nu 78/35/22%), mediană POZITIVĂ, supraviețuiește tăierii.**
>
> **CAND-0037 nu e candidatul cel mai EXPUS la nepotrivirea de domeniu. E cel mai puțin expus dintre toți. Predicția mea e că trece precondiția lejer — dar e o PREDICȚIE, nu un rezultat, și precondiția se rulează oricum.**

**Precondiția e cea deja ratificată la v2.7.45, neschimbată, nu una nouă:**

```
(1) distribuția net_R per tranzacție a lui CAND-0037 din screening (cu floor, cu cost) — artefact EXISTENT
(2) centrare pe medie → nul cu zero cunoscut, care păstrează forma, asimetria și punctul de masă al floor-ului
(3) >= 1.000 serii sintetice pe grila CALENDARISTICĂ a lui CAND-0037
(4) FPR@0,05 al oracolului sub blocare pe ZI
(5) POARTĂ: limita superioară CI pe FPR <= 0,07. Peste — CAND-0037 NU primește p-value.
```

**Numărul de blocuri (S-R2, pragul meu de la v2.7.45: ≥10 minim, ≥20 preferat): 246 breakout-uri săptămânale pe 8 ani se întind pe câteva sute de zile distincte. Pragul e satisfăcut cu mult. NU e constrângere aici.**

---

# PARTEA 2 — ÎNTREBAREA 2: n=246. Ce se poate și ce NU se poate concluziona.

**Derivez deviația standard din agregatele raportate (nu o presupun):**

```
PF = 1,302 și avg_R = +0,062 pe n=246  ⇒  câștig brut 65,75R, pierdere brută 50,50R
win 50,8%  ⇒  câștig mediu +0,526R   pierdere medie −0,417R
SD MINIMĂ POSIBILĂ (distribuția în două puncte, cea de varianță minimă cu aceste medii):
        SD_min = √(0,508 × 0,492) × (0,526 + 0,417) = 0,4714
```

**Efectul minim detectabil, la pragul BH de rang 1 cu m=19 (Partea 3), α unilateral = 0,05/19 = 0,00263, z = 2,79:**

```
SE = SD / √246 = SD / 15,684
MDE = 2,79 × SD / 15,684 = 0,1779 × SD
MDE la SD_min = 0,1779 × 0,4714 = 0,0839 R/tranzacție
```

> # **OBSERVAT +0,062 < MDE 0,0839. Sub pragul de detecție CHIAR ȘI la varianța minimă teoretic posibilă.**
>
> **SD-ul real e mai mare decât 0,4714 (există dispersie în interiorul câștigurilor și pierderilor), deci MDE-ul real e mai mare, deci decalajul e mai larg decât arată. Efectul tăiat (+0,043) e și mai departe.**

**Pre-declar, ÎNAINTE de orice rulare, ca să nu fie citit greșit după:**

```
SE POATE CONCLUZIONA        un interval de încredere pe expectanță — informativ și publicabil;
                            că oracolul e calibrat pe ACEST candidat (precondiția);
                            că datele NU SUNT INCOMPATIBILE cu un edge de mărimea observată.
NU SE POATE CONCLUZIONA     o RESPINGERE a H0. E aproape imposibilă prin construcție, nu prin
                            slăbiciunea candidatului.
CE AR FI O CITIRE GREȘITĂ   „CAND-0037 a fost testat formal și a picat." La această populație,
                            NE-RESPINGEREA E REZULTATUL AȘTEPTAT ȘI NU E DOVADĂ ÎMPOTRIVA LUI.
```

**Populația necesară pentru ca efectul observat să devină detectabil:**

```
n = (2,79 × SD / 0,062)²   ⇒   n ≈ 450 la SD_min,  ≈ 780 la SD = 0,6,  ≈ 990 la SD = 0,7
Adică de 2 până la 4 ORI populația actuală.
```

**Datele de descoperire sunt epuizate, iar holdout-ul e SIGILAT. Deci n suplimentar nu poate veni decât din acumulare ÎNAINTE — adică din Shadow, care e exact obiectivul fazei de integrare.**

---

# PARTEA 3 — FAMILIA. Nu se micșorează. Crește la 19.

**Mandatul spune: „Alpha a eliminat level-fade întreg — inclusiv CAND-0001... Deci CAND-0037 e singurul rămas. Familia se ajustează în consecință."**

> **Se ajustează, dar în SUS. Familia NU se micșorează, iar motivul e cel pe care l-am fixat la v2.7.48 și pe care l-am aplicat deja o dată contra propriului meu interes (CAND-0017 arhivat, slot NEreturnat).**

```
Eliminarea făcută de Alpha e ECONOMICĂ, adică BAZATĂ PE REZULTATE OBSERVATE.
A scoate din familie membrii pe baza rezultatelor lor e exact selecția pe care controlul
FDR există ca s-o prevină: „testează 16, raportează-l pe cel mai bun, corectează pentru 1".
În plus, PATRU dintre cei 16 au fost DEJA testați formal (verdictul 001). Sloturile lor sunt
consumate IREVERSIBIL — un p-value emis nu se retrage arhivând candidatul.
```

**Iar CAND-0037 nu adaugă UN slot, ci TREI. Motivul e în `dfadc04`, verbatim:**

```
„Executed the PRE-REGISTERED Route 2 ... on the same 3 level populations"
  · PDH/PDL break    avg_R +0,005, trimmed −0,023  → plat
  · session break    avg_R +0,007, trimmed −0,039  → plat
  · WEEKLY break     avg_R +0,062, trimmed +0,043  → CAND-0037
```

> **CAND-0037 e MAXIMUL A TREI populații pre-înregistrate. „Edge-ul e SPECIFIC săptămânalului" e formularea pozitivă a aceleiași observații: s-au încercat trei orizonturi, unul a mers. Un p-value pe maximul din trei, corectat ca și cum ar fi unul singur, are FPR de circa trei ori nominalul.**

```
FAMILIA:  m = 16  →  m = 19   (cele trei populații Ruta 2 intră ÎMPREUNĂ)
Pre-înregistrarea NU e o penalizare aici — e exact ce face corecția validă. Cele două plate
NU primesc protocol formal (sunt ARCHIVE-NEGATIVE prin triajul în trei rezultate), dar
RĂMÂN NUMĂRATE, fiindcă familia e monotonă.
Prag BH de rang 1:  0,05/19 = 0,00263  (față de 0,00294 la m=17)
```

**Și consemnez ce e mai important decât aritmetica: diferența dintre m=17 și m=19 e neglijabilă. La MDE 0,0839 față de un efect observat de 0,062, verdictul nu se schimbă la niciun m. AL DOILEA VERDICT AL PROIECTULUI VA FI, CA ȘI PRIMUL, LIMITAT DE PUTERE, NU DE MULTIPLICITATE. O spun acum ca să nu se caute vinovatul în corecție.**

---

# PARTEA 4 — CE NU E ÎN MANDAT (1): dependență NEGATIVĂ cu CAND-0006

**CAND-0006 (PWH/PWL, Ruta 3) și CAND-0037 (weekly breakout) folosesc ACELEAȘI niveluri săptămânale, în direcții OPUSE: unul face fade la nivel, celălalt tranzacționează ruperea lui.**

```
Poziții OPUSE pe bare comune  ⇒  dependență NEGATIVĂ  ⇒  PRDS ÎNCĂLCAT  ⇒  BH-FDR NU acoperă.
E EXACT problema pe care am rezolvat-o deja pentru perechea CAND-0001 / CAND-0009 (W-partition).
```

**Remediul e cel deja ratificat, reutilizat verbatim, NU unul nou:**

```
POPULAȚII DE TEST DISJUNCTE: populația de test a lui CAND-0006 exclude barele de breakout
al aceluiași nivel; măsurătoarea pe populația completă se raportează ALĂTURI, ca ediție a
costului. Politica NU se modifică — asta ar fi treaba Alpha.
Fracția de suprapunere se raportează per regim ÎNAINTE de orice test.
ALTERNATIVA, dacă disjuncția nu e posibilă: BY în loc de BH, la ~3,55x severitate pe m=19.
Prefer disjuncția — aceeași alegere, același motiv ca la CAND-0001/0009.
```

---

# PARTEA 5 — CE NU E ÎN MANDAT (2 și 3): două precondiții BLOCANTE

## 5.1 Detectorul de niveluri săptămânale nu e atacat de Red Team

**Mandatul de acum trei zile, decizie CEO, verbatim: „PWH/PWL — EXCLUS prin decizie CEO, până la ratificare completă. Detectorul e construit, `5443077`, dar NEATACAT de Red Team."**

> **CAND-0037 se sprijină pe ACELAȘI detector, la ACELAȘI commit. Aplic standardul CEO, nu unul inventat de mine: dacă `compute_prior_week_levels` nu e destul de ratificat ca să fie o TRĂSĂTURĂ în N3, nu e destul de ratificat ca să susțină un VERDICT FORMAL. BLOCANT până la atacul Red Team.**

## 5.2 Săptămâni COMPLETE vs PARȚIALE — condiționare nedeclarată

**La `e68e0cd` am stabilit, pe același detector: `completeness` se PROPAGĂ (COMPLETE și PARTIAL emise amândouă, NU filtrate în primitivă), 538 COMPLETE / 34 PARTIAL, iar poolarea ar umfla rata — o săptămână PARȚIALĂ are extreme pe mai puține zile, deci mai aproape de preț, deci atinsă mai des.**

```
`dfadc04` NU declară dacă cele 246 de breakout-uri sunt COMPLETE-only sau pooled.
OBLIGATORIU înainte de test: raportat separat pe cele două grupuri. Dacă e pooled, populația
e condiționată de un factor care afectează rata de atingere — și n=246 s-ar reduce.
```

---

# PARTEA 6 — PROTOCOLUL FORMAL

## 6.1 Ipoteza și estimandul

```
H0   E[net_R] <= 0   pe populația CAND-0037, parametrizarea din POLICY_WEEKLY_BREAKOUT_v1
H1   E[net_R] >  0   unilateral, coada DREAPTĂ
estimand: media per-tranzacție a net_R, cu costuri MODELATE (0,20 dus-întors) și
          min_executable_risk activ. NU o rată de câștig, NU un PF.
```

## 6.2 Protocolul temporal — ordinea e obligatorie și fiecare pas poate opri următorul

```
T0  PRECONDIȚII BLOCANTE          atac Red Team pe detectorul săptămânal (5.1)
                                  declarare COMPLETE/PARTIAL (5.2)
                                  ⇒ dacă vreuna cade, NU se trece la T1
T1  PARTIȚIE DISJUNCTĂ            vs CAND-0006 (Partea 4); fracția de suprapunere raportată
T2  PRECONDIȚIA DE CALIBRARE      v2.7.45, per candidat, poartă FPR CI-sup <= 0,07
T3  NUMĂR DE BLOCURI              zile distincte cu tranzacții >= 10 (>= 20 preferat)
T4  TESTUL                        calendar_block_bootstrap din restante_validation.py,
                                  bloc = ZI, B = 20.000, seed = sha256(candidate_id)[:8],
                                  p = (k+1)/(B+1)
T5  BH peste m = 19               prag de rang k = k × 0,05/19
T6  DIAGNOSTICE, raportate ORICUM ani pozitivi, regimuri pozitive, best-share, trimmed
```

**`schema_hash` peste: politica, m=19, cheia de partiție, W, seed, pragurile. Înghețat la T0. Orice modificare ulterioară e o ipoteză NOUĂ, cu slot NOU.**

## 6.3 Criteriul de succes — conjunctiv, pre-declarat

```
(a) precondiția de calibrare TRECE (FPR CI-sup <= 0,07)
(b) p <= pragul BH de rang k la m = 19
(c) semn pozitiv în >= 2/3 regimuri
(d) efectul TĂIAT la top-1% rămâne pozitiv        ← deja satisfăcut la screening (+0,043)
TOATE patru, altfel NU e promovare. (b) e cel care va cădea, prin putere.
```

## 6.4 Specificația exactă pentru VE

```
1. Extrage seria net_R per tranzacție a lui CAND-0037 din rularea `cand_level_breakout.py`
   (weekly_break), CU floor și CU cost. IMPORTĂ modulul; nu re-implementa detectorul.
2. Raportează, ÎNAINTE de orice test: n, SD, zile distincte, split COMPLETE/PARTIAL,
   suprapunerea cu populația CAND-0006.
3. Rulează precondiția de calibrare v2.7.45. Dacă poarta cade — STOP, fără p-value.
4. Rulează `calendar_block_bootstrap` cu parametrii de la 6.2. NU scrie un oracol nou.
5. Raportează p, CI pe expectanță, și MDE-ul realizat la SD-ul MĂSURAT.
6. NU emite verdict. Verdictul e al meu.
```

---

# PARTEA 7 — RECOMANDARE DE SECVENȚIERE. Protocolul e livrat; ordinea e a CEO.

**Protocolul de mai sus e complet și executabil. Dar consemnez, fiindcă e consecința directă a Părții 2:**

> **A rula testul acum consumă IREVERSIBIL trei sloturi de familie, pentru un rezultat pre-declarat drept ne-respingere. Familia e MONOTONĂ: pragul coborât nu se mai ridică pentru nimeni, niciodată.**

```
OPȚIUNEA A  se rulează acum. Se obține un CI publicabil și calibrarea. Cost: m 16 → 19,
            permanent, pentru un verdict cunoscut dinainte.
OPȚIUNEA B  se rulează T0-T3 acum (precondițiile, care nu consumă sloturi și care sunt
            oricum obligatorii), CAND-0037 intră în Shadow ca să ACUMULEZE, iar T4-T6 se
            execută la n >= 450, pre-declarat acum.
```

**Recomand B. Nu ca să evit un rezultat prost — un rezultat prost e pre-declarat oricum — ci fiindcă sloturile cumpărate acum nu cumpără nicio informație pe care B n-o dă mai târziu și mai bine. Decizia e a CEO; faptul de putere e al meu și e la Partea 2.**

**Și e coerent cu faza de integrare: obiectivul declarat e o oportunitate urmăribilă cap-coadă până la Shadow. CAND-0037 e primul candidat care merită să fie ACEA oportunitate.**

---

# PARTEA 8 — DESCHIS, CLASIFICAT

```
BLOCKING      detectorul de niveluri săptămânale, neatacat de Red Team (5.1)
BLOCKING      declararea COMPLETE vs PARTIAL (5.2)
BLOCKING      partiția disjunctă față de CAND-0006 — fără ea BH e invalid pe pereche (Partea 4)
MATERIAL      precondiția de calibrare per candidat — obligatorie, dar prezic că trece
MATERIAL      m = 16 → 19, nu → 17. Cele trei populații Ruta 2 intră împreună.
MATERIAL      puterea: efect observat 0,062 < MDE 0,0839 chiar la varianța minimă teoretică
LIMITATION    SD derivat din agregate, nu măsurat. VE îl raportează; MDE se recalculează.
LIMITATION    verdictul va acoperi parametrizarea testată, pe datele de descoperire, cu
              costuri modelate. Holdout SIGILAT și neatins.
NON-MATERIAL  2020 negativ din 8 ani — 7/8 e stabilitate, nu fragilitate; se raportează.
NON-MATERIAL  cost-robustețea (stopul ≫ spread) e reală, dar costul REALIZAT rămâne nemăsurat
              până când colectarea de spread se încheie.
```

**Nu cere: gate nou, framework nou, oracol nou, primitivă nouă. Precondiția de calibrare, blocarea calendaristică, partiția disjunctă și triajul în trei rezultate există toate deja și se reutilizează verbatim.**

---

**Manifest:** `config/split_manifest.json` v2.7.62, secțiunea `cand0037_formal_protocol_v2_7_62`.
