# STATISTICIAN — NIVELUL 1: REGIMUL PIEȚEI PE H4. SPECIFICAȚIE

**Document ID:** STAT-LEVEL1-REGIME-H4-SPEC-v1.0
**Data:** 2026-08-04 · **Autor:** Statistician

**Verificare de sursă:** citit direct `code/market_state.py`, `code/market_structure.py`, `code/mtf.py`, `config/split_manifest.json`. **Măsurători noi, proprii, P&L-oarbe pe `H4_from_M15_v2` (12.832 bare).** **Trei constatări schimbă forma specificației, iar una îmi infirmă propria ipoteză.**

---

# PARTEA 0 — DOUĂ CORECȚII ÎNAINTE DE ORICE DEFINIȚIE

## 0.1 `COMPRESSION_WINDOW = 460` e un TRANSPLANT DE UNITATE pe H4

**Din `market_state.py`, verbatim: „Lungimea 460 = media empirică de săptămână". Derivată pe M15.** Pe H4:

```
media empirică H4, măsurată de mine:  ZI = 5,98 bare    SĂPTĂMÂNĂ = 29,84 bare
⇒ fereastra de săptămână în unități H4 = 30, NU 460.
   460 de bare H4 = 15,4 săptămâni. E o fereastră de TRIMESTRU purtând eticheta „săptămână".
```

**Aceeași clasă de eroare ca `L=28` la bootstrap (v2.7.45): o constantă derivată într-o unitate, aplicată în alta fără re-derivare.** Re-derivarea folosește EXACT aceeași metodă care a produs 460 — nu aleg 30, îl obțin.

### Și aici e partea care contează metodologic

```
rata de compresie la fereastra 460 : 11,10% din barele valide
rata de compresie la fereastra  30 : 10,70% din barele valide
```

> **Rata NU se schimbă — pentru că e o percentilă. O tăietură P10 produce ~10% prin construcție, indiferent de fereastră.** Deci **o definiție bazată pe rang e IMUNĂ la verificarea prin rata de ieșire: eroarea de unitate e INDETECTABILĂ în aval.** Se schimbă doar ÎNTREBAREA la care răspunde: „comprimat față de ultima săptămână" vs „față de ultimul trimestru". **Nimeni n-ar fi prins-o privind rezultatul. De aceea se prinde la specificație sau deloc.**

**Beneficiu secundar măsurat:** la 460, 3,6% din bare rămân neclasificabile (warmup); la 30, doar 0,2%.

## 0.2 `volrank` NU e un rang de volatilitate

**Din `mtf.py:19`: `volrank = pv.rolling(60)...` — e un rang de VOLUM.** Coliziune de nume. **Nu există o primitivă ratificată de rang de VOLATILITATE.** O construiesc mai jos din mașinăria compresiei, care e ratificată — nu inventez o convenție paralelă.

---

# PARTEA 1 — CELE NOUĂ STĂRI SUNT AXE. Iar măsurătoarea le comprimă mai mult decât credeam.

## Formatul cerut de CEO își contrazice singur propria încadrare

```
Trend Long: 82%   Trend Short: 18%     ← o distribuție pe o axă DIRECȚIONALĂ
Volatilitate: HIGH                      ← o etichetă pe o axă SEPARATĂ
Confidence: 91                          ← o a treia mărime
```

**Ieșirea cerută e deja multi-axială. „Clasificare în nouă stări" și formatul de ieșire nu pot fi ambele adevărate — iar ieșirea e cea coerentă.** Răspunsul la întrebarea 4 e deci: **se SUPRAPUN, sunt axe.** Dar măsurătoarea merge mai departe.

## Măsurat: compresia și volatilitatea mică sunt ACEEAȘI VARIABILĂ

**`compression` e definită ca P10 al log-range-ului Parkinson. „Volatilitate mică" nu poate fi decât banda de jos a aceleiași măsuri.** Nu sunt două stări — **compresia e decila inferioară a axei de volatilitate.** Ocupanța măsurată (fereastră 30):

