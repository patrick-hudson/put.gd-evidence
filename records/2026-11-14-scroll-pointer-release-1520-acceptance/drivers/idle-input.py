import os,time,struct,subprocess
from pathlib import Path
from trial import Rfb
l=Path.home()/'work/s1520'
r=Rfb(5900)
r.sock.sendall(struct.pack('>BxxxBBBBHHHBBBxxx',0,32,24,0,1,255,255,255,16,8,0));r.sock.sendall(struct.pack('>BxHi',2,1,0))
r.pointer(800,500);time.sleep(1);print('after negotiated VNC',subprocess.check_output(['hyprctl','cursorpos'],text=True).strip())
m=subprocess.Popen(['sudo','-n','python3',str(l/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
print(m.stdout.readline().strip());time.sleep(1)
print('before relative',subprocess.check_output(['hyprctl','cursorpos'],text=True).strip())
m.stdin.write('m 100 100\n');m.stdin.flush();time.sleep(1)
print('after relative',subprocess.check_output(['hyprctl','cursorpos'],text=True).strip())
print(subprocess.check_output(['hyprctl','devices','-j'],text=True)[:1000])
m.stdin.write('q\n');m.stdin.flush();m.wait()
