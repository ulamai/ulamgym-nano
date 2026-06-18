from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from . import __version__
from .io import (
    PUBLIC_PROMPTS,
    VERIFIER_MANIFEST,
    load_task_pack,
    load_taskpack_metadata,
    validate_public_prompt_leakage,
    write_jsonl,
)
from .leaderboard import build_leaderboard
from .rlvr import RLVRScorer
from .schema import PROMPT_SCHEMA_VERSION, VERIFIER_SCHEMA_VERSION
from .server import serve

DEFAULT_TASK_DIR = "taskpacks/nano-sample-v0.2"


def cmd_validate(args: argparse.Namespace) -> int:
    prompts, verifiers = load_task_pack(args.task_dir)
    metadata = load_taskpack_metadata(args.task_dir)
    warnings = validate_public_prompt_leakage(prompts)
    kinds = {}
    for v in verifiers.values():
        kind = str(v.verifier.get("kind"))
        kinds[kind] = kinds.get(kind, 0) + 1
    print(json.dumps({
        "ok": not warnings or args.allow_warnings,
        "taskpack_id": metadata.get("taskpack_id") if metadata else None,
        "taskpack_metadata": bool(metadata),
        "task_count": len(prompts),
        "verifier_kinds": kinds,
        "warnings": warnings,
        "leaderboard_normalization": "full_task_default",
    }, indent=2, ensure_ascii=False))
    return 0 if (not warnings or args.allow_warnings) else 1


def cmd_catalog(args: argparse.Namespace) -> int:
    scorer = RLVRScorer.from_task_dir(args.task_dir)
    rows = scorer.catalog()
    if args.out:
        write_jsonl(args.out, rows)
    else:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


