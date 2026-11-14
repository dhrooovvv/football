# Benchmark fuller Mac utilisation

Prepared November14,2026. All commands are user-run. No benchmark, new tests, fitting or inference has been executed by the assistant.

Start with this scheduling benchmark. It compares two and four concurrent fold/seed jobs, retaining one numerical thread per job. It uses ten64-update probes per allocation, then verifies training-state/loss/RNG equality against the other allocation and existing serial references. A fixed16384-frame inference check also requires identical CSV bytes. It reports actual wall times and sampled concurrent processRSS. The faster reproducible schedule is selected using runtime alone.

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_hybrid_parallel.py --benchmark
```

Return the completed benchmark for review. Runtime is unmeasured, and the benchmark may show that the complete workload still exceeds the November16freeze budget. Keep the Mac on power and awake using caffeinate. Do not rerun a failed/interrupted benchmark blindly because its partial evidence is preserved.

After review confirms correctness and sufficient time, the full graph comparison uses the selected allocation automatically.

```sh
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_hybrid_parallel.py --run
```

This still performs twenty40kdevelopmentfits with the original graph model and gate. Its ten paired-fold tasks have independent subprocesses, avoiding numerical multi-thread changes. Full fitting resumes using the identical command. Report completion before graph review/promotion. Use the existing explicit graph review command only after the saved evidence has been audited and commit that decision.

If graph qualifies, parallelize its four final-five-match fits with the selected allocation.

```sh
PYTHONPATH=src:scripts caffeinate -i data/gru-env/bin/python scripts/run_tcn_hybrid_parallel.py --fit-final
```

This supports the current graph-only branch over the frozen final B parent. Four first/repeat tasks produce two independent seeds, with exact repeated-training validation before the existing final manifest is written. The original release exporter can then consume models/tcn-hybrid/final/manifest-graph.json. Follow docs/run-tcn-hybrid-release.md for export, clean-environment/fresh-clone and once-only sealed qualification. No numerical gains follow from scheduling alone. Target accuracy remains unknown.
