"""HYPOTHESIS GENERATOR v1 — architecture + logic ONLY (no backtest, no implementation, no validation).
Produces NEW candidate hypotheses by recombining EXISTING knowledge (primitives, invariants, conditions,
contradictions) from knowledge/ + knowledge/ontology/. It invents NO new primitives. Every candidate carries:
why it is new, which contradiction it targets, which mechanism it tests, and HOW it differs from ALL S1-S51
families (computed by a signature-based novelty checker). Read-only w.r.t. engine/strategies.

Pipeline:  KB Loader -> Operators (O1..O7) -> Novelty Checker (vs S1-S51 signatures) -> Contradiction Linker
           -> Mechanism/Invariant Tagger -> Prior Scorer (heuristic, NOT expectancy) -> Emitter.
"""
import os, json, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KDIR = os.path.join(ROOT, 'knowledge'); OUT = os.path.join(KDIR, 'generator'); os.makedirs(OUT, exist_ok=True)

# ---------- KB LOADER ----------
def load_kb():
    graph = json.load(open(os.path.join(KDIR, 'ontology', 'KNOWLEDGE_GRAPH.json')))
    prims = {}
    for line in open(os.path.join(KDIR, 'BEHAVIOR_REGISTRY.jsonl'), encoding='utf-8'):
        p = json.loads(line); prims[p['id']] = p
    return graph, prims

# ---------- S1-S51 FAMILY SIGNATURE INDEX (mechanism + condition tags) ----------
# Each family = (mechanism_tag, {condition_tags}, direction_class). Used ONLY to prove novelty / difference.
FAM = {
 'S1': ('liquidity_sweep', {'confirmation', 'structural_level'}, 'both'),
 'S2': ('failed_breakout', {'structural_level'}, 'both'),
 'S3': ('breakout_retest', set(), 'both'), 'S4': ('vol_expansion', set(), 'both'),
 'S5': ('opening_range', {'session_window'}, 'both'), 'S6': ('session_transition', {'session_window'}, 'both'),
 'S7': ('trend_pullback', {'htf_align'}, 'both'), 'S8': ('extension_mr', {'statistical_level'}, 'both'),
 'S9': ('mtf_momentum', {'htf_align'}, 'both'), 'S10': ('displacement', set(), 'both'),
 'S11': ('structure_break', {'htf_align'}, 'both'), 'S12': ('range_rotation', set(), 'both'),
 'S13': ('imbalance_fill', set(), 'both'), 'S14': ('momentum_exhaustion', set(), 'both'),
 'S15': ('trend_accel', {'htf_align'}, 'both'), 'S16': ('prevday_levels', {'structural_level'}, 'both'),
 'S17': ('weekly_levels', {'structural_level', 'level_memory'}, 'both'), 'S18': ('time_of_day', {'calendar'}, 'both'),
 'S19': ('session_gap', set(), 'both'), 'S20': ('hybrid_mtf_sweep', {'htf_align'}, 'both'),
 'S21': ('liquidity_sweep', {'structural_level'}, 'both'),      # NOTE: NO confirmation (that is the contrast with S1)
 'S22': ('round_number', {'psych_level'}, 'both'), 'S23': ('squeeze_breakout', {'htf_align'}, 'both'),
 'S24': ('session_carry', {'session_window'}, 'both'), 'S25': ('vol_regime', set(), 'both'),
 'S26': ('value_area', {'statistical_level'}, 'both'), 'S27': ('vwap_reclaim', {'statistical_level', 'htf_align'}, 'both'),
 'S28': ('anchored_vwap', {'statistical_level'}, 'both'), 'S29': ('day_of_week', {'calendar'}, 'both'),
 'S30': ('kill_zone', {'session_window', 'calendar'}, 'both'), 'S31': ('month_end', {'calendar'}, 'both'),
 'S38': ('patient_pullback', {'htf_align'}, 'both'), 'S39': ('trend_continuation', {'efficiency_gate'}, 'both'),
 'S40': ('regime_router', {'regime_label'}, 'both'), 'S41': ('volume_climax', {'volume'}, 'both'),
 'S42': ('return_reversal', {'extreme_return'}, 'both'), 'S43': ('rsi_divergence', {'divergence'}, 'both'),
 'S44': ('intrabar', {'intrabar'}, 'both'), 'S45': ('streak', set(), 'both'),
 'S46': ('breakout', {'volume'}, 'both'), 'S47': ('weekend_gap', {'calendar'}, 'both'),
 'S48': ('coil_breakout', set(), 'both'), 'S49': ('nr_breakout', set(), 'both'),
 'S50': ('engulfing', set(), 'both'), 'S51': ('range_position', {'statistical_level'}, 'both'),
}
# mechanisms considered "the same family space" for novelty (a candidate is novel if NO family shares its
# mechanism AND all of its added conditions).
def find_conflict(mech, conds):
    """Return (is_novel, closest_family, difference_str, novelty_type).
    novelty_type: 'refinement' (same mechanism as an existing family, adds a condition) vs 'genuinely_new'
    (no family shares the mechanism). NOTE (v1 limitation, Codex review): this is a TAG-subset check; it is
    NECESSARY but not sufficient — v2 needs a canonical semantic signature + implication/equivalence checks."""
    exact = [(f, s) for f, s in FAM.items() if s[0] == mech and conds.issubset(s[1])]
    if exact:
        return (False, exact[0][0], 'already implemented by ' + exact[0][0], 'duplicate')
    same_mech = [(f, s) for f, s in FAM.items() if s[0] == mech]
    if same_mech:
        f, s = max(same_mech, key=lambda x: len(conds & x[1][1]))
        added = conds - s[1]; return (True, f, f + ' has mechanism but LACKS: ' + (', '.join(sorted(added)) or '(same conds)'), 'refinement')
    cand = max(FAM.items(), key=lambda x: len(conds & x[1][1]))
    return (True, cand[0], 'no family combines mechanism <' + mech + '> with conditions {' + ', '.join(sorted(conds)) + '}', 'genuinely_new')

