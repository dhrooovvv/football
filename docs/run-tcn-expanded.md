# Train TCN with all 53 eligible matches

The user chose more training data while preserving test matches. This runner uses all five IDSSE development matches and the existing 48 PFF training matches. It preserves the two sealed IDSSE matches and 16 PFF transfer matches.

The full command runs checks, prepares memory-mapped inputs, evaluates five held-out IDSSE matches using 52 training matches per fold, then trains a model using all 53 eligible matches. Training uses 20,000 updates per fit with the current architecture, augmentation, 50/50 CatBoost blend and penalty 16. Each fit is repeated for reproducibility.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_expanded.py --run
```

To run stages separately, use these commands in order. The first runs only the small code checks.

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_expanded.py --check
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_expanded.py --prepare
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_expanded.py --evaluate
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_expanded.py --fit-final
```

Code has been prepared and inspected. These commands and their checks have not been executed by the assistant. A check or data-contract failure should be reported with its traceback. Preserve outputs. Progress is saved every 1,000 updates. Rerunning the same command verifies completed work and resumes compatible checkpoints. Contract failures need review before rerunning. A process lock prevents two expanded commands running simultaneously.

Expect an hours-long job. Preparation parses 48 PFF matches and uses approximately 11 GB extra disk, with actual storage depending on timeline sizes. Runtime and peak RAM are unmeasured. Memory maps assemble only each training batch in RAM. CPU uses one thread with no custom memory cap. The original datasets must still be present in this workspace.

The larger pool makes PFF dominate the available windows. This first trial preserves uniform window sampling so that data expansion is the only scientific change. Coverage reports show actual sampled windows per match. The fixed update budget does not promise every unique frame is visited or that the larger model training converges. Earlier PFF expansion failed for CatBoost. A TCN benefit must be measured.

Development results are written to experiments/tcn-expanded-2026-11-10/evaluation/report.md and gate.json. The gate reference is the previous gap-trained blend (.592502 clean / .428386 corrupted), not the weaker CatBoost baseline. Standalone TCN scores are included as diagnostics. All source/array hashes are registered before execution.

The final model is models/tcn-expanded/final/tcn-53-matches.pt. It contains the model state, feature constants and training membership. Full-pool fitting creates a research variant even if the development comparison fails. Review the gate before considering it for use. Release reproduction and target integration remain required. No current production artifact is switched by these commands. No target game labels or protected-match data are loaded.
