# RED TEAM — F441 DUAL-DETECTOR PREDICTIONS FREEZE PROOF
### RT-RANGE-V4_4_1-FRESH-BLIND14-VALIDATION-001 · `F441_V44_PREDICTIONS_FROZEN` + `F441_V441_PREDICTIONS_FROZEN`

Committed after Env A inference (both frozen detectors on the 14 F441 windows) and **before any label
access**. Prediction payloads encode per-bar structure and are NOT committed; only hashes + a sanitized
manifest are published here. Both payloads are stored read-only in the Red Team escrow. Env B (scoring) is
created only after this commit is pushed and `local=remote` confirmed.

```
batch                    = F441-001 … F441-014   (14 windows, 3840 canonical bars, 5×96 + 5×288 + 4×480)
V4.4 detector            = 3bb61cf (range_semantic_v4_4 / range_engine_v4_4) · config_id 23d98c07 · contract range-hierarchical-v4.4
V4.4.1 detector          = 4ed4eb4 (range_semantic_v4_4_1 / range_engine_v4_4_1) · config_id d7b6c067… · contract range-hierarchical-v4.4.1 · params 29/4/3/12
V44_predictions_sha256   = 2830a712f2aade04e829629f9eaacc504256f321d1e291802572a0b98004f5ac
V441_predictions_sha256  = f96054f1fdaca181e191467ef006e29c40fe0d472f7cdd7e0cbdcde8a4c1fac0
window_payload_sha256    = f66a87526fc752b31f98a1ae7dacccc5ffda000334c91d343f6a5172674d5164  (labels_present=False, verified)
selection_manifest_sha256= c8aa83baa3e283b4ff6ff774848b44dd94306101e0339089f71a30fcaa2bb7bc
bars_sha256 reproduced   = 14/14 from canonical M15_v2 delivered df (197094 rows, file sha256 57f4ed95…)
confirmed MACRO structs  = V4.4: 22 · V4.4.1: 37   (pre-scoring counts, NO labels involved)
V4.4.1 T-STALE firings   = 32   (diagnostic, pre-scoring)
```

**Provable chronology (§10):**
```
F441 windows frozen (6a62243)  →  CEO labels frozen (0f6f1a9 / 2ad5cab, detector_state V4_4_EXECUTED=False,
  V4_4_1_EXECUTED=False, PREDICTIONS_EXIST=False)  →  Env A created WITHOUT label access  →  V4.4 executed
  →  V4.4.1 executed on byte-identical bars  →  BOTH predictions frozen (this commit)  →  ONLY THEN labels
  accessed by Env B
```

Env A read only the canonical corpus + the F441 window payload's canonical indices (`labels_present=False`,
verified; payload carries no MACRO/RANGE/CHANNEL/level fields). No CEO label, labels payload
(`payload-8838b8c521b5d26d.bin`), decryption key path to labels, or scorer was imported (isolation asserted in
the inference process). Both detectors ran on identical input; V4.4.1 emits more confirmed structures (37 vs 22)
and fired T-STALE 32 times — **measured, not yet scored**. Whether those extra confirmations are genuine RANGE
recoveries or false positives is decided only by Env B against the frozen labels, under the pre-registered
false-RANGE-averse H1/H2 hard gates.

`F441_V44_PREDICTIONS_FROZEN` · `F441_V441_PREDICTIONS_FROZEN` — labels are opened only after this commit is pushed and verified.
