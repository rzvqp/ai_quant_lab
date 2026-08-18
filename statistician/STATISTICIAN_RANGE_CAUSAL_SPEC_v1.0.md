# STATISTICIAN — SPECIFICAȚIE CAUZALĂ RANGE ȘI EVENIMENTE DE EXECUȚIE

**Document ID:** STAT-RANGE-CAUSAL-SPEC-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Status:** `RANGE_STATISTICAL_SPEC_DRAFT_READY`
**Regim:** pauză pe cercetare — respectată integral. **Nicio rulare, niciun acces la SEALED, nicio alegere pe PnL, nicio ratificare.**
**Verificare de sursă:** citit `market_structure.detect_swings` (fractali simetrici, fereastră `2k+1`) și `regime_classifier` (`StructBand`, `Direction`).

---

# PARTEA 0 — DOUĂ LUCRURI DE AȘEZAT ÎNAINTE DE ORICE DEFINIȚIE

## 0.1 Acest mandat ÎNCHIDE un blocant pe care l-am ridicat eu

**La v2.7.69 am declarat BLOCANT: RANGE nu e derivabil din N1, iar decizia era a CEO între trei rute — primitivă nouă, separarea lui `Direction.NEUTRAL`, sau scoaterea lui RANGE din taxonomie. Mandatul de față alege prima rută: se DEFINEȘTE ca primitivă nouă. Blocantul se închide prin această specificație.**

## 0.2 COLIZIUNEA DE NUME, fixată acum ca să nu se cableze greșit

```
StructBand.RANGE  (N1, existent)  |run| == 1  →  direcție PROASPĂT RĂSTURNATĂ, INSTABILĂ.
                                                 E o TRANZIȚIE.
RANGE_STATE       (acest spec)    oscilație MĂRGINITĂ, ambele limite atinse repetat,
                                                 eficiență direcțională MICĂ. E o STARE.
```

> **Sunt aproape opuse. Nu se substituie una alteia NICIODATĂ. Numele canonic al obiectului definit aici e `RANGE_STATE`, distinct lexical, tocmai ca substituția din greșeală să fie imposibilă.**

---

# PARTEA 1 — „70%" NU E UN FAPT DESPRE PIAȚĂ. E UN FAPT DESPRE DEFINIȚIE.

> **Procentul de timp în range NU e o proprietate a XAUUSD. E o proprietate a DEFINIȚIEI aplicate lui. O definiție permisivă dă 90%, una strictă dă 15%, pe exact aceleași date. Un număr fără definiția atașată nu e o măsurătoare — e o alegere deghizată în măsurătoare.**

**E aceeași clasă cu constatarea de la banda de confluență: contorul măsura BANDA, nu piața. Nu repet eroarea sub alt nume.**

```
PROTOCOL DE MĂSURARE (de rulat DUPĂ MANDATE_2_PASS, nu acum):
  `pct_time_in_range` se raportează PENTRU FIECARE definiție din grilă, niciodată ca număr
  unic, și mereu însoțit de parametrii care l-au produs.
  Se raportează pe FIECARE din cele 4 blocuri oficiale separat, și per timeframe evaluat.
  Un procent agregat peste blocuri ascunde exact eterogenitatea căutată.
  Ipoteza de 70% se consemnează ca IPOTEZĂ CEO cu status NEVERIFICAT și se compară cu
  intervalul observat peste grilă. NU se caută definiția care produce 70%.
```

---

# PARTEA 2 — DEFINIȚIA CAUZALĂ A LUI `RANGE_STATE`

## 2.1 Constrângerea de cauzalitate, exactă

**`detect_swings` folosește fractali simetrici cu fereastră `2k+1`: un swing la bara `i` cere `k` bare DUPĂ el.**

