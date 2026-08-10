# SPEC 2 — N4: CEASUL DE CONFIRMARE. CORECȚIE FUNCȚIONALĂ

**Document ID:** STAT-SPEC2-N4-CONFIRMATION-CLOCK-v1.0 · **Data:** 2026-08-11 · **Autor:** Statistician
**Corecție explicită:** N4 NU mai e post-decizie. E parte OBLIGATORIE a deciziei, înainte de N6.
**Obiectiv mărginit:** confirmare cauzală pre-decizie, cel mai scurt ceas valid, plus măsurarea explicită a oportunităților pierdute. **Atât.**
**Măsurat pe M5 real (155.258 bare, 1.161 evenimente de interacțiune, D7 prima atingere), P&L-oarb.**

---

## 1. PRECONDIȚIE, care leagă această specificație de SPEC 1

> **„Prețul intră în zonă" nu e definibil cât timp zona e ancorată pe preț — prețul e mereu în zonă. SPEC 1 (re-ancorarea) e PRECONDIȚIE BLOCANTĂ pentru SPEC 2. Nu e o dependență pe care o introduc; e una pe care o constat.**

## 2. TRADE-OFF-UL CERUT: măsurat, și NU EXISTĂ

**Praguri RE-DERIVATE per ceas ca terțile empirice (ancoră de ocupanță egală — instrument existent), fiindcă P33/P67 au fost ancorate la W=60 și compararea ceasurilor pe praguri fixe ar confunda ocupanța cu calitatea.**

```
  W  minute   MISSED_BEFORE_CONFIRMATION   DETERMINAT   ACCEPTANCE   ABSORPTION   deplasare
  1       5              57,88%              65,81%       32,82%       32,99%       2,52x
  2      10              61,33%              65,81%       32,82%       32,99%       2,87x
  3      15              63,82%              62,62%       32,82%       29,80%       2,91x
  4      20              66,06%              63,48%       32,82%       30,66%       3,11x
  6      30              68,56%              61,84%       32,73%       29,11%       3,48x
 12      60              75,02%              61,24%       32,82%       28,42%       4,31x
 24     120              78,38%              60,72%       32,56%       28,17%       4,97x
 60     300              86,47%              57,07%       31,21%       25,86%       6,38x   ← W actual
```

> # **Nu există trade-off. W=1 domină W=60 pe AMBELE axe.**
>
> **Oportunitățile pierdute cresc de la 57,88% la 86,47%, iar calitatea confirmării SCADE de la 65,81% la 57,07%. O fereastră mai lungă nu ACUMULEAZĂ dovezi — le DILUEAZĂ: cu mai multe bare, persistența și progresul se acordă mai rar în același sens.**

**CEO a cerut măsurarea unui compromis. Raportez că nu e un compromis, ci o dominanță — altfel ceasul s-ar alege ca și cum s-ar plăti ceva ce nu se plătește.**

## 3. AUTOCORECȚIE la propria măsurătoare, înainte de a fi citată

**Prima dată am măsurat MISSED contra ATR-ului M5 la hit și am obținut 69,08% la W=1. Banda RATIFICATĂ a zonei e 1×ATR **M15** (raport median măsurat: 1,84×). Cifra corectă e 57,88%. Coloana de mai sus e cea corectată. Ordonarea între ceasuri e neschimbată — dar nivelul absolut era supraevaluat cu ~11 puncte, și nu-l las să circule.**

## 4. CEASUL: cel mai scurt la care descriptorul RĂMÂNE cel ratificat

**W=1 și W=2 dau rezultate IDENTICE (65,81% / 32,82% / 32,99%). Nu e coincidență:**

```
W=1  persistence ∈ {0, 1}          binar  → terțilele colapsează la marginile {0,1}
W=2  persistence ∈ {0, 0.5, 1}     3 valori → terțilele încă degenerează
W=3  persistence ∈ {0, ⅓, ⅔, 1}    4 valori → terțilele sunt bine definite
```

> **La W ≤ 2, axa de persistență se reduce la un bit, iar clasificatorul cu DOUĂ condiții independente — cel ratificat — devine practic o condiție plus un bit. Rămâne cauzal și funcțional, dar NU mai e clasificatorul aprobat.**

```
CEAS SPECIFICAT:  W = 3 bare M5 = 15 minute = exact O bară M15.
  · cel mai SCURT ceas la care clasificatorul ratificat rămâne cel ratificat;
  · confirmation_delay = 15 min; descriptorul disponibil la hit+4;
  · MISSED_BEFORE_CONFIRMATION = 63,82%, jurnalizat, NU inginerit;
  · alinierea cu cadența M15 a lui N3 e o CONSECINȚĂ, nu un criteriu. Nu o invoc ca justificare.
```

**Dacă CEO preferă exemplul conceptual (prima bară M5 închisă, W=1): e cauzal valid și pierde mai puține oportunități (57,88%), dar cere RE-RATIFICAREA clasificatorului ca fiind cu o singură condiție. Spun ambele; aleg W=3 fiindcă nu cere re-ratificare — regula de scop interzice deschiderea unui gate nou.**

## 5. CE SE JURNALIZEAZĂ, obligatoriu

```
opportunity_id            același id de la N3 — N4 NU creează oportunitate, NU consumă slot
zone_entry_idx            prima interacțiune cu zona (hit)
confirmation_delay        W = 3 bare M5 = 15 min, constantă, în schema_hash
descriptor_available_idx  hit + W + 1
confirmation              LevelOutput[ZoneConfirmation]; UNDETERMINED e REZULTAT (Ok), nu Unavailable
outcome_class             CONFIRMED | MISSED_BEFORE_CONFIRMATION | UNDETERMINED
missed_reason             dacă MISSED: distanța la hit+W+1, în ATR M15
```

> **`MISSED_BEFORE_CONFIRMATION` se jurnalizează și RĂMÂNE pierdută. Ceasul NU se schimbă retrospectiv ca s-o salveze — asta ar fi alegerea momentului deciziei pe baza rezultatului observat, adică exact selecția interzisă la v2.7.59.**

## 6. CE RĂMÂNE DESCHIS

```
BLOCKING      SPEC 1 (re-ancorarea). Fără ea, „prețul intră în zonă" nu e un eveniment.
MATERIAL      P33/P67 se RE-DERIVĂ la W=3 (terțile empirice pe populația de la W=3).
              Reutilizare de instrument existent, NU un gate nou. Pragurile de la W=60 nu
              se transportă — ar fi transplant de unitate, eroarea semnalată de patru ori.
MATERIAL      63,82% MISSED e o atriție PRE-DECLARATĂ. Politica vede ~36% din interacțiuni.
              Se raportează la fiecare rulare; nu se compensează.
LIMITATION    măsurat pe zone de tip `level` (PDH/PDL). Sub SPEC 1 zonele au patru familii;
              curba se re-măsoară la implementare. Ordonarea între ceasuri e robustă — e
              monotonă pe toate cele opt ceasuri — dar nivelurile se vor deplasa.
NON-MATERIAL  ACCEPTANCE e stabil la 32,8% pe toate ceasurile; ABSORPTION scade cu W.
              Asimetria e reală și neexplicată. Nu blochează nimic; se consemnează.
```

**Nu cere: gate nou, framework nou, primitivă nouă, nivel nou. `classify_zone_confirmation` există; se schimbă `w` și se re-derivă două terțile.**
