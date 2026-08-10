# STATISTICIAN — CABLAREA NIVELELOR. SPECIFICAȚIE

**Document ID:** STAT-LEVEL-WIRING-SPEC-v1.0
**Data:** 2026-08-10 · **Autor:** Statistician

**Verificare de sursă:** citit direct `code/regime_classifier.py`, `code/bias_h1.py`, `code/zone_confirmation.py`. **Stare reală a pieselor: nivelele 1, 2 și 4 sunt CONSTRUITE și emit tipuri concrete; nivelele 3 și 6 sunt SPECIFICATE, nu construite.** Cablarea de mai jos se scrie contra tipurilor reale acolo unde există și contra contractelor acolo unde nu.

---

# PARTEA 1 — FLUXUL NU E LINIAR. Se RAMIFICĂ la nivelul 3.

**Fluxul din mandat — `4H → 1H → 15M → 5M → 6 → 7` — e liniar. Constrângerea Z4-L2, deja acceptată, îl face imposibil.**

```
Z4-L2: confirmarea de la nivelul 4 ÎNLOCUIEȘTE tranzacția nivelului 3.
       Intrare la hit+W+1, ~5 ore mai târziu, alt preț, alt stop, alt risc.
```

> **Dacă intrarea e alta, populația e alta. Iar dacă populația e alta, `p_t` e alt estimand.** O tranzacție de nivel 3 și o tranzacție de nivel 4 nu sunt aceeași ipoteză privită mai atent — **sunt două ipoteze diferite pe aceeași zonă.**

## Forma corectă a fluxului

```
        4H regim (L1)  ──┐
                         ├──► CONTEXT  ──►  15M harta de zone (L3)
        1H bias  (L2)  ──┘                        │
                                                  ├──► TRANZACȚIA L3   intrare la atingere
                                                  │        └──► nivel 6 ──► nivel 7
                                                  │
                                                  └──► 5M confirmare (L4)  fereastra [hit+1, hit+W]
                                                           └──► TRANZACȚIA L4  intrare la hit+W+1
                                                                   └──► nivel 6 ──► nivel 7
```

**Nivelele 1 și 2 sunt CONTEXT — coordonate care condiționează. Nivelul 3 produce OBIECTUL (zona). Nivelele 3 și 4 produc DOUĂ DEFINIȚII DE TRANZACȚIE pe același obiect.**

## Ce trece efectiv, și când se calculează

```
L1 → context   RegimeState{volatility, structure, direction, news : Axis(label, weights, confidence, status)}
               calculat la ÎNCHIDEREA fiecărei bare H4; valabil până la închiderea următoarei
L2 → context   BiasState{factors[(name, value, status, primitive, redundant_with)], shares, status}
               la închiderea fiecărei bare H1
L3 → obiect    ZoneMap{zones[(id, features[], k, feature_status[])], threshold_k, band_atr, status}
               la închiderea fiecărei bare M15
L4 → obiect    ZoneConfirmationResult{confirmation : enum, persistence, progress_atr, encounters,
               status, reason, schema_hash}
               la bara hit+W, disponibil la hit+W+1
```

---

# PARTEA 2 — CE FACE NIVELUL 6 CU FIECARE INPUT. Decizia centrală.

## Trei devin coordonate de ierarhie. Al patrulea NU.

```
L1 regim   ──► COORDONATĂ de ierarhie
L2 bias    ──► COORDONATĂ (după discretizare — vezi mai jos)
L3 hartă   ──► COORDONATĂ (contorul k)
L4 confirm ──► NU E COORDONATĂ. Definește o POPULAȚIE SEPARATĂ.
```

**Motivul e cel din Partea 1, și e o consecință necesară, nu o preferință:**

> **O coordonată de ierarhie rafinează estimarea ACELEIAȘI mărimi pe o SUBMULȚIME. Nivelul 4 nu restrânge populația tranzacțiilor de nivel 3 — o ÎNLOCUIEȘTE cu alta. Nu se poate contracta un copil într-un părinte când copilul măsoară altceva decât părintele.**

