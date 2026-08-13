#!/usr/bin/env python3
"""ForexFactory calendar — WEEKLY FORWARD CAPTURE (as-of freezing, append-only).

Rationale (CEO decision, 2026-08-10): no structured archive exists, so the only way to
build history is to start capturing now. One capture per week, automated, to quarantine.

Contract:
  * AS-OF FREEZING  — every capture is stamped with its download time (UTC) and stored
    under that stamp. The raw bytes are frozen exactly as served. This lets us later
    reconstruct what forecast/previous looked like AT capture time, immune to the
    source's retroactive revisions (the export carries no revision flag, no 'actual').
  * APPEND-ONLY     — never overwrites a prior capture. Each run writes NEW files under
    captures/<as_of>/ and appends ONE row to CAPTURE_LEDGER.csv.
  * NO FILTER       — all currencies, all impacts (filter is at USE, not storage).
  * NOT SEGMENTED, NOT in manifest — Statistician decides structure.

Idempotence: safe to run more than once; each run is a distinct as-of. It refuses to
clobber an existing as-of directory (second-level collision => abort that run).

Exit code 0 on successful capture (data on disk), 2 on fetch failure. Git push is
best-effort and reported, never silently swallowed.

Usage: python capture_calendar.py            # normal weekly run
       python capture_calendar.py --no-git    # capture only, skip git
       python capture_calendar.py --no-notify # skip notification
"""
import argparse, csv, hashlib, json, os, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]           # <repo>/acquisition_staging/calendar/this
CAL = REPO / "acquisition_staging" / "calendar"
CAPTURES = CAL / "captures"
LEDGER = CAL / "CAPTURE_LEDGER.csv"
NOTIFY = Path(r"C:\Users\MEDION GAMING\tools\notify.py")

# pythonw.exe / windowless-host safety: the scheduled task runs pythonw.exe (no console window, no
# freeze). Under a windowless host sys.stdout/sys.stderr are None and any print() would crash the
# run; redirect both to the log file, preserving every diagnostic line the .cmd used to capture.
if sys.stdout is None or sys.stderr is None:
    _cap_log = open(CAL / "capture_runs.log", "a", encoding="utf-8", buffering=1)
    if sys.stdout is None:
        sys.stdout = _cap_log
    if sys.stderr is None:
        sys.stderr = _cap_log
BASE = "https://nfs.faireconomy.media/ff_calendar_thisweek"
FORMATS = ("json", "csv", "xml")
UA = "Mozilla/5.0 (ai_quant_lab DATA ACQUISITION; weekly economic-calendar as-of capture)"
LEDGER_COLS = ["as_of_utc", "iso_year", "iso_week", "capture_dir",
               "json_sha256", "csv_sha256", "xml_sha256",
               "n_events_json", "server_last_modified", "etag", "http_ok"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
        return body, r.status, r.headers.get("Last-Modified", ""), r.headers.get("ETag", "")


def sha256(b): return hashlib.sha256(b).hexdigest()


def append_ledger(row):
    new = not LEDGER.exists()
    with open(LEDGER, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLS)
        if new:
            w.writeheader()
        w.writerow(row)


def git(*args):
    return subprocess.run(["git", *args], cwd=str(REPO), capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--no-notify", action="store_true")
    a = ap.parse_args()

    now = datetime.now(timezone.utc)
    as_of = now.strftime("%Y-%m-%dT%H%M%SZ")
    iso = now.isocalendar()
    cap_dir = CAPTURES / as_of
    if cap_dir.exists():
        print(f"[abort] capture dir already exists (as-of collision): {cap_dir}", file=sys.stderr)
        return 3
    CAPTURES.mkdir(parents=True, exist_ok=True)

    # ---- fetch all formats (append-only: fail before writing anything partial is fine;
    #      we write into a fresh per-as-of dir so no prior capture can be touched) ----
    blobs, hashes = {}, {}
    last_mod = etag = ""
    http_ok = True
    for fmt in FORMATS:
        try:
            body, status, lm, et = fetch(f"{BASE}.{fmt}")
        except Exception as e:
            print(f"[fetch-fail] {fmt}: {e}", file=sys.stderr)
            http_ok = False
            continue
        if status != 200 or not body:
            print(f"[fetch-fail] {fmt}: HTTP {status} size {len(body)}", file=sys.stderr)
            http_ok = False
            continue
        blobs[fmt] = body
        hashes[fmt] = sha256(body)
        last_mod = last_mod or lm
        etag = etag or et

    if "json" not in blobs:                          # json is the authoritative source
        print("[abort] authoritative JSON not fetched; nothing frozen this run.", file=sys.stderr)
        return 2

    n_events = len(json.loads(blobs["json"].decode("utf-8")))
    cap_dir.mkdir()
    for fmt, body in blobs.items():
        (cap_dir / f"ff_calendar_thisweek.{fmt}").write_bytes(body)   # frozen, immutable

    row = {
        "as_of_utc": as_of, "iso_year": iso.year, "iso_week": iso.week,
        "capture_dir": f"captures/{as_of}",
        "json_sha256": hashes.get("json", ""), "csv_sha256": hashes.get("csv", ""),
        "xml_sha256": hashes.get("xml", ""), "n_events_json": n_events,
        "server_last_modified": last_mod, "etag": etag, "http_ok": http_ok,
    }
    append_ledger(row)
    print(f"[ok] captured as-of {as_of}  week {iso.year}-W{iso.week:02d}  "
          f"events={n_events}  json={hashes.get('json','')[:12]}...")

    git_status = "skipped"
    if not a.no_git:
        git("add", "acquisition_staging/calendar/captures", "acquisition_staging/calendar/CAPTURE_LEDGER.csv")
        c = git("commit", "-m", f"calendar weekly capture as-of {as_of} (W{iso.week:02d}, {n_events} events, append-only)")
        if c.returncode != 0 and "nothing to commit" not in (c.stdout + c.stderr):
            git_status = f"commit-fail: {c.stderr.strip()[:200]}"
        else:
            git("fetch", "origin", "-q")
            br = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
            git("merge", f"origin/{br}", "--no-edit", "-m", f"merge origin into calendar capture {as_of}")
            p = git("push", "origin", br)
            git_status = "pushed" if p.returncode == 0 else f"push-fail: {p.stderr.strip()[:200]}"
    print(f"[git] {git_status}")

    if not a.no_notify and NOTIFY.exists():
        status = f"Weekly calendar capture as-of {as_of} (W{iso.week:02d}): {n_events} events frozen, append-only. git={git_status}"
        verdict = ("Live/forward history-building (no archive exists). Quarantined, as-of frozen, "
                   "NOT segmented, NOT in manifest. Statistician decides structure + revision policy.")
        subprocess.run([sys.executable, str(NOTIFY), "DATA ACQUISITION", status,
                        f"as-of {as_of}", verdict], capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
