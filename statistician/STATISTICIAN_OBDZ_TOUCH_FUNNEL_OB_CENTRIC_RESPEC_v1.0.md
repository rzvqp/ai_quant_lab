# STATISTICIAN — RESPECIFICAREA PÂLNIEI ÎN UNITĂȚI DE ORDER BLOCK (HOTFIX)

**Document ID:** STAT-OBDZ-TOUCH-FUNNEL-OB-CENTRIC-RESPEC-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă, pe toate cele trei corecții, nu doar acceptare:** citit integral `code/obdz_touch_funnel.py` (comitul `51cf4dc`) și **rulat direct** — confirmă exact cifrele raportate: T1=5.510/5.560 (99,1%; demand 2.736/2.763=99,0%, supply 2.774/2.797=99,2%), T2=0 în FIECARE celulă (toate regimurile, ambele polarități), zone 2.275/2.107/1.178 exacte. Verificat direct în manifest: contractul de confluență (Decizia 3) e la `composite_hypothesis_formalization_v2_7_10` — confirmă `v2.7.10`, nu `v2.7.7`. Verificat manifestul curent: **`v2.7.19`, nu `v2.7.18`** — o a patra discrepanță de versiune, semnalată mai jos. Verificat `interactions.py` direct — conține exact `to_mask`/`dilate`/`confluence`/`price_in_zone`/`price_in_any_zone`, zero stare, zero logică de tranzacționare, confirmă ratificarea (`v2.6.1`, `2fb948f`).

---

## Eroarea, confirmată ca fiind a mea, mecanic explicată

**Am scris pâlnia ZONĂ-CENTRIC la Mandatul 3.31. Decizia 3 (v2.7.10) e OB-CENTRIC. Sunt întrebări diferite, iar cea zonă-centrică dă zero din motiv geometric, nu din eroare de execuție.**

Verificat exact în `composite_hypothesis_formalization_v2_7_10.cross_candle_mechanical_spec_v2_7_10`: `OB_B` e obiectul care se MITIGHEAZĂ la `trigger_bar_t` (bara la care OB_B are propriul eveniment CALIFICAT de Mitigation); `DemandZone_A` e confluența NECONSUMABILĂ, care trebuie doar să EXISTE și să se suprapună la momentul t — **DemandZone_A nu are NICIO condiție de „nemitigat" asupra ei, pentru că nu consumă niciodată.** Pâlnia mea din Mandatul 3.31 a cerut exact inversul: „un OB nemitigat suprapus LA momentul atingerii zonei" — tratând zona ca ancoră și cerând starea de nemitigat pe OB LA UN MOMENT GREȘIT.

**De ce dă mecanic zero:** un OB se mitighează repede — corpul lui (zona proprie) e mult mai îngust decât zona `[Low,High]` a unei DemandZone (OB e submulțime geometrică a DemandZone pe bara de origine, deja stabilit). Când o DemandZone DIFERITĂ, aflată în altă parte, e în sfârșit atinsă (adesea mult mai târziu), aproape orice OB cross-candle din vecinătate s-a mitigat deja. T2=0 e consecința FORȚATĂ a întrebării puse invers, nu dovadă că 654 nu există — cele 654 EXISTĂ demonstrat, măsurate deja de mai multe ori.

---

## CORECȚIA 1 — confirmată: contractul NU se schimbă

**De acord integral.** Decizia 3 e deja OB-centrică și a produs cele 654 declanșatoare corect. **Nu se atinge.** Instrumentul de măsurare (pâlnia din Mandatul 3.31) a fost greșit, nu obiectul măsurat.

## CORECȚIA 2 — confirmată, cu o precizare suplimentară

**Confirmat: contractul e la v2.7.10, nu v2.7.7.** Editarea lui v2.7.7 ar fi revenit peste opt versiuni și ar fi corupt tot ce s-a construit deasupra (Mandatele 3.25-3.33). **Precizare suplimentară, verificată acum:** manifestul e de fapt la **v2.7.19**, nu v2.7.18 — ordinul citează o versiune cu una în urmă față de ultima mea publicare (Mandatul 3.33, definițiile Mitigation/Breaker/Rejection Block). Semnalez asta explicit: pare un artefact de sincronizare (ordinul redactat înainte ca v2.7.19 să ajungă), nu o eroare de fond — dar contează pentru punctul următor.

## CORECȚIA 3 — confirmată: `interactions.py` neatins

