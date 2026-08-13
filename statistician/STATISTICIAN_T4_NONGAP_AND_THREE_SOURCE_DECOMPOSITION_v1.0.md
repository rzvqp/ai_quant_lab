# STATISTICIAN — T4 NON-GAP (ULTIMUL BLOCANT) ȘI DESCOMPUNEREA COMPLETĂ

**Document ID:** STAT-T4-NONGAP-AND-DECOMPOSITION-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Verificare de sursă:** citit `demo_gate_engine/pdh_pdl_demo_engine.py` (liniile 125-160), `phase1_screening.py:56`, istoricul `3344bff` / `2403aad`.

---

# PARTEA 1 — T4 NON-GAP: CÂȘTIG. Și R5 se corectează.

## Regula, completă

```
Pe bara de intrare, cu prețul de intrare ÎNTRE stop și țintă (cazul NON-GAP):

  SL atins  ȘI  TP atins   →  SL.   Worst-case. Ordinea intrabar e NECUNOSCUTĂ.
  DOAR TP atins            →  TP.   CÂȘTIG. Nu există ambiguitate DE REZOLVAT.
  DOAR SL atins            →  SL.
  Niciunul                 →  se continuă scanarea barelor următoare.
```

## Corecția de formulare a lui R5

**R5 spune azi „SL și TP se verifică inclusiv pe bara de intrare, iar SL primează la coliziune". Formularea acoperă coliziunea și tace pe restul — iar tăcerea a fost citită de DEMO ca „nicio ieșire pe bara de intrare".**

```
R5, CORECTAT:
  (i)  SL și TP se evaluează pe bara de intrare, ca pe orice altă bară;
  (ii) primatul SL se aplică EXCLUSIV când AMÂNDOUĂ sunt atinse pe aceeași bară;
  (iii) când e atins UNUL SINGUR, acela e ieșirea — indiferent care.
Punctul (iii) nu adaugă o excepție. Îl scrie pe cel implicat de (i), pe care (ii) îl ascundea.
```

> **Justificarea, o singură propoziție: regula worst-case există ca să REZOLVE o ambiguitate de ordonare; când doar ținta e atinsă, intervalul barei nu a ajuns niciodată la stop, deci NU EXISTĂ nicio ordonare de tick-uri care să producă o pierdere, deci nu e nimic de rezolvat.**

**A refuza câștigul nu e prudență — e o politică diferită, care interzice ieșirile pe aceeași bară. Și e deplasată SISTEMATIC: aruncă exact tranzacțiile care ating ținta cel mai repede, adică pe cele mai bune. Aceeași clasă de cenzurare informativă ca excluderea tranzacțiilor deschise la D-4.**

## Stratificarea față de garda de politică — găsită în cod, nu presupusă

**`pdh_pdl_demo_engine.py:155` are deja o gardă de POLITICĂ: „next-open deja dincolo de țintă / de stopul STRUCTURAL → NU se intră", cu comentariul că „pre-emptă clauza INVALID". VE a înțeles corect că e o pre-empțiune. O formalizez ca STRATIFICARE, ca să nu apară ca o a doua regulă concurentă:**

```
NIVEL 1  GARDA DE POLITICĂ, dacă politica o DECLARĂ  →  NO_ENTRY. Tranzacția nu există.
NIVEL 2  IMPLICITUL DE EVALUARE, când politica TACE  →  GEOMETRIA STRICTĂ (amendament A2):
             LONG:  stop < entry_open < target        SHORT: target < entry_open < stop
             risc <= 0  SAU  recompensă <= 0  →  INVALID_EXECUTION, fără tranzacție, fără P&L
             (inclusiv open EXACT pe stop și open EXACT pe țintă)
NIVEL 3  T4 non-gap, de mai sus.
Ordinea e obligatorie. „Intru sau nu" e o întrebare de POLITICĂ; „ce contabilizez dacă am
intrat" e una de MĂSURARE. Cele două nu se arbitrează în același loc.
```

**Toate cele trei motoare consumă ACEEAȘI declarație de politică. Divergența actuală — SCREEN/MSTRAT numără, DEMO ignoră — dispare fiindcă DEMO nu mai decide singur, ci citește.**

---

# PARTEA 2 — DESCOMPUNEREA: sursele sunt DOUĂ, nu trei. Demonstrație.

