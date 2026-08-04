# STATISTICIAN — BINNING DE VOLATILITATE PENTRU COLECTAREA DE SPREAD, ȘI O RETRAGERE A PROPRIEI MELE CERINȚE

**Document ID:** STAT-SPREAD-VOL-BINNING-SPEC-v1.0
**Data:** 2026-08-04 · **Autor:** Statistician

**Verificare de sursă:** citit direct `ai_trader/spread_collection/{types,observer,observing_rule,journal}.py`. **Două măsurători noi, proprii, P&L-oarbe** pe datele de descoperire (130.477 bare utilizabile). **Concluzia principală contrazice cerința pe care am formulat-o eu la v2.7.37.**

---

# PARTEA 0 — CE E CONSTRUIT E CORECT. Golul nu e binning-ul.

**Colectorul face deja lucrul greu, și îl face bine:** o observație per bară M15 ÎNCHISĂ (nu eșantionare pe orar), `atr` persistat, sesiunea din `market_state.sessions` ratificat, `day_boundary_label` pe ancora 17:00-NY, și `is_level_touch` calculat din `detect_level_touches` REAL — nu un proxy.

**Trei constatări despre starea raportată, înainte de orice specificație:**

```
1. „atingeri PDH/PDL marcate: ZERO" NU e un defect.
   Măsurat: atingerile sunt 1.341 / 130.477 bare = 1,03% dintre bare.
   Pe 16 bare, numărul AȘTEPTAT e 0,16. Zero e exact ce trebuia să iasă.

2. Golul real e UPTIME-ul, nu stratificarea.
   O zi are ~92 de bare M15 (constanta empirică proprie a laboratorului).
   16 observații = ~17% uptime. La 17%, ORICE design durează de 6x mai mult.

3. `close` nu e persistat, dar `bid`/`ask` sunt ⇒ mid = (bid+ask)/2.
   Deci banda de mai jos se calculează din ce EXISTĂ. Fără modificare de schemă.
```

> **Prima recomandare, înaintea oricărei stratificări: uptime-ul valorează mai mult decât orice rearanjare a celulelor.** De la 17% la ~100% e o accelerare de 6×, gratuită statistic. Nicio schemă de eșantionare nu compensează un colector care rulează 4 ore pe zi.

---

# PARTEA 1 — PREMISA MEA PENTRU STRATIFICAREA PE VOLATILITATE E MĂSURABIL FALSĂ

**La v2.7.37 am cerut stratificare pe volatilitate cu un motiv explicit: „declanșatorii se aglomerează unde spread-ul se lărgește structural, deci eșantionarea calendaristică e părtinitoare ÎN JOS."** Era o afirmație despre lume. **Am măsurat-o. Nu se susține.**

```
bandă      % din BARE     % din ATINGERI PDH/PDL
LOW           50,0%              46,6%
MID           30,0%              34,1%
HIGH          20,0%              19,3%     ← declanșatorii NU se aglomerează în volatilitate mare
```

**Distribuția declanșatorilor pe axa volatilității e practic identică cu distribuția timpului.** Banda HIGH poartă 19,3% dintre atingeri față de 20,0% dintre bare — dacă ceva, e ușor SUB-reprezentată.

> **Consecința e directă și o consemnez împotriva propriei mele cerințe: dacă ponderile coincid, media condiționată și cea necondiționată coincid — indiferent cât de tare variază spread-ul cu volatilitatea.** Stratificarea pe volatilitate a fost cerută ca să corecteze o părtinire care, măsurat, nu există pe această axă. **Cade ca CERINȚĂ de eșantionare.**

## Pe axa SESIUNII, însă, părtinirea e reală — și acolo cerința se menține

```
sesiune    % din BARE     % din ATINGERI      diferență
asia         34,7%           42,7%             +8,0
london       21,7%           19,6%             −2,1
ny           34,3%           21,5%            −12,8
late          9,3%           16,1%             +6,8
```

**Asta e ponderarea care contează, și e cunoscută ACUM, din date de descoperire — nu trebuie așteptată.** Sesiunile se umplu zilnic, deci cerința pe sesiune costă zile, nu luni.

