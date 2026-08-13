# STATISTICIAN — ESTIMANDUL RECENT_PRIMARY, WALK-FORWARD, ȘI PRAGUL EȘECULUI ISTORIC

**Document ID:** STAT-RECENT-PRIMARY-ESTIMAND-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Verificare de sursă:** măsurat direct populația livrată de `edge_research/_common.load` în AMBELE repouri; citit `m15_v2_discovery_blocks` și `M15.discovery_range`.

---

# PARTEA 0 — O MĂSURĂTOARE CARE RĂSTOARNĂ PREMISA PUNCTULUI 2

**Mandatul spune: „Alpha a văzut deja o parte din 2022-2025. Nu se poate redenumi «OOS virgin»." Am măsurat ce livrează efectiv loader-ul pe care s-a făcut screening-ul:**

```
wp5b  _common.load("M15_v2")  →  130.491 bare
ani acoperiți:  2011 · 2012 · 2013 · 2016 · 2017 · 2018 · 2020 · 2021   ← EXACT OPT ani
prima bară 2011-07-26 16:30   ·   ultima bară 2021-09-03 20:45
bare în 2022-12 → 2025-10:  ZERO
```

> **Cei „7/8 ani pozitivi" ai lui CAND-0037 sunt EXACT acești opt ani. Fereastra recentă nu conține NICIO bară din populația pe care a fost screenat. Pentru linia de screening wp5b — care a produs CAND-0037 și fiecare membru al familiei — fereastra recentă e COMPLET NEVĂZUTĂ.**

**Dar nu declar „OOS virgin" global, fiindcă ar fi fals în cealaltă direcție: căutarea Flow-B din `alpha-automation` (`73b7b81`) a rulat pe loader-ul cu 4 blocuri, deci A VĂZUT fereastra.**

```
REGULA CARE DECURGE, și e mai precisă decât întrebarea:
   „OOS virgin" NU e o proprietate a FERESTREI. E o proprietate a PERECHII (fereastră, candidat).
   Se urmărește PER CANDIDAT, în REGISTRUL DE EXPLORARE (36): cine s-a uitat, pentru care
   candidat, când, și cu ce loader. O fereastră „curată" pentru un candidat e contaminată
   pentru altul, în același proiect, în aceeași zi.
```

## Autocorecție, a șasea — și e împotriva unei corecții pe care eu am emis-o

**La mandatul anterior am semnalat că marginea a treia transmisă (2021-09-03) diferă de manifest (2021-09-05 12:15). Măsurătoarea de mai sus arată că ULTIMA BARĂ LIVRATĂ e 2021-09-03 20:45.**

```
2021-09-05 12:15   `end_epoch` al blocului — LIMITA DECLARATĂ, exclusivă (cade în weekend)
2021-09-03 20:45   ULTIMA BARĂ efectiv livrată în bloc
Amândouă sunt „marginea dreaptă", sub definiții diferite. Pentru D-4, cenzurarea se aplică la
ULTIMA BARĂ, nu la limita declarată — deci cifra transmisă era cea OPERAȚIONAL CORECTĂ,
iar corecția mea era ea însăși pe lângă. O retrag.
```

---

# PARTEA 1 — ESTIMANDUL

```
RECENT_PRIMARY
   estimand:   E[net_R] pe populația de tranzacții generate de politică, cu declanșatoarele
               ei, în [2022-12-16 10:45, 2025-10-12 23:15) — al patrulea bloc discovery.
   AFIRMĂ:     media pe trecut a acestei politici, în acea fereastră, sub configurația
               declarată (BASE sau STRESS), cu costurile modelate și podeaua activă.
   NU AFIRMĂ:  performanță viitoare · că fereastra e reprezentativă pentru viitor ·
               că edge-ul e cauzal · nimic despre alte perioade.
```

```
HISTORICAL_TRANSFER    aceeași politică, aceeași configurație, pe cele TREI blocuri vechi.
                       Estimand DISTINCT, pe populație DISJUNCTĂ. Nu e o replicare —
                       e o întrebare de TRANSFER: se ține mecanismul în afara ferestrei?
COMBINED_DIAGNOSTIC    toate patru blocurile. DIAGNOSTIC. Nu decide promovarea singur.
```

> **INTERDICȚIA, executabilă: nu se calculează NICIODATĂ o medie ponderată care amestecă blocul recent cu cele vechi ȘI e raportată ca „rezultatul". Cele trei se raportează SEPARAT, cu `n` propriu fiecare. Motivul e mecanic: cele trei blocuri vechi au 130.491 bare față de 66.603 recente, deci o medie combinată e dominată 2:1 de perioada care NU e estimandul — și ar ascunde exact ce vrea directiva să vadă.**

---

# PARTEA 2 — WALK-FORWARD ÎN INTERIORUL FERESTREI