**Mandatul spune că diferența BASE−STRESS are acum trei surse. Nu are. Se vede din algebra mulțimilor.**

```
S       toate semnalele
A(c)    R3-eligibile sub configurația de cost c        depinde de spread
M       MEAS-9-valide (risc realizat > 0)              NU depinde de spread
X(c)    populația executată  =  A(c) ∩ M
```

**`A(stress) ⊆ A(base)`, fiindcă podeaua e monotonă în spread. Deci:**

```
X(base) \ X(stress)  =  ( A(base) ∩ M ) \ ( A(stress) ∩ M )
                     =  ( A(base) \ A(stress) ) ∩ M
```

> **`M` apare în AMBII termeni și se INTERSECTEAZĂ afară. Diferența de populație dintre BASE și STRESS e atribuibilă INTEGRAL lui R3. MEAS-9 nu contribuie deloc la ea — el restrânge ambele configurații IDENTIC.**

## Ce ESTE, atunci, MEAS-9

```
CROSS-SECȚIONAL  BASE vs STRESS, la aceeași versiune de motor  →  DOUĂ surse: cost + R3.
LONGITUDINAL     versiunea N vs versiunea N+1                  →  MEAS-9 e AICI.
```

**Saga S3 e longitudinală, nu cross-secțională: `+0,23 → +0,395 → −0,13 → −0,17` sunt patru VERSIUNI DE MOTOR pe aceeași configurație. A o trata ca pe o a treia sursă a diferenței BASE−STRESS ar atribui un efect de VERSIUNE unui efect de CONFIGURAȚIE. Sunt axe diferite și nu se însumează.**

## Descompunerea, pe cele două axe

```
CROSS-SECȚIONAL, la versiune FIXĂ:
   A = costuri BASE   / X(base)          B = costuri STRESS / X(base)
   C = costuri STRESS / X(stress)        A' = costuri BASE  / X(stress)
   efect COST = B − A · efect R3 = C − B · total = C − A
   ordinea alternativă A → A' → C se raportează ȘI ea (dependență de drum).

LONGITUDINAL, la configurație FIXĂ:
   pentru fiecare pereche de versiuni consecutive, la ACELAȘI `run_hash` de configurație,
   se raportează diferența ȘI mulțimea pe care versiunea nouă o exclude în plus.
   NU se amestecă cu axa cross-secțională.
```

---

# PARTEA 3 — METODA MULȚIMII ARUNCATE NU SE EXTINDE. Și motivul e definiția lui MEAS-9.

**Am propus: media `net_R` a mulțimii aruncate, sub costuri BASE. Verificat — se aplică lui R3, dar NU lui MEAS-9:**

```
mulțimea aruncată de R3    = A(base) \ A(stress)
   risc PLANIFICAT > 0 pentru toate  ⇒  `net_R` e BINE DEFINIT  ⇒  metoda se aplică NESCHIMBATĂ.
   Spune direct dacă R3 filtrează zgomot sau taie edge.

mulțimea invalidată de MEAS-9 = A(c) \ M
   risc REALIZAT <= 0 pentru toate, PRIN DEFINIȚIE  ⇒  NUMITORUL nu există  ⇒  `net_R` NU SE POATE
   CALCULA. A cere media lui ar fi exact eroarea pe care MEAS-9 o repară.
```

> **Nu e o limitare a metodei — e conținutul lui MEAS-9. Un set definit prin numitor distrus nu are medie de randament, oricât de mult am vrea una.**

## Ce se raportează în locul ei

```
n_invalid și fracția, per configurație și per bloc
DISTRIBUȚIA MAGNITUDINII GAP-ULUI: (stop − open)/ATR pentru cele invalidate.
   E măsurabilă, e cauzală, și e singura care distinge un fenomen de piață
   de un defect de aliniere a datelor.
CONCENTRAREA TEMPORALĂ: dacă invalidările se aglomerează la deschideri de sesiune/săptămână,
   e o proprietate de calendar; dacă sunt uniforme, e una de geometrie.
```

---

# PARTEA 4 — 51% NU E O CORECȚIE DE COST. E un defect de geometrie pe care l-am semnalat deja.

**S3 e FVG-CE50-REACTION. Stopul lui e `ce_50 − lower = FVG_height/2`. La v2.7.36 am scris, despre exact acest candidat:**

