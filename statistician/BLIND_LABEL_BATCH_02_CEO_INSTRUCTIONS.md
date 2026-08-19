# INSTRUCȚIUNI — ETICHETARE BLIND INDEPENDENTĂ (`RANGE_V3_BLIND_LABEL_BATCH_02`)

**48 de ferestre XAUUSD M15, în 4 părți a câte 12.** Fiecare parte e completă în sine: conține exact
4 ferestre din fiecare lungime (96 / 288 / 480) și 3 din fiecare bloc canonic. **Te poți opri după
orice parte** — datele rămân echilibrate, doar precizia scade.

---

## Regula de interacțiune, obligatorie

```
1  TU spui PRIMUL ce vezi.
2  Eu NU ofer clasificare, sugestie sau corecție înainte de răspunsul tău.
3  Pot cere DOAR clarificări neutre („la ce index de bară se termină?"), niciodată sugestive.
4  După confirmarea ta, eticheta se BLOCHEAZĂ.
5  NU se revine la o fereastră după ce s-a văzut vreun output de detector.
6  AMBIGUOUS e legitim. Incertitudinea NU se forțează.
7  Eu doar TRANSCRIU verdictul tău.
```

**Proveniența finală va fi `CEO_INDEPENDENT_BLIND_LABEL`.** Nu `CEO_ASSISTED`.

---

## Ce e pe fiecare pagină

```
ID opac: BLIND-001 … BLIND-048   — nu conține blocul, perioada sau lungimea în nume
axa orizontală = INDEX DE BARĂ al ferestrei centrale, de la 0 la N. FĂRĂ date calendaristice.
axa verticală  = preț real
liniile verticale groase = granițele ferestrei centrale
capetele estompate, marcate CONTEXT = 24 bare înainte și 24 după, DOAR pentru orientare
```

**Clasifici NUMAI fereastra centrală.** Contextul e acolo ca să vezi de unde vine și încotro merge prețul.

Nu sunt afișate: output de detector, etichete, reason codes, PnL, swings, ATR, limite automate,
evenimente sau orice sugestie de clasificare.

---

## Cum se completează

O fereastră poate conține **mai multe segmente ordonate**. Nu ești obligat să alegi o singură clasă.

```
per SEGMENT      start_bar_approx · end_bar_approx   (în indexul afișat pe axă)
                 clasa:  RANGE · CHANNEL_UP · CHANNEL_DOWN · TREND_UP · TREND_DOWN ·
                         TRANSITION · AMBIGUOUS · UNAVAILABLE
                 confidence:  HIGH · MEDIUM · LOW

per EVENIMENT    SWEEP_UP · SWEEP_DOWN · BREAKOUT_UP · BREAKOUT_DOWN ·
                 FAILED_BREAKOUT_UP · FAILED_BREAKOUT_DOWN · NONE · AMBIGUOUS

dacă e RANGE     lower aprox · upper aprox · mid (opțional) ·
                 acumulare / distribuție, dacă observi · episodul CONTINUĂ sau S-A TERMINAT
```

Secvențele sunt explicit permise, de exemplu: `RANGE → SWEEP_DOWN → MARKUP_UP → RANGE`.

```
RANGE          lateral, cu două limite pe care prețul le testează repetat
CHANNEL_UP/DOWN oscilează în jurul unei drepte ÎNCLINATE — revine peste ea, dar derivează
TREND_UP/DOWN  direcțional, FĂRĂ să revină peste dreaptă
TRANSITION     trecere între două regimuri, fără să fie ea însăși un regim
AMBIGUOUS      nu poți decide. Răspuns LEGITIM și preferabil unei ghiciri.
UNAVAILABLE    nu se poate judeca din ce e afișat
```

> **Etichetele tale NU se convertesc automat în taxonomia detectorului.** Dacă o conversie va fi
> vreodată necesară, e un pas separat, versionat și vizibil.

---

## Ce urmează după

Etichetele se blochează, se hash-uiesc și se sigilează. **Detectorul nu a fost rulat pe aceste
ferestre și nu va fi rulat până după blocare.** Comparația e un mandat Red Team separat.
