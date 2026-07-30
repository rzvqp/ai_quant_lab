# STATISTICIAN — LINIA OBDZ REDESCHISĂ: CELE 12 TIPURI DE ZONE + CELE TREI CONFIRMĂRI M15

**Document ID:** STAT-OBDZ-LINE-REOPENED-TWELVE-ZONES-THREE-CONFIRMATIONS-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

## Consemnare obligatorie, cerută explicit

**Redeschiderea liniei OBDZ NU decurge din nicio măsurătoare sau inferență a mea.** Verdictul meu (Mandatul 3.38: `REJECTED_AT_DECLARED_PARAMETRIZATION`, linia închisă) a fost reafirmat explicit la Mandatul 3.39, respingând argumentul de reescalare la ATR-ul actual ca inferență nepermisă. Nimic din ce am măsurat sau argumentat de atunci s-a schimbat. **Aceasta e un ORDIN CTO — o decizie de alocare a resurselor laboratorului, nu o concluzie statistică a mea.** O consemnez ca atare, exact cum s-a cerut, și trec la execuție: specific și autorizez numărătorile cerute, cu rigoarea statistică ce rămâne exclusiv responsabilitatea mea, indiferent de cine a decis să redeschidă linia.

---

# DIRECȚIA 1 — CELE 12 TIPURI DE ZONE

## Corectarea numărului: 12, nu 13, cu Session Open explicit exclus acum

**Enumerarea din ordin conține 13 elemente numite** (8 în Valul 1 + 2 în Valul 2 + 3 în Valul 3), nu 12. Motivul discrepanței, verificat direct: **Session Open nu are nicio definiție sau primitivă în cod** — confirmat prin căutare exhaustivă la Mandatul 3.32 ("zero apariții session_open/SessionOpen") și niciodată rezolvat de atunci. Nu pot autoriza o numărătoare pentru ceva ce nu are nicio formulă de calculat. **Execut cu cele 12 deja corect enumerate în ordin dacă exclud Session Open din Valul 3** — exact cifra pe care ordinul o cere explicit ("Fixeaza familia... 12 tipuri de zone"). Session Open rămâne al 13-lea candidat, ÎN AȘTEPTARE, condiționat de propria lui definiție — status neschimbat, nu o respingere, doar imposibil de executat azi.

## Familia: 12, fixată acum, reconfirmată din precedentul deja ratificat

**12 tipuri numite** (Order Block, Breaker, Demand/Supply, FVG, CE-50, IFVG, BPR, Liquidity Void, PDH/PDL, PWH/PWL, Mitigation Block, Rejection Block) — aceeași cifră fixată la Mandatele 3.32-3.33, reconfirmată aici neschimbată. **Măsurătoarea descriptivă (trei brațe A/B/C) NU consumă familia** — precedent neschimbat: nu e un test de ipoteză cu propriul H0/H1/verdict, indiferent câte din cele 12 arată promițător descriptiv. Familia de 12 se aplică DOAR fazei eventuale de ipoteză formală, dacă vreunul din cele 12 devine o construcție comercială testată.

**O singură linie deja are rezultatul în mână, fără măsurătoare nouă:** Order Block × Demand/Supply — rezultatul deja măsurat în trei brațe al OBDZ-001/002 (`STATISTICIAN_OBDZ_PAIRED_TEST_VERDICT_v1.0.md`) numără ca acest element din cele 12, fără reluare.

**Rămân 10 măsurători noi de specificat și autorizat acum:**
```
Val 1 (rest, 6):  Breaker, FVG, CE-50, IFVG, BPR, Liquidity Void
Val 2 (2):        PDH/PDL, PWH/PWL
Val 3 (2):        Mitigation Block, Rejection Block   (Session Open EXCLUS, nedefinit)
```

## Metodologia — reutilizată EXACT, nu respecificată

**Aceeași metodologie, fără nicio modificare:** cele trei brațe (A = declanșator specific tipului de zonă, aliniat la bias; B = control aleatoriu aliniat la bias; C = retragere fără zonă, prin matching pe `pullback_depth` via Swing/StructureLabel, toleranță 25%/0,5×ATR cu lărgire progresivă) și aceleași ferestre (`obdz_three_arm_windows.py`, `WINDOWS` dict neschimbat: `t2_t3`, `t2_t5` PRIMAR, `t2_t10` PRIMAR, `t2_t20`, `ref92_volatility` ca referință de volatilitate generală). **Singura variabilă care se schimbă e sursa brațului A** — evenimentele-declanșator specifice fiecărui tip de zonă din lista de mai sus, deja implementate ca funcții pure (`track_breaker`, `detect_fvgs`, `detect_fvg_reactions`, `detect_inverse_fvgs`, `count_bpr`, `detect_liquidity_voids`, `compute_prior_day_levels`, `compute_prior_week_levels`, plus Mitigation Block / Rejection Block conform definițiilor ratificate la Mandatul 3.33). Zero cod nou de măsurare — doar reaplicarea scriptului existent cu o populație-sursă diferită per rulare.

