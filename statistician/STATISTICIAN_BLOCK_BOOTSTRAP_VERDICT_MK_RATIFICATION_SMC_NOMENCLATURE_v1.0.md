# STATISTICIAN — VERDICT block_bootstrap@v1, RATIFICARE MK-03/MK-04, NOMENCLATOR SMC_S* (Mandat 3.17)

**Document ID:** STAT-BLOCKBOOTSTRAP-MK-SMC-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician

**Verificare de sursă:** citit direct `edge_research/LM001_DENSITY_AND_CURVE_REPORT.md`, `edge_research/lm001_density_audit_results.json`, `edge_research/lm001_s8/lm001_s8_curve_completion.json` (commit `e441bcf`) — toate cifrele citate în mandat confirmate exact, inclusiv suma histogramei de grad (21.054, recalculată independent din JSON) și media ponderată a gradului (7,6408, identică cu `degree_mean` raportat). Citit integral `code/imbalance_mechanics.py` și `code/institutional_levels.py` la commit `1930467` — nu doar raportul (cerut explicit). Verificat direct `PROJECT_AUDIT.md` D11/§F în `ai_quant_lab` (nu în `alpha-automation`, unde fișierul nu conține secțiunea) — cifrele 27,0%/87% confirmate exact.

---

## PROBLEMA DE ORDINE — consemnată, exact cum ai cerut

Mi s-a cerut la mandatul anterior să derivez maparea densitate→φ ÎNAINTE de a vedea densitatea măsurată. Nu am apucat. Primesc acum densitatea (8,64 concurente, grad 7,64) și curba (φ=0,50 nominal, φ=0,60 anti-conservator) în același mesaj. **Orice mapare pe care o scriu acum nu poate fi demonstrată independentă de rezultat — la fel ca ratificarea codului pe care nu-l citisem, corecția 8→6, extinderea criteriului de certificare. Consemnat ca atare, nu ascuns.**

Dar problema de ordine nu e singurul motiv pentru care nu produc o mapare — mai jos.

## SARCINA 1 — verdictul: `block_bootstrap@v1` → **INVALIDATED_FOR_THIS_SCALE**, WP-5' activată

**Nu produc o mapare densitate→φ pe curba AR(1) existentă — nu doar din cauza problemei de ordine, ci pentru un motiv structural mai profund, pe care îl formulez acum, nu doar îl accept:**

Formula ta (`(20-6,2)/20 = 69%`) e corectă — e rezultatul clasic pentru autocorelația de ordinul 1 a unor sume pe ferestre suprapuse dintr-un proces cu increment i.i.d. (`ρ₁ = (k-m)/k`, k=orizont, m=distanța dintre evenimente). Dar acest proces are o proprietate pe care φ (AR(1)) NU o are: **memorie FINITĂ**. Autocorelația unei sume pe fereastră de 20 bare scade LINIAR și devine EXACT ZERO dincolo de lag~20 — pe când un AR(1) cu φ=0,69 are memorie INFINITĂ, cu decădere geometrică ce nu se anulează niciodată. Potrivirea doar pe `ρ₁` ignoră exact diferența care contează pentru un bootstrap pe blocuri: **`block_bootstrap@v1` a fost testat cu L=28 — mai lung decât orizontul de 20 bare al dependenței reale.** Dacă dependența reală se termină la ~20 bare, un bloc de 28 o CONȚINE integral — proprietate pe care un AR(1) cu memorie infinită nu o are la NICIO lungime finită de bloc. O potrivire pe `ρ₁` singur ar putea la fel de bine SUPRAESTIMA riscul cât să-l subestimeze — instrumentul (curba AR(1)) răspunde la o întrebare diferită de cea pe care o pune LM-001 (dependență cu memorie mărginită la orizont).

**Concluzie: nu resping pentru că am demonstrat φ>0,55 — resping pentru că nicio mapare pe acest instrument nu ar fi o dovadă credibilă, în niciun sens. Asta ESTE motivul pentru care se activează o calibrare structurală, nu un eșec al calculului.**

### Golul din prag, închis explicit

