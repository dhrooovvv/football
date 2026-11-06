# Approved augmentation and prerequisite report

Primary augmentation metric: target-like corrupted spellF1. Promotion gate unchanged: per-match arithmetic mean clean/corrupted spellF1; positive median paired gain, majority improve, median paired macroF1 delta >=-.01, tests pass. Frozen penalty8 parent for both isolated changes.

## Corruption fidelity

| Match | Target missing | Original corrupted missing | Target-like missing |
|---|---:|---:|---:|
| J03WMX | 0.4069 | 0.2683 | 0.3572 |
| J03WN1 | 0.4069 | 0.2808 | 0.4007 |
| J03WOH | 0.4069 | 0.2618 | 0.4752 |
| J03WOY | 0.4069 | 0.2625 | 0.4237 |
| J03WPY | 0.4069 | 0.2598 | 0.3590 |

Evaluation masks were applied to raw ball positions before feature computation. Cached training/evaluation features pass mask/gap-age/speed consistency checks. Training seeds20271106+i; evaluation20261106+i; replacement20281106+i. Actual missing rates vary because long runs and half-boundary truncation create sampling variance; no post-hoc calibration on labels.

Longer contiguous gaps can remove many flickering predicted spells while erasing more graded live frames. That can raise spellF1 while lowering macroF1: spells and frames are weighted differently. This is an evidence-supported mechanism, not an isolated causal experiment; missing fraction and run structure both changed.

## Decoder isolation and augmentation means

| Method | Condition | spellF1 | macroF1 |
|---|---|---:|---:|
| argmax | clean | 0.076666 | 0.840260 |
| argmax | targetlike | 0.064138 | 0.638499 |
| smooth50 | clean | 0.338277 | 0.821343 |
| smooth50 | targetlike | 0.233435 | 0.672781 |
| penalty8 | clean | 0.508566 | 0.889775 |
| penalty8 | targetlike | 0.312864 | 0.672865 |
| penalty16 | clean | 0.517654 | 0.895099 |
| penalty16 | targetlike | 0.323476 | 0.679401 |
| augmentation_penalty8 | clean | 0.512550 | 0.889686 |
| augmentation_penalty8 | targetlike | 0.316068 | 0.671941 |

Smoothing50 uses the supplied centered H/A majority logic on CatBoost argmax codes, D contributing no H/A vote. It is not a three-class probability smoother. Nearest-player+decoder used near-hard .98/.01 emissions and is not evidence isolating decoder quality.

## Label conventions

| Match | Dead share | Mean possession spell seconds |
|---|---:|---:|
| J03WMX | 0.4151 | 6.6825 |
| J03WN1 | 0.5170 | 5.4702 |
| J03WOH | 0.4757 | 7.1587 |
| J03WOY | 0.4648 | 6.6918 |
| J03WPY | 0.4429 | 7.7397 |
| Public window (semantics only) | 0.1959 | 14.1906 |

Documentation: external DFL/floodlight BallStatus0=Dead,1=Alive and BallPossession1=Home,2=Away (literature/idsse.md); target DATA.md public summary has17 maximal H/A spells, mean14.2s, with D denoting dead ball per EVALUATION.md. Both nominally use H/A/D, but exact ownership continuation through loose balls/flight is not established equivalent. External unknown ownership is excluded as X and breaks spells, which can shorten measured spells.

Baseline macroF1 about .38 externally versus the previously supplied target scores about .67 is a warning of possible convention/domain mismatch, not proof. External clean balls are essentially always observed: nearest-player almost never emits D despite41–52% dead labels. Target ball absence about41% makes its missing=>D heuristic behave differently; short public sampling also differs. Do not relabel, tune mappings or claim transfer equivalence from this comparison. No new public performance scoring.

## Per-match augmentation against penalty8

