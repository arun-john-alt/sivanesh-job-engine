import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import scan

URL='https://careers.example.com/job/42'
NODE={'title':'Senior Buyer','identifier':{'value':'42'},'description':'Supplier management, 5-7 years.','jobLocation':{'address':{'addressLocality':'Chennai','addressCountry':'IN'}}}

class IdentityTests(unittest.TestCase):
    def run_nodes(self,nodes):
        original=scan.extract(NODE,URL,'Example','2026-09-16')
        original['closesOn']='2026-12-31'
        class Fake:
            hosts={'careers.example.com'};count=0;limit=18
            def __init__(self,cfg):pass
            def page(self,url):
                self.count+=1
                if url!=URL:return None,'HTTP 403'
                return '<script type="application/ld+json">'+json.dumps([{'@type':'JobPosting',**n} for n in nodes])+'</script>','HTTP 200'
        with tempfile.TemporaryDirectory() as temp:
            cfg=Path(temp)/'config.json';data=Path(temp)/'jobs.json'
            cfg.write_text('{}');data.write_text(json.dumps({'schemaVersion':2,'jobs':[original]}))
            with patch.dict(os.environ,{},clear=True),patch.object(scan,'Fetcher',Fake):scan.run(cfg,data)
            return original,json.loads(data.read_text())['jobs'][0]
    def test_recommended_role_cannot_replace_evidence(self):
        other={**NODE,'title':'Procurement Manager','validThrough':'2020-01-01','baseSalary':{'currency':'INR','value':{'value':500000,'unitText':'YEAR'}}}
        old,new=self.run_nodes([other]);self.assertEqual(old,new)
    def test_same_title_different_requisition_not_same_role(self):
        old,new=self.run_nodes([{**NODE,'identifier':{'value':'99'},'validThrough':'2020-01-01'}]);self.assertEqual(old,new)
    def test_same_title_different_url_not_same_role(self):
        old,new=self.run_nodes([{**NODE,'url':'https://careers.example.com/job/99','validThrough':'2020-01-01'}]);self.assertEqual(old,new)
    def test_exact_role_updates_deadline(self):
        old,new=self.run_nodes([{**NODE,'url':URL,'validThrough':'2026-11-30'}]);self.assertEqual(new['closesOn'],'2026-11-30');self.assertEqual(new['verification'],'live')
