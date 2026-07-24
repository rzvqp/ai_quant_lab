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
