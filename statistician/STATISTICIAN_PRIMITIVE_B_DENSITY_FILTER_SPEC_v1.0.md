# STATISTICIAN — FILTRUL DE DENSITATE PENTRU PRIMITIVA B (niveluri de sesiune persistente)

**Document ID:** STAT-PRIMITIVE-B-DENSITY-FILTER-SPEC-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `code/session_levels.py` (`compute_persistent_session_levels`, `detect_session_level_touches`, `detect_session_mid_touches`, `count_active_persistent_levels`). **Măsurătoarea de referință a Red Team e reprodusă independent de mine: median 89, max 188 active** — deci filtrul de mai jos se aplică exact aceluiași obiect, nu altuia.

---

# PARTEA 1 — DE CE „CELE MAI APROPIATE N" E GREȘIT, ÎNAINTE DE ORICE MĂSURĂTOARE

**Verdictul Red Team conține DOUĂ acuzații distincte, iar ele cer remedii diferite:**

```
(1) DENSITATE   „89-188 niveluri active" — setul e prea mare ca să fie decidabil.
(2) FALSIFICABILITATE  „prețul e mereu lângă vreun nivel ⇒ NEFALSIFICABIL prin saturație."
```

**Un filtru de tip RANG (cele mai apropiate N, cele mai recente N) rezolvă (1) și NU rezolvă (2) — îl agravează.** Motivul e derivabil fără date: **un filtru de rang returnează ÎNTOTDEAUNA N niveluri.** Dacă iei mereu cele mai apropiate 5, atunci prin construcție prețul e mereu lângă 5 niveluri. Saturația nu dispare — devine invizibilă, fixată la N.

> **Criteriul care decide forma filtrului: filtrul trebuie să poată returna MULȚIMEA VIDĂ.** Doar un **PRAG** (nivelurile aflate în interiorul unei distanțe) poate face asta; un **RANG** nu poate, niciodată. Iar mulțimea vidă e exact ce cere falsificabilitatea: trebuie să existe bare unde afirmația „prețul reacționează la un nivel" **nu are ce să prezică**.

**Deci: prag de distanță, nu număr fix.** Vechimea a fost respinsă ca filtru PRIMAR dintr-un motiv separat: o limită de vechime scurtă ar transforma B în A (B există tocmai ca nivelurile vechi să persiste), iar una lungă n-ar mărgini nimic. **Distanța păstrează premisa lui B** — un nivel vechi și îndepărtat e irelevant ACUM, dar redevine eligibil dacă prețul se întoarce la el.

---

# PARTEA 2 — FILTRUL, FIXAT ÎNAINTE DE MĂSURĂTOARE

```
ELIGIBILITATE la bara j — un nivel lv e eligibil dacă TOATE:
  lv.available_idx < j                      (deja cerut de primitivă)
  lv neatins încă                            (deja cerut — D7)
  |lv.price − close[j−1]| <= k × ATR14[j−1]  ← FILTRUL

  k PRIMAR      = 1,0
  k SENSIBILITATE = {0,5 ; 2,0}   — declarate ÎN AVANS, nu alese ulterior
```

**`k=1,0` nu e o cifră inventată pentru ocazie: e unitatea de risc proprie a laboratorului** — distanța de stop folosită în toată linia DEMO (`SL = 1,0×ATR`, OBDZ-002 și cei patru piloți). Un nivel aflat în interiorul unui `1×ATR` e la mai puțin de o unitate de risc de preț, deci **realmente accesibil în cadrul propriului orizont al tranzacției**. Ancoră reutilizată, nu nouă.

## Demonstrația de absență a lookahead-ului

```
Filtrul citește la bara j EXCLUSIV:  close[j−1]  și  ATR14[j−1]
Ambele sunt complete ÎNAINTE ca bara j să se deschidă.
Nivelul însuși cere deja  available_idx < j  (fără lookahead prin primitivă).
⇒ mulțimea eligibilă la bara j e integral cunoscută înainte de bara j. Zero informație viitoare.
```

**Deliberat NU `close[j]`:** ar folosi bara care se evaluează. Decalajul de o bară e ce face filtrul executabil live, nu doar în backtest.

## Pragul de eficacitate — DERIVAT din baza măsurată, fixat înainte

```
median activ  <=  9    (ordin de mărime sub medianul măsurat de 89)
max activ     <= 19    (ordin de mărime sub maximul măsurat de 188)
fracția barelor cu ZERO eligibile  > 0, raportată  — condiția de falsificabilitate
```

**Ancora „un ordin de mărime sub baza măsurată" e derivată din cifra existentă, nu aleasă.** Fracția de zero nu primește un prag numeric inventat — primește o **regulă de interpretare**: dacă e ~0, saturația persistă indiferent de numărul de active.

---

# PARTEA 3 — MĂSURAT, NU ESTIMAT

**Măsurat de mine direct pe descoperire (130.491 bare, 3 regimuri), script temporar, necomis, șters.** Baza nefiltrată reproduce Red Team exact.

