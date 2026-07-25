# Discovery Candidate Handoff Log

Append-only. One line per freeze / new-version / addendum event. Never edited or reordered
retroactively -- corrections are new lines, not edits to existing ones. This is the sole audit
trail proving what Alpha handed to Red Team, and when.

**Ultima reconciliere administrativa**: 2026-07-23 (CEO-directed HANDOFF_LOG reconciliation --
backfilled missing FROZEN entries for DC-0008..DC-0012 and all 16 addendum SUBMITTED entries;
no scientific content, verdicts, confidence, observations, or addenda text were modified). CEO
reconciliation report ACCEPTED 2026-07-23.

**Open item**: DC-0001's recorded content hash cannot be reproduced by independent recomputation
of the current on-disk file (three recorded locations agree with each other, but not with a fresh
hash). Not corrected -- see `DC-0001_HASH_REPRODUCIBILITY_INVESTIGATION.md` (status: INVESTIGATION
COMPLETE 2026-07-25; hash disposition still awaits CEO/Red Team decision -- DC-0001's
hash/content/Handoff Statement remain unmodified).

**Alpha 1 official closure (2026-07-25)**: administrative closure per CEO directive -- see
`research_log/SESSION_STATE.md` top banner. No new Discovery Candidates or addenda produced as
part of closure. Three closure follow-up items also completed 2026-07-25 (no frozen text
modified in any case):
- DC-0001 hash investigation closed (above).
- `research_log/DATA_QUALITY_OPEN_ITEM_2025-09-17_1800UTC.md` closed administratively (substantive
  question unresolved, handed off).
- DC-0001 vs OBS-0014 contradiction reconciled at the definitional level -- see
  `research_log/DC0001_OBS0014_RECONCILIATION_NOTE.md` (scientific verdict remains open, owned by
  Red Team / Statistician).
- Red Team finding **F2** (DC-0022's 86.75pt "family record" claim, wrong against the family's
  current record, DC-0024 Addendum D's 514.165pt -- DC-0013 Addendum H's 180.53pt was itself only
  an intermediate value, since superseded) corrected via
  `DC-0022_ny_afternoon_record_duration_magnitude_sustained_expansion/CORRECTION_NOTE_2026-07-25.md`
  (revised 2026-07-25 to cite the correct current record after an earlier revision of this same
  note cited only the stale 180.53pt figure).
- Red Team finding **F4** (DC-0013 still reads "One instance" despite ~12 documented instances)
  corrected via
  `DC-0013_ny_session_large_sustained_expansion_no_reversal/CORRECTION_NOTE_2026-07-25.md`.

