import os,stat,json,hashlib,subprocess,time,sys
from pathlib import Path
P=Path.home()/'work/sfa15';host=sys.argv[1]
os.environ.update(DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus',XDG_RUNTIME_DIR='/run/user/1000')
for k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_CACHE_HOME']:os.environ.pop(k,None)
for name in ['putgd','putgd-record','putgd-ui','putgd-cli','firefox','firefox-bin','chrome','chrome_crashpad']:
 q=subprocess.run(['pgrep','-x',name],capture_output=True,text=True);assert not q.stdout.strip(),(name,q.stdout)
inputs=Path('/proc/bus/input/devices').read_text();assert 'putgd-lab relative mouse' not in inputs and 'sfa15 lab keyboard' not in inputs
restore=''
if host=='m74':
 d=json.loads((P/'cinnamon-acceleration-before.json').read_text());print('restore metadata keys',list(d))
 value=d['value'];subprocess.run(['gsettings','set','org.cinnamon.desktop.peripherals.mouse','accel-profile',value],check=True)
 got=subprocess.check_output(['gsettings','get','org.cinnamon.desktop.peripherals.mouse','accel-profile'],text=True).strip();assert got==value
 restore='Cinnamon global acceleration profile restored to '+got+'; the lab device is gone.'
elif host=='f44':
 assert (P/'gnome-restored.json').exists();assert json.loads((P/'gnome-restored.json').read_text())==json.loads((P/'gnome-before.json').read_text());restore='GNOME extension files/lists/disable flag and mouse profile restored exactly after final login.'
else:raise RuntimeError('Host-specific acceleration restoration must be supplied before cleanup')
removed=[]
for root in [P/'squashfs-root',P/'b/squashfs-root']:
 if not root.exists():continue
 assert root.is_dir() and not root.is_symlink()
 for current,dirs,files in os.walk(root,topdown=False,followlinks=False):
  for n in files+dirs:
   f=Path(current)/n;s=f.lstat();assert s.st_uid==os.getuid(),str(f)
   if stat.S_ISDIR(s.st_mode):f.rmdir()
   elif stat.S_ISREG(s.st_mode) or stat.S_ISLNK(s.st_mode):f.unlink();removed.append(str(f))
   else:raise RuntimeError('unexpected package member '+str(f))
 root.rmdir()
for root in [P,P/'b']:
 f=root/'r/putgd/session.sock'
 if f.exists():
  s=f.lstat();assert stat.S_ISSOCK(s.st_mode) and s.st_uid==os.getuid();f.unlink()
for name in ['candidate.AppImage','nightly.AppImage']:
 if (P/name).exists():(P/name).chmod(0o600)
receipt={'completed':True,'productAndBrowserProcesses':[],'labInputDevices':[],'accelerationRestored':restore,'nativePackagesInstalled':False,'appImageRuntimeFilesRemoved':len(removed),'packageInputs':'Original AppImages retained privately as non-executable inputs; extracted installed runtimes removed.','removedPathsSha256':hashlib.sha256('\n'.join(removed).encode()).hexdigest(),'gnomeExtensionsChanged':host=='f44','scopeStatus':subprocess.run(['systemctl','--user','is-active','sfa15-res.scope'],capture_output=True,text=True).stdout.strip()};(P/'cleanup-receipt.json').write_text(json.dumps(receipt,indent=1));print(json.dumps(receipt,indent=1))
