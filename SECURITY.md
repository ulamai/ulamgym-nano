# Security Policy

## Reporting Leaks or Vulnerabilities

Report suspected verifier leaks, hidden challenge data exposure, credential
exposure, unsafe verifier behavior, or challenge integrity issues privately.

Email: security@ulam.ai

If email is unavailable, open a GitHub issue with no sensitive details and ask
for a private disclosure channel.

## Scope

In scope:

- Accidental publication of hidden verifier manifests or answer keys.
- Public prompts leaking hidden answers or private source material.
- Hosted verifier endpoints exposing private challenge state.
- Verifiers that execute untrusted code unexpectedly.
- CI or packaging configuration that could publish private files.

Out of scope:

- Public sample task answers in public verifier manifests.
- Model performance claims based on the transparent sample taskpack.
- Bugs in external model providers or training frameworks.

## Maintainer Expectations

Do not commit private challenge manifests, answer keys, customer tasks, private
reviewer notes, or unreleased task packs to this repository. Keep official
hidden challenge scoring in hosted or private storage until results are meant to
be public.
