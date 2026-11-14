from pathlib import Path
from trial import Rfb
from localinput import Pointer
import time,subprocess,os,signal,json
l=Path.home()/'work/s5302';a=l/'a';m=Pointer(Rfb(5901));m.pointer(450,300,1);m.pointer(450,300);m.close();subprocess.run(['sudo','-n','python3',str(l/'keyboard.py')],check=True);time.sleep(.3);w=(a/'r12-received.txt').read_text().strip();assert w=='abc';subprocess.run(['python3',str(l/'rfbshot.py'),str(a/'r12-typed.png'),'--vnc','5901'],check=True)
pid=int((a/'r12-terminal.pid').read_text());p=Path('/proc')/str(pid);assert b'xterm' in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM);time.sleep(.3)
v={'witness':w,'testDevices':[p.read_text().strip() for p in Path('/sys/class/input').glob('event*/device/name') if 'putgd-lab' in p.read_text() or 'scroll-1520' in p.read_text()]};assert not v['testDevices']
for k,f in [('enabled-extensions','enabled-before.txt'),('disabled-extensions','disabled-before.txt')]:v[k]=subprocess.check_output(['gsettings','get','org.gnome.shell',k],text=True).strip();assert v[k]==(l/f).read_text().strip()
v['accel']=subprocess.check_output(['gsettings','get','org.gnome.desktop.peripherals.mouse','accel-profile'],text=True).strip();assert v['accel']==(l/'accel-before.txt').read_text().strip();v['rpm']=subprocess.run(['rpm','-q','putgd'],capture_output=True,text=True).stdout;assert 'not installed' in v['rpm'];(a/'cleanup.json').write_text(json.dumps(v,indent=2));subprocess.run(['python3',str(l/'rfbshot.py'),str(a/'r12-clean.png'),'--vnc','5901'],check=True);print(json.dumps(v))
