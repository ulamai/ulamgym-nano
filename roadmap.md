# UlamGym Nano Roadmap

**UlamGym Nano** is the public, lightweight version of UlamGym: a small RLVR environment for verifier-backed math, logic, and reasoning tasks that anyone can clone, run, extend, and use for public competitions.

Nano is intentionally separate from Ulam's internal/commercial UlamGym platform. Nano should be easy to run locally, transparent, community-friendly, and safe to publish. The internal UlamGym product can keep private task pools, hidden verifier manifests, customer tenants, task leasing, private scorecards, expert review, and larger proprietary task factories.

---

## Project positioning

### One-line description

> **UlamGym Nano is a small public RLVR gym for verifier-backed math tasks and community model-improvement challenges.**

### What Nano is

- A public GitHub repo for lightweight verifier-backed tasks.
- A local-first RLVR playground for model teams, students, and researchers.
- A simple task format with prompt rows, verifier manifests, submissions, rewards, and leaderboards.
- A place to host transparent public dev tasks and optional hosted-hidden public challenges.
- A bridge from toy math benchmarks toward richer proof-process tasks, without exposing Ulam's private data or internal commercial task pools.

### What Nano is not

- Not the private UlamGym customer product.
- Not a raw dump of Ulam's private task pools.
- Not a hidden benchmark if verifier manifests are public.
- Not a replacement for UlamGym Core / UlamGym RLVR Access.
- Not a place for private reviewer notes, proprietary research trajectories, full commercial corpora, or customer-specific tasks.

---

## Naming plan

### Repository

Recommended repository name:

```text
ulamgym-nano
```

### Python package

Recommended package name:

```text
ulamgym-nano
```

Recommended import module:

```python
import ulamgym_nano
```

### CLI

Recommended CLI:

```bash
ulamgym-nano
```

### Backwards compatibility

For v0.2 only, optionally keep a temporary alias:

```bash
ulamgym-small  # deprecated alias for ulamgym-nano
```

Remove or stop advertising the alias by v0.4.

---

## Design principles

1. **Public by default.** Anything committed to the Nano repo should be safe for public access.
2. **Verifier-backed.** Every task should have a deterministic or clearly labeled verifier.
3. **No hidden commercial data.** Private UlamGym data, customer tasks, and reference artifacts stay out of Nano.
4. **Local-first.** Anyone should be able to install Nano and run sample tasks without special credentials.
5. **Hosted-hidden optional.** Public competitions can use a hosted verifier for hidden official tasks, but local public dev tasks should always remain runnable.
6. **Model-provider agnostic.** Nano should work with local models, hosted APIs, fine-tuning loops, and simple JSONL completions.
7. **Leaderboard integrity.** Public leaderboards should score over the full task set by default, not only attempted tasks.
8. **Clear strictness labels.** Do not pretend rubric-style or informal checks are equivalent to strict machine verification.
9. **Small core, extensible edges.** Nano should stay simple, while allowing richer verifier plugins over time.

---

## Current baseline: v0.1

v0.1 is the public starter kit.

### Already present

- Basic task schema.
- Public prompt rows.
- Verifier manifest rows.
- Submission scoring.
- Reward vector.
- Local leaderboard generation.
- Local verifier server.
- Basic CLI.
- Docker and docker-compose support.
- GitHub Actions test workflow.
- Public sample tasks.
- Docs for task authoring, RLVR integration, hosted verifier mode, and competition rules.

### Initial verifier families

- `exact_answer`
- `numeric_interval`
- `multiple_choice`
- `json_fields`

### v0.1 limitation

v0.1 is not yet a serious public benchmark. It is a clean starter repo and integration scaffold.

---

# Version roadmap

## v0.2 — Rebrand and challenge-ready public skeleton

**Theme:** Rename to UlamGym Nano and make the repo ready for a first public challenge pack.

### Goals

- Complete the rename from UlamGym Small to UlamGym Nano.
- Make the repo feel polished enough for public launch.
- Strengthen task-pack validation and leaderboard fairness.
- Prepare the project for externally contributed task packs.

