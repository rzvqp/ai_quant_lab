# STATISTICIAN — VERDICT: CORPUL LEGACY 428 ATR, PERSISTENȚĂ PE TREI REGIMURI (Mandat 3.7 revizuit)

**Document ID:** STAT-LEGACY428-PERSISTENCE-VERDICT-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician
**Verificare de sursă:** citit direct `docs/THREE_REGIME_PERSISTENCE_RESULT_v1.0.md` (commit `7927441`), nu doar cifrele din mesaj. Confirmate exact: 3/7/51/367 (sumă 428); 74 rânduri profitabile peste regimuri, 30 (41%) wo1≤0, deci 44 wo1>0; S2 corecție net1=2.797/wo1=−0.031; S17 bull net1=4.962/wo1=−0.037; S17 corecție net1=23.869/wo1=−0.064; cei doi S2 identici (duplicat `lb` inert pe `pdh_pdl`); trei regimuri, confirmat independent din `changelog_v2_4` al manifestului.

---

## SARCINA 1 — ETICHETARE GRANULARĂ

### 367 → `REJECTED — ZERO_ALPHA_BASE_RATE`

**Scop, delimitat precis:** neprofitabile (nu satisfac n≥25 & sumR>0 & exp>0 & pf>1,00) în **toate cele trei regimuri testate**, la **această parametrizare înghețată** (combinația specifică sesiune/direcție/stop/exit per ID), cu **R (pnl/risc ATR-scalat) ca variabilă de rezultat**. **NU** înseamnă că familiile subiacente (S1-S51, orice concept de piață pe care se bazează) sunt infirmate definitiv — o parametrizare diferită (alt stop, alt exit, altă sesiune) în interiorul aceleiași familii, sau aceeași parametrizare pe alte regimuri, rămâne netestată de acest rezultat specific.

**Precizare metodologică obligatorie:** eticheta se bazează pe **screening-ul descriptiv** (pragul de profitabilitate brut n/sumR/exp/pf), nu pe un test statistic formal per ipoteză cu p-value — exact cum a specificat Research Lab ("măsurătoare descriptivă, nu test de ipoteză"). Nu confund asta cu rigoarea testului binomial de la §7 (E001/E002/E004), care avea p-value și corecție BH-FDR. Aici, `REJECTED` reflectă un fapt structural (eșec total, în toate regimurile, la un prag minim de profitabilitate) — decisiv ca DESCRIERE, dar nu echivalent evidențial cu un test de semnificație per-celulă.

### 58 → `REJECTED — REGIME_PERSISTENCE_FAILURE`

**Scop:** profitabile într-unul (51) sau două (7) din cele trei regimuri, dar eșuează criteriul de persistență globală (profitabilitate în TOATE regimurile testate). Aceasta **NU** infirmă rezultatul specific din regimul/regimurile unde AU fost profitabile — acel rezultat local poate fi real. Eticheta spune specific: **nu generalizează pe diversitatea de regim testată** — o pretenție de "edge robust la condiții de piață diferite" nu se susține pentru aceste 58, indiferent de ce se întâmplă într-un singur regim favorabil.

### 3 → `REJECTED — EXTREME_CONCENTRATION_FRAGILITY_wo1`

**Scop:** profitabile agregat în toate cele trei regimuri, dar **cel puțin un regim e integral o singură tranzacție** (wo1≤0 — fără cea mai bună tranzacție, acel regim devine net-negativ). Nu infirmă mecanismul de piață subiacent (breakout eșuat la PDH/PDL pentru S2; respingere la pw_high pentru S17) — infirmă pretenția că **dovada actuală** susține un edge distribuit, robust. Fiecare din cele două strategii distincte (vezi mai jos) e, în cel puțin un regim, o poveste de "o tranzacție mare", exact genul de bază evidențială insuficientă deja stabilită la S18 (net1=0,474 acolo; aici până la 23,9).

**Granularitate, consemnată dar nu schimbă eticheta:** S2 e distribuit în 2/3 regimuri (bear wo1=+0,033, bull wo1=+0,033) și concentrat doar în corecție (wo1=−0,031, net1=2,80). S17 e distribuit doar în 1/3 (bear wo1=+0,059) și concentrat în AMBELE celelalte (bull wo1=−0,037 net1=4,96; corecție wo1=−0,064 net1=23,9) — S17 e structural mai fragil decât S2, deși ambele primesc aceeași etichetă (niciunul nu satisface "distribuit în toate trei").

## DOUĂ FAPTE DE CONSEMNAT SEPARAT

