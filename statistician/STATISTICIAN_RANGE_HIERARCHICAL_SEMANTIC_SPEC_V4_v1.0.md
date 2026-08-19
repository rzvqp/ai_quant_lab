# STATISTICIAN — SPECIFICAȚIE SEMANTICĂ IERARHICĂ RANGE, V4

**Document ID:** STAT-RANGE-HIERARCHICAL-SPEC-V4-v1.0 · **Data:** 2026-08-19 · **Autor:** Statistician
**Status:** `RANGE_HIERARCHICAL_SEMANTIC_SPEC_V4_READY_FOR_CEO_REVIEW`
**Contract:** `range-hierarchical-v4.0` · **următorul proprietar:** CEO, pentru aprobare

> **NU autorizez: implementarea VE · wheel final · Red Team PASS · Strategy Catalog · Alpha · AI Trader deployment · LIVE_SHADOW cutover · brokerul · tranzacții.**

---

# 0 — VERIFICĂRI ȘI DOUĂ CIFRE CARE NU SE POTRIVESC

```
raport recalculat   ba8b59a  2026-08-19 15:33:47 +0300                        ✔
manifest v2.7.87    4b281d7 · fingerprint c9c39fe742d809e83bbe36b565d2aa6b7ffc17239d29d3f398f3ce5c8693652d  ✔
Red Team 0.4.1      10c2d46  RT-RANGE-0005 (E80)                              ✔
specificațiile V1-V3, matricea BLIND-001..048, addendumul 046-048             ✔ consumate
```

## 0.1 Mandatul amestecă două populații

```
                          45 ferestre   48 ferestre   cifra din mandat
bare                        12.960        13.824        12.960   ← e cea de 45
segmente RANGE CEO             103           114           114   ← e cea de 48
segmente create de detector    552           591           591   ← e cea de 48
```

**Nu se pot folosi împreună.** Cifrele corecte pentru populația completă sunt **13.824 bare · 114 segmente RANGE · 591 segmente de detector**. Restul faptelor de pornire din mandat se confirmă exact: zero `ESTABLISHED`, zero RANGE confirmate, IoU 0, vârstă mediană 17, maximă 80, zero ating `d_min=96`, `BREACH_PENDING` plafonat la 2.

## 0.2 O cifră greșită publicată de mine, corectată acum

> **În addendumul v1.1 am scris `14.328 bare`. Corect e `13.824`: `12.513 + 1.311 = 13.824`, iar `16×96 + 16×288 + 16×480 = 13.824`. O transpunere de cifre. E a DOUĂSPREZECEA cifră greșită a mea prinsă de mine. Am corectat-o în raport cu marcaj vizibil, nu în tăcere.**

---

# 1 — CAUZA RĂDĂCINĂ, ÎN LIMBAJ SIMPLU

Detectorul de azi ține **un singur lucru în minte deodată**. Când vede un canal urcând înăuntrul unui range, trebuie să aleagă: ori canal, ori range. Alege canalul, și range-ul dispare.

Omul nu face asta. El vede **un range mare care conține un canal**. Ambele sunt adevărate în același timp, la scări diferite.

De aici vin toate cele trei eșecuri, în ordine:

```
1  Segmentul se rupe de fiecare dată când apare o structură internă.
   De aceea trăiește mediana 17 bare și maximum 80.
2  Pragul de durată cere 96 de bare — mai mult decât cel mai lung segment observat.
   De aceea starea de confirmare nu s-a atins NICIODATĂ, în 13.824 de bare.
3  Fiindcă nimic nu se confirmă, tot ce iese sunt evenimente dintr-o stare provizorie:
   sweep-uri de două bare, emise de 15 ori mai des decât vede omul.
```

**Și partea care e a mea:** la V3 am legat ancora de segment — reparație corectă — dar am lăsat pragul de durată moștenit de la un design în care „durata" măsura altceva. **La V2 poarta nu putea eșua; la V3 nu poate reuși.** V4 nu repară asta cu un număr. O repară punând scara în model: dacă range-ul macro și structura internă sunt obiecte diferite, fiecare își are propria durată, iar niciuna nu o mai moștenește pe a celeilalte.