### Core work

- Rename package metadata from `ulamgym-small` to `ulamgym-nano`.
- Rename import module to `ulamgym_nano`.
- Rename CLI to `ulamgym-nano`.
- Keep `ulamgym-small` as a temporary deprecated CLI alias if easy.
- Update README, docs, examples, Dockerfile, GitHub workflow, and package metadata.
- Add `roadmap.md` to the repository root.
- Add a public logo/badge area to README.
- Add `CITATION.cff` or a simple citation section.
- Add `SECURITY.md` for reporting verifier or challenge leaks.

### Task-pack format improvements

Add a standard public task-pack layout:

```text
taskpacks/<pack_name>/
  public_prompts.jsonl
  verifier_manifest.jsonl
  sample_submissions.jsonl
  README.md
  TASK_CARD.md
  LICENSE.md
```

Add task-pack metadata:

```json
{
  "taskpack_id": "nano-dev-arithmetic-v0.2",
  "visibility": "public_dev",
  "license": "CC-BY-4.0 or custom",
  "intended_use": "local testing and public dev",
  "not_for": "hidden leaderboard claims",
  "verifier_visibility": "public",
  "schema_version": "ulamgym.nano.task.v0.2"
}
```

### Validation improvements

Add validators for:

- Prompt/verifier row matching.
- Duplicate task IDs.
- Missing verifier fields.
- Unsupported verifier kinds.
- Accidentally committed hidden/private fields.
- Empty prompts or answer-bearing prompts.
- Leaderboard normalization over all tasks.

### Leaderboard improvements

- Make full-task denominator the default.
- Keep attempted-only scoring as an explicit non-default option.
- Add per-verifier-family breakdown.
- Add `pass@1` and `mean_reward` summaries.
- Add `leaderboard.md` export.
- Add model metadata fields:
  - model name
  - model version/date
  - decoding settings
  - whether external tools were used
  - whether fine-tuning was used

### Release criteria

v0.2 is complete when:

- `pip install -e .` works.
- `make test` passes.
- `make smoke` passes.
- `ulamgym-nano --help` works.
- `ulamgym-nano catalog`, `score`, `leaderboard`, and `serve` work.
- Public sample task pack validates cleanly.
- README clearly distinguishes Nano from internal UlamGym.

---

## v0.3 — Verifier expansion and first real public dev pack

**Theme:** Add more interesting strict-machine verifier families and ship the first real Nano public dev pack.

### Goals

- Move beyond exact-answer smoke tests.
- Add verifier-backed math/logic tasks that are still easy to run locally.
- Release the first non-trivial public dev challenge pack.

### New verifier families

Add deterministic verifiers such as:

- `symbolic_expression_equivalence`
- `polynomial_identity`
- `rational_expression_equivalence`
- `integer_modular_check`
- `set_equality`
- `truth_table_tautology`
- `finite_counterexample_check`
- `json_schema_exact`
- `ordered_steps`

Optional, if kept lightweight:

- `sympy_simplify`
- `python_predicate`

The `python_predicate` verifier should be sandboxed or strongly restricted. It should not execute arbitrary untrusted code from task authors without guardrails.

### First public dev pack

Ship:

```text
taskpacks/nano-math-dev-v0.3/
```

Suggested composition:

| Task type | Count |
|---|---:|
| exact answer | 20 |
| symbolic equivalence | 20 |
| polynomial identity | 20 |
| modular arithmetic | 15 |
| finite counterexample | 15 |
| truth-table / logic | 10 |

Total: around 100 public dev tasks.

### Anti-gaming tests

Add tests that fail:

- Blank answers.
- Prompt copying.
- Always choosing option A.
- Overly broad numeric intervals.
- Malformed JSON accepted as correct.
- Symbolically equivalent-looking but invalid expressions.

### Release criteria

v0.3 is complete when:

- The new public dev pack validates.
- Each verifier has positive and negative tests.
- Sample baseline scripts run against the full dev pack.
- Leaderboard exports per-verifier-family metrics.

