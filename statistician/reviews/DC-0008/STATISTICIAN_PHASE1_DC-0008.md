# STATISTICIAN — PHASE 1 REPORT

**Report ID:** STAT-PHASE1-DC-0008-v1
**Discovery Candidate:** DC-0008 — "A Large M15 Candle Built From Sustained Multi-Minute Volume, Not Single-Minute Concentration"
**DC freeze hash (as cited by Red Team):** `sha256:ce52a96e39fcd44da03f9549c2ddfd6da63eadefd7edd24b01c205b31594e130`
**Phase:** Statistician Phase 1 — DESIGN AND TESTABILITY EVALUATION ONLY. No market validation executed. No new data collected. No statistics computed on live/historical bars.
**Date:** 2026-07-24 · **Reviewer:** Statistician
**Sources read (read-only, official artifacts only):**
- `ai_quant_lab-alpha-automation/discovery_candidates/DC-0008_sustained_multiminute_volume_vs_single_minute_concentration/candidate_v1.md`
- same folder: `addendum_2026-07-22_a.md`, `_b.md`, `_c.md`, `_d.md`, `metadata_v1.json`
- `ai_quant_lab/red_team/reviews/DC-0008/REVIEW_DC-0008_v1.md`
- `ai_quant_lab/red_team/RED_TEAM_PHASE1_REPORT.md` — sections 0, F1–F6, X1/X4/X5, I6, O1/O7, §6 DC-0008 entry, §7 items 1/2/3/7, §8 DC-0008 row.

**Explicitly NOT read:** Alpha or Red Team conversation/chat history; any Discovery Candidate other than DC-0008 beyond what the Red Team report's cross-references quote directly; Knowledge Base; confidence ratings.

**Nothing was modified.** DC-0008, its addenda, the Red Team report/review, Knowledge Base, Alpha artifacts, and existing confidence/classifications are untouched.

---

## 1. Reconstrucția exactă a ipotezei

Din `candidate_v1.md` §§1–4, fără reformulare în strategie:

> O lumânare M15 mare poate fi construită în două moduri opuse: (a) participare susținută, distribuită relativ uniform pe toate cele ~15 minute (respectiv toate cele 3 sub-lumânări M5), fără revenire la volumul de bază înainte de închiderea M15; sau (b) concentrare într-un singur minut (sau o singură sub-lumânare M5) dominant, cu restul intervalului la volum de bază. Lumânarea M15 singură — doar OHLCV la acel timeframe — nu poate distinge între cele două construcții; distincția este vizibilă doar coborând la M5/M1. Este posibil ca cele două construcții să aibă traiectorii ulterioare ("aftermath") diferite.

Aceasta este ipoteza așa cum a fost înghețată (frozen v1, 2026-07-22). Nu este reformulată aici ca regulă de tranzacționare, prag de intrare/ieșire sau strategie.

## 2. Variabila de expunere și rezultatul observat

- **Variabilă de expunere (exposure):** tipul de construcție al unei lumânări M15 mari — categorie binară propusă (susținută vs. concentrată), operaționalizată ca raport R = (volumul celei mai mari sub-lumânări M1 sau M5) ÷ (volumul total al lumânării M15), plus un indicator secundar: revine sau nu volumul la nivelul de bază înainte de închiderea M15.
- **Rezultatul observat (outcome):** ce se întâmplă cu prețul după închiderea lumânării M15 ("aftermath"). În documentul frozen, acest rezultat este descris narativ, nu operaționalizat: extindere la maxime noi (instanța 12:30 din v1), consolidare laterală la noul nivel (Addendum B), reluare choppy/incompletă (Addendum C), construcție susținută din nou (Addendum D). Nu există o definiție fixă a orizontului de timp sau a pragului care separă "extindere" de "consolidare" de "reluare".

## 3. Definiția operațională existentă

Singura definiție cantitativă prezentă în artefactele oficiale este raportul R de mai sus (§4 din `candidate_v1.md`, confirmată explicit ca fiind numărabilă direct din date de bare: "countable from bar data alone"). Red Team confirmă același lucru la C1 din review ("reduced to a countable ratio... clearest, most operational observation in the whole portfolio").

