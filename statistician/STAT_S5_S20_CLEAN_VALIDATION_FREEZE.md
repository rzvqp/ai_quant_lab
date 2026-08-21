# POPULAȚIA CURATĂ DE VALIDARE + PROTOCOALELE S5 ȘI S20

**Divizia Statistician · `CEO-S5-S20-CLEAN-VALIDATION-EVIDENCE-001` · 2026-08-21**

```
S5_S20_CLEAN_VALIDATION_EVIDENCE_FROZEN
S5_INDEPENDENT_VALIDATION_PROTOCOL_FROZEN
S20_INDEPENDENT_VALIDATION_PROTOCOL_FROZEN
READY_FOR_RT_S5_S20_INDEPENDENT_VALIDATION
```

`FINAL_HOLDOUT_ACCESS_COUNT = 0`. Nicio strategie nu a fost executată. Niciun rezultat de performanță
pe regiunea curată nu a fost inspectat — protocoalele de mai jos sunt scrise **înainte** de orice acces
la rezultat.

---

## 1 — POPULAȚIA CURATĂ, DERIVATĂ MECANIC

Nu am folosit datele aproximative din mandat; am derivat totul din artefacte.

| element | valoare exactă |
|---|---|
| start | **`2023-07-24 10:30:00Z`** (index canonic 144.522) |
| end | **`2025-10-12 23:00:00Z`** (index canonic 197.093) |
| **bare** | **52.572** |
| contiguitate | **da** — indici canonici consecutivi, fără goluri |
| proveniență | **integral blocul B4**, corpus manifest-gated |
| corpus-părinte | 197.094 bare, loader `alpha-automation-v1` / `_common.load('M15_v2')` |
| fișier sursă SHA-256 | `57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37` |
| **population OHLC hash** | `bac65b1a8840a0b82a384aa86bfafab9f38f36abb03cd030c6f7afdfbc457ea1` |
| **timeline hash** | `4c9ce7b7f245bb9a375edaec42bcf3355a78ba99d2dd2fbf8d897ecf2ed4728a` |
| rețetă hash | `bars_sha256_v1` (RT-RANGE-0010) |

★ **Corecție de cifră față de mandat: 52.572, nu ~52.567.** Diferența de 5 bare vine din faptul că
numărul meu anterior a fost obținut printr-un filtru de date pe fișierul **brut**, în timp ce cifra
de aici e derivată din corpusul **manifest-gated**. Cea corectă e **52.572**; o folosesc pe aceasta.

### Dovezile cerute (§2, §3), mecanice

```
felia VALIDATION istorica CONSUMATA : [2023-07-24 10:15Z inapoi ... 2020-07-21 00:15Z]
holdout FINAL ratificat incepe la   : 2025-10-23 09:15Z

toate barele > sfarsitul feliei consumate      : TRUE
toate barele < cutoff-ul holdout-ului final    : TRUE
suprapunere cu felia consumata (bare)          : 0
bare in holdout-ul final ratificat             : 0
FINAL_HOLDOUT_ACCESS_COUNT                     : 0
```

Regiunea se oprește la **2025-10-12**, adică la capătul populației canonice pre-holdout — cu **11 zile
marjă** sub cutoff-ul holdout-ului final. Nu se apropie de el.

**§4 respectat:** singurul criteriu de excludere folosit a fost **consumul anterior de dovezi**
(felia pozițională 60–80%) și eligibilitatea de guvernanță (holdout-ul ratificat). Niciun rezultat de
strategie nu a intrat în definirea regiunii — la momentul derivării nu exista niciunul.

Artefact off-Git: `clean_validation_population.json`.

---

## 2 — IDENTITĂȚILE CANDIDAȚILOR, VERIFICATE DIN DEPOZIT

