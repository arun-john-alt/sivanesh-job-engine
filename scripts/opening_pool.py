"""Bounded replenishment policy. Never relax eligibility or manufacture match scores."""
import argparse
import copy
import datetime as dt
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo('Asia/Kolkata')
ROOT = Path(__file__).resolve().parents[1]


def timestamp(value):
    try:
        parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed if parsed.tzinfo else None
    except (ValueError, AttributeError, TypeError):
        return None


def inventory(data, cfg, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    target = max(20, int(cfg.get('openingPool', {}).get('minimum', 20)))
    buffer = max(target, int(cfg.get('openingPool', {}).get('buffer', 25)))
    reviewed = pending = 0
    seen = set()
    for job in data.get('jobs', []):
        last = timestamp(job.get('lastConfirmedOpenAt'))
        if job.get('assessmentTier') == 'weak' or job.get('discoveryEligible') is False or job.get('verification') == 'closed' or job.get('availabilityHold') is True:
            continue
        if not last or not 0 <= (now-last).total_seconds() < 48*3600:
            continue
        if job.get('closesOn') and job['closesOn'] < now.astimezone(IST).date().isoformat():
            continue
        salary = job.get('salary') or {}
        ceiling = salary.get('maxLpa')
        if salary.get('kind') == 'employer-disclosed' and salary.get('basis') == 'Annual CTC' and isinstance(ceiling, (int, float)) and ceiling < cfg['minimumTargetLpa']:
            continue
        # Match the public dataset's unique application route contract.
        route = job.get('applyUrl', '').rstrip('/')
        if not route or route in seen:
            continue
        seen.add(route)
        if job.get('analysisStatus') == 'reviewed' and len(job.get('score', [])) == 5:
            reviewed += 1
        else:
            pending += 1
    return {'minimum': target, 'buffer': buffer, 'reviewedOpen': reviewed,
            'pendingOpen': pending, 'shortfall': max(0, target-reviewed),
            'bufferShortfall': max(0, buffer-reviewed)}


def plan(data, cfg, now=None):
    """Escalate source breadth, not fit rules. The reserve is an approved catalog."""
    counts = inventory(data, cfg, now)
    previous = data.get('run', {}).get('openingPool', {})
    attempts = int(previous.get('consecutiveShortfalls', 0))
    level = 0 if not counts['bufferShortfall'] else 2 if counts['shortfall'] >= 10 or attempts >= 2 else 1
    selected = copy.deepcopy(cfg)
    boards = selected.get('employerBoards', [])
    reserve = selected.get('reserveEmployerBoards', [])
    extra = reserve if level == 2 else reserve[:12] if level == 1 else []
    seen = {(b['kind'], b['slug']) for b in boards}
    for board in extra:
        if (board['kind'], board['slug']) not in seen:
            boards.append(board)
            seen.add((board['kind'], board['slug']))
    if level:
        regions = ['Chennai', 'remote India', 'Sriperumbudur', 'Oragadam', 'Thiruvallur', 'Chengalpattu']
        # Different Chennai-region locations can be indexed separately by Workday.
        for board in boards:
            if board['kind'] == 'workday':
                board['searchTerms'] = list(dict.fromkeys(board.get('searchTerms', []) + regions[:2+2*level]))
    return selected, {**counts, 'expansionLevel': level, 'boardsPlanned': len(boards)}


def record(data, cfg, planned, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    counts = inventory(data, cfg, now)
    run = data.setdefault('run', {})
    previous = run.get('openingPool', {})
    report = {**counts, 'expansionLevel': planned.get('expansionLevel', 0),
              'boardsPlanned': planned.get('boardsPlanned', 0),
              'lastReplenishedAt': now.isoformat(timespec='seconds'),
              'consecutiveShortfalls': int(previous.get('consecutiveShortfalls', 0))+1 if counts['shortfall'] else 0,
              'status': 'shortfall' if counts['shortfall'] else 'target-met',
              'nextCheckAfter': (now+dt.timedelta(minutes=45 if counts['bufferShortfall'] else 360)).isoformat(timespec='seconds')}
    run['openingPool'] = report
    detail = (f"{counts['reviewedOpen']}/{counts['minimum']} reviewed, confirmed openings; "
              f"{counts['pendingOpen']} additional confirmed vacancies awaiting match review. "
              f"Expansion level {report['expansionLevel']}; {report['boardsPlanned']} employer sources planned. "
              'Hourly credit-free checks replenish toward a buffer of 35. Broad search remains once daily at 9 AM IST. '
              'No expired, unconfirmed, excluded or unscored role counts toward the minimum. GitHub schedules may be delayed.')
    run['coverage'] = [{'source': 'Opening target', 'status': f"{counts['reviewedOpen']}/{counts['minimum']} confirmed matches", 'detail': detail}] + [c for c in run.get('coverage', []) if c.get('source') != 'Opening target']
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as out:
            out.write(detail+'\n')
    print(detail)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'record'])
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    path = ROOT/'site/data/jobs.json'
    data = json.loads(path.read_text())
    cfg = json.loads((ROOT/'config/search.json').read_text())
    if args.mode == 'prepare':
        selected, planned = plan(data, cfg)
        args.plan.write_text(json.dumps({'config': selected, 'planned': planned}))
        args.plan.with_suffix('.config.json').write_text(json.dumps(selected))
        print(planned)
    else:
        record(data, cfg, json.loads(args.plan.read_text())['planned'])
        path.write_text(json.dumps(data, ensure_ascii=True, indent=2)+'\n')
