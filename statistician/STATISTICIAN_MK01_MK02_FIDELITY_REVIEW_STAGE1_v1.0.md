# STATISTICIAN — REVIZIA DE FIDELITATE MK-01/MK-02, ETAPA 1 DIN 4

**Document ID:** STAT-MK01-MK02-FIDELITY-REVIEW-STAGE1-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Ce verific:** fidelitatea implementării față de deciziile D1-D7 pe care le-am ratificat (`STATISTICIAN_MARKET_STRUCTURE_RATIFICATION_AND_PREREG_v1.0.md`, Mandatul 3.9, și `STATISTICIAN_D3_FULL_RATIFICATION_AND_GOVERNANCE_v1.0.md`, Mandatul 3.10) — NU dacă codul rulează corect, NU dacă e testat, NU dacă ar trebui ratificat pentru execuție. Citit direct `code/market_structure.py` (292 linii) și `code/liquidity_mechanics.py` (229 linii), branch `discovery-mk-matrix-v1`, `git status` curat pe ambele fișiere (nimic necomis), istoricul: `efcee5f` (drafturile originale) → `d24845b` (patch-ul de re-armare, Mandatul 5.2). **Ambele fișiere încă poartă marcajul DRAFT DE REFERINȚĂ în docstring, exact cum a spus CTO.**

**Nu am rulat niciun cod. Nu am modificat niciun modul. Nu ratific implementarea — decizia finală rămâne a CEO, după VE și Red Team.**

---

## D1 — Lookahead (`confirmed_idx`) — **FIDEL**

`market_structure.py`: `Swing.confirmed_idx` calculat exact `i+k` (liniile 136, 150). `detect_breaks` filtrează: `if s.confirmed_idx >= c or s.idx in consumed: continue` (linia 253) — DOAR swing-uri cu `confirmed_idx < c` devin `live_*`. Exact D1.

`liquidity_mechanics.py`: `LiquidityPool.available_idx = s.confirmed_idx` (linia 114, `build_pools`) — propagă direct confirmed_idx-ul swing-ului sursă. `detect_sweeps` filtrează: `if pool.available_idx >= c: continue` (linia 167) — identic ca principiu cu filtrul din `market_structure.py`. **Fidel în ambele fișiere.**

## D2 — Departajare (inegalitate strictă pe ambele laturi) — **FIDEL**

`detect_swings`: `is_high = all(high[i] > high[j] for j in window if j != i)` (linia 131) — `>` strict, verificat pe TOATĂ fereastra `[i-k, i+k]` (ambele laturi). Simetric pentru low (`<` strict, linia 145). Nicio egalitate nu produce swing. Exact D2, cifră cu cifră cu ce am ratificat.

## D3 — Granițe de bloc (reset, primul swing UNCLASSIFIED) — **FIDEL**

`detect_swings`: bucla externă e `for b_i, block in enumerate(blocks):`, iar `Block.contains_window(i,k)` (linia 73-75) verifică explicit că `[i-k, i+k]` încape INTEGRAL în bloc — nicio fereastră de fractal nu poate traversa o graniță. `label_structure`: `last_high`/`last_low` sunt dicționare CHEIATE pe `block_index` (liniile 170-171) — un bloc nou nu are nicio intrare până nu apare primul lui swing, deci `prev is None` → `UNCLASSIFIED` (liniile 178-179, 188-189) automat pentru primul swing de fiecare tip per bloc. **Mecanismul e "reset prin cheie de dicționar per bloc", nu un apel explicit de `reset()`" — comportamental IDENTIC cu ce am ratificat, doar implementat printr-o structură de date diferită de cea pe care aș fi presupus-o eu; notez asta ca detaliu descriptiv, NU ca deviere**, întrucât rezultatul (reset per bloc, prim-swing-UNCLASSIFIED) e exact cel ratificat.

## D4 — Bazinele nu supraviețuiesc unui gol între blocuri — **FIDEL**

`liquidity_mechanics.py::detect_sweeps`: `active = [p for p in pools if p.block_index == b_i and block.start <= p.available_idx < block.end]` (liniile 156-160) — recalculat DIN NOU la fiecare bloc, filtrat strict pe `block_index`-ul curent. `consumed` (linia 161) e de asemenea redeclarat în interiorul buclei per-bloc. Niciun bazin nu poate persista peste o graniță — exact D4.

## D5 — Maparea M5→M15 neimplementată — **FIDEL**

