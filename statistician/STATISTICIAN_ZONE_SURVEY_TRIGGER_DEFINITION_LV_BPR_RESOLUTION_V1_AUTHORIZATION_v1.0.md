# STATISTICIAN — DECLANȘATORUL BRAȚULUI A, REZOLUȚIA LIQUIDITY VOID/BPR, AUTORIZAREA V1

**Document ID:** STAT-ZONE-SURVEY-TRIGGER-LV-BPR-V1-AUTH-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

---

## DECIZIA 1 — Declanșatorul brațului A: PRIMA ATINGERE bias-aliniată, NU formarea

**Formarea zonei.** RESPINSĂ ca declanșator, din două motive independente, nu unul singur:

1. **Precedentul deja stabilit și verificat al însuși OBDZ o exclude.** Bara `t` a declanșatorului compus original NU e formarea DemandZone_A — e prima Mitigation calificată a OB_B (o ATINGERE), cu DemandZone_A cerută doar să EXISTE deja la acel moment. "Aceleași trei brațe, aceleași ferestre" (cerut explicit) înseamnă aceeași DEFINIȚIE de declanșator — altfel comparația între cele 12 tipuri nu mai e pe picior de egalitate cu rezultatul OBDZ deja în mână.

2. **Brațul C (retragerea fără zonă) devine incoerent la formare.** `pullback_depth` se măsoară ca distanța de retragere ÎNAINTE de a ajunge la nivelul de intrare — un concept care presupune o ATINGERE (prețul se apropie și ajunge la zonă). La formare, prețul n-a "ajuns" nicăieri — e doar momentul în care nivelul e înregistrat. Un braț C definit relativ la o formare n-ar măsura nimic comparabil; întreaga metodologie de matching (Swing/StructureLabel, deja ratificată) presupune un brat de intrare care corespunde unei ABORDĂRI de preț, nu unei înregistrări abstracte.

**Regula fixată:** brațul A = prima atingere a zonei (convenția de atingere/consumare PROPRIE fiecărui tip de zonă, deja înghețată per detector — single-touch pentru OB/DemandZone, atingere-până-la-consumare pentru PDH/PDL etc.) care e ȘI bias-aliniată (H1+H4) la acea bară. Dacă prima atingere (per convenția proprie tipului) NU e bias-aliniată, zona respectivă nu produce niciun declanșator — nu se caută o atingere ulterioară (majoritatea tipurilor se consumă la prima atingere prin construcție proprie deja ratificată).

---

## DECIZIA 2 — Liquidity Void și BPR: DEFINIȚIE, nu excludere — dar manifestul greșește, corectat acum

**Verificat direct în cod, nu doar acceptat afirmația din ordin:** citit `code/order_block_void.py:52-83` (`LiquidityVoid` — câmpuri `at_idx`, `kind` (TEMPORAL/SIZE/BOTH — o clasificare a TIPULUI de gap, NU polaritate), `gap_seconds`, `price_jump` — **zero câmp de zonă, zero polaritate**) și `code/imbalance_mechanics.py:190-216` (`count_bpr` — returnează `dict[toleranță, număr]`, un CONTOR, calculează intern zona de suprapunere dar o ARUNCĂ înainte de return, fără să păstreze entitățile). **Confirmat exact: afirmația din ordin e corectă. Manifestul le listează greșit `ready_zero_new_code` — corectez această etichetă acum.**

**Nu le exclud ca Session Open, pentru un motiv precis:** la Session Open, NU EXISTĂ NIMIC în cod (zero ocurențe, niciun concept parțial de la care să pornesc) — orice definiție ar fi inventată din senin. La Liquidity Void și BPR, mecanica de bază E DEJA CALCULATĂ intern de funcțiile existente — lipsește doar EXPUNEREA acelor valori intermediare, nu un algoritm nou de detecție. Diferența contează: unul cere invenție de concept, celelalte cer expunerea a ceva deja produs.

