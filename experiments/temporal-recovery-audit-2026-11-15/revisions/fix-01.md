# Fix 01 — November 15, 2026

User-run initial attempt stopped at synthetic checks: eight tests, three passed, five errors. All errors were numeric internal codes passed to the official string-label converter. No model inference/scoring or graph checkpoint extraction started. Official scorer unchanged.

Correct diagnostic adapter to accept only validated integer0..3 codes directly, otherwise delegate H/A/D/X parsing to the unchanged official converter. Add representation-equivalence and invalid-code contracts: ten current tests. Keep all original scientific rules, membership, signals and freeze unchanged. Preserve original protocol and original source lock in v1-inputs.json (old code preserved in Git commit4e8c486). Initial registration ddf1b7a987107693b3780cd3c3e18cf72a8563e167f1a38128887503cd0c15c9.

The reviewed failed checks.txt is preserved and pinned. New attempts use unique checks log paths; successful status binds the current registration and exact log bytes. No deletion, overwrite or weakened test/scoring requirement. Resume output schema changes only for checks status; no numerical units or successful status exist from the failed attempt. User reruns the same command. Assistant performs no project imports/tests/compile/inference/scoring/training.

Original check log SHA256: c3af45aa309e13997ede4ae3986336df11996d6a49e494e858c2be4717f33900
