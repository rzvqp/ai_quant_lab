# STATISTICIAN — SPECIFICAȚIE MATEMATICĂ: CLASIFICATOR DE REGIM (HMM GAUSSIAN, 3 STĂRI)

**Document ID:** STAT-REGIME-HMM-SPEC-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Statut:** SPECIFICAȚIE, NU IMPLEMENTARE. Nu conține cod executabil. Nu atinge date — M15 extins nu există încă (verificare picată, retras). Execuția revine altei părți (Contract Statistician↔VE §1.7); acest document proiectează și specifică.
**Nu reface:** împărțirea 50/50 stratificată pe segmente de regim și carantina de 1.000 de bare (`TRACK_HORIZON`=960, rotunjit) — ambele deja în `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md` §1, stare comisă la `a002ab4`. Referite mai jos, nu redefinite.

---

## 0. Disambiguare obligatorie înainte de orice altceva

**"Harta de regimuri" (§1 din documentul de mai sus) și clasificatorul HMM specificat aici NU sunt același obiect.** Harta de regimuri e o regulă mecanică, disclosed, necalibrată statistic (ex. randament pe fereastră mobilă de N luni peste ±X%), folosită DOAR ca să împartă fiecare segment continuu 50/50 descoperire/confirmare. HMM-ul de aici e un artefact separat, antrenat pe features de piață, ale cărui stări **pot sau nu** să corespundă segmentelor bull/bear/range ale hărții — asta e o întrebare empirică, nu o presupunere. Oricine implementează nu trebuie să confunde cele două.

## 1. Obiectul — rol pasiv, etichete ca ipoteze

`market_regime` (int, {1,2,3}) și `regime_confidence` (float, [0,1]) — două câmpuri adăugate la `ContextSnapshot`. **Nu selectează strategii, nu atinge risk management.** Numărul de stări (3) e dat, nu derivat aici. **Etichetele semantice (mean-reverting/trending/anomaly) sunt ipoteze de verificat după antrenare, nu constrângeri impuse modelului în timpul potrivirii (fitting).** Dacă starea 2 descoperită nu arată a "trending", aceea e constatarea — modelul nu se reantrenează ca să producă etichetele așteptate.

## 2. Populația de antrenare

Antrenare **exclusiv** pe jumătatea de DESCOPERIRE a celor 11 ani, așa cum e definită de regula deja existentă (§1 din STAT-11YR-PREREG): reuniunea porțiunilor de 50% (sau 60/40 unde declarat) din FIECARE segment continuu al hărții de regimuri, cu cele 1.000 de bare de carantină excluse la fiecare graniță internă. Jumătatea sigilată **neatinsă** de orice pas din secțiunile 3-7.

**Tratament multi-secvență, nu o serie continuă:** segmentele de descoperire, separate de zonele de confirmare/carantină ale altor regimuri, NU se concatenează ca și cum ar fi o singură serie temporală continuă. Fiecare porțiune de descoperire e o secvență independentă pentru scopurile Baum-Welch (log-verosimilitatea totală = suma log-verosimilităților per secvență; statisticile de tranziție se acumulează peste secvențe, dar niciun pas de tranziție nu se calculează peste o graniță de carantină). Motiv: a trata granița ca fiind continuă ar însemna presupunerea unei dinamici Markov peste exact zona pe care carantina o exclude ca să prevină scurgerea de dependență serială.

## 3. Features — construcție cauzală obligatorie

Fiecare component al vectorului de features `x_t` trebuie să fie o funcție STRICT a barelor `≤ t` (nicio fereastră centrată, niciun calcul care privește înainte). Volatilitatea folosită trebuie să fie metrica oficială deja stabilită în laborator (E000: Parkinson log-range `ln(H/L)` ca primar) — nu se inventează o nouă definiție ad-hoc de volatilitate pentru acest artefact.

**Set propus ilustrativ** (proprietățile de mai jos sunt obligatorii; cifrele exacte de lookback pot fi finalizate de Data Acquisition/Flow A înainte de antrenare, cu disclosure, fără a viola proprietățile):
- `r_t^(L1)`: randament log pe fereastră mobilă de `L1` bare trecute.
- `σ_t^(L2)`: Parkinson log-range mediu pe `L2` bare trecute (volatilitate, metrica oficială).
- `skew_t^(L3)`: skewness eșantion a randamentelor pe `L3` bare trecute.

Propunere de valori (reutilizare din familia deja existentă `HORIZONS=(1,3,5,10,20,50)` din `_profile.py` — convenție generică deja folosită în laborator pentru scopuri fără legătură, trece testul de proveniență §2 din regulile de pre-înregistrare v1.1, punctul 1): `L1=20, L2=20, L3=50`.