```
swing la bara i      →  CONFIRMAT abia la bara i + k
limitele range-ului  →  cunoscute la  t_conf = max(confirmările swing-urilor folosite)

`RANGE_STATE` e ACȚIONABIL exclusiv de la `t_conf` înainte, chiar dacă limitele lui REFERĂ
bare anterioare. Începutul range-ului e RETROSPECTIV; activarea lui NU e.
Orice raportare a duratei distinge `duration_structural` (de la prima bară a range-ului) de
`duration_actionable` (de la `t_conf`). A doua e singura care contează pentru execuție.
```

## 2.2 Parametrii — cu SURSA derivării, niciunul din PnL

```
PARAMETRU               SURSA DERIVĂRII
limite H, L             extremele swing-urilor CONFIRMATE din fereastra de căutare
n_touch                 >= 2 pe FIECARE limită. Sub 2 nu există „limită atinsă repetat",
                        ci doar un extrem. Prag de FALSIFICABILITATE, nu de performanță.
tol                     × ATR — ancora de unitate deja ratificată în laborator; grila
                        explorează multipli, niciodată valori absolute.
d_min                   în BARE ale timeframe-ului evaluat, ancorat pe constantele deja
                        derivate (zi/săptămână per timeframe).
W = (H − L)/ATR         se RAPORTEAZĂ mereu; intră ca filtru doar dacă grila o include explicit.
ER                      |close_end − close_start| / Σ|close_i − close_{i−1}| pe fereastră.
                        ER mic = oscilație; ER mare = deplasare. Aritmetică pură pe bare
                        confirmate — nicio primitivă nouă.
comportament interior   fracția de bare cu close în banda mediană; numărul de traversări ale
                        mijlocului. DESCRIPTORI raportați, nu praguri implicite.
```

**Grila pre-înregistrată, MICĂ, declarată ÎNAINTE de orice rulare:**

```
n_touch ∈ {2, 3} × tol ∈ {0,10 · 0,25 · 0,50}×ATR × ER_max ∈ {0,25 · 0,40} × d_min ∈ {zi, săptămână}
Parametrii NU se ating după ce se vede un rezultat. Costul de multiplicitate: Partea 6.
```

## 2.3 RANGE vs COMPRESIE vs PAUZĂ ÎN TREND — cu suprapunerea admisă

```
RANGE_STATE   ambele limite atinse >= n_touch · ER <= ER_max · durată >= d_min
COMPRESSION   lățimea SCADE monoton pe fereastră; NU cere atingeri repetate. O compresie
              poate avea zero atingeri ale unei limite stabile — deci nu e range.
TREND_PAUSE   satisface RANGE_STATE, DAR contextul HTF (N1) e direcțional pe fereastră.
```

> **De scris, nu de ascuns: `TREND_PAUSE` e o SUBMULȚIME a lui `RANGE_STATE`, nu o alternativă. Orice pauză în trend ESTE, local, un range. Taxonomia NU e o partiție naturală, deci precedența e o DECIZIE DE MODEL — aceeași formă ca la conflictul 4-axe → 1-etichetă de la v2.7.69. Se declară și intră în `range_spec_id`; nu se deduce.**

## 2.4 Invalidarea — numai pe dovezi observabile

```
RANGE_INVALIDATED  ⟸  acceptare confirmată dincolo de o limită (BREAKOUT_ACCEPTED)
                   SAU expirarea unei durate maxime pre-declarate
                   SAU indisponibilitatea unei intrări din mulțimea necesară (fail-closed)

NU se invalidează retroactiv. Un range invalidat la t rămâne, în jurnal, ACTIV pe [t_conf, t).
Rescrierea istoriei unui episod ar schimba retroactiv contextul unei decizii deja luate —
aceeași clasă interzisă ca „N4 modifică decizia".
```

---

# PARTEA 3 — STĂRI ȘI EVENIMENTE

**Fiecare emite `LevelOutput` (contractul v2.7.59): `Ok` cu payload, sau `Unavailable(reason)`. `confirm_ts` e bara la care condiția devine cunoscută FĂRĂ bare viitoare.**

