# S20 — PREGĂTIREA VALIDĂRII INDEPENDENTE

**Divizia Statistician · mandat `STAT-ALPHA-S20-INDEPENDENT-VALIDATION-PREP-001` · 2026-08-21**

```
S20_VALIDATION_EVIDENCE_NOVELTY_AUDIT = PARTIALLY_CONSUMED
S20_INDEPENDENT_VALIDATION_EVIDENCE_NOT_CLEAN
FRESH_VALIDATION_EVIDENCE_REQUIRED
```

Protocolul **nu** e înghețat; nu am pre-înregistrat praguri și nu am executat S20.
`FINAL_HOLDOUT_ACCESS_COUNT = 0`.

★ **Acest raport conține și o CORECȚIE la o concluzie pe care am publicat-o ieri despre S5** (§6).

---

## 1 — IDENTITATEA S20, ÎNGHEȚATĂ ȘI NEAMBIGUĂ

| element | valoare |
|---|---|
| candidat | `C_09d2245b` · familia `S20` |
| mecanism | `S20/ctx=h4up/trig=breakout` — hybrid sweep + MTF |
| spec canonic | `S20{ctx=h4up, exit=rr3, lb=50, stop=atr, trig=breakout}` |
| ipoteză reprezentativă | `601e20753a4a` |
| direcție | **long** |
| membri RW în cluster | 5 |
| clasificare | `B_research_candidate`, `shortlisted = True` |
| migrare HTF | `ed57853` — `code/htf_context_historical.py`, 25/25 teste |
| rezultat corectat (`f491ad7`) | n = 690 · GROSS +0,175 · BASE **+0,153** · STRESS **+0,069** · best-1%-removed **+0,128** · ambele blocuri pozitive |

**§2 — o singură specificație istorică S20 candidează.** Registrul conține **un singur** candidat S20,
iar reprezentantul lui e reprodus exact de regula documentată a builder-ului (vezi §4.2). Nu există
ambiguitate de rezolvat tacit.

## 2 — POPULAȚIA DE CERCETARE, VERIFICATĂ INDEPENDENT

| element | verificat din `f491ad7` |
|---|---|
| block0 (DEV) | `2011-07-26 → 2013-09-27` · 52.404 bare |
| block1 (DEV) | `2016-01-11 → 2018-04-06` · 52.851 bare |
| **DEV total** | **105.255** — corespunde cerinței |
| OHLC sha256 (16) | `47c9b16ba77bcbaf` |
| evaluare | **per bloc**, combinată — golul 2013→2016 nu e niciodată punte |
| block2 (CALIB) | `2020-08-11 → 2021-09-05`, 25.237, nefolosit la scorare |

Nu emit `S20_RESEARCH_EVIDENCE_INTEGRITY_FAIL`: populația corectată e exact cea cerută, iar Wave 2 a
**semnalat singură** contaminarea Wave 1 (160.888 negated, ~34% din golul neratificat).

---

## 3 — ★ AUDITUL `val_exp` / RANKING — CONTAMINAT PE RANKING, CURAT PE SPECIFICAȚIE

Programul istoric S1–S20 folosește un split **pozițional**: `research [0,60%)`,
`validation [60%,80%)`, `holdout [80%,100%]`. Felia de validare = **`2020-07-21 → 2023-07-24`**.
Pe ea s-a calculat `val_exp`.

**Canalul contaminat — clasarea și preselecția.** `stratdev_registry.py:97`:

```python
reg['robustness_score'] = (rep_stability + mech_profitable_frac + log10(rep_n)/3
                           - rep_t1 - (rep_dd/25).clip(upper=1)
                           + rep_val_exp.fillna(0).clip(-0.3, 0.3))     # <- validare
```

Pentru S20: `rep_val_exp = 0,08733` → **+0,0873 (6,5%)** din `robustness_score = 1,3436`.

★ **Contra-factual măsurat — și aici S20 diferă de S5:**

