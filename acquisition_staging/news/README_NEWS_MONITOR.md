# Monitor de știri live — proces permanent (al 6-lea)

**Decizie CEO 2026-08-10 (GO).** Alertă Telegram pe știrile ROȘII (High Impact) de pe
`forexfactory.com/news`. Nu există feed structurat → parsare HTML (vezi `NEWS_MONITOR_INVENTORY.md`).
Separat de calendar. În carantină. Nu în manifest.

## Ce face, la fiecare 5 min
- Fetch `/news` (UA de browser, **gzip**, cookie jar persistent `__cf_bm`).
- Parse stream → **dedup pe ID** din `/news/<ID>-slug`.
- Persistă **TOATE** știrile (orice impact) în `NEWS_LEDGER.csv` (append-only).
- Trimite pe Telegram **DOAR** High, format scurt:
  ```
  [NEWS HIGH] titlul
  sursa, HH:MM UTC (timp relativ brut)
  link
  ```

## Cele patru mitigări (OBLIGATORII, built-in)
1. **Canar de selector** — 0 iconițe de impact pe întreaga pagină, **N=3 poll-uri consecutive** (15 min) → alertă `[NEWS PARSER RUPT]`. *N ales astfel:* iconița de impact e o trăsătură persistentă a paginii (caruselul hot-stories are aproape mereu ≥6 iconițe); o fereastră de 15 min cu ZERO pe toată pagina e implauzibilă → 3 zerouri consecutive = semnal de rupere cu specificitate mare, latență ≤15 min. Un singur zero e tolerat (render tranzitoriu).
2. **Detecție challenge** — lipsă `news-block__item` sau "Just a moment"/`cf-mitigated`/"Attention Required" → alertă `[NEWS ACCES BLOCAT]` (o singură dată la tranziția în starea blocată, fără spam la 5 min; + `[NEWS ACCES RESTABILIT]` la revenire).
3. **Cookie `__cf_bm` persistent** — `cookies.txt` (MozillaCookieJar), încărcat/salvat la fiecare ciclu.
4. **Ambele timestamp-uri** — `read_ts_utc` (data-timestamp al paginii = ancora față de care sunt măsurate relativele) + `deduced_ts_utc` (read_ts − relativ parsat) + textul relativ brut. Precizie ±5 min (intervalul de poll).

**Motivul (CEO):** riscul principal e eșecul TĂCUT exact pe funcția pentru care există sistemul. Canarul + detecția de challenge transformă ambele eșecuri tăcute în alerte zgomotoase. La crash neașteptat: alertă `[NEWS MONITOR CRASHED]`, apoi Task Scheduler repornește — **alertez, nu repar în grabă.**

## Bandă
gzip: **~43 KB/poll** (vs ~270 KB necomprimat) → **~12 MB/zi** la 5 min (de la ~78). Fără cost de latență. Pagina n-are ETag/Last-Modified utile, deci GET condiționat nu ajută; gzip e câștigul disponibil.

## Fișiere
- `news_monitor.py` — logica. `--once` (un ciclu, folosit de scheduler), `--dry-run` (un ciclu, nu trimite Telegram), fără flag = loop permanent 300s (mod alternativ, neutilizat de scheduler).
- `news_monitor.cmd` — wrapper Task Scheduler (UTF-8, log).
- **Runtime (pe disc, GITIGNORED — ca `spread_collection_state`):** `NEWS_LEDGER.csv`, `announced_ids.txt` (dedup de alertă, autoritar, append-only), `cookies.txt`, `monitor_state.json`, `news_monitor.log`.

*De ce runtime-ul e gitignored:* urmează pattern-ul proceselor permanente existente (`spread_collection_state` e gitignored). Datele trăiesc durabil pe disc în carantină. Dacă se vrea snapshot în git, e o decizie separată (ca la calendar).

## Proces permanent (al 6-lea)
- Task Windows **`AIQuantLab_NewsMonitor`** — **recurent la 5 min**, rulează `news_monitor.py --once` (un ciclu/rulare), **instanță unică** (`MultipleInstances=IgnoreNew`), StartWhenAvailable, limită 4 min/rulare. Supraviețuiește închiderii sesiunii ȘI reboot-ului.
- **De ce recurent-one-shot și nu loop `run_forever` ca `spread_collection`:** monitorul e stateless între cicluri (tot state-ul pe disc), deci recurent = echivalent funcțional și **strict mai robust la crash** (Task Scheduler deține cadența; un crash de ciclu nu cere logică de repornire). În plus, un task cu trigger **at-logon** a fost respins `Access denied` fără elevare, iar nu escaladez privilegii tăcut. Loop-ul `run_forever` rămâne disponibil (rulare fără flag) dacă se preferă modelul proces-lung.
- Stare: `Get-ScheduledTask -TaskName AIQuantLab_NewsMonitor`
- Pornire manuală a unui ciclu: `Start-ScheduledTask -TaskName AIQuantLab_NewsMonitor`
- Oprire: `Disable-ScheduledTask -TaskName AIQuantLab_NewsMonitor`

Nu atinge celelalte 5 procese, nu atinge captura de calendar.
