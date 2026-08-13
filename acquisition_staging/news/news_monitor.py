#!/usr/bin/env python3
"""ForexFactory LIVE NEWS MONITOR — permanent process, Telegram alert on HIGH (red) news.

CEO GO 2026-08-10; remediation GO 2026-08-10 (bug: a HIGH story showed announced=0 and a
consumer read "0 alerts" though the alert had actually gone out). No structured feed exists ->
parses the HTML page. Four ORIGINAL mandated mitigations + THREE remediation fixes are built-in.

ORIGINAL mitigations (non-optional):
  M1 PRESENCE CANARY — whole page yields ZERO impact icons for N=3 consecutive polls (15 min)
     -> "[NEWS PARSER RUPT]". (Detects the impact CSS class disappearing entirely.)
  M2 CHALLENGE DETECTION — response lacks `news-block__item` or looks like a Cloudflare
     interstitial -> "[NEWS ACCES BLOCAT]".
  M3 PERSISTENT __cf_bm COOKIE — a MozillaCookieJar on disk, loaded/saved every cycle.
  M4 BOTH TIMESTAMPS — read_ts (page's own data-timestamp = the anchor the relatives are
     measured against) AND deduced_ts (read_ts - parsed relative) AND raw relative text.

REMEDIATION (2026-08-10):
  R1 RECONCILIATION CANARY (by count) — within the STREAM region, the number of `impact-ff-high`
     icons (H_page) must equal the number of distinct stories tagged high (H_parsed). If
     H_parsed < H_page -> "[NEWS IMPACT ASSOCIATION MISMATCH]". This turns the SILENT miss (a
     high icon that failed to bind to a story) into a LOUD alert. Stream region only: the
     hot-stories carousel carries high icons that have NO /news/<ID> link (can't be alerted /
     deduped), so counting them would fire a permanent false mismatch (the carousel cross-check
     is the deliberately-deferred 3rd signal).
  R2 GLOBAL ICON->ID PAIRING — impact is no longer chunk-local. Each stream impact icon is paired
     to the NEAREST /news/<ID> on the page (verified: an item's icon sits ~102 chars from its own
     /news/<ID>). A story's impact = highest level paired to its id. Fewer silent misses.
  R3 TRUTHFUL LEDGER — the ledger is rewritten atomically each cycle: the `impact` and `announced`
     columns are REFRESHED to current truth (latest observed impact; announced_ids.txt authority),
     never left as an insert-time snapshot. Rows stay append-only (added, never removed/reordered);
     `impact_first` preserves the insert-time value for audit. announced_ids.txt remains the
     authority (written only AFTER a Telegram-confirmed send; a failed send retries).

AUDIT (CEO "constatare de dus mai departe" — other write-once-but-state-changes fields):
  `impact` was the SAME bug shape and MORE dangerous than `announced`: ForexFactory can upgrade a
  story's impact after first sighting; with impact written once at insert and dedup-on-seen
  preventing re-evaluation of the stored row, the ledger could show none/low for a story that
  became high. R2+R3 fix it: impact is re-observed and refreshed every cycle, and the alert loop
  runs over the CURRENT parse of ALL on-page stories (not just new ones), so a late upgrade to
  HIGH still alerts. read_ts/deduced_ts/relative_raw are intentionally first-sighting snapshots
  (absolute time does not change; relative is labeled raw) — those are correct as write-once.

Dedup: on ID from /news/<ID>-slug. Alert: HIGH only, exact short format. On unexpected crash:
"[NEWS MONITOR CRASHED]" then exit (Task Scheduler restarts). We ALERT, we do NOT rush-fix.

Usage: python news_monitor.py            # permanent loop (300s)
       python news_monitor.py --once     # single cycle (used by the 5-min scheduled task)
       python news_monitor.py --dry-run  # single cycle, parse + persist, NEVER send Telegram
"""
from __future__ import annotations

import argparse
import csv
import gzip
import html as htmllib
import json
import os
import re
import sys
import time
import urllib.request
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import Optional

try:
    import winreg
except ImportError:
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
RANK = {"none": 0, "low": 1, "medium": 2, "high": 3}
LEDGER_COLS = ["id", "title", "source", "impact", "impact_first", "deduced_ts_utc",
               "read_ts_utc", "relative_raw", "url", "announced", "last_seen_utc"]