> *„S2 LIVE & ROUTINE: stop = FVG_height/2, arbitrar de mic pentru FVG-uri mici → 1R nemărginit; podeaua min_executable_risk e esențială."*

```
Podeaua BASE, în unități canonice: 0,05 USD.
Un gap de deschidere de bară pe XAUUSD depășește rutinier 0,05 USD.
⇒ podeaua e pe ACEEAȘI SCARĂ cu gap-ul, și pierde.
```

> **51% INVALID nu e o surpriză de execuție — e consecința prezisă a unui stop mai mic decât gap-ul tipic dintre bare. R3 la 0,05 nu poate proteja împotriva lui MEAS-9, fiindcă cele două praguri sunt comparabile ca mărime. Cele două gărzi NU sunt independente.**

**NU propun un prag nou — ar fi o constantă aleasă ca să facă un număr să arate bine. Propun MĂSURĂTOAREA care ar decide: distribuția distanței de stop a lui S3 față de distribuția gap-ului de intrare, pe aceeași populație. Dacă prima e sistematic sub a doua, defectul e la geometria politicii și e treaba Alpha, nu a evaluatorului.**

---

# PARTEA 5 — O DIVERGENȚĂ DE MOTOR PE CARE AM GĂSIT-O CITIND

```python
executable_stop_distance = max(strategy_stop_distance, min_exec)   # DEMO: LĂRGEȘTE
floored = strategy_stop_distance < min_exec
```

**DEMO **lărgește** stopul la podea (S2, ratificat de mine la v2.7.34). Evaluatorul canonic **RESPINGE** (R3 reject-not-widen, ratificat la v2.7.66). Aceeași politică produce pe cele două linii populații DIFERITE ȘI numitori R DIFERIȚI.**

```
NU e un defect: sunt două linii cu `run_hash` diferit, deci NON-COMPARABILE prin construcție.
E un RISC DE CITIRE: cifrele „DEMO baseline" circulă, și cineva le va compara cu cele canonice.
CERINȚĂ: fiecare raport DEMO poartă vizibil `s2_mode = WIDEN` și fiecare raport canonic
`r3_mode = REJECT`. Ambele intră în `run_hash` — deci comparația RIDICĂ, nu comentează.
```

---

# PARTEA 6 — DESCHIS, CLASIFICAT

```
BLOCKING      niciunul. T4 non-gap e specificat; poarta de ratificare se poate deschide.
MATERIAL      R5 se re-formulează cu punctul (iii). Fără el, tăcerea rămâne interpretabilă.
MATERIAL      stratificarea politică → evaluare trebuie declarată per politică; toate cele
              trei motoare CITESC aceeași declarație, niciunul nu decide singur.
MATERIAL      51% INVALID pe S3 — se măsoară distanța de stop contra gap-ului de intrare
              ÎNAINTE de a interpreta orice rezultat S3. Rutat la Alpha dacă se confirmă.
MATERIAL      DEMO lărgește / canonicul respinge; `s2_mode` și `r3_mode` în `run_hash`.
LIMITATION    mulțimea invalidată de MEAS-9 NU are medie de randament, prin definiție.
              Se caracterizează prin număr, magnitudinea gap-ului și concentrare temporală.
LIMITATION    descompunerea cross-secțională rămâne dependentă de drum; ambele ordini.
NON-MATERIAL  saga S3 (+0,23 → +0,395 → −0,13 → −0,17) e LONGITUDINALĂ; nu se compară cu
              nicio diferență BASE−STRESS și nu se însumează cu ea.
```

**Nu cere: gate nou, framework nou, primitivă nouă, metrică nouă.**

---

---

# ANEXĂ — AMENDAMENT CEO A2/A3/A4, primit după redactare, încorporat înainte de publicare

**AMENDMENT_RECEIVED.**

## A3 — T4 non-gap: ratificat exact cum e specificat la Partea 1. Nicio schimbare.

## A2 — GEOMETRIA STRICTĂ înlocuiește regula asimetrică. Accept, și consemnez ce se pierde.

```
ÎNLOCUIT (v2.7.66)   risc <= 0 → INVALID · recompensă <= 0 → ieșire la intrare, R = 0 − costuri
ÎN VIGOARE (A2)      risc <= 0  SAU  recompensă <= 0  →  INVALID_EXECUTION, fără tranzacție
                     inclusiv egalitățile: open EXACT pe stop, open EXACT pe țintă
```

