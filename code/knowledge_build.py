"""Build the official knowledge/ base from verified artifacts (S1-S51). READ-ONLY: encodes behavioral
PRIMITIVES with evidence traced to on-disk results; writes registries + primitive files. No engine/strategy
change. Statuses never use VALIDATED. Sources: STRATEGY_REGISTRY.parquet, EXT_FAMILY_RESULTS.parquet,
S21_S40 reports, MECHANISM/KNOWLEDGE registries, MECHANISM_DIVERSITY_LOG."""
import os, json
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(ROOT, 'knowledge'); P = os.path.join(K, 'primitives')
os.makedirs(P, exist_ok=True)
SRC = 'results/FAMILY_RESULTS.parquet, results/ext_families/*.parquet, docs/S21_S40_IMPLEMENTATION_REPORTS.md, docs/S21_S31_TIERB_CONSOLIDATED.md, docs/MECHANISM_DIVERSITY_LOG.md, MECHANISM_REGISTRY.parquet, kb_dedup.json'

# 18 primitives (from the CEO's 23 candidates; 5 merged). status in
# {SUPPORTED EXPLORATORILY, MIXED, INCONCLUSIVE, REPEATEDLY NEGATIVE, TECHNICALLY INVALID, VALIDATION PENDING}
PRIM = [
 dict(id='P001', name='Confirmed Liquidity Sweep Reversal', file=True, status='SUPPORTED EXPLORATORILY', confidence='medium',
   defn='After price sweeps a resting-liquidity level (prior-day/swing/session high/low) it must show a CONFIRMATION (displacement / close-back / consecutive-close) before a reversal entry.',
   behavior='Sweep of a level + confirmation is followed by mean-reversion away from the swept side.',
   econ='Stop/breakout orders pooled beyond levels are triggered to fill size; confirmation filters the genuine reversal from the continuation.',
   fam_pos='S1 (low/swing OOS +0.29; high/pdh short OOS +0.35; multiple RW)', fam_neg='S21 (raw sweep, no confirmation, all negative)',
   ev_pos='S1 confirmed variants: several RW, positive OOS on two representatives', ev_neg='S1 low/pdh OOS ~+0.01 (near null); large spec dispersion',
   direction='both', sessions='all', regimes='2022-25 bull (untested bear)', oos='mixed-positive', fragility='spec-dispersion; some low OOS',
   next='confirmed vs unconfirmed sweep in a frozen side/regime-matched null'),
 dict(id='P002', name='Failed-Breakout Fade', file=True, status='SUPPORTED EXPLORATORILY', confidence='medium',
   defn='A breakout beyond a prior-day level that fails (closes back inside) is faded back into range.',
   behavior='Failed break at prior-day level reverts.', econ='Breakout buyers trapped on the failed extension are forced to unwind, feeding the fade.',
   fam_pos='S2 (low/pdh OOS +0.26)', fam_neg='S12 range-rotation (generic, negative)',
   ev_pos='S2 low/pdh: OOS +0.26, RW', ev_neg='high maxDD ~24R; limited independent replication', direction='long (tested)',
   sessions='all', regimes='bull', oos='positive', fragility='dd high; one family', next='matched null; test short-side symmetry'),
 dict(id='P003', name='Opening-Range Momentum', file=True, status='SUPPORTED EXPLORATORILY', confidence='medium',
   defn='Break of the session opening range (first ~1h) in the break direction (NY).',
   behavior='Opening-range break continues.', econ='Opening auction sets the day bias; early flow continues intraday.',
   fam_pos='S5 (ny/up exp .166, OOS +.18, positive every year 2022-25)', fam_neg='S30 kill-zone (fixed-clock range) negative',
   ev_pos='S5: PF 1.48, maxDD 7R, positive every year, OOS +.18', ev_neg='long/bull exposure (beta-suspect)', direction='long (tested)',
   sessions='NY', regimes='bull', oos='positive', fragility='beta-suspect', next='beta-adjusted matched null across regimes'),
 dict(id='P004', name='Round-Number Momentum', file=True, status='SUPPORTED EXPLORATORILY', confidence='low',
   defn='A clean break THROUGH a psychological round level ($100) continues; rejection at round levels does NOT work.',
   behavior='$100-level breakouts continue; rejections fade to noise.', econ='Clustered orders/stops at round levels; once cleared, momentum follows.',
   fam_pos='S22 (mode=breakout, $100, OOS +.15)', fam_neg='S22 (mode=reject, negative)',
   ev_pos='S22 $100 breakout: OOS +.15, RW, t1=.02', ev_neg='threshold ($100) may be selected; thin evidence', direction='both',
   sessions='all', regimes='bull', oos='positive', fragility='single-threshold selection', next='test $50/$100/$200 with multiplicity in a frozen null'),
 dict(id='P005', name='Trend Efficiency (gated continuation)', file=True, status='SUPPORTED EXPLORATORILY', confidence='low',
   defn='Continuation entries only when the trend is CLEAN (high Kaufman efficiency ratio); skip choppy trends.',
   behavior='Continuation in efficient trends is weakly positive; raw continuation is negative.', econ='Clean trends persist; efficiency filters noise.',
   fam_pos='S39 (er_thr=0.5, OOS +.02)', fam_neg='S15/S38 (raw continuation, negative)',
   ev_pos='S39 high-efficiency variant positive', ev_neg='effect ~.02R, only 2 RW, variant-dependent', direction='both',
   sessions='all', regimes='trend', oos='weak-positive', fragility='tiny effect; threshold-selected', next='efficiency-gate ablation in matched null'),
 dict(id='P006', name='Short-Term Overreaction / Return Reversal', file=True, status='SUPPORTED EXPLORATORILY', confidence='low',
   defn='Fade the largest L-bar return (overreaction); the biggest recent mover reverses.',
   behavior='Large 6-bar moves partially reverse.', econ='Liquidity providers are compensated for absorbing overreaction.',
   fam_pos='S42 (L=6, thr=1.2%, OOS +.18, 3 RW)', fam_neg='S8 distance-from-SMA extension (marginal)',
   ev_pos='S42: 3 RW, OOS +.18', ev_neg='small n (~43)', direction='both', sessions='all', regimes='bull', oos='positive',
   fragility='small n / high uncertainty', next='matched null; larger-n replication'),
 dict(id='P007', name='MTF Trend Alignment', file=True, status='MIXED', confidence='medium',
   defn='HTF-aligned (h4/h1) trend-continuation triggers on the LTF.',
   behavior='HTF-aligned longs positive but highly correlated with S20/S17-break.', econ='Higher-TF order-flow bias persists onto lower TF.',
   fam_pos='S9 (OOS +.10-.20), S20 (OOS +.17)', fam_neg='correlated cluster; beta-suspect',
   ev_pos='S9/S20 positive OOS', ev_neg='monthly-corr .75-.88 among S9/S20/S17-break -> ONE bet, not independent confirmations',
   direction='long', sessions='all', regimes='bull', oos='positive-but-correlated', fragility='beta + redundancy',
   next='collapse to one predeclared representative; beta-adjust'),
 dict(id='P008', name='Session Transition', file=True, status='MIXED', confidence='low',
   defn='Cross of the prior-session extreme at a new session start (breakout/fade).',
   behavior='Weak positive OOS but near-zero expectancy.', econ='New-session liquidity injection continues or fades the prior range.',
   fam_pos='S6 (OOS +.12-.16)', fam_neg='near-zero exp (~.02); fragile',
   ev_pos='S6 london/fade, ny/break: positive OOS', ev_neg='expectancy ~.02R; may not clear costs', direction='long',
   sessions='london/ny', regimes='bull', oos='positive-tiny', fragility='near-cost edge', next='matched null; is edge > costs?'),
 dict(id='P009', name='Streak Persistence', file=True, status='INCONCLUSIVE', confidence='low',
   defn='N consecutive same-direction closes then reverse (overextension) or continue.',
   behavior='Fade of a 6-bar streak weakly positive OOS but high drawdown.', econ='Short runs overextend / attract mean-reversion.',
   fam_pos='S45 (fade k=6, OOS +.13)', fam_neg='maxDD 39R; 0 RW',
   ev_pos='S45 fade-6 OOS +.13', ev_neg='high DD; not research-worthy', direction='both', sessions='all', regimes='bull',
   oos='weak-positive', fragility='high DD', next='drawdown control + matched null'),
 dict(id='P010', name='Liquidity Memory (levels revisited)', file=True, status='MIXED', confidence='low',
   defn='Prior-day / weekly reference levels are revisited and react (support/resistance memory).',
   behavior='Some level reactions (weekly pw_high break, pw_low reject) positive; prev-day marginal.', econ='Resting orders and reference anchoring at remembered levels.',
   fam_pos='S17 (weekly pw_high-break, pw_low-reject partial +OOS)', fam_neg='S16 (prev-day levels, marginal); several S17 variants OOS-negative',
   ev_pos='S17 some RW', ev_neg='S17 pw_high-break OOS -.10; mixed', direction='both', sessions='all', regimes='bull', oos='mixed',
   fragility='knife-edge variants', next='level-memory vs random-line reaction in a frozen null'),
 dict(id='P011', name='Raw Liquidity Sweep (no confirmation)', file=True, status='REPEATEDLY NEGATIVE', confidence='high',
   defn='Reverse immediately on a sweep of a level WITHOUT any confirmation.',
   behavior='Immediate sweep-reversal loses.', econ='Without confirmation the sweep is as likely continuation as reversal.',
   fam_pos='none', fam_neg='S21 (all 48 variants negative; short side worse)',
   ev_pos='none', ev_neg='S21 best -0.09; maxDD 262R', direction='both', sessions='all', regimes='bull', oos='negative',
   fragility='-', next='none (closed); contrast documents the value of confirmation (P001)'),
 dict(id='P012', name='Generic Trend / Pullback Continuation', file=True, status='REPEATEDLY NEGATIVE', confidence='high',
   defn='Enter continuation on a pullback to EMA/zone in an established trend, with or without confirmation.',
   behavior='Pullback continuation loses regardless of entry timing.', econ='On M15 gold the pullback whipsaws eat the continuation edge.',
   fam_pos='none (efficiency-gated variant is P005)', fam_neg='S7, S10, S15, S38 (all negative, early or late entry)',
   ev_pos='none', ev_neg='S38 early-entry -0.10; S7/S10/S15 negative', direction='both', sessions='all', regimes='bull', oos='negative',
   fragility='-', next='none (closed); the only live variant is efficiency-gated (P005)'),
 dict(id='P013', name='Breakout / Expansion Chasing (incl. volatility compression)', file=True, status='REPEATEDLY NEGATIVE', confidence='high',
   defn='Enter on a breakout/expansion of a range (with HTF filter, volume gate, squeeze, or duration).',
   behavior='Breakout chasing loses even with HTF/volume/duration gates.', econ='Fakeout rate + chasing the move + wide stops dominate.',
   fam_pos='none (round-number breakout is a distinct level mechanism, P004)', fam_neg='S3, S4, S23, S46, S48 negative',
   ev_pos='none', ev_neg='S23 (HTF) -0.09; S46 (volume) OOS -.02; S48 (duration) -0.13', direction='both', sessions='all',
   regimes='bull', oos='negative', fragility='-', next='none (closed); volume is NOT the missing ingredient (S46)'),
 dict(id='P014', name='Value / VWAP Reaction (incl. acceptance/rejection)', file=False, status='MIXED', confidence='medium',
   defn='Reversion/continuation at VWAP, VWAP bands, value-area edges, or anchored VWAP. NOTE: acceptance and rejection are OPPOSITE-direction subtypes (Codex review) — treated as subtypes, both tested.',
   behavior='Mostly negative with one isolated marginal exception (S8) -> MIXED, not uniformly negative (Codex review).', econ='Auction value should attract price, but the sigma-band VA proxy carries no edge on M15.',
   fam_pos='S8 marginal (OOS +.11, isolated)', fam_neg='S26 value-area, S27 reclaim, S28 anchored all negative',
   ev_pos='S8 vwap MR marginal', ev_neg='S26/S27/S28 negative', direction='long', sessions='all', regimes='bull',
   oos='mostly-negative', fragility='S8 exception', next='true volume-profile value area (needs finer data)'),
 dict(id='P015', name='Calendar Seasonality', file=False, status='REPEATEDLY NEGATIVE', confidence='high',
   defn='Fixed weekday / month-boundary / time-of-day directional effects.',
   behavior='Strong in-sample but failed to replicate OOS.', econ='No persistent mechanism; family-wise selection produces in-sample artifacts.',
   fam_pos='in-sample only (S29 exp up to .42)', fam_neg='OOS-refuted (S31 OOS -.44; S29-Thu -.03)',
   ev_pos='none robust', ev_neg='OOS failure under family-wise multiplicity', direction='long-biased', sessions='varies',
   regimes='in-sample only', oos='failed to replicate', fragility='overfit', next='single pre-registered window, family-wise-corrected, untouched data'),
 dict(id='P016', name='Regime Routing', file=False, status='REPEATEDLY NEGATIVE', confidence='medium',
   defn='A meta-router deploying continuation in trend regime and mean-reversion in range regime.',
   behavior='Always-on router adds no value.', econ='Firing in every regime doubles cost drag; a router must mostly stand aside.',
   fam_pos='none', fam_neg='S40 (all negative, n very high)', ev_pos='none', ev_neg='S40 best -0.12',
   direction='both', sessions='all', regimes='all', oos='negative', fragility='-', next='selective stand-aside router (future redesign)'),
 dict(id='P017', name='Intrabar Pressure (order-flow proxy)', file=False, status='REPEATEDLY NEGATIVE', confidence='medium',
   defn='Close-location-value (intrabar buying/selling pressure) continuation/exhaustion.',
   behavior='No edge.', econ='OHLC close position is too coarse a flow proxy on M15.', fam_pos='none', fam_neg='S44 (negative)',
   ev_pos='none', ev_neg='S44 best -0.07', direction='both', sessions='all', regimes='bull', oos='negative', fragility='-',
   next='requires true order-flow (tick/MBO) data — outside T0'),
 dict(id='P018', name='Momentum Divergence (RSI/price)', file=False, status='REPEATEDLY NEGATIVE', confidence='medium',
   defn='Price new extreme while RSI does not confirm -> reversal.',
   behavior='No edge; fires very often.', econ='Divergence is not predictive on M15 gold.', fam_pos='none', fam_neg='S43 (negative)',
   ev_pos='none', ev_neg='S43 best -0.10', direction='both', sessions='all', regimes='bull', oos='negative', fragility='-',
   next='none (closed)'),
 dict(id='P019', name='Volume-derived signals (climax reversal + breakout confirmation)', file=False, status='REPEATEDLY NEGATIVE', confidence='medium',
   defn='Two OPPOSITE-direction volume subtypes (Codex review): (a) volume-climax at an extreme -> REVERSAL; (b) volume expansion -> breakout CONTINUATION. Both tested; both negative.',
   behavior='No edge in either subtype; volume magnitude is not the missing ingredient for breakouts.', econ='Participation magnitude adds no predictive content on M15 OHLC volume.',
   fam_pos='none', fam_neg='S41 climax, S46 volume-confirmed breakout', ev_pos='none', ev_neg='S41 -0.04; S46 OOS -.02',
   direction='both', sessions='all', regimes='bull', oos='negative', fragility='-', next='none (closed)'),
]

