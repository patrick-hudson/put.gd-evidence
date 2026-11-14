"""Guest UI control through local uinput, avoiding a forwarded initial VNC warp.
R5 continues to use the separate relative-only trial path.
"""
import subprocess,time
from pathlib import Path
class Pointer:
 def __init__(self,rfb):
  self.sock=rfb.sock;self.width=rfb.width;self.height=rfb.height;self.at=None;self.buttons=0
  self.mouse=subprocess.Popen(['sudo','-n','python3',str(Path.home()/'work/s1520/umouse.py'),'--with-tablet'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
  if not self.mouse.stdout.readline().startswith('ready'):raise RuntimeError('uinput mouse unavailable')
 def send(self,s):self.mouse.stdin.write(s+'\n');self.mouse.stdin.flush()
 def pointer(self,x,y,buttons=0):
  if (int(x),int(y))!=self.at:
   self.send(f'a {int(x)} {int(y)} {self.width} {self.height}')
   for _ in range(20):self.send('m 1 0');time.sleep(.01)
   self.at=(int(x),int(y))
  if (buttons&1)!=(self.buttons&1):self.send('d' if buttons&1 else 'u')
  self.buttons=buttons
 def close(self):self.send('q');self.mouse.wait(5)
