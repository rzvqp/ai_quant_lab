# SPEC 1 — N3: HARTA OPERAȚIONALĂ. CORECȚIE FUNCȚIONALĂ

**Document ID:** STAT-SPEC1-N3-ZONE-MAP-CORRECTION-v1.0 · **Data:** 2026-08-11 · **Autor:** Statistician
**Obiectiv mărginit:** zone economice persistente + ranking real, fără saturația actuală. **Atât.**
**Verificare de sursă:** citit `zone_map.py`, `order_flow.py`, `order_block_void.py`, `imbalance_mechanics.py`. Măsurătoare nouă, P&L-oarbă, cu NUL.

---

## 1. CAUZA RĂDĂCINĂ: ancora, nu banda

```python
ref = float(close[i - 1])      # zone_map.py — zona e ancorată PE PREȚ
```

> **N3 întreabă „câte trăsături sunt lângă PREȚ". Răspunsul e mereu „toate", pentru că prețul e mereu unde e. De aici vin AMÂNDOUĂ defectele: saturația (contorul nu variază) ȘI absența ordonării (o singură zonă per bară, deci nimic de ordonat). Nu sunt două probleme — e una.**

**Corecția: ancora zonei se mută pe GRUPUL DE TRĂSĂTURI. Prețul ajunge la zonă; zona nu urmărește prețul.**

## 2. (a) BANDA DE CONFLUENȚĂ — măsurată, și rezultatul e NEGATIV

**Zone ancorate pe trăsături, `k` = numărul de TIPURI distincte în grup. NUL = log-randamente amestecate, geometria barei păstrată.**

```
 bandă   zone/bară    k>=2 REAL   k>=2 NUL   REAL−NUL   k VARIAZĂ între zone
  0,05      79,30       90,74%     89,71%    +1,02p          99,9%
  0,10      43,67       95,47%     95,06%    +0,41p         100,0%
  0,25      19,00       98,18%     98,03%    +0,15p          91,8%
  0,50       9,78       99,14%     99,00%    +0,13p          56,8%
  1,00       4,95       99,61%     99,44%    +0,16p          23,9%
```

> **NU EXISTĂ o bandă la care contorul de confluență discriminează. Diferența față de nul e +0,15…+1,02 puncte peste tot. Cerința (a) e MĂSURATĂ ȘI RAPORTATĂ CA EȘEC — a treia oară același rezultat, acum și cu ancorare corectată. Contorul e o proprietate a DENSITĂȚII, nu a pieței.**

**Dar ancorarea pe trăsături livrează totuși ce contorul nu putea: `k` VARIAZĂ între zone la aceeași bară (91,8% la 0,25×ATR). Ordonarea EXISTĂ. Doar că nu e demonstrabil informativă, deci `k` intră ca descriptor, NU ca scor.**

## 3. (b) SELECȚIA PRIMITIVELOR — coliniaritatea e dovedită ÎN COD

```
DemandZone   `detect_demand_zones` ITEREAZĂ peste `detect_order_blocks`; aceeași bară-ancoră,
             zona = [Low,High] în loc de corp. Superset geometric STRICT. COLINIAR cu OB.
Breaker      același corp de OB, polaritate inversată, la bara de flip. ACEEAȘI LOCAȚIE.
IFVG         aceeași zonă ca FVG-ul sursă, polaritate inversată. ACEEAȘI LOCAȚIE.
BPR          `count_bpr` întoarce NUMĂRĂTORI, nu instanțe localizate. Fără localizator,
             nu poate fi componentă. Un localizator ar fi PRIMITIVĂ NOUĂ → EXCLUS prin regula de scop.
discount/    NU e o locație. E un atribut al poziției prețului față de Mid.
premium      Rămâne, dar ca ATRIBUT al zonei, nu ca membru al contorului.
PWH/PWL      EXCLUS prin decizie CEO.
```

> **Mulțimea de componente NU crește: din cele opt candidate, trei sunt coliniare cu una deja înăuntru, una n-are localizator, una nu e locație, una e exclusă. Dar mulțimea SE SCHIMBĂ.**

