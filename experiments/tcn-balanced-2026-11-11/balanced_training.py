"""Fixed equal-provider sampling; the frozen TCN, optimizer and budget are unchanged."""
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

sys.path.insert(0, str(Path("experiments/tcn-expanded-2026-11-10").resolve()))
from expanded_data import valid_windows
from expanded_training import write_checkpoint, confirm_repeat
sys.path.insert(0, str(Path("experiments/tcn-2026-11-10").resolve()))
from tcn_candidate import TCN, SEED, WINDOW, HALO, CORE

SAMPLER = "equal_provider_mass_then_uniform_valid_starts_v1"
PROVIDER_SEED = SEED + 131313


class ProviderSampler:
    """Each valid start has conditional probability 1 / its provider's total."""
    providers = ("idsse", "pff")

    def __init__(self, cases):
        if {case.provider for case in cases} != set(self.providers):
            raise ValueError("Exactly idsse and pff providers are required")
        if len({case.key for case in cases}) != len(cases):
            raise ValueError("Training case keys must be unique")
        records = valid_windows(cases, WINDOW)
        self.records = {
            provider: [record for record in records if cases[record[0]].provider == provider]
            for provider in self.providers
        }
        self.cumulative = {
            provider: np.cumsum([record[2] for record in rows], dtype=np.int64)
            for provider, rows in self.records.items()
        }
        if any(len(counts) == 0 or counts[-1] <= 0 for counts in self.cumulative.values()):
            raise ValueError("Each provider requires complete known-label windows")
        self.totals = {provider: int(counts[-1]) for provider, counts in self.cumulative.items()}

    def locate(self, provider, draw):
        """Decode every conditional integer draw exactly once, without rejection."""
        if provider not in self.totals:
            raise ValueError("Unknown provider")
        if isinstance(draw, (bool, np.bool_)) or not isinstance(draw, (int, np.integer)):
            raise ValueError("Window draw must be an integer")
        if not 0 <= draw < self.totals[provider]:
            raise ValueError("Window draw is outside provider support")
        cumulative = self.cumulative[provider]
        index = int(np.searchsorted(cumulative, draw, side="right"))
        match_index, first, _ = self.records[provider][index]
        offset = int(draw - (cumulative[index - 1] if index else 0))
        return match_index, first + offset

    def sample_batch(self, window_rng, provider_rng, size=8):
        choices = provider_rng.integers(0, 2, size=size)
        return [self.locate(self.providers[int(choice)],
                            int(window_rng.integers(0, self.totals[self.providers[int(choice)]])))
                for choice in choices]


def train_fit(cases, directory, signature, steps=20000, save_every=1000):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "progress.pt"
    identity = dict(signature=signature, matches=[case.key for case in cases], steps=steps,
                    seed=SEED, sampler=SAMPLER, provider_seed=PROVIDER_SEED)
    sampler = ProviderSampler(cases)
    torch.manual_seed(SEED)
    rng = np.random.default_rng(SEED)
    provider_rng = np.random.default_rng(PROVIDER_SEED)
    view_rng = np.random.default_rng(SEED + 424242)
    model = TCN().cpu()
    optimizer = torch.optim.Adam(model.parameters(), lr=.001)
    losses = []
    coverage = {case.key: {"clean": 0, "gap": 0} for case in cases}
    first_step = 0
    if path.exists():
        saved = torch.load(path, map_location="cpu", weights_only=True)
        if saved["identity"] != identity:
            raise RuntimeError("Checkpoint training identity differs from this run")
        model.load_state_dict(saved["state"])
        optimizer.load_state_dict(saved["optimizer"])
        rng.bit_generator.state = saved["window_rng"]
        provider_rng.bit_generator.state = saved["provider_rng"]
        view_rng.bit_generator.state = saved["view_rng"]
        torch.set_rng_state(saved["torch_rng"])
        losses = saved["losses"]
        coverage = saved["coverage"]
        first_step = saved["step"]
        if len(losses) != first_step or not 0 <= first_step <= steps:
            raise RuntimeError("Checkpoint step/loss mismatch")
        print(f"Resuming {directory} at update {first_step}", flush=True)
    model.train()
    for step in range(first_step, steps):
        batch_x, batch_y = [], []
        for match_index, start in sampler.sample_batch(rng, provider_rng, size=8):
            case = cases[match_index]
            use_gap = bool(view_rng.random() < .5)
            batch_x.append(case.read(np.arange(start, start + WINDOW), use_gap))
            batch_y.append(np.asarray(case.labels[start + HALO:start + HALO + CORE], dtype=np.int64))
            coverage[case.key]["gap" if use_gap else "clean"] += 1
        optimizer.zero_grad(set_to_none=True)
        logits = model(torch.from_numpy(np.stack(batch_x)))[:, HALO:HALO + CORE]
        loss = nn.functional.cross_entropy(logits.reshape(-1, 3), torch.from_numpy(np.stack(batch_y)).reshape(-1))
        if not torch.isfinite(loss):
            raise RuntimeError("Nonfinite training loss")
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.)
        optimizer.step()
        losses.append(float(loss.detach()))
        if (step + 1) % save_every == 0 or step + 1 == steps:
            payload = dict(identity=identity, step=step + 1, state=model.state_dict(),
                           optimizer=optimizer.state_dict(), window_rng=rng.bit_generator.state,
                           provider_rng=provider_rng.bit_generator.state,
                           view_rng=view_rng.bit_generator.state, torch_rng=torch.get_rng_state(),
                           losses=losses, coverage=coverage)
            write_checkpoint(path, payload)
            print(f"{directory.name}: update {step + 1}/{steps}, minibatch loss {losses[-1]:.5f}", flush=True)
    # Small synthetic runs can have fewer draws than cases; actual 20k fits must visit all.
    if steps >= 20000 and any(sum(counts.values()) == 0 for counts in coverage.values()):
        raise RuntimeError("A training match was never sampled")
    model.eval()
    return model, losses, coverage
