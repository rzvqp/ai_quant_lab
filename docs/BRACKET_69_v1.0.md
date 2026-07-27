# BRACKET VERIFICATION — the 69 exclusion-flipped hypotheses

**Document ID:** STAT-BRACKET69-v1.0 · **Autor:** Research Lab · **Data:** 2026-07-26
**Cerere:** Statisticianul (via CEO 2026-07-25) — excluderea rămâne convenția primară corectă (mecanismul §WP-4b o susține), DAR verificare de bracket pentru orice ipoteză al cărei STATUS depinde de convenție = exact cele **69** care au trecut neprofitabil→profitabil sub excludere.
**Sferă:** măsurătoare. `target_first` e **toggle de instrument** (best-case), default False, **NEcomis ca implicit**. Fără holdout, fără promovare, fără re-rularea campaniei.

## Cele trei convenții
| convenție | tratament bară ambiguă | config |
|---|---|---|
| **worst-case** | toate rezolvate ca STOP (stop-first) = baseline actual | `mark_invalid=False, target_first=False` |
| **best-case** | toate rezolvate ca ȚINTĂ (target-first), tranzacții păstrate | `mark_invalid=False, target_first=True` |
| **excludere** | tranzacțiile lărgite-same-bar eliminate (convenția nouă) | `mark_invalid=True, target_first=False` |

**Sanity (refactor behavior-preserving):** worst == baseline (eșantion) ✅; excludere == reproduction_d2 (eșantion) ✅; supraviețuitor ATR sumR 33.52==33.52 ✅. Toggle-ul nu schimbă comportamentul default.

Status măsurat = `hist_prof` (n>0 & sumR>0 & exp>0 & pf>1.00). Prin construcție toate cele 69 au **worst=False** și **excludere=True**. Întrebarea de bracket: statusul sub **best-case**?

## Rezultat
| categorie | n | worst | best | excludere | interpretare (cifre) |
|---|---|---|---|---|---|
| **CONVENȚIE-DEPENDENTE** | **22** | False | **True** | True | statusul **DIFERĂ între worst și best** → aparține convenției de tie-break intrabar, NU ipotezei |
| **EXCLUDERE-CREATE** | **47** | False | **False** | True | neprofitabile sub AMBELE tie-break-uri (păstrând tranzacțiile); profitabile DOAR când tranzacțiile lărgite-same-bar (ne-executabile) sunt ELIMINATE |
| profitabile sub worst-case | 0 | — | — | — | niciuna (prin construcție) |

Familii: convenție-dependente = S3 (13), S1 (9). Excludere-create = S1 (23), S3 (9), S8 (8), S17/S2/S12 (2 fiecare), S16 (1).

## Ce spun cifrele (fără a concluziona — verdictul e al Statisticianului)
- **Niciuna dintre cele 69 nu e profitabilă sub convenția pesimistă worst-case** (prin construcție — sunt exact cele care au picat acolo).
- **22** au statusul determinat de **alegerea de tie-break** al barei ambigue: stop-first → pierzătoare, target-first → profitabile. Statusul lor **aparține convenției**, nu ipotezei (fragil la o presupunere intrabar arbitrară). Marcate ca **artefact-de-convenție**.
- **47** au statusul robust peste bracket-ul tie-break (worst==best==False) dar creat de **excluderea tranzacțiilor ne-executabile**: chiar scorând barele ambigue ca CÂȘTIGURI (best-case), ipoteza pierde; doar **eliminarea** tranzacțiilor lărgite-same-bar o face profitabilă. Statusul lor e contingent de **decizia de excludere** (pe care Statisticianul a marcat-o convenția primară corectă), nu de tie-break. Categorie neacoperită de binarul inițial (same-all-three / differ-worst-best) — o raportez explicit ca a treia.
- Notă mecanică: best-case (target-first) atinge TOATE barele ambigue din toate tranzacțiile, nu doar cele lărgite-same-bar; excluderea atinge doar cele lărgite-same-bar. De-aceea cele două nu sunt operații pe același set, și de-aceea 47 pot fi False sub best dar True sub excludere.

## Predare
Care dintre cele 22 (convenție-dependente) și 47 (excludere-create) contează ca profitabilitate reală = **decizie de Statistician**, împreună cu întrebarea despre potrivirea lui R și tratamentul barelor ambigue (excludere totală vs. raportare separată). Research Lab a livrat bracket-ul; nu concluzionează.

Artefacte: `results/reproduction_d2/bracket_69.{parquet,summary.json}`; instrument `code/bracket_69.py`; toggle `cfg['target_first']` în `mstrat.simulate` (default False). Baseline și reproduction_d2 neatinse. Holdout SEALED.
