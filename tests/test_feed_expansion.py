import datetime as dt
import unittest
from unittest.mock import patch
from scripts import employers, scan, workday_connector

class WorkdayTests(unittest.TestCase):
    url='https://flextronics.wd1.myworkdayjobs.com/Careers/job/India-Chennai/Senior-Analyst_WD123'
    def test_discovery_cannot_refresh_open_timestamp_from_metadata_alone(self):
        board={'kind':'smart'};item={'url':'https://jobs.smartrecruiters.com/Example/123'}
        self.assertFalse(employers.application_evidence(board,{'applyUrl':item['url']},item))
        self.assertFalse(employers.application_evidence(board,{'active':True,'applyUrl':'https://jobs.smartrecruiters.com/Example/456'},item))
        self.assertTrue(employers.application_evidence(board,{'active':True,'applyUrl':item['url']},item))
    def test_exact_identity_apply_flag_and_deadline(self):
        info={'externalUrl':self.url,'jobReqId':'WD123','canApply':True,'posted':True,'endDate':'2099-01-01'}
        job={'applyUrl':self.url,'requisition':'WD123'}
        with patch.object(workday_connector,'read',return_value=({'jobPostingInfo':info},'HTTP 200')):
            self.assertEqual(workday_connector.check(job,None,scan)[0],'open')
            self.assertEqual(workday_connector.check({**job,'requisition':'WD999'},None,scan)[0],'unconfirmed')
        for edits,expected in [({'canApply':False},'closed'),({'canApply':None},'unconfirmed'),({'endDate':'2020-01-01'},'closed'),({'externalUrl':self.url+'-other'},'unconfirmed')]:
            with patch.object(workday_connector,'read',return_value=({'jobPostingInfo':{**info,**edits}},'HTTP 200')):
                self.assertEqual(workday_connector.check(job,None,scan)[0],expected)
    def test_untrusted_career_endpoints_are_rejected(self):
        for url in ['https://evil.example/Careers/job/123','https://user:pass@flextronics.wd1.myworkdayjobs.com/Careers/job/123','http://flextronics.wd1.myworkdayjobs.com/Careers/job/123','https://flextronics.wd1.myworkdayjobs.com:444/Careers/job/123']:
            self.assertIsNone(workday_connector.parts(url))
    def test_career_search_is_read_only_and_robots_checked(self):
        class Blocked:
            def allowed(self,url):return False
            def request(self,*a,**kw):raise AssertionError('Must not bypass robots')
        blob,status=workday_connector.read(Blocked(),'https://flextronics.wd1.myworkdayjobs.com/wday/cxs/flextronics/Careers/jobs',{'searchText':'Chennai'})
        self.assertIsNone(blob)
    def test_pagination_does_not_turn_partial_feeds_into_closures(self):
        board={'kind':'smart','slug':'Example','company':'Example'}
        pages=[({'content':[{'id':str(i)} for i in range(100)],'totalFound':101},'HTTP 200'),(None,'HTTP 503')]
        with patch.object(employers,'get_json',side_effect=pages):
            rows,complete,status=employers.read_board(board,None,scan)
        self.assertEqual(len(rows),100);self.assertFalse(complete)
    def test_title_matching_cannot_merge_different_requisitions(self):
        title='Procurement Analyst' if 'Sivanesh' in scan.AGENT else 'QA Engineer'
        old={'id':'old','company':'Example','title':title,'location':'Chennai','requisition':'OLD','applyUrl':'https://jobs.smartrecruiters.com/Example/123','analysisStatus':'reviewed','score':[]}
        row={'id':'456','company':'Example','title':title,'location':'Chennai','requisition':'NEW','url':'https://jobs.smartrecruiters.com/Example/456','description':'Six years of relevant experience.','remote':False,'api':'https://api.smartrecruiters.com/v1/companies/Example/postings/456'}
        board={'kind':'smart','slug':'Example','company':'Example'}
        data={'jobs':[old]}
        with patch.object(employers,'collect_board',return_value=(board,[row],[row],'Complete')):
            employers.discover(data,{'allowedHosts':[],'employerBoards':[board]},scan)
        self.assertEqual(len(data['jobs']),2)
        self.assertEqual(old['requisition'],'OLD')
        self.assertEqual(old['analysisStatus'],'reviewed')
    def test_singular_year_and_unicode_ranges_are_understood(self):
        self.assertFalse(scan.is_relevant('Procurement Analyst' if 'Sivanesh' in scan.AGENT else 'QA Engineer','Chennai','Experience: 0 to 2 Year'))
        self.assertFalse(scan.is_relevant('Procurement Analyst' if 'Sivanesh' in scan.AGENT else 'QA Engineer','Chennai','Experience: 0–2 years'))