```
COMPRESSED (<=P10)  10,7%      LOW (P10-P33)  23,6%
NORMAL (P33-P67)    32,4%      HIGH (>P67)    33,1%      indisponibil 0,2%
```

## Măsurat: EXPANSIUNEA nu e nici ea o axă. Aici mi-am infirmat propria ipoteză.

**Presupuneam că expansiunea (eveniment de bară) și compresia (proprietate de fereastră) pot coexista — clasicul breakout-din-compresie. Măsurat: coexistă în 0,000% din bare.** Sunt disjuncte prin construcție: o bară de expansiune cere `range > 1,5×ATR`, deci nu poate fi în decila inferioară a range-ului.

**Dar corecția merge mai departe decât greșeala mea:**

```
% din barele fiecărei benzi care sunt expansiune:   HIGH 31,36%   NORMAL 0,10%   LOWISH 0,07%
% din TOATE barele de expansiune care stau în HIGH: 99,48%
```

> **Expansiunea e, cu 99,5%, un SUBSET al benzii HIGH. Nu e o axă ortogonală — e o subdiviziune a vârfului axei de volatilitate**, adăugând condiția de corp direcțional. **Deci cinci dintre cele nouă „stări" ale CEO — compresie, volatilitate mică, normală, volatilitate mare, expansiune — sunt UNA SINGURĂ AXĂ cu cinci benzi.**

## Structura finală

```
AXA A — VOLATILITATE (o variabilă, măsura Parkinson E000, fereastră cauzală de 30):
        COMPRESSED  |  LOW  |  NORMAL  |  HIGH_CHOPPY  |  HIGH_DIRECTIONAL (= expansiune)
AXA B — STRUCTURĂ (direcție + persistență, din market_structure):
        RANGE  |  UP_WEAK | UP_STRONG  |  DOWN_WEAK | DOWN_STRONG
AXA C — ȘTIRI:  TRUE | FALSE, cu STATUS separat (Partea 5)

„Piața normală" NU e o stare — e complementul celorlalte. Ceea ce se vede DOAR dacă sunt axe.
```

**5 × 5 × 2 = 50 de celule. Prea multe ca spațiu PLAT** — dar nu trebuie să fie plat: **motorul de decizie le consumă ca ierarhie ORDONATĂ ȘI IMBRICATĂ, adăugând o axă pe rând, iar contracția deja ratificată se ocupă de celulele subțiri automat.** Nicio informație nu se pierde, nicio celulă nu e forțată.

---

# PARTEA 2 — DEFINIȚIILE MECANICE, cu ce e derivat și ce e ales, marcat

## Axa A — volatilitate

```
măsura      m[i] = ln(high[i] / low[i])              metrica OFICIALĂ E000, primară
fereastra   W = 30 bare H4                            DERIVATĂ (media empirică de săptămână, 29,84)
benzile     COMPRESSED  m[i] <= P10(m, [i-29, i])     P10 = default declarat al spec-ului, reutilizat
            LOW         P10 < m[i] <= P33
            NORMAL      P33 < m[i] <= P67
            HIGH        m[i] > P67
            └─ HIGH_DIRECTIONAL dacă bara e și `expansion` (E010, ratificată); altfel HIGH_CHOPPY
cauzalitate fereastra e [i-29, i], strict retrospectivă — identic cu `compression`, zero lookahead
```

**P33/P67 sunt TERȚILE — alegere, cu bază declarată: ocupanță egală MAXIMIZEAZĂ celula minimă**, iar celula minimă e exact constrângerea impusă de consumatorul din aval. **Nu e o alegere de gust; e derivată din nevoia consumatorului, nu din date.**

## Axa B — structură

