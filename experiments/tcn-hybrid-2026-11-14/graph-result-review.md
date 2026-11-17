# Graph hybrid result review — November 15, 2026

Reject this fixed graph correction. The candidate fails paired clean/corrupted improvement and majority criteria.

|Setting|Trial B spellF1|Graph spellF1|Trial B macroF1|Graph macroF1|
|---|---:|---:|---:|---:|
|Clean|0.650385|0.647364|0.926752|0.926076|
|Target-like corrupted|0.509836|0.508415|0.837981|0.840447|

Median corrupted delta +0.002031002847passes. Paired median spell delta −0.003345496309fails, with only1/5pairedwins(WN1). Median pairedmacro delta −0.001918644068passes itsguard. ThreecorruptedmatchesimprovebutcleandegradationreversesWMXandWOHpairedoutcomes. Neither a positive corrupted median nor slightly higher corrupted macroF1 overrides the other criteria.

AtIoU.5clean missed953→955/spurious451→484, corrupted missed1278→1276/spurious658→699. Long-gap-exposed missed621→616 and corrupted dead/live wrong54752→52104 improve slightly, without enough ownership/spell recovery. These counts are descriptive associations, not a causal decomposition or a graph-capability ceiling.

Root verifies114registeredentries and180uniquehashes, tenpairproofs/twentycheckpointbytes, thirtycandidateCSVhashes, originalparentmetricbindings, savedgatearithmetic and four-jobruncompletion. Fitproofs reference the prior37passinggraphcorrectnesscontracts. The separate schedulingbenchmark recorded4additionalpassingcontracts. Recorded exactrepeat/reloadprobability/batchCSVproofs pass. No project imports, tests, model/array/CSV-row deserialization, inference or scoring by root. Sumtaskfitseconds is34.38hours, which is not concurrent walltime.

Both authorized hybrid trials are complete and rejected. Keep the fitted Trial-B two-seed ensemble and its qualified local CSV. No hybrid final branch fits are required. Trial A remains the historical higher corrupted mean candidate, but selection stays with the previously approved B. No automatic graph variant, A/B blend, loss change or additional trial follows these results.

Next complete clean-environment and fresh-clone frozen inference qualification for the existing B artifact, finish documentation, and perform the once-only sealed evaluation at freeze under its prospective investigation rule. The new SkillCorner match remains quarantined pending label admission; no additional provider enters training. Target accuracy remains unknown.
