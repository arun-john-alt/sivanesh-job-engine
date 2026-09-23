import datetime as dt
import json
import unittest
from scripts import availability, scan

class AvailabilityTests(unittest.TestCase):
    def setUp(self):
        self.url='https://careers.example.com/job/123'
        self.job={'id':'123','title':'QA Lead','applyUrl':self.url,'requisition':'123'}
    def check(self, html, status='HTTP 200'):
        return availability.decision(self.job,html,status,self.url,scan)[0]
    def test_metadata_is_not_proof_of_open_application(self):
        node={'@type':'JobPosting','title':'QA Lead','url':self.url,'identifier':{'value':'123'}}
        html='<script type="application/ld+json">'+json.dumps(node)+'</script>'
        self.assertEqual(self.check(html),'unconfirmed')
        self.assertEqual(self.check(html+'<a href="/apply/123">Apply now</a>'),'open')
        node['url']='https://careers.example.com/job/999'
        self.assertEqual(self.check('<script type="application/ld+json">'+json.dumps(node)+'</script><button>Apply now</button>'),'unconfirmed')
    def test_closure_and_blocking_are_distinct(self):
        self.assertEqual(self.check(None,'HTTP 403'),'unconfirmed')
        self.assertEqual(self.check(None,'HTTP 410'),'closed')
        self.assertEqual(self.check('<h1>QA Lead</h1>No longer accepting applications'),'closed')
        self.assertEqual(self.check('<h1>QA Lead</h1>Related jobs This job is closed'),'unconfirmed')
    def test_exact_api_identity_required(self):
        u='https://boards-api.greenhouse.io/v1/boards/example/jobs/123'
        self.job['applyUrl']='https://job-boards.greenhouse.io/example/jobs/123'
        for ident,result in [(123,'open'),(456,'unconfirmed')]:
            body=json.dumps({'id':ident,'absolute_url':'https://job-boards.greenhouse.io/example/jobs/123'})
            self.assertEqual(availability.decision(self.job,body,'HTTP 200',u,scan)[0],result)
    def test_48_hour_boundary_and_invalid_evidence(self):
        now=dt.datetime(2026,9,23,10,tzinfo=dt.timezone.utc)
        self.assertFalse(availability.fresh({},now))
        for hours,expected in [(47.99,True),(48,False),(-1,False)]:
            self.assertEqual(availability.fresh({'lastConfirmedOpenAt':(now-dt.timedelta(hours=hours)).isoformat()},now),expected)
    def test_endpoints_do_not_guess_requisitions(self):
        self.assertEqual(availability.endpoint('https://job-boards.greenhouse.io/example/jobs/123'),'https://boards-api.greenhouse.io/v1/boards/example/jobs/123')
        self.assertEqual(availability.endpoint(self.url),self.url)
    def test_audit_does_not_refresh_blocked_evidence(self):
        from types import SimpleNamespace
        class Fake:
            def __init__(self, config): pass
            def page(self, url): return None, 'HTTP 403'
        old='2026-01-01T00:00:00+00:00'
        job={**self.job,'verification':'live','lastConfirmedOpenAt':old}
        data={'jobs':[job]}
        availability.audit(data,{'allowedHosts':['careers.example.com']},SimpleNamespace(**{**vars(scan),'Fetcher':Fake}))
        self.assertEqual(job['lastConfirmedOpenAt'],old)
        self.assertTrue(job['availabilityHold'])
        self.assertEqual(job['availabilityStatus'],'unconfirmed')
        self.assertNotEqual(job['verification'],'closed')
    def test_closed_linkedin_does_not_close_employer_route(self):
        job={**self.job,'verification':'live','linkedinUrl':'https://www.linkedin.com/jobs/view/123'}
        self.assertFalse(scan.mark_index_closed(job,'2026-09-23',linkedin=True))
        self.assertEqual(job['verification'],'live')
        self.assertEqual(job['linkedinAvailability'],'closed')
