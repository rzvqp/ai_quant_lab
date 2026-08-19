# STATISTICIAN — ANALIZA CORPUSULUI `CEO_CONFIRMED` BLIND-001…048 CONTRA `ve_n1_replay 0.4.1`

**Document ID:** STAT-RANGE-V3-CORPUS-ANALYSIS-v1.0 · **Data:** 2026-08-19 · **Autor:** Statistician

## VERDICT TERMINAL

```
RANGE_V3_SEMANTIC_DELTA_REQUIRED
următorul proprietar: CEO — decizie asupra deltei de contract (NU trimit nimic către VE)
```

**NU emit `BLIND_PASS`, `RANGE_V3_SEMANTIC_PASS`, `STRATEGY_CATALOG_READY` sau `ALPHA_AUTHORIZED`.** Etichetarea nu e independentă: corpusul e `CEO_CONFIRMED`, utilizabil pentru diagnostic și construcție, atât.

---

# 1 — VERIFICĂRI

```
cele 5 fișiere: 5/5 SHA-256 se potrivesc EXACT                                    ✔
continuitate BLIND-001…048: COMPLETĂ, zero duplicate                              ✔
escrow RT-BLIND-ESCROW-RANGE-V3-002 desigilat, 48 mapări, window_list d9f77eea…   ✔
artefact rulat: ve_n1_replay 0.4.1, wheel 39673910…81f4, o SINGURĂ dată            ✔
```

## 1.1 Trei ferestre nu se pot alinia — și nu le repar

Am verificat încrucișat lungimea declarată în etichete cu lungimea reală din escrow. **45 din 48 se potrivesc exact.** Trei nu:

```
             real (escrow)   etichetă   index max din segmente
BLIND-046        288           480              480   ← depășește fereastra reală
BLIND-047         96           288              288   ← depășește fereastra reală
BLIND-048        480           288              288
```

**Nu e o permutare recuperabilă.** Fereastra reală de 96 de bare (`BLIND-047`) nu are corespondent: niciuna dintre cele trei etichete nu declară 96 de bare. Cel puțin o pagină reală nu a fost etichetată, iar pentru două dintre ele indicii de segment cad în afara ferestrei.

> **Nu le remap și nu le trunchiez. Le EXCLUD din comparația cantitativă și raportez faptul. O realiniere ghicită ar fabrica o corespondență pe care datele nu o susțin.** Analiza rulează pe **45 de ferestre**; rularea detectorului s-a făcut pe toate 48, ca o eventuală corectare a etichetelor să nu ceară o a doua rulare.

---

# 2 — CONFIGURAȚIA, DECLARATĂ ÎNAINTE DE RULARE

```
w_atr = 0.30   singura valoare ratificată vreodată (v2.7.80), TRANSPLANTATĂ PROVIZORIU.
               Spec V3 spune explicit că e INVALIDĂ sub noua ancoră și trebuie rederivată.
N     = 2      n_acceptance MOȘTENIT din V2 — singura valoare ratificată
K     = 2      maximul permis de constrângerea structurală K <= N. Nu există altă bază.
d_min = 96     MULTIDAY, valoarea implicită MOȘTENITĂ
n_touch = 2 · swing_k = 2 · atr_window = 14   moștenite
```

**Niciun parametru nu a fost căutat, potrivit sau reglat. O singură trecere, rezultatul care a ieșit.**

## Două note de proces, spuse înainte să fie descoperite

**(a) Prima execuție nu a capturat nimic** — citeam un câmp inexistent (`semantic_state`) și am obținut `None` pe fiecare bară. Am corectat extracția și am reexecutat. Calculul e determinist și configurația neschimbată: **nu e o a doua rulare a detectorului în sensul interzis, ci prima citire reușită a aceleiași rulări.** O consemnez fiindcă distincția e a mea de apărat, nu a cititorului de ghicit.

