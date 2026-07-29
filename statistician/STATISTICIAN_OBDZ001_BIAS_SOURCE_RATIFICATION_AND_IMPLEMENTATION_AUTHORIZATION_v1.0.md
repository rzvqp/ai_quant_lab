# STATISTICIAN — RATIFICAREA SURSEI DE BIAS ȘI AUTORIZAREA IMPLEMENTĂRII OBDZ-001

**Document ID:** STAT-OBDZ001-BIAS-SOURCE-RATIFICATION-IMPLEMENTATION-AUTHORIZATION-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

**Verificare de sursă, nu doar acceptarea auto-corecției VE:** citit direct `code/mtf.py:29-38` (`load_mtf()`) — confirmă exact ce a semnalat VE: citește `OANDA_XAUUSD_H4.csv`/`H1.csv`/`D1.csv` prin `pd.read_csv` BRUT, fără `load()`, fără `data_split_id`, fără `cutoff` — zero mascare de holdout. Confirmat în manifest: timeframe-ul `H1` nativ are status **`AWAITING_REGIME_MAP`** (fără hartă de regim = 100% sigilat, exact cum a spus VE), în timp ce `H1_from_M15_v2`/`H4_from_M15_v2`/`D1_from_M15_v2` (`context_derived_htf.entries`) sunt toate **`CONTEXT_DERIVED_VALIDATED`**. Citit `code/task_obdz_population.py` integral — confirmă exact ce a raportat VE: `_htf_trend()` calculează `ema20>ema50` (formula identică `mtf.py:_ind`) pe `dfh1`/`dfh4` încărcate via `load("H1_from_M15_v2"/"H4_from_M15_v2", data_split_id=PRE_HOLDOUT_SPLIT_ID, cutoff=RESEARCH_HOLDOUT_CUTOFF_UTC)` — ACEEAȘI cale discovery-safe folosită peste tot în acest lab. Merge forward-safe verificat identic: `avail=time.shift(-1)`, ultima bară `+period` — exact convenția deja existentă în `mtf.py:_htf_feat` însuși, aplicată acum sursei sigure. Verificat `_first_mitigation` linie cu linie contra `_scan_reactions`/`_breaker_stop` (post-fix, `formation_idx+2`) — logic identică (verificare de breaker înainte de atingere, în aceeași buclă, echivalent matematic cu pre-calcularea `stop` și scanarea până acolo). `mypy --strict` curat pe `order_flow.py`+`task_obdz_population.py`; `test_order_flow.py` 15/15 (a crescut de la 14, testul nou pentru bara de impuls confirmă zero reacții la impuls + o atingere legitimă rămâne detectată). **Rulat direct** `code/task_obdz_population.py` — toate cifrele reproduse exact (35.454/37.707/17.145 → 2.275/2.107/1.178 → 275/223/156 → 261/194/154; orizont sub-10: 6/10/8, peste-10: 255/184/146; ATR median la supraviețuitori: 2,11/1,346/2,203).

---

## RATIFICARE — calea de bias, amendament formal la specificație

