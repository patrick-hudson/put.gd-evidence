#!/usr/bin/env python3
import json,pathlib,subprocess,sys,time
import record_acceptance as setup
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run); rows=[]; active=None
 def row(name,**v): rows.append({'row':name,**v}); (self.run/'bars.json').write_text(json.dumps(rows,indent=2))
 def cli(method,p=None): return self.cli(b,method,p)
 from rfb import RFB
 vnc=RFB(self.args.vnc_port)
 def click(point): vnc.click(*point)
 def prepare():
  nonlocal active
  active=cli('recording.prepare',{'target':{'kind':'region','rect':[0,0,1500,1000]},'format':'mp4','audio':{'system':False}})['recordingId']
  self.wait_state(b,active,('ready',),60); return active
 def finish(name):
  state=self.wait_state(b,active,('reviewing',),60); self.desktop_frame(self.run/'frames'/(name+'-review.png'))
  path=self.run/'out'/(name+'.mp4'); cli('recording.saveCopy',{'id':active,'path':str(path)}); self.wait_state(b,active,('reviewing',),120)
  motion=self.motion(path); cli('recording.cancel',{'id':active}); return state,motion
 try:
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  prepare()
  self.desktop_frame(self.run/'frames/A5-ready.png'); points={'record':[760,1036]}
  vnc.pointer(*points['record'],True); time.sleep(.05); vnc.pointer(*points['record'],False)
  request=subprocess.Popen([b.cli,'--socket',str(self.socket),'recording.start',json.dumps({'id':active})],env=self.env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  out,err=request.communicate(timeout=30)
  state=self.wait_state(b,active,('recording',),20); self.desktop_frame(self.run/'frames/A5-recording.png'); time.sleep(3)
  cli('recording.stop',{'id':active}); review,motion=finish('A5'); row('A5',passed=state['state']=='recording' and motion>0,reply=json.loads(out),state=state,motion=motion); active=None
 except Exception as e: row('driver-error',passed=False,error=str(e))
 finally:
  if active:
   try: cli('recording.cancel',{'id':active})
   except Exception: pass
  self.stop_resident(b); self.close_cover()
 return 0
r.Driver.main=flow
sys.exit(r.main())
