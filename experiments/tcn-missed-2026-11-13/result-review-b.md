# Trial B review — November 13, 2026

Decision: provisionally accept under the exact preregistered median-based v2 gate. This is NOT a higher mean corrupted score: A retains the higher mean. Preserve both candidates and all evidence, with no production switch. Authorized two-trial round is finished; no coefficient, sampler, decoder or new seed follow-up.

Root checks295registeredentries,167committed source/input/review files and443unique byte hashes including A and B evidence. B logs91passingcontracts,20full40kfits/exactrepeat and reload/batchCSV proofs. A committed binding agrees with B's extended signature; B actually records positive segment-loss and segment exposure. No new project imports/tests/compile/model/scorer, model deserialization or CSV row reads. Independent aggregate review in result-review-b-scientist.md.

Mean clean spell .645261041→.650384708; mean corrupted spell .513496193→.509835640 (declines .003660554). Mean clean macro .924253358→.926751542; corrupted macro .843502465→.837980557. Corrupted median gain+.001962250, pairedspellmedian+.004976296,3/5pairedwins, pairedmacromedian+.002403227 qualify. Three corrupted matches improve, WMX(-.035910) and WOH(-.008743) regress, so mean declines. Do not claim a new corrupted-mean best or revise the gate post hoc. A is the highest mean corrupted among this round(.513496193); B is selected by the agreed gate, with independent/target performance unknown.

|Match|Setting|Parent spellF1|Candidate spellF1|Parent macroF1|Candidate macroF1|
|---|---|---:|---:|---:|---:|
|J03WMX|clean|0.633636|0.624036|0.933942|0.932480|
|J03WMX|targetlike|0.519396|0.483486|0.884808|0.861490|
|J03WN1|clean|0.588800|0.614756|0.899015|0.905193|
|J03WN1|targetlike|0.443977|0.452398|0.789555|0.796590|
|J03WOH|clean|0.695979|0.714674|0.937759|0.941679|
|J03WOH|targetlike|0.551841|0.543099|0.860079|0.821960|
|J03WOY|clean|0.661614|0.650614|0.918457|0.922153|
|J03WOY|targetlike|0.514429|0.516391|0.823786|0.845931|
|J03WPY|clean|0.646277|0.647843|0.932094|0.932253|
|J03WPY|targetlike|0.537838|0.553804|0.859285|0.863932|

At IoU.5, clean missed972→953,spurious463→451,short recalled189→198/732,dead/livewrong2386→2315. Corrupted missed1268→1278,spurious647→658,short recalled124→133/732,dead/livewrong50889→54752. Recalled counts inferred from saved per-match ratios. The objective helps short-spell recall and clean segmentation but does not establish improved overall gap robustness. Sum seed/fold durations21140.793seconds(~5h52m21s), not total concurrent wall or peakRAM.

Next delivery work: prepare an identical-config final two-member ensemble fit on five permitted development matches, preserving sealed exclusions, CPU determinism and sampler/segment-loss configuration. Existing original-model finalfit script does not implement this new training recipe and must not be reused blindly. All training/tests/export remain user-run. Clean environment/freshclone, target validator/byte reproduction and once-only freezeNov16 sealed comparison remain pending. No additional quality experiments or target/public-label tuning. Production and existing export unchanged. No downloads, publication, submission or push.
