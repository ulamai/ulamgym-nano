from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Tuple

from .rlvr import RLVRScorer


class NanoEnv:
    """Tiny reset/step environment wrapper, dependency-free.

    This intentionally mirrors the Gymnasium mental model without requiring
    Gymnasium as a dependency. Each episode is a single verifier-backed attempt.
    """

    def __init__(self, scorer: RLVRScorer):
        self.scorer = scorer
        self.task_id: Optional[str] = None
        self.terminated = False

    @classmethod
    def from_task_dir(cls, task_dir: str) -> "NanoEnv":
        return cls(RLVRScorer.from_task_dir(task_dir))

    def reset(self, task_id: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if task_id is None:
            task_id = sorted(self.scorer.prompts)[0]
        if task_id not in self.scorer.prompts:
            raise KeyError(f"Unknown task_id {task_id!r}")
        self.task_id = task_id
        self.terminated = False
        prompt = self.scorer.prompts[task_id]
        obs = {
            "task_id": prompt.task_id,
            "env": prompt.env,
            "prompt": prompt.prompt,
            "answer_format": prompt.answer_format,
        }
        info = {"domain": prompt.domain, "strictness": prompt.strictness, "metadata": dict(prompt.metadata)}
        return obs, info

    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, bool, Dict[str, Any]]:
        if self.task_id is None:
            raise RuntimeError("Call reset() before step().")
        if self.terminated:
            raise RuntimeError("Episode already terminated; call reset().")
        result = self.scorer.score_submission(self.task_id, action)
        self.terminated = True
        obs = {"task_id": self.task_id, "done": True}
        info = {"score": result.to_dict()}
        return obs, result.reward, True, False, info
