import subprocess,json,time,sys
from pathlib import Path
base=Path.home()/'putgd-lab/h1396-ci/control.py';root=Path('/tmp/h396k')
log=[]
def run(*args):
 p=subprocess.run(['python3',str(base),*args],capture_output=True,text=True)
 log.append({'args':args,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 (root/'walk-log.json').write_text(json.dumps(log,indent=2))
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout
def call(method,params={}):
 raw=run('cli',method,json.dumps(params));return json.loads(raw)
def state():
 for i in range(40):
  s=call('ui.history',{'action':'inspect'})['result']
  if not s.get('busy') and not s.get('page',{}).get('loading'):return s
  time.sleep(.1)
 raise RuntimeError('History did not settle')
def action(a,**kw):
 r=call('ui.history',dict(action=a,**kw));state();return r
def shot(n):run('capture',n)
results={}
try:
 action('clearFilters',scope='all');counts=call('history.counts')['result'];print(counts)
 for cat in ('all','images','videos','text+other','failed'):
  action('showCategory',category=cat);s=state();assert s['categoryTotals']==counts['categories'];shot('01-'+cat)
 assert action('removeFilter',key='uploadStatus')['error']['code']=='history_filter_locked'
 results['1']='state/category counts pass; empty categories included'
 action('showCategory',category='all');action('setFilter',key='mime',value='image/png');action('setFilter',key='localStatus',value='saved');shot('02-two-filters');assert len(state()['filterChips'])==2
 action('removeFilter',key='mime');action('clearFilters',scope='all');shot('02-cleared');results['2']='two filter chips/remove/clear passed; search not yet run'
 action('nextPage');assert state()['page']['page']==2;shot('03-page2')
 action('goToPage',page=5);assert state()['page']['lastItem']==236;shot('03-last')
 assert action('nextPage')['error']['code']=='history_page_unavailable'
 action('goToPage',page=1);run('input','key','alt','right');assert state()['page']['page']==2;shot('03-alt-right');run('input','key','alt','left');assert state()['page']['page']==1;shot('03-alt-left');results['3']='paging state and real Alt shortcuts pass'
 action('goToPage',page=2);shot('04-continued');results['4']='page2 day state captured; pinned scroll not yet run'
 ids=[r['id'] for r in call('history.list')['result']['records']]
 action('goToPage',page=1);action('select',ids=[ids[1]]);shot('05-open');run('input','key','esc');assert state()['detailsWanted']==False;action('select',ids=[ids[2]]);assert not state()['inspectorVisible'];shot('05-stays-closed');run('input','key','ret');shot('05-enter');action('toggleDetails');action('closeDetails');action('select',ids=ids[1:4]);assert state()['selectionHeader'];shot('07-selection');results['5']='Esc and closed selection checked; other real inputs pending'
 results['7']='selection header passed; no links or deletable destination IDs'
 action('setView',view='gallery');shot('08-gallery');action('setView',view='list');shot('08-list');results['8']='view switch passed; real gallery selection keys pending'
except Exception as e:results['stopped']=str(e)
finally:
 (root/'walk-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
