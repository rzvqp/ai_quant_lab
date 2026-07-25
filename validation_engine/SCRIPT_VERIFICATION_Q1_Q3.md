# VERIFICARE ÎMPOTRIVA SCRIPTURILOR ALPHA IN-SAMPLE
### Q1–Q3: definițiile Statisticianului vs. convențiile efective din obs0003/0008/0012/0013

**Document ID:** VE-SCRIPTVERIF-Q1Q3-v1.0
**Data:** 2026-07-24 · **Autor:** Validation Engine
**Declanșator:** instrucțiune CEO — verificarea definițiilor din `STATISTICIAN_OPERATIONAL_DEFINITIONS_v1.0.md` împotriva scripturilor originale, înainte de blocarea specificației oficiale.
**Acces:** DA. Scripturile au fost citite direct.

> **Rezultat, pe scurt: definițiile propuse de Statistician NU coincid cu convențiile folosite efectiv în testul in-sample.** Discrepanțele sunt materiale (graniță de zi, număr și granițe de sesiune), nu cosmetice. Un re-test pe holdout care ar folosi definițiile Statisticianului v1.0 **nu ar fi o replicare** a testului in-sample, ci un test diferit — exact riscul pe care Statisticianul l-a semnalat el însuși și a cerut să fie verificat.
>
> Conform mandatului, Validation Engine **raportează** diferențele. Nu le rezolvă. Reconcilierea este o decizie a Statisticianului și a CEO.

---

## 1. Sursele citite

| Fișier | Rol |
|---|---|
| `ai_quant_lab-alpha-automation/research_log/scripts/obs0003_session_reject.py` | testul de sesiune (6 celule) |
| `.../obs0008_ny_reject_null.py` | matched-null NY, escaladare |
| `.../obs0012_reject_allcells_null.py` | corecție de selecție pe toate celulele |
| `.../obs0013_ny_stability.py` | stabilitate temporală (split intern 2025-01-01) |
| `.../research_log/scripts/_lab.py` | helper comun: `add_prior_day`, `drift`, `fwd`, `boot_ci` |
| `ai_quant_lab-alpha-automation/edge_research/_common.py` | loader + etichetarea sesiunii (linia 91) |

Toate cele patru scripturi importă `from _lab import *` și, prin el, `_common`. Convențiile sunt deci **comune și identice** în toate patru.

---

## 2. Ce fac efectiv scripturile

### 2.1 Granița zilei (relevant pentru Q1)

`_lab.add_prior_day`:
```python
df["day"] = df["dt"].dt.date          # data calendaristică a timestamp-ului UTC
daily = df.groupby("day").agg(d_high=("high","max"), ...)
daily["pdh"] = daily["d_high"].shift(1)
```

`dt` este UTC (din CSV-uri). Deci **ziua = data calendaristică UTC**, cu granița la **00:00 UTC (miezul nopții UTC)**. „Prior-day high" se calculează prin gruparea pe această zi UTC și `shift(1)`.

### 2.2 Definiția evenimentului (relevant pentru Q1)

`obs0003` (identic în 0008/0012/0013):
```python
idx = list(g.index)                                   # barele zilei UTC
up = next((i for i in idx if df["high"].iat[i] > ph), None)   # PRIMA bară care depășește PDH
if up is not None and df["close"].iat[up] < ph:               # ...dacă acea bară închide sub PDH
    recs.append(("up", df["session"].iat[up], up))
```

Evenimentul este **prima bară a zilei care depășește nivelul**, verificată apoi pentru reject. Dacă prima bară care depășește PDH **nu** închide sub PDH, ziua nu are up-reject — chiar dacă o bară ulterioară ar depăși și ar respinge. Nu este „bara de deschidere a zilei" și nu este „orice bară de reject".

### 2.3 Sesiunile (relevant pentru Q3)

`_common.py`, linia 91:
```python
hh = d["dt"].dt.hour                                  # ora UTC
d["session"] = np.select([hh < 8, hh < 13, hh < 21],
                         ["asia", "london", "ny"], default="late")
```

**Patru** sesiuni, pe cupe de **oră UTC fixă, fără DST**:

| Sesiune | Interval UTC (fix) |
|---|---|
| asia | 00:00–07:59 |
| london | 08:00–12:59 |
| ny | 13:00–20:59 |
| late | 21:00–23:59 |

### 2.4 Baseline și orizonturi (context)

- `obs0003`: baseline = **drift global** (`drift(df,K)` pe toate barele).
- `obs0008/0012/0013`: baseline = **media forward a sesiunii proprii** (ex. media NY). Deci baseline-ul „propriu al sesiunii" apare abia de la escaladarea 0008, nu în 0003.
- Orizonturi: K6 și K12 calculate împreună (0003, 0008); `obs0013` folosește doar K6.
- Matched null: reeșantionare din barele aceleiași sesiuni, 3000 de trageri, `seed=7`, p pe coada stângă (reversie), one-sided.
- Split de stabilitate: `2025-01-01` (0013), nu granița de holdout.

---

## 3. Tabelul discrepanțelor

