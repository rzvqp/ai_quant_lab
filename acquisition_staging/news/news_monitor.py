#!/usr/bin/env python3
"""ForexFactory LIVE NEWS MONITOR — permanent process, Telegram alert on HIGH (red) news.

CEO GO 2026-08-10. No structured feed exists (verified in NEWS_MONITOR_INVENTORY.md) -> this
parses the HTML page. All four mandated mitigations are BUILT-IN and NON-OPTIONAL:

  1. SELECTOR CANARY — if the whole page yields ZERO impact icons for N=3 consecutive polls
     (15 min), send "PARSER RUPT" to Telegram. N justified below.
  2. CHALLENGE DETECTION — if the response lacks `news-block__item` or looks like a Cloudflare
     interstitial ("Just a moment", "cf-mitigated", "Attention Required"), send "ACCES BLOCAT".
  3. PERSISTENT __cf_bm COOKIE — a MozillaCookieJar on disk, loaded/saved every cycle.
  4. BOTH TIMESTAMPS STORED — read_ts (page's own data-timestamp = the anchor the relatives are
     measured against) AND deduced_ts (read_ts - parsed relative) AND the raw relative text.

Rationale for the mitigations (CEO): the principal risk is SILENT failure exactly on the function
the system exists for (catching red news). The canary + challenge detection turn both silent
failure modes into loud Telegram alerts.

N=3 justification: the impact icon is a persistent page feature — the hot-stories carousel
essentially always carries impact-rated items, and normally 6+ icons appear across the page. A
genuine 15-minute window with ZERO impact icons anywhere is implausible, so 3 consecutive zeros is
a high-specificity breakage signal while bounding detection latency to <=15 min. A single-poll zero
is tolerated (transient odd render); 3 is not.

Storage (quarantine, NOT in manifest, SEPARATE from calendar):
  NEWS_LEDGER.csv   append-only, ALL news regardless of impact (filter is at USE, like calendar).
                    cols: id,title,source,impact,deduced_ts_utc,read_ts_utc,relative_raw,url,announced
  announced_ids.txt append-only, AUTHORITATIVE alert-dedup set (an id here has been alerted; on
                    restart we read it so a story is never announced twice). The ledger's `announced`
                    column is an insert-time snapshot; this file is the source of truth.
  cookies.txt       persistent cookie jar (__cf_bm).
  monitor_state.json canary counter + challenge episode flag + counters (survives restart).
  news_monitor.log  run log (gitignored).

Dedup: on ID from /news/<ID>-slug (35/35 reliable, verified). Alert: HIGH only, short format.
On any unexpected crash: alert "MONITOR CRASHED" then exit (Task Scheduler restarts). We ALERT,
we do NOT rush-fix (CEO).

Usage: python news_monitor.py            # permanent loop (300s), the real process
       python news_monitor.py --once     # single cycle (testing / one-shot)
       python news_monitor.py --dry-run  # single cycle, parse + persist, NEVER send Telegram
"""
from __future__ import annotations

import argparse
import csv
import gzip
import html as htmllib
import json
import re
import sys
import time
import urllib.request
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import Optional

try:
    import winreg
except ImportError:  # non-Windows: fall back to os.environ inside _read_credentials
    winreg = None  # type: ignore[assignment]

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "NEWS_LEDGER.csv"
ANNOUNCED = HERE / "announced_ids.txt"
COOKIES = HERE / "cookies.txt"
STATE = HERE / "monitor_state.json"
NEWS_URL = "https://www.forexfactory.com/news"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
POLL_SECONDS = 300
N_CANARY = 3
LEDGER_COLS = ["id", "title", "source", "impact", "deduced_ts_utc",
               "read_ts_utc", "relative_raw", "url", "announced"]
_REG_VARS = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID_PRIMARY", "TELEGRAM_CHAT_ID")


# ----------------------------- credentials + telegram -----------------------------
def _read_credentials() -> tuple[Optional[str], Optional[str]]:
    """Read bot token + chat id from HKCU\\Environment (same source as tools/notify.py). Never
    persisted, never logged. Falls back to process env if the registry is unavailable."""
    vals: dict[str, str] = {}
    if winreg is not None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:  # type: ignore[attr-defined]
                for name in _REG_VARS:
                    try:
                        v, _ = winreg.QueryValueEx(k, name)  # type: ignore[attr-defined]
                        if v:
                            vals[name] = str(v)
                    except OSError:
                        pass
        except OSError:
            pass
    import os
    for name in _REG_VARS:
        vals.setdefault(name, os.environ.get(name, ""))
    token = vals.get("TELEGRAM_BOT_TOKEN") or None
    chat = vals.get("TELEGRAM_CHAT_ID_PRIMARY") or vals.get("TELEGRAM_CHAT_ID") or None
    return token, chat


