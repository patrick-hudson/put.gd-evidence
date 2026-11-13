#!/usr/bin/env python3
import json,pathlib,sys,time,threading,socket,uuid,urllib.request
import record_acceptance as setup
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run); receiver=None; active=None; done=threading.Event(); states=[]; reader=None
 def watch():
  while not done.is_set():
   try:
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
     c.settimeout(3); c.connect(str(self.socket)); ident=str(uuid.uuid4()); request={'schemaVersion':1,'requestId':ident,'session':str(self.socket),'method':'operation.inspect','params':{'id':active}}
     c.sendall(json.dumps(request).encode()+b'\n'); raw=b''
     while b'\n' not in raw: raw+=c.recv(65536)
     v=json.loads(raw)
     if v.get('ok'):
      state=v['result']['state']
      if not states or states[-1].get('state')!=state:
       states.append({'state':state,'at':time.monotonic(),'operation':v['result']}); (self.run/'upload-states.json').write_text(json.dumps(states,indent=2))
   except Exception as e: states.append({'errorType':type(e).__name__})
 try:
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  import offline_destination
  receiver,offline,origin=offline_destination.configure(self,b)
  active=self.cli(b,'recording.prepare',{'target':{'kind':'region','rect':[0,0,1500,1000]},'format':'mp4','audio':{'system':False}})['recordingId']; self.wait_state(b,active,('ready',),60)
  self.cli(b,'recording.start',{'id':active}); time.sleep(5); self.cli(b,'recording.stop',{'id':active})
  readers=[threading.Thread(target=watch) for _ in range(4)]
  for t in readers: t.start()
  reader=readers[0]; time.sleep(.1)
  state=self.cli(b,'recording.inspect',{'id':active}); self.cli(b,'recording.upload',{'id':active,'revision':state['edit']['revision']})
  for _ in range(500):
   op=self.cli(b,'operation.inspect',{'id':active})
   if op['state'] in ('completed','failed','partial','cancelled'): break
   time.sleep(.05)
  time.sleep(.2); done.set()
  for t in readers: t.join(5)
  history=self.cli(b,'history.list',{'limit':20}); self.cli(b,'ui.show',{'view':'history'}); self.desktop_frame(self.run/'frames/A8-history.png')
  url=op['items'][0]['receipt']['directUrl']; path=self.run/'out/uploaded.mp4'; path.write_bytes(urllib.request.urlopen(url).read()); motion=self.motion(path)
  report={'operation':op,'history':history,'states':[v.get('state') for v in states],'motion':motion}; (self.run/'upload.json').write_text(json.dumps(report,indent=2))
 finally:
  done.set()
  if reader: reader.join(5)
  if active:
   try: self.cli(b,'recording.cancel',{'id':active})
   except Exception: pass
  self.stop_resident(b); self.close_cover()
  if receiver: receiver.shutdown(); receiver.server_close()
 return 0
r.Driver.main=flow
sys.exit(r.main())
