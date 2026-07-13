"""Lab ONTOLOGY + KNOWLEDGE GRAPH builder. READ-ONLY. Extracts invariants from the 19 primitives, encodes
typed evidence-backed relations with confidence, and generates candidate hypotheses from the graph. Does NOT
implement, backtest, validate, or modify any strategy/engine. Outputs to knowledge/ontology/.
Evidence is traced to primitives (BEHAVIOR_REGISTRY) and families (STRATEGY_EVIDENCE_MAP / results parquets)."""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(ROOT, 'knowledge', 'ontology'); os.makedirs(O, exist_ok=True)

# ---------------- NODES ----------------
# primitive polarity from BEHAVIOR_REGISTRY
PRIM = {
 'P001': ('Confirmed liquidity sweep', 'positive'), 'P002': ('Failed-breakout fade', 'positive'),
 'P003': ('Opening-range momentum', 'positive'), 'P004': ('Round-number momentum', 'positive'),
 'P005': ('Trend-efficiency continuation', 'positive-weak'), 'P006': ('Short-term overreaction', 'positive-weak'),
 'P007': ('MTF alignment', 'mixed'), 'P008': ('Session transition', 'mixed'), 'P009': ('Streak persistence', 'inconclusive'),
 'P010': ('Liquidity memory (levels)', 'mixed'), 'P011': ('Raw sweep (no confirm)', 'negative'),
 'P012': ('Trend/pullback continuation', 'negative'), 'P013': ('Breakout/expansion chasing', 'negative'),
 'P014': ('Value/VWAP reaction', 'mixed-negative'), 'P015': ('Calendar seasonality', 'overfit'),
 'P016': ('Regime routing', 'negative'), 'P017': ('Intrabar pressure', 'negative'),
 'P018': ('Momentum divergence', 'negative'), 'P019': ('Volume-derived signals', 'negative'),
}
# conditions / ingredients (the qualifiers that modify a base behavior) + their observed effect
COND = {
 'C_confirmation': ('confirmation stage (displacement/close-back)', 'HELPS', 'P001>P011'),
 'C_efficiency': ('trend-efficiency gate (clean trend only)', 'HELPS', 'P005>P012'),
 'C_psych_level': ('psychological round level', 'HELPS', 'P004 break>reject'),
 'C_structural_level': ('structural reference level (PDH/PDL/weekly)', 'HELPS', 'P001/P002/P010'),
 'C_extreme_return': ('extreme realized short-term return', 'HELPS', 'P006'),
 'C_session_window': ('session opening/auction window', 'CONTEXT', 'P003/P008'),
 'C_htf_alignment': ('higher-timeframe trend alignment', 'MIXED', 'P007 (beta-confounded)'),
 'C_vwap_reference': ('VWAP / value-area sigma reference', 'WEAK', 'P014 (S8 exception)'),
 'C_volume': ('volume magnitude / participation', 'NO-HELP', 'P019 (S41/S46 negative)'),
 'C_divergence': ('oscillator-price divergence', 'NO-HELP', 'P018'),
 'C_intrabar': ('intrabar close-location pressure', 'NO-HELP', 'P017'),
 'C_regime_label': ('regime classifier label (always-on)', 'NO-HELP', 'P016'),
 'C_calendar': ('calendar/day-of-week/month window', 'OVERFIT', 'P015 (OOS-refuted)'),
 'C_cost_drag': ('per-trade cost (~0.027R)', 'DEGRADES', 'all high-frequency families'),
}

