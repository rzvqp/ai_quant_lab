# STATISTICIAN — PROTOCOLUL CAND-0006 (PWH/PWL Route 3) + STAREA REALĂ A COZII

**Document ID:** STAT-CAND0006-PROTOCOL-AND-BACKLOG-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `CANDIDATE_QUEUE.md` (`703805f`), `reports/phase1_screening_results.json`, `code/phase1_screening.py`, `code/institutional_levels.py`. **Trei măsurători noi, proprii, P&L-oarbe** (scripturi temporare, necomise, șterse). **Două corecții de consemnat înainte de protocol.**

---

# PARTEA 0 — DOUĂ CORECȚII DE FAPT

## 0.1 Populația lui CAND-0006 nu e 275. E 258.

**Cifra 275 e a mea (v2.7.40) și circulă acum în coadă și în verdictul Red Team. E măsurată pe TOATE cele 572 de niveluri.** Dar politica tranzacționează **doar săptămâni COMPLETE**. Măsurat separat:

```
             emise   atinse   rată      % din niveluri   % din atingeri
COMPLETE       538      258   48,0%          94,1%           93,8%
PARTIAL         34       17   50,0%           5,9%            6,2%
TOTAL          572      275
```

**Populația testabilă a lui CAND-0006 e 258, nu 275.** Diferența e mică (−6,2%), dar cifra circulă ca dat de intrare și se corectează acum, nu după test.

## 0.2 Screening-ul de sesiune E TERMINAT. Ce lipsește e altceva.

**Mandatul spune că VE n-a terminat screening-ul. Fișierul de rezultate conține deja CAND-0001..0031 complet** — inclusiv cei șase de sesiune. **Ce lipsește din rezultate e exact ce e nou în script: CAND-0006 și CAND-0032..0036.** Deci criteriul meu de triaj e aplicabil ACUM la tot ce e screenat, iar K nu mai e o necunoscută (Partea 3).

---

# PARTEA 1 — PREDICȚIA MEA, ÎNCHISĂ: am măsurat punctul care lipsea

**La v2.7.42 am fixat metrica ÎNAINTE de rezultate: fracția aliniată din atinse, și am cerut explicit ca fracția ZILNICĂ să fie calculată în aceeași trecere.** VE a produs pâlnia de sesiune, dar **nu și pe cea zilnică** — deci comparația nu putea fi făcută. **Am măsurat-o eu, cu același detector ratificat și aceeași definiție de aliniere.**

```
scară        atinse   aliniate   fracție aliniată      rată de atingere
SESIUNE       5.396     1.811        33,6%                 47,7%   (High+Low)
ZILNIC        1.341       356        26,6%                 47,3%   (PDH+PDL)
SĂPTĂMÂNAL      275         6         2,2%                 48,1%
```

**Verificare de identitate: cele 356 aliniate zilnic reproduc exact n=356 din survey-ul PDH/PDL** — deci măsor aceeași populație, nu alta.

## Verdict pe predicție: CONFIRMATĂ — dar o corectez în forma ei

**Ordinea prezisă înainte de date se ține: sesiune (33,6%) > zilnic (26,6%) > săptămânal (2,2%), monoton în lungimea perioadei.** A treia confirmare independentă.

**Corectez însă ce am sugerat implicit — că degradarea e graduală. Nu e.** Sesiune→zilnic pierde 7 puncte; zilnic→săptămânal se prăbușește de **12×**. **Anti-corelația nu crește lin cu perioada: e blândă până la zi și catastrofală la săptămână.** Consemnez asta pentru că e o slăbire a propriei mele generalizări, nu o întărire.

## Invariantul, care e constatarea mai interesantă

**Rata de ATINGERE e practic identică pe toate cele trei scări: 47,7% / 47,3% / 48,1% — un interval de 0,8 puncte peste un raport de perioadă de ~35×.** Geometria e invariantă la scară — jumătate din niveluri sunt atinse, indiferent de perioadă. **Întreaga diferență trăiește în etapa de ALINIERE.** Nu e o observație decorativă: izolează mecanismul la filtrul de bias și exclude explicația „nivelurile lungi sunt prea departe ca să fie atinse".

---

# PARTEA 2 — PROTOCOLUL CAND-0006, cele cinci elemente

## Element 1 — TESTUL DE DIRECȚIE. Cerința se transferă de la CAND-0028; CONSTRUCȚIA nu.

**Red Team cere „aceeași cerință ca la CAND-0028". Cerința da. Dar oglinda nu se construiește la fel, și motivul e structural:**

