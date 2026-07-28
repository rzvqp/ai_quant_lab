# STATISTICIAN — CLARIFICARE + CONTRACT DE EXECUȚIE SEPARAT (E001/E002/E004)

**Document ID:** STAT-EXEC-CONTRACT-STRUCTV1-v1.2
**Data:** 2026-07-27 (v1.0) · **Amendat:** 2026-07-27 (v1.1 — PATCH, patru corecturi decise de CTO după citirea integrală a Flow A, commit `3e8821b`) · **Amendat:** 2026-07-27 (v1.2 — §7 nou, statistic-testul ratificat, omisiune reală a v1.1)
**Nu modifică V1-urile.** E001/E002/E004 rămân exact cum sunt înghețate — binare, fără R, fără stop. Acest document specifică un contract de execuție SEPARAT, care simulează tranzacții în jurul evenimentului lor structural deja înghețat, fără să-l redefinească.

---

## PATCH v1.1 — LOG DE CORECȚII (textul vechi rămâne mai jos, marcat SUPERSEDED, nu șters)

Flow A a citit contractul integral și a raportat patru probleme, verificate direct de mine acum în `V1_OPERATIONALIZED_CONTRACTS.md` (secțiunile E001-V1/E002-V1/E004-V1) înainte de a scrie corecțiile — nu doar acceptate din mesaj:

1. **E001 — decizie CTO, aplicată:** intrarea e pe prima bară IMEDIAT DUPĂ bara de sweep (bara de manipulare), în direcția INVERSĂ spargerii — nu pe bara de rezultat ("a atins extrema opusă" e outcome-ul măsurat de V1, nu setup-ul).
2. **E002 — direcție confirmată de CTO; O EXTINDERE PROPRIE, semnalată ca atare, nu ca decizie CTO:** citind textul real E002-V1, observ ACELAȘI defect structural ca la E001 — formularea mea originală intra pe bara la care pragul de retrace 50% se satisface (outcome-ul), nu pe bara de setup (imediat după fereastra Frankfurt). Corectez prin analogie directă cu principiul deja decis pentru E001, dar marchez explicit: **aceasta nu e o decizie CTO transmisă, e propria mea aplicare a aceluiași raționament — cere confirmare sau respingere explicită**, nu se tratează ca finalizată doar pentru că "pare la fel".
3. **E004 — verificat ÎNAINTE de a îngheța, cum ai cerut:** textul V0/V1 complet există în `V1_OPERATIONALIZED_CONTRACTS.md`, secțiunea "E004-V1 — First Post-US-Open FVG Follow-Through". **E004 NU e un `movement_profile` generic** — e urmărirea unui FVG (fair value gap) de 3 bare, prima al cărei bar-mijlociu cade în fereastra 13:30–15:30 UTC (referință deschidere COMEX RTH), cu clasificare continuation/reversal/stall măsurată **în direcția polarității FVG-ului**, PLUS un binar separat, **fill** (prețul reintră în zona FVG în interiorul orizontului de 50 bare) — pe care contractul meu original nu-l cuprindea deloc, neavând vizibilitate pe text. Ambele corectate mai jos.
4. **RR — corecție aritmetică, confirmată eronată în original:** §3 vechi spunea "8,00 dolari (RR 1:1)" — greșit. La stop 4,00: RR 1:1 → țintă **4,00**; RR 1:2 → țintă **8,00**. La stop 5,00 (variantă): RR 1:1 → **5,00**; RR 1:2 → **10,00**.

---

## PARTEA 1 — CLARIFICAREA CERUTĂ, ÎNAINTE DE CONTRACT

**Verdict: a doua interpretare (a ta) e cea corectă. Prima ("niciun M5 nu poate rezolva, toate nedeterminate") e o citire greșită a propriului meu criteriu, nu o consecință validă a lui — o închid explicit aici.**

Criteriul `C(S,RR)=S(1+RR)` comparat cu percentilele distribuției (Q1/p90) e un **pre-screening**, nu testul decisiv — asta era deja scris în `STATISTICIAN_M5_INDETERMINACY_THRESHOLD_SPEC_v1.0.md` ("pre-screening-ul de mai sus doar economisește calcul, nu înlocuiește verificarea reală"), dar consecința lui la S=4,00-5,00/RR=2 (C=12-15) merită spusă explicit, ca să nu rămână loc de interpretare greșită pe un contract live.