# ---------------- INVARIANTS ----------------
# Wording softened per Codex review: association != necessity/causation; null result != ingredient
# ineffectiveness ("no incremental edge DETECTED"); scoped to the tested specifications only.
INV = [
 dict(id='I1', name='Selectivity Principle', conf='high (methodological)',
   claim='Across the tested families, a qualifying CONDITION tends to separate the profitable from the unprofitable version of the same base behavior; unconditioned versions underperformed their conditioned matched variants.',
   support='P001 vs P011 (confirmation), P005 vs P012 (efficiency), P004 break vs reject (psych level), P006 (extreme return); contrasts C1,C2,C4,C5',
   against='each contrast is a MATCHED CONTRAST (the condition also changes entry/exposure), not a clean single factor', scope='XAUUSD M15 2022-25, tested specs'),
 dict(id='I2', name='Confirmation Improved (reversals)', conf='medium',
   claim='In the tested S1 specification, adding a confirmation stage IMPROVED the sweep-reversal result; the raw version was non-positive. (One family — association, not established necessity.)',
   support='S1 confirmed positive vs S21 raw negative (matched contrast)', against='one family; confirmation also changes entry time/price/opportunity set', scope='M15, tested specs'),
 dict(id='I3', name='Cost-Drag Hurdle', conf='high (given fixed cost model)',
   claim='Under the lab CFG cost model, per-trade edge must exceed the ~0.027R implementation hurdle; high-frequency broad signals were cost-dominated. Not a universal floor (depends on costs/turnover/sizing/fills).',
   support='high-frequency negatives S21/S27/S40/S13/S46; positives are low-frequency selective', against='cost-model-dependent', scope='M15, this CFG'),
 dict(id='I4', name='Chasing Penalty (tested)', conf='high (conditional pattern)',
   claim='In the tested definitions, entering WITH an ongoing breakout/expansion/pullback without a level or quality gate was negative. Not "chasing loses" in general.',
   support='P012 (S7/S10/S15/S38), P013 (S3/S4/S23/S46/S48) negative', against='round-number break (P004) is a level mechanism, not generic chasing', scope='M15, tested specs'),
 dict(id='I5', name='Structure-Reversion (tested) outperformed Continuation', conf='medium',
   claim='In the tested families, fades at structural references / after return extremes OUTPERFORMED tested trend continuations. A tested-set comparison, not a universal law.',
   support='P001/P002/P006 positive vs P012/P013 negative', against='P014 value-reversion mostly negative (reference-type matters, I8)', scope='M15, tested families'),
 dict(id='I6', name='OOS-Selection Guard', conf='high (methodological)',
   claim='In-sample profitability under family-wise selection is not persistence; out-of-sample separated genuine edge from overfit in this lab.',
   support='P015 calendar strong in-sample but FAILED OOS (S29/S31)', against='none', scope='M15'),
 dict(id='I7', name='Beta Confound', conf='high (as a caution)',
   claim='Long positive results in a bull sample MAY reflect gold beta rather than entry-timing alpha; unresolved until a beta/regime-matched null runs on the full set.',
   support='19/22 distinct candidates long; only S1-short is short', against='matched-null engine removes drift-beta by construction but not yet applied to the full set', scope='2022-25 bull'),
 dict(id='I8', name='Level-Type Association', conf='medium',
   claim='Tested psychological/structural levels were ASSOCIATED with edge; sigma-band/VWAP/generic-range references were not (no incremental edge detected). Limited power; interactions uncontrolled.',
   support='P004 round-number & P002 structural positive vs P013 generic-range & P014 VWAP-sigma negative', against='S8 VWAP marginal exception; low power', scope='M15'),
 dict(id='I9', name='Ingredient Selectivity (no incremental edge detected)', conf='medium',
   claim='For volume/divergence/intrabar-pressure/regime-label, NO INCREMENTAL EDGE WAS DETECTED in the tested definitions (not proof of ineffectiveness); confirmation/efficiency/level-type were associated with edge.',
   support='P019/P017/P018/P016 negative; P001/P005/P004 positive', against='null results need ingredient ablations + more power; volume untested at tick/MBO', scope='M15 OHLCV'),
]

# ---------------- EDGES (typed relations, evidence + confidence) ----------------
E = []
def edge(s, rel, t, evidence, conf):
    E.append(dict(source=s, relation=rel, target=t, evidence=evidence, confidence=conf))