Ce NU este definit operațional: pragul numeric al lui R care separă "susținut" de "concentrat" (recunoscut și de Alpha, și de Red Team ca lipsă — vezi F3), definiția lui "lumânare M15 mare" (ce prag de magnitudine/volum califică drept "mare"), și definiția outcome-ului ("aftermath").

## 4. Elemente lipsă pentru măsurare

| Element | Status |
|---|---|
| **Denominator** | Absent. Toate cele ~6 instanțe (v1 ×2 + Addenda A–D) au fost găsite prin parcurgere discreționară a unui replay (2025-08-01 → 2025-08-15), nu prin scanare sistematică. Nu există niciun număr de lumânări M15 "mari" trecute cu vederea care nu au fost adăugate ca instanțe. |
| **Praguri** | Absent. R nu are un punct de tăiere numeric; clasificarea "susținut" vs. "concentrat" este în prezent o judecată vizuală. |
| **Ferestre temporale** | Absent pentru outcome (orizontul post-închidere M15 nu este fixat — 4 bare? 8? 16?); parțial absent pentru definirea "mare" (nu există un prag relativ, ex. percentilă față de o fereastră mobilă). |
| **Unitatea de analiză** | Ambiguă: nu este clar dacă populația țintă este "toate lumânările M15" sau doar "lumânările M15 deja semnalate ca outlier" — cele două sunt seturi foarte diferite. |
| **Reguli de includere/excludere** | Absente: nicio mențiune despre excluderea weekend-urilor, sesiunilor cu lichiditate redusă (Asia), ferestrelor de gap, sau a evenimentelor macro suprapuse. |
| **Criterii pentru rezultate** | Absente: "extindere", "consolidare", "reluare choppy" nu au praguri de preț/timp care să le delimiteze obiectiv. |

## 5. Evaluarea criticii Red Team

**Confirm:**
- **F3** (pragul lipsă face clasa nedecidabilă) — verificat direct în text: nici `candidate_v1.md`, nici Addenda A–D nu conțin vreun număr pentru R.
- **F5** (fără denominator) — confirmat: toate instanțele provin din stepping discreționar, fără o rată de bază declarată.
- **F4** (alternativa volatility-clustering nu e exclusă) — confirmat: nimic din DC-0008 sau addenda nu testează construcția "susținută" împotriva unui null bazat pe regimul de volatilitate/profilul orar deja promovat în lab.
- **I6** (autocritica NFP → day-of-week) — confirmat ca disciplină metodologică reală (Addendum A elimină premisa NFP; Addendum D o reformulează spre day-of-week), dar această autocritică **nu rezolvă** golul de măsurare de la F3/F5 — rămâne o observație descriptivă suplimentară, nu o testare formală.

**Infirm parțial / extind:**
- Clasificarea finală a Red Team (§8: "Class A — READY FOR STATISTICAL VALIDATION") este acceptată ca punct de plecare rezonabil, dar **nu ca adevăr** — vezi verdictul independent la §13, care ajunge la aceeași zonă practică prin criterii proprii, nu prin deferență.
- Aplic F2 (familia este nefalsifiabilă, fiecare rezultat posibil e deja catalogat) și la seria internă de 5 instanțe 12:30 UTC a lui **DC-0008 însuși** (v1 + Addenda A, B, C, D), nu doar la cele 6 candidați-familie externi (DC-0013…0018) cum face raportul Red Team la F2. În interiorul propriului DC-0008, aceeași oră (12:30 UTC) produce deja patru rezultate diferite (extindere, consolidare, choppy incomplet, susținut din nou) — același risc de "nefalsifiabilitate prin epuizarea spațiului de rezultate" există chiar la nivelul celor 6 instanțe folosite ca dovadă principală a candidatului.

