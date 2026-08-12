# STATISTICIAN — BASE/STRESS, TRIAJUL ÎN CONTRACT, DESCOMPUNEREA, T4, T12/T13, M-4

**Document ID:** STAT-BASE-STRESS-AND-FIVE-SPECS-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Verificare de sursă:** citit `phase1_screening.py` (constantele frozen), `split_manifest.json` (`regime_segments`, `overlap_with_M15`, `m15_v2_discovery_blocks`), `tests/test_loader_holdout_boundary.py`.

> **Două dintre cele șase puncte conțin contradicții pe care le-am găsit VERIFICÂND, nu presupunând. Le pun primele, fiindcă schimbă cifre din mandat.**

---

# 1 — T12/T13: LABORATORUL RĂSPUNDE SINGUR. Și valorile aprobate se contrazic.

## Formula e corectă — dovada e în constantele proprii

```python
EFF_SPREAD, COST, TICK_SIZE = 0.10, 0.20, 0.01     # phase1_screening.py:56, frozen
```

**Un dus-întors costă spread-ul COMPLET o singură dată (cumperi la ask, vinzi la bid). Iar `COST = 0.20 = 2 × EFF_SPREAD`. Deci:**

> **`effective_spread` E JUMĂTATE de spread. Spread-ul complet modelat e 0,20. Factorul 2 din `min_executable_risk = max(2 × effective_spread, …)` e CORECT ca scriere — Red Team are dreptate că e corect DOAR dacă spread-ul e half, iar constantele laboratorului confirmă că este.**

## Dar valorile aprobate de CEO se contrazic între ele

```
punctul 3:  BASE „spread 0,05 · entry_slip 0,00 · exit_slip 0,00 · TOTAL 0,05"
            ⇒ spread-ul intră în totalul de dus-întors O SINGURĂ DATĂ ⇒ 0,05 e spread COMPLET
punctul 4:  „BASE spread 0,05 → componenta spread a stopului minim = 0,10"
            ⇒ 2 × 0,05 ⇒ 0,05 e tratat ca JUMĂTATE de spread
```

> **Amândouă nu pot fi adevărate. Aceeași cifră, 0,05, e folosită ca spread complet în definiția costului și ca jumătate în aritmetica stopului minim.**

## Recomandarea, și ce se schimbă

**Citirea corectă e (A): 0,05 și 0,08 sunt bid-ask COMPLET.** Un feed de broker raportează `ask − bid`; e ce măsoară AI Trader; și e singura citire care face TOTALURILE CEO corecte.

```
                        spread COMPLET   effective_spread (=half)   componenta din stopul minim
BASE_PROVISIONAL             0,05                0,025                    2×0,025 = 0,05
STRESS_PROVISIONAL           0,08                0,040                    2×0,040 = 0,08
punctul 4 al mandatului spunea 0,10 și 0,16  —  adică EXACT DUBLU.
```

```
CONSECINȚE, obligatoriu re-măsurate înainte de orice comparație BASE/STRESS:
 · rata de respingere R3 SCADE sub ~18% măsurat de VE — pragul e jumătate din ce s-a presupus;
 · diferența de POPULAȚIE între BASE și STRESS se micșorează în consecință;
 · spread-ul REAL măsurat (complet 0,05-0,08) e de 2,5-4 ORI mai mic decât cel MODELAT (0,20).
   Fiecare cifră publicată ajustată la cost a folosit 0,20. Nu invalidează nimic — e conservator —
   dar înseamnă că rezultatele istorice sunt SUBESTIMATE, nu supraestimate.
```

**Cerință minimă pentru închidere definitivă: colectarea de spread declară EXPLICIT dacă înregistrează `ask − bid` sau `(ask − bid)/2`. Un câmp, o dată.**

---

# 2 — M-4: blocurile sunt PATRU, nu trei. Fereastrarea pe 3 ar arunca 3 ani.

**Verificat direct:**

```
regime_segments                  4 intrări — dar doar 3 poartă `discovery_range`;
                                 a 4-a e „TOO_SHORT_FULLY_SEALED" (182 bare, sub podeaua de 1000)
m15_v2_discovery_blocks          4 blocuri:
     2011-07-26 → 2013-09-27 · 2016-01-11 → 2018-04-06 · 2020-08-11 → 2021-09-05
     2022-12-16 → 2025-10-12   ← al patrulea
overlap_with_M15                 2022-12-16 → 2026-07-13, „Inherits M15's discovery/embargo/
                                 sealed classification VERBATIM"  ← de aici vine al patrulea bloc
```

> **„Manifestul dă 3 segmente discovery" numără `regime_segments` care poartă `discovery_range`. Lista OPERATIVĂ — `m15_v2_discovery_blocks`, cea pe care regula HTF o folosește deja — are PATRU. Al patrulea e moștenit prin `overlap_with_M15` și e perfect legitim.**
>
> **Dacă fereastrarea candidaților trece la 3 blocuri, se aruncă TĂCUT blocul 2022-12 → 2025-10: aproape 3 ani, cel mai recent și cel mai mare. Asta nu e corecția lui M-4 — e o a doua eroare, în direcția opusă.**

