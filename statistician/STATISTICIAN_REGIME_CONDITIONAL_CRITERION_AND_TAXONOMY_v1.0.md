# STATISTICIAN — BENCHMARK CONDIȚIONAT DE REGIM, CRITERIUL DE STABILITATE, ȘI CONFLICTUL DE TAXONOMIE

**Document ID:** STAT-REGIME-CONDITIONAL-CRITERION-AND-TAXONOMY-v1.0 · **Data:** 2026-08-13 · **Autor:** Statistician
**Verificare de sursă:** citit `regime_classifier.py` — vocabularele `VolBand`, `StructBand`, `Direction`, verbatim.

**Din mandatul anterior:** T4 non-gap și geometria strictă A2 sunt DEJA formalizate și publicate (doc `cb23777`, manifest v2.7.67 `70a99d2` + v2.7.68 `b66b935`). Descompunerea așteaptă cifrele VE, cum s-a stabilit. Nu le reiau.

---

# PARTEA 1 — BENCHMARK-UL. Portița se închide prin PRE-ÎNREGISTRARE, nu prin etichetă.

**Regula CEO — „condiția de regim FACE PARTE din strategie și nu poate fi adăugată după observarea rezultatului" — e corectă și o formalizez. Dar eticheta „diagnostic" NU e suficientă singură:**

```
UNCONDITIONAL și REGIME-CONDITIONAL se calculează pe ACELEAȘI date.
A raporta ambele și a promova pe unul e legitim DOAR dacă alegerea a fost făcută ÎNAINTE.
Dacă alegerea depinde de care arată mai bine, eticheta „diagnostic" nu schimbă nimic —
selecția s-a produs deja.
```

```
CERINȚĂ, executabilă:
   `promotable_variant ∈ {UNCONDITIONAL, REGIME_CONDITIONAL}` se declară ÎNAINTE de rulare
   și intră în `run_hash`, împreună cu:
       · definiția regimului țintă
       · regula de precedență a etichetei (Partea 3)
       · N1 `schema_hash`
   Un rezultat fără aceste câmpuri nu e promovabil — prin TIP, nu prin disciplină.
```

## Consecința de familie, care nu e în mandat

> **O condiție de regim adăugată DUPĂ observarea rezultatelor nu e o rafinare a ipotezei — e o IPOTEZĂ NOUĂ, cu estimand diferit pe populație diferită. Consumă un SLOT DE FAMILIE. Familia e MONOTONĂ: m trece de la 19 la 20, iar pragul BH de rang 1 scade de la 0,00263 la 0,00250 pentru TOATE celelalte, retroactiv.**

**Iar dacă AMBELE variante sunt testate formal, sunt DOUĂ ipoteze, deci DOUĂ sloturi. De asta „UNCONDITIONAL = numai diagnostic" e și economic corectă: un diagnostic nu produce p-value, deci nu consumă slot. Regula CEO cumpără un slot; merită spus.**

---

# PARTEA 2 — CRITERIUL DE STABILITATE. Episoade, nu ani.

## 2.1 Câte episoade — DERIVAT, nu ales

**Criteriul „stabil peste episoade" trebuie să fie FALSIFICABIL: trebuie să existe un rezultat care îl încalcă. Sub H0 (fără edge, semn simetric), fiecare episod e pozitiv cu probabilitate 0,5. Deci un palmares PERFECT are probabilitatea `0,5^k`:**

```
k = 3   0,125    k = 4   0,0625    k = 5   0,03125    k = 6   0,0156
```

