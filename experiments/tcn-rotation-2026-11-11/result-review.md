# Fixed pitch-rotation ensemble — independently audited development pass

November11. The registered equal average of original and180degree rotated TCN probabilities passes the complete development gate against standalone gapTCN. No new tests, imports of model/data modules, compilation, inference, scoring or training were executed for this review. Saved external aggregate metrics/logs and artifact byte hashes only.

|Mean metric|Parent clean|Ensemble clean|Parent corrupted|Ensemble corrupted|
|---|---:|---:|---:|---:|
|spellF1|.597707089|.602154622|.463139170|.477681884|
|macroF1|.917088737|.919369777|.825775931|.838610693|

Median corrupted spell gain+.014850015 exceeds+.01. Median pairedmean(clean,corrupted)spell gain+.016578383;3/5pairedwins. Median pairedmacro+.005863909 exceeds−.01. Exact ten-cell completeness and all saved per-match gate deltas independently recomputed within1e-12. Candidate/decision gate agree. Three pairedwins are J03WMX,J03WN1,J03WOY; J03WOH/J03WPY regress on pairedmean. Corruptedspell improves4/5, with J03WOH declining−.002743081. All five pairedmacro differences positive. Improvement is heterogeneous, not universal.

Verified158registered file hashes,10originalpreparedinput hashes,30candidateCSV hashes,10reconstructedparentCSV hashes and5checkpoint hashes matched archived standalone records. Parent metrics reproduce original standalone scores within1e-12. Recorded contracts35+4+2+5=46 pass; ten both-viewreload/batchCSV cases pass. No last-failure file. Saved fold stages sum105.259739seconds, not fullwalltime or peakRAM. The audit verifies saved inference evidence, not a new repeatedtraining test; no real-match model was retrained.

The method is eligible to become the new development candidate after root review; production remains unchanged pending qualification. Highest historical clean mean remains unaugmentedTCN .609882, distinct from robust-gate selection. Five repeatedlyreused matches/overlapping folds limit independent generalization. A gate pass is a project threshold, not statistical significance or a competition-rank guarantee. No targetpublic/held-out label use, protectedasset access, downloads, publication or submission.

Rotation averaging uses twice the neural views and cannot resolve the retained model's documented temporal-slotidentity transfer risk. Targetaccuracy unknown. Existing representation/source/decoder track stops remain. No alternateflip/weights/teamswap search or newtraining is authorized by this result. Winnerfinalfit/export/officialvalidation/cleanenvironment/freshclone qualification and single frozen sealed evaluation remain outstanding under existing rules.
