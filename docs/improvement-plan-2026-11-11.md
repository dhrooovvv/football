# Improvement plan through the November 16 freeze

November11: user authorizes improvement research, preparation and independent review, leaving ALL tests/training/inference to the user. No promise of winning, .8spellF1 or mistake-free code. Reduce error risk with independent static reviews, preregistration and user-run correctness/reproduction checks. Research never substitutes for measured improvement.

## Current evidence and objective

Production is still nine-core CatBoost16. Best eligible development candidate is gap-trained TCN plus frozenCatBoost50/50, penalty16: mean spellF1 .592502 clean/.428386 target-like corrupted. Best clean standalone is unaugmentedTCN .609882; different model/condition, not a blended robust score. The unweighted52-match training policy regressed to .520562/.376959. It failed0/5pairedwins. Target accuracy unknown; five reused development matches are not independent confirmation.

Independent scientist, implementation reviewer and primary-literature researcher support one fixed provider-mixture comparison next. No confirmed implementation bug explaining the regression was found. Roughly93%PFFsample exposure is observed; its causal contribution versus labels/noise/convergence remains unproven. No reviewed open checkpoint is both demonstrated superior on our official metric and cleared for data-overlap/licensing/adapter constraints.

## Step 1 — November11: one fixed mixed-provider trial

Run the already prepared data with P(IDSSE)=P(PFF)=.5; uniform eligible starts conditional on provider. Fresh initialization,20kupdates, originalarchitecture/gaps/seeds/budget/CatBoostblend/decoder/scorer/splits. Report actual exposure. Hypothesis and code: experiments/tcn-balanced-2026-11-11/protocol.md; user commands docs/run-tcn-balanced.md. No new data preparation. Failed expansion is descriptive; promotion must beat retained best under all original conditions, including median corruptedgain>=+.01.

Expect roughly1.5–2h based on priorfoldstages, not a guarantee. First user-run small checks; stop and preserve any failure. No all53fit after numeric rejection. Trial3 in the data-expansion sequence after CatBoost/TCNexpansionfailures; another failure stops thattrack, with no ratio, update-budget or adaptation rescue. Closed othertracks stay closed. A pass remains provisional.

## Step 2 — November12–13: one separately registered context intervention

After reviewing Step1, use whichever candidate remains eligible. The current learned field is17samples, approximately.68s by sample-duration count; precomputedgapage also retains longer scalar history. Input250frames does not make its learned field10seconds. Test a larger dense-support temporal field as ONE architecture intervention, with a fixed field/halo before execution, same retained200lossframes/update and budget, stricthalf boundaries and observationmasks. Larger field needs larger crops/halo; disclose extra parameters/compute and longer runtime rather than pretending identical cost. Do not bundle attention, boundaryloss, sampling, symmetry, calibration or moreupdates.

This is a prioritized proposal, not a registered/run experiment or a predetermined passing model. Exact design/source hashes and independent review follow the Step1decision, so the scientific parent is unambiguous. If testing/reproduction cannot finish before delivery reserve, do not start it. No target or sealed scoring for choosing context. Do not reopen the stopped data-expansion track under the label of context.

## Fine-tuning and model alternatives

Fine-tuning is technically available, but initialization is training data. The final53checkpoint has already seen every development match and cannot initialize LOMO quality evaluation. Safe sourcepretraining would use PFFtraining48only or each fold's52checkpoint for its own heldoutmatch, with totalupdatebudget and optimizerreset/retention fixed in advance. Added adaptation updates need an equal-total-budget comparison. If Step1fails and the data-expansion track stops, this is deferred unless the user explicitly reopens it; it is not a backdoor next trial.

TranSPORTmer/PathCRF suggest temporal/social or structured interactions, but reported tasks/scores are not our possession spellF1 and checkpoint provenance/admissibility remains unresolved. RelativeXYbundle already failed; do not repeat it as untested. Generic published pretrained weights are not a proven shortcut. No hosted model is required; all authorized local training can remain on the supplied machine.

## Step 3 — November14–15: qualify the actual retained winner

Reserve time for the winner's correct checkpoint/export registration, localtargetadaptercontinuity review, officialCSVvalidation, identical bytes onrepeat/reload/batch and cleanenvironment/freshlocalclone. Existingexporterloads the rejected uniform-expansionfinalmodel; it must not be mislabeled as the retainedwinner's releaseworkflow. Trainingreproduction and frozeninference reproduction are separate. Keep technicalreport/licences/citations/hashes/rejectedexperiments current. Complete the existing historyleakscan and freshclone checklist; do not infer completion from this preparation.

Stop research early if necessary to finish these checks. No newexperiment just because time remains. Do not trade away release verification for another unqualified developmental score.

## Freeze and delivery — November16

Freeze configuration before opening sealed data. Apply previously written interpretationrule, score candidate/suppliedbaselines once on sealed2clean/corrupted. Large regression triggers bug/transferinvestigation, never tuning. Protectedmatches never entertraining. Finalpublicwindowcheck is correctnessonly and cannot select anything. FinalCSV/regenerationcommand/officialvalidator/byteproof/hashes plus technicaldocument and organizer-required package. No external submission/publication without userinstruction; no research after freeze or action afterNovember17.

## Sources and reviews

- docs/tcn-training-strategy-review-2026-11-11.md — independent scientist.
- docs/tcn-expanded-static-review-2026-11-11.md and docs/tcn-balanced-static-review-2026-11-11.md — independent source review.
- literature/tcn-transfer-context-refresh-2026-11-11.md — primary-source research with contrary evidence and task limitations.
- experiments/tcn-expanded-2026-11-10/result-review.md — completed measured expansion failure.
- ball.md — append-only decisions and historical protocols/gates.


November11status: fixedbalancedtrial rejected; dataexpansiontrack STOP atthreefailures. User approvedStep2. Exactlongercontextregistration andusercommands are now experiments/tcn-context-2026-11-11/protocol.md and docs/run-tcn-context.md. No tests/training executed duringpreparation; parent remainsoriginalIDSSEgapblend. Release/freeze reserves unchanged.


November11 audited update: fixed standalone gapTCN comparison passes full gate (.597707clean/.463139corrupted,4/5pairedwins, medianprimary+.040271). New retained candidate is standalone gap-trained short-contextTCN+penalty16. Balanced expansion and longer context remain rejected. Next prepare candidate-specific finalfit/release qualification and resolve target slot continuity; user executes all checks. No automatic further training or reopening stopped tracks.
