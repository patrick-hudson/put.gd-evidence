from pathlib import Path
import os,sys,subprocess,time,json,hashlib
sys.path.insert(0,'/home/lab/work/s3a');import record_run,rfb
P=Path('/home/lab/work/s3a/c16');P.mkdir(mode=0o700);env,desktop=record_run.session_environment()
for n in ['c','d','s','cache','r','archive']:(P/n).mkdir(mode=0o700)
for k,n in [('CONFIG','c'),('DATA','d'),('STATE','s'),('CACHE','cache'),('RUNTIME','r')]:env['XDG_'+k+('_DIR' if k=='RUNTIME' else '_HOME')]=str(P/n)
env.update(PATH='/usr/bin:/bin',PUTGD_RECORD_DEBUG_LOG=str(P/'helper.log'),PIPEWIRE_RUNTIME_DIR='/run/user/1000',PULSE_SERVER='unix:/run/user/1000/pulse/native')
sock=str(P/'r/putgd/session.sock');assert len(sock.encode())<=107
(P/'socket-preflight.json').write_text(json.dumps({'path':sock,'utf8Bytes':len(sock.encode())}))
def cli(m,a={}):
 x=subprocess.run(['/usr/bin/putgd-cli','--socket',sock,m,json.dumps(a)],env=env,text=True,capture_output=True);o=json.loads(x.stdout);(P/'rpc.jsonl').open('a').write(json.dumps({'method':m,'params':a,'exitCode':x.returncode,'reply':o})+'\n');return o
q=subprocess.Popen(['/usr/bin/putgd','--background'],env=env,stdout=open(P/'resident.log','w'),stderr=subprocess.STDOUT);(P/'resident.pid').write_text(str(q.pid))
try:
 for _ in range(100):
  if Path(sock).exists():break
  time.sleep(.1)
 settings=cli('settings.get')['result'];doc=settings['document'];doc['archive'].update(keepUploads=True,root=str(P/'archive'));cli('settings.save',{'document':doc,'expectedRevision':settings['metadata']['observedRevision']})
 probe=json.loads(subprocess.check_output(['/usr/bin/putgd-record','--scroll-capabilities'],env=env));r={'build':json.loads(subprocess.check_output(['/usr/bin/putgd-cli','--version-json'],env=env)),'probe':probe,'capabilities':cli('scroll.capabilities'),'beforeHistory':cli('history.list',{'limit':200}),'requests':[]}
 cli('ui.show',{'view':'history'});time.sleep(2)
 v=rfb.RFB(5989);v.screenshot(P/'unavailable-button.png');v.close()
 r['uiSnapshot']=cli('ui.snapshot');r['uiViewState']=cli('ui.viewState')
 os.environ.update(env)
 try:
  import pyatspi
  found=[]
  def walk(n,depth=0):
   if depth>10:return
   if 'scroll' in (n.name or '').lower():found.append({'role':n.getRoleName(),'name':n.name,'description':n.description,'enabled':n.getState().contains(pyatspi.STATE_ENABLED)})
   for child in n:walk(child,depth+1)
  for app in pyatspi.Registry.getDesktop(0):
   if app.name=='putgd-ui':walk(app)
  r['accessibleScrollControls']=found
 except Exception as ex:r['accessibleError']=str(ex)
 for m,a in [('action.invoke',{'action':'scroll'}),('scroll.prepare',{}),('scroll.prepare',{'rect':[100,200,960,600],'maxHeight':30000})]:r['requests'].append({'method':m,'params':a,'reply':cli(m,a)})
 time.sleep(2);r['afterHistory']=cli('history.list',{'limit':200});r['archivePngs']=list(map(str,(P/'archive').rglob('*.png')));(P/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps({'probe':probe,'requests':r['requests'],'historyUnchanged':r['beforeHistory']['result']==r['afterHistory']['result'],'pngs':r['archivePngs']}),flush=True)
finally:
 cli('ui.quit');time.sleep(2)
 if q.poll() is None:q.terminate();q.wait(10)
