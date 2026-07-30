# STATISTICIAN — MĂRIMEA FAMILIEI ȘI ORDINEA PENTRU MĂSURAREA CELOR ZECE TIPURI DE ZONĂ (OBDZ)

**Document ID:** STAT-OBDZ-ZONE-TYPE-SURVEY-FAMILY-SIZE-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** verificat direct în cod fiecare din cele zece primitive citate ca „gata": `detect_order_blocks`, `track_breaker`, `detect_demand_zones` (`code/order_flow.py`); `detect_fvgs`, `detect_inverse_fvgs`, `detect_fvg_reactions` (CE-50), `count_bpr` (`code/imbalance_mechanics.py`); `detect_liquidity_voids` (`code/order_block_void.py:66`, confirmă citarea „order_block_void" — modulul conține atât definițiile OB cât și detectorul de Liquidity Void); `compute_prior_day_levels`, `compute_prior_week_levels` (`code/institutional_levels.py`). **Toate zece confirmate exact, zero cod nou.** Căutare exhaustivă: zero apariții `session_open`/`SessionOpen` în `code/` — confirmă „Session Open ca nivel" absent. Citit direct semnăturile `detect_mitigations(ob: OrderBlock, ...)` și `detect_rejections(ob: OrderBlock, ...)` — vezi Sarcina 4.

---

# SARCINA 1 — mărimea familiei

**Distincție necesară, care rezolvă aparenta tensiune:** sunt DOUĂ întrebări de familie diferite aici, nu una.

**(a) Familia pentru FAZA DESCRIPTIVĂ (MAE/MFE pe trei brațe, per tip) — vezi Sarcina 2, răspuns NU consumă familie.**

**(b) Familia pentru ORICE ipoteză FORMALĂ care ar rezulta din această trecere în revistă — ASTA e protecția reală împotriva capcanei de 1972.** Fixez ACUM, înainte de orice măsurătoare: **familia = 10**, indiferent câte din cele zece tipuri ies promițătoare descriptiv. Motivul exact al campaniei de 1972: a privi la mulți candidați și a testa formal DOAR pe cei care „arată bine", fără corecție pentru PRIVIRE, e capcana de selecție — nu contează câți din cei zece ajung să pară promițători descriptiv, corecția de semnificație pentru ORICE test formal ulterior trebuie să reflecte câți candidați au fost SUPUȘI PRIVIRII, nu câți au supraviețuit primei impresii.

**Suprapunere de urmărit, nu de ignorat:** „Order Block" și „Demand/Supply" din lista de zece SUNT construcția deja investigată la OBDZ-001/002 (rezultatele din măsurătoarea în trei brațe deja există). **Nu se re-măsoară de la zero** — acel rezultat deja obținut numără ca ELEMENTUL 1 din cele zece ale trecerii în revistă, nu ca o măsurătoare separată, necorelată. Cele nouă rămase (Breaker, FVG, CE-50, IFVG, BPR, Liquidity Void, PDH/PDL, PWH/PWL) sunt de măsurat efectiv nou.

---

# SARCINA 2 — descrierea (MAE/MFE) nu consumă familie deloc, pentru niciunul din cele zece

**Da, exact același raționament ca la pâlnia în atingeri, aplicat identic.** Măsurătoarea pe trei brațe (A/B/C) e o CARACTERIZARE, nu un test cu H0/H1/verdict propriu — la fel ca Măsurătoarea A' și pâlnia de atingeri, niciuna nu a consumat familie. **Cele „treizeci de comparații" (zece tipuri × trei brațe) rămân diagnostic pur, indiferent de câte ies cu un tipar care arată real** — protecția vine DIN FIXAREA family=10 la punctul (b) de mai sus pentru testul formal ulterior, NU din tratarea măsurătorii descriptive ca și cum ar fi ea însăși zece teste.

---

# SARCINA 3 — ordinea, confirm valurile propuse, cu motivul explicit

