# Competition Mode

UlamGym Nano supports two public competition patterns.

## Pattern A: Fully public local challenge

Use this for hackathons and demos.

```text
repo includes public prompts + verifier manifest
teams score locally
leaderboard is reproducible but answers are public
```

Pros:

- anyone can run it
- no server cost
- transparent
- good for community contributions

Cons:

- not hidden
- not suitable for strong capability claims

## Pattern B: Hosted hidden-verifier challenge

Use this for serious competitions.

```text
repo includes public prompts only
hosted scorer stores verifier manifest
teams submit completions to /v1/verify or /v1/batch_verify
leaderboard uses hosted scores
```

Pros:

- harder to game
- task answers stay hidden during the challenge
- scoring can be rate-limited

Cons:

- requires server operation
- requires written challenge rules

## Recommended public release ladder

```text
v0.2: public repo + sample taskpack + docs + local scoring
v0.2: official public dev pack + hosted hidden test pack
v0.3: monthly public mini-challenge with frozen prompts and private scorer
```

## Team submission format

Teams submit JSONL:

```json
{"team":"team-name","model":"model-name","run_id":"run-001","task_id":"...","completion":"..."}
```

## Leaderboard policy

A public leaderboard should report:

- mean reward normalized by the full task count
- pass rate normalized by the full task count
- number of tasks attempted
- coverage percentage
- model name
- run ID
- whether the track was public-local or hosted-hidden

## Skipped tasks

For real competitions, skipped tasks should count as zero. Build leaderboards with:

```bash
ulamgym-nano leaderboard \
  --scores runs/scores.jsonl \
  --task-dir data/challenge_pack \
  --out leaderboards/challenge.md
```

Or pass `--total-tasks N` if the verifier is hosted and the public repo only contains prompts.
