import sys, json; sys.path.insert(0, '.')
from engine import *

H6, H12, H24, H48 = 24, 48, 96, 192

def causal_pct(v, w=250):
    """percentile rank of v[i] against the previous w anchors -- prospectively observable."""
    out = np.full(len(v), np.nan)
    for i in range(w, len(v)):
        win = v[i - w:i]
        win = win[np.isfinite(win)]
        if len(win) >= w // 2 and np.isfinite(v[i]):
            out[i] = float((win < v[i]).mean())
    return out

class Sample:
    def __init__(self, hour, hbars, stride):
        self.idx = episodes(anchor_index(hour), hbars, stride)
        self.h = hbars
        i = self.idx
        self.tg = targets(i, hbars)
        self.tt = time_to_100(i, hbars)
        self.eff = causal_pct(eff24[i])
        self.mv = causal_pct((np.abs(ret24) / atr20d)[i])
        self.cmp = causal_pct(comp48[i])
        self.vr = causal_pct(volratio[i])
        self.acmp = causal_pct(a_comp[i])
        self.anet = causal_pct((np.abs(a_net) / atr20d)[i])
        self.dcon = causal_pct(d_contract[i])
        self.clp = clpos48[i]
        self.aclp = a_clpos[i]
        self.sret = np.sign(ret24[i])
        self.adir = np.sign(a_net[i])
        self.ddir = d_dirsign[i]
        self.drp = d_rngpct[i]
        self.dps = d_persist[i]
        self.drun = d_run[i]
        self.fu = fail_up[i]; self.fd = fail_dn[i]
    def dir_(self, sgn):  return self.tg["ret"] * sgn
    def mag(self):        return self.tg["absret"]

S6  = Sample(0, H6,  1)
S12 = Sample(0, H12, 1)
S24 = Sample(0, H24, 1)
S48 = Sample(0, H48, 2)
D6  = Sample(8, H6,  1)
D12 = Sample(8, H12, 1)
D24 = Sample(8, H24, 1)

print("="*112)
print("  DEV SCAN -- 60 declared hypotheses, scored on DEV ONLY (anchors before 2019-01-01)")
print("="*112)
for nm, s in (("24h-horizon sample", S24), ("48h-horizon sample (stride 2d)", S48), ("Branch-D 6h sample", D6)):
    d = TS[s.idx] < DEV_END_TS
    print(f"  {nm:32} episodes {len(s.idx):5d}   DEV {int(d.sum()):5d}   OOS {int((~d).sum()):5d}")

def M(a): return np.asarray(a, float)

# ---------------- BRANCH A -- multi-hour trend persistence (12)
A1 = lambda s: M(s.eff >= .8); A2 = lambda s: M(s.eff <= .2)
A3 = lambda s: M(s.mv >= .8);  A4 = lambda s: M(s.drun >= 3)
score("A1-DIR-6",  "A", "trailing-24h directional efficiency in top 20% -> continuation, 6h",  S6.idx,  A1(S6),  S6.dir_(S6.sret),  "DIRECTION")
score("A1-DIR-24", "A", "efficiency top 20% -> continuation, 24h",                             S24.idx, A1(S24), S24.dir_(S24.sret), "DIRECTION")
score("A1-MAG-6",  "A", "efficiency top 20% -> |move|, 6h",                                    S6.idx,  A1(S6),  S6.mag(),  "MAGNITUDE")
score("A1-MAG-24", "A", "efficiency top 20% -> |move|, 24h",                                   S24.idx, A1(S24), S24.mag(), "MAGNITUDE")
score("A2-DIR-6",  "A", "efficiency bottom 20% (churn) -> continuation, 6h",                   S6.idx,  A2(S6),  S6.dir_(S6.sret),  "DIRECTION")
score("A2-DIR-24", "A", "efficiency bottom 20% -> continuation, 24h",                          S24.idx, A2(S24), S24.dir_(S24.sret), "DIRECTION")
score("A2-MAG-6",  "A", "efficiency bottom 20% -> |move|, 6h",                                 S6.idx,  A2(S6),  S6.mag(),  "MAGNITUDE")
score("A2-MAG-24", "A", "efficiency bottom 20% -> |move|, 24h",                                S24.idx, A2(S24), S24.mag(), "MAGNITUDE")
score("A3-DIR-24", "A", "trailing-24h |move|/ATR20d top 20% -> continuation, 24h",             S24.idx, A3(S24), S24.dir_(S24.sret), "DIRECTION")
score("A3-MAG-24", "A", "trailing |move| top 20% -> |move|, 24h",                              S24.idx, A3(S24), S24.mag(), "MAGNITUDE")
score("A4-DIR-24", "A", "3+ consecutive same-direction daily closes -> continuation, 24h",     S24.idx, A4(S24), S24.dir_(S24.ddir), "DIRECTION")
score("A4-MAG-24", "A", "3+ consecutive same-direction days -> |move|, 24h",                   S24.idx, A4(S24), S24.mag(), "MAGNITUDE")

