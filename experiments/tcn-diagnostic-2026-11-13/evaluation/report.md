# Frozen A/B possession diagnostic

All scores reproduce the archive. No training or model selection.

|Trial|Match|Setting|spellF1|macroF1|Missed at IoU .5|
|---|---|---|---:|---:|---:|
|b|J03WMX|clean|0.624036|0.932480|234|
|b|J03WMX|targetlike|0.483486|0.861490|301|
|b|J03WN1|clean|0.614756|0.905193|220|
|b|J03WN1|targetlike|0.452398|0.796590|303|
|b|J03WOH|clean|0.714674|0.941679|138|
|b|J03WOH|targetlike|0.543099|0.821960|211|
|b|J03WOY|clean|0.650614|0.922153|189|
|b|J03WOY|targetlike|0.516391|0.845931|250|
|b|J03WPY|clean|0.647843|0.932253|172|
|b|J03WPY|targetlike|0.553804|0.863932|213|
|a|J03WMX|clean|0.633636|0.933942|232|
|a|J03WMX|targetlike|0.519396|0.884808|285|
|a|J03WN1|clean|0.588800|0.899015|235|
|a|J03WN1|targetlike|0.443977|0.789555|308|
|a|J03WOH|clean|0.695979|0.937759|143|
|a|J03WOH|targetlike|0.551841|0.860079|207|
|a|J03WOY|clean|0.661614|0.918457|185|
|a|J03WOY|targetlike|0.514429|0.823786|250|
|a|J03WPY|clean|0.646277|0.932094|177|
|a|J03WPY|targetlike|0.537838|0.859285|218|

Conditional proposal and ranked associations:

```json
{
  "ranking": [
    {
      "category": "long_gap_without_argmax_match",
      "affected_spells": 535
    },
    {
      "category": "decoder_removed_support",
      "affected_spells": 265
    },
    {
      "category": "observed_wrong_team",
      "affected_spells": 250
    },
    {
      "category": "merged",
      "affected_spells": 110
    },
    {
      "category": "boundary_misalignment",
      "affected_spells": 44
    },
    {
      "category": "dead_live_confusion",
      "affected_spells": 38
    },
    {
      "category": "other",
      "affected_spells": 31
    },
    {
      "category": "fragmented",
      "affected_spells": 5
    }
  ],
  "per_match": {
    "J03WMX": {
      "decoder_removed_support": 74,
      "long_gap_without_argmax_match": 106,
      "observed_wrong_team": 64,
      "dead_live_confusion": 12,
      "merged": 33,
      "fragmented": 2,
      "boundary_misalignment": 4,
      "other": 6
    },
    "J03WN1": {
      "decoder_removed_support": 67,
      "long_gap_without_argmax_match": 125,
      "observed_wrong_team": 65,
      "dead_live_confusion": 5,
      "merged": 24,
      "fragmented": 1,
      "boundary_misalignment": 14,
      "other": 2
    },
    "J03WOH": {
      "decoder_removed_support": 45,
      "long_gap_without_argmax_match": 113,
      "observed_wrong_team": 29,
      "dead_live_confusion": 7,
      "merged": 7,
      "fragmented": 0,
      "boundary_misalignment": 6,
      "other": 4
    },
    "J03WOY": {
      "decoder_removed_support": 45,
      "long_gap_without_argmax_match": 101,
      "observed_wrong_team": 41,
      "dead_live_confusion": 6,
      "merged": 28,
      "fragmented": 1,
      "boundary_misalignment": 13,
      "other": 15
    },
    "J03WPY": {
      "decoder_removed_support": 34,
      "long_gap_without_argmax_match": 90,
      "observed_wrong_team": 51,
      "dead_live_confusion": 8,
      "merged": 18,
      "fragmented": 1,
      "boundary_misalignment": 7,
      "other": 4
    }
  },
  "leading_category_matches": 5,
  "conditional_proposal": "temporal context spanning long gaps",
  "experiment_authorized": false,
  "interpretation": "Priority-partitioned associations, not causal effects or recoverable spellF1. No proposal if the leader is tied, unsupported in three matches, or outside the registered branches. Stopped tracks need explicit reopening; any proposal needs review and a new protocol."
}
```

Detailed per-IoU precision/recall, duration/gap strata, overlapping associations, boundary shifts, dead/live quality and paired corruption losses are in results.json. Counts are not recoverable spellF1 gains. Argmax support is an association, not a causal decoder verdict. Target accuracy unknown. Stop for review; no intervention is authorized.
