# STATISTICIAN — FORMALIZAREA MATEMATICĂ A CELOR 20 FAMILII SMC_S* (Mandat 3.18)

**Document ID:** STAT-SMC-STATE-MACHINES-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician

Verdictul de la Mandatul 3.17 rămâne acceptat integral, fără reluare aici.

---

## CORECȚIA DE SCOP — 20, nu 15

Confirmat direct în `code/mstrat.py` (`ECON` dict): S1-S20 din grila legacy sunt exact:

S1 liquidity-sweep mean-reversion · S2 failed-breakout fade · S3 breakout-retest momentum · S4 volatility-regime expansion · S5 opening-range momentum · S6 session-transition momentum · S7 trend-pullback continuation · S8 extension mean-reversion · S9 MTF-trend momentum · S10 displacement continuation · S11 structure-break reversal · S12 range rotation · S13 imbalance fill · S14 momentum exhaustion · S15 trend acceleration · S16 previous-day levels · S17 weekly levels · S18 time-of-day · S19 session gap · S20 hybrid sweep+MTF.

Documentul de la Mandatul 3.17 avea 5 dintre acestea (S1/S2/S3/S13/S16) doar ca **nomenclator** (opt mențiuni, nicio mașină de stare) — confirmat, corect semnalat. Sarcina de față formalizează **toate cele 20**.

## O NEPOTRIVIRE DE INSTRUMENT, SEMNALATĂ ÎNAINTE DE EXECUȚIE

Ordinul cere înregistrare în `validation_engine/capabilities.json` sub v2.5.8. **Am citit fișierul direct înainte de a scrie orice în el.** Câmpul lui propriu `deliberately_absent` spune, verbatim: *"Hypothesis-specific event primitives (sweep_reject, liquidity_grab, compression)"* și *"Predefined session definitions (NY/London/Asia)"* sunt **deliberat excluse din design** — registry-ul e o gramatică generică de primitive statistice (`test_methods`, `variable_primitives`, `population_predicates` — `atr@v1`, `crosses@v1`, `sequence@v1` etc.), nu un loc pentru ipoteze specifice precum sweep-reject sau FVG. A înregistra 20 de familii SMC_S* acolo ar încălca exact principiul de design pe care fișierul îl declară singur.

**Nu forțez.** Înregistrez cele 20 unde am autoritatea de proiectare și unde s-a înregistrat tot ce ține de LM-001/MK-03/MK-04 până acum — `config/split_manifest.json`, incrementat la **v2.5.8** pe `alpha-automation-v1` (aceeași schemă de versionare, consecventă). Semnalez nepotrivirea explicit, nu o ascund — dacă se dorește extinderea reală a lui `capabilities.json` cu primitive HIPOTEZĂ-AGNOSTICE (ex. un `structural_sweep@v1` generic, reutilizabil de orice ipoteză, nu specific SMC_S1), aia e o decizie separată, mai mare, de proiectare a registry-ului VE — nu ceva ce fac acum silențios.

## ȘABLONUL COMUN — cadrul de risc Open-R (identic tuturor celor 20)

```
R_i = (spike_i + 2 pips) × TICK(0,10$), NICIODATĂ lărgit
filtru eligibilitate: spike_i ∈ [10,1 ; 65,0) pips
net_R_i = direcție_i × (preț_ieșire − preț_intrare) / R_i − cost/R_i, cost = 0,40$
```
Podeaua (10,1 pips) e portabilă (derivată din cost/R, comună construcției). Plafonul (65 pips) rămâne PLACEHOLDER per familie, cf. Mandatului 3.17, până la propriul audit de geometrie.

## GOLUL ARITMETIC PE ORIZONTURI — închis prin grupare declarată, nu prin forțare

Patru constante de sesiune nu pot produce 20 de orizonturi distincte. Închid prin **patru grupuri declarate**, fiecare cu sursă proprie, nu o singură derivare forțată:

- **GRUPA A — reacție imediată, 20 bare** (reutilizat verbatim din derivarea LM-001, Mandat 3.13: `_profile.HORIZONS` legat de durata sesiunii london=5h=20 bare M15). Pentru familii al căror declanșator e un eveniment PUNCTUAL (sweep, BOS, CHoCH, formare FVG) și a căror întrebare e reacția imediată.
- **GRUPA B — durata proprie a sesiunii declanșatoare**, din cele patru constante deja stabilite (`code/mtf.py:37-38`): asia (<8h UTC) = 8h = **32 bare**; london = 5h = **20 bare**; ny = 8h = **32 bare**; late = 3h = **12 bare**. Pentru familii al căror declanșator E o sesiune anume.
- **GRUPA C — durata empirică a perioadei de nivel**, NUMĂRATĂ direct (nu asumată), exact disciplina deja scrisă în `institutional_levels.py` ("92 e doar cea mai frecventă valoare... nu o constantă"). **Am calculat-o eu direct** pe cele 130.491 bare de descoperire, cu ancora 17:00 NY deja stabilită: **zi = mediană 92 bare** (medie 91,9; mod 92 — confirmă exact discuția din cod); **săptămână = mediană 460 bare** (medie 451,5; mod 460), aplicând regula deja ratificată de gol-de-weekend pentru `derive_week_index`, confinat pe cele 3 blocuri (D4). Pentru familii ancorate la PDH/PDL/Weekly.
- **GRUPA D — negrupabil, primitivă lipsă.** Pentru familii a căror mecanică cere ceva ce NU e în cele patru module ratificate. Marcate explicit mai jos, nu forțate.

---

## CELE 9 FAMILII COMPLET FORMALIZABILE (pe cele 4 primitive ratificate)

### SMC_S1 — Liquidity Sweep Reversal ≡ LM-001 (deja specificat, referință nu redervare)
Primitive: `liquidity_mechanics` (D6 wick-sweep, D7 consumare) + `market_structure` (bazine din swing-uri). Intrare next-open, direcție mecanică. **Orizont: GRUPA A (20 bare)** — deja derivat. Populație: 21.048 evenimente `[10,1;65,0)` (Mandatele 3.13/3.17). Test: `net_R` mediu > 0, unilateral. Familie=1. `n≥25` per regim.

### SMC_S2 — Failed Breakout / Failed Sweep
Primitive: `market_structure` (BOS pe corp, CHoCH). **Mecanică:** BOS la bara `b` în direcția D (închidere dincolo de un swing CLASIFICAT) → un CHoCH (rupere structurală opusă) survine în ≤20 bare (GRUPA A, reutilizat ca fereastră de calificare) → intrare next-open după bara CHoCH, direcție = OPUSĂ BOS-ului inițial (fade). Fără CHoCH în fereastră → eveniment neeligibil (BOS "a ținut", nu exclus ca eșec separat, exclus din populație). **Prag:** spike = distanța de la intrare la extremul nivelului BOS spart + 2 pips. **Populație:** BOS-uri urmate de CHoCH calificat pe M15_v2 descoperire, minus filtrul `[10,1;65,0)`. **Orizont: GRUPA A (20 bare)**, atât fereastra de calificare cât și cea de măsurare. Test/familie/n identic șablonului S1.

### SMC_S3 — Breakout Retest Continuation
Primitive: `market_structure` (BOS) + asimetria D6 (fitil/închidere) reaplicată pe nivelul BOS-ului însuși. **Mecanică:** BOS la bara `b` în direcția D → o bară ulterioară ATINGE nivelul spart (fitil ajunge la nivel) în ≤20 bare, DAR ÎNCHIDEREA acelei bare rămâne de partea breakout-ului (nu se închide înapoi) → intrare next-open, direcție = ACEEAȘI ca BOS (continuare). **Distincție mecanică față de S2:** o bară de retest nu poate simultan închide-prin (S2) și nu-închide-prin (S3) — populațiile nu se suprapun pe ACEEAȘI bară de retest, chiar dacă pot porni din același BOS. **Prag:** spike = distanța de la intrare la nivelul retestat + 2 pips. **Orizont: GRUPA A (20 bare)**. Șablon identic altfel.

### SMC_S7 — Trend-Pullback Continuation
Primitivă: `market_structure` (secvență ≥2 swing-uri CLASIFICATE de aceeași direcție — HH+HL sau LH+LL). **Mecanică:** odată stabilit trendul (≥2 swing-uri consecutive), următorul swing ÎL CONTINUĂ (nou HL mai sus/LH mai jos, fără CHoCH declanșat) → intrare next-open după `confirmed_idx` al noului swing, direcție = trendul stabilit. **Prag:** spike = distanța de la intrare la noul extrem de swing + 2 pips. **Orizont: GRUPA A (20 bare)**, implicit — fără o derivare specifică familiei, declarat ca atare, nu ascuns.

