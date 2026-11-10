# User-run gap-augmented TCN blend

First prepare independently masked raw-ball training views:

```sh
cd '/Users/dhruv/Desktop/backend projects/barcelona-track'
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/prepare_tcn_gap.py --prepare
```

Only after `Training-view preparation complete; no fitting`, train/evaluate:

```sh
PYTHONPATH=src:scripts data/gru-env/bin/python scripts/run_tcn_gap.py --run
```

One change:50%clean/50%augmentedwindows in expectation, same20,000updates/CPU1/fiveLOMO/50-50CatBoostblend/penalty16. Trainingmaskseeds distinctfromevaluation. No longrun launched here. Rough1.5–2h estimate extrapolatesparent, notguaranteed. On failure/interrupt preserveoutputs andsenderror; no bypass ordelete/retrysearch. Preparationcreatesprivatearraysandtraining-corruption-fidelity.json; do not expose rawrows. Trialcomparescurrentunaugmentedblend .602554clean/.397037corrupted, notweakerCatBoost. Results/gate/report in experiments/tcn-gap-2026-11-10/. Gatepassprovisional; cleanenv/integration stillrequired. No targetpubliclabels orsealedmatches; no automaticpromotion.