| | S5 | S20 |
|---|---|---|
| candidat | `C_2d587447` | `C_09d2245b` |
| spec | `S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}` | `S20{ctx=h4up, exit=rr3, lb=50, stop=atr, trig=breakout}` |
| reprezentant | `7472f3d412f2` | `601e20753a4a` |
| direcție | long-only | long |
| mecanism | opening-range momentum | hybrid sweep + MTF |
| context HTF | — | `ed57853`, obligatoriu, fără implementare alternativă |

Verificate din registrul istoric și din `661bb8f` / `f491ad7`, nu din mesajul mandatului.

## 3 — DEZVĂLUIRILE DE CONTAMINARE ISTORICĂ (§13, păstrate)

**S5:** felia de validare istorică a fost consumată — `rep_val_exp = 0,17885` a intrat în
`robustness_score` și în poarta de încredere. Contra-factual: rangul rămâne **1**, reprezentantul
rămâne **RR3** — expunerea nu a schimbat nimic, dar nu restaurează orbirea.

**S20:** `rep_val_exp = 0,08733` a influențat clasarea de familie; contra-factual **rangul s-a mutat
4 → 6**. Selecția reprezentantului/specificației a rămas **`val_exp`-free** (regula
`[fragile, stab, n, t1]`, verificată că reproduce exact ambii reprezentanți).

Aceste fapte **nu se șterg** și nu sunt anulate de folosirea regiunii curate: ele privesc *cum a fost
ales* candidatul, nu *pe ce e testat acum*.

---

## 4 — PROTOCOALELE, PRE-ÎNREGISTRATE (identice ca structură, aplicate SEPARAT)

**Nu se pooling-uiesc. Nu există validare de portofoliu.** Fiecare strategie trece sau cade singură.
Jaccard 0,047 rămâne context de cercetare.

### 4.1 Contract de execuție (§9)

`XAUUSD` · intrare **next-bar open** · `min_tick = 0,01 USD` · stop minim
`max(2 × spread, 0,05 USD, 10% ATR)` · tratament bid-ask complet · BASE ratificat ·
**STRESS round-trip = 0,24** · fără fill favorabil pe aceeași bară.

> ★ **Constrângere pe care o impun explicit, dintr-o constatare făcută la inspecția motorului:**
> motorul istoric `mstrat.CFG` are `tick = 0.1` — valoare pe care **Red Team a marcat-o deja ca
> greșită de 10×** (`RT-AUDIT-MEAS-0001`, `RT-CODE-A-0007`). Validarea **nu** are voie să folosească
> `mstrat.CFG` pentru cost sau pentru podeaua de stop; se folosește exclusiv modelul ratificat de mai
> sus. Verificarea acestui punct e o **condiție de integritate**, nu o preferință.

### 4.2 Porți de acceptare, fixate acum

| poartă | criteriu |
|---|---|
| **A. adecvarea eșantionului** | `n >= 100` tranzacții. Sub prag → `VALIDATION_INCONCLUSIVE_INSUFFICIENT_SAMPLE`, **nu** FAIL, **nu** PASS |
| **B. expectanță BASE** | `BASE net > 0` |
| **C. supraviețuire la cost** | `STRESS net > 0` la round-trip 0,24 |
| **D. stabilitate temporală** | regiunea se împarte în **3 treimi cronologice egale**, fixate acum, înainte de orice rezultat; cerință: **cel puțin 2 din 3** treimi cu BASE net > 0, și **nicio** treime sub `−0,10` |
| **E. robustețea cozii** | `best-1%-removed BASE > 0`. Dacă e negativ dar `winsor-99 > 0` → `TAIL_DEPENDENT`, tratat ca **FAIL** al porții E |
| **F. robustețe de execuție** | intrare întârziată cu 1 bară: `BASE net > 0` |
| **G. degradare de risc** | drawdown maxim `<= 15R`; pierdere maximă pe o tranzacție `<= 2,0R` după podeaua de stop |
| **H. fidelitate de specificație** | spec-ul executat identic cu cel înghețat la §2; `config`/`fingerprint` verificate; zero variante |

