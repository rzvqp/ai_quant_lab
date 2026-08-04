# STATISTICIAN — NIVELUL 2: BIAS PE H1. SPECIFICAȚIE

**Document ID:** STAT-LEVEL2-BIAS-H1-SPEC-v1.0
**Data:** 2026-08-04 · **Autor:** Statistician

**Verificare de sursă:** citit direct `code/liquidity_mechanics.py` (`build_pools`, `PoolTier`), `code/market_structure.py`, `code/market_state.py`. **Trei măsurători proprii, P&L-oarbe, făcute ÎNAINTE de propunere — cerința 3 a moștenirii.** Două dintre ele schimbă răspunsul.

---

# 1. SCOP ȘI ÎNTREBARE

**Întrebarea CEO: „care e direcția cu probabilitatea cea mai mare în următoarele ore?"**

> **Asta e o PREVIZIUNE, spre deosebire de nivelul 1 care era o clasificare.** Un clasificator determinist nu poate emite o probabilitate prospectivă: ar trebui ESTIMATĂ din istoric. **Iar estimarea din istoric e exact ce face nivelul 6.**

```
Dacă nivelul 2 ar emite o probabilitate proprie, ar exista DOUĂ estimatoare pe aceleași date.
Ori sunt de acord — și unul e redundant — ori nu sunt, și unul greșește.
```

**DECIZIA DE PROIECTARE: nivelul 2 emite FACTORI, nu probabilitate.** Cifra „Bias Long 72%" rămâne disponibilă — dar vine din căutarea nivelului 6 CONDIȚIONATĂ pe factorii nivelului 2, nu din nivelul 2. **Un singur estimator, o singură poartă, în tot sistemul.**

---

# 2. RĂSPUNS LA ÎNTREBAREA DE PROIECTARE: axă nouă sau rafinare?

## Descompunerea celor patru factori ceruți

```
+ higher lows          ← market_structure         PRIMITIVA AXEI DE STRUCTURĂ de la nivelul 1
+ displacement bullish ← expansion (E010)         PRIMITIVA BENZII HIGH_DIRECTIONAL de la nivelul 1
+ momentum pozitiv     ← NU EXISTĂ primitivă ratificată. Nu inventez una.
− lichiditate deasupra ← build_pools              vezi secțiunea 3
```

**Doi din patru sunt deja ÎNĂUNTRUL nivelului 1. Unul nu există. Al patrulea are o problemă proprie.**

## Dar măsurat, aceeași primitivă la altă rezoluție NU e o reformulare

```
direcția structurală H1 vs direcția structurală H4 (nivelul 1), pe 49.516 bare comparabile:
   ACORD pe semn: 66,39%     (H1 sus 53,4% | H4 sus 52,5%)
```

**Dezacord pe o treime din bare. Deci nivelul 2 e o RAFINARE ca CONSTRUCȚIE și o axă NOUĂ ca VALOARE.**

> **Ce adaugă H1 peste H4 e RECENȚĂ, nu informație nouă** — aceeași întrebare structurală pe o fereastră mai scurtă. E legitim pentru o întrebare despre „următoarele ore", dar se justifică AȘA, nu ca sursă nouă. **Și spun limita: dezacordul dovedește NEREDUNDANȚĂ, nu UTILITATE.** Dacă cele 33,6% de dezacord poartă edge se decide la nivelul 6, prin contracție — nu se afirmă aici.

---

# 3. „LICHIDITATE DEASUPRA": premisa din mandat e FALSĂ, dar factorul are altă problemă

## D2 NU blochează factorul. Verificat în cod.

**`build_pools` emite UN bazin PER SWING ETICHETAT — HH și LH produc bazine ABOVE. NU cere o pereche de maxime egale.** D2 restrânge ce swing-uri se formează (o egalitate nu produce swing), dar **nu blochează construcția bazinelor.** Factorul e construibil azi, cu primitive ratificate.

## Problema reală e SATURAȚIA, și e mai gravă decât la primitiva B