**1. Duplicatul S2.** Cei doi `S2` din leaderboard-ul de persistență (`92481423c6b8`, `a53441048c3c`) sunt IDENTICI — `lb` (lookback) e inert structural când `ref=pdh_pdl` (o referință de nivel fix, care nu depinde de nicio fereastră de lookback), deci orice valoare `lb` produce tranzacții bit-identice. **Cei "3 persistenți" sunt de fapt 2 strategii distincte: un S2 (pdh_pdl) și un S17 (pw_high), ambele exit=time.** Acest fapt nu e izolat — auditul complet (`docs/DUPLICATE_AUDIT_v1.0.md`, commit `80fb243`, livrat cât timp scriam specificația de la Sarcina 2) confirmă că e **sistematic**: din cele 428 ATR, **360 sunt distincte, 68 redundante (15,9%)**; din întregul corp de 1972, **1440 distincte, 532 redundante (27,0%)** — 87% din cazuri din exact același tipar (`lb`/`liq_lb` inert când referința nu e `swing`). Etichetele 367/58/3 de mai sus rămân pe ID brut, cum a cerut mandatul — dar orice corecție de testare multiplă viitoare pe acest corp de 428 trebuie să folosească **360**, nu 428, ca `m` (regula înghețată în `PROJECT_AUDIT.md` §D/§F, D11).

**2. Trei regimuri, nu patru.** Testarea s-a făcut pe bear/bull/correction (2011-2021, descoperire M15_v2). Regimul 2022-2026 e exclus ca `SAME-WINDOW-RESAMPLED` (fereastra M15 legacy care a informat parametrizarea V1/S1-S51) — confirmat independent atât în acest document cât și în `changelog_v2_4` al manifestului (`ai_quant_lab-alpha-automation`). Consemnat aici ca fapt de sine stătător, nu doar reafirmat în context.

---

## ÎNTREBAREA TA SEPARATĂ — rata de bază 37×

**Răspuns: aproape sigur artefact de dependență, din DOUĂ mecanisme distincte, niciunul necesitând vreo pretenție de edge real. Nu construiesc o corecție formală acum — n e prea mic ca să merite, exact cum ai spus — dar înregistrez principiul ca regulă permanentă pentru orice lucrare viitoare la scară mai mare.**

**Mecanismul 1 — heterogenitate, nu independență, între regimuri PENTRU ACEEAȘI STRATEGIE.** Calculul `428 × p³` presupune că "profitabil în regim X" e o monedă aruncată independent, cu aceeași probabilitate `p`, pentru fiecare regim al FIECĂREI strategii. Fals prin construcție: o strategie are o rată latentă proprie (μ_i), stabilă ca proprietate a regulii ei — nu o probabilitate identică 5,8% pentru toate cele 428. Strategiile cu μ_i mai mare au șanse corelate, nu independente, să treacă pragul în MAI MULTE regimuri simultan. Sub eterogenitate pură (fără nicio pretenție de edge cauzal — doar strategii diferite ca "calitate" brută/suprapotrivire), coada "profitabil în toate trei" e ÎNTOTDEAUNA mai groasă decât ar prezice `p³` independent — e semnătura așteptată a eterogenității unei populații, nu dovadă de cauzalitate.

**Mecanismul 2 — cele 428 nu sunt 428 unități independente.** Duplicatul S2 confirmat mai sus e cea mai extremă formă a asta (corelație = 1,0), dar fenomenul e mai larg: multe din cele 428 sunt variații combinatorii (aceleași intrări, stop/exit diferite) ale unui semnal comun — exact tiparul deja găsit la S18 ("3 semnale × 2 ieșiri, nu 6 teste independente"). Corelația parțială între ID-uri, chiar fără duplicare exactă, reduce numărul EFECTIV de strategii independente cu mult sub 428 — ceea ce face `428 × p³` o subestimare și mai mare a numărului așteptat de "persistenți" doar din corelație.

**De ce nu construiesc o corecție numerică acum:** cu n=2-3 persistenți reali, nicio metodă (naivă sau corectată) nu poate distinge "corelație" de "edge real" — puterea statistică e efectiv zero la acest eșantion. Ar fi efort vărsat pe o întrebare pe care datele nu o pot răspunde, indiferent de rigoare.

**Ce înregistrez ca regulă permanentă, pentru scară mai mare, viitoare:** orice test formal viitor de "persistență de regim e semnificativă" (dacă se încearcă vreodată, pe un corp mai mare/mai divers) TREBUIE să folosească un model nul care ține cont de AMBELE surse de corelație (eterogenitate cross-regim + corelație combinatorie cross-ID) — niciodată calculul naiv independent `m × p^k`. Dedublarea (Sarcina 2) rezolvă DOAR forma extremă (corelație=1,0) — corelația parțială (semnal comun, ieșire diferită) rămâne, chiar după dedublare, o problemă separată, nerezolvată aici.

---

**Nu am atins date, nu am executat nimic. Statistician se oprește aici.**
