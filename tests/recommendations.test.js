// Exercise the app's actual filtering/rendering functions without browser storage.
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as engine from '../site/engine.js';import {companyLogo} from '../site/companies.js';
const raw=JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url)));
for(const j of raw.jobs){if(j.analysisStatus==='reviewed'&&j.verification!=='closed'){j.lastConfirmedOpenAt=new Date().toISOString();j.availabilityHold=false;}}
const code=fs.readFileSync(new URL('../site/app.js',import.meta.url),'utf8').split("document.addEventListener('click'")[0].replace(/^import .*;\n/gm,'');
function app(){const c=vm.createContext({...engine,companyLogo,document:{},location:{hostname:'localhost'},setTimeout,clearTimeout});vm.runInContext(code+'\nD=validateDataset('+JSON.stringify(raw)+');',c);return c;}
test('more open jobs shows fresh eligible unreviewed roles without inventing a match',()=>{
 const c=app();
 vm.runInContext(`const seed=D.jobs[0];const fresh={...seed,id:'pending-fresh',title:'QA <script>unsafe</script>',analysisStatus:'needs-review',score:[],verification:'live',availabilityHold:false,lastConfirmedOpenAt:new Date().toISOString(),closesOn:null,discoveryEligible:true};D.jobs=[fresh,{...fresh,id:'pending-stale',lastConfirmedOpenAt:'2020-01-01T00:00:00Z'},{...fresh,id:'pending-closed',verification:'closed'},{...fresh,id:'pending-excluded',discoveryEligible:false}];`,c);
 assert.equal(vm.runInContext("pendingJobs().map(j=>j.id).join(',')",c),'pending-fresh');
 assert.equal(vm.runInContext('eligible().length',c),0);
 const html=vm.runInContext('pendingRows()',c);
 assert.match(html,/Match review pending/);assert.doesNotMatch(html,/\d+% match|<script>/);
 assert.match(html,/&lt;script&gt;/);
});
test('new discoveries never enter recommendations, even with archive filter',()=>{
 const c=app();assert.equal(vm.runInContext('eligible().some(j=>scoreOf(j)===null)',c),false);
 assert.equal(vm.runInContext("filter.archived=true;eligible().some(j=>scoreOf(j)===null)",c),false);
 assert.equal(vm.runInContext("filter.archived=false;eligible().some(j=>isUnavailable(j))",c),false);
});
test('every card, including saved cards, carries its weighted match',()=>{
 const c=app();for(const html of vm.runInContext('eligible().flatMap(j=>[card(j),card(j,true)])',c)){assert.match(html,/\d+% match/);assert.match(html,/assets\/companies\//);assert.doesNotMatch(html,/Needs review|company-icon/);}
});
test('active counts and recommendations agree; salary unknown remains eligible',()=>{
 const c=app();assert.equal(vm.runInContext('activeJobs().length===eligible().length',c),true);
 assert.equal(vm.runInContext("eligible().some(j=>payGate(j)==='Budget unknown')",c),true);
});

test('opening target excludes pending, expired and out-of-scope roles and reports overdue checks',()=>{
 const c=app();vm.runInContext(`const seed=D.jobs[0];const live={...seed,closesOn:null,verification:'live',availabilityHold:false,discoveryEligible:true,lastConfirmedOpenAt:new Date().toISOString(),salary:{kind:'unknown'},analysisStatus:'reviewed',score:[{points:10},{points:10},{points:10},{points:10},{points:10}]};D.jobs=[live,{...live,analysisStatus:'needs-review',score:[]},{...live,discoveryEligible:false},{...live,verification:'closed'}];D.run.openingPool={lastReplenishedAt:new Date().toISOString()};`,c);
 assert.match(vm.runInContext('openingTarget()',c),/1 \/ 20/);
 assert.match(vm.runInContext('openingTarget()',c),/Hourly search/);
 vm.runInContext("D.run.openingPool.lastReplenishedAt='2020-01-01T00:00:00Z'",c);
 assert.match(vm.runInContext('openingTarget()',c),/Replenishment overdue/);
 assert.equal(vm.runInContext('activeJobs().length',c),1);
});