```
Măsurat pe H1: 13.292 swing-uri → 13.290 bazine, din care 6.755 ABOVE.

bazine ABOVE încă deasupra prețului, per bară:  median 474    max 2.916
dintre ele, în interiorul a 1×ATR:              median  10
bare cu ZERO bazine în 1×ATR:                    5,1%
```

> **„Există lichiditate deasupra" e adevărat pe 94,9% dintre bare. Ca factor, în forma cerută, e NEFALSIFICABIL prin saturație** — exact acuzația Red Team de la primitiva B (89-188 niveluri), aici la 474. **Bazinele se acumulează la nesfârșit: fiecare swing high din istorie rămâne.**

## Ce trebuie ca factorul să devină utilizabil — reutilizez ce e deja ratificat

```
1. DOAR bazine NECONSUMATE — `detect_sweeps` e ratificat; un bazin măturat nu mai e
   lichiditate în repaus. Consumare D7, o singură dată.
2. Filtru de PRAG pe distanță, nu de rang (v2.7.41: un rang nu poate returna mulțimea vidă,
   deci nu poate reface falsificabilitatea).
CRITERIU DE ACCEPTARE, pre-declarat: fracția barelor cu ZERO bazine eligibile trebuie să fie
   MATERIAL peste zero. Referință: primitiva B a ajuns la 83,6% cu k=1,0×ATR. Nu inventez un
   prag — pre-înregistrez precedentul măsurat ca punct de comparație.
```

---

# 4. VERIFICAREA DE REDUNDANȚĂ, făcută ÎNAINTE — și rezultatul e mai rău decât la nivelul 1

**`build_pools(swings)` primește swing-uri din `detect_swings` + `label_structure`. Deci factorul de lichiditate NU e independent de axa de structură — e o altă funcție a ACELUIAȘI set de swing-uri.**

```
factor                 primitivă        redundant cu declanșatorii care folosesc
higher lows            market_structure  S3, S11, MK-01 (CAND-0021/0022/0023)
displacement           expansion         CAND-0002, CAND-0008, CAND-0009
lichiditate deasupra   build_pools←swings  ORICE candidat pe market_structure  ← NOU, negăsit înainte
momentum               —                 nu există
```

> **Concluzie, spusă direct: ZERO dintre cei patru factori ceruți sunt complet independenți de primitivele pe care candidații deja declanșează. Singura axă genuin independentă din tot sistemul rămâne ȘTIRILE.** Nu e un motiv să nu construim nivelul 2 — e motivul pentru care fiecare factor poartă avertismentul de redundanță de la L-R1, atașat mecanic.

---

# 5. INPUTURI, OUTPUTURI, DEFINIȚII OBSERVABILE

```
INPUT      H1_from_M15_v2 (CONTEXT_DERIVED_VALIDATED)  +  RegimeState de la nivelul 1
           `h1_trend_up` NU se folosește: binar, fără magnitudine și fără status. Insuficient, confirmat.

OUTPUT     BiasState {
             factors: [ {name, value, status, primitive, redundant_with[]} ]
             direction_share_long / short   ← DESCRIPTIV pe fereastra recentă, etichetat `share`
             status: AVAILABLE | UNAVAILABLE
           }
           NU emite probabilitate prospectivă. Aceea vine de la nivelul 6.

DEFINIȚII OBSERVABILE (toate din primitive ratificate, toate pe bare ÎNCHISE)
  structure_run_h1   run cu semn din `detect_breaks` pe H1, propagat bară cu bară (identic nivelului 1)
  displacement_h1    `expansion` (E010) pe H1, cu direcția corpului
  liquidity_above    numărul de bazine ABOVE NECONSUMATE în interiorul pragului, la bara i−1
  momentum           ABSENT — cere primitivă nouă + ratificare, sau se scoate din listă
```

## Constantele, RE-DERIVATE în unități H1 (moștenirea 1)

```
media empirică H1, măsurată:   ZI = 23,08 bare      SĂPTĂMÂNĂ = 115,30 bare
                               (M15 era 92/460 ; H4 e 5,98/29,84)
NIMIC nu se transplantează. Orice fereastră a nivelului 2 se exprimă în aceste unități.
```

