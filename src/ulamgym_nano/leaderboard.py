from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from .io import read_jsonl


def aggregate_scores(score_rows: Iterable[Mapping[str, Any]], *, total_tasks: int | None = None) -> List[Dict[str, Any]]:
    """Aggregate score rows by team/model/run.

    If total_tasks is provided, mean_reward is normalized by the full task count,
    so skipping tasks counts as zero. This is the recommended leaderboard mode
    for competitions. Without total_tasks, mean_reward is normalized over
    attempted tasks for lightweight local debugging.
    """
    by_key: Dict[tuple[str, str, str], Dict[str, Any]] = {}
    for row in score_rows:
        team = str(row.get("team", "anonymous"))
        model = str(row.get("model", "unknown"))
        run_id = str(row.get("run_id", "default"))
        key = (team, model, run_id)
        agg = by_key.setdefault(key, {"team": team, "model": model, "run_id": run_id, "tasks": 0, "passed": 0, "total_reward": 0.0})
        agg["tasks"] += 1
        agg["passed"] += int(bool(row.get("passed", False)))
        agg["total_reward"] += float(row.get("reward", 0.0))
    rows = []
    for agg in by_key.values():
        attempted = max(1, int(agg["tasks"]))
        denom = max(1, int(total_tasks)) if total_tasks else attempted
        pass_denom = denom if total_tasks else attempted
        rows.append({
            **agg,
            "mean_reward": agg["total_reward"] / denom,
            "pass_rate": agg["passed"] / pass_denom,
            "attempted_tasks": int(agg["tasks"]),
            "total_tasks": int(total_tasks) if total_tasks else int(agg["tasks"]),
            "coverage": min(1.0, int(agg["tasks"]) / max(1, int(total_tasks))) if total_tasks else 1.0,
        })
    rows.sort(key=lambda r: (-r["mean_reward"], -r["pass_rate"], -r["coverage"], r["team"], r["model"]))
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows


def render_markdown(rows: List[Mapping[str, Any]], *, title: str = "UlamGym Nano Leaderboard") -> str:
    lines = [
        f"# {title}",
        "",
        "| Rank | Team | Model | Run | Mean reward | Pass rate | Coverage | Attempted / Total |",
        "|---:|---|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['rank']} | {row['team']} | {row['model']} | {row['run_id']} | "
            f"{row['mean_reward']:.4f} | {100 * row['pass_rate']:.1f}% | {100 * row.get('coverage', 1.0):.1f}% | "
            f"{row.get('attempted_tasks', row['tasks'])} / {row.get('total_tasks', row['tasks'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_leaderboard(scores_path: str | Path, out_path: str | Path, *, title: str = "UlamGym Nano Leaderboard", total_tasks: int | None = None) -> List[Dict[str, Any]]:
    rows = list(read_jsonl(scores_path))
    agg = aggregate_scores(rows, total_tasks=total_tasks)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() == ".json":
        out_path.write_text(json.dumps(agg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        out_path.write_text(render_markdown(agg, title=title), encoding="utf-8")
    return agg
