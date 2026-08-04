# STATISTICIAN — CELE TREI CONDIȚII DE APROBARE ALE NIVELULUI 1

**Document ID:** STAT-LEVEL1-RATIFICATION-CONDITIONS-v1.0
**Data:** 2026-08-04 · **Autor:** Statistician
**Închide:** L-U2, L-R1, L-U1 din APPROVED_WITH_LIMITATIONS (pas 4/4), pe clasificatorul `82b1ca3`.

**Verificare de sursă:** citit direct `code/regime_classifier.py` la `82b1ca3`. **O măsurătoare nouă, proprie, P&L-oarbă**, care verifică corecția transmisă și o găsește MAI MARE decât s-a raportat. **Iar la L-R1 extind acuzația dincolo de ce a numit Red Team.**

---

# CORECȚIA LA PROPRIA MEA AFIRMAȚIE — verificată, acceptată, și reformulată

**Am afirmat că eroarea de fereastră 460 e „indetectabilă în aval". Red Team a rafinat: adevărată la staționaritate, falsă la non-staționaritate. Am măsurat-o eu.**

```
GLOBAL, pe barele comparabile (12.373):   W=460  11,10%     W=30  10,64%      ← afirmația mea SE ȚINE
PER-BARĂ, dezacord de etichetă:           7,28%             ← RAPORTAT ~4%. E aproape DUBLU.
PER-AN, ocupanța W=460:  min 3,47%  max 22,02%   interval 18,54 puncte
PER-AN, ocupanța W=30 :  min 9,47%  max 12,84%   interval  3,38 puncte   ← de 5,5× mai stabil
```

## Mecanismul e vizibil direct în date, nu doar plauzibil

```
an     trend median al volatilității     ocupanță W=460
2018            +8,0%                        3,47%   ← cea mai mică
2013           +33,5%                        7,21%
2020           +47,0%                        7,74%
2012           −38,1%                       13,80%
2017           −29,1%                       13,02%
2011              —                         22,02%   ← cea mai mare
```

**Volatilitatea urcă ⇒ fereastra de trimestru compară bara cu un trecut mai calm ⇒ aproape nimic nu mai cade sub P10. Volatilitatea scade ⇒ invers.** Relația e inversă și consistentă pe cazurile tari.

## Reformularea afirmației mele — și e o corecție de fond, nu de nuanță

> **Nu „indetectabilă". CE SE ANULEAZĂ.** Erorile per-perioadă sunt mari și de semn OPUS, iar media lor e zero. **O eroare care se anulează e mai rea decât una ascunsă, într-un fel precis: e invizibilă exact în statistica agregată pe care ai verifica-o, și maximă exact în subperioadele unde clasificarea de regim contează cel mai mult — cele în care volatilitatea se schimbă.**

**Deci W=30 nu e o corecție cosmetică. La 460, clasificatorul spune „comprimat față de ultimul trimestru", iar într-o schimbare de regim de volatilitate asta înseamnă „comprimat față de o ALTĂ piață". Nu e o versiune mai lentă a aceluiași semnal — e alt semnal.** Se tratează ca decizie de modelare: **schemă NOUĂ, versiune nouă, `schema_hash` nou, append-only** (Condiția 3 de la nivelul 6). Deciziile luate cu W=460 își păstrează hash-ul vechi și nu se re-etichetează.

---

# L-U2 — PROPAGAREA NIVEL 1 → NIVEL 6

**Verificat: clasificatorul emite corect. `Axis` conține `soft` (distribuția pe benzi), `confidence` și `status`; `UNAVAILABLE` și `NEUTRAL` sunt produse unde trebuie. Golul e integral pe partea CONSUMATORULUI.** Regula CEO e scrisă, nu cablată.

## Regula devine demonstrabilă prin TIP, nu prin `if`

```
1. `regime: RegimeState` devine ARGUMENT OBLIGATORIU al căutării de probabilitate.
   Aceeași unealtă ca `as_of` la Condiția 2: omisiunea devine INEXPRIMABILĂ, nu doar interzisă.

2. Dacă ORICE axă folosită în cheie are `status == UNAVAILABLE`, căutarea returnează un
   SENTINEL, nu un număr. Aritmetica EV NU poate consuma sentinel-ul.
   ⇒ FAIL-CLOSED PRIN TIP, nu printr-un `if` care poate fi uitat la o refactorizare.

3. Distribuția `soft` alimentează NUMĂRĂTORI PONDERATE: fișa înregistrează un VECTOR DE PONDERI
   peste celule, nu un singur id de celulă. n_efectiv = Σw. Beta-Binomial acceptă numere ne-întregi.
```

## Corecția care contează cel mai mult: varianța ÎNTRE celule

**Un amestec peste celule are DOUĂ surse de incertitudine, iar a doua e cea care lipsește dacă nu e cerută explicit:**

