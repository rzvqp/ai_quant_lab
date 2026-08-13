# STATISTICIAN — ÎNGHEȚAREA DEFINIȚIEI T05 ȘI CORECȚIA DE AN PARȚIAL

**Document ID:** STAT-T05-FREEZE-AND-PARTIAL-YEAR-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Regim:** PAUZĂ pe cercetare. Acesta e artefact DOCUMENTAR — nicio rulare de strategie, nicio desigilare, niciun test nou.
**Verificare de sursă:** `CANDIDATE_QUEUE.md` (rândul CAND-T05), `git log` pe `edge_research/flowb_strategies.py`, și acoperirea calendaristică măsurată pe barele DEJA livrate de loader.

---

# PARTEA 0 — PAUZA, CONFIRMATĂ EXPLICIT

```
NU pornesc:  reevaluarea T05 · leaderboard · desigilare · teste economice noi ·
             re-rularea completă · descompunerea cost-vs-populație · verdictul CAND-0037
SE PĂSTREAZĂ neatinse:  registrul de expunere la date · numărătoarea unică a lui m (= 20) ·
             formalizarea RECENT_PRIMARY (v2.7.71) · cele PATRU blocuri oficiale
Se reiau după MANDATE_2_PASS.
```

**Ce urmează e aritmetică pe date deja livrate și transcriere din artefacte deja publicate. Nu consumă nimic.**

---

# PARTEA 1 — CORECȚIA DE AN PARȚIAL. Măsurată.

**Fereastra e `2022-12-16 10:45 → 2025-10-12 23:15`. Acoperirea reală, pe barele livrate:**

```
  an     bare   % din fereastră   zile tranz.   perioada efectiv observată      EV net raportat
2022      873        1,31%             12       2022-12-16 → 2022-12-30            +0,64
2023   23.563       35,38%            309       2023-01-02 → 2023-12-29            +0,38
2024   23.736       35,64%            313       2024-01-01 → 2024-12-31            +0,34
2025   18.431       27,67%            243       2025-01-01 → 2025-10-12            +0,45
                    ────────
total  66.603      100,00%            877
```

> # **„4/4 ani pozitivi" înseamnă: DOUĂ ani întregi, un an la 78%, și un CIOT DE 12 ZILE DE TRANZACȚIONARE.**
>
> **Iar ciotul de 12 zile — 1,31% din fereastră — poartă cea MAI MARE cifră dintre cele patru: +0,64. Cel mai bun „an" din palmares se sprijină pe o cincizecime din dovezi.**

**Consemnez că aceasta e EXACT clasa de artefact pentru care am înlocuit „7/8 ani pozitivi" cu stabilitatea pe episoade (v2.7.69). Nu e o eroare nouă — e vechea eroare, mutată în fereastra nouă. Anul calendaristic nu e o unitate de dovadă; e o unitate de calendar.**

```
REGULĂ DE RAPORTARE, obligatorie de acum pe fereastra recentă:
   orice afirmație „k/n ani" se raportează ÎNSOȚITĂ de perioada efectiv observată, zilele de
   tranzacționare și fracția din fereastră, PER AN. Un an fără aceste trei câmpuri nu se numără.
   2022 se etichetează PARTIAL_STUB (< 5% din fereastră), nu „an".
```

**Ce NU pot completa fără să încalc pauza: numărul de TRANZACȚII per an. Cifrele de EV există deja publicate în coadă și le transcriu; numărătorile de tranzacții nu sunt publicate, iar a le produce ar însemna rularea strategiei. Se transcriu de proprietar în înregistrarea înghețată — nu le invent.**

---

# PARTEA 2 — DEFINIȚIA T05, ÎNGHEȚATĂ

**Înghețarea e POSIBILĂ: codul e comis la `4f3396c` (`edge_research/flowb_strategies.py`), deci `code_version` are o referință imuabilă. Dacă ar fi fost necomis, înghețarea ar fi fost imposibilă — nu se poate îngheța o definiție al cărei cod n-are versiune.**

