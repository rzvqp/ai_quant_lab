"""BUILD the official Executable Strategy Library under knowledge/strategies/.

Converts EXISTING frozen research into one executable strategy spec per family (S1-S51). It ONLY READS:
  - the frozen result parquets (results/FAMILY_RESULTS.parquet, results/ext_families/EXT_FAMILY_RESULTS.parquet),
  - the frozen engine grammars (mstrat.REGISTRY / mstrat_ext.EXT_REGISTRY) to resolve the representative
    hypothesis's exact parameters,
  - the curated qualitative metadata (code/strategy_library_metadata.py, transcribed from the frozen family code).
It runs NO backtest, changes NO engine code, optimises NOTHING, invents NO strategy. Deterministic.

Per family it emits knowledge/strategies/S<NN>_<slug>/{README.md, strategy.json}. strategy.json is the
machine-readable interface for the future AI execution engine. Also writes knowledge/strategies/INDEX.md and
knowledge/strategies/library_manifest.json. S32-S37 (external-data, not implemented) get NOT_IMPLEMENTED stubs.
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS, mstrat_ext as MSX
from strategy_library_metadata import META, NOT_IMPLEMENTED

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, 'knowledge', 'strategies')
os.makedirs(LIB, exist_ok=True)

# Universal (engine-level) facts injected into every spec — NOT strategy-specific.
UNIVERSAL = dict(
    timeframe='M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.',
    position_sizing=dict(
        model='risk-normalised (1R per trade)',
        risk_definition='risk = |entry - executable_stop|; result R = (dir*(exit-entry) - 2*cost)/risk',
        stop_floor='executable risk = max(2*spread_ticks*tick, 5*tick, 0.10*ATR) = max(0.20, 0.50, 0.10*ATR) price units (v2, pre-registered)',
        costs='(spread 1 + slippage 1) ticks/side * 0.1 = 0.10/side; 0.20 round-trip charged in R',
        concurrency='ONE position at a time (overlapping signals suppressed until the open trade closes)',
        absolute_size='lot = per-trade risk budget / risk-distance — an EXECUTION-LAYER decision, NOT set by the research'),
    universal_invalid=['ATR non-finite or <= 0 at the signal bar',
                       'signal on the last available bar (no next-open to fill)',
                       'a position is already open (overlap suppression)'],
    walk_forward='NOT RUN (lab-wide; see PROJECT_AUDIT.md).',
    holdout='Terminal 20% M15 holdout SEALED — never used in any metric here.')

# Matched-null / Wave-1 provenance per family (only where a test was actually run; else the honest default).
MC_DEFAULT = ('NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. '
              'The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.')
MC_NOTES = {
 'S1': 'Matched-null pilot (research, engine-validation only). Wave-1 EXP-03 beta/regime-matched null p=0.0069 '
       '(Holm-adj 0.042) — DIAGNOSTIC-grade, and OOS expectancy is NEGATIVE. Wave-1 EXP-01 (confirmation contribution) '
       'and EXP-05 (level placebo) = NO DIFFERENCE DETECTED. NO confirmed alpha.',
 'S5': 'Matched-null pilot (research). Wave-1 EXP-04 beta/regime-matched null p=0.177 (NOT significant) -> the edge is '
       'substantially session/regime BETA (unstratified anchor p=0.034). I7 stands for this primitive.',
 'S9': 'Matched-null pilot representative tested (engine-validation pilot; no strategy verdict issued).',
 'S6': 'Matched-null pilot used an S6 extreme hypothesis as a known tiny-stop/outlier CONTROL (not this representative).',
 'S2': 'Wave-1 EXP-06 level placebo: real above shuffled but NOT significant (NO DIFFERENCE DETECTED).',
 'S39': 'Wave-1 EXP-02: the efficiency gate did NOT select better-than-random continuation trades at the family-wise bar '
        '(NO DIFFERENCE DETECTED).',
}

def slug(s):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', s.lower())).strip('_')

def load_all():
    fr = pd.read_parquet(os.path.join(ROOT, 'results', 'FAMILY_RESULTS.parquet'))
    ext = pd.read_parquet(os.path.join(ROOT, 'results', 'ext_families', 'EXT_FAMILY_RESULTS.parquet'))
    return pd.concat([fr, ext], ignore_index=True)

def representative(sub):
    """Frozen selection rule (same as the matched-null pilot): research_worthy -> largest n; else hist_prof ->
    largest n; else largest n. Returns (row, rule_tag)."""
    for flag, tag in [('research_worthy', 'research_worthy & largest-n'), ('hist_prof', 'hist_profitable & largest-n')]:
        s = sub[sub[flag]]
        if len(s):
            return s.sort_values('n', ascending=False).iloc[0], tag
    return sub.sort_values('n', ascending=False).iloc[0], 'largest-n (no positive hypothesis)'

def resolve_params(fam, hid):
    reg = MS.REGISTRY if fam in MS.REGISTRY else MSX.EXT_REGISTRY
    for h in reg[fam][0]():
        if h['id'] == hid:
            return {k: v for k, v in h.items() if k not in ('id', 'family')}
    return {}

def confidence(rep, m, override):
    if override:
        return 'INVALID'
    rw, hp, ve = bool(rep['research_worthy']), bool(rep['hist_prof']), float(rep['val_exp'])
    frag = bool(rep['fragile'])
    if rw and hp and ve > 0:
        c = 'LOW — exploratory; research-worthy with positive out-of-sample expectancy'
    elif rw and ve <= 0:
        c = 'VERY LOW — research-worthy in-sample but non-positive out-of-sample'
    elif hp:
        c = 'VERY LOW — historically profitable but not research-worthy'
    else:
        c = 'NEGATIVE — family unprofitable on the research segment'
    if frag:
        c += ' (flagged FRAGILE — dominated by few periods)'
    return c

def num(fam):
    return int(fam[1:])

def fnum(x, n=4):
    try:
        x = float(x)
        return None if (x != x) else round(x, n)
    except Exception:
        return None

def build_family(fam, allr):
    md = META[fam]; sub = allr[allr.fam == fam]
    override = md.get('status_override')
    status = 'INVALID' if override else 'IMPLEMENTED'
    fam_agg = dict(n_hypotheses=int(len(sub)), n_hist_profitable=int(sub['hist_prof'].sum()),
                   n_research_worthy=int(sub['research_worthy'].sum()),
                   best_exp=fnum(sub['exp'].max()), median_exp=fnum(sub['exp'].median()))
    if len(sub) == 0:
        rep, rule = None, 'no committed results'
    else:
        rep, rule = representative(sub)
    if rep is not None:
        m = dict(hypothesis_id=rep['id'], n=int(rep['n']), expectancy_R=fnum(rep['exp']), profit_factor=fnum(rep['pf'], 3),
                 drawdown_R=fnum(rep['dd'], 2), win_rate=fnum(rep['win'], 3), sumR=fnum(rep['sumR'], 2),
                 median_R=fnum(rep['median']), trimmed5_R=fnum(rep['trim5']), months=int(rep['months']),
                 pos_months=int(rep['pos_months']), years=fnum(rep['years'], 2), side=str(rep['side']),
                 hist_profitable=bool(rep['hist_prof']), research_worthy=bool(rep['research_worthy']),
                 fragile=bool(rep['fragile']), top1_share=fnum(rep['t1'], 3), oos_expectancy_R=fnum(rep['val_exp']))
        params = resolve_params(fam, rep['id'])
        conf = confidence(rep, m, override)
    else:
        m, params, conf = {}, {}, ('INVALID' if override else 'UNKNOWN — no committed results')
    mc = MC_NOTES.get(fam, MC_DEFAULT)
    invalid = list(UNIVERSAL['universal_invalid'])
    if md.get('invalid_extra'):
        invalid.append(md['invalid_extra'])
    if override:
        invalid.append(override)
    val = _validation_text(fam, status, fam_agg, m, override)
    spec = dict(
        id=fam, name=md['name'], klass=md['klass'], slug=f"S{num(fam):02d}_{slug(md['name'])}", status=status,
        timeframe=UNIVERSAL['timeframe'], sessions=md['sessions'], long_short=md['long_short'],
        htf_context=md['htf'], mechanism=md['mechanism'], entry_rules=md['entry'], exit_rules=md['exit_rules'],
        stop_loss_rules=md['stop_rules'], required_confirmations=md['confirmations'],
        invalid_conditions=invalid, position_sizing=UNIVERSAL['position_sizing'], grammar=md['grammar_dims'],
        executable_default=dict(selection_rule=rule, hypothesis_id=(rep['id'] if rep is not None else None), params=params),
        performance=dict(historical=m, oos_expectancy_R=(m.get('oos_expectancy_R') if m else None),
                         drawdown_R=(m.get('drawdown_R') if m else None),
                         profit_factor=(m.get('profit_factor') if m else None),
                         expectancy_R=(m.get('expectancy_R') if m else None), family=fam_agg),
        monte_carlo=mc, walk_forward=UNIVERSAL['walk_forward'], confidence=conf, validation_status=val,
        provenance=dict(engine='mstrat.py v2 (FROZEN)', module=('mstrat' if fam in MS.REGISTRY else 'mstrat_ext'),
                        results_parquet=('results/FAMILY_RESULTS.parquet' if fam in MS.REGISTRY else 'results/ext_families/EXT_FAMILY_RESULTS.parquet'),
                        generated_from='frozen research; NO re-backtest, NO optimisation, NO engine change',
                        holdout=UNIVERSAL['holdout']))
    return spec

def _validation_text(fam, status, agg, m, override):
    base = ('EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; '
            'walk-forward NOT run. ')
    if status == 'INVALID':
        return base + f"THIS FAMILY IS INVALID: {override}"
    fam_line = (f"Family: {agg['n_hypotheses']} hypotheses, {agg['n_hist_profitable']} historically-profitable, "
                f"{agg['n_research_worthy']} research-worthy. ")
    if m:
        rep_line = (f"Representative {m['hypothesis_id']}: n={m['n']}, exp={m['expectancy_R']}R, PF={m['profit_factor']}, "
                    f"maxDD={m['drawdown_R']}R, OOS exp={m['oos_expectancy_R']}R, pos-months {m['pos_months']}/{m['months']}, "
                    f"{'research-worthy' if m['research_worthy'] else ('hist-profitable' if m['hist_profitable'] else 'not profitable')}"
                    f"{', FRAGILE' if m['fragile'] else ''}. ")
    else:
        rep_line = 'No committed results. '
    return base + fam_line + rep_line

def render_readme(spec):
    p = spec; perf = p['performance']; m = perf['historical']; fam = perf['family']; d = p['executable_default']
    def g(x, dflt='—'):
        return dflt if x is None else x
    lines = []
    A = lines.append
    A(f"# {p['id']} — {p['name']}")
    A('')
    A(f"> **Class:** {p['klass']}  ·  **Status:** {p['status']}  ·  **Timeframe:** M15  ·  "
      f"**Applicability:** {p['long_short']}  ·  **Confidence:** {p['confidence']}")
    A('')
    A('*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine '
      'change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*')
    A('')
    A('## Mechanism'); A(p['mechanism']); A('')
    A('## Rules')
    A(f"- **Entry:** {p['entry_rules']}")
    A(f"- **Exit:** {p['exit_rules']}")
    A(f"- **Stop-loss:** {p['stop_loss_rules']}")
    A(f"- **Required confirmations:** {p['required_confirmations']}")
    A(f"- **Timeframe:** {p['timeframe']}")
    A(f"- **Sessions:** {p['sessions']}")
    A(f"- **Long/Short applicability:** {p['long_short']}")
    A(f"- **Higher-timeframe context:** {p['htf_context']}")
    A(f"- **Grammar (degrees of freedom):** {p['grammar']}")
    A('')
    A('### Invalid conditions')
    for c in p['invalid_conditions']:
        A(f"- {c}")
    A('')
    A('### Position sizing assumptions')
    ps = p['position_sizing']
    for k in ['model', 'risk_definition', 'stop_floor', 'costs', 'concurrency', 'absolute_size']:
        A(f"- **{k}:** {ps[k]}")
    A('')
    A('## Executable default (representative hypothesis)')
    A(f"- **Selection rule:** {d['selection_rule']}")
    A(f"- **Hypothesis id:** `{g(d['hypothesis_id'])}`")
    if d['params']:
        A(f"- **Parameters:** `{json.dumps(d['params'])}`")
    A('')
    A('## Performance summary (research segment; frozen)')
    if m:
        A('| metric | value |')
        A('|---|---|')
        A(f"| Expectancy (R/trade) | {g(m.get('expectancy_R'))} |")
        A(f"| Profit Factor | {g(m.get('profit_factor'))} |")
        A(f"| Max Drawdown (R) | {g(m.get('drawdown_R'))} |")
        A(f"| Win rate | {g(m.get('win_rate'))} |")
        A(f"| Trades (n) | {g(m.get('n'))} |")
        A(f"| Positive months | {g(m.get('pos_months'))}/{g(m.get('months'))} |")
        A(f"| Top-1 trade share | {g(m.get('top1_share'))} |")
        A(f"| **OOS expectancy (R/trade)** | {g(m.get('oos_expectancy_R'))} |")
        A(f"| Historically profitable | {g(m.get('hist_profitable'))} |")
        A(f"| Research-worthy | {g(m.get('research_worthy'))} |")
        A(f"| Fragile | {g(m.get('fragile'))} |")
    else:
        A('_No committed results for this family._')
    A('')
    A(f"**Family distribution:** {fam['n_hypotheses']} hypotheses · {fam['n_hist_profitable']} historically-profitable · "
      f"{fam['n_research_worthy']} research-worthy · best exp {g(fam['best_exp'])}R · median exp {g(fam['median_exp'])}R.")
    A('')
    A('## Validation')
    A(f"- **Historical metrics:** expectancy {g(m.get('expectancy_R'))}R, PF {g(m.get('profit_factor'))}, "
      f"maxDD {g(m.get('drawdown_R'))}R over n={g(m.get('n'))} (research 60%).")
    A(f"- **OOS metrics:** expectancy {g(m.get('oos_expectancy_R'))}R (validation 20%).")
    A(f"- **Drawdown:** {g(m.get('drawdown_R'))}R (research).")
    A(f"- **Profit Factor:** {g(m.get('profit_factor'))}.")
    A(f"- **Expectancy:** {g(m.get('expectancy_R'))}R/trade.")
    A(f"- **Monte Carlo summary:** {p['monte_carlo']}")
    A(f"- **Walk-forward status:** {p['walk_forward']}")
    A(f"- **Current confidence:** {p['confidence']}")
    A(f"- **Validation status:** {p['validation_status']}")
    A('')
    A(f"*Provenance: engine {p['provenance']['engine']} (module `{p['provenance']['module']}`), metrics from "
      f"`{p['provenance']['results_parquet']}`. {p['provenance']['generated_from']}. {p['provenance']['holdout']}*")
    A('')
    return '\n'.join(lines)

def write_family(spec):
    folder = os.path.join(LIB, spec['slug']); os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, 'strategy.json'), 'w') as f:
        json.dump(spec, f, indent=1)
    with open(os.path.join(folder, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(render_readme(spec))
    return spec['slug']

def write_not_implemented(fam, desc):
    sl = f"S{num(fam):02d}_not_implemented"
    folder = os.path.join(LIB, sl); os.makedirs(folder, exist_ok=True)
    spec = dict(id=fam, name=f"{fam} (not implemented)", status='NOT_IMPLEMENTED', reason=desc,
                timeframe='n/a', validation_status='NOT IMPLEMENTED — blocked on external data acquisition (CEO-gated).',
                provenance=dict(generated_from='no code, no results; documented for library completeness'))
    json.dump(spec, open(os.path.join(folder, 'strategy.json'), 'w'), indent=1)
    open(os.path.join(folder, 'README.md'), 'w', encoding='utf-8').write(
        f"# {fam} — NOT IMPLEMENTED\n\n> **Status:** NOT_IMPLEMENTED (external-data-blocked, CEO-gated)\n\n{desc}\n\n"
        f"No executable specification exists: this family has no engine code and no committed results. Listed for "
        f"library completeness across the S1-S51 numbering.\n")
    return sl, spec

def main():
    allr = load_all()
    specs = []
    for fam in sorted(META, key=num):
        spec = build_family(fam, allr); write_family(spec); specs.append(spec)
    ni = []
    for fam in sorted(NOT_IMPLEMENTED, key=num):
        sl, s = write_not_implemented(fam, NOT_IMPLEMENTED[fam]); ni.append((fam, sl, s))
    # manifest (machine index for the AI Trader)
    manifest = dict(
        library='Executable Strategy Library', interface='Research-Lab -> AI-Trader',
        engine='mstrat.py v2 (FROZEN)', generated_from='frozen research parquets + frozen family code; no re-backtest',
        holdout_status='SEALED', global_fdr='NOT RUN', walk_forward='NOT RUN',
        overall_verdict='EXPLORATORY — no confirmed alpha; specs are executable descriptions of researched behaviour',
        counts=dict(implemented=len(specs), invalid=sum(1 for s in specs if s['status'] == 'INVALID'),
                    not_implemented=len(ni), total_numbered=len(specs) + len(ni)),
        strategies=[dict(id=s['id'], slug=s['slug'], name=s['name'], status=s['status'],
                         expectancy_R=s['performance']['expectancy_R'], oos_R=s['performance']['oos_expectancy_R'],
                         profit_factor=s['performance']['profit_factor'], drawdown_R=s['performance']['drawdown_R'],
                         confidence=s['confidence']) for s in specs] +
                   [dict(id=f, slug=sl, name=s['name'], status='NOT_IMPLEMENTED') for f, sl, s in ni])
    json.dump(manifest, open(os.path.join(LIB, 'library_manifest.json'), 'w'), indent=1)
    _write_index(specs, ni)
    print(f"Strategy Library built: {len(specs)} implemented ({manifest['counts']['invalid']} invalid), "
          f"{len(ni)} not-implemented, {manifest['counts']['total_numbered']} total numbered.")
    print(f"Output: {LIB}")

def _write_index(specs, ni):
    L = ['# Executable Strategy Library — INDEX', '',
         'Official interface between the Research Lab and the future AI Trader. One folder per strategy '
         '(`S<NN>_<slug>/`) with a human `README.md` and a machine-readable `strategy.json`. Machine index: '
         '`library_manifest.json`.', '',
         '**Provenance:** generated from FROZEN research (result parquets + frozen family code). NO re-backtest, NO '
         'optimisation, NO engine change, NO new strategy. **Overall verdict: EXPLORATORY — no confirmed alpha.** '
         'Holdout SEALED · global-FDR NOT run · walk-forward NOT run. Metrics are research-segment (60%); OOS is the '
         'validation segment (20%).', '',
         '| id | strategy | status | exp (R) | OOS (R) | PF | maxDD (R) | confidence |',
         '|---|---|---|---|---|---|---|---|']
    for s in specs:
        pf = s['performance']; conf = s['confidence'].split(' — ')[0]
        L.append(f"| {s['id']} | [{s['name']}]({s['slug']}/README.md) | {s['status']} | "
                 f"{pf['expectancy_R']} | {pf['oos_expectancy_R']} | {pf['profit_factor']} | {pf['drawdown_R']} | {conf} |")
    for f, sl, s in ni:
        L.append(f"| {f} | [{s['name']}]({sl}/README.md) | NOT_IMPLEMENTED | — | — | — | — | — |")
    L += ['', '## Reading guide',
          '- **Positive-leaning (research-worthy + positive OOS):** the low-confidence exploratory candidates.',
          '- **Beta caveat:** S5 opening-range is substantially session/regime BETA (Wave-1 EXP-04); S1 sweep survives a '
          'beta-matched null on research but with NEGATIVE OOS (Wave-1 EXP-03) — neither is confirmed alpha.',
          '- **INVALID:** S47 (n<25), S49 (non-selective) — documented but not usable.',
          '- **NOT_IMPLEMENTED:** S32-S37 need external Tier-1/2 data (CEO-gated).',
          '- **No strategy here is validated alpha or production-ready.** The AI Trader must treat every spec as an '
          'exploratory hypothesis pending confirmatory testing (matched-null on the full universe, walk-forward, holdout).', '']
    open(os.path.join(LIB, 'INDEX.md'), 'w', encoding='utf-8').write('\n'.join(L))

if __name__ == '__main__':
    main()
