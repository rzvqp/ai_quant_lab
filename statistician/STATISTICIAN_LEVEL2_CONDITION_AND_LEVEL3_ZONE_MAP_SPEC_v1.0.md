# STATISTICIAN — CONDIȚIA B-L1, VERIFICAREA GĂURII L-R1, ȘI NIVELUL 3

**Document ID:** STAT-L2-CONDITION-AND-L3-ZONE-MAP-SPEC-v1.0
**Data:** 2026-08-10 · **Autor:** Statistician

**Verificare de sursă:** citit direct `code/bias_h1.py` (`81a0a62`), `ai_trader/zone_observer/{types,observer}.py`, `code/session_levels.py`, `code/imbalance_mechanics.py`. **Trei măsurători proprii, P&L-oarbe.** **Cifra corectată e mai rea decât cea raportată, iar la nivelul 3 măsurătoarea desființează întrebarea despre ponderi.**

---

# PARTEA 1 — B-L1: METRICA, RECALCULATĂ CAUZAL

## Cifra corectă, și e sub ce s-a raportat

```
                                        RAPORTAT (contaminat)    CAUZAL
zero_eligible_fraction                        99,21%             72,78%
contor eligibil: median / p90 / max            0 / 0 / 4         0 / 1 / 5
```

**Supraevaluarea e de 26,4 puncte, nu de ~19 cum s-a estimat.** Cauza, verificată: **96,9% dintre bazinele ABOVE sunt măturate LA UN MOMENT DAT** (6.543 din 6.755). Rezolvând „neconsumat" pe toată fereastra, metrica excludea la bara 300 un bazin măturat abia la bara 500 — deci excludea aproape tot, ceea ce e exact motivul pentru care cifra arăta atât de curată.

**Confirm ce s-a transmis: factorul EMIS e curat.** El se evaluează la ultima bară închisă, unde „măturat până la sfârșitul ferestrei" și „măturat până la bara curentă" coincid. Contaminarea atinge exclusiv bucla istorică peste `j < last`, adică metrica-justificare.

## Și consemnez că ambiguitatea din criteriu e a mea

**Am scris: „fracția trebuie să fie MATERIAL peste zero. Referință: primitiva B a ajuns la 83,6%."** Un criteriu calitativ lângă o cifră — iar VE a citit cifra ca prag și a scris `assert >= 0.836`. **Lectura lui e rezonabilă; formularea mea a permis-o. Ambiguitatea e a mea, nu a lui.**

```
CRITERIUL, REFORMULAT NUMERIC (înlocuiește §7.2 din spec-ul nivelului 2):
  fracția cauzală a barelor cu ZERO bazine eligibile >= 50%.
  Bază: sub 50%, majoritatea barelor au lichiditate eligibilă, deci afirmația „există lichiditate
  deasupra" e adevărată mai des decât falsă și nu mai separă nimic. Pragul e derivat din ce
  înseamnă ca un predicat să fie informativ, nu dintr-un precedent.
  Cei 83,6% ai primitivei B rămân PUNCT DE COMPARAȚIE, explicit NU prag.

VERDICT: 72,78% >= 50% ⇒ criteriul TRECE cauzal.
         Sub referința primitivei B (83,6%) ⇒ factorul de la nivelul 2 e MAI PUȚIN falsificabil
         decât primitiva B. Se consemnează ca atare, nu se ascunde.
```

**Testul VE se corectează în consecință: aserțiunea pe 0,836 se înlocuiește cu 0,50, iar bucla istorică se rescrie cauzal.** Fără asta, testul măsoară altceva decât criteriul.

---

# PARTEA 2 — GAURA L-R1, VERIFICATĂ

**Am căutat mecanismul de inspecție statică în toate cele trei repozitorii de cod.**

```
redundancy_by_static_inspection / _called_primitives / redundant_with
  code/bias_h1.py            implementare (nivelul 2)
  tests/test_bias_h1.py      testele ei
  config/generate_split_manifest.py   DOAR text descriptiv, nu cod executabil
```

> **Verdict: mecanismul NU e implementat nicăieri altundeva. Gaura e LATENTĂ, nu activă — nimic altceva nu e greșit acum.**

**Dar ce o poartă nu e codul, e SPECIFICAȚIA.** L-R1 spune „inspecție statică a apelurilor", iar orice implementator care citește doar atât va scrie versiunea intra-funcție și va rata exact aceleași muchii. **Se amendează L-R1, nu codul:**

```
AMENDAMENT LA L-R1: inspecția statică are DOUĂ tiere, ambele obligatorii.
  DIRECT   primitiva e apelată ÎN interiorul funcției de declanșator.
  INJECTAT primitiva e apelată în MODUL și rezultatul e PASAT ca parametru.
           Cazul real: `gen_cand0002` primește `exp`, iar `expansion()` e apelat de runner.
           Tier-ul intra-funcție e ORB la muchia asta.
Un raport care conține doar tier-ul DIRECT e INCOMPLET și se respinge ca atare.
```

