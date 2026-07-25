# STATISTICIAN → VALIDATION ENGINE — HANDOFF OFICIAL, STAGE S002
### Pachet complet de specificații de validare: DC-0003, DC-0004, DC-0008

**Document ID:** STAT-VE-HANDOFF-S002-v1.0
**Data:** 2026-07-24 · **Autor:** Statistician
**Format:** conform Contractului Statistician↔Validation Engine v1.0 (§1, puncte 1-7), extins cu elementele cerute explicit pentru acest handoff.
**Statut:** Specificație de execuție. **Niciun test statistic nu a fost executat. Niciun verdict VALIDATED/REJECTED nu a fost emis.**

**Notă de terminologie:** verdictul efectiv emis de Red Team pentru cei trei candidați este `🟢 CONTINUE INVESTIGATION` (nu literal "SURVIVED") — folosesc mai jos formularea oficială din rapoartele Red Team, tratând-o ca echivalentul cerut aici.

**Nu am generat ipoteze noi. Nu am modificat niciun rezultat Red Team. Nu am implementat nicio strategie. Nu trimit nimic către AI Trader. Nu am modificat Validation Engine sau Capability Registry.**

---

## Ordinea de execuție recomandată

**DC-0008 → DC-0003 → DC-0004**, nemodificată față de planul Stage S002 discutat anterior: DC-0008 și DC-0003 nu ating resurse irepetabile și pot rula în orice ordine relativ una la alta (DC-0008 primul, pentru că stabilește pipeline-ul de scanare a populației reutilizabil la DC-0003); DC-0004 ultimul, pentru că singurul consumă holdout-ul OOS rezervat, CEO-gated.

---

## PACHET 1 — DC-0008

### 1. Descrierea completă a ipotezei
O lumânare M15 mare poate fi construită în două moduri opuse: (a) participare susținută, distribuită relativ uniform pe toate cele ~15 minute (respectiv toate cele 3 sub-lumânări M5), fără revenire la volumul de bază înainte de închiderea M15; sau (b) concentrare într-un singur minut (sau o singură sub-lumânare M5) dominant, cu restul intervalului la volum de bază. Lumânarea M15 singură nu poate distinge între cele două construcții — vizibile doar la M5/M1. Este posibil ca cele două construcții să aibă traiectorii ulterioare ("aftermath") diferite. (Sursă: `candidate_v1.md` §§1-4, confirmată de Red Team `REVIEW_DC-0008_v1.md` C1.)

### 2. Ipoteza statistică (H0/H1)
- **H0:** distribuția raportului R = (volumul celei mai mari sub-lumânări M1 sau M5) ÷ (volumul total M15) e unimodală/continuă pe populația de lumânări M15 mari — nu există o dihotomie reală de construcție. Orice relație aparentă cu rezultatul post-M15 e explicată integral de regimul de volatilitate ambientă (primitivul Volatility deja promovat în lab).
- **H1:** distribuția lui R e bimodală (există o graniță reală, derivabilă din date) ȘI tipul de construcție rezultat prezice rezultatul post-M15 dincolo de ce explică regimul de volatilitate.

### 3. Metodologia de validare
Trei straturi, secvențiale:
- **Strat 1 — existența claselor:** test dip Hartigan + GMM (1 vs. 2 componente, comparație BIC) pe distribuția lui R.
- **Strat 2 — determinarea pragului** (doar dacă Strat 1 confirmă bimodalitate): metoda Otsu sau intersecția posterioarelor GMM, derivată **exclusiv din distribuția lui R**, înainte de a privi vreodată variabila de rezultat.
- **Strat 3 — informație marginală:** regresie outcome_post_M15 ~ R × regim_volatilitate, cu erori HAC (Newey-West) sau clusterizate pe zi/sesiune.