**Impunerea manifestului ca sursă unică e CORECTĂ, iar cele 12 granițe în plus sunt într-adevăr închideri de sărbători, nu găuri. Dar sursa unică are PATRU blocuri.**

```
Re-rularea se face pe cele PATRU blocuri. Populația se schimbă pentru toți candidații
evaluați prin `_screen` — inclusiv CAND-0037. Fiecare cifră publicată pe 15 blocuri devine
NON-COMPARABLE cu una pe 4. Se re-raportează n per candidat ÎNAINTE de orice test.
Și confirmă retroactiv D-4: sunt PATRU granițe de bloc, cum am scris la v2.7.64.
```

## Testul stale — reparat

**`test_h1_from_m15_v2_awaits_path_reconciliation` aserta `not isfile(file_path)`, documentând o reconciliere pe care o datoram eu. Reconcilierea a aterizat, deci aserțiunea s-a inversat. L-am CONVERTIT, nu șters — garda pe care o oferea (calea înregistrată e cea canonică și chiar se încarcă) e exact ce nu trebuie să regreseze tăcut.**

```
test_h1_from_m15_v2_path_reconciled:  status VALIDATED · file_path == calea canonică ·
   „acquisition_staging" absent · fișierul există · `load()` întoarce > 0 rânduri.
Suita: 139/143 → 140/143. Rămân 3 eșecuri preexistente, fără legătură.
```

---

# 3 — BASE și STRESS: numite și hash-uite

```
BASE_PROVISIONAL     spread_full 0,05 · entry_slip 0,00 · exit_slip 0,00 · cost_round_trip 0,05
                     effective_spread (half) 0,025 · min_stop_spread_component 0,05
STRESS_PROVISIONAL   spread_full 0,08 · entry_slip 0,08 · exit_slip 0,08 · cost_round_trip 0,24
                     effective_spread (half) 0,040 · min_stop_spread_component 0,08
AMBELE: calibration_status = "PROVISIONAL — NOT EMPIRICALLY CALIBRATED"
```

```
config_hash = sha256 peste dicționarul ORDONAT al câmpurilor de mai sus + calibration_status.
Intră în `schema_hash` al fiecărui rezultat. Un rezultat FĂRĂ config_hash e NON-COMPARABLE
cu orice altceva — prin TIP, nu prin disciplină.
`calibration_status` e parte din hash DELIBERAT: când calibrarea empirică sosește, hash-ul
se schimbă, deci rezultatele provizorii NU se pot compara tăcut cu cele calibrate.
```

---

# 4 — DESCOMPUNEREA: efect de COST versus efect de POPULAȚIE

**Podeaua e monotonă în spread (`max` cu un termen mai mare) ⇒ populația STRESS ⊆ populația BASE. Asta face descompunerea bine definită.**

```
A  = costuri BASE   pe populația BASE      (= BASE)
B  = costuri STRESS pe populația BASE      ← construit ANUME pentru descompunere
C  = costuri STRESS pe populația STRESS    (= STRESS)

efect de COST       = B − A        (aceleași tranzacții, alt cost)
efect de POPULAȚIE  = C − B        (același cost, alte tranzacții)
total               = C − A
```

**Descompunerea e DEPENDENTĂ DE DRUM, ca orice descompunere în doi factori. Se raportează AMBELE ordini:**

```
ordinea 1:  A → B → C     cost întâi, apoi populație
ordinea 2:  A → A' → C    populație întâi (A' = costuri BASE pe populația STRESS), apoi cost
Dacă cele două împărțiri diferă material, se SPUNE — nu se alege una.
```

## Măsurătoarea care chiar răspunde la întrebare

> **Descompunerea dă un rezidual. Mulțimea ARUNCATĂ dă un răspuns.**

```
OBLIGATORIU, alături de descompunere:
   n_base · n_stress · n_dropped = |populația BASE \ populația STRESS|
   media net_R a mulțimii ARUNCATE, evaluată sub costuri BASE.
Asta spune direct dacă tranzacțiile pe care R3 le respinge sunt sistematic diferite —
adică dacă podeaua filtrează zgomot sau taie edge. Un contor n-ar spune-o.
Instrumentul e cel deja folosit: evaluează tot, nu doar ce supraviețuiește.
```

---

# 5 — T4: ȚINTA ATINSĂ PE BARA DE INTRARE

## Decizia: e CÂȘTIG

```
R5 ratificat:  SL și TP se verifică INCLUSIV pe bara de intrare; SL primează LA COLIZIUNE.
Nespecificat:  TP atins, SL NEatins.
```