# ---------------- BRANCH B -- multi-hour compression / expansion (10)
B1 = lambda s: M(s.cmp <= .2); B2 = lambda s: M(s.cmp >= .8); B3 = lambda s: M(s.vr <= .2)
score("B1-MAG-12", "B", "48h range / 20d ATR bottom 20% (compressed) -> |move|, 12h",   S12.idx, B1(S12), S12.mag(), "MAGNITUDE")
score("B1-MAG-24", "B", "48h compression -> |move|, 24h",                               S24.idx, B1(S24), S24.mag(), "MAGNITUDE")
score("B1-MAG-48", "B", "48h compression -> |move|, 48h",                               S48.idx, B1(S48), S48.mag(), "MAGNITUDE")
score("B1-EXC-24", "B", "48h compression -> largest excursion, 24h",                    S24.idx, B1(S24), S24.tg["exc"], "MAGNITUDE")
score("B1-TTX-48", "B", "48h compression -> hours to first +-100p, 48h window",         S48.idx, B1(S48), S48.tt, "TIMING")
score("B2-MAG-24", "B", "48h range / 20d ATR top 20% (expanded) -> |move|, 24h",        S24.idx, B2(S24), S24.mag(), "MAGNITUDE")
score("B2-MAG-48", "B", "48h expansion -> |move|, 48h",                                 S48.idx, B2(S48), S48.mag(), "MAGNITUDE")
score("B2-TTX-48", "B", "48h expansion -> hours to first +-100p",                       S48.idx, B2(S48), S48.tt, "TIMING")
score("B3-MAG-48", "B", "5d/20d realised-vol ratio bottom 20% -> |move|, 48h",          S48.idx, B3(S48), S48.mag(), "MAGNITUDE")
score("B3-EXC-48", "B", "5d/20d vol contraction -> largest excursion, 48h",             S48.idx, B3(S48), S48.tg["exc"], "MAGNITUDE")