### 4. Toate testele de executat
1. Test dip Hartigan pe R (populația completă de lumânări M15 mari).
2. GMM 1 vs. 2 componente, comparație BIC.
3. Determinare prag (Otsu / crossover GMM) — doar dacă GMM(2) câștigă la BIC.
4. Bootstrap în **blocuri mobile** (nu i.i.d.) pentru stabilitatea pragului — lungime bloc pre-specificată (recomandare: echivalentul a ~5-10 zile de tranzacționare, de confirmat înainte de execuție), N reeșantionări.
5. Regresie cu interacțiune: outcome ~ R × regim_volatilitate, erori HAC/clusterizate pe zi.
6. Comparație complementară pe perechi potrivite (matching) susținut-vs-concentrat, regim de volatilitate similar — verificare de robustețe față de regresie.
7. Sensibilitate (multiverse): R calculat din bază M1 vs. M5; definiții alternative ale "M15 mare" (percentilă/z-score pe ferestre mobile diferite).
8. Corecție family-wise prin **permutare (max-T)**, nu Bonferroni simplu — rezultatul acestui test servește și DC-0013 (dependent direct) și informează statutul DC-0006/0015/0017.
9. Analiză de putere pe un interval **conservator** de mărimi de efect (nu valoarea brută observată din cele ~6 instanțe cunoscute — risc de "winner's curse"/regresie spre medie).

### 5. Datele necesare
- Serie completă M1 (ideal și M5) OHLCV + volum tick, XAUUSD/OANDA, întreaga fereastră pre-holdout (până la 2025-10-23T09:15:00Z).
- Variabila de regim de volatilitate (ATR local / Parkinson log-range, profil orar) — reutilizabilă din primitivul Volatility deja promovat în lab.
- Traiectorie de preț post-închidere M15, minimum N bare M15 ulterioare. **N trebuie pre-înregistrat explicit înainte de execuție** — recomandare N=8 (aproximativ media orizonturilor informale din familia DC-0013…0018, 4-11 candele); decizie finală la Validation Engine/CEO dacă diferă.
- Metadate de sesiune/calendar pentru stratificarea de robustețe.

### 6. Criteriile de acceptare și respingere
- **Acceptare** (candidat pentru STATISTICALLY ROBUST): dip test respinge unimodalitatea (p<0.01), replicat pe ≥2 subperioade, prag stabil în bootstrap (interval îngust), ȘI efectul de predicție a rezultatului supraviețuiește controlului de volatilitate la semnificație corectată family-wise, replicat pe holdout.
- **Respingere** (STATISTICALLY REJECTED): distribuția e unimodală/continuă, SAU efectul dispare după controlul de volatilitate.
- **Indeterminat** (TESTABLE BUT INSUFFICIENT EVIDENCE): eșantion sub puterea minimă calculată, sau rezultate instabile pe subperioade fără semnal direcțional clar.

### 7. Metricile de calculat
Statistica dip Hartigan + p-value; BIC(1), BIC(2), ΔBIC; pragul derivat (dacă aplicabil) + interval de încredere bootstrap; coeficienții regresiei (efect principal R, efect regim, termen de interacțiune) + erori HAC + p-values corectate family-wise; rata de succes per grup (din matching); numărul de evenimente din populație (denominator, pentru audit); histograma/densitatea lui R.

### 8. Condițiile de oprire
- Oprire, raportare INSUFICIENT: populația scanată produce sub pragul minim de putere calculat.
- Oprire, cerere de clarificare Statistician: dip test și GMM sunt în dezacord fără explicație clară — nu se trece la Strat 3 fără rezolvarea dezacordului.
- Oprire: datele de regim de volatilitate lipsesc pentru o parte semnificativă a populației scanate.

### 9. Limitările cunoscute
Risc de confound mecanic/tautologic — R ar putea fi doar o transformare monotonă a magnitudinii barei, nu o clasă reală (exact ce testează Strat 1, dar un rezultat negativ nu poate exclude complet acest artefact al alegerii variabilei R). Feed de volum broker (tick), nu volum de schimb — poate afecta comparabilitatea între sesiuni.

### 10. Riscurile identificate
Autocorelație serială (lumânările mari se aglomerează în regimuri de volatilitate — motivul bootstrap-ului în blocuri, nu i.i.d.). Testări multiple nedeclarate dacă rezultatul e reutilizat pentru DC-0013 fără corecție comună. Data snooping la alegerea pragului dacă e privit înainte de derivare (interzis explicit la Strat 2).

