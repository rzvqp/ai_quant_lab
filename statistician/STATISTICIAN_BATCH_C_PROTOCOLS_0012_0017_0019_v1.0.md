# STATISTICIAN — PROTOCOALELE PENTRU CAND-0012, CAND-0017, CAND-0019

**Document ID:** STAT-BATCH-C-PROTOCOLS-0012-0017-0019-v1.0
**Data:** 2026-08-10 · **Autor:** Statistician
**Închide:** restanța proprie declarată la v2.7.42 și reconfirmată la fiecare raport de stare de atunci.

**Verificare de sursă:** citit direct `reports/phase1_screening_results.json`. **Prima constatare răspunde întrebării din mandat înainte de a o pune: re-screening-ul S-A FĂCUT DEJA.**

---

# PARTEA 0 — CIFRELE DIN MANDAT SUNT STALE. Fișierul e deja post-reparație.

```
                     MANDAT (pre-reparație)              FIȘIER, CITIT ACUM
CAND-0012   199 tr  PF 1,20   +139 R  1/4  2/3     199 tr  PF 1,10   +14,1 R  1/4  2/3
CAND-0017 18275 tr  PF 0,98  −2432 R  3/8  1/3   18275 tr  PF 0,76  −2876,5 R  0/8  0/3
CAND-0019  1208 tr  PF 1,43   +440 R  7/8  3/3    1208 tr  PF 1,08    +80,6 R  4/8  2/3
```

**Numărul de tranzacții e IDENTIC la toate trei; fiecare cifră de performanță s-a mutat.** Aceea e semnătura exactă a reparației D1: aceleași declanșatoare, alte rezultate. **Deci nu cer re-screening de la VE — există.**

---

# PARTEA 1 — RĂSPUNSUL LA ÎNTREBARE, care se împarte în două

**„Am nevoie de re-screening înainte de protocol, sau protocolul se scrie independent de cifre?"**

```
CONȚINUTUL PROTOCOLULUI   INDEPENDENT DE CIFRE, prin construcție. Un protocol e un plan
                          PRE-ÎNREGISTRAT; dacă ar depinde de rezultate, ar fi testul ales
                          pe date, adică exact ce previne pre-înregistrarea.
TRIAJUL                   DEPINDE de cifre — el decide dacă se cheltuie un slot de familie.
```

**Deci întrebarea are răspuns dublu, iar partea care conta chiar avea nevoie de cifre proaspete. Ele există, și schimbă verdictul pentru unul dintre cei trei.**

**Nu e selecție:** criteriul de triaj a fost fixat la v2.7.42, cu mult înaintea acestor cifre. A-l aplica pe date noi e execuția regulii, nu alegerea ei.

---

# PARTEA 2 — TRIAJUL, APLICAT PE CIFRELE CURENTE

## CAND-0017 → ARHIVAT-NEGATIV. Reparația l-a mutat din C în A.

```
n = 18.275   minim pe regim = 3.548 (≫ N_MIN=25)   ani pozitivi 0/8   regimuri pozitive 0/3
E_R = −0,157   PF = 0,76
```

**Criteriul A cere: n ≥ N_MIN în fiecare regim ȘI negativ în TOATE regimurile ȘI niciun an pozitiv. Toate trei se îndeplinesc.** Înainte de reparație era 3/8 ani și 1/3 regimuri — semn mixt, deci categoria C. **Reparația l-a mutat din C în A.**

> **CAND-0017 se ARHIVEAZĂ. Nu primește protocol.** Și e cazul pe care CEO l-a semnalat: 18.275 de declanșatoare, tiparul de saturație. **Dar nu îl arhivez pe saturație — o arhivez pe criteriu.** Saturația explică de ce e negativ; criteriul decide ce facem.

## CAND-0012 și CAND-0019 → CATEGORIA C. Amândouă primesc protocol.

```
CAND-0012  min pe regim 39 ≥ 25 ⇒ NU e arhivat-insuficient. 1/4 ani, 2/3 regimuri ⇒ semn MIXT ⇒ C.
CAND-0019  min pe regim 231.    4/8 ani, 2/3 regimuri ⇒ semn MIXT ⇒ C.
```

