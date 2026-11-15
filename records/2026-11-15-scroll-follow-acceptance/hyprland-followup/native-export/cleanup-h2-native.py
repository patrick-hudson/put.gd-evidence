import os,json,subprocess,stat,hashlib
from pathlib import Path
P=Path.home()/'work/sfa15'
os.environ.update(json.loads((P/'session-env.json').read_text()))
os.environ['XDG_RUNTIME_DIR']='/run/user/1000'
subprocess.run(['systemctl','--user','stop','sfa15-res.scope'],check=True)
for name in ['putgd','putgd-ui','putgd-record','putgd-cli','firefox','firefox-bin']:
 r=subprocess.run(['pgrep','-x',name],capture_output=True,text=True);assert not r.stdout.strip(),(name,r.stdout)
inputs=Path('/proc/bus/input/devices').read_text();assert 'putgd-lab relative mouse'not in inputs and 'sfa15 lab keyboard'not in inputs
before=json.loads((P/'input-before.json').read_text());subprocess.run(['hyprctl','reload'],check=True,capture_output=True)
restored={k:subprocess.check_output(['hyprctl','getoption','input:'+k],text=True).strip()for k in before};assert restored==before,(before,restored)
removed=[]
def remove_owned_tree(root):
 if not root.exists()and not root.is_symlink():return
 assert root.is_dir()and not root.is_symlink()
 for current,dirs,files in os.walk(root,topdown=False,followlinks=False):
  for n in files+dirs:
   f=Path(current)/n;s=f.lstat();assert s.st_uid==os.getuid(),str(f)
   if stat.S_ISDIR(s.st_mode):f.rmdir()
   elif stat.S_ISREG(s.st_mode)or stat.S_ISLNK(s.st_mode):f.unlink();removed.append(str(f))
   else:raise RuntimeError('Unexpected installed member '+str(f))
 root.rmdir()
for root in [P/'squashfs-root',P/'b/squashfs-root']:remove_owned_tree(root)
f=P/'b/tools/firefox'
if f.is_symlink():assert f.resolve()==P/'tools/firefox';f.unlink()
remove_owned_tree(P/'tools/firefox')
for root in [Path('/tmp/sh25'),Path('/tmp/sb25')]:
 if not root.exists():continue
 f=root/'putgd/session.sock'
 if f.exists():s=f.lstat();assert stat.S_ISSOCK(s.st_mode)and s.st_uid==os.getuid();f.unlink()
 f=root/'hypr';assert f.is_symlink()and f.resolve()==Path('/run/user/1000/hypr');f.unlink()
 for f in sorted(root.rglob('*'),key=lambda x:len(x.parts),reverse=True):assert f.is_dir()and not f.is_symlink();f.rmdir()
 root.rmdir()
for name in ['candidate.AppImage','nightly.AppImage']:
 if(P/name).exists():(P/name).chmod(0o600)
receipt={'completed':True,'productAndBrowserProcesses':[],'labInputDevices':[],'accelerationRestored':restored,'originalAcceleration':before,'scopeStatus':subprocess.run(['systemctl','--user','is-active','sfa15-res.scope'],capture_output=True,text=True).stdout.strip(),'installedRuntimeFilesRemoved':len(removed),'removedPathsSha256':hashlib.sha256('\n'.join(removed).encode()).hexdigest(),'nativePackagesInstalled':False,'inputDeviceOwnership':'Must restore root:root0600 using protected stdin helper, then independently verify before retirement.'}
(P/'cleanup-receipt.json').write_text(json.dumps(receipt,indent=1));print(json.dumps(receipt),flush=True)