Docstring-ul modulului (liniile 18-25) declară explicit că maparea NU e implementată, cu motivul ("artefact de aliniere care nu există în manifest"). **Verificat prin absență, nu prin găsirea unei încercări eșuate:** zero cod de mapare M5, zero referință la M5 în vreo funcție a fișierului. Codul face EXACT ce am ratificat — nimic — cu scopul declarat explicit ("agnostic la timeframe," dar maparea nu e construită). Fidel.

## D6 — Wick-sweep, integral pe bara curentă — **FIDEL**

`detect_sweeps`, pentru bazin BELOW: `penetrated = low[c] < pool.price`, `back_inside = close[c] > pool.price` (liniile 171-172) — ambele calculate DOAR din `low[c]`/`close[c]`, nicio referință la bare viitoare sau anterioare. Simetric pentru ABOVE (liniile 175-176). Formula e cifră cu cifră cea ratificată: `low[c] < bazin ȘI close[c] > bazin`.

## D7 — Bazinul maturat se consumă, fără re-armare — **FIDEL**, verificat mai riguros decât cerut

`consumed: set[int]` (linia 161, indici în lista `active`) — verificat ÎNAINTE de orice evaluare de condiție (`if k in consumed: continue`, liniile 165-166), iar la o măturare, `consumed.add(k)` (linia 193). **Verificat suplimentar, nu doar acceptat pe cuvânt:** acest tipar (mulțime de indici, filtrare UPSTREAM înainte de atribuire) e EXACT mecanismul cerut explicit de patch-ul de re-armare (Mandatul 5.2/Sarcina 4 din `STATISTICIAN_D3_FULL_RATIFICATION_AND_GOVERNANCE_v1.0.md`: "la nivel de index/mulțime, NU prin setarea unei variabile downstream") — comitul `d24845b` confirmă că acest exact patch a fost aplicat aici. Fidel, cu conformitate directă la patch-ul deja specificat separat.

---

## Patch-ul de circularitate "_scan_reactions, formation_idx+2" — **AMBIGUU: nu se aplică literal acestor două fișiere**

**Mă opresc aici, exact cum s-a cerut, pentru o discrepanță care trebuie clarificată înainte de a continua.** Căutat direct în ambele fișiere: **nu există nicio funcție `_scan_reactions` și niciun offset literal `formation_idx+2` în `market_structure.py` sau `liquidity_mechanics.py`.** Acel patch specific (scanare de la `formation_idx+2`, evitând circularitatea impuls-bar-își-înghite-propria-zonă) a fost ratificat separat, pentru un modul DIFERIT — `order_flow.py` (Mitigation/Rejection pe Order Blocks), Mandatul 3.23 — nu pentru MK-01/MK-02.

**Verificat, totuși, dacă riscul ANALOG de circularitate există aici, chiar fără acel nume de funcție:** un swing HIGH la `idx` (k=2) cere, prin D2, `high[idx] > high[j]` STRICT pentru tot `j` din `[idx-2, idx+2]` — deci barele din chiar fereastra de confirmare a fractalului NU pot depăși propriul extrem, prin construcție. Filtrul `pool.available_idx >= c: continue` (D1) exclude oricum testarea măturării înainte de `confirmed_idx+1`. **Nu există o circularitate silențioasă analogă aici — proprietatea de siguranță e obținută corect, dar printr-un mecanism diferit (poarta `available_idx` + inegalitatea strictă D2), nu prin patch-ul `formation_idx+2` citat.**

**Concluzie pe acest punct:** referința mandatului la acest patch, ca aplicabil ACESTOR DOUĂ fișiere, e imprecisă — patch-ul aparține altui modul. Codul din `market_structure.py`/`liquidity_mechanics.py` nu are nevoie de el și nu-l conține, dar realizează aceeași proprietate de siguranță prin construcție proprie, deja verificată mai sus la D1/D2. Semnalez asta explicit, nu o trec sub tăcere ca "verificat."

---

## Ce NU am făcut, exact cum s-a cerut

Nu am rulat `detect_swings`/`detect_breaks`/`build_pools`/`detect_sweeps` pe date reale sau sintetice. Nu am verificat executabilitatea, acoperirea de teste, sau conformitatea la `mypy --strict` — acestea sunt ale VE. Nu am ratificat implementarea pentru execuție. Nu am modificat niciun modul.

## HANDOFF

**Validation Engine, etapa 2.** Rezultatul acestei revizii: **7 din 7 decizii FIDELE**, plus un punct de clarificare (nu o deviere de cod) pe patch-ul de circularitate citat greșit ca aplicabil acestor fișiere.

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
