# DESIGN — GOLUL G8
### Exprimarea unei familii de corecție formată din celulele cu `n ≥ 25`, declarată înainte de execuție, fără selecție după rezultate

**Document ID:** VE-GAP-G8-DESIGN-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Statut:** **DESIGN — pentru decizia CEO.** Registrul NU a fost modificat. Nicio implementare. F3 neînceput.
**Context:** decizie CEO — seed rămâne `derived_from_spec_hash` (fără excepție); G8 se tratează ca **limitare generică** de expresivitate, nu ca particularitate DC-0004. Descoperit la exprimarea Căii A (`F2_3_REPORT.md` §5).

---

## 1. Problema exactă

Statisticianul vrea să exprime: *„aplică Bonferroni pe celulele sesiune×direcție care au n ≥ 25 evenimente; pragul corectat = 0.05 / (numărul de celule eligibile)."* Aceasta este exact regula din `obs0012` (`cells = [(d,s) if len≥25]; thr = 0.05/len(cells)`).

Dificultatea: **mărimea familiei se cunoaște abia după atingerea datelor** (depinde de câte celule ating n≥25), dar **regula care o determină trebuie fixată înainte de execuție**. Cele două nu se contrazic — o regulă preînregistrată poate produce o familie de mărime dependentă de date — dar modelul actual nu poate exprima o astfel de familie.

Două comportamente cuplate, azi ambele inexprimabile corect:

- **(a) eligibilitate per-celulă la testare** — o celulă cu n < 25 produce *niciun rezultat* și este *exclusă din familie*, în loc să oprească rularea;
- **(b) dimensionarea familiei** — `m` = numărul de celule eligibile; corecția se aplică pe familia realizată, nu pe cea candidată.

Pericolul de evitat, formulat de CEO: regula **nu trebuie să permită selecție după rezultate**. Filtrarea după `n` (mărime de eșantion, cantitate pre-rezultat) este legitimă; filtrarea după `p` sau după efect ar fi circulară și ar umfla eroarea.

---

## 2. De ce modelul actual nu o poate exprima

1. **`multiple_testing.members` cere enumerare statică** (regula R7 a validatorului, întărită la G5): fiecare membru este un `test_target` enumerat, iar **motorul nu deduce apartenența la familie** (contract §2.9). O familie de mărime dependentă de date nu poate fi o listă fixă fără a preda motorului decizia „cine intră".
2. **`min_n` are semantică de OPRIRE, nu de excludere.** `population.min_n` și `matched_null@v1.min_n` opresc rularea (E6) sub prag — corect pentru populația întreagă, dar la nivel de celulă comportamentul dorit este *drop-and-exclude*, nu *halt*.
3. **Pragul corectat e derivat de metodă din `family_members`.** `bonferroni@v1` calculează `alpha / len(family_members)`; cu membri statici, pragul e fix, nu empiric.

---

## 3. Cerințele soluției

Toate obligatorii; oricare încălcată descalifică varianta.

| # | Cerință | Motiv |
|---|---|---|
| R1 | **Declarativă** — regula e un obiect din specificația înghețată, nu o alegere a motorului | contract §2.9 |
| R2 | **Preînregistrată** — fixată înainte de orice atingere a datelor, intră în hash-ul specificației | constituție §8 |
| R3 | **REGULA DE AUR — independență de rezultat:** eligibilitatea poate referi **exclusiv** cantități pre-rezultat (`n`, `denominator`, `event_count`). **Niciodată** `p`, statistica observată sau efectul | altfel corecția devine circulară; aceasta este linia dintre un filtru legitim de eșantion și un artefact de selecție după rezultat |
| R4 | **Fail-closed la încălcarea R3** — o regulă care referă o cantitate de rezultat e respinsă la validare, înainte de orice date | interdicția R3 trebuie mecanică, nu convenție |
| R5 | **Deterministă** — aceeași specificație + date → aceeași familie | reproductibilitate |
| R6 | **Auditabilă** — motorul raportează familia realizată: eligibili, excluși (cu cantitatea care a produs excluderea), `m`, pragul | Statisticianul reconstruiește și auditează `m` |
| R7 | **Motorul aplică, nu judecă** dacă `n≥25` e pragul statistic potrivit — aceea rămâne judecata Statisticianului | separarea rolurilor |
| R8 | **Compatibilă cu Bonferroni și BH existente** — consumă familia realizată, fără logică nouă de corecție | suprafață minimă |
| R9 | **Distincție halt vs. drop** — eligibilitatea per-celulă *exclude*; `min_n` la nivel de populație rămâne *oprire* | cele două nu se confundă |