**Rămâne nedeterminat:**
- Dacă distincția binară "susținut vs. concentrat" este reală (bimodală) sau este doar un artefact continuu corelat mecanic cu mărimea/volatilitatea barei. Acesta este un aspect pe care **Red Team nu l-a semnalat explicit** ca risc separat de F4 — F4 vorbește despre regimul de volatilitate ca sursă alternativă a "participării susținute", dar nu despre posibilitatea ca raportul R însuși să fie doar o transformare monotonă a magnitudinii lumânării M15 (bare mai mari → mecanic mai multe minute cu volum peste bază → R mai mic, indiferent de vreun mecanism distinct). Tratez acest lucru ca observație statistică proprie, nu ca preluare a criticii Red Team.

## 6. Cel mai puternic argument împotriva ipotezei

Combinând F3 și F4 cu observația proprie de la §5: raportul R propus pentru a separa "susținut" de "concentrat" ar putea fi pur și simplu o funcție continuă și monotonă a mărimii/volatilității lumânării M15, nu marca a doi mecanisme distincte. Dacă barele M15 mai mari apar preponderent în regimuri de volatilitate ridicată (deja un primitiv promovat în lab — clustering acf1 ≈ +0.53), atunci participarea "distribuită pe toate minutele" ar putea fi pur și simplu semnătura mecanică a unui regim activ pe toată durata de 15 minute, nu un tip de construcție separat cu putere predictivă proprie. Sub această interpretare, "cele două construcții" nu ar fi două clase, ci două capete ale aceleiași distribuții continue — exact ceea ce F3 semnalează ca fiind netestat, dar dus mai departe: nu doar pragul lipsește, ci **există riscul ca nicio separare reală să nu existe**.

## 7. Cea mai puternică explicație alternativă (inclusiv null-ul Volatility)

**Null-ul Volatility (F4, extins):** ipoteza nulă corespunzătoare este că regimul de volatilitate — deja stabilit ca primitiv în lab (clustering + profil orar) — generează, fără niciun mecanism nou, exact tiparul observat: în regim de volatilitate ridicată, participarea rămâne elevată pe toată durata unei ferestre M15, producând aparența de "construcție susținută"; în regim normal/scăzut, un șoc izolat de o clipă produce "concentrare într-un minut". Predicție testabilă a nulului: dacă se controlează statistic pentru regimul de volatilitate ambientă (ex. ATR local, profil orar), efectul marginal al lui R asupra rezultatului post-M15 ar trebui să dispară sau să scadă drastic. Această alternativă este cea mai serioasă pentru că este deja ratificată în laborator ca fenomen real (nu este speculativă) și pentru că explică simultan construcția *și* variația inconsistentă a rezultatelor la 12:30 UTC (seria proprie a lui DC-0008).

## 8. Experimentul statistic cu puterea maximă de discriminare

Proiect propus, în 3 straturi, executabil ca un singur pipeline:

1. **Existența claselor:** pe populația completă de lumânări M15 "mari" (definite pre-înregistrat, nu ales din cele ~6 instanțe cunoscute), se calculează R pentru fiecare. Se testează unimodalitate vs. bimodalitate cu **testul dip al lui Hartigan** și cu un **model de amestec Gaussian (GMM)** comparând BIC pentru 1 vs. 2 componente.
2. **Determinarea pragului (dacă bimodal):** punctul de tăiere se derivă din date (ex. metoda Otsu sau punctul de intersecție al posteriori-lor GMM), niciodată ales vizual.
3. **Testul de informație marginală (nulul Volatility):** se regresează rezultatul post-M15 (operaționalizat, vezi §12) pe R, controlând pentru regimul de volatilitate ambientă (variabila deja existentă în lab ca primitiv). Dacă efectul lui R dispare după control, nulul de la §7 este confirmat și ipoteza colapsează.

Acest design are puterea maximă de discriminare pentru că rezolvă simultan F3 (există clasele?), F4 (clasele, dacă există, cară informație dincolo de volatilitate?) și — conform Red Team §7 — decide soarta a încă 7 candidați dependenți printr-un singur test la nivel de populație.

## 9. Datele minime necesare

