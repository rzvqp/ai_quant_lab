# STATISTICIAN — SEMANTICA RUPERILOR ÎN CASCADĂ (MK-01, `detect_breaks`)

**Document ID:** STAT-MK01-CASCADE-BREAK-SEMANTICS-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `RT-CODE-A-0002_MK01_F2F3_remediation.md` (§4, constatarea de mis-timing) și `RT-CODE-A-0001_MK01_MK02.md` (§5, F4), plus codul curent `code/market_structure.py` la comitul `f4f8fab` — structura `if/elif` per direcție și pointerii `live_*` cu o singură poziție confirmate exact cum sunt descrise.

---

# PARTEA 1 — SEMANTICA MECANICĂ

## Cauza, precis: doi vectori de eșalonare, nu unul

Comportamentul actual eșalonează din **două** motive independente, iar corectarea trebuie să le acopere pe amândouă:

```
(a) pointeri live_* cu o SINGURĂ poziție — bucla reține doar ULTIMUL swing de fiecare etichetă,
    deci celelalte swing-uri active de aceeași etichetă nu sunt nici măcar evaluate la bara c;
(b) structura if/elif ÎN INTERIORUL fiecărei direcții — chiar dacă un LH e depășit de close[c],
    e suprimat când un HH e depășit pe aceeași bară.
```

## Specificația, mecanic

```
PENTRU fiecare bară c din bloc:

  1. MULȚIMEA ACTIVĂ (filtrare UPSTREAM — mecanica patch-ului de re-armare, NESCHIMBATĂ):
       active = { s ∈ block_swings : s.confirmed_idx < c  ȘI  s.idx ∉ consumed }

  2. EVALUARE împotriva TUTUROR membrilor activi, nu doar a celui mai recent.
     px = close[c]
       BOS_BULL     pentru FIECARE s ∈ active cu s.label = HH  și  px > s.price
       CHOCH_BULL   pentru FIECARE s ∈ active cu s.label = LH  și  px > s.price
       BOS_BEAR     pentru FIECARE s ∈ active cu s.label = LL  și  px < s.price
       CHOCH_BEAR   pentru FIECARE s ∈ active cu s.label = HL  și  px < s.price

  3. EMITE câte o StructureBreak(idx = c, ...) pentru FIECARE swing calificat — toate cu idx = c.

  4. CONSUMĂ toate idx-urile calificate în ACELAȘI pas, înainte de a trece la bara c+1.
```

**Inegalitățile rămân STRICTE** (`>` / `<`), exact ca acum — consecvent cu disciplina D2. Nu se ating.

**D7 neschimbat:** fiecare swing distinct produce exact o rupere, o singură dată, și nu se re-armează niciodată. Se schimbă **doar bara pe care e înregistrată**.

## Consecință pe care exemplul din mandat nu o arată — o semnalez explicit

Exemplul (două HH stivuite) ilustrează doar cauza (a), **aceeași etichetă**. Dar formularea deciziei — *„toate swing-urile depășite de close-ul barei c produc ruperea la bara c"* — acoperă și cauza (b), **etichete diferite**: un LH depășit de `close[c]` e un swing depășit, deci trebuie să rupă la `c`.

**Implementez formularea, nu doar exemplul** — dar consemnez consecința, pentru că schimbă o precedență care a existat până acum: **de azi, un BOS_BULL și un CHOCH_BULL pot apărea pe ACEEAȘI bară** (referind swing-uri diferite: un HH și un LH), unde înainte al doilea era suprimat. **Nu e dublă numărare** — sunt două evenimente pe două referințe distincte, exact ce cere disciplina „un break per swing distinct". **De atacat explicit de Red Team**, ca decizie conștientă, nu ca efect secundar tăcut.

## Numărul NU e strict conservat — și corecția e în direcția corectă

Mandatul spune că D7 a fixat numărul. **Corect ca principiu, dar comportamentul actual nu-l livra întotdeauna:**

