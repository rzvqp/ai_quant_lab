# STATISTICIAN — DIAGNOSTIC SEMANTIC RANGE ȘI SPEC V2

**Document ID:** STAT-RANGE-SEMANTIC-DIAGNOSIS-V2-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Status livrat:** `RANGE_SEMANTIC_SPEC_V2_DRAFT_READY`
**Ruling:** **`SEMANTIC_SPEC_DEFECT`** — remediu `ve_n1_replay 0.3.0`
**Regim:** fără backtest · fără PnL · fără cost gates · fără selecție de parametri pe rezultate · fără strategie · fără OOS/SEALED. LIVE_SHADOW și AI Trader neatinse; broker dezactivat.

---

# PARTEA 0 — VERIFICAREA DIN GIT, ȘI DOUĂ CONTRADICȚII DE SEMNALAT

**Verificate, toate PREZENTE și corecte:**

```
ve_n1_replay 0.2.0 wheel  SHA-256 real = 04b96a8b78b2d09bd8b54bd8044058282c6ab24bf2ac0f2aaec6c1f7a278786f
                          = DECLARAT în mandat.  ✔ MATCH (re-hash-uit de mine din wheel)
1dc355b  „ve_n1_replay 0.2.0: RANGE_STATE + longitudinal breakout events (N1 byte-identical)"  ✔
3577026  „ve_n1_replay 0.2.0 delivery: finalize manifest (build 1dc355b), cite d0d08c1/aec8f07" ✔
898e1b9  „RT-RANGE-0002: ve_n1_replay 0.2.0 RANGE_STATE_HANDOFF_PASS (E77)"                    ✔
d0d08c1  spec Statistician · aec8f07 manifest v2.7.77 · cbc576c raport Alpha                   ✔
```

## Contradicția 1 — formula mea pentru `n_generated_total` s-a învechit

```
la v2.7.75 am publicat:  m_total = completed + failed = 231 + 126 = 357   ✔ ATUNCI
azi:                     m_total = 363,  dar completed + failed = 357 în continuare
cauza, verbatim din cbc576c: „F1-F6: 6 new economic mechanisms registered ->
                              n_generated_total 357->363"
```

> **Nu e o contradicție cu mandatul — 363 e corect. E o contradicție cu FORMULA pe care am publicat-o eu. Contorul numără acum și ipoteze GENERATE dar neexpediate. Redenumirea pe care am cerut-o (`m_total → n_generated_total`) e exact ce face noua valoare coerentă: numără GENERATE, nu EXPEDIATE. Corectez formula: `n_generated_total >= completed + failed`, cu egalitate doar când coada e goală.**

## Contradicția 2 — „config hash `aec8f07`" numește obiectul greșit

```
aec8f07  = COMMIT-ul git al manifestului v2.7.77 în alpha-automation
content_hash al v2.7.77 = aa12f8804540301bcd95dd6066d8d4680bfd868b7d22be7b95c57c980457fba4
```

**Sunt două obiecte diferite. Le semnalez ca nimeni să nu verifice integritatea manifestului contra unui hash de commit. Ambele sunt corecte ca referințe; doar eticheta „config hash" e aplicată greșit.**

---

# PARTEA 1 — STATUTURI ÎNREGISTRATE

```
RANGE_SPEC_SEMANTIC_MISMATCH_PENDING_DIAGNOSIS   →  DIAGNOSTICAT în acest document
F1-F6                        BLOCKED_PENDING_RANGE_SEMANTIC_FIX
cele 44 ipoteze breakout     BLOCKED_PENDING_RANGE_SEMANTIC_FIX
                             (statut Alpha: EVENT_REACHABLE_BUT_TOO_RARE)
NICIUNA nu e declarată falsificată. Un detector care nu se activează nu falsifică nimic.
INVARIANTE NEATINSE: n_generated_total = 363 · m_inference = 26 · tombstones ·
                     verdictele existente · registrul Alpha · F7 = SAFETY_GUARD
```

> **Rezultatul Alpha (ESTABLISHED 23/355.696 = 0,0065%) NU e o măsurătoare despre XAUUSD. E o măsurătoare despre DEFINIȚIA MEA. Distincția e aceeași pe care am impus-o la banda de confluență și la „70%": contorul măsura banda, nu piața.**

---

# PARTEA 2 — `RANGE_SEMANTIC_CORPUS_MANIFEST`

**Intervalele sunt REZOLVATE DIN BARE CANONICE, nu estimate din capturi. Populația canonică livrată: 197.094 bare, 4 blocuri oficiale.**

