"""Decide whether a serialized workflow should scan or publish today."""
import datetime as dt
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo
try:
    from scripts.opening_pool import inventory, timestamp
except ModuleNotFoundError:
    from opening_pool import inventory, timestamp

IST = ZoneInfo('Asia/Kolkata')


def decision(data, event, requested=False, now=None):
    local = (now or dt.datetime.now(dt.timezone.utc)).astimezone(IST)
    if event != 'schedule' and not (event == 'workflow_dispatch' and requested):
        return False, True, 'Publish only; discovery was not requested.'
    if event == 'schedule' and local.hour < 9:
        return False, False, 'Waiting for the 9 AM IST daily window.'
    run = data.get('run') or {}
    # Older records stored UTC dates only. During the post-9-AM window,
    # the UTC and IST calendar dates agree.
    previous = run.get('scanDateIst') or run.get('checkedOn')
    if previous == local.date().isoformat():
        return False, event != 'schedule', 'Today already has a recorded scan; no search credits used.'
    return True, True, 'Daily scan is due.'


def replenishment_due(data, cfg, event, requested=False, now=None):
    if event != 'schedule' and not (event == 'workflow_dispatch' and requested):
        return False
    if event == 'workflow_dispatch' and requested:
        return True  # Explicit retries refresh employers, never repeat the paid daily search.
    now = now or dt.datetime.now(dt.timezone.utc)
    counts = inventory(data, cfg, now)
    previous = timestamp(data.get('run', {}).get('openingPool', {}).get('lastReplenishedAt'))
    # Credit-free employer checks continue overnight. Refresh a healthy buffer
    # every six hours; a shortfall retries at the next hourly trigger.
    interval = 45*60 if counts['bufferShortfall'] else 6*3600
    return not previous or (now-previous).total_seconds() < 0 or (now-previous).total_seconds() >= interval


if __name__ == '__main__':
    data = json.loads(Path('site/data/jobs.json').read_text())
    cfg = json.loads(Path('config/search.json').read_text())
    scan, publish, reason = decision(data, os.environ['GITHUB_EVENT_NAME'], os.getenv('REQUEST_SCAN') == 'true')
    replenish = scan or replenishment_due(data, cfg, os.environ['GITHUB_EVENT_NAME'], os.getenv('REQUEST_SCAN') == 'true')
    publish = publish or replenish
    if replenish and not scan:
        reason += ' Employer replenishment due; no search API credits used.'
    with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
        out.write(f'scan={str(scan).lower()}\nreplenish={str(replenish).lower()}\npublish={str(publish).lower()}\n')
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as out:
        out.write(reason + '\n')
    print(reason)
