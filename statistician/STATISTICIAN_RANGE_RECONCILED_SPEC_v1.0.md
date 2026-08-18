# STATISTICIAN — SPECIFICAȚIE RANGE RECONCILIATĂ: MULTIPLICITATE, CONTRACT, EVENIMENTE

**Document ID:** STAT-RANGE-RECONCILED-SPEC-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Status livrat:** `RANGE_STATISTICAL_SPEC_RECONCILED_READY`
**Metodă:** stabilit **EXCLUSIV DIN GIT**. Nicio implementare, nicio evaluare PnL, niciun acces SEALED, nicio rulare Alpha, nicio reinterpretare de enum-uri vechi, nicio atingere a LIVE_SHADOW, **nicio declarație de ratificare**.
**Consumat:** `RT-RANGE-0001` (`5e56396`, LEDGER [76]) · retragerea CEO `bd60c7a` · `71ebd13` · `loop_state.json` · `hypothesis_registry.json` · `duplicate_tombstones.json` · `N1_LEDGER_META.json` · `CANONICAL_RERUN_SUMMARY.json`.

---

# PARTEA 0 — CONSUMAREA RAPORTULUI RED TEAM, ȘI O CONVERGENȚĂ CARE CONTEAZĂ

**Toate cele șapte constatări sunt integrate. Nicio contradicție cu specificația mea — raportul o CONFIRMĂ și îi adaugă mecanismul:**

```
RT (static, din cod)   `applicable_regimes` @fbc0f20 L65 emite BREAKOUT_TRANSITION doar dacă
                       `is_displacement AND structure=="range"`; dar `RawAxesBuilder` @21ae632
                       setează structure NUMAI prin _BREAK_KIND_TO_STRUCTURE_DIRECTION =
                       {bos_bull/bos_bear→"strong", choch_bull/choch_bear→"weak"}, iar
                       `BreakKind` @61cbd58c are doar acele patru ⇒ structure ∈ {None, weak,
                       strong}, NICIODATĂ "range" ⇒ predicatul nu poate fi ADEVĂRAT NICIODATĂ.
EU (empiric, din ledger) `N1_LEDGER_META.regime_bar_counts.BREAKOUT_TRANSITION = 0` pe 355.696 bare.
```

> **★ Am ajuns la aceeași concluzie prin metode DIFERITE — eu numărând bare în ledger, Red Team demonstrând static din cod. Convergența contează tocmai fiindcă metodele sunt independente: măsurătoarea mea arăta CĂ e zero; demonstrația lor arată DE CE e imposibil să fie altceva. `is_displacement` e irelevant, fiind AND-gated în spatele unei condiții imposibile.**

