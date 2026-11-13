#!/usr/bin/env python3
import json,os,pathlib,signal,subprocess,sys,time,threading
import record_acceptance as setup
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run); rows=[]; active=None; receiver=None
 def save(name,**data):
  rows.append({'row':name,**data}); (self.run/'extra.json').write_text(json.dumps(rows,indent=2))
 def prepare(selecting=False):
  nonlocal active
  target={'kind':'region'}
  if not selecting: target['rect']=[0,0,1500,1000]
  v=self.cli(b,'recording.prepare',{'target':target,'format':'mp4','audio':{'system':False}}); active=v['recordingId']
  if selecting:
   for _ in range(200):
    v=self.cli(b,'recording.inspect',{'id':active})
    if v.get('selecting'): return active
    time.sleep(.05)
   raise RuntimeError('selector not observed')
  self.wait_state(b,active,('ready',),60); return active
 def record_to(state):
  rid=prepare()
  if state=='ready': return rid
  self.cli(b,'recording.start',{'id':rid}); time.sleep(3)
  if state=='recording': return rid
  self.cli(b,'recording.pause',{'id':rid})
  if state=='paused': return rid
  self.cli(b,'recording.resume',{'id':rid}); time.sleep(2)
  self.cli(b,'recording.stop',{'id':rid})
  return rid
 def clean():
  nonlocal active
  if active:
   try: self.cli(b,'recording.cancel',{'id':active})
   except Exception: pass
   active=None
 try:
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  import offline_destination
  receiver,offline,origin=offline_destination.configure(self,b)
  for state in ('selecting','ready','recording','paused','reviewing','exporting','stopping'):
   for attempt in (1,2):
    try:
     rid=prepare(True) if state=='selecting' else record_to('reviewing' if state=='exporting' else 'recording' if state=='stopping' else state)
     stopped=[]; worker=None
     if state=='exporting':
      self.cli(b,'recording.saveCopy',{'id':rid,'path':str(self.run/'out/cancel-export.mp4')})
      before=self.cli(b,'recording.inspect',{'id':rid}); assert before['state']=='exporting',before['state']
     elif state=='stopping':
      def stop():
       try: stopped.append(self.cli(b,'recording.stop',{'id':rid}))
       except Exception as e: stopped.append(str(e))
      worker=threading.Thread(target=stop); worker.start()
      observed=False
      for _ in range(100):
       before=setup.original_cli(self,b,'recording.inspect',{'id':rid})
       if before.get('pending')=='stop' or before.get('state')=='stopping': observed=True; break
       if before.get('state')=='reviewing': break
       time.sleep(.005)
      if not observed:
       worker.join(40); save('A3-'+state,status='not run',reason='stop drain finished before pending stop could be observed',attempt=attempt); clean(); break
     self.cli(b,'recording.cancel',{'id':rid})
     if worker: worker.join(40)
     op=self.cli(b,'operation.inspect',{'id':rid}); assert op['state']=='cancelled',op['state']
     time.sleep(.5); self.desktop_frame(self.run/'frames'/('A3-'+state+'-'+str(attempt)+'.png'))
     save('A3-'+state,status='protocol passed, visual inspection pending',operation=op,attempt=attempt); active=None; break
    except Exception as e:
     save('A3-'+state,status='failed',error=str(e),attempt=attempt); clean()
  # Deliberately stop only this resident's recorder for the late-reply case.
  rid=record_to('recording')
  def children(pid):
   path=pathlib.Path('/proc')/str(pid)/'task'/str(pid)/'children'
   try: direct=[int(v) for v in path.read_text().split()]
   except FileNotFoundError: return []
   return direct+[c for child in direct for c in children(child)]
  candidates=[p for p in children(self.resident.pid) if (pathlib.Path('/proc')/str(p)/'comm').read_text().strip()=='putgd-record']
  assert len(candidates)==1,candidates
  helper=candidates[0]
  pause=subprocess.Popen([b.cli,'--socket',str(self.socket),'recording.pause',json.dumps({'id':rid})],env=self.env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  stopped_at=time.monotonic(); os.kill(helper,signal.SIGSTOP)
  try: time.sleep(20)
  finally: os.kill(helper,signal.SIGCONT)
  stdout,stderr=pause.communicate(timeout=30); answer=json.loads(stdout)
  caught=self.wait_state(b,rid,('paused',),20)
  self.desktop_frame(self.run/'frames/A6-paused.png')
  self.cli(b,'recording.stop',{'id':rid})
  copy=self.run/'out/timeout.mp4'; self.cli(b,'recording.saveCopy',{'id':rid,'path':str(copy)})
  self.wait_state(b,rid,('reviewing',),120)
  score=self.motion(copy)
  save('A6',status='passed' if answer.get('error',{}).get('code')=='recording_helper_timeout' and score>0 else 'failed',helperPid=helper,stoppedSeconds=time.monotonic()-stopped_at,reply=answer,caughtUp=caught,motion=score)
  clean()
  # An explicit Upload is the only handoff to the operation pipeline.
  rid=record_to('reviewing'); state=self.cli(b,'recording.inspect',{'id':rid})
  self.cli(b,'recording.upload',{'id':rid,'revision':state['edit']['revision']})
  observations=[]
  for _ in range(400):
   op=self.cli(b,'operation.inspect',{'id':rid}); observations.append(op['state'])
   if op['state'] in ('completed','failed','cancelled'): break
   time.sleep(.02)
  self.desktop_frame(self.run/'frames/A8-completed.png')
  save('A8',status='completed' if op['state']=='completed' else 'failed',states=observations,operation=op,history=self.cli(b,'history.list',{'limit':20})); active=None
 except Exception as e: save('driver-error',status='failed',error=str(e))
 finally:
  clean(); self.stop_resident(b); self.close_cover()
  if receiver: receiver.shutdown(); receiver.server_close()
 return 0
r.Driver.main=flow
sys.exit(r.main())
