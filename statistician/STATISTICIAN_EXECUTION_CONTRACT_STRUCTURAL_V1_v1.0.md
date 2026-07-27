# STATISTICIAN — CLARIFICARE + CONTRACT DE EXECUȚIE SEPARAT (E001/E002/E004)

**Document ID:** STAT-EXEC-CONTRACT-STRUCTV1-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Nu modifică V1-urile.** E001/E002/E004 rămân exact cum sunt înghețate — binare, fără R, fără stop. Acest document specifică un contract de execuție SEPARAT, care simulează tranzacții în jurul evenimentului lor structural deja înghețat, fără să-l redefinească.

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

- **E001** ("a atins extrema opusă"): intrare la prima bară după cea pe care se atinge extrema opusă (referința rămâne cea din V1 — range-ul Asia — doar ca reper de eveniment, NU ca definiție de R; R-ul vechi, lățimea range-ului Asia, e înlocuit integral de stopul fix de mai jos).
- **E002** ("reversal ≥50% retrace până la 13:00"): intrare la prima bară după cea pe care pragul de 50% retrace e satisfăcut, DOAR dacă evenimentul se declanșează înainte de 13:00 — altfel, nicio tranzacție în acea zi/sesiune.
- **E004** (`movement_profile` continuation/reversal/stall): intrare la prima bară după cea pe care clasificarea deja înghețată rezolvă într-una din cele trei categorii. **Notă:** nu am vizibilitate directă asupra textului V0 complet pentru E004 (nu l-am putut localiza în acest checkout) — regula de mai sus e generică și corectă indiferent de mecanica exactă de clasificare; execuția aplică regula pe definiția deja înghețată a Flow A, nu inventează una nouă dacă mecanica diferă de presupunerea mea.

**Cel mult o intrare per sesiune/zi per contract**, dacă evenimentul structural e legat de sesiune (cazul aparent pentru toate trei).

### 2. Stop — fix, cu variantă de senzitivitate, nu doi candidați egali

**Oficial: 40 pips = 4,00 dolari.** Variantă de senzitivitate, raportată alături, nu ca test separat: **50 pips = 5,00 dolari** — același rol ca V-A/V-B din `MIN_STOP_FLOOR_PREREG.md`. Aleg 4,00 ca oficial pentru că e cifra pe care ai calculat-o deja explicit (cost/efect ≈10% din R) — o schimbare acum ar rupe acel calcul deja făcut.

**Verificare de siguranță față de podeaua de execuție (relevantă după cazul celor 47 REJECTED):** podeaua `max(2×spread, 5×tick, 0,10×ATR)` are componenta dominantă `5×tick`=0,50 pe M15/M5. Stopul de 4,00-5,00 e de **8-10× mai mare** decât podeaua — eșecurile de tip `gap_stop` care au ucis cele 47 nu sunt așteptate ca problemă structurală aici. Se verifică empiric, nu se presupune, dar nu e motiv de îngrijorare a priori.

### 3. Țintă — RR 1:1 și RR 1:2, raportate separat

Două ținte, niciodată combinate într-un singur rezultat: **8,00 dolari (RR 1:1)** și **8,00-10,00 dolari (RR 1:2, în funcție de stopul folosit — 8,00 la stop 4,00; 10,00 la stop 5,00)**. Fiecare combinație (contract × stop-oficial-sau-variantă × RR) raportată ca rând propriu, niciodată agregată.

### 4. Regula de tie-break same-bar

**Convenția implicită (worst-case, stop-first): neschimbată**, aceeași convenție deja pre-înregistrată în laborator (`mstrat.py`, stopul verificat înaintea țintei). **Obligatoriu, per §7c din `STATISTICIAN_M5_INDETERMINACY_THRESHOLD_SPEC_v1.0.md`:** raportare sub bracket complet — worst-case (stop-first) și best-case (target-first) — pentru orice combinație a cărei stare de profitabilitate depinde calitativ de tratament. Dat fiind Partea 1 de mai sus (nedeterminare așteptată RARĂ), acest bracket ar trebui să arate stabilitate — dacă NU arată, e un semnal că interpretarea din Partea 1 nu se confirmă empiric pentru acest profil specific, de raportat, nu de ignorat.

### 5. Costul — 0,40, aplicat identic

`cost_round_trip = 0,4 puncte` (`STATISTICIAN_NET_OF_COST_OUTCOME_DEFINITION_v1.0.md`), scăzut din pnl brut înainte de împărțirea la risc, identic pentru toate combinațiile. La stop 4,00: cost/risc = 10% (calculul tău, confirmat). La stop 5,00: cost/risc = 8%.

### 6. Corecție de testare multiplă — familia se declară acum

Familia primară: 3 contracte × 2 RR = **6 teste primare** (stopul-variantă de 5,00 e senzitivitate, nu un test suplimentar în familie). Corecție BH-FDR obligatorie peste această familie de 6, pragul declarat înainte de a atinge date, consecvent cu convenția deja stabilită în laborator — nu Bonferroni simplu, dat fiind corelația probabilă între cele trei contracte (aceeași fereastră de piață, posibil aceeași populație parțial suprapusă).

---

**Nu am atins date, nu am implementat. Statistician se oprește aici.**
