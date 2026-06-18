# RLVR Integration

UlamGym Nano provides the reward side of RLVR:

```text
task_id + completion -> verifier -> scalar reward + reward vector
```

It does not train a model. Connect it to your PPO/GRPO/RLVR trainer as a reward
function.

## Python reward function

```python
from ulamgym_nano import RLVRScorer

scorer = RLVRScorer.from_task_dir("taskpacks/nano-sample-v0.2")

def reward_fn(task_ids, completions):
    return scorer.reward_fn(task_ids, completions)
```

## Batch scoring

```bash
ulamgym-nano score \
  --task-dir taskpacks/nano-sample-v0.2 \
  --submissions taskpacks/nano-sample-v0.2/submissions_good.jsonl \
  --out runs/scores.jsonl
```

## HTTP scoring

Run:

```bash
ulamgym-nano serve --task-dir taskpacks/nano-sample-v0.2 --port 8000
```

Score one completion:

```bash
curl -s http://localhost:8000/v1/verify \
  -H 'content-type: application/json' \
  -d '{"task_id":"nano_exact_001","completion":"{\"answer\":\"56\"}","team":"demo","model":"manual"}'
```

Batch score:

```bash
curl -s http://localhost:8000/v1/batch_verify \
  -H 'content-type: application/json' \
  -d '{"team":"demo","model":"manual","submissions":[{"task_id":"nano_exact_001","completion":"{\"answer\":\"56\"}"}]}'
```

## Reward semantics

For strict tasks:

```text
passed -> reward 1.0
failed -> reward 0.0
```

For future semi-strict tasks, the reward vector can carry dense or expert
components, but v0.2's bundled sample taskpack is strict deterministic-verifier only.
