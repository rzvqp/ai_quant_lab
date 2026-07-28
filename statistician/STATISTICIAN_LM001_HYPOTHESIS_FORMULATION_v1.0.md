# STATISTICIAN — FORMULAREA IPOTEZEI TESTABILE LM-001 (Mandat 3.13)

**Document ID:** STAT-LM001-HYPOTHESIS-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician
**Precedent:** `STATISTICIAN_LM001_RISK_FRAMEWORK_DECISION_v1.0.md` (commit `156a883`); manifest v2.5.4 (`04c096e`, `alpha-automation-v1`).

**Verificare de sursă înainte de formulare:**
- Reconfirmat: manifestul e la `04c096e`, documentul de decizie la `156a883` — exact cum ai citat. Commit-ul `69df2b7` din ordin **nu există** în niciunul din cele două repo-uri (`git log --oneline --all | grep 69df2b7` gol în ambele) — nu e o discrepanță de-a mea, e o citare greșită undeva mai sus în lanț.
- Citit direct constantele de orizont: `edge_research/_profile.py:11` `HORIZONS = (1, 3, 5, 10, 20, 50)`; `edge_research/e015_order_block_remitigation.py:47` `TRACK_HORIZON = 960 # 10 trading days`; `e010_breaker_block_snatch.py:49`/`e012_inverted_fvg.py:38` `REVISIT_HORIZON = 480 # 5 trading days`; `e009_choch_retest.py:53` `PRIMARY_HORIZON = 480`.
- Citit direct `docs/OUTCOME_DISTRIBUTION_v1.0.md` — confirmă exact: `time` net1 mediană **0,628** (n=484), `rr2` net1 mediană **0,387** (n=580).
- Citit direct `validation_engine/BLOCK_BOOTSTRAP_S_CALIBRATION_RECORD.md` — confirmă exact: FPR@0,05 la n=250/L=8: φ=0,4→**0,077**, φ=0,6→**0,093**, ambele marcate ANTI-CONSERVATOR; verdict propriu al VE: **„rămâne UNVALIDATED"**.

---

## SEMNALAREA 1 — orizontul: eroarea era categoria, nu doar raportul

„12 bare" nu era doar nederivat — era comparat cu familia greșită de orizonturi. `TRACK_HORIZON`/`REVISIT_HORIZON` (960/480) răspund la o întrebare diferită: **cât timp aștepți ca un nivel VECHI să fie revizitat** — o mecanică de memorie pe termen lung, nepotrivită pentru LM-001, care testează o **reacție imediată** după sweep, nu o revizitare ulterioară. Familia corectă de comparat e `_profile.HORIZONS` — construită special pentru exact acest tip de măsurătoare (`movement_profile`, folosită deja pe toate cele 40 de edge-uri pentru clasificarea continuare/reversie/stagnare imediat după eveniment).

**Orizont PRIMAR/decisiv: 20 bare M15.** Derivare (nu alegere): 20 bare = 5 ore = durata EXACTĂ a sesiunii `london`, deja stabilită mecanic în `code/mtf.py:37-38` (`london` = ora UTC `[8,13)`, exact 5 ore). Alegerea leagă un orizont deja real (`_profile.HORIZONS` conține 20) de o graniță deja reală (durata unei sesiuni deja definite) — reacția se măsoară în interiorul unei ferestre comparabile cu o sesiune întreagă, nu peste mai multe sesiuni cu dinamici diferite. Niciun număr nou nu a fost inventat.

**Orizonturi secundare, descriptive, NU decizive:** restul lui `_profile.HORIZONS` — 1, 3, 5, 10, 50 bare — raportate integral, reutilizate ca atare (niciun număr nou), dar **nu intră în familia testată statistic** — exact precedentul K6-decisiv/K12-descriptiv de la DC-0004 (`STATISTICIAN_DEFINITION_RECONCILIATION_DECISION_v1.0.md`).

## SEMNALAREA 2 — nu există take-profit, declarat explicit

**Ieșire PURĂ pe timp, la orizontul de 20 bare — fără take-profit.** Rezultatul e prețul la bara `c+20` (închidere), indiferent de traiectoria intermediară. Coerent cu metodologia `net_R` (Sarcina 1, mandatul anterior): se măsoară ce dă prețul la un orizont fix, nu ce s-ar fi întâmplat dacă s-ar fi atins un prag intermediar. **Scris explicit aici ca să nu fie dedus greșit peste șase luni.**