## Parametrii intră în `schema_hash` (moștenirea 2)

**Lista ordonată a factorilor, primitiva fiecăruia, pragurile lui, ferestrele, și versiunea codului — toate în `schema_hash`, pre-înregistrate în manifest ÎNAINTE de prima decizie, append-only.** Nu e o cerință nouă: e Condiția 3 de la nivelul 6, aplicată corpului nivelului 2 înainte ca el să existe.

---

# 6. CONDIȚII FAIL-CLOSED

```
· fereastră incompletă (warmup)            → factor UNAVAILABLE, nu o valoare presupusă
· `momentum` cerut dar neconstruit         → factor UNAVAILABLE (NU zero, NU „neutru")
· RegimeState de la nivelul 1 UNAVAILABLE  → BiasState UNAVAILABLE (propagare în cascadă)
· orice factor din cheie UNAVAILABLE       → cheia îl EXCLUDE; dacă rămâne goală, UNAVAILABLE
· BiasState UNAVAILABLE                    → sentinel la nivelul 6 ⇒ NO-TRADE, prin TIP (L-U2)

AMBIGUU ≠ INDISPONIBIL, ca la nivelul 1: ambiguu ⇒ ponderi moi cu dispersie între celule;
indisponibil ⇒ fail-closed.
```

---

# 7. CRITERII DE ACCEPTARE

```
1. ZERO LOOKAHEAD    fiecare factor la bara i citește EXCLUSIV bare <= i−1. Test: perturbarea
                     barei i+1 nu schimbă niciun factor la i, pe TOT setul de descoperire.
2. FALSIFICABILITATE fracția barelor cu zero bazine eligibile material peste zero (§3).
3. NEREDUNDANȚĂ      acordul cu direcția nivelului 1 raportat per factor. 66,39% e valoarea
                     măsurată pentru structură; un factor care ar depăși ~95% e o reformulare
                     și se retrage.
4. DEZVĂLUIRE        fiecare factor poartă `redundant_with[]`, completat prin inspecție statică
                     a apelurilor, nu dintr-o listă de mână (L-R1).
5. CONSTANTE         nicio constantă în unități M15 sau H4 în corpul nivelului 2.
6. PROPRIETATE       ∀ bară cu BiasState UNAVAILABLE ⇒ decizia nivelului 6 == NO_TRADE,
                     asertat pe ÎNTREGUL set, nu pe cazuri alese.
```

---

## HANDOFF

**VE construiește.** Ordinea: factorii observabili din primitive ratificate → filtrul de bazine neconsumate cu criteriul de falsificabilitate → `redundant_with[]` prin inspecție statică → testele 1-6.
**Red Team, ținte:** dacă recența e o justificare suficientă pentru o axă construită pe aceleași primitive; dacă restricția la bazine neconsumate rezolvă saturația sau doar o mută; și dacă „un singur estimator" e o simplificare corectă sau o pierdere de informație.
**CEO, patru lucruri:** **(1) întrebarea ta e o PREVIZIUNE, iar un clasificator nu o poate emite — nivelul 2 livrează FACTORI, iar cei 72% vin de la nivelul 6 condiționat pe ei; altfel ar exista două estimatoare pe aceleași date. (2) D2 NU blochează „lichiditate deasupra" — `build_pools` emite un bazin per swing, nu per pereche de maxime egale; premisa era falsă, factorul e construibil. (3) Dar e NEFALSIFICABIL în forma cerută: 474 de bazine deasupra la bara mediană, și doar 5,1% dintre bare fără vreunul la 1×ATR. (4) Verificarea de redundanță făcută înainte: ZERO dintre cei patru factori sunt independenți de primitivele pe care candidații declanșează, iar `build_pools` derivă din swing-uri, deci nici lichiditatea nu e independentă — nou, negăsit la nivelul 1.**

**STOP aici, conform mandatului. VE construiește.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.51 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
