import unittest
from scripts import career_microdata, availability, scan

URL='https://careers.example.com/job/Test-Lead/123-en_GB/'
DESC='Lead automation and API testing. Coordinate a team, plan coverage, manage defects and improve continuous integration delivery.'
def html(control='',extra='',title='Test Lead'):
    return f'<link rel="canonical" href="{URL}"><h1 itemprop="title">{title}</h1><div itemtype="https://schema.org/JobPosting"><div itemprop="description">{DESC}{extra}</div><span itemprop="addressLocality">Chennai</span></div>{control}'
def decision(source):
    return availability.decision({'title':'Test Lead','applyUrl':URL},source,'HTTP 200',URL,scan)[0]

class MicrodataTests(unittest.TestCase):
    def test_exact_application_route_required(self):
        self.assertEqual(decision(html('<a href="/talentcommunity/apply/123/">Apply now</a>')),'open')
        for href in ['/talentcommunity/apply/456/','/join','https://other.example/talentcommunity/apply/123/']:
            self.assertEqual(decision(html(f'<a href="{href}">Apply now</a>')),'unconfirmed')
        self.assertEqual(decision(html('<button>Apply now</button>')),'unconfirmed')
    def test_embedded_manual_apply_binds_identity(self):
        control='<a id="applyOption--manual" href="#">Apply Now</a><script>j2w.Apply.init({jobID:123,locale:"en_GB"});</script>'
        self.assertEqual(decision(html(control)),'open')
        self.assertEqual(decision(html(control.replace('jobID:123','jobID:456'))),'unconfirmed')
    def test_deadline_in_description_overrides_apply_button(self):
        source=html('<a href="/talentcommunity/apply/123/">Apply now</a>',' Please apply on or before 30th Sep 2020')
        self.assertEqual(career_microdata.read(source)['validThrough'],'2020-09-30')
        self.assertEqual(decision(source),'closed')
    def test_multiple_postings_are_ambiguous(self):
        source=html()+ '<div itemtype="https://schema.org/JobPosting"></div>'
        self.assertIsNone(career_microdata.read(source))
    def test_scripts_not_job_description_or_location(self):
        node=career_microdata.read(html(extra='<script>Chennai SECRET</script><style>.SECRET{}</style>'))
        self.assertNotIn('SECRET',node['description'])
        self.assertEqual(node['jobLocation']['address']['addressLocality'],'Chennai')
    def test_hcl_primary_location_only(self):
        source=html().replace('careers.example.com','careers.hcltech.com').replace('<span itemprop="addressLocality">Chennai</span>','')
        source+='<div>Job Description Test Lead Hyderabad, Telangana Job Summary More details</div>'
        self.assertEqual(career_microdata.read(source)['jobLocation']['address']['addressLocality'],'Hyderabad, Telangana')

    def test_company_age_does_not_exclude_candidate(self):
        title='Supply Chain Professional' if 'Sivanesh' in scan.AGENT else 'QA Engineer'
        self.assertTrue(scan.is_relevant(title,'Chennai','Qualifications 5 to 7 years of experience. About Vestas: 40+ years of experience in wind energy.'))
