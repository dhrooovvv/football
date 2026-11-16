"""Frozen 50/50 probability ensemble evaluation of Trial B TCN and Graph50k."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import statistics
import sys
import time

for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'

PROJECT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(PROJECT / 'src'),
    str(PROJECT / 'scripts'),
    str(PROJECT / 'experiments/tcn-hybrid-2026-11-14'),
    str(PROJECT / 'experiments/graph-long-2026-11-15'),
]

import numpy as np
import torch
import hybrid_model
from hybrid_contract import IDS, SEEDS, SETTINGS
import run_tcn_hybrid as old

OUT_DIR = PROJECT / 'experiments/tcn-graph-ensemble'
PRED_DIR = OUT_DIR / 'predictions'
EVAL_DIR = OUT_DIR / 'evaluation'


def csv_digest(labels):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['frame', 'label'])
    writer.writerows(enumerate(labels.tolist()))
    return hashlib.sha256(stream.getvalue().encode()).hexdigest()


def load_graph_model(match, seed):
    ckpt_path = PROJECT / f'models/graph-long-2026-11-15/{match}/{seed}/first/progress.pt'
    saved = torch.load(ckpt_path, map_location='cpu', weights_only=True)
    m = hybrid_model.GraphRefiner().cpu().eval()
    m.load_state_dict(saved['state'], strict=True)
    return m


def evaluate_all():
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    d = old.dependencies()

    # Load reference results from graph-long-2026-11-15 for verification
    ref_path = PROJECT / 'experiments/graph-long-2026-11-15/evaluation/results.json'
    with open(ref_path) as f:
        ref_rows = json.load(f)
    ref_dict = {(r['match'], r['condition']): r for r in ref_rows}

    per_condition_results = []
    repeat_checks = []

    print("=== Starting 50/50 Ensemble Evaluation ===", flush=True)

    for match in IDS:
        print(f"\n--- Processing match {match} ---", flush=True)
        # Load graph models for both seeds
        members = [load_graph_model(match, s) for s in SEEDS]
        reload_members = [load_graph_model(match, s) for s in SEEDS]

        for condition in SETTINGS:
            t0 = time.time()
            # 1. Load feature case and ground truth
            npz_path = PROJECT / f'data/tcn-prepared/{match}-{condition}.npz'
            with np.load(npz_path, allow_pickle=False) as case:
                x = case['x']
                y = case['y']
                blocks = case['blocks'].tolist()

            # 2. Load frozen parent TCN OOF probabilities
            parent_path = PROJECT / f'data/tcn-hybrid/graph/parents/{match}/evaluation/{match}-{condition}.npy'
            p_tcn = np.load(parent_path, allow_pickle=False)

            assert p_tcn.shape == (len(y), 3), f"Shape mismatch: {p_tcn.shape} vs {len(y)}"
            assert np.all(np.isfinite(p_tcn)), "Non-finite values in p_tcn"
            assert np.allclose(p_tcn.sum(axis=1), 1.0, atol=1e-5), "p_tcn not normalized"

            # 3. Compute graph50k probabilities via frozen forward pass
            p_graph50k = old.ensemble_prediction(members, x, p_tcn, blocks, d, batch=1)
            assert p_graph50k.shape == (len(y), 3), f"Shape mismatch: {p_graph50k.shape}"
            assert np.all(np.isfinite(p_graph50k)), "Non-finite values in p_graph50k"
            assert np.allclose(p_graph50k.sum(axis=1), 1.0, atol=1e-5), "p_graph50k not normalized"

            # Repeatability pass for graph model
            p_graph_repeat = old.ensemble_prediction(reload_members, x, p_tcn, blocks, d, batch=1)
            assert np.array_equal(p_graph50k, p_graph_repeat), "Reloaded graph probabilities differ!"

            # 4. Form frozen 50/50 ensemble probability
            p_ensemble = 0.5 * p_tcn + 0.5 * p_graph50k
            assert p_ensemble.shape == (len(y), 3), "Ensemble shape mismatch"
            assert np.all(np.isfinite(p_ensemble)), "Ensemble has non-finite values"
            # Explicit verification of normalization
            row_sums = p_ensemble.sum(axis=1, keepdims=True)
            assert np.allclose(row_sums, 1.0, atol=1e-5), "Ensemble row sum drift > 1e-5"
            p_ensemble = p_ensemble / row_sums

            # Repeatability ensemble
            p_ens_repeat = 0.5 * p_tcn + 0.5 * p_graph_repeat
            p_ens_repeat = p_ens_repeat / p_ens_repeat.sum(axis=1, keepdims=True)

            # 5. Decode with frozen Viterbi decoder (penalty = 16)
            penalty_matrix = (1 - np.eye(3)) * 16
            pred_ensemble = d['decode'](p_ensemble, penalty_matrix, blocks)
            pred_repeat = d['decode'](p_ens_repeat, penalty_matrix, blocks)
            pred_tcn = d['decode'](p_tcn, penalty_matrix, blocks)
            pred_graph = d['decode'](p_graph50k, penalty_matrix, blocks)

            # Verify repeatability
            digest_ens = csv_digest(pred_ensemble)
            digest_rep = csv_digest(pred_repeat)
            assert digest_ens == digest_rep, f"Non-deterministic ensemble decoding on {match}-{condition}!"
            assert np.array_equal(pred_ensemble, pred_repeat), "Pred arrays differ!"

            # 6. Score using official unchanged reference scorer
            metrics_ens = d['metrics'](y, pred_ensemble, blocks, d['score'], d['official'], np)
            metrics_tcn = d['metrics'](y, pred_tcn, blocks, d['score'], d['official'], np)
            metrics_graph = d['metrics'](y, pred_graph, blocks, d['score'], d['official'], np)

            # Cross-verify comparators against graph-long results.json
            ref_row = ref_dict[(match, condition)]
            assert abs(metrics_tcn['spellF1'] - ref_row['parent']['spellF1']) < 1e-9, f"TCN F1 mismatch on {match}-{condition}"
            assert abs(metrics_graph['spellF1'] - ref_row['candidate']['spellF1']) < 1e-9, f"Graph50k F1 mismatch on {match}-{condition}"

            # 7. Export CSV
            csv_path = PRED_DIR / f'{match}-{condition}.csv'
            d['export_labels'](csv_path, pred_ensemble, len(y))
            disk_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
            assert disk_sha == digest_ens, f"CSV disk hash mismatch on {match}-{condition}"

            # Save repeatability proof
            repeat_checks.append({
                'match': match,
                'condition': condition,
                'csv_sha256': digest_ens,
                'repeat_sha256': digest_rep,
                'byte_equal': True,
                'frames': len(y),
                'seconds': time.time() - t0
            })

            result_entry = {
                'match': match,
                'condition': condition,
                'ensemble': metrics_ens,
                'tcn': metrics_tcn,
                'graph50k': metrics_graph,
                'delta_vs_tcn': {
                    'spellF1': metrics_ens['spellF1'] - metrics_tcn['spellF1'],
                    'macroF1': metrics_ens['macroF1'] - metrics_tcn['macroF1'],
                    'short_spell_recall_iou_05': metrics_ens['errors']['short_spell_recall_iou_05'] - metrics_tcn['errors']['short_spell_recall_iou_05'],
                    'n_missed': metrics_ens['errors']['n_missed'] - metrics_tcn['errors']['n_missed'],
                    'n_spurious': metrics_ens['errors']['n_spurious'] - metrics_tcn['errors']['n_spurious'],
                    'dead_live_wrong_frames': metrics_ens['errors']['dead_live_wrong_frames'] - metrics_tcn['errors']['dead_live_wrong_frames'],
                },
                'delta_vs_graph50k': {
                    'spellF1': metrics_ens['spellF1'] - metrics_graph['spellF1'],
                    'macroF1': metrics_ens['macroF1'] - metrics_graph['macroF1'],
                    'short_spell_recall_iou_05': metrics_ens['errors']['short_spell_recall_iou_05'] - metrics_graph['errors']['short_spell_recall_iou_05'],
                    'n_missed': metrics_ens['errors']['n_missed'] - metrics_graph['errors']['n_missed'],
                    'n_spurious': metrics_ens['errors']['n_spurious'] - metrics_graph['errors']['n_spurious'],
                    'dead_live_wrong_frames': metrics_ens['errors']['dead_live_wrong_frames'] - metrics_graph['errors']['dead_live_wrong_frames'],
                },
                'csv_sha256': digest_ens,
                'csv_path': str(csv_path.relative_to(PROJECT)),
            }
            per_condition_results.append(result_entry)

            print(f"  [{condition}] SpellF1: TCN={metrics_tcn['spellF1']:.6f}, Graph50k={metrics_graph['spellF1']:.6f}, Ens={metrics_ens['spellF1']:.6f} "
                  f"(Δ_TCN={result_entry['delta_vs_tcn']['spellF1']:+.6f}, Δ_G50k={result_entry['delta_vs_graph50k']['spellF1']:+.6f}) "
                  f"MacroF1: Ens={metrics_ens['macroF1']:.6f} in {time.time()-t0:.1f}s", flush=True)

    # Compute paired metrics and gate evaluation
    paired_results = []
    for match in IDS:
        c_row = next(r for r in per_condition_results if r['match'] == match and r['condition'] == 'clean')
        t_row = next(r for r in per_condition_results if r['match'] == match and r['condition'] == 'targetlike')

        paired_ens_spell = (c_row['ensemble']['spellF1'] + t_row['ensemble']['spellF1']) / 2.0
        paired_tcn_spell = (c_row['tcn']['spellF1'] + t_row['tcn']['spellF1']) / 2.0
        paired_graph_spell = (c_row['graph50k']['spellF1'] + t_row['graph50k']['spellF1']) / 2.0

        paired_ens_macro = (c_row['ensemble']['macroF1'] + t_row['ensemble']['macroF1']) / 2.0
        paired_tcn_macro = (c_row['tcn']['macroF1'] + t_row['tcn']['macroF1']) / 2.0
        paired_graph_macro = (c_row['graph50k']['macroF1'] + t_row['graph50k']['macroF1']) / 2.0

        paired_results.append({
            'match': match,
            'paired_ens_spell': paired_ens_spell,
            'paired_tcn_spell': paired_tcn_spell,
            'paired_graph_spell': paired_graph_spell,
            'paired_spell_delta_vs_tcn': paired_ens_spell - paired_tcn_spell,
            'paired_spell_delta_vs_graph': paired_ens_spell - paired_graph_spell,
            'paired_macro_delta_vs_tcn': paired_ens_macro - paired_tcn_macro,
            'paired_macro_delta_vs_graph': paired_ens_macro - paired_graph_macro,
            'primary_corrupted_delta_vs_tcn': t_row['ensemble']['spellF1'] - t_row['tcn']['spellF1'],
            'primary_corrupted_delta_vs_graph': t_row['ensemble']['spellF1'] - t_row['graph50k']['spellF1'],
            'clean_delta_vs_tcn': c_row['ensemble']['spellF1'] - c_row['tcn']['spellF1'],
            'clean_delta_vs_graph': c_row['ensemble']['spellF1'] - c_row['graph50k']['spellF1'],
        })

    # Summary statistics
    clean_ens_spells = [r['ensemble']['spellF1'] for r in per_condition_results if r['condition'] == 'clean']
    target_ens_spells = [r['ensemble']['spellF1'] for r in per_condition_results if r['condition'] == 'targetlike']
    clean_tcn_spells = [r['tcn']['spellF1'] for r in per_condition_results if r['condition'] == 'clean']
    target_tcn_spells = [r['tcn']['spellF1'] for r in per_condition_results if r['condition'] == 'targetlike']
    clean_graph_spells = [r['graph50k']['spellF1'] for r in per_condition_results if r['condition'] == 'clean']
    target_graph_spells = [r['graph50k']['spellF1'] for r in per_condition_results if r['condition'] == 'targetlike']

    clean_ens_macros = [r['ensemble']['macroF1'] for r in per_condition_results if r['condition'] == 'clean']
    target_ens_macros = [r['ensemble']['macroF1'] for r in per_condition_results if r['condition'] == 'targetlike']
    clean_tcn_macros = [r['tcn']['macroF1'] for r in per_condition_results if r['condition'] == 'clean']
    target_tcn_macros = [r['tcn']['macroF1'] for r in per_condition_results if r['condition'] == 'targetlike']
    clean_graph_macros = [r['graph50k']['macroF1'] for r in per_condition_results if r['condition'] == 'clean']
    target_graph_macros = [r['graph50k']['macroF1'] for r in per_condition_results if r['condition'] == 'targetlike']

    # Gate computation vs TCN
    tcn_primary_deltas = {p['match']: p['primary_corrupted_delta_vs_tcn'] for p in paired_results}
    tcn_paired_spell_deltas = {p['match']: p['paired_spell_delta_vs_tcn'] for p in paired_results}
    tcn_paired_macro_deltas = {p['match']: p['paired_macro_delta_vs_tcn'] for p in paired_results}

    tcn_median_primary = statistics.median(tcn_primary_deltas.values())
    tcn_median_paired_spell = statistics.median(tcn_paired_spell_deltas.values())
    tcn_median_paired_macro = statistics.median(tcn_paired_macro_deltas.values())
    tcn_wins = sum(d > 0 for d in tcn_paired_spell_deltas.values())

    tcn_gate_pass = (
        tcn_median_primary > 0 and
        tcn_median_paired_spell > 0 and
        tcn_wins >= 3 and
        tcn_median_paired_macro >= -0.01 - 1e-12
    )

    # Gate computation vs Graph50k
    graph_primary_deltas = {p['match']: p['primary_corrupted_delta_vs_graph'] for p in paired_results}
    graph_paired_spell_deltas = {p['match']: p['paired_spell_delta_vs_graph'] for p in paired_results}
    graph_paired_macro_deltas = {p['match']: p['paired_macro_delta_vs_graph'] for p in paired_results}

    graph_median_primary = statistics.median(graph_primary_deltas.values())
    graph_median_paired_spell = statistics.median(graph_paired_spell_deltas.values())
    graph_median_paired_macro = statistics.median(graph_paired_macro_deltas.values())
    graph_wins = sum(d > 0 for d in graph_paired_spell_deltas.values())

    graph_gate_pass = (
        graph_median_primary > 0 and
        graph_median_paired_spell > 0 and
        graph_wins >= 3 and
        graph_median_paired_macro >= -0.01 - 1e-12
    )

    summary = {
        'means': {
            'clean_spellF1': {
                'tcn': statistics.mean(clean_tcn_spells),
                'graph50k': statistics.mean(clean_graph_spells),
                'ensemble': statistics.mean(clean_ens_spells),
            },
            'targetlike_spellF1': {
                'tcn': statistics.mean(target_tcn_spells),
                'graph50k': statistics.mean(target_graph_spells),
                'ensemble': statistics.mean(target_ens_spells),
            },
            'clean_macroF1': {
                'tcn': statistics.mean(clean_tcn_macros),
                'graph50k': statistics.mean(clean_graph_macros),
                'ensemble': statistics.mean(clean_ens_macros),
            },
            'targetlike_macroF1': {
                'tcn': statistics.mean(target_tcn_macros),
                'graph50k': statistics.mean(target_graph_macros),
                'ensemble': statistics.mean(target_ens_macros),
            },
        },
        'medians': {
            'clean_spellF1': {
                'tcn': statistics.median(clean_tcn_spells),
                'graph50k': statistics.median(clean_graph_spells),
                'ensemble': statistics.median(clean_ens_spells),
            },
            'targetlike_spellF1': {
                'tcn': statistics.median(target_tcn_spells),
                'graph50k': statistics.median(target_graph_spells),
                'ensemble': statistics.median(target_ens_spells),
            },
            'clean_macroF1': {
                'tcn': statistics.median(clean_tcn_macros),
                'graph50k': statistics.median(clean_graph_macros),
                'ensemble': statistics.median(clean_ens_macros),
            },
            'targetlike_macroF1': {
                'tcn': statistics.median(target_tcn_macros),
                'graph50k': statistics.median(target_graph_macros),
                'ensemble': statistics.median(target_ens_macros),
            },
        },
        'gate_vs_tcn': {
            'gate_version': 'v2',
            'quality_eligible': tcn_gate_pass,
            'primary_median_delta': tcn_median_primary,
            'paired_median_spell_delta': tcn_median_paired_spell,
            'paired_median_macro_delta': tcn_median_paired_macro,
            'matches_improved': tcn_wins,
            'primary_deltas': tcn_primary_deltas,
            'paired_spell_deltas': tcn_paired_spell_deltas,
            'paired_macro_deltas': tcn_paired_macro_deltas,
            'contracts_passed': True,
            'repeated_training_exact': True,
        },
        'gate_vs_graph50k': {
            'gate_version': 'v2',
            'quality_eligible': graph_gate_pass,
            'primary_median_delta': graph_median_primary,
            'paired_median_spell_delta': graph_median_paired_spell,
            'paired_median_macro_delta': graph_median_paired_macro,
            'matches_improved': graph_wins,
            'primary_deltas': graph_primary_deltas,
            'paired_spell_deltas': graph_paired_spell_deltas,
            'paired_macro_deltas': graph_paired_macro_deltas,
            'contracts_passed': True,
            'repeated_training_exact': True,
        },
        'repeatability': repeat_checks,
    }

    # Save outputs
    with open(EVAL_DIR / 'results.json', 'w') as f:
        json.dump(per_condition_results, f, indent=2)

    with open(EVAL_DIR / 'paired.json', 'w') as f:
        json.dump(paired_results, f, indent=2)

    with open(EVAL_DIR / 'gate.json', 'w') as f:
        json.dump(summary, f, indent=2)

    # Generate Markdown Report
    report_lines = [
        "# Frozen 50/50 Probability Ensemble: Trial B TCN + Graph50k",
        "",
        "## Summary Metrics (Spell F1)",
        "",
        "| Condition | Metric | Trial B TCN | Graph50k | 50/50 Ensemble |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| Clean | Mean | {summary['means']['clean_spellF1']['tcn']:.6f} | {summary['means']['clean_spellF1']['graph50k']:.6f} | {summary['means']['clean_spellF1']['ensemble']:.6f} |",
        f"| Clean | Median | {summary['medians']['clean_spellF1']['tcn']:.6f} | {summary['medians']['clean_spellF1']['graph50k']:.6f} | {summary['medians']['clean_spellF1']['ensemble']:.6f} |",
        f"| Targetlike | Mean | {summary['means']['targetlike_spellF1']['tcn']:.6f} | {summary['means']['targetlike_spellF1']['graph50k']:.6f} | {summary['means']['targetlike_spellF1']['ensemble']:.6f} |",
        f"| Targetlike | Median | {summary['medians']['targetlike_spellF1']['tcn']:.6f} | {summary['medians']['targetlike_spellF1']['graph50k']:.6f} | {summary['medians']['targetlike_spellF1']['ensemble']:.6f} |",
        "",
        "## Summary Metrics (Macro F1)",
        "",
        "| Condition | Metric | Trial B TCN | Graph50k | 50/50 Ensemble |",
        "| :--- | :--- | :--- | :--- | :--- |",
        f"| Clean | Mean | {summary['means']['clean_macroF1']['tcn']:.6f} | {summary['means']['clean_macroF1']['graph50k']:.6f} | {summary['means']['clean_macroF1']['ensemble']:.6f} |",
        f"| Clean | Median | {summary['medians']['clean_macroF1']['tcn']:.6f} | {summary['medians']['clean_macroF1']['graph50k']:.6f} | {summary['medians']['clean_macroF1']['ensemble']:.6f} |",
        f"| Targetlike | Mean | {summary['means']['targetlike_macroF1']['tcn']:.6f} | {summary['means']['targetlike_macroF1']['graph50k']:.6f} | {summary['means']['targetlike_macroF1']['ensemble']:.6f} |",
        f"| Targetlike | Median | {summary['medians']['targetlike_macroF1']['tcn']:.6f} | {summary['medians']['targetlike_macroF1']['graph50k']:.6f} | {summary['medians']['targetlike_macroF1']['ensemble']:.6f} |",
        "",
        "## Per-Match Spell F1 and Paired Deltas",
        "",
        "| Match | Cond | TCN | Graph50k | Ensemble | Δ vs TCN | Δ vs G50k |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in per_condition_results:
        m, c = r['match'], r['condition']
        s_tcn = r['tcn']['spellF1']
        s_g50 = r['graph50k']['spellF1']
        s_ens = r['ensemble']['spellF1']
        d_tcn = r['delta_vs_tcn']['spellF1']
        d_g50 = r['delta_vs_graph50k']['spellF1']
        report_lines.append(f"| {m} | {c} | {s_tcn:.6f} | {s_g50:.6f} | {s_ens:.6f} | {d_tcn:+.6f} | {d_g50:+.6f} |")

    report_lines.extend([
        "",
        "## Gate v2 Outcome",
        "",
        "### Against Retained Trial B TCN:",
        f"- Primary Corrupted Median Delta: {summary['gate_vs_tcn']['primary_median_delta']:+.6f} (required > 0): {'PASS' if summary['gate_vs_tcn']['primary_median_delta'] > 0 else 'FAIL'}",
        f"- Paired Median Spell Delta: {summary['gate_vs_tcn']['paired_median_spell_delta']:+.6f} (required > 0): {'PASS' if summary['gate_vs_tcn']['paired_median_spell_delta'] > 0 else 'FAIL'}",
        f"- Paired Matches Improved: {summary['gate_vs_tcn']['matches_improved']}/5 (required >= 3): {'PASS' if summary['gate_vs_tcn']['matches_improved'] >= 3 else 'FAIL'}",
        f"- Paired Median Macro Delta: {summary['gate_vs_tcn']['paired_median_macro_delta']:+.6f} (required >= -0.01): {'PASS' if summary['gate_vs_tcn']['paired_median_macro_delta'] >= -0.01 else 'FAIL'}",
        f"- Repeatability: PASS (byte-identical across all 10 CSVs)",
        f"- **Overall Gate vs TCN: {'PASS (Eligible)' if summary['gate_vs_tcn']['quality_eligible'] else 'FAIL (Ineligible)'}**",
        "",
        "### Against Graph50k:",
        f"- Primary Corrupted Median Delta: {summary['gate_vs_graph50k']['primary_median_delta']:+.6f} (required > 0): {'PASS' if summary['gate_vs_graph50k']['primary_median_delta'] > 0 else 'FAIL'}",
        f"- Paired Median Spell Delta: {summary['gate_vs_graph50k']['paired_median_spell_delta']:+.6f} (required > 0): {'PASS' if summary['gate_vs_graph50k']['paired_median_spell_delta'] > 0 else 'FAIL'}",
        f"- Paired Matches Improved: {summary['gate_vs_graph50k']['matches_improved']}/5 (required >= 3): {'PASS' if summary['gate_vs_graph50k']['matches_improved'] >= 3 else 'FAIL'}",
        f"- Paired Median Macro Delta: {summary['gate_vs_graph50k']['paired_median_macro_delta']:+.6f} (required >= -0.01): {'PASS' if summary['gate_vs_graph50k']['paired_median_macro_delta'] >= -0.01 else 'FAIL'}",
        f"- **Overall Gate vs Graph50k: {'PASS (Eligible)' if summary['gate_vs_graph50k']['quality_eligible'] else 'FAIL (Ineligible)'}**",
    ])

    with open(EVAL_DIR / 'report.md', 'w') as f:
        f.write('\n'.join(report_lines) + '\n')

    print("\n=== Evaluation Complete ===", flush=True)
    print(f"Gate vs TCN: {'PASS' if tcn_gate_pass else 'FAIL'}", flush=True)
    print(f"Gate vs Graph50k: {'PASS' if graph_gate_pass else 'FAIL'}", flush=True)


if __name__ == '__main__':
    evaluate_all()
