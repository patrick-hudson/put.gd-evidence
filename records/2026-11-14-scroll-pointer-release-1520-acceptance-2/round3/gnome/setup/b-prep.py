from pathlib import Path
import os,subprocess,shlex,json,xml.etree.ElementTree as ET
l=Path.home()/'work/s5302';l.mkdir(mode=0o700,parents=True,exist_ok=True)
pid=subprocess.check_output(['pgrep','-x','budgie-panel'],text=True).split()[0]
e=dict(x.split('=',1) for x in Path(f'/proc/{pid}/environ').read_bytes().decode().split('\0') if '=' in x);os.environ.update(e)
native=e['XDG_RUNTIME_DIR'];wayland=e.get('WAYLAND_DISPLAY') or subprocess.check_output(['systemctl','--user','show-environment'],text=True).split('WAYLAND_DISPLAY=',1)[1].splitlines()[0]
e['WAYLAND_DISPLAY']=wayland if wayland.startswith('/') else native+'/'+wayland
e['PIPEWIRE_RUNTIME_DIR']=native;(l/'run').mkdir(mode=0o700);e['XDG_RUNTIME_DIR']=str(l/'run')
keys=['DISPLAY','WAYLAND_DISPLAY','XDG_RUNTIME_DIR','PIPEWIRE_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP','XDG_SESSION_ID','QT_QPA_PLATFORM','XAUTHORITY','LABWC_PID']
(l/'session.env').write_text(''.join(k+'='+shlex.quote(e[k])+'\n' for k in keys if k in e))
for p in [l/'run/putgd/session.sock',Path(e['WAYLAND_DISPLAY']),Path(native)/'bus']:
 print('socket',p,len(str(p).encode()));assert len(str(p).encode())<=107
rc=Path.home()/'.config/budgie-desktop/labwc/rc.xml';(l/'rc-before.xml').write_bytes(rc.read_bytes());tree=ET.parse(rc);root=tree.getroot();lib=root.find('libinput')
if lib is None:lib=ET.SubElement(root,'libinput')
devices=lib.findall('device')
if not devices:devices=[ET.SubElement(lib,'device',{'category':'default'})]
for d in devices:
 for k,v in [('accelProfile','flat'),('pointerSpeed','0')]:
  n=d.find(k)
  if n is None:n=ET.SubElement(d,k)
  n.text=v
tree.write(rc,encoding='utf-8',xml_declaration=True);subprocess.run(['labwc','--reconfigure'],check=True);(l/'rc-flat.xml').write_bytes(rc.read_bytes());print('flat configured')
