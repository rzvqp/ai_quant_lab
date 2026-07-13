"""Generate the structured Knowledge-System files from verified artifacts + the Claude/Codex reviews.
READ-ONLY. Writes STRATEGY_REGISTRY.md, MECHANISM_REGISTRY.parquet/.md, KNOWLEDGE_REGISTRY.jsonl/.md."""
import os, json
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

reg = pd.read_parquet(os.path.join(ROOT, 'STRATEGY_REGISTRY.parquet'))
magg = json.load(open(os.path.join(ROOT, 'kb_mechanism_agg.json')))
dedup = json.load(open(os.path.join(ROOT, 'kb_dedup.json')))['clusters']

# ---------- STRATEGY_REGISTRY.md ----------
with open(os.path.join(ROOT, 'STRATEGY_REGISTRY.md'), 'w', encoding='utf-8') as f:
    f.write('# STRATEGY_REGISTRY (S1-S40) — FACTS FROM ARTIFACTS\n\n')
    f.write('Every historically-profitable OR research-worthy hypothesis across S1-S40, from the verified '
            'on-disk parquets (results/FAMILY_RESULTS.parquet + results/ext_families/EXT_FAMILY_RESULTS.parquet). '
            'Full machine table: STRATEGY_REGISTRY.parquet. Read-only; no engine/strategy change.\n\n')
    f.write(f'- Total hypotheses S1-S40: **2300** · historically-profitable: **375** · research-worthy: **139**.\n')
    f.write(f'- Registry rows (profitable OR RW): **{len(reg)}**.\n')
    f.write('- Status values: HISTORICALLY PROFITABLE / RESEARCH WORTHY / FRAGILE / NEGATIVE; '
            'strict_validation = STRICT VALIDATION PENDING for all (matched-null validated but global-FDR CEO-gated).\n')
    f.write('- Missing-at-source fields (yearly, risk/ATR, ledgers) were recovered by read-only re-backtest for '
            'the 22 distinct representatives only (see kb_dedup.json).\n\n')
    f.write('## Counts by status\n\n| status | count |\n|---|---|\n')
    for k, v in reg['status'].value_counts().items():
        f.write(f'| {k} | {v} |\n')
    f.write('\n## Research-Worthy by family\n\n| family | rw_count |\n|---|---|\n')
    rwf = reg[reg['research_worthy']].groupby('family').size().sort_values(ascending=False)
    for k, v in rwf.items():
        f.write(f'| {k} | {v} |\n')