**Și a doua parte a amendamentului, din aceeași construcție:** vocabularul se restrânge mecanic la **FUNCȚIILE** modulelor ratificate. Fără asta, `float`, `len` și `Block` apar drept primitive partajate — avertismente adevărate și vide, care diluează exact semnalul pe care L-R1 îl cere.

---

# PARTEA 3 — NIVELUL 3: HARTA OPERAȚIONALĂ PE M15

## 3.1 Ce există: un OBSERVATOR, nu un scor

**Verificat în `ai_trader/zone_observer/`: nu există scor, ponderi, prag sau ordonare. Modulul înregistrează FORMAREA și ATINGEREA zonelor** (`SESSION_LEVEL_FORMED/TOUCH`, `DEMAND_ZONE_FORMED`, `INVERSE_FVG_FORMED`, `BPR_COUNT`, `WEEKLY_LEVEL_FORMED`), cu docstring-ul propriu: „Doar observare, fără politici."

> **Deci nu e un scor descriptiv construit în afara protocolului — e INTRAREA nivelului 3, construită corect ca observație pură.** Nimic de reconciliat, nimic de înlocuit. **Dar nici nu există un prototip din care să se moștenească ponderi.**

## 3.2 Ponderile NU se pot deriva la nivelul 3 — și motivul e structural

**A deriva ponderi înseamnă a le potrivi pe un REZULTAT. A potrivi pe rezultat înseamnă a ESTIMA. Iar estimarea e nivelul 6.**

```
Ponderi derivate la nivelul 3 ⇒ al DOILEA estimator pe aceleași date  (respins deja la nivelul 2)
                              ⇒ ȘI o problemă de selecție: ponderile ar fi alese pe exact datele
                                pe care candidatul se testează ulterior.
```

**Formatul cerut de CEO conține deja răspunsul: „5/6" e un CONTOR NEPONDERAT.** Cele două cifre din exemplu — „93" și „5/6" — sunt lucruri diferite, iar a doua e singura disponibilă fără estimare.

**DECIZIE, identică celei de la nivelul 2: nivelul 3 emite SETUL DE TRĂSĂTURI și CONTORUL, plus ordonarea. Cifra de „confidence" vine de la nivelul 6, condiționată pe celula de confluență.** Un singur estimator.

## 3.3 Pragul: derivabil — dar măsurătoarea arată că întrebarea era pusă pe axa greșită

**Măsurat pe descoperire M15, 25.800 de bare eșantionate, proximitate 1×ATR, patru trăsături ratificate (PDH/PDL, FVG, lichiditate, discount):**

```
contorul de confluență      k=4  42,82%    k=3  52,05%    k=2  4,76%    k=1  0,30%    k=0  0,07%
bare FĂRĂ nicio zonă calificată:
   prag k>=1   0,07%      prag k>=2   0,38%      prag k>=3   5,13%      prag k>=4  57,18%
```

> **La 1×ATR, trei din patru trăsături coincid pe 94,87% dintre bare. Harta e SATURATĂ la orice prag sub 4.** Doar cerința TOTALĂ (k≥4) lasă un complement material: 57,18% din bare fără nicio zonă calificată.

**Consecința care contează: problema nu e cum se ponderează trăsăturile, ci că la 1×ATR aproape totul e confluent. Un contor aproape constant nu poate ordona nimic, indiferent de ponderi.** E a treia oară când aceeași patologie apare — primitiva B (89-188 niveluri), bazinele de la nivelul 2 (474), acum confluența M15.

```
PRAGUL, DERIVAT: k >= 4 (confluență TOTALĂ), pentru că e singurul care satisface falsificabilitatea
                 (57,18% >= 50%, criteriul reformulat în Partea 1).
DAR derivarea corectă e COMUNĂ pe (bandă, k), nu pe k singur: banda de proximitate saturează
    contorul înainte ca pragul să apuce să conteze. Banda intră în `schema_hash` alături de k.
```

## 3.4 „Discount/Premium": se DEFINEȘTE, din primitivă ratificată

**Nu cere primitivă nouă. `session_levels.py` emite deja `SESSION_MID`, ratificat, cu propria convenție de disponibilitate și expirare.**

```
DISCOUNT[i]  ⇔  close[i-1] < price(SESSION_MID al sesiunii ANTERIOARE, încă neexpirat)
PREMIUM[i]   ⇔  close[i-1] > acel Mid
NEDEFINIT    dacă niciun Mid viu ⇒ trăsătura e UNAVAILABLE, nu FALSE
```

