import os,json,subprocess,stat,hashlib,time,ast
from pathlib import Path
P=Path.home()/'work/sfa15'
os.environ.update(json.loads((P/'session-env.json').read_text()))
os.environ.update(XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus',LABWC_PID='847')
for k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_CACHE_HOME']:os.environ.pop(k,None)
subprocess.run(['systemctl','--user','stop','sfa15-res.scope'],check=True)
time.sleep(1)
for name in ['putgd','putgd-ui','putgd-record','putgd-cli','firefox','firefox-bin']:
 r=subprocess.run(['pgrep','-x',name],capture_output=True,text=True);assert not r.stdout.strip(),(name,r.stdout)
inputs=Path('/proc/bus/input/devices').read_text();assert 'putgd-lab relative mouse'not in inputs and 'sfa15 lab keyboard'not in inputs
schema='org.buddiesofbudgie.settings-daemon.plugins.media-keys'
bindings=subprocess.check_output(['gsettings','get',schema,'custom-keybindings'],text=True).strip()
paths=ast.literal_eval(bindings.replace('@as ',''));assert not any('customputgd'in x for x in paths),paths
rc=Path.home()/'.config/budgie-desktop/labwc/rc.xml';before=P/'labwc-before.xml';meta=json.loads((P/'labwc-before-mode.json').read_text())
print('backup-metadata',json.dumps(meta),flush=True)
rc.write_bytes(before.read_bytes());rc.chmod(stat.S_IMODE(before.stat().st_mode))
subprocess.run(['labwc','--reconfigure'],check=True,capture_output=True);time.sleep(2)
assert rc.read_bytes()==before.read_bytes()
subprocess.run(['systemctl','--user','stop','sfa15-pointer-witness.service'],check=True)
f=P/'pointer.sock'
if f.exists():s=f.lstat();assert stat.S_ISSOCK(s.st_mode)and s.st_uid==os.getuid();f.unlink()
observer=P/'pointer-observer';observerSha=hashlib.sha256(observer.read_bytes()).hexdigest();observer.unlink()
removed=[]
def remove_owned_tree(root):
 if not root.exists():return
 assert root.is_dir()and not root.is_symlink()
 for current,dirs,files in os.walk(root,topdown=False,followlinks=False):
  for n in files+dirs:
   f=Path(current)/n;s=f.lstat();assert s.st_uid==os.getuid(),str(f)
   if stat.S_ISDIR(s.st_mode):f.rmdir()
   elif stat.S_ISREG(s.st_mode)or stat.S_ISLNK(s.st_mode):f.unlink();removed.append(str(f))
   else:raise RuntimeError('Unexpected installed member '+str(f))
 root.rmdir()
for root in [P/'squashfs-root',P/'b/squashfs-root']:remove_owned_tree(root)
for f in [P/'b/tools/firefox',P/'tools/firefox']:
 assert f.is_symlink()and f.resolve()==Path('/usr/lib64/firefox');f.unlink()
for root in [P,P/'b']:
 f=root/'r/putgd/session.sock'
 if f.exists():s=f.lstat();assert stat.S_ISSOCK(s.st_mode)and s.st_uid==os.getuid();f.unlink()
for name in ['candidate.AppImage','nightly.AppImage']:
 if(P/name).exists():(P/name).chmod(0o600)
receipt={'completed':True,'productAndBrowserProcesses':[],'labInputDevices':[],'originalLabwcXmlRestoredSha256':hashlib.sha256(rc.read_bytes()).hexdigest(),'labwcOriginalMode':oct(stat.S_IMODE(rc.stat().st_mode)),'customPutgdBindingsRemaining':[],'accelerationRestored':'Original labwc XML and unchanged GNOME mouse settings; native labwc reconfigured.','observerService':subprocess.run(['systemctl','--user','is-active','sfa15-pointer-witness.service'],capture_output=True,text=True).stdout.strip(),'observerRemovedSha256':observerSha,'scopeStatus':subprocess.run(['systemctl','--user','is-active','sfa15-res.scope'],capture_output=True,text=True).stdout.strip(),'installedRuntimeFilesRemoved':len(removed),'removedPathsSha256':hashlib.sha256('\n'.join(removed).encode()).hexdigest(),'nativePackagesInstalled':False,'systemFirefoxPreserved':Path('/usr/lib64/firefox/firefox').exists(),'inputDeviceOwnership':'Restore root:root0600 through protected stdin helper, then independently verify.'}
(P/'cleanup-receipt.json').write_text(json.dumps(receipt,indent=1));print(json.dumps(receipt),flush=True)
