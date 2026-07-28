# STATISTICIAN — GEOMETRIA STOPULUI ȘI DECIZIA DE PROIECTARE PE HARTA DE SENSIBILITATE

**Document ID:** STAT-STOP-GEOMETRY-SENSITIVITY-DESIGN-v1.0
**Data:** 2026-07-29 · **Autor:** Statistician

Acest document e o SPECIFICAȚIE — nimic nu se rulează aici. Măsurătoarea A și harta de sensibilitate rămân de executat de VE, DUPĂ publicare, exact cum au fost și celelalte specificații (LM-001, WP-5').

---

## MĂSURĂTOAREA A — geometria noului stop, specificată precis

**Populația: cele 34.670 evenimente de wick-sweep BRUTE (D6/D7), pe cele 130.491 bare de descoperire M15_v2 — NU cele 21.048 deja filtrate.** Motiv: filtrul `[10,1;65,0)` a fost DERIVAT pentru geometria VECHE (distanța la extremul fitilului) — aplicarea lui înainte de a măsura geometria NOUĂ ar fi circulară, chiar scopul măsurătorii fiind să verifice dacă acel filtru mai are sens pentru noua construcție.

**Definiția geometrică, folosind exclusiv `market_structure.py` (Swing/StructureLabel, deja ratificat):**

Pentru un sweep de suport (bazin din swing LOW, intrare LONG): bazinul e format dintr-un `Swing` CLASIFICAT (`label ≠ UNCLASSIFIED`, `kind=LOW`, preț = `basin_price`). „Swing-ul major precedent" = **cel mai apropiat `Swing` CLASIFICAT de tip LOW, cu `idx` STRICT ANTERIOR swing-ului care a format bazinul, ȘI cu `price` MAI EXTREM (mai jos) decât `basin_price`** — dacă un asemenea swing există în ACELAȘI bloc (D4, nu traversează granița). **Dacă nu există niciunul mai extrem** (swing-ul bazinului e deja cel mai jos punct clasificat anterior din bloc), referința rămâne bazinul însuși — geometria NU se lărgește artificial, degradează grațios la vechea construcție. Simetric pentru sweep de rezistență (HIGH, intrare SHORT).

**De ce „mai extrem", nu „doar precedent în secvență":** cuvântul „major" al CTO implică magnitudine, nu doar ordine cronologică — un swing anterior dar MAI PUȚIN extrem nu ar lărgi stopul, ar contrazice intenția de diluare a costului. Semnalez explicit această interpretare — dacă CTO a intenționat altceva (ex. pur și simplu swing-ul imediat precedent, indiferent de extremitate), trebuie reconfirmat înainte ca VE să codeze.

**Distanța măsurată:** `distanță_nouă = |preț_intrare_next-open − preț_swing_major|`, în pips. Raportare identică geometriei vechi: min, p10, p25, mediană, p75, p90, max. **Plus, explicit cerut:** fracția care depășește 65 pips (plafonul vechi) și fracția sub 10,1 pips (podeaua veche), pe agregat ȘI pe cele trei regimuri.

**Caz de margine, tratat explicit, nu ascuns:** evenimente unde NU există niciun swing CLASIFICAT anterior în bloc (aproape de începutul unui bloc, D3_bis) — EXCLUSE din distribuție, numărul lor raportat separat, nu tratate ca zero sau ignorate silențios.

**Consecința deja specificată de tine:** dacă majoritatea depășesc 65 pips, filtrul `[10,1;65,0)` nu se mai aplică mecanic — trebuie re-derivat pentru noua geometrie, nu reutilizat orbește. Rezultatul acestei măsurători DECIDE dacă re-derivarea e necesară, nu o presupun acum.

## DECIZIA — DIAGNOSTIC, nu FITTING, cu pragul scris ÎNAINTE

**Aleg DIAGNOSTIC, fără ambiguitate.** FITTING (care stop dă cel mai bun rezultat) e o optimizare pe date deja consumate — exact ce am respins de-a lungul întregii sesiuni (nicio alegere de prag după ce se văd cifrele). Aici ar fi și mai grav: SMC_S1 a fost deja testat pe ACEEAȘI populație — a alege stopul care „merge cel mai bine" acum ar fi o a doua trecere de optimizare peste date deja privite o dată, fără nicio valoare probatorie.

**Setul de stopuri testate — derivat din Măsurătoarea A, nu ales liber:** cinci puncte — **p25, p50 (mediană), p75, p90 ale noii distribuții de distanță** (Măsurătoarea A) **plus stopul vechi (14,7 pips)** ca ancoră de referință. Cinci puncte fixe, nu o căutare peste orice stop posibil.

**Pragul de decizie, fixat ACUM, înainte de orice cifră:**

```
ÎNCHIS DEFINITIV, nicio ipoteză nouă:
  expectancy net în DOLARI ≤ 0 la TOATE cele 5 stopuri, în TOATE cele 3 regimuri.
  (negativ peste tot, indiferent de stop — linia se închide, nu se mai reformulează SMC_S1_v2.)

MERITĂ IPOTEZĂ NOUĂ (SMC_S1_v2):
  expectancy net în DOLARI > 0 la CEL PUȚIN 2 din cele 3 stopuri mai largi (p75, p90),
  în CEL PUȚIN 2 din cele 3 regimuri.
  (nu un singur punct norocos — un TIPAR, în partea largă a distribuției, unde mecanismul de
  diluare a costului ar trebui să acționeze dacă e real.)

NICIUNA DIN CELE DOUĂ (tipar amestecat, un singur punct pozitiv izolat, sau pozitiv într-un
singur regim):
  se etichetează TESTABLE BUT INSUFFICIENT EVIDENCE / AMBIGUOUS — NU se declară nici închidere,
  nici ipoteză nouă. Cere date suplimentare (nu o retestare pe aceeași descoperire) înainte de
  orice concluzie.
```

Fără acest prag scris acum, orice cifră ulterioară ar fi citită ca justificând continuarea — exact motivul pentru care ceri decizia înainte de rulare.

## PROBLEMA R-vs-DOLARI — raportare duală obligatorie, dolarii sunt variabila de decizie

**Confirmat aritmetic, cifrele tale sunt corecte:** stop 14,7→R=1,67$→cost 24%; 30→3,20$→12%; 45→4,70$→8,5% — toate verificate. Și exemplul: +0,072 R la stop 14,7 pips ≈ 12 cenți/tranzacție; ACELAȘI +0,072 R la stop 45 pips ≈ 34 cenți — DOAR dacă edge-ul brut în R rămâne constant, o presupunere netestată și probabil falsă (winrate-ul și distribuția rezultatului se schimbă cu stopul).

**Regulă, aplicată la orice cifră din harta de sensibilitate:** **fiecare din cele 5×3 celule (stop×regim) se raportează ATÂT în R (expectancy_R) CÂT ȘI în DOLARI (expectancy_R × R_mediu_dolari_al_acelui_stop)** — niciodată doar R. **Variabila de decizie pentru pragurile de mai sus e DOLARII, nu R** — un R mai bun la stop mai larg, cu dolari mai proști, NU trece pragul „merită ipoteză nouă". Motivul exact pe care l-ai dat: R e o unitate normalizată; cost mai mic ca fracție din R nu înseamnă mai puțini bani pierduți, iar stopul mai larg mută ieșirea mai departe de invalidare, cu pierdere mai mare în dolari la aceleași rate de eșec.

## DACĂ PREMISA SUPRAVIEȚUIEȘTE — SMC_S1_v2 ca ipoteză nouă, nu recalibrare

Blocat acum, pentru aplicare ulterioară dacă harta de sensibilitate trece pragul „merită ipoteză nouă":

1. **Stopul derivat, nu ales** — din geometria efectiv măsurată (Măsurătoarea A), cu justificarea scrisă explicit, nu selectat din harta de sensibilitate direct (asta ar fi fitting deghizat).
2. **Filtrul de eligibilitate re-derivat** pentru noua geometrie — nu reutilizat `[10,1;65,0)` orbește (cf. concluziei Măsurătorii A).
3. **Orizontul reconfirmat SAU re-derivat** — un stop mai larg poate schimba timpul necesar pentru ca teza să se joace; nu presupun automat că cele 20 de bare rămân corecte.
4. **Declarație explicită, obligatorie:** descoperirea (aceleași 130.491 bare) e consumată a DOUA oară, pentru o ipoteză aproape identică cu SMC_S1. **Corecție de familie: SMC_S1 și SMC_S1_v2 se tratează ca familie de 2** pentru orice corecție de testare multiplă (același precedent deja aplicat la B.1/B2) — două teste in-sample pe același set, pentru ipoteze apropiate, NU sunt două dovezi independente, indiferent cât de diferite ies numeric.

## SMC_S13 și S10

**SMC_S13:** formularea varianta 3 (fără pretenție de rată peste linia de bază, intrare next-open de piață, orizont 20 bare Grupa A) — confirmată acceptată. Corecția 12→20 era necesară, cf. verificării deja făcute (12 = lungimea sesiunii `late`, declanșatorul nefiind legat de acea sesiune specific).

**S10:** rămâne deschis, neschimbat.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.7 (commit `b98070c`, `alpha-automation-v1`). Holdout SEALED — nimic executat aici, doar specificat.**