**Reguli obligatorii, indiferent de cifrele finale:**
1. Fiecare feature e cauzal (funcție a trecutului, nu a viitorului relativ la `t`).
2. Setul de features e FIX și disclosed ÎNAINTE de antrenare — nicio căutare iterativă de features ghidată de cât de bine separă stările sau de cât de bine corelează cu vreo ipoteză de edge. Aceasta ar fi exact un canal ascuns de multiplicitate.
3. Reutilizează primitive deja stabilite în laborator (Parkinson log-range) unde acoperă nevoia, în loc să inventeze una nouă.

`L_max` = cel mai lung lookback dintre features (propunerea de mai sus: `L_max = 50`).

## 4. Forma modelului și procedura de antrenare

**Model:** stare ascunsă `S_t ∈ {1,2,3}`, matrice de tranziție `Π` (3×3, stocastică pe linii), `x_t | S_t=k ~ N(μ_k, Σ_k)`.

**Structura covarianței:** decisă ÎNAINTE de antrenare, pe baza adecvării eșantionului, nu pe baza cât de "curate" arată stările rezultate. Regulă: dacă cel mai scurt segment de descoperire are mai puțin de ~30 observații efective per parametru liber de covarianță (regulă empirică standard, nu o derivare exactă — declarat ca atare), se folosește covarianță diagonală; altfel, covarianță completă (surprinde corelația dintre features în cadrul unei stări).

**Antrenare (Baum-Welch/EM):** stocastică — sensibilă la inițializare (premisă acceptată). Protocol obligatoriu:
1. `R=50` reporniri (restart), semințe fixate și disclosed înainte de rulare (ex. semințe 1..50) — numărul și semințele NU se aleg după ce se vede câte sunt necesare pentru un rezultat "bun".
2. Fiecare repornire converge la o toleranță fixă de log-verosimilitate și un număr maxim de iterații, ambele disclosed a priori.
3. Selecție mecanică: se alege repornirea cu cea mai mare log-verosimilitate pe jumătatea de descoperire. **Nu se alege repornirea ale cărei stări "arată" a mean-reverting/trending/anomaly** — asta ar injecta exact ipoteza semantică (premisă 1) în procedura de potrivire, interzis.
4. **Diagnostic de instabilitate obligatoriu:** raportează diferența de log-verosimilitate între cea mai bună și a doua cea mai bună repornire. Dacă diferența e sub un prag declarat ca "practic egale" (ex. o schimbare relativă < 0.1% în log-verosimilitate — declarat acum, nu ales după rezultat) SAU dacă stările celor două optime, aliniate prin cea mai apropiată medie de emisie (algoritm de tip Hungarian pentru rezolvarea permutării etichetelor), diferă substanțial în `Π`/`μ`/`Σ` — modelul e **INSTABIL** și intră direct la REJECTED (secțiunea 8), indiferent de orice altă verificare.

## 5. Decodare — producție (cauzală) vs. diagnostic (in-sample)

Distincție obligatorie, sursă frecventă de scurgere dacă e ignorată:

- **PRODUCȚIE (`ContextSnapshot`, orice utilizare live sau pe jumătatea sigilată):** filtrare înainte (forward filtering) STRICTĂ. `α_t(k) = P(S_t=k | x_1,...,x_t, Θ)`, calculat recursiv, folosind DOAR bare `≤ t` și parametrii ÎNGHEȚAȚI `Θ` din antrenare. `market_regime_t = argmax_k α_t(k)`; `regime_confidence_t = max_k α_t(k)`. **Netezirea (forward-backward) sau decodarea Viterbi peste o fereastră care include bare viitoare relativ la bara etichetată sunt INTERZISE în calea de producție** — ar constitui exact lookahead per-etichetă.
- **DIAGNOSTIC (secțiunile 6-7, EXCLUSIV pe jumătatea de descoperire):** decodare Viterbi (sau netezire) pe toată secvența de descoperire e PERMISĂ, pentru că scopul e diagnosticarea modelului însuși (stabilitate, separare), nu producerea unei etichete folosite ca input pentru altceva. **O etichetă din decodarea diagnostic nu iese niciodată din secțiunile 6-7** — nu alimentează nicio ipoteză de edge, nicio selecție, nimic.

Această distincție rezolvă premisa 2 (parametri globali din features rulante): problema nu e antrenarea în sine (asta înseamnă "antrenare"), ci ca o etichetă produsă de netezire in-sample să scape din scopul diagnostic și să fie tratată ca disponibilă în timp real la bara respectivă. Regula de mai sus închide exact acest canal.

