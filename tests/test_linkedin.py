import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import scan

ROW={'url':'https://in.linkedin.com/jobs/view/senior-buyer-at-example-1234567890?trk=search','title':'Example hiring Senior Buyer in Chennai, Tamil Nadu, India | LinkedIn','content':'Procurement and supplier management, 5-7 years.'}

class LinkedInTests(unittest.TestCase):
    def test_canonical_job_urls(self):
        self.assertEqual(scan.linkedin_url(ROW['url']),'https://www.linkedin.com/jobs/view/1234567890')
        for url in ['https://www.linkedin.com/jobs/search/?keywords=buyer','https://www.linkedin.com/in/person','https://linkedin.com.evil.test/jobs/view/123','https://user:pass@linkedin.com/jobs/view/123','http://linkedin.com/jobs/view/123']:
            self.assertIsNone(scan.linkedin_url(url))

    def test_unscored_indexed_lead(self):
        lead=scan.linkedin_lead(ROW,'2026-09-16')
        self.assertEqual(lead['company'],'Example')
        self.assertEqual(lead['title'],'Senior Buyer')
        self.assertEqual(lead['score'],[])
        self.assertEqual(lead['verification'],'indexed')
        self.assertEqual(lead['salary']['kind'],'unknown')
        self.assertIsNone(lead['postedOn'])
        self.assertEqual(lead['linkedinUrl'],lead['applyUrl'])
        self.assertNotIn(ROW['content'],json.dumps(lead))

    def test_relevance_requires_result_evidence(self):
        for title,content in [('Example hiring Buyer',''),('Example hiring Buyer in London',''),('Example hiring Procurement Intern in Chennai',''),('Example hiring Senior Buyer in Chennai','10-15 years')]:
            self.assertIsNone(scan.linkedin_lead({**ROW,'title':title,'content':content},'2026-09-16'))

    def test_tavily_basic_budget_and_domain(self):
        class Fake:
            def request(self,url,headers,payload):
                self.payload=payload
                return json.dumps({'results':[ROW]}),'HTTP 200'
        f=Fake();rows,status=scan.search_results(f,'Tavily','test-only','buyer',True)
        self.assertEqual(rows,[ROW])
        self.assertEqual(f.payload['search_depth'],'basic')
        self.assertFalse(f.payload['auto_parameters'])
        self.assertFalse(f.payload['include_raw_content'])
        self.assertEqual(f.payload['include_domains'],['linkedin.com'])

    def test_invalid_search_responses(self):
        class Fake:
            def request(self,*args):return '[]','HTTP 200'
        self.assertIsNone(scan.search_results(Fake(),'Tavily','test-only','buyer')[0])

    def test_authenticated_redirect_never_forwards_key(self):
        req=scan.urllib.request.Request('https://api.tavily.com/search',headers={'Authorization':'Bearer test-only'})
        with self.assertRaises(ValueError):
            scan.SafeRedirect({'careers.example.com'}).redirect_request(req,None,302,'',{},'https://careers.example.com/')

    def run_fixture(self,env,rows,initial=None):
        class Fake:
            hosts={'careers.example.com'};count=0;limit=18
            def __init__(self,cfg):pass
            def page(self,url):
                if scan.linkedin_url(url):raise AssertionError('Must not fetch LinkedIn')
                return None,'HTTP 403'
        with tempfile.TemporaryDirectory() as temp:
            cfg=Path(temp)/'config.json';data=Path(temp)/'jobs.json'
            cfg.write_text(json.dumps({'allowedHosts':['careers.example.com'],'linkedinQueries':['q']*3,'queries':['e']*3}))
            data.write_text(json.dumps({'schemaVersion':2,'jobs':initial or []}))
            with patch.dict(os.environ,env,clear=True),patch.object(scan,'Fetcher',Fake),patch.object(scan,'search_results',return_value=(rows,'HTTP 200')) as search:
                scan.run(cfg,data)
            return json.loads(data.read_text()),search.call_count

    def test_dedup_and_no_direct_linkedin_fetch(self):
        data,calls=self.run_fixture({'TAVILY_API_KEY':'test-only'},[ROW,ROW])
        self.assertEqual(len(data['jobs']),1)
        self.assertEqual(calls,6)
        again,_=self.run_fixture({'TAVILY_API_KEY':'test-only'},[ROW],data['jobs'])
        self.assertEqual(again['jobs'],data['jobs'])
        # Check the public client schema against generated leads, not only fixtures.
        import subprocess
        proc=subprocess.run(['node','--input-type=module','-e',"import {validateDataset} from './site/engine.js';let x='';for await(const c of process.stdin)x+=c;validateDataset(JSON.parse(x));"],input=json.dumps(data),text=True,capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr)

    def test_preserve_employer_link_and_review(self):
        lead=scan.linkedin_lead(ROW,'2026-09-16');lead['applyUrl']='https://careers.example.com/job/42';lead['analysisStatus']='reviewed'
        data,_=self.run_fixture({'TAVILY_API_KEY':'test-only'},[ROW],[lead])
        self.assertEqual(data['jobs'],[lead])

    def test_no_key_reports_not_configured(self):
        data,calls=self.run_fixture({},[])
        self.assertEqual(calls,0)
        self.assertEqual(data['run']['coverage'][0]['status'],'Not configured')

    def test_failure_not_zero_results(self):
        data,_=self.run_fixture({'TAVILY_API_KEY':'test-only'},None)
        self.assertEqual(data['run']['status'],'limited')
        self.assertTrue(any(c['status']=='Failed' for c in data['run']['coverage']))

if __name__=='__main__':unittest.main()
