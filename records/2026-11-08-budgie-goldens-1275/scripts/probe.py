#!/usr/bin/python3
"""Run in a fresh Budgie overlay as lab, using its real desktop environment."""
from pathlib import Path
import os,subprocess,json,time,xml.etree.ElementTree as ET
out=Path('/tmp/aprobe');out.mkdir(mode=0o700,exist_ok=False)
def run(label,args):
 p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
 (out/(label+'.txt')).write_text(p.stdout)
 return p
# Read selected session values only, never export arbitrary environment.
ps=[]
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:
  if p.stat().st_uid==os.getuid() and (p/'comm').read_text().strip()=='budgie-panel':ps.append(p)
 except OSError:pass
assert len(ps)==1
raw=(ps[0]/'environ').read_bytes().decode().split('\0'); env=dict(x.split('=',1) for x in raw if '=' in x)
keys=['XDG_CURRENT_DESKTOP','XDG_SESSION_TYPE','QT_QPA_PLATFORM','QT_QPA_PLATFORMTHEME','DISPLAY','WAYLAND_DISPLAY','XDG_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS']
(out/'environment.json').write_text(json.dumps({k:env.get(k) for k in keys},indent=2))
for k in keys:
 if env.get(k):os.environ[k]=env[k]
run('os',['cat','/etc/os-release'])
run('sessions',['sh','-c','grep -H -E "^(Name|Exec|DesktopNames)=" /usr/share/wayland-sessions/*.desktop /usr/share/xsessions/*.desktop'])
run('processes',['ps','-u',str(os.getuid()),'-o','pid,comm,args'])
run('portals',['gdbus','introspect','--session','-d','org.freedesktop.portal.Desktop','-o','/org/freedesktop/portal/desktop'])
run('portal-configuration',['sh','-c','cat /usr/share/xdg-desktop-portal/*portals.conf /usr/share/xdg-desktop-portal/portals/*.portal'])
if env.get('XDG_SESSION_TYPE')=='wayland':
 run('globals',['wayland-info'])
 run('outputs',['wlr-randr','--json'])
 schema='org.buddiesofbudgie.settings-daemon.plugins.media-keys'
 original=subprocess.check_output(['gsettings','get',schema,'custom-keybindings'],text=True).strip()
 (out/'bindings-original.txt').write_text(original)
 import ast
 paths=ast.literal_eval(original.removeprefix('@as '))
 for digit in '123':
  path='/org/buddiesofbudgie/settings-daemon/plugins/media-keys/custom-keybindings/customputgda'+digit+'/'
  target=schema+'.custom-keybinding:'+path
  for k,v in [('name','put.gd worker A probe '+digit),('command','touch /tmp/putgd-a-digit'+digit),('binding','<Control><Shift>'+digit)]:
   subprocess.run(['gsettings','set',target,k,v],check=True)
  paths.append(path)
 subprocess.run(['gsettings','set',schema,'custom-keybindings',repr(paths)],check=True)
 time.sleep(12)
 cfg=Path.home()/'.config/budgie-desktop/labwc/rc.xml'
 (out/'rc-bound.xml').write_bytes(cfg.read_bytes())
 (out/'ready-for-real-input').touch()
 print(str(out),flush=True)
