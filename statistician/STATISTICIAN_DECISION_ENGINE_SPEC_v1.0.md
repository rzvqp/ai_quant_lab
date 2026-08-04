# STATISTICIAN — MOTORUL DE DECIZIE (nivelul 6). SPECIFICAȚIE

**Document ID:** STAT-DECISION-ENGINE-SPEC-v1.0
**Data:** 2026-08-04 · **Autor:** Statistician

**Verificare de sursă:** citit direct `reports/phase1_screening_results.json` (RE-CITIT azi — cifrele s-au schimbat față de mai devreme în aceeași zi), `ai_trader/structural_observer/types.py`. **Prima constatare invalidează cel mai important input din mandat, și nu prin cantitate, ci prin categorie.**

---

# PARTEA 0 — „WINRATE" NU E PROBABILITATEA DE CARE ARE NEVOIE MOTORUL

**Cifrele citate în mandat (winrate 0,435, expectancy +0,334$) nu mai apar în fișier. Re-citit acum:**

```
                              n      winrate   E_R      exits: stop / target / time-stop
CAND-0001  PDH-PDL          1.225     0,175   +0,141      999 /   62 /  164
CAND-0007  LEVEL-FVG          373     0,260   +0,164      271 /   34 /   68
CAND-0029  SESSION-PDHPDL     443     0,178   +0,229      360 /   23 /   60
```

**Mandatul avertizează corect că cifrele s-au mutat. Dar problema e mai adâncă decât o re-verificare de clasament:**

```
CAND-0001:  winrate = 17,5%   dar   ținta e atinsă în 62/1.225 = 5,1% din cazuri.
            Deci ~152 din cele 214 tranzacții câștigătoare (71%) NU vin din atingerea țintei,
            ci din ieșirea pe TIME-STOP.
```

> **Probabilitatea care intră în EV e cea de ATINGERE A ȚINTEI, nu winrate-ul. La CAND-0001 diferența e de la 17,5% la 5,1% — un factor de 3,4.** A introduce winrate-ul ca `p` într-o formulă `p·RR − (1−p)` ar supraevalua EV cu un ordin de mărime, pentru că ar atribui câștigul de tip time-stop unui payoff de RR pe care acele tranzacții nu l-au primit niciodată.

**Consecința de structură: un model cu DOUĂ rezultate e greșit pentru aceste politici.** Ieșirile pe time-stop sunt 13-18% din total la toți candidații verificați, iar la CAND-0001 ele produc majoritatea câștigurilor. **Motorul are nevoie de un model cu TREI rezultate.**

---

# PARTEA 1 — EXPECTED VALUE

## Formula, cu trei rezultate

```
EV_R  =  p_t · RR  −  p_s · 1  +  p_h · E[X | time-stop]  −  c/R

  p_t + p_s + p_h = 1        țintă / stop / orizont
  R    = distanța de risc la intrare, DUPĂ podeaua min_executable_risk   [preț]
  RR   = distanța până la țintă / R                                       [adimensional]
  c    = cost round-trip                                                  [preț]
  E[X|h] = R-ul mediu la ieșirea pe orizont, cu SEMN — poate fi negativ
```

**`− p_s · 1` e exact −1R prin definiția lui R.** `c/R` e termenul care leagă totul de măsurătoarea de cost — și e singurul termen care NU scalează cu volatilitatea (v2.7.24, reconfirmat la v2.7.46).

## Ce e cunoscut în momentul deciziei — și ce nu

```
CUNOSCUT LA INTRARE (calculabil, fără nicio estimare)
  R      stopul e structural ⇒ prețul lui e determinat de bara curentă; podeaua se aplică
  RR     ținta e un nivel structural ⇒ distanța e determinată  (stabilit la CAND-0007:
         planned_RR e COMPUTABIL LA INTRARE, pe distanța PODITĂ)
  c      parametru de configurare, citit la decizie (Partea 4)

NECUNOSCUT — vine EXCLUSIV din istoric
  p_t, p_s, p_h,  E[X|h]
```

> **Deci motorul de decizie e o CĂUTARE DE PROBABILITATE plus aritmetică.** Toată dificultatea reală e în Partea 2. Restul e determinist și verificabil bară cu bară.

**Cerință de audit, derivată din faptul că cifrele se mișcă:** fiecare decizie loghează `R`, `RR`, `c`, vectorul `(p_t, p_s, p_h)`, `E[X|h]`, `EV`, **și hash-ul tabelei de probabilități folosite.** Fără hash, o re-verificare de clasament invalidează tăcut decizii deja luate; cu el, se poate spune exact care.

---

# PARTEA 2 — PROBABILITATEA PER SETUP

## De unde vine: din AMBELE, printr-o ierarhie, nu prin alegere între ele