**(b) Era să public o inferență greșită.** Comparasem durata sweep-urilor CEO (mediana 10 bare) cu `K = 2` și era să conchid că sweep-urile sunt nereprezentabile prin construcție. **Greșit:** `K` numără *închideri consecutive în afară*, nu bare scurse. Am retras inferența înainte de a o scrie și am testat-o corect după rulare (§5).

---

# 3 — CE PRODUCE DETECTORUL

```
12.960 bare pe 45 de ferestre

lifecycle   ESTABLISHING     11.731   90,52%
            BREACH_PENDING    1.229    9,48%
            ESTABLISHED            0    0,00%     ← NICIODATĂ
```

```
reason codes   TOO_SHORT                7.601
               IS_CHANNEL               6.685
               FEW_TOUCHES              5.426
               ESTABLISHING_FEW_SWINGS  5.359
               ZONES_DEGENERATE            24
```

```
evenimente emise   TRANSITION 6.079 · RANGE_MID 3.092 · BOUNDARY_TEST_UPPER 1.278 ·
                   BOUNDARY_TEST_LOWER 1.055 · RANGE_ESTABLISHING 512 ·
                   LIQUIDITY_SWEEP_DOWN 474 · LIQUIDITY_SWEEP_UP 473 ·
                   BREAKOUT_ACCEPTANCE_DOWN 262 · BREAKOUT_ACCEPTANCE_UP 247
                   RANGE_ESTABLISHED: 0
```

## Ce a construit VE CORECT — se spune înainte de ce lipsește

```
✔ ZONES_DEGENERATE EXISTĂ și se declanșează (24 emisii). Garda pe care am cerut-o la v2.7.80
  și am raportat-o LIPSĂ la v2.7.82 e implementată și vie.
✔ TOO_SHORT e VIU — 7.601 emisii. La V2 nu se declanșa NICIODATĂ (poarta era moartă).
  Reparația structurală pe care am cerut-o funcționează.
✔ BREACH_PENDING + NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT există: cursa sweep-vs-breakout
  e modelată explicit, exact cum cere spec-ul.
✔ predecessor_id există: un breakout acceptat ÎNCHEIE segmentul fără să-l șteargă.
✔ K, N, w_atr NU au valori implicite, iar construcția refuză fără acknowledge_construction_only.
  Statutul NEIDENTIFICAT e impus prin TIP, nu prin documentație.

Artefactul e FIDEL specificației mele. Ce urmează nu e o critică a execuției VE.
```

---

# 4 — LANȚUL DE PIERDERE: DE CE ZERO

```
552 segmente deschise pe cele 45 de ferestre
vârsta maximă atinsă de un segment:  mediana 17 bare · p90 39 · MAXIM 80
câte ating d_min = 96:  ZERO  (0,0%)
```

> **Aceasta e cauza dominantă, și e a MEA. La V3 am legat ancora de SEGMENT — reparație corectă, fiindcă la V2 ancora se calcula pe 512 bare fixe. Dar am lăsat `d_min = 96` MOȘTENIT dintr-un design în care „durata" măsura cu totul altceva (vârsta celui mai vechi swing reținut, plafonată la 512). O ancoră locală produce segmente scurte: mediana 17, maximul 80. Pragul de 96 stă DEASUPRA maximului observat, deci starea de confirmare e inaccesibilă.**
>
> **La V2 poarta de durată nu putea EȘUA. La V3 nu poate REUȘI. Am mutat vacuitatea dintr-un capăt în celălalt. E a UNSPREZECEA eroare a mea prinsă de mine în acest dosar, și e din aceeași familie ca celelalte: am transplantat o constantă peste o schimbare de sens.**

**Precizare necesară, ca să nu supra-afirm:** vârsta de 80 de bare e măsurată sub ACEASTĂ configurație transplantată. Un `w_atr` diferit ar schimba durata segmentelor. **Nu pot conchide că `96` e valoarea greșită** — pot conchide că interacțiunea dintre ancora legată de segment și un `d_min` moștenit e **NEREZOLVATĂ** și trebuie identificată împreună, nu transplantată.