# BEHAVIOR_REGISTRY
with open(os.path.join(K, 'BEHAVIOR_REGISTRY.jsonl'), 'w', encoding='utf-8') as f:
    for p in PRIM:
        rec = dict(p); rec.pop('file', None)
        rec['dataset_scope'] = 'XAUUSD OANDA M15 (H4/H1/D1 context), 2022-2025'; rec['sources'] = SRC; rec['date_added'] = '2026-07-13'
        f.write(json.dumps(rec) + '\n')
with open(os.path.join(K, 'BEHAVIOR_REGISTRY.md'), 'w', encoding='utf-8') as f:
    f.write('# BEHAVIOR_REGISTRY — behavioral primitives (S1-S51)\n\n')
    f.write('Primitives = observable market behaviors abstracted from strategy families. Status never uses '
            '"VALIDATED". Dataset scope: XAUUSD M15, 2022-2025 (predominantly bull). Machine copy: BEHAVIOR_REGISTRY.jsonl.\n\n')
    order = {'SUPPORTED EXPLORATORILY': 0, 'MIXED': 1, 'INCONCLUSIVE': 2, 'REPEATEDLY NEGATIVE': 3, 'TECHNICALLY INVALID': 4}
    for p in sorted(PRIM, key=lambda x: order.get(x['status'], 9)):
        f.write(f"## {p['id']} — {p['name']}  ·  **{p['status']}** (confidence {p['confidence']})\n")
        f.write(f"- Definition: {p['defn']}\n- Observable behavior: {p['behavior']}\n- Proposed mechanism: {p['econ']}\n")
        f.write(f"- Supporting families: {p['fam_pos']} · Contradicting: {p['fam_neg']}\n")
        f.write(f"- OOS: {p['oos']} · direction {p['direction']} · regimes {p['regimes']} · fragility: {p['fragility']}\n")
        f.write(f"- Next falsification test: {p['next']}\n\n")