# Relations are OBSERVATIONAL (Codex review): one-family evidence cannot support causal REQUIRES/BLOCKED_BY.
edge('P001', 'IMPROVED_BY', 'C_confirmation', 'S1 confirmed positive; S21 raw negative (matched contrast)', 'medium')
edge('P011', 'ASSOCIATED_WITH_FAILURE_WITHOUT', 'C_confirmation', 'S21 all negative', 'medium')
edge('P001', 'OUTPERFORMS_MATCHED_VARIANT', 'P011', 'sweep with vs without confirmation; NOTE confirmation also shifts entry/exposure (not a clean single factor) (C1)', 'medium')
edge('P005', 'IMPROVED_BY', 'C_efficiency', 'S39 er>=0.5 positive; low-efficiency negative', 'low-medium')
edge('P012', 'ASSOCIATED_WITH_FAILURE_WITHOUT', 'C_efficiency', 'S7/S10/S15/S38 negative', 'medium')
edge('P005', 'OUTPERFORMS_MATCHED_VARIANT', 'P012', 'efficiency-gated vs generic continuation (C2)', 'low-medium')
edge('P004', 'IMPROVED_BY', 'C_psych_level', 'S22 breakout positive; reject negative', 'low-medium')
edge('P004', 'OUTPERFORMS_MATCHED_VARIANT', 'P013', 'round-number vs generic break (C4)', 'low-medium')
edge('P013', 'ASSOCIATED_WITH_FAILURE_WITHOUT', 'C_psych_level', 'S3/S23 generic breakouts negative', 'medium')
edge('P006', 'IMPROVED_BY', 'C_extreme_return', 'S42 fade of large 6-bar move positive (small n)', 'low')
edge('P006', 'OUTPERFORMS_MATCHED_VARIANT', 'P014', 'return-ranked vs value-reference reversion (C5)', 'low')
edge('P002', 'IMPROVED_BY', 'C_structural_level', 'S2 fade at prior-day level positive', 'low-medium')
edge('P003', 'ASSOCIATED_WITH', 'C_session_window', 'S5 opening-range positive', 'low-medium')
edge('P003', 'OUTPERFORMS_MATCHED_VARIANT', 'P013', 'opening-range vs generic break (C7)', 'low-medium')
edge('P007', 'CONSISTENT_WITH_BETA', 'I7', 'S9/S20 long-momentum in bull; beta plausibly explains it (not proven)', 'medium')
edge('P007', 'CORRELATED_WITH', 'P003', 'monthly-corr with the momentum cluster', 'medium')
edge('P014', 'UNDERPERFORMED_WITH', 'C_vwap_reference', 'sigma-band VA a weak proxy; S8 marginal exception', 'low-medium')
edge('P019', 'NO_INCREMENTAL_EDGE_DETECTED', 'C_volume', 'S41/S46 negative (needs ablation + more power)', 'low-medium')
edge('P018', 'NO_INCREMENTAL_EDGE_DETECTED', 'C_divergence', 'S43 negative', 'low-medium')
edge('P017', 'NO_INCREMENTAL_EDGE_DETECTED', 'C_intrabar', 'S44 negative (OHLC proxy; tick data untested)', 'low-medium')
edge('P016', 'NO_INCREMENTAL_EDGE_DETECTED', 'C_regime_label', 'S40 always-on router negative', 'low-medium')
edge('P015', 'FAILED_OOS', 'C_calendar', 'strong in-sample, OOS-refuted (S29/S31); calendar not proven causal', 'high')
edge('P011', 'CONSISTENT_WITH', 'C_cost_drag', 'high-frequency + no edge', 'medium')
edge('P013', 'CONSISTENT_WITH', 'C_cost_drag', 'frequent breakouts, cost-dominated', 'medium')
# invariant support edges
for p in ['P001', 'P004', 'P005', 'P006']: edge(p, 'SUPPORTS', 'I1', 'positive conditioned version', 'high')
for p in ['P011', 'P012', 'P013']: edge(p, 'SUPPORTS', 'I1', 'negative unconditioned version', 'high')
edge('P015', 'SUPPORTS', 'I6', 'OOS-refuted calendar', 'high')
for p in ['P002', 'P004']: edge(p, 'SUPPORTS', 'I8', 'level-type dependence', 'medium')
for p in ['P019', 'P017', 'P018', 'P016']: edge(p, 'SUPPORTS', 'I9', 'unhelpful ingredient', 'medium')

