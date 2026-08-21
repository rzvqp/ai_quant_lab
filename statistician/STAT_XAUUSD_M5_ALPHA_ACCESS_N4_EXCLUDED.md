# XAUUSD M5 — ACCES ALPHA CU N4 EXCLUS

**Divizia Statistician · `CEO-XAUUSD-M5-ALPHA-N4-EXCLUSION-001` · 2026-08-21**

```
XAUUSD_M5_ALPHA_RESEARCH_EVIDENCE_FROZEN
M5_N4_EXCLUDED_FROM_ALPHA_TRIGGER_RESEARCH
M5_DEVELOPMENT_CALIBRATION_READY
READY_FOR_ALPHA_H1_M5_MULTI_REGIME_DISCOVERY
```

Nicio strategie executată. Manifestul **nu** a fost modificat, poarta **nu** a fost extinsă, N4 **nu** a
fost re-derivat sau atins.

---

## 1 — POARTA RATIFICATĂ, RECUPERATĂ MECANIC

```
load('M5', split=pre_holdout_2025-10-23T09-15-00Z_v1, cutoff=2025-10-23T09:15Z)

  livrate     155.258 bare      sigilate 169.312      carantina 22.458
  segmente de discovery: 3
  prima bara  2021-07-27 15:45:00Z
  CUTOFF      2024-06-20 00:40:00Z          <- capatul EXACT al ferestrei accesibile
  loader      flowA_common_v6_context_derived_2026-07-27
  fisier      OANDA_XAUUSD_M5.csv  sha256 cbb6eebe1a189ebb...
```

Cutoff-ul **nu** a fost preluat din mandat; l-am recuperat din poarta însăși. `2024-06-20 00:40:00Z`
confirmă aproximarea „~2024-06-20". Poarta **nu** a fost extinsă la `2024-12-31`.

## 2 — POPULAȚIILE ÎNGHEȚATE

**DEVELOPMENT**

```
2021-07-27 15:45:00Z  ->  2023-12-29 21:55:00Z        121.949 bare
ohlc_sha256      b30912e130ee0c1c640f29495b2de608403c002609dc2db2413c9960c24ad488
timeline_sha256  2a389cd7a382a02c64073f7c620280b6e098cee9159c6f2496a128e8f9816131
```

**CALIBRATION**

```
2024-01-01 23:00:00Z  ->  2024-06-20 00:40:00Z         33.309 bare
ohlc_sha256      3c170953fd65b5ce49ebbeb92f49c0c88a305f3b8da3d847aefe91bfaaf71deb
timeline_sha256  24e51ef4b128f3758dc1c3f41717b2e1aa43d77d84d124f3c659fedb8b3d700e
```

Granița e **schimbarea de an**, cronologică și rotundă, fixată fără nicio legătură cu vreun rezultat —
la momentul fixării nu există niciunul. `DEV` se termină la `12-29` fiindcă `12-30/31` a fost weekend;
`CALIB` începe la prima bară a anului. Verificări: `DEV + CALIB = 155.258` ✓ · suprapunere **0** ·
bare `>= 2025-01-01` în populația livrată: **0** · bare după cutoff: **0**.

---

## 3 — EXCLUDEREA N4, CU DOVADĂ ȘI CU DOMENIU EXACT

```
N4_M5_TRIGGER_OFF_LIMITS_FOR_ALPHA_DISCOVERY
```

**Dovada contaminării** (din mandatul precedent, `8a5c33e`): terțilele W=3 ale
`code/zone_confirmation.py` au fost derivate din M5 **real**, printr-un script care citește CSV-urile
**brute**, ocolind poarta, cu bucla până la `2026-07-27`.

**Suprafața interzisă, enumerată — nu doar fișierul:**

| element | motiv |
|---|---|
| `code/zone_confirmation.py` · `classify_zone_confirmation` | sursa pragurilor contaminate |
| pragurile W=3 existente și orice `ZoneConfirmationResult` derivat din ele | output contaminat |
| `ConfirmationSlot.confirmation` din `code/market_bus.py` | **cale tranzitivă** — `market_bus` importă N4 la linia 40 și îl populează la 266 |
| descriptorul `confirmation` atașat în `decide()` (liniile 180/187) | N4 **călătorește** în `AuditedDecision` ca dovadă atașată |
| `code/shadow_run.py`, serializarea `s.confirmation` (linia 63) | N4 apare în output-ul shadow |

★ **Ce am verificat mecanic, nu am presupus.** `market_bus._inputs_hash_n1n2n3` (linia 149) **exclude
explicit N4**, cu motivul scris în cod: *„Dacă N4 ar intra aici, ceasul ar aluneca"* — iar codul chiar
face ce spune comentariul: hash-ul se calculează doar peste `regime`, `bias`, `zones` (N1/N2/N3).
`decide()` **nu condiționează** pe N4; îl transportă doar ca descriptor de audit.

