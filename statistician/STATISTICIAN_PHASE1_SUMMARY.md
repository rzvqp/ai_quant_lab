# STATISTICIAN — PHASE 1 SUMMARY
### Sinteză metodologică din analiza DC-0008, DC-0003, DC-0004

**Report ID:** STAT-PHASE1-SUMMARY-v1
**Data:** 2026-07-24 · **Autor:** Statistician
**Bază:** cele trei rapoarte Statistician Phase 1 deja livrate și acceptate de CEO — `STATISTICIAN_PHASE1_DC-0008.md`, `STATISTICIAN_PHASE1_DC-0003.md`, `STATISTICIAN_PHASE1_DC-0004.md`. Niciun material nou nu a fost consultat pentru acest document; este o sinteză a analizelor deja făcute, nu o nouă analiză de candidat.

**Nu s-a modificat niciun Discovery Candidate, Addenda, raport Red Team sau Knowledge Base.**

---

## 1. Vulnerabilități metodologice recurente

Aceleași cinci goluri au apărut, sub forme diferite, în toate cele trei analize — deși toate trei au fost clasificate independent ca **READY FOR STATISTICAL VALIDATION**, niciuna nu avea, la momentul frozen-ului, un design complet:

| Vulnerabilitate | DC-0008 | DC-0003 | DC-0004 |
|---|---|---|---|
| **Prag numeric lipsă** (clasificarea rămâne o judecată vizuală) | Raportul R (sustained vs. concentrat) fără prag | Multiplul ATR care separă micro de HTF, propus dar netestat | N/A — pragul evenimentului (high>PDH, close<PDH) e deja numeric |
| **Denominator lipsă** (fără numărul de non-evenimente comparabile) | ~6 instanțe discreționare, fără scan sistematic | n=2 micro-C, fără număr de coiluri eșuate/reușite trecute cu vederea | Celula aleasă din 12, dar fără corecție pentru acel proces de alegere |
| **Variabile confundate** (două explicații se mișcă împreună în eșantion) | Construcție vs. magnitudine/volatilitate | Scală vs. lichiditate (ambele instanțe în tape asiatic subțire) | Sesiune vs. regim orar de volatilitate |
| **Outcome/rezultat neoperaționalizat** | "Aftermath" descris narativ, fără orizont fix | "Rezolvare" fără orizont fix | Deja fix (K6/K12) — singurul candidat fără acest gol |
| **Test decisiv necheltuit/neexecutat** | Testul de bimodalitate nu a fost rulat pe populație | Re-analiza OBS-0017 cu separare de scală nu a fost făcută | Holdout-ul OOS rezervat, CEO-gated, neatins |

**Observație transversală:** cu cât definiția evenimentului de expunere e mai precisă (DC-0004 > DC-0008 > DC-0003 pentru partea micro), cu atât golul se mută spre variabila de rezultat sau spre controlul pentru confound — niciun candidat din cele trei nu a avut ambele părți (expunere + rezultat) complet operaționalizate simultan.

## 2. Tipurile de bias întâlnite

- **Bias de selecție prin stepping discreționar** (DC-0008, DC-0003): instanțele au intrat în evidență tocmai pentru că rezultatul lor era vizibil/interesant în timpul unei parcurgeri manuale a replay-ului — mecanismul clasic prin care absența unui denominator devine periculoasă (dacă ai găsit fenomenul căutându-l, nu poți spune cât de rar e).
- **Bias de selecție post-hoc a celulei/pragului** (DC-0004): celula NY-up a fost aleasă după inspectarea a 12 celule; risc simetric pentru orice prag ales post-hoc pentru a maximiza separarea (semnalat de Statistician la DC-0003 ca risc propriu, neridicat de Red Team).
- **Confound mecanic/tautologic** (identificat de Statistician la DC-0008, nesemnalat de Red Team): raportul R propus ca marker al unui tip de construcție discret ar putea fi doar o transformare monotonă continuă a mărimii/volatilității barei — riscul ca o "dihotomie" să fie de fapt un artefact de eșantionare pe un continuum.
- **Confound de regim ambiental** (volatilitate/lichiditate) — cel mai frecvent tip întâlnit, prezent în toate trei sub forme diferite (vezi §3).
- **Testări multiple nedeclarate ca atare** (DC-0004 explicit — 6 celule, Bonferroni eșuat; DC-0008/0003 implicit — rezultatul unui singur test gatează alți 7, respectiv 1 candidați, fără ca acest lucru să fi fost tratat încă drept o familie de teste care necesită corecție comună).
- **Supra-ponderarea stabilității de semn la eșantioane mici** (identificat de Statistician la DC-0004): "sign-stable across both halves" cu n=29/n=13 și CI-uri ce includ zero este o dovadă mult mai slabă decât pare — sub null, semnul se păstrează la ~50% șansă oricum.

## 3. Explicații alternative recurente

O singură familie de explicații alternative a dominat toate cele trei analize: **regimul ambiental deja promovat ca primitiv în laborator (Volatility: clustering + profil orar).**