Restul lanțului, pentru completitudine: atingeri ≥2 pe ambele laturi pe **28,6%** din bare; `IS_CHANNEL` pe 6.685 din 12.960.

---

# 5 — REZULTATELE CERUTE, PE CLASĂ

| clasă / eveniment | segmente CEO | găsite de detector | recall | precizie |
|---|---|---|---|---|
| `RANGE` | 103 | **0** | **0,00** | n/a |
| `CHANNEL_UP` | 51 | 0 | 0,00 | n/a |
| `CHANNEL_DOWN` | 39 | 0 | 0,00 | n/a |
| `TRANSITION` | 64 | 6.079 bare | 0,00 | 0,00 |
| `BREAKOUT_UP` | 31 | 247 | 0,00 | 0,00 |
| `BREAKOUT_DOWN` | 21 | 262 | 0,00 | 0,00 |
| `SWEEP_UP` (+failed) | 31 | 473 | 0,00 | 0,00 |
| `SWEEP_DOWN` (+failed) | 41 | 474 | 0,00 | 0,00 |

```
IoU temporal pe cele 103 segmente RANGE:   mediana 0,000 · maxim 0,000
eroarea mediană a limitelor:               NECALCULABILĂ — nu există nicio limită de segment confirmat
false negative:                            227 segmente (lista completă în fișierul dedicat)
false positive:                            toate cele 1.456 de evenimente de sweep/breakout
```

## Confuzia principală: evenimentele nu sunt aceleași OBIECTE

```
episoade BREACH_PENDING ale detectorului:  721 · mediana 2 bare · MAXIM 2 bare
sweep-uri etichetate de CEO:                62 · mediana 10 bare · maxim 22 bare
```

> **`K = 2` TRUNCHIAZĂ fiecare depășire la două bare. Detectorul emite micro-evenimente de două bare de 15 ori mai des decât vede omul sweep-uri. Nu e o eroare de detecție — sunt obiecte diferite cu același nume. Orice recall/precizie pe sweep-uri sub această configurație e INADMISIBIL ca dovadă despre semantica detectorului, și îl raportez doar ca să fie vizibil de ce.**

## Pe lungime de fereastră și pe bloc

| | ferestre | RANGE etichetate | bare `ESTABLISHED` | evenimente detector |
|---|---|---|---|---|
| 96 bare | 15 | 25 | **0** | 1.495 |
| 288 bare | 15 | 36 | **0** | 4.490 |
| 480 bare | 15 | 42 | **0** | 7.487 |
| B1 | 11 | 24 | **0** | 3.089 |
| B2 | 12 | 29 | **0** | 3.592 |
| B3 | 11 | 20 | **0** | 3.295 |
| B4 | 11 | 30 | **0** | 3.496 |

**Rezultatul e invariant la lungime și la bloc.** Nu e un efect de eșantion, de epocă sau de regim: e structural.

---

# 6 — CELE ȘAPTE ÎNTREBĂRI DE REPREZENTABILITATE

```
1  RANGE macro cu CHANNEL_UP/DOWN interne          NU
   CEO a etichetat 8 ferestre astfel, cu 34 de segmente interne. Producătorul are UN SINGUR
   segment activ; nu există câmp de imbricare, doar `predecessor_id` — o listă înlănțuită,
   nu o ierarhie. ★ DEFECT DE CONTRACT, declarat explicit.

2  sub-range-uri succesive la niveluri diferite      PARȚIAL, neverificabil
   Lanțul prin `predecessor_id` există (552 segmente), dar niciunul nu ajunge confirmat,
   deci succesiunea nu poate fi observată ca serie de range-uri.

3  breakout care termină range-ul fără să șteargă că a existat     DA structural
   BREAKOUT_ACCEPTANCE emis de 509 ori, segmentul primește `predecessor_id`.
   Reparația cerută la V3 E implementată. Semantic neverificabilă aici: nimic nu ajunge ESTABLISHED.

4  SWEEP_DOWN → reintrare → rupere bullish → displacement          NU, ca SECVENȚĂ
   LIQUIDITY_SWEEP_DOWN există (474), dar nicio stare nu leagă sweep-ul de ruperea ULTERIOARĂ
   de structură. Contractul confirmă sweep-ul la reintrare — corect — dar se oprește acolo.
   ★ DEFECT DE CONTRACT.

5  varianta bearish simetrică                        IDENTIC cu 4

6  acumulare → manipulare/sweep → distribuție        NU
   Rolurile de acumulare/distribuție nu există în contract. CEO le folosește în 12 ferestre.
   ★ DEFECT DE CONTRACT.

7  tranziții range/canal/trend în trepte             NU
   ★ TREND nu există ca stare în V3 — OMISIUNEA MEA la redactarea spec-ului. CEO folosește
   macro de tip TREND_UP_STEPWISE în mai multe ferestre. Fără TREND, o mișcare direcțională
   e forțată în CHANNEL sau în TRANSITION.
```