# ---------- MECHANISM_REGISTRY ----------
# status per mechanism reconciled from Codex TASK-4 review + Claude; evidence from artifacts.
MECH_ROWS = [
 dict(mechanism_id='M01', mechanism_name='liquidity-sweep + confirmation', families='S1',
      status='SUPPORTED EXPLORATORILY', confidence='medium',
      positive='S1 low/swing OOS +.29, high/pdh(short) OOS +.35, multiple RW', negative='low/pdh OOS ~+.01 (~null)',
      contradictory='S21 raw sweep w/o confirmation all negative', regimes_pos='bull sample', regimes_neg='untested bear',
      direction_dep='both sides RW', cost_sens='low-mid', outlier_sens='low (t1<=.09)', oos='mixed-positive',
      next_test='confirmed vs unconfirmed sweep in a frozen side/regime-matched null'),
 dict(mechanism_id='M02', mechanism_name='raw liquidity sweep (no confirmation)', families='S21',
      status='REPEATEDLY NEGATIVE', confidence='high', positive='none', negative='all 48 variants negative',
      contradictory='none', regimes_pos='-', regimes_neg='all', direction_dep='short worse (bull)', cost_sens='high (freq)',
      outlier_sens='-', oos='negative', next_test='none — closed'),
 dict(mechanism_id='M03', mechanism_name='opening-range momentum', families='S5',
      status='SUPPORTED EXPLORATORILY', confidence='medium', positive='exp .166, OOS +.18, positive every year 2022-25',
      negative='long/bull exposure', contradictory='S30 kill-zone (fixed-clock range) negative', regimes_pos='bull',
      regimes_neg='untested', direction_dep='long (ny/up)', cost_sens='low', outlier_sens='low (t1=.02)', oos='positive',
      next_test='beta-adjusted matched null; test in flat/bear regimes'),
 dict(mechanism_id='M04', mechanism_name='failed-breakout fade / mean-reversion at prior-day level', families='S2',
      status='SUPPORTED EXPLORATORILY', confidence='medium', positive='OOS +.26, distinct mean-reversion',
      negative='dd 24R high; limited independent replication', contradictory='S12 range-rotation negative',
      regimes_pos='bull', regimes_neg='untested', direction_dep='long', cost_sens='low', outlier_sens='low', oos='positive',
      next_test='matched null; check short side symmetry'),
 dict(mechanism_id='M05', mechanism_name='MTF trend-momentum (HTF-aligned continuation)', families='S9,S20,S17-break',
      status='MIXED', confidence='medium', positive='OOS +.10-.20', negative='beta-suspect long',
      contradictory='monthly corr .75-.88 -> ONE bet, not independent confirmations', regimes_pos='bull', regimes_neg='untested',
      direction_dep='long', cost_sens='low', outlier_sens='low', oos='positive-but-correlated',
      next_test='collapse to one predeclared representative; beta-adjust'),
 dict(mechanism_id='M06', mechanism_name='round-number momentum breakout', families='S22',
      status='SUPPORTED EXPLORATORILY', confidence='low', positive='$100 breakout OOS +.15',
      negative='one threshold may be selected; thin evidence', contradictory='round-number REJECT negative',
      regimes_pos='bull', regimes_neg='untested', direction_dep='both', cost_sens='low', outlier_sens='low', oos='positive',
      next_test='test $50/$100/$200 in a frozen null; multiplicity over thresholds'),
 dict(mechanism_id='M07', mechanism_name='trend-efficiency-gated continuation', families='S39',
      status='MIXED', confidence='low', positive='high-efficiency variant +OOS .02', negative='economically weak, variant-dependent',
      contradictory='raw continuation (S15/S38) negative', regimes_pos='clean trends', regimes_neg='choppy',
      direction_dep='both', cost_sens='mid', outlier_sens='low', oos='weak-positive',
      next_test='efficiency-gate ablation in matched null'),
 dict(mechanism_id='M08', mechanism_name='breakout / expansion chasing', families='S3,S4,S23,S30',
      status='REPEATEDLY NEGATIVE', confidence='high', positive='none material', negative='consistent failures',
      contradictory='none', regimes_pos='-', regimes_neg='all tested', direction_dep='-', cost_sens='high', outlier_sens='-',
      oos='negative', next_test='none — closed'),
 dict(mechanism_id='M09', mechanism_name='pullback continuation', families='S7,S10,S15,S38',
      status='REPEATEDLY NEGATIVE', confidence='high', positive='none', negative='negative across entry-timing choices tested',
      contradictory='S39 efficiency-gated weakly positive', regimes_pos='-', regimes_neg='tested', direction_dep='-',
      cost_sens='mid', outlier_sens='-', oos='negative', next_test='none — closed (efficiency gate is the live variant, M07)'),
 dict(mechanism_id='M10', mechanism_name='value-area / VWAP reversion', families='S8,S26,S27,S28',
      status='REPEATEDLY NEGATIVE', confidence='medium', positive='S8 marginal OOS +.11 (isolated)',
      negative='family mostly negative; sigma-band VA is a weak proxy', contradictory='S8 exception -> not universally negative',
      regimes_pos='?', regimes_neg='most', direction_dep='long', cost_sens='high (freq)', outlier_sens='low', oos='mostly-negative',
      next_test='true volume-profile value area (needs finer data)'),
 dict(mechanism_id='M11', mechanism_name='calendar / day-of-week / month seasonality', families='S18,S29,S31',
      status='OVERFIT (failed OOS)', confidence='high', positive='strong in-sample (exp up to .42)',
      negative='OOS-refuted (S31 OOS -.44); family-wise selection', contradictory='one weekday (Fri) OOS+ but selection-suspect',
      regimes_pos='in-sample only', regimes_neg='OOS', direction_dep='long-biased', cost_sens='low', outlier_sens='low',
      oos='failed to replicate', next_test='pre-registered single window in a frozen family-wise-corrected test'),
 dict(mechanism_id='M12', mechanism_name='session-transition', families='S6',
      status='MIXED', confidence='low', positive='OOS +.12-.16', negative='near-zero expectancy (~.02), fragile',
      contradictory='-', regimes_pos='bull', regimes_neg='untested', direction_dep='long', cost_sens='mid', outlier_sens='low',
      oos='positive-but-tiny', next_test='matched null; is edge > costs?'),
 dict(mechanism_id='M13', mechanism_name='regime routing (meta)', families='S40',
      status='REPEATEDLY NEGATIVE', confidence='medium', positive='none', negative='always-on router doubles cost drag',
      contradictory='-', regimes_pos='-', regimes_neg='all', direction_dep='-', cost_sens='high', outlier_sens='-',
      oos='negative', next_test='selective stand-aside router (future redesign)'),
]
mdf = pd.DataFrame(MECH_ROWS)
mdf.to_parquet(os.path.join(ROOT, 'MECHANISM_REGISTRY.parquet'))
with open(os.path.join(ROOT, 'MECHANISM_REGISTRY.md'), 'w', encoding='utf-8') as f:
    f.write('# MECHANISM_REGISTRY (S1-S40)\n\n')
    f.write('Mechanism > strategy name. Status reconciled from **Codex inline mechanism review (TASK 4)** + '
            '**Claude interpretation**, evidence from verified artifacts. Statuses: SUPPORTED EXPLORATORILY / MIXED / '
            'REPEATEDLY NEGATIVE / OVERFIT / INCONCLUSIVE / DATA REQUIRED / VALIDATION PENDING. '
            'None are validated alpha (matched-null validated as an engine; global-FDR CEO-gated).\n\n')
    for r in MECH_ROWS:
        f.write(f"## {r['mechanism_id']} — {r['mechanism_name']}  ·  **{r['status']}** (confidence {r['confidence']})\n")
        f.write(f"- Families: {r['families']}\n- Positive: {r['positive']}\n- Negative: {r['negative']}\n")
        f.write(f"- Contradictory: {r['contradictory']}\n- Direction dep: {r['direction_dep']} · cost sens: {r['cost_sens']} · outlier sens: {r['outlier_sens']} · OOS: {r['oos']}\n")
        f.write(f"- Next falsification test: {r['next_test']}\n\n")

