# ve_n1_replay — CHANGELOG

## 0.1.0 — artefact N1 replay standalone (READY_FOR_N1_HANDOFF_REVALIDATION)

Împachetează handoff-ul N1 replay al AI Trader (`21ae632`) ca artefact INDEPENDENT, instalabil de Alpha într-un venv
separat, fără repo-ul ai_trader și fără coliziune cu ve_tower.

- **Closure git-only** (vezi `N1_REPLAY_CLOSURE.md`): 14 module `ai_trader.*` runtime @`21ae632` + 5 detectori @
  submodul `61cbd58c` (`market_structure` blob `52bb1eba…` — DIFERIT de ve_tower, NU reutilizat) + `ve_brain` 0.1.3
  (wheel extern pinuit) + numpy. Coada incompletă a AI Trader REZOLVATĂ: `market_scanner.exceptions`,
  `imbalance_mechanics`, `order_flow`, `order_block_void`.
- **Byte-identitate** verificată SEPARAT pentru modulele AI Trader (@21ae632) și detectori (@61cbd58c) — git-blob SHA1
  în `version.py`, verificabile independent (`git rev-parse <commit>:<path>`). Modulele vendate NU sunt rescrise.
- **Bootstrap izolat + tranzacțional** (`_bootstrap.py`): încarcă modulele vendate sub numele lor reale
  (`ai_trader.*`, `market_structure`, …) în ordine topologică; coliziune cu un modul STRĂIN (ex. detector ve_tower
  preîncărcat) ⇒ `N1ReplayLoadCollisionError` fail-closed cu rollback complet (zero reziduuri, excepția originală,
  retry curat, sigur la concurență) — NICIODATĂ substituție silențioasă. NU atinge module host preexistente.
- **Suprafață publică păstrată**: `N1ReplayEngine` (initialize prin constructor · `observe_closed_bar` · `replay` ·
  `snapshot` · `restore` · `reset`) + `Bar`, tipurile, erorile, `EvaluationIdentity`. Ieșire: RawAxes ·
  applicable_regimes · router verdict (eligibility_decisions) · reason_codes · availability_status · input_data_identity
  · output_fingerprint · router_output_fingerprint · regime_axes_status · last_closed_bar · router_version ·
  detector_configuration_fingerprint · evaluation_identity.
- **INTERZIS, absent prin construcție**: MT5/broker/ve_tower/ai_trader la runtime-ul consumatorului · set_authority ·
  order_send · probability_inputs · fallback legacy · clasificator alternativ.
- **Paritate DECISIVĂ**: sursă @21ae632 (import direct al modulelor vendate) vs wheel instalat ⇒ IDENTICE
  (output_fingerprint, applicable_regimes, availability, router_output_fingerprint) pe TREND_UP (→{TREND_UP}/FULL),
  UNCERTAIN (→{UNCERTAIN}/PARTIAL), BOS_BULL. Testul MT5 al celor 12 bare reale journaled cere terminal MT5 + jurnalul
  LIVE_SHADOW (NEATINS) — de aceea paritatea folosește fixture-urile oficiale (VE decision (b): constantele de bare
  copiate ca DATE, nu algoritm).
- 18 teste (byte-integritate ai+detectori, izolare/coliziune fail-closed, suprafață+refuzuri, snapshot/restore,
  determinism, acoperire de regim, zero importuri interzise), din wheel instalat, cu repo-ul ai_trader ABSENT.
  mypy --strict clean pe modulele proprii. ve_brain/N1/Router/EV neatinse; LIVE_SHADOW neatins.

Rollback: `pip install ve_n1_replay==<prev>` (nicio versiune anterioară — 0.1.0 e prima). Upgrade viitor: versiune nouă,
NU suprascriere. `N1_HANDOFF_PASS` NU e auto-declarat — verdictul e al Red Team.