def cmd_export_prompts(args: argparse.Namespace) -> int:
    scorer = RLVRScorer.from_task_dir(args.task_dir)
    write_jsonl(args.out, scorer.prompt_rows())
    print(f"wrote {args.out}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    scorer = RLVRScorer.from_task_dir(args.task_dir)
    results = scorer.score_jsonl_file(args.submissions, args.out)
    print(json.dumps({
        "scores": len(results),
        "mean_reward": sum(r.reward for r in results) / max(1, len(results)),
        "pass_rate": sum(1 for r in results if r.passed) / max(1, len(results)),
        "out": args.out,
    }, indent=2))
    return 0


def cmd_leaderboard(args: argparse.Namespace) -> int:
    total_tasks = None if args.attempted_only else args.total_tasks
    if args.task_dir and total_tasks is None and not args.attempted_only:
        prompts, _ = load_task_pack(args.task_dir)
        total_tasks = len(prompts)
    rows = build_leaderboard(args.scores, args.out, title=args.title, total_tasks=total_tasks)
    print(json.dumps({"rows": len(rows), "out": args.out, "total_tasks": total_tasks}, indent=2))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    serve(args.task_dir, args.host, args.port)
    return 0


def cmd_init_task(args: argparse.Namespace) -> int:
    task_dir = Path(args.task_dir)
    task_dir.mkdir(parents=True, exist_ok=True)
    prompts_path = task_dir / PUBLIC_PROMPTS
    manifest_path = task_dir / VERIFIER_MANIFEST

    prompt = {
        "schema_version": PROMPT_SCHEMA_VERSION,
        "task_id": args.task_id,
        "env": args.env,
        "domain": args.domain,
        "strictness": args.strictness,
        "max_steps": args.max_steps,
        "prompt": args.prompt,
        "answer_format": args.answer_format,
        "metadata": {
            "source_artifact_id": args.source_artifact_id,
            "source_license": args.source_license,
            "source_visibility": args.source_visibility,
            "contamination_risk": args.contamination_risk,
            "estimated_human_minutes": args.estimated_human_minutes,
            "skill_tags": args.skill_tags or [],
            "public_sample": args.public_sample,
            "hidden_holdout": False,
            "task_generator_version": "ulamgym-nano-init-task-0.1.0",
        },
    }

    verifier = {
        "schema_version": VERIFIER_SCHEMA_VERSION,
        "task_id": args.task_id,
        "verifier": {
            "kind": args.verifier_kind or args.env,
            "answers": args.answers,
            "normalization": args.normalization,
            "strictness": args.strictness,
        },
    }
    if args.verifier_kind == "numeric_interval" or args.env == "numeric_interval":
        verifier["verifier"] = {
            "kind": "numeric_interval",
            "target": args.answers[0] if args.answers else args.target,
            "tolerance": args.tolerance,
            "strictness": args.strictness,
        }
    if args.verifier_kind == "multiple_choice" or args.env == "multiple_choice":
        verifier["verifier"] = {
            "kind": "multiple_choice",
            "correct": args.answers[0] if args.answers else args.correct,
            "choice_count": args.choice_count,
            "strictness": args.strictness,
        }

    _append_jsonl(prompts_path, prompt)
    _append_jsonl(manifest_path, verifier)
    print(f"appended task {args.task_id} to {task_dir}")
    return 0


def cmd_submission_template(args: argparse.Namespace) -> int:
    scorer = RLVRScorer.from_task_dir(args.task_dir)
    rows = []
    for task in scorer.prompt_rows():
        rows.append({
            "schema_version": "ulamgym.nano.submission.v1",
            "team": args.team,
            "model": args.model,
            "run_id": args.run_id,
            "task_id": task["task_id"],
            "completion": "",
        })
    write_jsonl(args.out, rows)
    print(f"wrote {args.out}")
    return 0


def _append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ulamgym-nano", description="Small public RLVR gym for verifier-backed math tasks.")
    parser.add_argument("--version", action="version", version=f"ulamgym-nano {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate", help="Validate a task pack.")
    p.add_argument("--task-dir", default=DEFAULT_TASK_DIR)
    p.add_argument("--allow-warnings", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("catalog", help="Print or export public catalog metadata.")
    p.add_argument("--task-dir", default=DEFAULT_TASK_DIR)
    p.add_argument("--out")
    p.set_defaults(func=cmd_catalog)

    p = sub.add_parser("export-prompts", help="Export agent-visible prompt rows.")
    p.add_argument("--task-dir", default=DEFAULT_TASK_DIR)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_export_prompts)

    p = sub.add_parser("score", help="Score submission JSONL against a task pack.")
    p.add_argument("--task-dir", default=DEFAULT_TASK_DIR)
    p.add_argument("--submissions", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("leaderboard", help="Build a leaderboard from score JSONL.")
    p.add_argument("--scores", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--title", default="UlamGym Nano Leaderboard")
    p.add_argument("--task-dir", default=DEFAULT_TASK_DIR, help="Normalize leaderboard by this task pack's full task count.")
    p.add_argument("--total-tasks", type=int, help="Normalize leaderboard by a fixed full task count; skipped tasks count as zero.")
    p.add_argument("--attempted-only", action="store_true", help="Use attempted-task denominator for local debugging only.")
    p.set_defaults(func=cmd_leaderboard)

    p = sub.add_parser("serve", help="Run a local dependency-free verifier service.")
    p.add_argument("--task-dir", default=DEFAULT_TASK_DIR)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("init-task", help="Append a simple exact/numeric/multiple-choice task to a task pack.")
    p.add_argument("--task-dir", required=True)
    p.add_argument("--task-id", required=True)
    p.add_argument("--env", default="exact_answer")
    p.add_argument("--verifier-kind")
    p.add_argument("--domain", default="math")
    p.add_argument("--strictness", default="strict")
    p.add_argument("--max-steps", type=int, default=1)
    p.add_argument("--prompt", required=True)
    p.add_argument("--answer-format", required=True)
    p.add_argument("--answers", nargs="*", default=[])
    p.add_argument("--normalization", default="string")
    p.add_argument("--target")
    p.add_argument("--tolerance", type=float, default=0.0)
    p.add_argument("--correct")
    p.add_argument("--choice-count", type=int, default=0)
    p.add_argument("--source-artifact-id", default="generated")
    p.add_argument("--source-license", default="generated-public-sample")
    p.add_argument("--source-visibility", default="generated_public_sample")
    p.add_argument("--contamination-risk", default="high_public_sample")
    p.add_argument("--estimated-human-minutes", type=int, default=1)
    p.add_argument("--skill-tags", nargs="*", default=[])
    p.add_argument("--public-sample", action="store_true", default=True)
    p.set_defaults(func=cmd_init_task)

    p = sub.add_parser("submission-template", help="Create an empty submission JSONL template.")
    p.add_argument("--task-dir", default=DEFAULT_TASK_DIR)
    p.add_argument("--out", required=True)
    p.add_argument("--team", default="my-team")
    p.add_argument("--model", default="my-model")
    p.add_argument("--run-id", default="run-001")
    p.set_defaults(func=cmd_submission_template)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