---

# 2 — MODELUL IERARHIC

## 2.1 Trei niveluri, simultane

```
MACRO      RANGE_MACRO · TREND_UP · TREND_DOWN · TRANSITION_MACRO
INTERN     SUBRANGE · CHANNEL_UP · CHANNEL_DOWN · ACCUMULATION · DISTRIBUTION ·
           NEUTRAL_INTERNAL_STRUCTURE
EVENIMENT  SWEEP_UP · SWEEP_DOWN · FAILED_BREAKOUT_UP · FAILED_BREAKOUT_DOWN ·
           BREAKOUT_PENDING · BREAKOUT_ACCEPTED_UP · BREAKOUT_ACCEPTED_DOWN ·
           REENTRY_CONFIRMED · STRUCTURE_BREAK_UP · STRUCTURE_BREAK_DOWN
```

> **Regula centrală: o bară aparține simultan unui obiect MACRO și cel mult unui obiect INTERN. Un canal intern NU anulează range-ul macro. `IS_CHANNEL` încetează să fie un motiv de respingere și devine o observație despre nivelul intern.**

## 2.2 Identitatea

```
macro_episode_id         int, monoton, unic pe rulare
internal_structure_id    int, monoton, unic pe rulare
parent_episode_id        macro_episode_id-ul care CONȚINE structura internă;
                         NULL doar dacă structura internă apare fără macro deschis
predecessor_id           macro_episode_id-ul episodului ÎNCHEIAT din care acesta descinde
                         (ex.: range nou după un breakout acceptat)
```

**Fiecare obiect, macro sau intern, poartă obligatoriu:**

```
structural_start_ts   când a început, văzut retrospectiv
confirm_ts            când s-a putut ȘTI. Nicio decizie nu se ia la structural_start.
end_ts                când s-a încheiat; NULL cât timp e activ
boundary_lower        limita inferioară, cu banda ei
boundary_upper        limita superioară, cu banda ei
reason_codes          motivele stării curente
not_yet_available     ce anume NU se putea ști la bara curentă — câmp OBLIGATORIU, nu opțional
```

## 2.3 Cum se reprezintă imbricarea

```
Nu prin listă înlănțuită. Prin APARTENENȚĂ EXPLICITĂ:
   fiecare structură internă poartă `parent_episode_id`
   un macro activ poate avea 0..n structuri interne, dintre care CEL MULT UNA activă la bara i
   închiderea macro-ului închide implicit structura internă activă, cu end_ts = end_ts al macro-ului
Interogarea „ce e adevărat la bara i" returnează o PERECHE (macro, intern), niciodată una singură.
```

---

# 3 — EXISTENȚA RANGE-ULUI, SEPARATĂ DE TERMINAREA LUI

Opt stări distincte, care azi sunt amestecate în două:

```
1 RANGE_FORMING        precondiția structurală există, confirmarea nu
2 RANGE_CONFIRMED      s-au îndeplinit toate condițiile; episodul e ACȚIONABIL
3 RANGE_INTERNAL_MOVE  evoluție internă — canal, sub-range, acumulare. Macro NEATINS.
4 BOUNDARY_EXCURSION   preț dincolo de limită, nimic confirmat încă
5 SWEEP_CONFIRMED      excursia s-a întors; range-ul e CONFIRMAT, nu invalidat
6 BREAKOUT_PENDING     excursia persistă; ambele ipoteze rămân deschise
7 BREAKOUT_ACCEPTED    ruperea e acceptată; episodul macro se ÎNCHIDE
8 EPISODE_CLOSED       istoric, imutabil
```

> **`BREAKOUT_ACCEPTED` scrie `end_ts` și trece episodul în `EPISODE_CLOSED`. NU șterge episodul și NU îl reclasifică. Un range care s-a terminat rămâne un range care a existat. Orice interogare istorică trebuie să-l returneze cu limitele și cu `confirm_ts`-ul lui originale. Reclasificarea retroactivă e INTERZISĂ prin contract.**

