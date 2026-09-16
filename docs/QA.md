# Validation report - 16 September 2026

## Passed

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
