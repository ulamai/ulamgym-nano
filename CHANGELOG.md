# Changelog

## 0.2.0

Challenge-ready public skeleton.

- Added canonical `taskpacks/nano-sample-v0.2/` layout with metadata, task card, and taskpack license.
- Added `roadmap.md`, `SECURITY.md`, and `CITATION.cff`.
- Updated package version and Docker image examples to v0.2.
- Made full-task leaderboard normalization the CLI default.
- Added attempted-only leaderboard mode for local debugging.
- Added taskpack metadata, verifier-kind, verifier-field, empty-prompt, and answer-bearing prompt validation.
- Added per-verifier-family leaderboard metrics in JSON output.
- Kept `ulamgym-small` as a deprecated temporary CLI alias for v0.2 compatibility.

## 0.1.0

Initial public-facing release.

- Prompt/manifest task-pack format.
- Strict verifier-backed scoring for exact, interval, multiple-choice, and JSON-field tasks.
- RLVR reward function.
- Dependency-free local HTTP verifier.
- CLI for validation, scoring, prompts, leaderboards, and task initialization.
- Dockerfile and GitHub Actions CI.
- Transparent sample task pack.
