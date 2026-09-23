"""Direct, exact-vacancy availability checks. No search snippets establish openness."""
import datetime as dt
import json
import re
import urllib.parse

TTL_SECONDS = 48 * 60 * 60

def fresh(job, now):
    try:
        stamp = dt.datetime.fromisoformat(job.get('lastConfirmedOpenAt', '').replace('Z', '+00:00'))
        age = (now - stamp).total_seconds()
        return 0 <= age < TTL_SECONDS
    except (ValueError, TypeError):
        return False

def decision(job, text, status, url, scan):
    if status in ('HTTP 404', 'HTTP 410'):
        return 'closed', 'Exact vacancy endpoint returned ' + status
    if not text:
        return 'unconfirmed', status
    host = urllib.parse.urlsplit(url).hostname
    if host in ('boards-api.greenhouse.io', 'api.lever.co'):
        try:
            data = json.loads(text)
            expected = urllib.parse.urlsplit(url).path.rstrip('/').split('/')[-1]
            if str(data.get('id')) != expected:
                return 'unconfirmed', 'API vacancy identifier did not match'
            apply = data.get('absolute_url') or data.get('applyUrl')
            if apply and scan.valid_url(apply, scan_hosts(job, scan)) and scan.canonical(apply).removesuffix('/apply') == scan.canonical(job['applyUrl']):
                return 'open', 'Exact vacancy is published by the employer recruiting API with an application URL'
        except (ValueError, TypeError, AttributeError):
            pass
        return 'unconfirmed', 'API did not establish an exact published vacancy'
    page = scan.Page(); page.feed(text)
    visible = ' '.join(page.text)
    # Ignore related vacancy sections when interpreting closure messages.
    primary = re.split(r'similar jobs|related jobs|recommended jobs', visible, flags=re.I)[0]
    if scan.CLOSED.search(primary[:6000]):
        return 'closed', 'Exact vacancy page explicitly says applications are closed'
    matched = [n for n in scan.job_nodes(page.jsonld) if scan.matches_existing(n, job, url)]
    for node in matched:
        deadline = str(node.get('validThrough', ''))[:10]
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', deadline) and deadline < dt.datetime.now(dt.timezone.utc).date().isoformat():
            return 'closed', 'Exact vacancy application deadline has passed'
    # Metadata alone is insufficient: require application controls on the same page.
    controls = bool(re.search(r'<(?:a|button)\b[^>]*>\s*(?:<[^>]+>\s*)*(?:apply(?:\s+(?:now|for this job))?|submit application)\b', text, re.I))
    form = bool(re.search(r'<form\b', text, re.I) and re.search(r'resume|curriculum vitae|upload cv', primary, re.I))
    if matched and (controls or form):
        return 'open', 'Matching exact JobPosting and application control found on the employer page'
    return 'unconfirmed', 'No matching vacancy plus usable application evidence; metadata or page fetch alone is insufficient'

def scan_hosts(job, scan):
    return {urllib.parse.urlsplit(job['applyUrl']).hostname, 'jobs.lever.co', 'job-boards.greenhouse.io', 'boards.greenhouse.io'}

def endpoint(url):
    u = urllib.parse.urlsplit(url); parts = u.path.strip('/').split('/')
    if u.hostname in ('job-boards.greenhouse.io', 'boards.greenhouse.io') and len(parts) == 3 and parts[1] == 'jobs' and parts[2].isdigit():
        return f'https://boards-api.greenhouse.io/v1/boards/{parts[0]}/jobs/{parts[2]}'
    if u.hostname == 'jobs.lever.co' and len(parts) == 2 and re.fullmatch(r'[a-f0-9-]{36}', parts[1]):
        return f'https://api.lever.co/v0/postings/{parts[0]}/{parts[1]}'
    return url

def audit(data, config, scan):
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.isoformat(timespec='seconds')
    cfg = dict(config)
    cfg['allowedHosts'] = list(set(config['allowedHosts']) | {'www.linkedin.com', 'in.linkedin.com', 'boards-api.greenhouse.io', 'api.lever.co'})
    cfg['maxPageFetches'] = max(100, len(data['jobs']) * 2)
    fetcher = scan.Fetcher(cfg)
    totals = {'confirmed open':0, 'closed':0, 'unconfirmed':0, 'retained within 48h':0}
    for job in sorted(data['jobs'], key=lambda j: j.get('analysisStatus') != 'reviewed'):
        if job.get('verification') == 'closed':
            totals['closed'] += 1
            continue
        job['availabilityCheckedAt'] = stamp
        deadline = job.get('closesOn')
        if deadline and deadline < now.date().isoformat():
            state, reason = 'closed', 'Recorded application deadline has passed'
        else:
            target = endpoint(job['applyUrl'])
            text, status = fetcher.page(target)
            state, reason = decision(job, text, status, target, scan)
        secondary = job.get('linkedinUrl')
        if secondary and scan.canonical(secondary) != scan.canonical(job['applyUrl']):
            secondary_text, secondary_status = fetcher.page(secondary)
            secondary_job = dict(job, applyUrl=secondary)
            secondary_state, secondary_reason = decision(secondary_job, secondary_text, secondary_status, secondary, scan)
            job['linkedinAvailability'] = secondary_state
            job['linkedinAvailabilityReason'] = secondary_reason
            # The employer's exact application route takes precedence over LinkedIn.
        job['availabilityEvidenceUrl'] = endpoint(job['applyUrl'])
        job['availabilityStatus'] = state
        job['availabilityReason'] = reason
        if state == 'open':
            job.update(lastConfirmedOpenAt=stamp, availabilityHold=False, verification='live', checkedOn=now.date().isoformat())
            job['verificationNote'] = reason + '. Application submission was not attempted.'
            totals['confirmed open'] += 1
        elif state == 'closed':
            job.update(verification='closed', availabilityHold=False, verificationNote=reason)
            totals['closed'] += 1
        else:
            job['availabilityHold'] = not fresh(job, now)
            totals['unconfirmed'] += 1
            if not job['availabilityHold']: totals['retained within 48h'] += 1
    return {'source':'Direct application availability', 'status':'; '.join(f'{v} {k}' for k,v in totals.items()), 'detail':'Every non-closed record attempted before discovery. Blocked or unprovable vacancies stay unconfirmed; only positive exact-vacancy evidence refreshes the 48-hour clock. No application was submitted.'}

if __name__ == '__main__':
    from pathlib import Path
    import scan
    root = Path(__file__).resolve().parents[1]
    path = root/'site/data/jobs.json'
    data = json.loads(path.read_text())
    report = audit(data, json.loads((root/'config/search.json').read_text()), scan)
    coverage = data.setdefault('run', {}).setdefault('coverage', [])
    data['run']['coverage'] = [report] + [c for c in coverage if c.get('source') != report['source']]
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2)+'\n')
    print(report['status'])