**AUTORIZEZ cele 10 măsurători descriptive de mai sus, în ordinea valurilor deja stabilită** (Val 1 → Val 2 → Val 3, fiecare val condiționat de promisiunea valului anterior, cf. Mandatul 3.32). Raportare per regim, agregat, pe polaritate — obligatoriu, neschimbat.

---

# DIRECȚIA 2 — CONFIRMAREA PE M15, TREI VARIANTE

**Bara-ancoră pentru toate trei variante: `t` = bara declanșatorului compus OBDZ deja stabilit** (mitigarea calificată a OB_B, cu DemandZone_A/SupplyZone_A cross-candle suprapusă, Decizia 3, v2.7.10 — NEATINS). Populația de bază: cele 654 declanșatoare brute (275/223/156), aceeași populație pe care Varianta 3 (E010, eliminată la Mandatul 3.37) a fost testată. **Verificat direct** convenția deja existentă de atingere-zonă (`interactions.py::price_in_zone`, intersecție booleană preț↔bandă) — reutilizez principiul (suprapunere interval `[low,high]`↔`[zone_lower,zone_upper]`), aceeași logică folosită deja la Mitigation ("span suprapune zona"). **Verificat direct, prin căutare repo-wide: încă zero apariții `inside_bar` în cod** (neschimbat față de Mandatul 3.28) — Varianta 2 cere o comparație geometrică nouă, dar trivială și fără ambiguitate (nu o primitivă complexă).

## V1 — DUBLA RESPINGERE, specificată mecanic

```
bara 1 = t (ancora, neschimbată)
CAUTĂ prima bară q ∈ {t+1, t+2} unde:
  long:  (low[q]<=zone_upper ȘI high[q]>=zone_lower)  ȘI  close[q] >= low[t]
  short: (high[q]>=zone_lower ȘI low[q]<=zone_upper)  ȘI  close[q] <= high[t]
DACĂ q găsit:  entry_idx = q+1 (next-open)
               sl_price  = long: min(low[t], low[q])   |  short: max(high[t], high[q])
               bara de dimensionare (ATR sizing) = q
DACĂ nu -> ABANDONAT pentru acest declanșator, sub Varianta V1.
```

## V2 — INSIDE BAR BREAKOUT, secvență fixă, fără fereastră de căutare

```
bara 1 = t
bara 2 = t+1, INSIDE BAR:  high[t+1] <= high[t]  ȘI  low[t+1] >= low[t]
bara 3 = t+2, SPARGE ȘI ÎNCHIDE peste extrema Inside Bar-ului:
  long:  high[t+2] > high[t+1]  ȘI  close[t+2] > high[t+1]
  short: low[t+2]  < low[t+1]   ȘI  close[t+2] < low[t+1]
DACĂ ambele condiții (bara 2 ȘI bara 3) se confirmă EXACT:
  entry_idx = t+3 (next-open, "lumânarea 4")
  sl_price  = long: low[t+1]  |  short: high[t+1]
  bara de dimensionare = t+2
ALTFEL -> ABANDONAT, sub Varianta V2. (Secvență strictă, nu căutare — ori se întâmplă exact așa, ori nu.)
```

## V3 — SHIFT BAR, cu SL derivat explicit, motivul arătat

```
bara 1 = t, CU CONDIȚIA suplimentară de culoare (nu era cerută la V1/V2):
  long:  close[t] < open[t]  (bearish)   |   short: close[t] > open[t]  (bullish)
bara 2 = t+1, culoare OPUSĂ, corp mai mare, corp >=60% din propriul range:
  long:  close[t+1] > open[t+1]
         ȘI |close[t+1]-open[t+1]| > |close[t]-open[t]|
         ȘI |close[t+1]-open[t+1]| >= 0,60×(high[t+1]-low[t+1])
  short: simetric (bearish, aceleași praguri)
DACĂ confirmat:
  entry_idx = t+2 (next-open)
  sl_price  = long: min(low[t], low[t+1])   |   short: max(high[t], high[t+1])
  bara de dimensionare = t+1
ALTFEL -> ABANDONAT, sub Varianta V3.
```

