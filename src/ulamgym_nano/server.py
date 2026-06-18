from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict
from urllib.parse import urlparse

from . import __version__
from .rlvr import RLVRScorer


def make_handler(scorer: RLVRScorer):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ulamgym-nano/0.1"

        def _json(self, status: int, payload: Dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _read_json(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length > 10_000_000:
                raise ValueError("request too large")
            body = self.rfile.read(length).decode("utf-8") if length else "{}"
            obj = json.loads(body or "{}")
            if not isinstance(obj, dict):
                raise ValueError("request body must be a JSON object")
            return obj

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/health":
                self._json(200, {"ok": True, "service": "ulamgym-nano", "version": __version__})
            elif path == "/v1/catalog":
                self._json(200, {"schema_version": "ulamgym.nano.catalog.v1", "tasks": scorer.catalog()})
            elif path == "/v1/prompts":
                self._json(200, {"schema_version": "ulamgym.nano.prompts.v1", "tasks": scorer.prompt_rows()})
            else:
                self._json(404, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            try:
                req = self._read_json()
                if path == "/v1/verify":
                    task_id = str(req.get("task_id", ""))
                    completion = req.get("completion", req.get("submission", ""))
                    team = str(req.get("team", "anonymous"))
                    model = str(req.get("model", "unknown"))
                    run_id = str(req.get("run_id", "api"))
                    result = scorer.score_submission(task_id, completion, team=team, model=model, run_id=run_id)
                    self._json(200, {"result": result.to_dict()})
                elif path == "/v1/batch_verify":
                    items = req.get("submissions", [])
                    if not isinstance(items, list):
                        raise ValueError("submissions must be a list")
                    results = []
                    for item in items:
                        if not isinstance(item, dict):
                            raise ValueError("each submission must be an object")
                        task_id = str(item.get("task_id", ""))
                        completion = item.get("completion", item.get("submission", ""))
                        team = str(item.get("team", req.get("team", "anonymous")))
                        model = str(item.get("model", req.get("model", "unknown")))
                        run_id = str(item.get("run_id", req.get("run_id", "api")))
                        results.append(scorer.score_submission(task_id, completion, team=team, model=model, run_id=run_id).to_dict())
                    self._json(200, {"results": results})
                else:
                    self._json(404, {"error": "not_found"})
            except Exception as exc:  # intentional safe public message
                self._json(400, {"error": "bad_request", "message": str(exc)})

        def log_message(self, format: str, *args: Any) -> None:
            # Keep default server quiet for trainer loops.
            return

    return Handler


def serve(task_dir: str, host: str = "127.0.0.1", port: int = 8000) -> None:
    scorer = RLVRScorer.from_task_dir(task_dir)
    httpd = ThreadingHTTPServer((host, port), make_handler(scorer))
    print(f"ulamgym-nano serving {task_dir} on http://{host}:{port}", flush=True)
    httpd.serve_forever()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-dir", default="data/sample_tasks")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    serve(args.task_dir, args.host, args.port)


if __name__ == "__main__":
    main()