```
run[i] = numărul de BOS consecutive de ACELAȘI semn de la ultimul CHoCH opus, cu semn
         (+ pentru bull, − pentru bear), propagat înainte bară cu bară din fluxul
         `detect_breaks` deja ratificat (semantica de cascadă v2.7.38)
```

### Pragul „puternic vs slab" NU se poate deriva. O declar ALEGERE, cu măsurătoarea care o justifică.

**Măsurat, distribuția lui |run| pe bare:**

```
|run| >= 1  99,88%     >= 2  68,17%     >= 3  49,25%     >= 4  37,93%     >= 5  27,47%     >= 6  20,11%
hazard de continuare:  0,682 → 0,723 → 0,770 → 0,724 → 0,732
```

> **De la run 2 în sus hazardul e CONSTANT la ~0,73. Distribuția e geometrică, deci procesul e FĂRĂ MEMORIE — nicio lungime de run nu e specială.** Nu există punct de tăiere natural în date. **Orice prag e o alegere. O declar ca atare, exact cum s-a cerut.**

**Și mai spun consecința, ca predicție pusă la risc înainte de date: dacă nu există structură de persistență, distincția puternic/slab va aduce PUȚINĂ putere de condiționare.** Nu e un motiv să n-o construim — **motorul de decizie o va decide singur: dacă axa e neinformativă, celulele se contractă în părinte și nu costă nimic.** Mecanismul deja ratificat testează propria mea predicție.

```
ALEGEREA, ancorată pe ocupanță egală (aceeași bază ca terțilele de la axa A):
   RANGE   |run| == 1      31,70% din bare     ← o direcție proaspăt răsturnată, nestabilită
   WEAK    |run| in {2,3}  30,24%
   STRONG  |run| >= 4      37,93%
   direcția: semnul lui run.   up 52,5%  down 47,4%  fără structură 0,1%
```

**Constatare care schimbă definiția lui RANGE, cerută explicit în mandat:** **„range = absența BOS" e imposibilă — 99,88% dintre bare au un run nenul.** Structura are practic ÎNTOTDEAUNA o direcție pe H4. **Deci RANGE nu e absența structurii, e INSTABILITATEA ei** — o direcție care tocmai s-a răsturnat și n-a fost încă confirmată. Asta e ce măsoară `|run| == 1`.

---

# PARTEA 3 — PROBABILITĂȚI: ce poate și ce NU poate însemna „Trend Long: 82%"

**Trei lecturi posibile, și doar una e simultan disponibilă și onestă:**

```
(a) probabilitatea că eticheta E „trend long"  → clasificarea e DETERMINISTĂ. Ar fi 100/0. Inutilă.
(b) fracția din fereastra recentă petrecută în direcția long → descriptivă, cauzală, DISPONIBILĂ.
(c) probabilitatea că piața VA urca            → e o PREVIZIUNE. Cere validare ca previziune. NU există.
```

**Se specifică (b), pe aceeași fereastră de 30 de bare:**

```
trend_long_share[i]  = fracția barelor din [i-29, i] cu run > 0
trend_short_share[i] = fracția cu run < 0            (sumează la 1 minus fracția fără structură)
```

> **AVERTISMENT OBLIGATORIU ÎN IEȘIRE: „Trend Long: 82%" va fi citit de orice om ca o PREVIZIUNE. Nu e. Descrie trecutul recent.** Se etichetează în ieșire ca `share`, nu ca `probability`. **O cifră care invită la o lectură pe care nu o susține e o eroare de proiectare, nu de prezentare.**

**Se aplică și aici contracția ierarhică?** **NU la nivelul 1, și motivul e curat: contracția e pentru ESTIMAREA unei probabilități din numărători rare. Aici nu se estimează nimic — se CLASIFICĂ determinist.** Contracția intervine la nivelul 6, unde celula de regim devine cheie de căutare pentru `p_t`. **Nivelul 1 produce CHEIA; nivelul 6 estimează probabilitatea. A pune contracție la nivelul 1 ar contracta ceva ce nu e o estimare.**

