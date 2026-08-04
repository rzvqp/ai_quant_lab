# STATISTICIAN — SPECIFICAȚIA NIVELURILOR DE SESIUNE (High / Low / Mid + detector de atingere)

**Document ID:** STAT-SESSION-LEVELS-SPEC-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `code/institutional_levels.py` (`compute_prior_day_levels`, `detect_level_touches`, helper-ul `_runs`) și `code/market_state.py` (`sessions`, `session_of`). **Specificația de mai jos oglindește convenția PDH/PDL bară cu bară** — `available_idx`=prima bară a perioadei următoare (Q4), reset D3_bis pe prima perioadă din bloc, consumare D7 la prima atingere. **Zero convenții noi acolo unde una există deja.**

---

## Obiectul de bază: INSTANȚA de sesiune

```
instanță = rulaj MAXIMAL de bare consecutive cu ACEEAȘI etichetă de sesiune, ÎN INTERIORUL unui bloc.
           Se termină la schimbarea etichetei SAU la granița de bloc (D3_bis) — ce vine prima.
           Se obține cu helper-ul `_runs` DEJA existent, aplicat pe vectorul de etichete
           `market_state.sessions(time)` în loc de `day_index`. Zero cod nou de segmentare.
```

**Ceasurile NU se aliniază — semnalat, nu presupus.** Sesiunile sunt pe ora UTC (`asia<8`, `london<13`, `ny<21`, `late`), iar ziua e ancorată la 17:00 NY (21:00/22:00 UTC, în funcție de DST). **O instanță `late` poate călări o graniță de `day_index`.** Nu impun tăierea pe zi (nici D3_bis, nici absența lookahead-ului n-o cer, iar tăierea ar fragmenta artificial și ar înmulți nivelurile). **Cer în schimb un diagnostic obligatoriu: de câte ori o instanță traversează o graniță de zi**, ca alegerea să fie măsurată, nu asumată.

**Diagnostic suplimentar obligatoriu:** distribuția lungimii instanțelor. O instanță trunchiată de granița de bloc poate avea 1 bară ⇒ `High=Low`, `Mid` degenerat. **Valid mecanic, dar de raportat**, ca o politică să le poată exclude explicit, nu tăcut.

---

# 1 — CARE SESIUNE FOLOSEȘTE NIVELURILE CĂREIA

**Decizia: primitiva e GENERALĂ; restricția e a POLITICII.**

```
Fiecare instanță ÎNCHEIATĂ emite cele 3 niveluri, disponibile de la instanța următoare
(în același bloc). Fiecare nivel poartă eticheta `source_session` (asia/london/ny/late)
și indexul instanței-sursă.
```

**Motivul e precedentul deja ratificat, nu o preferință:** `interactions.py` a fost ratificat ca **localizator generic**, cu regula explicită că o combinație specifică e o *ipoteză* care se pre-înregistrează separat (Mandatul 3.21). **A îngheța „doar Asia→London" în primitivă ar băga o alegere de ipoteză într-un obiect de infrastructură** — exact ce acea decizie interzice. Politica poate filtra pe `source_session` și **trebuie** să declare filtrul ca parte a ipotezei ei.

**Cazul clasic Asia→London rămâne complet exprimabil** — ca filtru declarat de politică, unde e auditabil, nu ca o restricție ascunsă în detector.

**Control împotriva proliferării, obligatoriu:** orice candidat construit pe aceste niveluri **raportează numărul de declanșări defalcat pe `source_session`**, ca înmulțirea obiectelor să fie vizibilă înainte să devină un rezultat.

# 2 — CÂND DEVINE NIVELUL DISPONIBIL

```
available_idx = PRIMA BARĂ A INSTANȚEI URMĂTOARE
              = bara imediat după ultima bară a instanței-sursă.
```

**Identic cu convenția Q4 a lui PDH/PDL**, literal aceeași construcție (`cur_first = days[k][0]`, aici `instances[k][0]`). **Fără lookahead prin construcție:** `High`/`Low` sunt cunoscute abia după închiderea ultimei bare a instanței-sursă, iar `Mid=(High+Low)/2` derivă exclusiv din ele, deci nu adaugă nicio cerință temporală.

**D3_bis:** prima instanță din fiecare bloc **nu are predecesor** ⇒ nu emite niciun nivel (exact `for k in range(1, len(...))` din PDH/PDL). Fără împrumut peste graniță.

# 3 — CÂT TRĂIEȘTE: DOUĂ PRIMITIVE DISTINCTE, măsurate separat

## A — `SESSION_BOUNDED` (curat, analog PDH/PDL)

