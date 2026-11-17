# Frozen diagnostic and final ensemble export: static review

Reviewed November 14, 2026. This filename follows the November 13 preparation identifiers. Review used source and saved aggregate metadata only. **All supplied tests, project imports, inference, scoring, checkpoint loading and CSV validation remain USER RUN and UNEXECUTED by the reviewer.** No competition rows, arrays, model tensors or sealed assets were read.

## Boundary reviewed

- `scripts/diagnose_tcn_possessions.py`, its diagnostic definitions, registration/storage contract and two synthetic test modules under `experiments/tcn-diagnostic-2026-11-13/`.
- `scripts/export_tcn_final_b.py`, the delivery-only registration/storage contract and synthetic export tests under `experiments/tcn-final-b-export-2026-11-13/`.
- Integration against unchanged A/B runner/model inference, official spell matching, strict CSV serializer, final-five checkpoint identities and saved final-fit audit schema.

## Findings and mitigations

No confirmed blocking defect in the reviewed implementation. The exporter test initially referred to a not-yet-defined validator helper; the completed source now defines `validate_csv` and calls it from the export loop. No runtime pass is inferred from that static correction.

The delivery contract independently verifies frozen source, artifact and environment hashes without invoking final-training registration, whose pre-November-16 guard would otherwise reject authorized delivery. Delivery remains allowed through November 17; the separate development diagnostic still stops at the November 16 freeze.

The diagnostic first checks archived CSV bytes and full official metrics, then requires regenerated out-of-fold ensemble predictions and exact CSV digest to agree. Original-coordinate spell accounting splits both halves and unknown-label runs and must agree with the official per-IoU scores. Clean/corrupted comparison retains original ground-truth spell identities. The full intersecting missing-ball burst is measured within valid runs, rather than truncating a long burst to a short possession.

Taxonomy flags intentionally overlap. Its fixed exclusive priority is disclosed as an arbitrary ranking aid, not causal attribution. Raw-argmax matched/decoded missed is evidence of that particular representation difference, not proof of a beneficial decoder change. Proposal generation is conditional, has a three-match consistency requirement and does not select or execute a candidate.

Export validates the exact two-member manifest and repeated-fit proofs, loads first and repeat checkpoints, checks checkpoint identities and exact repeat state, and preserves rotation averaging within each member before equal member probability averaging and penalty-16 decoding. Three fresh-load passes include a batch-4 pass; all four member/view probabilities must agree after reload and every resulting CSV must have identical bytes. The unchanged official validator must return `None`; a truthy/falsey surrogate is not accepted. Output paths are separate private directories, and existing output directories are refused.

Both paths use the shared artifact storage lock and combined artifact roots, with the 2 GiB ceiling and 12 GiB free-space floor. No existing assets are deleted. Source/input/model hashes are rechecked after computation before completion evidence is trusted.

Final export protocol and user instructions were also reviewed. Fresh-environment setup uses the pinned dependency list, no pip cache, explicit pre/post storage checks and a separate output directory. Fresh-clone setup copies committed code locally and shares private inputs; it copies the expected final checks log instead of creating an individual-file symlink that the artifact scanner would reject. The code counts regular files in the new environment and clone, including the original workspace when invoked through the clone, while deduplicating resolved private inputs. Installer/clone transient disk usage is explicitly outside a hard quota and remains a user-monitored limit. Each subsequent command is contingent on success of the preceding one.

## Supplied scenarios, not executed

The diagnostic supplies 14 synthetic tests for half/unknown splits, official greedy tie matching, full-burst exposure and run clipping, absent versus decoder-removed argmax support, merge/fragment associations, clean/corrupted identity mismatches, empty spells, invalid probabilities, count partitions, recommendation consistency, serializer bytes and cache/archive failures.

The exporter supplies 11 synthetic tests for manifest/membership/recipe/repeat-proof rejection, private-output restrictions, delivery dates, official-validator return semantics, half-separated spell accounting, all-dead output, four-view averaging order and storage-floor rejection.

## Residual verification

Static review does not prove archived metric reproduction, actual checkpoint reload equality, deterministic inference, sufficient current disk space, successful clean-environment installation or fresh-clone qualification. Those require the supplied user commands and subsequent review of their saved evidence. Source locks must be generated from the final reviewed bytes and committed before execution. Independent accuracy on the sealed matches remains pending; target-match accuracy is unknown.
