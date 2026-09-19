# Sivanesh Job Engine: instructions for Codex

## Mission
Help Sivanesh pursue a better-paying job by 31 December 2026. The minimum target is INR 12 lakh annual CTC; current compensation is private and is loaded from the separate private workspace. Never promise a job or invent pipeline activity.

## First steps
Inspect Git status and remotes, and run the tests before changing code. Preserve uncommitted user work. Ask for the exact destination repository if no remote is configured. Never guess the user's GitHub account. Never force-push or overwrite an existing project. Prefer a reviewable branch for an existing repository.

## Architecture
- `site/` is the static GitHub Pages client; no backend, third-party scripts or secret-bearing API calls.
- `site/data/jobs.json` is shared public research (schema version 2).
- `site/engine.js` validates data and implements match/pay gates and resume approval.
- `site/resume.js` writes real DOCX files and encrypts explicit private backups.
- `scripts/scan.py` is conservative public-employer discovery. A search API is optional.
- `.github/workflows/engine.yml` tests, scans at 03:30 UTC / 09:00 IST, commits public data and deploys only `dist/`.
- `scripts/build.py` uses an exact public-file allowlist and a private-field gate.
- Private records, current CTC, contact details and the master resume are stored only in the browser. They do NOT automatically sync.

## Research rules
Never turn a title-only lead into a high match score. Weights: responsibilities 35, tools/analysis 20, relevant experience/seniority 20, industry 15, location 10. Scores are evidence heuristics, not ATS outcomes or interview probabilities. Record reasons and actual gaps. Do not confuse five years of total supply-chain work with five years of automotive strategic sourcing.

Salary and match are independent. Only an employer-disclosed annual TOTAL CTC maximum below the target can trigger the automatic pay exclusion. An old Glassdoor datapoint, a third-party estimate, base salary alone or unknown salary cannot. Preserve evidence type, age, location, sample size, basis and confidence. When no defensible estimate exists, say unknown.

Prefer exact employer requisitions. Distinguish employer-indexed results from direct live page checks. A 403, failed network fetch or absent search result does not mean the job is closed. Respect robots and portal restrictions; never bypass login or anti-bot controls.

Employee reviews are anecdotal; distinguish office and function. Do not merge ratings from similarly named company profiles. Do not present restructuring or layoffs as verified facts based on anonymous reviews alone.

## Resume rules
Never fabricate skills, metrics, responsibilities or employer-specific tool usage. The resume lists several tools globally but does not establish which employer used every one. Candidate-reported achievements include 99%+ dealer order fill, zero supplier past dues at Ford and 20% procurement cost reduction at Flex; retain their actual scope.

Only approved edits and explicitly user-confirmed new facts reach exports. Editing text clears approval. The master is immutable during tailoring. Each export stores a separate snapshot. Improved wording does not automatically increase factual match. Test DOCX validity and render-check output after layout changes.

## Privacy and deployment
Do not commit the user's PDF, private workspace JSON, recruiter notes, contact details, current compensation, generated resumes, .env files, passwords or tokens. Do not put GitHub tokens or API keys in client JavaScript. Public GitHub Pages is not a private login system. Encryption is for explicit exported backups; local browser storage is not encrypted at rest.

The user's authorization to host the app is not authorization to post private application data. Publish only the public build after checking the repository/account. A workflow file is not proof that a scan or deployment has run. Claim a public URL only after checking the successful Pages deployment.

## Tests
```
node --test tests/*.test.js
python3 -m unittest discover -s tests -p 'test_*.py'
node scripts/validate.mjs
python3 scripts/build.py
```
Run browser tests on a real local server where the environment permits it. The initial build additionally had offline DOM tests because browser navigation was restricted; see docs/QA.md. Preserve these limitations rather than claiming full end-to-end deployment validation.