| # | Aspect | Statistician OPDEF v1.0 (propus) | Scripturi Alpha (in-sample efectiv) | Coincid? |
|---|---|---|---|---|
| 1 | **Granița zilei** | 17:00 America/New_York, ajustat DST | data calendaristică UTC = **00:00 UTC** | ❌ **NU** |
| 2 | **PDH/PDL** | derivat din ziua ancorată la 17:00 NY | derivat din ziua UTC | ❌ **NU** (consecință a #1) |
| 3 | **Zile fără bară** | excluse din populație (fereastra [graniță, graniță+1h)) | concept inexistent: ziua UTC fără o primă-bară-de-reject nu produce eveniment; nu există „prima oră după graniță" | ❌ **mecanism diferit** |
| 4 | **Nr. de sesiuni** | 3 (Asia, London, NY) | **4** (asia, london, ny, **late**) | ❌ **NU** |
| 5 | **NY (UTC)** | 12:00–21:00 (EDT) / 13:00–22:00 (EST), DST | **13:00–21:00 fix** | ❌ **NU** |
| 6 | **Londra (UTC)** | 07:00–15:30 (BST) / 08:00–16:30 (GMT), DST | **08:00–13:00 fix** | ❌ **NU** |
| 7 | **Asia (UTC)** | 00:00–06:00 fix | **00:00–08:00 fix** | ❌ **NU** (ora de sfârșit) |
| 8 | **Ancorarea sesiunii** | ora locală a centrului financiar, conversie DST per dată | cupe de oră UTC fixă, fără DST | ❌ **NU** |
| 9 | **Sesiuni reciproc exclusive** | da | da | ✅ **DA** |
| 10 | **K6/K12 aceeași familie** | da; K6 primar | ambele calculate împreună; 0013 folosește doar K6 | ✅ compatibil |
| 11 | **Definiția evenimentului** | „prima bară H1 a zilei" (lectura nefixată în OPDEF) | „prima bară care **depășește** nivelul", apoi verificată reject | ⚠️ **de precizat** |
| 12 | **Baseline** | forward propriu al sesiunii | 0003 global; 0008+ pe sesiune | ⚠️ **parțial** |

**Șapte discrepanțe materiale (#1–#8), una compatibilă parțial, două de precizat.** Cele mai grave sunt #1 (granița zilei) și #4–#8 (sesiunile): schimbă direct compoziția populației și a celor 6 celule pe care se bazează întregul test.

---

## 4. Consecința metodologică

Statisticianul a cerut explicit (`OPDEF v1.0` §1, §3): definițiile propuse „trebuie confirmate contra convenției efectiv folosite în scripturile originale înainte ca Validation Engine să le blocheze ca definitive — altfel riscăm exact tipul de discrepanță tăcută între definiția in-sample și cea din re-test pe care tot acest proces încearcă să-l prevină."

Verificarea arată că **regula propusă și regula in-sample diferă**. Prin urmare:

- definițiile din `OPDEF v1.0` sunt **aprobate metodologic** de Statistician, dar **NU sunt o replicare a testului in-sample** — sunt un design *diferit*;
- blocarea lor în specificația oficială DC-0004 ar transforma re-testul pe holdout dintr-o replicare într-un test nou;
- Validation Engine **nu poate alege** între „replicăm exact in-sample (UTC-midnight, 4 sesiuni fixe)" și „adoptăm definiția nouă, mai corectă metodologic (17:00 NY, 3 sesiuni DST)". Este o decizie de proiectare statistică + o decizie de guvernanță (ce înseamnă „replicare" pentru acest candidat). Aparține Statisticianului și CEO.

Ambele opțiuni sunt legitime, dar **exclusiv una** poate fi numită „replicare a testului care a produs p=0.021/0.029". Cealaltă este un test nou, care nu moștenește rezultatul in-sample ca justificare.

---

## 5. Gol nou de vocabular descoperit prin verificare — G7

Independent de reconciliere, verificarea a scos la iveală un gol structural: **evenimentul in-sample „prima bară a zilei care depășește nivelul" nu este exprimabil în vocabularul actual.**

Predicatele curente pot selecta *toate* barele care satisfac o condiție (`compare` high>PDH ȘI close<PDH), dar nu pot selecta *prima bară din zi care satisface o condiție* — nu există o primitivă de tip „prima apariție în domeniu" (`first-in-scope`). `bar_position@v1` dă poziția absolută (index 0 = bara de deschidere), nu „prima care satisface predicatul P"; `cooldown@v1` deduplică evenimente apropiate, dar nu implementează „prima depășire a zilei".

Fixtura DC-0004 a folosit `bar_position` index 0 ca substituent nenormativ tocmai pentru că evenimentul real „prima depășire" nu este exprimabil. Cele două populații diferă.

**G7 este înregistrat în backlog. NU este rezolvat** (conform instrucțiunii permanente: gol nou → înregistrează, oprește-te, raportează). O posibilă rezolvare viitoare ar fi o primitivă `first_in_scope@v1 {scope, predicate}`, dar nu o proiectez acum.

---

## 6. Ce s-a modificat, ce nu

- **Nu s-a modificat niciun script Alpha, niciun artefact al lui Alpha, niciun Discovery Candidate, niciun raport.** Scripturile au fost citite, nu atinse.
- **Definițiile Statisticianului NU au fost blocate în nicio specificație normativă.** Fixturile DC-0004 și DC-0008 rămân explicit nenormative pe punctele Q1/Q3.
- Q1–Q3 rămân **întrebări deschise**: aprobate metodologic de Statistician, dar **contrazise de scripturile in-sample** — necesită reconciliere Statistician + CEO înainte de blocare.

---

**Validation Engine a executat verificarea cerută și raportează diferențele. Nu a ales între cele două definiții și nu a rezolvat G7. Nicio dată de piață nu a fost citită; scripturile au fost citite ca text-sursă, nu executate.**
