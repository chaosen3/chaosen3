#!/usr/bin/env python3
"""Render the restricted public snapshot without network access."""
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DATA,README,ASSETS=ROOT/'data/pulse.json',ROOT/'README.md',ROOT/'assets'
THEMES={
 'dark':dict(bg='#0d1117',line='#303b49',text='#ecf2f8',muted='#99a8b9',accent='#7cabf5',good='#69c69c',warning='#e3b76a'),
 'light':dict(bg='#ffffff',line='#d5deea',text='#152438',muted='#52647b',accent='#285fba',good='#23734e',warning='#8c5b0b'),
}
PROJECTS=[
 ('mailtools','MailTools','Email deliverability & DNS diagnostics','React · Node.js · PostgreSQL','Build, browser & image checks'),
 ('viewarr','Viewarr','Media library, playback & transcoding','Go · Next.js · SQLite · FFmpeg','Current-commit checks'),
 ('dankcity','Dank City','London roleplay on GTA V Enhanced','Lua · Python · GitHub Actions','Preflight & resource tests'),
]

def count(v):
 if isinstance(v,bool): return None
 try: n=float(v)
 except (ValueError,TypeError): return None
 return int(n) if math.isfinite(n) and n>=0 and n.is_integer() else None

def date(v,year=False):
 try: return datetime.fromisoformat(str(v).replace('Z','+00:00')).strftime('%d %b %Y' if year else '%d %b')
 except ValueError: return 'unavailable'

def fresh(s):
 try:
  stamp=datetime.fromisoformat(s.get('observed_at','').replace('Z','+00:00'))
  age=(datetime.now(timezone.utc)-stamp).total_seconds()
  return s.get('status')=='current' and 0<=age<48*3600
 except (ValueError,TypeError,AttributeError): return False

def text(x,y,value,c,size=13,weight=400,anchor='start'):
 return f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'

def start(w,h,title,desc,t):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc" font-family="Segoe UI,Helvetica,Arial,sans-serif">',f'<title id="title">{escape(title)}</title>',f'<desc id="desc">{escape(desc)}</desc>',f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/>']

def project_card(d,theme,mobile=False):
 t=THEMES[theme];w=420 if mobile else 840
 row=172 if mobile else 103;h=3*row+24
 parts=start(w,h,'Selected work','Three selected projects with dated current-commit checks.',t)
 rows={p.get('id'):p for p in d.get('projects',[]) if isinstance(p,dict)}
 for i,(key,name,description,stack,check_label) in enumerate(PROJECTS):
  p=rows.get(key,{});y=i*row+26
  parts += [text(0,y,name,t['text'],26 if mobile else 23,600),text(0,y+25,description,t['text'],17 if mobile else 14),text(0,y+47,stack,t['muted'],14 if mobile else 12)]
  x,sy=(0,y+75) if mobile else (526,y)
  known=fresh(p);state=p.get('checks','not_recorded')
  label={'passing':'Checks passed','failing':'Checks failing','pending':'Checks running','not_passed':'Checks not passed','not_recorded':'No checks recorded'}.get(state,'Checks unavailable')
  if not known: label='Checks unavailable' if not p.get('observed_at') else 'Last known · '+label.lower()
  colour=t['good'] if known and state=='passing' else t['warning'] if known and state=='failing' else t['muted']
  parts.append(text(x,sy,label,colour,15 if mobile else 13,600))
  parts.append(text(x,sy+20,check_label if state!='not_recorded' else 'Source private',t['muted'],14 if mobile else 11))
  milestone=('Updated '+date(p['updated'])+' · observed '+date(p.get('observed_at'))) if p.get('updated') else 'Project data unavailable'
  parts.append(text(x,sy+40,milestone,t['muted'],14 if mobile else 11))
  parts.append(f'<path d="M0 {(i+1)*row}H{w}" stroke="{t["line"]}"/>')
 parts.append(text(0,h-4,'Private repositories · dated checks, not deployment status',t['muted'],13 if mobile else 11))
 return '\n'.join(parts+['</svg>'])+'\n'

def card(d,theme,mobile=False):
 t=THEMES[theme];w=420 if mobile else 840;h=165 if mobile else 100
 s=d.get('infrastructure',{});a=d.get('automation',{})
 up,total=count(s.get('containers_running')),count(s.get('containers_total'))
 known=up is not None and total is not None and up<=total;current=fresh(s)
 label=f'{up} / {total} containers running' if known else 'Container snapshot unavailable'
 if known and not current: label='Last known · '+label
 parts=start(w,h,'Infrastructure snapshot','Running container counts, not application health or uptime.',t)
 parts.append(f'<path d="M0 1H{w}" stroke="{t["line"]}"/>')
 parts.append(text(0,30,label,t['text'],15,600))
 stamp=date(s.get('observed_at'),True)
 parts.append(text(0,52,('Observed ' if current else 'Last observation ')+stamp+' · daily snapshot',t['muted'],13 if mobile else 11))
 runs=count(a.get('completed_runs_7d'));success=count(a.get('successful_runs_7d'))
 auto='Automation data unavailable'
 if fresh(a) and runs is not None:
  auto=f'{runs} completed automation runs · 7 days'
  if runs and success is not None and success<=runs:
   if mobile: parts.append(text(0,108,f'{success/runs:.0%} successful',t['muted'],13))
   else: auto+=f' · {success/runs:.0%} successful'
 x,y=(0,85) if mobile else (w,30)
 parts.append(text(x,y,auto,t['muted'],13 if mobile else 11,anchor='start' if mobile else 'end'))
 parts.append(text(0,h-16,'Container state only; no health or uptime claim.',t['muted'],13 if mobile else 11))
 return '\n'.join(parts+['</svg>'])+'\n'

def picture(name,version,alt):
 base='https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets'
 return f'''<!-- {name}:start -->
<picture>
  <source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="{base}/{name}-dark-mobile.svg?v={version}">
  <source media="(prefers-color-scheme: dark)" srcset="{base}/{name}-dark.svg?v={version}">
  <source media="(max-width: 600px)" srcset="{base}/{name}-light-mobile.svg?v={version}">
  <img alt="{escape(alt,quote=True)}" src="{base}/{name}-light.svg?v={version}" width="840">
</picture>
<!-- {name}:end -->'''

def main():
 d=json.loads(DATA.read_text());content=README.read_text()
 if d.get('schema_version')!=3: raise ValueError('Expected public snapshot schema 3')
 for name in ('projects','pulse'):
  a,b=f'<!-- {name}:start -->',f'<!-- {name}:end -->'
  if content.count(a)!=1 or content.count(b)!=1 or content.index(a)>content.index(b): raise ValueError('Missing or repeated '+name+' markers')
 ASSETS.mkdir(exist_ok=True)
 for name,renderer,alt in [('projects',project_card,'MailTools, Viewarr and Dank City: selected work and dated project checks.'),('pulse',card,'Aggregate running container counts and completed automation runs. Dates shown in panel.')]:
  variants=[]
  for theme in THEMES:
   for mobile in (False,True):
    svg=renderer(d,theme,mobile);variants.append(svg)
    (ASSETS/f'{name}-{theme}{"-mobile" if mobile else ""}.svg').write_text(svg)
  version='3-'+hashlib.sha256(''.join(variants).encode()).hexdigest()[:12]
  content=re.sub(f'<!-- {name}:start -->.*?<!-- {name}:end -->',lambda _:picture(name,version,alt),content,flags=re.S)
 README.write_text(content)
 print('Rendered project and pulse panels in four variants each')

if __name__=='__main__': main()
