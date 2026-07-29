# STATISTICIAN — PRE-ÎNREGISTRAREA FORMALĂ A IPOTEZEI COMPUSE (DemandZone × OB, risc ATR, ieșire parțială)

**Document ID:** STAT-COMPOSITE-HYPOTHESIS-FORMAL-PREREGISTRATION-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

**Verificare de sursă:** re-confirmat `h1_trend_up`/`h4_trend_up` neschimbate în `code/mtf.py:98-102` (`ema20>ema50`, prag 0,5). Verificată aritmetic fiecare cifră din justificarea CEO (secțiunea următoare). Nimic rulat — document de specificație pură, cf. „Holdout SEALED, nimic nu rulează până la formalizare."

---

## Confirmare aritmetică — pragurile 0,7/1,4/2,1 nu sunt arbitrare, dar tot NU sunt derivate statistic

Verificat exact: `50/74=0,676`, `60/74=0,811` → intervalul CEO „0,68–0,81" confirmat. `100/74=1,351`, `120/74=1,622` → intervalul „1,35–1,62" confirmat. **0,7 cade în [0,68;0,81]; 1,4 cade în [1,35;1,62].** Confirmat și contrastul cu descoperirea: `50/17=2,94`, `100/17=5,88` — aceleași cifre în pips ar fi însemnat 2,9×/5,9× ATR pe regimul de descoperire, o strategie complet diferită (stop la aproape 3 ATR-uri e ceva ce nicio construcție anterioară din acest lab n-ar accepta ca "stop strâns"). Aceasta e exact demonstrația portabilității: 0,7/1,4 codifică intenția lui CEO (un stop de 50-60 pips la volatilitatea de azi) într-o formă care păstrează sensul la orice regim de volatilitate — spre deosebire de fixarea în pips.

**Decizie: rămân ALESE, nu derivate — declarat explicit, cum a cerut CEO.** Observația despre amplitudinea barei (74 pips azi) e o RAȚIONALIZARE a alegerii, nu o DERIVARE statistică (nu rezultă dintr-un test, un prag de putere, sau o optimizare) — e o intuiție de trader convertită portabil. Prefer, exact cum a spus CEO, să declar asta ca alegere de proiectare cu proveniență cunoscută, decât să pretind o derivare care nu există. RR ponderat: `1,4/0,7=2,0R`, `2,1/0,7=3,0R`, ponderat `0,75×2,0+0,25×3,0=2,25R` — confirmat identic mandatului anterior.

**Pragul de rentabilitate NU e un singur număr — reconfirm regula deja stabilită (R variază continuu).** Formula exactă: `w*=(1+cost/R)/(RR+1)=(1+cost/R)/3,25`. La cost/R→0 (ATR foarte mare, R>>cost), `w*→1/3,25=30,77%≈31%` — cifra lui CEO e limita fără-cost, nu valoarea reală la orice R. La ATR median pe regim (`$1,99/$1,23/$2,16`, din verificarea Task 1 anterioară): `R=0,7×ATR≈$1,4/$0,86/$1,51`, `cost/R=0,20/R≈14,3%/23,3%/13,2%`, deci `w*≈(1,143-1,233)/3,25≈35,2%-37,9%`. **Pragul real se mișcă între ~31% (ATR mare) și ~38% (ATR aproape de podea)** — raportez interval, nu punct, consecvent cu regula deja aplicată la LM-001/SMC_S1_v2.

---

## Decizia 1 — filtrul de eligibilitate: podeaua de ATR e SUFICIENTĂ, fără plafon