_REG_VARS = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID_PRIMARY", "TELEGRAM_CHAT_ID")

# --- pythonw.exe / windowless-host safety -------------------------------------------------------
# The scheduled task runs pythonw.exe (no console -> no black window, no freeze). Under a windowless
# host sys.stdout/sys.stderr are None, so any print() would raise AttributeError and crash the cycle.
# Redirect BOTH to the log file: this (a) keeps the process alive, and (b) PRESERVES every diagnostic
# line ([cycle]/[telegram]/[fetch] + canary/challenge state) that the old .cmd used to capture via
# `>> news_monitor.log 2>&1`. The ALERTS (PARSER RUPT / ACCES BLOCAT / NEWS HIGH) travel over the
# network via Telegram, NOT stdout, so they are unaffected by this. When run from a real console
# (manual --dry-run/--once) stdout stays the console, so interactive debugging is unchanged.
if sys.stdout is None or sys.stderr is None:
    _log_fh = open(HERE / "news_monitor.log", "a", encoding="utf-8", buffering=1)
    if sys.stdout is None:
        sys.stdout = _log_fh
    if sys.stderr is None:
        sys.stderr = _log_fh


# ----------------------------- credentials + telegram -----------------------------
def _read_credentials() -> tuple[Optional[str], Optional[str]]:
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
    for name in _REG_VARS:
        vals.setdefault(name, os.environ.get(name, ""))
    token = vals.get("TELEGRAM_BOT_TOKEN") or None
    chat = vals.get("TELEGRAM_CHAT_ID_PRIMARY") or vals.get("TELEGRAM_CHAT_ID") or None
    return token, chat


def send_telegram(text: str, *, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"[dry-run telegram]\n{text}\n", flush=True)
        return True
    token, chat = _read_credentials()
    if not token or not chat:
        print("[telegram] credentials missing — cannot send", file=sys.stderr, flush=True)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat, "text": text, "disable_web_page_preview": False}).encode()
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                if json.loads(r.read().decode("utf-8", "replace")).get("ok"):
                    return True
        except Exception as e:  # noqa: BLE001
            print(f"[telegram] attempt {attempt+1} failed: {type(e).__name__}", file=sys.stderr, flush=True)
        time.sleep(1.5 * (attempt + 1))
    return False