```
                 median   mean   p90   max   bare cu ZERO eligibile   atingeri păstrate
NEFILTRAT          89      94     —    188            0,0%            16.578  (100%)
k = 0,5             0     0,05     0     4           95,3%             3.932  (23,7%)
k = 1,0 ★           0     0,19     1     6           83,6%             8.833  (53,3%)
k = 2,0             0     0,74     2    12           50,4%            13.874  (83,7%)
```

## Verdict pe pragul pre-declarat

**`k=1,0` TRECE, comod: median 0 ≤ 9, max 6 ≤ 19, zero-fracție 83,6% > 0.** Reducere de **31×** la maxim (188 → 6).

**Consemnez explicit: valoarea PRIMARĂ pre-declarată a trecut. Nu a existat nicio re-alegere după ce am văzut cifrele** — exact disciplina cerută. `k=0,5` și `k=2,0` rămân ce au fost declarate: verificări de sensibilitate, nu candidate la promovare.

## Falsificabilitatea, cuantificată — de la 0% la 83,6%

**Nefiltrat: 0,0% din bare au zero niveluri eligibile.** Prețul e literalmente ÎNTOTDEAUNA lângă un nivel — exact acuzația Red Team, confirmată numeric.
**La `k=1,0`: 83,6%.** Pe 5 din 6 bare **nu există niciun nivel în joc**, deci afirmația „prețul reacționează la nivel" **poate acum să eșueze**. Saturația e rezolvată, măsurat.

## Filtrul NU distruge populația — și motivul e structural

**53,3% din atingeri sunt păstrate la `k=1,0`, deși densitatea scade de 31×.** Nu e o coincidență: **un nivel pe cale să fie atins e, prin construcție, deja aproape de preț** — deci trece filtrul exact în momentul în care contează. **Filtrul elimină nivelurile îndepărtate, care oricum nu urmau să fie atinse — adică exact diluția.** Asta e proprietatea care face un filtru de proximitate potrivit aici, iar acum e măsurată, nu presupusă.

---

# PARTEA 4 — CE NU REZOLVĂ FILTRUL. Spun asta explicit, ca să nu fie citit greșit.

**8.833 de atingeri rămân după filtrare. Asta e ACELAȘI ORDIN DE MĂRIME cu cele trei eșecuri citate:**

```
DZ × FVG     18.275 tranzacții   −2.432 $
CAND-0020    34.006 tranzacții   −15.409 R
CAND-0024    18.852 tranzacții   −2.605 R
B filtrat     8.833 atingeri     ← pool BRUT, înainte de orice direcție/bias/confluență
```

> **Filtrul rezolvă SATURAȚIA și FALSIFICABILITATEA — cele două lucruri pe care Red Team le-a cerut. NU rezolvă VOLUMUL.** Un candidat construit pe B filtrat **rămâne expus tiparului „prea multe zone"** și trebuie să-și adauge propria selectivitate, raportată separat.

**Cerință obligatorie, derivată din acest număr:** orice candidat pe B **raportează numărul final de declanșări ÎNAINTE de a raporta orice rezultat de performanță.** Cele trei eșecuri au fost descoperite abia după ce volumul fusese deja generat.

# PARTEA 5 — DOUĂ INTERDICȚII, respectate explicit

**1. Filtrul nu compensează D2 și nicio altă restricție.** E strict o reducere de densitate pe axa distanței. D2 (egalitățile nu produc swing) rămâne exact ce e: o restricție interpretativă permanentă, necompensată și necircumventată aici. Filtrul nu atinge nici D7, nici F4, nici granițele D3_bis.

**2. Pragul nu a fost ales după rezultate.** `k` și pragul de eficacitate au fost fixate înainte de măsurătoare; pragul derivă din baza deja publicată (89/188), nu din ce a ieșit. **Și, decisiv pentru integritatea acestei calibrări: măsurătoarea de mai sus e ORBITĂ LA P&L — conține exclusiv numărători de niveluri și atingeri, niciun rezultat de performanță.** Calibrarea unui filtru pe DENSITATE e scopul lui declarat; calibrarea pe REZULTATE ar fi fost exact abuzul de evitat. **Măsurătoarea de densitate nu poate deveni o portiță de tuning pentru că nu conține nicio cifră de performanță.**

---

## HANDOFF

**VE** implementează filtrul (o singură condiție de eligibilitate, pe `close[j−1]`/`ATR14[j−1]`) și **reverifică independent** tabelul din Partea 3 — cifrele mele sunt reproductibile prin construcție, dar verificarea independentă rămâne regula. **Dacă reverificarea confirmă pragul, Alpha poate construi pe B — cu selectivitatea proprie și cu numărul de declanșări raportat ÎNAINTE de performanță (Partea 4).** Red Team atacă filtrul, cu ținta explicită: forma prag-vs-rang (Partea 1) și decalajul de o bară (Partea 2).

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