# ---------------- BRANCH C -- path / inventory state (12)
def C1(s): return M((s.mv >= .7) & ((s.clp >= .8) | (s.clp <= .2)))
def C2(s): return M((s.mv >= .7) & (s.clp >= .35) & (s.clp <= .65))
def C3(s): return M((s.clp >= .9) | (s.clp <= .1))
def C4(s): return M(s.fu | s.fd)
def C3sgn(s): return np.where(s.clp >= .5, 1.0, -1.0)
def C4sgn(s): return np.where(s.fu, -1.0, 1.0)
score("C1-DIR-6",  "C", "large trailing move AND close at 48h-range edge -> continuation, 6h",  S6.idx,  C1(S6),  S6.dir_(S6.sret),  "DIRECTION")
score("C1-DIR-24", "C", "large move + close at range edge -> continuation, 24h",                S24.idx, C1(S24), S24.dir_(S24.sret), "DIRECTION")
score("C1-MAG-24", "C", "large move + close at range edge -> |move|, 24h",                      S24.idx, C1(S24), S24.mag(), "MAGNITUDE")
score("C2-DIR-6",  "C", "large trailing move BUT close mid-range (retraced) -> continuation, 6h", S6.idx, C2(S6), S6.dir_(S6.sret), "DIRECTION")
score("C2-DIR-24", "C", "large move, retraced -> continuation, 24h",                            S24.idx, C2(S24), S24.dir_(S24.sret), "DIRECTION")
score("C2-MAG-24", "C", "large move, retraced -> |move|, 24h",                                  S24.idx, C2(S24), S24.mag(), "MAGNITUDE")
score("C3-DIR-6",  "C", "close in top/bottom decile of 48h range -> move toward that edge, 6h", S6.idx,  C3(S6),  S6.dir_(C3sgn(S6)),  "DIRECTION")
score("C3-DIR-24", "C", "close at 48h-range decile edge -> move toward edge, 24h",              S24.idx, C3(S24), S24.dir_(C3sgn(S24)), "DIRECTION")
score("C3-MAG-24", "C", "close at 48h-range decile edge -> |move|, 24h",                        S24.idx, C3(S24), S24.mag(), "MAGNITUDE")
score("C4-DIR-6",  "C", "failed 48h extreme (touched then closed back inside) -> reclaim dir, 6h", S6.idx, C4(S6), S6.dir_(C4sgn(S6)), "DIRECTION")
score("C4-DIR-24", "C", "failed 48h extreme -> reclaim direction, 24h",                         S24.idx, C4(S24), S24.dir_(C4sgn(S24)), "DIRECTION")
score("C4-MAG-24", "C", "failed 48h extreme -> |move|, 24h",                                    S24.idx, C4(S24), S24.mag(), "MAGNITUDE")

# ---------------- BRANCH D -- multi-session transitions, 08:00 UTC anchor (8)
D1 = lambda s: M(s.acmp <= .2); D2 = lambda s: M(s.acmp >= .8)
D3 = lambda s: M(s.anet >= .8); D4 = lambda s: M((s.aclp >= .8) | (s.aclp <= .2))
def D4sgn(s): return np.where(s.aclp >= .5, 1.0, -1.0)
score("D1-MAG-6",  "D", "Asia(00-08) range / 20d ATR bottom 20% -> |move| next 6h",   D6.idx,  D1(D6),  D6.mag(), "MAGNITUDE")
score("D1-MAG-24", "D", "Asia range compressed -> |move| next 24h",                   D24.idx, D1(D24), D24.mag(), "MAGNITUDE")
score("D2-MAG-6",  "D", "Asia range top 20% -> |move| next 6h",                       D6.idx,  D2(D6),  D6.mag(), "MAGNITUDE")
score("D2-MAG-24", "D", "Asia range expanded -> |move| next 24h",                     D24.idx, D2(D24), D24.mag(), "MAGNITUDE")
score("D3-DIR-6",  "D", "Asia net move top 20% -> continuation next 6h",              D6.idx,  D3(D6),  D6.dir_(D6.adir), "DIRECTION")
score("D3-DIR-12", "D", "Asia net move top 20% -> continuation next 12h",             D12.idx, D3(D12), D12.dir_(D12.adir), "DIRECTION")
score("D4-DIR-6",  "D", "Asia closed at edge of Asia range -> move toward edge, 6h",  D6.idx,  D4(D6),  D6.dir_(D4sgn(D6)), "DIRECTION")
score("D4-MAG-6",  "D", "Asia closed at edge of its range -> |move| next 6h",         D6.idx,  D4(D6),  D6.mag(), "MAGNITUDE")