---

# 4 — SWEEP SEPARAT DE BREAKOUT

## 4.1 Cronologia cauzală

```
bara b0   prima închidere dincolo de limită        → BOUNDARY_EXCURSION deschisă
                                                     not_yet_available = SWEEP_VS_BREAKOUT
b0 .. b0+K_reentry     fereastra de reintrare
   dacă apare o închidere ÎNAPOI în interior       → REENTRY_CONFIRMED, apoi SWEEP_CONFIRMED
   dacă se acumulează N_accept închideri în afară  → BREAKOUT_ACCEPTED
   dacă expiră fereastra fără niciuna              → BREAKOUT_PENDING (ambele încă deschise)
după SWEEP_CONFIRMED, în fereastra K_struct
   rupere de structură în direcția OPUSĂ sweep-ului → LIQUIDITY_SWEEP_REVERSAL
```

> **`K_reentry` și `N_accept` sunt parametri SEPARAȚI, la niveluri diferite, fără constrângerea `K <= N` moștenită. Acea constrângere e ceea ce a plafonat fiecare excursie la două bare. `K_reentry` măsoară RĂBDARE — cât timp poate lipsi prețul înainte ca absența să conteze. `N_accept` măsoară CONVINGERE — câte închideri în afară fac ruperea credibilă. Sunt mărimi diferite și nu trebuie legate una de alta.**

## 4.2 Tiparul HBL-20, ca obiect semantic

```
ACCUMULATION → SWEEP_DOWN → REENTRY_CONFIRMED → BULLISH_STRUCTURE_BREAK → MARKUP
```

Instanța măsurată (2025-08-15 → 08-18, 96 bare): acumulare 3333,06–3346,10 · low de sweep bara 52 · **reintrare confirmată abia la bara 56** · markup bara 63 · maxim ulterior 3358,49.

```
★ Pe bara 52 informația nu exista. Între 52 și 56 AMBELE ipoteze rămân deschise, iar contractul
  trebuie să emită `not_yet_available = SWEEP_VS_BREAKOUT`, nu o clasificare.
★ E OBIECT SEMANTIC. Nu strategie, nu semnal, nu intrare. Zero PnL, zero Strategy Catalog.
```

---

# 5 — DURATA ȘI SCARA

**`d_min = 96` NU se moștenește.** Fiecare nivel își are propria durată minimă:

```
d_macro       durata minimă a unui RANGE_MACRO           NEIDENTIFICAT
d_sub         durata minimă a unui SUBRANGE              NEIDENTIFICAT
d_chan        durata minimă a unui canal intern          NEIDENTIFICAT
d_event       bare pentru confirmarea unui eveniment     NEIDENTIFICAT
```

**Constrângeri structurale, obligatorii prin tip:**

```
C1  d_sub  <  d_macro        un sub-range trebuie să încapă în părintele lui
C2  d_chan <  d_macro
C3  d_event << d_sub         un eveniment nu poate dura cât structura pe care o modifică
C4  fereastra ancorei unui obiect <= durata acelui obiect
    ★ Aceasta e regula pe care am încălcat-o la V2 (ancoră pe 512 pentru un range de 96)
      și pe care am lăsat-o pe jumătate la V3.
```

## 5.1 Testul de nevacuitate — obligatoriu, pre-declarat

> **Nicio condiție nu intră în contract fără să se fi demonstrat că poate ȘI să treacă, ȘI să eșueze, pe corpusul de construcție.**

```
pentru fiecare condiție c din contract:
    n_pass(c) = câte bare/episoade o satisfac
    n_fail(c) = câte o încalcă
    dacă n_pass = 0  → CONDIȚIE MOARTĂ prin construcție   → REFUZ
    dacă n_fail = 0  → CONDIȚIE VACUĂ prin construcție    → REFUZ
raportul se publică pentru FIECARE condiție, nu doar pentru cele care trec
```

