from pathlib import Path
import sys,shlex,time,json,subprocess,hashlib,tarfile
from PIL import Image
R=Path('/home/patrick/work/sc2');sys.path.insert(0,str(R/'tools/lab'));sys.path.insert(0,str(R/'drivers'));import lab,scroll_run,argparse
run=R/'work/lab-runs/ck';out=R/'evidence/k';bad=out/'failed-cp3';bad.mkdir(exist_ok=True)
for n in ['ready-region.png','readiness-verification.json']:
 if (out/n).exists():(bad/n).write_bytes((out/n).read_bytes())
lab.get(run,'/tmp/cap-proof.log',bad/'guest-error.log')
cleanup="""from pathlib import Path
import subprocess,time,os
p=Path('/tmp/cp3');js=p/'close-stale-own-notice.js';js.write_text("let a=[];for(const w of workspace.stackingOrder){let g=w.frameGeometry;if(String(w.resourceClass)==='org.kde.plasmashell'&&g.x===912&&g.y===632&&g.width===332&&g.height===78){a.push({id:String(w.internalId),x:g.x,y:g.y,width:g.width,height:g.height});w.closeWindow();}}print('cap-stale-close-'+JSON.stringify(a));")
i=subprocess.check_output(['qdbus6','org.kde.KWin','/Scripting','org.kde.kwin.Scripting.loadScript',str(js),'cap-stale-close'],text=True).strip();subprocess.run(['qdbus6','org.kde.KWin','/Scripting/Script'+i,'org.kde.kwin.Script.run'],check=True);time.sleep(1);subprocess.run(['qdbus6','org.kde.KWin','/Scripting','org.kde.kwin.Scripting.unloadScript','cap-stale-close']);r=subprocess.run(['journalctl','--user','-u','plasma-kwin_wayland.service','--since','2 minutes ago','--no-pager','-o','cat'],capture_output=True,text=True);print('\\n'.join(x for x in r.stdout.splitlines() if 'cap-stale-close-' in x))
"""
(out/'stale-notice-cleanup.log').write_text(lab.guest_session(run,'python3 -c '+shlex.quote(cleanup),timeout=60));time.sleep(1);lab.pointer(run,1150,400,1280,800);im=Image.open(lab.screenshot(run,'cap-ready-after-stale-notice')['path']).convert('RGB').crop((100,100,1060,700));im.save(out/'ready-region.png');v=scroll_run.verify(out/'ready-region.png',argparse.Namespace(scale=1,height=600,rows=600,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0));(out/'readiness-verification.json').write_text(json.dumps(v,indent=2));assert v['pass'],v
source=(R/'drivers/cap-proof-guest3.py').read_text();body=source[source.index("rpc('scroll.start'"):];header="""from pathlib import Path
import sys,os,subprocess,json,time,hashlib,shutil
P=Path('/tmp/cp3');paths=[P/'runtime/putgd/session.sock'];e=dict(os.environ);cli=str(Path.home()/'putgd-lab/bin/putgd-cli')
def rpc(m,a={}):
 r=subprocess.run([cli,'--socket',str(paths[0]),m,json.dumps(a)],env=e,capture_output=True,text=True,timeout=75);v=json.loads(r.stdout)
 with open(P/'rpc.jsonl','a') as f:f.write(json.dumps({'time':time.time(),'method':m,'params':a,'reply':v})+chr(10))
 assert v['ok'],v
 return v['result']
rows=[json.loads(l) for l in (P/'rpc.jsonl').read_text().splitlines()];ident=next(v['reply']['result']['id'] for v in rows if v['method']=='scroll.prepare');v=rpc('scroll.inspect',{'id':ident});assert v['state']=='ready',v
class Owned:
 def __init__(self,arg):
  self.pid=None
  for p in Path('/proc').iterdir():
   if not p.name.isdigit():continue
   try:
    a=(p/'cmdline').read_bytes().split(bytes([0]));env=(p/'environ').read_bytes().split(bytes([0]))
    if arg.encode() in a and (arg.endswith('receiver3.py') or b'XDG_CONFIG_HOME=/tmp/cp3/c' in env):self.pid=int(p.name)
   except OSError:pass
  assert self.pid,arg
 def terminate(self):os.kill(self.pid,15)
 def wait(self,t):time.sleep(.2)
fixture=Owned('/home/lab/cap-ruler.py');server=Owned('/home/lab/cap-receiver3.py')
""";temp=R/'drivers/k-resume-guest.py';temp.write_text(header+body);lab.put(run,temp,'/home/lab/k-resume-guest.py');print(lab.guest_session(run,'nohup python3 -u /home/lab/k-resume-guest.py > /tmp/k-resume.log 2>&1 < /dev/null & echo started'),flush=True)
def exists(n):return lab.ssh(run,'test -f /tmp/cp3/'+n+' && echo yes || true').strip()=='yes'
for _ in range(180):
 if exists('photo-ready'):break
 time.sleep(.2)
else:raise RuntimeError('no result after start')
time.sleep(1);Image.open(lab.screenshot(run,'cap-warning-after-clean-prepare')['path']).save(out/'warning.png');lab.ssh(run,'touch /tmp/cp3/release-upload')
for _ in range(180):
 if exists('done'):break
 time.sleep(.2)
else:raise RuntimeError('no upload proof')
for n in ['capture.png','received.png','received.multipart','result.json','verification.json','upload-verification.json','upload-completion.json','helper.log']:lab.get(run,'/tmp/cp3/case/'+n,out/n)
for n in ['rpc.jsonl','version.json','capabilities.json','socket-preflight.json']:lab.get(run,'/tmp/cp3/'+n,out/n)
files={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file() and f.name not in ['manifest.json','export-ready']};(out/'manifest.json').write_text(json.dumps(files,indent=2))
with tarfile.open(R/'cap-k.tgz','w:gz') as t:
 for f in out.rglob('*'):
  if f.is_file():t.add(f,arcname=str(f.relative_to(out)))
(out/'export-ready').write_text('ready');print('K CAP PROOF EXPORTED',flush=True)
