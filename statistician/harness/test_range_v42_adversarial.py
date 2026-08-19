"""Cele 16 cazuri adversariale (§E) + testele de nevacuitate (§D).

Verifica CONTRACTUL `range-hierarchical-v4.3`. NU e detector VE, NU e wheel,
NU produce semnale, NU calculeaza PnL.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from range_v42_contract_harness import (  # noqa: E402
    Cluster, ConfigV43, ContractError, Depth, Excursion, Registry, Structure,
    assign_level, confirmed_swings, degeneracy_check, guard_timestamp,
    evaluate_candidate, normalized_drift, offer_swing, promotion_check,
    restore, snapshot, sweep_reversal_confirmed,
)

CFG = ConfigV43()
CFG.validate()
PASS: list[str] = []
FAIL: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASS if cond else FAIL).append(f"{name}  {detail}")
    print(f"  {'PASS' if cond else '*** FAIL ***'}  {name}  {detail}")


def mk(st_id: int, atr: float, ups: list[float], dns: list[float], start: int = 0) -> Structure:
    s = Structure(structure_id=st_id, depth=Depth.MACRO, parent_structure_id=None, start_ts=start)
    s.atr_ref = atr
    s.up.members = list(ups)
    s.dn.members = list(dns)
    return s


print("=" * 78)
print(f"HARNESS CONTRACTUAL {CFG.contract_version} | config_id {CFG.config_id()[:24]}...")
print(f"derivate: tol_cluster={CFG.tol_cluster} · s_max={CFG.s_max} · plafon w_atr={CFG.w_atr_sanity_ceiling}")
print("=" * 78)

# ── 1. range cu CHANNEL_UP intern ─────────────────────────────────────────────
print("\n[1] range MACRO cu CHANNEL_UP intern")
macro = mk(1, atr=1.0, ups=[110.0, 110.4], dns=[100.0, 99.6])
macro.confirm_ts = 40
lvl, reason, parent = assign_level(50, 70, 102.0, 108.0, macro, CFG)
check("1a internal admis sub macro", lvl is Depth.INTERNAL and parent == 1, f"lvl={lvl} parent={parent}")
drift = normalized_drift([102 + 0.25 * i for i in range(20)], atr=1.0, duration=20)
check("1b deriva clasifica drept CANAL", drift > CFG.s_max, f"drift={drift:.3f} > s_max={CFG.s_max}")
check("1c MACRO ramane viu", macro.end_ts is None and degeneracy_check(macro, CFG) is None)

# ── 2. range cu CHANNEL_DOWN intern ───────────────────────────────────────────
print("\n[2] range MACRO cu CHANNEL_DOWN intern")
drift_dn = normalized_drift([108 - 0.25 * i for i in range(20)], atr=1.0, duration=20)
check("2a deriva negativa clasifica drept CANAL", drift_dn > CFG.s_max, f"drift={drift_dn:.3f}")
check("2b MACRO neatins de canalul intern", macro.end_ts is None)

# ── 3. sub-range ──────────────────────────────────────────────────────────────
print("\n[3] SUB-RANGE intern")
drift_flat = normalized_drift([104 + (0.05 if i % 2 else -0.05) for i in range(20)], atr=1.0, duration=20)
check("3a deriva mica -> SUBRANGE, nu canal", drift_flat <= CFG.s_max, f"drift={drift_flat:.3f}")
lvl3, _, p3 = assign_level(45, 62, 103.0, 106.0, macro, CFG)
check("3b sub-range admis ca INTERNAL", lvl3 is Depth.INTERNAL and p3 == 1)

# ── 4. sweep de durata mare ───────────────────────────────────────────────────
print("\n[4] sweep de durata MARE (20 bare, sub K_reentry=22)")
ex = Excursion(open_bar=100, direction=-1)
st = None
for b in range(101, 120):
    st, _ = ex.observe(b, outside=(b < 119), cfg=CFG)
check("4a nu se accepta breakout pe drum", ex.closes_outside == 0, f"contor={ex.closes_outside}")
st, _ = ex.observe(119, outside=False, cfg=CFG)
check("4b sweep confirmat la reintrare in K_reentry", st == "SWEEP_CONFIRMED", f"{st} la bara 119, dj={119-100}")

# ── 5. trei inchideri in exterior ─────────────────────────────────────────────
print("\n[5] N_accept=3 inchideri consecutive")
ex5 = Excursion(open_bar=200, direction=1)
r1, ny1 = ex5.observe(201, True, CFG)
r2, _ = ex5.observe(202, True, CFG)
r3, _ = ex5.observe(203, True, CFG)
check("5a prima inchidere = nedecis", r1 == "BOUNDARY_EXCURSION" and "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT" in ny1)
check("5b a treia inchidere = BREAKOUT_ACCEPTED", r3 == "BREAKOUT_ACCEPTED", f"{r1}/{r2}/{r3}")
ex5b = Excursion(open_bar=300, direction=1)
ex5b.observe(301, True, CFG); ex5b.observe(302, True, CFG)
rr, _ = ex5b.observe(303, False, CFG)
check("5c reintrarea inainte de a 3-a RESETEAZA contorul", ex5b.closes_outside == 0 and rr == "SWEEP_CONFIRMED")

# ── 6. reintrare DUPA breakout acceptat ───────────────────────────────────────
print("\n[6] reintrare DUPA breakout acceptat")
reg = Registry()
old = mk(reg.new_id(), 1.0, [110.0, 110.4], [100.0, 99.6]); old.confirm_ts = 40; old.end_ts = 203
reg.kill(old.structure_id)
new_id = reg.new_id()
succ = mk(new_id, 1.0, [112.0, 112.3], [105.0, 104.8], start=204)
succ.predecessor_id = old.structure_id
check("6a episodul vechi PASTREAZA id/limite/confirm", old.structure_id == 1 and old.confirm_ts == 40
      and old.boundary_upper == 110.2 and old.end_ts == 203)
check("6b succesorul are predecessor_id", succ.predecessor_id == 1 and succ.structure_id != 1)
try:
    reg.assert_alive(old.structure_id); ok6 = False
except ContractError as e:
    ok6 = "DEAD_ID_REUSE_REFUSED" in str(e)
check("6c id-ul mort NU poate reveni", ok6)

# ── 7. zone care se ating ─────────────────────────────────────────────────────
print("\n[7] zone care se ATING -> ZONES_DEGENERATE (KILL)")
deg = mk(9, atr=1.0, ups=[101.0, 101.2], dns=[100.0, 99.8])
check("7a degenerare detectata", degeneracy_check(deg, CFG) == "ZONES_DEGENERATE",
      f"sep={deg.boundary_upper - deg.boundary_lower:.2f} <= 2*w*ATR={2*CFG.w_atr}")
check("7b KILL, nu DELAY: candidatul nu se poate confirma", deg.confirm_ts is None)

# ── 8. zone INVERSATE ─────────────────────────────────────────────────────────
print("\n[8] zone INVERSATE")
inv = mk(10, atr=1.0, ups=[98.0, 98.2], dns=[105.0, 105.2])
check("8a inversare detectata", degeneracy_check(inv, CFG) == "ZONES_INVERTED",
      f"up={inv.boundary_upper} < dn={inv.boundary_lower}")

# ── 9. swing lipsa ────────────────────────────────────────────────────────────
print("\n[9] swing-uri insuficiente")
few = mk(11, atr=1.0, ups=[110.0], dns=[])
check("9a fara cluster inferior -> nu se confirma", few.boundary_lower is None)
check("9b reason ESTABLISHING_FEW_SWINGS", degeneracy_check(few, CFG) == "ESTABLISHING_FEW_SWINGS")

# ── 10. ATR indisponibil ──────────────────────────────────────────────────────
print("\n[10] ATR indisponibil")
noatr = Structure(structure_id=12, depth=Depth.MACRO, parent_structure_id=None, start_ts=0)
noatr.up.members = [110.0, 110.4]; noatr.dn.members = [100.0, 99.6]
check("10a ATR None -> ATR_UNAVAILABLE", degeneracy_check(noatr, CFG) == "ATR_UNAVAILABLE")
check("10b zonele nu se pot calcula", noatr.zones(CFG.w_atr) is None)

# ── 11. timestamp viitor ──────────────────────────────────────────────────────
print("\n[11] timestamp din VIITOR")
try:
    guard_timestamp(ts=500, as_of=400); ok11 = False
except ContractError as e:
    ok11 = "FUTURE_TIMESTAMP_REFUSED" in str(e)
check("11a refuz fail-closed", ok11)
guard_timestamp(ts=400, as_of=400)
check("11b bara curenta acceptata (<=)", True)

# ── 12. restart intre breach si confirmare ────────────────────────────────────
print("\n[12] restart intre breach si confirmare")
mid = mk(13, 1.0, [110.0, 110.4], [100.0, 99.6]); mid.confirm_ts = 40
snap = snapshot(mid, CFG)
back = restore(snap, CFG)
check("12a snapshot/restore identic", back.up.members == mid.up.members and back.dn.members == mid.dn.members
      and back.boundary_upper == mid.boundary_upper and back.confirm_ts == mid.confirm_ts)
bad = dict(snap); bad["contract_version"] = "range-hierarchical-v4.2"
try:
    restore(bad, CFG); ok12 = False
except ContractError as e:
    ok12 = "SNAPSHOT_CONTRACT_MISMATCH" in str(e)
check("12b snapshot de alta versiune REFUZAT fail-closed", ok12)
bad2 = dict(snap); bad2["config_id"] = "0" * 64
try:
    restore(bad2, CFG); ok12b = False
except ContractError as e:
    ok12b = "SNAPSHOT_CONTRACT_MISMATCH" in str(e)
check("12c alt config_id REFUZAT", ok12b)

# ── 13. doua structuri suprapuse fara containment ─────────────────────────────
print("\n[13] suprapunere partiala FARA containment")
lvl13, r13, p13 = assign_level(50, 70, 95.0, 108.0, macro, CFG)   # pretul iese sub limita inferioara
check("13a nu e INTERNAL si nu e MACRO", lvl13 is None, f"reason={r13}")
check("13b reason corect", r13 == "PARTIAL_OVERLAP_NO_CONTAINMENT", f"{r13}")

# ── 14. HBL-20 complet ────────────────────────────────────────────────────────
print("\n[14] HBL-20: BALANCE -> SWEEP_DOWN -> REENTRY -> STRUCTURE_BREAK -> MARKUP -> rol")
hbl = mk(20, atr=2.0, ups=[3346.10, 3345.6], dns=[3333.06, 3333.5]); hbl.confirm_ts = 31
check("14a range confirmat, rol NUL in timp real", hbl.role is None and hbl.confirm_ts == 31)
ex14 = Excursion(open_bar=52, direction=-1)
s52, ny52 = ex14.observe(52, True, CFG)
check("14b la bara 52 informatia NU exista", "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT" in ny52, f"{s52}")
s56, _ = ex14.observe(56, False, CFG)
check("14c sweep confirmat la REINTRARE (bara 56)", s56 == "SWEEP_CONFIRMED")
try:
    hbl.assign_role("ACCUMULATION_CONFIRMED", 52); ok14 = False
except ContractError as e:
    ok14 = "ROLE_ASSERTED_BEFORE_CONFIRMATION" in str(e)
check("14d rol pe episod DESCHIS -> refuzat", ok14)
hbl.end_ts = 63
try:
    hbl.assign_role("ACCUMULATION_CONFIRMED", 20); ok14b = False
except ContractError as e:
    ok14b = "ROLE_KNOWN_BEFORE_CONFIRM" in str(e)
check("14e role_known_ts < confirm_ts -> refuzat", ok14b)
hbl.assign_role("ACCUMULATION_CONFIRMED", 70)
check("14f rol retrospectiv acceptat", hbl.role == "ACCUMULATION_CONFIRMED" and hbl.role_known_ts == 70
      and hbl.confirm_ts == 31, f"known={hbl.role_known_ts} != start={hbl.start_ts}")

# ── 15. trend care intra in consolidare ───────────────────────────────────────
print("\n[15] TREND care intra in consolidare -> rol de trend")
tr = mk(30, 1.0, [130.0, 130.5], [120.0, 119.5]); tr.confirm_ts = 10; tr.end_ts = 90
tr.assign_role("TREND_EXHAUSTION_CONFIRMED", 95)
check("15a trendul inchis primeste rol", tr.role == "TREND_EXHAUSTION_CONFIRMED" and tr.role_known_ts == 95)
check("15b schema identica cu RANGE (S3 inchis)", tr.role in
      ("TREND_EXHAUSTION_CONFIRMED", "TREND_CONTINUATION_CONFIRMED"))

# ── 16. level shift ───────────────────────────────────────────────────────────
print("\n[16] LEVEL SHIFT: episod NOU, nu rescriere")
before = (old.structure_id, old.start_ts, old.confirm_ts, old.boundary_upper, old.boundary_lower)
after = (old.structure_id, old.start_ts, old.confirm_ts, old.boundary_upper, old.boundary_lower)
check("16a episodul vechi IMUTABIL dupa level shift", before == after)
check("16b succesorul e obiect NOU, legat prin predecessor_id",
      succ.structure_id != old.structure_id and succ.predecessor_id == old.structure_id)

# ── 17. C13: fereastra de reversal dupa sweep (gol de contract inchis) ────────
print(chr(10) + "[17] LIQUIDITY_SWEEP_REVERSAL — fereastra = viata episodului (C13)")
ex17 = Excursion(open_bar=52, direction=-1)
ex17.observe(52, True, CFG); ex17.observe(56, False, CFG)
ok, r17a = sweep_reversal_confirmed(ex17, 56, 3346.0, 3345.0, 30, 63)
check("17a la bara de reintrare NU se poate confirma", not ok and r17a == "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT")
ok, r17b = sweep_reversal_confirmed(ex17, 59, 3346.0, 3345.0, 30, 63)
check("17b ruptura opusa in viata episodului -> REVERSAL", ok and r17b == "LIQUIDITY_SWEEP_REVERSAL")
ok, r17c = sweep_reversal_confirmed(ex17, 59, 3344.0, 3345.0, 30, 63)
check("17c fara ruptura -> nedecis, NU fals", not ok and r17c == "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT")
ok, r17d = sweep_reversal_confirmed(ex17, 70, 3346.0, 3345.0, 30, 63)
check("17d dupa sfarsitul episodului -> WINDOW_EXPIRED", not ok and r17d == "REVERSAL_WINDOW_EXPIRED")
ok, r17e = sweep_reversal_confirmed(ex17, 59, 3346.0, None, None, 63)
check("17e referinta absenta -> REFERENCE_UNAVAILABLE", not ok and r17e == "REVERSAL_REFERENCE_UNAVAILABLE")
try:
    sweep_reversal_confirmed(ex17, 59, 3346.0, 3345.0, 55, 63); ok17 = False
except ContractError as e:
    ok17 = "FUTURE_TIMESTAMP_REFUSED" in str(e)
check("17f referinta confirmata DUPA sweep = lookahead, refuzat", ok17)
ex17b = Excursion(open_bar=200, direction=1)
ex17b.observe(201, True, CFG); ex17b.observe(202, True, CFG); ex17b.observe(203, True, CFG)
ok, r17g = sweep_reversal_confirmed(ex17b, 210, 90.0, 100.0, 190, None)
check("17g fara SWEEP_CONFIRMED nu exista reversal", not ok and r17g == "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT")

# ── 18. C14: adancimea maxima e IMPUSA, nu doar declarata ────────────────────
print(chr(10) + "[18] DEPTH_LIMIT_EXCEEDED — al treilea nivel refuzat (C14)")
inner = Structure(structure_id=5, depth=Depth.INTERNAL, parent_structure_id=1, start_ts=0)
inner.atr_ref = 1.0; inner.up.members = [110.0, 110.4]; inner.dn.members = [100.0, 99.6]
inner.confirm_ts = 10
lvl18, r18, p18 = assign_level(20, 40, 102.0, 108.0, inner, CFG)
check("18a candidat sub un parinte INTERNAL -> refuzat", lvl18 is None and p18 is None, f"lvl={lvl18}")
check("18b reason DEPTH_LIMIT_EXCEEDED", r18 == "DEPTH_LIMIT_EXCEEDED", f"{r18}")
check("18c sub parinte MACRO acelasi candidat TRECE (poarta nevacua)",
      assign_level(20, 40, 102.0, 108.0, macro, CFG)[0] is Depth.INTERNAL)

# ── 19. C15/C16/C17: conjunctia de confirmare + promovarea, ca functii ───────
print(chr(10) + "[19] conjunctia de confirmare si promovarea, apelabile (C15-C17)")
check("19a fara candidat -> BETWEEN_EPISODES", evaluate_candidate(None, 50, CFG) == "BETWEEN_EPISODES")
short = mk(40, 1.0, [110.0, 110.4], [100.0, 99.6], start=100)
check("19b sub d_macro=29 -> TOO_SHORT_MACRO", evaluate_candidate(short, 120, CFG) == "TOO_SHORT_MACRO",
      f"durata={120-100}")
check("19c peste d_macro -> OK_RANGE_MACRO", evaluate_candidate(short, 140, CFG) == "OK_RANGE_MACRO",
      f"durata={140-100}")
short_i = Structure(structure_id=41, depth=Depth.INTERNAL, parent_structure_id=40, start_ts=100)
short_i.atr_ref = 1.0; short_i.up.members = [108.0, 108.2]; short_i.dn.members = [102.0, 101.8]
check("19d INTERNAL sub d_internal=12 -> TOO_SHORT_INTERNAL",
      evaluate_candidate(short_i, 105, CFG) == "TOO_SHORT_INTERNAL")
check("19e INTERNAL peste d_internal -> OK_RANGE_INTERNAL",
      evaluate_candidate(short_i, 130, CFG) == "OK_RANGE_INTERNAL")
check("19f candidatul MORT are prioritate fata de poarta de durata",
      evaluate_candidate(mk(42, 1.0, [101.0, 101.2], [100.0, 99.8], start=100), 110, CFG)
      == "ZONES_DEGENERATE")
check("19g epizod inchis -> BETWEEN_EPISODES", evaluate_candidate(old, 300, CFG) == "BETWEEN_EPISODES")
ok19, r19 = offer_swing(short, 110.9, "high", CFG)
check("19h swing in toleranta -> acceptat", ok19 and 110.9 in short.up.members, f"{r19}")
ok19b, r19b = offer_swing(short, 130.0, "high", CFG)
check("19i swing in afara -> SWING_OUTSIDE_CLUSTER si NU se adauga",
      (not ok19b) and r19b == "SWING_OUTSIDE_CLUSTER" and 130.0 not in short.up.members)
check("19j promovare completa -> IS_TREND_MACRO", promotion_check(True, True, 2, True, CFG) == (True, "IS_TREND_MACRO"))
check("19k P1 lipsa", promotion_check(False, True, 2, True, CFG)[1] == "PROMOTION_REFUSED_PRECONDITION_P1")
check("19l P2 lipsa", promotion_check(True, False, 2, True, CFG)[1] == "PROMOTION_REFUSED_PRECONDITION_P2")
check("19m P3: UN singur swing exterior nu ajunge",
      promotion_check(True, True, 1, True, CFG)[1] == "PROMOTION_REFUSED_PRECONDITION_P3")
check("19n P4 lipsa", promotion_check(True, True, 2, False, CFG)[1] == "PROMOTION_REFUSED_PRECONDITION_P4")

# ── 20. toate codurile declarate sunt EMISIBILE (clasa de defect C14) ────────
print(chr(10) + "[20] acoperirea setului inchis de reason codes")
from range_v42_contract_harness import REASONS  # noqa: E402
emise = {
    "BETWEEN_EPISODES", "TOO_SHORT_MACRO", "TOO_SHORT_INTERNAL", "OK_RANGE_MACRO",
    "OK_RANGE_INTERNAL", "ZONES_DEGENERATE", "ZONES_INVERTED", "ATR_UNAVAILABLE",
    "ESTABLISHING_FEW_SWINGS", "SWING_OUTSIDE_CLUSTER", "SWEEP_CONFIRMED",
    "BREAKOUT_ACCEPTED", "NOT_YET_AVAILABLE_SWEEP_VS_BREAKOUT", "LIQUIDITY_SWEEP_REVERSAL",
    "REVERSAL_REFERENCE_UNAVAILABLE", "REVERSAL_WINDOW_EXPIRED", "IS_TREND_MACRO",
    "PROMOTION_REFUSED_PRECONDITION_P1", "PROMOTION_REFUSED_PRECONDITION_P2",
    "PROMOTION_REFUSED_PRECONDITION_P3", "PROMOTION_REFUSED_PRECONDITION_P4",
    "PARTIAL_OVERLAP_NO_CONTAINMENT", "DEPTH_LIMIT_EXCEEDED", "LEVEL_ASSIGNMENT_UNRESOLVED",
    "ROLE_ASSERTED_BEFORE_CONFIRMATION", "ROLE_KNOWN_BEFORE_CONFIRM",
    "SNAPSHOT_CONTRACT_MISMATCH", "FUTURE_TIMESTAMP_REFUSED", "DEAD_ID_REUSE_REFUSED",
}
lipsa = set(REASONS) - emise
extra = emise - set(REASONS)
check("20a niciun cod declarat-dar-neemisibil", not lipsa, f"lipsa={sorted(lipsa)}")
check("20b niciun cod emis-dar-nedeclarat", not extra, f"extra={sorted(extra)}")
check("20c setul e inchis si complet", len(REASONS) == len(emise) == 29, f"|REASONS|={len(REASONS)}")

# ── NEVACUITATE (§D) ──────────────────────────────────────────────────────────
print("\n" + "=" * 78)
print("TESTE DE NEVACUITATE — fiecare poarta TRECE si ESUEAZA")
print("=" * 78)
gates = {
    "durata MACRO (d=29)":   (60 >= CFG.d_macro, 10 >= CFG.d_macro),
    "durata INTERNAL (d=12)": (30 >= CFG.d_internal, 8 >= CFG.d_internal),
    "degenerare zone":       (degeneracy_check(deg, CFG) == "ZONES_DEGENERATE",
                              degeneracy_check(macro, CFG) == "ZONES_DEGENERATE"),
    "inversare zone":        (degeneracy_check(inv, CFG) == "ZONES_INVERTED",
                              degeneracy_check(macro, CFG) == "ZONES_INVERTED"),
    "sweep":                 (s56 == "SWEEP_CONFIRMED", r3 == "SWEEP_CONFIRMED"),
    "breakout acceptat":     (r3 == "BREAKOUT_ACCEPTED", s56 == "BREAKOUT_ACCEPTED"),
    "apartenenta la cluster": (Cluster(members=[100.0]).offer(100.5, CFG.tol_cluster * 1.0),
                               Cluster(members=[100.0]).offer(105.0, CFG.tol_cluster * 1.0)),
    "nivel INTERNAL":        (lvl is Depth.INTERNAL, lvl13 is Depth.INTERNAL),
    "nivel UNRESOLVED":      (r13 == "PARTIAL_OVERLAP_NO_CONTAINMENT", reason == "PARTIAL_OVERLAP_NO_CONTAINMENT"),
    "clasificare canal (s_max)": (drift > CFG.s_max, drift_flat > CFG.s_max),
    "rol retrospectiv":      (hbl.role is not None, macro.role is not None),
    "reversal dupa sweep":   (r17b == "LIQUIDITY_SWEEP_REVERSAL",
                              r17c == "LIQUIDITY_SWEEP_REVERSAL"),
    "limita de adancime":    (r18 == "DEPTH_LIMIT_EXCEEDED", reason == "DEPTH_LIMIT_EXCEEDED"),
}
for g, (p, n) in gates.items():
    ok = bool(p) and not bool(n)
    check(f"nevacuu: {g}", ok, f"trece={bool(p)} esueaza-corect={not bool(n)}")

print("\n" + "=" * 78)
print(f"REZULTAT: {len(PASS)} PASS · {len(FAIL)} FAIL")
if FAIL:
    print("ESECURI:")
    for f in FAIL:
        print("   ", f)
print("=" * 78)
sys.exit(1 if FAIL else 0)