---

## v0.4 — Hosted-hidden public challenge mode

**Theme:** Support official public competitions where prompts are public but verifier manifests stay server-side.

### Goals

- Keep local public dev mode simple.
- Add a hosted verifier path for official challenge scoring.
- Avoid making public leaderboards depend on publicly visible answers.

### Hosted mode

Add CLI support:

```bash
ulamgym-nano submit-hosted \
  --prompts challenge_prompts.jsonl \
  --submissions my_model_outputs.jsonl \
  --server https://nano.ulam.ai \
  --api-key $ULAMGYM_NANO_API_KEY
```

Add server endpoints:

```text
GET  /health
GET  /v1/challenges
GET  /v1/challenges/{challenge_id}/prompts
POST /v1/challenges/{challenge_id}/submit
GET  /v1/challenges/{challenge_id}/leaderboard
```

### Challenge pack split

Use two tracks:

```text
public_dev/
  public_prompts.jsonl
  verifier_manifest.jsonl

official_hidden/
  public_prompts.jsonl
  # verifier manifest is not committed
```

### Competition controls

Add support for:

- Submission limits per team.
- Team metadata.
- Challenge start/end timestamps.
- Frozen prompt snapshots.
- Server-side full-task denominator.
- Basic anti-probing limits.
- Public result exports after challenge close.

### Release criteria

v0.4 is complete when:

- A local hosted verifier can run official-hidden sample tasks.
- Public prompts can be downloaded without verifier manifests.
- Submissions can be scored by task ID only.
- The hosted leaderboard can be exported to Markdown/JSON.
- Docs clearly explain public dev vs official hidden scoring.

---

## v0.5 — Training-loop integrations

**Theme:** Make Nano useful for teams doing small-scale RLVR, GRPO/PPO-style experiments, and reward-model prototyping.

### Goals

- Provide examples that turn Nano rewards into training signals.
- Keep integrations minimal and optional.
- Help users compare before/after fine-tuned models.

### Integrations

Add examples for:

- Batch scoring JSONL model completions.
- Reward-function wrapper for RL loops.
- Minimal TRL/GRPO-style example.
- Hugging Face dataset export/import.
- Local model evaluation script.
- API-model evaluation script.
- Pass@k evaluation.
- Bootstrap confidence intervals for leaderboard scores.

### New commands

```bash
ulamgym-nano export-hf
ulamgym-nano import-hf
ulamgym-nano batch-score
ulamgym-nano compare-runs
ulamgym-nano make-scorecard
```

### Scorecards

Add generated scorecards with:

- Overall mean reward.
- Pass@1.
- Pass@k.
- Per-task-family score.
- Per-verifier-family score.
- Failure counts by verifier feedback class.
- Attempted vs full-task denominator.
- Model/decode metadata.

### Release criteria

v0.5 is complete when:

- A user can run a small supervised or RL-style loop against Nano tasks.
- Two model snapshots can be compared cleanly.
- Scorecards are reproducible from submitted JSONL files.

---

## v0.6 — Community task authoring and review

**Theme:** Let the community add public tasks without breaking task quality or leaking answers into prompts.

### Goals

- Make task authoring easy.
- Make review strict enough to protect leaderboard quality.
- Start building a public task ecosystem.

### Authoring tools

Improve:

```bash
ulamgym-nano init-task
ulamgym-nano init-taskpack
ulamgym-nano validate-taskpack
ulamgym-nano test-taskpack
ulamgym-nano render-task-card
```

### Task review checks

Add checks for:

- Prompt contains answer.
- Verifier accepts too many malformed answers.
- Verifier rejects known valid answer.
- Duplicate or near-duplicate tasks.
- Ambiguous problem statements.
- Missing source/license metadata.
- Non-deterministic verifier behavior.

### Public registry

Add a simple registry file:

```text
registry/taskpacks.json
```

Each entry:

```json
{
  "taskpack_id": "nano-logic-dev-v0.6",
  "owner": "ulam-ai",
  "version": "0.6.0",
  "status": "public_dev",
  "license": "CC-BY-4.0",
  "task_count": 120,
  "verifier_families": ["truth_table_tautology", "multiple_choice"]
}
```