```
episode_id  fisier                       interval captura        bare canonice  interval canonic exact       rol
RC-01       range3.pdf                   2015-12-10 → 12-18                  0  —                            POZITIV
RC-02       range4.pdf                   2015-12-21 → 12-30                  0  —                            POZITIV
RC-03       range5.pdf                   2016-12-20 → 12-27                460  2016-12-20 → 2016-12-27      POZITIV
RC-04       range6.pdf                   2016-09-21 → 10-31               2668  2016-09-21 → 2016-10-31      POZITIV
RC-05       range7.pdf                   2022-12-01 → 12-31                873  2022-12-16 → 2022-12-30      POZITIV
RC-06       range8.pdf                   2022-12-15 → 12-29                785  2022-12-16 → 2022-12-29      TRANZIȚIE
RC-07       channel bullish si range.pdf —                                  —   de rezolvat la livrarea VE   CONTROL NEG.
RC-08       range si trend bearish.pdf   —                                  —   de rezolvat la livrarea VE   CONTROL NEG.
simbol/timeframe pentru toate: XAUUSD / M15
```

## ★ Constatare pe care mandatul o cerea doar pentru un fișier, iar eu am aplicat-o la toate

> **RC-01 și RC-02 (decembrie 2015) au ZERO bare canonice. Cad în golul dintre blocul 1 (se termină 2013-09-27) și blocul 2 (începe 2016-01-11). NU sunt în populația canonică, deci NU pot susține nicio inferență — pot fi folosite EXCLUSIV semantic, ca etichete vizuale.**
>
> **RC-05 și RC-06 sunt TRUNCHIATE la stânga: blocul 4 începe 2022-12-16, deci prima jumătate a lui decembrie 2022 nu există canonic. Intervalul din captură depășește populația; intervalul canonic e cel din tabel, nu cel din captură.**

```
suprapunere: RC-05 ∩ RC-06 = 2022-12-16 → 2022-12-29 (RC-06 ⊂ RC-05). Se numără O SINGURĂ DATĂ
             în orice statistică de ocupare; altfel episodul e dublat.
start structural retrospectiv / primul moment cauzal: se completează din urma per-bară la
             livrarea VE (necesită producătorul, care nu există în forma corectă).
ieșire (bullish/bearish/failed/sweep): eticheta CEO se păstrează ca ATRIBUT SEMANTIC,
             neverificată, până la detectorul corectat.
```

**Capturile sunt ETICHETE SEMANTICE ale CEO, nu selecție după PnL. Le tratez ca atare: definesc CE trebuie să recunoască detectorul, nu CÂT trebuie să câștige.**

---

# PARTEA 3 — FUNNEL-UL DE RESPINGERE AL 0.2.0. Măsurat.

**Geometria pură a definiției, pe populația canonică: 197.094 bare, 26.824 swing-highs, 26.899 swing-lows, ferestre de 96 bare eșantionate din 8 în 8 → 24.623 ferestre.**

```
etapa                                      rămase    % din ferestre
ferestre evaluate                          24.623        100,000%
au >=1 swing sus ȘI >=1 jos                24.623        100,000%
ER <= 0,40                                 24.496         99,484%   ← NU leagă
>= 2 atingeri pe limita SUS                 1.400          5,686%
>= 2 atingeri pe limita JOS                   953          3,870%
AMBELE limite (regula completă)                61          0,248%   ← rezultatul
```

```
ER măsurat pe 96 bare: mediană 0,102 · p90 0,242 · fracție ER<=0,40 = 99,48%
atingeri SUS: mediană 0 · ZERO atingeri în 77,8% din ferestre · >=2 în 5,7%
atingeri JOS: mediană 0 · ZERO atingeri în 83,1% din ferestre · >=2 în 3,9%
```

> **Semnătura e „mediană ZERO atingeri". Nu „puține" — ZERO. Prețul practic nu revine niciodată la 0,25×ATR de extremul ferestrei.**

## Contrafactualul care izolează mecanismul

```
limita ca LINIE, față de extremul FINAL al ferestrei (regula specificată):   0,248%
limita ca ZONĂ,  față de extremul CURENT la momentul barei:                 17,658%
                                                                     factor  71×
```

## Măturarea de diagnostic — care criteriu LEAGĂ

```
 d_min   tol=0,25   tol=0,50   tol=1,00
    24     0,311%     6,831%    53,237%
    48     0,279%     6,549%    44,575%
    96     0,212%     4,784%    33,861%
   192     0,179%     4,071%    29,281%
```