| | cu `val_exp` | fără `val_exp` |
|---|---|---|
| rangul S20 între 17 candidați | **4** | **6** |

**Expunerea a mișcat efectiv poziția lui S20** (S5 rămânea 1 în ambele cazuri). Preselecția e plafonată
la 3 per familie și ordonată după `robustness_score`, deci rangul contează.

**Canalul CURAT — alegerea specificației.** `stratdev_registry.py:63`:

```python
g = g.sort_values(['fragile', 'stab', 'n', 't1'], ascending=[True, False, False, True])
rep = g.iloc[0]        # NU conține val_exp
```

Am verificat că regula reproduce **exact** reprezentantul declarat, pentru ambele familii:
`S20 → 601e20753a4a` ✓ și `S5 → 7472f3d412f2` ✓. Deci `lb=50`, `stop=atr`, `exit=rr3` **nu** au fost
alese cu dovezi de validare.

> **Corecție metodologică proprie.** Prima dată am recalculat reprezentantul cu formula `rob` din
> `knowledge_system.py:92` — care *chiar* conține `val_exp` — și am obținut un „reprezentant diferit",
> deci o aparentă neconcordanță în registru. **Era formula greșită**: acel `rob` construiește alt
> artefact (fișierul de deduplicare), nu `STRATEGY_CANDIDATE_REGISTRY.parquet`. Am verificat înainte
> de a publica; neconcordanța nu există. Consemnez eroarea fiindcă era la un pas de a deveni o
> constatare falsă despre integritatea registrului.

**Concluzie:** validarea a influențat **clasarea și preselecția** lui S20, dar **nu** specificația.
Invarianța contra-factuală nu restaurează orbirea — dar aici nici nu există: rangul chiar s-a mișcat.

---

## 4 — HARTA DE SUPRAPUNERE

```
felia VALIDATION istorica (60-80%) : 2020-07-21 -> 2023-07-24

  block0 (DEV)      2011-07-26 -> 2013-09-27   52.337 bare | consumat:      0   (0,0%)
  block1 (DEV)      2016-01-11 -> 2018-04-06   52.840 bare | consumat:      0   (0,0%)
  block2 (CALIB)    2020-08-11 -> 2021-09-05   25.264 bare | consumat: 25.264 (100,0%)   ★
  block3 (VALID)    2022-12-16 -> 2025-10-12   66.641 bare | consumat: 14.074  (21,1%)
```

★ **Blocul de CALIBRARE al Alpha e integral, 100%, felie de validare istorică.** Nu afectează verdictul
de mai jos (calibrarea nu e validare), dar e o constatare pe care o semnalez, nu o trec cu vederea.

**Descompunerea partiției de validare a lui S20 (block3):**

```
CONSUMAT istoric                          14.074  (21,1%)   2022-12-16 -> 2023-07-24
CURAT — nici consumat, nici holdout final 52.567  (78,9%)   2023-07-24 -> 2025-10-10
holdout FINAL ratificat (>= 2025-10-23)        0
```

---

## 5 — ★ DE CE „CURAT" ȘI „SIGILAT" DEPIND DE DEFINIȚIE

În proiect coexistă **două** definiții de holdout, ambele reale și ambele în cod:

| definiție | holdout începe | sursă |
|---|---|---|
| ratificată, curentă | **2025-10-23T09:15Z** | `_common.py:43`, `PRE_HOLDOUT_SPLIT_ID`, folosită de manifest și de toate artefactele RANGE |
| moștenită, S1–S20 | **2023-07-24** (ultimii 20% pozițional) | `run_ext_family.py:45` — *„holdout d[b:] SEALED"* |

Regiunea **2023-07-24 → 2025-10-23** e holdout sub definiția moștenită și **pre-holdout disponibil**
sub cea ratificată. Crucial: sub ambele, ea **nu a fost niciodată evaluată** — „sealed" înseamnă
neatins, nu consumat.

