# STATISTICIAN — REVIEW INDEPENDENT AL PRE-ÎNREGISTRĂRII SCOPED GLOBAL-FDR
### Comisă înainte de execuție, pentru Research Lab — nu aprobare, nu respingere

**Document ID:** STAT-REVIEW-SCOPEDFDR-v1.0
**Data:** 2026-07-25 · **Autor:** Statistician
**Statut:** Review independent. **Nu aprob, nu resping — nu e obiectul meu.** Livrat pentru ca Research Lab să-l citească înainte de rulare.
**Obiect revizuit:** `docs/SCOPED_FDR_PREREGISTRATION_v1.0.md` + `code/subset_enumerate.py` + `results/matched_null_validation/subset_prereg_enumeration.json`, toate din commit `ea36005`.
**Surse suplimentare citite pentru verificare:** `docs/MATCHED_NULL_VALIDATION.md` (commit `69747fd`, 2026-07-13), `docs/EMPIRICAL_PVALUE_SPEC.md`, `mstrat.py`.
**Nu am modificat pre-înregistrarea, codul, sau vreun artefact al Research Lab.**

---

## Răspuns la cele 5 întrebări

### 1. Criteriul de apartenență e derivat din gramatică, nu din rezultate?

**Da, verificat direct în cod, nu doar în text.** `code/subset_enumerate.py` construiește populația prin `for fam in MS.REGISTRY: for h in MS.REGISTRY[fam][0](): rows.append(dict(id=h['id'], fam=fam, stop=h.get('stop')))` — iterează generatoarele de gramatică (`s1_setups`...`s20_setups`) și extrage câmpul `stop`, o proprietate STRUCTURALĂ a ipotezei (tipul de stop pe care gramatica îl atribuie), nu o măsură de performanță. Clasificarea `atr_indomain` / `structural_excluded` / `ambiguous_excluded` se face exclusiv pe valoarea acestui câmp — nicio referință la R, win-rate, Sharpe sau orice rezultat de backtest intervine în această decizie.

Singurul loc unde `FAMILY_RESULTS.parquet` (date derivate din rulare) intră în calcul e filtrul de eligibilitate `n≥25` — dar acesta e un criteriu de **fezabilitate statistică** (destule tranzacții pentru ca un test să aibă sens), nu de performanță; se aplică identic peste toată gramatica, indiferent de cât de bine arată o ipoteză.

**Observație minoră, nu un defect:** `n` (numărul de tranzacții) ar putea, teoretic, să coreleze cu tipul de stop într-un fel care introduce o formă subtilă de distorsiune (ex. dacă stopurile structurale produc sistematic mai puține tranzacții executate din alte motive decât calitatea ipotezei). Pragul se aplică însă identic peste toată gramatica, nu selectiv — risc teoretic, nu unul concret identificat.

### 2. `m` efectiv și pragul BH sunt corect calculate?

**Da.** Verificare aritmetică directă: 1972 = 428 (atr) + 1532 (structural) + 12 (ema) — exact, fără categorie neexplicată. 428 − 16 (n<25) = 412. Prag BH rang-1: 0,05/412 = 1,214×10⁻⁴ — recalculat independent, se potrivește.

**Ambiguitatea m=1552 vs. m=1800, verificată independent, nu doar citată din documentul revizuit:** am citit direct `docs/EMPIRICAL_PVALUE_SPEC.md` — acolo se citează "m=1552 (valid)" și "m=1704 (incl. invalid)" ca diagnostic, **fără nicio formulă operațională** care să spună exact ce înseamnă "valid" dincolo de această mențiune. Confirm: ambiguitatea e reală și nu e rezolvabilă din artefactele disponibile — pre-înregistrarea nu ascunde o definiție pe care ar fi putut s-o găsească; ea chiar nu există explicit nicăieri. Alegerea m=412 (subset ATR-stop din n≥25=1800, nu din necunoscutul 1552) e conservatoare exact cum pretinde documentul — un `m` mai mare aici înseamnă un prag mai strict, deci mai greu de declarat supraviețuitor.

### 3. Configurația declarată e într-adevăr singura validată pentru acest obiect?

