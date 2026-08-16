# STATISTICIAN — SUBCONTRACTUL DE COST, RATIFICAT. ÎNREGISTRARE ȘI CONSECINȚE.

**Document ID:** STAT-COST-SUBCONTRACT-RATIFIED-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Regim:** pauză pe cercetare. Acesta e ÎNREGISTRARE DE CONTRACT — permisă explicit. Nicio rulare, nicio recalibrare.
**Verificare de sursă:** citit `canonical_contract_v2_7_66` din manifest — câmpurile `config_hash`, `data_identity`, `run_hash` și valorile BASE/STRESS, verbatim.

> **NU înlocuiesc și NU recalibrez decizia CEO. Costurile monitorizate în shadow devin sursa canonică. Ce urmează sunt consecințele mecanice ale acestei ratificări asupra contractului deja scris — plus trei lucruri care decurg din ea și pe care mandatul nu le conține.**

---

# PARTEA 1 — ÎNREGISTRAREA. Și mecanismul cerut EXISTĂ deja.

```
SUBCONTRACT_COST = RATIFICAT prin decizie CEO.
Contractul general rămâne NOT RATIFIED pe celelalte puncte. Ratificarea e PARȚIALĂ și se
consemnează ca atare: un subcontract ratificat nu ratifică nimic din jurul lui.
```

**Formula și unitățile, transcrise din contractul canonic — neschimbate, doar cu statutul mutat:**

```
UNITATE CANONICĂ   spread_price = bid-ask COMPLET (ask − bid), în USD
CONVERSIE          effective_spread_half = spread_price / 2
                   (dovada: COST 0,20 = 2 × EFF_SPREAD 0,10, iar un dus-întors costă
                    spread-ul complet o dată ⇒ `effective_spread` moștenit E jumătate)
COST DUS-ÎNTORS    cost_round_trip = spread_price + entry_slip + exit_slip
COMPONENTA R3      K_SPREAD × effective_spread_half = 2 × (spread_price/2) = spread_price
                   ⇒ factorul 2 nu dispare: se ANULEAZĂ cu conversia.

BASE     spread_price 0,05 · slip 0,00/0,00 · cost_round_trip 0,05 · componentă R3 0,05
STRESS   spread_price 0,08 · slip 0,08/0,08 · cost_round_trip 0,24 · componentă R3 0,08
```

## `SUPERSEDED_COST_MODEL` se impune PRIN CONSTRUCȚIE, nu prin disciplină

**`calibration_status` a fost pus ÎN `config_hash` la v2.7.65, deliberat, cu motivul scris atunci: „când sosește calibrarea empirică, hash-ul se SCHIMBĂ, deci rezultatele provizorii NU se pot compara tăcut cu cele calibrate."**

> **Ratificarea schimbă `calibration_status` din `PROVISIONAL — NOT EMPIRICALLY CALIBRATED` în `RATIFIED — SHADOW-MONITORED`. Asta schimbă `config_hash`, deci `run_hash`. Prin urmare TOATE rezultatele anterioare devin NON-COMPARABILE PRIN TIP, automat, iar `compare()` RIDICĂ. Nu e nevoie de niciun mecanism nou: eticheta `SUPERSEDED_COST_MODEL` e numele uman al unei stări pe care tipul o impune deja.**

```
Primesc SUPERSEDED_COST_MODEL, prin schimbarea hash-ului: leaderboard-ul · S3 · CAND-0037 ·
CAND-T05 · toate cele ~300 de eliminări Alpha · fiecare cifră publicată până acum.
```

---

# PARTEA 2 — CELE DOUĂ STATUTURI NOI, definite executabil

```
COST_BASE_FALSIFIED     candidatul iese din lista ACTIVĂ; RĂMÂNE în registrul complet
                        pentru audit și multiplicitate. `m` NU se modifică: familia e
                        MONOTONĂ, iar o schimbare de STATUT nu returnează un slot.
COST_STRESS_FRAGILE     eșec NUMAI în STRESS. Se raportează SEPARAT. NU e eșec BASE,
                        NU elimină, NU se confundă cu el.
```

## Predicatul lui `COST_BASE_FALSIFIED` — și de ce trebuie să fie exact acesta

**Eliminarea în BASE nu mai e provizorie DIN CAUZA COSTURILOR. Corect. Dar consemnez ce anume a încetat să fie provizoriu, fiindcă e o parte, nu tot:**

> **Motivul pentru care ne-respingerea lui CAND-0037 nu era o eliminare N-A FOST NICIODATĂ calibrarea costului. A fost PUTEREA: MDE 0,0839 față de un efect observat de 0,062. Ratificarea costului închide o sursă de provizorat și o lasă pe cealaltă exact cum era.**

```
COST_BASE_FALSIFIED cere AMBELE:
   (a) rularea a folosit modelul de cost RATIFICAT (`cost_model_version` în `run_hash`), ȘI
   (b) ê_BASE <= 0  ȘI  |ê_BASE| >= mde_BASE      ← adică ARCHIVE_NEGATIVE sub BASE

Dacă (b) cade fiindcă |ê| < mde  ⇒  ARCHIVE_INSUFFICIENT. NU e falsificat de cost — e NETESTAT.
```

**De ce contează formularea: eticheta spune „falsificat de COST". Ca s-o merite, costul trebuie să fie ce a falsificat. Fără condiția (b), fiecare candidat subputernic ar fi eliminat sub o etichetă de cost — iar asta ar include CAND-0037, al cărui eșec în BASE e garantat prin construcție la n=246.**

