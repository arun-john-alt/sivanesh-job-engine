import unittest
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('scan',Path(__file__).parents[1]/'scripts/scan.py')
scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan)
class ScannerTests(unittest.TestCase):
    def test_hosts(self):
        hosts={'careers.example.com'}
        self.assertTrue(scan.valid_url('https://careers.example.com/job/1',hosts))
        self.assertFalse(scan.valid_url('https://careers.example.com.attacker.com/job',hosts))
        self.assertFalse(scan.valid_url('http://careers.example.com',hosts))
        self.assertFalse(scan.valid_url('https://admin:password@careers.example.com',hosts))
    def test_relevance(self):
        self.assertTrue(scan.is_relevant('Senior Buyer','Chennai, India','5-7 years'))
        self.assertFalse(scan.is_relevant('SAP MM Implementation Consultant','Chennai, India','5-7 years'))
        self.assertFalse(scan.is_relevant('Buyer','London, UK','5-7 years'))
        self.assertFalse(scan.is_relevant('Procurement Intern','Chennai, India',''))
        self.assertFalse(scan.is_relevant('Senior Buyer','Chennai, India','10-15 years'))
    def test_discovery_never_invents_match_or_salary(self):
        node={'@type':'JobPosting','title':'Senior Buyer','description':'<p>Supplier management, 5-7 years.</p>','hiringOrganization':{'name':'Example'},'jobLocation':{'address':{'addressLocality':'Chennai','addressCountry':'IN'}}}
        out=scan.extract(node,'https://careers.example.com/jobs/42','Example','2026-09-16')
        self.assertEqual(out['analysisStatus'],'needs-review');self.assertEqual(out['score'],[]);self.assertEqual(out['salary']['kind'],'unknown')
    def test_salary_units(self):
        node={'title':'Senior Buyer','description':'Procurement','hiringOrganization':{'name':'Example'},'jobLocation':{'address':{'addressLocality':'Chennai','addressCountry':'IN'}},'baseSalary':{'currency':'INR','value':{'minValue':1200000,'maxValue':1500000,'unitText':'YEAR'}}}
        out=scan.extract(node,'https://careers.example.com/jobs/42','Example','2026-09-16')
        self.assertEqual(out['salary']['minLpa'],12);self.assertEqual(out['salary']['basis'],'Annual base pay')
        node['baseSalary']['value']['unitText']='MONTH'
        self.assertEqual(scan.extract(node,'https://careers.example.com/jobs/42','Example','2026-09-16')['salary']['kind'],'unknown')
    def test_remote_india_restriction(self):
        node={'title':'Procurement Specialist','description':'Procurement','jobLocationType':'TELECOMMUTE','applicantLocationRequirements':{'@type':'Country','name':'India'}}
        self.assertIsNotNone(scan.extract(node,'https://careers.example.com/job/1','Example','2026-09-16'))
        node['applicantLocationRequirements']={'@type':'Country','name':'USA'}
        self.assertIsNone(scan.extract(node,'https://careers.example.com/job/1','Example','2026-09-16'))
    def test_parse_jsonld(self):
        p=scan.Page();p.feed('<script type="application/ld+json">{"@type":"JobPosting","title":"Buyer"}</script><p>Visible text</p>')
        self.assertEqual(len(list(scan.job_nodes(p.jsonld))),1);self.assertEqual(p.text,['Visible text'])
if __name__=='__main__':unittest.main()
