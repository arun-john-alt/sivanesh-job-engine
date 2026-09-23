/* Pure domain logic. No network, secrets, or DOM dependencies. */
export const STAGES = ['Discovered','Reviewed','Shortlisted','Resume Tailored','Applied','Interview','Offer','Closed'];
export const DEFAULTS = {currentCtcLpa:null,targetCtcLpa:12,goalDate:'2026-12-31',weeklyApplications:5,noticeDays:null,repoUrl:''};
export const clone = x => JSON.parse(JSON.stringify(x));
export const esc = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function safeURL(value) {
  try { const u=new URL(String(value)); return u.protocol==='https:' && !u.username && !u.password ? u.href : ''; } catch { return ''; }
}
export function day(value) { if(typeof value!=='string' || !/^\d{4}-\d{2}-\d{2}/.test(value))return null; const d=new Date(value.slice(0,10)+'T00:00:00Z'); return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===value.slice(0,10)?d:null; }
export function today() { return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date()); }
export function daysBetween(a,b){ const x=day(a),y=day(b);return x&&y?Math.round((y-x)/86400000):null; }
export function scoreOf(job){ if(job.analysisStatus!=='reviewed'||!Array.isArray(job.score)||job.score.length!==5)return null;return job.score.reduce((s,c)=>s+c.points,0); }
export function fitOf(job){ const n=scoreOf(job);return n===null?'Needs review':n>=80?'High fit':n>=65?'Medium fit':'Low fit'; }
export function isExpired(job,now=today()){ return job.verification==='closed'||Boolean(job.closesOn&&day(job.closesOn)&&daysBetween(job.closesOn,now)>0); }
export function availabilityFresh(job,now=today()){const t=Date.parse(job.lastConfirmedOpenAt||'');const n=now===today()?Date.now():Date.parse(now+'T00:00:00Z');return Number.isFinite(t)&&n>=t&&n-t<48*60*60*1000;}
export function isUnavailable(job,now=today()){return isExpired(job,now)||job.availabilityHold===true||!availabilityFresh(job,now);}
export function stale(job,now=today()){ const age=daysBetween(job.checkedOn,now); return age===null||age>7; }
export function payGate(job,target=12){
  const s=job.salary||{};
  if(s.kind==='employer-disclosed'&&s.basis==='Annual CTC'&&Number.isFinite(s.maxLpa)&&s.maxLpa<target)return 'Below target';
  if(s.kind==='employer-disclosed'&&s.basis==='Annual CTC'&&Number.isFinite(s.minLpa)&&s.minLpa>=target)return 'Meets target';
  if(s.kind==='employer-disclosed'&&s.basis==='Annual CTC'&&Number.isFinite(s.maxLpa)&&s.maxLpa>=target)return 'Range overlaps';
  return 'Budget unknown';
}
export function increase(offer,current){return Number.isFinite(offer)&&Number.isFinite(current)&&current>0?(offer/current-1)*100:null;}
export function applicationFor(workspace,id){return workspace.applications?.[id]||{stage:'Discovered',notes:'',nextAction:'',followUpOn:'',history:[]};}
export function canonicalURL(value){const s=safeURL(value);if(!s)return '';const u=new URL(s);for(const k of [...u.searchParams.keys()])if(k.startsWith('utm_')||['source','ref','trk','trackingId'].includes(k))u.searchParams.delete(k);u.hash='';return u.href.replace(/\/$/,'');}
const cleanStr=(s,n=20000)=>typeof s==='string'?s.slice(0,n):'';
const strings=(a)=>Array.isArray(a)?a.slice(0,100).map(x=>cleanStr(x,3000)).filter(Boolean):[];
const dateOrNull=v=>day(v)?String(v).slice(0,10):null;
function sources(a){return Array.isArray(a)?a.slice(0,30).map(s=>({label:cleanStr(s.label,300),url:safeURL(s.url),scope:cleanStr(s.scope,1500),asOf:cleanStr(s.asOf,100),checkedOn:dateOrNull(s.checkedOn)})).filter(s=>s.url):[];}
export function validateDataset(raw){
  if(raw?.schemaVersion!==2||!Array.isArray(raw.jobs))throw new Error('Expected a version 2 public dataset with a jobs array.');
  if(raw.jobs.length>1000)throw new Error('Dataset limit is 1,000 jobs.');
  const ids=new Set(),urls=new Set();const jobs=raw.jobs.map(j=>{
    if(!j||!/^[a-z0-9][a-z0-9_-]{2,119}$/i.test(j.id)||['__proto__','constructor','prototype'].includes(j.id))throw new Error('Invalid job ID.');
    if(ids.has(j.id))throw new Error('Duplicate job ID: '+j.id);ids.add(j.id);
    const url=canonicalURL(j.applyUrl);if(!url)throw new Error('Each job requires an HTTPS application link.');
    if(urls.has(url))throw new Error('Duplicate application URL: '+j.id);urls.add(url);
    if(!j.title||!j.company)throw new Error('Each job needs a title and company.');
    const score=Array.isArray(j.score)?j.score.map(c=>({name:cleanStr(c.name,100),weight:Number(c.weight),points:Number(c.points),reason:cleanStr(c.reason,2000)})):[];
    if(score.length && (score.length!==5||score.reduce((s,c)=>s+c.weight,0)!==100||score.some(c=>!Number.isFinite(c.points)||!Number.isFinite(c.weight)||c.weight<=0||c.points<0||c.points>c.weight)))throw new Error('Invalid score breakdown: '+j.id);
    const sal=j.salary||{};const min=Number.isFinite(sal.minLpa)?sal.minLpa:null,max=Number.isFinite(sal.maxLpa)?sal.maxLpa:null;
    if((min!==null&&min<0)||(max!==null&&max<0)||(min!==null&&max!==null&&min>max))throw new Error('Invalid salary range.');
    const ssrc=sources(sal.sources);if(['employer-disclosed','third-party'].includes(sal.kind)&&!ssrc.length)throw new Error('Salary claims require a source.');
    return {id:j.id,company:cleanStr(j.company,200),title:cleanStr(j.title,300),family:cleanStr(j.family,100),location:cleanStr(j.location,300),workModel:cleanStr(j.workModel,200)||'Not specified',experience:cleanStr(j.experience,1000)||'Not verified',requisition:cleanStr(j.requisition,120),applyUrl:url,linkedinUrl:safeURL(j.linkedinUrl)||null,postedOn:dateOrNull(j.postedOn),closesOn:dateOrNull(j.closesOn),discoveredOn:dateOrNull(j.discoveredOn),checkedOn:dateOrNull(j.checkedOn),availabilityAttemptedOn:dateOrNull(j.availabilityAttemptedOn),availabilityHold:j.availabilityHold===true,lastConfirmedOpenAt:cleanStr(j.lastConfirmedOpenAt,40),availabilityCheckedAt:cleanStr(j.availabilityCheckedAt,40),availabilityEvidenceUrl:safeURL(j.availabilityEvidenceUrl),availabilityStatus:cleanStr(j.availabilityStatus,30),availabilityReason:cleanStr(j.availabilityReason,1000),verification:['indexed','live','closed','unverified'].includes(j.verification)?j.verification:'unverified',verificationNote:cleanStr(j.verificationNote),analysisStatus:j.analysisStatus==='reviewed'&&score.length===5?'reviewed':'needs-review',score,reviewNote:cleanStr(j.reviewNote,1500),summary:cleanStr(j.summary),hardGaps:strings(j.hardGaps),benefits:strings(j.benefits),risks:strings(j.risks),questions:strings(j.questions),salary:{kind:['unknown','employer-disclosed','third-party'].includes(sal.kind)?sal.kind:'unknown',minLpa:min,maxLpa:max,basis:cleanStr(sal.basis,100)||'Unknown',confidence:cleanStr(sal.confidence,100)||'Unknown',note:cleanStr(sal.note),historicalRange:cleanStr(sal.historicalRange,500),sources:ssrc},culture:{summary:cleanStr(j.culture?.summary),signals:strings(j.culture?.signals),sources:sources(j.culture?.sources)},ats:{supported:strings(j.ats?.supported),confirm:strings(j.ats?.confirm),unsupported:strings(j.ats?.unsupported)},resumeEdits:Array.isArray(j.resumeEdits)?j.resumeEdits.slice(0,30).filter(e=>/^[a-z0-9-]+$/i.test(e.id)&&validResumePath(e.path)).map(e=>({id:e.id,path:e.path,proposed:cleanStr(e.proposed),reason:cleanStr(e.reason),evidence:cleanStr(e.evidence)})):[],sources:sources(j.sources)};
  });
  return {schemaVersion:2,updatedAt:cleanStr(raw.updatedAt,60),run:{status:cleanStr(raw.run?.status,100),checkedOn:dateOrNull(raw.run?.checkedOn),note:cleanStr(raw.run?.note),automaticEnabled:raw.run?.automaticEnabled===true,coverage:Array.isArray(raw.run?.coverage)?raw.run.coverage.slice(0,100).map(c=>({source:cleanStr(c.source,200),status:cleanStr(c.status,200),detail:cleanStr(c.detail,3000)})):[]},jobs};
}
export function validResumePath(path){return ['summary','skills'].includes(path)||/^education\.\d{1,2}$/.test(path)||/^experience\.\d{1,2}\.bullets\.\d{1,2}$/.test(path);}
export function getPath(obj,path){if(!validResumePath(path))return '';let val=obj;for(const p of path.split('.')){if(!val||!Object.hasOwn(val,p))return '';val=val[p];}return Array.isArray(val)?val.join('\n'):String(val??'');}
export function applyApproved(master,job,draft){
  if(!master)throw new Error('Load the private master resume first.');const out=clone(master);
  for(const proposal of job.resumeEdits||[]){const e=draft?.edits?.[proposal.id];if(!e?.approved)continue;if(!validResumePath(proposal.path))continue;const parts=proposal.path.split('.');let target=out;for(const p of parts.slice(0,-1)){if(!target||!Object.hasOwn(target,p))throw new Error('Resume structure does not match proposal.');target=target[p];}const last=parts.at(-1);if(!Object.hasOwn(target,last))throw new Error('Resume field not found.');target[last]=proposal.path==='skills'?e.text.split('\n').filter(Boolean):e.text;
  }
  for(const extra of draft?.extraBullets||[]){if(extra.approved&&[0,1].includes(extra.company)&&out.experience?.[extra.company])out.experience[extra.company].bullets.push(cleanStr(extra.text,3000));}
  return out;
}
export function newWorkspace(){return {kind:'sivanesh-private-workspace',schemaVersion:2,settings:{...DEFAULTS},master:null,applications:{},drafts:{},versions:{}};}
// Validate the entire snapshot before replacing any browser state.
const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
function requireShape(ok,label){if(!ok)throw new Error('Invalid private workspace: '+label);}
function textList(v,label){requireShape(Array.isArray(v)&&v.every(x=>typeof x==='string'),label);return clone(v);}
function resumeShape(m){
  requireShape(object(m)&&typeof m.name==='string'&&m.name.trim(),'master resume');
  const out={};for(const k of ['name','summary','email','phone','linkedin']){requireShape(m[k]===undefined||typeof m[k]==='string','resume '+k);out[k]=m[k]||'';}
  out.skills=textList(m.skills,'resume skills');out.education=textList(m.education??[],'education');out.certifications=textList(m.certifications??[],'certifications');
  requireShape(Array.isArray(m.experience),'experience');out.experience=m.experience.map(e=>{requireShape(object(e),'experience section');const row={};for(const k of ['company','role','location','dates']){requireShape(typeof e[k]==='string','experience '+k);row[k]=e[k];}row.bullets=textList(e.bullets,'experience bullets');return row;});return out;
}
function privateMap(value,check,label){
  if(value===undefined)return {};requireShape(object(value),label);const out={};
  for(const [id,item] of Object.entries(value)){requireShape(/^[a-z0-9][a-z0-9_-]{0,119}$/i.test(id)&&!['__proto__','constructor','prototype'].includes(id),label+' ID');out[id]=check(item);}return out;
}
function draftShape(d){
  requireShape(object(d),'draft');const edits=privateMap(d.edits??{},e=>{requireShape(object(e)&&typeof e.text==='string'&&typeof e.approved==='boolean','approved edit');return {text:e.text,approved:e.approved};},'edits');
  requireShape(Array.isArray(d.extraBullets??[]),'extra bullets');const extraBullets=(d.extraBullets??[]).map(b=>{requireShape(object(b)&&[0,1].includes(b.company)&&typeof b.text==='string'&&typeof b.approved==='boolean','extra bullet');return {company:b.company,text:b.text,approved:b.approved};});
  requireShape(d.facts===undefined||typeof d.facts==='string','facts');requireShape(d.confirmed===undefined||typeof d.confirmed==='boolean','confirmation');return {edits,extraBullets,facts:d.facts||'',confirmed:d.confirmed===true};
}
export function validateWorkspace(raw){
  if(raw?.kind!=='sivanesh-private-workspace'||raw.schemaVersion!==2)throw new Error('Not a version 2 private workspace.');
  const out=newWorkspace();requireShape(raw.settings===undefined||object(raw.settings),'settings');
  for(const key of Object.keys(DEFAULTS))if(Object.hasOwn(raw.settings??{},key))out.settings[key]=raw.settings[key];
  for(const key of ['currentCtcLpa','targetCtcLpa','noticeDays','weeklyApplications']){const v=out.settings[key];requireShape(v===null?['currentCtcLpa','noticeDays'].includes(key):Number.isFinite(v)&&v>=0,'setting '+key);}
  requireShape(typeof out.settings.goalDate==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(out.settings.goalDate)&&day(out.settings.goalDate),'goal date');
  requireShape(typeof out.settings.repoUrl==='string'&&(!out.settings.repoUrl||/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/.test(out.settings.repoUrl)),'repository URL');
  if(raw.master!==null&&raw.master!==undefined)out.master=resumeShape(raw.master);
  out.applications=privateMap(raw.applications,a=>{
    requireShape(object(a)&&STAGES.includes(a.stage),'application stage');const row={stage:a.stage};
    for(const k of ['notes','nextAction','followUpOn','appliedOn','updatedAt','payEvidence']){requireShape(a[k]===undefined||typeof a[k]==='string','application '+k);if(a[k]!==undefined)row[k]=a[k];}
    for(const k of ['confirmedCtcLpa','fixedCtcLpa'])if(a[k]!==undefined){requireShape(a[k]===null||Number.isFinite(a[k])&&a[k]>=0,'application pay');row[k]=a[k];}
    requireShape(Array.isArray(a.history??[]),'application history');row.history=(a.history??[]).map(h=>{requireShape(object(h)&&typeof h.at==='string'&&typeof h.event==='string','history entry');return {at:h.at,event:h.event};});if(a.shortlisted===true)row.shortlisted=true;return row;
  },'applications');
  out.drafts=privateMap(raw.drafts,draftShape,'drafts');
  out.versions=privateMap(raw.versions,items=>{requireShape(Array.isArray(items),'versions');return items.map(v=>{requireShape(object(v)&&typeof v.createdAt==='string'&&typeof v.jobId==='string','version');return {createdAt:v.createdAt,jobId:v.jobId,resume:resumeShape(v.resume),approvedEdits:draftShape(v.approvedEdits)};});},'versions');
  return out;
}
