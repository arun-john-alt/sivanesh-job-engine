import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {companyLogo} from '../site/companies.js';
import {validateDataset,scoreOf,isUnavailable} from '../site/engine.js';
const data=validateDataset(JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url))));
test('every active reviewed company has a bundled authentic logo',()=>{
  for(const job of data.jobs.filter(j=>scoreOf(j)!==null&&!isUnavailable(j,'2026-09-18'))){
    const path=companyLogo(job.company);
    assert.notEqual(path,'assets/companies/company.svg',job.company);
    assert.ok(fs.existsSync(new URL('../site/'+path,import.meta.url)),job.company);
  }
});
test('untrusted company names cannot become paths or remote logo requests',()=>{
  for(const name of ['__proto__','constructor','../secret','https://example.org/logo','Unknown'])assert.equal(companyLogo(name),'assets/companies/company.svg');
});
test('review limitations survive public-data validation',()=>{
  const raw=JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url)));
  raw.jobs[0].reviewNote='Description omits detailed qualifications';raw.jobs[0].analysisStatus='needs-review';raw.jobs[0].score=[];
  const job=validateDataset(raw).jobs[0];
  assert.match(job.reviewNote,/omits detailed qualifications/);assert.equal(scoreOf(job),null);
});
