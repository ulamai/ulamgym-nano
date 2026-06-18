# Public Release Checklist

Before pushing a task pack publicly:

- [ ] Code license and data license are separate.
- [ ] Public sample data is clearly labeled as sample/demo.
- [ ] No private verifier manifests are committed.
- [ ] No answer keys are present in prompt rows.
- [ ] `private/` remains git-ignored.
- [ ] Every task has source/license metadata.
- [ ] Every task has `hidden_holdout=false` if public.
- [ ] Run `ulamgym-nano validate --task-dir ...`.
- [ ] Run sample good and bad submissions.
- [ ] Regenerate leaderboard.

For official hidden challenges:

- [ ] Publish prompts only.
- [ ] Keep verifier manifest in private storage or hosted scorer.
- [ ] Define submission limits and schedule.
- [ ] Freeze version and image digest.
- [ ] Publish results with clear caveats.