---

## 4. Variantele posibile

### V0 — Familie fixă (fără G8)
Se enumeră static toate cele 8 celule, corecție `0.05/8`. Nu rezolvă G8; este o **alegere de proiectare alternativă**.
- **Riscuri:** nu replică in-sample (familia empirică era `0.05/len(n≥25)`); mai conservatoare (pierde putere); reintră în tensiunea Calea A/B — necesită ca Statisticianul să renunțe explicit la familia empirică. **NU** este substituentul nenormativ respins de CEO — este un design onest, dar diferit de in-sample.

### V1 — Regulă de eligibilitate declarativă pe câmpuri pre-rezultat *(recomandată)*
Membrii candidați rămân enumerați static; se adaugă o **regulă de eligibilitate** — o comparație între un **câmp pre-rezultat al membrului** (dintr-o listă albă din registru) și o constantă numerică. Familia realizată = candidații eligibili; `m` derivat.
```
member_eligibility: { field: "n", op: ">=", value: 25 }
```
`field` provine dintr-o **listă ÎNCHISĂ**: `{n, denominator, event_count}` — care **nu conține** `p_hat/observed/effect`, deci R3 e impusă prin vocabular.
- **Riscuri:** calculul familiei realizate e o operație de execuție (cere `n`, deci date) — aparține F5+, nu validării; trebuie clar separat „validarea regulii" (fără date) de „aplicarea ei" (cu date). Risc rezidual: dacă lista albă e prost aleasă și include un câmp cvasi-rezultat, R3 slăbește — de aceea lista albă e ea însăși o decizie de guvernanță.

### V2 — Prag scalar dedicat pe metodă (`min_member_n`)
`bonferroni@v1`/`BH` primesc un parametru `min_member_n: 25`; motorul exclude membrii sub prag.
- **Riscuri:** rezolvă *doar* cazul „prag pe n", nu generic (denominator, event_count ar cere alți parametri, proliferare); mai puțin expresiv decât V1; totuși simplu și greu de folosit greșit (un scalar pe n nu poate referi un rezultat). Un compromis „îngust dar sigur".

