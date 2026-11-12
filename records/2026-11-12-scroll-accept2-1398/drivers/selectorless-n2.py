import sys,time,json,shlex,subprocess
from pathlib import Path
from PIL import Image
B=Path('/home/patrick/work/sa2lab');D=Path('/home/patrick/work/sa2vm');sys.path.insert(0,str(B/'tools/lab'));import lab
r=B/'work/lab-runs/sa2n2';o=D/'ev/sa2n2/selectorless';o.mkdir(exist_ok=True,parents=True)
def cmd(s):return lab.guest_session(r,s+' 2>&1 || true',timeout=240)
pkg=next((D/'artifacts').glob('*.deb'));lab.put(r,pkg,'/tmp/'+pkg.name);(o/'install.log').write_text(lab.ssh(r,'sudo -n apt-get install -y /tmp/'+pkg.name+' python3-pyqt6 python3-pil python3-numpy',timeout=240))
for n in ['qt_fixture.py','scroll_run.py']:lab.put(r,D/'fixtures'/n,'/home/lab/'+n)
init="""from pathlib import Path
import os,time,subprocess,json
P=Path('/tmp/s23');assert not P.exists()
for n in ['c','d','s','cache','r','archive','cases']:(P/n).mkdir(parents=True,mode=0o700)
(P/'runtime').symlink_to(P/'r',target_is_directory=True);e=dict(os.environ);real=e['XDG_RUNTIME_DIR'];e['WAYLAND_DISPLAY']=str(Path(real)/e['WAYLAND_DISPLAY']);e['PIPEWIRE_RUNTIME_DIR']=real
for k,n in [('CONFIG','c'),('DATA','d'),('STATE','s'),('CACHE','cache'),('RUNTIME','r')]:e['XDG_'+k+('_DIR' if k=='RUNTIME' else '_HOME')]=str(P/n)
e['PUTGD_RECORD_DEBUG_LOG']=str(P/'helper.log');paths=[P/'r/putgd/session.sock',P/'runtime/putgd/session.sock'];assert all(len(str(x.resolve()).encode())<=107 for x in paths);(P/'socket-preflight.json').write_text(json.dumps({str(x):len(str(x.resolve()).encode()) for x in paths}));(P/'env.json').write_text(json.dumps(e));os.chmod(P/'env.json',0o600)
q=subprocess.Popen(['/usr/bin/putgd','--background'],env=e,stdout=open(P/'resident.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'resident.pid').write_text(str(q.pid));time.sleep(5)
def rpc(m,a={}):
 z=subprocess.run(['/usr/bin/putgd-cli','--socket',str(P/'r/putgd/session.sock'),m,json.dumps(a)],env=e,capture_output=True,text=True,timeout=70);v=json.loads(z.stdout)
 with open(P/'rpc.jsonl','a') as f:f.write(json.dumps({'method':m,'params':a,'reply':v})+'\\n')
 return v
s=rpc('settings.get')['result'];doc=s['document'];doc['archive'].update(keepUploads=True,root=str(P/'archive'));rpc('settings.save',{'document':doc,'expectedRevision':s['metadata']['observedRevision']});caps=rpc('scroll.capabilities');b=rpc('history.list',{'limit':200});a=rpc('action.invoke',{'action':'scroll'});c=rpc('history.list',{'limit':200});(P/'refusal.json').write_text(json.dumps({'capabilities':caps,'action':a,'historyUnchanged':b['result']==c['result'],'before':b,'after':c},indent=2));(P/'version.json').write_text(subprocess.check_output(['/usr/bin/putgd-cli','--version-json'],text=True));(P/'capabilities.json').write_text(json.dumps(caps,indent=2));print(json.dumps(caps))
"""
(o/'probe.log').write_text(cmd('python3 -c '+shlex.quote(init)));lab.pointer(r,930,82,1280,800);time.sleep(1.5);Image.open(lab.screenshot(r,'selectorless-unavailable-tooltip')['path']).save(o/'window.png')
code="""from pathlib import Path
import os,json,subprocess,time,sys,hashlib,shutil,argparse
P=Path('/tmp/s23');e=json.loads((P/'env.json').read_text());closed=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:
  if (q/'comm').read_text().strip()=='putgd-ui' and ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (q/'environ').read_bytes().split(bytes([0])):os.kill(int(q.name),15);closed.append(int(q.name))
 except OSError:pass
(P/'dashboard-preparation.json').write_text(json.dumps({'closedOwnedUiPids':closed}));time.sleep(1)
def rpc(m,a={}):
 z=subprocess.run(['/usr/bin/putgd-cli','--socket',str(P/'r/putgd/session.sock'),m,json.dumps(a)],env=e,capture_output=True,text=True,timeout=70);v=json.loads(z.stdout)
 with open(P/'rpc.jsonl','a') as f:f.write(json.dumps({'method':m,'params':a,'reply':v})+'\\n')
 assert v['ok'],v
 return v['result']
q=type('OwnedFixture',(),{'terminate':lambda self:os.kill(int((P/'fixture.pid').read_text()),15),'wait':lambda self,t:None})();d=P/'cases/explicit-ruler';d.mkdir();off=(P/'helper.log').stat().st_size if (P/'helper.log').exists() else 0
try:
 v=rpc('scroll.prepare',{'rect':[100,200,960,600],'maxHeight':40000});ident=v['id']
 while v['state']!='ready':time.sleep(.1);v=rpc('scroll.inspect',{'id':ident})
 rpc('scroll.start',{'id':ident})
 for _ in range(1200):
  v=rpc('scroll.inspect',{'id':ident})
  if v['state'] in ['done','failed','cancelled']:break
  time.sleep(.1)
 (d/'result.json').write_text(json.dumps({'capture':v},indent=2));sha=v.get('result',{}).get('sha256')
 for _ in range(80):
  found=[f for f in (P/'archive').rglob('*.png') if hashlib.sha256(f.read_bytes()).hexdigest()==sha]
  if found:shutil.copyfile(found[0],d/'capture.png');break
  time.sleep(.1)
 sys.path.insert(0,'/home/lab');import scroll_run
 ver=scroll_run.verify(d/'capture.png',argparse.Namespace(scale=1,height=2400,rows=60,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0));(d/'verification.json').write_text(json.dumps(ver,indent=2));print('actual verifier',ver['pass'])
finally:q.terminate();q.wait(10);(d/'helper.log').write_bytes((P/'helper.log').read_bytes()[off:]);rpc('ui.quit')
"""
(o/'fixture-setup.log').write_text(cmd('python3 -c '+shlex.quote("from pathlib import Path\nimport os,json,subprocess,time,sys,hashlib,shutil,argparse\nP=Path('/tmp/s23');e=json.loads((P/'env.json').read_text());closed=[]\nfor q in Path('/proc').iterdir():\n if not q.name.isdigit():continue\n try:\n  if (q/'comm').read_text().strip()=='putgd-ui' and ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (q/'environ').read_bytes().split(bytes([0])):os.kill(int(q.name),15);closed.append(int(q.name))\n except OSError:pass\n(P/'dashboard-preparation.json').write_text(json.dumps({'closedOwnedUiPids':closed}));time.sleep(1)\ndef rpc(m,a={}):\n z=subprocess.run(['/usr/bin/putgd-cli','--socket',str(P/'r/putgd/session.sock'),m,json.dumps(a)],env=e,capture_output=True,text=True,timeout=70);v=json.loads(z.stdout)\n with open(P/'rpc.jsonl','a') as f:f.write(json.dumps({'method':m,'params':a,'reply':v})+'\\\\n')\n assert v['ok'],v\n return v['result']\nq=subprocess.Popen(['python3','/home/lab/qt_fixture.py','--rows','60'],env=dict(e,SC_Y='200'),stdout=open(P/'fixture.log','w'),stderr=subprocess.STDOUT,start_new_session=True);time.sleep(3);(P/'fixture.pid').write_text(str(q.pid))\n")))
ready=Image.open(lab.screenshot(r,'native-ruler-ready')['path']).convert('RGB').crop((100,200,1060,800));ready.save(o/'ready-region.png');sys.path.insert(0,str(D/'fixtures'));import scroll_run,argparse
ver=scroll_run.verify(o/'ready-region.png',argparse.Namespace(scale=1,height=600,rows=60,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0));(o/'readiness-verification.json').write_text(json.dumps(ver,indent=2));assert ver['pass'],ver
(o/'explicit.log').write_text(cmd('python3 -c '+shlex.quote(code)))
for n in ['version.json','capabilities.json','refusal.json','rpc.jsonl','socket-preflight.json','dashboard-preparation.json']:
 lab.get(r,'/tmp/s23/'+n,o/n)
(o/'explicit-ruler').mkdir(exist_ok=True)
for n in ['capture.png','result.json','helper.log','verification.json']:lab.get(r,'/tmp/s23/cases/explicit-ruler/'+n,o/'explicit-ruler'/n)
(o/'done').write_text('done');print('N2 SELECTORLESS COMPLETE')