## 6. Testul de stabilitate a etichetelor

**Derivarea lui N minim (nu alegere):** durata de ședere (sojourn) într-o stare cu probabilitate diagonală `p_kk` e geometrică, medie `1/(1-p_kk)`. Dar pragul absolut minim pentru ca "stabilitate" să însemne ceva, nu un artefact, vine din construcția features-urilor, nu dintr-o convenție externă: **niciun feature nu poate arăta o schimbare de stare mai rapid decât propria lui fereastră de calcul** — o rulare de `L_max` bare e prin construcție autocorelată pe acea fereastră. Deci orice "persistență" măsurată sub `L_max` bare e cel puțin parțial un artefact al netezirii features-ului, nu o descoperire despre piață. **Podeaua tare: `N_min ≥ L_max`.**

Peste podea, cer o marjă de siguranță explicită (declarată, nu complet derivată — marcată ca atare): `N_min = 3 × L_max`. Cu propunerea din §3 (`L_max=50`): `N_min = 150` bare. Motiv pentru factorul 3, nu 1: la 1×, o durată medie chiar la limita ferestrei de calcul tot s-ar putea confunda cu netezirea; 3× dă o separare clară față de artefactul de măsurare, în același spirit ca alte marje de siguranță deja folosite în laborator (ex. rotunjirea TRACK_HORIZON). Implică `p_kk,min = 1 - 1/N_min = 1 - 1/150 ≈ 0.9933`.

**Testul complet, la nivel de episod (nu bară cu bară):** decodează Viterbi (diagnostic) pe descoperire; extrage TOATE episoadele contigue ale fiecărei stări `k`: `{T_1,...,T_{m_k}}`. Tratarea episodului (nu bara) ca unitate de observație rezolvă parțial și problema de non-independență a secțiunii 7(b) — episoade diferite, adesea separate de vizite în alte stări, sunt mult mai aproape de independente decât barele brute din interiorul unui singur episod.

**Criteriul de eșec (nu doar media — cerința explicită):**
- **Eșec dacă `mediana({T_i}) < N_min`** pentru ORICE stare, indiferent de medie. Rezolvă exact exemplul "medie 50, mediană 2" — o coadă de câteva episoade lungi nu poate ascunde o majoritate care clipește.
- **Eșec suplimentar dacă fracția episoadelor cu `T_i < L_max` depășește 25%** pentru orice stare — reutilizare explicită, cu disclosure, a pragului de materialitate deja stabilit la regula M5 (`NOT-RESOLVABLE-AT-M5`, 25%), trecut prin propriul meu test de proveniență (§2, punct 1: convenție generică de "fracție semnificativă", nu calculată din acest rezultat specific).
- Raportare obligatorie, chiar dacă testul trece: histograma completă a duratelor per stare, nu doar media/mediana.

**Orice stare care eșuează oricare din cele două criterii → modelul întreg intră direct la REJECTED** (secțiunea 8) — o singură stare instabilă contaminează utilitatea operațională a etichetei ca întreg, pentru că `argmax` peste stări include acea stare.

## 7. Analiza de separare statistică

**(a) Testarea multiplă — familia se declară o singură dată, complet, înainte de rulare.** Familia = {toate perechile de stări} × {toate cele 3 momente: medie, varianță, skewness} × {toate features-urile din vectorul `x_t`} × {orice timeframe/segment suplimentar declarat de la început}. Cu 3 features din §3: 3 perechi × 3 momente × 3 features = 27 teste, nu 9 (9 e cazul cu un singur feature — corect ca ordin de mărime pentru premisa CEO, dar familia completă trebuie să includă toate dimensiunile vectorului, nu doar una). **Corecție: BH-FDR la `q=0.01`** (nu Bonferroni — testele sunt puternic corelate: aceleași stări, aceleași date de bază, momente care se suprapun; BH e mai eficient statistic păstrând control semnificativ, consecvent cu precedentul deja stabilit în acest laborator pentru familii corelate — scoped global-FDR, S18). **Extinderea familiei DUPĂ ce se vede un rezultat parțial (ex. "hai să verificăm și H1 fiindcă M15 n-a separat curat") e interzisă** — exact tiparul de "forking paths" pe care disciplina acestei sesiuni îl respinge sistematic.

