#!/usr/bin/env bash
# First publication of this project. Run from the extracted project folder.
# Does not overwrite an existing repository or force-push anything.
set -euo pipefail
REPO="${1:-}"
if [[ ! "$REPO" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || [[ "${2:-}" != '--public' ]]; then
  printf 'Usage: bash scripts/publish.sh OWNER/REPO --public\nThis creates a PUBLIC source repository and a public GitHub Pages site.\n'
  exit 1
fi
for bin in gh git python3 node; do
  command -v "$bin" >/dev/null || { printf 'Missing prerequisite: %s\n' "$bin"; exit 1; }
done
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
gh auth status >/dev/null
LOGIN="$(gh api user --jq .login)"
if [[ "${REPO%%/*}" != "$LOGIN" ]]; then
  printf 'Requested owner does not match the logged-in GitHub account. Review the destination before proceeding.\n'
  exit 1
fi
if gh repo view "$REPO" >/dev/null 2>&1; then
  printf 'Repository already exists. Open it in Codex and review an update branch instead; this script will not overwrite it.\n'
  exit 1
fi
if [[ -d .git ]]; then
  printf 'This folder already has Git history. Use a fresh extracted folder or review the existing repository manually.\n'
  exit 1
fi
node --test tests/*.test.js
python3 -m unittest discover -s tests -p 'test_*.py'
node scripts/validate.mjs
python3 scripts/build.py
# Private data and .env files are both outside the allowlist and ignored.
git init -b main
git add site scripts config tests docs .github .gitignore AGENTS.md package.json
if ! git var GIT_AUTHOR_IDENT >/dev/null 2>&1; then
  printf 'Set your Git author name and email, then commit and publish from Codex. No repository has been created on GitHub.\n'
  exit 1
fi
git commit -m 'feat: evidence-led job engine, private resume studio and scheduled discovery'
gh repo create "$REPO" --public --source . --remote origin --push
# Enable Actions-based Pages publishing, then dispatch a known build.
gh api --method POST "repos/$REPO/pages" -f build_type=workflow >/dev/null
gh workflow run engine.yml --repo "$REPO" -f scan=false
printf '\nRepository created and deployment requested. Watch the workflow before claiming the site is live:\n'
printf 'https://github.com/%s/actions\n' "$REPO"
printf 'Expected URL after a successful deployment: https://%s.github.io/%s/\n' "${REPO%%/*}" "${REPO#*/}"