> **Regula worst-case există ca să rezolve AMBIGUITATEA de ordine intrabar. Când doar TP e atins, NU EXISTĂ ambiguitate: intervalul barei nu a ajuns niciodată la stop, deci nicio ordonare a tick-urilor nu poate produce o pierdere. A refuza câștigul nu e conservatorism — e o ALTĂ POLITICĂ, una care interzice ieșirile pe aceeași bară.**

**Și e o politică deplasată sistematic: aruncă exact câștigătorii CEI MAI RAPIZI. Aceeași clasă cu cenzurarea informativă de la D-4 — se pierde selectiv, nu uniform.**

```
SCREEN și MSTRAT sunt CORECTE. DEMO e greșit și se aliniază.
Fiecare rezultat DEMO calculat sub vechea regulă e NON-COMPARABLE cu unul de după — se
re-etichetează, nu se compară.
```

## Cazul de graniță pe care regula trebuie să-l acopere

```
Dacă prețul de intrare (open[t+1]) e DEJA dincolo de TP (gap peste țintă):
   ieșirea e la PREȚUL DE INTRARE, deci R = 0 − costuri. NU la TP nominal.
REGULA GENERALĂ: nu se contabilizează NICIODATĂ o execuție mai bună decât prețurile
efectiv parcurse DUPĂ intrare. Un TP „atins" înainte de a fi în piață nu e o umplere.
```

---

# 6 — TRIAJUL, FORMALIZAT ÎN CONTRACT

**„Un candidat nu se elimină pentru că n-a putut fi testat" devine executabil:**

```python
@dataclass(frozen=True)
class TriageOutcome:                 # emis ODATĂ cu verdictul, nu după
    label: Literal["PROMOTED", "ARCHIVE_NEGATIVE", "ARCHIVE_INSUFFICIENT"]
    effect: float                    # ê observat
    se: float                        # măsurat, nu derivat din agregate
    mde: float                       # z* × se, unde z* = pragul BH pre-declarat
    reason: str
```

```
PRE-DECLARARE OBLIGATORIE: `mde` se calculează la pasul de precondiție, ÎNAINTE de test,
din SD-ul MĂSURAT și pragul BH pre-declarat, și intră în `schema_hash`.
Altfel clasificarea s-ar putea alege DUPĂ ce se vede rezultatul — exact selecția interzisă.

REGULA, mecanică:
   p <= prag BH                              →  PROMOTED
   p >  prag,  ê <= 0  ȘI  |ê| >= mde        →  ARCHIVE_NEGATIVE      eliminare CORECTĂ
   p >  prag,  |ê| < mde                     →  ARCHIVE_INSUFFICIENT  NU se elimină
   p >  prag,  ê > 0   ȘI  ê >= mde          →  ARCHIVE_INSUFFICIENT  (semn corect; ne-respingerea
                                                 e despre precizie, nu despre absența edge-ului)
```

**Justificarea pentru `ARCHIVE_NEGATIVE`: un ê negativ de magnitudine ≥ MDE înseamnă că testul avea putere amplă să vadă un efect pozitiv de acea mărime și a văzut opusul. Aia E dovadă. Sub MDE, nu e.**

> **Aplicat la CAND-0037: ê = +0,062, MDE = 0,0839 ⇒ `ARCHIVE_INSUFFICIENT`. NU se elimină. Exact ce am pre-declarat la v2.7.62, acum mecanic în loc de argumentativ.**

---

# 7 — DESCHIS, CLASIFICAT

```
BLOCKING      contradicția spread full/half din valorile aprobate (punctul 1). Fără rezolvare,
              stopul minim e ambiguu cu factor 2, deci populațiile BASE/STRESS sunt nedefinite.
              Recomandarea mea: citirea (A), spread COMPLET. Cere confirmare CEO — o propoziție.
BLOCKING      numărul de blocuri pentru re-fereastrare: PATRU, nu trei. Pe 3 se pierd ~3 ani.
MATERIAL      rata R3 de ~18% e măsurată sub praguri DUBLE față de citirea (A) — se re-măsoară.
MATERIAL      toate cifrele pe 15 blocuri devin NON-COMPARABLE cu cele pe 4; n se re-raportează.
MATERIAL      DEMO se aliniază la T4; rezultatele DEMO anterioare se re-etichetează.
LIMITATION    BASE și STRESS rămân PROVISIONAL — NECALIBRATE EMPIRIC. `calibration_status`
              e în hash tocmai ca să nu se compare tăcut cu variante calibrate.
LIMITATION    descompunerea e dependentă de drum; se raportează ambele ordini, nu se alege una.
NON-MATERIAL  spread-ul modelat (0,20) e de 2,5-4× mai mare decât cel real. Conservator, deci
              rezultatele istorice sunt SUBESTIMATE. Nu invalidează nimic.
```

**Nu cere: gate nou, framework nou, primitivă nouă, metrică nouă. Triajul, `schema_hash`, contractul `Ok`/`Unavailable` și podeaua N_MIN=25 există toate.**

---

**Manifest:** `config/split_manifest.json` v2.7.65, secțiunea `base_stress_and_five_specs_v2_7_65`.