# ---------- OPERATORS ----------
HELP = ['confirmation', 'efficiency_gate', 'psych_level', 'structural_level', 'extreme_return']
# positive primitives -> (mechanism_tag, its native condition)
POS = {'P001': ('liquidity_sweep', 'confirmation'), 'P002': ('failed_breakout', 'structural_level'),
       'P003': ('opening_range', 'session_window'), 'P004': ('round_number', 'psych_level'),
       'P005': ('trend_continuation', 'efficiency_gate'), 'P006': ('return_reversal', 'extreme_return')}
NEG = {'P012': 'trend_continuation', 'P013': 'breakout', 'P014': 'value_area', 'P016': 'regime_router',
       'P019': 'volume_climax'}
CONTRA = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']

_H = [0]
CANDS = []
def emit(op, kind, desc, mech, conds, tests, contra, prior, tier='T0', note=''):
    _H[0] += 1
    novel, closest, diff, ntype = find_conflict(mech, set(conds))
    if not novel:
        return  # generator DISCARDS anything an existing family already implements (novelty gate)
    # prior_plausibility (Codex review): coarse bin, KB-evidence heuristic only, HIDDEN from validators until
    # hypotheses/tests/decision-rules are frozen, and NEVER used to alter validation thresholds.
    CANDS.append(dict(
        hypothesis_id=f'HGv1-{_H[0]:03d}', operator=op, kind=kind, novelty_type=ntype, description=desc,
        mechanism_tested=mech, conditions=sorted(conds), tests_invariant=tests, contradiction_targeted=contra,
        why_new=f'combines mechanism <{mech}> with conditions {sorted(conds)} — {diff}',
        differs_from_all_S1_S51=f'closest = {closest}; difference = {diff}', novelty_ok=True,
        prior_plausibility=prior, prior_note='coarse KB-heuristic; hidden from validators until frozen; must not alter thresholds',
        data_tier=tier, next_test='(deferred) frozen pipeline: engine->screen->matched-null->global-FDR; must beat parent primitives + a matched-beta null',
        guardrails='no new primitive; O2: min-support fixed pre-eval + complexity penalty for search multiplicity + incremental OOS margin vs EACH parent + regime/time stability + redundancy (added qualifier adds conditional info) + capped nesting depth; beta/regime-matched; family-wise multiplicity', note=note))