**Referința e SESIUNEA, nu ziua sau săptămâna: nivelul 3 e harta operațională pe M15, iar sesiunea e cea mai scurtă perioadă ratificată care are un Mid.** Comparația preț-vs-Mid e aritmetică, nu un detector nou — deci nicio ratificare suplimentară.

**Avertisment atașat imediat, nu după:** `SESSION_MID` e primitiva pe care declanșează CAND-0028 și CAND-0033. **Pentru ei, `DISCOUNT` nu e context independent.**

## 3.5 Cele trei moșteniri

```
1. CONSTANTE: nimic de re-derivat — ZI 92 și SĂPTĂMÂNĂ 460 SUNT constantele M15, derivate acolo.
   Consemnez explicit ca să nu se producă o supra-corecție: 460 a fost transplant pe H4,
   NU pe M15. Pe timeframe-ul propriu e corect.
2. schema_hash: lista ORDONATĂ a trăsăturilor, primitiva fiecăreia, BANDA de proximitate, pragul k,
   ferestrele și versiunea codului. Pre-înregistrate înainte de prima decizie, append-only.
3. REDUNDANȚĂ, verificată ÎNAINTE: PDH/PDL ← institutional_levels; FVG ← imbalance_mechanics;
   lichiditate ← build_pools←swings; discount ← session_levels. TOATE au declanșatori care le
   folosesc. Ca la nivelul 2, ZERO trăsături complet independente; ȘTIRILE rămân singura axă
   independentă din sistem. Se atașează prin inspecția cu DOUĂ tiere (Partea 2).
```

## 3.6 Intrări, ieșiri, fail-closed, acceptare

```
INPUT   zonele din `zone_observer` (observație pură) + RegimeState (n1) + BiasState (n2)
OUTPUT  ZoneMap { zones: [{id, features[], k, feature_status[], redundant_with[]}], ranked_by_k,
                  threshold_k, band_atr, status }
        NU emite „confidence". Aceea vine de la nivelul 6, condiționată pe celula de confluență.

FAIL-CLOSED  fereastră incompletă → UNAVAILABLE, nu k=0. Mid absent → trăsătura UNAVAILABLE,
             nu FALSE. Nivel 1 sau 2 UNAVAILABLE → cascadă. Nicio zonă peste prag → mulțime VIDĂ
             (rezultat valid, nu eroare) ⇒ nu se caută intrare.

ACCEPTARE 1. zero lookahead: trăsăturile la i citesc doar bare <= i-1; test prin perturbare pe TOT setul.
          2. falsificabilitate: fracția barelor fără zonă calificată >= 50%, CAUZAL calculată.
          3. neredundanță: acordul fiecărei trăsături cu nivelele 1-2, raportat; >~95% ⇒ retragere.
          4. dezvăluire: `redundant_with[]` prin inspecția cu două tiere.
          5. constante: doar unități M15.
          6. proprietate: ∀ bară cu ZoneMap UNAVAILABLE sau mulțime vidă ⇒ nivelul 6 == NO_TRADE.
```

---

## HANDOFF

**VE:** (1) rescrie cauzal bucla din `zero_eligible_fraction` și înlocuiește aserțiunea 0,836 cu 0,50; (2) extinde inspecția la două tiere ORIUNDE e folosită; (3) construiește nivelul 3 după §3.6.
**Red Team, ținte:** dacă pragul de 50% e derivat sau tot ales; dacă „confluență totală" mai e o hartă sau doar un filtru; și dacă banda de 1×ATR, reutilizată a treia oară, mai e o ancoră sau a devenit un obicei.
**CEO, patru lucruri:** **(1) cifra cauzală e 72,78%, nu ~80% — supraevaluarea era de 26 de puncte; criteriul trece la pragul reformulat de 50%, dar factorul e mai puțin falsificabil decât primitiva B, și o consemnez. (2) Ambiguitatea care a permis eroarea de lectură a testului e a mea; criteriul e acum numeric. (3) Gaura L-R1 e latentă — mecanismul nu e implementat nicăieri altundeva — dar am amendat specificația, fiindcă ea o poartă, nu codul. (4) La nivelul 3, ponderile NU se pot deriva fără a construi al doilea estimator — iar măsurătoarea arată că întrebarea era oricum pe axa greșită: la 1×ATR, trei din patru trăsături coincid pe 94,87% din bare, deci contorul e aproape constant și nicio pondere nu l-ar putea salva. Pragul derivat e confluența TOTALĂ.**

**Restanța mea rămâne CAND-0012, 0017, 0019 — după nivelul 3, cum s-a stabilit.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.52 (`alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent, pytest 139/143 (aceleași 4 eșecuri pre-existente).**