**„Din fișele medicale sau din context?" e o dilemă falsă. Fișele medicale SUNT deja o tabelă contextuală** (tip × sesiune), iar problema lor e alta: **22 de observații per celulă, 46 din 220 suprimate sub 25.** La n=22, eroarea standard a unei frecvențe în jur de 0,05 e ~0,047 — **aproape la fel de mare ca valoarea estimată.** Folosită brut, o astfel de celulă e zgomot.

**Soluția standard, și e derivată, nu aleasă: contracție ierarhică (empirical Bayes).**

```
p̂(celulă)  =  ( n_celulă · p_celulă  +  k · p̂(părinte) ) / ( n_celulă + k )

  ierarhia (de la general la specific, se adâncește pe măsură ce nivelele 1-5 apar):
     nivel 0   rata globală pe toate setup-urile          ← singurul input necesar la pornire
     nivel 1   + tipul de setup           (PDH/PDL, sweep, FVG, ...)
     nivel 2   + sesiunea                 (fișele medicale existente)
     nivel 3   + regimul / bias-ul HTF    (nivelele 1-2 din arhitectura CEO)
     nivel 4   + harta de zone            (nivelul 3)
     nivel 5   + microstructura           (nivelul 5)
```

**`k` NU se alege: se estimează prin potrivire de momente din varianța ÎNTRE celule** (Beta-Binomial). Dacă celulele diferă mult între ele, `k` iese mic și datele proprii ale celulei domină; dacă diferă puțin, `k` iese mare și celula e trasă spre părinte. **Datele decid cât de mult își merită celula propria estimare.**

## Setup nou, fără istoric: NU are nevoie de o regulă separată

```
n_celulă = 0   ⇒   p̂ = p̂(părinte).    Fără caz special, fără excepție, fără prag.
```

**Asta e proprietatea care face ierarhia potrivită aici.** Un setup nou moștenește automat estimarea celui mai apropiat strămoș cu date; pe măsură ce acumulează observații, se desprinde de el gradual. **Iar dacă nu există nici măcar rata globală, motorul nu are `p` și refuză (Partea 5).**

## Cele 165 de observații structurale

**Se conectează ca STRAT DE CONDIȚIONARE (nivel 5), nu ca declanșator.** `StructuralObservation` e explicit „one recorded fact — never a signal, never evaluated", ceea ce e corect și trebuie păstrat.

**Dar spun direct: 165 de evenimente sunt mult prea puține pentru a condiționa ceva.** Împărțite pe tipuri și pe rezultate, fiecare celulă ar avea o mână de observații.

> **Și tocmai de aceea formula de mai sus e răspunsul potrivit la plângerea din mandat: stratul poate fi CONECTAT ACUM fără să facă rău.** La `n` mic, contracția îl trage aproape integral spre părinte, deci contribuția lui e ~zero până când are date. **Observațiile încetează să fie ignorate, fără ca puținătatea lor să contamineze deciziile.** Asta e ce înseamnă „degradare grațioasă" concret, nu ca slogan.

---

# PARTEA 3 — PRAGURILE. Două sunt derivabile, unul e alegere, iar trei porți se reduc la una.

## Observația care simplifică problema: cele trei condiții din mandat se suprapun

**„EV > 0 ȘI RR ≥ prag ȘI Confidence ≥ prag" conține o redundanță.** EV e deja o funcție de `p`, `RR` și cost. Un prag FIX pe RR, adăugat peste EV > 0, nu mai e o condiție despre valoarea așteptată — e o condiție despre altceva, și trebuie spus despre ce. La fel „confidence".

## Pragul de RR: derivabil, dar NU ca o constantă

```
EV > 0  ⇔  RR  >  [ 1 − p_h(1 + E[X|h]) + c/R  −  p_t ] / p_t
```

**Deci „pragul de RR" e o FUNCȚIE de `p` și de cost, nu un număr.** Condiția EV > 0 îl conține deja; un prag fix suplimentar ar fi arbitrar.

**Există totuși un prag FIX derivabil, dintr-o considerație diferită — fezabilitatea:**

```
RR_min = c / R          ← chiar și la p_t = 1, un câștig mai mic decât costul e pierdere
```

**Se calculează per tranzacție, nu global.** Și leagă direct constatarea de la v2.7.46: **când podeaua mușcă prin termenul absolut, `c/R = 1`, deci `RR_min = 1`** — o tranzacție podită trebuie să câștige cel puțin 1R doar ca să nu piardă. Nu e o preferință, e aritmetică.

## Pragul de winrate: aceeași derivare ca înainte, corectată pentru orizont

```
p_t*  =  [ 1 + c/R − p_h·(1 + E[X|h]) ] / ( 1 + RR )
```

