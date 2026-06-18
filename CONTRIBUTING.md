# Contributing

Contributions are welcome for:

- new public sample tasks
- verifier kinds
- docs and examples
- leaderboard/reporting utilities
- integrations with RL trainers

Before submitting a task pack, run:

```bash
make smoke
ulamgym-nano validate --task-dir <your_task_dir>
```

Do not submit private verifier manifests, answer keys for hidden challenges,
private reviewer notes, or unreleased task packs.