# ---------------- BRANCH E -- daily state transitions (12)
E1 = lambda s: M(s.drp <= .2); E2 = lambda s: M(s.drp >= .8)
E3 = lambda s: M(s.dps >= .7); E4 = lambda s: M(s.dps <= .3); E5 = lambda s: M(s.dcon <= .2)
score("E1-MAG-24", "E", "previous day range in bottom 20% of its 20d history -> |move| 24h", S24.idx, E1(S24), S24.mag(), "MAGNITUDE")
score("E1-MAG-48", "E", "low-range day -> |move| 48h",                                       S48.idx, E1(S48), S48.mag(), "MAGNITUDE")
score("E1-EXC-48", "E", "low-range day -> largest excursion 48h",                            S48.idx, E1(S48), S48.tg["exc"], "MAGNITUDE")
score("E2-MAG-24", "E", "previous day range in top 20% -> |move| 24h",                       S24.idx, E2(S24), S24.mag(), "MAGNITUDE")
score("E2-MAG-48", "E", "high-range day -> |move| 48h",                                      S48.idx, E2(S48), S48.mag(), "MAGNITUDE")
score("E3-DIR-24", "E", "persistent directional day (|net|/range >= .7) -> continuation 24h", S24.idx, E3(S24), S24.dir_(S24.ddir), "DIRECTION")
score("E3-MAG-24", "E", "persistent directional day -> |move| 24h",                          S24.idx, E3(S24), S24.mag(), "MAGNITUDE")
score("E4-DIR-24", "E", "failed directional day (|net|/range <= .3) -> continuation 24h",    S24.idx, E4(S24), S24.dir_(S24.ddir), "DIRECTION")
score("E4-MAG-24", "E", "failed directional day -> |move| 24h",                              S24.idx, E4(S24), S24.mag(), "MAGNITUDE")
score("E5-MAG-48", "E", "5d/20d daily-range contraction bottom 20% -> |move| 48h",           S48.idx, E5(S48), S48.mag(), "MAGNITUDE")
score("E5-EXC-48", "E", "multi-day contraction -> largest excursion 48h",                    S48.idx, E5(S48), S48.tg["exc"], "MAGNITUDE")
score("E5-TTX-48", "E", "multi-day contraction -> hours to first +-100p",                    S48.idx, E5(S48), S48.tt, "TIMING")

# ---------------- BRANCH F -- tail / positive-skew states (6)
p300 = M(S48.tg["exc"] >= 300); p500 = M(S48.tg["exc"] >= 500)
mfe300 = M(S48.tg["mfe"] >= 300); mae300 = M(S48.tg["mae"] >= 300)
score("F1-P300-48", "F", "5d/20d vol contraction -> P(|excursion| >= 300p) in 48h",  S48.idx, B3(S48), p300, "TAIL")
score("F1-P500-48", "F", "5d/20d vol contraction -> P(|excursion| >= 500p) in 48h",  S48.idx, B3(S48), p500, "TAIL")
score("F2-P300-48", "F", "48h range expanded -> P(|excursion| >= 300p) in 48h",      S48.idx, B2(S48), p300, "TAIL")
score("F3-UP300",   "F", "close at 48h-range decile edge -> P(MFE >= 300p) in 48h",  S48.idx, C3(S48), mfe300, "TAIL")
score("F3-DN300",   "F", "close at 48h-range decile edge -> P(MAE >= 300p) in 48h",  S48.idx, C3(S48), mae300, "TAIL")
score("F4-P300-48", "F", "trailing efficiency bottom 20% -> P(|excursion| >= 300p) in 48h", S48.idx, A2(S48), p300, "TAIL")

# ---------------- results
rows = [r for r in SCORED if r["dev"]]
print(f"\n  scored {len(SCORED)} / {BUDGET} declared    (estimable: {len(rows)})")
rows.sort(key=lambda r: -abs(r["dev"]["z"]))
print(f"\n  {'ID':<12} {'BR':<3} {'class':<10} {'n_cond':>7} {'clus':>5} {'base':>9} {'cond':>9} {'lift':>9} {'z':>7}")
for r in rows:
    d = r["dev"]
    print(f"  {r['id']:<12} {r['branch']:<3} {r['target_class']:<10} {d['n_cond']:>7} {d['clusters']:>5} "
          f"{d['base']:>9.2f} {d['cond']:>9.2f} {d['lift']:>+9.2f} {d['z']:>+7.2f}")
bad = [r for r in SCORED if not r["dev"]]
if bad: print(f"\n  NOT ESTIMABLE (too few conditional episodes): {[r['id'] for r in bad]}")
json.dump(SCORED, open("dev_scan.json", "w"), indent=1, default=float)
print(f"\n  Bonferroni at m=60 requires |z| > 3.02")
print(f"  survivors: {[r['id'] for r in rows if abs(r['dev']['z'])>3.02]}")