```
fereastră activă: [available_idx, ultima bară a instanței URMĂTOARE]
expiră: la finalul acelei instanțe, atins sau nu.
active simultan: 3 (H/L/Mid ale unei singure instanțe-sursă) — mărginit prin construcție.
```

## B — `SESSION_PERSISTENT` (acumulativ)

```
fereastră activă: [available_idx, prima atingere (D7) SAU sfârșitul blocului] — ce vine prima.
active simultan: NEMĂRGINIT prin construcție — crește cu fiecare instanță neatinsă.
```

## Controlul obligatoriu pe B, derivat din eșecul deja plătit

**Riscul e cunoscut și cuantificat: DZ×FVG a produs 18.275 tranzacții și −2.432 dolari** — prea multe zone, fiecare fără valoare. **Acel eșec a fost descoperit abia DUPĂ ce au fost generate 18.275 de tranzacții.** Preventivul e ieftin și se impune ACUM:

```
ÎNAINTE ca vreun candidat să fie construit pe B, se măsoară, ca diagnostic de sine stătător:
  (i)  distribuția numărului de niveluri ACTIVE pe bară, per regim (medie, median, max);
  (ii) numărul total de atingeri pe care B le-ar produce, per regim.
Dacă (i) crește monoton fără plafon și (ii) e de ordinul miilor, tiparul DZ×FVG se repetă —
și se știe ÎNAINTE, nu după.
```

**Nu interzic B** — e legitimă, și CEO a semnalat corect că prețul reacționează la un Asia Mid vechi de luni. **Impun doar ca prețul ei structural să fie vizibil înainte de a fi plătit.**

# 4 — CONSUMAREA

**Default: D7 — prima atingere consumă, fără re-armare.** Consecvent cu **fiecare** primitivă de nivel deja ratificată aici (`detect_level_touches` Q5/D7, mitigarea OB, măturarea bazinelor). A devia fără dovadă ar fi o inconsecvență, nu o îmbunătățire.

**Limitarea cunoscută, consemnată nu ascunsă:** Red Team a stabilit deja (RT-CODE-A-0001, §D7) că această convenție **face invizibilă o a doua reacție genuină** la același nivel. Se aplică identic aici. **Alternativa cu re-armare rămâne menționată-dar-neimplementată** — exact tratamentul dat lui D2/D7 la ratificarea originală: dacă se dorește vreodată, cere propria verificare, nu o schimbare tăcută.

---

# 5 — DETECTORUL DE ATINGERE: `Mid` NU e ca `High`/`Low`

**Distincție structurală pe care o adaug, pentru că altfel ar fi un gol tăcut:**

`High` și `Low` sunt **niveluri de lichiditate** — stopurile se odihnesc dincolo de ele; asta e mecanismul pe care se sprijină întreaga familie MK-04. **`Mid` e un punct geometric mediu: nicio lichiditate nu se odihnește acolo.** Sunt clase de obiect diferite, cu mecanisme de reacție diferite.

```
ATINGERE — High:  high[j] >= price     (rezistență, o singură latură — ca PDH)
ATINGERE — Low:   low[j]  <= price     (suport, o singură latură — ca PDL)
ATINGERE — Mid:   low[j] <= price <= high[j]     (range-ul barei CONȚINE nivelul)
```

**`Mid` nu are latură intrinsecă** — se poate aborda din ambele direcții, deci **direcția tranzacției NU poate veni din nivel**, spre deosebire de PDH(short)/PDL(long). **Orice politică ce folosește `Mid` trebuie să DECLARE cum se stabilește direcția** (bias, direcția de abordare, altceva) — nu poate moșteni convenția PDH/PDL, pentru că aceasta nu se aplică.

**Cerință de raportare, obligatorie:** `High`, `Low` și `Mid` se raportează **SEPARAT**, niciodată agregate. Mecanismele diferă; o medie comună ar ascunde exact diferența care contează.

**Restul detectorului oglindește `detect_level_touches` verbatim:** fereastra de disponibilitate de la `available_idx`, mărginită de bloc (D4), consumare la prima atingere (D7), iterare forward-only.

---

## Ce NU am făcut

Nu am implementat nimic. Nu am ales care variantă (A sau B) e „cea bună" — se măsoară separat, exact cum s-a cerut. Nu am construit niciun candidat pe ele.

## HANDOFF

**VE** implementează: segmentarea în instanțe (via `_runs`), cele două primitive de nivel (A și B, distincte), detectorul de atingere cu cele trei reguli, plus **cele trei diagnostice obligatorii** (straddling de zi, lungimea instanțelor, iar pentru B numărul de niveluri active + atingeri totale). **Red Team** atacă. **Alpha** construiește candidați abia după — cu filtrul de `source_session` **declarat**, și cu direcția pentru `Mid` **declarată**.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.39 (commit `2d795bc`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
