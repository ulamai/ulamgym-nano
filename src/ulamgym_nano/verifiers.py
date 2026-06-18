from __future__ import annotations

import ast
import json
import math
import re
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from .schema import RewardVector, ScoreResult, PromptRow, VerifierRow


class VerificationError(Exception):
    """Raised when a verifier configuration is invalid."""


def verify(prompt: PromptRow, verifier: VerifierRow, completion: Any, *, team: str = "anonymous", model: str = "unknown", run_id: str = "default") -> ScoreResult:
    cfg = dict(verifier.verifier)
    kind = str(cfg.get("kind", ""))
    if not kind:
        raise VerificationError(f"Task {prompt.task_id} has no verifier.kind")

    extracted = extract_answer(completion)

    if kind == "exact_answer":
        passed, diagnostics = _verify_exact(extracted, cfg)
    elif kind == "numeric_interval":
        passed, diagnostics = _verify_numeric_interval(extracted, cfg)
    elif kind == "multiple_choice":
        passed, diagnostics = _verify_multiple_choice(extracted, cfg)
    elif kind == "json_fields":
        passed, diagnostics = _verify_json_fields(completion, cfg)
    else:
        raise VerificationError(f"Unsupported verifier.kind {kind!r} for task {prompt.task_id}")

    strictness = str(cfg.get("strictness", prompt.strictness))
    if strictness == "strict":
        rv = RewardVector(strict=1.0 if passed else 0.0, dense=0.0, integrity=1.0)
        reward = rv.scalar()
    else:
        rv = RewardVector(strict=0.0, dense=1.0 if passed else 0.0, integrity=1.0)
        reward = rv.scalar(dense_weight=1.0)

    feedback = "Accepted." if passed else "Rejected."
    return ScoreResult(
        task_id=prompt.task_id,
        passed=passed,
        reward=reward,
        reward_vector=rv,
        strictness=strictness,
        feedback=feedback,
        diagnostics=diagnostics,
        team=team,
        model=model,
        run_id=run_id,
    )


def extract_answer(completion: Any) -> Any:
    """Extract answer from common completion formats.

    Supported inputs:
      - a raw scalar/string answer
      - JSON string with key `answer`
      - dict with key `answer`
      - a list/set answer for root/set tasks
    """
    if isinstance(completion, Mapping):
        if "answer" in completion:
            return completion["answer"]
        if "final_answer" in completion:
            return completion["final_answer"]
        return completion
    if isinstance(completion, str):
        s = completion.strip()
        if not s:
            return s
        try:
            parsed = json.loads(s)
        except Exception:
            return s
        if isinstance(parsed, Mapping):
            if "answer" in parsed:
                return parsed["answer"]
            if "final_answer" in parsed:
                return parsed["final_answer"]
        return parsed
    return completion


def normalize(value: Any, mode: str = "string") -> Any:
    if mode == "raw":
        return value
    if mode == "string":
        return str(value).strip().lower()
    if mode == "number":
        n = _to_number(value)
        if n is None:
            return str(value).strip().lower()
        if isinstance(n, Fraction) and n.denominator == 1:
            return int(n)
        return n
    if mode == "set":
        values = _as_sequence(value)
        return tuple(sorted(normalize(v, "number") for v in values))
    if mode == "json":
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value.strip()
        return value
    raise VerificationError(f"Unknown normalization mode {mode!r}")


def _verify_exact(answer: Any, cfg: Mapping[str, Any]) -> tuple[bool, Dict[str, Any]]:
    answers = cfg.get("answers")
    if answers is None:
        raise VerificationError("exact_answer verifier requires answers")
    if not isinstance(answers, Sequence) or isinstance(answers, (str, bytes)):
        answers = [answers]
    mode = str(cfg.get("normalization", "string"))
    got = normalize(answer, mode)
    expected = [normalize(x, mode) for x in answers]
    passed = got in expected
    # Trainer-safe diagnostics: never return gold answers.
    return passed, {"verifier_kind": "exact_answer", "normalization": mode, "accepted_count": len(expected)}