```
SCHEMA          origine rulantă (walk-forward), NU k-fold aleator: ordinea temporală e
                informație, iar amestecarea ei ar permite antrenarea pe viitor.
PURGING         din fiecare fereastră de antrenare se ELIMINĂ tranzacțiile a căror PERIOADĂ
                DE DEȚINERE se suprapune cu fereastra de test. Suprapunerea e la nivel de
                TRANZACȚIE (intrare→ieșire), nu de semnal.
EMBARGO         după fiecare fereastră de test, un interval mort înainte de reluarea
                antrenării. Lungime = orizontul de dependență MĂSURAT (~5 ore = 20 bare M15),
                rotunjit în SUS la o ZI calendaristică — aceeași unitate cu blocarea bootstrap,
                ca să nu apară un al doilea orizont concurent.
LOEO            leave-one-episode-out peste episoadele regimului țintă din fereastră.
RAPORTARE       per EPISOD și per AN, în interiorul ferestrei. Anul rămâne raportat;
                NU mai e criteriu de trecere.
```

## Regula de secvențiere, cu mecanismul care o face verificabilă

> **„Aceeași perioadă nu se folosește succesiv pentru optimizare și apoi pentru confirmare finală" e corectă, dar o regulă fără mecanism e o promisiune. Mecanismul: felia de CONFIRMARE FINALĂ se declară ACUM, se înregistrează în `run_hash`, și nu se atinge până la verdict. E un mini-holdout ÎN INTERIORUL ferestrei recente.**

```
COSTUL, spus deschis: fereastra are ~2,82 ani. Orice felie de confirmare o micșorează, iar
`n` și numărul de episoade scad proporțional. Dimensiunea feliei e o DECIZIE DE MODEL, se
pre-înregistrează, și se raportează ce rămâne DUPĂ tăiere — nu înainte.
```

---

# PARTEA 3 — CRITERIILE. Ce pot formaliza, și ce îmi lipsește.

**Mandatul spune „CEO a enumerat zece condiții". Cele zece NU sunt în acest mesaj și nu le-am găsit în niciun document pe care îl pot citi. NU LE INVENTEZ. Formalizez ce E enunțat aici; restul se formalizează când lista ajunge — o listă de zece condiții ghicite ar fi mai rea decât una absentă.**

**Ce e enunțat și se formalizează acum:**

```
NU se cere ca fiecare an recent să fie pozitiv.        ← anul iese ca poartă, rămâne ca raport
Se cere ca edge-ul să NU DEPINDĂ de un singur an sau episod.
```

**„Să nu depindă" devine mecanic, prin instrumente care există deja:**

```
(a) LOEO pe EPISOD      rezultatul rămâne pozitiv scoțând ORICARE episod          — portant
(b) LOEO pe AN          idem, pe an calendaristic din fereastră
(c) best_episode_share  concentrarea la nivel de EPISOD  — R10 ridicat cu un nivel
(d) best_trade_share, trimmed_top1_avg_R, n_trimmed      — R10, deja ratificat
(e) BASE și STRESS      amândouă                                                   — deja obligatoriu
Toate cinci trebuie să treacă. Un singur eșec ⇒ dependența e reală și e localizată de
instrumentul care a picat, ceea ce e mai informativ decât un scor agregat.
```

---

# PARTEA 4 — k_min = 5: SE TRANSFERĂ NESCHIMBAT. Dar fezabilitatea e o întrebare NOUĂ.

**Derivarea nu depinde de lungimea ferestrei — depinde DOAR de numărul de episoade: sub H0 un palmares perfect are probabilitatea `0,5^k`, iar la k=4 asta e 0,0625 > 0,05. Deci `k_min = 5` rămâne valabil identic în fereastra recentă. CONFIRM, nu ajustez.**

**Ce e nou e FEZABILITATEA, și e o aritmetică pe cifre verificate:**

```
fereastra recentă: 197.094 − 130.491 = 66.603 bare M15  ≈  724 zile de tranzacționare  ≈  2,82 ani
pentru k >= 5 episoade:  durata MEDIE a unui episod trebuie să fie <= ~145 zile ≈ 7 luni
```

> **Dacă regimul țintă are episoade mai lungi de ~7 luni, fereastra recentă NU POATE satisface criteriul de stabilitate — prin CONSTRUCȚIE, nu prin performanță. Asta trebuie știut ÎNAINTE de a fixa fereastra, altfel se fixează o fereastră în care criteriul e imposibil de îndeplinit.**

```
PRECONDIȚIE, obligatorie înainte de prima rulare: VE raportează numărul de episoade ale
regimului țintă în fereastră. k < 5 ⇒ RECENT_PRIMARY e ARCHIVE_INSUFFICIENT prin construcție,
și se spune ACUM, nu după.
```

---

# PARTEA 5 — EȘECUL ISTORIC CARE NU ELIMINĂ. Pragul, ca să nu devină scuză universală.

> **Scutirea nu are voie să fie o NARAȚIUNE. Trebuie să fie un PREDICAT MĂSURABIL — iar el există deja, fiindcă eticheta routerului se calculează CAUZAL și pe datele vechi.**