### Release criteria

v0.6 is complete when:

- A third party can create a task pack from template to validated PR.
- CI validates task packs.
- Docs define task acceptance criteria.
- Public task registry exists.

---

## v0.7 — Proof-process Lite

**Theme:** Add public-safe proof-process tasks without importing private Ulam research data.

### Goals

- Introduce process-level reasoning beyond final answers.
- Keep scoring conservative and transparent.
- Avoid overclaiming informal proof verification.

### New task families

Add lightweight public task types:

- `proof_step_ordering`
- `first_bad_step`
- `assumption_repair`
- `counterexample_repair`
- `dependency_check`
- `claim_scope_check`

These should be marked with strictness labels:

```text
strict_machine      deterministic machine check
source_strict       deterministic source/step check
semi_strict         rubric or heuristic check
experimental        not leaderboard-grade
```

### Public proof-process pack

Ship:

```text
taskpacks/nano-proof-process-dev-v0.7/
```

Suggested composition:

| Task type | Count |
|---|---:|
| proof step ordering | 25 |
| first bad step | 25 |
| assumption repair | 20 |
| counterexample repair | 20 |
| dependency check | 20 |

### Important caveat

Do not call informal proof rubrics strict RLVR unless they are backed by deterministic checks, executable witnesses, Lean, symbolic verification, or another replayable certificate.

### Release criteria

v0.7 is complete when:

- Proof-process tasks have clear strictness labels.
- Generic keyword-stuffing answers fail.
- Prompt-copying answers fail.
- Public docs explain what is and is not verified.

---

## v0.8 — Certificate DSL and VPP-style public sample pack

**Theme:** Add a small certificate-backed proof-process layer inspired by verified proof-process tasks.

### Goals

- Provide strict-machine proof-process tasks without requiring Lean.
- Let models submit compact certificates that can be deterministically checked.
- Make Nano more distinct from ordinary exact-answer math benchmarks.

### Certificate verifier families

Add a `certificate_dsl` verifier with families such as:

- `algebra_identity`
- `polynomial_nonnegative_sos`
- `residue_divisibility`
- `finite_sum_induction`
- `truth_table_tautology`
- `finite_counterexample`

### Task families

- `certificate_reconstruction`
- `certificate_completion`
- `certificate_critique`
- `proof_step_with_certificate`

### Public sample pack

Ship:

```text
taskpacks/nano-certificate-dev-v0.8/
```

Suggested size: 100-200 public tasks.

### Release criteria

v0.8 is complete when:

- Certificate verifiers are deterministic.
- Invalid certificates fail with trainer-safe feedback.
- Valid certificates pass across clean environments.
- Certificate tasks can be used in local RLVR loops.

---

## v0.9 — First public hosted Nano Challenge

**Theme:** Run a real community challenge.

### Goals

- Test the full competition workflow.
- Build a public leaderboard.
- Encourage teams to improve models on verifier-backed tasks.

### Challenge structure

```text
Nano Challenge 0
  public dev set: 100-300 tasks
  official hidden set: 100-300 tasks
  duration: 2-4 weeks
  max submissions: configurable
  scoring: full-task mean reward + pass@1 + per-family metrics
```

### Public outputs

After the challenge:

- Public leaderboard.
- Baseline model results.
- Challenge report.
- Failure-mode analysis.
- Updated task-authoring recommendations.

### Release criteria

v0.9 is complete when:

- At least one hosted challenge has run end-to-end.
- Results are reproducible from server logs.
- Challenge governance works.
- Public postmortem identifies what to improve before v1.0.

---

## v1.0 — Stable public API and first official Nano benchmark cycle

**Theme:** Make Nano stable enough for external teams to depend on.

### Goals

- Freeze core task schema v1.
- Freeze core CLI commands.
- Publish a stable public dev suite.
- Publish a repeatable hosted-hidden benchmark process.

### Stability guarantees

