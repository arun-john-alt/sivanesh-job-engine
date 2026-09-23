// Exercise the app's actual filtering/rendering functions without browser storage.
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
import * as engine from '../site/engine.js';import {companyLogo} from '../site/companies.js';
const raw=JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url)));
for(const j of raw.jobs){if(j.analysisStatus==='reviewed'&&j.verification!=='closed'){j.lastConfirmedOpenAt=new Date().toISOString();j.availabilityHold=false;}}
const code=fs.readFileSync(new URL('../site/app.js',import.meta.url),'utf8').split("document.addEventListener('click'")[0].replace(/^import .*;\n/gm,'');
function app(){const c=vm.createContext({...engine,companyLogo,document:{},location:{hostname:'localhost'},setTimeout,clearTimeout});vm.runInContext(code+'\nD=validateDataset('+JSON.stringify(raw)+');',c);return c;}
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