> **Ratificarea face eliminarea DEFINITIVĂ acolo unde se aplică. Nu LĂRGEȘTE unde se aplică. Compoziția mulțimii eliminate e neschimbată; ce se schimbă e că nu mai poate fi redeschisă prin recalibrare.**

---

# PARTEA 3 — TREI CONSECINȚE CARE NU SUNT ÎN MANDAT

## 3.1 Cele ~300 de eliminări sunt SUPERSEDED, deci NEEVALUATE — nu confirmate

**Mandatul spune „acum modelul e oficial, deci eliminările sunt definitive". Sunt definitive sub modelul NOU. Dar eliminările au fost făcute sub modelul VECHI, iar la v2.7.65 am măsurat direcția:**

```
spread modelat vechi:  cost_round_trip 0,20
spread oficial BASE:   cost_round_trip 0,05        ⇒ de PATRU ORI mai mic
```

> **Cele ~300 de eliminări au fost făcute cu un cost de patru ori mai mare decât cel oficial. Un candidat respins la −0,03R sub 0,20 poate fi pozitiv sub 0,05. Direcția erorii e sistematic către FALSE NEGATIVE.**

```
„SUPERSEDED_COST_MODEL se aplică la tot ce s-a măsurat până acum" ȘI „eliminările sunt
definitive" NU pot fi amândouă adevărate pentru eliminările făcute sub modelul înlocuit.
SUPERSEDED înseamnă NEEVALUAT sub modelul curent — nu CONFIRMAT.
REZOLVARE, compatibilă cu pauza: eliminările vechi rămân `SUPERSEDED_COST_MODEL`, NU trec în
`COST_BASE_FALSIFIED`, până la re-rularea sub modelul oficial. Re-rularea e cercetare, deci
DUPĂ `MANDATE_2_PASS`. Nu cer nimic acum; cer doar să nu se marcheze definitiv ce n-a fost
evaluat cu modelul care le face definitive.
```

## 3.2 Costul devine o MĂRIME MĂSURATĂ, deci are eroare standard

**Un cost monitorizat în shadow nu e o constantă — e o estimare dintr-un eșantion. Folosit ca punct exact, subestimează incertitudinea din `net_R`, iar `net_R` e estimandul.**

```
CERINȚĂ MINIMĂ, un câmp: modelul de cost poartă `n_observations` și dispersia măsurată
(p50/p75/p95 pe spread), nu doar punctul. Nu cer propagarea incertitudinii acum — cer ca
datele necesare ei să nu se piardă. Un punct fără dispersie nu se mai poate desface înapoi.
```

## 3.3 Costul e măsurat pe O perioadă și aplicat pe TOATE — și asta are direcție

> **Shadow măsoară costul ACUM. Evaluarea îl aplică pe 2011-2025. Spread-urile pe XAUUSD în 2011 erau aproape sigur mai largi decât azi. Aplicarea unui spread măsurat în 2026 pe date din 2011 face rezultatele vechi să pară MAI BUNE decât au fost.**

**Combinat cu 3.1 — vechiul model era de 4× mai scump — `HISTORICAL_TRANSFER` al fiecărui candidat se va îmbunătăți substanțial, dintr-un motiv care nu are NIMIC de-a face cu strategia. Consemnez asta ACUM, înainte de re-rulare, ca îmbunătățirea să nu fie citită ca descoperire.**

```
CERINȚĂ MINIMĂ, un câmp: `cost_provenance_window` — perioada pe care s-a măsurat costul —
intră în `config_hash`. Aplicarea în afara ei rămâne permisă, dar devine o ASUMPȚIE DECLARATĂ,
atacabilă, exact ca polaritatea lichidității de la SPEC 3. Niciun gate nou.
```

---

# PARTEA 4 — DESCHIS, CLASIFICAT

```
BLOCKING      niciunul pentru integrarea AI Trader.
MATERIAL      cele ~300 de eliminări rămân SUPERSEDED_COST_MODEL, NU trec în
              COST_BASE_FALSIFIED, până la re-rularea sub modelul oficial (după MANDATE_2_PASS).
              Direcția erorii vechi e către FALSE NEGATIVE: cost de 4× prea mare.
MATERIAL      `COST_BASE_FALSIFIED` cere ARCHIVE_NEGATIVE sub BASE, nu simpla ne-respingere.
              Altfel eticheta de cost elimină candidați subputernici — CAND-0037 inclus.
MATERIAL      `cost_model_version`, `cost_provenance_window`, `n_observations` și dispersia
              intră în `config_hash`. Patru câmpuri, niciun mecanism nou.
LIMITATION    costul e măsurat pe o perioadă și aplicat pe toate; HISTORICAL_TRANSFER se va
              îmbunătăți pentru un motiv care nu ține de strategie. Consemnat ÎNAINTE.
LIMITATION    costul e o estimare cu eroare standard, folosită ca punct. Se păstrează dispersia.
NON-MATERIAL  `SUPERSEDED_COST_MODEL` nu cere mașinărie: schimbarea lui `calibration_status`
              schimbă `config_hash`, deci comparația RIDICĂ deja. Eticheta e numele uman al
              unei stări impuse de tip.
```

**Nu cere: gate nou, framework nou, metrică nouă, nicio rulare. `config_hash`, `run_hash`, triajul în trei rezultate și familia monotonă există toate.**

---

**Manifest:** `config/split_manifest.json` v2.7.73, secțiunea `cost_subcontract_ratified_v2_7_73`.
