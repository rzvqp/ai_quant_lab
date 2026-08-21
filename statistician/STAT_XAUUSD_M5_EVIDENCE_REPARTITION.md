# XAUUSD M5 — REPARTIȚIA DOVEZILOR

**Divizia Statistician · `STAT-XAUUSD-M5-EVIDENCE-REPARTITION-001` · 2026-08-21**

```
XAUUSD_M5_REPARTITION_INTEGRITY_BLOCKED
```

Nicio strategie executată, niciun rezultat Alpha inspectat. Motivul blocării e la §3 și e **material**,
nu procedural: **regiunea pe care mandatul o vrea sigilată nu mai e `OUTCOME_UNSEEN`.**

---

## 1 — SURSA CANONICĂ, VERIFICATĂ

| element | valoare |
|---|---|
| fișier | `data/market/OANDA_XAUUSD_M5.csv` — OANDA nativ, **nu** resamplat din M15 |
| SHA-256 | `cbb6eebe1a189ebb20972318a8d98a36bfa461d2cd030bbaa7ba5430cc9f3814` (`CONFIRMED_BY_STATISTICIAN`) |
| status manifest | `VALIDATED` |
| **prima bară nativă** | **`2021-07-27 15:45:00Z`** — confirmă data aproximativă din mandat |
| ultima bară | `2026-07-27 17:55:00Z` |
| bare | **354.669** |
| pas modal | 300 s · pauze > 1 h: 1.290 · pauza maximă 73,1 h |
| bare lipsă față de o serie continuă | 171.246 (weekend + sărbători — normal pentru FX/metale) |

## 2 — POPULAȚIILE EXACTE (calculate, nu aproximate)

**Research-eligibil propus (`< 2025-01-01`)**

```
2021-07-27 15:45Z  ->  2024-12-31 21:55Z        243.676 bare
ohlc_sha256      d2e66ad0abcc4fd41a78fcdcbe9679fd31894d3aadc1cf1e98c96ad3a7db2d87
timeline_sha256  24ec318e46cb364090b95655d862ca041ceadd3775f3304aa1f67d5b5258ac4f
```

**Sigilat propus (`>= 2025-01-01`)**

```
2025-01-01 23:00Z  ->  2026-07-27 17:55Z        110.993 bare   (31,3% din fișier)
ohlc_sha256      0cfee388495871970e30e8ffa1e586c670eb58d68c74ef8777c60abe862e764b
timeline_sha256  409fc0ca042a29c34500ba605399fe2dfa4ab53baa3caf699fb0c619a996cf4a
```

---

## 3 — ★ AUDITUL DE CONSUM ANTERIOR — MOTIVUL BLOCĂRII

### 3.1 Constatarea

`ve_n1_replay`/wp5b conține `code/zone_confirmation.py` — clasificatorul **N4 de confirmare a zonei pe
M5**, ratificat. Documentația lui proprie spune:

> *„Măsurătoare pe M5 real (`OANDA_XAUUSD_M5`)… **Terțile RE-DERIVATE la W=3 (măsurate pe M5 real,
> 3.508 evenimente…). ALEGERI, nu derivate.**"*

Adică **praguri alese pe baza datelor M5 reale** — exact categoria „parameter selection" din §5.

Scriptul de derivare, `scratch_verify/measure_n4_w3_tertiles.py`:

```python
linia 20-21   M15 = pd.read_csv("data/market/OANDA_XAUUSD_M15.csv")
              M5  = pd.read_csv("data/market/OANDA_XAUUSD_M5.csv")   # <- fisierul BRUT
linia 37      START = max(WIN, 20000)
linia 46      for i in range(START, n15 - 1, STEP):                  # <- pana la CAPATUL fisierului
linia 63      SL = 2000                                              # cautare M5 inainte de ancora
```

**Citește fișierele brute, fără poarta de manifest**, iar bucla merge până la ultima bară M15
(`2026-07-27`), căutând înainte în M5. Prin urmare regiunea M5 **2025+** — **110.993 bare, 31,3% din
fișier** — a fost **accesibilă și folosită** la derivarea pragurilor.

### 3.2 Clasificarea

```
2021-07-27 -> 2024-12-31   PARTIALLY_CONSUMED   (N4 tertile + arhitectura de split deja ratificata)
2025-01-01 -> 2026-07-27   PARTIALLY_CONSUMED   (N4 tertile) -- NU este OUTCOME_UNSEEN
```

### 3.3 De ce blochează, și cât de tare

§4 cere ca regiunea sigilată să fie `OUTCOME_UNSEEN`. **Nu este.** Nuanțez însă onest, în ambele
sensuri:

- Consumul e **inter-program**: 2025+ a fost văzut de un clasificator **structural** de nivel 4
  (confirmarea zonei), nu de vreo strategie Alpha, și **nicio expectanță/PnL** nu a fost calculată
  acolo.
- **Riscul devine material exact în cazul pe care mandatul îl are în vedere.** §7 spune că evidența
  M5 va servi arhitecturii `H4/H1/M15 EDGE → M5 ENTRY/TRIGGER`. **N4 *este* confirmarea zonei pe M5** —
  adică fix stratul din care s-ar construi un trigger M5. Dacă triggerul Alpha folosește pragurile N4,
  atunci un clasificator calibrat pe 2025+ ar fi validat pe 2025+ → scurgere reală.
- Dacă triggerul M5 al Alpha **nu** atinge pragurile N4, contaminarea rămâne inertă pentru acest scop.

Nu pot decide eu care variantă e — depinde de un design care nu există încă. De aceea raportez blocat,
nu „curat cu asterisc".

---

## 4 — A DOUA CONSTATARE: O ARHITECTURĂ M5 RATIFICATĂ EXISTĂ DEJA, ȘI E MAI STRICTĂ

Manifestul are deja pentru M5 `split_method = 50_50_stratified_by_regime_segment`, `embargo_bars 3000`,
3 segmente de regim. Loaderul **fail-closed** livrează azi:

```
load('M5', split=pre_holdout, cutoff=2025-10-23)
  ->  155.258 bare livrate     2021-07-27 15:45Z .. 2024-06-20 00:40Z
      169.312 sigilate · 22.458 carantina · 3 segmente de discovery
```

Două consecințe:

1. **§8 e deja satisfăcut mai bine decât prin filtru de timestamp.** Poarta există, e manifest-gated și
   fail-closed, iar sub ea **2025+ nu a fost niciodată livrabil** cercetării. `ALPHA_ACCESS_TO_2025_PLUS`
   e **0 pe calea gated** — încălcarea a venit din **ocolirea** porții (citire directă a CSV-ului), nu
   din poartă.
2. **Regiunea cerută de mandat e mai LARGĂ decât cea ratificată**: mandatul vrea până la `2024-12-31`,
   poarta se oprește la `2024-06-20`. Extinderea cu ~6 luni **nu e o formalitate**: cere modificarea
   intervalelor de discovery dintr-un manifest ratificat, cu recalcularea `content_hash` și
   re-ratificare.

---

## 5 — DEVELOPMENT / CALIBRATION (pregătite, NEînghețate)

Nu îngheț splitul cât timp §3 blochează. Îl las pregătit, cronologic, ca să fie gata dacă deblochezi:

```
DEVELOPMENT  2021-07-27 15:45Z -> 2023-12-31 23:55Z
CALIBRATION  2024-01-01 00:00Z -> 2024-12-31 21:55Z   (sau -> 2024-06-20, sub poarta actuala)
```

Granița e **cronologică și rotundă** (schimbarea de an), aleasă înainte de orice rezultat și fără nicio
legătură cu performanța — nu există performanță de consultat. Calibrarea păstrează un an întreg,
suficient pentru robustețe fără să atingă 2025+.

## 6 — CE AR DEBLOCA

Decizia e a ta; enumăr doar variante care nu rescriu tăcut regulile:

1. **Restrângerea sigiliului la ce e cu adevărat nevăzut.** Dacă accepți că N4 a văzut 2025+, sigiliul
   nu mai poate fi „nevăzut" — dar poate fi declarat **`SEALED_FOR_ALPHA_STRATEGY_EVIDENCE`**, cu
   limitarea explicită: **nu poate valida nimic care depinde de pragurile N4**.
2. **Interzicerea explicită a N4 în triggerul M5 al Alpha.** Atunci 2025+ redevine utilizabil pentru
   validarea acelui trigger, iar restricția e verificabilă static.
3. **Re-derivarea pragurilor N4 exclusiv pe `< 2025-01-01`**, sub poarta manifestului. Costă o
   re-ratificare N4, dar curăță regiunea sigilată pentru orice folosință viitoare.
4. **Date M5 noi**, dincolo de `2026-07-27`, acumulate prospectiv.

Recomand (3) dacă vrei un sigiliu cu adevărat curat, sau (2) dacă vrei viteză și acceptarea unei
limitări declarate.

## 7 — CE NU AM FĂCUT

Nu am rulat nicio strategie, nu am inspectat niciun rezultat Alpha, nu am modificat manifestul, nu am
extins poarta la `2024-12-31`, nu am înghețat DEV/CALIB și nu am produs niciun artefact de acces pentru
Alpha. Nu am folosit Dukascopy și nu am sintetizat M5 din M15.

**Proprietar următor: CEO.** Nicio autorizare pentru Alpha M5 entry research, AI Trader sau live.
