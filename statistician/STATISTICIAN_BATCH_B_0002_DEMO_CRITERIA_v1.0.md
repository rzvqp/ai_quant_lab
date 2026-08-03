# STATISTICIAN — CRITERII DEMO: CAND-0002, CAND-0003, CAND-0007 (DEMO_BASELINE)

**Document ID:** STAT-BATCH-B-0002-DEMO-CRITERIA-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `red_team/policy_reviews/RT-OPS-B-0002_batch.md` și secțiunile Part B din `POLICY_COMPRESSION_EXPANSION_v2.md`, `POLICY_FVG_REACTION_v2.md`, `POLICY_LEVEL_FVG_CONFLUENCE_v2.md` (comitul `de31dcc`). **Constrângerea respectată: nu proiectez metoda de risc** — toate trei sunt înghețate. Definesc măsurarea și gardurile pe care motorul trebuie să le impună.

---

## Gardul comun — REUTILIZAT VERBATIM, nu re-derivat

**Convenția există deja și e ratificată: `STAT-CAND0001-DEMO-CRITERIA-v1.0` (v2.7.34).** Se aplică identic, cuvânt cu cuvânt, la toate trei:

```
S1  ierarhia worst-case:  STOP > TIME-STOP > TARGET, în această ordine, la orice bară cu coliziune.
    INVALID_EXECUTION rămâne NARROW — doar ce convenția rezervă (fill nerezolvabil de modelul
    worst-case), niciodată lărgit la coliziuni pe care ierarhia le rezolvă.
    Câmp de audit obligatoriu: intrabar_ordering.
S2  min_executable_risk = max(2×effective_spread, 5×tick_size, 0,10×ATR);
    executable_stop_distance = max(strategy_stop_distance, min_executable_risk);
    sizing 1R calculat pe distanța PODITĂ. effective_spread = REALIZAT pe DEMO, nu presupus.
    Câmpuri: strategy_stop_distance, min_executable_risk, executable_stop_distance, floored(bool).
S3  ținta se scanează STRICT de la entry_idx+1 înainte.
```

**Nu re-derivez nimic din ce e deja fixat.** Mai jos doar accentele per candidat și ce e NOU.

## Cele trei deferite — identice cu CAND-0001, reutilizate

`min_trades = 25` per celulă raportată — **prag de SUPRIMARE a raportării, NU de putere** (puterea cere un test; DEMO nu rulează niciunul). `regimes_permitted = fără filtru` — regimul e retrospectiv, necalculabil live. `Convenția de cost = OBSERVAT, nu modelat` — spread/slippage realizate per fill + reconciliere explicită cu constanta modelată a laboratorului. **Motivul e identic în toate trei cazurile; nu-l repet pe candidat.**

---

# CAND-0002 — Finding H, și o constatare mai gravă decât cea raportată

## Constatarea mea: pe DEMO, time-stop-ul de BLOC nu degenerează în „săptămâni" — degenerează în NICIUN time-stop

**Red Team a încadrat Finding H ca „orizont lung, potențial săptămâni". Verificat mai departe: e mai rău, și dintr-un motiv structural deja stabilit de mine.**

„Blocul" e un **construct de descoperire** — segmentele de regim din manifest (`Block(start,end)`, D3_bis). **Pe un cont DEMO care rulează ÎNAINTE, în timp real, nu există niciun bloc curent și nicio graniță de bloc de atins.** E exact aceeași categorie ca `regimes_permitted` (fixat la v2.7.34) și ca distincția live-vs-metodologic de la v2.7.30: **o etichetă derivată retrospectiv nu e calculabilă înainte.**

**Consecință mecanică:** al treilea termen al regulii „first of: stop · expansiune opusă · graniță de bloc" **nu se declanșează niciodată pe DEMO.** Regula degenerează la „first of: stop · expansiune opusă" — **fără nicio limită de timp.** Un trade fără expansiune opusă rămâne deschis **nedefinit**, nu „până la finalul blocului".

**Nu proiectez înlocuitorul** — un termen nou de orizont ar fi metodă de risc, deci a lui Alpha. **Rutez ca cerere de specificație către Alpha:** Part B al CAND-0002 are nevoie de un termen de orizont **calculabil forward** înainte de a putea tranzacționa pe DEMO. Până atunci, orizontul e nemărginit prin construcție, nu prin accident.

## Regula de orizont — ce impun EU (măsurare), fără a inventa un prag

**Nu aleg un număr de bare** (ar fi un parametru ales, exact ce toată această linie evită). Impun **măsurarea pe scala deja derivată a laboratorului**, reutilizată verbatim:

