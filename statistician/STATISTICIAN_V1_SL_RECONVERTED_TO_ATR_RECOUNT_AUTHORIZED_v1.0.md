# STATISTICIAN — V1: SL RECONVERTIT LA ATR14[t], RENUMĂRARE AUTORIZATĂ

**Document ID:** STAT-V1-SL-ATR-RECOUNT-AUTHORIZED-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

## Punctul de bookkeeping — verificat, nu doar acceptat

**Verificat direct: rezumatul meu de la mandatul anterior CHIAR a inclus "Decizia 1"**, ca primul punct marcat explicit ("**Decision 1 — arm-A trigger = first bias-aligned touch, not zone formation.**"). Dacă "punctul 1" se referă la altceva (poate intrarea din memoria persistentă, sau un punct dintr-un mandat mai vechi) — spune-mi exact la ce te referi și corectez. Nu insist pe asta — trec direct la partea substanțială, care e clară și verificabilă independent de această întrebare.

## Verificare directă a cifrelor citate — ambele confirmate exact

Rulat direct pe fișierele deja existente: `obdz_confirmation_variants_count_results.json` (V1, câmpul `confirmed`, ÎNAINTE de orice podea) = **157/125/99** — exact cifrele citate. `obdz002_population_results.json` (`step3_composite` minus `step4_after_floor_0_60`) = **0/3/0** exclus — exact cifrele citate. **Ambele cifre pe care se sprijină motivul CTO sunt corecte, nu aproximative.**

---

## CONFIRM parametrii — SL revine la ATR14[t], identic cu OBDZ-002

```
entry_idx   = q+1   (NESCHIMBAT — momentul intrării rămâne dictat de pattern-ul Dubla Respingere,
              q = a doua atingere calificată, căutare în {t+1,t+2})
SL          = 1,0 × ATR14[t]   (NU structural, NU la bara q — la bara t, EXACT convenția OBDZ-002)
TP1         = 2,0 × ATR14[t]
TP2         = 3,0 × ATR14[t]
podea       = 0,60 × ATR14[t]
R           = 1,0 × ATR14[t]   (prin construcție, identic cu OBDZ-002 — nu mai e geometric per-tranzacție)
```

**Motivul CTO e solid și-l confirm ca atare:** un stop structural (sub cel mai adânc dintre cele două fitile) poate fi foarte apropiat dacă cele două respingeri se întâmplă la niveluri apropiate — o singură lumânare suplimentară care testează din nou lichiditatea (fără să invalideze teza de reversal) ar putea scoate trade-ul din piață prematur. ATR14[t] oferă o marjă consecventă cu volatilitatea reală a momentului, exact motivul pentru care OBDZ-002 a folosit-o de la început.

**Notez explicit, pentru completitudine, nu ca obiecție:** asta abandonează convenția "bara de dimensionare = bara de confirmare" fixată la Mandatul 3.36/3.40 (evitarea unui ATR învechit la intrare). Aici, intrarea (q+1) poate fi cu 1-2 bare mai târziu decât t, deci ATR14[t] e, prin construcție, potențial ușor învechit față de momentul real de intrare — un compromis real, nu invizibil. Dar e EXACT alegerea pe care CTO o specifică explicit ("ATR14[t]", nu "ATR14[q]"), motivată de un risc diferit (stop prea aproape) pe care nicio bară de dimensionare n-ar fi rezolvat-o — aleg să respect litera instrucțiunii, cu acest compromis consemnat clar, nu ascuns.

## Consecința pentru numărare — confirmată, dar NU asum cifra finală fără recalcul mecanic

**De acord cu diagnosticul:** podeaua ATR abia leagă (0/3/0 la OBDZ-002, pe întreaga populație de 654/651) — motivul e structural: un stop bazat pe ATR e rareori sub 0,6 (comparativ cu un stop geometric care poate fi oricât de mic, de aici cele 28/35/18 excluderi la podeaua R-geometrică din numărătoarea V1 originală). **Dar "~157/125/99" e o ESTIMARE a CTO, marcată explicit cu "~"** — subsetul CONFIRMAT de V1 (157/125/99) e o populație DIFERITĂ, mai mică, decât populația completă de 654/651 pe care s-a măsurat exclusiv 0/3/0 — nu presupun automat că exact ACELEAȘI 0/3/0 evenimente s-ar exclude aici. **Cer recalculul mecanic real, nu adopt aproximarea ca finală.**

## Procedura de renumărare, autorizată

```
PENTRU fiecare din cele 654 declanșatoare brute:
  aplică pattern-matching-ul V1 NESCHIMBAT (căutare q ∈ {t+1,t+2}, re-atingere fără închidere
    sub extrema barei t) -> dacă nu se confirmă, ABANDONAT (neschimbat)
  DACĂ confirmat: calculează ATR14[t] (NU ATR14[q])
    DACĂ ATR14[t] < 0,60 -> ABANDONAT la podea
    ALTFEL -> SUPRAVIEȚUITOR, entry_idx=q+1, R=1,0×ATR14[t]
Raportare: per regim, agregat, PE POLARITATE (obligatoriu, neschimbat) — verifică din nou
  INSUFFICIENT_N>=25/regim pe cifra FINALĂ (aproape sigur trecută, dat fiind tiparul 0/3/0, dar
  verificarea rămâne mecanică, nu presupusă).
```

**AUTORIZEZ această renumărare, ÎNAINTE de orice rulare WP-5'** — exact ordinea cerută.

## Familia — neschimbată

Acesta rămâne EXACT V1 (Dubla Respingere), doar cu risc-sizing finalizat înainte de rulare — nu o ipoteză nouă, nu un slot suplimentar de familie. **Familia rămâne 2 (deja consumată) + 1 (V1) = 3**, neschimbată față de Mandatul 3.41.

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
