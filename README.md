# Sivanesh Job Engine - v2

An evidence-led job-search dashboard, private application tracker and editable resume studio. Built for a minimum INR 12 LPA move before 31 December 2026. No outcome is guaranteed.

## What is built

- Search, match/location/pay filters, recency/deadline sorting, direct employer links and shareable job deep links.
- Every recommended role has an explainable weighted match score and a locally bundled company logo; pay screening is separate.
- Salary source, confidence, historical-data warnings, review scope and evidence dates.
- Job-specific benefits, risks, recruiter questions, ATS matches and actual gaps.
- Private stages, notes, follow-up dates, recruiter-confirmed total/fixed CTC and application history.
- Private master resume import; editable suggestions; individual approvals; user-confirmed extra facts.
- Genuine DOCX export, browser print / Save PDF, plain-text preview and separate local versions. Master remains unchanged.
- Light/dark themes, mobile layout, keyboard support, safe URL handling and schema validation.
- Separate public JSON export and private backups; optional AES-GCM encrypted backup transfer.
- Python discovery script, daily 09:00 IST GitHub Actions workflow, tests and public-only Pages deployment.
- `AGENTS.md` so Codex has the project requirements and safety constraints without rereading the conversation.

## Current status - be precise

Published at https://arun-john-alt.github.io/sivanesh-job-engine/ from https://github.com/arun-john-alt/sivanesh-job-engine. GitHub Pages deployment and a Tavily-powered discovery run have succeeded. The daily 09:00 IST schedule is configured; scheduled execution remains best-effort. See docs/QA.md for release checks and limitations.

Four employer-hosted listings were researched on 16 September 2026: Vestas 79195, Comcast R441661, Ford 64092, and RNTBCI JOBREQ_50275099. They were found in the search index; fresh direct page fetches failed. They are therefore labelled **employer-indexed**, not guaranteed-live vacancies. Actual source URLs are included per claim. Unsupported salary guesses from the earlier starter were removed.

The included crawler is discovery and availability checking, **not a fully autonomous salary/culture/recruiter-research agent**. New leads stay out of the Jobs and Resume lists until their full descriptions support reviewed match percentages. Their specific limitations are listed under Sources → Not listed yet. Daily discovery does not perform that review. Broad discovery requires a search API key; without it, only configured employer pages and existing roles are checked. No coverage of restricted/logged-in portals is promised.

The earlier ChatGPT task is separate. It does not automatically push into this repository. This package contains an independent GitHub workflow; it begins functioning only after deployment/setup.

## Local use - no package installation

```
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`. Do not double-click index.html: browser ES modules and JSON fetch need an HTTP server.

Download the separate **sivanesh-private-workspace.json** supplied in the conversation. Click **Import profile** in the app. This restores the supplied professional profile, private current CTC and baseline resume. Do NOT upload that JSON to GitHub. The original PDF is not modified and is not part of this public repository.

## First GitHub publication

Use Codex in the extracted project folder. It should inspect this README and AGENTS.md, authenticate with GitHub, verify the destination account and publish the public files only.

For a new public repository, an optional guarded helper is included. Prerequisites: Git, Node 20+, Python 3.10+, GitHub CLI, Git author configuration and `gh auth login`.

```
bash scripts/publish.sh YOUR_USERNAME/sivanesh-job-engine --public
```

The helper checks the logged-in account, runs tests, refuses to overwrite an existing repository, creates a public repository, enables Actions-based Pages and requests a deployment. Check the Actions result before calling it live. It never force-pushes. For an existing repository, use an inspected update branch in Codex instead.

Manual publication: commit this project to the chosen repository's `main` branch. In **Settings > Pages**, select **GitHub Actions** as the publishing source. Run **Job engine - scan, test and publish** under Actions, with scan set to false for the initial deployment. The workflow deploys `dist/`, which contains only the allowlisted `site/` files.

## Daily discovery

The workflow has `30 3 * * *` UTC, which is 09:00 IST. GitHub scheduled jobs are best-effort and can be delayed or disabled by platform/repository conditions. They are not precise-time alerts.