**Acest test ar fi prins ambele defecte istorice:** `TOO_SHORT` la V2 avea `n_pass = 0` (nu se declanșa niciodată), iar `RANGE_CONFIRMED` la V3 are `n_fail = 13.824`, adică `n_pass = 0`. **Amândouă ar fi fost refuzate înainte de livrare.**

---

# 6 — PARAMETRII

Pentru fiecare: ce măsoară · unitate · nivel · interval identificabil din corpus · relații · protocol de alegere · când devine neidentificabil.

| parametru | măsoară | unitate | nivel | ce spune corpusul, MĂSURAT | relații |
|---|---|---|---|---|---|
| `d_macro` | durata minimă a range-ului macro | bare | MACRO | durate observate **[4, 480]**, mediană 55, n=114 | `> d_sub`, `> d_chan` |
| `d_sub` | durata minimă a sub-range-ului | bare | INTERN | observate **[8, 132]**, n=12 | `< d_macro` |
| `d_chan` | durata minimă a canalului intern | bare | INTERN | observate **[11, 110]**, n=22 | `< d_macro` |
| `K_reentry` | răbdare: bare până la reintrare | bare | EVENIMENT | observate **[4, 22]**, mediană 10, n=65 | INDEPENDENT de `N_accept` |
| `N_accept` | convingere: închideri consecutive în afară | bare | EVENIMENT | **NEOBSERVABIL** din etichete — CEO nu numără închideri | INDEPENDENT de `K_reentry` |
| `w_atr` | semilățimea zonei | ×ATR | ambele | **NEIDENTIFICAT** sub ancora nouă | `s_max = 2·w_atr` |
| `tol_touch` | toleranța atingerii | ×ATR | ambele | NEIDENTIFICAT | `<= w_atr` |

> **★ CORECȚIE A MEA, făcută înainte de livrare. În prima redactare scrisesem `d_macro ∈ [48,288]`, `d_sub ∈ [12,96]` și `d_chan ∈ [8,96]` — din memorie, nu din măsurătoare. Le-am verificat și toate trei erau greșite: cel mai scurt RANGE macro etichetat are 4 bare, nu 48; sub-range-urile ajung la 132, nu la 96; canalele la 110. Le-am înlocuit cu distribuțiile măsurate. Singurul interval scris corect era `K_reentry ∈ [4,22]`. E a TREISPREZECEA oară când îmi prind o cifră proprie, și e din exact aceeași familie: am scris un număr fără să import măsurătoarea.**

> **Ce NU spune corpusul: coloana de mai sus dă DISTRIBUȚIA observată, nu pragul. Un `d_macro` peste 4 exclude prin construcție cel puțin un range etichetat; sub 4 e vacuu. Corpusul dă compromisul, nu punctul — punctul cere protocolul de la §6.1, pe date care nu sunt și sursa etichetelor. `N_accept` nu e nici măcar observabil aici: CEO etichetează sweep-uri prin REINTRARE, nu numărând închideri în afară.**
## 6.1 Protocolul determinist de alegere — și de ce NU se execută acum

```
1  Fiecare parametru se alege pe un corpus care NU e și sursa etichetelor de validare.
2  Alegerea se face prin regula deja folosită la w_atr: o MĂSURĂTOARE plus o REGULĂ
   (cel mai mic punct dintr-o rețea declarată care satisface o condiție derivată),
   niciodată printr-o căutare care maximizează potrivirea.
3  Ordinea e fixată: mai întâi ancora și segmentarea, apoi duratele, apoi toleranțele.
   Ancora, segmentarea și durata se identifică ÎMPREUNĂ — transplantul e ceea ce a stricat V3.
4  Fiecare valoare se preînregistrează înainte de a fi măsurată pe datele de verificare.
```

```
NEIDENTIFICABIL dacă:  corpusul de construcție e și sursa validării (cazul de acum) ·
                       condiția e vacuă sau moartă pe corpus · două valori diferite dau
                       rezultate identice (bandă goală — atunci alegerea e liberă și se declară)
```