Freeze:

- Task schema v1.
- Verifier manifest schema v1.
- Submission schema v1.
- Leaderboard schema v1.
- CLI command names for core workflows.
- Public challenge report format.

### v1.0 task suites

Recommended public suites:

```text
nano-math-dev-v1
nano-logic-dev-v1
nano-symbolic-dev-v1
nano-proof-process-dev-v1
nano-certificate-dev-v1
```

### v1.0 public challenge

Run:

```text
Nano Challenge 1
```

with:

- Public dev set.
- Hosted hidden set.
- Frozen scoring.
- Published baselines.
- Published challenge rules.
- Public scorecard.

### Release criteria

v1.0 is complete when:

- External users can install and run Nano without support.
- Public task packs validate cleanly.
- At least one hosted-hidden public challenge has completed.
- Docs clearly distinguish local dev tasks, public hidden challenges, and private UlamGym products.

---

# Beyond v1.0

## v1.1 — Better model-evaluation ergonomics

- Rich HTML scorecards.
- Interactive leaderboard dashboard.
- More baseline model integrations.
- Run comparison UI.
- Failure clustering.

## v1.2 — More verifier plugins

- More symbolic algebra.
- More finite combinatorics.
- More counterexample search.
- Optional Lean-lite plugin if deterministic and easy to install.

## v1.3 — Education and tutorials

- Classroom mode.
- Beginner task packs.
- Notebook tutorials.
- Visual explanation of reward vectors.

## v1.4 — Community challenge seasons

- Seasonal public challenges.
- Community-submitted task packs.
- Maintainer-reviewed official packs.
- Archive of historical leaderboards.

---

# Boundary with internal UlamGym

Nano should remain the public, lightweight version. The internal UlamGym product can be larger, private, and commercially valuable.

| Capability | UlamGym Nano | Internal UlamGym |
|---|---:|---:|
| Public sample tasks | Yes | Yes |
| Local verifier manifests | Yes, for public dev tasks | Internal only |
| Hosted hidden public challenges | Optional | Yes |
| Private customer tenants | No | Yes |
| Task leasing API | Minimal public version | Full private product |
| Private task pools | No | Yes |
| Private verifier manifests | No | Yes |
| Reference proofs / hidden rubrics | No | Yes |
| Expert-reviewed research trajectories | No | Yes |
| Customer scorecards | No | Yes |
| Custom task generation | No | Yes |
| Dedicated/VPC deployment | No | Yes |
| Proprietary benchmark claims | No | Yes, contract-dependent |

Nano should create visibility, adoption, and community trust. Internal UlamGym should preserve the scarce assets: hidden tasks, private proof-process data, expert review, customer-specific environments, and hosted verifier infrastructure.

---

# Suggested issue labels

Use GitHub labels like:

```text
area:cli
area:docs
area:verifier
area:leaderboard
area:taskpack
area:hosted
area:training
area:competition
area:schema
area:security
kind:bug
kind:feature
kind:taskpack
kind:good-first-issue
release:v0.2
release:v0.3
release:v1.0
```

---

# Suggested milestones

Create GitHub milestones:

```text
v0.2 Rebrand + challenge skeleton
v0.3 Verifier expansion
v0.4 Hosted challenge mode
v0.5 Training integrations
v0.6 Community task authoring
v0.7 Proof-process Lite
v0.8 Certificate DSL
v0.9 First hosted challenge
v1.0 Stable public API
```

---

# Public README roadmap summary

A shorter README version can say:

```text
Roadmap:
- v0.2: Rename to UlamGym Nano and polish the public challenge scaffold.
- v0.3: Add symbolic/math verifiers and the first real public dev pack.
- v0.4: Add hosted-hidden competition mode.
- v0.5: Add training-loop integrations and scorecards.
- v0.6: Add community task-authoring workflow.
- v0.7: Add proof-process-lite tasks.
- v0.8: Add certificate-backed tasks.
- v0.9: Run the first public hosted Nano Challenge.
- v1.0: Stabilize the public API and challenge process.
```

