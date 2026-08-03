# STATISTICIAN — PROTOCOALE STATISTICE, LOTUL RT-OPS-A-0001 (CAND-0001/0002/0003/0007)

**Document ID:** STAT-BATCH-A-0001-PROTOCOL-SPEC-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Primul lot procesat sub OPERATIONAL MODE.** Verificat direct: `CANDIDATE_QUEUE.md` (`alpha-automation-v1`, comitul `bcc0b21`) și `red_team/policy_reviews/RT-OPS-A-0001_batch.md` — patru candidați cu `SURVIVED_RED_TEAM_A`: CAND-0001 (PDH-PDL), CAND-0002 (Compression-Expansion-Breakout), CAND-0003 (FVG-CE50-Reaction), CAND-0007 (Level-FVG-Confluence). Citite integral cele patru politici (`POLICY_PDH_PDL_v1.md`, `POLICY_COMPRESSION_EXPANSION_v1.md`, `POLICY_FVG_REACTION_v1.md`, `POLICY_LEVEL_FVG_CONFLUENCE_v1.md`). **Nu modific nicio politică. Nu execut teste. Nu aleg parametri după rezultate — parametrii de mai jos sunt fie convenții deja stabilite în laborator, fie derivați ÎNAINTE de a vedea vreun rezultat.**

---

## Limitarea comună, care se aplică TUTUROR celor patru — declarată explicit, nu ocolită

**Partea B (risc: SL/exit/management) e UNSPECIFICATĂ la toate patru — un gol la sursă, nu al meu de rezolvat azi.** Fiecare politică o rutează separat, ca "specification request" — un task DIFERIT de cel de azi (ratificarea unei metode structurale de risc, nu definirea protocolului statistic). **Consecință directă: niciun test nu poate fi EFECTIV RULAT până Partea B nu e rezolvată separat** — protocoalele de mai jos sunt complete metodologic (definesc `net_R` generic, testul, familia, criteriile), dar rămân neexecutabile până există o metodă de risc structural ratificată. Notez asta ca precondiție standing pentru toate patru, nu o rezolv azi.

## Familia — fixată ACUM, pentru tot lotul, motiv explicit

**Familia = 4** (CAND-0001, 0002, 0003, 0007 împreună) — nu patru familii separate de 1. Motiv: toți patru au apărut din ACEEAȘI rulare de producție continuă ("Alpha Discovery"), pe ACELEAȘI date de descoperire, evaluați împreună de Red Team în ACELAȘI lot (`RT-OPS-A-0001`) — exact criteriul deja aplicat consecvent în acest laborator ("o privire asupra acelorași date merită aceeași precauție, nu mai puțină," indiferent dacă mecanismele diferă). **CAND-0007 rămâne în ACEEAȘI familie, nu una separată**, deși testul lui are o formă diferită (vezi mai jos) — corecția BH-FDR se aplică pe p-value-uri, indiferent de forma nulei fiecăruia.

## Elemente comune tuturor celor patru protocoale

```
regimes_permitted  = cele 3 deja stabilite (bear 2011-08→2015-12, bull 2015-12→2020-07,
                      corecție 2020-07→2022-10) — convenție reutilizată, nu aleasă azi
min_trades         = N_MIN=25/regim, aceeași convenție universală — sub prag, celula
                      SUPRIMĂ cifrele (nu doar le etichetează), raportează doar n+INSUFFICIENT_N
oracol             = WP-5' block_bootstrap, L>=28, pe net_R (odată ce Partea B există)
corecție           = BH-FDR, α=0,05, peste familia de 4
holdout            = sigilat, neatins — neschimbat, indiferent de rezultat
walk-forward       = 2 pliuri, fereastră EXPANSIVĂ, folosind granițele de regim deja stabilite
                      (nu o fereastră arbitrară nouă):
                      Pliul 1: antrenare=bear, testare=bull
                      Pliul 2: antrenare=bear+bull, testare=corecție
                      Raportat per pliu, niciodată colapsat într-o singură cifră
```

---

## CAND-0001 — PDH/PDL

**H0:** `mean(net_R) <= 0`, pe declanșatoarele PDH+PDL puse laolaltă (raportate și separat PDH vs PDL).

**Control obligatoriu — W-conf, rezolvat prin reutilizarea metodologiei deja stabilite:** null-ul simplu NU e suficient — **reutilizez explicit șablonul în trei brațe deja stabilit la OBDZ** (brațul A = atingerile reale PDH/PDL; brațul B = control placebo, potrivit pe SESIUNE ȘI pe distanța-până-la-nivel, aceeași metodologie de matching Swing/StructureLabel deja folosită). Fără acest control potrivit, nu putem separa "nivelul contează" de "orice bară aliniată pe sesiune, la distanță similară, s-ar fi comportat la fel."