**Consecință practică, verificabilă static:** Alpha poate folosi `market_bus` **cu
`confirmations = ()`** — linia 180 tratează explicit cazul gol — și atunci N4 nu e nici apelat, nici
populat, nici atașat. Regula operațională e deci: **nu apela `classify_zone_confirmation`, nu popula
`ConfirmationSlot`, nu citi descriptorul `confirmation`.**

**Statutul canonic al N4 în altă parte rămâne neschimbat.** Interdicția e strict pentru ramura de
cercetare a triggerului M5.

## 4 — AUDITUL CELORLALTE FEATURE-URI (§5)

Am căutat, pe suprafața accesibilă căii de cercetare, **clasa de defect care a contaminat N4**:
scripturi care citesc fișierele de piață **brute**, ocolind poarta manifestului.

```
grep  read_csv("data/market...  peste  code/  +  scratch_verify/
  ->  UN SINGUR fisier: scratch_verify/measure_n4_w3_tertiles.py    (deja exclus)
```

Modulele cu praguri „re-derivate" de aceeași natură — `bias_h1.py` (H1) și `regime_classifier.py`
(H4, `COMPRESSION_WINDOW` re-derivat la W=30) — **nu conțin citiri de fișiere brute**; constantele lor
sunt declarate în modul. Sunt pe calea `H1 EDGE + H4 context`, deci le-am verificat tocmai fiindcă
sunt relevante, nu le-am sărit.

**O a doua constatare, semnalată fără a bloca:** `scratch_verify/shadow_driver.py` citește tot brut și
pășește deliberat prin **coada** datelor (`m5 = load("OANDA_XAUUSD_M5.csv")`, până în 2026). E un driver
de observație prospectivă, **nu** derivează parametri — dar a *văzut* 2025+. Îl marchez
`OFF_LIMITS_FOR_M5_ALPHA_DISCOVERY` din precauție, fiindcă nu costă nimic și elimină o cale de
scurgere.

Nu am auditat exhaustiv sisteme fără legătură, conform §5.

## 5 — INFORMAȚIA M5 PERMISĂ

În interiorul populației gated: OHLC, timestamp, sesiune/oră, volatilitate calculată **cauzal**,
structura brută de preț, geometrie de breakout/retest, higher-low / lower-high, displacement,
acceptare, compresie/expansiune, mișcare eșuată, sweep/rejecție.

**Condiție fermă:** orice feature sau prag derivat trebuie construit **exclusiv din DEVELOPMENT**
(`b30912e1…`). `CALIBRATION` se folosește pentru robustețe, **nu** pentru alegerea pragurilor. Niciun
parametru derivat din `>= 2024-06-20` sau din 2025+ nu poate intra pe calea de cercetare.

## 6 — STATUTUL 2025+ (formulat exact cum ai cerut)

```
ALPHA_STRATEGY_OUTCOME_UNCONSUMED
BUT
STRUCTURAL_FEATURE_PARAMETERIZATION_CONSUMED_BY_N4
ALPHA_ACCESS = ZERO
```

Nu îl descriu ca `OUTCOME_UNSEEN` — nu este, și am refuzat formularea comodă și în mandatul precedent.

## 7 — DOVADA CĂ ALPHA NU POATE TRECE DE POARTĂ

Calea de acces e **una singură**: `edge_research._common.load('M5', data_split_id=…, cutoff=…)`,
fail-closed pe (a) `content_hash`-ul manifestului, (b) status `VALIDATED`, (c) SHA-256-ul fișierului de
date. Măsurat pe populația livrată: **0 bare `>= 2025-01-01`**, **0 bare după `2024-06-20 00:40Z`**.

★ Poarta n-a fost niciodată încălcată **prin ea însăși** — singura scurgere a venit din **ocolire**,
prin citirea directă a CSV-ului. De aceea regula operativă pentru Alpha e: **niciun `read_csv` pe
`data/market/`**; exclusiv loaderul gated. Asta e verificabil static, cu un singur `grep`, exact cum
am detectat contaminarea N4.

## 8 — PREDAREA CĂTRE ALPHA

Arhitectura vizată: `H1 PRIMARY EDGE` + context H4 opțional + structură M15 opțională → **M5 = strat de
intrare/trigger**. Regimuri permise: `TREND_UP`, `TREND_DOWN`, `RANGE`, `TRANSITION`,
`REGIME_INDEPENDENT`. Profilurile economice (A: 70–80% WR la 1:1,5–2; B: 45–55% WR la 1:3–4; țintă
preferată `>= 70–80` pips de proiect, `10 pips = 1,00 USD`) sunt **obiective de cercetare**, nu praguri
de acceptare — acest mandat nu face cercetare de strategie și nu evaluează nimic.

**Ce primește Alpha:** loaderul gated, cele două populații de mai sus cu hashurile lor, lista de
excluderi de la §3–§4, și regula „fără `read_csv` pe `data/market/`".

---

*Nicio autorizare pentru AI Trader, Strategy Catalog, LIVE_SHADOW, broker sau tranzacții. `ALPHA_ACCESS_TO_2025_PLUS = 0`.*
