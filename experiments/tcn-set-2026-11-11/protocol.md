# Identity-robust frame-set TCN — approved fixed training experiment

November11,2026. User explicitly approved an identity-robust TCN after asking to prioritize models and methods over standalone diagnostics. This registration supersedes the proposed sequencing prerequisite of the still-unexecuted slot audit; it does not claim that diagnostic was run or that target damage was measured. The slot audit is optional/deferred. ALL execution including synthetic tests, imports/compilation, model inference and training stays with the user. Commit protocol, source, membership and fingerprints before execution; commit results separately.

## Parent and hypothesis

Parent: current best eligible standalone short-context gap-trained TCN + uniform Viterbi16, mean development spellF1 .597707089clean/.463139170target-like corrupted. Production stays CatBoost16. Candidate is also standalone, with NO CatBoost blend. Use the original five leave-one-match-out matches and ten frozen full-match clean/corrupted evaluations.

Hypothesis: model football as a sequence of per-frame player sets, avoiding the target's documented unstable player-slot identity. Official DATA.md99–101/OVERVIEW.md90–93 says target slots swap identity; IDSSE external tracks use persistentPersonId. Removing reliance on same-slot velocity/history before pooling may improve robust possession estimates. This is a transfer-motivated architectural hypothesis, not a demonstrated target defect or guaranteed development gain. No target accuracy or winning-score forecast.

## One fixed representation redesign

Keep the encoded521input schema (64slots×8 +9core) and all prepared arrays. For each frame and object, select ONLY centeredX, centeredY, visibility (channels0,1,4). Shared nn.Linear(3,8) +ReLU independently embeds every object at that frame. Multiply by instantaneous visibility×home/away/ball role mask, then take three maskedmeans (denominator at least1). Concatenate24pooledchannels with unchanged9core features =33channels. No convolution over an object's time history before pooling. No stored objectvelocity channels2:4 consumed, for players ORball. Existing core scalar ball speed remains; do not call this a motion-free model. Do not append counts, pairwise relations, centroids, newmaskfeatures or augmentation.

Apply EXACT parent temporal stack AFTER pooling: Conv1d33->32,k3,dilation1,pad1/ReLU;32->32,k3,dilation2,pad2/ReLU;32->32,k3,dilation4,pad4/ReLU;32->3,k1. No dropout/normalization/residual/attention/refinement/loss/temperature/decoder change. Candidate9,539parameters versus9,635parent (-96); encoded receptivefield15/radius7 versus17/radius8. No capacity/RF compensation. Per-slot velocity removal and object temporal encoder removal together define this ONE semantic redesign; any gain cannot be attributed causally to only one component. Changes in ball vector information/capacity/support are disclosed.

With correct teams and instantaneous observation masks, the candidate is mathematically invariant to independently changing same-team player ordering at every frame. Float reduction order may cause numerical differences; synthetic tolerance checks do not establish exact permutation CSVbytes or target quality. Missing/duplicate detections and team errors remain unresolved; this is not a tracking repair.

## Fixed data, folds, training budget

IDs in original order: J03WMX,J03WN1,J03WOH,J03WOY,J03WPY. Train each candidate from scratch on the OTHERfour, never from a fold/full-pool checkpoint. No sealedJ03WQQ/J03WR9, PFFtrain/holdout, target data, public labels or new data. Reuse ONLY five existing compactIDSSE cases under data/tcn-expanded/idsse-<ID>; despite directory name no PFFsource is loaded. Hash exact manifests and all sixarray/metadata members before modelling. Previous lossless preparation links the cases to originalclean and training-gap inputs. No raw re-preparation/corruption refit.

Preserve valid known-label250frame anchor support/order from parent, windowRNG seed20261106, independent gapview RNG seed20261106+424242 and Bernoulli(.5). Existing raw-ball traininggap seeds20261206+i are distinct from fixed evaluation seeds20261106+i. Training masks were applied BEFORE feature computation in prior preparation; no encoded-only gap manipulation is added. Each sample uses exactly250frames, originalHALO25 and central200losslabels. No half crossing or label-dependent inference reset. Same normalized inputs and identity scaler; train fits no preprocessing on held-out matches.

