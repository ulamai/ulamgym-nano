"""Minimal RLVR reward function example."""

from ulamgym_nano import RLVRScorer

scorer = RLVRScorer.from_task_dir("data/sample_tasks")


def reward_fn(task_ids, completions):
    """Return scalar rewards for a trainer rollout batch."""
    return scorer.reward_fn(task_ids, completions)


if __name__ == "__main__":
    task_ids = ["nano_exact_001", "nano_roots_001"]
    completions = ['{"answer":"56"}', '{"answer":[2,3]}']
    print(reward_fn(task_ids, completions))