Podeaua `ATR_min≈$0,857` (89,75% din barele de descoperire o depășesc, confirmat) rămâne singurul filtru de eligibilitate necesar. **Nu adaug un plafon de ATR** — motiv structural, nu omisiune: în construcția veche (spike+2 pips), R era o distanță geometrică FIXĂ, independentă de volatilitatea curentă, motiv pentru care un plafon (65 pips) era necesar ca să excludă coada extremă (evenimente rare, risc de concentrare). Aici, **R=0,7×ATR e proporțional cu volatilitatea curentă prin construcție** — o bară de ATR extrem de mare nu produce un R disproporționat de riscant în termeni normalizați, R crește exact odată cu volatilitatea. Riscul de bare extreme (știri, gap-uri) e deja gestionat ALTUNDE, de primitivele existente (LiquidityVoid, excluderea ferestrei de mentenanță) — nu e o funcție a ACESTUI filtru de eligibilitate. **Podeaua singură e suficientă.**

## Decizia 2 — orizontul variabil: agregare pentru decizie, stratificare obligatorie ca diagnostic

Testul PRINCIPAL (H0: μ_netR≤0) rulează AGREGAT, pe toate tranzacțiile eligibile combinate, indiferent de ora de intrare — motivul: orizontul variabil nu e un artefact de eliminat, e o PROPRIETATE a strategiei așa cum a fost specificată (închiderea intraday obligatorie face parte din definiția ei, nu dintr-un defect de măsurare). Stratificarea pe ora de intrare AR testa o strategie DIFERITĂ (una unde ora nu afectează orizontul) — consecvent cu convenția deja fixată la Blocul 3 (family=8, pooled peste regimuri, nu 24 de teste separate): agregăm ce aparține aceleiași construcții.

**Diagnostic obligatoriu, secundar, NU parte din decizie:** raportare separată pe sesiune (asia/london/ny/late, convenția deja stabilită) ȘI pe bucket de orizont realizat (scurt <10 bare vs lung ≥10 bare) — exact disciplina deja aplicată la NET_CONCENTRATION_INVENTORY și la stratificarea pe sesiune a oracolului: dacă rezultatul agregat e condus de o singură sesiune sau de tranzacțiile cu orizont scurt, trebuie vizibil, nu ascuns într-o medie.

## Decizia 3 — intersecția cross-candle, specificată mecanic

- **OB_B**: un `OrderBlock` (din `detect_order_blocks`) cu `kind` = direcția bias-ului H1/H4 curent, NEMITIGAT la bara de evaluare `t` (niciun eveniment de Mitigation cu `event_idx<t`, niciun Breaker înainte de `t`).
- **Bara-declanșator `t`** = bara la care OB_B are propriul eveniment CALIFICAT de Mitigation (scanare de la `formation_idx+2`, cf. corecției de circularitate ratificate).
- **DemandZone_A** (din `detect_demand_zones`), calificată dacă TOATE: (a) `kind_A == kind_B` (aceeași polaritate — un long cere zone/OB bullish, un short cere bearish); (b) `formation_idx_A != formation_idx_B` (eveniment de formare DIFERIT — cross-candle, prin construcție); (c) `formation_idx_A < t` (DemandZone_A trebuie să existe/fie observabilă înainte de bara de declanșare — siguranță forward, nicio privire în viitor); (d) `|formation_idx_A − formation_idx_B| <= 460` bare (fereastra de o săptămână empirică, REUTILIZATĂ verbatim din Compression/Volatility, Mandatul 3.21 — nu invenez o cifră nouă); (e) ACEEAȘI bloc de descoperire (D4) ca B — nicio pereche peste granița de bloc.
- **Suprapunere geometrică**: `OB_B.zone_lower <= DemandZone_A.zone_upper ȘI OB_B.zone_upper >= DemandZone_A.zone_lower` (test standard de suprapunere de intervale, nu containment complet).
- **Condiția compusă e satisfăcută** dacă EXISTĂ cel puțin o `DemandZone_A` care satisface (a)-(e) și suprapunerea geometrică, la bara `t`. Intrarea = next-open după `t`, în direcția bias-ului.

## Decizia 4 — familia de corecție: SEPARATĂ, family=1

Reconfirm decizia mandatului anterior: construcția (DemandZone×OB, risc ATR, ieșire parțială) nu aparține grammaticii Open-R (S1-S20) — nu e o variantă apropiată a vreunei familii existente, testată o singură dată, nu de 8 ori în aceeași trecere. Includerea ei în familia-8 (fixată la Blocul 3 pentru S1+cele 7) ar fi la fel de arbitrară ca excluderea lui S1 din acea familie ar fi fost. **Family=1, separată.**

