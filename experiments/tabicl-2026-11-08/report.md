# TabICLv2 admission result — November 8

Status: RESOURCE ADMISSION FAILED. No possession quality scores, promotion test or standalone/blend comparison executed. Current nine-core unaugmented CatBoost+penalty16 retained. This result says nothing about achievable TabICL spellF1 with a different resource budget.

Protocols committed b0b2e70 and2309457 before probes. Public weight revision4dcd344ece2c00be9e831fdd35bed57b5ad83e19, SHA256bdc7dbd5e4ff21f8f0456fcf90c6b7cdf72dbea960f2d05b19bec19f9b3d4ed0,110368038bytes; BSD3model card. Local-only download and CPU execution; no target/sealed/PFFholdout assets or labels read. No hosted inference. Isolated data/tabicl-deps over research GRUenvironment, production dependencies unchanged.

Independent scientist review corrected original full-frame context wording to exact parent stride5 thenXfilter BEFORE probes. H/A/D probability columns explicitly remapped. Initial synthetic1000 failed strict decoder sum tolerance due to float32 probabilities; preserved failure log/JSON. Commitf5a28f9 corrected float64 row normalization before rerun, without model hyperparameter rescue or observed quality scores. Missing einops/sklearn imports during isolated setup were resolved by installing dependencies locally; dependency versions recorded in successful probe JSON. No production environment change.

| Probe | Context rows | Query rows | Wall seconds | Observed peak GiB | Result |
|---|---:|---:|---:|---:|---|
| 1000 | 1000 | 64 | 3.385 | 0.752 | PASS |
| 10000 | 10000 | 64 | 26.490 | 2.148 | PASS |
| actual | 113507 | 64 | 15.787 | 6.377 | 6 GiB resident-memory cap |

Both synthetic probes repeated independent fits/predictions with exact probability equality and identical decoder CSV bytes. These establish only tested numerical behavior, not football accuracy. Actual matched context exceeded6GiB sampled RSS and was terminated(SIGTERM,-15) after15.787s. The0.25s polling monitor allows overshoot; this is observed peak, not an OS-enforced memory ceiling. It did not finish even one actual-context admission. No scored supplement committed and neither B nor C ran, per preregistered stop. No smaller-context rescue, offload/cache change, blendweight search or metric-based decision.

29 production tests pass. Existing production CSV SHA256 remainsab253e43f46fc9a7885b689498a220595e78d67ad2a6099a07316e081ca3f815. Existing clean/fresh-clone evidence remains applicable because production source/config did not change; no new target inference/reproduction claimed. Target accuracy unknown. Repeated use of five development matches remains a selection risk; this admission adds no accuracy evidence.

The new bounded track stops after its resource failure; no metric-failure count was fabricated. Previous tracks remain closed. A higher-memory/offload or smaller-context candidate would require a new protocol and must disclose changed resource/context assumptions; not executed. November13 freeze and14–16delivery unchanged. No submission. Evidence: admission.json, context-provenance.json, weight-source.json, 1000/10000.json, failure logs and docs/tabicl-protocol-review-2026-11-08.md.