**De ce e rar, nu universal:** `C(S,RR)` care depășește p90 (5,645 pe ny, cea mai volatilă sesiune) înseamnă, prin propria formulare a criteriului meu, **"foarte probabil rar ambiguu"** — nu "imposibil de rezolvat". Testul decisiv rămâne per-tranzacție, pe bara DECISIVĂ (cea pe care se declanșează ieșirea): dacă acea bară specifică, prin întâmplare, are o amplitudine ≥12-15 dolari — un eveniment extrem de coadă (spike de știri), nu tipic — ATUNCI e nedeterminată. Un stop de 4-5 dolari cu țintă de 8-10 nu se rezolvă în cinci minute — exact cum ai spus, e o mișcare de ore. Bara decisivă a unei asemenea tranzacții e, aproape întotdeauna, o bară obișnuită, ale cărei high/low ating UN singur nivel, nu ambele. Nedeterminarea rămâne posibilă (nu exclud tail-uri de știri), dar rară.

**Ce era, de fapt, punctul slab în formularea mea anterioară:** nu conținutul regulii (era deja corect — pre-screening vs. test decisiv), ci absența unui exemplu explicit la scară mare care să prevină exact citirea greșită pe care ai testat-o acum. **Corectez prin acest document:** pre-screening-ul "C(S,RR) depășește p90" NU e o poartă de respingere — e o predicție că fracția de nedeterminare va fi MICĂ, verificabilă empiric prin testul per-tranzacție, nu presupusă din pre-screening singur. Poarta de 25% (`NOT-RESOLVABLE-AT-M5`) se aplică pe fracția EMPIRICĂ măsurată, niciodată pe o inferență din pre-screening.

**Constatare, nu eșec, dacă empiricul contrazice:** dacă, odată rulat testul real, fracția de nedeterminare pentru oricare din E001/E002/E004 depășește totuși 25% — asta ar fi o constatare validă (mecanism neanticipat, poate volatilitate mult mai mare decât distribuția generală în jurul evenimentelor structurale specifice acestor contracte), nu o respingere a interpretării de mai sus. Se marchează atunci, per contract, `NOT-RESOLVABLE-AT-M5`, conform regulii deja stabilite.

---

## PARTEA 2 — CONTRACTUL DE EXECUȚIE

**Precondiție de guvernanță, explicită:** conform `config/split_manifest.json` (branch `alpha-automation-v1`, publicat azi), M5 are status `AWAITING_REGIME_MAP` — **100% din bare rămân sigilate** până la un manifest nou, validat. Acest contract e proiectat, nu executabil, până acel status devine `VALIDATED`.

### 1. Regula de intrare — derivată din evenimentul structural, nu redefinită

Intrarea are loc la **deschiderea barei imediat următoare** barei pe care se satisface pentru prima dată condiția structurală/binară deja înghețată a fiecărui V1 — convenția `entry@next-open`, lookahead-safe, deja stabilită în `mstrat.py`, reutilizată identic, nu reinventată. Contractul de execuție NU introduce o definiție structurală nouă — adaugă doar CÂND se intră și CUM se dimensionează riscul în jurul unui eveniment a cărui existență/moment sunt determinate integral de definiția înghețată a fiecărui V1.

