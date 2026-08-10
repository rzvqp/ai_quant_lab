# STATISTICIAN — NIVELUL 4: CONFIRMAREA ZONEI PE M5. SPECIFICAȚIE

**Document ID:** STAT-LEVEL4-M5-CONFIRMATION-SPEC-v1.0
**Data:** 2026-08-10 · **Autor:** Statistician

**Verificare de sursă:** citit direct `config/split_manifest.json` (intrările M5 și M15_v2), `code/institutional_levels.py`, `code/market_state.py`. **Trei măsurători proprii, P&L-oarbe, făcute ÎNAINTE de propunere.** **Precondiția cerută e curată; există însă ALTA, pe care n-o cere nimeni și care e blocaj.**

---

# PARTEA 0 — PRECONDIȚIILE

## 0.1 Contextul HTF pe M5: NU e cerut. Nu e blocaj.

**Nivelul 4 măsoară comportamentul prețului față de un NIVEL, pe bare M5: penetrare, persistență, progres, revenire. Niciuna nu cere H1/H4 derivate din M5.** Contextul de regim și bias vine de la nivelele 1 și 2, calculate pe `H4_from_M15_v2` și `H1_from_M15_v2` — **ambele există, ambele CONTEXT_DERIVED_VALIDATED, verificat în manifest.**

> **Deci anularea contextului HTF pe M5 NU blochează nivelul 4.** Nivelul 4 are nevoie de bare M5 aliniate la o zonă M15, nu de HTF derivat din M5.

## 0.2 Dar EXISTĂ un blocaj, în altă parte: ferestrele de descoperire NU se suprapun

**Citit din manifest:**

```
M5      correction   descoperire  2021-07-27 → 2022-02-27
M5      bull         descoperire  2022-11-11 → 2024-06-20
M5      correction   descoperire  2026-03-10 → 2026-04-20

M15_v2  bear         descoperire  2011-07-26 → 2013-09-27
M15_v2  bull         descoperire  2016-01-11 → 2018-04-06
M15_v2  correction   descoperire  2020-08-11 → 2021-09-05
```

> **Singura suprapunere din tot tabelul e 2021-07-27 → 2021-09-05. Aproximativ 40 de zile, într-un singur regim (corecție).**

**Consecința e structurală, nu de comoditate.** Nivelul 4 confirmă pe M5 o zonă identificată pe M15. Dacă zona se identifică pe descoperire M15 și se confirmă pe descoperire M5, **setul comun de descoperire e de ~40 de zile.** Orice altceva rupe sigiliul: o bară de descoperire M15 din 2016 n-are date M5, iar o bară de descoperire M5 din 2023 cade pe teritoriu M15 care NU e descoperire.

```
BLOCAJ, declarat: nivelul 4 NU poate fi validat împreună cu nivelul 3 pe date de descoperire.
                  ~40 de zile, un singur regim, fără bull, fără bear.
CE NU E blocat:   construirea și testarea MECANICĂ a modulului (non-lookahead, fail-closed,
                  determinism) — acelea nu cer suprapunere de ferestre.
```

**Ce ar debloca: o decizie explicită de re-partiționare a M5 aliniată la M15_v2, sau acceptarea că nivelul 4 se validează pe holdout-ul M15 — adică desigilarea lui. Niciuna nu e a mea; le enunț ca opțiuni și mă opresc.** Nu propun desigilarea.

---

# PARTEA 1 — CELE PATRU MĂSURĂTORI SUNT TREI, ȘI UNA E SELECȚIA

**Tabelul de contrast are patru rânduri. Măsurat, doar două discriminează.**

```
PENETRARE      DA la ambele. Nu e o măsurătoare — e CRITERIUL DE SELECȚIE. O interacțiune fără
               penetrare nu intră în populație, deci rândul nu poate separa nimic.
PERSISTENȚĂ și REVENIRE sunt ACEEAȘI variabilă cu semn opus. Măsurat pe M5:
               persistență median 0,517   revenire median 0,483   ⇒ sumează la ~1 prin construcție.
               Tabelul CEO o arată deja: NU/DA față de DA/NU, perfect anti-corelate.
PROGRES        singura măsurătoare cu adevărat independentă de persistență.
```

> **Deci nivelul 4 are DOUĂ axe de discriminare, nu patru: PROGRES și PERSISTENȚĂ (cu revenirea = complementul ei).** A le trata ca patru ar produce praguri redundante și ar sugera mai multă informație decât există.

---

# PARTEA 2 — PRAGURILE: am încercat derivarea, și o raportez unde a eșuat

**Măsurat la prima penetrare a PDH/PDL pe M5, fereastră W=60 bare, n=1.261 interacțiuni:**

```
                                    p10      p33   median     p67      p90
încercări (bare care penetrează)   3,00    20,00    38,00    54,00    60,00
progres dincolo / ATR              0,85     2,53     4,04     5,99    12,19
persistență (fracție închise dincolo) 0,02   0,22     0,52     0,80     1,00
revenire (fracție închise înapoi)  0,00     0,20     0,48     0,78     0,98
```

