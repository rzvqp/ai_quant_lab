# STATISTICIAN — R10, D-3, D-4: CONVENȚII DE CONCENTRARE, ROTUNJIRE ȘI CENZURARE

**Document ID:** STAT-R10-D3-D4-CONVENTIONS-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Verificare de sursă:** citit `edge_research/mandate41_eval.py::_conc` (implementarea actuală a concentrării) și căutat `BASE` / `STRESS` / `R7` / `R10` în manifest și în toate documentele laboratorului.

---

# PARTEA 0 — DOUĂ CONSTATĂRI ÎNAINTE DE DECIZII

## 0.1 R10, aplicat literal, NU e satisfiabil azi

**Implementarea existentă, verbatim:**

```python
if s > 0:
    d["best_over_sumR"] = round(float(a[0]) / s, 4)      # s = sumR = NET
else:
    d["concentration"] = "N/A (net sumR <= 0)"           # metrica LIPSEȘTE
```

> **Numitorul e NETUL. Deci `best_trade_share` e NEDEFINIT pentru orice candidat cu net ≤ 0 — și e NEMĂRGINIT când netul se apropie de zero: la net +0,001R și o tranzacție de +2,6R, raportul e 260.000%. R10 spune „obligatoriu în fiecare rezultat", dar pentru CAND-0009 (net negativ) numărul nu există.**

**Rezolvarea e la Partea 1 și nu cere o metrică nouă.**

## 0.2 BASE și STRESS nu există în nimic ce pot citi

```
căutat în split_manifest.json:   "STRESS" 0 apariții · "R7" 0 · "R10" 0 · "trimmed_top1" 0
căutat în toate .md din lab:     "STRESS" 0 fișiere
(„R7"/„R10" apar doar ca ID-uri de risc Red Team dintr-un audit fără legătură)
```

> **Leg convenții de un cadru pe care NU l-am putut verifica. Nu blochez — D-3, D-4 și câmpurile R10 sunt decidabile independent — dar consemnez: „compari numai rezultate cu aceeași configurație" nu e VERIFICABIL până când BASE și STRESS au o definiție scrisă și un hash. Cerința minimă e la Partea 4; nu construiesc cadrul, cer doar să fie numit.**

---

# PARTEA 1 — R10: cele trei câmpuri, definite executabil

```
best_trade_share      LevelOutput[float]
                      value = max(R) / sum(R)   DOAR dacă sum(R) > 0
                      altfel Unavailable(reason="net_non_positive")
trimmed_top1_avg_R    float — media R după eliminarea celor mai mari n_trimmed valori
n_trimmed             int   — numărul EFECTIV eliminat (vezi D-3)
```

## De ce PĂSTREZ netul ca numitor, deși e cel fragil

**Am considerat mutarea pe profitul brut (suma R pozitivi): mereu definit, mărginit în (0,1]. Am RESPINS-O, din două motive:**

```
1. Ar INVALIDA fiecare cifră publicată. CAND-0037 raportat la 17% (best/NET) ar deveni 3,9%
   (best/BRUT, din agregatele derivate: best 2,59R / brut 65,75R). Toate comparațiile
   istorice — 78%, 35%, 22% — ar deveni necomparabile, pentru zero câștig de informație.
2. Netul e mărimea DECIZIONAL relevantă. „17%" înseamnă: scoți tranzacția, pierzi 17% din
   linia de jos. Brutul răspunde la o întrebare pe care n-o pune nimeni.
```

**Fragilitatea se rezolvă prin CONTRACT, nu prin schimbarea metricii: câmpul e OBLIGATORIU ÎNTOTDEAUNA, valoarea există doar când e definită. Asta face R10 satisfiabil literal — R10 impune CÂMPUL, nu NUMĂRUL.**

**Însoțitor obligatoriu, ca instabilitatea să fie vizibilă: se raportează `sum(R)` alături, plus `wo1_still_positive` (deja calculat în `_conc`, versiunea binară robustă, definită ori de câte ori netul e definit). Niciun câmp nou.**

---

# PARTEA 2 — D-3: rotunjirea. ACCEPT `ceil`, minim 1 — dar singură NU e deterministă.

## Decizia

```
n_trimmed = max(1, ceil(0.01 * n))
```