**La întrebarea „CAND-0012 e sub prag de stabilitate?" — răspunsul e NU, și refuz să inventez unul acum.** Criteriul are `n ≥ N_MIN` per regim (39 trece) și testul de semn. **A adăuga un prag de stabilitate DUPĂ ce văd 1/4 ani ar fi exact selecția pe care o refuz peste tot.**

**Dar spun ce e adevărat despre putere, ca un rezultat nul să nu fie citit greșit:** la n=199 și E_R = +0,071, cu distribuția R grea de coadă, **testul aproape sigur nu va atinge semnificația.** **Un „nu se respinge H0" la CAND-0012 va însemna PUTERE INSUFICIENTĂ, nu absența edge-ului.** Se pre-declară acum.

## Familia: rămâne 16. Arhivarea NU returnează slotul.

**Cei trei erau deja numărați în familia de 16 la v2.7.43. Iar la v2.7.48 am fixat că familia e MONOTONĂ — un candidat admis nu iese niciodată, pentru că scoaterea ar SLĂBI pragul pentru ceilalți.** Se aplică și când mă dezavantajează: **CAND-0017 se arhivează, dar rămâne numărat. Familia stă la 16.**

---

# PARTEA 3 — PROTOCOALELE

## Elemente comune (reutilizate neschimbat de la STAT-BATCH-A-0001/A-0002)

```
REGIMURI      cele 3, cu N_MIN=25 și suprimare-nu-etichetare
ORACOL        block_bootstrap pe `net_R`, cu BLOC PE TIMP CALENDARISTIC (v2.7.45) — o zi de
              tranzacționare; L=28 pe indexul tranzacției e RETRAS ca transplant de unitate.
              Prag: ≥10 blocuri (zile distincte cu tranzacții), ≥20 preferat.
PRAG          BH-FDR α=0,05 peste familia de 16 (pragul celui de-al k-lea p ordonat = k·α/16)
HOLDOUT       sigilat, neatins
WALK-FORWARD  2 pliuri pe granițele de regim deja stabilite
PRECONDIȚIE   calibrarea PER CANDIDAT (v2.7.45): ≥1.000 replicări pe distribuția PROPRIE de
              screening, centrată la medie zero, poartă = limita superioară a CI pe FPR ≤ 0,07.
              NICIUN p-value înainte de ea. Se aplică ambilor.
```

## W-incr — obligatoriu la amândoi, pentru că amândoi sunt confluențe

```
CAND-0012 = OB-rejection × nivel zilnic   constituenți: CAND-0011 și CAND-0001
CAND-0019 = demand-zone × nivel zilnic    constituenți: CAND-0013 și CAND-0001

H0 : mean(net_R_confluență) <= mean(net_R al CELUI MAI BUN constituent | ACELEAȘI bare)
     Pe subsetul EXACT unde declanșează confluența. Niciodată populația mai mare a părintelui,
     niciodată contra unui null aleator. Identic cu CAND-0007 și CAND-0010.
```

### Constatare care schimbă cine e baza de comparație

**Măsurat pe cifrele curente: `CAND-0011` e 0/8 ani, 0/3 regimuri, E_R = −0,570; `CAND-0013` e 0/7, 0/3, E_R = −0,325. AMÂNDOI sunt ARHIVAT-NEGATIV.**

> **Deci la ambele confluențe, constituentul „propriu" e structural negativ, iar „cel mai bun constituent" va fi de fiecare dată CAND-0001.** Consecința e că testul incremental NU verifică dacă confluența bate zona sau rejecția — verifică dacă bate NIVELUL SINGUR. **Se raportează așa, altfel „confluența adaugă valoare" s-ar citi ca și cum ar fi bătut ambii constituenți, când unul dintre ei e sub zero.**

**Și limita bazei: CAND-0001 e el însuși netestat formal și e pilot DEMO.** Pentru un test INCREMENTAL asta e admisibil — comparăm cu o populație MĂSURATĂ, nu cu o afirmație validată — dar se consemnează, ca nimeni să nu citească rezultatul ca pe o comparație cu un etalon confirmat.