# primitive files
for p in PRIM:
    if not p.get('file'):
        continue
    with open(os.path.join(P, f"{p['id']}_{p['name'].split('(')[0].strip().replace(' ', '_').replace('/', '_')}.md"), 'w', encoding='utf-8') as f:
        f.write(f"# {p['id']} — {p['name']}\n\n## Claim\n{p['behavior']} ({p['status']}, confidence {p['confidence']}; NOT validated alpha.)\n\n")
        f.write(f"## Operational definition\n{p['defn']}\n\n## Evidence FOR\n{p['ev_pos']}\nSupporting families: {p['fam_pos']}\n\n")
        f.write(f"## Evidence AGAINST\n{p['ev_neg']}\nContradicting families: {p['fam_neg']}\n\n")
        f.write(f"## Proposed economic mechanism\n{p['econ']}\n\n")
        f.write(f"## Context where it APPEARS\nregimes {p['regimes']}, sessions {p['sessions']}, direction {p['direction']}\n\n")
        f.write(f"## Context where it DISAPPEARS / reducibility\n{p['fam_neg']}; OOS {p['oos']}. Reducible to gold beta not yet ruled out.\n\n")
        f.write(f"## Status\n{p['status']} (confidence {p['confidence']})\n\n## Limitations\n{p['fragility']}; 4-yr bull sample; family-wise selection not corrected; costs not stress-tested.\n\n")
        f.write(f"## Next test\n{p['next']}\n\n## Sources\n{SRC}\n")

n_files = sum(1 for p in PRIM if p.get('file'))
print(f"primitives total {len(PRIM)}, files {n_files}")
print('supported', sum(1 for p in PRIM if p['status'] == 'SUPPORTED EXPLORATORILY'),
      'mixed', sum(1 for p in PRIM if p['status'] == 'MIXED'),
      'inconclusive', sum(1 for p in PRIM if p['status'] == 'INCONCLUSIVE'),
      'negative', sum(1 for p in PRIM if p['status'] == 'REPEATEDLY NEGATIVE'))
# also copy the mechanism registry into knowledge/
import shutil
for fn in ('MECHANISM_REGISTRY.md', 'MECHANISM_REGISTRY.parquet'):
    if os.path.exists(os.path.join(ROOT, fn)):
        shutil.copy(os.path.join(ROOT, fn), os.path.join(K, fn))
print('done')
