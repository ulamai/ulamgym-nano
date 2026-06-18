# Challenge Rules Template

Use this file when turning UlamGym Nano into a public competition.

## Track type

Choose one:

- **Public-local track:** prompts and verifier manifests are public. Anyone can reproduce scores locally. This is good for demos and community contributions, but not hidden capability claims.
- **Hosted-hidden track:** prompts are public, verifier manifests stay private. Teams submit completions to a hosted scorer. This is the recommended format for serious leaderboards.

## Submission format

Teams submit JSONL rows:

```json
{"team":"team-name","model":"model-name","run_id":"run-001","task_id":"...","completion":"..."}
```

## Scoring

- Each task is worth at most 1.0.
- Skipped tasks count as 0.0.
- The primary metric is mean reward over the full task set.
- Secondary metrics: pass rate, coverage, task count, and verifier family breakdown.

Build the leaderboard with full-task normalization:

```bash
ulamgym-nano leaderboard \
  --scores runs/scores.jsonl \
  --task-dir data/challenge_pack \
  --out leaderboards/challenge.md
```

For hosted-hidden tracks, use:

```bash
ulamgym-nano leaderboard \
  --scores runs/hosted_scores.jsonl \
  --total-tasks <N> \
  --out leaderboards/challenge.md
```

## Allowed model behavior

Define whether teams may use:

- external tools
- retrieval/search
- code execution
- majority voting / pass@k
- fine-tuning on public dev tasks
- self-generated data

## Disallowed behavior

For hosted-hidden tracks, prohibit:

- probing the verifier with manual answer searches
- sharing leased hidden prompts outside the team
- using leaked verifier manifests or answer keys
- submitting another team's outputs
- exploiting server bugs or request-format bugs

## Reproducibility

Require teams to report:

- model name and version/checkpoint
- decoding settings
- tool-use settings
- number of attempts per task
- whether public dev tasks were used for tuning
- commit hash of any submitted code

## Release notes

When the challenge closes, publish:

- prompt pack version
- total task count
- verifier kinds
- scoring policy
- leaderboard
- known caveats
- whether verifier manifests remain hidden or are released for reproducibility
