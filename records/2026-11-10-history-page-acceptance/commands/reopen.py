import subprocess,json,time,sys
from pathlib import Path
base=Path.home()/'putgd-lab/h1396-ci/control.py';root=Path('/tmp/h396k')
log=[]
def run(*args):
 p=subprocess.run(['python3',str(base),*args],capture_output=True,text=True)
 log.append({'args':args,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 (root/'reopen-log.json').write_text(json.dumps(log,indent=2))
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
 action('setView',view='list');action('clearSelection');run('input','click','500','300');run('input','key','esc');run('input','double','500','300');results['doubleClickReopens']=state()['inspectorVisible'];shot('05-doubleclick');run('input','key','esc');state();run('input','click','1032','24');call('ui.show',{'view':'history'});s=state();results['closedChoiceSurvivesWindowReopen']=not s['detailsWanted'];shot('05-window-reopened')
 action('toggleDetails');state();shot('05-toggle');action('closeDetails')
 current=call('settings.get')['result'];call('settings.patch',{'expectedRevision':current['metadata']['observedRevision'],'patch':{'preferences':{'appearance':{'theme':'light'}}}});time.sleep(.5);shot('09-light-final');run('input','key','down');state();shot('08-down-final')
except Exception as e:results['stopped']=repr(e)
finally:(root/'reopen-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
