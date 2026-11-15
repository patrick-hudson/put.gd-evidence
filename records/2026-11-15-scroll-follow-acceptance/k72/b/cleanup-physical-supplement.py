import os,sys,json,subprocess,stat,hashlib,time
from pathlib import Path
P=Path.cwd();host=sys.argv[1];env=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
for k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_CACHE_HOME']:env.pop(k,None)
loaded=subprocess.run(['systemctl','--user','show','sfa15-res.scope','-p','LoadState','--value'],env=env,capture_output=True,text=True).stdout.strip()
if loaded!='not-found':subprocess.run(['systemctl','--user','stop','sfa15-res.scope'],env=env,check=True)
for name in ['putgd','putgd-ui','putgd-record','putgd-cli','firefox','firefox-bin','chrome','chrome_crashpad']:
 v=subprocess.run(['pgrep','-x',name],capture_output=True,text=True).stdout.strip();assert not v,(name,v)
inputs=Path('/proc/bus/input/devices').read_text();assert 'putgd-lab relative mouse'not in inputs and 'sfa15 lab keyboard'not in inputs
before=json.loads((P/'input-before.json').read_text());restored={}
if host in ['aurora-amd','k72']:
 f=Path.home()/'.config/kcminputrc'
 if before['exists']:
  b=P/'kcminputrc-before';assert hashlib.sha256(b.read_bytes()).hexdigest()==before['sha256'];f.write_bytes(b.read_bytes());f.chmod(int(before['mode'],8));assert hashlib.sha256(f.read_bytes()).hexdigest()==before['sha256'];restored={'kcminputrcSha256':before['sha256'],'mode':before['mode']}
 else:
  if f.exists():
   assert f.read_text().strip()=='[Libinput][4660][22137][putgd-lab relative mouse with wheel]\nPointerAccelerationProfile=1',f.read_text();f.unlink()
  restored={'kcminputrcAbsent':True}
 if host=='k72':
  f=Path.home()/'.local/share/applications/putgd-sfa15-record.desktop';assert f.read_bytes()==(P/'installed-recorder-permission-entry.txt').read_bytes();f.unlink();subprocess.run(['kbuildsycoca6','--noincremental'],env=env,stdout=(P/'kbuildsycoca-cleanup.log').open('w'),stderr=subprocess.STDOUT,check=True)
elif host=='f44':
 assert json.loads((P/'gnome-restored.json').read_text())==json.loads((P/'gnome-before.json').read_text());restored={'gnomeExtensionsAndMouse':'Exact originals restored after final GDM login'}
else:
 for k,v in before['values'].items():subprocess.run(['gsettings','set',before['schema'],k,v],env=env,check=True)
 restored={'mouseSettings':{k:subprocess.check_output(['gsettings','get',before['schema'],k],env=env,text=True).strip()for k in before['values']}};assert restored['mouseSettings']==before['values']
removed=[]
for root in [P/'squashfs-root',P/'b/squashfs-root']:
 if not root.exists():continue
 assert root.is_dir()and not root.is_symlink()
 for current,dirs,files in os.walk(root,topdown=False,followlinks=False):
  for n in files+dirs:
   f=Path(current)/n;s=f.lstat();assert s.st_uid==os.getuid()
   if stat.S_ISDIR(s.st_mode):f.rmdir()
   elif stat.S_ISREG(s.st_mode)or stat.S_ISLNK(s.st_mode):f.unlink();removed.append(str(f))
   else:raise RuntimeError('Unexpected package member '+str(f))
 root.rmdir()
for root in [P,P/'b']:
 f=root/'r/putgd/session.sock'
 if f.exists():s=f.lstat();assert stat.S_ISSOCK(s.st_mode)and s.st_uid==os.getuid();f.unlink()
for n in ['candidate.AppImage','nightly.AppImage']:
 if(P/n).exists():(P/n).chmod(0o600)
assert not list(Path('/tmp').glob('sfa15-pointer-*.js')),'Temporary pointer script remained'
receipt={'completed':True,'productAndBrowserProcesses':[],'labInputDevices':[],'accelerationRestored':restored,'installedRuntimeFilesRemoved':len(removed),'removedPathsSha256':hashlib.sha256('\n'.join(removed).encode()).hexdigest(),'nativePackagesInstalled':False,'scopeStatus':subprocess.run(['systemctl','--user','is-active','sfa15-res.scope'],env=env,capture_output=True,text=True).stdout.strip(),'recorderPermissionEntryRemoved':host=='k72','kwinWitness':'One-shot scripts unloaded per query; no temporary script files remain'if host=='k72'else None}
(P/'cleanup-receipt.json').write_text(json.dumps(receipt,indent=1));print(json.dumps(receipt),flush=True)
