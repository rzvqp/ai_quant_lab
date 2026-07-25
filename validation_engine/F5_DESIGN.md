# F5 — DESIGN + CONTRADICȚIE DE REPRODUCERE (OPRIRE ÎNAINTE DE IMPLEMENTARE)
### Execuția `matched_null@v1` și reproducerea valorii p a obs0012

**Document ID:** VE-F5-DESIGN-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Statut:** **DESIGN — REZOLVAT.** Documentul a oprit inițial pentru o contradicție de parametri (§3). **CEO a ales opțiunea A** (2026-07-25): separare strictă calibrare/oficial. F5 a fost apoi implementat integral — vezi `F5_REPORT.md` (calibrarea reproduce obs0012 bit-exact; oficialul rulează cu B=200000 și seed derivat per celulă, independent de ordine). Acest document rămâne ca istoric al deciziei.

> **Rezoluție (CEO, opțiunea A):** harness de calibrare (seed=7, B=3000, generator partajat, ordinea obs) care reproduce obs0012 exact + execuție oficială separată (B=200000, `derived_from_spec_hash` per celulă). Contradicția din §3 a fost rezolvată prin separarea celor două moduri, fără a modifica DC-0004 sau registrul.

---

### Statut inițial (istoric)
**DESIGN — OPRIT la verificarea de fezabilitate.** O contradicție de parametri între specificația oficială DC-0004 și criteriul de reproducere (obs0012) face imposibilă îndeplinirea simultană a tuturor cerințelor F5. Nu am implementat și nu am executat nimic. Aștept decizia CEO.

Conform mandatului F5 — „dacă apare orice diferență între rezultatul Validation Engine și Alpha, oprește imediat execuția și raportează înainte de orice corecție" — semnalez această diferență **la nivel de design**, înainte de a executa, pentru că este previzibilă și deterministă (nu depinde de rulare).

---

## 1. Domeniul F5 (cerințele CEO)

Execuția metodelor statistice pe fereastra **deschisă**. Prima metodă: `matched_null@v1`, exact conform protocolului Alpha. Criteriu de reproducere: **valoarea p a obs0012** (seed=7, 3000 reeșantionări). Fără atingerea holdout-ului. Fără modificarea motorului F4, a DC-0004, a registrului sau a vocabularului. Exclusiv intrări validate în F4.

---

## 2. Protocolul `matched_null` al obs0012 (referința)

Din `obs0012_reject_allcells_null.py` (verificat în cod):
```python
rng = np.random.default_rng(7)                 # UN SINGUR generator, partajat
for (d, s) in cells:                           # cells = rej.keys() cu n>=25, în ordinea de inserție
    base = mean(fwd[i] for i in sess_idx[s])   # baseline per sesiune, TOATE barele
    ex   = [sgn*(fwd[i]-base) for i in events]  # excess pe evenimentele celulei
    pool = [sgn*(fwd[i]-base) for i in sess_idx[s]]  # excess pe TOATE barele sesiunii
    m    = mean(ex)
    null = [pool[rng.integers(0,len(pool),len(ex))].mean() for _ in range(3000)]  # B=3000
    p_left = mean(null <= m)                    # coada stângă
```
Valori de referință (obs0012, K=6): up/ny **0.0253**, down/london 0.3620, down/asia 0.3640, down/ny 0.4123, up/london 0.6570, up/asia 0.9593.

**Trei proprietăți esențiale pentru reproducerea EXACTĂ:**
1. **seed=7 literal**, un singur generator;
2. **B=3000** reeșantionări;
3. **generatorul partajat este consumat între celule în ordinea de inserție a dicționarului `rej`** — deci valoarea p a fiecărei celule depinde de ordinea celulelor și de starea generatorului moștenită de la celulele anterioare.

---

## 3. CONTRADICȚIA — parametrii DC-0004 ≠ parametrii obs0012

Specificația oficială DC-0004 (validată în F4, pe care F5 trebuie să o folosească) declară pentru `matched_null@v1`:

| Parametru | DC-0004 oficial (intrare F4) | obs0012 (criteriu de reproducere) | Coincid? |
|---|---|---|---|
| **B** (reeșantionări) | **200000** | **3000** | ❌ **NU** |
| **seed** | `seed_policy: derived_from_spec_hash` (seed derivat, NU 7) | `default_rng(7)` | ❌ **NU** |
| tail | left | left (coada stângă) | ✅ |
| preserve | session | pool per sesiune | ✅ |
| statistic | mean excess | mean excess | ✅ |

Consecință directă și deterministă (nu necesită execuție pentru a fi cunoscută):

> **Rulând `matched_null@v1` cu parametrii declarați de DC-0004 (B=200000, seed derivat), valoarea p va DIFERI de cea a obs0012 (B=3000, seed=7)** — atât pentru că B diferă (altă precizie Monte-Carlo), cât și pentru că sămânța diferă (alt flux de numere aleatoare). Nu există nicio sămânță derivată din hash-ul specificației care să coincidă cu 7, și niciun B=200000 care să dea exact valoarea p a unui B=3000.