## Decizia 5 — populația așteptată: NU dau o cifră falsă-precisă; fixez pragul ÎNAINTE de măsurătoare

**Nu am o rată empirică pentru formarea OB pe acest set de date** — spre deosebire de podeaua de ATR (unde am rulat direct verificarea), formarea OB (impuls E010 ȘI înghițire de corp) nu a fost încă numărată pe cele 130.491 bare. Orice cifră aș da acum ar fi o înmulțire de rate necunoscute (rata de formare OB × rata de mitigare × rata de suprapunere cu o DemandZone cross-candle × alinierea cu bias-ul H1/H4) — patru factori, fiecare cu incertitudine de ordinul 2-5×, compunându-se într-o eroare de ordin de mărime. **Refuz să prezint o estimare fals-precisă.**

**În loc, fixez pragul ACUM, înainte ca cifra să existe** (aceeași disciplină ca la harta de sensibilitate SMC_S1_v2): cer VE un script READ-ONLY, de numărare pură (analog `task1_atr_eligibility.py`), care aplică EXACT lanțul de filtre de mai sus (bias + OB nemitigat + eveniment de Mitigation + suprapunere cross-candle cu DemandZone + podeaua de ATR) pe cele 130.491 bare, raportând numărul de tranzacții eligibile per regim, ÎNAINTE de orice rulare a testului statistic. **Regula INSUFFICIENT_N se aplică automat**: dacă populația rezultată per regim e sub pragul stabilit `n>=25` (convenția minimă a lab-ului), acel regim se marchează NOT TESTABLE ON THIS DATA — nu un eșec al ideii, o insuficiență de evenimente, exact distincția deja aplicată la S17-corecție (n=27 sub prag).

---

## Pre-înregistrare formală — cele cinci criterii

1. **Prag numeric:** `H0: μ_netR<=0` vs `H1: μ_netR>0`, unilateral, α=0,05, family=1.
2. **Orizont ca bare:** VARIABIL, `min(entry+20,EOD)`, mărginit superior la 20 (acoperire oracol confirmată la L>=28, Mandatul 3.20/3.23); testul principal AGREGAT peste orele de intrare, diagnostic obligatoriu stratificat pe sesiune și pe bucket de orizont realizat.
3. **Populație:** de măsurat de VE prin script read-only dedicat (cf. Decizia 5), ÎNAINTE de orice test; pragul INSUFFICIENT_N (n>=25/regim) fixat AICI, înainte de a exista cifra.
4. **Prag de clasificare:** α=0,05, family=1, separată de familia-8 a Blocului 3 (cf. Decizia 4).
5. **Zero parametri liberi:** pragurile ATR (0,7/1,4/2,1) declarate ca ALESE (Decizia arithmetică de mai sus), filtrul de eligibilitate fixat (Decizia 1), intersecția cross-candle specificată mecanic complet (Decizia 3), orizontul și agregarea rezolvate (Decizia 2) — nimic rămas nedecis care ar afecta execuția.

**Numele:** construcția nu are încă un nume în grammatica protejată a lab-ului. Propun **OBDZ-001** (Order Block × Demand Zone), verificat fără coliziune cu prefixele existente (E0xx, S0xx, LM-00x) — flag pentru ratificare CEO înainte ca VE să-l folosească în cod/rapoarte.

**AWAITING VALIDATION_ENGINE_CODE.** VE implementează mașina de stare (bias → intersecție cross-candle → SL/TP1/TP2 ATR → ieșire parțială) DUPĂ publicare, cf. instrucțiunii. Prima execuție permisă e scriptul de numărare a populației (Decizia 5) — NU testul statistic complet — până când pragul INSUFFICIENT_N e verificat.

---

**Holdout SEALED. Nimic rulat în acest document. Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.10 (commit `75deeca`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