**Cu `p_h = 0` se reduce la `(1 + c/R)/(1 + RR)` — exact formula din care a ieșit banda de 32-36% la RR≈2-2,5.** Nu e o derivare nouă: e aceeași, cu termenul de orizont adăugat. **Iar termenul de orizont contează: la `p_h ≈ 0,13` și ieșiri pe orizont majoritar câștigătoare, pragul de atingere a țintei SCADE substanțial** — ceea ce explică de ce CAND-0001 e marginal pozitiv cu o rată de atingere a țintei de doar 5,1%.

## Pragul de „confidence": îl elimin ca poartă separată. E o alegere, dar una singură.

**„Confidence" nu poate fi decât fiabilitatea estimării lui `p`. Iar atunci nu are ce căuta ca poartă paralelă — trebuie să intre ÎN EV:**

```
EV_LCB  =  EV calculat cu p_t la LIMITA INFERIOARĂ a intervalului de credibilitate,
           nu la estimarea punctuală.
INTRĂ  ⇔  EV_LCB > 0.
```

**Trei porți devin una, și una principială.** Proprietăți care rezultă gratuit:

```
· un setup cu istoric bogat are interval îngust ⇒ LCB ≈ estimare punctuală ⇒ trece ușor
· un setup nou are interval lat ⇒ LCB mic ⇒ NU trece, fără nicio regulă anti-setup-nou
· mai multe date ⇒ interval mai îngust ⇒ poarta se relaxează MONOTON, automat
```

**Nivelul de credibilitate rămâne singura alegere reală, și o declar ca atare: 80% unilateral.**

**Baza alegerii, spusă explicit:** o poartă prea strictă nu produce tranzacții, deci nu produce date — **exact patologia din mandat, unde 165 de evenimente nu sunt citite de nimeni.** În etapa DEMO scopul e MĂSURAREA, iar o poartă care blochează tot nu măsoară nimic. 80% e permisiv cât să genereze un eșantion măsurabil în orizontul DEMO. **Nu e derivat, e ancorat — și se strânge la 95% în momentul în care motorul trece de DEMO. Condiția de schimbare e declarată acum, nu la momentul rezultatelor.**

## Principiul unificator: fiecare input incert intră la capătul PESIMIST

```
p_t   →  limita INFERIOARĂ a intervalului
c     →  limita SUPERIOARĂ a estimării de cost (Partea 4)
```

**O singură regulă, aplicată consecvent, în loc de o colecție de marje ad-hoc. Incertitudinea împinge întotdeauna spre a NU tranzacționa.**

---

# PARTEA 4 — SLIPPAGE

## Ce folosește motorul până există fill-uri: 0,20. NU 0,05.

**Cea mai tentantă greșeală disponibilă acum ar fi actualizarea la 0,05, și ar fi greșită prin construcție:**

```
c = 0,20 = effective_spread 0,10  +  slippage 0,10
                                     ↑ fixat = spread prin CONVENȚIE (v2.7.37), niciodată măsurat

0,05 e o observație de SPREAD, din cotații.
A pune c = 0,05 înseamnă a seta TĂCUT slippage-ul la ZERO. Nicio măsurătoare nu susține asta.
```

**Regula de substituție, pe jumătăți separate:**

```
c  =  2 × s_măsurat  +  slip

s_măsurat   se înlocuiește când colectarea de spread atinge orizontul de 20 de zile
            (v2.7.44) — se folosește limita SUPERIOARĂ a mediei post-stratificate, nu media.
slip        rămâne 0,10 prin convenție PÂNĂ CÂND există fill-uri reale.
            Înlocuire: slip = 2 × medie(|preț_fill − preț_intenționat|), pe ≥25 de fill-uri,
            din ≥15 zile distincte. Sub asta, convenția rămâne.
```

**Nu se poate măsura din cotații — trebuie ordine EXECUTATE contra prețului intenționat.** Motorul nu poate produce singur datele astea decât tranzacționând, ceea ce e circular; **deci prima serie de fill-uri DEMO e ea însăși instrumentul de măsurare, iar deciziile luate cu `slip` convențional se marchează în jurnal ca atare.**

**Cerință de implementare, nu de statistică: `c` e PARAMETRU citit la momentul deciziei, nu constantă compilată** — altfel înlocuirea cere o re-lansare și deciziile vechi nu mai pot fi re-evaluate cu costul corect.

---

# PARTEA 5 — CRITERIUL DE DECIZIE

