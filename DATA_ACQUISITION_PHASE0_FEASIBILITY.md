# DATA ACQUISITION — FAZA 0: RAPORT DE FEZABILITATE

**Divizie:** Data Acquisition · **Instrument:** OANDA:XAUUSD (sursă unică, neschimbată)
**Data:** 2026-07-25 · **Status:** FEZABILITATE — nu s-a tras / salvat nimic
**Metodă:** replay-walk read-only prin `tradingview-mcp` (CDP :9222), identică cu mecanismul `pull_replay_m15.mjs`

> Disciplină respectată: nu s-a scris niciun CSV, nu s-a citit/calculat niciun OHLC, nu s-a rulat niciun
> edge/indicator. Probele au citit **doar** epoch-ul primei/ultimei bare + numărul de bare. Datele
> pre-2022-12-16 rămân nevăzute la nivel de comportament.

---

## Rezultat de titlu (decizie CEO necesară)

1. **Ținta M5 la 2018 este IMPOSIBILĂ prin OANDA/TradingView.** Podeaua M5 verificată = **2021-07-22**.
   Se pot obține ~5 ani de M5, nu ~8. Lipsesc ~3,5 ani față de ținta minimă.
2. **M1 acoperă doar ~1 an** (podea 2025-07-24). §9.2 cere M1 ca rezoluție de execuție — deci §9 devine
   testabil, dar numai pe ~12 luni. E puțin pentru sample-size + corecții multiple-testing (§9.5).
3. **Oportunitate mare pe TF mari:** M15 merge înapoi până la **2011-07** (~15 ani) și H1 până la
   **2006-03** (~20 ani). Asta închide complet golul Tier-0 (~5-6 ani ceruți de protocol §2) și îl
   depășește de ~2-3×.

---

## Q1 — Poate `pull_replay_m15.mjs` să tragă M5? Ce modificări cere?

**Da, mecanismul funcţionează** (confirmat live: replay-walk M5 coboară fereastră cu fereastră).
Modificări necesare:

| # | Modificare | Detaliu |
|---|---|---|
| 1 | `TF='15'` → `'5'` | script/parametru separat per timeframe |
| 2 | `TARGET` | acum `2023-01-01`; de setat la podeaua reală (M5: 2021-07-22) sau la start dorit |
| 3 | `OUT` | fişier **nou** `OANDA_XAUUSD_M5.csv`; NU atinge fişierele existente |
| 4 | **CRITIC — walk-ul actual e rupt de întărirea replay** | `pull_replay_m15` cere `replay.start({date: dstr})` cu `dstr` = zi la miezul nopţii (`slice(0,10)`). Noul `replay.start` (commit `c839e91`) e **fail-closed**: miezul nopţii nu e bară validă → toast „Data point unavailable" → **throw**. `try/catch` îl înghite → walk se opreşte prematur ca „stale". **Fix:** cere timestamp-ul exact al celei mai vechi bare (ex. `(oldest-1)*1000`), aşa cum face proba `probe_floor.mjs`. |
| 5 | Plafon iteraţii | `iter<400` insuficient pentru M5 (~1200 iteraţii); ridică la ~2000 |
| 6 | (opţional) lărgire fereastră | replay livrează exact **300 bare/iteraţie**; dacă se măreşte zoom-ul/lăţimea înainte de citire, se pot obţine mai multe bare/iteraţie şi timpul de tragere scade proporţional |

---

## Q2/Q3/Q4 — Cât istoric e efectiv disponibil (VERIFICAT, nu presupus)

Fiecare podea a fost găsită prin walk iterativ până la blocaj de ≥3 încercări (M1/M5/M15) sau single-seek
adânc (H1). Single-seek subestimează uşor (M5: 2021-07-25 vs. podea reală 2021-07-22), deci podelele
iterative sunt cele de încredere.

| TF | Podea verificată (UTC) | Istoric total | Metodă | Nou faţă de setul actual |
|----|------------------------|---------------|--------|--------------------------|
| **M1** | **2025-07-24 16:00** | ~1,0 an | iterativ, blocaj confirmat | tot (nu există M1 deloc) |
| **M5** | **2021-07-22 19:00** | ~5,0 ani | iterativ, blocaj confirmat | tot (nu există M5 deloc) |
| **M15** | **2011-07-25 16:30** | ~15 ani | iterativ, blocaj confirmat | ~11,4 ani înainte de 2022-12-16 |
| **H1** | **2006-03-19 ~20:00** | ~20 ani | single-seek (de reconfirmat iterativ) | ~16,8 ani înainte de 2023-01-02 |

- **Q3 (M1):** confirmat — fereastră rulantă de ~365 zile. Podeaua se va deplasa în timp cu „azi".
- **Q4 (extindere M15 înainte de 2022-12-16):** **DA.** Setul actual s-a oprit la 2022-12-16 doar din
  cauza `TARGET=2023-01-01` din script — **nu** din limita furnizorului. Podeaua reală M15 = 2011-07-25.

## Q5 — Volum estimat (ancoră: M15 existent = 23.556 bare/an, 50,6 bytes/bară)

| Set de tras | Interval | Bare (~) | Dimensiune (~) | Iteraţii (~) |
|-------------|----------|----------|----------------|--------------|
| **M5** | 2021-07-22 → azi | **351k** | 17,8 MB | 1.170 |
| **M1** | 2025-07-24 → azi | **342k** | 17,3 MB | 1.140 |
| **M15 extindere** | 2011-07 → 2022-12 | **268k** | 13,6 MB | 895 |
| **H1 extindere** | 2006-03 → 2023-01 | **132k** | 6,7 MB | 439 |

## Q6 — Timp de tragere · rate limiting · blocări

- **Timp** (la 300 bare/iter, ~2,6 s/iter, seed lângă podea): M5 ~**50 min**, M1 ~**50 min**,
  M15-ext ~**40 min**, H1-ext ~**20 min**. Adaugă +30-50% marjă pentru goluri/retry/modal →
  planifică **~1-1,5 h/timeframe**, total **~4-5 h** dacă se trag toate patru.
- **Rate limiting HTTP:** niciunul observat — tragerea e prin UI/CDP, nu prin API cu cote.
- **Blocări reale de gestionat în Faza 1:**
  1. modalul „Continue your last replay?" (deja tratat de `replay.start` întărit);
  2. toast-uri „Data point unavailable" la goluri/weekend → necesită retry + cerere de timestamp exact;
  3. TradingView Desktop trebuie să rămână viu/în prim-plan câteva ore;
  4. bug-ul Q1#4 trebuie reparat înainte de orice tragere, altfel walk-ul se opreşte prematur.

---

## Recomandare (nu execut — aştept aprobarea intervalului)

- **M5:** trage tot ce există: **2021-07-22 → azi** (nu se poate atinge 2018; nu are rost un TARGET mai
  vechi decât podeaua).
- **M1:** trage tot: **2025-07-24 → azi** (~1 an — util pentru §9, dar CEO trebuie să ştie limita).
- **M15/H1:** extindere de mare valoare şi cost mic; recomand **M15 → 2011-07** şi **H1 → 2006-03**.
- Ordine sugerată după raport valoare/cost: **M5 → M1 → M15-ext → H1-ext.**

**Aştept aprobarea explicită a intervalului per timeframe înainte de Faza 1.**