**Reziduu declarat onest:** în interiorul sesiunii NY mixul de volatilitate al atingerilor chiar se deplasează spre sus (LOW 24%→10% din atingerile NY). E singura sesiune unde reziduul e material, și NY poartă 21,5% din atingeri. **Se raportează, nu se presupune.**

---

# PARTEA 2 — ELEMENTUL 1: CÂTE BENZI ȘI CU CE GRANIȚE

## Variabila: ATR RELATIV (`atr14 / mid`), nu ATR absolut

**Motivul e o capcană concretă, nu o preferință.** Aurul a trecut de la ~1.200 la ~4.200 între descoperire și azi. **Un prag ATR în dolari, derivat pe 2011-2019, ar clasifica azi aproape totul în banda de sus.** ATR relativ e invariant la scară, deci granițe fixate pe date sigilate rămân valide la prețul de azi. E și forma adimensională a metricii oficiale de volatilitate a laboratorului (Parkinson `ln(H/L)`), nu o metrică nouă.

## Granițele — percentile ale distribuției de descoperire, MĂSURATE

```
ATR relativ (atr14/close), percentile pe 130.477 bare de descoperire, în puncte de bază:
  p10  6,03    p25  7,86    p50 11,04    p75 16,15    p80 17,81    p90 22,63    p95 27,94    p99 44,12

GRANIȚE FIXATE:   LOW  < 11,04 bp  <=  MID  < 17,81 bp  <=  HIGH
```

**De ce TREI benzi, nu două și nu cinci:** două benzi dau o diferență, dar nu o FORMĂ. Îngrijorarea aici e specific una de coadă — dacă costul explodează la volatilitate mare — iar minimul care poate distinge „crește liniar" de „explodează sus" e trei. Peste trei, doar timpul de umplere crește.

**De ce p50/p80 și nu terțile:** rezoluția se pune unde e riscul. Terțilele ar da praguri egale acolo unde nu e nimic de văzut; p80 izolează pătrimea superioară unde spread-ul chiar s-ar putea lărgi.

**De ce percentile de DESCOPERIRE și nu praguri inventate:** datele de descoperire sunt sigilate și **nu conțin nicio cifră de spread**. Granițele sunt deci fixate înainte de orice date de spread prin construcție, nu prin promisiune — aceeași garanție ca la filtrul de densitate (v2.7.41), unde măsurătoarea de calibrare era P&L-oarbă.

---

# PARTEA 3 — ELEMENTUL 2: CELULA, ȘI DE CE „25 PER CELULĂ" E PÂRGHIA GREȘITĂ

## Cerința de 25 pică — nu prin relaxare, ci pentru că a fost aplicată greșit

**25 vine din `N_MIN`, pe care eu însumi l-am definit ca prag de SUPRIMARE-LA-RAPORTARE, nu ca prag de putere.** Aplicat unei măsurători de cost, e o cerință de VARIANȚĂ. Dar varianța nu e constrângerea aici:

```
spread observat: min 0,05  max 0,09  majoritatea la 0,05   ⇒  SD ≈ 0,01
Distanța de decis: 0,05 măsurat  vs  0,10 modelat  =  0,05  =  5 ABATERI STANDARD.
SE la n=25 : 0,002.  SE la n=9 : 0,003.  Ambele mult sub distanța de decis.
```

> **Măsurătoarea nu e limitată de varianță — e limitată de REPREZENTATIVITATE.** A cere 25 per celulă e a aplica o soluție de varianță unei probleme de părtinire. **Multe celule cu puține observații bat puține celule cu multe.**

## Designul corect: POST-STRATIFICARE, nu eșantionare echilibrată

```
NU:  design echilibrat — umple fiecare celulă până la 25 de zile distincte.
     Necesar: fiecare celulă atinge un cvorum. Costul: luni.
DA:  post-stratificare — colectezi uniform în timp, apoi REPONDEREZI celulele
     cu ponderile de declanșare din Partea 1.
     Necesar: fiecare celulă are ACOPERIRE (>=1 observație), nu ECHILIBRU.
```

