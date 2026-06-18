"""Evaluate sample submissions and print score rows."""

import json

from ulamgym_nano import RLVRScorer
from ulamgym_nano.io import load_submissions

scorer = RLVRScorer.from_task_dir("data/sample_tasks")
submissions = load_submissions("data/sample_tasks/submissions_good.jsonl")
for result in scorer.score_submissions(submissions):
    print(json.dumps(result.to_dict(), ensure_ascii=False))
