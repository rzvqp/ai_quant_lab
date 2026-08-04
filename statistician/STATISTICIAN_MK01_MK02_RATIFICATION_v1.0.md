# STATISTICIAN — CONSEMNAREA RATIFICĂRII MK-01 / MK-02, CU TREI DESCHISE ATAȘATE

**Document ID:** STAT-MK01-MK02-RATIFICATION-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare directă a măsurătorii, nu acceptare:** citit `reports/cascade_frequency_results.json` (comitul `0000225`) și recalculat agregatele:

```
bare cu rupturi 18.961 · cu ≥2 rupturi 7.752 → 40,9%   ✅ exact cifra citată
maxim pe o bară  24                                     ✅ exact
rupturi pierdute definitiv sub semantica veche  542     ✅ exact
```

**Verificare de consistență internă pe care o adaug:** `breaks_new − breaks_old = 34.731 − 34.189 = 542` — **exact** numărul de referințe pierdute definitiv. Cele două cifre se derivă independent în raport și coincid la unitate. **Asta confirmă empiric predicția pe care am derivat-o la v2.7.38**: `elif`-ul nu întârzia doar, ci **PIERDEA** ruperi, iar creșterea de număr e exact mulțimea pierdută — nu o inflație de altă natură. Predicția era teoretică; acum e măsurată.

---

# CONSEMNEZ RATIFICAREA

**MK-01 `market_structure.py` și MK-02 `liquidity_mechanics.py` — RATIFICATE.** Alpha poate construi pe ele.

Lanțul e complet: fidelitate D1-D7 (7/7, Mandatul 3.45) → executabilitate + remediere F2/F3 (VE) → reatac Red Team (RT-CODE-A-0001, RT-CODE-A-0002) → semantică de cascadă specificată și implementată (Mandatul 3.51) → măsurătoare care confirmă amploarea → **ratificare CEO.**

## O precizare care trebuie ÎNGHEȚATĂ, nu doar consemnată

VE a stabilit că zero din patru situri sunt afectate prin schimbarea de referință. **Confirm concluzia. Dar ascut motivul, pentru că formularea contează pentru viitor:**

Argumentul „`_first_break_after` filtrează pe `kind`, deci tipul nu se poate schimba" e adevărat, **dar nu e suficient singur** — la aceeași bară pot apărea acum **două rupturi de ACELAȘI `kind`** (două BOS_BULL, pe două HH-uri distincte), iar `b.idx < best.idx` e **strict**, deci nu le departajează: câștigă **prima din listă**. Ordinea decide.

**Motivul real pentru care nimic nu se schimbă e a doua clauză — „la egalitate, alegerea rămâne aceeași ca înainte" — și ea ține EXACT pentru că am specificat ordinea DESCENDENTĂ după `reference_swing.idx`** (Mandatul 3.51), aleasă tocmai ca prima poziție să rămână cel mai recent swing, adică fix ce emitea `live_hh` înainte.

> **Consecință operațională: regula de ordonare descendentă e PORTANTĂ, nu incidentală. Dacă ordinea se schimbă vreodată, referința se schimbă odată cu ea, tăcut, în S2/S3/S10/S11.** Se îngheață ca invariant, cu test dedicat (mai jos), nu ca o convenție de stil.

---

# DESCHIS 1 — F4: nu se rezolvă acum, și spun exact ce înseamnă

## Poziția: F4 NU e un defect al detectorului

Când `live_lh.price < close[c] < live_hl.price` (un LH sub un HL — structură încrucișată, apex de triunghi), se emit `CHOCH_BULL` și `CHOCH_BEAR` pe aceeași bară. **Ambele afirmații sunt adevărate despre bară.** Ambiguitatea e în **structura etichetată**, nu în detecție — detectorul raportează fidel o stare structural contradictorie.

**A suprima arbitrar una dintre ele ar ASCUNDE o ambiguitate reală** și ar reintroduce exact clasa de artefact pe care tocmai am eliminat-o (o regulă de precedență care șterge un eveniment adevărat). **Deci: nu se rezolvă în interiorul detectorului. Ambele se emit.**

## Regula de interpretare downstream — FAIL-CLOSED implicit, declarată explicit per consumator

```
Orice consumator care primește, la aceeași bară, CHOCH_BULL și CHOCH_BEAR:
  DEFAULT (dacă nu declară altfel):  NICIUN semnal pe acea bară — fail-closed.
  Alternativ: poate declara o regulă proprie, dar EXPLICIT, auditabilă, pre-înregistrată
              alături de ipoteza care o folosește — niciodată un default implicit în cod.
```

**Motivul default-ului:** e convenția deja stabilită a acestui laborator pentru ambiguitate nerezolvabilă (trigger FAIL-CLOSED la CAND-0004/0005/0006, `after=0` fixat fail-closed la CAND-0007, INVALID_EXECUTION la fill ambiguu). **Un semnal contradictoriu e exact cazul în care a acționa pe oricare latură e nejustificat.**