- ~~**E001** ("a atins extrema opusă"): intrare la prima bară după cea pe care se atinge extrema opusă...~~ **SUPERSEDED — Flow A avea dreptate, decizie CTO:** "a atins extrema opusă" e outcome-ul V1 (măsurat pe orizontul de 52 bare), nu setup-ul. La momentul ăla mișcarea e deja consumată, nu rămâne nicio direcție forward. **Intrare corectă:** pe prima bară IMEDIAT DUPĂ bara de sweep — bara London (`session=='london'`) a cărei extremă tranzacționează ≥0,25×ATR14 dincolo de o extremă Asia (E027, deja verificat în textul V1). **Direcție: INVERSĂ spargerii** — dacă sweep-ul a spart extrema Asia de SUS, tranzacția e SHORT (pariu pe atingerea extremei Asia de jos, opusă); simetric pentru sweep în jos → LONG.
- ~~**E002** ("reversal ≥50% retrace până la 13:00"): intrare la prima bară după cea pe care pragul de 50% retrace e satisfăcut...~~ **SUPERSEDED — extindere proprie prin analogie cu E001, NU decizie CTO, cere confirmare explicită:** citind E002-V1 (`V1_OPERATIONALIZED_CONTRACTS.md`), pragul de retrace 50% e outcome-ul măsurat pe fereastra Londra (20 bare, 08:00→13:00), exact ca la E001 — nu setup-ul. **Intrare propusă:** pe prima bară după închiderea ferestrei Frankfurt (bara 08:00 UTC), condiționat de mișcarea agresivă deja confirmată (`|Δ|≥1,5×ATR14` la 06:00, per V1). **Direcție: OPUSĂ mișcării Frankfurt** (pariu pe reversal/retrace, nu pe continuare). Direcția de reversal față de extinderea pre-market e cea confirmată de CTO — timing-ul de intrare de mai sus e propria mea corecție, marcată explicit ca atare.
- ~~**E004** (`movement_profile` continuation/reversal/stall): intrare la prima bară după cea pe care clasificarea deja înghețată rezolvă...~~ **SUPERSEDED — text V0/V1 verificat acum, nu presupus:** E004-V1 = "First Post-US-Open FVG Follow-Through" (`V1_OPERATIONALIZED_CONTRACTS.md`) — nu e un `movement_profile` generic. Populație: primul FVG (imbalance 3 bare) al zilei a cărui bară-mijlocie cade în fereastra 13:30–15:30 UTC (deschidere COMEX RTH). **Intrare corectă:** pe prima bară după formarea completă a FVG-ului (imediat după închiderea celei de-a 3-a bare a pattern-ului) — nu la rezolvarea clasificării `movement_profile` (aceea e outcome-ul, orizont 50 bare). **Direcție = polaritatea FVG-ului** (gap bullish → long, gap bearish → short). **Mapare binară (decizie CTO):** continuation = mișcare în direcția polarității FVG-ului (impulsul care a format gap-ul); reversal = direcția opusă. **Metrică suplimentară, omisă din original, adăugată acum:** `fill` — binar separat, prețul reintră în zona FVG `[zone_low, zone_high]` în interiorul orizontului de 50 bare — se raportează alături de rezultatul de tranzacție (win/loss/R), nu combinat cu el.

**Cel mult o intrare per sesiune/zi per contract**, dacă evenimentul structural e legat de sesiune (cazul aparent pentru toate trei).

### 2. Stop — fix, cu variantă de senzitivitate, nu doi candidați egali

**Oficial: 40 pips = 4,00 dolari.** Variantă de senzitivitate, raportată alături, nu ca test separat: **50 pips = 5,00 dolari** — același rol ca V-A/V-B din `MIN_STOP_FLOOR_PREREG.md`. Aleg 4,00 ca oficial pentru că e cifra pe care ai calculat-o deja explicit (cost/efect ≈10% din R) — o schimbare acum ar rupe acel calcul deja făcut.

**Verificare de siguranță față de podeaua de execuție (relevantă după cazul celor 47 REJECTED):** podeaua `max(2×spread, 5×tick, 0,10×ATR)` are componenta dominantă `5×tick`=0,50 pe M15/M5. Stopul de 4,00-5,00 e de **8-10× mai mare** decât podeaua — eșecurile de tip `gap_stop` care au ucis cele 47 nu sunt așteptate ca problemă structurală aici. Se verifică empiric, nu se presupune, dar nu e motiv de îngrijorare a priori.

### 3. Țintă — RR 1:1 și RR 1:2, raportate separat

~~Două ținte, niciodată combinate într-un singur rezultat: **8,00 dolari (RR 1:1)** și **8,00-10,00 dolari (RR 1:2...)**~~ **SUPERSEDED — eroare aritmetică, corectată:** RR = țintă/stop, deci RR 1:1 înseamnă țintă EGALĂ cu stopul, nu 8,00.