# ---------- KNOWLEDGE_REGISTRY (claims weakened per Codex TASK 5) ----------
CLAIMS = [
 dict(knowledge_id='K01', claim='On XAUUSD M15 (2022-2025), in the tested S1 specifications, liquidity sweeps WITHOUT a confirmation stage produced non-positive expectancy, while confirmed variants performed better; the evidence is consistent with the confirmation stage carrying the S1 result (not proof of causation; selection and sample composition uncontrolled).',
      evidence_for='S21 (raw sweep) all 48 variants negative; S1 confirmed variants multiple RW with +OOS', evidence_against='S1 low/pdh OOS ~+.01 (near null)',
      supporting_families='S1', contradicting_families='S21', methodological_status='EXPLORATORY, selection-uncontrolled',
      confidence='medium', limitations='4 years, bull sample, family-wise selection not corrected', next_test='confirmed vs unconfirmed in frozen matched null'),
 dict(knowledge_id='K02', claim='On XAUUSD M15 (2022-2025), the tested breakout/expansion-chasing and pullback-continuation variants were generally negative across the entry-timing choices tested (not proven for all possible timings).',
      evidence_for='S3/S4/S23/S30 and S7/S10/S15/S38 negative', evidence_against='S39 efficiency-gated continuation weakly positive',
      supporting_families='S3,S4,S23,S30,S7,S10,S15,S38', contradicting_families='S39', methodological_status='EXPLORATORY',
      confidence='high', limitations='entry-timing coverage not exhaustive', next_test='exhaustive entry-timing sweep in matched null'),
 dict(knowledge_id='K03', claim='On XAUUSD M15, trend continuation became weakly positive OOS only when gated by high trend-efficiency (S39, +OOS .02); this is weak and variant-dependent and does NOT demonstrate a validated efficiency effect.',
      evidence_for='S39 high-efficiency variant +OOS; low-efficiency variants negative', evidence_against='effect size ~.02R, only 2 RW',
      supporting_families='S39', contradicting_families='S15,S38', methodological_status='EXPLORATORY, weak',
      confidence='low', limitations='tiny effect, threshold-selected', next_test='efficiency-gate ablation in matched null'),
 dict(knowledge_id='K04', claim='On XAUUSD M15, calendar / day-of-week / month-boundary effects were strong in-sample but FAILED TO REPLICATE out-of-sample (S31 OOS -.44) — evidence consistent with overfitting under family-wise selection, not a proven persistent effect.',
      evidence_for='S29/S31 in-sample exp up to .42 but OOS negative/near-zero', evidence_against='one weekday (Fri) OOS+ (selection-suspect)',
      supporting_families='S18,S29,S31', contradicting_families='', methodological_status='OVERFIT / failed-OOS',
      confidence='high', limitations='family-wise multiplicity; few events', next_test='single pre-registered window, family-wise-corrected, untouched data'),
 dict(knowledge_id='K05', claim='On XAUUSD M15, of the ~13 OOS-positive distinct candidates, 11 are long-only in a 2023-2025 gold bull trend; the split between timing-alpha and long gold beta is UNRESOLVED and remains so until a beta/regime-matched null is run.',
      evidence_for='exposure-weighted long dominance; only S1 high/pdh is short', evidence_against='matched-null (engine) removes drift-beta by construction but not yet applied to the full candidate set',
      supporting_families='most', contradicting_families='S1(short)', methodological_status='UNRESOLVED',
      confidence='high', limitations='no beta-adjusted expectancy computed yet', next_test='beta/regime/direction-matched null over the full candidate set in one global multiplicity procedure'),
]
with open(os.path.join(ROOT, 'KNOWLEDGE_REGISTRY.jsonl'), 'w', encoding='utf-8') as f:
    for c in CLAIMS:
        c2 = dict(c); c2['dataset_scope'] = 'XAUUSD OANDA M15'; c2['timeframe_scope'] = 'M15 (H4/H1/D1 context)'
        c2['regime_scope'] = '2022-2025, predominantly bull'; c2['date_added'] = '2026-07-13'
        c2['source_artifacts'] = 'FAMILY_RESULTS.parquet, ext_families/*.parquet, S21_S40 reports'
        f.write(json.dumps(c2) + '\n')
with open(os.path.join(ROOT, 'KNOWLEDGE_REGISTRY.md'), 'w', encoding='utf-8') as f:
    f.write('# KNOWLEDGE_REGISTRY (falsifiable claims)\n\n')
    f.write('Each claim is dataset/timeframe/regime-scoped and falsifiable. Wording WEAKENED per Codex TASK-5 '
            'review (no causal over-claims; "failed to replicate OOS" not "proven overfit"). Machine copy: KNOWLEDGE_REGISTRY.jsonl.\n\n')
    for c in CLAIMS:
        f.write(f"### {c['knowledge_id']}  (confidence {c['confidence']}, status {c['methodological_status']})\n")
        f.write(f"**Claim:** {c['claim']}\n\n")
        f.write(f"- For: {c['evidence_for']}\n- Against: {c['evidence_against']}\n")
        f.write(f"- Supporting families: {c['supporting_families']} · Contradicting: {c['contradicting_families']}\n")
        f.write(f"- Limitations: {c['limitations']}\n- Next test: {c['next_test']}\n\n")
print('generated STRATEGY_REGISTRY.md, MECHANISM_REGISTRY.parquet/.md, KNOWLEDGE_REGISTRY.jsonl/.md')
