# ve_brain — DEPENDENȚE (gate 8)

## Runtime
**NICIUNA externă.** Stdlib-only: `hashlib, json, math, dataclasses, enum, typing`. Fără numpy/pandas/scipy.
Fără importuri din branch-ul de dezvoltare, fără căi locale.

## Provenance internă (ce vinde artefactul, cu commit-ul sursă)
| Modul ve_brain | Sursă | Commit |
|---|---|---|
| `_ev_core.py` (motorul EV, byte-identic) | `decision_engine/decision_engine.py` @ `alpha-automation-v1` | `bdd15e5` |
| contractul de măsurare (referit, nu vândut aici) | `code/canonical_evaluator.py` | `dc28e4a` (A2 geometrie strictă) |
| taxonomia/nivelele (referite ca etichete) | `code/regime_classifier.py` (N1) | `62c447e` |

## Nivelele N1-N4 (turnul)
Artefactul consumă IEȘIRILE turnului prin contract (etichete/booleeni în `DecisionRequest`), **NU importă** modulele
turnului și **NU reconstruiește** detectoarele. Turnul (N1 `62c447e`, N2 `850815f`, N3 `5888978`, N4 `7f2694f`,
bus `ad8b586`) rămâne în `code/`; ve_brain nu-l copiază.

## Verificare gate 10 (motorul EV nu folosește nivelurile vechi)
`_ev_core.py` are ZERO importuri de proiect (doar stdlib) — deci nu poate atinge niciun tip de nivel, nou sau vechi.
Byte-identic cu `bdd15e5`: `git show bdd15e5:decision_engine/decision_engine.py` == `ve_brain/ve_brain/_ev_core.py`.
Adaptorul (`ev_engine.py`) mapează geometria ACTUALĂ (rr/r/cost) + probabilități în `DecisionInput`; nu reactivează
logica veche de niveluri.
