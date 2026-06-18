from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

PROMPT_SCHEMA_VERSION = "ulamgym.nano.prompt.v1"
VERIFIER_SCHEMA_VERSION = "ulamgym.nano.verifier.v1"
SUBMISSION_SCHEMA_VERSION = "ulamgym.nano.submission.v1"
SCORE_SCHEMA_VERSION = "ulamgym.nano.score.v1"


@dataclass(frozen=True)
class PromptRow:
    task_id: str
    env: str
    prompt: str
    answer_format: str
    domain: str = "math"
    strictness: str = "strict"
    max_steps: int = 1
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = PROMPT_SCHEMA_VERSION

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "PromptRow":
        missing = [k for k in ["task_id", "env", "prompt", "answer_format"] if not row.get(k)]
        if missing:
            raise ValueError(f"Prompt row missing required fields: {missing}")
        metadata = row.get("metadata") or {}
        if not isinstance(metadata, Mapping):
            raise ValueError("Prompt row metadata must be an object")
        return cls(
            task_id=str(row["task_id"]),
            env=str(row["env"]),
            prompt=str(row["prompt"]),
            answer_format=str(row["answer_format"]),
            domain=str(row.get("domain", "math")),
            strictness=str(row.get("strictness", "strict")),
            max_steps=int(row.get("max_steps", 1)),
            metadata=dict(metadata),
            schema_version=str(row.get("schema_version", PROMPT_SCHEMA_VERSION)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "env": self.env,
            "domain": self.domain,
            "strictness": self.strictness,
            "max_steps": self.max_steps,
            "prompt": self.prompt,
            "answer_format": self.answer_format,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class VerifierRow:
    task_id: str
    verifier: Mapping[str, Any]
    schema_version: str = VERIFIER_SCHEMA_VERSION

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "VerifierRow":
        if not row.get("task_id"):
            raise ValueError("Verifier row missing task_id")
        verifier = row.get("verifier") or {}
        if not isinstance(verifier, Mapping):
            raise ValueError("Verifier row verifier must be an object")
        if not verifier.get("kind"):
            raise ValueError(f"Verifier row {row.get('task_id')} missing verifier.kind")
        return cls(
            task_id=str(row["task_id"]),
            verifier=dict(verifier),
            schema_version=str(row.get("schema_version", VERIFIER_SCHEMA_VERSION)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "task_id": self.task_id,
            "verifier": dict(self.verifier),
        }


@dataclass(frozen=True)
class SubmissionRow:
    task_id: str
    completion: Any
    team: str = "anonymous"
    model: str = "unknown"
    run_id: str = "default"
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SUBMISSION_SCHEMA_VERSION

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "SubmissionRow":
        if not row.get("task_id"):
            raise ValueError("Submission row missing task_id")
        if "completion" not in row and "submission" not in row:
            raise ValueError(f"Submission row {row.get('task_id')} missing completion")
        metadata = row.get("metadata") or {}
        if not isinstance(metadata, Mapping):
            raise ValueError("Submission metadata must be an object")
        return cls(
            task_id=str(row["task_id"]),
            completion=row.get("completion", row.get("submission")),
            team=str(row.get("team", "anonymous")),
            model=str(row.get("model", "unknown")),
            run_id=str(row.get("run_id", "default")),
            metadata=dict(metadata),
            schema_version=str(row.get("schema_version", SUBMISSION_SCHEMA_VERSION)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "team": self.team,
            "model": self.model,
            "run_id": self.run_id,
            "task_id": self.task_id,
            "completion": self.completion,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class RewardVector:
    strict: float = 0.0
    dense: float = 0.0
    integrity: float = 1.0
    efficiency: float = 0.0
    expert: float = 0.0

    def scalar(self, dense_weight: float = 0.0, efficiency_weight: float = 0.0, expert_weight: float = 0.0) -> float:
        value = self.strict + dense_weight * self.dense + efficiency_weight * self.efficiency + expert_weight * self.expert
        value *= self.integrity
        return max(0.0, min(1.0, float(value)))

    def to_dict(self) -> Dict[str, float]:
        return {
            "strict": float(self.strict),
            "dense": float(self.dense),
            "integrity": float(self.integrity),
            "efficiency": float(self.efficiency),
            "expert": float(self.expert),
        }


@dataclass(frozen=True)
class ScoreResult:
    task_id: str
    passed: bool
    reward: float
    reward_vector: RewardVector
    strictness: str = "strict"
    feedback: str = ""
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    team: str = "anonymous"
    model: str = "unknown"
    run_id: str = "default"
    schema_version: str = SCORE_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "team": self.team,
            "model": self.model,
            "run_id": self.run_id,
            "task_id": self.task_id,
            "passed": bool(self.passed),
            "reward": float(self.reward),
            "reward_vector": self.reward_vector.to_dict(),
            "strictness": self.strictness,
            "feedback": self.feedback,
            "diagnostics": dict(self.diagnostics),
        }
