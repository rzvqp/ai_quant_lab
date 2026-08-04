# Telegram Notifier — Cross-Division Usage

For any division running in its own repo/session on this machine that needs to send a Telegram
notification. Full design: `TELEGRAM_NOTIFIER_PHASE5_DESIGN.md` (see §9 for the 2026-08-04 credential
fix, §10 for the standalone CLI this doc leads with).

## Recommended: the standalone script (no import, no repo dependency)

```
python "C:\Users\MEDION GAMING\tools\notify.py" "<DIVIZIE>" "<status line>" ["<commit>"] ["<verdict>"]
```

Example:

```
python "C:\Users\MEDION GAMING\tools\notify.py" "STATISTICIAN" "CAND-0009 v3.0 ratified" "fd4fcb2" "DEFINED (DEMO_BASELINE)"
```

- Lives at `C:\Users\MEDION GAMING\tools\notify.py` -- **outside every repo**, not tracked by any of
  them, like a system tool. Nothing to check out, nothing to keep in sync.
- Works from **any working directory** -- verified by calling it from `Downloads`, with no repo
  checked out there at all.
- Works with **any Python** (bare system interpreter, no venv, no `pip install`) -- the package it
  wraps has zero third-party dependencies.
- `commit` and `verdict` are optional -- pass `""` or omit trailing args to leave them out of the
  message.
- Exit code tells you what happened: `0` sent and confirmed, `1` usage error, `2` credentials missing,
  `3` send failed (network or Telegram rejected it) -- the reason is always printed to stderr, never a
  silent failure.
- Reads the token/chat-ID straight from the Windows registry (`HKCU\Environment`), not from this
  process's possibly-stale inherited environment -- same reliability guarantee as the AI Trader
  division's own established PowerShell mechanism.
- Internally just calls the official package (`ai_trader.telegram_notifier`) for credential loading and
  the actual send -- it does not reimplement retry, redaction, or the HTTP call.

This is the answer to "Le pun in fiecare directiva": the exact line above, with your division name,
status, commit, and verdict filled in.

## Alternative: import it directly (if you're already writing Python and want structured control)

```python
import sys
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-research-main")

from ai_trader.telegram_notifier import load_credentials_from_env, notify, NotificationEvent
```

```python
credentials = load_credentials_from_env()  # reads TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID_PRIMARY
                                            # (or the legacy TELEGRAM_CHAT_ID, same registry)
event = NotificationEvent(
    event_type="STATISTICIAN",
    summary="CAND-0009 v3.0 ratified -- live-valid exit horizon.",
    correlation_id="cand-0009-v3-ratified",  # short and meaningful, not a UUID
    as_of=0,
    detail={"commit": "fd4fcb2", "verdict": "DEFINED (DEMO_BASELINE)"},  # optional
)
outcome = notify(event, credentials)
assert outcome.overall_success  # never raises -- inspect outcome.results for per-chat detail instead
```

Use this instead of the script only if you want the `NotificationOutcome`/`SendResult` objects back in
the same process (e.g. to branch on which of two chats failed) rather than just a process exit code.
`notify()` reads credentials from `os.environ` only (no registry read of its own) -- the script's
registry-direct read is what makes the CLI path more robust to a stale shell session; call
`load_credentials_from_env()` with an explicit `env=` dict if you need that same robustness inline.

**If this ever needs to run on a different machine** (not just a different repo on this one), both
paths above break on their hardcoded absolute path, and a real packaging step (submodule, or extracting
`telegram_notifier` into its own tiny installable repo) becomes necessary. Not needed today -- every
division currently runs on this machine. Flag if that assumption changes.

## Message format

Both paths produce the same shape via `NotificationEvent.render_text()`:

```
[EVENT_TYPE] summary
correlation_id=...
commit=...
verdict=...
```

(`detail` keys print alphabetically -- `commit` before `verdict`, matching the requested order.) Mapped
onto the requested phone-readable shape:

```
[DIVIZIE] o linie de status
commit-ul publicat
verdictul, daca exista
```

The `correlation_id=...` line is a Phase 5 contract, not something dropped for either path -- keep it
short (the CLI derives one from division+commit automatically) and it stays readable; it's the field
that lets a later message reference "the same event" without guessing. `verdict`/`commit` are only
present in the rendered text when you actually supply them -- never a blank line.

## Credentials

Nothing to configure. `TELEGRAM_BOT_TOKEN` and a chat-ID variable are already set as User-scope
environment variables (Windows registry, `HKCU:\Environment`) on this machine -- any process under this
Windows account can read them, from any repo. **Never** hardcode the token, put it in a `.env` file, or
commit it anywhere -- `load_credentials_from_env()` (and the script's registry read) are the only
sanctioned ways to obtain it, and `TelegramCredentials.__repr__`/`__str__` redact it unconditionally so
it can't leak through a log or traceback by accident. `notify.py` itself is not tracked in any repo.

## Verified

- Official package, direct import: a real message sent 2026-08-04, HTTP 200, `ok: true`, first attempt.
- Standalone script: a real message sent 2026-08-04 from `Downloads` (no repo checked out there),
  confirmed `sent ok (1 chat(s))`, exit code 0. Failure paths verified in isolation: missing credentials
  → exit 2 with reason on stderr; a deliberately invalid bot token → exit 3, `HTTP Error 401:
  Unauthorized` on stderr.