**Motivul, în direcția Arhitectului: `floor` lasă orice n < 100 NETĂIAT, adică exact eșantioanele mici scapă de test — și acolo concentrația e cel mai periculoasă. `round` e DESCALIFICAT separat, pe determinism: half-to-even vs half-up diferă între implementări, iar la n=50 (1% = 0,5) dau răspunsuri diferite.**

## Ce lipsește din recomandare, și fără ce regula NU e deterministă

> **`ceil, min 1` fixează CÂTE se taie. Nu fixează CARE. Dacă mai multe tranzacții au R identic la graniță, rezultatul depinde de stabilitatea sortării — adică de implementare. Recomandarea e necesară, dar nu suficientă.**

```
DEPARTAJARE, obligatorie:  sortează după (R DESC, entry_index ASC); ia primele n_trimmed.
Tăierea e pe valoarea R, INDIFERENT de semn — nu „primii n_trimmed câștigători".
```

## Două consecințe pe care le impun odată cu regula

```
1. FRACȚIA REALIZATĂ variază cu n:  1,2% la n=246 · 4% la n=25 · 10% la n=10.
   Deci „top-1% tăiat" NU e comparabil între candidați cu n diferiți.
   OBLIGATORIU: se raportează `n_trimmed` ȘI `n_trimmed/n`. Comparația e permisă
   DOAR la fracție realizată egală. Altfel NON-COMPARABLE — regula CEO, aplicată aici.
2. Tăierea e UNILATERALĂ și e DELIBERAT deplasată în jos. NU e un estimator de tip
   trimmed-mean (acela ar fi simetric). E un STRESS ADVERSARIAL.
   `trimmed_top1_avg_R` NU se raportează NICIODATĂ ca estimare a expectanței.
```

**Cazul degenerat (n=3 ⇒ 33% tăiat) nu poate apărea: pragul N_MIN=25 de raportare, deja ratificat, îl exclude. Nu introduc un prag nou.**

---

# PARTEA 3 — D-4: tranzacțiile deschise la finalul datelor

## Decizia

```
PRIMAR (BASE)   marcate la ultima bară disponibilă, DECLARATE CENZURATE (`censored=True`)
STRESS          varianta „doar închise" (cenzurate EXCLUSE)
```

## De ce nu excluderea

> **Ce tranzacții sunt încă deschise la final? Cele de DURATĂ LUNGĂ. Iar durata nu e independentă de rezultat — o tranzacție care n-a atins nici stopul, nici ținta, e o tranzacție care n-a mers nicăieri sau care încă trendează. **Excluderea e CENZURARE INFORMATIVĂ**: criteriul de excludere e determinat de rezultatul însuși, nedeterminat. Deplasarea e de direcție NECUNOSCUTĂ.**

**Și magnitudinea e specifică fiecărui candidat, ceea ce face excluderea și mai proastă ca regulă uniformă:**

```
CAND-0037    time-stop la granița săptămânii  ⇒  cel mult ~1 deschisă la final. Neglijabil.
CAND-0011/0013/0014/0015/0017/0018  —  Finding H': singurul lor time-stop e granița de BLOC,
             care e INERTĂ live. Fără stop sau țintă, tranzacția NU se închide niciodată.
             Acolo fracția cenzurată poate fi MARE.
O regulă care e inofensivă la un candidat și materială la altul nu e o convenție — e o loterie.
```

## De ce nu „raportate separat cu rezultat necunoscut"

**Aceea e o regulă de RAPORTARE, nu de ESTIMARE. Lasă estimarea primară calculată pe submulțimea închisă — adică E excluderea, cu o notă de subsol.**

## De ce marcarea, și argumentul decisiv

```
· păstrează FIECARE tranzacție în populație ⇒ nicio cenzurare informativă;
· ★ marcarea la graniță e EXACT ce arată un cont live. Dacă Shadow s-ar opri azi, P&L-ul
  poziției deschise ESTE marcajul ei. Aceeași regulă de FIDELITATE pe care am impus-o la
  derivarea HTF live: convenția offline trebuie să producă ce produce live-ul.
```

**Costul, spus deschis: valoarea marcată NU e rezultatul tranzacției — regula de ieșire nu s-a declanșat. E deplasată spre zero față de o rezolvare prin stop/țintă. De asta varianta „doar închise" nu dispare, ci devine STRESS.**

