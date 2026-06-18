from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from .io import load_task_pack, load_submissions, write_jsonl
from .schema import PromptRow, VerifierRow, SubmissionRow, ScoreResult
from .verifiers import verify


class RLVRScorer:
    """Verifier-backed reward function for RLVR trainers and batch scoring."""

    def __init__(self, prompts: Mapping[str, PromptRow], verifiers: Mapping[str, VerifierRow]):
        self.prompts = dict(prompts)
        self.verifiers = dict(verifiers)

    @classmethod
    def from_task_dir(cls, task_dir: str | Path) -> "RLVRScorer":
        prompts, verifiers = load_task_pack(task_dir)
        return cls(prompts, verifiers)

    def catalog(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for task_id in sorted(self.prompts):
            p = self.prompts[task_id]
            rows.append({
                "task_id": p.task_id,
                "env": p.env,
                "domain": p.domain,
                "strictness": p.strictness,
                "max_steps": p.max_steps,
                "metadata": dict(p.metadata),
            })
        return rows

    def prompt_rows(self) -> List[Dict[str, Any]]:
        return [self.prompts[k].to_dict() for k in sorted(self.prompts)]

    def score_submission(self, task_id: str, completion: Any, *, team: str = "anonymous", model: str = "unknown", run_id: str = "default") -> ScoreResult:
        if task_id not in self.prompts:
            raise KeyError(f"Unknown task_id {task_id!r}")
        return verify(
            self.prompts[task_id],
            self.verifiers[task_id],
            completion,
            team=team,
            model=model,
            run_id=run_id,
        )

    def score_submissions(self, submissions: Iterable[SubmissionRow]) -> List[ScoreResult]:
        results = []
        for sub in submissions:
            results.append(self.score_submission(
                sub.task_id,
                sub.completion,
                team=sub.team,
                model=sub.model,
                run_id=sub.run_id,
            ))
        return results

    def reward_fn(self, task_ids: Sequence[str], completions: Sequence[Any]) -> List[float]:
        if len(task_ids) != len(completions):
            raise ValueError("task_ids and completions must have the same length")
        return [self.score_submission(tid, comp).reward for tid, comp in zip(task_ids, completions)]

    def score_jsonl_file(self, submissions_path: str | Path, out_path: str | Path) -> List[ScoreResult]:
        submissions = load_submissions(submissions_path)
        results = self.score_submissions(submissions)
        write_jsonl(out_path, [r.to_dict() for r in results])
        return results