---

# PARTEA 4 — SCORUL DE ÎNCREDERE. Raționamentul de la nivelul 6 se transferă — și consecința e că nivelul 1 NU trebuie să aibă poartă.

**La nivelul 6 am stabilit: „confidence" nu poate însemna decât fiabilitatea lui `p`, deci aparține ÎNĂUNTRUL lui EV, nu ca poartă paralelă. Aici clasificarea e deterministă, deci nu există eroare de eșantionare în etichetă. Ce există e altceva:**

```
FRAGILITATE DE FRONTIERĂ: cât de aproape e măsura de o graniță de bandă.
  m[i] la percentila 66,8 cu tăietura la 67 → eticheta NORMAL e la un fir de HIGH.
  confidence[i] = distanța normalizată până la cea mai apropiată graniță a benzii atribuite.
```

**Iar consecința e cea care contează, și e aceeași concluzie ca la nivelul 6, pe același drum:**

> **O etichetă fragilă înseamnă că CHEIA DE CONDIȚIONARE e incertă. Incertitudinea cheii se propagă în incertitudinea lui `p_t`, care intră DEJA în `EV_LCB`. Deci nivelul 1 nu trebuie să aibă propria poartă — trebuie să-și TRANSMITĂ incertitudinea în jos, unde poarta unică există deja.**

```
MECANISM: atribuire MOALE. Bara se repartizează pe benzile adiacente cu ponderi date de
          `confidence`; `p_t` devine un amestec, iar varianța suplimentară lărgește intervalul.
          Ambiguitate mare ⇒ interval lat ⇒ `p_LCB` mic ⇒ `EV_LCB` cade ⇒ NU se tranzacționează.
```

**Cerința CEO „fără regim identificat → NU TRANZACȚIONEAZĂ" se OBȚINE ca CAZ-LIMITĂ al mecanismului general, nu ca regulă separată.** Ambele sunt satisfăcute, cu o singură poartă în tot sistemul.

## O distincție care trebuie păstrată: AMBIGUU ≠ INDISPONIBIL

```
AMBIGUU      eticheta există dar e fragilă  ⇒ ponderi moi, incertitudinea coboară la nivelul 6.
INDISPONIBIL nu există etichetă (warmup de fereastră, date lipsă) ⇒ FAIL-CLOSED, NU se tranzacționează.
```

**Aceeași distincție ca arhivat-negativ vs arhivat-insuficient, și ca `FALSE` vs `UNAVAILABLE` la știri.** Absența dovezii nu e dovada absenței, aplicată a treia oară în același sistem.

---

# PARTEA 5 — AXA DE ȘTIRI: structură acum, activare fără reproiectare

```
INTERFAȚĂ   news_state(as_of) -> (value: bool, status: {AVAILABLE, UNAVAILABLE})
FILTRU      CEO: doar USD, doar impact HIGH și MEDIUM.
FEREASTRĂ   bara e „dominată de știri" dacă un eveniment eligibil cade în [t − w_before, t + w_after].
ACUM        value = FALSE, status = UNAVAILABLE. Axa e EXCLUSĂ din ierarhie cât timp e indisponibilă.
```

## De ce DOUĂ câmpuri și nu unul — și aici e capcana care ar otrăvi datele în tăcere

**CEO cere `FALSE` până la date, și operațional are dreptate: `UNAVAILABLE` care blochează ar opri totul.** Dar:

> **Dacă axa returnează doar `FALSE`, atunci tot istoricul de dinainte de date arată ca o perioadă FĂRĂ EVENIMENTE. Când datele apar, estimarea lui `p_t | fără-știri` s-ar face pe un istoric CONTAMINAT cu bare de știri etichetate greșit — biasată, și nimeni n-ar ști.**