**Da, confirmat direct în raportul de validare, nu doar acceptat din pre-înregistrare.** `docs/MATCHED_NULL_VALIDATION.md` §9, Limitări, punctul 1: *"Validated in the unstratified + ATR-scaled configuration only. Session×vol stratified nulls are NOT separately validated → deferred."* Coincide cuvânt cu cuvânt cu ce declară pre-înregistrarea. Calibrare (§7 PASS), putere (§8 PASS, monoton în mărimea efectului), robustețe adversarială (§9, 12 scenarii, toate FPR≤0,075) și paritate cu `mstrat.simulate` (§11, diferență <1e-12) — toate verificate ca fiind pe **exact** această configurație, nu pe o versiune generică a motorului.

### 4. Regula de nedecis, MC-ul adaptiv, separarea research/validare — suficiente, sau lipsește ceva ce aș fi cerut la un Discovery Candidate?

Măsurat pe propriul meu standard (`STATISTICIAN_CONSTITUTION_v1.0.md`, checklist-ul de 20 de puncte):

**Prezente și solide:** populație fixată înainte de rezultate ✓; metodă de prag fixată în avans (BH, nu ales post-hoc) ✓; criterii de succes/eșec scrise înainte de date ✓; separare research/validare fără agregare ✓ (aceasta e exact controlul placebo/independent pe care l-aș fi cerut); regula UNRESOLVED bazată pe interval de încredere, nu pe un singur p ✓; oprire secvențială cu păstrarea secvenței RNG pentru cazurile escaladate ✓.

**Ce aș fi cerut suplimentar la un Discovery Candidate, și lipsește aici:**
- **O analiză de putere specifică pragului BH efectiv (1,214×10⁻⁴), nu doar curba de putere generică a motorului.** §8 din raportul de validare arată putere ≈0,98-1,00 la o mărime de efect de 1,0×ATR — dar acea curbă a fost calibrată la un prag de semnificație mai permisiv (zona α=0,05), nu la pragul mult mai strict al acestui test scopat. Nu există, în pre-înregistrare, o afirmație de tipul "la m=412 și acest n tipic, puterea de a detecta un efect de mărime X este Y%". Fără ea, un rezultat "zero supraviețuitori" nu poate fi distins complet de "testul n-a avut destulă putere să vadă un efect real la acest prag".
- **O verificare de sensibilitate a pragului n≥25.** N-am găsit nicio mențiune a ce s-ar întâmpla cu m (și deci cu pragul BH) dacă eligibilitatea ar fi n≥20 sau n≥30 — un test simplu, ieftin, care ar arăta dacă alegerea 25 e robustă sau fragilă.

Niciunul din acestea două nu invalidează designul — dar la un Discovery Candidate, aș fi cerut ambele înainte de a considera specificația "gata pentru validare".

### 5. Poate designul, așa cum e scris, produce un FALS NEGATIV — poate ascunde un efect real?

Trei mecanisme concrete, nu doar unul generic:

**(a) Configurația "unstratified" e conservatoare, iar conservatorismul taie în ambele direcții.** Raportul de validare admite explicit (§9, Limitări, punctul 2): *"conservative under strong drift... means the test is a touch harder to pass for genuinely-timed edges in a trending market."* Dacă un efect real e condiționat de sesiune sau regim de volatilitate (funcționează doar în NY, sau doar în regim de volatilitate ridicată), un nul nestratificat — care amestecă toate sesiunile/regimurile la reeșantionare — poate dilua exact acel semnal condiționat, reducând puterea de a-l detecta. Aceasta nu e o presupunere abstractă — e recunoscută direct de raportul de validare al motorului, aplicată acum la un test cu un prag de 400× mai strict decât cel calibrat.

**(b) Scoparea la regimul ATR face invizibil, prin construcție, orice efect din regimul structural (D2).** Cele 1532 ipoteze cu stop structural nu sunt doar "excluse din test" — sunt excluse din a fi testate DELOC în această rundă. Dacă un efect real există specific acolo, acest FDR scopat nu-l va găsi niciodată, nu pentru că testul a eșuat, ci pentru că nu a fost rulat pe acel domeniu. Aceasta e o limitare de domeniu declarată onest (nu ascunsă) — dar merită spusă direct, nu doar dedusă: **"zero supraviețuitori" la finalul acestei runde nu spune nimic despre cele 1532 de ipoteze structurale.**