> **La k = 4, chiar și 4 din 4 episoade pozitive apar din pur hazard mai des de 5% din timp — deci criteriul nu poate distinge nimic. La k = 5 devine prima dată distinctibil. `k_min = 5` e un PLAFON DE FALSIFICABILITATE, derivat, nu ales — același instrument cu care am derivat pragul lui N3 („pragul trebuie să lase «nicio zonă nu se califică» să se întâmple efectiv").**

**Sub 5 episoade: `ARCHIVE_INSUFFICIENT`, nu eșec. Aceeași distincție ratificată la v2.7.65 — un candidat nu se elimină fiindcă n-a putut fi testat.**

**Precizare, ca să nu fie citit mai tare decât e: calculul binomial derivă PRAGUL DE VACUITATE. NU e un test și NU produce un p-value — altfel ar intra în familie și ar adăuga multiplicitate.**

## 2.2 Cum se măsoară stabilitatea — fiecare dependență are deja un instrument

**CEO cere independență față de CINCI lucruri. Niciunul nu cere unealtă nouă:**

```
un singur AN            performanța per an ÎN REGIM, raportată — dar NU mai e criteriu de trecere
un singur EPISOD        (a) LEAVE-ONE-EPISODE-OUT: rezultatul rămâne pozitiv scoțând ORICARE episod
                        (b) `best_episode_share` și `trimmed_top1_episode` — R10 ridicat cu un nivel,
                            de la tranzacție la episod. Aceeași metrică, altă unitate.
o singură TRANZACȚIE    R10, deja ratificat: `best_trade_share`, `trimmed_top1_avg_R`, `n_trimmed`
o singură CONFIGURAȚIE  BASE și STRESS, amândouă, deja obligatorii
etichete RETROSPECTIVE  eticheta de regim se calculează CAUZAL din N1 (as_of ≤ decision_ts)
                        + pre-înregistrarea din Partea 1
```

**LEAVE-ONE-EPISODE-OUT e criteriul portant, fiindcă e exact traducerea cerinței: „să nu depindă de un singur episod" înseamnă „scoate oricare, rezultatul supraviețuiește".**

## 2.3 Două capcane pe care le impun odată cu criteriul

```
1. EPISOADELE NU SUNT EGALE. Unul poate conține 3 tranzacții, altul 300. Media mediilor
   per episod dă pondere EGALĂ unor dovezi INEGALE.
   ⇒ estimandul rămâne media PONDERATĂ PE TRANZACȚII. Distribuția per episod e DIAGNOSTIC.
   Media mediilor per episod NU se calculează NICIODATĂ ca estimare.
2. EPISOADELE NU SUNT INDEPENDENTE. Blocarea ratificată e pe ZI calendaristică, derivată
   dintr-un orizont de dependență MĂSURAT de ~5 ore. Condiționarea pe regim nu schimbă acea
   măsurătoare — dar ridică o întrebare nouă: sunt tranzacțiile din ACELAȘI episod mai
   asemănătoare între ele decât cele din episoade diferite?
   ⇒ SE MĂSOARĂ (varianță intra-episod vs inter-episod) ÎNAINTE de a presupune că blocarea
   pe zi mai e suficientă. MATERIAL, măsurabil, nu blocant.
```

---

# PARTEA 3 — TAXONOMIA. Patru din șase; una e o COLIZIUNE DE NUME, nu o lipsă.

**Vocabularele N1, verbatim din cod:**

```python
VolBand     COMPRESSED · LOW · NORMAL · HIGH_CHOPPY · HIGH_DIRECTIONAL
StructBand  NONE ("fără structură, 0,1% din bare") · RANGE ("|run| == 1 — direcție PROASPĂT
            RĂSTURNATĂ, INSTABILĂ") · WEAK ("|run| in {2,3}") · STRONG ("|run| >= 4")
Direction   DOWN · WEAK_DOWN · NEUTRAL ("RANGE / fără structură / sub n_min, fail-closed") ·
            WEAK_UP · UP
```

## 3.1 Verdict per stare

```
TREND_UP             DERIVABIL   Direction ∈ {UP, WEAK_UP} ∧ StructBand ∈ {WEAK, STRONG}
TREND_DOWN           DERIVABIL   simetric
COMPRESSION          DERIVABIL   VolBand == COMPRESSED. O axă, direct.
UNCERTAIN            DERIVABIL   dar NU are voie să înghită `Unavailable` — sunt stări diferite
                                 (măsurat-și-neconcludent vs n-am-putut-măsura), distincția
                                 ratificată la v2.7.59. UNCERTAIN e un `Ok`.
RANGE                ✗ NEDERIVABIL — și e o COLIZIUNE DE NUME (§3.2)
BREAKOUT_TRANSITION  ~ CONSTRUIBIL, NU DERIVABIL (§3.3)
```

## 3.2 RANGE — cea mai periculoasă dintre cele două, fiindcă PARE derivabilă

> **`StructBand.RANGE` NU înseamnă „lateral". Docstring-ul e explicit: „|run| == 1 — direcție PROAPSĂT RĂSTURNATĂ, INSTABILĂ". Adică o TRANZIȚIE, aproape opusul consolidării. A ruta strategii de „range" pe această etichetă le-ar trimite exact în barele de răsturnare proaspătă.**

**Se poate construi din alte axe? `VolBand ∈ {LOW, COMPRESSED} ∧ Direction == NEUTRAL`? NU, și motivul e precis:**

```
`Direction.NEUTRAL` CONFLATEAZĂ TREI situații: range real · fără structură · sub n_min (fail-closed).
A construi RANGE peste NEUTRAL ar ruta și barele de WARMUP în regimul de range.
Ca să fie derivabil, N1 ar trebui întâi să SEPARE neutrul-măsurat de neutrul-fail-closed.
Aia e o REDEFINIRE a lui N1 — exact ce mi s-a cerut să nu fac.
```

**Deci: RANGE cere ori o primitivă nouă (un detector genuin de consolidare), ori separarea lui `Direction.NEUTRAL`. Nu îl inventez. Spun ce ar costa: minim, o axă suplimentară sau un al patrulea membru de enum care distinge fail-closed de neutru măsurat — și re-ratificarea lui N1.**

## 3.3 BREAKOUT_TRANSITION — nu e o STARE, e o TRANZIȚIE

```
Construibil din DOUĂ ieșiri N1 consecutive:  VolBand[i-1] == COMPRESSED  ∧  VolBand[i] ∈ {…}
FĂRĂ a redefini N1 — dar cu trei costuri care fac din el o DECIZIE DE MODEL, nu o derivare:
  1. routerul trebuie să PĂSTREZE STARE (ieșirea N1 precedentă). Plumbărie nouă, mică.
  2. e observabil abia DUPĂ închiderea barei ⇒ rutarea are un LAG de o bară H4 = 4 ore.
  3. HIGH_DIRECTIONAL sau HIGH_CHOPPY? Un breakout în CHOPPY nu e un breakout util.
     Alegerea e o DECIZIE, nu o consecință.
```

**Verdict: construibil fără redefinirea lui N1, dar definiția (ce bandă țintă, ce lag) e o alegere de model NOUĂ, care se PRE-ÎNREGISTREAZĂ în `schema_hash`, nu se deduce.**

## 3.4 Conflictul REAL nu e la stări. E la FORMĂ.

> **O etichetă unică e o PARTIȚIE — exclusivă și exhaustivă. Patru axe sunt un SPAȚIU PRODUS: 5 × 4 × 5 = 100 de celule, plus știri. A colapsa 100 în 6 cere o REGULĂ DE PRECEDENȚĂ, iar regula de precedență e exact locul unde se face modelarea.**

**Exemplu concret, nu ipotetic: `COMPRESSED ∧ UP ∧ STRONG`. E COMPRESSION sau TREND_UP? N1 afirmă AMBELE fapte. Routerul are nevoie de UN răspuns. Nimic din N1 nu îl dă.**

```
CERINȚĂ: regula de precedență se DECLARĂ explicit, se PRE-ÎNREGISTREAZĂ în `run_hash`
(Partea 1) și se raportează matricea de ocupanță — câte bare cad în fiecare din cele 6
etichete, și câte celule ale spațiului produs colapsează în fiecare.
Fără matricea de ocupanță nu se poate ști dacă o etichetă e rară sau dacă precedența
a înghițit-o.
```

> **Și motivul pentru care asta leagă de Partea 1: dacă precedența s-ar alege DUPĂ ce se vede care rutare a mers, ar fi exact portița pe care regula CEO o închide — doar mutată cu un nivel mai jos, de la condiția de regim la definiția regimului.**

---

# PARTEA 4 — DESCHIS, CLASIFICAT

```
BLOCKING      RANGE nu e derivabil fără redefinirea lui N1 (`Direction.NEUTRAL` conflatează
              range real / fără structură / fail-closed). Nu îl inventez. Decizia e a CEO:
              primitivă nouă, separarea lui NEUTRAL, sau RANGE iese din taxonomie.
MATERIAL      regula de precedență 4-axe → 1 etichetă e o DECIZIE DE MODEL; se pre-înregistrează
              în `run_hash` ÎNAINTE de orice rezultat, altfel e aceeași portiță, un nivel mai jos.
MATERIAL      BREAKOUT_TRANSITION: construibil, dar definiția (bandă țintă, lag de 1 bară H4)
              se declară, nu se deduce.
MATERIAL      dependența la scară de EPISOD nu e măsurată; blocarea pe ZI e derivată dintr-un
              orizont de 5 ore. Se măsoară varianța intra- vs inter-episod înainte de a o presupune.
MATERIAL      o condiție de regim adăugată post-hoc e o IPOTEZĂ NOUĂ: m 19 → 20, prag de rang 1
              de la 0,00263 la 0,00250, retroactiv pentru toți.
LIMITATION    `k_min = 5` e un plafon de FALSIFICABILITATE, nu un prag de putere. Sub el,
              `ARCHIVE_INSUFFICIENT`, nu eșec.
LIMITATION    episoadele sunt inegale; media mediilor per episod NU e niciodată estimarea.
NON-MATERIAL  UNCERTAIN nu înghite `Unavailable` — distincție deja ratificată, se reafirmă.
```

**Nu cere: gate nou, framework nou, metrică nouă. LEAVE-ONE-EPISODE-OUT e R10 ridicat cu un nivel; `run_hash`, triajul în trei rezultate și contractul `Ok`/`Unavailable` există toate.**

---

**Manifest:** `config/split_manifest.json` v2.7.69, secțiunea `regime_conditional_criterion_and_taxonomy_v2_7_69`.
