# CALENDAR ECONOMIC FOREXFACTORY — INVENTAR (înainte de a trage tot)

**Divizie:** Data Acquisition · **Sursă:** ForexFactory export via `nfs.faireconomy.media`
**Data:** 2026-08-04 · **Status:** INVENTAR + snapshot săptămâna curentă (singurul disponibil).
**NU s-a integrat în manifest. NU s-a filtrat la achiziție** (toate monedele, toate impacturile).

---

## VERDICT DE SUS

| Întrebare | Răspuns scurt |
|---|---|
| **1. Fus orar** | JSON = timestamp absolut cu offset explicit `-04:00` (America/New_York, EDT). CSV/XML = aceleași instanțe în **UTC**, dar **fără marcaj de fus în fișier** (capcană). Reconciliat pe toate 98 evenimentele, 0 mismatch. **Recomand JSON.** |
| **2. Revizii / lookahead** | **Exportul NU are flag de revizie ȘI NU are câmpul `actual` — în niciun format.** `previous` e un scalar fără indicație dacă e valoarea publicată inițial sau cea revizuită. **NU se poate distinge → lookahead nedetectabil din export.** |
| **3. Acoperire istorică** | **Doar `thisweek` (HTTP 200).** `lastweek`/`nextweek`/`thismonth`/dated = **toate 404.** Fără arhivă structurată. **Descoperirea 2011-2021 e de neatins prin export.** Util doar live/forward. |

---

## 1. FUS ORAR — verificat contra NFP (oră publică 8:30 ET)

| Format | Câmp timp | Exemplu (NFP) | Fus |
|---|---|---|---|
| **JSON** | `date` ISO-8601 offset-aware | `2026-08-07T08:30:00-04:00` | **America/New_York, offset EXPLICIT** |
| **CSV** | `Date` + `Time` separate | `08-07-2026`, `12:30pm` | **UTC**, dar fără marcaj în fișier |
| **XML** | `<date>`+`<time>` (CDATA) | `08-07-2026`, `12:30pm` | **UTC**, fără marcaj |

- NFP JSON `08:30:00-04:00` = **12:30 UTC** = ora publică cunoscută a NFP → **confirmat**.
- CSV/XML dau `12:30pm` = 12:30 UTC → aceeași instanță, dar cine presupune "ora NY declarată pe pagină" greșește cu 4 ore. **Capcana pe care ai semnalat-o.**
- **Reconciliere sistematică:** am convertit toate cele 98 de evenimente din JSON la UTC și le-am potrivit cu timpii CSV: **98 matched / 0 mismatch → PASS.** Deci CSV/XML sunt UTC pe întreg fișierul, nu doar la NFP.
- **DST:** offset-ul JSON e per-înregistrare (`-04:00` acum, EDT). Iarna va fi `-05:00` (EST) — nu am putut verifica o săptămână de iarnă (nu există arhivă), dar fiindcă offset-ul e explicit în fiecare rând, **instanța UTC e neambiguă indiferent de sezon.** CSV/XML fiind mereu UTC nu au problema DST.
- **Convenția scrisă (în livrabil):** coloana `datetime_utc` (ISO-8601 `...Z`) este autoritatea. `date_ny`/`time_ny`/`src_offset` sunt păstrate ca proveniență a sursei.
- **Recomandare de achiziție: JSON** (offset explicit, zero ambiguitate), cu CSV alăturat doar pentru câmpul `url` (JSON nu are URL).

## 2. REVIZII — lookahead (CRITIC)

- Câmpuri în export, TOATE formatele: `title, country, date, impact, forecast, previous` (+`url`, `time` doar în CSV/XML). 
- **NU există câmp `actual`.** Pagina web afișează `actual` după release; **exportul structurat nu-l conține niciodată.** Un backtest are nevoie de `actual` (surpriza = actual − forecast mișcă prețul) → **exportul singur nu poate susține analiza de surpriză.** Actual trebuie capturat live la/după fiecare release (sau din pagină = scraping, exclus de mandat).
- **NU există flag de revizie.** Pagina marchează reviziile cu icoană; exportul o pierde. `previous` e un singur scalar, fără să spună dacă e valoarea **publicată inițial** sau cea **revizuită**.
- **Consecință:** dacă `previous` din export e valoarea revizuită, folosirea ei retroactiv într-un backtest e **lookahead**, iar din export **nu se poate distinge**. Raportat exact ca atare: **nedistingibil din export.**
- **Singura cale curată:** capturezi `thisweek` săptămână-de-săptămână și îngheți `forecast`/`previous`/`actual` **la momentul capturii** (as-of), construind propriul istoric imun la revizii retroactive. Asta e o decizie de infrastructură, nu de achiziție — o semnalez, nu o construiesc (structura o decide Statisticianul).

## 3. ACOPERIRE ISTORICĂ

| Endpoint testat | HTTP |
|---|---|
| `ff_calendar_thisweek.{json,csv,xml,ics}` | **200** |
| `ff_calendar_lastweek.json` | 404 |
| `ff_calendar_nextweek.json` | 404 |
| `ff_calendar_thismonth.json` | 404 |
| `ff_calendar_aug2.2026.json` (dated) | 404 |

