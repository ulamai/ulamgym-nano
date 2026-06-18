import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ulamgym_nano import RLVRScorer, NanoEnv
from ulamgym_nano.io import load_task_pack, load_submissions, validate_public_prompt_leakage
from ulamgym_nano.leaderboard import aggregate_scores

ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "data" / "sample_tasks"


class CoreTests(unittest.TestCase):
    def test_load_task_pack(self):
        prompts, verifiers = load_task_pack(TASK_DIR)
        self.assertEqual(len(prompts), 5)
        self.assertEqual(set(prompts), set(verifiers))

    def test_public_prompt_leakage_only_answer_format_allowed(self):
        prompts, _ = load_task_pack(TASK_DIR)
        warnings = validate_public_prompt_leakage(prompts)
        self.assertEqual(warnings, [])

    def test_good_submissions_pass(self):
        scorer = RLVRScorer.from_task_dir(TASK_DIR)
        submissions = load_submissions(TASK_DIR / "submissions_good.jsonl")
        results = scorer.score_submissions(submissions)
        self.assertTrue(all(r.passed for r in results))
        self.assertEqual(sum(r.reward for r in results), len(results))

    def test_bad_submissions_fail(self):
        scorer = RLVRScorer.from_task_dir(TASK_DIR)
        submissions = load_submissions(TASK_DIR / "submissions_bad.jsonl")
        results = scorer.score_submissions(submissions)
        self.assertTrue(all(not r.passed for r in results))
        self.assertEqual(sum(r.reward for r in results), 0.0)

    def test_reward_fn(self):
        scorer = RLVRScorer.from_task_dir(TASK_DIR)
        rewards = scorer.reward_fn(["nano_exact_001", "nano_roots_001"], ['{"answer":"56"}', '{"answer":[3,2]}'])
        self.assertEqual(rewards, [1.0, 1.0])

    def test_env_reset_step(self):
        env = NanoEnv.from_task_dir(str(TASK_DIR))
        obs, info = env.reset("nano_exact_001")
        self.assertEqual(obs["task_id"], "nano_exact_001")
        _, reward, terminated, truncated, info = env.step('{"answer":"56"}')
        self.assertTrue(terminated)
        self.assertFalse(truncated)
        self.assertEqual(reward, 1.0)
        self.assertTrue(info["score"]["passed"])

    def test_leaderboard_aggregate(self):
        scorer = RLVRScorer.from_task_dir(TASK_DIR)
        submissions = load_submissions(TASK_DIR / "submissions_good.jsonl")
        rows = [r.to_dict() for r in scorer.score_submissions(submissions)]
        agg = aggregate_scores(rows)
        self.assertEqual(len(agg), 1)
        self.assertEqual(agg[0]["mean_reward"], 1.0)
        self.assertEqual(agg[0]["pass_rate"], 1.0)

    def test_leaderboard_full_task_normalization_penalizes_skips(self):
        scorer = RLVRScorer.from_task_dir(TASK_DIR)
        row = scorer.score_submission("nano_exact_001", '{"answer":"56"}', team="skip-team").to_dict()
        agg = aggregate_scores([row], total_tasks=5)
        self.assertEqual(agg[0]["attempted_tasks"], 1)
        self.assertEqual(agg[0]["total_tasks"], 5)
        self.assertEqual(agg[0]["mean_reward"], 0.2)
        self.assertEqual(agg[0]["coverage"], 0.2)

    def test_score_does_not_leak_gold(self):
        scorer = RLVRScorer.from_task_dir(TASK_DIR)
        result = scorer.score_submission("nano_exact_001", '{"answer":"55"}')
        encoded = json.dumps(result.to_dict())
        self.assertNotIn('"56"', encoded)
        self.assertNotIn('answers', encoded.lower())
        self.assertEqual(result.feedback, "Rejected.")


class CLITests(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "ulamgym_nano.cli", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            env={"PYTHONPATH": str(ROOT / "src")},
            check=True,
        )

    def test_cli_validate(self):
        proc = self._run("validate", "--task-dir", str(TASK_DIR), "--allow-warnings")
        self.assertIn('"task_count": 5', proc.stdout)

    def test_cli_score_and_leaderboard(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            scores = d / "scores.jsonl"
            lb = d / "leaderboard.md"
            self._run("score", "--task-dir", str(TASK_DIR), "--submissions", str(TASK_DIR / "submissions_good.jsonl"), "--out", str(scores))
            self.assertTrue(scores.exists())
            self._run("leaderboard", "--scores", str(scores), "--out", str(lb))
            self.assertIn("baseline", lb.read_text())

    def test_cli_init_task(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            self._run(
                "init-task",
                "--task-dir", str(d),
                "--task-id", "tmp_001",
                "--prompt", "Compute 2+2.",
                "--answer-format", '{"answer":"..."}',
                "--answers", "4",
                "--normalization", "number",
            )
            prompts, verifiers = load_task_pack(d)
            self.assertIn("tmp_001", prompts)
            result = RLVRScorer.from_task_dir(d).score_submission("tmp_001", '{"answer":"4"}')
            self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
