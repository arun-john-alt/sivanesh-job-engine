"""Read public SuccessFactors JobPosting microdata without executing page scripts."""
import datetime as dt
import re
import urllib.parse
from html.parser import HTMLParser

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Element:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []
    def text(self):
        if self.tag in ('script','style','noscript'): return ''
        return ' '.join(c if isinstance(c,str) else c.text() for c in self.children)
    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Element): yield from c.walk()

class Tree(HTMLParser):
    def __init__(self):
        super().__init__(); self.root=Element(); self.stack=[self.root]
    def handle_starttag(self, tag, attrs):
        e=Element(tag,attrs); self.stack[-1].children.append(e)
        if tag not in VOID:self.stack.append(e)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:
                del self.stack[i:];break
    def handle_data(self, data):self.stack[-1].children.append(data)

def clean(text):return re.sub(r'\s+',' ',text).strip()
def date(value):
    for fmt in ('%a %b %d %H:%M:%S UTC %Y','%d/%m/%Y','%Y-%m-%d'):
        try:return dt.datetime.strptime(value,fmt).date().isoformat()
        except ValueError:pass
    return None

def read(html):
    tree=Tree();tree.feed(html);all_nodes=list(tree.root.walk())
    roots=[e for e in all_nodes if e.attrs.get('itemtype','').rstrip('/').endswith('/JobPosting')]
    if len(roots)!=1:return None
    canonical=next((e.attrs.get('href','') for e in all_nodes if e.tag=='link' and e.attrs.get('rel')=='canonical'),'')
    u=urllib.parse.urlsplit(canonical)
    ident=re.search(r'/job/[^/]+/(\d+)(?:-[^/]+)?/?$',u.path)
    if u.scheme!='https' or not ident:return None
    ident=ident[1]
    props={}
    for e in roots[0].walk():
        name=e.attrs.get('itemprop')
        if name:props[name]=clean(e.attrs.get('content') or e.text())
    if not props.get('title'):
        titles=[clean(e.text()) for e in all_nodes if e.attrs.get('itemprop')=='title']
        if len(titles)==1:props['title']=titles[0]
    if not props.get('title') or len(props.get('description',''))<100:return None
    # Identity-bound application route, not a generic "Join our talent community" CTA.
    controls=[]
    for e in all_nodes:
        if e.tag!='a' or not re.match(r'apply\b',clean(e.text()),re.I):continue
        dest=urllib.parse.urlsplit(urllib.parse.urljoin(canonical,e.attrs.get('href','')))
        if dest.scheme=='https' and dest.netloc==u.netloc and dest.path.rstrip('/')==f'/talentcommunity/apply/{ident}':controls.append(dest.geturl())
    # SAP's embedded manual-apply controller binds a visible control to one job.
    manual=any(e.attrs.get('id')=='applyOption--manual' and re.match(r'apply\b',clean(e.text()),re.I) for e in all_nodes)
    bound=re.search(r'j2w\.Apply\.init\(\{\s*jobID\s*:\s*[\"\']?'+re.escape(ident)+r'[\"\']?\s*,',html)
    if manual and bound:controls.append(canonical)
    visible=clean(tree.root.text())
    locality=props.get('addressLocality') or props.get('streetAddress') or ''
    if not locality:
        match=re.search(r'Job Location(?: \(Short\))?:\s*(.+?)(?= Global Grade:| Contract Type:| Employment Type:| Work Type:| Job Experience| Segment:)',visible,re.I)
        if match:locality=match[1].strip()
    if not locality and u.hostname=='careers.hcltech.com':
        # The location is rendered in the primary job description header.
        m=re.search(r'Job Description\s+'+re.escape(props['title'])+r'\s+(.+?)(?= Job Summary)',visible)
        if m:locality=m[1].strip()
    deadline=date(props.get('validThrough',''))
    if not deadline:
        m=re.search(r'Posting End Date:\s*(\d{2}/\d{2}/\d{4})',visible)
        if m:deadline=date(m[1])
    if not deadline:
        m=re.search(r'apply on or before\s+(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})',visible,re.I)
        if m:
            for fmt in ('%d %b %Y','%d %B %Y'):
                try:deadline=dt.datetime.strptime(' '.join(m.groups()),fmt).date().isoformat();break
                except ValueError:pass
    node={'@type':'JobPosting','title':props['title'],'description':props['description'],'url':canonical,
          'hiringOrganization':{'name':props.get('hiringOrganization','')},
          'identifier':{'value':ident},'jobLocation':{'address':{'addressLocality':locality,'addressRegion':props.get('addressRegion',''),'addressCountry':props.get('addressCountry','')}},
          'datePosted':date(props.get('datePosted','')),'validThrough':deadline,
          '_applicationRoute':controls[0] if controls else None}
    return node
