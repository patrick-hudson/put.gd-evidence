from pathlib import Path
import json,hashlib,subprocess,os,sys
P=Path.cwd();host=sys.argv[1];env=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
if host=='m74':
 schema='org.cinnamon.desktop.peripherals.mouse';data={'schema':schema,'values':{k:subprocess.check_output(['gsettings','get',schema,k],env=env,text=True).strip()for k in ['accel-profile','speed']}}
 pk=subprocess.check_output(['dpkg-query','-W','cinnamon','muffin'],text=True)
else:
 f=Path.home()/'.config/kcminputrc';data={'exists':f.exists(),'mode':oct(f.stat().st_mode&0o777)if f.exists()else None,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()if f.exists()else None}
 if f.exists():(P/'kcminputrc-before').write_bytes(f.read_bytes())
 pk=subprocess.check_output(['rpm','-q','plasma-workspace','kwin'],text=True)
(P/'input-before.json').write_text(json.dumps(data,indent=1))
(P/'host-proof.json').write_text(json.dumps({'osRelease':Path('/etc/os-release').read_text(),'packages':pk,'nativeSession':{k:v for k,v in (line.split('=',1)for line in subprocess.check_output(['systemctl','--user','show-environment'],env=env,text=True).splitlines()if '='in line)if k in ['DISPLAY','WAYLAND_DISPLAY','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP']},'memory':subprocess.check_output(['free','-g'],text=True),'load':subprocess.check_output(['uptime'],text=True)},indent=1))
import rfb
v=rfb.RFB(5900);v.screenshot(P/'baseline-desktop.png');v.close()
print('Baseline recorded')
