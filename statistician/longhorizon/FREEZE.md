# TOP-5 FREEZE — written BEFORE any OOS inspection

Selection rule (mechanical, no discretion): **the 5 highest |DEV z| among the 60 declared hypotheses.**

| rank | ID | branch | class | state | horizon | DEV n_cond | DEV lift | DEV z |
|---|---|---|---|---|---|---|---|---|
| 1 | F1-P500-48 | F | TAIL | 5d/20d realised-vol ratio in bottom 20% | 48h | 57 | −0.070 | −3.64 |
| 2 | B3-EXC-48 | B | MAGNITUDE | same state (5d/20d vol contraction) | 48h | 57 | −53.08 p | −3.58 |
| 3 | E1-MAG-24 | E | MAGNITUDE | previous day's range in bottom 20% of its 20-day history | 24h | 389 | −14.36 p | −3.00 |
| 4 | D4-MAG-6 | D | MAGNITUDE | Asia (00–08 UTC) closed in the top/bottom 20% of its own range | 6h | 720 | −8.25 p | −2.87 |
| 5 | E1-EXC-48 | E | MAGNITUDE | same state as #3 (low-range previous day) | 48h | 185 | −34.71 p | −2.68 |

Noted at freeze time, before OOS:

- The 5 collapse to **3 distinct states** (vol-contraction, low-range-day, Asia-close-at-edge).
- **Every one is a MAGNITUDE/TAIL result, and every lift is NEGATIVE** — these states predict *smaller*
  subsequent movement. None of them predicts direction.
- **#1 and #2 rest on 57 DEV episodes**; #1's conditional cell is 0/57, so its z is a zero-cell artefact
  risk and is expected to be fragile.
- Best DIRECTION result in the whole scan is |z| = 1.98 (C4-DIR-24). 27 direction hypotheses, none reach 2.
- Bonferroni at m = 60 requires |z| > 3.02: only #1 and #2 clear it on DEV.

Pre-declared post-freeze battery (run once, no definition changes afterwards):
OOS · era blocks · matched controls (time-of-day is exact by construction; add trailing volatility,
recent return, trend state, range position as covariates) · outlier robustness (top-1%/5% contribution,
drop-best) · dependence robustness (double stride).