**Ponderile nu trebuie așteptate: le am deja, măsurate pe descoperire.** Post-stratificarea cere doar ca celulele să fie OBSERVATE, nu umplute — iar asta schimbă ordinul de mărime al așteptării.

**Cerința de acoperire, fixată:** ≥9 observații per celulă (SE ≈ 0,003, sub o zecime din distanța de decis), **fără cerință de zile distincte pe celulă** — cerința de zile distincte rămâne la nivelul ORIZONTULUI, nu al celulei (Partea 6).

## Ce ar fi costat designul echilibrat — măsurat, nu estimat

```
celula        % din zile în care apare      zile de uptime COMPLET până la 25 de zile distincte
ny x HIGH              70,0%                          36   (~7 săptămâni)
london x HIGH          27,7%                          90   (~18 săptămâni)
asia x HIGH            17,9%                         140   (~28 săptămâni)
late x HIGH            16,2%                         154   (~31 săptămâni)  ← constrângerea
```

**Designul echilibrat pe 12 celule cere ~154 de zile de tranzacționare cu uptime COMPLET — circa 7 luni. La uptime-ul curent de 17%, ar fi ~3,5 ani.** Estimarea de „~5 săptămâni pentru o singură celulă" e corectă pentru cazul nestratificat; stratificarea completă o multiplică de ~6 ori, și încă o dată de 6 prin uptime.

---

# PARTEA 4 — ELEMENTUL 3: CELULELE CARE NU SE UMPLU NICIODATĂ

**Regula, în trei părți, cu o distincție care e chiar miezul:**

```
1. O celulă goală NU e un gol de așteptat — e o MĂSURĂTOARE, dacă e goală pentru că
   e rară. Ponderea ei de declanșare e mică, deci contribuția ei la media ponderată e mică.
2. DAR: absența observației nu e absența evenimentului. O celulă poate fi goală pentru că
   piața n-a produs-o, SAU pentru că colectorul nu rula atunci — iar la 17% uptime a doua
   variantă e cea probabilă. ⇒ OBLIGATORIU: uptime per sesiune (bare observate / bare
   așteptate) jurnalizat, ca golul să poată fi ATRIBUIT.
3. La ORIZONT (Partea 6), o celulă tot goală se declară NEGLIJABILĂ-CA-FRECVENȚĂ,
   ponderea ei se redistribuie, iar EXCLUDEREA se raportează cu ponderea ei de declanșare.
   Nu se așteaptă la nesfârșit.
```

**Distincția din punctul 2 e exact cea dintre ARHIVAT-NEGATIV și ARHIVAT-INSUFICIENT (v2.7.42): absența dovezii nu e dovada absenței.** Fără jurnal de uptime, cele două cauze sunt indistinguibile și celula goală nu spune nimic.

## Obiecția pe care mi-o fac singur, și cum se închide

**`late × HIGH` și `asia × HIGH` sunt celulele cele mai lente ȘI cele mai suspecte** — sesiuni subțiri cu volatilitate mare e exact unde spread-ul ar exploda. A le declara „neglijabile" pentru că sunt rare în TIMP ar fi o eroare.

**Dar contează rare în DECLANȘATORI, nu în timp. Măsurat: `late × HIGH` = 2,4% din atingeri, `asia × HIGH` = 3,1%.** Împreună 5,5%. **Mărginit: chiar dacă spread-ul acolo ar fi TRIPLU față de restul, media ponderată se deplasează cu ≤11% din bază** — de la 0,05 la ~0,056. Nu schimbă nicio decizie. **Obiecția e reală și e mărginită numeric, nu respinsă prin asigurări.**

---

# PARTEA 5 — ELEMENTUL 4: EȘANTIONUL CARE CONTEAZĂ

## Nu se stratifică — nici la fel, nici separat. Și motivul e logic, nu practic.

