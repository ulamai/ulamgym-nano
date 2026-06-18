# Task Card: nano-sample-v0.2

## Purpose

`nano-sample-v0.2` is a public development taskpack for testing UlamGym Nano's
prompt, verifier, submission, scoring, and leaderboard flow.

## Intended Use

- Local installation checks.
- CI smoke tests.
- Verifier integration examples.
- Documentation examples.

## Not For

- Hidden benchmark claims.
- Frontier model capability claims.
- Official challenge ranking.

## Contents

The pack contains five simple tasks covering exact answer, numeric interval,
multiple choice, and JSON-field verification.

## Verification

All verifier manifests are public. The tasks are therefore useful for debugging
and demos, not for measuring performance on hidden data.

## Contamination Risk

High after public release. The prompts and verifier behavior are intentionally
transparent.