**(b) Non-independență — agregare la nivel de episod, nu ajustare de N pe bară.** Barele consecutive din aceeași stare sunt masiv autocorelate — proprietatea care FACE starea să fie stare, cum ai spus. Nu folosesc `block_bootstrap@v1` sau `permutation_test@v1` generic din registru pentru asta — ambele UNVALIDATED (confirmat `capabilities.json` VE-CAPREG-v1.6), și tocmai am respins azi o excepție pentru un membru al aceleiași familii de metode nevalidate (`STATISTICIAN_BLOCK_BOOTSTRAP_EXCEPTION_DENIAL_v1.0.md`) — ar fi incoerent să folosesc acum, tacit, o rudă a metodei pe care am refuzat-o.

În loc, specific un test NOU, la nivel de episod: pentru fiecare feature și fiecare stare, calculează statistica per episod (media/varianța/skewness a feature-ului ÎN INTERIORUL episodului, nu bară cu bară) — episoadele, fiind separate în timp de vizite în alte stări, sunt mult mai aproape de unități independente decât barele brute. Compară distribuțiile acestor statistici episod-nivel între stări printr-un **test de permutare la nivel de episod** (permută etichetele de stare ale episoadelor, păstrând numărul de episoade per stare fix; recalculează diferența observată pentru fiecare permutare; p empiric = fracția de permutări cu diferență ≥ cea observată). Aceasta e o metodă NOUĂ, specifică acestui context (`episode_permutation_separation_test@v1`, propunere de nume de capabilitate) — distinctă de `permutation_test@v1` generic deja UNVALIDATED în registru, nu se confundă cu el, și necesită PROPRIA ei baterie de acceptanță înainte de VALIDATED (secțiunea 9). Testul nu presupune iid pe bare — presupune doar că episoadele (nu barele) sunt schimbabile sub null, o presupunere mult mai slabă și mai defendabilă.

**(c) "Stările diferă" vs. "stările înseamnă ceva" — propunerea ta se acceptă, cu buget explicit.** Un HMM găsește ÎNTOTDEAUNA stări care diferă pe descoperire — asta face algoritmul, exact cum ai spus. Separarea pe descoperire NU e suficientă pentru "înseamnă ceva". **Cer replicarea separării pe jumătatea sigilată, cu modelul ÎNGHEȚAT (parametrii `Θ` din antrenarea pe descoperire, fără reantrenare), decodat prin filtrare cauzală (§5) — apoi ACELAȘI test episod-permutare, ACEEAȘI familie, ACELAȘI `q=0.01`, rulat O SINGURĂ DATĂ.**

Bugetul cerut de tine ("cât din sigilat se cheltuie, decis acum, o singură dată"): tratez replicarea de separare ca **o a doua familie pre-înregistrată, separată de familia celor 8 ipoteze de edge**, cu propriul prag `q=0.01`, rulată exact o dată, fără iterație. Nu se combină cu familia celor 8 edge-uri (întrebări structural diferite — una întreabă dacă o segmentare nesupervizată replică, cealaltă dacă un edge specific are efect real) și niciuna nu informează cealaltă (un rezultat "regim replicat" nu poate justifica post-hoc adăugarea condiționării pe regim la un edge, decât dacă acea condiționare era deja pre-înregistrată înainte de a atinge datele sigilate — vezi secțiunea 9). Dacă replicarea eșuează, verdictul e "clasificatorul nu generalizează" — nu se reantrenează, nu se reîncearcă alte features pe sigilat.

## 8. Regula de decizie completă — ACCEPTED / REJECTED / UNDECIDED

**ACCEPTED** — toate, fără excepție:
1. Antrenare stabilă (§4.4: nicio ambiguitate de optim local).
2. Testul de stabilitate (§6) trece pentru toate cele 3 stări, pe descoperire.
3. Testul de separare (§7a,b) trece la BH-FDR `q<0.01`, familia completă, pe descoperire.
4. Separarea REPLICĂ (§7c) la `q<0.01`, aceeași familie, pe sigilat, model înghețat, o singură rulare, pentru toate cele 3 stări.

**REJECTED** — oricare, necondiționat:
- Instabilitate de antrenare (§4.4).
- Eșec de stabilitate (§6) pentru orice stare, pe descoperire.
- Eșec de separare (§7a,b) pe descoperire.
- Eșec TOTAL de replicare pe sigilat (toate cele 3 stări eșuează replicarea).

**UNDECIDED** — zona gri, ruta explicit către decizie de guvernanță, NU spre "reparare" folosind sigilatul a doua oară:
- Replicare parțială: 1-2 din cele 3 stări replică pe sigilat, restul nu. Nu e nici ACCEPTED (nu tot modelul e validat) nici REJECTED curat (ceva real ar putea exista pentru stările care replică).
- Diagnosticul de instabilitate (§4.4) cade într-o bandă ambiguă, nici clar unic nici clar concurent (prag exact de declarat înainte de rulare de către implementator, dar banda ambiguă însăși trebuie recunoscută ca o a treia categorie, nu forțată binar).