```
RANGE_ACTIVE
  inputuri      swing-uri confirmate <= t · ATR <= t · N1 (context, opțional)
  condiție      toți parametrii din 2.2 satisfăcuți pe fereastră
  confirm_ts    t_conf = max(confirmările swing-urilor folosite)
  reason        OK_RANGE · FEW_TOUCHES · ER_TOO_HIGH · TOO_SHORT · WIDTH_OUT_OF_GRID
  INDISPONIBIL  dacă range-ul va fi invalidat mai târziu; dacă limitele se vor extinde

RANGE_LOW_ZONE / RANGE_HIGH_ZONE
  condiție      close ∈ [L, L + tol×ATR]  /  [H − tol×ATR, H]
  confirm_ts    închiderea barei curente
  reason        IN_ZONE · OUTSIDE_ZONE · RANGE_NOT_ACTIVE
  INDISPONIBIL  dacă zona va fi respinsă sau străpunsă

RANGE_MID — stare EXPLICIT FĂRĂ ENTRY
  condiție      close strict între cele două zone
  reason        NO_ENTRY_BY_CONSTRUCTION
  observație    e o stare EMISĂ, nu o absență. O absență nu se poate audita; o stare da.

BREAKOUT_CANDIDATE
  condiție      close dincolo de o limită, prima dată, cu range ACTIV
  confirm_ts    închiderea barei care depășește
  reason        BREACH_UP · BREACH_DOWN
  INDISPONIBIL  DACĂ VA FI ACCEPTAT SAU EȘUAT. Aceasta e informația centrală absentă.

BREAKOUT_ACCEPTED
  condiție      N închideri consecutive dincolo de limită, N pre-declarat în grilă
  confirm_ts    închiderea celei de-a N-a bare  ⇒  ÎNTÂRZIERE de N bare față de CANDIDATE
  reason        ACCEPTED_UP · ACCEPTED_DOWN · REENTERED_BEFORE_N
  ⚠ COMPROMIS DE MĂSURAT, nu de presupus: N mai mare = acceptare mai sigură, dar mai multe
    oportunități pierdute. Se raportează `MISSED_BEFORE_ACCEPTANCE` pentru FIECARE N din grilă,
    exact ca `MISSED_BEFORE_CONFIRMATION` la nivelul 4. Un N ales fără această curbă e ALES,
    nu derivat. Și consemnez precedentul: la N4 curba a arătat că nu există compromis —
    ceasul scurt domina pe ambele axe. Nu presupun că se repetă; cer măsurătoarea.

BREAKOUT_RETEST
  condiție      după ACCEPTED, revenire în banda `tol` a limitei străpunse, fără re-închidere
                înăuntru
  confirm_ts    închiderea barei de atingere
  reason        RETEST_HELD · RETEST_FAILED_BACK_INSIDE

FAILED_BREAKOUT
  condiție      după CANDIDATE, închidere înapoi ÎNĂUNTRU înainte de a atinge N
  confirm_ts    închiderea barei de revenire
  reason        FAILED_UP · FAILED_DOWN

LIQUIDITY_SWEEP_AND_RETURN
  condiție      depășire prin FITIL peste limită + închidere înăuntru pe ACEEAȘI bară
  confirm_ts    închiderea barei
  reason        SWEEP_HIGH · SWEEP_LOW
  observație    reutilizează convenția D6 (wick-sweep-reject), deja ratificată. NU o redefinesc.

RANGE_INVALIDATED
  condiție      vezi 2.4
  confirm_ts    bara la care condiția devine adevărată
  reason        ACCEPTED_BREAK · MAX_DURATION · INPUT_UNAVAILABLE
```

---

# PARTEA 4 — FAMILII DE STRATEGII (specificație, FĂRĂ rulare)