```
close[c] = 120 depășește HH=110 ȘI LH=115.
  ACUM:  BOS vs 110 la c; CHoCH vs 115 SUPRIMAT de elif; LH rămâne neconsumat.
         Dacă la c+1 close scade la 112 (< 115), CHoCH-ul NU se mai produce NICIODATĂ.
  DUPĂ:  ambele la bara c.
```

**Deci `elif` nu doar întârzia — putea PIERDE definitiv un break** dacă condiția lapsa pe bara următoare. Noua semantică produce, în acest caz, **mai multe** ruperi decât cea veche. **Nu e o schimbare a lui D7 — e livrarea a ceea ce D7 specifica deja** („fiecare swing distinct produce una"), pe care artefactul de o-rupere-pe-bară o sub-livra. Consemnat ca atare, nu ascuns sub „doar timing".

---

# PARTEA 2 — ORDINEA ÎN INTERIORUL BAREI: CONTEAZĂ, și am un consumator concret

**Răspunsul la întrebare e DA, și nu ipotetic.** `code/trading_strategies.py::_first_break_after` selectează prin `if best is None or b.idx < best.idx` — un `<` strict. **Cu mai multe ruperi având ACELAȘI `idx = c`, comparația nu le departajează: rămâne prima întâlnită în listă.** Până acum situația nu apărea niciodată (o rupere pe bară per tip era garantată). **De azi, ordinea listei devine semantic încărcată pentru un consumator care există deja.**

## Regula, aleasă ca să CONSERVE comportamentul, nu din estetică

```
Ruperile emise la bara c se ordonează DESCENDENT după reference_swing.idx
(cel mai RECENT swing depășit primul).
`idx` e unic per swing — detect_swings emite cel mult un Swing per bară (ramurile
is_high/is_low se exclud prin `continue`) — deci ordinea e TOTALĂ, fără tie-break.
```

**Motivul e derivat, nu preferință:** în codul actual, `live_hh` reține **ultimul** HH parcurs, adică **cel mai recent** — deci ruperea emisă azi la bara `c` referă cel mai recent swing depășit. **Ordinea descendentă păstrează exact acea referință pe prima poziție**, deci consumatorii existenți (`_first_break_after`) primesc aceeași `reference_swing` ca înainte, iar schimbarea rămâne strict una de *timing*, nu de *referință*. Ordinea ascendentă ar fi schimbat tăcut și referința.

## Dar decizia semantică din spate NU e a mea — o semnalez

`_first_break_after` alimentează `reference_swing.price` ca „nivelul BOS spart" (ex. distanța de spike la S2). **Cu mai multe niveluri sparte pe aceeași bară, „care e nivelul" devine o întrebare de strategie:** cel mai recent (cel mai apropiat) sau cel mai vechi (cel mai îndepărtat)? **Regula mea de mai sus alege implicit „cel mai recent", pentru continuitate — dar proprietarul lui `trading_strategies.py` trebuie s-o confirme conștient**, nu s-o moștenească dintr-un default de ordonare. Semnalat, nu decis de mine.

**Regulă de igienă pentru orice consumator viitor:** ordinea în interiorul barei e **doar pentru determinism/reproductibilitate** — nu codifică semnificație. Cine are nevoie de „cea mai semnificativă rupere" o calculează din `price`, niciodată din poziția în listă.

---

# PARTEA 3 — F4 NU se rezolvă aici, și suprafața lui CREȘTE

**F4** (RT-CODE-A-0001 §5): blocurile bullish și bearish rulează independent pe același `close[c]`, deci cu `live_lh.price < close[c] < live_hl.price` se pot emite simultan `CHOCH_BULL` și `CHOCH_BEAR` — două schimbări de caracter contradictorii pe o bară. **Rămâne DESCHIS — nu îl rezolv aici** (ar depăși decizia CEO și ar schimba semantica dincolo de timing).

**Dar semnalez o interacțiune reală:** de azi, fiecare direcție poate emite **mai multe** ruperi pe bară, deci numărul de perechi contradictorii posibile pe o singură bară **crește**. **Fixul de timing nu creează F4, dar îi lărgește suprafața** — de luat în calcul la reatacul Red Team și la ratificarea finală.

---

# PARTEA 4 — CE E AFECTAT: corectez premisa mandatului

**Premisa („detectoarele MK-01 nu au fost folosite în niciun candidat… nimic nu se re-rulează") e ADEVĂRATĂ pentru candidați și FALSĂ în general. Verificat direct, nu acceptat.**

```
✅ CONFIRMAT — candidații sunt curați:
   institutional_levels.py : `from market_structure import Block`   (doar Block)
   imbalance_mechanics.py  : `from market_structure import Block`   (doar Block)
   market_state / interactions / order_block_void : nu importă deloc market_structure
   ⇒ niciun CAND-000x nu atinge detect_breaks.

❌ DAR — `code/trading_strategies.py` CHEAMĂ detect_breaks, în patru locuri:
   linia 173 → detect_s2      linia 203 → detect_s3
   linia 276 → detect_s10     linia 305 → detect_s11
```

**Și consumul e sensibil la TIMING, nu doar la existență:** `_first_break_after(breaks, kind, lo, hi)` filtrează pe `lo < b.idx <= hi` — o **fereastră de calificare de 20 de bare** (Grupa A) ancorată pe indexul ruperii. O rupere deplasată cu până la N−1 bare poate **intra sau ieși din fereastră**, deci schimbă nu doar bara de intrare, ci **eligibilitatea însăși** a setup-ului.

**Consecință: rezultatele descriptive deja măsurate pentru S2, S3 și S11 au consumat ieșirea `detect_breaks` și sunt, în principiu, afectate.** (S10 e oricum exclus — rebuclă deschisă.)

**Ce NU e afectat, verificat:** `detect_s1` **nu** apelează `detect_breaks` (cele patru apeluri sunt doar în s2/s3/s10/s11) — deci **verdictul SMC_S1 STATISTICALLY REJECTED rămâne neatins**. La fel S7, S13, S16, S17.

## Calibrarea onestă a magnitudinii — nu o exagerez

**Nu susțin că rezultatele S2/S3/S11 sunt greșite material.** Cazul de cascadă cere ≥2 swing-uri de aceeași etichetă, active și neconsumate, depășite de un singur close — Red Team confirmă că e **accesibil**, dar și că **nu e testat niciodată** („no test sustains a close above ≥2 stacked unconsumed same-label swings"). **Frecvența lui e necunoscută.**

**Pasul corect, în această ordine:** (1) VE implementează semantica; (2) se **măsoară frecvența cascadei** pe datele de descoperire — de câte ori o bară rupe ≥2 swing-uri active; (3) **abia atunci** se decide dacă S2/S3/S11 cer re-rulare. **Dacă frecvența e neglijabilă, nu se re-rulează nimic** și constatarea rămâne consemnată. **Dacă nu e, re-rularea e o corecție de execuție, nu un test nou — deci NU consumă familie** (nu e o ipoteză nouă, e aceeași ipoteză pe un detector reparat).

**Nu declanșez nicio re-rulare aici.** Semnalez că afirmația „nimic nu se re-rulează" nu poate fi susținută înainte de pasul (2).

---

## Ce NU se schimbă, reconfirmat

**D2** (inegalități stricte, ambele laturi) — neatins. **D7 pentru bazine** (`liquidity_mechanics`, consumare la prima măturare) — neatins, alt modul. **Precondiția de ordonare F3** — neatinsă (inclusiv constatarea Red Team că e *over-strict* global-vs-per-bloc, care rămâne deschisă separat). **Filtrarea `consumed` UPSTREAM** — neatinsă, e chiar mecanica pe care se sprijină pasul 1.

## HANDOFF

**VE** implementează Partea 1 + Partea 2, și **măsoară frecvența cascadei** (Partea 4, pasul 2) în același pas — e ieftin și decide singura întrebare rămasă deschisă. **Red Team** reatacă, cu trei ținte numite explicit: BOS+CHoCH pe aceeași bară (Partea 1), ordinea încărcată semantic pentru `_first_break_after` (Partea 2), suprafața lărgită a lui F4 (Partea 3). **Apoi** ratificarea finală.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.38 (commit `b1fdb08`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