```
CAND-0028 (Mid)          fade și invers au AMBELE țintă: cele două extreme ale sesiunii.
                         Oglindă curată — diferă doar semnul.
CAND-0006 (extremă)      la un WEEKLY_HIGH, brațul fade are țintă (WEEKLY_LOW).
                         Brațul invers NU are: nu există niciun nivel săptămânal DEASUPRA
                         maximului săptămânal.
```

**Dacă păstrez ținta, cele două brațe diferă și prin MECANISMUL DE IEȘIRE, nu doar prin direcție — iar o diferență de rezultat n-ar mai fi atribuibilă direcției.** Singura opțiune simetrică ce nu inventează niciun parametru:

```
TESTUL DE DIRECȚIE — pereche potrivită, ACELEAȘI bare de atingere, ACEEAȘI intrare
  d = |intrare − extrema barei de atingere pe latura de fade|   ← distanța de stop DECLARATĂ
                                                                   a lui CAND-0006, podită S2
  braț F (fade)    direcția declarată;   stop = intrare ∓ d
  braț I (invers)  direcția opusă;       stop = intrare ± d     ← ACELAȘI d, oglindit
  ieșire, AMBELE   DOAR time-stop la granița săptămânii
  H0 : mean(net_R | F) <= mean(net_R | I),  împerecheat pe același eveniment,
       bootstrap pe bloc (L>=28) aplicat DIFERENȚEI
```

**Brațul F al testului de direcție NU e politica CAND-0006** (aceea are ținta). Sunt două întrebări distincte: *contează direcția?* (perechea potrivită) și *face bani politica declarată?* (testul ei propriu). Ambele stau în **același slot de familie** — teste de componentă, ca la CAND-0028.

**Nedegenerare, verificată:** cu d comun și time-stop comun, brațele NU sunt imagini în oglindă, pentru că **stopul rupe simetria** — dacă F e stopat la −1R, I continuă până la granița săptămânii. Exact acolo se manifestă un avantaj de direcție, dacă există.

### Amplificatorul lui Red Team, cuantificat — și consecința pe care o schimbă

**„Un maxim se atinge urcând, iar tu îl vinzi." Măsurat: la scară săptămânală doar 2,2% dintre atingeri au bias-ul propriu al pieței de partea fade-ului. CAND-0006 e contra-bias în 97,8% din cazuri, prin construcție** (zilnic 73,5%, sesiune 66,4%).

**Asta face cele două brațe ASIMETRIC de informative, și trebuie pre-declarat, altfel rezultatul se citește greșit:**

```
F câștigă    → avantaj de fade REAL, și e un rezultat TARE: bate un braț care e
               aliniat la trend în 97,8% din bare.
I câștigă    → NU e dovadă că „nivelul funcționează invers". Brațul I e confundat cu
               simplu trend-following. Trebuie să bată în plus nulul potrivit pe bias,
               pe bare FĂRĂ nivel. Dacă nu-l bate, e trend, nu structură.
```

### Interpretarea celor patru rezultate, pre-angajată ACUM

```
1. F > I, semnificativ                    → fade-ul se transferă la săptămână.
2. I > F ȘI I bate nulul potrivit pe bias → CAND-0006 RESPINS ca încadrat.
                                            NU promovează teza de continuare.
                                            Aceea e o ipoteză NOUĂ, aleasă DUPĂ rezultat
                                            ⇒ slot de familie propriu ȘI date neatinse
                                            (holdout sigilat sau date noi).
3. I > F dar NU bate nulul pe bias        → e trend-following. CAND-0006 respins,
                                            nimic nou.
4. niciunul semnificativ                  → nivelul e inert la săptămână. Arhivat.
```

**Punctul 2 e gardul care contează.** Fără el, orice rezultat s-ar putea explica: fade câștigă → „gramatica se confirmă"; invers câștigă → „amplificatorul explică, deci continuarea era teza". **Ambele ieșiri explicate = test nefalsificabil.** Se închide acum, nu după.

**Regula de decizie, conjunctivă:** politica trece **doar dacă** bate zero **ȘI** F bate I. Un fade care bate inversul dar pierde bani nu e tranzacționabil; o politică profitabilă a cărei direcție nu bate propriul invers n-a arătat că nivelul contează.

## Element 2 — COMPLETE-only: declarată ȘI mărginită prin măsurare

**Red Team are dreptate ca direcție și greșește ca magnitudine. Măsurat (Partea 0.1): PARTIAL 50,0% vs COMPLETE 48,0%.** Săptămânile scurte chiar sunt atinse mai des — cu **2,0 puncte**. Sunt 5,9% din niveluri și 6,2% din atingeri.