- **DC-0008:** "construcție susținută" ar putea fi doar semnătura mecanică a unui regim de volatilitate ridicat pe toată durata ferestrei M15, nu un mecanism separat.
- **DC-0003:** varianta locală a aceleiași explicații — regim de **lichiditate** scăzută (trough-ul profilului orar) în loc de scară, pentru cele două instanțe micro-C.
- **DC-0004:** aceeași explicație, la nivel de sesiune — efectul "NY" ar putea fi pur și simplu fereastra de vârf a profilului orar de volatilitate/participare, nu o proprietate a nivelului prior-day-high.

**Concluzie transversală:** primitivul Volatility (deja ratificat în lab) este, de departe, cea mai ieftină și mai puternică ipoteză nulă disponibilă pentru orice candidat viitor din Grupul I (microstructură/construcție) sau din orice candidat condiționat de sesiune/oră. Niciun candidat analizat până acum nu a testat explicit împotriva ei — toate trei o citează ca posibilă reducere, dar niciunul nu a rulat testul.

## 4. Controale statistice recomandate pentru toate Discovery Candidates viitoare

1. **Control obligatoriu pentru regimul de volatilitate/lichiditate ambientă** ori de câte ori candidatul implică o condiționare temporală (oră, sesiune, zi) sau o clasificare bazată pe volum/range — ca variabilă de control explicită într-un model cu termen de interacțiune, nu doar ca notă textuală.
2. **Determinarea pragurilor din date, nu din ochi** — orice separare propusă între "tip A" și "tip B" trebuie testată pentru bimodalitate/discontinuitate reală (dip test, GMM, changepoint) înainte de a fi tratată ca o clasă validă.
3. **Test placebo/control negativ** ori de câte ori e fezabil — un nivel arbitrar, o fereastră temporală de control, sau un eșantion matched-null generic — pentru a verifica specificitatea efectului dincolo de confound-urile cunoscute.
4. **Corecție family-wise explicită** de fiecare dată când rezultatul unui test servește sau gatează alți candidați din portofoliu (situație frecventă — vezi F1/F3/O1/O7 din raportul Red Team) — tratarea acestora ca o singură familie de ipoteze, nu ca teste izolate gratuite.
5. **Analiză de sensibilitate/multiverse** — re-rularea testului central cu 2-3 definiții alternative rezonabile (ferestre, orizonturi, praguri) pentru a verifica dacă rezultatul depinde de o alegere arbitrară.
6. **Verificare explicită temporal leakage / outcome leakage** — separarea strictă a ferestrei de clasificare de fereastra de rezultat, și confirmarea că populația de testare nu a fost asamblată prin reutilizarea instanțelor descoperite discreționar (care au intrat în evidență tocmai datorită rezultatului lor).
7. **Analiză de putere înainte de interpretare** — dimensiunea eșantionului necesară trebuie estimată (prin simulare sau calcul de putere), nu presupusă; un rezultat "nesemnificativ" pe un eșantion sub puterea minimă calculată nu poate fi citit ca infirmare.

## 5. Reguli de preînregistrare recomandate pentru laborator

- **Populația și criteriile de includere/excludere** se fixează înainte de a inspecta rezultatele (nu se aleg retroactiv pentru a se potrivi instanțelor deja găsite).
- **Metoda de determinare a pragului** (dacă există o clasificare binară) se fixează în avans — niciun prag nu se alege pentru a maximiza separarea observată pe același set de date pe care va fi testat efectul.
- **Orizontul și definiția variabilei de rezultat** se fixează în avans, cu un număr fix de bare/ore post-eveniment.
- **Planul de corecție pentru testări multiple** (care familie de teste, ce metodă de corecție) se declară înainte de rulare, mai ales când candidatul e explicit legat de alți candidați din portofoliu.
- **Analiza de putere/dimensiunea eșantionului** se calculează și se documentează înainte de rulare, chiar dacă aproximativă.
- **Criteriile de succes și eșec** se scriu înainte de a atinge datele, în termeni care permit un verdict din cele cinci categorii ale protocolului Statistician.
- **Resursele irepetabile (holdout OOS)** se cheltuiesc o singură dată, cu designul complet blocat/aprobat înainte de execuție — niciodată în încercări repetate până la un rezultat convenabil.

## 6. Recomandări pentru Alpha — formularea ipotezelor pentru testabilitate mai ușoară