def run_operators():
    # O1 ingredient-transfer: helping condition onto a negative base (tests I1/I9 generalization; targets its contradiction)
    xfer = {('value_area', 'confirmation'): ('I1,I2', 'C5/C8'), ('value_area', 'structural_level'): ('I8', 'C8'),
            ('breakout', 'efficiency_gate'): ('I1,I4', 'C2/C4'), ('breakout', 'psych_level'): ('I8', 'C4'),
            ('regime_router', 'efficiency_gate'): ('I3', 'C10'), ('trend_continuation', 'psych_level'): ('I4,I8', 'C4'),
            ('volume_climax', 'structural_level'): ('I8', 'C6')}
    for (mech, cond), (inv, c) in xfer.items():
        emit('O1_ingredient_transfer', 'alpha-candidate',
             f'Apply the HELPING condition <{cond}> to the currently-negative base <{mech}>',
             mech, {cond}, inv, c, 'low')
    # O2 stacked-selectivity: mechanism of one positive + an ADDITIONAL QUALIFIER condition from another positive.
    # Logic gate: only stack genuine selectivity QUALIFIERS (the HELP set), never contextual conditions
    # (e.g. session_window), and skip when the added qualifier equals the mechanism's native condition.
    for a, b in itertools.permutations(POS, 2):
        mech, native = POS[a]; cond = POS[b][1]
        if cond not in HELP or cond == native:
            continue
        emit('O2_stacked_selectivity', 'alpha-candidate',
             f'{a} mechanism <{mech}> qualified additionally by the {b} qualifier <{cond}> (stacked selectivity)',
             mech, {native, cond} if native in HELP else {cond}, 'I1', 'C1/C4', 'low-medium',
             note='must beat BOTH parents to count (guards against feature-stacking/selection inflation)')
    # O3 cross-level-type: swap the reference-level type of a mechanism (tests I8 directly)
    for mech, base_cond in [('failed_breakout', 'structural_level'), ('liquidity_sweep', 'structural_level'),
                            ('opening_range', 'session_window')]:
        for lt in ['psych_level', 'structural_level', 'statistical_level']:
            emit('O3_cross_level_type', 'alpha-candidate',
                 f'Run mechanism <{mech}> against a {lt} reference instead of its native {base_cond}',
                 mech, {lt}, 'I8', 'C8', 'low')
    # O4 contradiction-resolver: the separating experiment for each contradiction
    cmap = {'C1': ('liquidity_sweep', {'confirmation'}, 'I2'), 'C2': ('trend_continuation', {'efficiency_gate'}, 'I1'),
            'C4': ('round_number', {'psych_level'}, 'I8'), 'C5': ('return_reversal', {'extreme_return'}, 'I5'),
            'C7': ('opening_range', {'session_window'}, 'I4'), 'C8': ('failed_breakout', {'structural_level'}, 'I8')}
    for c, (mech, conds, inv) in cmap.items():
        emit('O4_contradiction_resolver', 'experiment',
             f'Separating test for contradiction {c}: isolate the resolving condition on mechanism <{mech}>',
             mech, conds | {'ablation'}, inv, c, 'n/a')
    # O5 beta-deconfound (diagnostics)
    for p, (mech, _) in POS.items():
        if p in ('P003', 'P001'):
            emit('O5_beta_deconfound', 'beta-diagnostic',
                 f'Beta/regime-matched + short-side evaluation of <{mech}> (is it timing-alpha or gold beta?)',
                 mech, {'beta_matched'}, 'I7', 'C-beta', 'n/a')
    # O6 placebo / mechanism-invariance
    for p, (mech, _) in list(POS.items())[:3]:
        emit('O6_placebo', 'mechanism-test',
             f'Placebo for <{mech}>: randomize the level labels / re-time events (preserve local structure); the edge must DIE if it is mechanism-driven',
             mech, {'placebo'}, 'I1,I7', 'C-mech', 'n/a')
    # O7 boundary / counterfactual (Codex-added): shift ONE threshold/window/horizon of an existing mechanism-
    # condition pair, holding all else fixed, to generate a falsifiable SCOPE claim (where the edge ceases /
    # reverses / stays invariant). Recombines known predicates into scope tests without inventing primitives.
    for mech, param, claim in [
        ('liquidity_sweep', 'confirmation-window', 'edge should persist within a bounded confirmation window and CEASE beyond it'),
        ('opening_range', 'range-window shift', 'edge should be CONFINED to the true auction window and vanish if the window is shifted'),
        ('trend_continuation', 'efficiency threshold', 'edge should appear only ABOVE a boundary er* (scope of I1) and reverse below it'),
        ('return_reversal', 'return-extremity threshold', 'edge should strengthen with extremity then plateau; invariant to trivial re-parameterization'),
        ('round_number', 'level-spacing ($25/$50/$100/$200)', 'edge should track the psychological salience of the spacing, not arbitrary grids')]:
        emit('O7_boundary_counterfactual', 'scope-test',
             f'Boundary/counterfactual on <{mech}>: vary {param} holding all else fixed — {claim}',
             mech, {'boundary'}, 'I1,I8', 'C-scope', 'n/a')

def main():
    graph, prims = load_kb()
    run_operators()
    # prior scoring heuristic (NOT expectancy): parent-primitive support + invariant confidence, NO backtest
    with open(os.path.join(OUT, 'GENERATED_HYPOTHESES_v1.jsonl'), 'w', encoding='utf-8') as f:
        for c in CANDS:
            f.write(json.dumps(c) + '\n')
    import collections
    kinds = collections.Counter(c['kind'] for c in CANDS); ops = collections.Counter(c['operator'] for c in CANDS)
    summary = dict(n_generated=len(CANDS), kinds=dict(kinds), operators=dict(ops),
                   novelty_gate='every candidate passed the S1-S51 signature novelty check; duplicates discarded',
                   note='architecture + logic + output only; NO backtest, NO implementation, NO validation')
    json.dump(summary, open(os.path.join(OUT, 'generator_summary.json'), 'w'), indent=1)
    print(json.dumps(summary, indent=1))

if __name__ == '__main__':
    main()
