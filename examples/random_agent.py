"""Tiny baseline agent that emits intentionally weak completions."""

import json
from pathlib import Path

from ulamgym_nano import RLVRScorer
from ulamgym_nano.io import write_jsonl

scorer = RLVRScorer.from_task_dir("data/sample_tasks")
rows = []
for task in scorer.prompt_rows():
    rows.append({
        "schema_version": "ulamgym.nano.submission.v1",
        "team": "random-baseline",
        "model": "constant-zero",
        "run_id": "demo",
        "task_id": task["task_id"],
        "completion": json.dumps({"answer": "0"}),
    })

out = Path("runs/random_agent_submissions.jsonl")
write_jsonl(out, rows)
print(f"wrote {out}")