Ordinul: `φ≤0,50` deblochează, `φ>0,55` comută pe WP-5'; nimic specificat în `(0,50; 0,55]`. Închid mecanic, reutilizând principiul deja existent în manifest (`fail_closed_default`), nu o convenție nouă: **banda netestată `(0,50; 0,55]` se grupează cu partea CONSERVATOARE a deciziei — `φ≤0,50` → deblocare (singurul punct măsurat nominal); `φ>0,50` (inclusiv banda netestată) → WP-5'.** Această regulă rămâne valabilă pentru orice folosire viitoare a curbei AR(1) — chiar dacă, pentru LM-001 specific, nu mă bazez pe ea (secțiunea de mai sus).

### WP-5' pentru LM-001 — dimensionată concret, nu doar numită

Nu o baterie F6-style generică — o baterie construită pe MECANISMUL REAL de dependență al LM-001 (ferestre suprapuse), nu pe un proxy AR(1):

1. **Generator de null potrivit:** simulează șocuri i.i.d. per-bară; construiește statistici tip-`net_R` pe ferestre de 20 bare, eșantionate la distanțele REALE dintre evenimente (folosind distribuția empirică completă a distanțelor — histograma de grad deja livrată de VE, nu doar media 6,2).
2. **Rulează `block_bootstrap@v1`** (L variabil — 10/20/28/40) contra acestui null, la n≈21.048, măsurând FPR@0,05 exact ca bateria S8 existentă (reutilizează `ve/calibration/synthetic_block_bootstrap.py`, doar generatorul de null se schimbă).
3. **Prag de acceptare fixat ÎNAINTE de rulare** (de data asta corect, ca să nu se repete problema de ordine): aceeași convenție „nominal" deja folosită (FPR cu CI ce acoperă ~0,05).
4. Dacă nominal la L=28 (sau mai mare): `block_bootstrap@v1` devine validat SPECIFIC pentru mecanismul real de suprapunere — o validare mai puternică decât orice mapare pe AR(1) ar fi putut da. Dacă tot anti-conservator, se crește L (blocurile trebuie să fie cel puțin cât orizontul) sau se reconsideră estimatorul.

## SARCINA 2 — MK-03/MK-04 RATIFICAT la commit `1930467`, cod citit integral

Am citit ambele fișiere complet, linie cu linie, nu doar raportul. Confirmat: `detect_inverse_fvgs` (Q4, close decisiv, verbatim E010/E012), `detect_fvg_reactions` (gradientul în 3 trepte + consumarea D7 la CE-50), `derive_week_index` (gol >1 zi calendaristică), `detect_level_touches` (PDH consumat la prima atingere în fereastra zilnică) — toate implementează EXACT deciziile ratificate în `STATISTICIAN_MK03_MK04_NINE_QUESTIONS_RESOLUTION_v1.0.md`, nicio convenție nouă introdusă tacit. Verificat logica de ordine a gradientului (CE-50 ≤ umplere ≤ inversare, geometric garantat prin `lower < ce_50 < upper`) — corectă.

**Verificat direct, nu doar acceptat:** `mypy --strict` curat pe ambele module; **34 teste trec** (`test_mk03_mk04.py` + `test_mk03_mk04_closures.py` + `test_structure.py` + `test_detect_breaks_rearm.py` = 11+8+10+5=34, exact); cele 4 eșecuri pre-existente din restul repo-ului confirmate să NU importe niciunul din aceste module (`grep` direct, zero potriviri).

**O observație minoră, găsită prin citirea codului, nu blocantă:** antetul docstring al `institutional_levels.py` spune încă „IMPLEMENTARE PARȚIALĂ (doar ce e ratificat)" — deși toate deciziile MK-04 enumerate mai jos în același docstring sunt RATIFICAT/RESOLVED, nimic mai rămâne DESCHIS. `imbalance_mechanics.py` și-a actualizat corect antetul la „ÎNCHIS"; `institutional_levels.py` nu. Semnalez pentru o corecție cosmetică viitoare — nu blochează ratificarea, codul funcțional e corect.

**RATIFICAT: MK-03 și MK-04, ambele module, complet.**

## SARCINA 3 — nomenclatorul SMC_S*

