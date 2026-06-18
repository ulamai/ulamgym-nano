# UlamGym Nano Schema

UlamGym Nano uses a prompt/manifest split.

## Files

```text
public_prompts.jsonl
verifier_manifest.jsonl
submissions.jsonl
scores.jsonl
```

## Public prompt row

Required fields:

```json
{
  "schema_version": "ulamgym.nano.prompt.v1",
  "task_id": "unique_task_id",
  "env": "exact_answer",
  "domain": "arithmetic",
  "strictness": "strict",
  "max_steps": 1,
  "prompt": "Problem text shown to the agent.",
  "answer_format": "Return JSON: {\"answer\": \"...\"}",
  "metadata": {}
}
```

The prompt row is safe to show to agents and teams.

## Verifier row

```json
{
  "schema_version": "ulamgym.nano.verifier.v1",
  "task_id": "unique_task_id",
  "verifier": {
    "kind": "exact_answer",
    "answers": ["42"],
    "normalization": "number"
  }
}
```

For public sample packs, this can be committed. For official competitions, keep
this hidden or hosted.

## Submission row

```json
{
  "schema_version": "ulamgym.nano.submission.v1",
  "team": "my-team",
  "model": "my-model",
  "run_id": "run-001",
  "task_id": "unique_task_id",
  "completion": "{\"answer\": \"42\"}"
}
```

## Score row

```json
{
  "schema_version": "ulamgym.nano.score.v1",
  "team": "my-team",
  "model": "my-model",
  "run_id": "run-001",
  "task_id": "unique_task_id",
  "passed": true,
  "reward": 1.0,
  "reward_vector": {
    "strict": 1.0,
    "dense": 0.0,
    "integrity": 1.0,
    "efficiency": 0.0,
    "expert": 0.0
  },
  "strictness": "strict",
  "feedback": "Accepted.",
  "diagnostics": {}
}
```

## Supported verifier kinds in v0.1

### `exact_answer`

```json
{"kind":"exact_answer", "answers":["56"], "normalization":"number"}
```

Normalization modes:

- `string`
- `number`
- `set`
- `raw`
- `json`

### `numeric_interval`

```json
{"kind":"numeric_interval", "target":"1.4142", "tolerance":0.001}
```

### `multiple_choice`

```json
{"kind":"multiple_choice", "correct":"B", "choice_count":4}
```

### `json_fields`

```json
{
  "kind": "json_fields",
  "fields": {
    "x": {"answers": [2], "normalization": "number"},
    "y": {"answers": [3], "normalization": "number"}
  }
}
```
