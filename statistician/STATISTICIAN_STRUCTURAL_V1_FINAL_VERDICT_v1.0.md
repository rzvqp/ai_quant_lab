# STATISTICIAN — VERDICT FINAL: E001/E002/E004 (Mandat 3.6)

**Document ID:** STAT-STRUCTV1-FINAL-VERDICT-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Verificare de sursă:** citit direct commit `1a64812` (`edge_research/MANDATE41_TRANSACTIONAL_EVAL.md`, `mandate41_eval.py`, `mandate41_eval_results.json`) — nu doar cifrele din mesaj. Confirmat: pragurile de break-even (0,550/0,367) se potrivesc exact formulei `w* = (1+cost/S)/(RR+1)` la cost=0,4/S=4,00; testul e `scipy.stats.binom.sf(win-1, n, w_star)` — binomial exact, one-sided, nu aproximare normală; familia BH de 6 e pe numărători **puși laolaltă (pooled) peste cele 3 regimuri**, nu pe cele 18 celule individual.

---

## SARCINA 1 — RATIFICAREA STATISTIC-TESTULUI

**Ratific testul binomial exact, one-sided, contra pragului de break-even ajustat la cost, ca standard canonic pentru această suită. Adăugat în contract (§7 nou, v1.2).**

### De ce se ratifică

1. **Exact, nu aproximat:** `binom.sf` calculează probabilitatea binomială exactă, nu o normalizare z — corect indiferent de mărimea eșantionului (n=129 la cea mai mică celulă), consecvent cu preferința deja stabilită în acest laborator pentru teste exacte/de permutare peste formule analitice aproximative.
2. **Pragul, nu variabila de rezultat, poartă costul:** `w*` încorporează costul de 0,4 direct în pragul de break-even (derivat matematic: `w×(T+S) = cost+S`), nu ca o corecție aplicată post-hoc rezultatului brut. Pentru un design cu țintă/stop FIXE (nu R variabil ca la restul laboratorului), asta e alegerea corectă — nu are nevoie de un t-test pe o variabilă continuă când rezultatul e fundamental binar (win/loss la R fix).
3. **Familia de 6, pe numărători puși laolaltă:** consecvent cu §6 deja scris (3 contracte × 2 RR), NU 18 (× 3 regimuri). Regimul e o defalcare DESCRIPTIVĂ de robustețe (verifică dacă nulul ține consistent pe condiții diferite de piață), nu o multiplicare a testelor — exact principiul deja stabilit pentru programul celor 4 regimuri (`FOUR_REGIME_RUN_STATUS_v1.0.md`: "măsurătoare descriptivă, nu test de ipoteză"). Aplicat corect de Flow A.

### O rezervă condiționată, pentru înregistrare — nu schimbă verdictul de azi

Asumpția binomială presupune tranzacții independente (Bernoulli iid). Aici e rezonabilă — cel mult o intrare per sesiune/zi per contract, rezultate separate temporal — dar **dacă o suită viitoare sub acest contract are frecvență mult mai mare sau poziții suprapuse, asumpția de independență trebuie reexaminată** (posibil N efectiv sub autocorelație), înainte de a refolosi acest test necondiționat. Nu contează azi: winrate-urile sunt cu mult sub prag în toate cele 18 celule (ex. E001 RR1:1 = 0,4776 pooled vs. prag 0,550) — chiar dacă testul corect (cu ajustare de corelație) ar avea o incertitudine mai largă, concluzia "nu depășește pragul" nu s-ar răsturna la o asemenea distanță.

---

## SARCINA 2 — ETICHETA: `REJECTED — NEGATIVE_EXPECTANCY_UNDER_COST`

**Etichetă formală, aplicată la toate trei: E001, E002, E004, la parametrizarea din contractul de execuție §9.4.1 (stop 4,00/5,00, RR 1:1/1:2).**

### Delimitarea scopului — exact ca la cele 47, mai importantă aici

`REJECTED` înseamnă precis: **profitabilitatea ipotezei, AȘA CUM E SPECIFICATĂ ÎN CONTRACTUL DE EXECUȚIE (stop fix 40-50 pips, țintă RR 1:1 sau 1:2), nu se susține — winrate sub pragul de break-even ajustat la cost, în toate cele 3 regimuri, la ambele RR, la ambele stopuri.** NU înseamnă că conceptele ICT subiacente (sweep-and-reverse pe range-ul Asia, reversal Frankfurt→Londra, urmărire FVG post-deschidere) sunt infirmate ca fenomene de piață. Contractul de execuție a adăugat un stop/țintă/cost — o parametrizare NOUĂ, nu parte din V1-urile înghețate — și acea parametrizare specifică e cea respinsă.

