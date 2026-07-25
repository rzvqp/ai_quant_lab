# STATISTICIAN — VERDICT: HOLDOUT CONTAMINATION, DC-0004
### Determinare formală, nu observație

**Document ID:** STAT-DC0004-HOLDOUT-VERDICT-v1.0
**Data:** 2026-07-25 · **Autor:** Statistician
**Statut:** Determinare metodologică formală. **Amendează Pachetul 3 (DC-0004) din `VALIDATION_ENGINE_HANDOFF_S002_v1.0.md`** — secțiunile 3, 5 și 8 ale acelui pachet sunt înlocuite de acest document până la o nouă decizie CEO. Nu s-a executat niciun test. Nu s-au modificat artefacte Alpha sau Red Team.

**Verificare de sursă (înainte de a construi pe ea):** finding-ul citat e real și l-am confirmat direct în document — provine din `ai_quant_lab/red_team/audits/RT-AUDIT-0002_ALPHA1.md` ("Red Team Research Audit #2 — Alpha #1"), §2, F3: *"The reserved holdout has been consumed by observation."* Nu e F3 din `RED_TEAM_PHASE1_REPORT.md` (acolo F3 e despre raportul R nedefinit al DC-0008 — un document diferit, cu propria numerotare F#, nelegat de acesta). Le tratez ca două seturi de findings distincte, nu le confund.

**Surse folosite:** `RT-AUDIT-0002_ALPHA1.md` (§0, F3, tabelul din §3 rândul DC-0004, I5); `DISCOVERY_CANDIDATE_INDEX.md` (26 rânduri, confirmat); `candidate_v1.md` + `metadata_v1.json` pentru DC-0019 până la DC-0026 (toate 8, citite direct pentru acest document).

---

## (a) Intervalul exact observat dincolo de cutoff

Din metadatele celor 8 candidați post-cutoff, ferestrele explicite de eveniment sunt:

| Candidat | Fereastra observată (UTC) | Dată replay |
|---|---|---|
| DC-0019 | 21:45 (vineri) → ~02:15 (luni) | 2025-10-24 → 2025-10-26/27 |
| DC-0020 | 17:45–20:30 | 2025-10-29 |
| DC-0021 | 14:00–16:45 | 2025-11-06 |
| DC-0022 | 14:30–19:45 | 2025-11-12 |
| DC-0023 | 13:00–21:00 | 2025-11-13 |
| DC-0024 | 11:45–16:30 (+ Addendum A citată în DC-0026 la ~154.665pt/~8h) | 2025-11-14 |
| DC-0025 | 15:00–16:45 | **2026-01-16** |
| DC-0026 | 23:00 → ~01:50 (+2h de chop post-eveniment) | **2026-01-28 → 2026-01-29** |

**Interval explicit confirmat:** de la **2025-10-24T21:45Z** (prima bară observată dincolo de cutoff, DC-0019) până la **~2026-01-29T01:50Z** (ultima bară explicit descrisă, DC-0026 + chop-ul ulterior) — aproximativ **97 de zile** de timp de replay.

**Notă importantă, nu presupunere ascunsă:** acesta e intervalul confirmat de **ferestrele explicit numite**. Metodologia Alpha (confirmată chiar de DC-0025: *"the standard 30-step `replay_step` batch"*, plus tiparul deja stabilit pre-cutoff de "~29 zile de replay, zero candidați noi" — zile parcurse și văzute, doar nedocumentate ca DC separat) susține puternic inferența că **întregul interval continuu** dintre aceste date a fost parcurs bară-cu-bară, nu doar cele 8 ferestre punctuale — zilele "liniștite" dintre ele au fost la fel de văzute, pur și simplu n-au produs un candidat. Această continuitate e o **inferență metodologică justificată**, nu un fapt citat literal din metadate — o marchez explicit ca atare.

Salt notabil: DC-0024 (2025-11-14) → DC-0025 (**2026-01-16**) e un salt de aproape două luni în timpul de replay, confirmând că Alpha a continuat să avanseze mult dincolo de fereastra inițial "redeschisă" de 6 candidați observată la Stage S001.

## (b) Mai are DC-0004 un test decisiv?

**Nu.** Testul decisiv, așa cum a fost specificat (confirmare oarbă pe un holdout neatins, post 2025-10-23T09:15Z), nu mai poate exista în forma promisă — nu poate fi "de-observat." Confirmat independent de determinarea Red Team (F3/I5, clasificat **MAJOR**, "ireversibil") și de propria mea verificare a metadatelor: fereastra rezervată a fost parcursă activ de Alpha, cel puțin din 2025-10-24 până în ~2026-01-29.

**Ce îl înlocuiește — design condiționat, în două ramuri, executabil de Validation Engine:**

### Ramura 1 — DACĂ există o coadă necontaminată confirmată
Dacă se confirmă (vezi §c) că datasetul se întinde dincolo de ultima bară observată (~2026-01-29) ȘI acea coadă nu a fost parcursă de Alpha:
- Se redefinește holdout-ul ca **exclusiv acea coadă necontaminată**, nu întregul interval post-2025-10-23.
- Se execută **exact același protocol de replicare strictă** deja specificat în Pachetul 3 al handoff-ului S002 (graniță zi UTC, 4 sesiuni fixe, definiția "prima depășire," familie Bonferroni empirică n≥25, K6 singur decisiv, one-sided, seed=7) — neschimbat, doar aplicat pe fereastra nouă, mai îngustă.
- **Condiție de oprire suplimentară:** dacă numărul de evenimente NY-up-reject disponibile în coada rămasă e sub pragul de putere deja calculat (~15-20), rezultatul se raportează ca INSUFICIENT, nu se forțează un verdict.

### Ramura 2 — DACĂ nu există nicio coadă necontaminată confirmabilă (sau e prea scurtă)
- DC-0004 **nu poate primi verdict STATISTICALLY ROBUST** în acest ciclu — plafonul maxim atins e **TESTABLE BUT INSUFFICIENT EVIDENCE**.
- Se execută în schimb o **extensie de robustețe in-sample**: re-rularea metodologiei matched-null pe fereastra observată (2025-10-24 → ultima bară), dar **etichetată explicit "extensie in-sample," niciodată "confirmare out-of-sample."** Rezultatul se raportează separat, alături de p-ul original (0.021/0.029), nu combinat cu el ca dovadă nouă independentă.
- Această ramură nu repară pierderea evidențială — doar evită să pretindă o confirmare oarbă care nu mai există.

**Care ramură se aplică:** nu pot decide singur — depinde de răspunsul la (c), pe care nu-l pot confirma din artefactele autorizate pentru această sarcină.

## (c) Există o fereastră necontaminată rămasă? — REZOLVAT, verificat direct din artefacte

Cele două fapte lipsă au fost furnizate de CEO și **verificate direct de mine în artefacte**, nu acceptate ca atare:

1. **Cursorul de replay al lui Alpha:** `research_log/SESSION_STATE.md` linia 15 — *"Replay OANDA:XAUUSD M15: pozitie finala **2026-05-15 20:59:59 UTC** (current_date 1778878799)"* — confirmat literal, epoch 1778878799 convertește exact la 2026-05-15 20:59:59 UTC. Textul "Reia de la..." e la **linia 3821** (nu 3800 — corecție minoră de citare, conținutul identic): *"Reia de la 2026-05-15 20:59:59 UTC pe M15, stepping manual (current_date confirmat 1778878799...)"*. Confirmat: Alpha a parcurs **106 zile** dincolo de ultima observație documentată în DC-0026 (~2026-01-29) fără să înghețe niciun candidat nou.
2. **Întinderea dataset-ului:** `data/market/OANDA_XAUUSD_M15.csv` — 84.152 linii totale (84.151 bare de date + 1 antet — diferență de o unitate față de cifra citată, neglijabilă). Prima bară: epoch 1671187500 = **2022-12-16 10:45:00 UTC**. Ultima bară: epoch 1783922400 = **2026-07-13 06:00:00 UTC** — confirmat exact.

**Concluzie (c): DA, există o coadă necontaminată.** Fereastra **2026-05-15T20:59:59Z → 2026-07-13T06:00:00Z**, aproximativ **59 zile calendaristice (~42 zile de tranzacționare)**, nu a fost parcursă de Alpha și nu a produs niciun candidat — e singura porțiune a dataset-ului rezervat inițial care rămâne, tehnic, neobservată.

### Calculul ratei empirice și proiecția pe coadă

Rata de bază pentru celula NY-up-reject (K6), din `candidate_v1.md` al DC-0004: n=42 evenimente pe fereastra de cercetare 2023-01-02 → 2025-10-23 (1025 zile calendaristice).

| Bază de calcul | Rată | Proiecție pe coada de 59 zile |
|---|---|---|
| Rata pe întreaga perioadă de cercetare (n=42/1025 zile ≈ 14.97/an) | 0.04098/zi | **≈2.42 evenimente** |
| Rata doar din jumătatea 2025 (n=13/294 zile ≈ 16.14/an, mai recentă) | 0.04422/zi | **≈2.61 evenimente** |
| Aceeași rată, bază zile de tranzacționare (~42 zile din cele 59) | echivalent | **≈2.42 evenimente** (identic, cum era de așteptat) |

**Rezultatul calculului meu: ≈2.4–2.6 evenimente proiectate.** Estimarea CEO (3-4) e ușor mai optimistă decât ce obțin eu din cele două baze de rată disponibile — semnalez diferența deschis, nu o ascund — dar **concluzia calitativă e identică sub ambele estimări**: cu mult sub pragul de putere de ~15-20 evenimente stabilit pentru K6. Chiar și estimarea cea mai favorabilă (4) rămâne la ~20-27% din pragul minim.

**Condiția de oprire proprie se declanșează.** Conform §8/§14(g) din pachetul DC-0004 al handoff-ului S002: eșantion sub pragul minim de putere → raportare **INSUFICIENT**, nu se forțează un verdict.

**Ramura 1 (test decisiv pe coada necontaminată) e declarată INDISPONIBILĂ** — nu pentru că fereastra n-ar exista (există, confirmat), ci pentru că e prea scurtă pentru puterea statistică necesară testului K6 preînregistrat. **Se trece la Ramura 2.**

## (d) Câte teste sunt de fapt în familia care necesită corecție comună acum?

Două probleme distincte, care nu se rezolvă cu același răspuns:

**Familia tehnică internă a testului DC-0004** rămâne, ca număr, **neschimbată** de contaminare: tot celulele sesiune×direcție determinate empiric (n≥25), până la 8 posibile (4 sesiuni × 2 direcții), din care ~6 au atins pragul in-sample. Contaminarea nu adaugă celule noi acestui test — corecția Bonferroni empirică rămâne exact cea specificată în handoff.

**Problema reală nu e o familie mai mare de teste — e o fereastră deja minată.** Cele 8 candidați noi (DC-0019…0026) au fost **derivați prin căutare discreționară** exact în fereastra care trebuia să rămână neatinsă pentru DC-0004. Asta nu e o problemă de "multe teste formale de corectat" — e o problemă de **selecție**: fereastra a fost deja cernută vizual, de un proces care caută activ fenomene notabile, și a găsit 8. Orice test formal rulat acum pe aceeași fereastră testează pe date care nu mai sunt "neexplorate," indiferent de câte celule corectăm Bonferroni. **A răspunde cu un singur număr mai mare (ex. "14" sau "16 teste") ar sugera greșit că problema se rezolvă printr-o corecție mai strictă — nu se rezolvă. Corecția family-wise repară riscul de fals-pozitiv din testări multiple formale; nu repară pierderea caracterului "orb" al datelor.**

Dacă se cere totuși un număr pentru contabilitate: familia formală a DC-0004 = ~6-8 celule (neschimbată); numărul de ipoteze noi derivate discreționar din aceeași fereastră = 8 (DC-0019…0026). Suma lor (14-16) nu e o "familie de corectat" în sensul statistic obișnuit — e mărimea contaminării, nu un prag Bonferroni de aplicat.

---

## Determinare finală

Cu (c) rezolvat, decizia nu mai e condiționată:

1. **Ramura 2 e calea operativă pentru DC-0004.** Specificația executabilă de VE (din secțiunea (b) de mai sus) rămâne cea din Ramura 2: re-rulare a metodologiei matched-null pe fereastra observată (2025-10-24 → ~2026-01-29, plus opțional zilele intermediare parcurse tacit), **etichetată explicit "extensie de robustețe in-sample," niciodată "confirmare out-of-sample."** Rezultatul se raportează separat de p-ul original (0.021/0.029 K6/K12), nu combinat cu el.
2. **Plafon de verdict:** DC-0004 rămâne la **TESTABLE BUT INSUFFICIENT EVIDENCE** — nu poate atinge STATISTICALLY ROBUST în acest ciclu, pentru că testul decisiv promis (confirmare oarbă pe holdout) nu mai poate fi executat în formă validă; coada rămasă (~2.4-2.6 evenimente proiectate) e structural incapabilă să servească acest rol.
3. Recomandarea #7 din `RT-AUDIT-0002_ALPHA1.md` ("Record the holdout's status explicitly in any candidate that names it as a decisive test") e adoptată implicit prin acest document.
4. **Coada de 59 de zile (2026-05-15 → 2026-07-13) nu trebuie cheltuită acum** pe un test subalimentat doar pentru că există — recomand fie acumularea ei ca parte a unei ferestre viitoare mai lungi (dacă replay-ul continuă și nu se mai creează candidați noi în acel interval), fie folosirea ei exclusiv ca o a treia sub-perioadă descriptivă în extensia de robustețe de la Ramura 2, nu ca test independent cu pretenție proprie de putere.

---

**Acest document amendează Pachetul 3 din `VALIDATION_ENGINE_HANDOFF_S002_v1.0.md`. Pachetele 1 și 2 (DC-0008, DC-0003) nu sunt afectate.**

**Statistician a finalizat determinarea. DC-0004 intră în Ramura 2, plafonat la TESTABLE BUT INSUFFICIENT EVIDENCE, până la apariția unei ferestre de date genuin noi și suficient de lungi.**
