from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Tuple

from .schema import PromptRow, VerifierRow, SubmissionRow

PUBLIC_PROMPTS = "public_prompts.jsonl"
VERIFIER_MANIFEST = "verifier_manifest.jsonl"

ALLOWED_PUBLIC_KEYS = {"answer_format", "reference_solution_hash", "hidden_holdout"}

HIDDEN_FIELD_HINTS = [
    "answer",
    "answers",
    "gold",
    "solution",
    "reference",
    "verifier",
    "manifest",
    "secret",
    "hidden",
    "accepted_ids",
    "valid_witness",
]


def read_jsonl(path: str | Path) -> Iterator[Dict[str, Any]]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{lineno}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"JSONL row at {path}:{lineno} must be an object")
            yield row


def write_jsonl(path: str | Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n")


def load_task_pack(task_dir: str | Path) -> Tuple[Dict[str, PromptRow], Dict[str, VerifierRow]]:
    task_dir = Path(task_dir)
    prompts_path = task_dir / PUBLIC_PROMPTS
    manifest_path = task_dir / VERIFIER_MANIFEST
    if not prompts_path.exists():
        raise FileNotFoundError(f"Missing {prompts_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing {manifest_path}")

    prompts: Dict[str, PromptRow] = {}
    for row in read_jsonl(prompts_path):
        prompt = PromptRow.from_dict(row)
        if prompt.task_id in prompts:
            raise ValueError(f"Duplicate prompt task_id {prompt.task_id}")
        prompts[prompt.task_id] = prompt

    verifiers: Dict[str, VerifierRow] = {}
    for row in read_jsonl(manifest_path):
        verifier = VerifierRow.from_dict(row)
        if verifier.task_id in verifiers:
            raise ValueError(f"Duplicate verifier task_id {verifier.task_id}")
        verifiers[verifier.task_id] = verifier

    prompt_ids = set(prompts)
    verifier_ids = set(verifiers)
    missing = sorted(prompt_ids - verifier_ids)
    extra = sorted(verifier_ids - prompt_ids)
    if missing:
        raise ValueError(f"Missing verifier rows for tasks: {missing}")
    if extra:
        raise ValueError(f"Verifier rows without public prompts: {extra}")
    return prompts, verifiers


def load_submissions(path: str | Path) -> List[SubmissionRow]:
    return [SubmissionRow.from_dict(row) for row in read_jsonl(path)]


def validate_public_prompt_leakage(prompts: Mapping[str, PromptRow]) -> List[str]:
    warnings: List[str] = []
    for task_id, prompt in prompts.items():
        row = prompt.to_dict()
        for key in _walk_keys(row):
            low = key.lower()
            if any(hint == low or hint in low for hint in HIDDEN_FIELD_HINTS):
                if key in ALLOWED_PUBLIC_KEYS:
                    continue
                warnings.append(f"{task_id}: prompt contains suspicious key {key!r}")
    return warnings


def _walk_keys(obj: Any) -> Iterable[str]:
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            yield str(k)
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v)
