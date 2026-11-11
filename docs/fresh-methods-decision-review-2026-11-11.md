# Fresh-methods decision review — November11

## Supported finding and decision

We have not measured a ceiling. The current scientific question is whether an untested method can improve the retained pipeline under the registered match-level gate, while preserving transfer validity and release feasibility. The decision is which ONE next prospective comparison, if any, deserves a new authorization and preregistration. This note is research only: it registers/runs no experiment and does not reopen stopped tracks.

The original gap-trained standalone TCN achieved .597707clean/.463139corrupted. During this review the user's rotation run completed; a separate read-only aggregate/hash audit found its registered gate passes, with .602155/.477682, medianprimary+.014850 and3/5pairedwins. Root owns acceptance/state changes. Any future comparison must use the actual newly retained winner, not a weaker historical parent. The modest rotation gain is proof that one tested method improved the reused-development metric; it does not estimate the remaining headroom.

## Error evidence and uncertainty

Saved standalone-parent aggregates show1,086missed/497spurious spells clean and1,373/772corrupted atIoU.5. Short-spell recall is142/732(19.4%)clean and90/732(12.3%)corrupted. Under targetlikecorruption,286,943missing-ball gradedframes include31,970dead frames predictedlive and24,074liveframes predicteddead. These are descriptive summed errors from five matches, not independent samples, the official mean-over-IoU score, or necessarily the latest rotation model's taxonomy. The parent corrupted per-matchspell range is.377544–.521379, showing heterogeneity.

No frame-level confidence interval, independent-binomial interpretation of matchwins, or causal claim follows. Exact repeatedfits/CSV hashes measure computational repeatability, not sampling uncertainty. Five repeatedly reused matches have selection optimism; the preserved frozen sealed evaluation is the next independent existing-source check, and PFFholdout remains transfer-risk measurement only. A further architecture win on the samefive is not proof of target transfer.

The failed frame-set model removed storedmotion, per-objecthistory and somecapacity/support together; its .502256/.361285 result rejects that design/budget, not invariant representations generally. The retained model's targetslotidentity dependence remains unquantified. An accuracy ceiling cannot be inferred without knowing labelnoise, missing observations and the conditional information available at inference. Long ball gaps can make different true possession sequences observationally indistinguishable. More optimization cannot guarantee recovery of unavailable evidence.

## Ranked paths

### 1. Near-term lower-risk method: one fixed seed ensemble

After the current rotation decision, the simplest untested way to obtain model diversity is one additional fold-safe scratch training seed, with the retained architecture/budget/data/augmentation unchanged, then an equal average of two seeds. Apply the same retained view policy to both models. Keep penalty16 and every evaluationmask fixed. One scientific intervention is fixedseed averaging; a changedarchitecture/extraobjectives/corruptionratio must not be added.

Each member keeps20kupdates, but total training and inference compute increases; this is not equal-total-compute to a singlemodel. Two exact computational repeats are still required for each newseed/fold. No model trained on allfive or final53 may initialize folds. Predeclare seed, two equalweights and fixedfinalcheckpoint; no bestseed/checkpoint search. Compare the exact ensemble to the actual retained parent under the complete gate, with allfive clean/corrupted results and regressions. Additional walltime/peakRAM are unmeasured; historical shortfoldtimings cannot certify the new run.

Rationale is plausible error diversity, not new information or a forecast of a largegain. Correlated seederrors can erase the benefit, and averaging can delete shortspells. Confidence moderate in evaluability, low in gain direction/magnitude. This would need a new bounded authorization/protocol and explicit accounting of ensemble compute; research alone does not start it. Existing evidence: literature/tcn-next-step-evidence-2026-11-11.md primaryDeepEnsembles source.

### 2. Higher conceptual relevance: train for boundaries/segments, not only frame labels

