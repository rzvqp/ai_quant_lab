# STATISTICIAN — SPECIFICAȚIE: ANALIZĂ DE PUTERE LA PRAGUL BH REAL
### Constatare (4) escaladată la blocantă — proiectare, nu execuție

**Document ID:** STAT-POWER-BH-SPEC-v1.0
**Data:** 2026-07-25 · **Autor:** Statistician
**Statut:** Specificație executabilă de Validation Engine sau Research Lab. **Nu execut. Nu ating date.**
**Context:** amendament obligatoriu la `docs/SCOPED_FDR_PREREGISTRATION_v1.0.md` (`ea36005`), cerut înainte de rulare.

---

## 0. De ce e blocantă, nu doar un gol

Fără ea, "zero supraviețuitori" și "testul n-a avut putere să vadă" produc exact același output. Nu se pot distinge după rulare fără să devină ajustare post-hoc — trebuie stabilit acum ce ar însemna un rezultat nul.

## 1. Verificarea aritmeticii CEO — confirmată, și extinsă

Recalculat independent:

| B | Granularitate 1/(B+1) | Prag/granularitate |
|---|---|---|
| 20.000 (MC-1) | 5,000×10⁻⁵ | **2,43 pași** |
| 200.000 (MC-2) | 5,000×10⁻⁶ | **24,27 pași** |

Corect. Dar numărul de "pași de granularitate" subestimează cât de nesigură e de fapt estimarea. Am derivat separat, din eroarea standard a proporției (`SE(p̂) ≈ √(α(1-α)/B)`), precizia relativă reală lângă prag:

| B | SE(p̂) lângă prag | Precizie relativă (SE/α) |
|---|---|---|
| 20.000 | 7,79×10⁻⁵ | **64%** — inutilizabil |
| 200.000 | 2,46×10⁻⁵ | **20%** — marginal |
| 1.000.000 | 1,10×10⁻⁵ | **9,1%** — acceptabil |

**Concluzie la sub-întrebarea CEO "la ce B minim devine pragul rezolvabil":** derivat din `B ≥ 100/α` (pentru precizie relativă ≤10%): **B ≥ 824.000**. Coincide, cu marjă, cu treapta MC-3 deja specificată în pre-înregistrare (B≥1.000.000) — treapta existentă e corect dimensionată pentru rezoluția p-value-ului individual. **Aceasta NU rezolvă însă întrebarea de putere** — rezoluția MC spune dacă putem calcula corect p; puterea spune dacă testul poate detecta un efect real la acest prag. Sunt lucruri diferite, ambele necesare.

## 2. Ce spune deja curba de putere existentă — și de ce nu e suficientă

`docs/MATCHED_NULL_VALIDATION.md` §8: putere monotonă în mărimea efectului, "putere la edge=1.0×ATR = 0,98–1,00", calibrată la **α=0,05** (implicit din "power at edge=0 ≈ α"). Pragul real al acestei runde e **1,2136×10⁻⁴, de ~412× mai mic**. Puterea scade, în general, substanțial pe măsură ce pragul de semnificație scade — e foarte plauzibil ca puterea la acest prag, pentru aceleași mărimi de efect care dădeau ~100% la α=0,05, să fie mult mai mică. **Nu pot afirma cu certitudine cât de mică fără execuție — asta e exact motivul pentru care specificația de mai jos e necesară, nu opțională.**

## 3. Specificația analizei de putere (executabilă)

**Metodologie:** reutilizează exact metodologia deja validată (`code/mn_power.py`, seturi de date sintetice cu efect injectat, executate prin `mstrat.simulate`), cu trei schimbări:

1. **Prag de respingere = 1,2136×10⁻⁴** (nu 0,05).
2. **B intern per test = 1.000.000** (nu 1.000 ca în calibrarea originală) — pentru precizia derivată la §1. Nu se economisește aici, deși execuția de producție poate folosi scara adaptivă MC-1→MC-3.
3. **N repetiții per celulă** (mărime efect × frecvență): dimensionat astfel încât intervalul Wilson 95% pe rata de respingere estimată să aibă semi-lățime ≤0,10. Recomandare de pornire: **N=100 per celulă**, ajustabil dacă costul de calcul o cere.

**Grila de mărimi ale efectului:** reutilizează cele 5 puncte din curba originală (comparabilitate directă) **plus 2 puncte suplimentare** concentrate în regiunea unde puterea trece de la aproape-zero la aproape-unu la ACEST prag mai strict (plasarea exactă se poate stabili printr-o privire intermediară asupra rezultatelor grosiere — aceasta nu compromite integritatea preînregistrării FDR, pentru că privește designul studiului de putere, nu decizia de semnificație a ipotezelor testate).

**Frecvențe de tranzacționare:** reutilizează cele 3 niveluri din validarea originală (reprezintă variația reală din corp).

**Livrabil cerut:**
- Curba putere-vs-mărime-efect la α=1,2136×10⁻⁴, per nivel de frecvență.
- **Mărimea minimă detectabilă a efectului (MDES) la putere convențională 80%**, pentru fiecare nivel de frecvență prezent în corpul de 412 — atât în unități ATR-bump, cât și tradusă în R/tranzacție (statistica reală a testului).

## 4. Limită de interpretare rezultată (scrisă acum, nu după)

**Dacă puterea la mărimile de efect plauzibile pentru acest corp e joasă sau necunoscută:** orice rezultat "zero supraviețuitori" trebuie raportat împreună cu MDES-ul calculat aici, cu formularea explicită: *"acest rezultat nu exclude efecte reale sub [MDES] R/tranzacție — testul nu avea puterea să le vadă la acest prag."* Un rezultat nul obținut fără o putere cunoscută **nu închide nimic** și nu trebuie prezentat ca și cum ar închide.

## 5. Recomandare de secvențiere, dat fiind fereastra care se închide

Ideal, analiza de putere precede sau rulează în paralel cu FDR-ul, nu după. Dacă precizia completă (N=100/celulă) nu e fezabilă în timp, recomand minimum: 2-3 mărimi de efect considerate plauzibile pentru acest corp (Research Lab/Alpha ar trebui să indice ce mărimi sunt realiste, din rezultatele de backtest deja existente — nu am acces direct la asta), N=50 per celulă, B=1.000.000 — suficient pentru o determinare calitativă (adecvată / la limită / clar inadecvată), chiar dacă nu o curbă completă, netedă.

---

**Nu am executat nimic. Nu am atins date de piață sau rezultate de backtest. Aceasta e o specificație de proiectare, pentru Validation Engine sau Research Lab.**

**Statistician se oprește aici.**