| Match | Condition | Parent spellF1 | Aug spellF1 | Parent macroF1 | Aug macroF1 |
|---|---|---:|---:|---:|---:|
| J03WMX | clean | 0.499781 | 0.497380 | 0.902245 | 0.901670 |
| J03WMX | targetlike | 0.304892 | 0.306849 | 0.685807 | 0.691008 |
| J03WN1 | clean | 0.496432 | 0.496104 | 0.873339 | 0.870904 |
| J03WN1 | targetlike | 0.310214 | 0.317900 | 0.675876 | 0.683337 |
| J03WOH | clean | 0.527205 | 0.532497 | 0.894625 | 0.896916 |
| J03WOH | targetlike | 0.325326 | 0.323209 | 0.637961 | 0.632202 |
| J03WOY | clean | 0.483060 | 0.494537 | 0.874689 | 0.875849 |
| J03WOY | targetlike | 0.294293 | 0.302133 | 0.654699 | 0.651082 |
| J03WPY | clean | 0.536352 | 0.542234 | 0.903977 | 0.903090 |
| J03WPY | targetlike | 0.329596 | 0.330251 | 0.709985 | 0.702075 |

## Gates

{
  "augmentation_penalty8": {
    "promoted": true,
    "paired_spell_deltas": {
      "J03WMX": -0.00022193826318522847,
      "J03WN1": 0.0036787241429445117,
      "J03WOH": 0.001587724148415015,
      "J03WOY": 0.00965871609835689,
      "J03WPY": 0.003268297228421202
    },
    "paired_macro_deltas": {
      "J03WMX": 0.0023127285947391885,
      "J03WN1": 0.0025130177800606335,
      "J03WOH": -0.0017340576715769718,
      "J03WOY": -0.0012284997026200672,
      "J03WPY": -0.004398661314549468
    },
    "median_paired_spell_delta": 0.003268297228421202,
    "median_paired_macro_delta": -0.0012284997026200672,
    "matches_improved": 4,
    "primary_corrupted_spell_deltas": {
      "J03WMX": 0.0019573924291301226,
      "J03WN1": 0.0076859846144252675,
      "J03WOH": -0.0021164459962100257,
      "J03WOY": 0.00784019477507153,
      "J03WPY": 0.000655162852059521
    },
    "primary_median_delta": 0.0019573924291301226
  },
  "penalty16": {
    "promoted": true,
    "paired_spell_deltas": {
      "J03WMX": 0.010056145887024415,
      "J03WN1": -0.004355378129752785,
      "J03WOH": 0.029795910809050974,
      "J03WOY": 0.02553331089575983,
      "J03WPY": -0.011780114797252161
    },
    "paired_macro_deltas": {
      "J03WMX": 0.006132432243620589,
      "J03WN1": 0.002911878637101184,
      "J03WOH": 0.00878120529098314,
      "J03WOY": 0.009536229165395538,
      "J03WPY": 0.002286797387688666
    },
    "median_paired_spell_delta": 0.010056145887024415,
    "median_paired_macro_delta": 0.006132432243620589,
    "matches_improved": 3,
    "primary_corrupted_spell_deltas": {
      "J03WMX": 0.01853377005585105,
      "J03WN1": 0.003039235326102452,
      "J03WOH": 0.018345271025298093,
      "J03WOY": 0.017997698823072783,
      "J03WPY": -0.0048550871601720225
    },
    "primary_median_delta": 0.017997698823072783
  }
}

23 existing tests pass plus ten cache consistency audits. Sealed matches untouched. No combined augmentation+penalty16 experiment, no new target prediction export. Stop after this report.

## Decisions and failure log

Promote penalty16 independently; production selection.json now uses16. Retain augmentation+penalty8 as an independently passing branch; no augmentation+16 evaluation or deployment. Existing target CSV/model completion record still describes the previous penalty8 artifact; no new target inference was run.

Original corruption had mean440.6 spurious and324.2 missed spells atIoU.5; target-like has217.0 spurious and336.0 missed. Reduced fragmentation supports the spellF1 rise despite additional missed spells; macroF1 falls as long missing intervals erase more frames. This comparison changes multiple properties and does not establish causality.

Reporting initially failed to serialize a numpy int64 match count; converted to Python int and reran report only. No training rerun. No experimental variant was rejected: both pass; per-match regressions remain visible.