### SMC_S10 — Displacement Continuation (redefinire declarată)
**Substituție transparentă:** conceptul legacy „displacement" (bară de range >1,5×ATR) foloseau ATR, în afara celor 4 module ratificate. Substitui cu `market_structure`-ul propriu: un BOS (deja o rupere direcțională decisivă prin închidere) JOACĂ rolul de „displacement" aici. Cititorul poate respinge substituția dacă o consideră prea departe de concept — semnalată, nu ascunsă. **Mecanică:** BOS confirmat → intrare next-open, direcție = BOS, testează CONTINUAREA (nu fade-ul, spre deosebire de S2). **Prag:** spike = distanța la nivelul BOS + 2 pips. **Orizont: GRUPA A**.

### SMC_S11 — Structure-Break Reversal
Primitivă: `market_structure` (CHoCH, ca semnal PRIMAR, nu ca urmare a unui BOS eșuat recent — distincție explicită față de S2). **Mecanică:** CHoCH survine la finalul unei secvențe de trend stabilit → intrare next-open după `confirmed_idx`-ul CHoCH, direcție = NOUA direcție (opusă trendului anterior). **Prag:** spike = distanța la extremul CHoCH-ului + 2 pips. **Orizont: GRUPA A**.

### SMC_S13 — Liquidity Void / Imbalance Fill (deja nomenclator, acum mașină de stare)
Primitive: `imbalance_mechanics` (`detect_fvgs`, `ce50_touch_idx` = punctul de consumare D7, `detect_fvg_reactions`). **Mecanică:** FVG se formează → atingere CE-50 (fitil, consumare D7) → intrare next-open după bara de atingere, direcție = ÎNAPOI spre direcția ORIGINALĂ a FVG-ului (pariu pe respectarea golului ca suport/rezistență). **Prag:** spike = distanța de la intrare la CE-50 + 2 pips. **Orizont: GRUPA A (20 bare)**.

### SMC_S16 — Previous Day Levels (deja nomenclator, acum mașină de stare)
Primitive: `institutional_levels` (`compute_prior_day_levels`, `detect_level_touches` — deja consumare D7 implementată). **Mecanică:** PDH/PDL disponibil (Q4) → atingere prin fitil (deja implementată, consumată la prima atingere) → intrare next-open, direcție = ÎNSPRE DEPĂRTARE de nivel (respingere, analog S1 dar pe niveluri instituționale nu bazine din swing). **Prag:** spike = distanța la PDH/PDL + 2 pips. **Orizont: GRUPA C — 92 bare** (mediană empirică zilnică, calculată direct mai sus, nu asumată).

### SMC_S17 — Weekly Levels
Primitivă: `institutional_levels` (`compute_prior_week_levels`, D-WEEK). **Mecanică:** identică S16, pe Weekly H/L. **Restricție obligatorie:** doar nivelurile `COMPLETE` (≥5 zile) intră în populația PRIMARĂ — cele `PARTIAL` se exclud din populația principală (disclosed separat, nu pool-ate silențios, cf. D-WEEK). **Orizont: GRUPA C — 460 bare** (mediană empirică săptămânală, calculată direct, aceeași regulă de gol-de-weekend).

---

## CELE 11 FAMILII CU PRIMITIVĂ LIPSĂ SAU NATURĂ DIFERITĂ — marcate, nu forțate

**„Goluri ieftine" (extensie aproape mecanică a unui tipar deja existent, nu o clasă nouă de primitivă):**
- **SMC_S5 — Opening-Range Momentum:** lipsește un calcul „high/low al primelor K bare de sesiune" — nu există în niciunul din cele 4 module (nici `institutional_levels`, care face doar zi/săptămână, nu interval-de-deschidere). Extensie directă a tiparului `institutional_levels`, neimplementată încă.
- **SMC_S6 — Session-Transition Momentum:** lipsește „high/low al sesiunii ANTERIOARE" (analog PDH/PDL dar pe sesiune, nu zi) — aceeași lipsă ca S5, extensie a aceluiași tipar.
- **SMC_S19 — Session Gap:** lipsește „preț de deschidere/închidere al sesiunii" — aceeași familie de lipsă ca S5/S6.