## „Mai multe încercări" nu discriminează — mediana e 38 din 60

**63% dintre barele ferestrei penetrează, la interacțiunea mediană. „Efort repetat" e adevărat aproape întotdeauna.** Ca prag, numărul de încercări e saturat — a patra oară când întâlnesc acest tipar.

> **Deci EFORTUL, exprimat ca număr de încercări, NU separă absorbția de acceptare.** Ce separă e raportul efort/rezultat, iar rezultatul e PROGRESUL. **Definiția CEO e corectă tocmai în punctul pe care îl subliniază — „absorbția cere RELAȚIA dintre efort și rezultat" — iar măsurătoarea arată că efortul singur e inutil, deci relația e obligatorie, nu opțională.**

## Derivarea binomială pentru „predominant": ÎNCERCATĂ, ȘI EȘUATĂ. Spun de ce.

**Raționamentul: sub o mișcare simetrică în jurul nivelului, fracția barelor care închid dincolo ar fi ~0,5, deci „predominant" înseamnă surprinzător de mult sub simetrie. La W=60, un test unilateral p≤0,05 cere k ≥ 37 bare, adică 61,7% din fereastră.**

```
sub nul, ar trebui să treacă pragul ~5% dintre interacțiuni.
MĂSURAT: îl trec 44,7%.
```

> **Nulul binomial e mis-specificat cu un ordin de mărime. Barele dintr-o fereastră NU sunt independente — prețul care închide dincolo tinde să continue. Derivarea nu se poate folosi, iar cifra de 61,7% ar fi un prag care pare derivat și nu e.** O raportez ca eșec, nu o ascund; alternativa ar fi fost un prag cu aparență de rigoare.

## Ce rămâne: PRAGURI CA ALEGERE, cu ancoră de ocupanță egală — declarate ca atare

```
PERSISTENȚĂ  ACCEPTARE dacă fracția închiderilor dincolo >= p67 (0,80)
             ABSORBȚIE dacă <= p33 (0,22)
             între ele ⇒ NEDETERMINAT
PROGRES      ABSORBȚIE cere progres <= p33 (2,53 × ATR)
             ACCEPTARE cere progres >= p67 (5,99 × ATR)
ANCORA: terțile — ocupanță egală maximizează celula minimă, exact ancora de la nivelul 1.
        NU sunt derivate din structura fenomenului; sunt ALEGERI cu bază declarată.
```

**Consecința aritmetică, spusă înainte de rezultate: cerând AMBELE condiții în același sens, fiecare clasă va prinde CEL MULT o treime din interacțiuni, iar NEDETERMINAT va fi starea majoritară. Asta e corect — o dovadă care se declanșează mereu nu e o dovadă.**

---

# PARTEA 3 — IEȘIREA: O SINGURĂ VARIABILĂ ORDINALĂ, nu două steaguri

**Definiția interzice ca absorbția și acceptarea să fie simultan adevărate. Două booleene independente PERMIT starea contradictorie.**

```
ZoneConfirmation ∈ { ACCEPTANCE_BEARISH, ABSORPTION_PROXY_BULLISH, UNDETERMINED,
                     ABSORPTION_PROXY_BEARISH, ACCEPTANCE_BULLISH }
O singură variabilă ⇒ contradicția devine INEXPRIMABILĂ, nu doar interzisă.
```

**Aceeași unealtă ca sentinel-ul de la L-U2: se face imposibilă prin tip, nu se apără printr-un `if`.**

**Și, ca la nivelul 2: nivelul 4 NU emite probabilitate.** CEO a spus-o deja — absorbția e o DOVADĂ care modifică probabilitatea unei oportunități, nu o strategie. **Modificarea o face nivelul 6, condiționat pe descriptor.** Un singur estimator.

---

# PARTEA 4 — GRANIȚA DE TIMP, care e cea mai ușor de greșit

**Absorbția și acceptarea se măsoară pe barele de DUPĂ penetrare. Rezultatul unei tranzacții intrate la penetrare se determină pe ACELEAȘI bare.**

> **A condiționa intrarea pe un descriptor calculat din bare care determină și rezultatul e condiționare pe rezultat — lookahead față de decizie, chiar dacă fiecare bară e „închisă".**

```
REGULA, obligatorie:
  fereastra de confirmare se ÎNCHIDE la bara  hit + W.
  intrarea e permisă cel mai devreme la bara  hit + W + 1.
  Descriptorul e disponibil la hit+W+1; ORICE utilizare mai devreme e invalidă.
```

**Consecința, spusă explicit: tranzacția NU mai e cea de la nivelul 3.** Intrarea e cu W bare mai târziu, la alt preț, cu alt risc. **Confirmarea nu „filtrează" oportunitatea de pe M15 — o ÎNLOCUIEȘTE cu alta.** Asta trebuie să se vadă în politica ce o consumă, altfel se compară două lucruri diferite.