**Și RT închide o întrebare pe care eu o lăsasem deschisă: `RANGE` nu lipsește din neglijență — a fost RETRAS prin decizia CEO `bd60c7a` („Retract RANGE mapping + single-state partition"), iar strategiile dependente de el primesc `TRUE_RANGE_NOT_IDENTIFIABLE` (Router L245). Deci celulele RANGE sărite de generator sunt consecința unei decizii, nu un accident.**

```
Tabelul de adevăr RT:  ACCESIBILE = {UNCERTAIN, TREND_UP, TREND_DOWN, COMPRESSION}
                       IMPOSIBILE = {RANGE, BREAKOUT_TRANSITION}
Breakout-uri reale azi: BOS/CHoCH bull→TREND_UP, bear→TREND_DOWN — ABSORBITE în trend.
Retest · sweep-reversal · trendline breakout: NICIUN detector N1 canonic ⇒ PIERDUTE.
```

---

# A — RECONCILIEREA MULTIPLICITĂȚII

## A.1 Aritmetica, închisă exact din Git

```
loop_state.m_total = 357 = completed_ids(231) + failed_ids(126)          ✔ EXACT
hypothesis_registry = 355 intrări, 355 candidate_id UNICE, zero duplicate
diferența 2, nominal: CAND-G0260, CAND-G0298 — expediate, FĂRĂ înregistrare în registru
duplicate_tombstones.json = dicționar de 6 chei; „16" e VALOAREA lui
    n_economic_duplicates_dropped, iar regula spune literal: „m unchanged; not re-run"
gen_seq = 367  ⇒  gen_seq − m_total = 10
```

## A.2 Ce este `m = 20` (răspuns 1–2)

**Numărul de IPOTEZE ADMISE PENTRU TESTARE FORMALĂ, fiecare producând EXACT UN p-value comparat cu un prag BH. Unitatea e tripletul ratificat la v2.7.71: `(politică, POPULAȚIE, estimand)`.**

**NU e niciunul dintre celelalte universuri — verificat prin numărare directă în registrul Alpha:**

```
familii distincte în registru    15    ≠ 20
mechanism_cluster distincte      2     ≠ 20   (SHORTLIST_CORRECTION.distinct_mechanisms = 4)
configurații generate            357   ≠ 20
```

## A.3 Ce este `m = 357` și de ce NU controlează pragul (răspuns 3)

**Contorul de EXPEDIERE al generatorului: câte configurații au fost generate și trimise spre evaluare. Monoton prin regula proprie („m unchanged" la dedup).**

> **Nu controlează pragul BH pentru un motiv VERIFICABIL: cele 357 au produs ZERO p-value-uri. Statusurile din registru sunt toate verdicte de SCREENING (`GROSS_STRUCTURALLY_FALSIFIED` 271, `GROSS_EPISODE_SURVIVOR_AWAITING_COST` 34, `RECENT_GROSS_SIGNAL_AWAITING_COST` 28, `GROSS_FAT_TAIL_DEPENDENT` 22), iar în sumar `COST_BASE_FALSIFIED = 0`. BH controlează FDR peste ipotezele pentru care se CALCULEAZĂ p-value-uri. Zero p-value-uri ⇒ 357 nu poate fi numitorul, așa cum stă.**

**Confirmat de RT: cele 44 de ipoteze de breakout rămân `NOT_EVALUATED / REGIME_UNREACHABLE`, corect, **nu falsificate** — iar `hsf` și `m` nu se schimbă la re-rulare. Un obiect care nu a fost evaluat nu poate contribui la o rată de descoperiri false.**

## A.4 Cele DOUĂ registre (răspuns 4)

```
                     REGISTRUL DE EXPLORARE          FAMILIA DE MULTIPLICITATE
nume actual          loop_state.m_total              family m (Statistician)
valoare              357                             20
unitate              configurație GENERATĂ           ipoteză (politică, populație, estimand)
                     și expediată                    care produce UN p-value
scop                 buget generator · dedup ·       NUMITORUL corecției BH-FDR
                     contabilitate de explorare
formulă              completed + failed;             ipoteze ADMISE; arhivarea NU
                     duplicatele NU decrementează    returnează slot
monoton              DA (regula tombstone)           DA (v2.7.48)
p-value-uri          ZERO                            toate
relația              familia se ADMITE DIN explorare; explorarea o MĂRGINEȘTE
nu se dublează       un obiect e numărat în ambele, dar în ROLURI diferite — „privit" vs
                     „TESTAT". Doar al doilea intră în prag.
```

> **★ Defectul real nu e aritmetic, e LEXICAL. În notația FDR, `m` denotă universal dimensiunea familiei din corecție. Alpha folosește `m_total` pentru un contor de explorare. E A TREIA OARĂ aceeași clasă: `StructBand.RANGE` vs range real; `effective_spread` half vs full; acum `m`. Remediu cu cost zero: `loop_state.m_total` → `exploration_total`, iar `m` REZERVAT numitorului BH. NU modific registrul Alpha — cer redenumirea.**

## A.5 Numărătoarea pentru noile familii (răspunsuri 5–7)

```
definiție RANGE_STATE PRIMARĂ    1 slot per FAMILIE formal testată
variante de sensibilitate        0 sloturi — DACĂ primara e pre-declarată și DOAR rezultatul
                                 ei se raportează
LONG și SHORT                    sloturi SEPARATE dacă se testează separat. Registrul Alpha
                                 poartă `direction` ca CÂMP al celulei ⇒ direcția face parte
                                 din identitatea ipotezei. O regulă simetrică unică = 1 slot.
breakout vs failed-breakout      DOUĂ sloturi, chiar pe populații DISJUNCTE.
pe populații disjuncte           ★ Disjuncția repară ÎNCĂLCAREA PRDS; NU reduce numărătoarea.
                                 Două lucruri diferite, separate explicit.
mecanisme deja ecranate de Alpha au consumat sloturi de EXPLORARE, nu de familie. Dacă o
                                 familie RANGE reproduce un mecanism ecranat, regula proprie
                                 a lui Alpha o marchează `DUPLICATE_HYPOTHESIS` prin
                                 `hypothesis_semantic_fingerprint` și NU se re-numără.
cele 44 REGIME_UNREACHABLE       rămân în EXPLORARE, `m` neschimbat. NU intră în familie:
                                 nu au produs p-value și nu au fost falsificate.
```

**(7) CONFIRMAT: dacă ORICE variantă din grilă e selectată DUPĂ ce se văd rezultatele, TOATE variantele evaluate intră RETROACTIV în numărătoare. Numărătoarea e peste ce s-a EVALUAT, nu peste ce s-a RAPORTAT. Regula proprie a lui Alpha o susține din cealaltă direcție: la dedup, `m unchanged`.**

## A.6 Pragurile recalculate, cu formula explicită (răspuns 8)

```
BH-FDR:  pentru p ordonate p_(1) <= … <= p_(m), se resping primele k cu  p_(k) <= k · α / m
         α = 0,05 ;  pragul de RANG 1 = α/m
MDE   =  z_{1−α/m} × SE ,  SE = SD/√n = 0,4714/√246 = 0,03006   (SD = varianța MINIMĂ teoretică)
```

```
   univers m   prag rang-1 = 0,05/m        z        MDE   observat 0,062
          20               0,002500   2,8070     0,0844        SUB
          27               0,001852   2,9024     0,0872        SUB    ← +7 familii RANGE
          55               0,000909   3,1184     0,0937        SUB    ← grila tratată ca ipoteze
         357               0,000140   3,6330     0,1092        SUB    ← ecranul Alpha
```

> **★ Efectul observat al lui CAND-0037 e SUB efectul minim detectabil la FIECARE dintre cele patru universuri, inclusiv la cel mai permisiv. Reconcilierea multiplicității NU schimbă niciun verdict. A patra oară aceeași constatare: CONSTRÂNGEREA E PUTEREA, NU MULTIPLICITATEA.**

## A.7 Ce NU apăr: limita lui `m = 20`

**Ecranarea Alpha e DEPENDENTĂ DE REZULTATE — supraviețuitorii avansează. Candidații ajunși la test formal au fost aleși dintre 357 PE BAZA screening-ului, deci p-value-urile lor nu sunt uniforme sub nul. `m = 20` NU controlează FDR la 0,05 dacă admiterea depinde de screening. E o limitare a familiei MELE și o declar.**

```
(A) ADMITERE PRE-DECLARATĂ, independentă de rezultat  ⇒ m = mulțimea pre-declarată; BH valid.
(B) ADMITERE PE SUPRAVIEȚUIRE (practica de facto)     ⇒ numitorul onest e mulțimea ECRANATĂ.
Decizia e a CEO. Din tabelul A.6: alegerea NU schimbă niciun verdict azi. Costul e ZERO acum
și devine material abia când un candidat se apropie de prag.
```

---

# B — CONTRACTUL `RANGE_STATE`

**Nume nou, distinct lexical. `StructBand.RANGE` NU se reutilizează și NU se reinterpretează — RT a confirmat că înseamnă INSTABILITATE, nu lateralitate (H1: `regime_routing` L11-12, CONTRACTS L54, `bd60c7a`).**

```
INPUTURI (toate ≤ momentul evaluării)
  swing-uri CONFIRMATE (fractali simetrici 2k+1 ⇒ swing la i confirmat la i+k)
  ATR cauzal · seria de close/high/low a barelor ÎNCHISE
  NU consumă: `StructBand`, `Direction`, `BREAKOUT_TRANSITION` — niciunul nu poate exprima range

STARE INCREMENTALĂ (producător versionat, nu recalcul pe fereastră)
  upper, lower, touches_upper, touches_lower, first_bar_id, confirm_bar_id,
  path_sum (Σ|Δclose|), net_disp, bars_in_state, last_update_bar_id

LIMITE
  upper = extremul swing-urilor high confirmate din fereastră
  lower = simetric
  boundary_validity ∈ {PROVISIONAL, CONFIRMED, EXTENDED, VIOLATED}
     PROVISIONAL  < n_touch atingeri          CONFIRMED  >= n_touch pe AMBELE
     EXTENDED     un swing nou depășește limita fără acceptare ⇒ limita se MUTĂ, starea NU moare
     VIOLATED     acceptare confirmată dincolo ⇒ invalidare

TIMESTAMPS
  structural_start_ts   prima bară a ferestrei care satisface definiția — RETROSPECTIV
  actionable_start_ts   = confirm_ts = max(confirmările swing-urilor folosite) — PROSPECTIV
  ★ actionable_start_ts − structural_start_ts >= k bare, PRIN CONSTRUCȚIE. Execuția NU are
    acces la începutul structural. Orice durată se raportează pe AMBELE ceasuri.

data_readiness ∈ {WARMUP, READY, DEGRADED}   (reutilizează work item-ul existent, CONTRACTS L52)
  WARMUP    < bare necesare pentru swing_k + ATR ⇒ `Unavailable(reason="warmup")`
  DEGRADED  o intrare din mulțimea necesară lipsește ⇒ `Unavailable`, motiv PROPAGAT
  Fail-closed: niciodată o stare presupusă.

consolidation_state ∈ {NONE, FORMING, ESTABLISHED, DECAYING}   (CONTRACTS L53)
  FORMING      boundary_validity = PROVISIONAL
  ESTABLISHED  CONFIRMED și ER <= ER_max și bars_in_state >= d_min
  DECAYING     ER crește peste ER_max fără violare — semnal, NU invalidare

INVALIDARE (numai pe dovezi observabile, NICIODATĂ retroactiv)
  ACCEPTED_BREAK · MAX_DURATION · INPUT_UNAVAILABLE
  Un range invalidat la t rămâne ACTIV în jurnal pe [confirm_ts, t). Rescrierea istoriei ar
  schimba retroactiv contextul unei decizii deja luate — clasa interzisă.

SNAPSHOT / RESTART
  Starea incrementală e SERIALIZABILĂ integral și restaurabilă EXACT.
  Cerință preluată din `N1_LEDGER_META`: `verify_snapshot_restore_unbounded = true` și
  `snapshot_schema_version`. `RANGE_STATE` primește `range_state_schema_version` propriu.
  Restaurarea dintr-un snapshot trebuie să producă BIT-IDENTIC aceeași ieșire ca rularea
  continuă — altfel starea incrementală introduce o a doua sursă de adevăr.

REASON CODES
  OK_RANGE · FEW_TOUCHES · ER_TOO_HIGH · TOO_SHORT · WIDTH_OUT_OF_GRID · WARMUP ·
  INPUT_UNAVAILABLE · BOUNDARY_EXTENDED · ACCEPTED_BREAK · MAX_DURATION

CONFIG FINGERPRINT
  range_spec_id = sha256 peste dicționarul ORDONAT:
    {n_touch, tol_atr, er_max, d_min_bars, width_filter, N_acceptance, precedence_rule,
     timeframe, swing_k, atr_window, range_state_schema_version, producer_version}
  Un rezultat FĂRĂ `range_spec_id` e NON-COMPARABIL PRIN TIP cu orice alt rezultat de range.
```

---

# C — CONTRACTUL DE EVENIMENTE (mașină de stări VERSIONATĂ)

**`event_contract_version = range-events-v1`. Breakout-ul e EVENIMENT LONGITUDINAL într-un regim, NU regim per-bară — verdictul arhitectural RT, adoptat integral.**

```
EVENIMENT                CONFIRM_TS            DATE DISPONIBILE LA CONFIRMARE
RANGE_LOW_REJECTION      închiderea barei      bare <= t; RANGE_STATE ESTABLISHED; close a
                         de respingere         intrat în [lower, lower+tol×ATR] și a închis peste
RANGE_HIGH_REJECTION     simetric
RANGE_MID                închiderea barei      close strict între zone — STARE EMISĂ, fără entry
BREAKOUT_CANDIDATE       închiderea barei      prima close dincolo de o limită CONFIRMED
                         care depășește
BREAKOUT_ACCEPTED        închiderea barei      N închideri CONSECUTIVE dincolo, N pre-declarat
                         a N-a                 ⇒ ÎNTÂRZIERE de N bare față de CANDIDATE
BREAKOUT_RETEST          închiderea barei      după ACCEPTED, revenire în banda tol a limitei
                         de atingere           străpunse, FĂRĂ re-închidere înăuntru
FAILED_BREAKOUT          închiderea barei      după CANDIDATE, close înapoi ÎNĂUNTRU înainte de N
                         de revenire
LIQUIDITY_SWEEP_REVERSAL închiderea barei      depășire prin FITIL + close înăuntru pe ACEEAȘI
                                               bară (reutilizează D6, ratificat)

TRANZIȚII PERMISE (singurele)
  ESTABLISHED → {LOW_REJECTION, HIGH_REJECTION, MID, BREAKOUT_CANDIDATE}
  BREAKOUT_CANDIDATE → {BREAKOUT_ACCEPTED, FAILED_BREAKOUT}      (exclusive)
  BREAKOUT_ACCEPTED  → {BREAKOUT_RETEST, ∅}  și RANGE_STATE → VIOLATED
  FAILED_BREAKOUT    → ESTABLISHED (range-ul SUPRAVIEȚUIEȘTE)
  Orice altă tranziție = eroare de contract, fail-closed.

INVALIDARE PER EVENIMENT
  CANDIDATE  expiră dacă nici ACCEPTED nici FAILED în N+1 bare ⇒ `Unavailable("indeterminate")`
  RETEST     expiră dacă nu se produce în fereastra pre-declarată
  Toate celelalte sunt punctuale: se confirmă sau nu la bara lor.

ZERO-LOOKAHEAD, per eveniment
  fiecare `confirm_ts` folosește EXCLUSIV bare <= `confirm_ts`;
  niciun eveniment nu se emite retroactiv;
  informația care NU e disponibilă la confirmare se DECLARĂ explicit — la CANDIDATE, dacă va
  fi acceptat sau eșuat; la ACCEPTED, dacă va urma retest.
  ★ Cerință de măsurare, nu de presupunere: `MISSED_BEFORE_ACCEPTANCE` se raportează pentru
  FIECARE N din grilă, exact ca `MISSED_BEFORE_CONFIRMATION` la N4. Un N ales fără curbă e
  ALES, nu derivat. Precedent consemnat fără a presupune că se repetă: la N4 curba a arătat
  că NU există compromis — ceasul scurt domina pe ambele axe.

ABSENTE ASTĂZI, semnalate de RT și NEINVENTATE aici
  retest · sweep-reversal · trendline breakout NU au detector N1 canonic. Evenimentele de mai
  sus le SPECIFICĂ; producerea lor e mandatul VE. Până atunci: `Unavailable("no_detector")`.
```

---

# D — PRECEDENȚA

```
TREND_PAUSE ⊆ RANGE_STATE, prin construcție: orice pauză în trend E, local, un range.
⇒ TAXONOMIA NU E O PARTIȚIE. Nu pretind că e.
```

**Confirmare numerică independentă, din `N1_LEDGER_META`: `TREND_UP 181.795 + TREND_DOWN 173.442 + UNCERTAIN 459 = 355.696` = EXACT `bar_count`, iar `COMPRESSION = 37.047` e ÎN PLUS. Deci partiția reală e {TREND_UP, TREND_DOWN, UNCERTAIN}, iar COMPRESSION e un STRAT SUPRAPUS. Suprapunerea nu e o ipoteză — e măsurată.**

```
precedence_rule = "RANGE_STATE_OVER_TREND_PAUSE"  (valoare declarată, nu dedusă)
  o bară care satisface AMBELE se etichetează RANGE_STATE, iar apartenența la TREND_PAUSE
  se păstrează ca ATRIBUT (`trend_context`), nu se pierde.
Intră în `range_spec_id` (Partea B) ⇒ e hash-uită.
OBLIGATORIU la raportare: MATRICEA DE OCUPANȚĂ — câte bare cad în fiecare etichetă și câte
celule ale spațiului produs colapsează în fiecare. Fără ea nu se poate distinge o etichetă
RARĂ de una pe care PRECEDENȚA a înghițit-o.
```

---

# E — POPULAȚII DE TEST DISJUNCTE

```
PROBLEMA: F3/F4 (breakout, în direcția străpungerii) și F5/F6 (failed breakout / sweep, în
direcția OPUSĂ) iau poziții CONTRARII pe ACEEAȘI limită, pe bare care se suprapun.
⇒ DEPENDENȚĂ NEGATIVĂ ⇒ PRDS ÎNCĂLCAT ⇒ BH-FDR nu acoperă perechea.

REMEDIU (identic cu cel ratificat pentru CAND-0001/0009 și CAND-0006/0037):
  populația de test a lui F3/F4 = evenimentele care ating BREAKOUT_ACCEPTED
  populația de test a lui F5/F6 = evenimentele care ating FAILED_BREAKOUT sau SWEEP
  Cele două sunt DISJUNCTE PRIN CONSTRUCȚIA MAȘINII DE STĂRI: din BREAKOUT_CANDIDATE,
  tranzițiile spre ACCEPTED și FAILED sunt EXCLUSIVE (Partea C). Disjuncția nu e impusă
  din afară — e o proprietate a contractului de evenimente.
  Fracția de suprapunere se raportează PER BLOC ÎNAINTE de orice test, ca verificare.
ALTERNATIVA: BY în loc de BH, la severitate ~4,0× pe m=27. Prefer disjuncția, același motiv.

REGULA ANTI-DUBLĂ-NUMĂRARE
  1. Disjuncția POPULAȚIILOR nu reduce numărul de IPOTEZE: F3/F4 și F5/F6 rămân sloturi
     separate. Sunt două lucruri diferite și nu se compensează.
  2. O tranzacție NU poate apărea în ambele populații — garantat de exclusivitatea tranziției.
  3. Dacă o familie RANGE reproduce un mecanism deja ecranat, `hypothesis_semantic_fingerprint`
     o marchează `DUPLICATE_HYPOTHESIS` (regula proprie a lui Alpha) ⇒ nu se re-numără.
  4. Un eveniment care generează DOUĂ familii (ex. ACCEPTED → F3 și RETEST → F4) contribuie
     la ambele POPULAȚII, dar tranzacțiile lor sunt distincte prin `confirm_ts` diferit.
     Se raportează suprapunerea de BARE, nu se presupune că e zero.
```

---

# F — DEFINIȚIA PRIMARĂ

```
DEFINIȚIA PRIMARĂ, PRE-ÎNREGISTRATĂ, UNA SINGURĂ:
    n_touch    = 2          minimul la care „limită atinsă repetat" are sens; sub 2 e un extrem.
                            Prag de FALSIFICABILITATE, nu de performanță.
    tol        = 0,25×ATR   valoarea de mijloc a grilei — aleasă ÎNAINTE de orice rezultat,
                            pentru a nu fi nici cea mai permisivă, nici cea mai strictă.
    ER_max     = 0,40       idem, valoarea mai permisivă a grilei, ca definiția primară să nu
                            fie cea care minimizează populația.
    d_min      = o ZI a timeframe-ului evaluat (constantă deja derivată în laborator)
    N_acceptance = 2        cel mai mic N la care „închideri consecutive" are sens.
                            Se raportează curba MISSED_BEFORE_ACCEPTANCE pentru întreaga grilă.
    precedence_rule = RANGE_STATE_OVER_TREND_PAUSE

VARIANTELE RĂMÂN SENSITIVITY-ONLY. Nu produc p-value independent, deci nu consumă slot.
★ Dacă se selectează retrospectiv cea mai bună variantă, TOATE variantele evaluate intră în
multiplicitate, retroactiv. Numărătoarea e peste ce s-a EVALUAT, nu peste ce s-a RAPORTAT.
Parametrii de mai sus sunt aleși pe CRITERII STRUCTURALE declarate, ZERO pe PnL — niciun
rezultat nu exista la momentul alegerii, iar pauza pe cercetare o face verificabil.
```

---

# PARTEA G — DESCHIS, CLASIFICAT

```
BLOCKING     `RANGE_STATE` nu există: retras prin `bd60c7a`, iar producătorul versionat e
             mandatul VE care urmează. Cele 7 familii nu sunt admisibile în familie până atunci.
BLOCKING     F3/F4 rutează pe breakout, iar azi `BREAKOUT_TRANSITION` e STATIC IMPOSIBIL
             (RT `5e56396`, confirmat empiric de mine: 0 bare din 355.696).
             `ARCHIVE_INSUFFICIENT` prin construcție, NU eșec.
MATERIAL     coliziune lexicală `m`: `loop_state.m_total` → `exploration_total`; `m` rezervat
             numitorului BH. A treia oară aceeași clasă de coliziune.
MATERIAL     admiterea în familie e de facto dependentă de screening ⇒ `m = 20` subestimează
             selecția. Ruta (A) sau (B), decizie CEO, ÎNAINTE de următorul test formal.
MATERIAL     `CAND-G0260` și `CAND-G0298`: expediate, fără înregistrare. Nu le ating.
MATERIAL     retest · sweep · trendline nu au detector N1 canonic — specificate aici,
             producerea lor e mandatul VE. Până atunci `Unavailable("no_detector")`.
LIMITATION   `pct_time_in_range` e o proprietate a DEFINIȚIEI, nu a pieței. Niciodată un număr
             unic; se raportează per definiție, per bloc, per timeframe.
LIMITATION   `actionable_start_ts` întârzie cu >= k bare față de `structural_start_ts`,
             PRIN CONSTRUCȚIE.
NON-MATERIAL alegerea universului de multiplicitate nu schimbă niciun verdict azi:
             0,062 < MDE la m ∈ {20, 27, 55, 357}.
```

**Nu am: implementat, evaluat PnL, accesat SEALED, rulat Alpha, reinterpretat enum-uri vechi, atins LIVE_SHADOW, sau declarat RANGE ratificat. Nu am modificat `m=357`, tombstones sau registrul Alpha.**

---

**Manifest:** `config/split_manifest.json` v2.7.75, secțiunea `range_reconciled_spec_v2_7_75`.