# ---------------- HYPOTHESIS GENERATOR ----------------
# Rules operate on the graph. Positive ingredients transferable to negative/untested bases; positive combos; beta-tests.
POS_INGRED = ['C_confirmation', 'C_efficiency', 'C_psych_level', 'C_structural_level', 'C_extreme_return']
NEG_BASES = ['P012', 'P013', 'P014', 'P016', 'P019']
POS_PRIMS = ['P001', 'P002', 'P003', 'P004', 'P005', 'P006']
GEN = []
hid = [0]
def gen(desc, source, invariant, prior, extends, test, kind, tier='T0'):
    hid[0] += 1
    GEN.append(dict(hypothesis_id=f'H{hid[0]:03d}', kind=kind, description=desc, source=source, tests_invariant=invariant,
                    prior_confidence=prior, extends_family=extends, next_test=test, data_tier=tier))
# kind: alpha-candidate | beta-diagnostic | experiment | mechanism-test. (Codex review: separate these.)

# RULE A — transfer a HELPING ingredient onto a currently-negative base (test I1/I9 generalization)
gen('Value/VWAP reaction (P014) WITH a confirmation stage — precisely define reaction/direction/timing first (Codex: VWAP evidence is weak)', 'P014 + C_confirmation', 'I1,I2,I9', 'low', 'S8/S26/S27', 'confirmed vs raw value-reaction in a matched null', 'alpha-candidate')
gen('Breakout (P013) gated by high trend-efficiency — distinguish from P005 to avoid duplication (Codex)', 'P013 + C_efficiency', 'I1,I4', 'low', 'S3/S23', 'efficiency-gated breakout vs generic breakout AND vs P005', 'alpha-candidate')
gen('Breakout (P013) restricted to psychological round levels (from P004)', 'P013 + C_psych_level', 'I8', 'low-medium', 'S3/S46', 'level-type ablation on breakouts', 'alpha-candidate')
gen('Regime router (P016) with a STAND-ASIDE default (deploy only high-conviction sub-setups)', 'P016 refined', 'I3', 'low', 'S40', 'selective router vs always-on router', 'alpha-candidate')
gen('Round-number REJECT leg (P004 negative half) WITH a confirmation stage', 'P004-reject + C_confirmation', 'I2', 'low', 'S22', 'does confirmation rescue the reject leg?', 'experiment')

# RULE B — combine two positive primitives / ingredients (stacked selectivity) — RISK: feature stacking / selection inflation (Codex)
gen('Confirmed liquidity sweep (P001) that occurs AT a psychological round level (P004) — guard against redundant stacking', 'P001 + P004', 'I1,I8', 'medium', 'S1/S22', 'stacked-selectivity sweep vs single-condition sweep (must beat both parents)', 'alpha-candidate')
gen('Failed-breakout fade (P002) AT round-number levels (P004)', 'P002 + P004', 'I8', 'medium', 'S2/S22', 'level-type ablation on failed-breakout fade', 'alpha-candidate')
gen('Short-term overreaction fade (P006) AT a structural level (P002/P010)', 'P006 + C_structural_level', 'I5,I8', 'low-medium', 'S42/S2', 'return-extreme fade with vs without a level anchor', 'alpha-candidate')
gen('Opening-range momentum (P003) WITH a confirmation filter — define base+confirmation precisely (Codex)', 'P003 + C_confirmation', 'I1', 'low-medium', 'S5', 'confirmed vs raw opening-range break', 'alpha-candidate')
gen('Confirmed sweep (P001) applied to WEEKLY level memory (P010)', 'P001 + P010', 'I2', 'medium', 'S1/S17', 'confirmed weekly-level reaction', 'alpha-candidate')

