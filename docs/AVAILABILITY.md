# Application availability — 23 September 2026

The daily workflow audits every non-closed stored vacancy before discovery. It respects robots rules and approved hosts. LinkedIn access failures do not establish closure. Search snippets may establish an explicit closure but never establish a new positive open timestamp.

Positive evidence requires either an exact published Greenhouse/Lever vacancy identifier with the matching application URL, or matching employer JobPosting metadata plus an application control. Fetch success and metadata alone are insufficient. No application is submitted. This does not guarantee that a vacancy cannot close immediately afterwards.

Only `lastConfirmedOpenAt` controls freshness. Unknown or 48-hour-old evidence is excluded from active recommendations, even if the daily workflow fails. A minute timer updates an open jobs view. Previous evidence is not refreshed by blocked requests. Unknown records remain under Sources → Availability unconfirmed. Explicit closure/deadline records remain archived. When a separately stored LinkedIn route closes, it does not close an independently confirmed employer route.

Current records generally have only one exact application URL; the checker cannot infer an equivalent employer requisition from a LinkedIn title. Those blocked LinkedIn-only records remain unconfirmed until an exact employer route is established or public verification becomes available. There is no LinkedIn login, anti-bot bypass or promise of complete LinkedIn coverage.

Audit outcome: Nixon 5 open records (3 reviewed recommendations, 2 awaiting description review), 1 closed and 46 unconfirmed. Sivanesh 0 directly confirmed, 12 already closed and 77 unconfirmed. Existing records and private user work are preserved. The smaller main lists are deliberate.

Validation: endpoint identity, metadata-only rejection, closure versus blocked requests, 48-hour expiry, preserved timestamps and employer/LinkedIn route independence have regression tests. Both mobile previews show the correct active count, no overflow, no broken images and no browser errors. Build allowlist and privacy gates pass. The primary 09:00 IST schedule and search quota are unchanged.