```
COMPONENTE (numără în k), patru familii NECOLINIARE:
    level      PDH/PDL                 compute_prior_day_levels
    fvg        FVG ∪ IFVG              detect_fvgs, detect_inverse_fvgs   (o familie)
    pool       lichiditate             build_pools
    ob         OB ∪ DemandZone ∪ Breaker  detect_order_blocks, ...        (o familie)
ATRIBUTE (nu numără în k):  discount/premium, tip, vechime, distanță
IEȘIRE: `discount` din contor (nu e locație).  INTRARE: familia `ob` (era absentă).
```

**Regula anti-recidivă, mecanică: două primitive sunt în ACEEAȘI familie dacă una o apelează pe cealaltă în sursă. Se reutilizează `redundancy_by_static_inspection` din `bias_h1.py` — instrument existent, nu unul nou.**

## 4. (c) ORDONAREA — din axe cauzale care există DOAR după re-ancorare

**Măsurat, bandă 0,25×ATR, date reale:**

```
distanța până la zonă (×ATR)   p10 0,51   mediană 2,55   p90 4,66     ← continuă, larg răspândită
vechimea zonei (bare M15)      p10 3      mediană 45     p90 1.284    ← continuă, larg răspândită
```

> **Sub ancorarea pe preț, distanța e identic ~0 — axa nu EXISTĂ. Re-ancorarea o creează. Asta răspunde la decizia E1: o ordonare reală E posibilă, dar NU din contorul de confluență.**

**Ieșirea lui N3, per zonă:**

```
zone_id            cheia din STAT-OPPORTUNITY-IDENTITY-SPEC (ancoră+bandă înghețate, ciclu D7)
price_anchor       media prețurilor instanțelor din grup           ← ancora, nu prețul curent
band               banda de confluență × ATR la creare, ÎNGHEȚATĂ
composition        tipurile prezente + numărul de instanțe per tip
k                  contorul — DESCRIPTOR, cu eticheta „ne-discriminant vs nul"
distance_atr       |price_anchor − close[j-1]| / ATR                ← axă de ordonare
age_bars           j − max(available_idx din grup)                  ← axă de ordonare
attributes         discount/premium, dacă Mid viu; altfel UNAVAILABLE
relative_rank      poziția în ordonarea la bara j (1 = primul)
evidence_available bool — dacă N4 a atașat descriptor (SPEC 2)
status / reason    contractul LevelOutput
expiry             ieșirea din bandă sau consumarea D7
```

**`relative_rank` se calculează pe o cheie de sortare PRE-ÎNREGISTRATĂ în `schema_hash`: `(distance_atr ASC, age_bars DESC, k DESC)`. Ordinea e ARHITECTURALĂ — proximitatea e acționabilitate, vechimea e persistență netestată, contorul e ultimul fiindcă e cel mai slab. NU se acordează pe rezultate; fiind fixată de structură, nu poate fi acordată.**

## 5. CE RĂMÂNE DESCHIS

```
BLOCKING      re-ancorarea pe trăsături. Fără ea nu există eveniment „prețul intră în zonă",
              deci SPEC 2 n-are ce observa și milestone-ul e de neatins.
MATERIAL      banda de confluență: NICIUNA nu discriminează. Se alege 0,25×ATR fiindcă acolo
              `k` variază între zone în 91,8% din cazuri, iar numărul de zone (19/bară) e
              tractabil. Ales pe TRACTABILITATE ȘI VARIABILITATE, nu pe informativitate —
              și o spun, fiindcă nu e derivare.
LIMITATION    `k` rămâne ne-discriminant față de nul. Se emite ca descriptor etichetat, nu ca
              scor. Nu se raportează niciodată drept „harta aduce informație".
LIMITATION    ordonarea după distanță/vechime e CAUZALĂ și OBSERVABILĂ, dar NEVALIDATĂ ca
              predictivă. E o ordonare reală, nu o ordonare demonstrat utilă.
NON-MATERIAL  BPR — ar cere un localizator nou. Amânat, nu necesar pentru milestone.
NON-MATERIAL  ZM-L1 în sensul original (banda măsura la preț) e ÎNCHIS de re-ancorare.
```

**Nu cere: gate nou, framework nou, primitivă nouă, nivel nou. Detectoarele OB/DZ/Breaker/IFVG există deja și sunt ratificate.**