**Goluri reale (clasă de primitivă genuin absentă din cele 4 module):**
- **SMC_S4 — Volatility-Regime Expansion:** cere un clasificator de regim de volatilitate. Există conceptual în Baza de Cunoștințe a lab-ului (Volatilitate = PRIMITIVĂ PROMOVATĂ) dar NU e implementat în niciunul din cele 4 module de cod ratificate aici.
- **SMC_S8 — Extension Mean-Reversion:** cere o distanță relativă la ATR. ATR există și e deja folosit în cod (`alpha_lab.py`, `mstrat.py`) dar NU face parte din cele 4 module ratificate — gol mai mic decât S4/S9/S14 (feature-ul există deja în lab, doar nu în acest set).
- **SMC_S9 — MTF-Trend Momentum:** cere trend multi-timeframe (H1/H4/D1) — niciun modul ratificat nu produce clasificare de trend cross-timeframe.
- **SMC_S14 — Momentum Exhaustion:** cere un indicator de tip ROC/RSI — absent din cele 4 module.
- **SMC_S15 — Trend Acceleration:** cere o măsură de accelerație swing-la-swing — `market_structure` detectează swing-uri dar nu calculează rate-of-change între ele.
- **SMC_S20 — Hybrid Sweep+MTF:** depinde explicit de aceeași lipsă MTF ca S9.

**Parțial gol (mecanica de bază există, dar o componentă structurală lipsește):**
- **SMC_S12 — Range Rotation:** mecanica sweep-reject (D6/D7) există la fiecare capăt, DAR lipsește o primitivă de „pereche de bazine care delimitează un range stabil" — orice două bazine apropiate NU înseamnă automat un range coerent. Fără această pereche-declarată, aș forța o definiție arbitrară — nu o fac.

**Natură diferită, nu o familie de sine stătătoare:**
- **SMC_S18 — Time-of-Day:** legacy S18 era deja o DIMENSIUNE de stratificare (oră/sesiune aplicată peste ALTE semnale), nu un declanșator propriu — confirmat, era exact tiparul „3 semnale × 2 ieșiri" deja documentat la Mandatul 3.10. Recomand: S18 NU devine a 20-a ipoteză independentă — rămâne o stratificare (asia/london/ny/late, deja aplicată la S1/LM-001) aplicată în raportare la CELELALTE familii, nu un declanșator propriu.

## DEDUBLAREA — obligatorie înainte de înrolare, aplicată conceptual acum, mecanic mai târziu

Nu există încă cod/tranzacții pentru nicio familie (`AWAITING_VALIDATION_ENGINE_CODE`) — pre-screening-ul D11/§F (hash pe jurnalul de tranzacții) nu poate rula încă mecanic. Semnalez totuși, ACUM, perechile cu risc conceptual de coliziune, ca VE să verifice mecanic imediat ce hash-urile există, nu ca să presupun rezultatul:

- **S2 vs S11** — ambele folosesc CHoCH. Diferențiate deliberat (S2 cere BOS-eșuat-recent specific; S11 cere doar CHoCH la finalul unui trend stabilit) — dar ambele rulează pe ACELAȘI cod `market_structure`, risc real de suprapunere parțială a evenimentelor detectate. **Verificare hash obligatorie la implementare.**
- **S3 vs S7** — ambele „continuare", diferite condiții de declanșare (S3 cere BOS explicit + retest; S7 cere trend stabilit + swing următor, fără BOS nou) — la fel, cod comun, verificare obligatorie.
- **S1/S13/S16** — toate trei „sweep-reject", pe entități diferite (bazin din swing / CE-50 FVG / nivel instituțional) — geometric distincte prin construcție (bazine vs FVG vs PDH/PDL sunt structuri diferite), risc de coliziune mai mic, dar tot verificabil mecanic, nu asumat.

**Raport (obligatoriu conform D11/§F, NU un număr încă disponibil):** N ID brut va fi cel puțin 9 (cele formalizate) × variante de parametri (direcție mecanică nu multiplică, dar orice grilă viitoare de praguri/orizonturi ar putea). N distinct NU poate fi raportat înainte ca VE să genereze jurnale de tranzacții reale — orice cifră acum ar fi presupunere, nu măsurătoare. Regula D11/§F (hash SHA-256 pe `entry_epoch,exit_epoch,R`, ID canonic = cel mai mic lexicografic, raportare duală brut/distinct) rămâne mandatorie ÎNAINTE de orice înrolare pentru testare.

---

**Stare pentru toate cele 9 formalizate: `AWAITING_VALIDATION_ENGINE_CODE`. Cele 11 rămase: `GAPPED` (primitivă lipsă) sau `NOT_A_STANDALONE_FAMILY` (S18). Nicio familie nu trece în `VALIDATED` până când WP-5' nu livrează oracolul (Mandatul 3.17).** Holdout SEALED, neatins. Niciun backtest rulat.

**Înregistrat în `config/split_manifest.json` (NU `capabilities.json`, cf. secțiunii de mai sus), incrementat la v2.5.8 (commit `74de879`, `alpha-automation-v1`).**