**Confirm: VE a găsit o scurgere REALĂ, nu o falsă alarmă, și a rezolvat-o corect.** Referirea specificației mele (`h1_trend_up`/`h4_trend_up` „există în `code/mtf.py`") era ambiguă asupra CĂREI căi de încărcare să fie folosită — citind literal spre `mtf.py`, un implementator ar fi ajuns natural la `load_mtf()`, care citește CSV-urile native, complet nemascate. Nu era o eroare de raționament în sensul unui calcul greșit — era o referință de cod scrisă înainte ca arhitectura de mască discovery/embargo/sealed să existe pentru H1/H4 (native H1 e încă `AWAITING_REGIME_MAP`, niciodată nu i s-a atribuit o hartă de regim). Dacă VE ar fi urmat acea cale literal, bias-ul întregii ipoteze ar fi venit din date 100% sigilate — o contaminare reală, nu ipotetică.

**Ratific: calea context-derivată e cea corectă. Specificația se amendează** — sursa de bias pentru OBDZ-001 este **`ema20>ema50` (formula `mtf.py`, neschimbată) aplicată pe `H1_from_M15_v2`/`H4_from_M15_v2`** (livrate discovery-safe de loader, `CONTEXT_DERIVED_VALIDATED`), NU pe `mtf.py::load_mtf()`'s cale nativă. **NU am intenționat H1 nativ** — chiar dacă aș fi intenționat-o, ar fi imposibil discovery-safe (100% sigilat), deci întrebarea CEO are un singur răspuns valid, nu o alegere reală.

### Verificare de proces — alte locuri riscante în specificații: NU, doar aceeași ipoteză, plus un cluster legacy identificat separat

Am căutat exhaustiv toate documentele Statistician pentru referințe la `mtf.py`/`load_mtf`/`h1_trend_up`/`h4_trend_up`. **Toate celelalte referințe la `mtf.py`** (în `STATISTICIAN_LM001_GEOMETRY_AUDIT...`, `STATISTICIAN_MODULE5_6_7_PARAMETERS...`, `STATISTICIAN_SMC_S_STATE_MACHINES...`, `STATISTICIAN_WP5_Q1_DEFINITIONS...`) **citesc DOAR constantele de sesiune** (`asia<8h/london<13h/ny<21h/late`) — aritmetică pură pe ora UTC a barei M15 proprii, ZERO dependență de fișiere H1/H4/D1. Niciun risc acolo. **Singurele referințe riscante** erau cele la `h1_trend_up`/`h4_trend_up` din documentele PROPRII acestei ipoteze (`STATISTICIAN_COST_CONSTANT_CORRECTION...` și `STATISTICIAN_COMPOSITE_HYPOTHESIS_FORMAL_PREREGISTRATION...`) — aceeași ambiguitate, repetată de mine de-a lungul evoluției aceleiași ipoteze, nu o instanță nouă găsită într-o ipoteză diferită.

**Descoperire suplimentară, dincolo de ce a cerut CEO — un cluster legacy separat care folosește ACTIV calea nesigură:** am căutat în tot `code/` cine mai apelează `load_mtf()` sau citește direct CSV-urile H1/H4/D1 native. Găsit: **`code/s1.py:11` (`d=M.load_mtf()`) și `code/run_mtf.py:108` (`m15=M.load_mtf()`)** — apeluri REALE, nu doar referințe în comentarii. Verificat critic dacă acestea afectează vreun verdict deja emis: **NU** — `code/s1.py` e un modul COMPLET SEPARAT și mai vechi (`load_s1`, `generate`, `backtest`, `_pool`, `analytic_p` — un motor de căutare/genetic exploratoriu, pre-dating arhitectura `market_structure`/`liquidity_mechanics`/`order_flow`), distinct de `code/trading_strategies.py::detect_s1` (funcția REALĂ folosită de `task2_cost_rerun.py` și `lm001_s1_execution.py`, pe care se bazează verdictul SMC_S1 STATISTICALLY REJECTED) — verificat direct: `trading_strategies.py` importă doar din `market_structure`/`liquidity_mechanics`/`imbalance_mechanics`/`institutional_levels`, zero `mtf`. **Niciun verdict ratificat până acum se bazează pe calea nesigură.** Notez și că `code/wave1_harness.py:92` citește `h4_trend_up` dintr-o sursă nespecificată aici — probabil ACELAȘI cluster legacy; e relevant că `test_wave1_harness.py` conține 2 din cele 4 eșecuri pre-existente confirmate identic la fiecare mandat de generare a manifestului — consistent cu un modul vechi, nemigrat, nu întreținut activ.

**Recomandare de guvernanță, nu o corecție pe care o fac eu:** `code/s1.py`, `code/mstrat.py`, `code/run_mtf.py`, `code/wave1_harness.py` ar trebui etichetate explicit ca **LEGACY PRE-MASCĂ — A NU SE FOLOSI PENTRU IPOTEZE RATIFICATE**, exact pentru a preveni recurența acestui scenariu (aproape s-a întâmplat aici, prin propria mea citare ambiguă). Semnalez pentru CEO/Architect — nu o implementez eu, e o decizie de organizare a codului, nu de statistică.

---

## Reconfirmarea specificației OBDZ-001 — neschimbată, cu bias-ul amendat

```
bias           ema20>ema50 pe H1_from_M15_v2 ȘI H4_from_M15_v2 (context-derived, discovery-safe),
               consistente (ambele up / ambele down) — AMENDAMENT: nu mtf.py::load_mtf (nativ, sigilat)
intrare        M15, în direcția bias-ului, DemandZone x OB nemitigat, cross-candle (specificat mecanic,
               v2.7.10)
SL             0,7 x ATR(14)
TP1            1,4 x ATR -> închide 75%, apoi breakeven
TP2            2,1 x ATR -> restul de 25%
plasă          min(entry+20, EOD)
eligibilitate  doar podeaua de ATR ($0,857), fără plafon
familia        1, separată de familia-8 (SMC_S1 + cele 7)
variabila      net_R
test           WP-5' block_bootstrap, L>=28
```

**Neschimbat față de v2.7.10 în afara amendamentului de bias.** Toate celelalte decizii (Deciziile 1-6 din mandatul anterior) rămân exact cum au fost ratificate.

## Pragul de winrate — recalculat pe ATR-ul REAL al supraviețuitorilor, nu se îngustează la un punct, precizat

**Verificare, nu doar acceptare a cifrei „34-36%":** recalculând `w*=(1+cost/R)/3,25` pe **medianele** ATR ale supraviețuitorilor (2,11/1,346/2,203, exact cifrele reproduse): `cost/R` = 13,5%/21,2%/13,0%, deci **w*≈34,9%/37,3%/34,8%** — un interval de **~[35%,37%]**, nu [34%,36%]. Recalculând pe **mediile** ATR (2,447/1,555/2,573, de asemenea reproduse exact): `cost/R`=11,7%/18,4%/11,1%, **w*≈34,4%/36,4%/34,2%** — interval **~[34%,36%]**, care se potrivește cu cifra CEO.

**Discrepanța explicată, nu ascunsă:** distribuția ATR e asimetrică la dreapta în toate cele trei regimuri (media > mediana peste tot — bear 2,447>2,11, bull 1,555>1,346, corecție 2,573>2,203), deci media e trasă în sus de câteva bare de volatilitate extremă, ceea ce face `cost/R` să pară MAI MIC și pragul de winrate MAI OPTIMIST decât e reprezentativ pentru tranzacția tipică. **Recomand mediana ca reper de interpretare** (~35-37%, nu 34-36%) — mai robustă la coadă, mai reprezentativă pentru ce experimentează majoritatea tranzacțiilor eligibile.

**Dar — subliniez din nou, aceeași regulă stabilită la Mandatul 3.13: niciun prag unic de winrate nu e CRITERIUL de test.** Testul pre-înregistrat e `H0: medie(net_R)<=0`, calculat direct per-tranzacție cu R-ul PROPRIU al fiecărei tranzacții, nu o comparație contra unui singur prag de winrate agregat — orice cifră de „prag" de mai sus e un AJUTOR INTERPRETATIV, nu regula de decizie. **Da, la interpretare, un winrate de 33% s-ar citi ca respins (sub orice punct din intervalul 35-37%), nu marginal** — dar decizia FORMALĂ vine din testul de bootstrap pe `net_R`, nu din compararea unui winrate observat cu acest interval.

---

## AUTORIZAREA IMPLEMENTĂRII — DA, cu scopul precizat

**Autorizez implementarea mașinii de stare și rularea testului statistic complet pe OBDZ-001.** INSUFFICIENT_N nu se declanșează în niciun regim (261/194/154, toate ≥10x pragul de 25). Îngrijorarea mea despre orizontul variabil nu s-a materializat — peste 95% din supraviețuitori primesc orizontul complet de 20 de bare (255/261=97,7%, 184/194=94,8%, 146/154=94,8%), confirmând că ipoteza măsoară exact ce pretinde, nu un artefact de trunchiere la finalul zilei.

**Scop explicit:** VE implementează mașina de stare COMPLETĂ (bias→intersecție cross-candle→SL/TP1/TP2 ATR→ieșire parțială→`net_R`) și rulează testul WP-5' `block_bootstrap` (L≥28, H0: medie(net_R)≤0, family=1) **STRICT pe cele 130.491 bare de descoperire M15_v2** — holdout-ul rămâne SIGILAT, neatins, exact ca la orice alt test din acest lab. Diagnosticele obligatorii deja specificate (stratificare pe sesiune și pe bucket de orizont) se raportează ODATĂ CU rezultatul, nu separat/opțional.

---

**GARD 1 rămâne True (raportat de VE, consistent cu deblocarea deja confirmată). GARD 2 neatins. Sigilatul intact — nimic din acest document sau din numărătoarea de populație a atins vreodată datele sigilate.**

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.11 (commit `f782f0d`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
