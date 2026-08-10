# MONITOR DE ȘTIRI LIVE — INVENTAR (înainte de a construi)

**Divizie:** Data Acquisition · **Sursă:** `https://www.forexfactory.com/news` · **Data:** 2026-08-10
**Status:** INVENTAR + gate. NU s-a construit procesul. Separat de calendar. Nu în manifest.

---

## VERDICT DE SUS

| Verificare | Răspuns |
|---|---|
| **1. Feed structurat?** | **NU.** `/news/rss`→301→HTML, `/rss`,`/feed`,`news.php?do=rss`→HTML, `rss.php`→404, `nfs.faireconomy.media/ff_news_*`→404. **Trebuie parsată pagina HTML.** |
| **2. Rată / acces** | robots.txt = niciun `Disallow`. `/news` întoarce 200 + HTML real (~270KB) cu UA de browser, fără challenge. DAR `Cache-Control: private`, `cf-cache-status: DYNAMIC`, **fără ETag/Last-Modified** → GET condiționat NU ajută; fiecare poll = descărcare completă. Cloudflare emite `__cf_bm` (bot-management). |
| **3. Timestamp** | **Relativ** în stream ("22 min ago"). Timp absolut există DOAR în caruselul hot-stories (`title="Aug 10, 2026 3:07pm"`), nu pe știrile din stream. Pagina poartă un `data-timestamp` global = ora de render a serverului (ancoră de citire autoritară). |

**Concluzie:** nu există feed; **e scraping**, funcționează acum, dar are fragilități reale (mai jos). Mă opresc la gate per instrucțiunea "RAPORTEAZĂ înainte de a construi".

---

## 1. Feed structurat — NU EXISTĂ

| URL testat | Rezultat |
|---|---|
| `nfs.faireconomy.media/ff_news_thisweek.{xml,json}` | 404 (calendarul are echivalent, știrile NU) |
| `forexfactory.com/rss.php`, `/ff_news.xml`, `/news.xml` | 404 |
| `/news/rss` | 301 → `/news` (HTML) |
| `/rss`, `/feed`, `news.php?do=rss` | 200 dar `text/html` (pagina, nu XML) |

Spre deosebire de calendar (care are `nfs.faireconomy.media` cu JSON/CSV/XML/ICS), **știrile nu au niciun export**. Singura cale = parsarea `/news`.

## 2. Acces & rată

- **robots.txt:** doar linie `Sitemap`, **niciun `Disallow`** → nimic interzis.
- **/news:** HTTP 200, ~270KB HTML server-rendered, conținut real cu UA de browser (fără JS-challenge acum). Setează cookie `__cf_bm` (Cloudflare bot management) + cookies de sesiune.
- **Fără cache util:** `Cache-Control: private`, `cf-cache-status: DYNAMIC`, **fără ETag, fără Last-Modified**. GET condiționat inutil → 288 poll-uri/zi × ~270KB ≈ **~78 MB/zi**, fiecare descărcare completă.
- 5 min e o cadență blândă; robots permite. **Nu opresc — dar recomand persistarea cookie-urilor `__cf_bm` între poll-uri și un UA de browser stabil.**

## 3. Timestamp — convenție declarată

- Stream principal: **doar relativ** ("22 min ago", "1 hr 46 min ago"). 0/35 știri din stream au timp absolut.
- Ancoră autoritară: `data-timestamp` global al paginii = ora de render a serverului (epoch UTC), identică pe toată pagina.
- **Convenție (de persistat):** `read_ts` = `data-timestamp` al paginii (sau ora locală de fetch dacă lipsește); `deduced_ts` = `read_ts − parse("X min/hr ago")`. **Precizie limitată de intervalul de poll (±5 min).** Persist AMBELE, plus textul relativ brut, ca nimic să nu se piardă.

---

## FRAGILITATE (răspuns direct: "spune-o")

**Extragere fiabilă (dovedit pe 35 știri din stream):** ID (din `/news/<ID>-slug`), titlu, sursă, timp relativ = **35/35**. Dedup pe ID = solid.

**Fragil:**
1. **Detecția impactului.** Impactul (roșu/High) e o iconiță `svg-img--impact-ff-high` (fișier `impact/ff/high.svg`) prezentă **doar pe ~17% din știri** (în snapshot: 1 High, 5 Low, 29 fără impact în stream + caruselul hot-stories). Asocierea impact→știre se face prin **proximitate în DOM/clase CSS**. Dacă ForexFactory redenumește clasele sau restructurează DOM-ul, parserul returnează tăcut `impact=none` → **alerte High RATATE fără eroare vizibilă.** Acesta e riscul principal.
2. **Cloudflare.** Merge acum cu UA de browser, dar bot-management-ul (`__cf_bm`) poate escalada la un JS-challenge ("Just a moment...") → `curl` cedează. Nedetectat, ar opri tăcut fluxul de alerte.
3. **Fără contract stabil.** Spre deosebire de JSON-ul calendarului (schemă declarată), HTML-ul e o suprafață de prezentare care se poate schimba oricând.

**Mitigări propuse (dacă aprobi construcția):**
- **Canar de selector:** dacă N poll-uri consecutive găsesc 0 iconițe de impact pe întreaga pagină (când istoric erau >0), alertă "PARSER POSIBIL RUPT" pe Telegram — ca o detecție tăcută să devină zgomotoasă.
- **Detecție challenge:** dacă răspunsul conține "Just a moment"/`cf-mitigated` sau nu conține `news-block__item`, alertă "ACCES BLOCAT" și nu marca poll-ul ca reușit.
- **Persistă cookie-urile** `__cf_bm` + UA stabil; onorează 5 min.
- **Persistă read_ts + deduced_ts + relativ brut**; dedup pe ID; la repornire citește ID-urile deja anunțate.

---

## DACĂ APROBI — ce aș construi (ca `spread_collection`)

Proces permanent detașat, în `acquisition_staging/news/`, **separat de calendar**:
- La 5 min: fetch `/news` (cookies persistente) → parse stream → dedup pe ID.
- Persistă **TOATE** știrile: `id, titlu, sursa, impact, deduced_ts, read_ts, url, anuntat(bool)` (+ relativ brut) în `NEWS_LEDGER.csv` (append-only) + ID-urile anunțate în `announced_ids.txt`.
- Telegram DOAR pe High: `[NEWS HIGH] titlu / sursă, timp / link`.
- Canar de selector + detecție challenge + heartbeat.
- Nu atinge celelalte 5 procese, nu atinge captura de calendar, nu în manifest.

**Aștept go/no-go.** Recomandare: **construiește-l cu mitigările** — funcționează acum, iar canarul + detecția de challenge transformă cele două fragilități tăcute în alerte zgomotoase, deci nu ratăm în tăcere.
