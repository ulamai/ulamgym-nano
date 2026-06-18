from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Tuple

from .schema import PromptRow, VerifierRow, SubmissionRow

PUBLIC_PROMPTS = "public_prompts.jsonl"
VERIFIER_MANIFEST = "verifier_manifest.jsonl"
TASKPACK_METADATA = "taskpack.json"

SUPPORTED_VERIFIER_KINDS = {
    "exact_answer",
    "json_fields",
    "multiple_choice",
    "numeric_interval",
}

REQUIRED_TASKPACK_METADATA_KEYS = {
    "taskpack_id",
    "visibility",
    "license",
    "intended_use",
    "not_for",
    "verifier_visibility",
    "schema_version",
}

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

ANSWER_BEARING_PATTERNS = [
    re.compile(r"\banswer\s*(?:is|=|:)", re.IGNORECASE),
    re.compile(r"\bsolution\s*(?:is|=|:)", re.IGNORECASE),
    re.compile(r"\bcorrect\s+answer\b", re.IGNORECASE),
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
    errors = validate_task_pack(prompts, verifiers, task_dir=task_dir)
    if errors:
        raise ValueError("; ".join(errors))
    return prompts, verifiers


def load_taskpack_metadata(task_dir: str | Path) -> Dict[str, Any] | None:
    path = Path(task_dir) / TASKPACK_METADATA
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid taskpack metadata at {path}: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError(f"Taskpack metadata at {path} must be an object")
    return obj


def validate_task_pack(
    prompts: Mapping[str, PromptRow],
    verifiers: Mapping[str, VerifierRow],
    *,
    task_dir: str | Path | None = None,
) -> List[str]:
    errors: List[str] = []
    prompt_ids = set(prompts)
    verifier_ids = set(verifiers)

    missing = sorted(prompt_ids - verifier_ids)
    extra = sorted(verifier_ids - prompt_ids)
    if missing:
        errors.append(f"Missing verifier rows for tasks: {missing}")
    if extra:
        errors.append(f"Verifier rows without public prompts: {extra}")

    for task_id, prompt in prompts.items():
        if not prompt.prompt.strip():
            errors.append(f"{task_id}: prompt is empty")
        if not prompt.answer_format.strip():
            errors.append(f"{task_id}: answer_format is empty")
        for pattern in ANSWER_BEARING_PATTERNS:
            if pattern.search(prompt.prompt):
                errors.append(f"{task_id}: prompt appears to contain an answer-bearing phrase")
                break

    for task_id, verifier in verifiers.items():
        kind = str(verifier.verifier.get("kind", ""))
        if kind not in SUPPORTED_VERIFIER_KINDS:
            errors.append(f"{task_id}: unsupported verifier.kind {kind!r}")
        if kind == "exact_answer" and "answers" not in verifier.verifier:
            errors.append(f"{task_id}: exact_answer verifier missing answers")
        if kind == "numeric_interval":
            if "target" not in verifier.verifier:
                errors.append(f"{task_id}: numeric_interval verifier missing target")
            if "tolerance" not in verifier.verifier:
                errors.append(f"{task_id}: numeric_interval verifier missing tolerance")
        if kind == "multiple_choice":
            if "correct" not in verifier.verifier:
                errors.append(f"{task_id}: multiple_choice verifier missing correct")
            if "choice_count" not in verifier.verifier:
                errors.append(f"{task_id}: multiple_choice verifier missing choice_count")
        if kind == "json_fields" and "fields" not in verifier.verifier:
            errors.append(f"{task_id}: json_fields verifier missing fields")

    if task_dir is not None:
        metadata = load_taskpack_metadata(task_dir)
        if metadata is not None:
            missing_keys = sorted(REQUIRED_TASKPACK_METADATA_KEYS - set(metadata))
            if missing_keys:
                errors.append(f"Taskpack metadata missing required keys: {missing_keys}")

    return errors


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
