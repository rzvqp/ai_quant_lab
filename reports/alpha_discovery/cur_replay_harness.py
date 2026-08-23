"""cur_replay_harness.py — VE-CURRENT-REGIME-TEMPORAL-CAUSALITY-REPAIR-001 mandate section 7.

Replays CR-1 through CR-15's EXACT preregistered definitions against the now causally-repaired
cur_screen.like_at / cur_data.causal_bucket_asof. NO modification to any cur_cr*/cur_p*/cur_info*/
cur_verify script -- each is imported and its own existing main()/entry point is called unchanged.
NO new filter, threshold, or parameter selection is introduced here. NO Alpha interpretation is
performed -- this harness records each script's OWN self-reported, pre-registered verdict text
verbatim; it does not compute, select, or discover anything beyond what each script already prints.

Usage: python cur_replay_harness.py [--only cr13,cr7,...]  (default: runs the full manifest below)
Output: prints each script's own stdout, unmodified, prefixed with a manifest header; writes the
same to cur_replay_manifest_output.txt for the delivery report to cite.
"""
import contextlib, io, importlib, sys, time

# Manifest: (label, module_name, entry_callable_name). "CR-1" here = the pre-numbered first-pass /
# support scripts the ledger's own Phase 3/4 narrative describes before CR-2 is first named as such
# (ALPHA_CURRENT_REGIME_RESCREEN_LEDGER.md lines 1-73) -- included for completeness of "CR-1..CR-15"
# per the mandate's own framing that the whole series inherits the same lookahead.
MANIFEST = [
    ("CR-1 (first-pass re-screen)",      "cur_screen",       "main"),
    ("CR-1 (info-first a)",              "cur_info",         "main"),
    ("CR-1 (info-first b)",              "cur_info2",        "main"),
    ("CR-1 (info-first c)",              "cur_info3",        "main"),
    ("CR-1 (skepticism gate)",           "cur_verify",       "main"),
    ("CR-1 (phase4b p4)",                "cur_p4",           "main"),
    ("CR-1 (phase4b p5)",                "cur_p5",           "main"),
    ("CR-1 (payoff-asym p6)",            "cur_p6",           "main"),
    ("CR-1 (payoff-asym p7)",            "cur_p7",           "main"),
    ("CR-1 (confirmed-downtrend p8)",    "cur_p8",           "main"),
    ("CR-2 (lower-high)",                "cur_cr2",          "main"),
    ("CR-3 (vol-expansion-down info)",   "cur_cr3",          "main"),
    ("CR-3 (vol-expansion-down trade)",  "cur_cr3_trade",    "main"),
    ("CR-4 (capitulation-bounce)",       "cur_cr4",          "main"),
    ("CR-5 (broken-support retest)",     "cur_cr5",          "main"),
    ("CR-6 (session-inheritance info)",  "cur_cr6",          "main"),
    ("CR-6 (session-inheritance trade)", "cur_cr6_trade",    "main"),
    ("CR-7 (episode-age hazard)",        "cur_cr7",          "main"),
    ("CR-8 (macro-session x fresh)",     "cur_cr8",          "main"),
    ("CR-9 (range-migration coil)",      "cur_cr9",          "main"),
    ("CR-10 (PDL/PDH reference)",        "cur_cr10",         "main"),
    ("CR-11 (vol-expansion follow)",     "cur_cr11",         "main"),
    ("CR-12 (coil-breakout fade)",       "cur_cr12",         "main"),
    ("CR-13 (cross-scale info)",         "cur_cr13",         "main"),
    ("CR-13 (cross-scale tradeable)",    "cur_cr13_trade",   "main"),
    ("CR-13 (skepticism gate)",          "cur_cr13_verify",  "main"),
    ("CR-13 (label-dependency probe)",   "cur_cr13_robust",  "main"),
    ("CR-14 (divergence LONG)",          "cur_cr14",         "main"),
    ("CR-15 (M15xH1 decomposition)",     "cur_cr15",         "main"),
]


def run_one(label, modname, fnname):
    """Runs a candidate's own exact code unmodified. Prefers calling its own main() when one exists
    (avoids re-importing already-imported modules); falls back to runpy.run_path (executes the file's
    own top-level `if __name__=="__main__":` block exactly as `python <file>.py` would) for the files
    that inline their logic there instead of defining main() -- both are the file's own EXACT
    preregistered code, unmodified either way."""
    t0 = time.time()
    buf = io.StringIO()
    try:
        mod = importlib.import_module(modname)
        fn = getattr(mod, fnname, None)
        if fn is not None:
            with contextlib.redirect_stdout(buf):
                fn()
            return label, modname, "OK", buf.getvalue(), time.time() - t0
        import runpy
        with contextlib.redirect_stdout(buf):
            runpy.run_path(f"{modname}.py", run_name="__main__")
        return label, modname, "OK (via runpy, no main())", buf.getvalue(), time.time() - t0
    except Exception as e:
        return label, modname, f"ERROR: {type(e).__name__}: {e}", buf.getvalue(), time.time() - t0


def main():
    only = None
    if len(sys.argv) > 1 and sys.argv[1] == "--only":
        only = set(sys.argv[2].split(","))
    out_lines = []
    for label, modname, fnname in MANIFEST:
        if only is not None and modname not in only:
            continue
        header = f"\n{'='*100}\n{label}  [{modname}.{fnname}()]\n{'='*100}"
        print(header); out_lines.append(header)
        lbl, mod, status, text, dt = run_one(label, modname, fnname)
        print(text, end="" if text.endswith("\n") else "\n")
        print(f"--- status={status}  wall={dt:.2f}s ---")
        out_lines.append(text)
        out_lines.append(f"--- status={status}  wall={dt:.2f}s ---")
    with open("cur_replay_manifest_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"\nfull manifest output written to cur_replay_manifest_output.txt")


if __name__ == "__main__":
    main()
