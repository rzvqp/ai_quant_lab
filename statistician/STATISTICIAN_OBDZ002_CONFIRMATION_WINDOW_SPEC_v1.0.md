# STATISTICIAN — FEREASTRA DE CONFIRMARE PENTRU OBDZ-002 (SPECIFICAȚIE MECANICĂ)

**Document ID:** STAT-OBDZ002-CONFIRMATION-WINDOW-SPEC-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă înainte de a scrie orice specificație:** citit direct `code/obdz001.py` — confirmă `entry_idx = t + 1` (linia 129, `entry = t + 1`), unde `t` = prima Mitigation calificată (linia 104, `_first_mitigation`). Citit direct `code/obdz_three_arm_windows.py` — confirmă `_win()` calculează fereastra ca `s = entry + 1`, `e = entry + end_off` (liniile 84-85), iar `WINDOWS["t2_t5"] = 4` (linia 52). **Verificare aritmetică directă, nu presupusă:** `s = (t+1)+1 = t+2`, `e = (t+1)+4 = t+5`. **Confirmat: fereastra `t2_t5` folosită ca citire principală pentru verdictul +0,232×ATR ESTE, literal, exact `[t+2, t+5]` în notație relativă la bara de atingere — nu o coincidență, o identitate aritmetică directă.** Citit direct `code/order_flow.py::detect_order_blocks` (liniile 84-119) pentru criteriul de impuls+înghițire reutilizat mai jos — confirmă `DISP_MULT=1.5`, `BODY_FRAC=0.5`, criteriul (a) impuls (`range[i] > 1,5×ATR14[i-1]` ȘI `corp >= 0,5×range[i]`) plus (b) înghițire completă de corp a barei opuse precedente. Citit `reports/obdz002_population_results.json` — confirmă cifrele citate exact: 275/220/156=651 (step4_after_floor_0_60), floor aplicat la ATR14[t] (nu la bara de confirmare, care încă nu exista la acel pas).

---

## Rezultatul principal: fereastra CTO NU e o alegere — e o identitate deja verificată

**Ratific [+2, +5] fără rezerve, cu demonstrația de mai sus, nu doar acceptarea ei.** Fereastra `t2_t5` (folosită ca citire principală în STATISTICIAN_OBDZ_PAIRED_TEST_VERDICT_v1.0.md pentru cei +0,232×ATR agregat) ESTE aritmetic identică cu `[t+2, t+5]` unde `t` e bara de atingere. Cerința de a căuta confirmarea EXACT acolo unde s-a măsurat efectul, nu mai departe, e corectă — nu pentru că a spus-o CTO, ci pentru că e literalmente aceeași fereastră, doar exprimată în altă convenție de numărare a barelor.

## Bara zero, fixată mecanic, fără ambiguitate

```
bara 0 (t)      = bara de ATINGERE = prima Mitigation calificată pe OB_B (mecanica deja înghețată,
                  detect_mitigations, scanare de la formation_idx+2, v2.7.9). ANCORA fixă.
bara +1 (t+1)   = bara care INTRĂ în zonă = entry_idx din construcția OBDZ-001 (next-open după t).
                  NU e candidat de confirmare — vezi motivul de mai jos.
bara +2..+5     = FEREASTRA DE CĂUTARE a confirmării (4 bare candidate: t+2, t+3, t+4, t+5).
```

**De ce bara +1 e explicit EXCLUSĂ din căutarea de confirmare, nu doar omisă mecanic:** bara +1 e deja definită ca intrarea automată a construcției OBDZ-001 (fără confirmare) — dacă ar putea servi și ca propria ei confirmare, "confirmarea" ar deveni vidă (ar coincide mereu cu intrarea de bază, ori de câte ori criteriul de impuls s-ar întâmpla să fie satisfăcut chiar la bara imediat următoare atingerii). Distincția dintre OBDZ-001 (fără confirmare) și OBDZ-002 (cu confirmare) cere ca bara de confirmare să fie un eveniment SEPARAT, verificabil independent de bara automată de intrare — de aceea căutarea începe la +2, nu la +1, consecvent cu identitatea aritmetică de mai sus.

## Criteriul de confirmare — reutilizare verbatim, zero cod nou de detecție

**Bara `j` ∈ {t+2, t+3, t+4, t+5} califică drept confirmare dacă satisface EXACT criteriul (a)+(b) din `detect_order_blocks`, aplicat punctual la `j` față de `j-1`, în direcția bias-ului:**

```
(a) impuls:      range[j] > 1,5 × ATR14[j-1]   ȘI   |close[j]-open[j]| >= 0,5 × range[j]
(b) înghițire:   corpul lui j înghite complet corpul lui j-1 (direcție opusă impulsului)
direcție:        impuls_bull dacă bias=long, impuls_bear dacă bias=short (Variant 3, Mandatul 3.28,
                 neschimbat — confirmarea trebuie să fie ÎN direcția trade-ului, nu orice impuls)
```

**Prima bară `j` care califică = confirmarea.** Nu se așteaptă o a doua sau o mai bună — convenție identică cu "prima Mitigation calificată" și "primul sweep calificat" folosită peste tot în acest track. Forward-safe prin construcție (criteriul folosește doar date până la `j` inclusiv, exact ca la orice altă aplicare a acestei formule deja ratificate).

**Precizare care previne o confuzie reală:** ATR14[j-1] din criteriul (a) e un ingredient FIXAT, ratificat, INTERN formulei de impuls — NU are legătură cu ATR-ul de dimensionare de mai jos. Nu se schimbă nimic aici; e exact aceeași convenție folosită deja în `detect_order_blocks`/`track_breaker`.