> **Condiționarea e reală, e în direcția prezisă, și e neglijabilă ca mărime.** Se declară cu orice rezultat — dar se declară cu cifra, nu ca avertisment deschis. **Un rezultat pe CAND-0006 se citește ca valabil pentru săptămâni complete, care sunt 94% din populație.**

## Element 3 — FAMILIA FDR: RESPING sub-familia {0001, 0027, 0006}

**Decizia e a mea, și e NU.**

**Motivul e derivat, nu de gust: o sub-familie de trei ar aplica α peste 3 în loc de α peste 7+K, adică ar SLĂBI corecția exact pentru cei trei candidați cei mai favorizați.** E aceeași formă cu familiile pe lot, pe care am refuzat-o deja când am fixat familia cumulativă: gruparea după gramatică e capcana de selecție purtând altă etichetă.

**Dar observația Red Team nu e inutilă — are alt loc corect, două de fapt:**

```
DEPENDENȚĂ  aceeași gramatică pe perioade diferite ⇒ dependență POZITIVĂ ⇒ PRDS ⇒ BH rămâne valid.
ANALIZĂ     {0001, 0027, 0006} = exact gradientul din Partea 1, raportate una lângă alta.
```

**Grupare de ANALIZĂ, nu partiție de α.** Aceeași separare ca între registrul de familie și cel de explorare: două numere, scopuri diferite, niciodată amestecate.

## Element 4 — PRAGUL S2

**`min_executable_risk` se aplică verbatim, cu fracția podită raportată.** Trei observații care nu se moștenesc de la alți candidați:

```
SEMNIFICAȚIE  spre deosebire de CAND-0003, podeaua NU distruge sensul structural al stopului:
              stopul e „dincolo de nivel"; lărgit, rămâne dincolo de nivel.
R:R           spre deosebire de CAND-0003, ținta e la o amplitudine SĂPTĂMÂNALĂ distanță
              ⇒ R:R rămâne mare chiar podit. S2 mușcă în frecvență, nu în calitate.
TESTUL DE     d e COMUN celor două brațe ⇒ podeaua se aplică identic ⇒ NU poate înclina
DIRECȚIE      comparația de direcție. Proprietate a construcției, nu presupunere.
```

## Element 5 — NU e submulțime. Dar NU e nici independentă — măsurat.

**Confirm: perioadă disjunctă, fără W-incr.** Dar „nu e submulțime" nu înseamnă „nu se suprapune", iar un maxim săptămânal coincide adesea în preț cu un maxim al zilei anterioare. **Măsurat pe barele de atingere:**

```
atingeri săptămânale (COMPLETE)          258
  și atingere PDH/PDL pe ACEEAȘI bară    105   (40,7%)
    direcția de fade COINCIDE            105   (100% dintre suprapuneri)
    direcția de fade SE OPUNE              0   (0,0%)
```

**40,7% suprapunere, cu direcție identică în 100% din cazuri ⇒ dependență POZITIVĂ ⇒ PRDS ⇒ BH rămâne valid, fără partiție.** Fracția se raportează per regim înainte de test, ca la CAND-0009.

> **Și clarifică retroactiv problema CAND-0009: acolo nu submulțimea era problema, ci SEMNUL.** Poziții opuse pe bare comune = dependență negativă, pe care BH n-o acoperă. Aici semnul coincide, deci construcția disjunctă nu e necesară. **Aceeași geometrie de suprapunere, verdict opus — pentru că criteriul n-a fost niciodată suprapunerea.**

## Elementele comune

Cele 3 regimuri; N_MIN=25 cu suprimare-nu-etichetare; bootstrap pe bloc (L≥28) pe `net_R`; **BH-FDR α=0,05 peste familia din Partea 3**; holdout sigilat; walk-forward 2 pliuri pe granițele de regim. **Protocolul se activează doar dacă CAND-0006 iese categoria C la triaj — screening-ul lui încă nu există.**

---

# PARTEA 3 — CE AM LIVRAT, CE LIPSEȘTE, ȘI CÂT E FAMILIA

**Am aplicat criteriul de triaj de la v2.7.42 la TOT ce e screenat. Rezultatul e mai decisiv decât mă așteptam.**

```
A ARHIVAT-NEGATIV (11)  0003 0010 0011 0013 0014 0015 0020 0021 0022 0024 0025
B ARHIVAT-INSUFICIENT(3) 0016 (n_regim 19)  0018 (n=12)  0023 (n=7)
C PROTOCOL FORMAL (14)  0001 0002 0007 0008 0009 0012 0017 0019 0026 0027 0028 0029 0030 0031
NESCREENAT (6)          0006  0032 0033 0034 0035 0036
```