| Stop | RR 1:1 (țintă) | RR 1:2 (țintă) |
|---|---|---|
| 4,00 (oficial) | **4,00** | **8,00** |
| 5,00 (senzitivitate) | **5,00** | **10,00** |

Fiecare combinație (contract × stop-oficial-sau-variantă × RR) raportată ca rând propriu, niciodată agregată. Familia de 6 teste primare din §6 (3 contracte × 2 RR) rămâne neschimbată ca număr — doar valorile țintă erau greșite, nu structura familiei.

### 4. Regula de tie-break same-bar

**Convenția implicită (worst-case, stop-first): neschimbată**, aceeași convenție deja pre-înregistrată în laborator (`mstrat.py`, stopul verificat înaintea țintei). **Obligatoriu, per §7c din `STATISTICIAN_M5_INDETERMINACY_THRESHOLD_SPEC_v1.0.md`:** raportare sub bracket complet — worst-case (stop-first) și best-case (target-first) — pentru orice combinație a cărei stare de profitabilitate depinde calitativ de tratament. Dat fiind Partea 1 de mai sus (nedeterminare așteptată RARĂ), acest bracket ar trebui să arate stabilitate — dacă NU arată, e un semnal că interpretarea din Partea 1 nu se confirmă empiric pentru acest profil specific, de raportat, nu de ignorat.

### 5. Costul — 0,40, aplicat identic

`cost_round_trip = 0,4 puncte` (`STATISTICIAN_NET_OF_COST_OUTCOME_DEFINITION_v1.0.md`), scăzut din pnl brut înainte de împărțirea la risc, identic pentru toate combinațiile. La stop 4,00: cost/risc = 10% (calculul tău, confirmat). La stop 5,00: cost/risc = 8%.

### 6. Corecție de testare multiplă — familia se declară acum

Familia primară: 3 contracte × 2 RR = **6 teste primare** (stopul-variantă de 5,00 e senzitivitate, nu un test suplimentar în familie). Corecție BH-FDR obligatorie peste această familie de 6, pragul declarat înainte de a atinge date, consecvent cu convenția deja stabilită în laborator — nu Bonferroni simplu, dat fiind corelația probabilă între cele trei contracte (aceeași fereastră de piață, posibil aceeași populație parțial suprapusă).

### 7. Statistic-testul — RATIFICAT [v1.2], omisiune reală în v1.1

Flow A a semnalat corect că v1.1 nu specifica testul și a ales, declarat explicit înainte de a-l aplica tacit, un **binomial exact, one-sided**, contra pragului de break-even ajustat la cost. **Ratific — vezi `STATISTICIAN_STRUCTURAL_V1_FINAL_VERDICT_v1.0.md` pentru raționamentul complet.**

- **Prag:** `w* = (1 + cost/S) / (RR + 1)` — la stop 4,00/cost 0,4: RR1:1 → 0,550; RR1:2 → 0,367. La stop 5,00: RR1:1 → 0,540; RR1:2 → 0,360.
- **Test:** `P(X ≥ k | n, w*)` binomial exact (ex. `scipy.stats.binom.sf(k-1, n, w*)`) — NU aproximare normală, validă indiferent de n.
- **Familia FDR (§6, neschimbată ca număr = 6):** numărătorii se pun laolaltă (pooled) peste toate regimurile testate pentru fiecare pereche contract×RR, ÎNAINTE de test — regimul e o defalcare descriptivă de robustețe, nu o multiplicare a testelor (consecvent cu regula deja stabilită pentru programul celor 4 regimuri).
- **Condiție de valabilitate, pentru orice reutilizare viitoare a acestui test sub acest contract:** asumpția de independență (Bernoulli iid) e rezonabilă la ≤1 intrare/sesiune/zi per contract — dacă o suită viitoare are frecvență mult mai mare sau poziții suprapuse, independența trebuie reexaminată înainte de a reutiliza testul necondiționat.

---

**Nu am atins date, nu am implementat. Statistician se oprește aici.**
