# Data Card: UlamGym Nano v0.2 Sample Pack

## Purpose

`ulamgym-nano-v0.2` is a public technical-preview RLVR gym. It contains a
compact, transparent sample pack so anyone can run the verifier loop locally.
The sample pack exists to test integration, task formats, submissions, scoring,
and leaderboards.

## Included data

- `taskpacks/nano-sample-v0.2/taskpack.json`: taskpack metadata.
- `taskpacks/nano-sample-v0.2/public_prompts.jsonl`: agent-visible prompts.
- `taskpacks/nano-sample-v0.2/verifier_manifest.jsonl`: sample verifier metadata.
- `taskpacks/nano-sample-v0.2/submissions_good.jsonl`: smoke-test submissions.
- `taskpacks/nano-sample-v0.2/submissions_bad.jsonl`: negative smoke submissions.

## Not included

This public repo does not include hidden holdouts, private verifier manifests,
private reviewer notes, raw private proof traces, or unreleased task packs.

## Public benchmark warning

Bundled sample tasks are public and likely contaminated after release. They are
for integration tests and demos, not for capability claims.

## Adding tasks

When adding a new public task pack, include:

- source artifact or source URL
- source license
- source visibility
- contamination risk
- task generator version, if generated
- estimated human minutes
- skill tags
- hidden-holdout status