### V3 — Eligibilitate ca proprietate a testului stratificat (nu a corecției)
Testul (`matched_null@v1` etc.) capătă o regulă de eligibilitate per-celulă; celulele neeligibile nu produc rezultat; familia = celulele care au produs rezultat.
- **Riscuri:** leagă mărimea familiei de un efect secundar al testului („ce celule au produs rezultat"), mai greu de auditat decât o regulă explicită; ambiguu dacă o celulă a fost exclusă prin eligibilitate sau printr-o eroare de execuție (E7). Amestecă drop-ul cu raportarea.

### V4 — Post-procesare de către Statistician
Motorul returnează p și `n` per celulă; Statisticianul aplică manual pragul empiric.
- **Riscuri:** mută corecția din specificația preînregistrată în interpretarea manuală — exact ce contractul cere să fie în spec (§1.5); pierde auditabilitatea mecanică; reintroduce o etapă discreționară. Contrazice R1/R2.

---

## 5. Recomandarea mea

**V1** (regulă declarativă pe listă albă pre-rezultat), cu **V2 ca formă redusă acceptabilă** dacă se dorește o suprafață minimă acum.

Argumente:
1. **Respectă toate cele nouă cerințe.** R3 devine mecanică prin lista albă de câmpuri, nu prin disciplină — o regulă care încearcă să filtreze după `p` se oprește (E3), pentru că `p_hat` nu e în lista albă.
2. **Generică** (vezi §7), nu o rezolvare punctuală pentru DC-0004.
3. **Auditabilă** — familia realizată e raportată integral.
4. **Compatibilă** cu corecțiile existente; nu atinge logica Bonferroni/BH.

Resping V3 și V4 (auditabilitate slabă / mută corecția din spec). V0 rămâne o cale validă **dacă** decideți amânarea G8 și Statisticianul acceptă o familie fixă în locul celei empirice — dar atunci nu mai e replicare strictă.

Observație de guvernanță (R7): motorul garantează mecanic că **nu** se filtrează după rezultat, dar **nu** poate garanta că `n≥25` este pragul statistic corect — aceea rămâne judecata Statisticianului. G8 mută în cod *siguranța* (anti-circularitate), nu *corectitudinea alegerii*.

---

## 6. Modificările necesare (registru, validator, teste)

**Neimplementate — enumerate pentru designul detaliat de după aprobare.**

### 6.1 Registru (v1.4, dacă se aprobă)
- **Listă albă publicată** de câmpuri pre-rezultat eligibile: `member_eligibility_fields = [n, denominator, event_count]`. Explicit **fără** `p_hat/observed/effect`.
- Parametru nou la `bonferroni@v1` și `benjamini_hochberg@v1`: `member_eligibility` (obiect `{field, op, value}`), sau — pentru V2 — `min_member_n` scalar.
- Regulă nouă: `family_realized_reporting` — motorul raportează obligatoriu eligibili/excluși/`m`/prag.
- Clarificarea semanticii **drop vs. halt** la nivel de celulă (R9): eligibilitatea exclude; `min_n` de populație oprește.

### 6.2 Validator
- Verificarea **R3/R4**: `member_eligibility.field` trebuie să fie din lista albă; altfel E3, **înainte de orice acces la date**.
- `value` numeric (R2), `op` din setul de comparatori.
- **Fără calcul de familie la validare** — determinarea familiei realizate are nevoie de `n`, deci aparține execuției (F5+); validarea verifică doar buna-formare a regulii.
- Membrii candidați rămân enumerați static și validați ca acum (R7 existent).

### 6.3 Teste
- **Mutații** (extind bateria): `member_eligibility.field = p_hat` → respins (R3, E3); `field` inexistent → E3; `value` ne-numeric → E2; regulă bine-formată pe `n` → trece forma, se oprește doar pe calibrare.
- **Invarianți de registru:** lista albă nu conține niciun câmp de rezultat; `member_eligibility_fields` prezent.
- **Conformitate (F5+, când există execuția):** familie realizată corectă pe date sintetice cu suport per-celulă cunoscut; determinism; raportarea eligibili/excluși; verificarea că schimbarea rezultatelor (p) **nu** schimbă familia (dovada R3 la runtime).
- **Specificația de referință DC-0004:** înlocuirea substituentului static cu regula `member_eligibility {field: n, op: ">=", value: 25}`, ajungând la replicare strictă completă.

### 6.4 Schema
- **Probabil niciun impact:** regula poate locui în `multiple_testing.params` (obiect liber validat de registru). Dacă se preferă un câmp de nivel superior în `multiple_testing`, atunci **da**, schemă nouă. Se fixează la designul detaliat. Preferința mea: în `params`, pentru a păstra invariantul „extinderea vocabularului nu cere schemă nouă".

---

## 7. Generic sau specific DC-0004?

**Generic.** DC-0004 este doar primul loc unde apare. Aceeași structură reapare la:

| Situație | Cum apare G8 |
|---|---|
| **DC-0008 + 7 dependenți** (§11d) | familia cross-candidat — dependenții cu prea puține instanțe trebuie excluși prin aceeași regulă |
| **Orice test stratificat** | celule cu suport mic (sesiuni subțiri, sub-perioade scurte) |
| **Multiverse** | variante de grilă fără suficiente instanțe |
| **FDR de portofoliu** | `docs/EMPIRICAL_PVALUE_SPEC.md` folosește deja „universul eligibil" (m=1552 valid vs 1704) — G8 **operaționalizează un concept pe care laboratorul îl folosește deja informal**, dându-i formă declarativă și auditabilă |

Ultimul rând este decisiv: G8 nu introduce un concept nou; face din „eligibil" o proprietate **declarată și preînregistrată**, în loc de una ad-hoc. De aceea trebuie tratat generic, nu ca un plasture pentru DC-0004.

---

## 8. Ce urmează (proces, nu implementare)

1. Aprobați **V1** ca mecanism (sau V2 ca formă redusă), cu **R3 impusă prin lista albă**.
2. Decideți **momentul:** registru v1.4 acum (deblochează replicarea strictă completă a DC-0004) vs. amânare (DC-0004 pe familie fixă V0, dacă Statisticianul acceptă abaterea de la in-sample).
3. **Nu se implementează** până la un design detaliat care fixează: lista albă exactă, locul regulii (params vs. schemă), semantica drop-vs-halt.
4. **R3 este ne-negociabilă** indiferent de variantă.

---

**Registrul nu a fost modificat. Nicio implementare. Nicio dată de piață citită. Validation Engine se oprește și așteaptă decizia CEO asupra §5 și §8.**
