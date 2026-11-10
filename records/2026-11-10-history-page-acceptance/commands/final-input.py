import subprocess,json,time,sys
from pathlib import Path
base=Path.home()/'putgd-lab/h1396-ci/control.py';root=Path('/tmp/h396k')
log=[]
def run(*args):
 p=subprocess.run(['python3',str(base),*args],capture_output=True,text=True)
 log.append({'args':args,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 (root/'final-input-log.json').write_text(json.dumps(log,indent=2))
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
 call('ui.show',{'view':'history'});action('goToPage',page=1);action('clearSelection');action('closeDetails');run('input','click','700','140');run('input','key','ctrl','a')
 for key in '001':run('input','key',key)
 run('input','key','ret');s=state();results['search']=s['query']['search'];action('setFilter',key='mime',value='image/png');action('setFilter',key='localStatus',value='saved');shot('02-search-two-filters');results['countLabel']=state()['countLabel'];action('clearFilters',scope='all')
 run('input','click','500','300');action('openDetails');run('input','click','1276','200');results['realCloseButton']=not state()['detailsWanted'];shot('05-real-close-centered');run('input','click','500','380');results['staysClosed']=not state()['inspectorVisible'];run('input','key','ret');results['realEnter']=state()['inspectorVisible'];run('input','key','esc');results['realEsc']=not state()['detailsWanted']
 action('setView',view='gallery');action('clearSelection');run('input','click','350','390');run('input','key','shift','right');s=state();results['galleryRange']=s['selectedRows'];shot('08-caption-shift');run('input','key','down');state();shot('08-caption-arrow');action('setView',view='list');action('clearSelection')
 run('resize');current=call('settings.get')['result'];call('settings.patch',{'expectedRevision':current['metadata']['observedRevision'],'patch':{'preferences':{'appearance':{'theme':'light'}}}});time.sleep(.5);shot('09-light-minimum');current=call('settings.get')['result'];call('settings.patch',{'expectedRevision':current['metadata']['observedRevision'],'patch':{'preferences':{'appearance':{'theme':'dark'}}}});time.sleep(.5);shot('09-dark-minimum')
except Exception as e:results['stopped']=repr(e)
finally:(root/'final-input-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
