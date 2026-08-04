# STATISTICIAN — TREI DETECTOARE DE REACȚIE (Void, BPR, Weekly) + O CONSTATARE CARE SCHIMBĂ CAND-0006

**Document ID:** STAT-THREE-REACTION-DETECTORS-SPEC-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `order_block_void.detect_liquidity_voids`, `imbalance_mechanics.count_bpr` + `detect_fvg_reactions`, `institutional_levels.compute_prior_week_levels` + `detect_level_touches`. **Precedentul urmat e cel indicat: `session_levels.py` — oglindire bară cu bară, zero convenții paralele.**

---

# PARTEA 0 — CONSTATARE DECISIVĂ PE PWH/PWL: detectorul NU e problema

**Mi s-a cerut să spun ÎNAINTE de construcție dacă detectorul poate produce populație utilizabilă. L-am măsurat, nu l-am estimat** — script temporar, necomis, șters după rulare, reutilizând exclusiv primitive ratificate și exact calea de încărcare a survey-ului existent.

## Descompunerea pâlniei, pe descoperire, cele 3 regimuri

```
etapă                                        bear    bull   corecție   TOTAL
1. niveluri săptămânale emise                 230     232      110       572   (538 COMPLETE)
2. atinse geometric în fereastra lor          108     113       54       275   = 48,1% ✅ SĂNĂTOS
3. ȘI cu bias aliniat la bara de atingere       3       2        1         6   = 2,2% din atinse ❌
```

**Reproduce exact n=6 (3/2/1) din survey — deci descompunerea e a aceleiași populații, nu a alteia.**

## Unde moare, și de ce — mecanismul, nu doar cifra

**Etapa 2 e perfect sănătoasă: aproape jumătate din nivelurile săptămânale SUNT atinse.** 275 de evenimente e o populație pe deplin utilizabilă. **Colapsul e integral la etapa 3: filtrul de bias distruge 97,8% dintre ele.**

**Cauza e structurală, nu statistică.** `WEEKLY_HIGH` e maximul săptămânii trecute; ca prețul să-l atingă, trebuie să urce până acolo — o mișcare ASCENDENTĂ. Dar direcția lui de tranzacție e SHORT (rezistență), deci cere bias DESCENDENT pe H1 ȘI H4. **Cele două condiții se bat între ele prin construcție:** a ajunge la un maxim săptămânal înseamnă, aproape prin definiție, că trendul pe orizonturi comparabile e ascendent. Cifrele o confirmă direct: **H atins de 147 de ori, aliniat de 2; L atins de 128, aliniat de 4.**

**Generalizarea, cu o predicție verificabilă:** pentru ORICE nivel-extremă-a-perioadei-anterioare, „atingere" și „bias aliniat pentru REVERSAL" sunt anti-corelate structural, **iar anti-corelația se agravează cu lungimea perioadei** — la zi e slabă (PDH/PDL: n=356), la săptămână e severă (n=6). **Predicție testabilă: nivelurile de SESIUNE (sub-zilnice) ar trebui să fie AFECTATE MAI PUȚIN decât cele zilnice**, fiind mai apropiate și atinse în ambele direcții. Ieftin de verificat la prima măsurătoare pe `session_levels.py`.

## Concluzia operațională — economisește tura, dar altfel decât se aștepta

```
✅ CONSTRUIȚI detectorul de atingere săptămânală — funcționează, dă 275 de evenimente.
❌ NU CAND-0006 în forma actuală — degenerarea NU vine din detector, ci din ÎNCADRAREA
   candidatului: reversal la extrema săptămânală, filtrat pe bias aliniat.
```

**CAND-0006 trebuie RE-ÎNCADRAT, nu deblocat.** Trei căi, toate exprimabile pe același detector, niciuna aleasă de mine (e decizie Alpha): (a) fără filtru de bias — bias-ul dă direcția, nu eligibilitatea; (b) teza inversată — continuare prin nivel, nu reversal de la el (ar fi aliniată natural cu mișcarea care produce atingerea); (c) fără bias deloc, ca test pur al nivelului. **Populația disponibilă pentru (a)/(c) e 275, nu 6.**

**Diagnosticul comun era greșit: nu lipsa detectorului bloca CAND-0006.** Detectorul se construiește oricum — e util celorlalte încadrări și e ieftin.

---

# PARTEA 1 — `detect_void_reactions`

**Oglindește `detect_fvg_reactions` (gradientul Q6 în 3 trepte), pentru că un void e același tip de obiect: un interval de preț sărit.** Zero convenție nouă.

```
INTRARE     void-uri din detect_liquidity_voids + zona/polaritatea derivate la v2.7.27:
              zone  = [min(close[c], open[c+1]), max(close[c], open[c+1])]
              mid   = (zone_lower + zone_upper) / 2
              polaritate = BULLISH dacă open[c+1] > close[c] (gap în sus → suport dedesubt)
                           BEARISH dacă open[c+1] < close[c]
            available_idx = c+1  (ambii termeni cunoscuți la c+1 — verificat de Red Team)

GRADIENT în 3 trepte, primul index al fiecărui eveniment, fiecare OPȚIONAL:
  partial_fill_idx   prima bară care atinge MID          BULL: low[j] <= mid   BEAR: high[j] >= mid
  full_fill_idx      prima bară care traversează zona    BULL: low[j] <= lower BEAR: high[j] >= upper
  rejection_idx      prima bară care INTRĂ și ÎNCHIDE înapoi în afară
                     BULL: low[j] <= upper ȘI close[j] > upper
                     BEAR: high[j] >= lower ȘI close[j] < lower
```

