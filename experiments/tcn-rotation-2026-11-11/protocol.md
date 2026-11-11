# Fixed two-view pitch-rotation ensemble — November 11

## Scope and parent

Next bounded method under the user's standing request to improve metrics, following rejection of the frame-set model. This is inference-only output averaging using existing retained checkpoints. No architecture/training/representation redesign, new training data, augmentation, seed ensemble or decoder tuning. Source/decoder/representation tracks remain stopped with recorded failures. Commit protocol/code/input fingerprints BEFORE user execution; commit reviewed results separately. All tests/import/compile/model/scoring execution remains with the user.

Parent: retained standalone gap-trained original short-context TCN + uniformViterbi16, mean spellF1 .597707089clean/.463139170target-like corrupted. Five checkpoints models/tcn-gap/<ID>.pt; originally trained on otherfourIDSSEmatches,20kupdates,seed20261106. No rejected set/context/all53weights. Checkpoints lack embedded membership: original run/protocol/repeated-fit provenance plus pinned hashes and parent reconstruction are necessary; filenames alone are not proof. Production CatBoost16 stays unchanged.

## One fixed intervention

For encoded x define R as180degree full-pitch rotation about normalized center(.5,.5). Reshape first512columns into64x8objects and negate objectchannels0:4 (centeredXY and bothvelocitycomponents) on a copy. Preserve visibility, H/A/ballroles and all9corechannels exactly. Core nearestH/A distance/margin, ball-speed magnitude, edge distance, masks and gap age are invariant under this rotation. Physical H/A/D states and outputclassorder remain unchanged. Do NOTswapteams or H/Aprobabilitycolumns. No time reversal, reflections, newmissingness or half changes. Do not rotate onlyplayers while leavingball unchanged.

Let f be original whole-half TCN inference. Candidate p=.5*f(x)+.5*f(Rx), normalize row sums once, then unchangedViterbi16. Identityparent uses f(x) only. Fixedweights50/50, exactlytwoviews; rotated-only scores are NOTanotherselectionarm. No searchoverrotation/reflection/weight/temperature. Modeltraining remains exactlytheparent; deployment neuralforward work approximatelydoubles relativeoneview. Extra views are not additional independentdata.

Hypothesis: averaging can remove nuisance coordinate-orientation sensitivity in signedXY/velocity filters and improve teamcontrol/spellboundaries. Averaging can also blur briefpossessions or harm validlearnedpatterns. Symmetry theory/other-task ensemble results do not guarantee nonlinear decodedspellF1. Source reviews supporting mechanism: docs/tcn-next-quality-review-2026-11-11.md and literature/tcn-next-step-evidence-2026-11-11.md. The latter proposed team-role swap; deliberately choose ONLYpitchrotation here as the scientist's lower-mapping-risk hypothesis. Neither proposal has measured superiority; this choice is fixed before scores.

## Inputs, evaluation and checks

IDs exactlyJ03WMX,J03WN1,J03WOH,J03WOY,J03WPY, originalten cacheddata/tcn-prepared clean/targetlike inputs. Samefeatures, labels, independenthistoricaltraining/evaluationmaskseeds and halfblocks. No rawpreparation/refit. No target/publiclabels/sealed/PFF inputs, not even diagnosticselection. No targetexport. Original traininggapviews/20kbudget/seed unchanged because no trainingperformed.

First reproduce pureidentity parentCSV bytes against data/tcn-standalone/<ID>-<condition>-first.csv, archiveddeterminism and archivedspell/macro within1e-12. Abort on mismatch. Score candidate and parent through unchangedofficialscorer on fullhalves, Xoutsideblocks and referenceunknown-label handling. Report alltenmatch/condition spellF1/macroF1 pluserrors, shortspells andmissing-ball dead/livequality. Do not replace per-match gate with pooledframes, stressscores or meanalone.

One --run integrates existing35production+4TCN+2gap contracts and newrotationcontracts beforeinference. Synthetic rawtrack/core/encoding rotationagreement, involution/noinputmutation/maskrolecorepreservation andprobabilitygroup-average contracts check semantics only, neverquality. CPUthreads1/interop1/deterministicTorch/MKLDNNoff; same original H/A/Dorder and uniformpenalty16. Reloadbothviewprobabilities must be exact; first/reload/batch4candidateCSVbytes identical for allten cases. Input/code/archive/environment/checkpoint/scorerhashes frozen and reverified before finalgate. Refuseoverwriting completed/partialattempt; preservefailures for review, no automaticrerun.

## Promotion and stopping

Against current standaloneparent require ALL: median per-match mean(clean,corrupted) spell gain>0;>=3/5pairedwins; medianpairedmacro delta>=-.01; median targetlikecorrupted spellgain>=+.01; contracts/repeatability pass. Passing means eligibledevelopmentcandidateonly; stillrequiresactualwinner finalfit/export, servingcompatibility, officialvalidation andclean/freshclone reproduction. Five repeatedlyreusedmatches do not establish independentgeneralization or targetaccuracy.

Failure closes THISfixedtwo-viewensemble comparison and keepsparent. No automaticalternateflip/team-swap/weights/checkpointsearch. Historicalthreefailedrepresentation changes, threedataexpansionfailures andstoppeddecoder remainclosed. This method changes neither architecture nor learnedfeatureaccess and does not reopen those tracks. Broaderensembletrack stoprule remains threeconsecutivefailures; do not erase earlier failedCatBoostblendcomponents or infer that adding any secondmodel helps. No newseedtraining authorized bythisprotocol.

Newstarts on/afterNov16blocked; reserveNov14–15qualification, then frozenmodel/sealedinterpretation onNov16. No actions afterNov17, no externalpush/submission. Targettemporalidentity transfer risk remainsunresolved: rotationaveraging cannot certify orrepairchanging identities. Targetaccuracyunknown. Runendsaftertencomparisons/noautopromotion. Timing andpeakRAM unmeasured; expectminutesratherthanhours becauseweightsreused, basedonpreviousstandalone~66s offoldstages. Exactruntime must be recordedbyuser-run.
