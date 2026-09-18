import json
import unittest
from pathlib import Path
from scripts import scan
import test_linkedin
ROW=test_linkedin.ROW

class DiscoveryTests(unittest.TestCase):
    def test_closed_index_result_is_rejected_even_if_snippet_looks_open(self):
        row={**ROW,'raw_content':'Senior Buyer Chennai. No longer accepting applications. Supplier management.'}
        self.assertTrue(scan.closed_result(row));self.assertIsNone(scan.linkedin_lead(row,'2026-09-18'))
    def test_recommendation_closure_does_not_close_target(self):
        self.assertFalse(scan.closed_result({**ROW,'raw_content':'Senior Buyer Chennai Apply now. Similar jobs Procurement Analyst No longer accepting applications'}))
    def test_closed_existing_exact_id_is_archived(self):
        initial=scan.linkedin_lead(ROW,'2026-09-16')
        data,_=test_linkedin.LinkedInTests().run_fixture({'TAVILY_API_KEY':'test-only'},[{**ROW,'raw_content':'No longer accepting applications'}],[initial])
        self.assertEqual(len(data['jobs']),1);self.assertEqual(data['jobs'][0]['verification'],'closed')
    def test_same_title_other_id_does_not_close_existing(self):
        initial=scan.linkedin_lead(ROW,'2026-09-16')
        row={**ROW,'url':'https://www.linkedin.com/jobs/view/9876543210','raw_content':'No longer accepting applications'}
        data,_=test_linkedin.LinkedInTests().run_fixture({'TAVILY_API_KEY':'test-only'},[row],[initial])
        self.assertEqual(data['jobs'][0]['verification'],'indexed')
    def test_missing_result_does_not_close_or_reopen_a_job(self):
        initial=scan.linkedin_lead(ROW,'2026-09-16')
        data,_=test_linkedin.LinkedInTests().run_fixture({'TAVILY_API_KEY':'test-only'},[],[initial])
        self.assertEqual(data['jobs'][0]['verification'],'indexed')
        initial['verification']='closed'
        data,_=test_linkedin.LinkedInTests().run_fixture({'TAVILY_API_KEY':'test-only'},[ROW],[initial])
        self.assertEqual(data['jobs'][0]['verification'],'closed')
    def test_employer_without_jsonld_can_be_indexed_not_live(self):
        row={'url':'https://careers.vestas.com/job/Chennai-Operational-Buyer/1437376433','title':'Operational Buyer Job Details | Vestas','content':'Chennai, India. Procurement and purchase orders.'}
        item=scan.employer_index_lead(row,{'careers.vestas.com'},'2026-09-18')
        self.assertEqual(item['verification'],'indexed');self.assertEqual(item['analysisStatus'],'needs-review');self.assertEqual(item['score'],[])
        self.assertIsNone(scan.employer_index_lead({**row,'url':'https://evil.test/job/42'},{'careers.vestas.com'},'2026-09-18'))
        self.assertIsNone(scan.employer_index_lead({**row,'url':'https://careers.vestas.com/jobs'},{'careers.vestas.com'},'2026-09-18'))
    def test_nearby_locations_and_adjacent_titles(self):
        for role,loc in [('Materials Planner','Sriperumbudur'),('Purchasing Specialist','Oragadam'),('Inventory Analyst','Chennai'),('Supply Planner','Remote India')]:self.assertTrue(scan.is_relevant(role,loc,'5-7 years'))
        self.assertFalse(scan.is_relevant('Buyer','Bengaluru','5-7 years'))
    def test_configured_search_budget_and_diversity(self):
        cfg=json.loads((Path(__file__).parents[1]/'config/search.json').read_text())
        queries=scan.discovery_queries(cfg);self.assertEqual(len(queries),16);self.assertEqual(sum(li for _,li in queries),8)
        self.assertLessEqual(len(queries)+cfg['maxAvailabilityQueries'],26)
    def test_raw_search_evidence_not_published(self):
        item=scan.linkedin_lead({**ROW,'raw_content':'Senior Buyer Chennai Procurement. contact private-test@example.invalid'},'2026-09-18')
        self.assertNotIn('private-test',json.dumps(item))

    def test_expired_explicit_deadline_excludes_result(self):
        row={**ROW,'raw_content':'Senior Buyer Chennai. Job Posting End Date: 2020-08-31 Apply now'}
        self.assertEqual(scan.result_deadline(row),'2020-08-31');self.assertTrue(scan.closed_result(row));self.assertIsNone(scan.linkedin_lead(row,'2026-09-18'))

    def test_company_chennai_office_does_not_override_foreign_linkedin_location(self):
        row={**ROW,'title':'Example hiring Senior Buyer in London, United Kingdom','raw_content':'Example has offices in Chennai, India. Purchasing and supplier management.'}
        self.assertIsNone(scan.linkedin_lead(row,'2026-09-18'))

    def test_common_employer_closure_phrases(self):
        for phrase in ('This job has expired','This position has been filled','This job is no longer available','Applications are closed'):
            self.assertTrue(scan.closed_result({'content':phrase}),phrase)
