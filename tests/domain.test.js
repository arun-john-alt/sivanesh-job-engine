import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {validateDataset,scoreOf,payGate,increase,isExpired,safeURL,canonicalURL,applyApproved,validateWorkspace,newWorkspace} from '../site/engine.js';
import {resumeDocx} from '../site/resume.js';
const raw=JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url),'utf8'));
const data=validateDataset(raw),base=data.jobs[0];
test('seed dataset passes strict schema',()=>assert.ok(data.jobs.length>=4));
test('weighted scores sum and reviewed jobs alone get scores',()=>{assert.equal(scoreOf(base),89);assert.equal(scoreOf({...base,analysisStatus:'needs-review'}),null);});
test('percentage increase uses recurring annual CTC values',()=>assert.ok(Math.abs(increase(12.5,10)-25)<1e-8));
test('unknown salary is not a rejection',()=>assert.equal(payGate(base,12),'Budget unknown'));
test('low third-party estimate cannot reject a role',()=>assert.equal(payGate({...base,salary:{kind:'third-party',minLpa:9,maxLpa:11,basis:'Annual CTC'}},12),'Budget unknown'));
test('employer CTC ceiling below target is a gate',()=>assert.equal(payGate({...base,salary:{kind:'employer-disclosed',minLpa:9,maxLpa:11,basis:'Annual CTC'}},12),'Below target'));
test('base salary is not automatically compared to total CTC',()=>assert.equal(payGate({...base,salary:{kind:'employer-disclosed',minLpa:9,maxLpa:11,basis:'Annual base pay'}},12),'Budget unknown'));
test('expired deadline removed, closing day itself retained',()=>{assert.equal(isExpired({...base,closesOn:'2026-09-16'},'2026-09-17'),true);assert.equal(isExpired({...base,closesOn:'2026-09-16'},'2026-09-16'),false);});
test('unsafe link protocols and embedded credentials rejected',()=>{for(const url of ['javascript:alert(1)','data:text/html,test','https://user:pass@example.com'])assert.equal(safeURL(url),'');});
test('tracking removed but requisition query retained',()=>assert.equal(canonicalURL('https://example.com/jobs?gh_jid=42&utm_source=x#top'),'https://example.com/jobs?gh_jid=42'));
test('public serializer excludes personal fields',()=>{
  const mixed=structuredClone(raw),marker='PRIVATE_TEST_VALUE_7e912c';
  mixed.master={phone:marker};mixed.jobs[0].notes=marker;mixed.jobs[0].currentCtcLpa=8.2;
  mixed.run.note='Add a search API secret in GitHub Actions.';
  const out=validateDataset(mixed);
  assert.equal(Object.hasOwn(out,'master'),false);
  assert.equal(Object.hasOwn(out.jobs[0],'notes'),false);
  assert.equal(Object.hasOwn(out.jobs[0],'currentCtcLpa'),false);
  assert.ok(!JSON.stringify(out).includes(marker));
  assert.equal(out.run.note,mixed.run.note);
});
test('duplicate IDs and invalid score ranges rejected',()=>{const a=structuredClone(raw);a.jobs.push(a.jobs[0]);assert.throws(()=>validateDataset(a));const b=structuredClone(raw);b.jobs[0].score[0].points=300;assert.throws(()=>validateDataset(b));});
test('master remains unchanged and only approved changes apply',()=>{const master={summary:'Original',experience:[{bullets:['Real fact']}],skills:[]};const j={resumeEdits:[{id:'s',path:'summary',proposed:'Proposed'}]};const draft={edits:{s:{text:'Approved fact',approved:true}},extraBullets:[]};const result=applyApproved(master,j,draft);assert.equal(result.summary,'Approved fact');assert.equal(master.summary,'Original');draft.edits.s.approved=false;assert.equal(applyApproved(master,j,draft).summary,'Original');});
test('unapproved new facts are excluded',()=>{const master={summary:'Original',experience:[{bullets:['Real fact']}],skills:[]};assert.equal(applyApproved(master,{resumeEdits:[]},{extraBullets:[{company:0,text:'Unverified',approved:false}]}).experience[0].bullets.length,1);});
test('prototype paths do not modify master or globals',()=>{const result=applyApproved({summary:'Safe'},{resumeEdits:[{id:'bad',path:'__proto__.polluted'}]},{edits:{bad:{approved:true,text:'yes'}}});assert.equal(result.summary,'Safe');assert.equal({}.polluted,undefined);});
test('workspace defaults contain no current CTC or personal contacts',()=>{const w=newWorkspace();assert.equal(w.settings.currentCtcLpa,null);assert.equal(w.master,null);assert.equal(validateWorkspace(w).settings.targetCtcLpa,12);});
test('DOCX is a genuine ZIP, not HTML renamed .docx',async()=>{const blob=resumeDocx({name:'Test Candidate',summary:'A real summary.',skills:['Procurement'],experience:[],education:[],certifications:[]});const bytes=new Uint8Array(await blob.arrayBuffer());assert.equal(bytes[0],0x50);assert.equal(bytes[1],0x4b);assert.ok(blob.type.includes('wordprocessingml'));});
test('encrypted backup round trip and incorrect password rejection',async()=>{const {encryptWorkspace,decryptWorkspace}=await import('../site/resume.js');const data={private:'sample-only'};const encrypted=await encryptWorkspace(data,'a-long-unique-test-passphrase');assert.deepEqual(await decryptWorkspace(encrypted,'a-long-unique-test-passphrase'),data);await assert.rejects(()=>decryptWorkspace(encrypted,'incorrect-passphrase'));assert.ok(!JSON.stringify(encrypted).includes('sample-only'));});
test('employer-specific education edits preserve master dates',()=>{const m={education:['Degree | 2020']};const result=applyApproved(m,{resumeEdits:[{id:'edu',path:'education.0'}]},{edits:{edu:{approved:true,text:'Degree'}}});assert.equal(result.education[0],'Degree');assert.equal(m.education[0],'Degree | 2020');});

