#!/usr/bin/env python3
"""Conservative job discovery. Python standard library only.

Public employer pages only; robots respected. Search is opt-in via a GitHub
Actions secret. New jobs are unscored leads, never invented recommendations.
The scanner neither accesses the private workspace nor applies to jobs.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html import unescape
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
AGENT='SivaneshJobEngine/2.0 (public job discovery; no login bypass)'
ROLE=re.compile(r'procurement|purchasing|\bbuyer\b|supply.?chain|material.?plan|demand.?plan|supply.?plan|sourcing',re.I)
EXCLUDE=re.compile(r'\bintern\b|\binternship\b|\bgraduate trainee\b|\bjunior\b|warehouse|SAP.*(?:consultant|implementation|configuration)|\bvice president\b|\bdirector\b',re.I)

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.text=[];self.links=[];self.jsonld=[];self.capture=False;self.buf=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script':
            self.capture=a.get('type','').lower()=='application/ld+json';self.buf=[];self.skip+=1
        elif tag in ('style','noscript'):self.skip+=1
        elif tag=='a' and a.get('href'):self.links.append(a['href'])
    def handle_endtag(self,tag):
        if tag=='script':
            if self.capture:
                try:self.jsonld.append(json.loads(''.join(self.buf)))
                except (ValueError,TypeError):pass
            self.capture=False;self.skip=max(0,self.skip-1)
        elif tag in ('style','noscript'):self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if self.capture:self.buf.append(data)
        elif not self.skip and data.strip():self.text.append(data.strip())


def plain(value):
    if not isinstance(value,str):return ''
    p=Page();p.feed(value);return ' '.join(p.text)

def canonical(url):
    u=urllib.parse.urlsplit(url)
    query=urllib.parse.urlencode([(k,v) for k,v in urllib.parse.parse_qsl(u.query) if not k.startswith('utm_') and k not in ('ref','source','trk')])
    return urllib.parse.urlunsplit((u.scheme,u.netloc,u.path.rstrip('/'),query,''))

def valid_url(url,hosts,resolve=False):
    try:
        u=urllib.parse.urlsplit(url)
        if u.scheme!='https' or u.hostname not in hosts or u.username or u.password or (u.port not in (None,443)):return False
        if resolve:
            addresses=socket.getaddrinfo(u.hostname,443,type=socket.SOCK_STREAM)
            if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):return False
        return True
    except (ValueError,OSError):return False

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self,hosts):self.hosts=hosts
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not valid_url(newurl,self.hosts,True):raise ValueError('Redirect outside approved public hosts')
        return super().redirect_request(req,fp,code,msg,headers,newurl)

class Fetcher:
    def __init__(self,config):
        self.hosts=set(config['allowedHosts']);self.delay=config.get('requestDelaySeconds',1.2);self.limit=config.get('maxPageFetches',18);self.count=0;self.robot_cache={};self.last=0
        self.opener=urllib.request.build_opener(SafeRedirect(self.hosts|{'api.search.brave.com'}))
    def request(self,url,headers=None):
        hosts=self.hosts|{'api.search.brave.com'}
        if not valid_url(url,hosts,True):return None,'Not an approved public HTTPS endpoint'
        time.sleep(max(0,self.delay-(time.monotonic()-self.last)));self.last=time.monotonic()
        try:
            req=urllib.request.Request(url,headers={'User-Agent':AGENT,**(headers or {})})
            with self.opener.open(req,timeout=15) as res:
                raw=res.read(2_000_001)
                if len(raw)>2_000_000:return None,'Response too large'
                return raw.decode('utf-8',errors='replace'),'HTTP '+str(res.status)
        except urllib.error.HTTPError as e:return None,'HTTP '+str(e.code)
        except (urllib.error.URLError,TimeoutError,ValueError,OSError) as e:return None,type(e).__name__+': '+str(e)[:160]
    def allowed(self,url):
        u=urllib.parse.urlsplit(url);base=u.scheme+'://'+u.netloc
        if base not in self.robot_cache:
            text,status=self.request(base+'/robots.txt')
            if status=='HTTP 404':self.robot_cache[base]=True
            elif text is None:self.robot_cache[base]=False
            else:
                robot=urllib.robotparser.RobotFileParser();robot.set_url(base+'/robots.txt');robot.parse(text.splitlines());self.robot_cache[base]=robot
        r=self.robot_cache[base]
        return r if isinstance(r,bool) else r.can_fetch(AGENT,url)
    def page(self,url):
        if self.count>=self.limit:return None,'Fetch budget reached'
        if not valid_url(url,self.hosts):return None,'Host not approved'
        if not self.allowed(url):return None,'Skipped: robots disallow or robots could not be checked'
        self.count+=1
        return self.request(url)


def job_nodes(value):
    if isinstance(value,list):
        for v in value:yield from job_nodes(v)
    elif isinstance(value,dict):
        kind=value.get('@type',[])
        if kind=='JobPosting' or isinstance(kind,list) and 'JobPosting' in kind:yield value
        for key in ('@graph','itemListElement','item'):
            if key in value:yield from job_nodes(value[key])


def is_relevant(title,location,description):
    if not ROLE.search(title) or EXCLUDE.search(title):return False
    loc=location.lower();text=(title+' '+description).lower()
    if 'chennai' not in loc and not ('india' in loc and 'remote' in loc):return False
    years=re.search(r'(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years|yrs)',text)
    if years and (int(years[1])>8 or int(years[2])<4):return False
    return True


def extract(node,url,default_company,now):
    title=plain(node.get('title',''));desc=plain(node.get('description',''))
    org=node.get('hiringOrganization') or {};company=(plain(org.get('name','')) or default_company) if isinstance(org,dict) else default_company
    rawloc=node.get('jobLocation') or [];rawloc=rawloc if isinstance(rawloc,list) else [rawloc]
    locs=[]
    for obj in rawloc:
        if not isinstance(obj,dict):continue
        address=obj.get('address',{})
        if isinstance(address,dict):
            country=address.get('addressCountry','');country=country.get('name','') if isinstance(country,dict) else country
            if country=='IN':country='India'
            locs.append(', '.join(str(address[k]) for k in ['addressLocality','addressRegion'] if address.get(k))+(', '+country if country else ''))
    remote=node.get('jobLocationType')=='TELECOMMUTE'
    if remote:
        restrictions=node.get('applicantLocationRequirements') or []
        restrictions=restrictions if isinstance(restrictions,list) else [restrictions]
        if any('india' in str(x).lower() or isinstance(x,dict) and x.get('name')=='IN' for x in restrictions):locs.append('Remote India')
    location=' / '.join(locs)
    if remote and location:location+=' (remote)'
    if not is_relevant(title,location,desc):return None
    ident=node.get('identifier') or {};req=str(ident.get('value','') if isinstance(ident,dict) else ident)
    uid=re.sub('[^a-z0-9-]','',company.lower().replace(' ','-'))[:30]+'-'+hashlib.sha256((company+'|'+(req or canonical(url))).encode()).hexdigest()[:12]
    source={'label':'Employer job posting','url':url,'scope':'Public JobPosting metadata','asOf':now,'checkedOn':now}
    salary={'kind':'unknown','minLpa':None,'maxLpa':None,'basis':'Unknown','confidence':'Unknown','note':'No defensible salary estimate generated. Ask for the annual fixed/variable split and total CTC.','sources':[]}
    rawsalary=node.get('baseSalary') or {}
    if not isinstance(rawsalary,dict):rawsalary={}
    value=rawsalary.get('value',{})
    if rawsalary.get('currency')=='INR' and isinstance(value,dict) and value.get('unitText','').upper() in ('YEAR','ANNUAL'):
        lo=value.get('minValue',value.get('value'));hi=value.get('maxValue',value.get('value'))
        if isinstance(lo,(int,float)) and isinstance(hi,(int,float)) and 100000<=lo<=hi<=100000000:
            salary.update(kind='employer-disclosed',minLpa=round(lo/100000,2),maxLpa=round(hi/100000,2),basis='Annual base pay',confidence='Employer metadata; verify',note='Employer JobPosting baseSalary metadata. Annual base pay is not necessarily total CTC.',sources=[source])
    closing=str(node.get('validThrough') or '')[:10]
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',closing):closing=None
    posted=str(node.get('datePosted') or '')[:10]
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',posted):posted=None
    return dict(id=uid,company=company,title=title,location=location,workModel='Remote - verify eligibility' if remote else 'Not specified',family='Needs classification',experience=plain(node.get('experienceRequirements','')) or 'Review full JD',requisition=req,applyUrl=canonical(url),linkedinUrl=None,postedOn=posted,closesOn=closing,discoveredOn=now,checkedOn=now,verification='closed' if closing and closing<now else 'live',verificationNote='Employer JobPosting metadata fetched directly. This checks the page, not completion of the application form.',analysisStatus='needs-review',score=[],summary=' '.join(desc.split()[:90]),hardGaps=['Full JD and candidate evidence require review before scoring.'],benefits=[],risks=['Compensation and team conditions unverified.'],questions=['Confirm role level, salary budget, work model and required experience.'],salary=salary,culture={'summary':'Not researched; no review claims generated.','signals':[],'sources':[]},ats={'supported':[],'confirm':[],'unsupported':[]},resumeEdits=[],sources=[source])


def run(config_path,data_path):
    cfg=json.loads(config_path.read_text());data=json.loads(data_path.read_text());now=dt.datetime.now(dt.timezone.utc).date().isoformat();fetcher=Fetcher(cfg)
    coverage=[];queue=[];known={canonical(j['applyUrl']):j for j in data['jobs']};seen=set();new_count=0;success=0
    for job in data['jobs']:queue.append((job['applyUrl'],job['company'],True))
    for watch in cfg.get('watchPages',[]):queue.append((watch['url'],watch['company'],False))
    key=os.getenv('BRAVE_SEARCH_API_KEY')
    if key:
        search_ok=0
        for q in cfg.get('queries',[])[:5]:
            url='https://api.search.brave.com/res/v1/web/search?'+urllib.parse.urlencode({'q':q,'count':8,'freshness':'pm','country':'IN','search_lang':'en'})
            text,status=fetcher.request(url,{'X-Subscription-Token':key})
            if not text:coverage.append({'source':'Web search','status':'Failed','detail':status});continue
            try:results=json.loads(text).get('web',{}).get('results',[])
            except ValueError:coverage.append({'source':'Web search','status':'Failed','detail':'Non-JSON response'});continue
            search_ok+=1
            for row in results:
                u=row.get('url','')
                if valid_url(u,fetcher.hosts):queue.append((u,urllib.parse.urlsplit(u).hostname,True))
        coverage.append({'source':'Brave web discovery','status':str(search_ok)+' queries completed','detail':'Public search only; only approved employer hosts are fetched. No claim of complete job-board coverage.'})
    else:coverage.append({'source':'Broad web discovery','status':'Not configured','detail':'No BRAVE_SEARCH_API_KEY secret. Only the employer watchlist and existing roles are checked.'})
    while queue and fetcher.count<fetcher.limit:
        url,company,is_job=queue.pop(0);url=canonical(url)
        if url in seen:continue
        seen.add(url);text,status=fetcher.page(url);existing=known.get(url)
        if not text:
            if existing and status in ('HTTP 404','HTTP 410'):
                existing['verification']='closed';existing['checkedOn']=now;existing['verificationNote']='Employer returned '+status+'. Confirm before attempting to apply.'
            coverage.append({'source':company,'status':status,'detail':url});continue
        page=Page();page.feed(text);nodes=list(job_nodes(page.jsonld));visible=' '.join(page.text)
        if existing:
            same_job=any(plain(n.get('title','')).lower()==existing['title'].lower() for n in nodes)
            if same_job:
                existing['verification']='live';existing['checkedOn']=now;existing['verificationNote']='Matching employer JobPosting metadata fetched directly. Application submission was not attempted.';success+=1
            elif re.search(r'this job is no longer available|this position has been filled|this job has expired',visible,re.I):
                existing['verification']='closed';existing['checkedOn']=now;existing['verificationNote']='Employer page explicitly indicates closure.';success+=1
            else:coverage.append({'source':company,'status':'Unresolved','detail':'Page fetched but exact JobPosting could not be confirmed. Prior evidence retained: '+url})
        for node in nodes:
            item=extract(node,url,company,now)
            if not item:continue
            u=canonical(item['applyUrl'])
            if u in known:
                # Never overwrite a reviewed human analysis with a crawler draft.
                if item['closesOn']:known[u]['closesOn']=item['closesOn']
                if item['salary']['kind']=='employer-disclosed':known[u]['salary']=item['salary']
                if item['verification']=='closed':known[u]['verification']='closed'
                continue
            if any(item['requisition'] and item['company'].lower()==j['company'].lower() and item['requisition']==j.get('requisition') for j in data['jobs']):continue
            data['jobs'].append(item);known[u]=item;new_count+=1;success+=1
        if not is_job:
            for href in page.links:
                candidate=urllib.parse.urljoin(url,href)
                if valid_url(candidate,fetcher.hosts) and re.search(r'/job/|/jobs/|gh_jid=',candidate,re.I):queue.append((candidate,company,True))
        coverage.append({'source':company,'status':'Fetched','detail':url+(' - job metadata found' if nodes else ' - no structured job data')})
    coverage.append({'source':'Salary, culture and resume analysis','status':'Human review required','detail':'New leads are unscored. The crawler never invents pay, reviews, candidate achievements or tailored bullets.'})
    data['updatedAt']=now;data['run']={'status':'completed' if success else 'limited','checkedOn':now,'automaticEnabled':os.getenv('GITHUB_ACTIONS')=='true','note':f'{new_count} new lead(s); {success} job metadata / closure check(s). Failed or unresolved checks do not establish availability. Broad discovery requires the search API secret.','coverage':coverage[:40]}
    temp=data_path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=True,indent=2)+'\n');temp.replace(data_path)
    print(data['run']['note'])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,default=ROOT/'config/search.json');parser.add_argument('--data',type=Path,default=ROOT/'site/data/jobs.json');args=parser.parse_args();run(args.config,args.data)
