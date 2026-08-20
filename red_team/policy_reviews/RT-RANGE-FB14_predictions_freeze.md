# RED TEAM — FB14 DUAL-DETECTOR PREDICTIONS FREEZE PROOF
### RT-RANGE-V4_4-FRESH-BLIND14-VALIDATION-001 · `FB14_V43_PREDICTIONS_FROZEN` + `FB14_V44_PREDICTIONS_FROZEN`

Committed after Env A inference (both frozen detectors on the 14 FB14 windows) and **before any label
access**. Prediction payloads are not committed (they encode per-bar structure); only hashes + a sanitized
manifest are published. Both payloads are stored read-only in the Red Team escrow. Env B (scoring) is created
only after this commit is pushed and `local=remote` confirmed.

```
batch                    = FB14-001 … FB14-014   (14 windows, 3840 bars, 5×96 + 5×288 + 4×480)
V4.3 detector            = bc6b9dc (range_semantic_v4_3 098fa144) · config_id 24f72a60
V4.4 detector            = 3bb61cf (range_semantic_v4_4 833aedfd) · config_id 23d98c07 · contract range-hierarchical-v4.4
V43_predictions_sha256   = a9bf1ef28929cd7eac426ef6a33c032495e0a5bf3118a5c05a5064fe2ef88bcd
V44_predictions_sha256   = 2c247f0c786127b23fc1841a69d640dbcafd9c48266afef0c6a066551fd42593
confirmed MACRO structs  = V4.3: 34 · V4.4: 22   (pre-scoring counts, no labels involved)
f1 sub-tick bars         = 2   (tolerated via the ratified engine path; OHLC unmodified, no clip/repair)
```

**Provable chronology (§11):**
```
FB14 windows frozen (20bf599)  →  labels frozen elsewhere (c6d9e02/a520039, detector_state_at_freeze all False)
  →  Env A created WITHOUT label access  →  V4.3 executed  →  V4.4 executed on identical bars
  →  BOTH predictions frozen (this commit)  →  ONLY THEN labels accessed by Env B
```

Env A read only the corpus + the FB14 window payload's canonical indices (input contains no
MACRO/RANGE/CHANNEL/level fields — verified). No CEO label, labels payload, key, or scorer was present. Both
detectors ran on byte-identical input; V4.4 emits fewer confirmed structures (22 vs 34), consistent with the
directional-discrimination gate — measured, not yet scored.

`FB14_V43_PREDICTIONS_FROZEN` · `FB14_V44_PREDICTIONS_FROZEN` — labels are opened only after this commit is pushed and verified.