---

## 6 — ★ CORECȚIE LA RAPORTUL MEU DESPRE S5 (`9091ec2`)

În raportul S5 am scris că partiția propusă e „17,5% consumată + **82,5% holdout sigilat** → **ZERO**
bare utilizabile". **Am folosit definiția moștenită fără să o compar cu cea ratificată.**

Măsurat corect, pentru S5:

```
CONSUMAT istoric                          15.086  (22,3%)
CURAT — nici consumat, nici holdout final 52.567  (77,7%)   2023-07-24 -> 2025-10-10
holdout FINAL ratificat                        0
```

**„ZERO bare utilizabile" era greșit.** Sub arhitectura ratificată există aceleași ~52.567 bare
neconsumate și în afara holdout-ului final. Verdictul de fond al S5 — evidența propusă **nu e curată**
— rămâne valabil, fiindcă partiția *ca întreg* conține 22,3% material consumat. Ce se schimbă e
concluzia despre disponibilitate: **nu e „nimic de folosit"**, ci „există un rest curat substanțial,
iar restrângerea la el e o decizie CEO". Aceasta e **a 15-a eroare a mea într-o cifră publicată**;
o corectez explicit, nu tacit.

---

## 7 — VERDICT ȘI CE URMEAZĂ

Per §8, `PARTIALLY_CONSUMED` conduce la:

```
S20_INDEPENDENT_VALIDATION_EVIDENCE_NOT_CLEAN
FRESH_VALIDATION_EVIDENCE_REQUIRED       -> STOP inainte de executia strategiei
```

Nu îngheț protocolul și nu restrâng singur partiția: a exciza 21,1% **după** ce am măsurat
contaminarea e o decizie de design care îți aparține, nu o consecință mecanică. Nu improvizez altă
partiție.

**Răspunsul la §6, explicit:** *da*, există evidență simultan neconsumată istoric **și** în afara
holdout-ului final ratificat — **52.567 bare, `2023-07-24 → 2025-10-10`**, comună lui S20 și S5.

Trei opțiuni, decizia ta:

1. **Restrângerea validării la restul curat** (52.567 bare) — pre-înregistrată explicit ca partiție
   redusă, cu contaminarea celor 21,1% documentată și exclusă. Cea mai apropiată de validare
   independentă reală, fără date noi.
2. **Date cu adevărat noi**, în afara celor 355.696 bare actuale.
3. **Validare pe partiția întreagă**, etichetată `NOT_INDEPENDENT`, cu greutate redusă.

Dacă alegi (1), pot îngheța protocolul complet — praguri, adecvarea eșantionului, diagnostice de coadă
și temporale, izolarea ENV A/ENV B, procedura de îngheț a registrului de tranzacții — într-un mandat
următor, **înainte** de orice execuție.

## 8 — CONTRACTUL DE EXECUȚIE (înregistrat, neaplicat)

`XAUUSD` · intrare **next-bar open** · `min_tick = 0,01` · stop minim
`max(2 × spread, 0,05 USD, 10% ATR)` · BASE ratificat · **STRESS round-trip 0,24** · fără fill
favorabil pe aceeași bară. Context HTF exclusiv prin `ed57853`; nicio implementare HTF alternativă.

**Nu am făcut:** execuție S20, registru de tranzacții, metrici de validare, atingerea holdout-ului,
combinare cu S5 (Jaccard 0,047 rămâne context de cercetare), praguri pre-înregistrate. BASE +0,153 și
STRESS +0,069 rămân **dovezi de cercetare**, nu rezultate de acceptare.

---

**Proprietar următor: CEO.** Nimic către Red Team — nu există protocol înghețat de auditat.
S20 rămâne `HISTORICAL_CANDIDATE_CONFIRMED_FOR_DEEPER_RESEARCH`. Nicio autorizare pentru Strategy
Catalog, Alpha, AI Trader, LIVE_SHADOW, broker sau tranzacții.
