# GitHub Initialization

From the repo root:

```bash
git init
git add .
git commit -m "Initialize UlamGym Nano v0.1"
git branch -M main
git remote add origin git@github.com:<ORG>/ulamgym-nano.git
git push -u origin main
```

Recommended GitHub repo settings:

- Protect `main`.
- Require CI before merge.
- Disable public write access to `data/` unless reviewing task licenses.
- Add a clear README warning that sample tasks are not hidden benchmarks.
- Use GitHub Releases for frozen challenge versions.