**Lotul actual e `CEO_ASSISTED_CONSTRUCTION_ONLY`. NU poate ratifica niciun parametru. Nu aleg niciunul aici.**

**Ocuparea nu e țintă.** Cele 70% sunt o ipoteză, nu un criteriu. Procentul se raportează *după* ce definiția e fixată, nu invers.

---

# 7 — TRUTH TABLE ȘI MAȘINA DE STĂRI

## 7.1 Truth table — nivelul MACRO la bara `i`

| swings ≥2/latură | durată ≥ `d_macro` | zone disjuncte | ATR disponibil | excursie activă | → stare MACRO |
|---|---|---|---|---|---|
| nu | — | — | da | nu | `TRANSITION_MACRO` |
| da | nu | da | da | nu | `RANGE_FORMING` |
| da | da | da | da | nu | `RANGE_CONFIRMED` |
| da | da | **nu** | da | nu | `Unavailable(ZONES_DEGENERATE)` |
| — | — | — | **nu** | — | `Unavailable(ATR_UNAVAILABLE)` |
| da | da | da | da | **da** | `BOUNDARY_EXCURSION` → vezi 7.2 |
| pantă > `s_max` peste durata macro | — | — | da | nu | `TREND_UP` / `TREND_DOWN` |

> **★ Deosebirea decisivă față de V1-V3: panta mare produce `TREND` la nivel MACRO, dar un canal intern NU mai produce respingere. `IS_CHANNEL` migrează de la „motiv de refuz" la „etichetă de nivel intern".**

## 7.2 Truth table — rezolvarea excursiei

| închidere înapoi în interior ≤ `K_reentry` | `N_accept` închideri în afară | ruptură structură opusă ≤ `K_struct` | → rezultat |
|---|---|---|---|
| nu (încă) | nu | — | `BREAKOUT_PENDING` + `not_yet_available = SWEEP_VS_BREAKOUT` |
| **da** | nu | nu | `SWEEP_CONFIRMED` — macro RĂMÂNE deschis |
| **da** | nu | **da** | `SWEEP_CONFIRMED` + `LIQUIDITY_SWEEP_REVERSAL` |
| nu | **da** | — | `BREAKOUT_ACCEPTED` — macro se ÎNCHIDE, `end_ts` scris |
| fereastra expiră fără niciuna | nu | — | `BREAKOUT_PENDING` persistă până la una dintre rezolvări |

## 7.3 Tranziții permise și interzise

```
PERMISE      FORMING → CONFIRMED → {INTERNAL_MOVE, BOUNDARY_EXCURSION}
             BOUNDARY_EXCURSION → {SWEEP_CONFIRMED, BREAKOUT_PENDING, BREAKOUT_ACCEPTED}
             SWEEP_CONFIRMED → CONFIRMED            (range-ul supraviețuiește)
             BREAKOUT_ACCEPTED → EPISODE_CLOSED → (nou macro cu predecessor_id)
             orice stare → Unavailable, la lipsă de input

INTERZISE    ★ CONFIRMED → FORMING           (regres de stare, fără eveniment)
             ★ EPISODE_CLOSED → orice        (istoricul e imutabil)
             ★ reclasificarea retroactivă a unui episod încheiat
             ★ structură internă fără parent_episode_id când există un macro activ
             ★ două structuri interne active simultan
             ★ orice tranziție care folosește o bară cu index > i
```

## 7.4 Precedența

```
1  Unavailable are întâietate absolută asupra tuturor
2  la nivel MACRO: BREAKOUT_ACCEPTED > SWEEP_CONFIRMED > BOUNDARY_EXCURSION > CONFIRMED > FORMING
3  MACRO se evaluează ÎNAINTEA internului; internul nu poate schimba macro-ul
4  între două structuri interne candidate, câștigă cea cu structural_start mai VECHI
```

## 7.5 Pseudo-cod cauzal

