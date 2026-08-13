# STATISTICIAN — CONTRACTUL CANONIC: UNITĂȚI, R3, CONFIGURAȚII, DESCOMPUNERE, GAP-GUARD, TRIAJ

**Document ID:** STAT-CANONICAL-CONTRACT-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Verificare de sursă:** citit `demo_gate_engine/pdh_pdl_demo_engine.py::min_executable_risk`, `phase1_screening.py:56`, și `red_team/audit/LEDGER.md` (MEAS-9, MEAS-10, T17, R3/R4/R5 verbatim).

> **Am citit raportul Red Team și am găsit TREI lucruri care schimbă ce trebuie scris aici. Două dintre ele fac inoperante cerințe pe care le-am emis chiar eu. Le pun la punctele 3 și 7.**

---

# 1 — UNITĂȚI: canonic COMPLET, moștenit JUMĂTATE, conversia scrisă o singură dată

```
CANONIC          spread_price = bid-ask COMPLET (ask − bid), în USD.
MOȘTENIT         min_executable_risk(effective_spread, tick, atr) primește o JUMĂTATE.
DOVADA           EFF_SPREAD, COST = 0,10 · 0,20  și  COST = 2 × EFF_SPREAD  (phase1_screening.py:56)
                 Un dus-întors costă spread-ul COMPLET o dată ⇒ effective_spread ERA jumătate.
CONVERSIA        effective_spread_half = spread_price / 2
```

**Consecința aritmetică, care e și verificarea de coerență:**

```
componenta R3 = K_SPREAD × effective_spread_half = 2 × (spread_price / 2) = spread_price
   BASE    spread_price 0,05  →  componenta 0,05      ✓ valorile CEO
   STRESS  spread_price 0,08  →  componenta 0,08      ✓ valorile CEO
   MOȘTENIT MODELAT  spread_price 0,20 → componenta 0,20 = 2 × 0,10   ✓ identic cu comportamentul vechi
```