**Coliziunea confirmată direct** (`code/mstrat.py`): S1=`liquidity-sweep mean-reversion`, S2=`failed-breakout fade`, S3=`breakout-retest momentum`, S13 (grilă FVG: `fvg/mode/stop/exit`), S16 (grilă niveluri: `pdh/pdl/pd_open/pd_close/pd_mid`) — toate cinci există deja în `REGISTRY`-ul legacy. **S13 și S16 au fișiere reale de implementare** (`ai_trader/strategy_runtime/families/s13_imbalance_fill.py`, `s16_previous_day_levels.py`, plus teste proprii) — o coliziune cu forme scurte ar fi lovit cod de producție, nu doar nume de cercetare.

**Înregistrat, prefix rigid protejat, obligatoriu:**

| Nume | Concept |
|---|---|
| `SMC_S1` | Liquidity Sweep Reversal |
| `SMC_S2` | Failed Breakout / Failed Sweep |
| `SMC_S3` | Breakout Retest Continuation |
| `SMC_S13` | Liquidity Void / Imbalance Fill |
| `SMC_S16` | Previous Day Levels |

**Interdicție explicită:** forma scurtă (`S1`, `S13`, etc.) NU se folosește NICIODATĂ pentru familiile noi — întotdeauna `SMC_S13`, niciodată `S13`. **`S1`-`S51` fără prefix se referă PERMANENT la corpul legacy dezafectat** — nu la vreo familie SMC nouă, indiferent cât de asemănător conceptul.

**Cadrul Open-R** (numele tău, adoptat — e cadrul deja ratificat la Mandatele 3.11-3.13, acum numit reutilizabil): stop geometric = distanța structurală („spike"-ul propriu fiecărei familii — extremul fitilului la sweep pentru SMC_S1, marginea zonei la SMC_S13 etc., fiecare familie își instanțiază propriul „spike" geometric, principiul RĂMÂNE comun) + 2 pips, FĂRĂ podea; filtru `[10,1 ; 65,0]` pips; `net_R` ca variabilă de rezultat.

**O distincție pe care o adaug, nu doar aplic cifrele:** **podeaua (10,1 pips) e PORTABILĂ** — derivată exclusiv din formula de cost/R (`cost_stres_3× / R = 100%`), o proprietate a CONSTRUCȚIEI de risc (comună tuturor familiilor Open-R), nu a distribuției empirice specifice LM-001. Se reutilizează direct. **Plafonul (65 pips) NU e portabil în același fel** — a fost derivat din percentila p90 EMPIRICĂ a distribuției proprii LM-001 (46,98 pips); celelalte patru familii pot avea distribuții de deplasare complet diferite (o zonă FVG nu e geometric identică cu un fitil de sweep). **Tratez 65 pips ca PLACEHOLDER pentru SMC_S2/S3/S13/S16, nu ca valoare finală** — fiecare necesită propriul audit de geometrie (analog celui făcut pentru LM-001) înainte ca plafonul să fie confirmat, nu asumat orbește.

**Pre-screening de dedublare (`PROJECT_AUDIT.md` D11/§F) — obligatoriu ÎNAINTE de înrolare, nu după:** criteriul e identitatea jurnalului de tranzacții (hash SHA-256 pe `entry_epoch,exit_epoch,R`), nu statistici sumare; ID canonic = cel mai mic lexicografic din clasa de echivalență; raportare duală obligatorie (N brut / N distinct), iar N distinct e cel folosit la orice corecție FDR viitoare. Dacă cele 20 de variante (5 familii combinate cu dimensiuni gramaticale) se enumeră combinatoriu peste primitivele deja existente (swing/session/pdh_pdl ca referință, lookback-uri, exit-uri), riscul e IDENTIC celui deja documentat (27,0% redundanță pe corpul de 1972, 87% din clustere dintr-un singur parametru condiționat-inert, `D11`) — nu teoretic, deja materializat o dată în acest lab. Regula se aplică MECANIC pe orice grilă pe care VE o construiește, ÎNAINTE ca vreo variantă să fie înrolată pentru testare.

**Stare: `AWAITING_VALIDATION_ENGINE_CODE`** — niciun detector construit încă pentru cele 5 familii SMC_S*; înregistrare de nomenclator + cadru de risc, nu de execuție.

---

**Holdout SEALED, neatins. Niciun backtest rulat. UTF-8, LF — verificat la generare.** Manifestul se incrementează la v2.5.7 după publicarea acestui document.
