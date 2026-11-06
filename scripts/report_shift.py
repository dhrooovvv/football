import json
from pathlib import Path
import numpy as np
p=Path('data/diagnostics-review');out=Path('experiments/diagnostics-review');t=json.loads((p/'target-shift.json').read_text());files=sorted(p.glob('J*-shift.json'));d=[json.loads(f.read_text()) for f in files]
lines=['# Label-free input shift','', 'Aggregate summaries only; target rows and empirical run lists stay private. Quantiles use all frames inside configured halves, including development unknown-label frames. Player corruption remains the original fixed burst model. Target-like ball masks bootstrap alternating empirical observed/missing runs within each half; intrinsic external gaps remain, so total missingness may exceed the target. This is a label-free stress model, not a claim of realistic conditional missingness.','', '| Feature | External mean finite fraction | Target finite fraction | External median (mean over matches) | Target median |','|---|---:|---:|---:|---:|']
for n,s in t['features'].items():
 ext=[z['clean'][n] for z in d];lines.append(f"| {n} | {np.mean([z['finite_fraction'] for z in ext]):.4f} | {s['finite_fraction']:.4f} | {np.mean([z['quantiles'][2] for z in ext]):.4f} | {s['quantiles'][2]:.4f} |")
g=np.array(t['missing_runs']);lines+=['',f"Target missing fraction: {t['missing_fraction']:.4f}; missing-run p50/p90/p99/max frames: {np.quantile(g,[.5,.9,.99,1]).tolist()}.",'','| Match | External clean missing-run quantiles | Target-like missing-run quantiles |','|---|---|---|']
for f,z in zip(files,d):lines.append(f"| {f.stem} | {z['missing_run_quantiles']} | {z['targetlike_missing_run_quantiles']} |")
(out/'input-shift.md').write_text('\n'.join(lines)+'\n')