**Regula de cauzalitate a sweep-ului e respectată de artefact:** confirmarea vine la reintrare, nu pe bara care ia lichiditatea, iar `NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT` marchează explicit intervalul în care nu se poate ști. **Ce lipsește e continuarea** — ruperea de structură în direcția opusă.

---

# 7 — DELTA DE CONTRACT CERUTĂ

```
D1  IERARHIE. Un segment macro trebuie să poată CONȚINE segmente interne, cu un câmp de
    imbricare real. Nu se poate obține prin niciun parametru.
D2  TREND_UP / TREND_DOWN ca stări de plin drept. Omisiunea mea din V3.
D3  ROLURI de segment: ACCUMULATION / DISTRIBUTION / REENTRY / CORRECTION — CEO le folosește
    consecvent, contractul nu le are.
D4  SECVENȚĂ DE SWEEP: sweep → reintrare → rupere de structură în sens opus → displacement,
    ca obiect UNIC cu confirmare în trepte, nu ca eveniment punctual.
D5  IDENTIFICAREA COMUNĂ a lui d_min ÎMPREUNĂ cu ancora legată de segment și cu w_atr.
    Transplantul e ceea ce a produs starea de confirmare inaccesibilă.
```

**Niciunul dintre acestea nu poate fi ratificat din acest corpus.** Lotul e `CEO_CONFIRMED`, nu independent: orice prag scos din el ar fi ales și validat pe același material.

---

# 8 — REZUMAT PENTRU CEO

```
1. Toate cele 5 fișiere se verifică la hash; BLIND-001…048 e complet.
2. Trei ferestre (046/047/048) au lungimi care contrazic escrow-ul; le-am exclus, nu le-am ghicit.
3. Detectorul 0.4.1 a rulat o singură dată, cu parametri moșteniți, nealeși.
4. Din 103 segmente RANGE etichetate de tine, detectorul a confirmat ZERO.
5. Motivul: niciun segment nu trăiește 96 de bare — cel mai lung a ajuns la 80.
6. Cauza e a mea: am legat ancora de segment, dar am lăsat pragul de durată moștenit.
7. La V2 poarta de durată nu putea eșua; la V3 nu poate reuși. Am mutat problema, nu am rezolvat-o.
8. VE a construit corect tot ce am cerut — garda de zone degenerate, cursa sweep/breakout, istoricul.
9. Contractul nu poate reprezenta ierarhia macro/micro, TREND, rolurile de acumulare și secvența de sweep.
10. Nu declar niciun PASS și nu trimit nimic către VE. Aștept decizia ta.
```

---

# 9 — ELEMENTE DESCHISE