## SEMNALAREA 3 — concentrarea asociată ieșirii pe timp: confirmată, acceptată cu obligație de disclosure

Confirmat direct (`docs/OUTCOME_DISTRIBUTION_v1.0.md`): `exit=time` are concentrare NET 1,6× mai mare decât `exit=rr2` (0,628 vs 0,387, mediană `net1`). **Știu asta și păstrez totuși ieșirea pe timp** — motivul: e singura coerentă cu metodologia `net_R` la un R continuu, geometric-derivat (un target RR fix ar necesita urmărire bar-cu-bar dependentă de traiectorie, o construcție diferită, mai grea, nespecificată încă). Nu ignor riscul — îl transform în **obligație de disclosure mecanică**: orice verdict pe LM-001 trebuie însoțit obligatoriu de aceleași diagnostice de concentrare deja folosite în `NET_CONCENTRATION_INVENTORY_v1.0.md` (ponderea celei mai mari tranzacții în `net_R` total, verificarea colaps-la-eliminarea-celei-mai-bune-tranzacții) — dacă rezultatul e condus de 1-2 valori extreme de `net_R`, asta trebuie vizibil alături de orice verdict pozitiv, nu ascuns în spatele unei medii.

## SARCINA — ipoteza testabilă LM-001, cele cinci criterii

1. **Prag numeric explicit:** `H0: μ_netR ≤ 0` vs `H1: μ_netR > 0` (unilateral), exact cum ai specificat.
2. **Orizont ca număr de bare:** 20 bare M15 (decisiv, derivat); 1/3/5/10/50 (descriptiv, reutilizat din `_profile.HORIZONS`).
3. **Populație și numitor — CORECȚIE FAȚĂ DE MANDAT:** wick-sweep-uri valide (D6/D7) pe cele 130.491 bare de descoperire M15_v2, cu deplasare în **`[10,1, 65,0)` pips** (ambele limite deja ratificate) — **N = 21.048, nu 22.887.** Cifra din mandat (22.887) e doar filtrul de podea (`≥10,1`, nemărginit superior) — nu scade și cele 1.839 evenimente (5,3%) care sunt ȘI `≥65` și trebuie excluse de plafon. Verificat direct, reconstruind cele 34.670 evenimente: `≥10,1` singur = 22.887 (66,0%); `≥65` (excluse de plafon) = 1.839 (5,3%); **ambele limite simultan = 21.048 (60,7%)**. Defalcare pe regim: bear 9.248/13.863 (66,7%), bull 7.186/14.190 (50,6%), correction 4.614/6.617 (69,7%). Corectez aici — nu construiesc pe cifra din mandat fără verificare.
4. **Prag de clasificare:** respinge H0 la `alpha=0,05` (BH-FDR peste familia de 1 — trivial, fără ajustare, familie unitară).
5. **Zero parametri liberi:** intrare (next-open, mecanic), direcție (mecanică din tipul bazinului), prag inferior (10,1 pips, derivat), prag superior (65 pips, confirmat), R (`(deplasare+2)×0,10`, geometric), cost (0,40, stabilit), orizont (20 bare, derivat), preț de ieșire (`close[c+20]` față de `open[c+1]`), statistică (`net_R`), test (bootstrap/permutare unilateral) — nimic rămas liber pentru optimizare ulterioară.

**Formula rezultatului per tranzacție:**
```
net_R_i = direcție_i × (close[c+20] − open[c+1]) / R_i − cost / R_i
direcție_i = +1 (bazin inferior → LONG) / −1 (bazin superior → SHORT)
R_i = (deplasare_i + 2) × 0,10
cost = 0,40
```
**Siguranță de graniță:** bara de ieșire `c+20` trebuie să rămână în ACELAȘI `discovery_range` ca bara de sweep `c` (aceeași regulă de carantină ca la intrarea next-open) — evenimentele unde `c+20` iese din interval sunt EXCLUSE, numărul lor raportat explicit de VE la execuție, nu ascuns.

## CRITERIUL DE SUCCES — familie, metodă de bootstrap

**Mărimea familiei: 1.** Un singur orizont decisiv (20 bare), o singură direcție (mecanică, nu multiplică familia — aceeași convenție deja scrisă în preînregistrarea originală LM-001). Fixată ACUM, înainte de orice test.