```
p̂ = Σ_c w_c · p̂_c
Var(p̂) = Σ_c w_c · Var(p̂_c)              ← eroare de eșantionare, INSUFICIENT
       + Σ_c w_c · (p̂_c − p̂)²            ← DISPERSIA ÎNTRE CELULE, OBLIGATORIE
```

**Fără al doilea termen, atribuirea moale ar produce un interval MAI ÎNGUST decât adevărul — exact pe barele ambigue.**

## Și de aici o corecție la intuiția naturală: căderea în părinte NU e varianta conservatoare

> **Părintele e estimat pe mai multe date, deci are interval MAI ÎNGUST. A cădea în părinte când cheia e ambiguă înlocuiește „nesigur pe care copil" cu „sigur pe medie" — ASCUNDE incertitudinea în loc s-o propage.** Punctual dă aproape aceeași cifră; ca interval, e fals precis. **Amestecul ponderat cu termenul de dispersie e singura variantă care propagă corect.**

## Demonstrabilitatea, definită operațional

```
TEST DE PROPRIETATE, pe ÎNTREGUL set de descoperire, nu pe cazuri alese:
  ∀ bară cu status == UNAVAILABLE pe o axă din cheie  ⇒  decizia == NO_TRADE.
  ∀ bară cu confidence == 0 pe axa direcțională       ⇒  cheia NU include direcția.
```

**„Semnalul iese, no-trade nu e demonstrabil" se închide doar când există o aserțiune care rulează pe toate barele.** Un exemplu care trece nu demonstrează o regulă universală.

---

# L-R1 — REDUNDANȚA AXEI DE STRUCTURĂ. Dezvălui, nu repar — și extind acuzația.

## Ce e problema, formulată exact

**`detect_breaks` e partajat cu candidații de structură. Pentru ei, condiționarea pe axa de structură e condiționare pe o FUNCȚIE A PROPRIULUI DECLANȘATOR.** Nu e lookahead — e circularitate: **orice câștig aparent de condiționare poate fi tautologic.** Un candidat pe BOS declanșează după un BOS; `UP_STRONG` înseamnă mai multe BOS. Aceleași evenimente, de două ori.

## Regula de atașare — MECANICĂ, nu o listă întreținută de mână

```
AVERTISMENTUL se atașează automat oricărui candidat al cărui calcul de DECLANȘATOR
apelează aceeași primitivă ratificată din care derivă axa.
Verificabil prin inspecție statică a apelurilor, NU dintr-o listă care se învechește.
```

## EXTINDEREA: „volatilitatea rămâne independentă" e adevărat pentru unii candidați și FALS pentru alții

**Red Team a numit structura. Dar aceeași acuzație lovește axa de VOLATILITATE, pentru candidații care declanșează pe deplasare:**

```
axa de STRUCTURĂ    derivă din  detect_breaks (market_structure)
axa de VOLATILITATE derivă din  log-range Parkinson + `expansion` (market_state)
axa de ȘTIRI        derivă din  calendar — fără suprapunere cu nimic
```

**Banda `HIGH_DIRECTIONAL` a axei de volatilitate ESTE `expansion`. Iar `expansion` e declanșatorul pentru CAND-0002 (COMPRESSION-EXPANSION), CAND-0008 (VOID-DISPLACEMENT) și CAND-0009 (LEVEL-BREAK-DRIVE).** Pentru cei trei, **axa de volatilitate nu e context independent** — exact aceeași eroare, pe cealaltă axă, și nenumită până acum.

```
VERDICT PE AXE, per candidat:
  candidați pe market_structure  → axa de STRUCTURĂ nu e independentă
  candidați pe `expansion`       → axa de VOLATILITATE nu e independentă  ← EXTINDERE
  ORICE candidat                 → axa de ȘTIRI e independentă (calendarul nu intră în niciun declanșator)
```

## Controlul care face avertismentul verificabil, nu doar declarativ

**Un avertisment fără test rămâne text.** Deci:

```
Pentru un candidat cu axă redundantă: se compară condiționarea pe axa REDUNDANTĂ cu
condiționarea pe o axă INDEPENDENTĂ pentru acel candidat.
Dacă axa redundantă nu adaugă nimic peste cea independentă ⇒ redundanța era totală,
iar „regimul aduce informație" NU se poate raporta pentru acel candidat.
```

---

# L-U1 — REDENUMIRE. Acceptat imediat, și consecința e o constatare.

```
StructBand.RANGE  →  StructBand.POST_FLIP        (|run| == 1)
```

**Acceptat fără rezerve: propriul meu text descria starea ca „direcție proaspăt răsturnată, INSTABILĂ" — adică post-flip — în timp ce eticheta spunea „range". Eticheta contrazicea propria ei definiție.**

## Consecința, care nu e o lacună ci un rezultat