```
la fiecare bară închisă i:
    dacă ATR indisponibil: emite Unavailable(ATR_UNAVAILABLE); return
    actualizează swing-urile confirmate cu date de la indici <= i
    # --- MACRO ---
    dacă macro activ:
        dacă excursie activă: rezolvă conform 7.2
        altfel dacă preț dincolo de limită: deschide BOUNDARY_EXCURSION,
                                            not_yet_available = SWEEP_VS_BREAKOUT
        altfel: reevaluează CONFIRMED/FORMING; NU regresa din CONFIRMED
    altfel:
        încearcă deschiderea unui macro nou (7.1); dacă predecesor există, leagă predecessor_id
    # --- INTERN --- se evaluează DOAR dacă macro e CONFIRMED sau INTERNAL_MOVE
    dacă structură internă activă: verifică continuarea; la încheiere scrie end_ts
    altfel: încearcă deschiderea uneia, cu parent_episode_id = macro curent
    emite PERECHEA (macro, intern) + reason_codes + not_yet_available
```

## 7.6 Exemple pozitive și negative, din corpus

```
POZITIV   BLIND-019 (480 bare): CEO etichetează RANGE macro 0-480 CU șase structuri interne
          (canale sus/jos și un sub-range superior). V4 trebuie să producă UN macro deschis
          pe toată fereastra și șase interne succesive. V3 produce ZERO.
POZITIV   BLIND-005 (288): un singur RANGE macro, canale interne explicit declarate de CEO
          drept microstructuri care NU anulează macro-ul.
POZITIV   HBL-20 / BLIND-022: secvența sweep → reintrare → rupere → displacement.
NEGATIV   BLIND-002 (96): CHANNEL_DOWN 0-49 apoi RANGE 56-96. Aici canalul e MACRO, nu intern —
          V4 nu are voie să-l îngroape într-un macro inexistent.
NEGATIV   orice fereastră în care CEO vede TREND în trepte: macro-ul trebuie să fie TREND,
          cu range-uri INTERNE, nu invers.
```

---

# 8 — CONTRACTUL PENTRU VE

```
contract_version              range-hierarchical-v4.0
range_state_schema_version    range-state-v4          (V2/V3 INCOMPATIBILE)
snapshot_schema_version       range-snapshot-v4
identity_version              range-identity-v4
fingerprint                   RECALCULAT; rezultatele V1-V3 devin NECOMPARABILE PRIN TIP
```

## 8.1 Schema snapshot

```
macro_stack        episodul macro activ + istoricul mărginit al celor închise
internal_active    structura internă activă sau null
internal_history   mărginit, cu parent_episode_id pentru fiecare
excursion_state    {open_bar, direction, closes_outside, reentry_seen, expires_at}
swing_buffer       swing-urile confirmate, cu fereastra de reținere DECLARATĂ
id_counters        macro_episode_id, internal_structure_id — monotone
contract_version   OBLIGATORIU în snapshot
```

> **Restaurarea unui snapshot cu altă `contract_version` trebuie să EȘUEZE ÎNCHIS, prin tip. Restaurarea tăcută a snapshot-urilor V1-V3 e INTERZISĂ.**

## 8.2 Reason codes V4

```
OK_RANGE_MACRO · RANGE_FORMING_FEW_SWINGS · TOO_SHORT_MACRO · TOO_SHORT_SUB · TOO_SHORT_CHANNEL ·
ZONES_DEGENERATE · ATR_UNAVAILABLE · BETWEEN_EPISODES · IS_TREND_MACRO ·
INTERNAL_CHANNEL_UP · INTERNAL_CHANNEL_DOWN · INTERNAL_SUBRANGE ·
SWEEP_VS_BREAKOUT_PENDING · SWEEP_CONFIRMED · BREAKOUT_ACCEPTED · LIQUIDITY_SWEEP_REVERSAL
```

**Regula de audit din contractul v2.1 se păstrează: se înregistrează PERECHEA (cod, însoțitor).** Un jurnal care păstrează `INTERNAL_CHANNEL_UP` și pierde `parent_episode_id` distruge tocmai ierarhia pentru care există V4.

## 8.3 Politica de invalidare