**Stratificarea există ca să REPONDEREZE un eșantion calendaristic către distribuția declanșatorilor. Un eșantion luat LA declanșator e deja din acea distribuție — nu are ce să repondereze.** Marcajul `is_level_touch` face exact asta, per bară, corect.

**Și practic e imposibil oricum:** ~1,03% dintre bare, ≈1 atingere/zi. Împărțită pe 12 celule, ar cere ani per celulă. **Deci: eșantion de declanșare POOL, nesegmentat.**

## Câte sunt necesare

```
Precizia nu e constrângerea (SD ~ 0,01, distanța de decis 0,05).
CERINȚA: >=25 de atingeri, provenind din >=15 zile distincte.
  25 de atingeri  ⇒ SE ~ 0,002.
  >=15 zile       ⇒ nu toate dintr-un singur regim de piață de o zi.
La uptime COMPLET: ~1 atingere/zi ⇒ ~25-35 de zile de tranzacționare. La 17%: ~5 luni.
```

**Ceea ce livrează eșantionul de declanșare nu e doar o medie — e TESTUL PREMISEI MELE, pe date live:**

```
dacă  media(spread | atingere)  ~=  media(spread | toate barele)
      ⇒ părtinirea de care mă temeam la v2.7.37 e nulă și LIVE, nu doar pe descoperire,
        iar eșantionul calendaristic e suficient prin el însuși.
dacă  media(spread | atingere)  >>  media(spread | toate barele)
      ⇒ premisa se ține live deși nu se ține pe descoperire, iar stratificarea revine.
```

**Ambele ieșiri sunt informative, iar cea care mă contrazice se raportează la fel de clar ca cealaltă.**

---

# PARTEA 6 — ÎNTREBAREA DE REALISM. Răspunsul meu: cerința inițială NU e proporțională.

**Mi s-a cerut să spun dacă cerința e proporțională cu ce se poate obține. Nu e — și nu din cauza timpului, ci din cauza a ceea ce poate atinge măsurătoarea în principiu.**

## Plafonul: colectarea asta poate corecta cel mult JUMĂTATE din constantă

```
cost_round_trip = 0,20 = effective_spread 0,10  +  slippage 0,10
                                    ↑                    ↑
                          măsurabil prin cotații    NU e măsurabil prin cotații
                                                    (cere ordine EXECUTATE vs preț intenționat;
                                                     a fost fixat = spread prin CONVENȚIE, v2.7.37)

CEL MAI BUN caz al acestei colectări:  0,10 → ~0,05.  Total: 0,20 → 0,15.  NU 0,20 → 0,05.
```

## Ce cumpără asta, în R — și răspunsul e „aproape nimic din ce contează"

```
economie 0,05$/tranzacție ; R ~ 1xATR ~ 2$ în epoca de descoperire  ⇒  0,025 R/tranzacție

Verificarea mea de robustețe de la v2.7.42 folosea 0,075 R (cazul optimist 0,20→0,05).
La 0,025 R:  NICIUNUL dintre cei 11 candidați arhivați-negativ nu se mișcă. Nici pe aproape.
Se mișcă doar banda marginală:
  CAND-0017  −0,013 → +0,012   ← singurul care traversează zero
  CAND-0031  −0,047 → −0,022
  CAND-0026  −0,067 → −0,042
  CAND-0030  +0,043 → +0,068
```

> **Șapte luni de colectare stratificată ca să muți estimarea punctuală a UNUI candidat peste zero — un candidat deja programat la test formal, care va folosi oricum constanta curentă la momentul rulării. Asta e disproporționat, și o spun clar.**

## Forma mai slabă care răspunde totuși la întrebare: DOMINANȚĂ, nu estimare

**Întrebarea CEO nu e „cât e E[cost | declanșator]". E „e costul real sub 0,20". Aceea e o inegalitate, iar inegalitățile au o proprietate pe care estimarea nu o are:**

```
E[cost | declanșator] = Σ_c w_c · μ_c   <=   max_c μ_c

⇒ dacă MAXIMUL pe celule e sub prag, ORICE ponderare e sub prag,
  și distribuția declanșatorilor NU mai trebuie cunoscută deloc.
```