### 11. Observații importante pentru execuție
Testul cu cea mai mare pârghie de portofoliu — rezultatul deblochează automat DC-0013 și informează DC-0006/0015/0017. Recomand execuția înaintea celorlalte doi, pentru reutilizarea pipeline-ului de scanare a populației.

---

## PACHET 2 — DC-0003

### 1. Descrierea completă a ipotezei
Compresia nu înseamnă același lucru la orice scară. HTF-C (compresie H4/multi-day după o extensie) se rezolvă printr-o expansie direcțională autentică (subiectul DC-0002). Micro-C (coil M15 de ~5-10 candele, tipic în tape asiatic subțire) produce o spargere marginală dincolo de limita coil-ului, care eșuează imediat și se inversează. Granița dintre cele două ar sta la un anumit multiplu al ATR predominant (propus, netestat). (Sursă: `candidate_v1.md` §§1-3, `REVIEW_DC-0003_v1.md`.)

### 2. Ipoteza statistică (H0/H1)
- **H0:** raportul scale_ratio (range pre-spargere ÷ ATR local) nu prezice outcome-ul spargerii (continuare vs. eșec) pe populația de 384 swing-high exceedances din OBS-0017 — nulul agregat al OBS-0017 nu se descompune prin separare de scală; orice efect aparent e explicat integral de regimul de lichiditate.
- **H1:** scale_ratio prezice outcome-ul, cu sens constant (scale mai mic → eșec mai probabil), și efectul supraviețuiește controlului pentru regimul de lichiditate.

### 3. Metodologia de validare
Re-analiza OBS-0017 (n=384, dataset **deja existent**, nu date noi) cu o variabilă continuă scale_ratio, nu o dihotomie fixă a priori. Regresie cu interacțiune scale_ratio × regim_lichiditate. Regresie **segmentată** (piecewise, tip Bai-Perron) cu test de raport de verosimilitate (1 segment vs. 2 segmente) — preferată unui spline generic, pentru un statistic de test unic, interpretabil, paralel metodologic cu Strat 1 al DC-0008.

### 4. Toate testele de executat
1. Calculul scale_ratio pentru fiecare din cele 384 evenimente (range pre-spargere ÷ ATR local la momentul evenimentului, strict din date anterioare — fără leakage).
2. Regresie (logistică sau liniară, după tipul outcome-ului) cu interacțiune: outcome ~ scale_ratio + regim_lichiditate + scale_ratio:regim_lichiditate, erori HAC/clusterizate pe zi.
3. Test de raport de verosimilitate: model 1-segment vs. 2-segmente pe relația scale_ratio→outcome.
4. Sensibilitate: ATR pe ferestre alternative (14/20/50 bare); range pre-spargere pe orizonturi alternative (5/10 candele).
5. Corecție family-wise dacă rezultatul e raportat simultan cu DC-0002 (F8 — DC-0002 e cazul special HTF al acestui candidat).
6. Robustețe: stratificare pe sesiune (Asia/Londra/NY); replicare pe subperioade disjuncte din cele 384 evenimente.

### 5. Datele necesare
Setul OBS-0017 existent (384 evenimente) cu variabilele brute — range pre-spargere, volum, rezultat — nu doar concluzia agregată (CI spans 0). ATR local per eveniment (reconstruit din seria de bare dacă nu există deja în OBS-0017), strict din date anterioare evenimentului. Variabilă de regim de lichiditate/sesiune per eveniment.

### 6. Criteriile de acceptare și respingere
- **Acceptare:** relația scale_ratio→outcome semnificativă, sens constant, supraviețuiește termenului de interacțiune cu lichiditatea, stabilă la definiții alternative de ATR/fereastră și pe subperioade.
- **Respingere:** relația nu e semnificativă pe cele 384 evenimente (falsifier-ul propriu al candidatului), SAU dispare după controlul de lichiditate.
- **Indeterminat:** coada "micro-scale" a distribuției prea mică pentru putere adecvată.

### 7. Metricile de calculat
Coeficienți regresie (efect principal, efect lichiditate, interacțiune) + erori HAC + p-values; statistica raportului de verosimilitate (1 vs. 2 segmente) + p-value; locația pragului estimat (dacă segmentarea câștigă) + interval de încredere; distribuția lui scale_ratio (audit vizual).

