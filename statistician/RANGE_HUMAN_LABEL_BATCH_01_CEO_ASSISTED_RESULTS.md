# RANGE_HUMAN_LABEL_BATCH_01 — CEO-assisted labels

Data etichetării: 2026-08-18  
Instrument: OANDA:XAUUSD  
Timeframe: M15  
Lot sursă: `RANGE_HUMAN_LABEL_BATCH_01.pdf` (24 ferestre)

## Protocol și transparență

- Etichetarea a fost făcută pagină cu pagină, numai pe graficul afișat.
- CEO-ul a avut verdictul final pentru fiecare fereastră și a corectat explicit clasificările unde a considerat necesar.
- Asistentul a exprimat opinii vizuale înaintea confirmării CEO; prin urmare lotul este **CEO_ASSISTED**, nu independent și nu poate fi prezentat ca blind human-only.
- Zonele estompate `CONTEXT` au fost folosite doar pentru orientare; eticheta descrie fereastra centrală.
- `AMBIGUOUS / MULTI-REGIME` înseamnă că fereastra conține mai multe faze reale și nu trebuie forțată într-o singură clasă.

## Etichete finale confirmate

| ID | Etichetă finală CEO | Detalii |
|---|---|---|
| HBL-01 | RANGE | Breakout DOWN / posibil SWEEP; încredere MEDIUM; oscilație aproximativ 1463–1478. |
| HBL-02 | CHANNEL_DOWN | Încredere HIGH. |
| HBL-03 | AMBIGUOUS / MULTI-REGIME | Mai multe regimuri; fără o singură etichetă dominantă. |
| HBL-04 | RANGE | Breakout DOWN; încredere HIGH; aproximativ 1665–1678. |
| HBL-05 | AMBIGUOUS / MULTI-REGIME | CHANNEL_UP → RANGE → BREAKOUT_DOWN → CHANNEL_UP. |
| HBL-06 | AMBIGUOUS / MULTI-REGIME | RANGE-uri succesive → CHANNEL_UP. |
| HBL-07 | RANGE | Breakout DOWN; încredere HIGH. |
| HBL-08 | RANGE | Breakout DOWN; încredere HIGH. |
| HBL-09 | AMBIGUOUS / MULTI-REGIME | RANGE → CHANNEL_UP → RANGE. |
| HBL-10 | AMBIGUOUS / MULTI-REGIME | RANGE → CHANNEL_UP. |
| HBL-11 | AMBIGUOUS / MULTI-REGIME | CHANNEL_UP → CHANNEL_DOWN → BREAKOUT_UP → RANGE. |
| HBL-12 | AMBIGUOUS / MULTI-REGIME | CHANNEL_UP → RANGE → CHANNEL_DOWN; range aproximativ 1344–1352. |
| HBL-13 | CHANNEL_UP | Încredere HIGH. |
| HBL-14 | AMBIGUOUS / MULTI-REGIME | CHANNEL_UP → CHANNEL_DOWN → RANGE; range final aproximativ 1834–1838. |
| HBL-15 | AMBIGUOUS / MULTI-REGIME | RANGE → SWEEP/FAILED_BREAKOUT_UP → BREAKOUT_DOWN → CHANNEL_DOWN; range aproximativ 1835–1847. |
| HBL-16 | AMBIGUOUS / MULTI-REGIME | RANGE → BREAKOUT_DOWN → CHANNEL_DOWN → RANGE; primul range aproximativ 1853–1862, ultimul aproximativ 1767–1797. |
| HBL-17 | RANGE | Range larg și volatil; aproximativ 1936–1973; breakout NONE; încredere HIGH. |
| HBL-18 | AMBIGUOUS / MULTI-REGIME | CHANNEL_UP → RANGE → CHANNEL_DOWN → RANGE → BREAKOUT_UP → RANGE. |
| HBL-19 | AMBIGUOUS / MULTI-REGIME | CHANNEL_UP → BREAKDOWN_DOWN → CHANNEL_UP → RANGE. |
| HBL-20 | AMBIGUOUS / MULTI-REGIME | RANGE/ACUMULARE → MANIPULARE/SWEEP_DOWN → EXPANSIUNE/MARKUP_UP → RANGE nou. Tipar candidat pentru studiu separat, fără declarare de profitabilitate. |
| HBL-21 | AMBIGUOUS / MULTI-REGIME | BREAKDOWN_DOWN → RANGE/ACUMULARE → BREAKOUT_UP / CHANNEL_UP; range aproximativ 1864–1880. |
| HBL-22 | AMBIGUOUS / MULTI-REGIME | CHANNEL_UP → RANGE/CORECȚIE_LATERALĂ → CHANNEL_UP; range aproximativ 2376–2398. |
| HBL-23 | AMBIGUOUS / MULTI-REGIME | CHANNEL_DOWN → CHANNEL_UP → RANGE larg și volatil; range aproximativ 2020–2036. |
| HBL-24 | AMBIGUOUS / MULTI-REGIME | RANGE → BREAKOUT_UP → CHANNEL_UP → CHANNEL_DOWN → CHANNEL_UP; range inițial aproximativ 2307–2321. |

## Concluzie vizuală a CEO-ului

Ferestrele arată că piața nu trebuie redusă la o singură etichetă pe intervale lungi. Multe ferestre conțin secvențe de tip range → manipulare/sweep → breakout/expansiune → canal → range nou. Detectorul trebuie evaluat atât pe segmentele locale, cât și pe tranzițiile dintre ele; o singură etichetă pentru întreaga fereastră ar pierde informație importantă.

## Reguli pentru consumator

1. Nu prezenta acest lot drept blind sau independent: este `CEO_ASSISTED`.
2. Nu folosi aceste etichete pentru alegerea parametrilor și apoi pentru validarea acelorași parametri pe același lot.
3. Păstrează etichetele multi-regime ca secvențe; nu le colapsa automat la RANGE sau TREND.
4. HBL-20 este doar un candidat semantic de strategie. Necesită definiție cauzală, test separat, costuri și control al multiplicității înainte de orice implementare live.
5. Raportează separat potrivirea detectorului pe RANGE pur, CHANNEL pur, secvențe multi-regime și tranziții/sweep-uri.
