#!/usr/bin/env python3
import json,pathlib,subprocess,sys,time,hashlib
import record_acceptance as setup
import offline_destination,native_tray
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run); receiver=None; results=[]; viewer=None
 def save(): (self.run/'tray.json').write_text(json.dumps(results,indent=2))
 def observe(label):
  bus,name=native_tray.service_for(self.resident.pid)
  props=native_tray.call(bus,name,'/StatusNotifierItem','org.freedesktop.DBus.Properties','GetAll','(s)',('org.kde.StatusNotifierItem',))[0]
  icon=pathlib.Path(props['IconName']) if props.get('IconName') else None
  info={'label':label,'at':time.monotonic(),'tooltip':props['ToolTip'],'iconName':props.get('IconName')}
  if icon and icon.is_file():
   data=icon.read_bytes(); (self.run/'frames'/(label+'-icon.png')).write_bytes(data); info['iconSha256']=hashlib.sha256(data).hexdigest()
  if props.get('IconPixmap'):
   from PIL import Image
   w,h,data=props['IconPixmap'][-1]; Image.frombytes('RGBA',(w,h),bytes(data),'raw','ARGB').save(self.run/'frames'/(label+'-pixmap.png'))
  viewer.screenshot(str(self.run/'frames'/(label+'.png'))); results.append(info); save()
 def wait(op):
  for _ in range(500):
   v=self.cli(b,'operation.inspect',{'id':op})
   results.append({'operationId':op,'state':v['state'],'progress':[i.get('uploadProgress') for i in v['items']]})
   if v['state'] in ('completed','partial','failed','cancelled'): save(); return v
   time.sleep(.1)
  raise RuntimeError('upload did not finish')
 try:
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  receiver,offline,origin=offline_destination.configure(self,b)
  import rfb
  viewer=rfb.RFB(5900)
  viewer.frame()
  self.cli(b,'ui.show',{'view':'history'}); time.sleep(1)
  request={'probe':'accessible','query':{'application':'cinnamon*','role':'label','name':'put.gd'}}
  probe=subprocess.run([sys.executable,str(r.HERE/'surface_driver/probe.py'),json.dumps(request)],env=self.env,capture_output=True,text=True,timeout=15)
  observed=json.loads(probe.stdout); results.append({'trayAccessible':observed}); save()
  matches=observed.get('result',[])
  if matches and matches[0].get('rect'):
   x,y,w,h=matches[0]['rect']; subprocess.run(['xdotool','mousemove',str(x+w//2),str(y+h//2)],env=self.env,check=True)
  subprocess.run(['xdotool','mousemove','1688','1060'],env=self.env,check=True); time.sleep(1)
  original=offline.Handler.body
  def slow(handler):
   if not handler.path.startswith('/upload/'): return original(handler)
   remaining=int(handler.headers.get('Content-Length') or 0); data=bytearray()
   while remaining:
    chunk=handler.rfile.read(min(65536,remaining))
    if not chunk: break
    data.extend(chunk); remaining-=len(chunk); time.sleep(.03)
   return bytes(data)
  offline.Handler.body=slow
  payload=self.run/'synthetic.bin'; payload.write_bytes(b'putgd synthetic tray\n'*(1024*768))
  observe('B6-idle-before')
  op=self.cli(b,'upload.files',{'paths':[str(payload)],'profileId':'sweep-http'})['operationId']
  observe('B6-initial'); time.sleep(1); observe('B6-ring-1'); time.sleep(1); observe('B6-ring-2')
  completed=wait(op)
  bus,tray=native_tray.service_for(self.resident.pid)
  titles=[]
  for _ in range(200):
   title=native_tray.call(bus,tray,'/StatusNotifierItem','org.freedesktop.DBus.Properties','Get','(ss)',('org.kde.StatusNotifierItem','ToolTip'))[0][2]; titles.append(title)
   if title=='Upload complete': break
   time.sleep(.005)
  results.append({'completionTitles':titles}); observe('B6-complete'); time.sleep(7); observe('B6-idle-after')
  offline.Handler.body=original
  with offline.lock: offline.state['rules']=[{'call':'upload','status':401,'remaining':1}]
  failed=self.cli(b,'upload.files',{'paths':[str(payload)],'profileId':'sweep-http'})['operationId']; failure=wait(failed)
  time.sleep(.8); observe('B6-attention')
  results.append({'completed':completed,'failed':failure,'visualInspectionPending':True}); save()
 except Exception as e: results.append({'error':str(e)}); save()
 finally:
  if viewer: viewer.close()
  self.stop_resident(b); self.close_cover()
  if receiver: receiver.shutdown(); receiver.server_close()
 return 0
r.Driver.main=flow
sys.exit(r.main())