### 8. Condițiile de oprire
Oprire dacă selecția celor 384 evenimente din OBS-0017 nu poate fi confirmată ca sistematică (nu discreționară) — risc de leakage nerezolvat, dependență deschisă semnalată deja în Phase 1. Oprire dacă sub-eșantionul micro-scale e prea mic pentru puterea calculată.

### 9. Limitările cunoscute
Confuzia scale/lichiditate — ambele instanțe originale micro-C sunt în tape asiatic subțire, perfect confundate la n=2 (motiv exact pentru care termenul de interacțiune e obligatoriu, nu opțional). Nu s-a confirmat dacă selecția celor 384 evenimente OBS-0017 a fost discreționară sau sistematică.

### 10. Riscurile identificate
Risc de "prag ales post-hoc" dacă segmentarea ar fi lăsată să optimizeze pe același set folosit pentru testul de outcome — de aceea metoda de segmentare trebuie fixată în avans. Autocorelație serială similară cu DC-0008.

### 11. Observații importante pentru execuție
Cel mai ieftin dintre cele trei — reutilizează un dataset deja colectat, fără nevoie de scanare nouă a datelor brute. Recomand execuția a doua, după DC-0008, pentru reutilizarea tooling-ului de regresie/populație construit acolo.

---

## PACHET 3 — DC-0004

### 1. Descrierea completă a ipotezei
Pe XAUUSD H1, prima bară a zilei al cărei maxim depășește prior-day-high dar care închide înapoi sub acel nivel (sweep-reject) este urmată de reversie — dar doar când evenimentul are loc în sesiunea New York. În alte sesiuni același eveniment nu arată reversie, iar pe partea Asia/Londra semnul e inversat. (Sursă: `candidate_v1.md` §1.)

### 2. Ipoteza statistică (H0/H1)
- **H0:** continuation-excess-ul la evenimentele sweep-reject-NY nu diferă sistematic de cel produs de un eșantion matched-null comparabil (aceeași sesiune/perioadă, fără condiționarea de eveniment).
- **H1:** continuation-excess e negativ (reversie), semnificativ diferit de nulul potrivit, specific sesiunii NY.

### 3. Metodologia de validare — REPLICARE STRICTĂ, nu design nou
Conform deciziei de reconciliere `STATISTICIAN_DEFINITION_RECONCILIATION_DECISION_v1.0.md`: convenția oficială pentru acest test e **identică** cu cea din scripturile care au produs p=0.021/0.029 (obs0003/0008/0012/0013), nu cu propunerile inițiale ale Statisticianului din OPDEF v1.0. Re-rulare a metodologiei matched-null pe holdout-ul rezervat (post 2025-10-23T09:15:00Z), pe **toate celulele** sesiune×direcție care ating pragul minim de eșantion — nu doar celula câștigătoare NY-up.

**Definiții blocate pentru replicare** (obligatorii, nu discreționare):
- Graniță zi = 00:00 UTC, zi calendaristică simplă.
- Sesiuni = 4 categorii, cupe UTC fixe, fără DST: asia [00,08), london [08,13), ny [13,21), late [21,24).
- Eveniment = prima bară H1 a zilei al cărei `high` depășește prior-day-high; se verifică **exclusiv acea bară** pentru `close < prior-day-high`; dacă nu respinge, ziua nu are eveniment în populație — chiar dacă o bară ulterioară ar respinge independent (limitare cunoscută a convenției originale, purtată neschimbată).
- min_n = 25 evenimente per celulă.
- Baseline = forward-ul propriu al sesiunii (nu drift global).
- Test one-sided (coadă stângă, testând specific reversia).
- 3000 reeșantionări, seed=7.
- **K6 e singurul orizont corectat/decisiv.** K12 se raportează descriptiv, fără pretenție de semnificație corectată — exact ca în scripturile originale.

