PYTHON ?= python3
TASK_DIR ?= taskpacks/nano-sample-v0.2

.PHONY: help test smoke validate score-good score-bad leaderboard serve docker-build zip clean

help:
	@echo "Available targets:"
	@echo "  make test          Run unit tests"
	@echo "  make smoke         Validate + score sample submissions + build sample leaderboard"
	@echo "  make validate      Validate TASK_DIR (default: taskpacks/nano-sample-v0.2)"
	@echo "  make serve         Run local verifier server"
	@echo "  make docker-build  Build Docker image"
	@echo "  make clean         Remove local run artifacts"

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

smoke: validate score-good score-bad leaderboard
	@echo "ulamgym-nano smoke ok"

validate:
	PYTHONPATH=src $(PYTHON) -m ulamgym_nano.cli validate --task-dir $(TASK_DIR) --allow-warnings

score-good:
	mkdir -p runs
	PYTHONPATH=src $(PYTHON) -m ulamgym_nano.cli score --task-dir $(TASK_DIR) --submissions $(TASK_DIR)/submissions_good.jsonl --out runs/good_scores.jsonl

score-bad:
	mkdir -p runs
	PYTHONPATH=src $(PYTHON) -m ulamgym_nano.cli score --task-dir $(TASK_DIR) --submissions $(TASK_DIR)/submissions_bad.jsonl --out runs/bad_scores.jsonl

leaderboard:
	mkdir -p leaderboards
	PYTHONPATH=src $(PYTHON) -m ulamgym_nano.cli leaderboard --scores runs/good_scores.jsonl --out leaderboards/sample.md --task-dir $(TASK_DIR)

serve:
	PYTHONPATH=src $(PYTHON) -m ulamgym_nano.cli serve --task-dir $(TASK_DIR) --host 0.0.0.0 --port 8000

docker-build:
	docker build -t ulamgym-nano:0.2 .

zip:
	cd .. && zip -r ulamgym-nano-v0.2.zip ulamgym-nano -x 'ulamgym-nano/.git/*' 'ulamgym-nano/.venv/*' 'ulamgym-nano/runs/*' 'ulamgym-nano/leaderboards/*' 'ulamgym-nano/**/__pycache__/*' 'ulamgym-nano/**/*.pyc'

clean:
	rm -rf runs leaderboards build dist *.egg-info .pytest_cache