- Serie completă M1 (ideal și M5) OHLCV + volum tick pentru XAUUSD/OANDA, pe toată fereastra pre-holdout (până la 2025-10-23T09:15:00Z), nu doar cele ~6 instanțe observate în replay discreționar.
- Variabila de regim de volatilitate (ATR local / Parkinson log-range, profil orar) — reutilizabilă direct din primitivul Volatility deja promovat în lab.
- Traiectoria de preț post-închidere M15 pentru minimum N bare M15 ulterioare (N de pre-înregistrat, ex. 4/8/16), pentru a calcula rezultatul.
- Metadate de sesiune/calendar (zi a săptămânii, sesiune Asia/London/NY) pentru stratificare de robustețe — nu obligatorii pentru testul central, dar necesare la §11(g).

## 10. Dimensiunea minimă a eșantionului / metoda de estimare

Eșantionul actual (n≈6, toate din același replay continuu, 2025-08-01→2025-08-15) este cu 1-2 ordine de mărime sub ce ar fi necesar pentru oricare din cele două teste:

- **Pentru testul de bimodalitate:** dimensiunea minimă trebuie derivată printr-o **analiză de putere prin simulare** — se generează amestecuri bimodale sintetice calibrate pe varianța aproximativă observată în cele ~6 instanțe cunoscute, apoi se estimează câte evenimente sunt necesare pentru ca testul dip/GMM să detecteze separarea cu putere ≥0.8. Ca reper orientativ (nu final), literatura de detectare a bimodalității sugerează ordinul a 150-300 evenimente pentru separări moderate — cifra exactă trebuie confirmată prin simularea specifică lab-ului, nu presupusă.
- **Pentru testul de informație marginală (aftermath vs. R, controlând Volatility):** dimensiunea se estimează prin putere statistică țintind un efect minim relevant (ex. o diferență de 10-15 puncte procentuale în rata de "extindere" între cele două clase, la putere 0.8), cu prag alpha corectat pentru testări multiple (vezi §11(d)) — probabil câteva sute de evenimente "mari", în funcție de rata de bază.

Concluzie: eșantionul actual nu permite nici testul de bimodalitate, nici testul de informație marginală — este suficient doar pentru a proiecta experimentul, nu pentru a-l rula.

## 11. Testele necesare

**(a) Distribuție unimodală vs. separare reală:** test dip Hartigan + GMM 1 vs. 2 componente (BIC/AIC) + interval de încredere bootstrap pe statistica dip.

**(b) Stabilitatea pragului:** re-derivarea pragului (Otsu/intersecție GMM) pe eșantioane bootstrap repetate ale populației; dacă pragul variază substanțial între reeșantionări, clasa nu este stabilă.

**(c) Sensibilitate la definiții:** rulare paralelă cu R calculat din sub-lumânări M1 vs. M5; cu definiții alternative ale "lumânării M15 mari" (prag pe volum vs. prag pe range vs. z-score față de fereastră mobilă de lungimi diferite) — o formă de analiză multiverse/specification-curve pentru a verifica dacă rezultatul depinde de o alegere arbitrară de definiție.

**(d) Testări multiple:** rezultatul acestui test servește simultan drept test și pentru DC-0010, DC-0011, DC-0013–DC-0018 (conform §7 din raportul Red Team). Orice prag de semnificație pentru efectul de tip-construcție-asupra-rezultatului trebuie corectat family-wise (Bonferroni, alpha ≈ 0.05/7 ≈ 0.007, sau Benjamini-Hochberg FDR) — nu poate fi tratat ca un test izolat, gratuit pentru DC-0008.

**(e) Temporal leakage:** fereastra de calcul a lui R folosește exclusiv date din interiorul lumânării M15 clasificate (nu există risc structural aici); dar variabila de regim de volatilitate și pragul "revenire la baseline" trebuie calculate exclusiv din date strict anterioare/interne ferestrei clasificate — fereastra de lookback pentru "baseline" trebuie pre-înregistrată (ex. 20 bare M15 anterioare) înainte de rulare.

**(f) Outcome leakage:** fereastra de rezultat (post-închidere M15) trebuie strict separată de fereastra de clasificare. Populația de validare TREBUIE construită printr-un scan automat, criteriu-condus — niciodată prin reutilizarea sau extinderea celor ~6 instanțe discreționare, care au intrat în evidență tocmai prin faptul că rezultatul lor era interesant (exact mecanismul de selecție descris la F5/F2).

