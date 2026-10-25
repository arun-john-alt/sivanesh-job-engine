# Shared discovery and reliability

Both sites consume the canonical `shared/` implementation and source registry from Nixon's repository. Candidate facts, targets and role/location restrictions remain in each site's own config. Supported employer boards are learned from actual vacancy links and the rotating career directory. The registry is a research source list, not a claim of current hiring or location eligibility.

Every replenishment performs source discovery, full-description evidence assessment, availability checks, shortfall accounting, validation and a public-only build. The working buffer is 35 with a minimum target of 20; job supply is not guaranteed. Failing connectors retry once and report independently. A source error never establishes that a vacancy is closed. Scores require at least 100 words of employer description plus relevant responsibility evidence. Rules compare confirmed candidate facts against job text; they are disclosed heuristics, not AI judgment or an ATS score. Unknown salary does not exclude a role. Existing human assessments survive unchanged descriptions. New scores retain unconfirmed skills as gaps, and low-fit automated results are excluded from the active count.

Public recruiting GET responses are cached for at most 45 minutes. Nixon uploads the cache as an artifact retained one day; Sivanesh attempts reuse and falls back to live requests. Cached data retains the original evidence timestamp. No credentials or private candidate data enter this cache. Workday uses direct requests. Both websites remain static; shared runtime and cache are excluded from public builds.

The GitHub engine runs at 9 AM IST with hourly replenishment. A separate hourly recovery workflow checks for a missing/failed run, avoids dispatching while an engine run is active and caps retries at three per 24 hours. This recovers individual workflow failures, but a GitHub-wide outage or dropped schedules can affect both workflows. An independently hosted trigger would need a separate execution service; none has been provisioned or claimed.

`run.reliability` retains seven days of actual observations with source failures, opening counts and shortfalls. The Sources page exposes progress. Seven successful calendar days cannot be certified on deployment day. Review the recorded history after seven days, including Actions deployment outcomes and simulated connector-failure tests. The code already tests failure isolation and conservative scoring.

Career Ops remains a supplemental independent assessment. Its Mac-based deep review is no longer required for routine discovery, basic matching or publication. Its strict recommendations can still overlap; unique additions must be reported honestly.

## Expanded directory and retirement policy — 25 October 2026

The company directory now includes 698 research targets compiled from the existing employer registry, a pinned Chennai community directory and publicly displayed Chennai startup company records. Public company names, domains and career links are retained with attribution; recruiter emails, contacts and source instructions are not imported. Homepage entries follow actual employer-owned career links, never guessed paths. Public network/robots checks and job-level eligibility still determine actual coverage. Directory size is never presented as the number of verified openings.

Company probes run in parallel with a per-company page budget and isolated errors. Unchecked employers take priority over rechecks. Below 20 confirmed assessments, 60 directory targets are attempted per replenishment; below the 35-role buffer, 40; otherwise 20. A larger initial sweep can be run with --directory-limit. Source registry entries learned from actual career links persist in public research state.

Made Card's public posting API returns 404 and its employer-linked public embed explicitly reports jobBoard=null. The invalid feed has been retired from active vacancy polling, with primary evidence recorded; its official careers page remains watched. A daily API check can restore the source if its public feed returns. This does not imply that individual roles were filled.

The user reaffirmed no new login on 25 October. No authenticated external cloud host is connected, so no new hosting account or external scheduler was created. GitHub recovery remains active; the existing Codex follow-up was expanded to check both sites hourly from 09:45 through 14:45 IST. That supplemental check requires the Mac/app running. Routine cloud discovery and publication do not.

Reliability observations use contiguous real IST calendar days. Missing dates, opening shortfalls and source errors remain visible. Fault simulations test recovery today but never count as elapsed production history.

The recovery watchdog now checks actual research freshness and live/repository agreement, including JSON datasets above 1 MiB. Successful publish-only workflows cannot hide overdue discovery. Operator dispatches are distinct from automatic recovery, which retains its own three-attempt budget and 25-minute cooldown. The watchdog uses the same policy in cloud and supplemental local execution. Lowercase Workday locale segments are normalized before selecting a board, and newly learned Workday hosts enter the approved public host set before any request.
