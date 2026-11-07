#!/usr/bin/env python3
"""Publish only approved project summaries, using the existing gh login."""
import argparse
import base64
import json
import subprocess
import time
from datetime import datetime,timedelta,timezone
from pathlib import Path

SPECS=[('MailTools','mailtools',{'CI':['build-test','e2e','image-smoke']}),('viewarr','viewarr',{}),('dankcity','dankcity',{'Preflight':['preflight'],'Resource Tests':['test']})]
QUERY='''query Profile($repo:String!, $cursor:String) {
 repository(owner:"chaosen3",name:$repo) {
  name
  defaultBranchRef { target { ... on Commit {
   committedDate
   statusCheckRollup { contexts(first:100) { pageInfo { hasNextPage } nodes {
    ... on CheckRun { name status conclusion startedAt completedAt checkSuite { app { slug } workflowRun { workflow { name } } } }
   } } }
  } } }
  pullRequests(first:100,after:$cursor,states:MERGED,orderBy:{field:UPDATED_AT,direction:DESC}) {
   pageInfo { hasNextPage endCursor }
   nodes { id mergedAt updatedAt author { __typename } }
  }
 }
}'''

def api(endpoint,body=None,method=None):
 args=['gh','api',endpoint]
 if method: args+=['--method',method]
 if body is not None: args+=['--input','-']
 for attempt in range(3):
  result=subprocess.run(args,input=json.dumps(body) if body is not None else None,capture_output=True,text=True,timeout=60)
  if result.returncode==0:
   data=json.loads(result.stdout)
   if not data.get('errors'): return data
  if attempt<2: time.sleep(2**attempt)
 raise RuntimeError('GitHub request failed; raw response withheld')

def check_state(repo,expected):
 commit=(repo.get('defaultBranchRef') or {}).get('target') or {}
 rollup=(commit.get('statusCheckRollup') or {}).get('contexts') or {}
 matches=[]
 for workflow,names in expected.items():
  for name in names:
   candidates=[c for c in rollup.get('nodes',[]) if c.get('name')==name and (c.get('checkSuite') or {}).get('app',{}).get('slug')=='github-actions' and ((c.get('checkSuite') or {}).get('workflowRun') or {}).get('workflow',{}).get('name')==workflow]
   matches.append(max(candidates,key=lambda c:c.get('startedAt') or '',default=None))
 if not matches or not all(matches) or rollup.get('pageInfo',{}).get('hasNextPage'): return 'not_recorded',None
 if any(c.get('conclusion') in ['FAILURE','TIMED_OUT','ACTION_REQUIRED','STARTUP_FAILURE'] for c in matches): state='failing'
 elif any(c.get('status')!='COMPLETED' for c in matches): state='pending'
 elif all(c.get('conclusion')=='SUCCESS' for c in matches): state='passing'
 else: state='not_passed'
 return state,max((c.get('completedAt') or '')[:10] for c in matches) or None

def summarise(pages,key,expected,now):
 end=now.replace(hour=0,minute=0,second=0,microsecond=0);start=end-timedelta(days=30)
 first=pages[0];last=pages[-1]['pullRequests']
 complete=not last['pageInfo']['hasNextPage'] or any(p['updatedAt']<start.isoformat() for p in last['nodes'])
 prs={p['id']:p for page in pages for p in page['pullRequests']['nodes']}
 prs=[p for p in prs.values() if (p.get('author') or {}).get('__typename')!='Bot']
 days=[(start+timedelta(days=i)).date().isoformat() for i in range(30)]
 daily=[sum(p['mergedAt'][:10]==day for p in prs) for day in days]
 state,checked=check_state(first,expected)
 commit=(first.get('defaultBranchRef') or {}).get('target') or {}
 return dict(id=key,status='current',observed_at=now.replace(minute=0,second=0,microsecond=0).isoformat().replace('+00:00','Z'),updated=(commit.get('committedDate') or '')[:10] or None,last_merge=max((p['mergedAt'][:10] for p in prs),default=None),checks=state,checks_date=checked,activity_complete=complete,merged_prs_30d=sum(daily) if complete else None,daily_merges=daily if complete else None,window_start=days[0],window_end=days[-1])

def collect(now):
 result=[];start=(now.replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=30)).isoformat()
 for repo,key,expected in SPECS:
  cursor=None;pages=[];seen=set()
  try:
   for _ in range(20):
    response=api('graphql',{'query':QUERY,'variables':{'repo':repo,'cursor':cursor}})
    page=response['data']['repository']
    if not page or page['name']!=repo: raise ValueError('Unexpected project')
    pages.append(page);prs=page['pullRequests']
    if not prs['pageInfo']['hasNextPage'] or any(p['updatedAt']<start for p in prs['nodes']): break
    cursor=prs['pageInfo']['endCursor']
    if not cursor or cursor in seen: raise ValueError('Repeated pagination cursor')
    seen.add(cursor)
   result.append(summarise(pages,key,expected,now))
  except (KeyError,TypeError,ValueError,RuntimeError,subprocess.TimeoutExpired):
   result.append({'id':key,'status':'unavailable','observed_at':None})
 return {'schema_version':1,'projects':result}

def publish(payload):
 path='repos/chaosen3/chaosen3/contents/data/projects.json'
 # The file is created as part of the initial profile publication.
 current=api(path)
 content=base64.b64encode((json.dumps(payload,indent=2)+'\n').encode()).decode()
 if ''.join(current['content'].split())==content: return
 api(path,{'message':'chore: refresh approved project summaries','sha':current['sha'],'content':content},'PUT')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');parser.add_argument('--output',type=Path)
 args=parser.parse_args();payload=collect(datetime.now(timezone.utc))
 if args.output: args.output.write_text(json.dumps(payload,indent=2)+'\n')
 if args.publish: publish(payload)
 print(json.dumps({'projects':[{k:p.get(k) for k in ('id','status','checks','merged_prs_30d')} for p in payload['projects']]}))
 if not any(p['status']=='current' for p in payload['projects']): raise SystemExit(1)

if __name__=='__main__': main()
