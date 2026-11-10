import subprocess,json,time,sys
from pathlib import Path
base=Path.home()/'putgd-lab/h1396-ci/control.py';root=Path('/tmp/h396k')
log=[]
def run(*args):
 p=subprocess.run(['python3',str(base),*args],capture_output=True,text=True)
 log.append({'args':args,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 (root/'followup-log.json').write_text(json.dumps(log,indent=2))
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
 call('ui.show',{'view':'history'});action('goToPage',page=1);action('closeDetails');run('input','click','500','300');run('input','key','alt','right');s=state();results['altRightFocused']=s['page']['page'];shot('03-focused-right');run('input','click','500','300');run('input','key','alt','left');results['altLeftFocused']=state()['page']['page'];shot('03-focused-left')
 action('openDetails');shot('05-before-real-close');run('input','click','1288','200');results['closeButton']=state()['detailsWanted']==False;run('input','click','500','380');results['staysClosed']=not state()['inspectorVisible'];shot('05-real-closed');run('input','key','ret');results['enterReopens']=state()['inspectorVisible'];shot('05-real-enter');run('input','key','esc');results['escCloses']=not state()['detailsWanted'];shot('05-real-esc')
 run('input','click','500','300');run('input','key','pgdn');s=state();shot('04-pinned-scroll');before=s['selectedIds'];run('input','click','400','180');results['headingClickPreservesSelection']=state()['selectedIds']==before;shot('06-heading-click')
 action('setView',view='gallery');run('input','click','350','260');run('input','key','shift','right');s=state();results['galleryShiftSelection']=s['selectedRows'];shot('08-shift-range');run('input','key','down');state();shot('08-arrow');action('setView',view='list')
 current=call('settings.get')['result'];call('settings.patch',{'expectedRevision':current['metadata']['observedRevision'],'patch':{'preferences':{'appearance':{'theme':'light'}}}});shot('09-light');results['theme']='light captured'
except Exception as e:results['stopped']=repr(e)
finally:
 (root/'followup-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
