#!/usr/bin/env bash
set -euo pipefail

git init
git add .
git commit -m "Initialize UlamGym Nano v0.1"
git branch -M main

echo "Now add your remote:"
echo "  git remote add origin git@github.com:<ORG>/ulamgym-nano.git"
echo "  git push -u origin main"