```
COMUN TUTUROR
  ENTRY      la DESCHIDEREA barei următoare celei de confirmare. Niciodată pe bara de semnal.
  STOP       în afara limitei, cu bufferul canonic `min_executable_risk`
             = max(spread_price, 5×tick, 0,10×ATR)   — contractul de cost RATIFICAT (v2.7.73)
  GEOMETRIE  STRICTĂ la intrare (A2): LONG cere stop < entry_open < target, SHORT invers;
             altfel INVALID_EXECUTION, fără tranzacție, fără P&L.
  T4         ținta atinsă pe bara de intrare, cu stopul neatins = CÂȘTIG (v2.7.67).

F1  BUY_LOW_ZONE_REJECTION    LOW_ZONE + respingere M5 confirmată → long
F2  SELL_HIGH_ZONE_REJECTION  simetric
F3  BREAKOUT_ACCEPTED         după ACCEPTED, în direcția străpungerii
F4  BREAKOUT_RETEST           după RETEST_HELD
F5  FAILED_BREAKOUT           după FAILED_*, în direcția OPUSĂ străpungerii
F6  LIQUIDITY_SWEEP_REVERSAL  după SWEEP_*, în direcția opusă fitilului
F7  interzis prin construcție: NICIO intrare în RANGE_MID — emis ca stare, auditat ca refuz

TP, pre-declarat per familie, O SINGURĂ variantă per familie (nu ambele):
  F1/F2   mijlocul range-ului SAU limita opusă
  F3/F4   measured move (= W) SAU următoarea zonă N3
  F5/F6   limita opusă
```

> **⚠ F5 și F6 sunt CONTRARII lui F3/F4 pe aceeași limită, pe bare care se suprapun. Iau poziții OPUSE, deci sunt NEGATIV DEPENDENTE — iar BH-FDR cere PRDS. Vezi Partea 6.**

---

# PARTEA 5 — PROTOCOL DE VALIDARE

```
UNITATEA PRINCIPALĂ = EPISODUL RANGE. Nu anul calendaristic. (v2.7.69 / v2.7.72)
k_min = 5 episoade — plafonul de falsificabilitate derivat (0,5^4 = 0,0625 > 0,05).
Sub 5 episoade eligibile: ARCHIVE_INSUFFICIENT, NU eșec.

RAPORTARE OBLIGATORIE, per definiție din grilă ȘI per bloc oficial:
  n_episoade · durată (STRUCTURALĂ și ACȚIONABILĂ, separat) · lățime în ATR ·
  atingeri per limită · pct_time_in_range · false_breakout_rate ·
  breakout_acceptance_rate · MISSED_BEFORE_ACCEPTANCE per N ·
  EV_net per episod · best_episode_share · trimmed_top1 (cu n_trimmed ȘI fracția realizată) ·
  walk-forward (origine rulantă · purging pe suprapunerea perioadei de DEȚINERE · embargo 1 zi) ·
  HISTORICAL_TRANSFER separat · BASE și STRESS separat, cu DIFERENȚA ·
  MDE calculat ÎNAINTE de test · corecția BH

PERIOADĂ FĂRĂ RANGE = `NOT_APPLICABLE`, NU pierdere.
  Mecanic: e mulțimea NEELIGIBILĂ din partiția de la v2.7.71. Strategia n-ar fi tranzacționat
  acolo, deci absența ei nu e un rezultat. Se NUMĂRĂ și se raportează; nu se șterge.
```

---

# PARTEA 6 — MULTIPLICITATEA. Riscul cel mai mare al acestui mandat.

```
azi                        m = 20        prag BH de rang 1 = 0,05/20 = 0,00250
+ 7 familii                m = 27        prag = 0,05/27 = 0,00185
+ grilă de 5 definiții     m = 20 + 35   prag = 0,05/55 = 0,00091   ← de 2,7× mai strict
Familia e MONOTONĂ: coborârea pragului e PERMANENTĂ și se aplică RETROACTIV tuturor.
```

