# MK-01/MK-02 — VERIFICARE STEP 1 (compilare + teste + constatări)

**Autor:** Validation Engine · **Data:** 2026-07-28 · **Branch:** discovery-mk-matrix-v1
**Mandat:** CEO 5.0, Pasul 1. **Statut:** compilare + teste TREC; DOUĂ constatări raportate, ZERO reparate.

**Tensiune de guvernanță (repetată, nerezolvată):** sub Calea A designul e al CEO și verific un design primit — dar scriu testele și rulez măsurătoarea (Pasul 2) pe propriul cod de test, peste implementarea CEO. Statisticianul decide dacă CROSS-VERIFY-SPEC se aplică modulelor de cod sau doar artefactelor derivate din date. Nu o rezolv.

---

## Compilare
`mypy --strict market_structure.py liquidity_mechanics.py` (din `code/`): **Success: no issues found in 2 source files.**

## Teste — `tests/test_structure.py`, 10/10 TREC (array-uri sintetice în memorie, fără CSV)
Scrise independent de VE, nu ale CEO. Verifică mecanic:
- **D1** — nicio rupere nu referă un swing la c ≤ idx+k; `confirmed_idx == idx+k` pentru orice swing. PASS.
- **D2** — platou (maxim egal pe 2 bare) → ZERO swing; vârf unic → 1 swing. PASS.
- **D3** — primul swing de fiecare tip din fiecare bloc = UNCLASSIFIED; blocul 2 nu împrumută referință din blocul 1; nicio fereastră nu traversează o graniță. PASS.
- **D4** — un bazin din blocul 0 NU e măturat în blocul 1 (control pozitiv: e măturat în blocul lui). PASS.
- **D6** — wick-sweep evaluat integral pe bara curentă; penetrare fără close-back ≠ wick-sweep. PASS.
- **D7** — bazin maturat consumat, nu se re-armează (2 bare calificate → 1 singură măturare). PASS.

Implementarea CONFORMEAZĂ celor șase decizii testate.

---

## CONSTATAREA 1 — importul absolut (semnalat de CEO). Găsit citind; nuanțat la verificare.
`liquidity_mechanics.py:42` — `from market_structure import Block, StructureLabel, Swing, SwingKind`.
- Confirmat: import absolut, funcționează doar cu `code/` în `sys.path`.
- **Nuanță (contrazice premisa mandatului):** `code/` NU e pachet (fără `__init__.py`) și TOATE modulele lui importă absolut — `mstrat.py`: `from alpha_lab import CFG`, `import s1`. Deci importul e **consecvent cu convenția reală a lui `code/`**, nu o încalcă. Premisa „restul repo-ului folosește pachete + importuri relative" se aplică la `validation_engine/ve/`, NU la `code/`.
- `mypy --strict` trece (rulat din `code/`).
- **Recomandare (nu aplicată):** (a) păstrează absolut — consecvent cu modelul de execuție al pipeline-ului (`code/` în `sys.path`); niciun risc suplimentar față de restul lui `code/`. SAU (b) transformă `code/` în pachet (`__init__.py` + `from .market_structure import …`) — dar atunci TOT `code/` trebuie convertit și `python code/run_*.py` se rupe. Decizie separată, mai mare. Nu repar.

## CONSTATAREA 2 — `detect_breaks` re-armează swing-uri consumate (găsită la verificare)
`market_structure.py:229` (docstring): *"Un swing e consumat de prima rupere… nu se refolosește."* Codul NU respectă asta.
- Bucla de activare (liniile 241-253) re-atribuie `live_hh`/`live_ll`/… la FIECARE bară. După ce o rupere consumă swing-ul (`live_hh = None`, l.259), bara următoare îl re-activează.
- **Demonstrat:** un singur HH (idx6, preț 30) cu `close > 30` pe barele 9,10,11 produce **3 BOS_BULL**, toate referind swing idx6. Ar trebui 1.
- **Impact:** NU afectează Pasul 2 (auditul de volum folosește `detect_swings` + `label_structure`, nu `detect_breaks`). DAR ar umfla numărul de rupturi pentru orice ipoteză bazată pe BOS/CHoCH (inclusiv, potențial, LM-001 dacă ar folosi rupturi).
- **Recomandare (nu aplicată):** urmări swing-urile consumate într-un `set` (ca `detect_sweeps` cu `consumed`), sau restructura activarea să nu re-armeze. Nu repar — raportez.

---

**Nu am modificat modulele CEO. Nu am atins date reale. mypy curat, 10/10 teste. Continui la Pasul 2 (audit de volum M15_v2) după publicarea acestui pas.**
