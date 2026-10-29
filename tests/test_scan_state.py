import importlib.util,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
s=importlib.util.spec_from_file_location('state_scan',Path(__file__).parents[1]/'scripts/scan.py');scan=importlib.util.module_from_spec(s);s.loader.exec_module(scan)
class ScanStateTests(unittest.TestCase):
 def test_daily_search_preserves_discovery_health_and_history(self):
  state={'sharedPipeline':{'workingSources':121},'reliability':{'samples':[{'checkedAt':'2026-10-25T00:00:00+00:00'}]},'retiredSourceWatch':{'ashby:madecard':{'recovered':False}},'companyDiscovery':{'companies':{'one':{'status':'ats-linked'}}},'coverage':[{'source':'Reliability trial','status':'1/7 days','detail':'Existing history'},{'source':'Web search','status':'Failed','detail':'Old search error'}]}
  with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{},clear=True):
   cfg=Path(t)/'cfg.json';cfg.write_text(json.dumps({'allowedHosts':[],'watchPages':[]}));data=Path(t)/'data.json';data.write_text(json.dumps({'jobs':[],'run':state}))
   scan.run(cfg,data);actual=json.loads(data.read_text())['run']
  for key in ['sharedPipeline','reliability','retiredSourceWatch','companyDiscovery']:self.assertEqual(actual[key],state[key])
  self.assertTrue(any(c['source']=='Reliability trial' for c in actual['coverage']))
  self.assertFalse(any(c['source']=='Web search' for c in actual['coverage']))