```
Durata de deținere se raportează per trade, în bare M15, ȘI bucketizată pe constantele DEJA derivate:
   <= 20 bare      (Grupa A, orizontul de reacție imediată, deja stabilit)
   <= 92 bare      (mediana empirică de ZI, deja derivată)
   <= 460 bare     (mediana empirică de SĂPTĂMÂNĂ, deja derivată)
   > 460 bare      (peste o săptămână — raportat separat, niciodată agregat tăcut)
Plus, obligatoriu: numărul de treceri overnight și de weekend per trade; expunerea maximă simultană.
```

**Zero constante noi.** Decizia dacă se impune un plafon rămâne a lui Alpha/CEO, informată de această distribuție — nu pre-decisă de mine.

## S2 la CAND-0002 — imunitate confirmată, dar verificată mecanic, nu presupusă

Red Team are dreptate: bara de expansiune (`range > 1,5×ATR`, corp `>= 0,5×range`) garantează un stop lat, deci podeaua practic nu leagă niciodată. **Dar nu se presupune — se verifică:** câmpul `floored(bool)` se raportează oricum. Dacă podeaua leagă vreodată aici, e un semnal că premisa structurală nu ține și trebuie investigat, nu ignorat.

---

# CAND-0003 — poarta cea mai strânsă, plus două consecințe pe care le adaug

## Consecința 1: podeaua DISTRUGE sensul structural al stopului — exact pe populația unde leagă

**Rațiunea declarată a politicii pentru stop:** „falsificarea structurală ratificată e o mișcare decisivă prin marginea îndepărtată — chiar granița a cărei închidere-dincolo definește inversarea FVG (Q4)." **Stopul are un SENS: e granița de inversare.**

**Când podeaua `min_executable_risk` leagă (gol mic — cazul de RUTINĂ, nu excepția), stopul se lărgește DINCOLO de marginea îndepărtată.** Nu mai e la granița de inversare — e la o distanță arbitrară dincolo de ea. **Aplicarea podelei nu doar ajustează dimensiunea poziției: schimbă ce ÎNSEAMNĂ stopul.** Rațiunea structurală a politicii nu mai ține pentru acele tranzacții.

**Nu e un defect de politică și nu-l repar** (ar fi redesign de risc). **Îl declar și îl rutez către Alpha/CEO ca observație**, pentru că schimbă interpretarea rezultatelor, nu doar execuția.

## Consecința 2: podeaua + ținta fixă = R:R care se prăbușește sistematic, exact acolo

**Aritmetic, derivat, nu presupus.** Intrarea = `ce_50` (mijloc), deci:
```
distanța la stop  = (upper − lower)/2 = jumătate din înălțimea golului
distanța la țintă = (upper − lower)/2 = ACEEAȘI  →  R:R ≈ 1 (consecință geometrică, nu aleasă)
```
**Dar podeaua lărgește DOAR stopul, nu și ținta** (ținta rămâne marginea apropiată, o coordonată structurală fixă). Deci pe golurile mici:
```
risc  = min_executable_risk  (PODIT, mai mare)
câștig = jumătate din înălțimea golului  (NESCHIMBAT, mic)
→ R:R << 1, SISTEMATIC, pe exact subpopulația unde podeaua leagă
```

**Cu cât golul e mai mic, cu atât R:R e mai prost** — și golurile mici sunt tocmai cazul de rutină pe care Red Team l-a semnalat. **Cerință obligatorie: tranzacțiile PODITE și cele NEPODITE se raportează SEPARAT**, cu R:R realizat per grup. A le agrega ar ascunde o subpopulație structural diferită și sistematic dezavantajată sub o medie unică.

## Consecința 3: fracția rezolvată de S1 e un INDICATOR DE VALIDITATE, nu doar un câmp de audit

**Red Team spune că S1 e acut aici: o singură bară acoperă de regulă ambele margini ale aceluiași gol.** Consecința pe care o adaug: **cu cât mai multe tranzacții sunt rezolvate de ierarhia worst-case, cu atât mai mult rezultatul măsoară CONVENȚIA MEA, nu comportamentul pieței.**

```
Obligatoriu, raportate una lângă alta:
  fracția de tranzacții rezolvate NEAMBIGUU (doar stop, SAU doar țintă, pe bare diferite)
  fracția de tranzacții rezolvate PRIN IERARHIA S1 (ambele atinse pe aceeași bară → STOP prin convenție)
```