const sampleMaster={name:'QA Candidate',summary:'Procurement professional.',skills:['Procurement'],experience:[{company:'Example',role:'Buyer',location:'Chennai',dates:'2021–present',bullets:['Supported supplier coordination.']}],education:[],certifications:[]};
test('private backup preserves complete valid state',()=>{
  const w=newWorkspace();w.master=sampleMaster;w.applications[base.id]={stage:'Applied',notes:'Private test note',confirmedCtcLpa:14,history:[{at:'2026-09-16T00:00:00Z',event:'Applied'}]};
  w.drafts[base.id]={edits:{summary:{text:'Approved summary',approved:true}},extraBullets:[],facts:'Check facts',confirmed:true};
  w.versions[base.id]=[{createdAt:'2026-09-16T00:00:00Z',jobId:base.id,resume:sampleMaster,approvedEdits:w.drafts[base.id]}];
  const out=validateWorkspace(w);assert.equal(out.applications[base.id].notes,'Private test note');assert.equal(out.versions[base.id][0].resume.name,'QA Candidate');assert.deepEqual(out.drafts,w.drafts);
});
test('malformed private imports cannot become persistent broken state',()=>{
  const mutations=[w=>w.settings.goalDate='2026-12-31" autofocus data-test="injected',w=>w.settings.targetCtcLpa=null,w=>w.master={...sampleMaster,experience:[{company:'Example',bullets:null}]},w=>w.applications[base.id]={stage:'Applied',confirmedCtcLpa:'" autofocus'},w=>w.applications[base.id]={stage:'Applied',history:{}},w=>w.drafts[base.id]={edits:[]},w=>w.drafts[base.id]={extraBullets:[null]},w=>w.versions[base.id]={},w=>w.versions[base.id]=[{resume:{}}],w=>w.applications=JSON.parse('{"__proto__":{}}')];
  for(const mutate of mutations){const w=newWorkspace();mutate(w);assert.throws(()=>validateWorkspace(w));}
});
test('optional resume lists normalized for both export formats',async()=>{const w=newWorkspace();w.master={...sampleMaster,education:undefined,certifications:undefined};const {resumePrintHTML}=await import('../site/resume.js');assert.ok(resumePrintHTML(validateWorkspace(w).master).includes('QA Candidate'));});