```
Pe fiecare bară istorică se calculează eticheta N1/Router, cu ACEEAȘI definiție pre-înregistrată.
   ELIGIBIL_ISTORIC = barele pe care routerul AR FI ACTIVAT strategia
   NEELIGIBIL       = restul
SCUTIREA se aplică EXCLUSIV pierderilor din NEELIGIBIL. Acolo strategia n-ar fi tranzacționat,
deci pierderea nu e a ei.
Pe ELIGIBIL_ISTORIC scutirea NU se aplică DELOC. Acolo condițiile erau aceleași.
```

## Pragul de respingere — nu e o constantă nouă, e triajul ratificat aplicat pe submulțime

```
Pe ELIGIBIL_ISTORIC se calculează ê_hist, se_hist, mde_hist (mde ÎNAINTE de test, ca la v2.7.65):

   ê_hist <= 0  ȘI  |ê_hist| >= mde_hist   →  ARCHIVE_NEGATIVE pe populația eligibilă istorică
                                              = RESPINGERE. Testul avea putere și a văzut opusul.
   |ê_hist| < mde_hist                     →  ARCHIVE_INSUFFICIENT. NU respinge, NU absolvă.

„REPETAT" se impune prin LOEO: respingerea trebuie să SUPRAVIEȚUIASCĂ scoaterii oricărui episod
istoric. Dacă dispare scoțând unul, nu e repetată — e un episod.
```

> **De ce asta închide scuza: dacă regimul țintă CHIAR nu exista în anii vechi, `ELIGIBIL_ISTORIC` e aproape gol, `mde_hist` e uriaș, și rezultatul e `ARCHIVE_INSUFFICIENT` — scutirea se aplică singură, prin lipsă de date, fără să fie invocată. Dacă regimul EXISTA și strategia a pierdut acolo, `ELIGIBIL_ISTORIC` e populat, `mde_hist` e mic, și respingerea se produce. Scutirea nu se poate invoca; ori se demonstrează, ori nu.**

---

# PARTEA 6 — REGULA `m`: se extinde, iar extinderea are o capcană

**„O fereastră alternativă e ipoteză nouă sau reparametrizare?" — O ipoteză e definită de tripletul (politică, POPULAȚIE, estimand). O fereastră diferită e o populație diferită, deci un estimand diferit. Deci: IPOTEZĂ NOUĂ. Regula se extinde corect.**

```
m: 19 → 20 la fixarea lui RECENT_PRIMARY.
   CAND-0037 rămâne numărat pe populația lui de admitere (familia e MONOTONĂ, sloturile nu se
   întorc), iar RECENT_PRIMARY e o ipoteză SUPLIMENTARĂ pe aceeași politică.
   Prag BH de rang 1: 0,05/20 = 0,00250.
```

> **CAPCANA, care nu e în mandat: numărătoarea se face peste ferestrele EVALUATE, nu peste cele RAPORTATE. Dacă se încearcă trei ferestre și se raportează cea mai bună, m crește cu TREI, nu cu una. Altfel „pre-înregistrată" ar deveni „pre-înregistrată după ce am văzut", exact portița închisă la v2.7.69 pentru condiția de regim — aceeași formă, alt obiect.**

**Consemnare: la MDE 0,0839 față de un efect observat de 0,062, diferența dintre m=19 și m=20 e neglijabilă. Ca și la verdictul 001 și la CAND-0037, constrângerea rămâne PUTEREA, nu multiplicitatea. O spun ca să nu se caute vinovatul în corecție.**

---

# PARTEA 7 — DESCHIS, CLASIFICAT

```
BLOCKING      cele ZECE condiții CEO nu sunt în niciun document pe care îl pot citi.
              Nu le invent. Se transmit, se formalizează.
BLOCKING      numărul de episoade ale regimului țintă în fereastra recentă — dacă e sub 5,
              criteriul de stabilitate e imposibil ACOLO, prin construcție. Se măsoară ÎNAINTE.
MATERIAL      statutul „OOS virgin" e per PERECHE (fereastră, candidat), nu global. Nevăzut de
              linia wp5b (măsurat: zero bare), VĂZUT de Flow-B în alpha-automation (`73b7b81`).
              Se urmărește în registrul de explorare, per candidat.
MATERIAL      felia de confirmare finală se declară ACUM și micșorează `n` și numărul de
              episoade. Dimensiunea ei e decizie de model, pre-înregistrată.
MATERIAL      m 19 → 20; numărătoarea peste ferestrele EVALUATE, nu raportate.
LIMITATION    fereastra recentă are ~2,82 ani. Orice criteriu care cere multe episoade lungi
              e la limită acolo, indiferent de strategie.
LIMITATION    RECENT_PRIMARY nu afirmă nimic despre viitor. Recența nu e reprezentativitate.
NON-MATERIAL  autocorecția a șasea: marginea 2021-09-03 transmisă era OPERAȚIONAL corectă
              (ultima bară livrată); a mea, 2021-09-05, era limita declarată a blocului.
              Pentru D-4 contează BARA. Retrag corecția.
```

**Nu cere: gate nou, framework nou, metrică nouă. LOEO, R10, triajul în trei rezultate, `run_hash`, registrul de explorare și blocarea pe zi există toate.**

---

**Manifest:** `config/split_manifest.json` v2.7.71, secțiunea `recent_primary_estimand_v2_7_71`.