**Nu fixez un prag numeric** (ar fi un parametru ales). Impun regula de interpretare: **dacă fracția rezolvată prin S1 e comparabilă cu sau mai mare decât cea neambiguă, rezultatul DEMO al CAND-0003 e determinat în majoritate de o convenție de tie-break, nu de piață — și trebuie citit ca atare, explicit, nu ca dovadă despre mecanism.** Convenția worst-case e corectă și conservatoare; dar un rezultat dominat de ea nu spune aproape nimic despre ipoteză.

## Poarta Red Team pentru CAND-0003 — păstrată VERBATIM

> **„Dacă motorul DEMO nu poate fi arătat că aplică podeaua + convenția worst-case, CAND-0003 NU trebuie să tranzacționeze"** — golurile mici fac din ambele defecte cazul comun, nu coada.

---

# CAND-0007 — raportul risc/câștig, și extinderea W-incr la risc

## R:R < 1 — calculabil LA INTRARE, deci măsurabil per trade, nu doar constatabil retrospectiv

**Constatare utilă: atât stopul combinat (`min(low[touch_idx], FVG.lower)`) cât și ținta (`PDH`/`PDL`) sunt cunoscute LA INTRARE.** Deci raportul risc/câștig e **calculabil înainte de a intra**, nu doar după.

```
Obligatoriu, per trade, ca un câmp declarat la intrare:
  planned_RR = |target − entry| / executable_stop_distance   (pe distanța PODITĂ, nu cea brută)
Agregat: distribuția lui planned_RR + fracția de tranzacții cu planned_RR < 1.
```

**NU impun un filtru „fără trade dacă R:R<1"** — ar fi o condiție de intrare nouă, deci metodă de risc, deci a lui Alpha. **Măsor și rutez.** Dacă fracția sub 1 e materială, Alpha/CEO au baza factuală pentru a decide un filtru; eu nu o pre-decid.

**Simetria cu CAND-0003, notată explicit:** la CAND-0003 podeaua strică R:R prin lărgirea stopului; la CAND-0007 R:R poate fi sub 1 prin construcție (stop lat + țintă la nivelul opus). **Cauze diferite, aceeași consecință măsurabilă** — de aceea ambele raportează `planned_RR` în același format, comparabil.

## S2 la CAND-0007 — protejat, dar verificat

Stopul combinat e cel mai adânc dintre două praguri ⇒ mai lat ⇒ podeaua rar leagă. **Confirmat ca proprietate structurală, dar `floored(bool)` se raportează oricum** — dacă leagă, premisa nu ține.

## Extinderea W-incr la stratul de RISC — semnalat de Red Team, îl bind aici

Part B al CAND-0007 folosește **ieșirea CAND-0001** (nivelul opus) iar zona lui de intrare e **⊂ CAND-0003**. **Deci testul W-incr deja specificat la STAT-BATCH-A-0001 (valoare incrementală față de constituenți, pe barele identice) trebuie să acopere ACUM și riscul, nu doar intrarea** — altfel „confluența adaugă valoare" s-ar putea datora exclusiv stopului mai lat, nu confluenței. **Precizare adăugată la protocolul existent, nu un protocol nou.**

---

## Regula de raportare — identică, neschimbată

**DEMO NU E VALIDARE STATISTICĂ.** Zero p-value, zero H0, zero familie consumată — deși cei trei candidați FAC parte din familia de 7 pentru testele formale viitoare, **DEMO nu consumă din ea, pentru că nu rulează niciun test.** Niciun rezultat DEMO nu promovează nimic; o cifră pozitivă **nu e nici măcar un candidat care cere pre-înregistrare** — e neconcludentă prin construcție.

## HANDOFF

**Validation Engine** — executabilitate + verificarea mecanică a gardurilor, per candidat, cu câmpurile de audit numite mai sus.
**Alpha / CEO** — trei rutări, niciuna decisă de mine: (1) termenul de orizont forward-calculabil pentru CAND-0002; (2) observația că podeaua schimbă sensul structural al stopului la CAND-0003; (3) dacă un filtru R:R e dorit la CAND-0007.

---

## Notă separată — protocoalele CAND-0008/0009/0010 sunt DEJA livrate

Mandatul le cere „când ai capacitate". **Sunt deja publicate**, turul trecut: `STATISTICIAN_BATCH_A_0002_PARTITION_AND_PROTOCOLS_v1.0.md` (manifest v2.7.35) — inclusiv decizia W-partition, W-incr pe CAND-0010 și W-dir-mask. **Nu le refac.** CAND-0011…0019 așteaptă Faza A la Red Team — nu sunt încă în declanșatorul meu.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.36 (commit `40bc63f`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