> **REGULA care previne explozia: grila de definiții NU e o mulțime de ipoteze. Se pre-înregistrează O SINGURĂ definiție PRIMARĂ; restul grilei rulează ca ANALIZĂ DE SENZITIVITATE pe rezultatul primarei. O senzitivitate nu produce p-value independent, deci nu consumă slot.**
>
> **Dar dacă se raportează „cea mai bună definiție din grilă", atunci TOATE au fost ipoteze și m crește cu toată grila. Numărătoarea e peste ce s-a EVALUAT, nu peste ce s-a RAPORTAT (v2.7.71).**

```
A DOUA PROBLEMĂ, structurală: F3/F4 vs F5/F6 iau poziții OPUSE pe aceeași limită, pe bare
suprapuse ⇒ DEPENDENȚĂ NEGATIVĂ ⇒ PRDS încălcat ⇒ BH-FDR nu acoperă perechea.
Remediul e cel deja ratificat pentru CAND-0001/CAND-0009 și CAND-0006/CAND-0037:
POPULAȚII DE TEST DISJUNCTE, cu fracția de suprapunere raportată PER BLOC ÎNAINTE de orice test.
Alternativa: BY în loc de BH, la severitate ~4,0× pe m=27. Prefer disjuncția, același motiv.
```

---

# PARTEA 7 — IDENTITATE DE CONFIGURAȚIE PROPUSĂ

```
range_spec_id = sha256 peste dicționarul ORDONAT:
   {n_touch, tol_atr, er_max, d_min_bars, width_filter, N_acceptance,
    precedence_rule (RANGE vs TREND_PAUSE), timeframe, swing_k, atr_window}

run_hash = sha256( config_hash ‖ sha256(data_identity) ‖ range_spec_id )
   config_hash include cost_model_version · cost_provenance_window · calibration_status
                 (contractul de cost RATIFICAT, v2.7.73)
   data_identity include n_blocks = 4

Un rezultat fără `range_spec_id` e NON-COMPARABIL PRIN TIP cu orice alt rezultat de range.
```

---

# PARTEA 8 — INTERDICȚII RESPECTATE, ȘI CE RĂMÂNE DESCHIS

```
RESPECTATE   nicio rulare de strategie · nicio alegere de definiție pe PnL (grila e
             pre-înregistrată, parametrii au sursă structurală) · niciun acces la 2025-11+ ·
             nicio atingere a rezultatelor TREND_UP · niciun contact cu LIVE_SHADOW ·
             NU declar RANGE sau BREAKOUT ratificat — statutul e DRAFT.

BLOCKING     ruling-ul Arhitectului nu a sosit. Îl consum când vine și semnalez orice
             contradicție ÎNAINTE de implementare, conform mandatului.
MATERIAL     precedența RANGE vs TREND_PAUSE e o DECIZIE DE MODEL (suprapunere prin
             construcție); se declară și intră în `range_spec_id`.
MATERIAL     grila se tratează ca SENZITIVITATE, nu ca ipoteze — altfel m: 20 → 55 și pragul
             se strânge de 2,7× pentru toți, PERMANENT.
MATERIAL     F3/F4 vs F5/F6 sunt NEGATIV DEPENDENTE — populații de test disjuncte, obligatoriu.
MATERIAL     N din BREAKOUT_ACCEPTED cere curba `MISSED_BEFORE_ACCEPTANCE`; fără ea e ales.
LIMITATION   `pct_time_in_range` e o proprietate a DEFINIȚIEI, nu a pieței. Niciodată un
             număr unic.
LIMITATION   durata acționabilă < durata structurală cu `k` bare, PRIN CONSTRUCȚIE. Execuția
             nu are acces la începutul range-ului.
NON-MATERIAL coliziunea de nume cu `StructBand.RANGE` — rezolvată lexical prin `RANGE_STATE`.
```

**Nu cere: gate nou, framework nou, metrică nouă. `detect_swings`, `atr14`, D6, `min_executable_risk`, contractul `Ok`/`Unavailable`, triajul în trei rezultate, `run_hash` și blocarea pe zi există toate.**

---

**Manifest:** `config/split_manifest.json` v2.7.74, secțiunea `range_causal_spec_v2_7_74`.