```
BLOCANT      d_min NU poate fi identificat din acest corpus. Identificarea cere date care nu sunt
             și sursa etichetelor — altfel se alege și se validează pe același material.
BLOCANT      Ierarhia macro/micro e un defect de CONTRACT: niciun parametru nu o poate produce.
MATERIAL     Corpusul e CEO_CONFIRMED în trei regimuri diferite de proveniență, iar BLIND-001
             e singura fereastră etichetată independent înainte de orice sugestie.
MATERIAL     Trei ferestre excluse; dacă apar etichete corectate, rularea detectorului există deja
             pentru toate 48, deci nu e nevoie de o a doua rulare.
LIMITARE     w_atr = 0.30 e transplantat de sub ancora VECHE. Toate cifrele sunt condiționate de el.
LIMITARE     d_min = 96 (MULTIDAY) aplicat și ferestrelor de 96 de bare cere ca un range să umple
             întreaga fereastră. O rulare INTRADAY ar fi o a doua rulare — neautorizată.
NON_MATERIAL ZONES_DEGENERATE se declanșează de 24 de ori: garda e vie, dar rar activă.
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 · F7 `SAFETY_GUARD` · LIVE_SHADOW · broker gate. Zero PnL, zero optimizare, zero acces SEALED/OOS, zero rerulare.

**Manifest:** v2.7.86.

---
---

# ADDENDUM v1.1 — RECALCULARE PE POPULAȚIA COMPLETĂ DE 48, DUPĂ CORECȚIA `BLIND-046..048`

**Data:** 2026-08-19 · **Verdict:** `RANGE_V3_SEMANTIC_DELTA_REQUIRED` — **NESCHIMBAT.**
**Detectorul NU a fost rerulat.** Ieșirile capturate anterior acoperă toate cele 48 de ferestre, exact cum am prevăzut când am exclus cele trei.

## A.1 — O contradicție între documentele primite, semnalată înainte de orice calcul

Mandatul cere să folosesc *JSON-urile atașate* ca sursă finală. **Le-am verificat și sunt BYTE-IDENTICE cu cele deja consumate — nu conțin corecția:**

```
PART3 atașat  e2a48eec…  ==  PART3 consumat anterior   IDENTIC
PART4 atașat  e77abb89…  ==  PART4 consumat anterior   IDENTIC
ADDENDUM      2b2960f81485af5cf26bf175db36f23f5ff7839ff76b48604bb3588cf9c057a4

                JSON atașat   addendum   escrow (adevăr sigilat)
BLIND-046           480          288        288      ← JSON contrazice
BLIND-047           288           96         96      ← JSON contrazice
BLIND-048           288          480        480      ← JSON contrazice
```

> **Rezolvarea, declarată: pentru `BLIND-046..048` am folosit ADDENDUMUL, fiindcă e singurul document care se potrivește cu escrow-ul sigilat — iar escrow-ul e sursa de adevăr, fixată înainte de etichetare. Pentru `BLIND-025..045` am folosit JSON-urile, neschimbate. Nu am ales între două variante după rezultat: am ales-o pe cea care se verifică împotriva unui artefact sigilat anterior.**

Verificat mecanic: fiecare listă de segmente din addendum se termină EXACT la lungimea reală (288 / 96 / 480), fără indici în afara ferestrei. **Cele trei ferestre sunt acum aliniate și reintegrate.**

## A.2 — Rezultatul principal: CONFIRMAT, neschimbat

```
                                     45 ferestre        48 ferestre (complet)
bare ESTABLISHED                          0                    0
segmente RANGE etichetate               103                  114
segmente RANGE confirmate                 0                    0
IoU mediană / maximă                  0,000 / 0,000        0,000 / 0,000
```

**Toate cele trei condiții cerute se confirmă pe populația completă: zero bare `ESTABLISHED`, zero segmente RANGE confirmate, IoU zero.** Verdictul rămâne, iar restul raportului rămâne valabil literă cu literă.

## A.3 — Cifrele recalculate

```
bare                     14.328   (ESTABLISHING 12.513 = 90,52% · BREACH_PENDING 1.311 = 9,48%)
                         ★ proporțiile sunt IDENTICE cu cele pe 45 de ferestre, la a doua zecimală
reason codes             TOO_SHORT 8.111 · IS_CHANNEL 7.136 · FEW_TOUCHES 5.765 ·
                         ESTABLISHING_FEW_SWINGS 5.713 · ZONES_DEGENERATE 24
