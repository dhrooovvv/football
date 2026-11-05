# H1 preliminary contracts — results

Run h1-contracts-001: six preregistered confirmatory tests passed and three exploratory tests passed. Command/environment/source hashes are in results/run.json; raw output is in results/test-output.txt. Protocol was committed at 14385bb before implementation/execution. Original protocol remains unchanged as historical evidence.

The decoder suppresses the specified ambiguous frame, preserves the two-frame strong turnover and stoppage/restart, resets across halves, and is deterministic. Invalid probability arrays fail. Exploratory exhaustive enumeration of ten five-frame sequences with asymmetric transition costs agrees with the decoder optimum; additional tests cover output gaps, zero probabilities, empty arrays and malformed blocks/costs.

No failures occurred on this run. These results establish the specified implementation contracts only. They do not establish H1's external-match spellF1 prediction, model quality, or a complete fallback. Uniform ties use the fixed H/A/D order, so symmetry is only claimed for non-tied fixtures.

Decision: retain the decoder component. Next: strict adapters/exporter and external-match label feasibility. No target assets or target/public labels were read in this experiment.
