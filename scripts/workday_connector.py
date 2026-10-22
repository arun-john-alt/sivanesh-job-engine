"""Read public employer career-search data. Robots rules apply; no application submission."""
import datetime as dt
import json
import re
import urllib.parse

def parts(url):
    try:
        u=urllib.parse.urlsplit(url)
        port=u.port
    except (ValueError,TypeError):return None
    if u.scheme!='https' or not re.fullmatch(r'[a-z0-9-]+\.wd\d+\.myworkdayjobs\.com',u.hostname or '') or u.username or u.password or port not in (None,443):return None
    path=u.path.strip('/').split('/')
    if path and re.fullmatch(r'[a-z]{2}-[A-Z]{2}',path[0]):path=path[1:]
    if len(path)<3 or path[1]!='job' or path[-1]=='apply':return None
    return u.hostname,path[0],'/'+ '/'.join(path[1:])

def endpoint(url,tenant=None):
    p=parts(url)
    if not p:return None
    host,site,path=p
    return f'https://{host}/wday/cxs/{tenant or host.split(".")[0]}/{site}{path}'

def read(fetcher,url,payload=None):
    if not fetcher.allowed(url):return None,'Robots disallow or unavailable'
    text,status=fetcher.request(url,headers={'Accept':'application/json','Content-Type':'application/json'},payload=payload)
    if not text:return None,status
    try:return json.loads(text),status
    except ValueError:return None,'Invalid career JSON'

def check(job,fetcher,scan):
    url=endpoint(job['applyUrl'])
    if not url:return None
    blob,status=read(fetcher,url)
    if not isinstance(blob,dict):return 'unconfirmed','Employer career data unavailable: '+status,url
    info=blob.get('jobPostingInfo') or {}
    if not info or parts(info.get('externalUrl',''))!=parts(job['applyUrl']):return 'unconfirmed','Exact employer vacancy identity could not be established',url
    if job.get('requisition') and info.get('jobReqId')!=job['requisition']:return 'unconfirmed','Employer requisition does not match the stored record',url
    if info.get('canApply') is False or info.get('posted') is False:return 'closed','Employer explicitly marks this vacancy non-applicable or unpublished',url
    if info.get('endDate') and info['endDate'][:10]<dt.datetime.now(dt.timezone(dt.timedelta(hours=5,minutes=30))).date().isoformat():return 'closed','Employer application deadline passed',url
    if info.get('canApply') is True and info.get('posted') is True:return 'open','Exact employer career record explicitly permits applications',url
    return 'unconfirmed','Employer did not establish that applications are accepted',url

def read_board(board,fetcher,scan):
    host=board['host'];tenant=board['slug'];site=board['site']
    if not re.fullmatch(r'[a-z0-9-]+\.wd\d+\.myworkdayjobs\.com',host) or not all(re.fullmatch(r'[A-Za-z0-9_-]+',x) for x in (tenant,site)):return [],False,'Invalid career-site configuration'
    rows=[];seen=set();complete=True
    for query in board.get('searchTerms',['Chennai','remote India']):
        for offset in range(0,400,20):
            blob,status=read(fetcher,f'https://{host}/wday/cxs/{tenant}/{site}/jobs',{'appliedFacets':{},'limit':20,'offset':offset,'searchText':query})
            if not isinstance(blob,dict) or not isinstance(blob.get('jobPostings'),list):complete=False;break
            batch=blob['jobPostings']
            for row in batch:
                title=row.get('title','');loc=row.get('locationsText','');path=row.get('externalPath','')
                if path in seen or not path.startswith('/job/') or not scan.ROLE.search(title) or scan.EXCLUDE.search(title):continue
                seen.add(path)
                # Pre-filter location; full role eligibility is checked after detail retrieval.
                if not re.search(r'chennai|sriperumbudur|oragadam|chengalpattu|thiruvallur|tiruvallur|pallavaram|remote|india|\d+ locations|multiple locations',loc,re.I):continue
                detail,ds=read(fetcher,f'https://{host}/wday/cxs/{tenant}/{site}{path}')
                if not isinstance(detail,dict):continue
                info=detail.get('jobPostingInfo',{})
                url=info.get('externalUrl','')
                if parts(url)!=(host,site,path) or info.get('canApply') is not True or info.get('posted') is not True:continue
                deadline=info.get('endDate','')[:10]
                if deadline and deadline<dt.datetime.now(dt.timezone(dt.timedelta(hours=5,minutes=30))).date().isoformat():continue
                location=info.get('location',loc)
                locations=info.get('additionalLocations',[])
                if locations:location+=' / '+' / '.join(str(x) for x in locations)
                remote=bool(re.search(r'fully remote|^remote$',info.get('remoteType',''),re.I))
                company=detail.get('hiringOrganization',{}).get('name') if tenant=='hitachi' else board['company']
                rows.append({'id':info.get('jobReqId',''),'title':info.get('title',title),'location':location,'remote':remote,'description':scan.plain(info.get('jobDescription','')),'url':url,'requisition':info.get('jobReqId',''),'posted':info.get('startDate','')[:10],'closesOn':deadline or None,'api':f'https://{host}/wday/cxs/{tenant}/{site}{path}','kind':'workday','slug':tenant,'company':company or board['company']})
            if len(batch)<20 or offset+len(batch)>=blob.get('total',0):break
        else:complete=False
    return rows,complete,'Search complete' if complete else 'Partial career search; absence is not closure'