**Deci: aceleași coordonate de context (L1, L2, L3) se aplică AMBELOR populații; ierarhia se bifurcă în nodul terminal.**

```
ierarhia, ORDONATĂ ȘI IMBRICATĂ:
  nivel 0   rata globală
  nivel 1   + tipul de setup
  nivel 2   + sesiunea
  nivel 3   + regim (L1)
  nivel 4   + bias (L2)
  nivel 5   + contorul hărții (L3)
  nivel 6   + FRUNZA: {tranzacție-L3} sau {tranzacție-L4 × starea de confirmare}
```

**Ordinea NU se alege pe rezultate: e ordinea ARHITECTURII — contextul mai larg condiționează pe cel mai îngust. Fiind fixată de structură, nu de măsurătoare, nu poate fi ajustată. Intră în `schema_hash`.**

## Ce trebuie discretizat, și avertismentul care merge cu asta

**`BiasState` emite valori CONTINUE (`structure_run` întreg cu semn, `liquidity_above` contor). O coordonată de ierarhie cere o cheie CATEGORIALĂ. Deci discretizarea e obligatorie — și e o SCHEMĂ, deci intră pre-înregistrată în `schema_hash`, cu ancora de ocupanță egală, ca la nivelele 1 și 4.**

**Iar la contorul hărții spun ce am măsurat deja: la 1×ATR, `k≥3` apare pe 94,87% din bare. Ca discriminator e cvasi-constant.** Nu e motiv să-l scot: **contracția îl va colapsa în părinte de la sine, la cost zero. Îl includ și las mecanismul să decidă — exact ce am spus la predicția de la nivelul 1.**

## Consecința de guvernanță pe care nimeni n-a preț-uit-o

> **Dacă tranzacția L3 și tranzacția L4 sunt două populații, sunt DOUĂ IPOTEZE. Fiecare testată formal CONSUMĂ UN SLOT DE FAMILIE.** Cablarea nivelului 4 nu adaugă un filtru gratuit la o politică existentă — **dublează potențial numărul de ipoteze pe zonă.** La m=16 azi, activarea nivelului 4 pe politicile de zonă poate împinge familia semnificativ mai sus, iar familia e MONOTONĂ. **Se decide înainte de a construi, nu după.**

---

# PARTEA 3 — FAIL-CLOSED, UNIFICAT

**L-U2 și Z4-L1 sunt același lucru spus de două ori. Regula generală care le produce pe amândouă:**

> **O stare „fără informație" nu are voie să fie REPREZENTABILĂ în același tip ca o stare informativă.** Dacă e, aritmetica sau comparația o vor trata tăcut ca informativă. `0` e un număr; `UNAVAILABLE` nu e.

```
CONTRACTUL, identic la toate nivelele:
    LevelOutput[T]  =  Ok(value: T, as_of: int, valid_until: int, schema_hash: str)
                    |  Unavailable(reason: str, as_of: int)

  · aritmetica EV acceptă EXCLUSIV `Ok`. `Unavailable` nu are operator aritmetic.
  · nivelul 6 ramifică pe CONSTRUCTOR (sau pe membru de enum / `status`), NICIODATĂ pe o valoare.
  · o valoare ordinală există DOAR pentru ordonare și afișare. Nu intră în nicio decizie.
```

**Instanțele:**

```
L-U2   regim UNAVAILABLE → `Unavailable` → EV nu îl poate consuma → NO-TRADE prin TIP.
Z4-L1  UNDETERMINED → `Unavailable` sau ramificare pe `ZoneConfirmation.UNDETERMINED`.
       Ordinala 0 NU e citită niciodată. Ea rămâne în `Ok` doar ca payload de afișare.
```

## Mecanismul de impunere există deja și nu e documentar

**`mypy --strict` rulează pe tot codul laboratorului. Un tip-sumă (sau `Optional[T]`) face ca omiterea ramurii `Unavailable` să fie o EROARE DE TIP, nu o scăpare de review.**