# RULE C — beta de-confound (I7). These are DIAGNOSTICS, not alpha (Codex): raw shorts can add asymmetric regime beta.
gen('Opening-range momentum (P003) short-side / down-flat regimes — BETA DIAGNOSTIC (not an alpha hypothesis)', 'P003 short', 'I7', 'n/a', 'S5', 'beta/regime-matched null on the short side', 'beta-diagnostic')
gen('MTF alignment (P007) beta-neutralized (residualize vs gold trend) before scoring — BETA DIAGNOSTIC', 'P007 - beta', 'I7', 'n/a', 'S9/S20', 'beta-adjusted expectancy of MTF alignment', 'beta-diagnostic')

# RULE D — contradiction separating tests are EXPERIMENTS, not trading hypotheses (Codex)
gen('Confirmation-ablation on the sweep signal set (isolate the confirmation contribution) — EXPERIMENT', 'C1', 'I2', 'n/a', 'S1/S21', 'frozen matched null with/without confirmation', 'experiment')
gen('Level-type ablation: structural vs statistical reference for the SAME reversion signal — EXPERIMENT', 'C5/C8', 'I8', 'n/a', 'S2/S26', 'structural-vs-sigma reference in a null', 'experiment')

# RULE E — data-gated upgrades
gen('True volume-profile value area (POC/VA) replacing the sigma-band proxy (P014)', 'P014 fixed', 'I8', 'unknown', 'S26', 'volume-profile VA reaction', 'alpha-candidate', tier='needs finer/volume data')
gen('Intrabar pressure (P017) at tick/MBO resolution instead of OHLC proxy', 'P017 upgraded', 'I9', 'unknown', 'S44', 'order-flow at tick resolution', 'alpha-candidate', tier='T2 (tick/MBO)')

# RULE F — placebo / mechanism-invariance (Codex-added): survive beta-irrelevant transforms, fail mechanism-breaking placebos.
gen('Level-label PLACEBO: confirmed-sweep (P001) with RANDOMIZED level labels (local structure preserved) should LOSE edge; survival implies the edge is not level-driven', 'P001 placebo', 'I1,I8', 'n/a', 'S1', 'randomized-level-label placebo vs real levels', 'mechanism-test')
gen('Timing PLACEBO: a positive edge should survive a beta-preserving TIME-SHIFT but fail a mechanism-breaking random re-timing (matched-null already partly does this)', 'any positive', 'I7', 'n/a', 'S5/S2/S1', 'time-shift-invariance vs random-retiming placebo', 'mechanism-test')
gen('Market-neutral RESIDUAL: test each positive primitive on gold returns residualized vs its own trend/beta; survivors are non-beta alpha, the rest are beta', 'positives - beta', 'I7', 'n/a', 'all positives', 'beta-residualized expectancy per primitive', 'mechanism-test')

# ---------------- WRITE ----------------
nodes = ([dict(id=k, type='primitive', label=v[0], polarity=v[1]) for k, v in PRIM.items()]
         + [dict(id=k, type='condition', label=v[0], effect=v[1], evidence=v[2]) for k, v in COND.items()]
         + [dict(id=i['id'], type='invariant', label=i['name'], confidence=i['conf']) for i in INV])
graph = dict(nodes=nodes, edges=E, invariants=INV, generated_hypotheses=GEN,
             meta=dict(n_primitives=len(PRIM), n_conditions=len(COND), n_invariants=len(INV), n_edges=len(E), n_generated=len(GEN),
                       scope='XAUUSD M15 2022-25', note='exploratory knowledge; no validated alpha; generator PROPOSES, does not implement'))
json.dump(graph, open(os.path.join(O, 'KNOWLEDGE_GRAPH.json'), 'w'), indent=1)
with open(os.path.join(O, 'KNOWLEDGE_GRAPH.jsonl'), 'w') as f:
    for n in nodes: f.write(json.dumps(dict(kind='node', **n)) + '\n')
    for e in E: f.write(json.dumps(dict(kind='edge', **e)) + '\n')
with open(os.path.join(O, 'GENERATED_HYPOTHESES.jsonl'), 'w') as f:
    for g in GEN: f.write(json.dumps(g) + '\n')
print('nodes', len(nodes), 'edges', len(E), 'invariants', len(INV), 'generated', len(GEN))