> **Pe orizontală (toleranța), la `d_min` fix: 0,212% → 33,9%. FACTOR ~160×.**
> **Pe verticală (`d_min`), la toleranță fixă: 0,311% → 0,179%. FACTOR 1,7×.**
>
> **Toleranța domină cu DOUĂ ORDINE DE MĂRIME. `d_min` contribuie cu mai puțin de un factor 2.**

## Verdictul pe fiecare cauză candidată din mandat

```
defect de implementare              ✗  geometria singură reproduce aproape-zero; RT PASS;
                                       Alpha a reprodus identic de două ori, 3 ere
`d_min = 96` prea mare              ✗  factor 1,7×. Real, dar NU cauza.
`ER_max`                            ✗  trece 99,48%. Nu leagă deloc.
criteriul de touch + toleranța ATR  ✓✓ FACTOR ~160×. CAUZA PRINCIPALĂ.
resetarea limitei la structura      ✓  FACTOR 71× (contrafactualul). Aceeași cauză, alt unghi:
internă / extremul curent              limita e ancorată pe un PUNCT care se DEPLASEAZĂ
combinare incompatibilă             ✓  cele două de mai sus se AGRAVEAZĂ reciproc (vezi Partea 4)
confundare cu trend/canal           —  nedeterminabil până când detectorul se activează
```

---

# PARTEA 4 — DE CE E DEFECT SEMANTIC, NU BUG. Argumentul structural.

**Definiția mea conține trei cerințe care se BAT ÎNTRE ELE, iar conflictul e demonstrabil fără nicio rulare:**

```
(1) limita := extremul swing-urilor CONFIRMATE din fereastră
    ⇒ este MAXIM PE O MULȚIME CRESCĂTOARE ⇒ NEDESCRESCĂTOR în lungimea ferestrei
(2) atingere := close la <= 0,25×ATR de acea limită
(3) durată >= 96 bare
```

> **Ca să atingi (3) trebuie să crești fereastra. Creșterea ferestrei ridică limita prin (1). Ridicarea limitei INVALIDEAZĂ RETROACTIV atingerile numărate prin (2), fiindcă ele fuseseră aproape de limita VECHE, mai joasă. Cu cât ceri o durată mai mare, cu atât distrugi mai multe dintre propriile atingeri.**
>
> **Nu e o implementare greșită a unei definiții bune. E o definiție care nu se poate satisface. Implementarea a executat-o fidel — de asta RT a dat PASS și de asta Alpha a reprodus-o identic.**

## Ce am greșit eu, exact

**La v2.7.77 am scris că `tol = 0,25×ATR` e „valoarea de mijloc a grilei — aleasă ÎNAINTE de orice rezultat, pentru a nu fi nici cea mai permisivă, nici cea mai strictă". Raționamentul era despre POZIȚIA ÎN GRILĂ. Nu am verificat niciodată dacă GRILA ÎNSĂȘI acoperă regiunea semantic plauzibilă.**

```
grila mea {0,10 · 0,25 · 0,50}×ATR  →  cel mai PERMISIV membru dă 4,78%
regiunea semantic plauzibilă începe abia pe la 1,00×ATR (33,9%)
```

> **O alegere atentă în interiorul unui interval greșit e tot greșită. Asta e eroarea, și e a mea.**

---

# PARTEA 5 — RULING

```
                    ★  SEMANTIC_SPEC_DEFECT  ★
remediu: contract nou + versiune nouă  →  ve_n1_replay 0.3.0
NU `IMPLEMENTATION_BUG_ONLY`: geometria definiției singură reproduce aproape-zero.
NU `MIXED`: nu am nicio dovadă de abatere a implementării de la spec. Dacă urma per-bară
   livrată de VE arată o abatere, ruling-ul se REVIZUIEȘTE la MIXED — condiție pre-declarată.
NU ratific noul detector. Ruling-ul e despre CAUZĂ, nu o aprobare.
```

---

# PARTEA 6 — `RANGE_SEMANTIC_SPEC_V2` (DRAFT)

## 6.1 Schimbarea centrală: limita e o ZONĂ ANCORATĂ, nu un punct mobil

```
V1 (defect)   boundary = extremul curent al swing-urilor; touch = close la <= tol de acel punct
V2            boundary_zone = [anchor − w, anchor + w], unde
              anchor  = MEDIANA extremelor swing-urilor de pe acea latură din fereastră
                        (mediană, nu max ⇒ NU e monotonă în lungimea ferestrei ⇒ nu se
                         auto-invalidează; un singur spike nu mută limita)
              w       = lățime de zonă, în unități ATR, PRE-ÎNREGISTRATĂ
touch   = orice bară al cărei INTERVAL [low, high] intersectează `boundary_zone`
          (interval, nu close ⇒ o respingere prin fitil E o atingere, semantic corect)
```