**Confirmat direct în cod:** modulul conține DOAR funcții pure de intersecție booleană (`to_mask`, `dilate`, `confluence`, `price_in_zone`, `price_in_any_zone`) — zero stare, zero logică de tranzacționare, zero orizonturi, exact ratificarea de la Mandatul 3.21 (`v2.6.1`). **Mutarea stării de mitigare acolo ar anula delimitarea explicită** („FĂRĂ logică de trade, FĂRĂ management de poziție" — chiar în docstring-ul modulului). Starea de mitigare rămâne exact unde e deja — `order_flow.py`, prin `_scan_reactions`/`detect_mitigations` — și pâlnia (un script de măsurare, nu un modul primitiv) o REFOLOSEȘTE ca funcție, nu o realoacă.

---

## Pâlnia respecificată, în unități de ORDER BLOCK

**Populația-ancoră: OB-urile detectate (`detect_order_blocks`, criteriul E010 deja ratificat) — nu DemandZone.**

```
PAS 1  DETECTED   toate OB-urile detectate (ambele polarități, orice regim/bias) — populație fixă,
                  independentă de orice zonă.

PAS 2  MITIGATED  dintre acestea, câte au un eveniment CALIFICAT de Mitigation (`detect_mitigations`,
                  scanare de la formation_idx+2, oprire la breaker — mecanica deja înghețată, v2.7.9).
                  Bara PRIMULUI astfel de eveniment = `t`, ancora pentru pașii următori. OB-urile care
                  se RUP (breaker) ÎNAINTE de orice atingere calificată NU produc niciun `t` — excluse
                  corect aici, nu artificial.

PAS 3  ZONE       dintre OB-urile mitigate (la bara lor proprie `t`), câte au O DemandZone_A cross-candle
                  care satisface EXACT condițiile Decizia 3: kind_A == kind_B, formation_A != formation_B,
                  formation_A < t, |formation_A − formation_B| <= 460, ACELAȘI bloc, suprapunere de interval
                  OB_B(corp) × DemandZone_A(range). NICIO condiție de „nemitigat" pe DemandZone_A — nu
                  consumă niciodată.

PAS 4  BIAS       dintre acelea, câte au bias H1+H4 aliniat = kind_B, la bara `t`. = FINAL.
```

**Aceeași unitate pe tot lanțul: OB-uri (per formare), nu bare, nu zone.**

**Verificare de corectitudine, obligatorie:** rezultatul de la Pasul 4 trebuie să reproducă aproximativ **654** (275+223+156, deja confirmate de mai multe ori independent). **Dacă nu se apropie, pâlnia încă măsoară altceva** — nu se acceptă un rezultat divergent fără explicație mecanică, exact disciplina aplicată acum pentru a găsi eroarea originală.

**Raportare:** per regim, agregat, ȘI pe polaritate (demand/supply) la fiecare pas — consecvent cu tot ce s-a cerut deja în acest fir.

---

## Ce se păstrează din rularea „eșuată" — nu era eșuată, era corectă

**T1 = 99,1% (5.510/5.560) rămâne o constatare validă și utilă, independentă de eroarea de mai sus.** Răspunde la o întrebare DIFERITĂ, corect pusă: „DemandZone-urile sunt vreodată atinse?" — răspuns, aproape toate. **Confirmă: disponibilitatea NU e problema.** Colapsul de frecvență (609 din potențial mult mai mult) se întâmplă la COMPUNERE (confluența specifică + bias), nu la existența zonelor. Această constatare NU se remăsoară — rămâne câștigată.

**Scriptul `obdz_touch_funnel.py` rămâne comis, neschimbat** — un artefact istoric corect, care a implementat fidel o specificație greșită și s-a oprit corect la ambiguitate, exact cum trebuia. **Pâlnia OB-centrică de mai sus se implementează într-un script NOU** (ex. `obdz_ob_centric_touch_funnel.py`), nu prin editarea celui vechi — păstrează dovada erorii și a corecției, nu le suprascrie.

---

## Ce rămâne neatins, reconfirmat

- **Contractul de confluență, Decizia 3, v2.7.10 — neatins.**
- **`interactions.py` — neatins.**
- **Familia — actualizată la 12 la Mandatul 3.33 (nu mai 10, cf. corecției de versiune de mai sus) — neatinsă suplimentar aici.**
- **Testul pereche pe OB×DemandZone rămâne poarta.** Nimic altceva nu se rulează dincolo de pâlnia read-only de mai sus.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.20 (commit `19a63dc`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
