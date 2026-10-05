"""Employer-first discovery through documented, public recruiting APIs.

API GETs use their documented contracts, not HTML scraping or login bypass.
No application POSTs, authentication, or candidate information are involved.
"""
import datetime as dt
import hashlib
import json
import re
import urllib.parse
from pathlib import Path

API_HOSTS={'api.smartrecruiters.com','api.ashbyhq.com','api.lever.co','boards-api.greenhouse.io'}
JOB_HOSTS={'jobs.smartrecruiters.com','jobs.ashbyhq.com','jobs.lever.co','job-boards.greenhouse.io','boards.greenhouse.io'}

def norm(value):
    return re.sub(r'[^a-z0-9]+',' ',str(value).casefold()).strip()

def exact_key(url):
    u=urllib.parse.urlsplit(url); parts=u.path.strip('/').split('/')
    if u.hostname=='jobs.smartrecruiters.com' and len(parts)==2:
        ident=re.match(r'\d+',parts[1])
        return ('smart',parts[0].lower(),ident[0]) if ident else None
    if u.hostname in ('jobs.ashbyhq.com','jobs.lever.co') and len(parts)>=2:
        return ('ashby' if 'ashby' in u.hostname else 'lever',parts[0].lower(),parts[1])
    if u.hostname in ('job-boards.greenhouse.io','boards.greenhouse.io') and len(parts)==3 and parts[1]=='jobs':
        return ('greenhouse',parts[0].lower(),parts[2])
    return None

def api_url(kind,slug,ident=None,offset=0):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',slug):raise ValueError('Invalid board identifier')
    if ident and not re.fullmatch(r'[A-Za-z0-9_-]+',str(ident)):raise ValueError('Invalid posting identifier')
    if kind=='smart':return f'https://api.smartrecruiters.com/v1/companies/{slug}/postings'+(f'/{ident}' if ident else f'?limit=100&offset={offset}&country=in')
    if kind=='ashby':return f'https://api.ashbyhq.com/posting-api/job-board/{slug}'
    if kind=='lever':return f'https://api.lever.co/v0/postings/{slug}'+(f'/{ident}' if ident else f'?mode=json&limit=20&skip={offset}')
    if kind=='greenhouse':return f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs'+(f'/{ident}' if ident else '')
    raise ValueError('Unsupported public API')

def get_json(fetcher,url):
    # Only endpoints generated above reach this function. Web pages still use robots checks.
    if urllib.parse.urlsplit(url).hostname not in API_HOSTS:return None,'Unsupported API host'
    text,status=fetcher.request(url,headers={'Accept':'application/json'})
    if not text:return None,status
    try:return json.loads(text),status
    except ValueError:return None,'Invalid API JSON'

def normalize(board,row,scan):
    kind,slug=board['kind'],board['slug'];ident=str(row.get('id',''))
    if row.get('active') is False:return None
    title=row.get('name') if kind=='smart' else row.get('text') if kind=='lever' else row.get('title')
    if kind=='smart':
        l=row.get('location',{});loc=l.get('fullLocation') or ', '.join(str(l.get(k,'')) for k in ['city','region','country'])
        remote=l.get('remote') is True
        sections=row.get('jobAd',{}).get('sections',{})
        desc=' '.join(scan.plain(v.get('text','')) for v in sections.values() if isinstance(v,dict))
        url=f'https://jobs.smartrecruiters.com/{slug}/{ident}'
        req=row.get('refNumber','');posted=row.get('releasedDate','')
        company=row.get('company',{}).get('name') or board['company']
    elif kind=='ashby':
        loc=row.get('location','');remote=row.get('isRemote') is True and row.get('workplaceType')!='Hybrid'
        desc=row.get('descriptionPlain') or scan.plain(row.get('descriptionHtml',''))
        url=row.get('jobUrl','');req=ident;posted=row.get('publishedAt','');company=board['company']
        if row.get('isListed') is False:return None
    elif kind=='lever':
        loc=row.get('categories',{}).get('location','');remote=row.get('workplaceType')=='remote'
        desc=scan.plain(row.get('description',''))+' '+' '.join(scan.plain(x.get('content','')) for x in row.get('lists',[]))
        url=row.get('hostedUrl','');req=ident;posted='';company=board['company']
    else:
        loc=row.get('location',{}).get('name','');remote=bool(re.search(r'remote',loc,re.I))
        desc=scan.plain(row.get('content',''));url=row.get('absolute_url','');req=ident;posted=row.get('updated_at','');company=board['company']
    loc=re.sub(r'\bin\b','India',loc,flags=re.I)
    if remote and re.search(r'india',loc,re.I):loc+=' (fully remote India)'
    if not ident or not title or not scan.valid_url(url,JOB_HOSTS):return None
    return dict(id=ident,title=title.strip(),company=company,location=loc,remote=remote,description=desc,url=url,requisition=str(req),posted=posted[:10],api=api_url(kind,slug,ident),kind=kind,slug=slug)

def relevant(row,scan):
    if not scan.ROLE.search(row['title']):return False
    location='Remote India' if row['remote'] and re.search(r'india',row['location'],re.I) else row['location']
    if not scan.is_relevant(row['title'],location,row['description']):return False
    if not re.search(r'chennai|sriperumbudur|oragadam|chengalpattu|thiruvallur|tiruvallur|pallavaram',row['location'],re.I):
        if not row['remote'] or not re.search(r'india',row['location'],re.I):return False
        if re.search(r'(?:must|only|based|reside|located).{0,60}(?:bangalore|bengaluru|pune|mumbai|gujarat|maharashtra)|(?:hybrid|onsite)\s+(?:role|position)|relocat',row['description'],re.I):return False
    return True