### 4. Toate testele de executat
1. Matched-null resampling pe fiecare celulă sesiune×direcție cu n≥25, 3000 reeșantionări, seed=7, coadă stângă.
2. Corecție Bonferroni **empirică**: prag = 0.05 ÷ (numărul de celule care ating n≥25 în holdout, determinat din date, nu fixat în avans la 6).
3. K6 ca orizont decisiv unic; K12 raportat separat, descriptiv.
4. *(Analiză secundară, recomandare proprie a Statisticianului — NU parte a convenției replicate, nu determină verdictul principal):* control de regresie pentru regimul de volatilitate orară; test placebo pe nivel de referință arbitrar.

### 5. Datele necesare
Seria H1 completă XAUUSD/OANDA pentru fereastra holdout (post 2025-10-23T09:15:00Z) — rezervată, neatinsă până acum. Nivelurile D1 prior-day-high pentru aceeași fereastră, calculate cu granița de zi UTC blocată mai sus. Aceleași scripturi/parametri ca obs0003/0008/0012/0013, aplicate identic, fără modificări ad-hoc.

### 6. Criteriile de acceptare și respingere
- **Acceptare:** efectul NY-up-reject replică pe holdout la pragul Bonferroni empiric corectat (peste toate celulele calificate), semn negativ consistent cu in-sample.
- **Respingere:** nu replică la prag corectat, sau schimbă semnul.
- **Indeterminat:** numărul de evenimente NY-up-reject în fereastra holdout sub pragul minim de putere (estimare: ~15-20 evenimente, extrapolat din rata de bază in-sample ~15/an).

### 7. Metricile de calculat
Continuation-excess la K6 pentru fiecare celulă calificată + CI95 + p-value matched-null; numărul de celule cu n≥25 (denominator pentru Bonferroni); K12 raportat separat, descriptiv, fără statut corectat; rezultatul controlului de volatilitate/testului placebo (dacă executate) raportat separat de verdictul principal bazat pe replicare.

### 8. Condițiile de oprire
**Nu se atinge holdout-ul până la confirmarea finală CEO a acestei specificații** — resursă irepetabilă, CEO-gated. Oprire, raportare indeterminat: numărul de evenimente NY-up-reject în holdout sub pragul minim de putere.

### 9. Limitările cunoscute
Convenția replicată (graniță UTC, eveniment "prima depășire") are o slăbiciune cunoscută — poate subnumăra rejecturile care nu au loc pe chiar prima bară exceedantă. Purtată deliberat neschimbată, pentru validitatea replicării, nu pentru că ar fi optimă. p-ul in-sample (0.021/0.029) nu trece pragul Bonferroni deja cunoscut — "acceptarea" aici înseamnă doar replicare pe eșantion nou, nu că ipoteza in-sample a fost vreodată robustă statistic.

### 10. Riscurile identificate
Eșantion mic așteptat pe holdout (fereastra e finită). Risc de a repeta selecția in-sample dacă s-ar raporta doar celula câștigătoare, fără toate celelalte calificate. Resursă irepetabilă — orice eroare de specificație cheltuită pe ea nu mai poate fi corectată printr-o a doua încercare.

### 11. Observații importante pentru execuție
Singurul din cele trei care consumă o resursă CEO-gated, irepetabilă — recomand execuția ultima, după ce pipeline-ul a fost verificat pe DC-0008/DC-0003. Controlul de volatilitate și testul placebo sunt recomandări proprii ale Statisticianului, distincte de convenția replicată — trebuie raportate ca analiză secundară, niciodată amestecate cu verdictul principal bazat pe replicarea strictă.

---

## Declarație finală

Cele trei pachete de mai sus conțin specificația completă necesară pentru ca Validation Engine să execute testele fără nicio interpretare suplimentară din partea sa, conform Contractului Statistician↔Validation Engine v1.0. Nu am executat niciun test. Nu am emis niciun verdict VALIDATED sau REJECTED. Nu am generat ipoteze noi și nu am modificat rezultatele Red Team.

**DC-0008, DC-0003 și DC-0004 sunt declarați pregătiți pentru execuția în Validation Engine**, în ordinea recomandată la începutul acestui document.

---

**Statistician se oprește aici și așteaptă confirmarea CEO / rezultatele brute de la Validation Engine.**