# ----------------------------- fetch (gzip, cookies) -----------------------------
def fetch_news(jar: MozillaCookieJar) -> tuple[int, Optional[str], int]:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    req = urllib.request.Request(NEWS_URL, headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "gzip", "Accept-Language": "en-US,en;q=0.9",
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
    t = text.strip().lower()
    if "just now" in t or t == "now":
        return 0
    total, found = 0, False
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


def _iso(ep: int) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_page(page: str) -> tuple[int, list[dict[str, str]], int, int]:
    """Returns (read_ts, stories, stream_high_icons, total_page_icons).
    Impact is assigned by GLOBAL icon->nearest-/news/ID pairing within the STREAM region (R2).
    read_ts = page's own data-timestamp (anchor for relatives); falls back to now()."""
    m = re.search(r'data-timestamp="(\d{9,})"', page)
    read_ts = int(m.group(1)) if m else int(time.time())
    total_page_icons = len(re.findall(r"impact-ff-(?:high|medium|low)", page))

    si = page.find("news-block__item")
    stream = page[si:] if si >= 0 else page
    id_positions = [(mm.start(), mm.group(1)) for mm in re.finditer(r"/news/(\d+)-[a-z0-9-]+", stream)]

    impact_by_id: dict[str, str] = {}   # R2: id -> highest impact paired to it
    stream_high_icons = 0
    for mm in re.finditer(r"impact-ff-(high|medium|low)", stream):
        lvl = mm.group(1)
        if lvl == "high":
            stream_high_icons += 1
        if not id_positions:
            continue
        pos = mm.start()
        nid = min(id_positions, key=lambda ip: abs(ip[0] - pos))[1]
        if RANK[lvl] > RANK.get(impact_by_id.get(nid, "none"), 0):
            impact_by_id[nid] = lvl

    stories: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for chunk in re.split(r'(?=<div class="news-block__item)', page):
        mid = re.search(r"/news/(\d+)-[a-z0-9-]+", chunk)
        if not mid:
            continue
        nid = mid.group(1)
        if nid in seen_ids:
            continue
        mt = re.search(r'/news/\d+-[a-z0-9-]+">\s*([^<]+?)\s*</a>', chunk)
        if not mt:
            continue
        seen_ids.add(nid)
        ms = re.search(r'class="darklink">\s*(?:From\s*)?([^<]+?)\s*</a>', chunk)
        mrel = re.search(r'<span class="nowrap">\s*([^<]+?)\s*</span>', chunk)
        mslug = re.search(r"/news/\d+-([a-z0-9-]+)", chunk)
        rel = mrel.group(1) if mrel else ""
        off = parse_relative_seconds(rel)
        deduced = read_ts - off if off is not None else read_ts
        stories.append({
            "id": nid,
            "title": htmllib.unescape(mt.group(1)),
            "source": htmllib.unescape(ms.group(1)) if ms else "",
            "impact": impact_by_id.get(nid, "none"),
            "deduced_ts_utc": _iso(deduced),
            "read_ts_utc": _iso(read_ts),
            "relative_raw": rel,
            "url": f"https://www.forexfactory.com/news/{nid}-" + (mslug.group(1) if mslug else ""),
        })
    return read_ts, stories, stream_high_icons, total_page_icons


# ----------------------------- persistence -----------------------------
def load_announced() -> set[str]:
    if not ANNOUNCED.exists():
        return set()
    return {ln.strip() for ln in ANNOUNCED.read_text(encoding="utf-8").splitlines() if ln.strip()}


def append_announced(nid: str) -> None:
    with open(ANNOUNCED, "a", encoding="utf-8") as f:
        f.write(nid + "\n")


def load_ledger() -> dict[str, dict[str, str]]:
    """Ordered by insertion. Migrates old 9-col rows (no impact_first/last_seen_utc)."""
    out: dict[str, dict[str, str]] = {}
    if not LEDGER.exists():
        return out
    with open(LEDGER, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nid = row.get("id", "")
            if not nid:
                continue
            row.setdefault("impact_first", row.get("impact", "none"))
            row.setdefault("last_seen_utc", row.get("read_ts_utc", ""))
            out[nid] = {c: row.get(c, "") for c in LEDGER_COLS}
    return out


def write_ledger_atomic(rows: dict[str, dict[str, str]]) -> None:
    """R3: rewrite the whole ledger atomically. Rows append-only (added, never removed/reordered);
    impact + announced columns carry current truth (set by caller)."""
    tmp = LEDGER.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS)
        w.writeheader()
        for r in rows.values():
            w.writerow({c: r.get(c, "") for c in LEDGER_COLS})
    os.replace(tmp, LEDGER)


def load_state() -> dict[str, object]:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {"consec_zero_icons": 0, "canary_fired": False, "blocked": False,
            "assoc_mismatch_fired": False, "polls": 0, "successful_polls": 0}


def save_state(st: dict[str, object]) -> None:
    STATE.write_text(json.dumps(st, indent=2), encoding="utf-8")


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

    # ---- M2: challenge / block detection ----
    blocked = (page is None or status != 200 or "news-block__item" not in page
               or re.search(r"just a moment|cf-mitigated|attention required|cf-browser-verification",
                            page, re.I) is not None)
    if blocked:
        if not st.get("blocked"):
            send_telegram(f"[NEWS ACCES BLOCAT] ForexFactory /news inaccesibil (HTTP {status}, "
                          f"{'no page' if page is None else 'challenge/DOM missing'}). "
                          f"Monitorul continua; nu repar in graba.", dry_run=dry_run)
        st["blocked"] = True
        save_state(st)
        print(f"[cycle] BLOCKED status={status} wire={wire}B", flush=True)
        return
    if st.get("blocked"):
        send_telegram("[NEWS ACCES RESTABILIT] ForexFactory /news accesibil din nou.", dry_run=dry_run)
    st["blocked"] = False

    read_ts, stories, h_page, total_icons = parse_page(page)  # type: ignore[arg-type]
    st["successful_polls"] = int(st.get("successful_polls", 0)) + 1

    # ---- M1: presence canary (whole page) ----
    if total_icons == 0:
        st["consec_zero_icons"] = int(st.get("consec_zero_icons", 0)) + 1
        if int(st["consec_zero_icons"]) >= N_CANARY and not st.get("canary_fired"):
            send_telegram(f"[NEWS PARSER RUPT] {N_CANARY} poll-uri consecutive cu ZERO iconite de "
                          f"impact pe intreaga pagina — selector probabil rupt (risc de HIGH ratat). "
                          f"Nu repar in graba; raportez.", dry_run=dry_run)
            st["canary_fired"] = True
    else:
        if st.get("canary_fired"):
            send_telegram("[NEWS PARSER OK] iconite de impact detectate din nou.", dry_run=dry_run)
        st["consec_zero_icons"] = 0
        st["canary_fired"] = False

    # ---- R1: reconciliation canary (stream region high icons vs stories tagged high) ----
    h_parsed = len({s["id"] for s in stories if s["impact"] == "high"})
    if h_parsed < h_page:
        if not st.get("assoc_mismatch_fired"):
            send_telegram(f"[NEWS IMPACT ASSOCIATION MISMATCH] pagina are {h_page} iconite HIGH in "
                          f"stream dar doar {h_parsed} stiri au fost taguite HIGH — o iconita HIGH nu "
                          f"s-a legat de nicio stire (risc de alerta ratata). Nu repar in graba.",
                          dry_run=dry_run)
            st["assoc_mismatch_fired"] = True
    else:
        if st.get("assoc_mismatch_fired"):
            send_telegram("[NEWS IMPACT ASSOCIATION OK] reconciliere HIGH restabilita.", dry_run=dry_run)
        st["assoc_mismatch_fired"] = False

    # ---- persist ALL (truthful ledger, R3) + alert HIGH only ----
    ledger = load_ledger()
    announced = load_announced()
    high_alerted = 0
    for s in stories:
        # alert HIGH from the CURRENT parse (covers late impact upgrades), dedup on announced_ids.txt
        if s["impact"] == "high" and s["id"] not in announced:
            if send_telegram(high_alert_text(s), dry_run=dry_run) and not dry_run:
                append_announced(s["id"])
                announced.add(s["id"])
                high_alerted += 1
        row = ledger.get(s["id"])
        if row is None:  # first sighting
            ledger[s["id"]] = {
                "id": s["id"], "title": s["title"], "source": s["source"],
                "impact": s["impact"], "impact_first": s["impact"],
                "deduced_ts_utc": s["deduced_ts_utc"], "read_ts_utc": s["read_ts_utc"],
                "relative_raw": s["relative_raw"], "url": s["url"],
                "announced": "", "last_seen_utc": _iso(read_ts),
            }
        else:  # refresh mutable state (impact -> highest observed; last_seen)
            if RANK.get(s["impact"], 0) > RANK.get(row.get("impact", "none"), 0):
                row["impact"] = s["impact"]
            row["last_seen_utc"] = _iso(read_ts)
    # R3: announced column reflects the AUTHORITY (announced_ids.txt) for every row
    for nid, row in ledger.items():
        row["announced"] = "1" if nid in announced else "0"
    if not dry_run or stories:
        write_ledger_atomic(ledger)

    save_state(st)
    print(f"[cycle] ok status={status} wire={wire}B stories={len(stories)} "
          f"high_alerted={high_alerted} h_page={h_page} h_parsed={h_parsed} "
          f"icons={total_icons} zero_streak={st['consec_zero_icons']} read_ts={read_ts}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        run_cycle(dry_run=True)
        return 0
    if a.once:
        run_cycle()
        return 0
    print(f"news_monitor: starting permanent loop, poll={POLL_SECONDS}s, canary N={N_CANARY}", flush=True)
    while True:
        try:
            run_cycle()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            send_telegram(f"[NEWS MONITOR CRASHED] {type(e).__name__}: {e}. "
                          f"Task Scheduler va reporni; nu repar in graba.")
            raise
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
