"""EXPERIMENT PLANNER v1 — turns the 54 HGv1 hypotheses into a small falsifiable experiment plan.
READ-ONLY: no implementation, no backtest, no engine/strategy change. Stages: structural validation ->
semantic dedup -> type classification (A-F) -> Information-Value score (NOT expectancy/prior) -> shortlist (<=12)
-> registry. Frozen per-experiment specs and wave docs are authored separately (the scientific core)."""
import os, json, itertools, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, 'knowledge', 'generator', 'GENERATED_HYPOTHESES_v1.jsonl')
OUT = os.path.join(ROOT, 'knowledge', 'experiments'); os.makedirs(OUT, exist_ok=True)
MARKERS = {'ablation', 'placebo', 'boundary', 'beta_matched'}

def load():
    return [json.loads(l) for l in open(G, encoding='utf-8')]

# ETAPA 1 — structural validation
def struct_status(h):
    conds = [c for c in h['conditions'] if c not in MARKERS]
    if h['data_tier'] != 'T0':
        return 'NEEDS EXTERNAL DATA'
    if len(conds) > 2:
        return 'TOO COMPLEX'
    return 'STRUCTURALLY VALID'

# ETAPA 3 — type A..F from operator (+ contradiction split for O4)
def etype(h):
    op = h['operator']
    if op.startswith('O5'): return 'D'          # beta diagnostic
    if op.startswith('O6'): return 'E'          # placebo / negative control
    if op.startswith('O7'): return 'F'          # scope / boundary
    if op.startswith('O4'):
        c = h['contradiction_targeted']
        return 'B' if c in ('C1', 'C2') else 'C'  # isolate-a-mechanism vs separate-two-explanations
    return 'A'                                    # O1/O2/O3 alpha candidate

# ETAPA 2 — semantic dedup key (mechanism + non-marker conditions + type)
def dkey(h):
    conds = tuple(sorted(c for c in h['conditions'] if c not in MARKERS))
    return (h['mechanism_tested'], conds, etype(h))

# ETAPA 4 — Information-Value score (0-3 per factor; NOT expectancy/prior)
def info_value(h, t):
    s = {}
    s['uncertainty_reduction'] = 3 if t in ('B', 'C', 'E') else (2 if t == 'D' else 1)
    s['kg_updates'] = 3 if t in ('B', 'C') else 2
    s['contradiction_resolution'] = 3 if h['contradiction_targeted'].startswith('C') and h['contradiction_targeted'][1:].isdigit() else (1 if t in ('B',) else 0)
    s['novelty'] = 2 if h['novelty_type'] == 'genuinely_new' else 1
    s['feasibility'] = 3 if h['data_tier'] == 'T0' else 0
    s['low_compute'] = 3                          # all are single-family backtests (cheap) when eventually run
    s['low_mt_risk'] = 1 if h['operator'].startswith('O2') else (3 if t in ('D', 'E', 'B') else 2)
    s['addresses_beta'] = 3 if t == 'D' else (2 if t in ('E', 'F') else 1)
    s['matched_control'] = 3 if t in ('B', 'C', 'D', 'E') else 1
    s['interpretable_if_negative'] = 3 if t in ('B', 'C', 'D', 'E', 'F') else 1
    return s, sum(s.values())

def main():
    hs = load()
    for h in hs:
        h['struct_status'] = struct_status(h); h['exp_type'] = etype(h)
        h['iv_breakdown'], h['iv_score'] = info_value(h, h['exp_type'])
    # dedup
    clusters = collections.OrderedDict()
    for h in hs:
        clusters.setdefault(dkey(h), []).append(h)
    reps = []
    for k, grp in clusters.items():
        valid = [g for g in grp if g['struct_status'] == 'STRUCTURALLY VALID'] or grp
        rep = max(valid, key=lambda g: g['iv_score'])
        for g in grp:
            g['dedup'] = 'REPRESENTATIVE' if g is rep else 'SEMANTICALLY REDUNDANT'
            g['cluster'] = '|'.join(map(str, k))
        reps.append(rep)
    # registry (all 54 with tags)
    with open(os.path.join(OUT, 'EXPERIMENT_REGISTRY.jsonl'), 'w', encoding='utf-8') as f:
        for h in hs:
            f.write(json.dumps({k: h[k] for k in ('hypothesis_id', 'operator', 'exp_type', 'novelty_type',
                    'mechanism_tested', 'conditions', 'contradiction_targeted', 'struct_status', 'dedup',
                    'iv_score', 'data_tier', 'cluster')}) + '\n')
    # counts
    sv = [h for h in hs if h['struct_status'] == 'STRUCTURALLY VALID']
    dedup_valid = [h for h in sv if h['dedup'] == 'REPRESENTATIVE']
    t0 = [h for h in dedup_valid if h['data_tier'] == 'T0']
    by_type = collections.Counter(h['exp_type'] for h in dedup_valid)
    print('initial', len(hs))
    print('structurally valid', len(sv))
    print('after semantic dedup (representatives, valid)', len(dedup_valid))
    print('implementable T0', len(t0))
    print('valid representatives by type', dict(by_type))
    # top by info-value per type (candidate pool for the <=12 selection)
    quota = {'B': 3, 'C': 2, 'D': 2, 'E': 2, 'A': 3}
    pool = {}
    for t, q in quota.items():
        cand = sorted([h for h in dedup_valid if h['exp_type'] == t and h['data_tier'] == 'T0'],
                      key=lambda g: -g['iv_score'])
        pool[t] = cand[:q]
    print('\n=== candidate pool for the <=12 (top by info-value per type) ===')
    for t, q in quota.items():
        for h in pool[t]:
            print(f"  [{t}] {h['hypothesis_id']} iv={h['iv_score']} mech={h['mechanism_tested']} conds={[c for c in h['conditions'] if c not in MARKERS]} contra={h['contradiction_targeted']} :: {h['description'][:60]}")
    json.dump(dict(initial=len(hs), structurally_valid=len(sv), dedup_valid=len(dedup_valid), t0=len(t0),
                   by_type=dict(by_type), selected_pool={t: [h['hypothesis_id'] for h in pool[t]] for t in pool}),
              open(os.path.join(OUT, 'planner_summary.json'), 'w'), indent=1)

if __name__ == '__main__':
    main()