### Liquidity Void — zonă + polaritate, derivate mecanic din câmpuri deja calculate

```
zonă      = [min(close[c], open[c+1]), max(close[c], open[c+1])]   (intervalul sărit, deja calculat
            ca price_jump — doar semnul, aruncat la abs(), trebuie păstrat)
polaritate = BULLISH (acționează ca suport la retragere) dacă open[c+1] > close[c]
             BEARISH (acționează ca rezistență) dacă open[c+1] < close[c]
formare   = c (= at_idx, deja stocat, neschimbat)
```

### BPR — zonă din suprapunerea deja calculată intern, polaritate NEUTRĂ prin propria natură

```
zonă      = [max(a.lower, b.lower), min(a.upper, b.upper)]   (deja calculat intern ca `gap`,
            doar bounds-urile, aruncate înainte de return, trebuie păstrate)
formare   = max(a.formed_idx, b.formed_idx)   (bara la care AMBELE jumătăți există)
toleranță = 0,0 (strict) ca prim candidat — DEJA anticipat explicit în docstring-ul funcției
            ("regula de îngheț... e a consumatorului, decisă în avans") — decid ACUM: 0,0 întâi,
            escaladare la următoarea toleranță (0,10, apoi 0,25) DOAR dacă 0,0 nu atinge n>=25,
            regulă pre-înregistrată, nu aleasă după ce se vede rezultatul.
```

**Diferență structurală importantă, de semnalat explicit:** BPR nu are polaritate proprie — e prin definiție o zonă BALANSATĂ (suprapunere bullish×bearish FVG). **Nu poate folosi convenția "polaritatea zonei aliniată cu bias-ul"** ca celelalte 11 tipuri, pentru simplul motiv că nu are propria polaritate de aliniat. Rezoluție: direcția trade-ului la o atingere BPR e dată DOAR de bias-ul predominant (H1+H4) la acea bară, nu de zonă — geometria zonei rămâne aceeași indiferent de direcție, doar convenția de intrare/SL se oglindește după bias. Coerent cu felul în care BPR e tratat deja în literatura SMC (nivel care poate juca ambele roluri, în funcție de direcția de abordare) — nu o soluție inventată independent.

**AUTORIZEZ implementarea acestor două extensii minime** (expunerea zonei+polarității, nu un detector nou) ca precondiție pentru includerea lor în valul respectiv al numărătorii descriptive.

---

## PARTEA 3 — Numărătoarea confirmărilor: V1 verificat, autorizez rularea

**Verificat direct** `reports/obdz_confirmation_variants_count_results.json` (comitul `e5de461`) — reproduce exact: V1 = 129/90/81 (min=81, `abandoned: false`); V2 = 19/20/14 (min=14, `abandoned: true`); V3 = 24/17/14 (min=14, `abandoned: true` — bear la 24, la un pas de prag, dar tot sub). **V2 și V3 corect abandonate — decizia VE e conformă exact cu regula fixată la Mandatul 3.40.**

**AUTORIZEZ rularea V1 (Dubla Respingere) pe declanșatorul compus**, exact construcția specificată la Mandatul 3.40: `entry_idx=q+1`, `sl_price` = min/max al celor două fitile, `R=|entry-sl|` (floor R>=0,60 deja aplicat corect în numărătoare), `TP1=entry+2R`, `TP2=entry+3R`, orizont = `min(entry_idx+20, EOD)`, test WP-5' standard pe `net_R`, populația = 300 supraviețuitori agregat (181 demand/119 supply — raportare pe polaritate obligatorie, per regim: 129/90/81).

**Familia, fixată conform regulii deja stabilită înainte de a vedea rezultatele (Mandatul 3.40):** familia declanșatorului compus = 2 (deja consumată, OBDZ-001+002) **+ 1 (V1, care trece pragul ȘI se rulează acum) = 3.** V2 și V3, abandonate ÎNAINTE de rulare, NU consumă familie — neschimbat față de regula pre-fixată.

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
