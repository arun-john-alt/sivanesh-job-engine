# Validation report - 16 September 2026

## UI refresh verification — 16 September 2026

Neutral/indigo redesign with compact navigation, condensed job cards, expandable evidence, and mobile list/detail navigation. No private-storage keys, domain scoring, discovery schedule, or resume document generator changed.

Passed: 19 Node tests, 16 Python tests, dataset validation, JavaScript syntax check, public build privacy gate and Git whitespace checks. Real browser preview checked at desktop size, 390×844, 320×740 and 820×1180. Verified mobile search, filter panel, job selection and Back, saving a job into the local preview pipeline, resume import empty state, settings and dark theme. DOM width checks at 320px and 820px showed no page overflow; no browser console errors were captured. Export logic remains covered by the existing tests; a new resume document layout was not introduced or re-rendered.

Design references: [Linear interface refresh](https://linear.app/now/behind-the-latest-design-refresh) and [Dribbble job-search mobile concept](https://dribbble.com/shots/26496497-Job-Finder-Mobile-App-Dashboard-Search-UI). The older dashboard screenshot below documents the initial design, not this refresh.

## Initial package checks

### Passed

19 Node unit tests and 6 Python unit tests (25 total): data validation, weighted scores, salary gates, date expiry, duplicate rejection, unsafe links, private/public separation, resume approval and immutability, actual ZIP/DOCX output, encrypted backup round-trip/wrong-password rejection, source URL restrictions, role filtering, structured job parsing, salary unit handling and India-remote eligibility.

12 offline Chromium interface checks: rendering four sourced jobs; private CTC comparison; approval-driven DOCX blob generation; resetting approval after edits; state reinitialization; safe public export; pipeline rendering; source coverage; search/reset; salary filtering; mobile/dark layout; and absence of JavaScript errors in the exercised flows.

Public build allowlist/private-field checks and shell syntax validation passed. The site has no required third-party JavaScript or npm packages.

A test resume was created with the exact client DOCX exporter, opened by the document renderer, and rendered into two pages. Both pages were visually inspected. A further role-specific education edit removes graduation dates for Vestas without altering the master. After this change, the two-page document was rendered and visually checked again.

## Important limits

This environment's browser policy blocked navigation, including to a local HTTP server. The interface was therefore tested in an offline DOM harness with mocked fetch, localStorage and download delivery. These tests do not establish real-browser persistence, real network/module loading, clipboard permissions, download delivery or a successful GitHub Pages deployment. The real module code also passed Node syntax/import tests.

Live crawler requests, search-provider credentials, GitHub repository creation, Actions execution and remote deployment were NOT run here. No GitHub credentials or confirmed repository destination were available. The first actual Pages deployment should be checked in a normal browser, including file import, actual DOCX download, PDF printing, HTTPS backup encryption, persistence across a reload, and mobile navigation.

The initial job dataset is an employer-indexed research snapshot, not a promise that every application form is still accepting applications.

## Preview

`dashboard-preview.png` is a screenshot of the real client rendered offline, not an image-generated mockup. Initial pipeline counts are zero; no applications were fabricated in the delivered dataset.

## Share-readiness QA — 16 September 2026

Release review after the Nextmove UI refresh. All checks use synthetic private data; no personal workspace or generated resume is committed.

Fixed findings:
- Private imports now validate settings, resume structure, application records, approvals and saved versions before replacing local state. Noncanonical dates, injected pay values, prototype keys and broken nested records are rejected. Optional resume lists normalize safely for printing.
- Settings validate a prospective copy before mutation. Import success messages no longer mask browser-storage failures.
- Employer scans require matching title, URL (when present) and requisition (when present) before updating an existing listing. Recommended-job metadata cannot replace another role's deadline, salary or availability. Distinct listing URLs are fetched separately.
- Dataset import works after an initial fetch failure. Empty mobile result sets exit detail mode. Hash-based shared links clear conflicting filters.
- README deployment status and current UI labels corrected.

Verification:
- 22 Node tests and 20 Python tests passed, including malformed private import cases, full private snapshot round-trip, encryption/wrong-passphrase checks and four scanner identity regressions.
- Public validation passed for 13 jobs (9 LinkedIn-indexed leads); exact build allowlist and private-field gate passed.
- Real browser on isolated localhost: synthetic profile import; Applied status and notes persist after reload; malformed import rejected while existing note remains; editing approved text disables final export; DOCX action creates a separate saved version; no console errors observed.
- Search no-results/reset, keyboard Enter job opening, mobile Back, shared Comcast link after a Vestas filter, 390 px job detail, 320 px settings/dark mode passed with no horizontal overflow. Prior refresh QA also covered desktop and tablet layouts.
- Generated a genuine DOCX via the production generator and rendered it with bundled LibreOffice. Both synthetic two-page output images inspected: text readable, no clipping or overlap. This does not guarantee every candidate-edited resume fits two pages.
- Tracked files inspected for credential patterns, personal email addresses and prohibited private artifacts; none found. Public output contains only index.html, styles.css, app.js, engine.js, resume.js, favicon.svg, data/jobs.json and .nojekyll.
- GitHub account verified as arun-john-alt; Tavily secret name present; previous manual scan and Pages deployments succeeded. Cron remains 03:30 UTC / 09:00 IST.

Limits:
- The automated browser tool blocked blob download/PDF-popup navigation. DOCX generator structure/rendering and UI snapshot creation passed, but actual browser download delivery and Print-to-PDF remain manual smoke checks. No workaround of that browser policy was attempted.
- Chromium-based desktop/browser viewport QA is not a physical iOS/Android or Safari compatibility certification.
- A scheduled run has not yet been observed after initial setup; successful manual execution and configured cron establish setup, not precise future timing.
- LinkedIn coverage is partial search-index discovery, not logged-in access or verified live vacancies. New leads still need review. Application submission remains manual.
- Private resume/profile and tracker data are local to each browser. Sivanesh must import the separate profile to tailor resumes and keep encrypted backups for transfer/recovery. Public sharing does not grant GitHub edit access.

## Discovery expansion — 18 September 2026

- Confirmed the 17 September scheduled run (35201513733) succeeded. It started at 08:46 UTC / 14:16 IST, showing that GitHub delayed the 09:00 IST schedule. The 18 September manual expanded run (35300998406) also succeeded.
- Discovery increased from six queries × eight results to sixteen focused queries × twenty results, split evenly between LinkedIn and employer discovery. Scope remains Chennai and nearby areas plus remote India, as confirmed by the owner. Ten additional exact-URL availability rechecks rotate oldest-first; the basic-search budget is capped at 26 calls/run (806 per 31 daily runs, excluding manual runs).
- Closed search results and expired explicit application deadlines are rejected. Existing records close only on an exact URL/LinkedIn ID match; missing results, other requisitions and recommended-role closures are not closure evidence. Two Hired records are held outside the active feed following the owner's concern, rather than misrepresented as independently confirmed closed.
- Search-provider raw text is transient and never published. Employer listings lacking JSON-LD can now enter as unscored indexed leads. Existing employer rechecks are capped at twelve to leave room for discovery; unrelated watch-page links no longer consume the whole budget.
- The expanded live run added 13 records (7 LinkedIn, 6 employer), taking 14 stored records to 27. The scan performed 8 LinkedIn searches, 8 employer searches and 10 rotating rechecks. No existing listing was independently confirmed closed by those search checks. This is partial coverage, not a complete inventory or a guarantee that every indexed listing remains open.
- Separately reviewed full public JDs for Buying Simplified Senior Buyer and HP Supply Chain Planner. Added transparent 75% and 78% profile-match breakdowns; availability stays indexed, pay unknown and experience/ownership gaps explicit. Scores are not ATS probabilities. Other leads remain unscored until sufficiently reviewed.
- 23 JavaScript and 32 Python tests pass. Regression coverage includes closure/deadline rejection, identity-sensitive rechecks, missing-result preservation, held versus confirmed-closed semantics, employer indexing without JSON-LD, Chennai-region geography, foreign job-location rejection and transient-text privacy.
- Browser checks: Hired search yields no default-feed results, unscored explanation renders, no console errors. The public build and schema validation pass. Private browser records are unchanged.
- Final browser regression found and fixed: opening/reloading any job deep link previously enabled the archived filter globally. Active shared links now keep closed/held roles hidden; archive inclusion is only enabled when opening an unavailable role explicitly. Reopening a reviewed LinkedIn job was checked with zero Ford/Hired cards visible. Chennai-region filtering was also checked against the Sriperumbudur Rockwell role.
