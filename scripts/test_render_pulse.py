import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime,timezone,timedelta
from pathlib import Path
from unittest.mock import patch
import render_profile as render
import collect_projects as collector

NOW=datetime.now(timezone.utc)
STAMP=NOW.replace(minute=0,second=0,microsecond=0).isoformat().replace('+00:00','Z')

def payload():
 return {'schema_version':3,'projects':[dict(id=key,status='current',observed_at=STAMP,updated='2026-11-01',checks='passing',checks_date='2026-11-01',activity_complete=True,daily_merges=[1]*30,window_start='2026-10-07',window_end='2026-11-05') for key,*_ in render.PROJECTS],'infrastructure':dict(status='current',observed_at=STAMP,containers_running=5,containers_total=7),'automation':dict(status='current',observed_at=STAMP,completed_runs_7d=0,successful_runs_7d=0)}

class RenderTests(unittest.TestCase):
 def test_all_variants_and_metric_meanings(self):
  for theme in render.THEMES:
   for mobile in (False,True):
    svg=render.project_card(payload(),theme,mobile);ET.fromstring(svg)
    self.assertNotIn('Merged pull requests',svg);self.assertNotIn('90 · 30 days',svg);self.assertIn('Checks passed',svg)
    svg=render.card(payload(),theme,mobile);ET.fromstring(svg)
    self.assertIn('5 / 7 containers running',svg);self.assertNotIn('healthy',svg);self.assertNotIn('100%',svg);self.assertNotIn('Deployments',svg)
 def test_old_or_missing_sources_never_look_current(self):
  d=payload();d['projects'][0]['observed_at']=(NOW-timedelta(days=3)).isoformat();d['infrastructure']['status']='unavailable'
  svg=render.project_card(d,'dark');self.assertIn('Last known',svg);self.assertNotIn('90 · 30 days',svg)
  self.assertIn('Last known',render.card(d,'dark'))
  self.assertNotIn('Checks passed',render.project_card({},'dark'))
 def test_project_checks_do_not_depend_on_pr_activity(self):
  original=render.project_card(payload(),'light')
  for modify in [lambda p:p.update(activity_complete=False),lambda p:p.update(window_end='2026-11-04'),lambda p:p.update(daily_merges=[None]*30),lambda p:p.update(daily_merges=[9999]*30)]:
   d=payload();modify(d['projects'][1]);self.assertEqual(original,render.project_card(d,'light'))
 def test_only_markers_replaced_and_render_is_stable(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);data=root/'pulse.json';readme=root/'README.md';assets=root/'assets'
   data.write_text(json.dumps(payload()));readme.write_text('Intro\n<!-- projects:start -->old<!-- projects:end -->\nMiddle\n<!-- pulse:start -->old<!-- pulse:end -->\nEnd')
   with patch.multiple(render,DATA=data,README=readme,ASSETS=assets):
    render.main();a=readme.read_text();render.main();self.assertEqual(a,readme.read_text());self.assertEqual(len(list(assets.glob('*.svg'))),8);self.assertIn('Middle',a)
    readme.write_text('no markers')
    with self.assertRaises(ValueError):render.main()

class CollectorTests(unittest.TestCase):
 def page(self,prs,more=False):
  return {'name':'MailTools','defaultBranchRef':{'target':{'committedDate':'2026-11-06T01:00:00Z'}},'pullRequests':{'nodes':prs,'pageInfo':{'hasNextPage':more,'endCursor':'next'}}}
 def pr(self,id,day,bot=False):
  return dict(id=id,mergedAt=day+'T12:00:00Z',updatedAt=day+'T12:00:00Z',author={'__typename':'Bot' if bot else 'User'},title='PRIVATE TEXT',url='https://private.invalid')
 def test_paginated_deduplication_bots_and_complete_utc_days(self):
  now=datetime(2026,11,6,23,tzinfo=timezone.utc)
  old=self.pr('old','2026-10-06');inside=self.pr('one','2026-10-07');today=self.pr('today','2026-11-06');bot=self.pr('bot','2026-10-08',True)
  result=collector.summarise([self.page([today,bot,inside],True),self.page([inside,old])],'mailtools',{},now)
  self.assertEqual(result['merged_prs_30d'],1);self.assertEqual(result['daily_merges'][0],1);self.assertEqual(result['checks'],'not_recorded');self.assertNotIn('PRIVATE',json.dumps(result));self.assertNotIn('private.invalid',json.dumps(result))
 def test_capped_pagination_is_not_reported_as_zero(self):
  r=collector.summarise([self.page([self.pr('one','2026-11-01')],True)],'mailtools',{},datetime(2026,11,6,tzinfo=timezone.utc))
  self.assertFalse(r['activity_complete']);self.assertIsNone(r['merged_prs_30d'])
 def test_only_expected_latest_actions_checks_can_pass(self):
  def check(name,state,started,wf='CI'):
   return dict(name=name,conclusion=state,status='COMPLETED',startedAt=started,completedAt=started,checkSuite={'app':{'slug':'github-actions'},'workflowRun':{'workflow':{'name':wf}}})
  r=self.page([]);r['defaultBranchRef']['target']['statusCheckRollup']={'contexts':{'nodes':[check('build-test','SUCCESS','2026-11-01'),check('build-test','FAILURE','2026-11-02')],'pageInfo':{'hasNextPage':False}}}
  self.assertEqual(collector.check_state(r,{'CI':['build-test']})[0],'failing')
  self.assertEqual(collector.check_state(r,{'CI':['build-test','e2e']})[0],'not_recorded')
  r['defaultBranchRef']['target']['statusCheckRollup']['contexts']['pageInfo']['hasNextPage']=True
  self.assertEqual(collector.check_state(r,{'CI':['build-test']})[0],'not_recorded')

if __name__=='__main__':unittest.main()