## Completare: sunt PATRU granițe, nu una

> **Datele de descoperire au PATRU blocuri, cu benzi de embargo între ele. O tranzacție deschisă la granița unui bloc e în exact aceeași situație ca una deschisă la finalul setului — iar eu am ratificat deja că time-stop-ul pe graniță de bloc e INERT live (Finding H'). D-4 se aplică la FIECARE graniță de bloc, nu doar la ultima bară. `n_censored` se raportează PER GRANIȚĂ.**

**Sensibilitatea nu cere un gate nou: BASE folosește marcarea, STRESS include varianta doar-închise. Divergența materială între ele e un eșec de STRESS, deci „nu permite promovarea ca robust sau pregătit pentru live" — exact regula CEO, fără mașinărie adăugată.**

---

# PARTEA 4 — RAPORTAREA, ȘI O CONSECINȚĂ A REGULILOR DE PROMOVARE

## Separarea, impusă mecanic

```
BASE și STRESS sunt configurații DIFERITE ⇒ `schema_hash` DIFERIT.
O comparație între două rezultate cu hash-uri diferite e NON-COMPARABLE prin TIP, nu prin
disciplină. Se raportează AMÂNDOUĂ plus DIFERENȚA. Media lor nu se calculează NICIODATĂ —
n-ar fi nici estimare, nici stres, ci un al treilea obiect care nu corespunde niciunei rulări.
Cerința minimă pentru ca asta să fie verificabil: BASE și STRESS trebuie NUMITE și HASH-UITE.
Nu construiesc cadrul; cer doar să existe înainte de prima comparație.
```

## Consecința pe care o semnalez fiindcă e imediată și costisitoare

**Regula CEO: „eșecul în BASE elimină candidatul."**

> **Aplicată literal, elimină CAND-0037 — singurul candidat cu edge robust din proiect. Am pre-declarat la v2.7.62 că nu poate respinge H0: MDE 0,0839 la varianța minimă teoretică față de un efect observat de 0,062. Eșecul lui în BASE e GARANTAT prin construcție, la n=246.**

```
Distincția există deja și e ratificată — triajul în TREI rezultate:
   ARCHIVE-NEGATIVE      semn greșit, putere suficientă   ⇒ eliminare CORECTĂ
   ARCHIVE-INSUFFICIENT  semn corect, putere insuficientă ⇒ NU e eșec; e lipsă de date
   FORMAL PROTOCOL       eligibil de test
„Eșec în BASE" trebuie citit ca ARCHIVE-NEGATIVE, nu ca ne-respingere.
Nu propun un gate nou — cer ca regula CEO să fie citită prin triajul deja ratificat.
```

---

# PARTEA 5 — DESCHIS, CLASIFICAT

```
BLOCKING      niciunul.
MATERIAL      BASE/STRESS nedefinite în orice sursă pe care o pot citi. Necesar: nume + hash
              înainte de prima comparație.
MATERIAL      „eșec în BASE elimină" trebuie citit prin triajul în trei rezultate, altfel
              elimină CAND-0037 prin construcție (Partea 4).
MATERIAL      `best_trade_share` rămâne pe NET, deci instabil când netul → 0. Mitigat prin
              raportarea lui `sum(R)` și `wo1_still_positive` alături, nu prin schimbarea metricii.
LIMITATION    fracția realizată de tăiere variază cu n (1,2%…10%); trimmed comparabil DOAR
              la fracție egală.
LIMITATION    valoarea marcată a unei tranzacții cenzurate e deplasată spre zero. De asta
              varianta doar-închise rămâne obligatorie ca STRESS.
NON-MATERIAL  departajarea la egalitate de R (R DESC, entry_index ASC) — atinge foarte rar
              rezultatul, dar fără ea regula nu e deterministă.
```

**Nu cere: gate nou, framework nou, metrică nouă, prag nou. `_conc` are deja `wo1_still_positive`; N_MIN=25, contractul `Ok`/`Unavailable`, `schema_hash` și triajul în trei rezultate există toate.**

---

**Manifest:** `config/split_manifest.json` v2.7.64, secțiunea `r10_d3_d4_conventions_v2_7_64`.