**(g) Robustețe pe regimuri și perioade:** eșantionul pre-holdout se împarte în minimum 2-3 subperioade neconsecutive (ex. pe luni) și pe sesiune (Asia/London/NY); se verifică dacă (i) bimodalitatea, (ii) pragul, și (iii) efectul de predicție a rezultatului rămân stabile pe subperioade — inclusiv stratificare explicită pe eticheta de regim a primitivului Volatility, ca test central pentru F4.

## 12. Criterii preînregistrate de succes și eșec

- **Succes (candidat pentru promovare condiționată, nu automată):** distribuția lui R este semnificativ bimodală (dip test p<0.01, replicat pe ≥2 subperioade, prag stabil în bootstrap) **ȘI** clasificarea rezultată prezice rezultatul post-M15 pre-definit, cu efect care supraviețuiește controlului pentru regimul de volatilitate, la semnificație corectată family-wise, replicat pe holdout-ul rezervat (post 2025-10-23).
- **Eșec (STATISTICALLY REJECTED):** distribuția este unimodală/continuă (dip test nu respinge unimodalitatea, sau GMM cu 2 componente nu depășește 1 componentă la BIC) → dihotomia de construcție este artefact, iar DC-0008 și cei 7 candidați dependenți colapsează; SAU distribuția e bimodală dar efectul de predicție dispare după controlul pentru volatilitate (nulul de la §7 confirmat).
- **Indeterminat (rămâne TESTABLE BUT INSUFFICIENT EVIDENCE):** eșantionul asamblat este sub pragul minim de putere pre-înregistrat de la §10, sau rezultatele sunt instabile între subperioade fără semnal direcțional clar.

## 13. Verdictul permis conform protocolului

**READY FOR STATISTICAL VALIDATION.**

Motivare independentă (nu prin deferență la clasificarea Red Team, deși ajunge în aceeași zonă practică): partea de expunere a ipotezei (raportul R) este deja operaționalizabilă direct din date de bare, fără judecăți discreționare noi — acesta este singurul element din portofoliu care întrunește acest standard (confirmat independent la §3). Golurile identificate (prag, denominator, definiție outcome, populație) nu sunt goluri de **claritate conceptuală** care ar justifica NOT TESTABLE, ci goluri de **execuție a măsurării** — exact ce Faza 1 Statistician este mandatată să completeze prin proiectare (§§8-12 de mai sus). Cu designul preînregistrat furnizat aici (populație, prag derivat din date, orizont de rezultat, criterii de succes/eșec, corecție pentru testări multiple, control pentru nulul Volatility), candidatul poate intra într-o etapă formală de validare statistică.

Acest verdict **nu** este o confirmare a ipotezei — eșantionul actual (n≈6) este mult sub pragul minim necesar (§10), iar cel mai puternic argument împotrivă (§6-7) rămâne deschis și nerezolvat până la execuția testului.

## 14. Acțiunea următoare recomandată

1. Nu executa nimic pe piață live și nu colecta date noi în această fază — necesită autorizare CEO separată, conform mandatului Fazei 1.
2. Recomand CEO să autorizeze o **Fază 2 (Execuție Validare Statistică)** care implementează exact pipeline-ul de la §§8-12: scanare automată a populației de lumânări M15 mari (criteriu pre-înregistrat, nu cele ~6 instanțe discreționare), testul dip/GMM, testul de informație marginală controlat pentru volatilitate, robustețe pe subperioade, corecție family-wise.
3. Dat fiind că rezultatul acestui test decide simultan soarta a 7 candidați dependenți (DC-0010, 0011, 0013–0018 per raportul Red Team §7), recomand ca acesta să fie secvențiat înaintea evaluării separate a acelor candidați — decizia de secvențiere rămâne, desigur, a CEO.

---

**Statistician nu a modificat DC-0008, Addenda, raportul/review-ul Red Team, Knowledge Base, artefactele Alpha, sau clasificările/confidence existente.**

**Statistician se oprește aici și așteaptă aprobarea CEO înainte de următorul candidat.**