**SL derivat, motiv explicit — nu ales arbitrar:** am aplicat EXACT precedentul deja stabilit la V1 din același ordin (SL sub minimul ambelor fitile relevante), nu doar sub fitilul barei 1 singure. Motivul: dacă bara 2 (reversul bullish/bearish) are propriul extrem MAI ADÂNC decât bara 1 înainte de a închide în favoarea trendului, un SL bazat doar pe bara 1 ar plasa stopul DEASUPRA unui nivel pe care prețul tocmai l-a testat și l-a respins — expunând trade-ul la un stop prematur la o simplă re-testare a aceluiași nivel deja dovedit. Plasarea sub ambele extreme (ca la V1) protejează exact împotriva acestui scenariu, cu aceeași logică, nu una nouă și nelegată.

## R geometric, nu ATR-multiplu — floor generalizat corect

**Schimbare structurală față de OBDZ-002: SL nu mai e 1,0×ATR — e nivelul geometric de mai sus.** `R = |entry_price − sl_price|` (convenția deja existentă în `partial_exit.py`, neschimbată, motorul nu necesită nicio modificare). TP1/TP2 rămân 2×R/3×R (progresia 1:2:3 păstrată, neschimbată). **Podeaua de eligibilitate se generalizează corect, nu se copiază literal:** vechea podea (0,6×ATR) era doar un proxy valabil ATÂTA TIMP CÂT R era EXACT 1,0×ATR — acum că R e derivat geometric (variază per-tranzacție), podeaua corectă e cea originală, nederivată din ATR: **R ≥ 3×cost = 3×0,20 = 0,60$**, aplicată direct pe R-ul geometric al fiecărei tranzacții, nu pe un ATR proxy.

**ATR-ul de dimensionare** (dacă mai e nevoie de el pentru vreun raportaj diagnostic, nu pentru floor) = bara indicată explicit mai sus per variantă (q la V1, t+2 la V2, t+1 la V3) — bara cea mai apropiată de intrarea reală, consecvent cu principiul deja stabilit la Mandatul 3.36.

## Constrângerea de numărare — mecanică, per variantă, per regim

**"Sub 25 pe regim, varianta se abandonează"** — aplic EXACT convenția deja folosită la fiecare hotar `INSUFFICIENT_N` din acest track: dacă ORICARE regim are sub 25 supraviețuitori pentru o variantă dată, ÎNTREAGA VARIANTĂ se abandonează (nu doar regimul respectiv) — nu o interpretare nouă, aceeași disciplină aplicată la OBDZ-002-cu-confirmare (Mandatul 3.36-3.37).

```
PENTRU fiecare variantă (V1, V2, V3), PENTRU fiecare din cele 654 declanșatoare brute:
  aplică pattern-matching-ul mecanic de mai sus (specific variantei)
  DACĂ supraviețuiește -> R=|entry-sl|; DACĂ R<0,60 -> ABANDONAT (podea)
  ALTFEL -> SUPRAVIEȚUITOR
Raportare: per regim, agregat, PE POLARITATE (obligatoriu) — pentru fiecare din cele trei variante separat.
DACĂ vreun regim < 25 supraviețuitori pentru o variantă -> acea variantă ÎNTREAGĂ, ABANDONATĂ.
```

**AUTORIZEZ EXACT numărătorile de mai sus pentru V1, V2, V3 — NU rulările.** Consecvent cu tot precedentul acestui track (numărătoare de populație ÎNTOTDEAUNA separată și anterioară oricărei rulări WP-5'): odată ce numărătorile revin, un mandat SEPARAT confirmă care variante (dacă vreuna) trec pragul și autorizează rularea efectivă.

## Familia pentru Direcția 2 — fixată acum, condiționată corect, nu presupusă

**Familia declanșatorului compus OBDZ (OBDZ-001 + OBDZ-002-fără-confirmare) rămâne 2, deja consumată.** Fiecare variantă NOUĂ (V1, V2, V3) care TRECE pragul de 25/regim ȘI e efectiv RULATĂ prin testul WP-5' consumă exact UN slot suplimentar de familie — nu trei automat, nu zero automat. **Regula fixată ACUM, înainte de a ști rezultatele numărătorii** (disciplina standard a acestui proiect): familia finală = 2 (deja consumată) + K, unde K = numărul de variante care ating pragul ȘI sunt efectiv testate (K ∈ {0,1,2,3}). O variantă abandonată ÎNAINTE de rulare (sub prag) NU consumă familie — consecvent cu precedentul stabilit (măsurătoarea/numărătoarea care nu ajunge la un test formal nu se numără).

---

## Rezumat — ce se autorizează AZI, ce urmează separat

**AUTORIZAT ACUM:** cele 10 măsurători descriptive noi (Direcția 1, val cu val); cele 3 numărători de populație (Direcția 2, V1/V2/V3, mecanic specificate mai sus).
**NEAUTORIZAT ÎNCĂ:** orice rulare WP-5' pe vreo variantă de confirmare; orice fază de ipoteză formală pe vreunul din cele 12 tipuri de zone; Session Open (nedefinit).

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