Add `TAVILY_API_KEY` under **Settings > Secrets and variables > Actions** for public web and LinkedIn discovery. Tavily offers 1,000 free credits/month with no credit card required (checked 16 September 2026). Keep the free plan; paid billing is not enabled by this project. The scanner uses eight LinkedIn queries and eight employer queries, each at basic depth with up to 20 results, plus up to ten exact-URL availability rechecks: at most 26 credits/run or 806 credits in a 31-day month. Coverage stays within Chennai and nearby industrial areas plus remote India. Manual runs also consume credits. `BRAVE_SEARCH_API_KEY` remains supported if Tavily is absent; when both are present, only Tavily is used. Keys stay in Actions and never reach the browser.

LinkedIn discovery uses search-index results, never a LinkedIn login or direct LinkedIn scraping. Only individual job URLs with relevant role and location evidence and no explicit closure signal become unscored, salary-unknown leads marked **LinkedIn indexed**. Search dates are not posting dates. Tracking/country/slug URL variants are deduplicated. Existing reviewed records and linked employer application URLs are preserved. Explicit closure language in the exact search result hides that listing; the oldest indexed jobs rotate through availability rechecks. Missing results never imply closure, and search-index status can lag the live page. Reported uncertain listings may be held out of the active feed pending verification. Matching an employer listing to a LinkedIn lead requires checking the requisition and adding `linkedinUrl` to the reviewed record; the scanner does not guess a match from similar titles. No complete LinkedIn coverage or live availability is promised.

Without either secret, employer checks still run and coverage explicitly reports LinkedIn as **Not configured**. After adding the key, manually run the workflow with scan=true and check its coverage report. Search failures are recorded and do not remove previous jobs.

Change `config/search.json` to manage queries, approved employer hosts, request budget and watch pages. The script respects robots, refuses private/unapproved network destinations, limits requests, deduplicates exact role URLs and retains reviewed analyses. Employer search-index leads can be retained without JobPosting metadata; they remain indexed rather than live. Raw provider page text is used transiently for status/relevance and is not published. Up to 12 existing employer pages are rechecked per run, leaving discovery capacity within a 48-page fetch budget. New discoveries require review before qualification. A failed check is not an expired vacancy.

A scheduled run commits only `site/data/jobs.json`, then deploys in the same workflow. This avoids depending on a bot push triggering another workflow. Branch protection that forbids direct bot commits requires a pull-request adaptation; it must not be bypassed with a force push.

## Research and application workflow

1. Review the exact JD and source evidence. Research current salary/culture where accessible; otherwise retain unknown.
2. Update `site/data/jobs.json`, keeping schema version 2 and per-claim sources. Run validation and tests, commit and push.
3. In the app, shortlist and record a next action. Confirm fixed/variable/total compensation early.
4. Open Resume studio; review/edit proposals and approve truthful facts. Confirm the final version, export and check the document layout.
5. Apply manually on the employer website, then record the application and follow-up date.

High fit is 80%+, Medium is 65-79%, Low is below 65%. The score is a documented heuristic, not an employer ATS rating. Only verified employer annual **total CTC** ceilings below the target cause automatic pay exclusion. Unknown pay, low third-party estimates and annual base-pay figures are not automatic rejections.

## Privacy and multi-device use

The published job dataset is shared. Application status, recruiter notes, private compensation, master resume and approved versions are local to each browser. They do not automatically sync between Arun and Sivanesh or between devices.

Use **Encrypted backup** and import the snapshot on the other device. This is explicit transfer, not real-time collaboration. Encryption uses PBKDF2-SHA256 (250,000 iterations, random salt) and AES-256-GCM (random IV). Use a strong unique passphrase, shared separately. Local browser storage itself is not encrypted by the app. Clearing site data can lose local records; keep backups.

Plain private JSON backups contain personal data. Never publish them. The build has an exact-file allowlist and private-field checks; those are safeguards, not a substitute for reviewing free-text research for personal information. `noindex` is not access control.

## Validation

```
node --test tests/*.test.js
python3 -m unittest discover -s tests -p 'test_*.py'
node scripts/validate.mjs
python3 scripts/build.py
```

No npm packages are required. See `docs/QA.md` for what was and was not tested. Development preview: `docs/dashboard-preview.png`.

## Technical references

- GitHub Pages custom workflows: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- Workflow schedules: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule
- Tavily Search API: https://docs.tavily.com/documentation/api-reference/endpoint/search
- Brave Search API: https://api-dashboard.search.brave.com/app/documentation/web-search

Reviewed 16 September 2026. Use official documentation when changing provider integrations; do not assume previous chat claims are current facts.
