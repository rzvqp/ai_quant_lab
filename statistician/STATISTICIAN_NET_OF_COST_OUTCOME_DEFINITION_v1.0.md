# STATISTICIAN — DEFINIȚIA VARIABILEI DE REZULTAT NET DE COSTURI
### Spread, slippage și comision ca variabile explicite în definițiile operaționale

**Document ID:** STAT-COST-OUTCOME-DEF-v1.0
**Data:** 2026-07-25 · **Autor:** Statistician
**Statut:** Amendament la toate pachetele de specificație existente (Pachetele 1-3 din `VALIDATION_ENGINE_HANDOFF_S002_v1.0.md`) — introduce variabila de rezultat net de costuri ca înlocuitor obligatoriu al rezultatului brut de preț, oriunde un candidat testează dacă o mișcare de preț "prezice" sau "e urmată de" ceva.

**Verificare de sursă înainte de a construi pe ea:** am citit direct `code/mstrat.py` și `code/alpha_lab.py` — nu am presupus parametrizarea din memorie sau din citarea CEO.

---

## 0. Precizare de mandat, înainte de definiție

Constituția (§3) interzice Statisticianului să evalueze profitabilitatea unei strategii. Definiția de mai jos **nu evaluează profitabilitatea** — definește **unitatea de măsură** a variabilei de rezultat (la fel cum orizontul K6/K12 sau pragul R sunt decizii de unitate de măsură, nu judecăți de valoare). Diferența: a spune "efectul X e mai mare decât frecarea minimă de execuție, deci e distinguibil de zgomot" e o afirmație statistică despre puterea de discriminare a testului; a spune "X ar fi profitabil de tranzacționat" e o afirmație de profitabilitate, pe care nu o fac aici. **Semnalez explicit această graniță pentru confirmare CEO** — dacă se consideră că introducerea costurilor depășește mandatul, rog o decizie explicită înainte ca Validation Engine să o încorporeze.

## 1. Parametrizarea verificată în cod

Din `code/alpha_lab.py` linia 10-11:
```
CFG = dict(tick=0.1, spread_ticks=1.0, slip_ticks=1.0, ...)
```
Din `code/mstrat.py` (liniile 45, 53, 80, 86, 110) și `alpha_lab.py` (liniile 78, 155):
```
cost = (cfg['spread_ticks'] + cfg['slip_ticks']) * cfg['tick']   # per side
```

**Cost implicit per parte (side) a tranzacției, cu valorile implicite:** (1.0 + 1.0) × 0.1 = **0.2 unități de preț** (pentru XAUUSD, echivalentul a 0.2 puncte). Pentru o tranzacție completă round-trip (intrare + ieșire), costul total e 2× acest cost per-parte = **0.4 puncte**, presupunând aceleași valori implicite la intrare și ieșire.

**Corecție față de formularea sarcinii primite:** codul parametrizează exclusiv **spread + slippage** combinate (`spread_ticks`, `slip_ticks`), transformate în unități de preț prin `tick`. **Nu există o variabilă de "comision" separată nicăieri în `mstrat.py` sau `alpha_lab.py`** — nu invenntez una din lipsă de sursă; semnalez explicit acest gol. Dacă comisionul e o cerere reală, separată de spread/slippage, trebuie fie confirmat unde există parametrizarea lui (nu în aceste două fișiere), fie adăugat ca a treia componentă explicită, cu propria valoare implicită, înainte de blocarea specificației.

**Variantă de stres deja existentă în cod** (`alpha_lab.py` linia 197): `c2['spread_ticks']*=3; c2['slip_ticks']*=3` — o convenție deja stabilită în lab pentru testarea sensibilității la costuri de 3× valoarea implicită. Recomand reutilizarea acestei convenții pentru analiza de sensibilitate (§5), nu inventarea unui multiplicator nou.

## 2. Definiția operațională a variabilei de rezultat net de costuri

Pentru orice candidat unde variabila de rezultat măsoară o mișcare de preț ca proxy pentru "continuare," "extensie," "reversie" sau orice rezultat direcțional (DC-0008 aftermath, DC-0003 outcome-ul spargerii, DC-0004 continuation-excess):

```
rezultat_net = rezultat_brut_de_preț − cost_round_trip
cost_round_trip = 2 × (spread_ticks + slip_ticks) × tick
                = 2 × (1.0 + 1.0) × 0.1 = 0.4 puncte (valori implicite CFG)
```

Semnul se aplică consistent cu direcția poziției implicite a testului (ex. pentru DC-0004, care testează reversie/short după sweep-reject, costul se scade din magnitudinea mișcării în direcția prezisă, indiferent de semn).

**Această variabilă înlocuiește, nu completează, rezultatul brut** în toate testele de semnificație și criteriile de succes/eșec — un rezultat statistic semnificativ pe date brute dar nesemnificativ (sau cu efect sub cost_round_trip) pe date nete NU poate fi raportat ca dovadă a unui efect real, indiferent de valoarea p brută.

## 3. Impact asupra pachetelor existente (DC-0008, DC-0003, DC-0004)

- **DC-0008:** metrica de "aftermath" (extensie/consolidare/reversie post-M15) trebuie recalculată ca mișcare netă de cost, nu doar puncte brute, înainte de testul de interacțiune R × regim_volatilitate.
- **DC-0003:** outcome-ul spargerii (continuare vs. eșec) trebuie prag-uit pe mișcarea netă, nu pe range-ul brut — un "succes" de sub 0.4 puncte nu poate fi distins de cost la execuție reală.
- **DC-0004:** continuation-excess-ul (K6/K12) trebuie raportat atât brut, cât și net — dat fiind că p=0.021/0.029 a fost calculat pe date brute, orice concluzie nouă (inclusiv extensia de robustețe in-sample din Ramura 2) trebuie să raporteze ambele, separat, nu doar varianta netă suprapusă peste rezultatul original.

## 4. De ce lipsa acestei variabile era un gol real

Fără cost_round_trip explicit, un test poate emite STATISTICALLY ROBUST pentru un efect de, să zicem, 0.15 puncte medii — statistic semnificativ dacă eșantionul e suficient de mare, dar **mai mic decât costul minim de execuție (0.4 puncte)** — adică un rezultat care nu poate fi niciodată distins de zgomotul de execuție în practică, oricât de mic ar fi p-value-ul. Zero mențiuni de cost existau, până acum, în lanțul activ de validare (Pachetele 1-3 din handoff-ul S002) — corectat prin acest document.

## 5. Testul de sensibilitate recomandat

Reutilizând convenția `c2` deja existentă (3× spread_ticks, 3× slip_ticks): re-rularea oricărui test de semnificație cu cost_round_trip la 1× (0.4 puncte, implicit) și la 3× (1.2 puncte, convenția de stres deja stabilită) — dacă concluzia se schimbă calitativ între cele două, efectul e marginal față de costurile de execuție și trebuie raportat ca atare, nu ca robust necondiționat.

---

**Acest document amendează Pachetele 1, 2 și 3 din `VALIDATION_ENGINE_HANDOFF_S002_v1.0.md`. Nu s-a executat niciun test, nu s-a modificat niciun cod.**

**Statistician se oprește aici și așteaptă (a) calea corectă către registrul de status, dacă există, și (b) confirmarea că definirea variabilei nete de cost nu depășește mandatul.**
