# CROSS-VERIFICATION — order_block_void.py (edca965)

**Document ID:** STAT-OBVOID-XVERIFY-v1.0 · **Autor:** Research Lab (divizie neutră) · **Data:** 2026-07-28
**Cerere:** CEO — clauza din CROSS_VERIFICATION_SPEC, **prima aplicare efectivă**. Motiv: `order_block_void.py` e modul persistent proiectat ȘI implementat de VE, fără verificare independentă. Research Lab nu a atins niciodată modulele MK.
**Țintă:** `code/order_block_void.py`, commit `edca965` pe `discovery-mk-matrix-v1` („freeze Order Block + Liquidity Void definitions").
**Metodă:** suită externă, matrici sintetice generate în memorie (`tests/test_ob_void_cross.py`), fiecare caz derivat din **textul definiției ratificate**, NU din cod. Nu reutilizează testele VE. Nu împarte presupunerile implementării.

## Rezultat
- **21/21 teste TREC.** `mypy --strict`: **curat** (no issues).
- **Numărătoare de referință reprodusă EXACT** pe fișierul canonic de 84.152 bare, criteriu înghețat: **size-only 248 · time-only 119 · both 96 · total 463** (potrivire perfectă; a 4-a confirmare independentă după Statistician/VE/CEO).
- **NICIO neconformitate. NICIUN defect găsit.**

## Ce s-a verificat (conform definiției ratificate)
**Liquidity Void (hibrid):**
- Temporal: strict `> 900s`. Fereastra de mentenanță izolată **FAIL-CLOSED** — suprimă DOAR `gap ≤ 4500s ȘI ora(start) ∈ {20,21} UTC` (verbatim gapfind). Verificat că NU suprimă: gap > 75min la h20; gaps la orele 0/12/19/22/23; **weekend-urile (incluse)**; folosește ora barei de **START** (`time[c]`); boundary 4500 inclusiv; și că mentenanța **nu atinge brațul de mărime** (un gap de mentenanță cu salt > $1.20 rămâne SIZE void).
- Mărime: strict `> $1.20` = `3 × COST_ROUND_TRIP` (0.40); valoare absolută.
- Hibrid: temporal SAU mărime → BOTH/TEMPORAL/SIZE; `at_idx == c`.

**Order Block:**
- Zona = **CORPUL** `[min(Close,Open), max(Close,Open)]`. Semnătura `order_block_zone(open_bar, close_bar)` **nu are high/low** → fitilul e exclus prin construcție (nu doar declarat).
- Separarea ferestrelor (anti-E010): contractul `ObValidityEvent` are `measurement_start = event_idx` (NU `formation_idx`) și `measurement_end = event_idx + 20` → fereastra de valabilitate `[formation, event)` și cea de măsurare `[event, event+20)` sunt **disjuncte** (verificat pe contract). Resolver-ul `resolve_validity_and_measurement` ridică `NotImplementedError` → nu poate returna tăcut o fereastră suprapusă.

Criteriul de FORMARE al OB rămâne `NotImplementedError` — **nu l-am implementat, nu l-am testat** (conform mandatului).

## Observații pentru înregistrare (NU defecte)
1. **Boundary float** (linia `size = jump > size_threshold`): pragul e strict-exact în aritmetică (salt exact $1.20 NU e void). Dar un salt nominal de $1.20 construit din prețuri reale ~$2000 depășește pragul prin eroare de reprezentare: `100.0 + 1.20 − 100.0 = 1.2000000000000028 > 1.20` → SE înregistrează ca void. Nu e defect de cod (strict `>` e corect per „peste 1.20") — doar o notă de reprezentare pentru cine raționează despre boundary-ul exact. (Numărătoarea 463 nu e afectată — reprodusă exact.)
2. **Separarea ferestrelor — garanție de DESIGN, nerulabilă la acest commit** (linia `raise NotImplementedError` din `resolve_validity_and_measurement`). Non-suprapunerea e DECLARATĂ + disjunctă pe contract, dar codul de detecție a evenimentului (care ar popula `measurement_start`) nu există — e gate-uit pe criteriul de FORMARE deschis, prin design. Deci cerința „verifică prin test că nu se pot suprapune, nu doar declarat" e satisfăcută **structural** (contract disjunct + resolver refuză), dar non-suprapunerea la **runtime** nu poate fi exercitată complet până când formarea e ratificată și resolver-ul implementat. Raportat ca atare — nu e defect (item deschis, enumerat), dar garanția anti-E010 e la nivel de design, nu încă exercitabilă la runtime.

## Notă de proces
Două teste au „picat" în timpul dezvoltării — ambele **erori ale MELE de date de test** (confuzia barei la care se referă saltul `Open[c+1]−Close[c]`; imprecizia float la boundary), corectate și dezvăluite. **În ambele cazuri modulul era corect** — procesul de verificare independentă mi-a prins erorile, nu ale modulului. Exact motivul pentru care un test care împarte presupunerile implementării n-ar detecta o presupunere greșită: aici presupunerile au fost testate din definiție, nu din cod.

**Nu am reparat nimic (nu e codul meu; oricum n-am găsit defect). Holdout SEALED. Datele de descoperire neatinse. LM-001 nerulat.**
