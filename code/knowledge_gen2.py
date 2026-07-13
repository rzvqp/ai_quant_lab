"""Generate STRATEGY_PROFILES.md and EXPLORATORY_PORTFOLIO_DIAGNOSTICS.md from verified JSON. READ-ONLY."""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, 'kb_dedup.json')))['clusters']
cor = json.load(open(os.path.join(ROOT, 'kb_correlations.json')))
SHORT = {'K_S5_session=ny_side=up', 'K_S2_side=low_ref=pdh_pdl', 'K_S1_side=high_liq_ref=pdh_pdl',
         'K_S1_side=low_liq_ref=swing', 'K_S20_ctx=h4up_trig=breakout', 'K_S22_mode=breakout',
         'K_S1_side=low_liq_ref=pdh_pdl', 'K_S17_level=pw_low_mode=reject'}

def status(c):
    v = c.get('rep_val')
    if c['cluster_id'] in ('K_S29_dow=3_side=up', 'K_S29_dow=4_side=up', 'K_S31_window=month_start_side=down'):
        return 'EXPLORATORY (calendar / family-wise-selection overfit)'
    if c['rep_fragile']:
        return 'FRAGILE'
    if c['cluster_id'] in SHORT:
        return 'RESEARCH WORTHY — SHORTLISTED (strict validation pending)'
    if v is not None and v < 0:
        return 'EXPLORATORY (negative OOS)'
    return 'RESEARCH WORTHY (strict validation pending)'

with open(os.path.join(ROOT, 'STRATEGY_PROFILES.md'), 'w', encoding='utf-8') as f:
    f.write('# STRATEGY_PROFILES — 22 distinct candidates (post-dedup)\n\n')
    f.write('Profiles from verified artifacts + read-only re-backtest (yearly, risk/ATR, long/short recovered '
            'for the representative). No validated alpha; strict validation (matched-null → global-FDR) CEO-gated.\n\n')
    for c in sorted(d, key=lambda x: (x['cluster_id'] not in SHORT, -(x.get('rep_val') or -9))):
        f.write(f"## {c['mechanism']}  ·  {status(c)}\n")
        f.write(f"- family {c['family']} · representative_hypothesis_id `{c['representative_id']}` · "
                f"{c['n_members']} RW member(s) · side {c['rep_side']}\n")
        f.write(f"- trades {c['rep_n']} · expectancy {c['rep_exp']:+.3f}R · PF {c['rep_pf']:.2f} · "
                f"win {c['rep_win']:.2f} · maxDD {c['rep_dd']:.1f}R · pos-months {c['rep_stab']:.2f} · years {c['rep_years']}\n")
        v = c.get('rep_val'); f.write(f"- OOS(validation) {('%+.3f'%v) if v is not None else 'NA'}R · "
                f"top1 share {c['rep_t1']:.2f} · fragile {c['rep_fragile']}\n")
        f.write(f"- yearly: {c.get('yearly', {})} · risk/ATR pctiles {c.get('risk_atr_pct', {})}\n")
        f.write(f"- long {c.get('long_n')}@{c.get('long_exp')} / short {c.get('short_n')}@{c.get('short_exp')}\n\n")

# PORTFOLIO diagnostics
cids = list(cor['month_streams'].keys())
long_ct = sum(1 for c in d if c['rep_side'] == 'long'); short_ct = sum(1 for c in d if c['rep_side'] == 'short')
both_ct = sum(1 for c in d if c['rep_side'] == 'both')
with open(os.path.join(ROOT, 'EXPLORATORY_PORTFOLIO_DIAGNOSTICS.md'), 'w', encoding='utf-8') as f:
    f.write('# EXPLORATORY_PORTFOLIO_DIAGNOSTICS (diagnostic only — NO weight optimization, NOT a validated portfolio)\n\n')
    f.write('## A. FACTS — exposure of the 22 distinct candidates\n')
    f.write(f'- Direction: **{long_ct} long, {short_ct} short, {both_ct} both**. The book is near-pure LONG gold.\n')
    f.write('- Common monthly window ≈ 26 months (2022-12 → 2025-02); correlations therefore have WIDE CIs.\n\n')
    f.write('## B. Correlation structure (monthly summed-R, 1500-boot 95% CI)\n')
    f.write('Strongest positive (redundant, CI excludes 0):\n\n| pair | r | 95% CI |\n|---|---|---|\n')
    for p in sorted([p for p in cor['pairs'] if p['r'] is not None], key=lambda z: -z['r'])[:8]:
        f.write(f"| {p['a'].replace('K_','')} ↔ {p['b'].replace('K_','')} | {p['r']:+.2f} | [{p['lo']:+.2f},{p['hi']:+.2f}] |\n")
    f.write('\nStrongest negative (complementary):\n\n| pair | r | 95% CI |\n|---|---|---|\n')
    for p in sorted([p for p in cor['pairs'] if p['r'] is not None], key=lambda z: z['r'])[:6]:
        f.write(f"| {p['a'].replace('K_','')} ↔ {p['b'].replace('K_','')} | {p['r']:+.2f} | [{p['lo']:+.2f},{p['hi']:+.2f}] |\n")
    f.write('\n## C. CLAUDE INTERPRETATION\n')
    f.write('- **Long-momentum cluster** (S9-any/align, S20-break, S17-pwhigh-break, S39; r .6–.88, CI excludes 0) '
            'is ONE bet — redundant; collapse to one representative before validation.\n')
    f.write('- Most "complementary" pairs have CIs crossing 0 (26 months) → **low correlation is NOT decorrelation**. '
            'The only resolved diversifier is the single SHORT candidate (S1 high/pdh) vs the long book.\n')
    f.write('- **Bull-beta domination risk (HIGH):** 19/22 candidates are long in a 2023-25 gold bull. The shortlist '
            'is largely one long-gold-beta exposure; genuine diversification is minimal until a beta-matched null runs.\n')
    f.write('- Concentration: candidates lean on 2023-24-25 (bull years); no bear-regime evidence exists in-sample.\n\n')
    f.write('## D. Guardrail\n- No weights optimized, no portfolio declared validated. Portfolio Architect stays '
            'deferred (correlations too uncertain at 26 months; beta not removed). CODEX FILESYSTEM REVIEW PENDING.\n')
print('generated STRATEGY_PROFILES.md, EXPLORATORY_PORTFOLIO_DIAGNOSTICS.md')