> **Asta transformă regula din text în constrângere verificată mecanic. Un `if` pe valoare se pierde la o refactorizare; o ramură lipsă nu trece de type-checker.** E a patra oară când aceeași unealtă rezolvă aceeași clasă de problemă — o reutilizez, nu o reinventez.

---

# PARTEA 4 — CADENȚA. „Vechi de 4 ore" nu e problema reală.

## Prima corecție: un regim de la 12:00 folosit la 15:55 NU e stale

**E cea mai recentă observație COMPLETĂ. Un sistem pe bare nu are altceva — iar alternativa (o bară H4 neînchisă) ar fi LOOKAHEAD.**

> **Pericolul nu e vârsta. E (a) folosirea unei bare neînchise, și (b) purtarea unei valori dincolo de fereastra ei de valabilitate.**

## Regula, mecanică

```
Fiecare nivel emite `as_of` și `valid_until`.
Nivelul 6, la `decision_ts`:
      as_of <= decision_ts < valid_until   ⇒  `Ok` se folosește
      altfel                                ⇒  `Unavailable(reason="stale")`
NICIODATĂ carry-forward nemărginit. O gaură în seria sursă (graniță de bloc, piață închisă)
⇒ valid_until expiră ⇒ UNAVAILABLE, nu „ultima valoare cunoscută".
```

**Asta face „stale" o eroare de TIP, nu o judecată de la caz la caz.**

## A doua parte a întrebării, și refuz să inventez un model de decădere

**„E acceptabil un regim vechi de aproape 4 ore?" — dacă informația regimului se degradează MATERIAL în interiorul propriei bare, atunci H4 e timeframe-ul GREȘIT pentru regim. Aia e o întrebare de proiectare a nivelului 1, nu de cablare.**

```
CE FAC ÎN SCHIMB: `age = decision_ts − as_of` se ÎNREGISTREAZĂ la fiecare decizie și devine
CANDIDAT de coordonată de ierarhie. Dacă vârsta contează, contracția o va găsi; dacă nu,
se colapsează în părinte la cost zero. Nu presupun, nu ignor — măsor prin mecanismul existent.
```

---

# PARTEA 5 — ORDINEA DE EVALUARE: TOATE, ÎNTOTDEAUNA

**Întrebarea e pusă ca economie de calcul vs observații pentru nivelul 9. Dar are un răspuns statistic care o precede.**

> **Fail-fast ar reintroduce exact CENZURA pe care am închis-o la Condiția 1.** Dacă nu se evaluează harta când regimul e indisponibil, nu se va ști niciodată ce ar fi spus harta în acele condiții — deci nu se va putea estima nimic condiționat pe ele. **E aceeași buclă: nu evaluezi ⇒ nu acumulezi ⇒ nu poți evalua niciodată.**

```
REGULA: se evaluează TOATE nivelele, ÎNTOTDEAUNA, indiferent de ce a returnat vreunul.
        Poarta acționează EXCLUSIV la decizie, niciodată la evaluare.
        Un nivel care primește `Unavailable` de la un părinte emite el însuși `Unavailable`
        cu motivul propagat — dar SE EVALUEAZĂ și SE ÎNREGISTREAZĂ.
```

**Costul de calcul nu decide aici, și spun de ce: sunt funcții pure peste bare deja încărcate. Costul e neglijabil față de informația pierdută — iar informația pierdută e nerecuperabilă, pe când calculul se poate cumpăra.**

**E aceeași regulă ca fișa-umbră de la C1: se înregistrează pe FIECARE declanșare, indiferent de motivul refuzului. Cablarea o extinde de la tranzacții la NIVELE.**

---

# PARTEA 6 — CE SE PERSISTĂ

**Nivelul 9 va avea nevoie de lanț, nu de concluzie. Un singur artefact per evaluare:**