def read_board(board,fetcher,scan):
    rows=[];offset=0;complete=False
    for _ in range(20):
        blob,status=get_json(fetcher,api_url(board['kind'],board['slug'],offset=offset))
        if blob is None:return rows,False,status
        batch=blob if isinstance(blob,list) else blob.get('content' if board['kind']=='smart' else 'jobs',[])
        if not isinstance(batch,list):return rows,False,'Malformed job feed'
        rows.extend(batch)
        if board['kind'] in ('ashby','greenhouse') or len(batch)<(20 if board['kind']=='lever' else 100) or board['kind']=='smart' and offset+len(batch)>=blob.get('totalFound',10**9):
            complete=True;break
        offset+=len(batch)
    return rows,complete,'Complete' if complete else 'Page cap reached; absence is not closure'

def discover(data,cfg,scan,cache_dir=None):
    fetcher=scan.Fetcher({**cfg,'allowedHosts':list(set(cfg['allowedHosts'])|API_HOSTS|JOB_HOSTS)})
    now=dt.datetime.now(dt.timezone.utc);stamp=now.isoformat(timespec='seconds');date=now.date().isoformat()
    reports=[];catalog=[];added=0;linked=0
    for board in cfg.get('employerBoards',[]):
        raw,complete,status=read_board(board,fetcher,scan)
        selected=[]
        for row in raw:
            item=normalize(board,row,scan)
            if not item or not relevant(item,scan):continue
            if board['kind'] in ('smart','greenhouse'):
                detail,detail_status=get_json(fetcher,item['api'])
                if not detail:continue
                item=normalize(board,detail,scan)
            if item and relevant(item,scan) and item['description']:
                selected.append(item);catalog.append(item)
        reports.append({'source':'Employer feed: '+board['company'],'status':f'{len(raw)} postings examined; {len(selected)} relevant','detail':status+'; documented public '+board['kind']+' API. Full descriptions required before scoring.'})
        if cache_dir:Path(cache_dir).mkdir(parents=True,exist_ok=True);(Path(cache_dir)/(board['slug']+'.json')).write_text(json.dumps(selected))
        for item in selected:
            key=exact_key(item['url'])
            matches=[j for j in data['jobs'] if exact_key(j['applyUrl'])==key or (j.get('requisition') and j['requisition']==item['requisition'] and norm(j['company'])==norm(item['company']))]
            if not matches:
                # A title/location match is a candidate association, not proof of identical JD.
                matches=[j for j in data['jobs'] if norm(j['company'])==norm(item['company']) and norm(j['title'])==norm(item['title']) and ('chennai' in j['location'].lower())==('chennai' in item['location'].lower())]
                if len(matches)==1:
                    matches[0].update(analysisStatus='needs-review',score=[],reviewNote='Employer vacancy matched by company, exact normalized title and location. Re-review the current employer description before restoring a match score.')
                elif len(matches)>1:matches=[]
            if matches:
                j=matches[0]
                # The API identifier is the authority for the current vacancy. Preserve
                # any prior route as supporting evidence, but use the exact current
                # employer route for application and future availability checks.
                if exact_key(j['applyUrl']) != key:
                    if 'linkedin.com' in j['applyUrl']:
                        j['linkedinUrl']=j['applyUrl']
                    else:
                        j.setdefault('sources',[]).append({'label':'Previous employer route','url':j['applyUrl'],'scope':'Older route retained for provenance; the current exact API vacancy is used for availability.','asOf':date,'checkedOn':date})
                    j['applyUrl']=item['url'];linked+=1
            else:
                node={'title':item['title'],'description':item['description'],'hiringOrganization':{'name':item['company']},'identifier':{'value':item['requisition']},'jobLocation':{'address':{'addressLocality':item['location'],'addressCountry':'IN'}}}
                if item['remote']:
                    node.update(jobLocation=[],jobLocationType='TELECOMMUTE',applicantLocationRequirements={'name':'India'})
                j=scan.extract(node,item['url'],item['company'],date)
                if not j:continue
                data['jobs'].append(j);added+=1
            digest=hashlib.sha256(item['description'].encode()).hexdigest()
            if j.get('employerDescriptionHash') and j['employerDescriptionHash']!=digest:
                j.update(analysisStatus='needs-review',score=[],reviewNote='Employer description changed; match review required.')
            j['employerDescriptionHash']=digest
            j.update(verification='live',availabilityStatus='open',availabilityHold=False,lastConfirmedOpenAt=stamp,availabilityCheckedAt=stamp,availabilityEvidenceUrl=item['api'],availabilityReason='Exact vacancy published in the employer recruiting API with its application route.',checkedOn=date)
            j['employerPostingId']=item['id'];j['employerBoard']=board
            source={'label':'Employer recruiting API','url':item['url'],'scope':'Exact published vacancy; full description available from employer API','asOf':date,'checkedOn':date}
            if not any(s.get('url')==source['url'] for s in j.get('sources',[])):j.setdefault('sources',[]).append(source)
    data.setdefault('run',{})['employerDiscovery']={'checkedAt':stamp,'boards':len(cfg.get('employerBoards',[])),'newLeads':added,'linkedEmployerRoutes':linked,'relevantPostings':len(catalog)}
    coverage=data['run'].get('coverage',[])
    data['run']['coverage']=reports+[c for c in coverage if not c.get('source','').startswith('Employer feed:')]
    return data['run']['employerDiscovery']

if __name__=='__main__':
    import scan,os
    root=Path(__file__).resolve().parents[1];path=root/'site/data/jobs.json'
    data=json.loads(path.read_text());print(discover(data,json.loads((root/'config/search.json').read_text()),scan,os.getenv('EMPLOYER_RESEARCH_CACHE')))
    path.write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n')