**`rejection` oglindește semnătura D6 wick-sweep-reject verbatim** (`low[c] < nivel ȘI close[c] > nivel`) — deja ratificată în `liquidity_mechanics`. Nu inventez o a patra convenție de respingere.

**D7:** ca la FVG — **fiecare dintre cele trei se înregistrează la PRIMA apariție**, o singură dată; void-ul e consumat ca DECLANȘATOR la primul `partial_fill`. Fără re-armare. Limitarea D7 cunoscută (a doua reacție genuină invizibilă) se aplică identic; consemnată, nu ascunsă.

**Ferestre disjuncte (anti-E010):** selecția se încheie la `available_idx = c+1`; măsurarea începe la bara de reacție și rulează înainte; intrarea la `next-open` după bara de reacție. Fără suprapunere prin construcție. Mărginit de bloc (D3_bis/D4).

# PARTEA 2 — `detect_bpr_reactions`

```
INTRARE     perechi FVG bull×bear din count_bpr + zona derivată la v2.7.27:
              zone = [max(lower_a, lower_b), min(upper_a, upper_b)]
              formation    = max(formed_idx_a, formed_idx_b)
              available_idx = max(confirmed_idx_a, confirmed_idx_b)   ← AMBELE confirmate
            toleranță 0,0 (strictă) ca prim candidat, escaladare doar dacă n<25 — regula fixată la v2.7.27
```

## BPR nu are polaritate — cum se aplică asta la REACȚIE (confirmat)

**Confirmat: direcția vine din bias, iar detectorul NU o codifică.** Dar „umplere completă" și „respingere" cer o LATURĂ ca să însemne ceva. **Rezolvarea: detectorul emite geometrie direcțional-agnostică, INCLUSIV latura de intrare; politica adaugă direcția din bias.**

```
touch_idx        prima bară al cărei range SUPRAPUNE zona (CONȚINERE, ca la Mid):
                 low[j] <= zone_upper ȘI high[j] >= zone_lower
entry_side       'above' dacă bara vine dinspre peste zonă, 'below' dacă dinspre sub
                 (determinat de poziția lui close[j-1] față de zonă — cauzal, bara anterioară)
traverse_idx     prima bară care traversează COMPLET, dinspre entry_side spre latura opusă
reject_idx       prima bară care intră și ÎNCHIDE înapoi pe latura de INTRARE  (D6, verbatim)
```

**`entry_side` e piesa care face traversarea și respingerea interpretabile fără o polaritate proprie.** Politica combină `entry_side` + bias și **trebuie să declare regula** — nu poate moșteni convenția PDH/PDL, care presupune o latură intrinsecă. Exact tratamentul dat lui `Mid` la `session_levels.py`.

**D7, ferestre, blocuri:** identic cu Partea 1.

# PARTEA 3 — `detect_weekly_level_touches`

**Oglindește `detect_level_touches` VERBATIM, cu o singură schimbare: fereastra e SĂPTĂMÂNA curentă, nu ziua.**

```
ATINGERE   WEEKLY_HIGH: high[j] >= price   (rezistență, o latură — ca PDH)
           WEEKLY_LOW:  low[j]  <= price   (suport,     o latură — ca PDL)
           → DEPĂȘIRE, nu conținere. Sunt extreme, nu puncte medii — conținerea e pentru Mid.
FEREASTRA  de la available_idx până când week_index[j] != week_index[available_idx], în același bloc
           (exact structura `if day_index[j] != day: break`, cu week în loc de day)
D7         consumat la PRIMA atingere, fără re-armare — identic cu PDH/PDL
```

**De ce depășire și nu conținere:** PWH/PWL sunt extreme reale ale unei perioade, unde se odihnește lichiditate — aceeași clasă cu PDH/PDL, **nu** cu `Mid`. Distincția pe care am stabilit-o la `session_levels.py` se aplică direct și dă răspunsul fără o decizie nouă.

## Flag-ul PARTIAL la săptămâni carantinate — se propagă, NU se filtrează în detector

**Măsurat: 538 din 572 sunt COMPLETE, 34 sunt PARTIAL.** Regula:

```
Detectorul emite AMBELE și propagă `completeness` în înregistrarea de atingere.
Excluderea PARTIAL e o alegere de POLITICĂ, declarată — nu un filtru ascuns în primitivă.
```

**Dar impun o cerință de raportare, dintr-un motiv derivat:** o săptămână PARTIAL are High/Low calculate pe MAI PUȚINE zile ⇒ **extremele ei sunt sistematic mai puțin extreme** (un max pe 3 zile < un max pe 5 zile) ⇒ **nivelul e mai aproape de preț ⇒ e atins MAI DES.** A le agrega ar umfla artificial rata de atingere. **COMPLETE și PARTIAL se raportează SEPARAT, obligatoriu** — aceeași logică ca separarea High/Low/Mid.

---

## Ce NU am făcut

Nu am implementat nimic. **Nu am re-încadrat CAND-0006** — am arătat că trebuie și am dat trei căi; alegerea e a lui Alpha. Nu am ales toleranța finală pentru BPR (regula de escaladare e deja fixată). Nu am construit niciun candidat.

## HANDOFF

**VE** implementează cele trei detectoare (oglindind `detect_fvg_reactions` / `detect_level_touches` / D6, fără convenții paralele) și, la prima măsurătoare pe niveluri de sesiune, **verifică predicția din Partea 0** (sesiunile ar trebui să sufere mai puțin decât ziua). **Red Team** atacă. **Alpha** re-încadrează CAND-0006 înainte de a-l relua — populația reală e 275, nu 6, dar numai fără filtrul de bias-reversal.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.40 (commit `74a8d50`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
