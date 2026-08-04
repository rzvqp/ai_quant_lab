# Phase 5 — Telegram Notification Service — Design

**CEO scope**: separate, non-blocking, controlled retry, rate limiting, secret redaction, two
configurable chat IDs with dual-send support, notifies all official architecture events, must never
block the trading pipeline on failure.

## 1. Investigation finding: nothing to reuse, build from scratch

Repo-wide search (code + docs) found **no existing Telegram integration anywhere** in this repository —
only narrative "Telegram sent" lines in changelog/report Markdown documenting a human manually
confirming receipt, never automated code. A sibling project on this machine uses a Windows-registry
credential convention for Telegram (per this session's own memory), but that pattern has **zero
footprint in this repo** (`winreg` appears nowhere) — it is not reused here; env-var credentials are used
instead (see §4), a disclosed, independent implementation choice for this project. No `Notifier`/
`NotificationService` abstraction exists in `ai_trader/` either. `execution_engine.adapters.base.
RetryPolicy` is generic enough to import directly, but doing so would create an upward dependency from a
cross-cutting, domain-independent service onto the execution/broker layer — rejected; a field-identical
`RetryPolicy` is duplicated here instead (17 lines, self-contained, explicitly disclosed as intentional
duplication for zero coupling, not an oversight). No HTTP library (`requests`/`httpx`) is installed or
declared anywhere in the repo — this module uses `urllib.request` (stdlib) instead of adding a new
dependency for a single HTTPS POST call.

## 2. Architectural decision: zero upward coupling to the trading domain

Unlike every other phase so far, this module **imports nothing from `risk_manager`/`risk_manager_live`/
`execution_engine`/`order_manager`/`portfolio_manager_live`** (verified by a dedicated static test). It
exposes a single generic transport primitive:

```python
def notify(event: NotificationEvent, credentials: TelegramCredentials, config: TelegramNotifierConfig | None = None) -> NotificationOutcome: ...
def notify_fire_and_forget(event: NotificationEvent, credentials: TelegramCredentials, config: TelegramNotifierConfig | None = None) -> None: ...
```

Callers (the future Execution Orchestrator, Phase 9, or any other module) construct a `NotificationEvent`
(plain strings: `event_type`, `summary`, `detail: dict[str, str]`, `correlation_id`, `as_of`) from their
OWN domain objects and pass it in — this module never reaches into Risk/Portfolio/Order Manager types.
This is the strictest possible reading of CEO rule 10 ("stays strictly observational, cannot initiate
trading actions") and rule 7 (strict module separation): a side-channel that cannot even SEE trading
domain types, let alone act on them.

## 3. Non-blocking guarantee

`notify()` is synchronous but strictly bounded: `RetryPolicy` caps attempts (default 3, capped backoff),
every HTTP call has an explicit timeout, and the function body is wrapped so **no exception ever
propagates past its own boundary** — matching this codebase's own established "failure isolation"
vocabulary (`ai_trader/simulation/harness.py`'s Shadow Evidence tap: broad `except Exception`, a
warning-level log, a captured-failure record, a safe fallback, never a re-raise). `notify_fire_and_forget()`
goes further: it spawns a daemon `threading.Thread` running `notify()` and returns immediately, so the
calling pipeline is never blocked even by the bounded synchronous path -- the caller does not wait for
Telegram at all. Both are provided; `notify()` is the tested, deterministic core primitive, and
`notify_fire_and_forget()` is a thin wrapper for callers on a real hot path.

## 4. Credentials

`TelegramCredentials(bot_token, primary_chat_id, secondary_chat_id=None)` -- frozen, `__repr__`/`__str__`
redact `bot_token` unconditionally (same mandatory pattern as Phase 1's `BrokerCredentials`). Loaded via
`load_credentials_from_env()` reading `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID_PRIMARY`/
`TELEGRAM_CHAT_ID_SECONDARY` -- no hardcoded credentials, no invented registry mechanism (none exists in
this repo today; a future session may add one if the CEO specifies it, out of this phase's scope).

## 5. Dual-send

`NotificationEvent.chat_target: ChatTarget` (`PRIMARY`/`SECONDARY`/`BOTH`). `BOTH` sends to each chat
independently, each with its OWN retry budget and its OWN `SendResult` -- one chat's failure never
affects delivery to the other (isolated `try/except` per chat, same "failure isolation" discipline).

## 6. Redaction

`redact_secrets(text, credentials)` strips any literal occurrence of `bot_token` from a string before it
is ever logged or placed in an error/exception message -- defense in depth against the token leaking via
a URL echoed back in a stdlib `urllib` exception message.

## 7. Rate limiting

`RateLimiter(max_messages, per_seconds)` -- a simple fixed-window counter (deterministic, tests inject
a `clock: Callable[[], float]` instead of `time.monotonic`, mirroring `RealBrokerAdapterBase`'s own
`_sleep` injection precedent for testability without a real clock). When the window's budget is
exhausted, `notify()` returns a `NotificationOutcome` with `rate_limited=True` and sends nothing -- never
blocks waiting for the window to reset (a caller wanting delivery guarantees uses its own queue; this
service's contract is "best-effort, never blocking").

## 8. Safety boundary

Static tests forbid: any `MetaTrader5` reference, any import from `risk_manager`/`risk_manager_live`/
`execution_engine`/`order_manager`/`portfolio_manager_live`/`simulation`, and any order-submission
vocabulary -- this module cannot initiate a trading action even in principle (CEO rule 10).

## 9. Addendum (2026-08-04) -- legacy chat-ID fallback, cross-division exposure

§4 named the registry-based sibling convention and explicitly left closing that gap "out of this
phase's scope, [for] a future session ... if the CEO specifies it." The CEO specified it: the machine's
persisted User-scope environment carries `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` (no suffix, set by
the older ad-hoc PowerShell mechanism referenced in §1) but not `TELEGRAM_CHAT_ID_PRIMARY`, so
`load_credentials_from_env()` failed if actually invoked.

**Fix**: `credentials.py` now reads `TELEGRAM_CHAT_ID_PRIMARY` first; if unset, it falls back to
`TELEGRAM_CHAT_ID`. Chosen over the alternative (set `TELEGRAM_CHAT_ID_PRIMARY` manually via `setx`,
keep the old variable too) because it is a code-level fix, not a machine-state fix -- it holds on any
machine that only ever had the old variable, with no manual step to lose or forget, while a
canonically-named variable still takes priority the moment one is set. Still zero registry code (`winreg`
still appears nowhere) -- both variables are read the same way, via `os.environ`.

**Verified live**: a real message sent through `notify()` (not the ad-hoc PowerShell path) reached the
configured chat, HTTP 200, `ok: true`, first attempt.

**Cross-division exposure**: this package has zero runtime dependencies beyond the standard library and
zero imports from the rest of `ai_trader` (confirmed by import, not merely by reading the source: a bare
system Python interpreter with no project venv, invoked from a sibling repo's working directory,
successfully imported and used it after only `sys.path.insert(0, ".../ai_quant_lab-research-main")` --
no `pip install`, no `pandas`/`numpy`/MetaTrader5 needed). See `TELEGRAM_NOTIFIER_CROSS_DIVISION_USAGE.md`
for the exact snippet and message-format convention other divisions should use.

## 10. Standalone CLI script (2026-08-04) -- for divisions that can't import this repo at all

The other divisions (Alpha, Statistician, Red Team, VE) run in separate repos and sessions -- some
callers of this service will never be Python code inside `ai_quant_lab-research-main` at all. Rather
than making each division vendor or submodule this package, a small standalone script,
`C:\Users\MEDION GAMING\tools\notify.py`, lives **outside every repo** (not tracked by any of them) and
wraps the official package: `sys.path`-imports `ai_trader.telegram_notifier` for credential validation
and the send itself (no duplicated retry/redaction/HTTP logic), adds a direct `HKCU\Environment`
registry read (`winreg`) so it never depends on a shell session's possibly-stale inherited environment,
and exposes a plain CLI:

```
python notify.py "<DIVIZIE>" "<status line>" ["<commit>"] ["<verdict>"]
```

Exit codes are the contract: `0` sent, `1` usage error, `2` credentials missing, `3` send failed --
reason always on stderr, never silent. Verified working from a directory with no repo checked out in
it, and verified failing correctly (isolated, without touching the real registry) for both the missing-
credentials and send-rejected cases. See `TELEGRAM_NOTIFIER_CROSS_DIVISION_USAGE.md` for the exact
call other divisions should paste into their own directives.