**Argumentul meu — numitor distrus vs numărător zero — a fost recunoscut și decizia e alta. Nu îl reiau. Consemnez o singură dată ce cumpără și ce costă decizia, ca să fie pe hârtie:**

```
CUMPĂRĂ   o singură regulă, un singur predicat, fără caz special. Contract mai mic, mai greu
          de implementat greșit. Și face DEMO și evaluatorul canonic să COINCIDĂ: garda de
          politică din `pdh_pdl_demo_engine.py:155` refuză deja intrarea în AMBELE cazuri,
          deci sub geometria strictă divergența dintre linii DISPARE pe acest punct.
COSTĂ     tranzacțiile cu recompensă <= 0 aveau numitor INTACT, deci un R CALCULABIL (0 − costuri).
          Excluderea lor aruncă o observație care se putea calcula. Iar mulțimea aruncată e
          corelată cu gap-uri FAVORABILE — oglinda exactă a îngrijorării de cenzurare
          informativă de la D-4. Selectivitatea ei devine nemăsurată prin construcție.
```

**Toate rezultatele produse sub varianta asimetrică sunt PROVISIONAL și NON-COMPARABLE. Predicatul intră în `run_hash` (`geometry_mode = STRICT`), deci comparația cu rulările asimetrice RIDICĂ, nu comentează.**

## Descompunerea: demonstrația de la Partea 2 e INVARIANTĂ la A2

**Mandatul spune că sub geometria strictă „a treia sursă se lărgește". Se lărgește ca MULȚIME. Nu devine o sursă a diferenței BASE−STRESS, iar motivul e că demonstrația nu depinde de CE e `M`, ci doar de faptul că e INDEPENDENT DE COST:**

```
geometria strictă schimbă M în M' ⊂ M.  entry_open, stop și target sunt toate STRUCTURALE,
deci M' rămâne INDEPENDENT DE SPREAD. Prin urmare:
     X(base) \ X(stress) = ( A(base) \ A(stress) ) ∩ M'
M' se intersectează afară EXACT ca M.
```

> **Diferența BASE−STRESS are, și sub geometria strictă, DOUĂ surse: costul și R3. A treia rămâne LONGITUDINALĂ — o schimbare de versiune de motor, nu una de configurație. Cifrele noi ale VE vor schimba MĂRIMILE, nu STRUCTURA.**

**Ce se re-specifică efectiv după raportul VE: nimic din structură; doar se reportează `n_invalid` sub noul predicat, separat pe cele două cauze (`risk_le_0`, `reward_le_0`), fiindcă acum sunt contopite într-o singură etichetă și altfel n-am putea măsura cât a adăugat A2 față de regula anterioară.**

## A4 — porți separate. Confirm și nu le confund.

```
POARTA CONTRACTULUI CANONIC   T4 e NECESAR, nu suficient. Cere în plus: întreaga suită
                              Red Team, ZERO divergențe neexplicate, aprobare finală CEO.
CELE 25 DE TESTE END-TO-END   aparțin Mandatului 2, se rulează DUPĂ VE_HANDOFF_PASS.
Nu am afirmat niciodată că T4 deschide singur poarta; consemnez separarea ca să rămână scrisă.
```

## Fișiere de corectat

```
SPEC (ale mele)   statistician/STATISTICIAN_CANONICAL_CONTRACT_v1.0.md  §5 gap-guard  → înlocuit
                  acest document, Partea 1 nivel 2                       → DEJA corectat mai sus
MANIFEST          canonical_contract_v2_7_66.gap_guard_closes_MEAS_9     → superseded de A2
                  t4_nongap_and_decomposition_v2_7_67                    → nivelul 2 actualizat
                  secțiune nouă `strict_geometry_amendment_v2_7_68`
COD (VE)          evaluatorul canonic (`3344bff`): ramura asimetrică → predicat unic strict
                  `run_hash`: adaugă `geometry_mode`
                  raportare: `n_invalid` DEFALCAT pe `risk_le_0` / `reward_le_0`
COD (neatins)     `demo_gate_engine/pdh_pdl_demo_engine.py` — garda de politică refuză DEJA
                  ambele cazuri. Sub A2 devine CONFORMĂ, nu divergentă.
```

---

**Manifest:** `config/split_manifest.json` v2.7.67 (T4 + descompunere) și v2.7.68 (amendamentul A2).
