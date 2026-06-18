# UlamGym Nano v0.1

A compact public RLVR environment where teams can compete to improve models on
verifier-backed math tasks.

This repo is the public-facing, lightweight version of the broader UlamGym
architecture. It keeps the same core shape:

```text
public prompt row -> model completion -> verifier manifest -> reward vector -> leaderboard
```

It is intentionally compact, transparent, dependency-light, and easy to run.
You can add your own tasks later without changing the package API.

## What this is

- A public RLVR scoring harness for math/reasoning tasks.
- A local verifier-backed competition starter kit.
- A GitHub repo template you can initialize and publish.
- A simple interface for teams to submit JSONL completions and compare scores.

## What this is not

- Not a hidden benchmark by itself.
- Not a private Ulam task dump.
- Not a Lean/mathlib production verifier.
- Not a trainer; it provides the reward function and evaluation loop.

For official public competitions, use this repo for prompts, docs, SDK, local
samples, and leaderboard tooling. Keep official hidden verifier manifests in a
hosted scorer or private storage until the challenge is over.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

make test
make smoke
```

Inspect the sample catalog:

```bash
ulamgym-nano catalog --task-dir data/sample_tasks
```

Score good sample submissions:

```bash
ulamgym-nano score \
  --task-dir data/sample_tasks \
  --submissions data/sample_tasks/submissions_good.jsonl \
  --out runs/good_scores.jsonl
```

Create a leaderboard:

```bash
ulamgym-nano leaderboard \
  --scores runs/good_scores.jsonl \
  --task-dir data/sample_tasks \
  --out leaderboards/sample.md
```

For competitions, pass `--task-dir` or `--total-tasks` to the leaderboard command so skipped tasks count as zero rather than improving a team's average by omission.

Serve the verifier locally:

```bash
ulamgym-nano serve --task-dir data/sample_tasks --host 0.0.0.0 --port 8000
```

Then call:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/catalog
```

## Docker

Build and run:

```bash
docker build -t ulamgym-nano:0.1 .
docker run --rm -p 8000:8000 ulamgym-nano:0.1
```

Or:

```bash
docker compose up --build
```

## Repository layout

```text
src/ulamgym_nano/        package code
  schema.py               public prompt, verifier, submission, score schemas
  verifiers.py            exact/numeric/multiple-choice/json verifiers
  rlvr.py                 RLVR scorer + reward_fn adapter
  env.py                  tiny reset/step environment wrapper
  server.py               dependency-free HTTP verifier service
  cli.py                  command-line interface
  leaderboard.py          score aggregation

data/sample_tasks/        transparent sample task pack
examples/                 reward_fn and agent examples
docs/                     schema, competition, challenge rules, and task-adding guides
tests/                    dependency-free tests
private/                  git-ignored private challenge material
```

## Task-pack format

A public task pack has two files:

```text
public_prompts.jsonl       agent-visible task rows
verifier_manifest.jsonl    verifier rows; sample packs may include this publicly
```

For a real challenge, keep `verifier_manifest.jsonl` private or hosted.

### Prompt row

```json
{
  "schema_version": "ulamgym.nano.prompt.v1",
  "task_id": "nano_exact_001",
  "env": "exact_answer",
  "domain": "arithmetic",
  "strictness": "strict",
  "prompt": "Compute 7 * 8.",
  "answer_format": "Return JSON: {\"answer\": \"...\"}",
  "metadata": {
    "source_visibility": "generated_public_sample",
    "contamination_risk": "high_public_sample",
    "estimated_human_minutes": 1,
    "skill_tags": ["arithmetic", "exact_answer"]
  }
}
```

### Verifier row

```json
{
  "schema_version": "ulamgym.nano.verifier.v1",
  "task_id": "nano_exact_001",
  "verifier": {
    "kind": "exact_answer",
    "answers": ["56"],
    "normalization": "number"
  }
}
```

### Submission row

```json
{
  "team": "baseline",
  "model": "manual",
  "task_id": "nano_exact_001",
  "completion": "{\"answer\": \"56\"}"
}
```

## RLVR reward function

```python
from ulamgym_nano import RLVRScorer

scorer = RLVRScorer.from_task_dir("data/sample_tasks")

# task IDs and completions from your rollout worker
rewards = scorer.reward_fn(
    ["nano_exact_001", "nano_roots_001"],
    ['{"answer":"56"}', '{"answer":[2,3]}'],
)
```

The scalar reward defaults to strict verified reward:

```text
1.0 if verifier accepts
0.0 otherwise
```

The full score row also includes a reward vector:

```json
{
  "strict": 1.0,
  "dense": 0.0,
  "integrity": 1.0,
  "efficiency": 0.0,
  "expert": 0.0
}
```

## Adding your tasks later

Create a new task interactively:

```bash
ulamgym-nano init-task \
  --task-dir data/my_public_pack \
  --task-id my_exact_001 \
  --env exact_answer \
  --domain number_theory \
  --prompt "What is the largest prime factor of 91?" \
  --answer-format 'Return JSON: {"answer": "..."}' \
  --answers 13 \
  --normalization number \
  --skill-tags number_theory exact_answer
```

Validate:

```bash
ulamgym-nano validate --task-dir data/my_public_pack
```

See `docs/ADDING_TASKS.md` for task design guidance.

## Public competition pattern

For an open local challenge:

```text
1. Commit public prompts and public verifier manifests.
2. Teams run local scoring.
3. Teams submit score JSONL or leaderboard PRs.
```

For a harder-to-game official challenge:

```text
1. Commit public prompts only.
2. Keep hidden verifier manifests on a hosted scorer.
3. Teams submit completions to the hosted endpoint.
4. Publish aggregate scorecards.
```

## Initialize GitHub repo

```bash
git init
git add .
git commit -m "Initialize UlamGym Nano v0.1"
git branch -M main
git remote add origin git@github.com:<ORG>/ulamgym-nano.git
git push -u origin main
```

## Current caveat

The included task pack is deliberately tiny and transparent. It proves the
public RLVR harness works. It is not meant to be a hidden benchmark. Replace or
extend `data/sample_tasks/` when you provide the actual public challenge tasks.