**UNDECIDED nu se rezolvă revenind la jumătatea sigilată** — acel set e cheltuit. Rezolvarea, dacă se dorește, cere date genuin noi, viitoare, nu o a doua privire asupra sigilatului curent.

## 9. Determinarea cerută — antrenarea HMM consumă jumătatea de descoperire pentru cele 8 ipoteze de edge?

**Nu, nu prin simplul fapt al antrenării — dar cu o condiție care trebuie respectată activ, nu presupusă.**

O etichetă de regim e o transformare de context derivată EXCLUSIV din features de preț/volatilitate — nu citește, nu e informată de, și nu calculează nimic despre variabila de rezultat (pnl, R, hit rate) a NICIUNEIA din cele 8 ipoteze. Prin criteriul deja stabilit în această sesiune ("a fost PARAMETRUL NUMERIC SPECIFIC al ipotezei informat de un rezultat CALCULAT pe aceste date anume?" — `STATISTICIAN_11YR_DATASET_PREREGISTRATION_RULES_v1.0.md` §2), antrenarea HMM nu atinge parametrizarea niciunei ipoteze de edge. E categoric diferit de "testarea unei ipoteze" — care prin definiție calculează/consumă informație DESPRE performanța acelei ipoteze. Segmentarea nesupervizată a seriei de preț nu e, în sine, un act de testare împotriva vreunuia din cele 8 edge-uri.

**Condiția care ține asta adevărat:** `market_regime` rămâne pasiv EXACT cum mandatul cere. Din momentul în care regimul e folosit ca să SELECTEZE, filtreze, sau aleagă cea mai bună felie pentru o ipoteză de edge PE BAZA unei corelații observate pe descoperire între regim și performanța acelei ipoteze — asta E o parametrizare informată de un rezultat calculat pe aceste date, deja acoperită de regula existentă §2, consumând acea felie exact ca orice alt prag împrumutat netransparent. **Concluzie practică:** se poate antrena HMM-ul ȘI dezvolta/testa cele 8 ipoteze pe aceeași jumătate de descoperire, ATÂTA TIMP CÂT (i) definițiile și parametrii celor 8 rămân ficși independent de orice rezultat condiționat pe regim, ȘI (ii) dacă vreo ipoteză intenționează să folosească `market_regime`/`regime_confidence` ca variabilă de condiționare la confirmarea pe sigilat, acea intenție (care regim, ce direcție de efect așteptată) trebuie pre-înregistrată ÎNAINTE de a vedea performanța pe regim a acelei ipoteze pe descoperire — altfel alegerea regimului "care a mers" e exact carving post-hoc al unei sub-populații câștigătoare.

**Replicarea separării pe sigilat (§7c) e o poveste diferită** — aceea CHIAR cheltuie din bugetul evidențial al sigilatului, tratată ca familie separată, o singură rulare (secțiunea 7c, 8).

## 10. Statut de guvernanță — registrul de capabilități

Tot ce specifică acest document e o **capabilitate nouă**, nu o rulare pe o metodă deja validată. Candidați propuși pentru registru, fiecare cu `calibration_status: UNVALIDATED` până trece propria baterie de acceptanță (analog `matched_null@v1`, `bonferroni@v1`):
- `gaussian_hmm_3state@v1` (antrenare, §4)
- `hmm_forward_filter@v1` (decodare producție, §5)
- `hmm_viterbi_diagnostic@v1` (decodare diagnostic, in-sample only, §5)
- `episode_sojourn_stability_test@v1` (§6)
- `episode_permutation_separation_test@v1` (§7) — distinct de `permutation_test@v1` generic, deja UNVALIDATED în registru; nu se confundă.

**Regula `unvalidated_not_executable` se aplică integral:** niciuna din aceste capabilități nu poate produce o valoare `market_regime`/`regime_confidence` folosită în orice specificație oficială (inclusiv condiționarea vreunei confirmări de edge pe sigilat) până nu sunt VALIDATED prin bateriile lor proprii. Înregistrarea și proiectarea bateriilor de acceptanță e o decizie separată de guvernanță (VE/CEO), nu o autorizez sau execut eu aici.

---

**Nu am atins date. Nu am implementat cod. M15 extins nu există încă — specificația așteaptă disponibilitatea lui și proiectarea bateriilor de acceptanță pentru capabilitățile de mai sus.**

**Statistician se oprește aici.**