```
strategy_id          CAND-T05
strategy_version     v1 (prima înghețare; orice modificare ⇒ id NOU, nu versiune nouă a acestuia)
code_version         4f3396c · edge_research/flowb_strategies.py
regim                TREND_UP  (etichetă de router; definiția ei atârnă de regula de precedență
                     ne-pre-înregistrată încă — vezi v2.7.69, MATERIAL)
teza                 pullback LONG în TREND_UP, cu stop structural LARG la swing-low
entry / stop /       DE TRANSCRIS VERBATIM din 4f3396c de către proprietar.
target / holding     NU le transcriu din memorie sau din rezumat — o definiție înghețată
                     dintr-o parafrază nu e înghețată.
data_exposure        PRIMARY_RECENT_WINDOW 2022-12-16 10:45 → 2025-10-12 23:15
                     4 blocuri oficiale · holdout SIGILAT și neatins
                     ⚠ perechea (fereastră, candidat): fereastra a fost VĂZUTĂ la screening,
                       deci pentru T05 NU e out-of-sample. Vezi v2.7.71.
hypothesis_lineage   T03 (fat-tail dependent) → T05 = ipoteză NOUĂ cu stop lărgit, id NOU.
                     T03 rămâne neatins și rămâne NUMĂRAT (familia e monotonă).
run_hash             ABSENT. Cerut de contract (v2.7.66): sha256(config_hash ‖ data_identity),
                     cu geometry_mode, s2/r3 mode și mde pre-calculat. Fără el, rezultatele T05
                     sunt NON-COMPARABILE prin tip cu orice altceva.
cifre raportate      EV_net recent +0,389 · PF 1,63 · trimmed_top1 +0,202 · best_share 0,14 ·
(transcrise din      DD −26R · HISTORICAL_TRANSFER +0,120 cu DD −99R
CANDIDATE_QUEUE.md)  status PROVISIONAL_SCREENED
```

> **Toate cifrele de mai sus sunt PROVIZORII prin propria lor etichetă și au fost produse înainte de contractul canonic. Le transcriu ca înregistrare, NU ca rezultat validat. Înghețarea documentează CE s-a măsurat și CU CE; nu conferă nimic.**

---

# PARTEA 3 — DOUĂ LUCRURI DE CONSEMNAT

```
1. `m_total = 6` apare în coadă, lângă lotul T0x. Numărătoarea de FAMILIE pe care o țin eu
   e m = 20 (v2.7.71). Nu afirm că una e greșită — probabil sunt contoare DIFERITE (un lot
   local vs familia de multiplicitate). Dar dacă cineva le confundă, corecția BH se aplică
   la 6 în loc de 20 și pragul e de 3,3 ori prea permisiv. SE RECONCILIAZĂ ÎNAINTE de orice
   test formal, nu după. Nu consumă nimic: e o clarificare de contract.
2. T05 raportează HISTORICAL_TRANSFER pozitiv (+0,120, DD −99R). Sub v2.7.71 acela e un
   estimand DISTINCT pe populație DISJUNCTĂ — se raportează separat, nu se mediază cu
   recentul, și nu contribuie la promovare. Consemnat ca deja conform.
```

---

# PARTEA 4 — DESCHIS

```
BLOCKING      niciunul care să blocheze integrarea AI Trader.
MATERIAL      entry/stop/target/holding se transcriu VERBATIM din 4f3396c — înghețarea nu e
              completă până atunci.
MATERIAL      `run_hash` absent pentru T05. Fără el, non-comparabil prin tip.
MATERIAL      numărul de tranzacții per an lipsește; se transcrie de proprietar, nu se produce.
MATERIAL      `m_total=6` vs familia m=20 — se reconciliază înainte de orice test formal.
LIMITATION    2022 e PARTIAL_STUB: 12 zile, 1,31% din fereastră, și poartă cea mai mare cifră.
              „4/4 ani" nu se raportează fără cele trei câmpuri de acoperire.
LIMITATION    eticheta TREND_UP atârnă de o regulă de precedență încă ne-pre-înregistrată.
```

**Nu cere: gate nou, framework nou, metrică nouă, nicio rulare.**

---

**Manifest:** `config/split_manifest.json` v2.7.72, secțiunea `t05_freeze_and_partial_year_v2_7_72`.