## Dacă nicio bară nu califică în [t+2, t+5]: SETUP-UL SE ABANDONEAZĂ — nu e o alegere, e o consecință logică

**Decizie: ABANDONARE, nu intrare forțată la +5.** Motivul nu e preferință, e coerență cu ce înseamnă "confirmare": dacă absența unei confirmări ar duce oricum la intrare, confirmarea n-ar mai fi un filtru — ar fi doar o întârziere de 4 bare fără niciun efect asupra populației sau riscului, contrazicând exact ideea pentru care Varianta 3 a fost introdusă la Mandatul 3.28 (un filtru post-intrare, nu un contor de bare). Tabelul de sensibilitate pe care VE l-a raportat (populația scade progresiv la filtrare mai severă: 488→326→163→65) e el însuși dovada că designul implicit deja tratează absența confirmării ca excludere — dacă orice setup neconfirmat ar deveni oricum trade, populația n-ar scădea deloc față de cei 651/654. Confirm acest comportament deja implicit, îl fac explicit și mecanic: **fără confirmare în fereastră = zero trade pentru acel setup, nu se numără, nu se intră.**

## ATR-ul de dimensionare — O SINGURĂ bară pentru toate trei, clarificat exact cum a cerut VE

**Confirmat, reafirmat din STATISTICIAN_OBDZ_PAIRED_TEST_VERDICT_v1.0.md, acum făcut mecanic explicit:** SL, podeaua de eligibilitate, TP1 și TP2 se calculează TOATE la `ATR14[j]` — bara de CONFIRMARE, nu bara de atingere `t`. Motiv real, nu doar consecvență de nume: `j` poate fi cu până la 4 bare mai târziu decât `t` (dacă `j=t+5`), iar întreaga premisă a acestei ferestre e că prețul se mișcă activ în acest interval — folosirea unui ATR învechit de la `t` ar dimensiona riscul pe o volatilitate care s-ar putea să nu mai reflecte condiția reală la intrare, exact riscul pe care VE l-a semnalat corect.

```
SL         = entry_price ∓ 1,0 × ATR14[j]
podeaua    = 0,6 (= 3×cost/1,0×ATR, re-derivată, ACEEAȘI valoare numerică ca înainte) aplicată la ATR14[j]
TP1        = entry_price ± 2,0 × ATR14[j]
TP2        = entry_price ± 3,0 × ATR14[j]
entry_price = open[j+1]     (next-open după bara de confirmare, NU după t)
entry_idx  = j+1            (înlocuiește entry_idx=t+1 din construcția OBDZ-001, pentru OBDZ-002)
orizont    = min(entry_idx+20, EOD)   (Grupa A, 20 bare, măsurată de la NOUL entry_idx=j+1)
```

**O consecință de numărare care trebuie corectată explicit, altfel recontarea ar fi greșită:** populația de 651 deja livrată (275/220/156, `step4_after_floor_0_60`) a aplicat podeaua la `ATR14[t]`, singurul disponibil înainte ca bara de confirmare să existe conceptual — corect ca limită superioară provizorie, cum a semnalat chiar VE, dar GREȘIT ca bază de pornire pentru recontarea finală. **Recontarea trebuie să pornească de la populația BRUTĂ de compunere (654 = 275/223/156, `step3_composite`, ÎNAINTE de orice podea), nu de la cei 651 deja filtrați la ATR[t]** — un declanșator exclus de podeaua veche (ATR[t] prea mic) ar putea totuși trece podeaua nouă (ATR[j] diferit), și invers. Filtrarea la podea se aplică o singură dată, la sfârșit, pe `ATR14[j]`, pentru fiecare declanșator care a găsit deja o confirmare validă.

## Procedura de numărare, mecanică, autorizată

```
PENTRU fiecare declanșator compus din step3_composite (654, brut, fără podea):
  1. t = trigger_idx (neschimbat)
  2. CAUTĂ prima bară j în {t+2, t+3, t+4, t+5} care satisface criteriul (a)+(b) în direcția bias-ului
  3. DACĂ nu există j -> ABANDONAT, nu se numără mai departe
  4. DACĂ există j -> calculează ATR14[j]; aplică podeaua 0,6×ATR14[j]
  5. DACĂ ATR14[j] < 0,6 -> ABANDONAT (podea)
  6. ALTFEL -> SUPRAVIEȚUITOR OBDZ-002: entry_idx=j+1, atr=ATR14[j], entry_price=open[j+1]

Raportare: per regim, agregat, ȘI pe polaritate (demand/supply) — consecvent cu tot restul track-ului.
Prag: INSUFFICIENT_N >= 25/regim, aplicat pe numărul FINAL de supraviețuitori (după pașii 1-6 de mai sus).
```

**Autorizez EXACT acest pas de numărare — nimic altceva.** Nu e o măsurătoare nouă în sensul interzis de mandatul anterior (nicio caracterizare descriptivă, niciun MFE/MAE, nicio distribuție) — e numărătoarea mecanică de populație deja specificată ca prim pas autorizat, acum completată cu partea care lipsea (fereastra de confirmare). Dacă populația finală trece pragul în toate cele trei regimuri, următorul pas rămâne cel deja specificat: testul complet WP-5' pe `net_R`, fără nimic intermediar.

## Ce rămâne neatins

Contractul de confluență (Decizia 3, v2.7.10), `interactions.py`, familia (2, cu OBDZ-001), orizontul (20 bare, Grupa A), progresia SL/TP1/TP2 (1,0×/2,0×/3,0×) — toate neschimbate, doar ancorate acum explicit la o singură bară (`j`), nu la `t`. Cele douăsprezece tipuri de zone, palnia, Session Open — rămân exact cum au fost specificate, neautorizate aici.

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