```
DecisionTrace {
  decision_ts, bar_ref, setup_id, population : {"L3_TRADE" | "L4_TRADE"}
  levels : [ per nivel:
      level_id, kind : {"Ok" | "Unavailable"}, value_or_null, reason_if_unavailable,
      status, as_of, valid_until, age, schema_hash, redundant_with[] ]
  engine : { R, RR, c, (p_t, p_s, p_h), E[X|h], EV, EV_LCB, k_shrinkage,
             prob_table_hash, table_cutoff_ts, cell_key, cell_weights }
  outcome : { decision : {"ENTER" | "NO_TRADE"}, blocking_reason, shadow : bool }
}
```

**Trei cerințe care nu sunt evidente:**

```
1. SENTINEL-UL SE PERSISTĂ CU MOTIV. Fără el, nivelul 9 nu poate distinge „regimul a fost
   indisponibil" de „regimul n-a fost niciodată calculat". Absența nu e o valoare.
2. `population` e OBLIGATORIU. Fără el, tranzacțiile L3 și L4 se amestecă într-o singură
   populație și orice estimare pe ele e a unui amestec fără sens.
3. `table_cutoff_ts` și cele DOUĂ hash-uri se persistă la fiecare decizie (C2, C3) — altfel
   o re-verificare invalidează tăcut decizii deja luate.
```

---

# PARTEA 7 — CE NU SPECIFIC

**Nivelele 5, 8 și 9 nu există. Cablarea le lasă locul FĂRĂ să le presupună:**

```
· ierarhia e o LISTĂ ORDONATĂ extensibilă — un nivel nou se adaugă la coadă, iar dacă n-are
  date se contractă în părinte. Adăugarea nu poate strica nimic (proprietatea de la nivelul 6).
· `DecisionTrace.levels` e o LISTĂ, nu o structură cu câmpuri fixe. Un nivel nou apare ca
  intrare nouă; consumatorii vechi îl ignoră.
· NU presupun ce va emite nivelul 5, nici ce va citi nivelul 9. Contractul `LevelOutput[T]`
  e singura obligație, și e satisfăcut de orice nivel viitor.
```

---

## HANDOFF

**VE construiește** în ordinea: (1) tipul-sumă `LevelOutput[T]` + `as_of`/`valid_until` la toate cele trei nivele deja existente; (2) `DecisionTrace` cu persistarea sentinel-ului și a motivului; (3) evaluarea completă, fără fail-fast; (4) discretizarea factorilor L2, pre-înregistrată în `schema_hash` înainte de prima decizie. **Nivelele 3 și 6 nu există — cablarea lor se scrie când există modulele.**
**Red Team, ținte:** dacă bifurcarea în două populații e forțată de Z4-L2 sau dacă e o interpretare a mea; dacă „evaluează tot mereu" chiar evită cenzura sau doar o mută în stratul de înregistrare; și dacă `valid_until` poate fi definit fără să reintroducă o presupunere de staționaritate.
**CEO, cinci lucruri:** **(1) fluxul liniar din mandat nu se poate cabla — Z4-L2 îl RAMIFICĂ la nivelul 3, iar tranzacția L3 și tranzacția L4 sunt două populații, nu una filtrată. (2) Regimul, bias-ul și harta devin COORDONATE de ierarhie; confirmarea NU — ea definește a doua populație, fiindcă o coordonată rafinează aceeași mărime, iar nivelul 4 măsoară altceva. (3) Consecința pe care n-a preț-uit-o nimeni: două populații = DOUĂ IPOTEZE, deci activarea nivelului 4 poate DUBLA numărul de sloturi de familie pe politicile de zonă, iar familia e monotonă — se decide înainte de a construi. (4) „Vechi de 4 ore" nu e problema: cea mai recentă bară ÎNCHISĂ e tot ce există, iar alternativa ar fi lookahead; problema reală e carry-forward-ul dincolo de `valid_until`, și îl fac eroare de TIP. Nu inventez un model de decădere — înregistrez vârsta și las contracția să decidă dacă contează. (5) Fail-fast NU se face: ar reintroduce exact cenzura închisă la Condiția 1. Se evaluează tot, mereu; poarta acționează doar la decizie.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.57 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