## Constatarea incomodă: criteriul meu arhivează doi membri ai familiei actuale

**CAND-0003 (n=6.326, 0/8 ani, 0/3 regimuri, −0,405 R) și CAND-0010 (n=5.874, 0/8, 0/3, −0,408 R) satisfac ARHIVAT-NEGATIV.** Iar **CAND-0003 e unul dintre cei patru piloți DEMO autorizați**, cu criterii DEMO definite de mine la v2.7.36.

**Nu ascund asta și nu o rezolv singur. Ce spun clar:**

```
FAMILIA E MONOTONĂ. Un candidat intrat în familie NU iese, oricât de rău arată datele.
Scoaterea lui ar SLĂBI pragul pentru ceilalți — adică exact capcana refuzată la Elementul 3.
⇒ familia rămâne >= 7. Arhivarea POST-includere nu returnează slotul.
```

**Decizia DEMO e a CEO, nu a mea. Faptul statistic e că a cheltui un cont DEMO pe o politică fără niciun an pozitiv și niciun regim pozitiv pe n=6.326 e greu de justificat.** Îl consemnez și îl rutez.

## Familia, numărată

```
FAMILIE = 7 (blocată, monotonă) + C-uri noi neincluse încă:
          0012 0017 0019 0026 0027 0028 0029 0030 0031   → +9
        = 16 acum,  până la 22 dacă 0006 + toți cei cinci B trec triajul
EXPLORARE = 36 candidați priviți. Raportat lângă orice rezultat, niciodată în α.
```

### Corecție la premisa „familia 19 ⇒ pragul α/19"

**α/m e pragul DOAR pentru cel mai mic p. La BH, pragul celui de-al k-lea p ordonat e k·α/m.** La m=16, α=0,05:

```
p(1) <= 0,0031    p(5) <= 0,0156    p(8) <= 0,0250    p(16) <= 0,05
```

**Creșterea familiei costă mult mai puțin decât sugerează intuiția Bonferroni — iar dacă mai multe efecte sunt reale, ele se protejează reciproc.** O parte din anxietatea „arhivăm ca să salvăm puterea" se dizolvă aici: **arhivarea corectă rămâne justificată pentru că negativii nu merită testați, nu pentru că familia ar fi periculoasă.**

## Restanța mea, declarată

```
LIVRAT     triaj MK (0020-0025) · protocoale sesiune (0026-0031) · CAND-0006 (acest document)
           · triaj aplicat la 0011-0019 (acest document)
LIPSEȘTE   protocoale formale pentru C-urile noi: 0012, 0017, 0019   ← restanță reală, a mea
           protocoale pentru 0032-0036 (Primitiva B)  ← blocate pe screening, nu pe mine
           CAND-0004 / 0005 — detectoarele Void și BPR specificate (v2.7.40), nu construite
```

**Cele trei — 0012, 0017, 0019 — au ajuns la Red Team și au trecut screening-ul, iar eu nu le-am dat protocol. E restanța mea, nu a nimănui altcuiva.** 0017 (DZ-FVG, 18.275 tranzacții, −0,013 R) intră la C prin criteriu, deși e eșecul pe care l-am citat de trei ori ca avertisment de volum: **criteriul e deliberat conservator și trimite semnul mixt la test în loc să-l arhiveze pe judecată. Îl aplic așa cum l-am fixat, inclusiv când nu-mi place rezultatul.**

---

## HANDOFF

**VE, în ordinea asta — nimic nu se rulează înainte de (1):**

1. **termină cele trei sarcini în curs**, inclusiv screening-ul pentru CAND-0006 și 0032-0036;
2. **aplică triajul** celor șase nescreenați; doar categoria C primește protocol și slot;
3. **reverifică independent cele trei măsurători din acest document** (258/275 COMPLETE, gradientul 33,6/26,6/2,2%, suprapunerea 40,7% cu direcție identică) — sunt reproductibile prin construcție, dar regula e verificarea independentă;
4. **execută protocolul CAND-0006** dacă iese C, cu testul de direcție împerecheat și interpretarea celor patru rezultate pre-angajată.

**Alpha:** populația CAND-0006 e **258**, nu 275 — se corectează în coadă și în politică.
**Red Team:** ținta explicită e Elementul 1 — construcția perechii potrivite (de ce ținta se scoate din ambele brațe) și gardul de la punctul 2 al interpretării.
**CEO:** o singură decizie rutată, nu luată de mine — **CAND-0003 satisface arhivat-negativ și e pilot DEMO.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.43 (commit `e3e9745`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