Exactly20,000updates×batch8×200lossframes=32millionloss-frame presentations per fit, repeats included. Adam lr.001, clipnorm1, crossentropy, fixed seed20261106, float32, CPUthreads1/interop1, deterministicTorch/MKLDNNoff. No early stopping/checkpoint selection, more updates, class/provider weighting, symmetry, seedensemble or newdata. Same seed does not imply identical initial tensors for different architecture shapes. No customRAMcap. Two independent complete fits per fold must reproduce states, loss histories and coverage exactly; do not count that repeated fit as another scientific seed.

## Integrated checks and reproducibility

One --run command performs contracts THEN fivefold training/scoring. No prerequisite standalone slotdiagnostic or separate mandatory --check job. Existing35production+4TCN+2gapcontracts plus newsetcontracts cover per-frame set/masking invariance, ignored velocities, modeldimension/support, half/chunk/reload behavior and interrupted synthetic training resumption. These are supplied, not executed by assistant; synthetic performance is not quality evidence.

Checkpoint every1000updates and at end atomically records optimizer, Torch/window/viewRNG, losses, coverage, membership, architecture/schema and registration signature. Resumption requires identical inputs/source/config and valid checkpoint; preserve errors. Completedfold cache requires both conditions, exacttrainingmembership, unchanged source signature, checkpoint and threeCSVhashes. No silently reused all-five/all53 model. Report user-run exact repeated training and reload probabilities; initial/reload/batch4 CSVbytes identical on all10cases.

## Evaluation and gate

Use unchanged reference scorer, H/A/D order, full-half inference and decode16; X outside blocks. Frozen parent CSVs from data/tcn-standalone/<ID>-<condition>-first.csv and archived parent results must hash/score match; no public/target rows or newcorruption. Candidate scores alltenconditions. Record per-match spellF1/macroF1, missed/spuriousspells, shortspellrecall, boundary distributions, missing-ball dead/live quality, coverage/losses/timings and hashes.

Compare ONLY this candidate to current standaloneparent under ALL existing conditions: median per-match mean(clean,corrupted) spell gain>0; at least3/5pairedwins; medianpairedmacro delta>=-.01; median targetlikecorrupted spell gain>=+.01; tests and deterministicchecks pass. No wins based on meanalone, stressscore, cleaner-lookingCSV or targetaggregate shares. A passing gate is developmenteligibility, pending release qualification, not automaticproductionpromotion. Five reusedmatches imply selectionoptimism; no claim of independent targetgeneralization.

This is one user-authorized temporal-identity representation trial, not reopening stopped source/decodertracks or erasing earlier sequence/context/feature failures. Keep all failurecounts; failure rejects this exactmodel and closes its fixedbudget. No automatic MLPwidth/layer/velocity/RF/trainingbudget rescue. Stop any broader track atthree consecutivefailures; model rename is not resetauthority.

## Outputs and schedule

Results experiments/tcn-set-2026-11-11/evaluation/, modelresumption models/tcn-set/evaluation/, privateCSV data/tcn-set/. The command stops afterfivefolds. No finalall5fit, targetexport, protectedevaluation, externalpush or submission. Next reviewed decision either retains currentparent or provisionally selects thiscandidate; then separatelyregister actual winner's finalfit/export/validator/cleanenvironment/freshclone proof. Preserve Nov14–15qualification and Nov16freeze/sealedinterpretation. Newstarts on/afterNov16blocked; no action afterNov17. Targetaccuracyunknown. Runtime unmeasured; originalgapTCNinitialfits were about450seconds each; tenfits pluspreparationchecks/inference could take around1–2hours, with compactI/O/thermals potentially changing this substantially. User runs every part; no assistanttest/import/compile/modeljob.

Stop-accounting clarification before execution: conservatively treat the rejected relative-XY and longer-context TCN trials as two prior failed representation changes. If this fixed representation trial also fails, stop that representation-improvement line at three; no automatic width/kernel/velocity redesign. Historical outcomes in all other tracks remain recorded. A protocol pass is not a statistical significance result or permission to use protected matches early.