**Metoda de bootstrap: NU confirm `block_bootstrap@v1` fără o verificare suplimentară — nu resping direct, dar nu extrapolez orbește.**

Două motive independente, niciunul suficient singur pentru o respingere completă, dar împreună insuficiente pentru o confirmare simplă:
1. Verdictul propriu al VE rămâne, textual, **„UNVALIDATED"** — nu a fost reparat, doar raportat.
2. n=21.048 (populația corectă — vezi criteriul 3 de mai jos) e **>10× peste cel mai mare punct calibrat (n=2.000)** — iar chiar la n=2.000, φ=0,6 (autocorelație moderată) tot arăta „ușor anti-conservator" (0,066), nu complet convergent. Extrapolarea unei metode încă nevalidate dincolo de intervalul calibrat nu e o bază defensabilă pentru o preînregistrare.

**`matched_null@v1` NU e o alternativă validă aici** — verificat direct în `docs/D2_CLOSURE_SIZING_v1.0.md` l.27-32: `matched_null@v1` rămâne validat DOAR pentru regimul ATR-scaled; regimul structural/geometric (exact ce e R-ul LM-001 — derivat din deplasare, nu din ATR) rămâne neacoperit ("regimul structural real nu a fost niciodată în baterie"), necesitând propria calibrare structurală (WP-5′, deja identificată, NEAUTORIZATĂ/neexecutată — `D2_CLOSURE_EXECUTION_v1.0.md` l.56). Folosirea lui aici ar repeta exact eroarea de scop deja semnalată la D2.

**Legătură cu întrebarea deschisă lăsată Statisticianului la închiderea D2:** același document (`D2_CLOSURE_SIZING_v1.0.md` l.55) ridică, nerezolvată încă, întrebarea dacă `R = pnl/risc` e statistica potrivită de rezultat când numitorul riscului poate fi mic — varianța explozivă la stop mic e o proprietate a statisticii, nu a rezoluției datelor. LM-001 nu ocolește întrebarea prin construcție implicită — filtrul de deplasare minimă (10,1 pips → R≥1,21$, Mandatul anterior) e exact motivul pentru care regimul de risc-aproape-de-zero care produce varianța explozivă (stopuri de ~0,05-0,12$ din familia D2 originală) e deja EXCLUS din populația LM-001 înainte de a ajunge la testul statistic — nu rezolvă întrebarea generic pentru toate ipotezele structurale, dar înseamnă că LM-001 specific nu moștenește cel mai rău caz al ei. Nu declar problema închisă — doar arăt de ce nu se aplică la fel de tare aici ca la stopurile structurale cu risc sub-$0,20 din familia originală D2.

**Specific, nu doar aleg din cele două:**
1. **Pas de verificare, ieftin, pe harness-ul deja existent:** VE extinde bateria S8 (`ve/calibration/synthetic_block_bootstrap.py`, deja construit) la un n sintetic ≈ populația reală (≈21.000) — un singur punct suplimentar, nu infrastructură nouă.
2. **Prag de acceptare, fixat acum:** dacă FPR@0,05 la acest n cade în banda deja numită „nominal" în raportul de calibrare (aproximativ ≤0,055-0,06, comparabil cu φ=0,4 la n=1.000-2.000), `block_bootstrap@v1` e utilizabil pentru LM-001, ca specificat.
3. **Dacă NU cade nominal** (plauzibil, dat fiind că φ=0,6 nu convergase complet nici la n=2.000): nu recurg la `matched_null@v1` (scop greșit, cum arătat mai sus) — LM-001 devine primul caz concret care cere execuția calibrării structurale WP-5′, deja identificată ca necesară în lucrarea de închidere D2, nu o invenție nouă acum.

**Regula n≥25 rămâne** (Discovery Screen V1), evaluată pe populația DUPĂ ambele filtre (`[10,1, 65,0)`), per regim — regim cu n<25 → `INSUFFICIENT_N`, exclus din contorul agregat, fracția dezvăluită.

---

**Manifestul se incrementează la v2.5.5 după publicarea acestui document, nu înainte.** Nu am rulat niciun test, nu am atins holdout-ul, nu am construit tranzacții reale. Statistician se oprește aici.
