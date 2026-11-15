"""Relative-only functional control after prepare; absolute anchor is setup before prepare.
For paused Wayland helpers, read their last motion/observation and any one correction.
The pointer benchmark is separate and measures every post-hand injection.
"""
import time,re,subprocess
import rfb
class Control:
 def __init__(self,A,mouse):self.A=A;self.P=A.P;self.mouse=mouse;self.known=None;self.offset=0;self.rect=[0,0,1920,1080]
 def anchor_before_prepare(self,x=960,y=540):
  v=rfb.RFB(5900);v.pointer(x,y);v.close();time.sleep(.15);self.known=[x,y];self.offset=(self.P/'helper.log').stat().st_size if (self.P/'helper.log').exists() else 0
 def origin(self):
  if self.A.os.environ.get('SFA_NATIVE_POINTER')=='1':
   import trial_relative
   return trial_relative.native_pointer()
  if self.A.E.get('XDG_SESSION_TYPE')=='x11':
   v=dict(x.split('=',1) for x in subprocess.check_output(['xdotool','getmouselocation','--shell'],env=self.A.E,text=True).splitlines());return [int(v['X']),int(v['Y'])]
  at=list(self.known) if self.known else None
  with (self.P/'helper.log').open('rb') as f:f.seek(self.offset);text=f.read().decode('utf-8','replace')
  for line in text.splitlines():
   m=re.search(r'scroll inject: t=\d+ pointer (-?\d+),(-?\d+) sent',line)
   if m:at=[self.rect[0]+int(m[1]),self.rect[1]+int(m[2])];continue
   m=re.search(r'scroll: pointer at (-?[\d.]+),(-?[\d.]+) (?:on the watch|on the rest surface)',line)
   if m:at=[float(m[1]),float(m[2])];continue
   m=re.search(r'pointer put back at .*\(desktop (-?[\d.]+),(-?[\d.]+)\) sent',line)
   if m:at=[float(m[1]),float(m[2])];continue
   m=re.search(r'pointer put back by (-?[\d.]+),(-?[\d.]+) sent',line)
   if m and at:at=[at[0]+float(m[1]),at[1]+float(m[2])]
  if at is None:raise RuntimeError('no observed pointer origin for relative control')
  return at
 def move(self,x,y):
  time.sleep(.4) # functional clicks wait for the one permitted correction; benchmark does not
  sx,sy=self.origin();steps=max(1,int(((x-sx)**2+(y-sy)**2)**.5/6))
  for i in range(1,steps+1):
   dx=round((x-sx)*i/steps)-round((x-sx)*(i-1)/steps);dy=round((y-sy)*i/steps)-round((y-sy)*(i-1)/steps);self.mouse.stdin.write(f'm {dx} {dy}\n');self.mouse.stdin.flush();time.sleep(.01)
  time.sleep(.1);self.known=[x,y];self.offset=(self.P/'helper.log').stat().st_size
 def click(self):
  self.mouse.stdin.write('d\n');self.mouse.stdin.flush();time.sleep(.06);self.mouse.stdin.write('u\n');self.mouse.stdin.flush();time.sleep(.4)
