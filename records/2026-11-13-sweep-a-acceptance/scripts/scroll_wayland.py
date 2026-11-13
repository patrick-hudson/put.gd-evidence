#!/usr/bin/env python3
import json,pathlib,subprocess,sys,time
import record_acceptance as setup
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run); fixture=None; active=None; report={}
 def save(**v): report.update(v); (self.run/'scroll.json').write_text(json.dumps(report,indent=2))
 try:
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  fixture=subprocess.Popen([sys.executable,str(pathlib.Path(__file__).parent/'scroll_fixture.py'),str(self.run)],env=self.env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=open(self.run/'logs/scroll-fixture.log','w'))
  for _ in range(100):
   if (self.run/'scroll-rect.json').is_file(): break
   time.sleep(.1)
  rect=json.loads((self.run/'scroll-rect.json').read_text())['rect']
  if self.env.get('XDG_SESSION_TYPE')=='wayland':
   windows=self.cli(b,'recording.windows')['windows']; w=next(w for w in windows if w.get('title')=='Sweep synthetic scroll page')
   # Locate painted rows in the independent full-desktop VNC frame before any wheel input.
   from rfb import RFB
   vnc=RFB(self.args.vnc_port); vnc.screenshot(str(self.run/'frames/A7-reference.png')); vnc.close()
   from PIL import Image
   image=Image.open(self.run/'frames/A7-reference.png')
   # Unique first line is black (i=0), second line RGB(37,71,13); find its solid left/right edge.
   pixels=image.convert('RGB'); candidates=[]
   for y in range(pixels.height):
    xs=[x for x in range(pixels.width) if pixels.getpixel((x,y))==(37,71,13)]
    if len(xs)>700: candidates.append((y,min(xs),max(xs)))
   assert candidates,'scroll viewport not independently located'
   y,x,x2=candidates[0]; rect=[x+3,y-26+3,x2-x-6,550]
   (self.run/'wayland-rect-proof.json').write_text(json.dumps({'window':w,'rect':rect,'firstSecondLine':candidates[0]}))
  caps=self.cli(b,'scroll.capabilities'); save(capabilities=caps,rect=rect)
  assert caps['available'],caps
  active=self.cli(b,'scroll.prepare',{'rect':rect})['id']
  for _ in range(200):
   state=self.cli(b,'scroll.inspect',{'id':active})
   if state['state']=='ready': break
   time.sleep(.1)
  self.desktop_frame(self.run/'frames/A7-ready.png')
  self.cli(b,'scroll.start',{'id':active})
  for _ in range(800):
   state=self.cli(b,'scroll.inspect',{'id':active})
   if state['state'] in ('done','failed','cancelled'): break
   time.sleep(.25)
  self.desktop_frame(self.run/'frames/A7-finished.png'); save(result=state,passed=state.get('endReason')=='end_of_content',history=self.cli(b,'history.list',{'limit':20})); active=None
 except Exception as e: save(passed=False,error=str(e))
 finally:
  if active:
   try: self.cli(b,'scroll.cancel',{'id':active})
   except Exception: pass
  if fixture: fixture.terminate(); fixture.wait(10)
  self.stop_resident(b); self.close_cover()
 return 0
r.Driver.main=flow
sys.exit(r.main())