## Ce cer măsurat, ca deschisul să nu rămână de severitate necunoscută

**Frecvența F4 nu e măsurată.** Cascada a fost măsurată (40,9%); F4 cere în plus structură încrucișată. **Cer măsurarea în același pas ca restul: câte bare emit simultan `CHOCH_BULL` și `CHOCH_BEAR`, per regim, absolut și ca fracție din barele cu rupturi.** Ieftin, aceeași infrastructură. **Fără cifra asta, „nebocant" e o presupunere; cu ea, e un fapt.**

---

# DESCHIS 2 — cele patru teste lipsă, specificate ca cerințe de acceptare

```
T1  F4 — structură încrucișată (LH.price < HL.price), close între ele.
    ASERT: se emit AMBELE (CHOCH_BULL + CHOCH_BEAR) la aceeași bară; ambele consumate;
    ordinea deterministă. (Pinuiește comportamentul, nu îl rezolvă.)

T2  SELECȚIA REFERINȚEI — ≥2 rupturi de ACELAȘI kind pe o bară.
    ASERT: `_first_break_after` returnează swing-ul CEL MAI RECENT.
    ★ Testul cel mai important din cele patru: transformă regula de ordonare descendentă
    dintr-o convenție într-un INVARIANT IMPUS. O schimbare viitoare de ordonare va sparge
    un test, în loc să schimbe tăcut semantica S2/S3/S10/S11.

T3  CONSERVAREA AGREGATĂ — pe un bloc întreg.
    ASERT: numărul de rupturi = numărul de swing-uri distincte depășite vreodată cât erau
    active. Niciunul pierdut, niciunul dublat.
    ★ Testul cu cea mai mare putere diagnostică: e EXACT invariantul pe care bug-ul vechi
    îl încălca (542 pierdute) și pe care nicio suită nu-l verifica.

T4  MULTIPLICITATE MARE — o bară care rupe ≥24 swing-uri stivuite (maximul MĂSURAT).
    ASERT: toate emise la acea bară, toate consumate, ordine totală, fără trunchiere sau
    off-by-one la scară. Testele existente ating maximum 3; realitatea a produs 24.
```

**Cerute lui VE.** Ratificarea nu e condiționată de ele (CEO a decis), dar **golul de acoperire rămâne consemnat până sunt livrate** — nu se închide tăcut.

---

# DESCHIS 3 — re-rularea S2, S3, S11: ce și cum

## Cauza reală, acceptată: se schimbă MULȚIMEA, nu referința

VE a stabilit corect: nu e o deplasare de referință (T2/ordinea o previn), ci **mulțimea de rupturi se schimbă** — 542 de rupturi care nu existau deloc sub semantica veche există acum, plus mii mutate pe bara corectă. **Apar setup-uri genuin noi**, nu doar deplasate. Cu fereastra de eligibilitate de 20 de bare ancorată pe indexul rupturii, o rupere nouă sau mutată **schimbă eligibilitatea**, nu doar momentul intrării.

## Rămâne CORECȚIE DE EXECUȚIE — nu consumă familia. Motivul, explicit:

**Ipoteza nu se schimbă.** S2 rămâne „BOS → CHoCH opus în ≤20 bare → fade". Detectorul sub-livra evenimente pe care ipoteza le acoperea dintotdeauna. **A repara implementarea și a re-rula NU e o a doua încercare pe aceleași date — e prima încercare corectă.** Familia (7) rămâne neatinsă.

## Dar disciplina care ține asta adevărată — PRE-ANGAJAMENT, specificat ACUM

**Riscul real nu e conceptual, e comportamental:** o re-rulare care produce cifre mai bune poate deveni, retrospectiv, „am reparat până a ieșit bine". **Se previne prin pre-angajament, scris înainte de re-rulare:**

```
DOMENIU  exact S2, S3, S11 — cele trei care consumă detect_breaks și au rezultate măsurate.
         S10 EXCLUS (rebuclă deschisă, exclus deja). S1/S7/S13/S16/S17 NU se ating
         (verificat: nu apelează detect_breaks).
CE       exact aceleași metrici, aceleași regimuri, același cost și aceeași podea ca la
         rularea originală. NIMIC ALTCEVA nu se schimbă odată cu detectorul.
CUM      rezultatul nou ÎNLOCUIEȘTE rezultatul vechi, în ORICE direcție ar merge —
         inclusiv dacă iese mai prost. Ambele se păstrează în consemnare, cu delta.
RAPORTAT obligatoriu: n vechi vs n nou per familie/regim (câte setup-uri sunt genuin noi),
         ca amploarea schimbării de populație să fie vizibilă, nu îngropată în medie.
INTERZIS orice altă modificare de parametru „profitând" de re-rulare.
```

**Cu pre-angajamentul de mai sus, re-rularea rămâne o corecție. Fără el, ar deveni o a doua șansă deghizată.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.39 (commit `2d795bc`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