```
REGULĂ: `value = FALSE` (nu blochează) ȘI `status = UNAVAILABLE` (marchează).
        Fiecare decizie loghează statusul.
        Înregistrările făcute cu status UNAVAILABLE se EXCLUD din estimarea condiționată pe știri
        când datele sosesc. Nu se recuperează retroactiv — se exclud.
```

**Aceeași disciplină cu două câmpuri ca la cele două registre de familie și la cele două hash-uri.**

## Fereastra: metoda se pre-specifică, cifra NU se poate alege acum

**`w_before`/`w_after` nu pot fi derivate fără date. Se pre-specifică METODA, nu numărul:** fereastra = intervalul în jurul evenimentelor programate în care volatilitatea realizată depășește propria linie de bază, măsurată pe evenimentele eligibile după livrare. **Cifra se fixează atunci, o dată, înainte de orice utilizare.**

**O clarificare care arată a lookahead și nu e:** clasificarea folosește CALENDARUL, care e publicat în avans — programul e cunoscut cauzal la bara `t`, chiar dacă evenimentul e la `t + 30min`. **Ce NU se poate folosi e REZULTATUL evenimentului.** Programul da, rezultatul nu.

---

# PARTEA 6 — HARTA RETROSPECTIVĂ DE REGIM: confirm interdicția, și consemnez legătura

**Confirm integral: harta bear/bull/corecție e derivată din închideri lunare pe TOT istoricul, deci eticheta unei bare din 2013 depinde de prețuri din 2015. E lookahead în forma cea mai tare — eticheta FIECĂREI bare depinde de întregul viitor.**

**Nu e o descoperire nouă pentru divizie, și consemnez unde a fost deja tratată:** la criteriile DEMO ale CAND-0001 (v2.7.34) am fixat `regimes_permitted = fără filtru`, **exact pe motivul că regimul nu e calculabil live.**

> **Nivelul 1 e tocmai piesa care face condiționarea pe regim disponibilă LIVE — adică deblochează ce am refuzat atunci pentru că nu exista.** Harta retrospectivă rămâne validă pentru ce a fost folosită (stratificare descriptivă la validare); **nu devine niciodată input de decizie, iar cele două nu se amestecă și nu se compară direct.**

---

## HANDOFF

**VE construiește, în ordine:** (1) fereastra de compresie RE-DERIVATĂ în unități H4 (W=30) — **`460` NU se transplantează**; (2) axa A cu cele cinci benzi pe măsura Parkinson, fereastră cauzală [i−29, i]; (3) axa B din fluxul `detect_breaks` ratificat, cu `run` propagat și tăieturile 1 / 2-3 / ≥4; (4) `share`-urile direcționale pe aceeași fereastră, **etichetate `share`, niciodată `probability`**; (5) `confidence` ca distanță normalizată până la frontieră, cu atribuire moale către nivelul 6; (6) axa de știri cu DOUĂ câmpuri, `value=FALSE` + `status=UNAVAILABLE`.
**Red Team, ținte explicite:** dacă ocupanța egală e o ancoră legitimă sau doar o conveniență; dacă `|run|==1` e într-adevăr „range" sau doar „post-flip"; și dacă atribuirea moale poate ascunde o etichetă sistematic greșită sub un interval lărgit.
**CEO, patru lucruri:** **(1) cele nouă stări sunt DOUĂ axe plus știrile — măsurat, nu presupus: compresia e decila inferioară a axei de volatilitate, iar expansiunea e 99,5% în banda HIGH, deci cinci „stări" sunt una singură. (2) Pragul puternic/slab NU e derivabil — distribuția run-urilor e geometrică, fără memorie; îl declar ALEGERE, ancorată pe ocupanță egală. (3) „Trend Long: 82%" NU e o previziune și se etichetează `share`. (4) `COMPRESSION_WINDOW=460` e o fereastră de TRIMESTRU pe H4, nu de săptămână — iar eroarea era indetectabilă în aval, pentru că o percentilă dă aceeași rată la orice fereastră.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.49 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