**(c) Regula de oprire secvențială (MC-1, k_ge>1000 la B=20.000) — precisă numeric, dar formulată informal.** Textul spune că acest prag "garantează p>0,05" — corect doar dacă interpretat ca fapt determinist despre estimarea la acest B, nu ca o garanție asupra p-ului adevărat (asimptotic). Am verificat totuși magnitudinea: pragul de oprire corespunde unei rate de ~0,05, în timp ce pragul BH real aplicabil e 1,214×10⁻⁴ — o distanță de ~400×. La o ipoteză cu p adevărat în jurul pragului BH real, k_ge așteptat la B=20.000 e de ordinul a 2-3, cu o abatere standard minusculă; a ajunge la k_ge>1000 din zgomot Monte Carlo pur ar cere o deviație de zeci de abateri standard — practic imposibil. **Concluzie: regula e sigură numeric, dat fiind decalajul enorm dintre pragul de oprire și pragul real de respingere — dar formularea ("garantează") ar merita o derivare explicită (ex. o margine formală de încredere), nu doar afirmată, mai ales dacă acest tipar de oprire se refolosește vreodată la un decalaj mai mic între prag și rang-1.**

---

## Evaluare generală

Designul e solid. Nu am găsit nimic care ar trebui să blocheze execuția. Cele două goluri de la Q4 (putere specifică pragului, sensibilitate n≥25) și cele trei mecanisme de la Q5 nu sunt defecte care invalidează pre-înregistrarea — sunt limite cunoscute, parțial declarate deja, pe care le fac explicite acum, cât încă se poate, fără să devină ajustare post-hoc.

---

## Întrebarea de guvernanță — recomandare, nu decizie

**Recomand: separare parțială, cu Statistician emitent al verdictului agregat asupra campaniei, nu al fiecărei ipoteze individual.**

Motivare:

1. **Opțiunea "Research Lab proiectează, execută ȘI interpretează" reintroduce exact conflictul pe care separarea Statistician↔Validation Engine a fost creată să-l elimine la nivel de DC.** Nu văd niciun motiv pentru care riscul ar fi diferit la nivel de campanie — dimpotrivă, la m=412 ipoteze mecanice, tentația de a "explica" un rezultat nul sau de a acorda mai multă greutate unui supraviețuitor marginal e la fel de reală.

2. **Statistician nu ar trebui să repete, pentru fiecare din cele 412 (sau câți supraviețuiesc), analiza narativă de 17 pași folosită pentru un Discovery Candidate.** Ipotezele de gramatică nu au aceeași natură — sunt combinatorii, nu descoperite discreționar. Ce Statistician ar trebui să facă, așa cum tocmai am făcut aici, e (a) revizuirea independentă a designului **înainte** de rulare, și (b) certificarea rezultatului agregat **după** rulare — a spune dacă "zero supraviețuitori" e un rezultat valid al unui test bine construit, sau dacă un supraviețuitor rezistă la controlul de validare independent — nu re-judecarea fiecărei ipoteze una câte una.

3. **Execuția rămâne a celui care rulează Monte Carlo-ul** (Research Lab sau echivalentul său pentru campanie, analog rolului Validation Engine la DC) — dar verdictul final asupra a ce înseamnă statistic rezultatul nu ar trebui să fie emis de aceeași parte care a rulat testul.

4. **Nu presupun această extindere ca fiind deja în vigoare.** Contractul actual acoperă explicit doar Discovery Candidates. Recomand ca această separare să fie ratificată explicit de CEO, ca amendament sau contract paralel — exact cum a fost ratificat contractul Statistician↔Validation Engine — nu asumată tacit de mine acum.

---

**Nu am aprobat, nu am respins pre-înregistrarea. Nu am modificat niciun artefact al Research Lab.**

**Statistician se oprește aici. Livrat pentru citire de Research Lab înainte de rulare, și pentru decizia CEO asupra structurii de guvernanță.**