**Încadrarea CEO e deja corectă** („modifică probabilitatea unei oportunități deja identificate"); aici doar fac granița mecanică.

---

# PARTEA 5 — VOLUMUL: exclus, și motivul se reutilizează

**`tick_volume` e numărul de cotații, cu proveniență NECONFIRMATĂ, și a fost deja eliminat din formarea Order Block-ului prin decizie. Se aplică identic aici: nu intră în definiție.**

**Efortul se exprimă din OHLC pur, ca număr de încercări — dar Partea 2 arată că numărul de încercări e saturat, deci efortul intră DOAR prin raportul cu progresul.** Dacă `tick_volume` se adaugă vreodată, se marchează opțional și declarat nefiabil, **și NU poate intra în clasificarea primară** — altfel un canal de proveniență neconfirmată ar decide o dovadă.

---

# PARTEA 6 — CELE TREI MOȘTENIRI

```
1. CONSTANTE, RE-DERIVATE în unități M5, măsurate:  ZI = 274,72 bare   SĂPTĂMÂNĂ = 1.369,38 bare
   (M15 92/460 ; H1 23/115 ; H4 6/30)
   FEREASTRA W=60: NU e „20 de bare" transplantat. E orizontul de dependență de 5 ORE — cel care a
   justificat H=20 pe M15 — convertit în unități M5. **Un orizont în TIMP CALENDARISTIC se transferă;
   unul în BARE nu.** Exact inversul erorilor de la L=28 și fereastra 460.
2. schema_hash: lista ordonată a descriptorilor, W, terțilele pe progres și persistență, versiunea
   codului, și EXCLUDEREA explicită a `tick_volume`. Pre-înregistrate înainte de prima decizie.
3. REDUNDANȚĂ, verificată ÎNAINTE: descriptorii derivă din penetrarea la nivel (`institutional_levels`,
   convenția D6) și din `atr14`. AMBELE sunt primitive pe care declanșează candidații de nivel —
   CAND-0001 și toate confluențele pe nivel. **Deci nivelul 4 NU e context independent pentru ei.**
   Se atașează prin inspecția cu DOUĂ tiere (amendamentul L-R1).
```

---

# PARTEA 7 — FAIL-CLOSED ȘI ACCEPTARE

```
FAIL-CLOSED  fereastră incompletă (hit + W depășește seria) → UNDETERMINED, nu o clasă presupusă
             ATR absent/nefinit → UNDETERMINED
             zonă de la nivelul 3 absentă sau UNAVAILABLE → cascadă, UNDETERMINED
             UNDETERMINED → sentinel la nivelul 6 ⇒ NO-TRADE prin TIP

ACCEPTARE 1. zero lookahead: descriptorul la hit+W+1 citește doar bare <= hit+W; test prin perturbare.
          2. exclusivitate: ABSORPTION și ACCEPTANCE nu pot coexista — garantat prin tipul ordinal,
             asertat pe tot setul.
          3. ne-saturație: fiecare clasă <= ~1/3 din interacțiuni, UNDETERMINED majoritar.
          4. dezvăluire: `redundant_with[]` prin inspecția cu două tiere.
          5. constante: doar unități M5; nicio constantă M15 sau H4 în corp.
          6. proprietate: ∀ interacțiune UNDETERMINED ⇒ nivelul 6 == NO_TRADE.
```

---

## HANDOFF

**VE construiește** modulul și testele mecanice — **acelea NU sunt blocate de Partea 0.2.**
**Red Team, ținte:** dacă terțilele mai sunt o ancoră sau au devenit reflexul meu; dacă granița de timp din Partea 4 chiar elimină condiționarea pe rezultat sau doar o mută; și dacă „efortul e saturat" nu e cumva un artefact al ferestrei de 60 de bare.
**CEO, patru lucruri:** **(1) contextul HTF pe M5 NU e cerut de nivelul 4 — nu e blocaj. (2) DAR e altul, negăsit până acum: ferestrele de descoperire M5 și M15_v2 se suprapun ~40 de zile, într-un singur regim. Nivelul 4 nu poate fi VALIDAT împreună cu nivelul 3 pe date de descoperire; construcția și testele mecanice nu sunt blocate. Opțiunile de deblocare sunt ale tale, iar desigilarea holdout-ului nu o propun. (3) Cele patru măsurături sunt DOUĂ: penetrarea e criteriul de selecție, iar persistența și revenirea sunt aceeași variabilă (median 0,517 vs 0,483). (4) Am încercat derivarea binomială pentru „predominant" și a EȘUAT — sub nul ar trebui să treacă 5% dintre interacțiuni, trec 44,7%, deci barele nu sunt independente. Pragurile rămân ALEGERI cu ancoră de ocupanță egală, și le declar așa în loc să folosesc o cifră cu aparență de rigoare.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.54 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