Cele două cerințe CEO nu pot fi satisfăcute simultan:
- **„utilizează exclusiv intrările validate în F4"** → B=200000, seed derivat (din DC-0004);
- **„criteriul de reproducere este valoarea p a obs0012 (seed=7, 3000)"** → B=3000, seed=7;
- **„nu modifica DC-0004", „nu modifica registrul/vocabularul"** → nu pot alinia parametrii DC-0004 la obs.

Aceasta este a patra oară când materializarea/execuția scoate la lumină o diferență între specificația oficială și scripturile Alpha (după F4-1/F4-2/F4-3), de data aceasta la nivelul **parametrilor metodei**, nu ai intrărilor.

O a treia dificultate, tehnică: chiar cu seed=7 și B=3000, reproducerea EXACTĂ necesită și consumul generatorului partajat **în aceeași ordine a celulelor** ca obs0012 (ordinea de inserție a dicționarului `rej`), care este un artefact de implementare, nu un element principial al protocolului. Ordinea celulelor din specificația DC-0004 (declarată explicit) diferă de ordinea de inserție a lui `rej`.

---

## 4. Opțiunile (pentru decizia CEO) — NU aleg singur

| Opțiune | Descriere | Respectă „nu modifica DC-0004/registru"? |
|---|---|---|
| **A — harness de calibrare cu parametrii referinței** | `matched_null@v1` se rulează, pentru **testul de reproducere**, cu parametrii obs0012 (seed=7, B=3000, ordinea de consum a obs), pe intrările F4. Aceasta verifică fidelitatea implementării metodei față de Alpha. Rularea oficială DC-0004 (B=200000, seed derivat) rămâne separată = execuția reală, mai precisă, cu p **echivalent statistic**, nu bit-identic | ✅ da — nu modifică DC-0004/registrul; reproducerea folosește parametrii referinței ca criteriu de calibrare |
| **B — echivalență statistică** | Se acceptă că p-ul rulării oficiale DC-0004 (B=200000, seed derivat) este **echivalent statistic** cu obs0012 (în intervalul Monte-Carlo), nu bit-identic. Criteriul devine „p în CI-ul obs", nu „p exact" | ✅ da |
| **C — alinierea DC-0004 la obs** | Se schimbă B→3000 și seed→7 în DC-0004 | ❌ NU — contrazice „nu modifica DC-0004" și politica de seed (decizia F2.3) |

**Recomandarea mea: Opțiunea A.** Motive:
1. Verifică **fidelitatea metodei** față de Alpha bit-exact (folosind parametrii referinței ca criteriu de calibrare), fără a modifica DC-0004, registrul sau politica de seed.
2. Păstrează separarea corectă: *reproducerea/calibrarea* (seed=7, B=3000, pentru a demonstra că implementarea = Alpha) vs. *rularea oficială* (B=200000, seed derivat, conform politicii de reproductibilitate). Aceasta este exact distincția din arhitectura F5–F6 (execuție vs. calibrare).
3. Sub opțiunea A, intrările F4 rămân cele validate; doar parametrii de *reeșantionare* ai testului de reproducere provin din referință.

Punct rămas deschis chiar și sub A: consumul generatorului **în ordinea celulelor obs0012**. Recomand ca reproducerea să replice explicit ordinea obs (artefact de implementare) pentru bit-exactitate, marcând clar că ordinea de consum nu este un element principial al protocolului.

---

## 5. Impactul asupra arhitecturii

`matched_null@v1` se implementează în `ve/methods/` (nou), consumând intrările F4 (excess per eveniment, pool per sesiune). Nu atinge motorul de materializare F4, registrul, schema sau DC-0004. La calibrare (F6) metoda ar primi `VALIDATED`; până atunci rămâne `UNVALIDATED` (execuția de reproducere este o probă de fidelitate, nu o promovare).

**Dar** — designul NU poate fi finalizat până când contradicția din §3 nu este rezolvată de CEO, pentru că determină cu ce parametri rulează metoda și ce înseamnă „reproducere".

---

## 6. Oprire

Conform procesului („implementează numai după ce designul este clar") și mandatului („oprește imediat și raportează înainte de orice corecție"), **mă opresc aici**. Nu am implementat `matched_null@v1`, nu am executat nicio metodă, nu am atins holdout-ul, nu am modificat nimic.

Aștept decizia CEO asupra §4 (A/B/C) înainte de a implementa și executa F5.

---

**Nu s-a implementat nicio metodă. Nicio execuție. Holdout neatins. Registru/DC-0004/motor neatinse. Validation Engine se oprește și așteaptă decizia CEO asupra contradicției de parametri.**