**Cele două schimbări atacă exact cei doi factori măsurați: mediana în loc de max elimină factorul 71×; zona în loc de linie elimină factorul 160×. Nu adaug criterii — le REPAR pe cele existente.**

## 6.2 Persistența peste structura internă

```
BOS/CHoCH INTERN nu invalidează RANGE_STATE. Un range conține prin definiție rupturi de
structură interne — altfel n-ar oscila. Invalidarea vine EXCLUSIV din acceptarea confirmată
DINCOLO de `boundary_zone` exterioară.
`structure_events_inside` se NUMĂRĂ și se raportează ca descriptor, niciodată ca invalidare.
```

## 6.3 Două clase, derivate din corpus, nu alese

```
INTRADAY_RANGE   d_min = 24 bare M15 (6 ore)   — ancorat pe sesiune
MULTIDAY_RANGE   d_min = 96 bare M15 (o zi)    — constanta deja derivată
Justificarea e SEMANTICĂ, nu de performanță: RC-03 (460 bare) și RC-04 (2.668 bare) sunt
episoade multi-zi; RC-05 conține „aproximativ trei range-uri" în 873 bare ⇒ episoade
individuale sub o zi. O clasă unică nu poate reprezenta ambele.
Cele două clase sunt IPOTEZE SEPARATE dacă se testează separat (regula de multiplicitate).
```

## 6.4 Separarea range / canal ascendent / canal descendent

```
RANGE_STATE      panta regresiei pe close în fereastră ≈ 0 în unități ATR/bară
                 |slope| × d_min <= s_max × ATR   (s_max pre-înregistrat)
CHANNEL_UP/DOWN  |slope| depășește pragul, DAR ER rămâne mic și ambele limite sunt atinse
                 ⇒ e oscilație ÎNCLINATĂ, nu range
Controalele negative RC-07/RC-08 există exact ca să falsifice această separare: dacă
detectorul le marchează RANGE_STATE, separarea a eșuat. Sunt criteriul de FAIL, nu decor.
```

## 6.5 RANGE_STATE în interiorul unui trend mai mare · TREND_PAUSE

```
RANGE_STATE se evaluează pe FEREASTRA LUI, independent de contextul HTF.
TREND_PAUSE = RANGE_STATE ∧ context HTF direcțional  ⇒  SUPRAPUNERE, nu subtip exclusiv.
Precedența `RANGE_STATE_OVER_TREND_PAUSE` rămâne declarată și hash-uită; contextul de trend
se păstrează ca ATRIBUT (`trend_context`), nu se pierde. Taxonomia NU e o partiție și nu
pretind că e — confirmat numeric deja (cele trei stări de trend însumează exact bar_count).
```

## 6.6 Cauzalitate, snapshot, exclusivitate

```
structural_start_ts   prima bară a ferestrei — RETROSPECTIV
confirm_ts            max(confirmările swing-urilor folosite) — PROSPECTIV; >= k bare mai târziu
                      ZERO LOOKAHEAD: fiecare câmp folosește exclusiv bare <= confirm_ts
snapshot/restart      starea longitudinală serializabilă integral; restaurarea reproduce
                      BIT-IDENTIC — altfel starea incrementală e a doua sursă de adevăr
exclusivitate         BREAKOUT_ACCEPTED ⊕ (FAILED_BREAKOUT ∪ LIQUIDITY_SWEEP): din
                      BREAKOUT_CANDIDATE tranzițiile sunt EXCLUSIVE prin mașina de stări,
                      deci disjuncția e o PROPRIETATE, nu o constrângere impusă
raportare dublă       ocupare STRUCTURALĂ retrospectivă ȘI ocupare ACȚIONABILĂ post-confirmare,
                      întotdeauna separat
```

---

# PARTEA 7 — CRITERII PASS/FAIL, MĂSURABILE

```
PASS cere TOATE:
  P1  fiecare episod POZITIV din corpusul de construcție (RC-03, RC-04, RC-05) conține
      >= 1 interval RANGE_STATE care se SUPRAPUNE >= 50% cu intervalul canonic al episodului
  P2  niciun CONTROL NEGATIV (RC-07, RC-08) nu produce RANGE_STATE pe intervalul de canal
  P3  ocuparea acționabilă pe populația canonică e în (0,5%, 60%) — interval LARG, deliberat:
      exclude „aproape zero" și „aproape tot", fără să țintească vreo valoare
  P4  zero-lookahead verificat: perturbarea barelor > confirm_ts nu schimbă niciun câmp
  P5  snapshot→restore reproduce BIT-IDENTIC
  P6  BREAKOUT_ACCEPTED și FAILED/SWEEP: zero coliziuni pe aceeași bară
FAIL dacă oricare cade. `P3` NU e o țintă de 70% și nu se acordează pentru a o atinge.
```

