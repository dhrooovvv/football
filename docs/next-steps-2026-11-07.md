# Decision plan — November7–13
Recommendation: prioritize trustworthy PFF ingestion and the two authorized data evaluations. Preserve current production9core/unaugmentedCatBoost/penalty16. Do not reopen failed decoder grids or add features to compensate for ingestion bugs.

Evidence: PFFintake64matches/29.97Hz, prospective48training16transfer split locked; all64show repeated frame IDs; firstprobe401conflictingpayload duplicates. These are ingestion findings, not performance evidence (experiments/pff-intake). Decoder3failures and nestedsettings rejection documented under extension-2026-11-07. Current reproduction already passes. Independent transfer remains unmeasured.

| Target date | Contributor | Work / exit criterion |
|---|---|---|
| Nov7–8 | A:data | Preregister duplicate/CLK/time contracts. Separate coordinate conflicts from label conflicts; check whether generated/smoothed timestamps establish provider-supported update order. Never choose first/last by model score. Collapse identical observations; conflicting unresolved observations/labels remain missing/unknown or fail contract, not averaged labels. Validate half boundaries and29.97→25Hz mapping without filling tracking gaps. Compare team/coordinate/state semantics against pinned Kloppy parser as an independent implementation, not unquestioned truth. |
| Nov8–9 | B:evaluation | Synthetic contracts, all64admission report with exclusion counts/provenance; keep48/16split fixed. Train-more comparison: each existing IDSSE outer match excluded from baseline and expanded training; same features/settings/seeds/budget/penalty16, CPU1. Original gate plus corrupted median+.01. No admission if adapter contracts fail. |
| Nov9–10 | B:evaluation | Frozen IDSSE→16PFFtransfer holdout; PFF48→IDSSE5reverse where labels support it. Clean and fixed target-like corruption, per-match metrics and missing-ball dead/live quality. No calibration, tuning, selection or promotion based on transfer results. Report uncertainty/ranges and label-convention caveats. |
| Nov7–12 | C:delivery | Keep technical report, licences/access terms, every rejection, hashes, leak scan and one-command raw-input reproduction current. Reproduce in clean environment after any production promotion. |
| Before Nov11 | All | GRU eligibility decision only after Tracks1–3 actually complete. One small deterministic scratchCPUmodel/blend if time permits; otherwise explicitly skip. No automatic reopening of stoppedTrack2 or expanding fixedTrack3search. |
| Nov11–12 | A+B | Resolve contract/transfer bugs without tuning to transfer measurements; produce stable candidate/config manifest. Preserve independently fixed splits and current best if more-data candidate fails. |
| Nov13 freeze | All | Commit configuration and sealed interpretation before opening files. One sealed evaluation candidate+suppliedbaselines,2matches clean/corrupted; lower scores trigger bug/transfer investigation, NOT tuning. Final frozen public score once for correctness only. Prepare separate all-compatible retrain variant EXCLUDINGsealed2, sameconfig, reportcost, await user decision before switching. |
| Nov14–16 | All | Delivery only: finalCSV official validation, two independent runs and clean/fresh-clone equality, hashes; team-namedCSV, publicsource, technicaldocument. No external submission. |

Dates are target allocations, not claims of completed work or assigned humans. Contributor roles are a proposed division for the user's3contributors. No automations scheduled.

Main downside: more labels can worsen the model if PFFownership/dead conventions differ; keep it only through the strengthened gate. Repeated use of IDSSE5means a passed gate does not establish unbiased superiority; nestedCV does not erase history. Transfer holdout is diagnostic and cannot become another tuning leaderboard. Unresolved PFFusage terms prevent claiming redistribution rights; keep all rawassetsprivate and retain access terms if supplied.

Primary implementation references: https://kloppy.pysport.org/user-guide/loading-data/pff/ and pinned PySport/kloppy PFFparser a9651eba7c4dbbe2d2fc6d4cffb4aea63fadac11. Local specifications/manifest in pff-intake/report.md. Generic loader support does not resolve this release's duplicate conflicts or CLKsemantics.

Immediate next action: commit the strict adapter-validation protocol, then implement/test it. No new performance experiment until its contracts pass. Plan/gates/freeze unchanged except the already-authorizedNov13extension.


## Completed checkpoint — November7
Adapter admission64/64(rawVISIBLEonly, no label-conditioned smoothedball), 48/16split unchanged. Train-more failed0/5 and bothgates; keeporiginalIDSSE5ninecore16. Descriptive providertransfer completed and poor, no tuning fromscores. See experiments/pff-evaluation/report.md. OptionalGRUprerequisitesnowfinished; stillrequires owncommittedprotocol/startbeforeNov11 and deterministicreproduction. Not started in this sequence. Freeze/delivery gates unchanged.