**Confirm structura ta în trei valuri, cu justificare, nu doar acceptare:**

**Valul 1 — cele opt tipuri de ZONĂ (interval `[low,high]` sau `[close,open]`), zero cod nou:** Order Block (deja măsurat, cf. Sarcinii 1), Breaker, Demand/Supply, FVG, CE-50, IFVG, BPR, Liquidity Void. Toate împart aceeași NATURĂ geometrică (o zonă cu interval propriu) — omogene, cel mai natural grup de măsurat împreună mai întâi.

**Valul 2 — PDH/PDL, PWH/PWL, separate de Valul 1 pe un motiv structural, nu arbitrar:** acestea sunt NIVELE de preț unice (o singură valoare), nu zone cu interval `[low,high]` — semantica de „atingere"/„nemitigat" pentru un nivel unic e diferită de o zonă (poate fi retestat repetat fără ambiguitate de „interval", spre deosebire de o zonă care are o lățime proprie de negociat). Grupare separată, nu din cauza vreunei ierarhii de prioritate, ci pentru că mecanica de măsurare diferă genuin.

**Valul 3 — cele trei primitive NOI (Session Open ca nivel, Mitigation Block, Rejection Block) — DOAR dacă Valurile 1-2 arată că merită.** De acord cu secvențierea: nu se investește în cod nou pentru o întrebare la care Valurile 1-2 ar putea deja răspunde „nu, niciun tip nu adaugă nimic peste retragere" — exact disciplina deja aplicată la Variantele 1/2 de confirmare (ținute pe loc până Varianta 3 arată ceva).

---

# SARCINA 4 — Mitigation Block / Rejection Block: NU sunt aceleași cu detectoarele existente, cer clarificare de intenție înainte de specificare

**Confirmat direct în cod:** `detect_mitigations(ob: OrderBlock, ...)` și `detect_rejections(ob: OrderBlock, ...)` primesc un `OrderBlock` DEJA EXISTENT ca intrare și returnează `list[ReactionEvent]` — sunt detectoare de EVENIMENT DE REACȚIE pe o zonă deja formată de altcineva (OB-ul), NU primitive care își definesc PROPRIA zonă din prețul brut (spre deosebire de OB/FVG/PDH, care fiecare își definesc propriul interval direct din bare).

**Dacă „Mitigation Block"/„Rejection Block", așa cum le intenționează CEO, înseamnă „bara de reacție însăși devine o zonă nouă, testabilă independent"** (analog modului în care un Breaker reutilizează zona OB dar cu polaritate inversată, dar aici ANCORAT la bara de reacție, nu la OB-ul original) — **asta e o primitivă genuin nouă**, care ar cere: definirea propriei zone (ex. corpul sau intervalul barei de reacție), o regulă proprie de valabilitate/consumare, și separarea fereastră-de-valabilitate/fereastră-de-măsurare cu aceeași rigoare ca la OB/DemandZone. **Nu invenez această definiție unilateral** — rămâne o întrebare de clarificare a intenției CEO înainte de a fi specificată, nu de presupus din numele dat.

**Concluzie: NU sunt același lucru cu alt nume — sunt fie o primitivă nouă (dacă intenția e „zonă proprie la reacție"), fie o simplă redenumire fără conținut nou (dacă intenția era doar etichetarea evenimentelor deja existente).** Rămân în Valul 3, condiționate de clarificare, nu presupuse rezolvate.

---

## Ce rămâne neatins

**Testul pereche pe OB×DemandZone rămâne prioritatea, neschimbat.** Nimic din acest document autorizează rularea vreunei măsurători de tip zonă — doar mărimea familiei și ordinea sunt fixate acum, gata de aplicat imediat ce verdictul testului pereche confirmă că metodologia găsește ceva real, nu zgomot repetat în zece forme. Sigilatul intact.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.18 (commit `b10098f`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