---

# PARTEA 8 — SEPARAREA CORPUSULUI, PRE-ÎNREGISTRATĂ ACUM

```
CONSTRUCȚIE / CALIBRARE SEMANTICĂ   RC-03 · RC-04 · RC-05          → VE primește intervalele
BLIND DE VALIDARE SEMANTICĂ         RC-06 · RC-07 · RC-08          → VE NU le primește
RC-01 · RC-02  în afara populației canonice ⇒ EXCLUSE din ambele; utilizare exclusiv semantică
Intervalele blind se transmit Red Team, nu VE. Pre-înregistrate ÎNAINTE de orice verificare.
NU se alege definiția care apropie ocuparea de 70%. NU se alege „cea mai bună" grilă.
```

---

# PARTEA 9 — CONTRACTE ȘI VERSIUNI DE SCHIMBAT

```
ve_n1_replay              0.2.0 → 0.3.0     RANGE_STATE producer: ancoră MEDIANĂ + zonă +
                                            persistență peste BOS/CHoCH intern + două clase
range_state_schema        v1 → v2           boundary_zone, anchor, w, structure_events_inside,
                                            range_class, slope
range-events              v1 → v2           touch pe INTERVAL, nu pe close
range_spec_id             recalculat        parametri noi ⇒ fingerprint nou ⇒ rezultatele 0.2.0
                                            devin NON-COMPARABILE PRIN TIP (automat)
N1 contract / router      NESCHIMBATE       RANGE_STATE e producător separat; N1 rămâne
                                            byte-identic — cerință, nu preferință
N3 / N4 / EV / N6         NESCHIMBATE       conform verdictului arhitectural RT
```

---

# PARTEA 10 — PLANUL DE VERIFICARE BLIND (Red Team)

```
1. VE livrează 0.3.0 antrenat/calibrat semantic DOAR pe RC-03/04/05
2. Red Team rulează pe RC-06/07/08, ale căror intervale VE nu le-a văzut
3. RT verifică P1-P6; P2 pe controalele negative e testul DECISIV — un detector care
   marchează un canal drept range a eșuat, indiferent de ocupare
4. RT verifică independent zero-lookahead și snapshot bit-identic
5. Nicio ratificare fără RT PASS + aprobare CEO. Eu nu ratific detectorul.
```

---

# PARTEA 11 — DESCHIS, CLASIFICAT

```
BLOCKING     niciunul pentru livrarea acestui diagnostic.
MATERIAL     RC-01 și RC-02 au ZERO bare canonice ⇒ utilizare exclusiv semantică, fără inferență.
MATERIAL     RC-05/RC-06 trunchiate la 2022-12-16; intervalul din captură depășește populația.
MATERIAL     RC-06 ⊂ RC-05 ⇒ se numără o singură dată în orice statistică de ocupare.
MATERIAL     formula mea pentru `n_generated_total` s-a învechit: 363 ≠ completed+failed = 357.
             Corectată la `>=`, cu egalitate doar când coada e goală.
MATERIAL     „config hash aec8f07" numește COMMIT-ul, nu `content_hash` (aa12f880…).
LIMITATION   RC-07/RC-08 nu au încă intervale canonice rezolvate — capturile nu conțin date
             suficiente; se rezolvă la livrarea VE, împreună cu urma per-bară.
LIMITATION   „confundare cu trend/canal" rămâne NEDETERMINABILĂ până când detectorul se
             activează. De asta controalele negative sunt în subsetul BLIND.
LIMITATION   ruling-ul e SEMANTIC_SPEC_DEFECT pe dovezile disponibile; se REVIZUIEȘTE la MIXED
             dacă urma per-bară a VE arată o abatere a implementării de la spec.
```

**Zero modificări în Alpha, AI Trader, LIVE_SHADOW sau datele SEALED. `n_generated_total = 363`, `m_inference = 26`, tombstones, verdictele și registrul Alpha — neatinse și verificate neatinse.**

---

**Manifest:** `config/split_manifest.json` v2.7.78, secțiunea `range_semantic_diagnosis_v2_7_78`.