> **După redenumire, axa de structură NU ARE stare de „range". Și nici nu poate avea: 99,88% dintre bare au un `run` nenul, deci structura are practic întotdeauna o direcție pe H4.**

**„Range" nu dispare din taxonomie — e servit de ALTĂ axă:** banda `COMPRESSED` a axei de volatilitate e exact „piața nu merge nicăieri", măsurată pe amplitudine în loc de structură. **Conceptul e acoperit; doar nu de axa pe care intuiția l-ar căuta.** Dacă CEO vrea un range structural distinct, cere un construct nou (containment într-o bandă de preț, sau densitate de CHoCH) — și acela ar fi o axă nouă, nu o redenumire.

---

# LIMITAREA DE CONSEMNAT — atribuirea moale e LOCALĂ. Accept, și îi dau un gardian.

**Accept integral: atribuirea moale apără doar la FRONTIERĂ. O bară adâncă în bandă primește `confidence = 1,0` pe o etichetă posibil greșită, iar exact așa s-a ascuns eroarea de fereastră. Propagă incertitudine de EȘANTION, nu de SPECIFICAȚIE.**

**Nu e o limitare nouă în sistem — e aceeași distincție pe care am stabilit-o la Condiția 3 de la nivelul 6:**

```
incertitudine de EȘANTION      → apărată de confidence / EV_LCB
incertitudine de SPECIFICAȚIE  → apărată de SCHEMA PRE-ÎNREGISTRATĂ + bateria de frontieră
```

**Consecință directă: parametrii nivelului 1 — fereastra W, tăieturile de bandă, măsura, tăieturile de `run` — SUNT o schemă și intră în `schema_hash`.** Nu e o cerință nouă; e cea de la nivelul 6, aplicată corpului care tocmai a fost aprobat.

## Și transform limitarea într-o cantitate măsurabilă

**O bandă global prost definită nu e invizibilă — se vede în STABILITATEA OCUPANȚEI, exact cum s-a văzut acum:**

```
MONITOR PERMANENT: ocupanța fiecărei benzi, raportată PER PERIOADĂ, nu doar agregat.
LINIA DE BAZĂ, pre-înregistrată acum:  W=30 → interval de 3,38 puncte pe 11 ani.
                                       W=460 → 18,54 puncte (respinsă din acest motiv).
O lărgire materială față de linia de bază = semnal de re-examinare a schemei.
```

**Nu inventez un prag — pre-înregistrez linia de bază măsurată.** Aceeași disciplină ca la termenul de gap: o limitare care nu se poate elimina se transformă într-o cantitate care se urmărește.

---

## HANDOFF

**VE construiește, în ordine:** (1) `regime` ca argument OBLIGATORIU al căutării, cu sentinel pe `UNAVAILABLE` — fail-closed prin tip; (2) numărători PONDERATE din `soft`, **cu termenul de dispersie între celule în varianță — fără el intervalul e fals îngust**; (3) testul de proprietate pe TOT setul de descoperire, nu pe cazuri alese; (4) redenumirea `RANGE → POST_FLIP`; (5) atașarea mecanică a avertismentului de redundanță prin inspecția apelurilor, **pe AMBELE axe, nu doar pe structură**; (6) monitorul de ocupanță per perioadă, cu linia de bază de 3,38 puncte.
**Red Team, ținte explicite:** dacă termenul de dispersie între celule e suficient ca să facă amestecul conservator; dacă inspecția statică a apelurilor prinde redundanța indirectă (o primitivă apelată prin alt modul); și dacă linia de bază de ocupanță e un gardian real sau doar un jurnal.
**CEO, patru lucruri:** **(1) corecția transmisă e CONFIRMATĂ și mai mare — dezacordul per-bară e 7,28%, nu ~4%; iar afirmația mea se reformulează: eroarea nu era indetectabilă, era CE SE ANULEAZĂ, adică invizibilă exact în agregatul pe care l-ai verifica și maximă exact unde contează. (2) Căderea în părinte NU e varianta conservatoare — părintele are interval mai îngust, deci ar ascunde incertitudinea; doar amestecul ponderat cu dispersie o propagă. (3) „Volatilitatea rămâne independentă" e FALS pentru CAND-0002, 0008 și 0009, care declanșează pe `expansion`, adică pe chiar banda `HIGH_DIRECTIONAL` — aceeași redundanță, pe cealaltă axă. (4) După redenumire nu mai există stare de „range" pe axa de structură, și nici nu poate exista; conceptul e servit de banda `COMPRESSED`.**
**Nivelul 2:** dă-mi-l **în paralel**. Cele trei condiții sunt muncă de specificație și nu blochează. **Ce trebuie să moștenească nivelul 2, ca să nu repet aceleași trei: constantele se re-derivă în unitățile H1, nu se transplantează; parametrii intră în `schema_hash`; și axa lui se verifică de redundanță față de declanșatorii care o vor consuma, înainte de a fi propusă.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.50 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