**Verdict:** `PASS` cere **A…H toate**. Orice poartă căzută → `NOT_SUPPORTED`. `A` nesatisfăcută →
`INCONCLUSIVE`. **Niciun prag nu se modifică după ce se vede vreun rezultat**, și nicio metrică nouă nu
se adaugă pentru că arată favorabil.

### 4.3 Geometria tranzacțiilor (§10) — raportare obligatorie

Pentru fiecare strategie, prospectiv:

```
SL median in USD           ·  SL median in pips de proiect
TP median in USD           ·  TP median in pips de proiect
distanta pana la tinta     :  P25 / P50 / P75
procentul tranzactiilor cu tinta >= 70 / >= 80 / >= 100 pips de proiect
conventie: 10 pips = 1,00 USD   (2400 -> 2408 = 80 pips de proiect)
```

★ **Un fapt derivabil din specificație, fără să rulez nimic:** ambele strategii au `exit = rr3`, iar
motorul calculează ținta ca `entry + dir × 3 × risk`, unde `risk = |entry − stop|` **după** aplicarea
podelei de stop. Deci, pentru ambele, **distanța până la țintă este exact de 3× distanța de stop**.
Întrebarea „micro-scalping sau nu" se reduce, pentru amândouă, la **mărimea stopului**: un stop median
de `X` USD implică o țintă mediană de `3X` USD, adică `30X` pips de proiect. Pragul de 80 de pips de
proiect (8,00 USD) e atins de o tranzacție **dacă și numai dacă** stopul ei depășește **2,67 USD**.

Geometria **nu se măsoară în acest mandat**: ar cere rularea strategiilor pe regiunea curată, ceea ce
§11 interzice. Se raportează de Red Team, la execuție. **Nu am modificat nimic din S5 sau S20** ca să
satisfacă preferința pentru ținte mai mari; o măsurăm cum e.

### 4.4 Izolarea mediilor

**ENV A — execuție:** acces la populația curată înghețată, la spec-urile înghețate, la contextul HTF
`ed57853` și la modelul de cost. Produce registrul complet de tranzacții (timestamp semnal, timestamp
intrare, direcție, entry, stop, exit, costuri, R brut, BASE net, STRESS net, amprenta strategiei,
amprenta contextului HTF) și îl **îngheață**: `S5_VALIDATION_TRADES_SHA256`,
`S20_VALIDATION_TRADES_SHA256`. Fără adaptare pe baza rezultatului.

**ENV B — scorare:** consumă registrul înghețat, protocolul înghețat și modelul de cost ratificat.
**Nu execută** nicio strategie. Nicio tranzacție nu se șterge după ce metricile sunt cunoscute.

### 4.5 Condiții de eșec de integritate

Oricare dintre acestea → `S5/S20_VALIDATION_INTEGRITY_FAIL`, oprire fail-closed, fără verdict:
populația executată ≠ hash-ul înghețat; atingerea holdout-ului final; folosirea `mstrat.CFG` pentru
cost/podea; spec diferit de cel înghețat; context HTF din altă implementare decât `ed57853`; ștergere
de tranzacții după calcularea metricilor; modificarea unui prag după vederea rezultatelor.

### 4.6 Izolarea comparației istorice (§19 al mandatului anterior)

`BASE +0,064 / +0,153` și `STRESS +0,032 / +0,069` sunt **dovezi de cercetare**. Nu intră în niciun
calcul de acceptare. Pot apărea **numai după** ce verdictul independent e calculat, ca simplu context.

---

## 5 — CE NU AM FĂCUT

Nu am executat S5 sau S20, nu am generat registre de tranzacții, nu am calculat nicio metrică, nu am
măsurat geometria, nu am atins holdout-ul final, nu am combinat cele două strategii și nu am inspectat
niciun rezultat pe regiunea curată.

**Proprietar următor: Red Team**, pentru execuția în două medii și scorarea contra acestor porți.
Nicio autorizare pentru Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker sau tranzacții live.