## Criteriul de succes, per candidat

```
PROMOVARE  cere TOATE:
  (a) precondiția de calibrare TRECE (CI sup pe FPR ≤ 0,07);
  (b) p-value BH-semnificativ peste familia de 16;
  (c) W-incr semnificativ contra celui mai bun constituent, pe barele identice;
  (d) semnul se menține în ≥2 din 3 regimuri cu n ≥ N_MIN.
ORICE eșec ⇒ NU se promovează. Nu există promovare parțială.
```

## Specificația pentru VE

```
1. rulează precondiția de calibrare per candidat ÎNAINTE de orice p-value;
2. bloc pe ZI calendaristică, nu pe indexul tranzacției; raportează numărul de blocuri;
3. p-value pe `net_R`, apoi W-incr pe barele IDENTICE ale confluenței;
4. raportează per regim și per an ÎNAINTE de agregat;
5. matricea de corelații LUNARĂ înainte de pasul BH (S-R6);
6. CAND-0017: NU se rulează. Arhivat pe criteriu.
```

---

# PARTEA 4 — CAND-0019: e pe DEMO, și trebuie spus ce a pățit

**E singurul din cei trei care tranzacționează acum, deci protocolul lui contează cel mai mult — iar cifra care contează cel mai mult e cât a pierdut la reparație:**

```
net_R    +440  →  +80,6      −82%
PF       1,43  →   1,08
ani +     7/8  →     4/8
regimuri  3/3  →     2/3
```

> **Candidatul care tranzacționează acum pe DEMO a pierdut 82% din edge-ul măsurat când s-a reparat un bug. Nu e o re-ordonare de clasament — e cvasi-dispariția marjei.** La PF 1,08 și +0,067 R/tranzacție, e la un fir de zero. **O consemnez ca fapt, nu ca recomandare: oprirea DEMO e decizie CEO, nu a mea.**

## Tranzacțiile DEMO NU intră în eșantionul de validare

```
Motivul NU e că sunt puține. E că sunt CENZURATE pe rezultatul propriei porți: pe DEMO
există doar tranzacțiile pe care motorul le-a permis. A le adăuga la eșantion ar însemna a
condiționa pe o selecție făcută de sistemul testat — aceeași eroare ca bucla de la Condiția 1.
```

**Ce fac tranzacțiile DEMO în schimb: alimentează măsurarea de cost realizat și verificarea de execuție.** Roluri separate, care nu se amestecă.

---

## HANDOFF

**VE:** rulează în ordinea din Partea 3, punctele 1-6. **CAND-0017 nu se rulează.**
**Red Team, ținte:** dacă mutarea lui CAND-0017 din C în A e reală sau un artefact al reparației; dacă un W-incr cu un constituent sub zero mai e un test incremental; și dacă declarația mea de putere insuficientă pentru CAND-0012 e o predicție onestă sau o scuză scrisă înainte.
**CEO, patru lucruri:** **(1) nu-mi trebuie re-screening — s-a făcut deja; cifrele din mandat sunt stale, iar fișierul e post-reparație, cu numărul de tranzacții identic și toate cifrele de performanță mutate. (2) Conținutul protocolului e independent de cifre PRIN CONSTRUCȚIE — dar triajul nu e, iar pe cifrele noi CAND-0017 trece din C în A și se ARHIVEAZĂ, fără protocol. (3) CAND-0012 rămâne C: refuz să inventez acum un prag de stabilitate, dar pre-declar că la n=199 un rezultat nul va însemna putere insuficientă, nu absența edge-ului. (4) CAND-0019, singurul pe DEMO, a pierdut 82% din net_R la reparație și e la PF 1,08 — faptul e al meu, decizia de a-l opri e a ta.**

**Familia rămâne 16: arhivarea lui CAND-0017 nu returnează slotul, pentru că familia e monotonă — regula se aplică și când mă dezavantajează.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.53 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