def send_telegram(text: str, *, dry_run: bool = False) -> bool:
    """Send raw text to Telegram (exact format control the official renderer can't give). Minimal
    retry. Returns True on confirmed ok. Never raises past its boundary."""
    if dry_run:
        print(f"[dry-run telegram]\n{text}\n", flush=True)
        return True
    token, chat = _read_credentials()
    if not token or not chat:
        print("[telegram] credentials missing (registry/env) — cannot send", file=sys.stderr, flush=True)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat, "text": text, "disable_web_page_preview": False}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read().decode("utf-8", "replace")
                if json.loads(body).get("ok"):
                    return True
        except Exception as e:  # noqa: BLE001 — transport failures must not crash the monitor
            print(f"[telegram] attempt {attempt+1} failed: {type(e).__name__}", file=sys.stderr, flush=True)
        time.sleep(1.5 * (attempt + 1))
    return False


# ----------------------------- fetch (gzip, cookies) -----------------------------
def fetch_news(jar: MozillaCookieJar) -> tuple[int, Optional[str], int]:
    """GET /news with a browser UA, gzip, and the persistent cookie jar. Returns
    (http_status, decoded_html_or_None, bytes_over_the_wire)."""
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    req = urllib.request.Request(NEWS_URL, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with opener.open(req, timeout=30) as r:
            raw = r.read()
            wire = len(raw)
            if (r.headers.get("Content-Encoding") or "").lower() == "gzip":
                raw = gzip.decompress(raw)
            return r.status, raw.decode("latin-1"), wire
    except Exception as e:  # noqa: BLE001
        print(f"[fetch] {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        return 0, None, 0


# ----------------------------- parsing -----------------------------
_REL = re.compile(r"(\d+)\s*(sec|min|hr|hour|day)", re.I)


def parse_relative_seconds(text: str) -> Optional[int]:
    """'1 hr 46 min ago' -> 6360. Returns None if nothing parseable ('just now' -> 0)."""
    t = text.strip().lower()
    if "just now" in t or "now" == t:
        return 0
    total = 0
    found = False
    for num, unit in _REL.findall(t):
        found = True
        n = int(num)
        if unit.startswith("sec"):
            total += n
        elif unit.startswith("min"):
            total += n * 60
        elif unit.startswith(("hr", "hour")):
            total += n * 3600
        elif unit.startswith("day"):
            total += n * 86400
    return total if found else None


def parse_page(page: str) -> tuple[int, list[dict[str, str]], int]:
    """Returns (read_ts_epoch, stories, total_impact_icon_count).
    read_ts = the page's own data-timestamp (anchor for the relatives); falls back to now()."""
    m = re.search(r'data-timestamp="(\d{9,})"', page)
    read_ts = int(m.group(1)) if m else int(time.time())
    total_icons = len(re.findall(r"impact-ff-(?:high|medium|low)", page))

    stories: list[dict[str, str]] = []
    for chunk in re.split(r'(?=<div class="news-block__item)', page):
        mid = re.search(r"/news/(\d+)-[a-z0-9-]+", chunk)
        if not mid:
            continue
        mt = re.search(r'/news/\d+-[a-z0-9-]+">\s*([^<]+?)\s*</a>', chunk)
        if not mt:
            continue
        ms = re.search(r'class="darklink">\s*(?:From\s*)?([^<]+?)\s*</a>', chunk)
        mrel = re.search(r'<span class="nowrap">\s*([^<]+?)\s*</span>', chunk)
        mimp = re.search(r"impact-ff-(high|medium|low)", chunk)
        rel = mrel.group(1) if mrel else ""
        off = parse_relative_seconds(rel)
        deduced = read_ts - off if off is not None else read_ts
        stories.append({
            "id": mid.group(1),
            "title": htmllib.unescape(mt.group(1)),
            "source": htmllib.unescape(ms.group(1)) if ms else "",
            "impact": mimp.group(1) if mimp else "none",
            "deduced_ts_utc": _iso(deduced),
            "read_ts_utc": _iso(read_ts),
            "relative_raw": rel,
            "url": f"https://www.forexfactory.com/news/{mid.group(1)}-" +
                   (re.search(r"/news/\d+-([a-z0-9-]+)", chunk).group(1)  # type: ignore[union-attr]
                    if re.search(r"/news/\d+-([a-z0-9-]+)", chunk) else ""),
        })
    return read_ts, stories, total_icons


def _iso(ep: int) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ----------------------------- persistence -----------------------------
def load_seen() -> set[str]:
    if not LEDGER.exists():
        return set()
    with open(LEDGER, newline="", encoding="utf-8") as f:
        return {row["id"] for row in csv.DictReader(f) if row.get("id")}


def load_announced() -> set[str]:
    if not ANNOUNCED.exists():
        return set()
    return {ln.strip() for ln in ANNOUNCED.read_text(encoding="utf-8").splitlines() if ln.strip()}


def append_ledger(rows: list[dict[str, str]]) -> None:
    new = not LEDGER.exists()
    with open(LEDGER, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in LEDGER_COLS})


def append_announced(nid: str) -> None:
    with open(ANNOUNCED, "a", encoding="utf-8") as f:
        f.write(nid + "\n")


def load_state() -> dict[str, object]:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {"consec_zero_icons": 0, "canary_fired": False, "blocked": False,
            "polls": 0, "successful_polls": 0}


def save_state(st: dict[str, object]) -> None:
    STATE.write_text(json.dumps(st, indent=2), encoding="utf-8")


# ----------------------------- alert format -----------------------------
def high_alert_text(story: dict[str, str]) -> str:
    hhmm = story["deduced_ts_utc"][11:16]
    rel = story["relative_raw"] or "time n/a"
    return (f"[NEWS HIGH] {story['title']}\n"
            f"{story['source'] or 'source n/a'}, {hhmm} UTC ({rel})\n"
            f"{story['url']}")


# ----------------------------- one cycle -----------------------------
def run_cycle(*, dry_run: bool = False) -> None:
    jar = MozillaCookieJar(str(COOKIES))
    if COOKIES.exists():
        try:
            jar.load(ignore_discard=True, ignore_expires=True)
        except Exception:  # noqa: BLE001
            pass
    st = load_state()
    st["polls"] = int(st.get("polls", 0)) + 1

    status, page, wire = fetch_news(jar)
    try:
        jar.save(ignore_discard=True, ignore_expires=True)
    except Exception:  # noqa: BLE001
        pass

    # ---- MITIGATION 2: challenge / block detection ----
    blocked = (page is None or status != 200
               or "news-block__item" not in page
               or re.search(r"just a moment|cf-mitigated|attention required|cf-browser-verification",
                            page, re.I) is not None)
    if blocked:
        if not st.get("blocked"):  # alert only on transition INTO blocked (no 5-min spam)
            send_telegram(f"[NEWS ACCES BLOCAT] ForexFactory /news inaccesibil "
                          f"(HTTP {status}, {'no page' if page is None else 'challenge/DOM missing'}). "
                          f"Monitorul continua sa incerce; nu repar in graba.", dry_run=dry_run)
        st["blocked"] = True
        save_state(st)
        print(f"[cycle] BLOCKED status={status} wire={wire}B", flush=True)
        return
    if st.get("blocked"):  # recovered
        send_telegram("[NEWS ACCES RESTABILIT] ForexFactory /news accesibil din nou.", dry_run=dry_run)
    st["blocked"] = False

    read_ts, stories, total_icons = parse_page(page)
    st["successful_polls"] = int(st.get("successful_polls", 0)) + 1

    # ---- MITIGATION 1: selector canary ----
    if total_icons == 0:
        st["consec_zero_icons"] = int(st.get("consec_zero_icons", 0)) + 1
        if int(st["consec_zero_icons"]) >= N_CANARY and not st.get("canary_fired"):
            send_telegram(f"[NEWS PARSER RUPT] {N_CANARY} poll-uri consecutive cu ZERO iconite de "
                          f"impact pe intreaga pagina — selectorul de impact e probabil rupt "
                          f"(risc de alerte HIGH ratate). Nu repar in graba; raportez.", dry_run=dry_run)
            st["canary_fired"] = True
    else:
        if st.get("canary_fired"):
            send_telegram("[NEWS PARSER OK] iconite de impact detectate din nou.", dry_run=dry_run)
        st["consec_zero_icons"] = 0
        st["canary_fired"] = False

    # ---- persist ALL new stories; alert HIGH only ----
    seen = load_seen()
    announced = load_announced()
    new_rows: list[dict[str, str]] = []
    high_new = 0
    for s in stories:
        is_new = s["id"] not in seen
        # alert HIGH if not already announced (independent of seen, so a send-failure retries)
        if s["impact"] == "high" and s["id"] not in announced:
            ok = send_telegram(high_alert_text(s), dry_run=dry_run)
            if ok and not dry_run:
                append_announced(s["id"])
                announced.add(s["id"])
                s = {**s, "announced": "1"}
                high_new += 1
            else:
                s = {**s, "announced": "0"}
        else:
            s = {**s, "announced": "1" if s["id"] in announced else "0"}
        if is_new:
            new_rows.append(s)
            seen.add(s["id"])
    if new_rows:
        append_ledger(new_rows)

    save_state(st)
    print(f"[cycle] ok status={status} wire={wire}B stories={len(stories)} "
          f"new={len(new_rows)} high_alerted={high_new} icons={total_icons} "
          f"zero_streak={st['consec_zero_icons']} read_ts={read_ts}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="single cycle then exit")
    ap.add_argument("--dry-run", action="store_true", help="single cycle, never send Telegram")
    a = ap.parse_args()
    if a.dry_run:
        run_cycle(dry_run=True)
        return 0
    if a.once:
        run_cycle()
        return 0
    # permanent loop (the real process). Per-cycle errors are caught and reported, never fatal.
    print(f"news_monitor: starting permanent loop, poll={POLL_SECONDS}s, canary N={N_CANARY}", flush=True)
    while True:
        try:
            run_cycle()
        except Exception as e:  # noqa: BLE001 — a crash is alerted, then we re-raise for Task Scheduler restart
            import traceback
            traceback.print_exc()
            send_telegram(f"[NEWS MONITOR CRASHED] {type(e).__name__}: {e}. "
                          f"Task Scheduler va reporni; nu repar in graba.")
            raise
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
