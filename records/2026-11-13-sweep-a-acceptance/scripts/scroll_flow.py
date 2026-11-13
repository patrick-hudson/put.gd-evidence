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
