"""Pure metadata contract for the actual staged40k supervised fold checkpoints."""
import hashlib
import json
import math

IDS = ('J03WMX', 'J03WN1', 'J03WOH', 'J03WOY', 'J03WPY')
ARCHITECTURE = 'original_motion_tcn_geometric_pretraining_head_v1'
SCHEMA = 'original_encoded521_core9_observed_masked_ballXY_v1'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def expected_identity(match, signature, allowed_pff):
    require(match in IDS, 'Only original development folds are allowed')
    require(isinstance(signature, str) and bool(signature), 'Registration signature missing')
    return dict(signature=signature, arm='control', held_out=match,
                supervised_matches=['idsse-' + m for m in IDS if m != match],
                geometry_matches=[], allowed_pff=[str(v) for v in allowed_pff],
                total_steps=40000, stage_steps=20000, architecture=ARCHITECTURE,
                schema=SCHEMA, seed=20261106, pretext_seed=20968176,
                view_seed=20685348, window=250, halo=25, core=200, batch=8,
                optimizer='Adam', learning_rate=.001, gradient_clip=1.,
                supervised_gap_probability=.5,
                stage_boundary='reset_Adam_and_supervised_RNG_in_both_arms',
                pretext_target='clean_observed_cached_synthetic_hidden_ballXY',
                pretext_loss='mean_squared_XY_error_over_valid_batch_frames',
                pretext_sampler='uniform_match_then_uniform_eligible_start')


def validate_control(saved, match, signature, membership, record):
    """Reject another recipe/fold/incomplete fit before model state is loaded."""
    identity = expected_identity(match, signature, membership['pff_training'])
    require(saved['identity'] == identity, 'Checkpoint is not the registered40k control fold')
    require(saved['step'] == 40000 and saved['stage'] == 'stage2', 'Incomplete control checkpoint')
    require(record['registration'] == signature and record['arm'] == 'control'
            and record['architecture'] == ARCHITECTURE and record['parent'] == 'rotation20k'
            and record['training_steps'] == 40000 and record['stage_steps'] == 20000
            and record['training_matches'] == identity['supervised_matches']
            and record['geometry_matches'] == [] and record['repeated_training_exact'],
            'Archived fold recipe differs')
    require(len(saved['losses']) == 40000 and all(
        isinstance(v, (float, int)) and math.isfinite(v) for v in saved['losses']),
        'Invalid completed training loss evidence')
    require(hashlib.sha256(json.dumps(saved['losses']).encode()).hexdigest()
            == record['training_loss_sha256'], 'Loss evidence differs from archive')
    require(saved['target_counts'] == record['target_counts'] == {'stage1': 0, 'stage2': 0},
            'Reconstruction was used by the control')
    require(saved['coverage'] == record['coverage'] and saved['supervised_views'] == record['supervised_views'],
            'Sampling evidence differs from archive')
    for stage in ('stage1', 'stage2'):
        counts = saved['coverage'][stage]
        require(set(counts) == set(identity['supervised_matches'])
                and all(isinstance(v, int) and v > 0 for v in counts.values())
                and sum(counts.values()) == 160000, 'Invalid supervised sampling coverage')
        views = saved['supervised_views'][stage]
        require(set(views) == {'clean', 'gap'} and all(isinstance(v, int) and v > 0 for v in views.values())
                and sum(views.values()) == 160000, 'Invalid supervised gap-view coverage')
    require(saved['coverage']['stage1'] == saved['coverage']['stage2']
            and saved['supervised_views']['stage1'] == saved['supervised_views']['stage2'],
            'Registered sampler reset evidence differs')
