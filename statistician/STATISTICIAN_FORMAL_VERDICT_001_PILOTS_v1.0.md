# STATISTICIAN — VERDICT FORMAL 001: CEI PATRU PILOȚI

**Document ID:** STAT-FORMAL-VERDICT-001-PILOTS-v1.0
**Data:** 2026-08-10 · **Autor:** Statistician
**Primul verdict formal din proiect.** Precondiții închise: RV-L1, RV-L2 (v2.7.55), RT-CODE-A-0013 (`651c491`).

---

# PARTEA 0 — CUM S-A RULAT

```
ORACOL        `calendar_block_bootstrap` din `code/restante_validation.py` — construit de VE,
              verificat NUMERIC de Red Team. NU mi-am scris propriul instrument.
              Separarea care contează: nu construiesc aparatul pe care apoi îl citesc.
BLOC          ZI calendaristică (v2.7.45). L=28 pe indexul tranzacției rămâne retras.
NUL           centrat la zero; coadă DREAPTĂ; p = (k+1)/(B+1).
B             20.000 replicări — rezoluție 5×10⁻⁵, necesară fiindcă pragul BH coboară la 0,0031.
SEED          pe CHEIE STABILĂ: sha256(candidate_id)[:8]. Reziduul de seed se închide AICI,
              nu prin promisiune — rularea asta nu depinde de ordinea vreunei liste.
CALIBRARE     precondiția per candidat trecută deja: 0,011 / 0,022 / 0,025 / 0,043, toate sub 0,07.
```

**Verificare de integritate, făcută înainte de a raporta:** media observată de bootstrap coincide EXACT cu `expectancy_R` din fișierul de screening la toți patru (+0,1414 / −0,1009 / −0,6145 / +0,1643). **Oracolul citește aceeași populație pe care o descrie screening-ul.**

---

# PARTEA 1 — VERDICTUL

```
cand       politică                    n    zile    E_R obs      p       ani+   reg+
CAND-0001  PDH-PDL                  1225    1093    +0,1414   0,18519    4/8    2/3
CAND-0002  COMPRESSION-EXPANSION    1061     738    −0,1009   0,88501    3/8    0/3
CAND-0003  FVG-CE50-REACTION        6326    1400    −0,6145   1,00000    0/8    0/3
CAND-0007  LEVEL-FVG-CONFLUENCE      373     352    +0,1643   0,19459    3/7    3/3
```

**Per regim, raportat înaintea agregatului (net_R):**

```
CAND-0001   bear +163,3   bull  +72,7   corecție  −62,8
CAND-0002   bear  −58,1   bull   −5,6   corecție  −43,4
CAND-0003   bear −1535,4  bull −1583,2  corecție −768,9
CAND-0007   bear   +1,1   bull  +45,5   corecție  +14,6
```

## Corecția BH, familia m=16

```
k=1  CAND-0001  p=0,18519   prag 0,003125   >
k=2  CAND-0007  p=0,19459   prag 0,006250   >
k=3  CAND-0002  p=0,88501   prag 0,009375   >
k=4  CAND-0003  p=1,00000   prag 0,012500   >
cel mai mare k cu p₍ₖ₎ ≤ k·α/m  =  0
```

