# ALPHA — STARE SESIUNE (ultima actualizare 2026-07-22)

## Pozitie replay (punct de pornire pentru sesiunea urmatoare)
- Simbol: OANDA:XAUUSD
- Timeframe principal: **M15**
- Replay: **2025-08-01 07:10 UTC**, manual, autoplay OFF, pre-cutoff
- Cutoff holdout: 2025-10-23. La reluare: `replay_stop` INAINTE de re-seek (defect de stale-state).

## Ce am investigat in aceasta sesiune
Anatomia multi-TF a unei singure rupturi, 2025-08-01 03:40 UTC:
- **M15**: lumanare range 6.8pt, volum 3862 — arata ca ruptura curata a benzii asiatice
- **M5**: nu e o miscare, ci 5 trepte mici, volum crescand 794 -> 1239 -> 1464
- **M1**: TOATA miscarea = **o singura lumanare** 3284.11 -> 3282.65, volum 459 vs baseline 163-219.
  Restul minutelor: derita in 2.5pt.

## Concluzie
Marimea aparenta a unei rupturi pe M15 supraestimeaza masiv activitatea concentrata care a produs-o
— aici ~60 de secunde. Lumanarea M15 urmatoare a redat integral miscarea (3283.5 -> 3291.3).
Observatie secundara: minimele M1 3281.93 / 3281.745 / 3281.785 = cluster de 3 minime aproape egale
in 5 minute — aceeasi geometrie ca DC-0007, dar la scara minutului.

## Urmatorul punct de pornire
Reia manual de la **2025-08-01 07:10 UTC pe M15**. Continua lumanare cu lumanare prin 1 august.
La orice fenomen: coboara pe M5/M1 sau urca pe H1/H4 pana intelegi constructia, apoi revino pe M15.

## Stare portofoliu
7 Discovery Candidates: DC-0002 … DC-0007 (toate FROZEN, hash verificat, index + handoff la zi).
Jurnal: intrari pana la QC-05. Fara datorii administrative deschise.