def _verify_numeric_interval(answer: Any, cfg: Mapping[str, Any]) -> tuple[bool, Dict[str, Any]]:
    center_raw = cfg.get("target")
    tol_raw = cfg.get("tolerance", 0.0)
    if center_raw is None:
        raise VerificationError("numeric_interval verifier requires target")
    got = _to_float(answer)
    center = _to_float(center_raw)
    tol = _to_float(tol_raw)
    if got is None or center is None or tol is None:
        passed = False
        err = None
    else:
        err = abs(got - center)
        passed = err <= abs(tol)
    return passed, {
        "verifier_kind": "numeric_interval",
        "tolerance": float(tol) if tol is not None else None,
        "absolute_error_bucket": _bucket_error(err, tol),
    }


def _verify_multiple_choice(answer: Any, cfg: Mapping[str, Any]) -> tuple[bool, Dict[str, Any]]:
    correct = cfg.get("correct")
    if correct is None:
        raise VerificationError("multiple_choice verifier requires correct")
    got = str(answer).strip().upper()
    if len(got) > 1:
        m = re.search(r"\b([A-H])\b", got.upper())
        got = m.group(1) if m else got[:1]
    passed = got == str(correct).strip().upper()
    return passed, {"verifier_kind": "multiple_choice", "choice_count": int(cfg.get("choice_count", 0) or 0)}


def _verify_json_fields(completion: Any, cfg: Mapping[str, Any]) -> tuple[bool, Dict[str, Any]]:
    fields = cfg.get("fields")
    if not isinstance(fields, Mapping):
        raise VerificationError("json_fields verifier requires object fields")
    if isinstance(completion, str):
        try:
            obj = json.loads(completion)
        except Exception:
            obj = {}
    elif isinstance(completion, Mapping):
        obj = completion
    else:
        obj = {}
    if not isinstance(obj, Mapping):
        obj = {}
    passed_count = 0
    total = len(fields)
    for key, spec in fields.items():
        expected = spec.get("answers") if isinstance(spec, Mapping) else [spec]
        mode = spec.get("normalization", "string") if isinstance(spec, Mapping) else "string"
        got = normalize(obj.get(key), mode)
        exp = [normalize(v, mode) for v in (expected if isinstance(expected, list) else [expected])]
        if got in exp:
            passed_count += 1
    passed = passed_count == total and total > 0
    return passed, {"verifier_kind": "json_fields", "fields_total": total, "fields_passed": passed_count}


def _as_sequence(value: Any) -> List[Any]:
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, str):
        s = value.strip()
        try:
            parsed = json.loads(s)
            if isinstance(parsed, (list, tuple, set)):
                return list(parsed)
        except Exception:
            pass
        s = s.strip("{}[]()")
        if not s:
            return []
        return [part.strip() for part in re.split(r"[,;]", s) if part.strip()]
    return [value]


def _to_number(value: Any) -> Any:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isfinite(value) and abs(value - round(value)) < 1e-12:
            return int(round(value))
        return value
    if isinstance(value, Fraction):
        return value
    s = str(value).strip()
    if not s:
        return None
    try:
        frac = Fraction(s)
        return frac
    except Exception:
        pass
    try:
        return float(s)
    except Exception:
        return None


def _to_float(value: Any) -> float | None:
    n = _to_number(value)
    if n is None:
        return None
    try:
        x = float(n)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def _bucket_error(err: float | None, tol: float | None) -> str:
    if err is None or tol is None:
        return "invalid"
    tol = abs(tol)
    if err <= tol:
        return "within_tolerance"
    if tol == 0:
        return "nonzero_error"
    if err <= 2 * tol:
        return "near"
    if err <= 10 * tol:
        return "far"
    return "very_far"
