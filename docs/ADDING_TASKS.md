# Adding Tasks

UlamGym Nano is task-pack oriented. Each pack contains public prompts and a
verifier manifest.

## 1. Create a task pack

```bash
mkdir -p taskpacks/my_pack
```

Add taskpack metadata:

```json
{
  "taskpack_id": "my-pack-v0.2",
  "visibility": "public_dev",
  "license": "CC-BY-4.0 or custom",
  "intended_use": "local testing and public dev",
  "not_for": "hidden leaderboard claims",
  "verifier_visibility": "public",
  "schema_version": "ulamgym.nano.task.v0.2"
}
```

## 2. Add a task with the CLI

```bash
ulamgym-nano init-task \
  --task-dir taskpacks/my_pack \
  --task-id nt_factor_001 \
  --env exact_answer \
  --domain number_theory \
  --prompt "What is the largest prime factor of 91?" \
  --answer-format 'Return JSON: {"answer": "..."}' \
  --answers 13 \
  --normalization number \
  --skill-tags number_theory factorization exact_answer
```

## 3. Validate

```bash
ulamgym-nano validate --task-dir taskpacks/my_pack
```

## 4. Create a submission template

```bash
ulamgym-nano submission-template \
  --task-dir taskpacks/my_pack \
  --out runs/template.jsonl \
  --team my-team \
  --model my-model
```

## 5. Score

```bash
ulamgym-nano score \
  --task-dir taskpacks/my_pack \
  --submissions runs/template.jsonl \
  --out runs/scores.jsonl
```

## Task-design checklist

For every task, add metadata:

```json
{
  "source_artifact_id": "...",
  "source_license": "...",
  "source_visibility": "generated_public_sample/public/private",
  "contamination_risk": "low/medium/high_public_sample",
  "created_at": "YYYY-MM-DD",
  "task_generator_version": "...",
  "reference_solution_hash": "...",
  "estimated_human_minutes": 3,
  "skill_tags": ["..."]
}
```

## Public vs official challenge tasks

Public/local tasks may include `verifier_manifest.jsonl` in the repo. Teams can
run scoring locally, but the answers become public.

Official challenge tasks should use one of these safer patterns:

1. Publish only `public_prompts.jsonl`, keep `verifier_manifest.jsonl` hosted.
2. Release a public dev pack locally, but score the test pack on a hosted server.
3. Release the hidden manifest only after the challenge closes.

## Verifier-backed does not mean leak-proof

If the verifier manifest contains the answers, public users can inspect it.
That is okay for sample packs and dev tracks. It is not okay for hidden evals.
