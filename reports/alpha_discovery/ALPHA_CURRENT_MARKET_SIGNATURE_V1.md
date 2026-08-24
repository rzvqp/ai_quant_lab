# ALPHA_CURRENT_XAUUSD_MARKET_SIGNATURE_V1 (FROZEN)

Mandate `ALPHA-XAUUSD-CURRENT-REGIME-SPECIALIST-DISCOVERY-001` §2. Mechanical, causal, price-normalized description of the CURRENT XAUUSD market. Frozen BEFORE any candidate P&L re-screen. NO future return / MFE / MAE / profitability used. Impl `sig_build.py` on the rebased current M15 (2011-07..2026-07-27, dataHash `57f4ed9544993c8f`).

## Descriptors (H4, causal, price-normalized)
`vol_norm`=atr/close · `vol_rel`=atr/atr_ma · `effic`=20-bar directional efficiency · `ddfh`=(close − 120-H4-high)/close · `ret60`=60-H4 return/close. z-normalized over full history (mu/sd frozen in `sig_build.py` output).

## Current window & frozen signature centroid
- Current window = last **90 days** (n_H4=396), latest closed bar **2026-07-27 16:00 UTC**, price ~$4085.
- Signature centroid (z): **vol_norm +1.09, vol_rel −0.06, effic −0.33, ddfh −1.06, ret60 −0.92**.
- Raw medians: vol_norm 0.0083 (0.83%/H4 = HIGH), vol_rel 0.997, effic −0.085, ddfh −0.064 (−6.4% off recent high), ret60 −0.027.
- **Economic reading: a HIGH-VOLATILITY CORRECTION within a high-price regime** — elevated vol, deep drawdown-from-high, negative medium-term drift, choppy efficiency. NOT a clean low-vol bull.
- **SIGNATURE_FINGERPRINT = `c8f5a8091e22aec1`** (frozen).

## CURRENT_LIKE_POPULATION_V1 (structural, NOT calendar)
- Definition: H4 bars within Euclidean z-distance ≤ p12 (=1.77) of the frozen centroid. **3030 H4 bars = 12.6% of history.** Saved `__cur_cache__/current_like_h4.parquet`.
- **Fraction of each year that is current-like:** 2011 22%, 2012 10%, 2013 22%, 2014 13%, 2015 19%, 2016 13%, 2017 2%, 2018 1%, 2019 4%, 2020 14%, 2021 16%, 2022 24%, 2023 7%, 2024 10%, 2025 10%, 2026 30%.
- **Key validation of the mandate:** current-like episodes are the HIGH-VOL CORRECTIONS across all history (2011/2013/2015/2020/2022/2026), NOT the low-vol clean-trend years (2017/2018/2019/2023/2024 all <10%). "Now" is structurally like the 2013 crash and 2022 correction, NOT the 2024 clean bull. The old cross-era gate demanded stability across BOTH — structurally inappropriate for a current-regime specialist.

## Time partition for current-regime research (§11 / rebase addendum §3)
Within CURRENT_LIKE_POPULATION_V1, partition by time (exposure recorded in the rebase audit):
- **DISCOVERY** = current-like bars ≤ 2021-12-31 (older high-vol corrections: 2011/2013/2015/2020/2021).
- **CONFIRMATION** = current-like 2022-01 → 2024-12 (2022 correction + 2024 pockets).
- **RECENT OOS (once-touched)** = current-like 2025-01 → 2026-07 (the newly-exposed slice; forward MT5 DEMO is the true untouched confirmation).

## Regime OFF-switch (§12, causal)
A CURRENT_REGIME_SPECIALIST activates only when the live H4 state is within z-distance ≤ 1.77 of the frozen centroid (same 5 causal descriptors), and deactivates when it leaves. Causal, no P&L. (Live routing uses the frozen mu/sd/centroid/threshold.)

## Status
`CURRENT_SIGNATURE_FROZEN` + `CURRENT_LIKE_POPULATION_FROZEN`. Next: reconstruct candidate inventory → re-screen ALL eligible candidates on CURRENT_LIKE (exact frozen defs, no retuning) → buckets A/B/C.
