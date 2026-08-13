# Inventar date mai noi decât 2025-10 (2025-11 → prezent) + propunere segment forward

**Divizie:** Data Acquisition · **Data:** 2026-08-13 · **Instrument:** OANDA:XAUUSD.
Datele EXISTĂ deja în M15_v2 și M5 (fișierele merg până în 2026-07-27). Întrebarea nu e achiziție — e **ce se poate desigila și în ce condiții**. **NU am desigilat nimic.** Propun; Statisticianul decide. Manifestul nu e atins.

---

## 1. Inventar (structură, nu comportament) — coadă M15_v2 / M5 după discovery (2025-10-12)

| Segment | M15_v2 bare | M5 bare | Interval | Span | Continuitate | Invariant contabilitate |
|---|---|---|---|---|---|---|
| **EMBARGO** 2025-10-12→2025-11-02 | 1.375 | 4.125 | ..2025-10-31 20:45 | 18,9d (~20,8d calendar) | 75,8% | **TRUE** |
| **SEALED** 2025-11-02→2026-07-27 | 17.193 | 51.577 | ..2026-07-27 16:15 | 266,7d (~8,9 luni) | 67,1% | **TRUE** |
| **Total nou** (post-discovery) | 18.568 | 55.702 | 2025-10-12→2026-07-27 | 287,7d | 67,2% | **TRUE** |

Continuitatea 67,1% **NU e goluri de date** — sunt weekend-uri + fereastra de mentenanță OANDA 21:00Z + sărbători (cele mai lungi goluri intra-săptămână: Crăciun 28,5h, Anul Nou 25,2h — normale). Invariantul `present + missing_slots == nominal grid` = **TRUE** pe fiecare segment.

## 2. Integritate & compatibilitate — CONFIRMATE

- **Aceeași sursă/convenție ca M15_v2:** coada e chiar în fișierele existente `OANDA_XAUUSD_M15.csv` / `M5.csv` (aceeași grilă 15m/5m, timestamp UTC, 6 coloane OHLCV) — nimic de re-achiziționat, e continuarea aceluiași feed.
- **Invariant de contabilitate:** TRUE pe embargo + sealed + total (fiecare slot e ori prezent, ori contabilizat).
- **Hash de conținut (referință versionare, times-only ale cozii sealed):** M15_v2 `5720c773…`, M5 `52b2c84b…`. Hash-ul autoritar rămâne cel al fișierului complet din manifest (`57f4ed95…` M15_v2, `cbb6eebe…` M5); coada e parte din el.

## 3. Propunere segment forward recent (granițe, clasificare, rol)

Split al SEALED-ului (2025-11-02→2026-07-27, ~8,9 luni) în trei, oglindind structura manifestului (discovery / embargo / sealed):

| Rol | Interval propus | M15_v2 | M5 | Rol declarat |
|---|---|---|---|---|
| **RECENT DISCOVERY** | 2025-11-02 → 2026-04-08 (~5,2 luni) | 9.993 | 29.959 | Optimizare/cercetare pe relevanța recentă 2026 |
| **EMBARGO** | 2026-04-08 → 2026-04-29 (~20,8d) | 1.380 | 4.140 | Bandă anti-leakage între discovery și validare |
| **FORWARD VALIDATION** | 2026-04-29 → 2026-07-27 (~3 luni) | 5.820 | 17.478 | **REZERVAT — holdout forward, NICIODATĂ optimizat** |

**Cât se rezervă și de ce: ~34% (cel mai recent trimestru) pentru forward validation.**
- Rezerva = **cel mai recent** trimestru → cel mai onest test al relevanței în 2026 (out-of-sample pe cele mai noi date).
- 5.820 bare M15 / 17.478 bare M5 = suficient pentru un test forward cu putere rezonabilă (mii de bare).
- ~59% discovery recent + ~7% embargo. Alpha optimizează DOAR pe RECENT DISCOVERY; **nu are voie** să atingă FORWARD VALIDATION.
- Banda de embargo ~20,8d (aceeași convenție ca 2025-10-12→2025-11-02) previne leakage-ul peste graniță.

*(Granițele exacte le fixează Statisticianul; propun fracțiile și rolurile.)*

## 4. Ce ar cere DESIGILAREA (guvernanță — nu achiziție)

Datele sunt SEALED deliberat: erau **holdout-ul** pentru munca de discovery existentă (până 2025-10-12). Desigilarea are un COST și cere:
1. **Decizia Statisticianului** de a re-clasifica banda (embargo→? , sealed→ recent-discovery + noul forward-holdout) — el deține manifestul.
2. **Versionare în manifest ÎNAINTE de orice utilizare:** un nou segment cu hash de conținut, granițe explicite, clasificare (discovery/embargo/forward-validation) și rol declarat. Fără asta, orice adăugare la fereastra de discovery e TACITĂ = interzisă.
3. **Pre-înregistrare** că Alpha optimizează exclusiv pe RECENT DISCOVERY, iar FORWARD VALIDATION rămâne sigilat până la un test forward pre-declarat.
4. **Recunoașterea costului:** partea desigilată **nu mai poate valida candidații VECHI** (holdout-ul lor pentru 2025-10 e parțial consumat). Desigilarea pentru relevanță-recentă sacrifică folosirea acelei porțiuni ca holdout al muncii vechi.

**NU am desigilat nimic.** Livrez inventarul + propunerea; decizia de guvernanță e a Statisticianului/CEO.

---

## Rămas din mandatul anterior — fereastra neagră: REZOLVATĂ
Ambele task-uri pe `pythonw.exe` (zero consolă). `AIQuantLab_NewsMonitor`: State Ready, `LastResult=0x0`, `news_monitor.log` crește la 300s (cicluri curate, fără crash, fără fereastră). `AIQuantLab_CalendarWeeklyCapture`: pe pythonw, `0x00041303` = „nu a rulat încă de la re-înregistrare" (rulează luni 07:00 pe pythonw). Confirmat rezolvat.
