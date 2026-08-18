# TABEL SEGMENT-CU-SEGMENT — `HBL-01 … HBL-24`

**Sursa etichetelor:** `RANGE_HUMAN_LABEL_BATCH_01_CEO_ASSISTED_RESULTS.md` — proveniență **`CEO_ASSISTED`**.
**Detector:** `ve_n1_replay 0.3.1`, config pinuit `w_atr = 0,30` / `s_max = 0,60`, fingerprint `432170ff…`,
480 bare de încălzire înainte de fiecare fereastră. **Rulat exclusiv pentru DIAGNOSTIC.**

> Segmentele CEO nu au timestamp-uri, deci potrivirea e la nivel de **fereastră** — „detectorul a produs
> vreodată starea X aici" — nu la nivel de bară. `Început prea târziu` și `închis prea devreme` NU se pot
> măsura fără granițe de segment; sunt raportate ca element deschis, nu estimate.

```
66 segmente etichetate · 37 OMISE (56%) · 18 parțiale · restul tranziții/sweep-uri fără stare
```

| HBL_ID | segment | eticheta CEO | iesire detector (bare) | potrivire | defect semantic | actiune recomandata |
|---|---|---|---|---|---|---|
| `HBL-01` | S1 | `RANGE` | RANGE 0 · CANAL 0 · INDISP 89/96 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-02` | S1 | `CHANNEL_DOWN` | RANGE 0 · CANAL 0 · INDISP 73/96 | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-03` | S1 | `AMBIGUOUS` | RANGE 0 · CANAL 0 · INDISP 268/288 | - | neclasificabil | - |
| `HBL-04` | S1 | `RANGE` | RANGE 0 · CANAL 0 · INDISP 268/288 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-05` | S1 | `CHANNEL_UP` | RANGE 0 · CANAL 0 · INDISP 426/480 | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-05` | S2 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-05` | S3 | `BREAKOUT_DOWN` | ^ | - | 36 ruperi ACCEPTATE intr-o fereastra unde CEO vede UNA | acceptarea trebuie separata de invalidare |
| `HBL-05` | S4 | `CHANNEL_UP` | ^ | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-06` | S1 | `RANGE` | RANGE 0 · CANAL 4 · INDISP 404/480 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-06` | S2 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-06` | S3 | `CHANNEL_UP` | ^ | partial | partial: 4 bare de canal | prelungirea starii |
| `HBL-07` | S1 | `RANGE` | RANGE 0 · CANAL 0 · INDISP 87/96 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-08` | S1 | `RANGE` | RANGE 0 · CANAL 0 · INDISP 89/96 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-09` | S1 | `RANGE` | RANGE 0 · CANAL 4 · INDISP 260/288 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-09` | S2 | `CHANNEL_UP` | ^ | partial | partial: 4 bare de canal | prelungirea starii |
| `HBL-09` | S3 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-10` | S1 | `RANGE` | RANGE 0 · CANAL 0 · INDISP 264/288 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-10` | S2 | `CHANNEL_UP` | ^ | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-11` | S1 | `CHANNEL_UP` | RANGE 0 · CANAL 17 · INDISP 397/480 | partial | partial: 17 bare de canal | prelungirea starii |
| `HBL-11` | S2 | `CHANNEL_DOWN` | ^ | partial | partial: 17 bare de canal | prelungirea starii |
| `HBL-11` | S3 | `BREAKOUT_UP` | ^ | - | 34 ruperi ACCEPTATE intr-o fereastra unde CEO vede UNA | acceptarea trebuie separata de invalidare |
| `HBL-11` | S4 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-12` | S1 | `CHANNEL_UP` | RANGE 0 · CANAL 0 · INDISP 438/480 | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-12` | S2 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-12` | S3 | `CHANNEL_DOWN` | ^ | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-13` | S1 | `CHANNEL_UP` | RANGE 0 · CANAL 0 · INDISP 90/96 | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-14` | S1 | `CHANNEL_UP` | RANGE 0 · CANAL 0 · INDISP 90/96 | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-14` | S2 | `CHANNEL_DOWN` | ^ | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-14` | S3 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-15` | S1 | `RANGE` | RANGE 0 · CANAL 0 · INDISP 259/288 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-15` | S2 | `SWEEP_FAILED_BREAKOUT_UP` | ^ | - | eveniment emis de 4 ori, dar NU exista stare de sweep | stare LIQUIDITY_SWEEP_UP/DOWN distincta |
| `HBL-15` | S3 | `BREAKOUT_DOWN` | ^ | - | 23 ruperi ACCEPTATE intr-o fereastra unde CEO vede UNA | acceptarea trebuie separata de invalidare |
| `HBL-15` | S4 | `CHANNEL_DOWN` | ^ | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-16` | S1 | `RANGE` | RANGE 0 · CANAL 0 · INDISP 267/288 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-16` | S2 | `BREAKOUT_DOWN` | ^ | - | 21 ruperi ACCEPTATE intr-o fereastra unde CEO vede UNA | acceptarea trebuie separata de invalidare |
| `HBL-16` | S3 | `CHANNEL_DOWN` | ^ | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-16` | S4 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-17` | S1 | `RANGE` | RANGE 0 · CANAL 32 · INDISP 321/480 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-18` | S1 | `CHANNEL_UP` | RANGE 4 · CANAL 13 · INDISP 387/480 | partial | partial: 13 bare de canal | prelungirea starii |
| `HBL-18` | S2 | `RANGE` | ^ | partial | partial: doar 4 bare RANGE_STATE in fereastra | prelungirea starii |
| `HBL-18` | S3 | `CHANNEL_DOWN` | ^ | partial | partial: 13 bare de canal | prelungirea starii |
| `HBL-18` | S4 | `RANGE` | ^ | partial | partial: doar 4 bare RANGE_STATE in fereastra | prelungirea starii |
| `HBL-18` | S5 | `BREAKOUT_UP` | ^ | - | 38 ruperi ACCEPTATE intr-o fereastra unde CEO vede UNA | acceptarea trebuie separata de invalidare |
| `HBL-18` | S6 | `RANGE` | ^ | partial | partial: doar 4 bare RANGE_STATE in fereastra | prelungirea starii |
| `HBL-19` | S1 | `CHANNEL_UP` | RANGE 0 · CANAL 0 · INDISP 89/96 | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-19` | S2 | `BREAKDOWN_DOWN` | ^ | - | 6 ruperi ACCEPTATE intr-o fereastra unde CEO vede UNA | acceptarea trebuie separata de invalidare |
| `HBL-19` | S3 | `CHANNEL_UP` | ^ | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-19` | S4 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-20` | S1 | `RANGE_ACUMULARE` | RANGE 0 · CANAL 8 · INDISP 62/96 | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-20` | S2 | `SWEEP_DOWN` | ^ | - | eveniment emis de 1 ori, dar NU exista stare de sweep | stare LIQUIDITY_SWEEP_UP/DOWN distincta |
| `HBL-20` | S3 | `MARKUP_UP` | ^ | partial | partial: 8 bare de canal | prelungirea starii |
| `HBL-20` | S4 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-21` | S1 | `BREAKDOWN_DOWN` | RANGE 0 · CANAL 0 · INDISP 267/288 | - | 21 ruperi ACCEPTATE intr-o fereastra unde CEO vede UNA | acceptarea trebuie separata de invalidare |
| `HBL-21` | S2 | `RANGE_ACUMULARE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-21` | S3 | `BREAKOUT_UP_CHANNEL_UP` | ^ | NU | SEGMENT OMIS — detectorul nu clasifica nici macar canalul | episodul moare inainte de clasificare |
| `HBL-22` | S1 | `CHANNEL_UP` | RANGE 0 · CANAL 13 · INDISP 195/288 | partial | partial: 13 bare de canal | prelungirea starii |
| `HBL-22` | S2 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-22` | S3 | `CHANNEL_UP` | ^ | partial | partial: 13 bare de canal | prelungirea starii |
| `HBL-23` | S1 | `CHANNEL_DOWN` | RANGE 0 · CANAL 9 · INDISP 382/480 | partial | partial: 9 bare de canal | prelungirea starii |
| `HBL-23` | S2 | `CHANNEL_UP` | ^ | partial | partial: 9 bare de canal | prelungirea starii |
| `HBL-23` | S3 | `RANGE` | ^ | NU | SEGMENT OMIS — zero bare RANGE_STATE in toata fereastra | segmentare longitudinala + ancore locale |
| `HBL-24` | S1 | `RANGE` | RANGE 12 · CANAL 73 · INDISP 322/480 | partial | partial: doar 12 bare RANGE_STATE in fereastra | prelungirea starii |
| `HBL-24` | S2 | `BREAKOUT_UP` | ^ | - | 28 ruperi ACCEPTATE intr-o fereastra unde CEO vede UNA | acceptarea trebuie separata de invalidare |
| `HBL-24` | S3 | `CHANNEL_UP` | ^ | partial | partial: 73 bare de canal | prelungirea starii |
| `HBL-24` | S4 | `CHANNEL_DOWN` | ^ | partial | partial: 73 bare de canal | prelungirea starii |
| `HBL-24` | S5 | `CHANNEL_UP` | ^ | partial | partial: 73 bare de canal | prelungirea starii |