**De ce distincția contează mai mult aici decât la cele 47:** la cele 47, respingerea venea dintr-un artefact de măsurare (execuție eșuată structural). Aici, respingerea vine dintr-un test statistic curat, pe date rezolvabile, cu bracket stabil — e o respingere mult mai credibilă STATISTIC, ceea ce face și mai tentant să fie citită peste șase luni ca "ideea ICT nu funcționează", nu doar "acest stop/RR anume nu funcționează". O respecificare (alt stop, altă țintă, alt RR) ar fi un candidat NOU, cu propria evaluare completă de la zero — nu o resuscitare a acestor trei.

---

## SARCINA 3 — `E004 fill` (0,662–0,736): CER CONTROLUL, ÎNAINTE DE CONSEMNARE

**Aleg opțiunea 1, exact preferința ta, cu motivul propriu, nu doar prin acceptare.**

### De ce nu consemnez `CONFIRMED_STRUCTURAL_ANOMALY` acum

Rata de umplere a unui gap, în general, e cunoscută ca fiind ridicată pe orice instrument/timeframe — un orizont generos de 50 bare M15 dă mult timp pentru reintrare. Fără un numitor (rata de umplere a UNUI GAP COMPARABIL, ne-selectat prin criteriul FVG specific — fereastra 13:30-15:30 UTC, "primul din sesiune"), nu pot distinge "FVG-urile astea se umplu neobișnuit de des" de "orice gap de pe acest instrument se umple cam așa des, iar E004 nu observă nimic special". Exact eroarea deja găsită la analiza Phase 1 a candidaților DC: găsești fenomenul căutându-l, dar nu știi cât de rar e fără o comparație.

`CONFIRMED_STRUCTURAL_ANOMALY` e o etichetă tare, exact genul care se citează peste șase luni ca fapt stabilit. Nu o pun fără control.

### Controlul cerut — specificat, ca Flow A să-l poată executa fără tur suplimentar

Pe aceleași 3 regimuri (bear/bull/correction, excluzând regimul 2022-2026 pentru același motiv SAME-WINDOW-RESAMPLED), măsoară rata de umplere pentru o populație de gap-uri **generice**, NU selectate prin criteriile specifice E004:
- Detecție: același imbalance standard 3-bare (`E012 detect_fvgs`), fără restricția de fereastră 13:30-15:30 UTC și fără condiția "primul din sesiune" — orice imbalance 3-bare de pe M15, în interiorul acelorași ferestre de descoperire.
- Orizont identic: 50 bare M15 de la formare.
- Rezultat identic: binar `fill` = prețul reintră în `[zone_low, zone_high]` în interiorul orizontului.
- Populația de control trebuie să fie suficient de mare (n comparabil sau mai mare decât cele ~450-480 per regim de la E004) pentru un interval de încredere util.

**Interpretare, pre-înregistrată acum, înainte de rezultat:** dacă rata de control e apropiată de 0,66-0,74 (ex. în interiorul unui interval de ±0,10), rata E004 e **nespecifică** — nu susține `CONFIRMED_STRUCTURAL_ANOMALY`, se etichetează `OBSERVED_NOT_DISTINCTIVE`. Dacă rata de control e semnificativ mai mică (ex. sub 0,40-0,50, cu un test formal de comparație a două proporții), rata E004 devine un candidat real pentru `CONFIRMED_STRUCTURAL_ANOMALY`, dar tot cere verdictul meu final după ce văd cifrele, nu automat.

**Până la control:** cifrele (0,718 bear / 0,736 bull / 0,662 corecție) se consemnează ca `PENDING_CONTROL` — observate, raportate, dar NU etichetate ca anomalie, NU tratate ca fapt stabilit.

---

## AUTO-CORECȚIE, DE CONSEMNAT SEPARAT — 3 regimuri, nu 4

**Am cerut patru regimuri în mandatul anterior. Eroarea e a mea.** Regimul 2022-2026 (bull +223,3%) e integral în M15 legacy — fereastra care a informat parametrizarea V1 (proveniența convențiilor deja stabilită, `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md` §2) — și cade sub regula `SAME-WINDOW-RESAMPLED` pe care am scris-o eu însumi. Flow A l-a exclus corect, fără să aștepte corecția mea. Consemnez aici, nu doar în conversație: **testul E001/E002/E004 s-a rulat pe 3 regimuri (bear/bull/correction, 2011-2021), nu pe 4** — al patrulea nu poate exista ca test independent pentru aceste ipoteze, prin propria regulă a laboratorului.

---

**Nu am atins date, nu am executat nimic. Statistician se oprește aici.**