- **CDN-ul servește exclusiv `thisweek`.** Fără arhivă structurată prin acest mecanism.
- Pagina `/calendar?week=` / `?month=` există, dar e **HTML → scraping**, exclus explicit de mandat ("EXPORT STRUCTURAT — nu scraping").
- **Concluzie:** pentru descoperirea **2011-2021, calendarul e inutil ca sursă istorică structurată.** E o sursă **live/forward-only**: istoricul se poate construi doar capturând `thisweek` de acum înainte. Confirmă contingența ta: "util doar live și pe M1".
- Parametrul `version` din URL-uri: **nu e necesar azi** — URL-urile simple (fără `?version=`) au întors 200. Dacă expiră, se re-verifică pe `/calendar`.

## Termeni de serviciu & rată de acces

- `robots.txt` pe `nfs.faireconomy.media`: `User-agent: * / Disallow:` → **nimic interzis.**
- Feed pe Cloudflare, header-e: `Cache-Control: public, max-age=60`, `ETag`, `Last-Modified`. Originea se împrospătează cel mult la 60 s.
- **Rată recomandată (politicoasă):** GET condiționat (`If-None-Match`/`If-Modified-Since`), **maxim 1 cerere / 60 s** (podeaua de cache; peste asta primești HIT), realist **1/oră** sau punctual în jurul release-urilor; un singur fir; User-Agent descriptiv; atribuire ForexFactory.
- *(Nu e consultanță juridică; termenii formali sunt cei ai site-ului ForexFactory. robots permite, feed-ul e public.)*

---

## STATISTICI DE UTILIZARE (filtru la UTILIZARE, stocare completă)

**Eșantion = săptămâna curentă (2026-W32).** O medie reală cere N săptămâni (doar forward).

| Metrică (această săptămână) | Valoare |
|---|---|
| Evenimente totale | 98 |
| USD total | 31 |
| **USD High / săptămână** | **4** |
| **USD Medium / săptămână** | **5** |

**USD High (ceas ET):**
- 2026-08-03 **10:00 ET** — ISM Manufacturing PMI
- 2026-08-07 **08:30 ET** — Average Hourly Earnings m/m
- 2026-08-07 **08:30 ET** — Non-Farm Employment Change
- 2026-08-07 **08:30 ET** — Unemployment Rate

**USD Medium (ceas ET):** ISM Manuf. Prices 10:00 · JOLTS 10:00 · ADP 08:15 · ISM Services 10:00 · Unemployment Claims 08:30.

**Distribuția pe oră (USD High+Medium, ET):** `08:15 ET ×1 · 08:30 ET ×4 · 10:00 ET ×4`.

- **Toate cele 9 evenimente USD High/Med cad în fereastra 08:15–10:00 ET = sesiunea NY dimineață.** Zero în Asia/London.
- **Este sistematic, prin mecanism, nu coincidență:** BLS publică la **8:30 ET** (NFP, AHE, Unemployment Rate, Claims, CPI, PPI), iar ISM/Census publică la **10:00 ET** (ISM PMI, JOLTS). Programul e fix instituțional. Eșantionul de 1 săptămână confirmă tiparul; robustețea vine din calendarul de release al agențiilor, nu din statistica pe o săptămână.
- **Implicație pentru filtrul de știri:** un filtru USD High/Med ar bloca tranzacții aproape exclusiv **08:15–10:00 ET**, adică exact deschiderea NY — nu Asia, nu London. Costul filtrului e concentrat, nu difuz.

**Distribuție completă (fără filtru):** impact `{High:8, Medium:8, Low:80, Holiday:2}` · monede `{USD:31, EUR:25, JPY:8, AUD:6, NZD:6, CNY:6, CAD:6, CHF:5, GBP:4, All:1}`.
Notă taxonomie: exportul folosește impact **`Holiday`** (nu "Non-Economic" ca pe pagină).

---

## LIVRABIL (această tragere)

Arhiva istorică **nu e disponibilă** → am tras **ce se poate** (săptămâna curentă) + inventarul. În carantină, `acquisition_staging/calendar/`:

| Fișier | sha256 | Rol |
|---|---|---|
| `ff_calendar_2026-W32_UTC.csv` | `3f41dd8a…06ee5` | **Normalizat, 10 coloane, timestamp UTC** (livrabilul) |
| `ff_calendar_2026-W32_raw.json` | `f7541d97…e543b1` | sursă brută (offset-aware) |
| `ff_calendar_2026-W32_raw.csv` | `4aaf0369…0bbd19` | sursă brută (UTC) |
| `ff_calendar_2026-W32_raw.xml` | `4685066e…bf6e23` | sursă brută (UTC) |
| `build_calendar.py` | `1b439038…e465f4` | normalizator + stats (reproductibil) |

**Coloane declarate (`ff_calendar_2026-W32_UTC.csv`):**
`datetime_utc` (autoritate, ISO-8601 Z) · `date_ny` · `time_ny` · `src_offset` · `currency` · `impact` · `event` · `forecast` · `previous` · `url`.
**Absente prin natura sursei:** `actual` (niciodată în export) și orice flag de revizie.

**NU segmentat, NU integrat în manifest.** Structura (as-of freezing, join pe `url`/event-id, politica de revizii) o decide Statisticianul.
