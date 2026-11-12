from pathlib import Path
import sys,subprocess,json,time,shlex,hashlib,tarfile
from PIL import Image
R=Path('/home/patrick/work/sc2');sys.path.insert(0,str(R/'tools/lab'));sys.path.insert(0,str(R/'drivers'));import lab,scroll_run,argparse
k=sys.argv[1];run=R/'work/lab-runs'/('c'+k);out=R/'evidence'/k;out.mkdir(parents=True)
profile,golden,key,port,vnc={'o':('omarchy-hyprland','omarchy-hyprland-20261108','lab-bootstrap-omarchy/identity',22440,80),'b':('fedora45-budgie','fedora45-budgie','lab-bootstrap-d69/identity',22442,82),'n':('neon-kde-wayland','neon-user-6.8.1-20261023-9ef808278853','lab-bootstrap-d69/neon-user/identity',22472,44),'k':('kde-scroll-appimage','transfer-541c1316ab6b','lab-bootstrap-d69/rec-ws/identity',22234,46)}[k]
G=Path('/home/patrick/work/put.gd/work/lab-images')/golden;paths=[run/'qmp.sock',run/'vnc.sock',Path('/tmp/cp2/runtime/putgd/session.sock')];assert all(len(str(p.resolve()).encode())<=107 for p in paths);(out/'host-socket-preflight.json').write_text(json.dumps({str(p):len(str(p.resolve()).encode()) for p in paths}));c=['python3',str(R/'tools/lab/lab.py'),'launch','--profile',profile,'--golden',str(G/'image.qcow2'),'--run',str(run),'--bootstrap-key','/home/patrick/work/put.gd/work/'+key,'--known-hosts','/home/patrick/work/put.gd/work/lab-bootstrap-d69/known_hosts-kde' if k=='k' else str(G/'known_hosts'),'--ssh-port',str(port),'--vnc-display',str(vnc),'--timeout','300'];p=subprocess.run(c,cwd=R,capture_output=True,text=True);(out/'launch.log').write_text(p.stdout+p.stderr);p.check_returncode();Image.open(lab.screenshot(run,'cap-followup-desktop')['path']).save(out/'desktop-ready.png');(out/'booted').write_text('ready')
while not (out/'wall-verified').exists():time.sleep(.2)
deps={'o':'pacman -Sy --noconfirm python-pyqt6 python-pillow python-numpy','b':'dnf --setopt=zchunk=False install -y python3-pyqt6-base python3-pillow python3-numpy','n':'apt-get update && sudo -n apt-get install -y python3-pyqt6 python3-pil python3-numpy','k':'apt-get update && sudo -n apt-get install -y python3-pyqt6 python3-pil python3-numpy'}[k];(out/'dependencies.log').write_text(lab.ssh(run,'sudo -n '+deps,timeout=300));(out/'install.json').write_text(json.dumps(lab.install(run,appimage=next((R/'pkg').glob('*.AppImage'))),indent=2))
for src,dst in [('cap-proof-guest.py','cap-proof-guest.py'),('cap-receiver.py','cap-receiver.py'),('v3ruler.py','cap-ruler.py'),('scroll_run.py','scroll_run.py')]:lab.put(run,R/'drivers'/src,'/home/lab/'+dst)
print(lab.guest_session(run,'nohup python3 -u /home/lab/cap-proof-guest.py > /tmp/cap-proof.log 2>&1 < /dev/null & echo started',timeout=60),flush=True)
def exists(name):return lab.ssh(run,'test -f /tmp/cp2/'+name+' && echo yes || true',timeout=30).strip()=='yes'
for _ in range(360):
 if exists('ready'):break
 time.sleep(.5)
else:raise RuntimeError('capture not ready')
lab.pointer(run,1150,400,1280,800);time.sleep(.3);im=Image.open(lab.screenshot(run,'cap-ready-before-start')['path']).convert('RGB').crop((100,100,1060,700));im.save(out/'ready-region.png');v=scroll_run.verify(out/'ready-region.png',argparse.Namespace(scale=1,height=600,rows=600,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0));(out/'readiness-verification.json').write_text(json.dumps(v,indent=2));assert v['pass'],v;lab.ssh(run,'touch /tmp/cp2/start-verified')
for _ in range(360):
 if exists('photo-ready'):break
 time.sleep(.5)
else:raise RuntimeError('no captured result')
time.sleep(1);Image.open(lab.screenshot(run,'held-cap-warning')['path']).save(out/'warning.png');lab.ssh(run,'touch /tmp/cp2/release-upload')
for _ in range(240):
 if exists('done'):break
 time.sleep(.5)
else:raise RuntimeError('capture proof not completed')
for n in ['capture.png','received.png','received.multipart','result.json','verification.json','upload-verification.json','upload-completion.json','helper.log']:lab.get(run,'/tmp/cp2/case/'+n,out/n)
for n in ['rpc.jsonl','version.json','capabilities.json','socket-preflight.json']:lab.get(run,'/tmp/cp2/'+n,out/n)
receipt=json.loads((out/'upload-verification.json').read_text());assert receipt['loopbackPayloadEqualsPng'] and json.loads((out/'verification.json').read_text())['pass'];(out/'run-identity.json').write_bytes((run/'state.json').read_bytes());files={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()};(out/'manifest.json').write_text(json.dumps(files,indent=2))
with tarfile.open(R/('cap-'+k+'.tgz'),'w:gz') as t:
 for f in out.iterdir():
  if f.is_file():t.add(f,arcname=f.name)
(out/'export-ready').write_text('ready');print(k,'CAP PROOF EXPORTED',flush=True)