1. **Propune un prag candidat**, chiar aproximativ, pentru orice distincție categorică (ex. "sustained vs. concentrat", "micro vs. HTF") — chiar dacă netestat, un punct de plecare numeric scurtează drastic drumul spre "ready for validation".
2. **Definește orizontul de rezultat** de la formularea inițială (ex. "N bare după eveniment"), nu doar descrierea narativă a ce s-a întâmplat ulterior.
3. **Raportează explicit denominatorul sau absența lui** — o singură propoziție de tipul "nu am numărat câte evenimente comparabile am trecut cu vederea" (deja practicată de Alpha în mai multe candidate) ajută enorm și ar trebui generalizată ca standard, nu excepție.
4. **Continuă practica de a numi confound-urile cunoscute** (scale/liquiditate la DC-0003, NFP/day-of-week la DC-0008) — aceasta a fost, de fiecare dată, punctul de plecare exact pentru testul cel mai puternic proiectat de Statistician. Este deja un punct forte real al metodologiei Alpha și nu ar trebui slăbit.
5. **Când se depune o familie de candidați înrudiți** (ex. seria de construcție din DC-0008/0013-0018), semnalează explicit dacă descriptorii care îi diferențiază au fost specificați înainte de observare sau notați post-hoc — asta ajută la detectarea timpurie a riscului de tip F1/F2 (familie nefalsifiabilă).

## 7. Recomandări pentru Red Team — criticile cu cea mai mare valoare

- **Critica C3 (Alternative Explanation)** a fost, de departe, critica cu cea mai mare valoare marginală în toate cele trei cazuri — a numit exact confound-ul (volatilitate/lichiditate) pe care Statistician l-a folosit ca bază pentru designul testului decisiv de fiecare dată. Recomand ca această critică să rămână prioritatea #1 a bateriei, cu accent explicit pe "este acest efect reductibil la un primitiv deja promovat în lab?"
- **Analiza la nivel de portofoliu** (F1-F9, contradicții cross-candidat, denominator absent peste tot) a adăugat mai multă valoare decât critica per-candidat izolată — a expus goluri (F3, F4, F5) pe care niciun review individual nu le-ar fi putut vedea. Recomand continuarea/extinderea acestui tip de analiză transversală la fiecare rundă de Discovery Candidates noi.
- **Critica C1 (Observation Quality)**, deși utilă pentru triaj, a adăugat cea mai mică valoare marginală pentru testabilitate — un candidat poate fi "clar formulat" (C1 ✓) și totuși complet netestabil din lipsă de prag/denominator/orizont. Recomand ca C1 să rămână un filtru de intrare, nu un indicator de pregătire pentru validare.
- Continuarea practicii de a marca explicit "Reducible to: [primitiv X]" per candidat (folosită deja la DC-0008 și DC-0004) este exact ce a permis Statistician să proiecteze rapid testul de control — recomand generalizarea acestei etichete la toți candidații viitori din Grupul I sau condiționați temporal.

## 8. Checklist statistic standard — reutilizabil în toate evaluările viitoare

```
[ ] 1. Ipoteza reconstruită fidel din artefactele oficiale, fără reformulare ca strategie
[ ] 2. Variabila de expunere identificată și operaționalizată explicit
[ ] 3. Variabila de rezultat (outcome) identificată, cu orizont fix sau semnalată ca lipsă
[ ] 4. H0 și H1 formulate explicit
[ ] 5. Definiția operațională completă verificată: prag, fereastră temporală, populație,
       reguli de includere/excludere, criterii de rezultat
[ ] 6. Denominator: declarat de sursă sau semnalat explicit ca lipsă
[ ] 7. Dacă există o dihotomie/clasificare propusă: testată pentru bimodalitate/discontinuitate
       reală (dip test / GMM / changepoint), nu presupusă vizual
[ ] 8. Confound-uri cunoscute din lab (Volatility clustering, profil orar, lichiditate)
       identificate și incluse ca variabile de control obligatorii, nu doar menționate
[ ] 9. Test placebo/control negativ inclus, dacă fezabil
[ ] 10. Testări multiple: identificată familia de candidați/teste conexă și metoda de
        corecție (Bonferroni/BH)
[ ] 11. Verificare temporal leakage (variabilele de control/clasificare folosesc doar
        date anterioare evenimentului)
[ ] 12. Verificare outcome/selection leakage (populația de test nu reutilizează instanțe
        descoperite discreționar pe baza rezultatului lor)
[ ] 13. Sensibilitate la definiții alternative (multiverse) planificată pentru cel puțin
        2-3 variante rezonabile
[ ] 14. Putere statistică / dimensiune minimă a eșantionului estimată explicit (simulare
        sau calcul), nu presupusă
[ ] 15. Criterii preînregistrate de succes și eșec scrise înainte de orice rulare
[ ] 16. Evaluare independentă a criticii Red Team: ce se confirmă, ce se infirmă, ce
        rămâne nedeterminat — niciodată deferență automată la verdictul lor
[ ] 17. Verdict ales dintre cele 5 categorii permise, cu motivare independentă
[ ] 18. Pas următor recomandat fără a executa testul propriu-zis (Statistician proiectează,
        nu validează)
[ ] 19. Resurse irepetabile (holdout OOS) semnalate explicit ca atare, cu recomandare
        de a nu fi cheltuite fără design complet aprobat
```

---

**Acest document este un ghid metodologic reutilizabil, nu o analiză de candidat. Nu modifică Discovery Candidates, Addenda, rapoartele Red Team sau Knowledge Base.**

**Statistician se oprește aici și așteaptă aprobarea CEO.**
