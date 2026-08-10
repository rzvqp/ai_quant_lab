# Calendar — captura săptămânală forward (as-of freezing)

**Decizie CEO 2026-08-10:** arhiva istorică nu există (doar `thisweek`), deci singura cale de a
construi istoric e să capturăm de acum, o dată pe săptămână, automat, în carantină.

## Ce face
- Descarcă `ff_calendar_thisweek.{json,csv,xml}` de pe `nfs.faireconomy.media`.
- **As-of freezing:** stampilează captura cu timpul descărcării (UTC) și o îngheață sub acel stamp.
- **Append-only:** nu suprascrie nimic. Fiecare rulare = un director nou `captures/<as_of>/` + un rând nou în `CAPTURE_LEDGER.csv`.
- **Fără filtru:** toate monedele, toate impacturile (filtrul e la utilizare).
- **NU segmentează, NU integrează în manifest** — structura o decide Statisticianul.
- git add/commit/merge/push best-effort (raportat, nu înghițit tăcut) + notificare săptămânală.

## De ce as-of freezing contează
Exportul nu are flag de revizie și nu are `actual`. `previous`/`forecast` se pot schimba retroactiv
la sursă. Înghețând bytes-ii bruți cu timestamp-ul de captură, putem reconstitui ce arăta calendarul
**la momentul T**, imun la revizii retroactive — condiția minimă ca datele să fie folosibile fără lookahead.

## Fișiere
- `capture_calendar.py` — logica (as-of, append-only, hash, git, notify). Rulare manuală: `python capture_calendar.py [--no-git] [--no-notify]`.
- `capture_calendar.cmd` — wrapper pentru Task Scheduler (setează UTF-8, loghează în `capture_runs.log`).
- `captures/<as_of>/ff_calendar_thisweek.{json,csv,xml}` — capturi brute înghețate (pinuite `-text`).
- `CAPTURE_LEDGER.csv` — registrul append-only: `as_of_utc, iso_year, iso_week, capture_dir, json/csv/xml sha256, n_events, server_last_modified, etag, http_ok`.
- `capture_runs.log` — log de rulare (gitignored).

## Programare (Windows Task Scheduler)
- Task: **`AIQuantLab_CalendarWeeklyCapture`** — Weekly, **luni 07:00 local**, la logon (fără parolă stocată), limită 15 min.
- Verificare: `Get-ScheduledTask -TaskName AIQuantLab_CalendarWeeklyCapture`
- Rulare manuală imediată: `Start-ScheduledTask -TaskName AIQuantLab_CalendarWeeklyCapture`
- Prima captură de setup (manuală): as-of `2026-08-10T125009Z` (W33).

**Trade-off de timing (ajustabil de Statistician):** captura de luni dimineață prinde săptămâna curentă
cu forecast-urile înainte de release-urile US mari (mar–vin, 08:30/10:00 ET). Evenimentele de luni
dimineață (rare pentru USD High) ar fi capturate post-release. Cadența/ziua/ora se pot schimba
re-înregistrând trigger-ul; append-only face sigură și rularea mai deasă.
