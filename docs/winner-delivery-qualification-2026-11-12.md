# Delivery qualification for the audited40k supervised winner

Prepared November12,2026. This is an implementation specification/checklist, not evidence that qualification has run. User executes every test, fit, inference, validation and scoring command. Current eligible development recipe .632870845clean/.497549978corrupted; production remains CatBoost16 until qualification.

## Exact recipe to carry forward

- Original521-column motion representation, nine core features and original9635parameterclassnetwork; no boundaryloss or geometricpretraining. The registered control's unused reconstructionhead can remain for checkpoint compatibility; it never influences classforward.
-40k supervised updates split into two20k stages. Adam .001/clipnorm1/batch8/window250/halo25/core200. ResetAdam and supervisedwindow/view RNGs at20k, exactly as preregistered. Original seeds, training-gap views, uniform original supervisedwindow sampler, CPU1 deterministic settings.
- Equal original/180degree probability averaging followed by Viterbi16; H/A/Dclassorder andXoutsidevalidblocks. No CatBoostblend.
- Developmentfinalfit trains on the five permitted IDSSEdevelopmentmatches; no PFFlabels, two sealed matches or PFF16holdouts. A separately prepared all-compatible-labelledmatch variant remains unswitched pending user'sdecision after authorized sealedevaluation.

## Files/artifacts to implement next

1. New current-winnerfinalfit registration and manifest, with exactly five allowed matches and source/input/environment hashes. Existing pretrain trainer deliberately rejects five-memberfolds; do not fake a held-outID or weaken its protectedfoldguard. Implement an explicit finalfitentrypoint using identical optimization semantics and new membershipcontract. Two exactfit states/losses/samplingchecks required. No developmentquality claim from this fit.
2. New winner-specific exporter with manifestvalidation. The existing export_neural_candidate.py expects a rejected53matchTCN and hardcodesCatBoost50/50. It must not be repointed at this winner. Preserve legacy evidence; new output staysprivate.
3. Registered servingdiagnostic for documented target slots/identityswitch behavior, localaggregatesonly. Use existing external slotstress protocol ifappropriate, and inspect targetlabel-free structure without claiming identitycorrectness. No silentvelocity repair/identityremapping/modelchange. An unresolved materialtransfer risk must be reported before a release decision.
4. Private generation with unchanged officialformatvalidator, initial/reload/batch4byteequality underbothviews; exactframeindex andXhandling from officialspecification, never manualCSVediting.
5. Freshpinnedenvironment andfreshlocalclone reproduction with matching model/config/input/output hashes. Distinguish frozen-modelinference reproduction from fulltraining reproduction; record both explicitly, and leave unexecuted items pending.
6. FreezeNov16. Evaluate frozenwinner and suppliedbaselines once on each sealedmatch, clean/targetlikecorrupted, only in authorizedstep. Prewrittenrule: weaksealedperformance triggersbug/transferinvestigation, never tuning. Complete finalpublic-window correctnesscheck only within existing authorized limits, neverselectfromit.

## Three deliverables and status

|Deliverable|Status|Completion evidence required|
|---|---|---|
|PossessionCSV|Neuralwinnernotexported|Officialvalidatorpass; exact repeat/cleanenv/cloneCSVhash|
|Source repository|Currentresearchcommittedlocally; releasecommandpending|Newwinnerregenerationcommand, dependencylicences, reachablehistoryassetreview andcleanfreshclonebuild|
|Technical document|Currentresearch/resultslogged; releasefields pending|Finaltrainingmanifest, sources/licences, gap/slotlimitations, rejectedexperiments, hashes and honesttargetaccuracyunknown|

The reachablehistoryassetcheckpreparedalongside thisaudit reports path/commitonly in docs/history-assets-2026-11-12.json. It doesnot certify arbitraryencoded/embeddedderivatives oruntrackedfiles. No externalpublication/submission orhistoryrewrite authorized by thisdocument.

Working development milestone .55targetlike spellF1 andstretch.60 areaspirations, notnewpromotioncriteria orpermissionforserialexperiments. Finiteimprovementcomparisonclosed; qualificationisnext. ReserveNov14–15releasework/Nov16freeze; noactionafterNov17. No newtrainingorvalidationcommand is supplied until exactprotocol/source/inputsarecommitted.
