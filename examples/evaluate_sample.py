"""Evaluate sample submissions and print score rows."""

import json

from ulamgym_nano import RLVRScorer
from ulamgym_nano.io import load_submissions

scorer = RLVRScorer.from_task_dir("taskpacks/nano-sample-v0.2")
submissions = load_submissions("taskpacks/nano-sample-v0.2/submissions_good.jsonl")
for result in scorer.score_submissions(submissions):
    print(json.dumps(result.to_dict(), ensure_ascii=False))
