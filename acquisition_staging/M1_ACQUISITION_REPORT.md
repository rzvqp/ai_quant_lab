# M1 ACQUISITION — RAPORT DE ACOPERIRE REALĂ

**Divizie:** Data Acquisition · **Instrument:** OANDA:XAUUSD · **Timeframe:** M1 (1 minut)
**Data:** 2026-08-04 · **Ordin:** CEO — "achiziționează M1, inventarul e acceptat, decizia e luată în cunoștință de cauză"
**Status livrare:** în CARANTINĂ (`acquisition_staging/OANDA_XAUUSD_M1.csv`) · **format 6 coloane** (ca M5)

> ## ⛔ UNFIT FOR VALIDATION
> Un singur regim (bull, ~1 an, fereastră rulantă) · cost/R prohibitiv (11–28% vs ~3% pe M15).
> **Utilizare defensabilă: strat de execuție/confirmare pe fereastra recentă — NICIODATĂ bază de
> backtest / validare de edge.** NU s-a segmentat. NU s-a derivat HTF (per ordin — structura o decide Statisticianul).

---

## 1. Integritate + invariant de contabilitate

| Metrică | Valoare |
|---|---|
| **sha256** | `8387296e06839938c8c130e8b946701c1a9d9bd9d82c3ad13ba55672a08c10d1` |
| Bare | **354.177** |
| Timpi distincți | 354.177 (duplicate: **0**) |
| Strict crescător (sortat, unic) | **True** |
| Prima bară | `1754266140` — **2025-08-04 00:09:00Z** |
| Ultima bară | `1785848220` — **2026-08-04 12:57:00Z** |
| Span | 365,5 zile (**1,00 an**) |
| Dimensiune fișier | 17.293.385 bytes (~17 MB) |

**Invariant de contabilitate (fail-closed):**
`present 354.177 + missing_slots 172.192 == nominal grid 526.369` → **True**
(fiecare slot de pe grila de 1 minut între prima și ultima bară este ori prezent, ori contabilizat ca lipsă — fără scurgeri).

Hash-ul a fost calculat cu **Python `hashlib`** (nu shell), citind fișierul în mod binar.

## 2. Acoperire reală (goluri + continuitate)

| Metrică | Valoare |
|---|---|
| **Podeaua (cea mai adâncă bară)** | **2025-08-04 00:09:00Z** — re-măsurată LIVE de walk (replay a refuzat sub, DATA_UNAVAILABLE) |
| Goluri de weekend | 63 |
| Goluri intra-săptămână > 1 bară | 225 |
| **Continuitate** | 354.177 prezente / 526.369 nominal = **67,3%** |

Continuitatea de 67,3% **NU este date lipsă/netezite** — golurile sunt:
1. **Weekend-uri** (piața închisă vineri seara → duminică seara),
2. **Fereastra de mentenanță OANDA la 21:00Z** (vizibilă în harta orară: 21:00 cade la ~1/3),
3. Sărbători (ex. Crăciun 24–25 dec, Anul Nou 31 dec–1 ian).

Cele mai lungi 10 goluri intra-săptămână (toate explicabile prin sărbători/mentenanță):

| De la | Până la | Durată |
|---|---|---|
| 2025-12-24 18:44Z | 2025-12-25 23:04Z | 1700 min (Crăciun) |
| 2025-12-31 21:59Z | 2026-01-01 23:04Z | 1505 min (Anul Nou) |
| 2025-09-01 18:29Z | 2025-09-01 22:04Z | 215 min (Labor Day US) |
| 2026-01-19 19:29Z | 2026-01-19 23:04Z | 215 min (MLK Day) |
| 2026-02-16 19:29Z | 2026-02-16 23:04Z | 215 min (Presidents' Day) |
| 2026-05-25 18:29Z | 2026-05-25 22:04Z | 215 min (Memorial Day) |
| 2026-01-06 21:58Z | 2026-01-06 23:04Z | 66 min |
| 2025-08-04 20:59Z | 2025-08-04 22:04Z | 65 min (mentenanță) |
| ... | ... | ~65 min (mentenanță zilnică) |

**Harta orară** (bare/oră UTC) confirmă acoperire uniformă 00:00–20:00Z (~15.500 bare/oră), cădere la 21:00Z (mentenanță, 4.984) și revenire graduală 22:00–23:00Z.

## 3. Consistență încrucișată (M1 → M5 agregat vs M5 existent)

Control independent: agregez M1 în bucket-uri de 5 minute și compar cu fișierul M5 real din `data/market/`.

| Metrică | Valoare |
|---|---|
| Bucket-uri de 5 min complete comparate | 69.179 |
| Bucket-uri incomplete sărite | 282 |
| **Nepotriviri OHLC (EXACT)** | **0** |
| Nepotriviri de volum | 6 |
| **VERDICT CONSISTENȚĂ (OHLC)** | **PASS** |

OHLC-ul agregat din M1 reproduce **exact** M5-ul independent pe ~69k bucket-uri → cele două trageri (M1 nouă, M5 veche) descriu aceeași piață bar-cu-bar. Cele **6 nepotriviri de volum** (din 69.179 = 0,009%) sunt reziduu minor la marginile bucket-urilor de weekend/mentenanță; **OHLC-ul, care contează pentru orice logică de preț, e curat**. Raportat transparent, nemascat.

## 4. De ce UNFIT FOR VALIDATION — cost/R măsurat direct

Amplitudinea barei (high−low) pe M1, măsurată pe cele 354k bare:

| Sesiune | n | Median (pt) | IQR (25–75) |
|---|---|---|---|
| Asia | 124.310 | 1,745 | [1,115 – 2,740] |
| London | 77.650 | 1,675 | [1,095 – 2,615] |
| NY | 122.622 | 2,000 | [1,190 – 3,305] |
| Late | 29.595 | 1,340 | [0,740 – 2,420] |
| **ALL** | 354.177 | **1,775** | [1,100 – 2,880] |

**Cost/R** la stop = 1× amplitudinea mediană:

| Spread | cost/R |
|---|---|
| $0,20/oz | **11%** |
| $0,30/oz | **17%** |
| $0,50/oz | **28%** |

Pe M15 costul echivalent e ~3%. Pe M1 e de 4–9× mai mare — **confirmă ordinul de mărime ~40% citat de CEO și ucide orice edge cu RR asimetric.** Aceasta este cauza mecanică a verdictului UNFIT, nu o opinie.

## 5. Ce NU s-a făcut (per ordin explicit)

- ❌ **NU s-a segmentat** în blocuri de regim (discovery/quarantine/sealed).
- ❌ **NU s-a derivat HTF** din M1.
- ❌ **NU s-a atins** M15_v2 / M5 / H1 / `split_manifest.json`.
- ❌ **NU s-a injectat** nimic în manifest — structura M1 (dacă vreuna) o decide **Statisticianul**.

Livrare = fișier brut în carantină + acest raport + verificatorul reproductibil (`verify_m1.py`).

## 6. Reproducere

```bash
cd ai_quant_lab-data-acq
python acquisition_staging/verify_m1.py \
  --m1 acquisition_staging/OANDA_XAUUSD_M1.csv \
  --m5 data/market/OANDA_XAUUSD_M5.csv
```

Tragerea a folosit puller-ul reparat (`pullers/pull_replay.mjs`, overlap=5, adaptive stall recovery). Podeaua a fost confirmată automat: `reachedFloor=true`, cea mai adâncă bară stabilă la 2025-08-04 00:09Z, sleep adaptiv escaladat la 12000ms fără resume manual.
