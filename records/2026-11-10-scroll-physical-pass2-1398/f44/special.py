import pass2,os,sys,json,time,subprocess,threading,hashlib,shutil
from pathlib import Path
P=pass2.P;e=json.loads((P/'env.json').read_text());rpc=pass2.rpc
import rfb
kind=sys.argv[1]
def patch(p):
 s=rpc('settings.get');return rpc('settings.patch',{'patch':p,'expectedRevision':s['metadata']['observedRevision']})
if kind=='user':
 s=rpc('settings.get');old=s['document']['actions']['scroll']['shortcut'];patch({'actions':{'scroll':{'shortcut':'Ctrl+Shift+F7'}}})
 f=subprocess.Popen(['python3',str(P/'qt_fixture.py')],env=e,stdout=open(P/'user-fixture.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
 try:
  time.sleep(3);v=rfb.RFB(5901 if os.uname().nodename=='fedora' else 5900);before=rpc('history.list',{'limit':200});v.key('ctrl','shift','f7');time.sleep(1);v.screenshot(P/'user-selector.png');v.drag(100,200,1060,800)
  for i in range(25):v.screenshot(P/('user-%02d.png'%i));time.sleep(.3)
  (P/'user-result.json').write_text(json.dumps({'before':before,'after':rpc('history.list',{'limit':200})},indent=2))
 finally:f.terminate();f.wait(10);patch({'actions':{'scroll':{'shortcut':old}}})
elif kind in ['stop','stop2']:
 f=subprocess.Popen(['python3',str(P/'qt_fixture.py'),'--rows','600','--start','23400'],env=e,stdout=open(P/'stop-fixture.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
 try:time.sleep(3);pass2.capture('stop-top2' if kind=='stop2' else 'stop-top',600,40000,stop=.9 if kind=='stop2' else .05)
 finally:f.terminate();f.wait(10)
elif kind=='settings':
 rpc('ui.show',{'view':'settings'});time.sleep(3);v=rfb.RFB(5901 if os.uname().nodename=='fedora' else 5900);v.screenshot(P/'settings.png');(P/'view-state.json').write_text(json.dumps(rpc('ui.viewState'),indent=2))