evenimente detector      TRANSITION 6.479 · RANGE_MID 3.303 · BT_UPPER 1.372 · BT_LOWER 1.121 ·
                         RANGE_ESTABLISHING 547 · LS_DOWN 505 · LS_UP 499 ·
                         BA_DOWN 282 · BA_UP 263 · RANGE_ESTABLISHED 0
segmente CEO macro       RANGE 114 · TRANSITION 70 · CHANNEL_UP 53 · CHANNEL_DOWN 45   (282)
segmente CEO interne     CHANNEL_UP 13 · RANGE 12 · CHANNEL_DOWN 9                      (34)
evenimente CEO           BREAKOUT_UP 34 · SWEEP_DOWN 38 · SWEEP_UP 28 · BREAKOUT_DOWN 24 ·
                         FAILED_BREAKOUT_DOWN 6 · FAILED_BREAKOUT_UP 5 · LSR_BULLISH 1
false negative           246 segmente
lanț de pierdere         591 segmente deschise · vârstă mediană 17 · MAXIM 80 · ating d_min=96: ZERO
BREACH_PENDING           767 episoade · mediană 2 · MAXIM 2
```

| | ferestre | RANGE etichetate | `ESTABLISHED` | evenimente detector |
|---|---|---|---|---|
| 96 bare | 16 | 28 | **0** | 1.596 |
| 288 bare | 16 | 40 | **0** | 4.787 |
| 480 bare | 16 | 46 | **0** | 7.988 |
| B1 | 12 | 28 | **0** | 3.590 |
| B2 | 12 | 29 | **0** | 3.592 |
| B3 | 12 | 24 | **0** | 3.592 |
| B4 | 12 | 33 | **0** | 3.597 |

**Design-ul echilibrat se vede acum complet: 16 ferestre pe fiecare lungime, 12 pe fiecare bloc.** Rezultatul rămâne invariant pe ambele axe.

## A.4 — O eroare de parsare a mea, prinsă și corectată

La prima transcriere a addendumului am pus rolul segmentului (`UPPER`, `BEARISH_DRIFT`, `REENTRY`) în același câmp cu evenimentul, iar contorul le-a numărat drept evenimente — apăreau șapte „evenimente" inexistente. **Am corectat: doar segmentele `TRANSITION` poartă evenimente; la `RANGE`/`CHANNEL` acel câmp e un ROL.** Cifrele din A.3 sunt cele de după corecție.

## A.5 — Două ambiguități din addendum, consemnate nu netezite

```
BLIND-048  235–330  „acumulare și recuperare CHANNEL_UP"  — două clase într-un segment.
                    Am codificat RANGE cu rol ACCUMULATION_AND_RECOVERY_AMBIGUOUS.
BLIND-048  460–480  „CHANNEL_DOWN / reintrare în range superior" — la fel.
                    Am codificat CHANNEL_DOWN, prima clasă numită.
```

**Niciuna nu schimbă rezultatul** — detectorul nu confirmă nimic în niciuna dintre interpretări. Le consemnez fiindcă o alegere de codificare rămâne o alegere, chiar când e inconsecventă.

## A.6 — Ce NU s-a schimbat

```
verdictul                        RANGE_V3_SEMANTIC_DELTA_REQUIRED
configurația detectorului        NEATINSĂ retroactiv: K=2 · N=2 · w_atr=0.30 · d_min=96
rularea                          UNA singură, cea din raportul principal; zero rerulări
cauza rădăcină                   a mea: ancoră legată de segment + d_min moștenit la 96,
                                 iar segmentele ating maximum 80 de bare
cele 4 defecte de contract       ierarhie · TREND · roluri · secvența de sweep — neschimbate
proveniența                      lotul rămâne CEO_ASSISTED; NU e validare blind independentă
```

**Nu autorizez VE, Alpha, Strategy Catalog, AI Trader, LIVE_SHADOW sau brokerul.**

**Manifest:** v2.7.87.