```
INVALIDEAZĂ macro-ul       DOAR breakout acceptat, ATR indisponibil, zone degenerate
NU invalidează macro-ul    sweep · excursie nerezolvată · canal intern · sub-range ·
                           acumulare/distribuție · atingere de frontieră
```

## 8.4 Incompatibilități cu V1-V3

```
V1  ancoră pe maxim + close    → înlocuită                      INCOMPATIBIL
V2  ancoră fixă pe 512 bare    → înlocuită cu ancoră pe obiect  INCOMPATIBIL
V3  un singur segment activ    → înlocuit cu pereche macro/intern  INCOMPATIBIL
V3  K <= N                     → ELIMINAT; parametri independenți   INCOMPATIBIL
V3  IS_CHANNEL = respingere    → devine etichetă de nivel intern    INCOMPATIBIL
toate  d_min moștenit          → durate separate pe nivel           INCOMPATIBIL
```

---

# 9 — PLANUL DE EVALUARE A PROTOTIPULUI, PREÎNREGISTRAT

```
recall + precision   pe segmente MACRO, separat pe clasă
recall               SEPARAT pentru structurile interne
IoU                  pentru limitele fiecărui obiect
eroarea limitelor    început și sfârșit, în bare, mediană și p90
stratificat          separat pe 96 / 288 / 480 și separat pe B1-B4
confuzie             RANGE vs CHANNEL vs TREND, matrice completă
precizie temporală   pentru sweep și breakout, în bare față de confirm_ts-ul CEO
zero lookahead       verificat prin construcție: nicio ieșire la bara i nu folosește index > i
snapshot/restart     rezultat BIT-IDENTIC după restaurare
AMBIGUOUS            se păstrează ca atare; NU se forțează într-o clasă
nevacuitate          raportul n_pass/n_fail pentru FIECARE condiție (§5.1)
```

> **Corpusul actual poate arăta doar că stările sunt VII și că prototipul nu e mort. NU poate produce `BLIND_PASS`. Verdictul final cere un lot NOU, nevăzut de detector, definit înainte de înghețarea prototipului.**

---

# 10 — CONTRADICȚII RĂMASE ȘI DECIZII CERUTE DE LA CEO

```
DECIZIA 1  Când un canal intern devine TREND macro? Un canal care urcă 500 de bare nu mai e
           „intern". Îmi lipsește criteriul care separă structura internă de schimbarea de regim.
           NU îl inventez: e o alegere semantică, nu una statistică.

DECIZIA 2  Un sub-range poate conține la rândul lui un sub-sub-range? Am specificat DOUĂ niveluri.
           CEO a etichetat, în câteva ferestre, structuri pe trei niveluri. Adâncimea trebuie fixată
           prin decizie — recursivitatea nemărginită face contractul netestabil.

DECIZIA 3  Corpusul de identificare a parametrilor. Cel actual e CEO_ASSISTED și nu poate servi și
           la alegere, și la validare. Fie se acceptă un lot nou etichetat independent, fie se
           acceptă explicit că parametrii rămân NEIDENTIFICAȚI și prototipul e doar structural.

DECIZIA 4  Rolurile ACCUMULATION / DISTRIBUTION sunt semantice sau derivabile? CEO le folosește
           consecvent, dar nu am o definiție cauzală care să le distingă de un sub-range obișnuit
           fără a invoca intenția participanților. Dacă rămân doar etichete umane, nu pot fi testate.

CONTRADICȚIE  Mandatul cere „durata minimă demonstrată nevacuă" ȘI „nu alege valori numerice".
              Nevacuitatea se poate demonstra doar pe un interval, nu pe un punct — de aceea am
              livrat intervale identificabile (§6) și testul (§5.1), nu valori. Semnalez tensiunea
              ca să nu pară că am ocolit una dintre cerințe.
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 · F7 `SAFETY_GUARD` · LIVE_SHADOW · broker gate. Detectorul nu a fost rerulat și configurația lui nu a fost modificată retroactiv. Zero PnL, zero strategie, zero `SEALED/OOS`.

**Manifest:** v2.7.88.