**W-sel, consemnat ca limitare, NU corectat cu o cifră inventată:** cifrele exploratorii citate în politică (winrate 0,435@n=356, 4/4 sesiuni, 6/7 ani) sunt explicit "1-din-9" — PDH/PDL a fost UNA din nouă construcții de nivel-referință scanate informal înainte de a ajunge aici. **Nu inventez un factor de corecție "9" fără să știu ce erau celelalte opt** — consemnez asta ca o LIMITARE OBLIGATORIE DE RAPORTAT, nu o corecție numerică improvizată: orice rezultat pe CAND-0001 trebuie să declare explicit acest "1-din-9" ca risc de selecție separat de familia formală de 4.

**W-ovl:** diagnostic descriptiv OBLIGATORIU (nu consumă familie) — fracția de suprapunere între declanșatoarele PDH/PDL (acest candidat) și declanșatoarele CAND-0007 (confluența) — raportată, nu testată formal.

**W-e010, semnalat ca AMBIGUU, nu rezolvat prin ghicire:** referința Red Team la o legătură cu E010 nu are un corespondent clar în construcția PDH/PDL (`compute_prior_day_levels`/`detect_level_touches` nu citează E010 direct). **Nu presupun ce înseamnă și nu-l rezolv azi** — îl predau către VE ca punct de clarificare necesară de la Red Team, exact disciplina aplicată la patch-ul "_scan_reactions" din revizia MK-01/MK-02.

**Criteriu de respingere:** BH-FDR peste familia de 4, α=0,05, PE PRAGUL NULEI de mai sus (nu doar zero — trebuie să bată controlul placebo potrivit).

## CAND-0002 — Compression-Expansion-Breakout

**H0:** `mean(net_R) <= 0`, pe declanșatoarele de expansiune imediat după o bară comprimată.

**Limitare obligatorie, nu re-derivată azi:** riscul de "ancorare arbitrară" al compresiei (deja dezvăluit — percentila, fereastra de 460, granularitatea măsurii sunt alegeri de definiție, nu ancorate la un consumator, riscul "zece variante plauzibile" redus, NU eliminat) **rămâne o condiție interpretativă permanentă a acestui rezultat, nu ceva de rezolvat aici** — re-derivarea definiției de compresie ar fi o re-litigare a unei primitive deja ratificate, în afara scopului de azi. **Orice variantă alternativă de compresie (altă percentilă, altă fereastră, inegalitate strictă) cere propria ei pre-înregistrare separată** — aceeași disciplină aplicată deja la D2/D7 din revizia MK-01/MK-02.

**Criteriu de respingere:** BH-FDR peste familia de 4, α=0,05.

## CAND-0003 — FVG-CE50-Reaction

**H0:** `mean(net_R) <= 0`, pe primele atingeri CE-50 ale FVG-urilor neinversate.

**Fără controale suplimentare** — Red Team nu a semnalat nimic special ("cel mai curat din lot"). Protocolul standard, neschimbat, se aplică direct.

**Criteriu de respingere:** BH-FDR peste familia de 4, α=0,05.

## CAND-0007 — Level-FVG-Confluence

**H0, DIFERIT de celelalte trei — nu "mean(net_R)<=0", ci un null de VALOARE INCREMENTALĂ, cerut explicit de W-incr:** deoarece FIECARE declanșator CAND-0007 e și un declanșator CAND-0001 ȘI CAND-0003 (mulțime strict inclusă, confirmat de Red Team), întrebarea relevantă NU e "confluența are edge peste zero" — e **"a cere ambele condiții deodată bate mai bine decât UNA singură, pe EXACT ACELEAȘI bare unde ambele coincid."**

```
H0: mean(net_R_confluence) <= max(mean(net_R_CAND0001|aceleași bare), mean(net_R_CAND0003|aceleași bare))
```

Calculat pe subsetul EXACT de bare unde CAND-0007 declanșează, comparând construcția confluenței cu FIECARE construcție single-primitivă, restrânsă la ACELEAȘI bare (nu pe populația lor completă, mai mare) — un test potrivit, nu un null generic.

**W-dilate:** verificare mecanică obligatorie, predată VE — confirmă `dilate(before=k, after=0)` rămâne strict cauzal în implementare (after=0 respectat, nu doar declarat). `k` (toleranța de întârziere): **k=0 (aceeași bară, strict) ca specificație PRIMARĂ**, cu k∈{1,2} ca verificări de senzitivitate DEZVĂLUITE dinainte — nu alese după ce se vede care arată mai bine.

**Criteriu de respingere:** BH-FDR peste familia de 4, α=0,05, pe nula incrementală de mai sus.

---

## HANDOFF

**Validation Engine.** Pentru fiecare candidat: implementează Partea A (deja ratificată, neschimbată), NU rula nimic până Partea B nu e rezolvată (specification request separată, către Statistician). Pentru CAND-0001: clarifică W-e010 cu Red Team înainte de a-l considera rezolvat.

## Candidate Queue — actualizată

Cele patru rânduri (`CAND-0001/0002/0003/0007`) trec de la `SURVIVED_RED_TEAM_A → Statistician` la `STATISTICIAN_PROTOCOL_SPECIFIED (STAT-BATCH-A-0001) → Validation Engine (blocat pe Partea B)`.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.33 (commit `a13b01b`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
