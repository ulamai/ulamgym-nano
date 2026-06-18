# Hosted Verifier Notes

The dependency-free HTTP server in this repo is suitable for local demos. For an
official public competition, harden it before opening it to the internet.

Minimum production additions:

- HTTPS behind a reverse proxy
- API keys or signed submissions
- request size limits
- rate limits
- persistent submission store
- per-team quotas
- replay/audit logging
- private verifier manifest mounted read-only
- no arbitrary filesystem paths
- container isolation for expensive verifiers

The public repo should not contain official hidden verifier manifests.