Short possessions are frequently missed while frameclassification remains relatively strong. A fundamentally different objective is to weight training errors near true training-set possession boundaries, while keeping the architecture unchanged. An interpretable prospective singletrial would retaincrossentropy but apply one fixed training-only boundaryweight schedule, computed insideeachfold from its four traininglabelsequences. It must not use heldout/target boundarytruth at inference. Hold all20kbudget/seeds/windowstarts/gapviews/decoder/viewpolicy fixed. Predeclare one coefficient and one boundarywidth, not a lossgrid, and report shortspellrecall, missed/spurious counts and boundaryshift changes alongside the fullqualitygate.

This is a hypothesis, not an evidence-backed optimal weighting formula; no numerical coefficient is selected here. It may overfit annotationnoise, trade longspellquality forshortspells or change calibration unfavorably. The current counts do not causally prove that boundaryweighting addresses the dominant error. MS-TCN-style smoothing is a different intervention and could further suppress shortspells; do not add it automatically.

This line requires an explicit plan amendment: representation/decoder/model-search stops cannot be bypassed by renaming an architecture or silently changing loss. No protocol/code/run is supplied by this review. Confidence moderate in mismatch between frameCE and spellmetric, low in achievablegain. Given freeze, do not launch this plus seedensembling simultaneously.

### 3. Largest information-change opportunity: external-validated video evidence

Reducing unobserved-ball intervals with genuine visual measurements or playercrop evidence could add information absent from tracking. That offers a different mechanism from largerTCN/decoder/ensembles. It also has the highest integration risk: synchronised external evaluationvideo, calibration, labels, detectorlicence/provenance, visibility/error modeling and localcompute are prerequisites. A target-only visual addition evaluated by publiclabels would violate the selection rule; pseudo-predicted ballpositions do not create trueobservations and must carry uncertainty/masks.

The parent owns a separate public-source/video feasibility review. Without compatible external evaluationvideo, this is a researchlead rather than a valid nextpromotionexperiment. Targetvideo is available but alone does not establish a fair development comparison. No hostedprocessing, handlabellingtarget or downloads are authorized here. Confidence in theoretical value of additional reliableobservations is high; practical compatibility and scoregain remain unknown.

## Paths not to repeat automatically

A largerhiddenwidth, anotherdilationgrid, per-framecollectiveencoder tweak, blind40kextension, newPFFmixture, alternativeViterbipenalty or rebrandedfragmentationaugmentation would reopen stopped/closed work. Searching their papers is permitted; executing requires explicit amended scope and a locked protocol. Training-time slotfragmentation may preserve usefulmotion better than discardingit, but the current dataset/modelstate does not prove this, and it belongs to the stopped representation line. It is not a loophole.

External eventweaklabels are not automatically better than the fullteamlabels alreadyavailable. TargetSmartTagging cannot silently become trainingtruth; any use must satisfy competitionrules, featureavailability and externaltrain/test parity. A possession/state feature supplied by anotherpaper may itself be a label leak. Priors cannot identify a long-gap state when no distinguishing observations exist.

## Recommendation

Finish/audit the alreadyregistered rotation comparison, then qualify the retained winner. If the user wants one further bounded model-method experiment before the freeze, rank fixedtwo-seed averaging ahead of a new architecture because it is fold-safe and uses unchanged validinputs; no majorgain promised. If pursuing a structuraljump, prioritize feasibility of genuinely newvisualevidence or an explicitlyamended boundaryobjective—not another unnamed transformerreplacement. Do not run multiple paths together. Preserve fullpromotiongate, allfailurehistory, Nov14–15qualification/Nov16freeze and targetaccuracyunknown.

Sources: projectAGENTS/journal/state/findings; savedstandalone/core/set/rotation reports; docs/tcn-release-readiness-review-2026-11-11.md; literature/possession-benchmark-audit-2026-11-09.md; literature/tcn-next-step-evidence-2026-11-11.md. Analysis uses saved externalaggregate JSON arithmetic and source inspection only; no new tests/imports/compile/model/scorer/dataarray execution, rawtarget/protected assets, downloads or externalmessages. This document adds no empirical performance claim beyond the separately audited saved rotation result.
