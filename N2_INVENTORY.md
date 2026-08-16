# MANDAT N2 — INVENTAR EXCLUSIV DIN GIT + VERDICT

Repo `ai_quant_lab-wp5b`, branch `discovery-mk-matrix-v1`. Toate faptele de mai jos sunt confirmate DIRECT din git;
indiciile din conversație sunt tratate ca ipoteze de verificat (rezultatul verificării e notat).

## ETAPA 1 — Matricea de inventar

| componentă | repo | commit | fișier | input | output | contract/version | determinist/statistic | ratificat? | limitări | consumator azi | împachetat? | acțiune |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **N2 producer** | wp5b | head `850815f` (build `81a0a62`) | `code/bias_h1.py` | H1 OHLC + `i` + `regime_axes_status` (N1) | `LevelOutput[BiasState]` (factori `FactorDirection` LONG/SHORT/UNKNOWN: structure/displacement/liquidity/momentum) | `SCHEMA_VERSION="STAT-LEVEL2-BIAS-H1-SPEC-v1.0"` (spec id, NU un contract runtime de producător) | **DETERMINIST** (`emits_probability=False`; `direction_share_*` = descriptiv, nu previziune) | spec ratificat, dar **fără N2 Red Team handoff standalone în git** | momentum permanent `Unavailable`; `liquidity_above` = assumption | vendat în ve_tower `_tower/bias_h1.py` | **DA — dar doar ca dependență vendată, NU expus ca producător** | **PACKAGE (verdict B)** |
| N2 spec | wp5b | `1b2933c` | (mesaj commit) STAT-LEVEL2-BIAS-H1-SPEC-v1.0 | — | — | — | — | Statistician spec v1.0 | — | bias_h1 | n/a | referință |
| N2 directional | wp5b | `404b6c8` | SPEC3 (N3 anchor + N4 clock + **N2 directional**) | — | — | STAT-SPEC3-N2-DIRECTIONAL-SEMANTICS-v1.0, **manifest v2.7.61** | — | Statistician SPEC3 | — | bias_h1 head 850815f | n/a | referință |
| N2 test | wp5b | (curent) | `tests/test_bias_h1.py` | fixture-uri sintetice | — | — | — | test de cercetare | — | — | NU | reutilizabil ca fixture |
| n2_fingerprint (hook) | wp5b | ve_tower 0.3.0 | `contracts.py:46,111`; `n3.py:45`; `n4.py:48` | **string furnizat de apelant** | intră în node_input_fingerprint | `tower-n3/n4-request-v2` | — | PASS (ca parte din 0.3.0) | **NU validat, NU legat de un răspuns N2 real, NU propagat** | N3/N4 node fingerprint | DA | **clarificat + legat de N2 real (contract nou)** |

**Indicii verificate (NU acceptate orbește):** `81a0a62`=build N2 "NOT ratified" ✓; `1b2933c`=spec N2 ✓; `850815f`=head directional ✓; `404b6c8`=SPEC3 ✓; manifest real = **v2.7.61** (indiciul "v2.7.51" e GREȘIT); `RT-CODE-A-0011` / `B-L1` / `APPROVED_WITH_LIMITATIONS` / `PASS_WITH_LIMITATIONS` = **NECONFIRMATE în git** (nici în docs, nici în mesaje de commit). Afirmația „N2 emite factori deterministici, nu probabilitate" = **CONFIRMATĂ** din sursă (`emits_probability=False`).

## ETAPA 2 — Cele șase întrebări

1. **Ce e oficial N2?** Bias-ul direcțional H1 ca FACTORI deterministici (structure/displacement/liquidity/momentum → LONG/SHORT/UNKNOWN), per STAT-LEVEL2-BIAS-H1-SPEC-v1.0 + SPEC3 directional. **NU probabilitate, NU EV, NU decizie.**
2. **A existat un producător N2 real?** DA — `compute_bias(...)` în `code/bias_h1.py` (cod de cercetare cu spec ratificat), cu test `tests/test_bias_h1.py`.
3. **Nume/repo/commit?** `ai_quant_lab-wp5b` · `code/bias_h1.py` · head `850815f` (build `81a0a62`). Vendat byte-identic în ve_tower 0.3.0 (`_tower/bias_h1.py`, blob `1638c7dd…`, source commit `850815f`).
4. **bias_h1/market_state/directional-factors = N2 canonic?** `bias_h1` = **DA** (producătorul N2). `market_state` = primitivă partajată (atr14/expansion), NU N2. „directional factors" = OUTPUT-ul N2 (`BiasState.factors`).
5. **De ce N3Request/N4Request cer n2_fingerprint?** N3 ratificat gate-uiește pe `bias_available` (cascada N1→N2→N3); ve_tower a adăugat `n2_fingerprint` ca identitate de intrare în node_input_fingerprint — **ca hook pentru identitatea ieșirii N2 reale**, dar azi e doar un string al apelantului.
6. **Nod separat sau urmă contractuală fără producător?** N2 **ESTE un nod real separat** (H1, distinct de N1 H4 și N3 M15). În ve_tower 0.3.0, `n2_fingerprint` e o **urmă contractuală fără producător împachetat** — exact golul.

**Separare obligatorie:** factorii deterministici N2 ≠ `probability_inputs` pentru EV. N2 NU e sursă de probabilitate (`emits_probability=False`). `probability_inputs` vin din tabele de rezultate istorice, consumate de motorul EV din ve_brain — o cale COMPLET separată.

## VERDICT: **B — N2_EXISTS_BUT_IS_NOT_PACKAGED**

Implementarea ratificată EXISTĂ (`bias_h1.py @ 850815f`) și e deja vendată byte-identic în ve_tower 0.3.0 (PASS), dar
NU e expusă ca producător VERSIONAT: lipsesc `N2_CONTRACT_VERSION`, schema runtime N2, `run_n2`, `N2Response`
versionat, reason codes N2, fixture oficial N2. `n2_fingerprint`-ul din N3/N4 e o urmă fără producător.

**Plan (fără rescriere semantică):** livrez un producător N2 versionat ca **versiune NOUĂ a ve_tower (0.4.0)** care
EXPUNE `run_n2` peste `bias_h1` DEJA VENDAT (byte-identic, aceeași proveniență `850815f`) — fără re-vendorizare, fără
atingerea modulelor ratificate. Contract `tower-n2-request-v1` + `N2Response` cu `data_identity` + `node_input_fingerprint`
+ `output_fingerprint` + reason codes + `N2_UNAVAILABLE` fail-closed. Interzis: default LONG / wildcard / placeholder /
fingerprint dintr-un string al apelantului. Plus: contract N3/N4 **v3** care leagă `n2_fingerprint` de răspunsul N2
REAL (nu bias_direction, nu axes.direction). ve_tower 0.3.0 NU se suprascrie; 0.4.0 = handoff nou + Red Team nou.
ve_brain 0.1.3 / N1 / Router / EV / N6 — neatinse.

**Notă de onestitate pe ratificare:** git-ul confirmă EXISTENȚA + spec-ul ratificat + includerea într-un artefact
PASS-uit (ve_tower 0.3.0). NU există în git un handoff N2 Red Team standalone (RT-CODE-A-0011 neconfirmat). De aceea
verdictul B se închide cu un **N2_HANDOFF nou** pe care Red Team îl emite (PASS/FAIL) după împachetare.