```
1  R  = distanța structurală de stop, cu podeaua min_executable_risk aplicată.
2  RR = distanța până la țintă / R.                    [ambele la intrare, pe R PODIT]
3  c  = parametrul de cost, la limita superioară.
4  FEZABILITATE:  RR > c/R   ?  altfel  NO-TRADE, motiv = FEASIBILITY
5  p̂_t, p̂_h, E[X|h] și intervalul lui p_t, din ierarhia Partea 2.
6  EV_LCB = p_LCB·RR − (1 − p_LCB − p_h) + p_h·E[X|h] − c/R
7  INTRĂ  ⇔  EV_LCB > 0  ȘI  toate filtrele dure trec.
```

## Egalitatea

```
EV_LCB == 0  exact  ⇒  NO-TRADE.  Inegalitate STRICTĂ.
```

**Nu e o alegere nouă: e convenția D2 a laboratorului — egalitățile nu produc evenimentul** — reutilizată, nu reinventată. La break-even exact, tranzacția aduce doar varianță.

## Input lipsă: FAIL-CLOSED, explicit

```
ORICE input absent sau ne-finit  ⇒  NO-TRADE, cu CÂMPUL NUMIT în jurnal. Fără valori implicite.

Ce poate lipsi, concret:
  ATR în warmup (primele 14 bare)      → colectorul face deja asta corect
  niciun strămoș cu date în ierarhie   → nu există nici măcar rata globală
  parametrul de cost nesetat            → NICIODATĂ o valoare implicită tăcută
  E[X|h] indisponibil                   → vezi mai jos
```

**`E[X|h]` merită o regulă proprie, pentru că e singurul termen care poate ÎMBUNĂTĂȚI EV.** Dacă lipsește, valoarea fail-closed nu e „refuză", ci **`E[X|h] = −1`** — adică ieșirea pe orizont se presupune la fel de rea ca un stop. **Un termen necunoscut care poate ajuta se pune la valoarea lui cea mai rea, nu la zero.** Zero ar fi o presupunere ascunsă că orizontul iese pe nul.

## Ce NU face motorul

**Nu alege direcția, nu alege stopul, nu alege ținta.** Acelea vin din politică (Alpha). **Motorul răspunde exclusiv la „merită riscul?" pentru un setup deja complet definit.** Dacă ar alege vreuna dintre ele, ar deveni o politică, iar politicile se validează separat.

---

# PARTEA 6 — PORNIREA CU UN SINGUR INPUT

```
ZIUA 1   ierarhia are un singur nivel: rata globală de atingere a țintei pe toate setup-urile.
         EV se calculează. Intervalul e lat ⇒ poarta e strictă ⇒ puține tranzacții. CORECT.
+ fișele medicale     nivel 2 activ; celulele cu n mare se desprind de părinte, restul nu.
+ nivelele 1-2 CEO    regim/bias devin nivel 3.
+ nivelul 3 CEO       harta de zone devine nivel 4.
+ observatorul (165)  devine nivel 5 — conectat ACUM, contribuție ~zero până are date.
```

> **Adăugarea unui nivel nu poate strica motorul, pentru că un nivel fără date se contractă în părintele lui.** Asta e cerința de formă din mandat, satisfăcută de MECANISMUL de estimare, nu de o schelă separată de compatibilitate.

**Și consecința de guvernanță: motorul de decizie NU e o ipoteză testabilă și NU consumă slot de familie.** E o regulă de agregare peste politici deja numărate. **Ce consumă familie e fiecare POLITICĂ pe care o execută** — motorul nu adaugă un test, doar decide dacă unul deja numărat merită executat.

---

## HANDOFF

**VE construiește** în ordinea: (1) formula EV cu trei rezultate + jurnalul complet cu hash-ul tabelei; (2) ierarhia cu `k` estimat prin momente — **`k` se raportează, nu se hardcodează**; (3) criteriul din Partea 5, inclusiv `E[X|h] = −1` la lipsă; (4) `c` ca parametru, niciodată constantă.
**Red Team, ținte explicite:** dacă `EV_LCB` la 80% e o poartă sau o formalitate; dacă `E[X|h] = −1` e într-adevăr cea mai rea valoare posibilă sau doar cea mai rea plauzibilă; și dacă ierarhia poate fi adâncită oportunist după ce se văd rezultatele.
**Alpha:** nimic de schimbat; motorul nu atinge politicile.
**CEO, trei lucruri:** **(1) winrate NU e probabilitatea din EV — la CAND-0001 diferența e 17,5% vs 5,1%, un factor de 3,4**, și cifrele din mandat nu mai există în fișier; **(2) cele trei porți se reduc la una, `EV_LCB > 0`**, singura alegere rămasă fiind nivelul de 80%, declarat ca alegere cu baza ei; **(3) costul rămâne 0,20 până există FILL-uri — 0,05 e o cifră de spread, iar a o folosi ca `c` ar seta tăcut slippage-ul la zero.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.47 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