> # **VERDICT: NICIUN CANDIDAT NU RESPINGE H0. ZERO PROMOVĂRI.**
>
> **CAND-0001, CAND-0002, CAND-0003, CAND-0007 — H0 („media net_R ≤ 0") NU se respinge pentru niciunul.**

---

# PARTEA 2 — CORECȚIA DE MULTIPLICITATE NU A FOST CONSTRÂNGEREA

**Cel mai mic p e 0,185.**

```
față de pragul BH la m=16 (0,0031):  de 59× mai mare
față de un test SINGULAR necorectat (0,05):  de 3,7× mai mare
```

> **Niciunul dintre candidați nu ar fi trecut nici măcar un test unic, necorectat.** Familia de 16 nu a costat nimic aici — **rezultatul ar fi fost identic la m=1.** O spun explicit ca să nu se citească verdictul ca fiind produs de severitatea corecției: **corecția n-a mușcat, pentru că nimic nu s-a apropiat de prag.**

---

# PARTEA 3 — CONDIȚIA PE CAND-0003 E SATISFĂCUTĂ

**Clearance-ul condiționat de la RV-L1 spunea: verdict admisibil DOAR ca NE-RESPINGERE, fiindcă VIF=4,76 subestimează eroarea standard de 2,18×.**

```
p(CAND-0003) = 1,00000.  E o ne-respingere, la limita superioară a scalei.
⇒ condiția e ÎNDEPLINITĂ, verdictul lui e ADMISIBIL, iar autocorelația cross-zi nu îl atinge.
```

**Argumentul de direcție s-a ținut: o eroare standard subestimată face respingerea prea ușoară, iar CAND-0003 nu s-a apropiat de respingere. Corectat cu SE real, ne-respingerea devine și mai fermă.**

---

# PARTEA 4 — CE ÎNSEAMNĂ, ȘI CE NU ÎNSEAMNĂ

## Puterea: ce ar fi putut testul să vadă

**Aproximând distribuția bootstrap ca normală, doar pentru interpretare:**

```
CAND-0001   SE ≈ 0,158   efect minim detectabil la pragul BH ≈ 0,43 R/tranzacție   observat 0,141
CAND-0007   SE ≈ 0,191   efect minim detectabil                ≈ 0,48 R/tranzacție   observat 0,164
```

> **Testul putea vedea doar un edge de ~0,43-0,48 R pe tranzacție. Cei doi candidați pozitivi au ~0,14-0,16 R — de trei ori sub pragul de detecție.** Nu sunt „aproape semnificativi": sunt la sub o abatere standard de zero.

## Cele două citiri, separate

```
CE SPUNE VERDICTUL      Datele nu disting expectanța acestor patru politici de zero, la α=0,05
                        cu corecție BH peste familia de 16.
CE NU SPUNE             NU spune că edge-ul e zero. O ne-respingere nu e o dovadă de absență.
                        Pentru CAND-0001 și CAND-0007, un edge real de 0,14-0,16 R ar fi
                        INVIZIBIL pentru acest test la acest n. Verdictul e compatibil ȘI cu
                        „nu există edge", ȘI cu „există un edge mic pe care n-avem putere să-l vedem".
```

**Pentru CAND-0002 și CAND-0003 însă, citirea e mai tare: expectanța observată e NEGATIVĂ (−0,10 și −0,61), și negativă în toate cele trei regimuri la CAND-0003. Acolo ne-respingerea nu e o chestiune de putere — semnul e greșit.**

## Ce se întâmplă cu criteriul conjunctiv

**Criteriul meu cerea TOATE: (a) calibrare, (b) BH-semnificativ, (c) W-incr la confluențe, (d) semn în ≥2/3 regimuri.**

```
(a) trece la toți patru.
(b) EȘUEAZĂ la toți patru  ⇒  promovarea cade aici, pentru toți.
(c) W-incr pentru CAND-0007 (contra celui mai bun dintre CAND-0001 / CAND-0003) NU a fost rulat.
    Nu s-a ajuns la el — dar consemnez că, dacă (b) ar fi trecut, (c) ar fi fost obligatoriu
    și NEEXECUTAT, deci promovarea ar fi fost oricum blocată.
(d) CAND-0007 ar fi trecut (3/3 regimuri pozitive); CAND-0001 nu (2/3); ceilalți doi nu.
```

**Nicio promovare parțială. Verdictul e uniform: NU.**

---

# PARTEA 5 — DELIMITAREA DE SCOP, care e obligatorie

```
CE ACOPERĂ VERDICTUL   politicile CAND-0001/0002/0003/0007 în parametrizarea lor actuală,
                       pe datele de DESCOPERIRE, cu costurile MODELATE (0,20 round-trip),
                       cu stopurile și ieșirile structurale declarate, pe cele 3 regimuri.
CE NU ACOPERĂ          holdout-ul, SIGILAT și neatins. Alte parametrizări. Alte instrumente.
                       Costul realizat, încă nemăsurat (colectarea de spread rulează).
                       Mecanismele de piață din spate — verdictul respinge o PARAMETRIZARE
                       TESTATĂ, nu un concept.
```

**Și limita pe care am enunțat-o înainte de rulare, care rămâne valabilă: măsurătorile RV-L1/RV-L2 și calibrarea validează MAȘINĂRIA. Verdictul de aici e prima afirmație despre EDGE — iar afirmația e că nu s-a găsit unul.**

## Consecință pentru DEMO

**Cei patru piloți sunt pe linia DEMO. Verdictul NU îi oprește — DEMO nu a fost niciodată justificat de un p-value; a fost declarat explicit NEVALIDAT de la prima zi (v2.7.34).** Ce se schimbă e că acum există o măsurătoare formală care spune că edge-ul nu e demonstrabil pe date istorice. **Ce face linia DEMO mai departe e decizie CEO; faptul statistic e al meu și e mai sus.**

---

# PARTEA 6 — CELE DOUĂ REZIDUURI, ÎNCHISE

```
SEED     ÎNCHIS PRIN EXECUȚIE. Rularea de mai sus folosește sha256(candidate_id)[:8], nu indexul
         de enumerare. Rezultatul e invariant la reordonarea listei — verificabil prin
         re-rulare după orice arhivare. VE preia aceeași convenție în cod.
RV-L3    ÎNCHIS CA REGULĂ OBLIGATORIE, formulată executabil:
         un candidat verdict-eligibil a cărui verificare de dependență NU se rezolvă la
         rezoluția standard NU intră în pasul BH. Are exact două căi, alese ÎNAINTE de test:
           (1) verificare la o rezoluție mai fină, cu SE(r) raportat, sau
           (2) declarare pe BY pentru el, cu costul Σ(1/i) — 3,38× la m=16.
         Tăcerea nu e o a treia cale. Un candidat fără una dintre cele două NU primește p-value.
```

---

# PARTEA 7 — NIVELUL 4: CONDIȚIILE RT-CODE-A-0014

## Z4-L1 — `UNDETERMINED` nu se citește NICIODATĂ prin valoarea ordinală

**Constatarea e corectă și e gravă: codificat ca 0 la mijlocul aritmetic al scalei −2..+2, `UNDETERMINED` arată ca „neutru, continuă" pentru orice consumator care citește VALOAREA. Iar cazul majoritar e tocmai el, purtând `status=AVAILABLE`.**

```
REGULA, obligatorie:
  nivelul 6 ramifică pe MEMBRUL ENUM sau pe STATUS. NICIODATĂ pe valoarea ordinală.
  Valoarea ordinală există EXCLUSIV pentru ordonare/afișare, niciodată pentru decizie.

ȘI SE FACE INEXPRIMABIL, nu doar interzis — aceeași unealtă ca L-U2:
  descriptorul ajunge la nivelul 6 ca SENTINEL atunci când e UNDETERMINED, iar aritmetica EV
  nu poate consuma un sentinel. Un `if` pe valoare poate fi uitat la o refactorizare; un tip
  care nu se poate aduna, nu.
```

**Consemnez că e a treia oară când aceeași formă rezolvă problema: sentinel la L-U2, ordinal unic la Z4 (ca să nu existe contradicția), sentinel din nou aici (ca să nu existe citirea aritmetică). Mecanismul e stabil; îl reutilizez, nu îl reinventez.**

## Z4-L2 — ce validează de fapt un rezultat de nivel 4

**Accept integral, și consemnez cu cuvintele care închid ambiguitatea:**

```
Granița de timp (fereastra se închide la hit+W, intrarea la hit+W+1) ÎNLOCUIEȘTE tranzacția
nivelului 3 cu alta: intrare cu ~5 ore mai târziu, alt preț, alt risc, alt stop.

⇒ Un rezultat de nivel 4 validează o INTRARE PE MOMENTUM POST-FEREASTRĂ.
  NU validează un filtru de zonă. NU spune nimic despre oportunitatea de la nivelul 3.
  Cele două NU se compară direct și NU se raportează una ca „versiunea filtrată" a celeilalte.
```

**Am spus deja la specificație că „confirmarea nu filtrează oportunitatea, o înlocuiește". Red Team duce consecința mai departe decât am dus-o eu: nu doar că tranzacția e alta, ci că OBIECTUL VALIDAT e altul. Accept formularea lui.**

---

## HANDOFF

**VE:** preia seed-ul pe cheie stabilă în cod; implementează sentinel-ul Z4-L1 la interfața nivel-4 → nivel-6; nu rula W-incr pentru CAND-0007 — nu s-a ajuns la el.
**Red Team:** ținta explicită e Partea 4 — dacă declarația de putere („efect minim detectabil ~0,43-0,48 R") e o măsurătoare onestă sau o scuză scrisă după un rezultat nul; și dacă aproximarea normală folosită pentru ea e legitimă pe o distribuție cu coadă grea.
**CEO, cinci lucruri:** **(1) VERDICT: niciun candidat nu respinge H0. Zero promovări. (2) Corecția de multiplicitate NU a fost constrângerea — cel mai mic p e 0,185, de 3,7× peste un prag NECORECTAT de 0,05; rezultatul ar fi fost identic la m=1. (3) Condiția pe CAND-0003 e satisfăcută (p=1,000, ne-respingere), deci verdictul lui e admisibil. (4) Pentru CAND-0001 și CAND-0007 verdictul e o afirmație despre PUTERE la fel de mult ca despre piață — testul putea vedea doar ~0,43-0,48 R, iar ei au 0,14-0,16; pentru CAND-0002 și CAND-0003 citirea e mai tare, fiindcă semnul e negativ. (5) Verdictul respinge o PARAMETRIZARE TESTATĂ pe date de descoperire cu costuri modelate — nu un concept, nu holdout-ul, care rămâne sigilat.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.56 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