> **În unități canonice componenta R3 ESTE spread-ul complet. Factorul 2 nu dispare — se ANULEAZĂ cu conversia. Coerent și cu R4 al Red Team („spread ONCE, no 2x factor").**

## Impunerea, ca eroarea de unitate să fie NESCRIIBILĂ

```python
SpreadFull = NewType("SpreadFull", float)     # ask − bid
SpreadHalf = NewType("SpreadHalf", float)     # (ask − bid) / 2
def half_of(s: SpreadFull) -> SpreadHalf: return SpreadHalf(float(s) / 2.0)
def min_executable_risk(spread: SpreadHalf, tick: float, atr: float) -> float: ...
```

**`mypy --strict` respinge trecerea unui `SpreadFull` acolo unde se cere `SpreadHalf`. E a ȘAPTEA folosire a aceluiași instrument — și e cea mai potrivită: transplantul de unitate e clasa de eroare pe care am prins-o de patru ori. Aici devine imposibil de scris, nu doar interzis.**

---

# 2 — R3, RE-SPECIFICAT

```
min_executable_risk = max( spread_price , K_TICK × tick_size , K_ATR × atr )
                      K_TICK = 5 · K_ATR = 0,10 · tick_size = 0,01   (NESCHIMBATE)

SEMANTICA (R3 Red Team, adoptată): REJECT-NOT-WIDEN.
   Un semnal a cărui distanță de risc a strategiei e sub podea se RESPINGE. Stopul NU se
   lărgește. Fără P&L fictiv, fără risc extins.
RAPORTARE OBLIGATORIE: n_rejected_R3 și fracția, per configurație. O respingere se NUMĂRĂ
   întotdeauna — niciodată un `continue` tăcut.
```

**Rata de ~18% măsurată de VE a fost obținută contra unor praguri DUBLE (0,10/0,16 în loc de 0,05/0,08). Se RE-MĂSOARĂ. Nu o extrapolez: pragul înjumătățit reduce respingerile, dar cu cât depinde de distribuția distanțelor de risc, pe care n-am măsurat-o.**

---

# 3 — CONFIGURAȚII: hash-ul meu de la v2.7.65 era INSUFICIENT. Îl corectez.

**Red Team, T17(b), verbatim: *„DATA-BLIND (payload omits symbol/date-range/block-manifest → two runs on DIFFERENT instruments share ONE config_id → falsely comparable)".***

> **Asta lovește exact ce am specificat eu. `config_hash`-ul meu acoperea doar câmpurile de cost plus `calibration_status`. Două rulări pe INSTRUMENTE DIFERITE ar fi împărțit un hash, deci ar fi trecut drept comparabile. Corectez: identitatea rulării trebuie să acopere ȘI DATELE, nu doar configurația.**

```
config_hash   = sha256 peste dicționarul ORDONAT:
                {spread_price, entry_slip, exit_slip, cost_round_trip,
                 K_SPREAD, K_TICK, K_ATR, calibration_status}
data_identity = {symbol, timeframe, split_id, block_manifest_hash, n_blocks, holdout_cutoff}
run_hash      = sha256(config_hash ‖ sha256(data_identity))

BASE_PROVISIONAL    spread_price 0,05 · slips 0,00/0,00 · cost_round_trip 0,05 · componentă R3 0,05
STRESS_PROVISIONAL  spread_price 0,08 · slips 0,08/0,08 · cost_round_trip 0,24 · componentă R3 0,08
ambele: calibration_status = "PROVISIONAL — NOT EMPIRICALLY CALIBRATED"   ← ÎN hash, deliberat
n_blocks = 4 · block_manifest_hash peste cele PATRU blocuri oficiale (decizia 2)
```

**Impunerea, tot din T17(a) — Red Team spune că azi e un COMENTARIU, nu o refuzare:**

```python
def compare(a: Result, b: Result) -> Comparison:
    if a.run_hash != b.run_hash:
        raise NonComparableError(a.run_hash, b.run_hash)     # REFUZĂ, nu comentează
```

**Un `assert` care verifică doar inegalitatea plus un comentariu „NON-COMPARABLE" nu impune nimic. Comparația trebuie să fie IMPOSIBILĂ, nu descurajată.**

---

# 4 — DESCOMPUNEREA COST vs POPULAȚIE

**Sub reject-not-widen, populația e definită de podea, iar podeaua e monotonă în `spread_price` ⇒ populația STRESS ⊆ populația BASE. Descompunerea e bine definită.**

```
A = costuri BASE   / populația BASE        B = costuri STRESS / populația BASE
C = costuri STRESS / populația STRESS      A' = costuri BASE  / populația STRESS

efect COST = B − A     efect POPULAȚIE = C − B     total = C − A
ordinea alternativă: A → A' → C. AMBELE se raportează; o diferență materială se SPUNE.
```

## Măsurătoarea care dă răspunsul, nu reziduul

```
OBLIGATORIU alături:  n_base · n_stress · n_dropped = |BASE \ STRESS|
                      media net_R a mulțimii ARUNCATE, evaluată sub costuri BASE
Spune direct dacă podeaua FILTREAZĂ ZGOMOT sau TAIE EDGE. Descompunerea dă un rezidual;
mulțimea aruncată dă un răspuns. Instrumentul evaluează-tot, deja în uz.
```

---

# 5 — T4 ȘI GAP-GUARD-UL: închiderea lui MEAS-9

## Cazul normal, deja specificat

```
R5: SL și TP se verifică INCLUSIV pe bara de intrare; SL primează LA COLIZIUNE.
TP atins, SL NEatins  →  CÂȘTIG. Nu există ambiguitate de ordine: intervalul barei
nu a atins niciodată stopul, deci nicio ordonare de tick-uri nu produce o pierdere.
```

## Gap-guard-ul, aplicat ÎNAINTE de orice evaluare de ieșire

**Preț de intrare realizat = `open[entry_idx]`. Long: `risc = entry − stop`, `recompensă = target − entry`; short simetric.**

```
(a) risc <= 0        intrarea a trecut PRIN stop (gap)
    →  INVALID_EXECUTION. R e NEDEFINIT — NUMITORUL e distrus.
       Exclus din populația de randamente, dar NUMĂRAT și raportat. NICIODATĂ un câștig.
       Repară defectul măsurat: long entry 97 / stop 98 contabilizează azi +0,95.

(b) recompensă <= 0  intrarea a trecut PRIN țintă (gap)
    →  ieșire LA PREȚUL DE INTRARE. R = 0 − costuri, marcat `gap_through_target`.
       Numitorul e INTACT; doar numărătorul e zero. NICIODATĂ o pierdere forțată.
       Repară defectul măsurat: entry 105 / target 102 contabilizează azi −0,436.
```

> **Asimetria e PRINCIPIALĂ, nu o preferință: (a) distruge NUMITORUL, deci niciun număr nu poate fi contabilizat; (b) atinge doar NUMĂRĂTORUL, deci zero e răspunsul corect. Sunt cazuri diferite ca NATURĂ.**

```
REGULA GENERALĂ: nu se contabilizează NICIODATĂ o execuție mai bună decât prețurile
efectiv parcurse DUPĂ intrare.
TOATE CELE TREI MOTOARE o consumă IDENTIC. Și `continue`-ul tăcut din SCREEN e la rândul
lui greșit: ARUNCĂ în loc să NUMERE. Un semnal respins trebuie să apară în audit.
```

---

# 6 — TRIAJUL MECANIC

```python
@dataclass(frozen=True)
class TriageOutcome:
    label: Literal["PROMOTED", "ARCHIVE_NEGATIVE", "ARCHIVE_INSUFFICIENT"]
    effect: float; se: float; mde: float; reason: str
```

```
`mde = z* × se` se calculează la PRECONDIȚIE, ÎNAINTE de test, din SD-ul MĂSURAT și pragul
BH pre-declarat, și intră în `run_hash`. Altfel clasificarea s-ar alege DUPĂ rezultat.

p <= prag BH                          →  PROMOTED
p >  prag,  ê <= 0  ȘI  |ê| >= mde    →  ARCHIVE_NEGATIVE       eliminare CORECTĂ
p >  prag,  |ê| < mde                 →  ARCHIVE_INSUFFICIENT   NU se elimină
p >  prag,  ê > 0   ȘI  ê >= mde      →  ARCHIVE_INSUFFICIENT   semn corect; e despre precizie
```

**CAND-0037: ê = +0,062, mde = 0,0839 ⇒ `ARCHIVE_INSUFFICIENT`. NU se elimină.**

---

# 7 — MEAS-10: cerința R10, pe care am emis-o EU, e azi INOPERANTĂ

**Red Team, verbatim: *„StrategyReport has NO best_share / trimmed_top1pct / any concentration metric (regression from _screen); CEO fat-tail guard UNCOMPUTABLE from canonical output."***

> **Am specificat cele trei câmpuri R10 la v2.7.64 ca obligatorii în fiecare rezultat. Ieșirea canonică nu le poartă. O cerință care nu poate fi calculată din ieșirea oficială nu e o cerință — e un text. BLOCANT pentru R10.**

```
`StrategyReport` primește, cu semantica deja ratificată la v2.7.64:
   best_trade_share    LevelOutput[float]  — Unavailable(reason="net_non_positive") dacă sum(R) <= 0
   trimmed_top1_avg_R  float
   n_trimmed           int   ·  n_trimmed / n   (fracția realizată)
   sum_R  ·  wo1_still_positive
Departajare la tăiere: (R DESC, entry_index ASC). Tăierea e STRES ADVERSARIAL, nu estimator.
Fără ele, garda fat-tail a CEO nu se poate evalua pe ieșirea canonică — deci nu se poate
promova nimic prin ea.
```

---

# 8 — DESCHIS, CLASIFICAT

```
BLOCKING      MEAS-9: gap-guard-ul absent din evaluator (un câștig de +0,95 dintr-un stop
              depășit prin gap). Specificat la punctul 5; VE îl implementează.
BLOCKING      MEAS-10: cele trei câmpuri R10 lipsesc din `StrategyReport` ⇒ R10 inoperant.
BLOCKING      T17: `run_hash` trebuie să acopere DATELE, nu doar configurația, și comparația
              trebuie să REFUZE, nu să comenteze. Hash-ul meu de la v2.7.65 era insuficient.
MATERIAL      rata R3 se re-măsoară la praguri înjumătățite (0,05/0,08, nu 0,10/0,16).
MATERIAL      rezultatele pe 3 sau pe 15 blocuri sunt NON-COMPARABLE cu cele pe 4.
MATERIAL      DEMO se aliniază la T4 + gap-guard; rezultatele anterioare se RE-ETICHETEAZĂ.
LIMITATION    BASE și STRESS rămân PROVISIONAL — NECALIBRATE. `calibration_status` e în hash
              tocmai ca să nu se compare tăcut cu variante calibrate.
LIMITATION    descompunerea e dependentă de drum; ambele ordini se raportează.
NON-MATERIAL  spread-ul modelat (0,20) e de 2,5-4× mai mare decât cel canonic. Conservator ⇒
              rezultatele istorice sunt SUBESTIMATE. Nu invalidează nimic.
```

**Nu cere: gate nou, framework nou, primitivă nouă, metrică nouă. `NewType`, `schema_hash`/`run_hash`, contractul `Ok`/`Unavailable`, triajul în trei rezultate și podeaua N_MIN=25 există toate.**

---

**Manifest:** `config/split_manifest.json` v2.7.66, secțiunea `canonical_contract_v2_7_66`.