**Asta elimină integral problema reponderării — deci și motivul principal al stratificării.** Designul devine unul care ȚINTEȘTE COLȚUL CEL MAI RĂU în loc să echilibreze douăsprezece celule.

### Protocolul propus, cu regula de decizie fixată ACUM

```
ORIZONT      20 de zile de tranzacționare cu uptime >= 90%.  (NU 154.)
COLECTARE    neschimbată — colectorul e deja corect. Se adaugă DOAR:
               (a) jurnal de uptime per sesiune;
               (b) banda derivată la citire din atr/mid (fără schimbare de schemă).
RAPORT       media si p95 per celula sesiune x banda + numarul de observatii;
             ponderile de declansare din Partea 1; media post-stratificata;
             media pe subesantionul de atingere, alaturi de cea calendaristica.

REGULA DE DECIZIE, pre-declarata:
  A. max_c medie_c < 0,10  SI  p95 global < 0,10
     ⇒ jumatatea de SPREAD e supra-modelata sub ORICE ponderare. Se corecteaza la valoarea
       post-stratificata. Jumatatea de SLIPPAGE ramane 0,10 prin conventie, NEMASURATA.
  B. vreo celula >= 0,10
     ⇒ dominanta esueaza, reponderarea redevine necesara, si ATUNCI merita stratificare
       completa — dar pe celula care a esuat, nu pe toate douasprezece.
  C. media(spread|atingere) >> media(spread|calendar)
     ⇒ premisa mea de la v2.7.37 se tine LIVE; stratificarea revine integral.
```

**Ce trebuie ca să vreau designul complet, spus înainte, nu după: ieșirea B sau C.** Nu „dacă rezultatul arată interesant".

## Verdictul pe proporționalitate, delimitat

```
JUMĂTATEA DE SESIUNE a cerinței mele:      PROPORȚIONALĂ. Părtinire reală (+8 asia, −12,8 ny),
                                            cost în zile, ponderi deja cunoscute. Se menține.
JUMĂTATEA DE VOLATILITATE:                  NU e proporțională. Premisa care o justifica e
                                            măsurabil falsă (19,3% vs 20,0%). Cade ca cerință
                                            de eșantionare; rămâne câmp raportat, gratuit.
CERINȚA DE 25 PER CELULĂ:                   CADE. Era o cerință de varianță pe o problemă de
                                            părtinire, într-un design care nu mai e echilibrat.
```

**Nu e o relaxare de conveniență pentru că așteptarea e lungă. Cade pentru că am măsurat lucrul pe care îl controla și nu e acolo.** Dacă măsurătoarea ieșea invers, cerința ar fi rămas, cu tot cu cele șapte luni.

---

## HANDOFF

**AI Trader:** (1) **uptime la ≥90% — asta valorează mai mult decât orice altceva din documentul ăsta**, plus jurnal de uptime per sesiune; (2) banda derivată la citire din `atr/mid` cu granițele 11,04 / 17,81 bp — fără schimbare de schemă; (3) raportul din Partea 6 la orizontul de 20 de zile, cu numărul de observații per celulă ÎNAINTE de orice medie. **Nu se raportează percentile pe celule sub 9 observații** — refuzul de a raporta percentile la n=16 a fost corect și devine regulă.
**VE:** reverifică independent cele două măsurători (percentilele ATR relativ; ponderile de declanșare pe bandă și pe sesiune) — reproductibile prin construcție, dar regula rămâne verificarea independentă.
**Red Team:** ținta explicită e Partea 1 — dacă ponderile de declanșare măsurate pe descoperire sunt un ghid valid pentru comportamentul live, și dacă argumentul de dominanță din Partea 6 are o portiță.
**CEO:** o singură cifră de reținut — **plafonul acestei colectări e 0,20 → 0,15, nu → 0,05**, pentru că jumătatea de slippage nu e măsurabilă prin cotații. Asta mărginește ce merită cheltuit pe ea.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.44 (commit `90c9cff`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