| Date | Candidate ID | Version | Event | Content Hash | Title |
|---|---|---|---|---|---|
| 2026-07-21 | DC-0001 | v1 | FROZEN / SUBMITTED | sha256:1f1b3d399f2e9613b18d1d4ecaede8d7e3b0dec085ab709482b4d2c3f40cf75c | Isolated Single-Bar Velocity Outlier Followed by Gradual Multi-Bar Continuation |
| 2026-07-22 | DC-0002 | v1 | FROZEN / SUBMITTED | sha256:8dcf79e3f4b77e7f78d934b9c8d51b4a3bc960052b34466f19c25147f3afcdad | Higher-Timeframe Compression Resolves Into Expansion In The Direction Of The Prevailing H4 Bias |
| 2026-07-22 | DC-0003 | v1 | FROZEN / SUBMITTED | sha256:d88cf4bc746d2669a7d8f806f9a2a085375ad6a12e798a9f5a4259e3cbab8720 | Scale Inversion — Micro-Scale Coils And Higher-Timeframe Compressions Resolve In Opposite Ways |
| 2026-07-22 | DC-0004 | v1 | FROZEN / SUBMITTED | sha256:c42c8d7c646a86c2f242e25267df02a86fb2c01f88236e1a1fbacc4dd86141bb | New-York-Session Prior-Day-High Sweep-Reject Is Followed By Reversion |
| 2026-07-22 | DC-0002 | v1 | ADDENDUM (Library Concept Scan added; hash recomputed) | sha256:9970263b17fdbcb886955bda7bb51b2ebc60a53de824b71b62868f6315c73bab | see index |
| 2026-07-22 | DC-0003 | v1 | ADDENDUM (Library Concept Scan added; hash recomputed) | sha256:e56076c5c4fce6a296f77e996fe050f03ae6b27fc3b929819e8824033195ac7d | see index |
| 2026-07-22 | DC-0004 | v1 | ADDENDUM (Library Concept Scan added; hash recomputed) | sha256:4560ba15e08226a9614097e1bd500db5a53d5095aa11ed02296876c64d665038 | see index |
| 2026-07-22 | DC-0005 | v1 | FROZEN / SUBMITTED | sha256:7c8750551b31c2e8da4833a40f9a31a12c58a5000c3fed782838f4a23dc01714 | The Third Test Of A Level Behaves Differently From The First Two |
| 2026-07-22 | DC-0006 | v1 | FROZEN / SUBMITTED | sha256:ef1e217fd3ff1aeb0fd8fa96f6e110f5cc4bcdbffb7a2c49474190f2af6585a4 | Candles With Extreme Relative Volume Frequently Fail To Extend |
| 2026-07-22 | DC-0007 | v1 | FROZEN / SUBMITTED | sha256:1823d33ec7394c21d0494d72d47ae0d9310ca0c306b028490152c353282fff10 | A Cluster Of Near-Equal Lows Is Taken And Reclaimed Within A Single Candle |
| 2026-07-22 | DC-0008 | v1 | FROZEN / SUBMITTED (backfilled 2026-07-23) | sha256:ce52a96e39fcd44da03f9549c2ddfd6da63eadefd7edd24b01c205b31594e130 | A Large M15 Candle Built From Sustained Multi-Minute Volume, Not Single-Minute Concentration |
| 2026-07-22 | DC-0009 | v1 | FROZEN / SUBMITTED (backfilled 2026-07-23) | sha256:ac7ffdec7dcd15472caafc6e93196381a9427446e7ea4773778746c560354c15 | A Narrow Resistance Band Survives Seven Touches Across Three Calendar Days, Including A Weekend Gap |
| 2026-07-22 | DC-0010 | v1 | FROZEN / SUBMITTED (backfilled 2026-07-23) | sha256:5855f9606e7070f86bab1f98b3a8599b5a2a7a684916ab157418e9b2a52b538c | A Consistently Quiet Hour Breaks With A Sustained Volume Expansion On One Session |
| 2026-07-22 | DC-0011 | v1 | FROZEN / SUBMITTED (backfilled 2026-07-23) | sha256:dc0607e02329bfa6818e5f91a049949199a8c32420b13572bfdba0a29207ea33 | A Single-Minute Sweep Is Reclaimed And The Move Extends To New Highs, Not Just Back To Pre-Sweep Levels |
| 2026-07-22 | DC-0012 | v1 | FROZEN / SUBMITTED (backfilled 2026-07-23) | sha256:4a4791c183230291c9af6f1665d78f76886da8a06131385d2a5301bba3b24081 | Sustained High Volume With No Net Displacement (Two-Sided Absorption) |
| 2026-07-22 | DC-0008 | v1 | ADDENDUM A / SUBMITTED (backfilled 2026-07-23) | sha256:07acae0e39d7d33f405503960e71c3e363addeda3373a61995fa0251cef7ced3 | `addendum_2026-07-22_a.md` |
| 2026-07-22 | DC-0008 | v1 | ADDENDUM B / SUBMITTED (backfilled 2026-07-23) | sha256:3eb64bcfdd312a645899c373f66b2e40c2c1b4e6c55f58720242d3ac68419cad | `addendum_2026-07-22_b.md` |
| 2026-07-22 | DC-0008 | v1 | ADDENDUM C / SUBMITTED (backfilled 2026-07-23) | sha256:e28514cb4b18559444c4e87e667b26cd57234a87df23ae0a1d93bcc9b88baa3e | `addendum_2026-07-22_c.md` |
| 2026-07-22 | DC-0008 | v1 | ADDENDUM D / SUBMITTED (backfilled 2026-07-23) | sha256:5c44a91b9bc4e467829f038c42dc2e8a8081e6a4bbe138ce7158304f18f0ef89 | `addendum_2026-07-22_d.md` |
| 2026-07-22 | DC-0009 | v1 | ADDENDUM A / SUBMITTED (backfilled 2026-07-23) | sha256:48a89c0e1f1a9621a4c69d1f8141764c77bed66ea9f52d66fbfd5f63350a9af7 | `addendum_2026-07-22_a.md` |
| 2026-07-22 | DC-0009 | v1 | ADDENDUM B / SUBMITTED (backfilled 2026-07-23) | sha256:d771b284a5628a021d897e506c2420607b0fb4572b2c60b12b186403d5d0e525 | `addendum_2026-07-22_b.md` |
| 2026-07-22 | DC-0009 | v1 | ADDENDUM C / SUBMITTED (backfilled 2026-07-23) | sha256:d8b6c32527d90a7969580872b457f83f34729c363103363555fbd27b70424ddc | `addendum_2026-07-22_c.md` |
| 2026-07-22 | DC-0009 | v1 | ADDENDUM D / SUBMITTED (backfilled 2026-07-23) | sha256:fb7256da9eb12e8e071a0dd4e3aad4eaaf948f4f91faba5165e6f579533281aa | `addendum_2026-07-22_d.md` |
| 2026-07-22 | DC-0010 | v1 | ADDENDUM A / SUBMITTED (backfilled 2026-07-23) | sha256:a6bb365efad2f9bdc7746a86c2ff469ee6765a308b4669866e0b62fb74ec7bdb | `addendum_2026-07-22_a.md` |
| 2026-07-22 | DC-0011 | v1 | ADDENDUM A / SUBMITTED (backfilled 2026-07-23) | sha256:b9a21bb72a935967533b248003df8fca472a57c11c24b11a619d264a1418ef55 | `addendum_2026-07-22_a.md` |
| 2026-07-22 | DC-0011 | v1 | ADDENDUM B / SUBMITTED (backfilled 2026-07-23) | sha256:8418e3fa38dba5dd21d69c0f587eb104b62baf033222ffc3b8fd65a9358f3515 | `addendum_2026-07-22_b.md` |
| 2026-07-22 | DC-0012 | v1 | ADDENDUM A / SUBMITTED (backfilled 2026-07-23) | sha256:e4aadfebec531f47271430794285bf78d8241ad31f452d512e3ed1c05a8f5124 | `addendum_2026-07-22_a.md` |
| 2026-07-23 | DC-0013 | v1 | FROZEN / SUBMITTED | sha256:fc8991fbf2f994e7d4ea112fac913610a31c95eacbbb37ec6dcbcff4c36c3b9a | A Large NY-Session Directional Expansion Built From Sustained Multi-Minute Volume, Extending Across Four Consecutive M15 Candles With No Reversal |
| 2026-07-23 | DC-0014 | v1 | FROZEN / SUBMITTED | sha256:3cdc39b74e1db801b2ead9ff0c2b63d93a92347d58ab49570bcc7f2fb7b056df | A V-Shaped Reversal at the 00:00-01:00 UTC Hour Builds Into a Sustained Four-Candle Rally, Then Reverses |
| 2026-07-23 | DC-0015 | v1 | FROZEN / SUBMITTED | sha256:f6526ab36f30391622309f27519583a735abd9f60589e52362e3d6797af15d8e | A Sustained NY-Session Directional Expansion Persists Across Eleven Consecutive M15 Candles (~2h45m), the Longest Single-Direction Run Observed in This Replay |
| 2026-07-23 | DC-0016 | v1 | FROZEN / SUBMITTED | sha256:e1c1c4dce4455e9046e786358546bac2359b50b8217bc364357faad8e9660ff2 | A Sustained Early-Asia/Pre-London Directional Expansion Reaches the Largest Point Move of This Family, Then Reverses at a Marginal New High |
| 2026-07-23 | DC-0017 | v1 | FROZEN / SUBMITTED | sha256:dbd07f90a927b2a9b9c5fb81a924803c3ab74437fa3242294b9f386d4213c712 | An NFP-Scale 12:30 UTC Impulse, Built From Sustained Multi-Minute Volume, Holds Its Gains Across Four Subsequent High-Volume Candles Without Reversing or Extending Dramatically Further |
| 2026-07-23 | DC-0018 | v1 | FROZEN / SUBMITTED | sha256:40ce847f27f85220eb26b9ee569b3869fb440b2282d4b07006a4764a1cf4786f | An Extreme-Volume Spike to a Fresh Multi-Session High Fails Completely Within the Same Candle, Then Extends Into a Sustained Multi-Candle Decline |
| 2026-07-23 | DC-0013 | v1 | ADDENDUM A / SUBMITTED (backfilled 2026-07-23) | sha256:c82b3a1bd0f292f7797b18ba870d379689f48ebc0d8451118bf1ded6ff124949 | `addendum_2026-07-23_a.md` |
| 2026-07-23 | DC-0016 | v1 | ADDENDUM A / SUBMITTED (backfilled 2026-07-23) | sha256:9f76941ca0755e69a25ca81b0ccc25cc7c4d3e9b259c87708d20a2c83d00eec8 | `addendum_2026-07-23_a.md` |
| 2026-07-23 | DC-0017 | v1 | ADDENDUM A / SUBMITTED (backfilled 2026-07-23) | sha256:783962cb1b12047bbfe54535f8ff5e55bf3b312e836a66a7b53f0fae21e3eb1b | `addendum_2026-07-23_a.md` |
| 2026-07-23 | DC-0017 | v1 | ADDENDUM B / SUBMITTED (backfilled 2026-07-23) | sha256:3118f8126f70a05d776e4cf1a397f5a7d740bd949dfcfbeeb135bb2853b54a3a | `addendum_2026-07-23_b.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM B / SUBMITTED | sha256:58e8d86a67629a64400b5c042e5f168a62380f0c994d9c020946c2944949ea38 | `addendum_2026-07-24_b.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM C / SUBMITTED | sha256:67aee77367c425d3bf2dcfdce7aa63ad770b0e2938688a99dddb866a5cebaf82 | `addendum_2026-07-24_c.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM D / SUBMITTED | sha256:195bb307667b5784c848ebb51a68c6382c384df5af3cadd15314a2ad8f695cf3 | `addendum_2026-07-24_d.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM E / SUBMITTED | sha256:861b821a0158fcccc50427638eb12f998d90475858e563e9f33f9687d8435ee1 | `addendum_2026-07-24_e.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM F / SUBMITTED | sha256:5877794fb23741a2993c7b977b20a8a79ffd65069a3a5e46e82561a0dea85326 | `addendum_2026-07-24_f.md` |
| 2026-07-24 | DC-0017 | v1 | ADDENDUM C / SUBMITTED | sha256:5581069f1d03ac5cf4e6c519cf572fa9b6ec45aaae4c6131268a188f1e437562 | `addendum_2026-07-24_c.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM G / SUBMITTED | sha256:9f5fb9ade9c470a7ece593711b3762e3aa0cdd5362958ac718905dcd0e98516f | `addendum_2026-07-24_g.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM H / SUBMITTED | sha256:071dfe174f328153421b7bd6556b341e8e6976fcecf545cc991e0e934b25668d | `addendum_2026-07-24_h.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM I / SUBMITTED | sha256:2adcacb212037cac9bcc0a20fe6d293ceb7df02a8c01d80d85d3e7f34f533fb9 | `addendum_2026-07-24_i.md` |
| 2026-07-24 | DC-0017 | v1 | ADDENDUM D / SUBMITTED | sha256:d7b3f00d12e5e96f7d3b2e48523c2b91c4c3c8d13204ab1062c8efd7d246dcef | `addendum_2026-07-24_d.md` |
| 2026-07-24 | DC-0019 | v1 | FROZEN / SUBMITTED | sha256:4130deed316f517237f3473b5bbb1730df0c2c5e560e0ec25083a705814391d8 | A Weekend Gap Nearly Double the Prior Record Fails to Retrace, Extending Into a Sustained Sunday-Reopen Decline Before a Partial Recovery |
| 2026-07-24 | DC-0019 | v1 | ADDENDUM A / SUBMITTED | sha256:34c39002f7d25ff03c8e5c6d384714282438341a7e70426caf05f8cdc8783afb | `addendum_2026-07-24_a.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM J / SUBMITTED | sha256:4dc2ba87e4850e89ef8a084d9ee9c3591518a43e9a3171e0c1328faf6e373b4a | `addendum_2026-07-24_j.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM K / SUBMITTED | sha256:ea0f3bf15693dc9ef4943ea4f598246ec85d8e0ee7d45bee4eaabd071be3443c | `addendum_2026-07-24_k.md` |
| 2026-07-24 | DC-0020 | v1 | FROZEN / SUBMITTED | sha256:211c6dad5b369dd4377055adc1971b657f2cb5dce0e0587150e9956c18537ec0 | An 18:00 UTC Low Sweep Followed By a Failed Fresh-High Reclaim Sets a New All-Time Volume Record and Extends Into a Multi-Leg, Bidirectional Decline |
| 2026-07-24 | DC-0021 | v1 | FROZEN / SUBMITTED | sha256:2988116288277a049c65127c0e97c780801e6566fb384beb7adf5f7f2c15a9f8 | A Sustained NY-Morning Decline Transitions Directly Into a Multi-Candle Absorption Phase at Persistently Elevated Volume, With No Volume Decay Between Phases |
| 2026-07-24 | DC-0021 | v1 | ADDENDUM A / SUBMITTED | sha256:3c4ebd17a2c6faa81a400010d4ba32dd746e150fac8894b55449b92ebcd313fa | `addendum_2026-07-24_a.md` |
| 2026-07-24 | DC-0022 | v1 | FROZEN / SUBMITTED | sha256:eedbe3c0840aefad24b60bfa0b13ca5023e8c8eda9887b1680ef495e30c5a318 | An NY-Afternoon Sustained Directional Expansion Sets New Duration and Magnitude Records for the Family, Nearly Doubling the Prior Longest Run Before Reversing |
| 2026-07-24 | DC-0023 | v1 | FROZEN / SUBMITTED | sha256:5113f459c27ae3ce39110515e923db31a7db2fc8f146116fa7283ed1993e288e | An 8-Hour Multi-Leg, Choppy Episode at Persistently Extreme Volume, Containing a Single Candle Among the Largest-Volume Candles in the Replay |
| 2026-07-24 | DC-0024 | v1 | FROZEN / SUBMITTED | sha256:813c1d0edb21b54885374fa4e5b34f8309817ddee01f1bf1e84924b863757dad | A London-Morning Sustained Decline Sets a New All-Time Magnitude Record (125.7 Points), Then Partially Recovers |
| 2026-07-24 | DC-0010 | v1 | ADDENDUM B / SUBMITTED | sha256:132b611557121681d780513d5ae7916a69207937c57f2b4134bd1e5863861476 | `addendum_2026-07-24_b.md` |
| 2026-07-24 | DC-0011 | v1 | ADDENDUM C / SUBMITTED | sha256:da9173d62056cd8d5bd3858168b4c3e3ed565dfc56907bbb8b4eeda20c2f7e35 | `addendum_2026-07-24_c.md` |
| 2026-07-24 | DC-0023 | v1 | ADDENDUM A / SUBMITTED | sha256:d9fa5d35aabd31754a99b624d19759e546db03ec14cfb0044e0298f17b93dbee | `addendum_2026-07-24_a.md` |
| 2026-07-24 | DC-0013 | v1 | ADDENDUM L / SUBMITTED | sha256:bc10a30f15cf33f0324bd526d15d213cd6f420232998261506c980598a8fff80 | `addendum_2026-07-24_l.md` |
| 2026-07-24 | DC-0019 | v1 | ADDENDUM B / SUBMITTED | sha256:2f3c1517a2a50751e4499af7d4fa5cae4121d7e180f6718774c99ee6f8cfe93f | `addendum_2026-07-24_b.md` |
| 2026-07-25 | DC-0025 | v1 | FROZEN / SUBMITTED | sha256:b0929b2063ac55b659418067b8d6b5f3dba0c576a8b8dd68e767bb8d60be4539 | A Two-Candle Escalating-Volume Waterfall Decline Sets a New All-Time Volume Record, Then Retraces ~75% Before Consolidating |
| 2026-07-25 | DC-0019 | v1 | ADDENDUM C / SUBMITTED | sha256:fc5cd113d280ed8d5e63d73e1fa719c74126a951135dacf8f512febb226aac7f | `addendum_2026-07-25_c.md` |
| 2026-07-25 | DC-0025 | v1 | ADDENDUM A / SUBMITTED | sha256:8c9965f62fe7be1eb98223a62430b7d166030e0fcfa64830ffcb1b78b3b1df74 | `addendum_2026-07-25_a.md` |
| 2026-07-25 | DC-0013 | v1 | ADDENDUM M / SUBMITTED | sha256:3094b1fee5cdf01d5c2f90ec9d00b77261a3ae3a3568ece0e97f950eaa53e1e3 | `addendum_2026-07-25_m.md` |
| 2026-07-25 | DC-0024 | v1 | ADDENDUM A / SUBMITTED | sha256:4d81a14aa1651c975c2cb307b63cc30c0d1f8e43246bdcd98d97420a5d78db50 | `addendum_2026-07-25_a.md` |
| 2026-07-25 | DC-0025 | v1 | ADDENDUM B / SUBMITTED | sha256:f05af824ff747d2d66bbab3d7119dc23813aa396e4aa11ff63a3e33baf38b1ef | `addendum_2026-07-25_b.md` |
| 2026-07-25 | DC-0026 | v1 | FROZEN / SUBMITTED | sha256:c4155ef5caf0a154543e77cd0929fca90a3db64d6170caccaf7dacae84fa97e6 | A Thin-Liquidity Daily-Rollover Reopen Produces a ~100-Point Parabolic Spike That Fully Reverses Within Minutes |
| 2026-07-25 | DC-0023 | v1 | ADDENDUM B / SUBMITTED | sha256:acf342afe8c01241d05504ec093a2008a140f0a3d3113291f06195f378da325c | `addendum_2026-07-25_b.md` |
| 2026-07-25 | DC-0024 | v1 | ADDENDUM B / SUBMITTED | sha256:8e301ec1a62aab14ade7cce7395a3af44685ee628a3d236c17f96dfe3d2f3352 | `addendum_2026-07-25_b.md` |
| 2026-07-25 | DC-0023 | v1 | ADDENDUM C / SUBMITTED | sha256:089bf2048868c4b43e676353ca2352318d358ac02eff9bea30a34f60519f12bd | `addendum_2026-07-25_c.md` |
| 2026-07-25 | DC-0024 | v1 | ADDENDUM C / SUBMITTED | sha256:a5c986f63355a0553046c80255ebb269f7dee7473f2b2e7480b01d748a114250 | `addendum_2026-07-25_c.md` |
| 2026-07-25 | DC-0019 | v1 | ADDENDUM D / SUBMITTED | sha256:f568038cc9cc9d89fd420459355dba41932ad740e7fa2cdd71fa186ab8532e14 | `addendum_2026-07-25_d.md` |
| 2026-07-25 | DC-0024 | v1 | ADDENDUM D / SUBMITTED | sha256:7e1e5903eb306161fe1f444cd18a885449c8311a9e6b370ed8e90aecdb8ad80e | `addendum_2026-07-25_d.md` |
| 2026-07-25 | DC-0019 | v1 | ADDENDUM E / SUBMITTED | sha256:99ca3398550b3a5df729a57eb70a98d62b2182ffb8d8b164653ce7dd3b644bf0 | `addendum_2026-07-25_e.md` |
| 2026-07-25 | DC-0022 | v1 (unmodified) | CORRECTION_NOTE_FILED (F2, bookkeeping only) | N/A -- administrative, not a scientific addendum | `CORRECTION_NOTE_2026-07-25.md` |
| 2026-07-25 | DC-0013 | v1 (unmodified) | CORRECTION_NOTE_FILED (F4, bookkeeping only) | N/A -- administrative, not a scientific addendum | `CORRECTION_NOTE_2026-07-25.md` |
