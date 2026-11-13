#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess,sys,time,urllib.request
import record_acceptance as setup
import offline_destination
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run); receiver=None; rows=[]
 def row(name,**data): rows.append({'row':name,**data}); (self.run/'offline.json').write_text(json.dumps(rows,indent=2))
 def inspect(op): return self.cli(b,'operation.inspect',{'id':op})
 def wait(op):
  for _ in range(400):
   v=inspect(op)
   if v['state'] in ('completed','failed','partial','cancelled'): return v
   time.sleep(.1)
  raise RuntimeError('operation timeout')
 def upload(path): return self.cli(b,'upload.files',{'paths':[str(path)],'profileId':'sweep-http'})['operationId']
 try:
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  receiver,offline,origin=offline_destination.configure(self,b)
  original_body=offline.Handler.body
  def body(handler):
   if handler.path.startswith('/upload/'):
    time.sleep(3 if int(handler.headers.get('Content-Length') or 0)<1000000 else 12)
   return original_body(handler)
  offline.Handler.body=body
  self.cli(b,'ui.show',{'view':'history'}); time.sleep(2)
  small=self.run/'small.txt'; small.write_bytes(b'putgd synthetic offline acceptance\n')
  large=self.run/'large.bin'; large.write_bytes(b'putgd synthetic large\n'*(1024*512))
  second=self.run/'second-large.bin'; second.write_bytes(large.read_bytes())
  ids=[upload(p) for p in (small,large,second)]
  for _ in range(80):
   view=self.cli(b,'ui.history',{'action':'inspect'})
   if view['activeOperationCount']>=3: break
   time.sleep(.1)
  before=self.cli(b,'ui.history',{'action':'cancelAll'}); self.desktop_frame(self.run/'frames/B7-open.png')
  assert before['cancelAllConfirmation']['open'],before
  done=wait(ids[0]); assert done['state']=='completed',done
  running=[op for op in ids if inspect(op)['state'] not in ('completed','failed','partial','cancelled')]
  after=self.cli(b,'ui.history',{'action':'confirmCancelAll'}); time.sleep(1)
  self.desktop_frame(self.run/'frames/B7-confirmed.png')
  final=[wait(op) for op in ids]
  item=final[0]['items'][0]; link=item['receipt']['directUrl']
  got=urllib.request.urlopen(link,timeout=10).read(); assert hashlib.sha256(got).hexdigest()==hashlib.sha256(small.read_bytes()).hexdigest()
  row('B7',status='protocol passed, inspect status-line frame',runningAtConfirmation=len(running),confirmation=before,outcomes=final,finishedLinkReadback=True)
  try: self.cli(b,'operation.cancel',{'id':ids[0]}); refused=False
  except r.RunError as e: refused='operation_inactive' in str(e); error=str(e)
  kept=inspect(ids[0]); row('B5-inactive',passed=refused and kept['state']=='completed' and kept['items'][0]['receipt']['directUrl']==link,error=error if refused else None,operation=kept)
  history=self.cli(b,'history.list',{'limit':30})
  selected=[v for v in history['records'] if v['operationId']==ids[0]]; assert len(selected)==1
  selection=[selected[0]['id']]; preview=self.cli(b,'delete.prepare',{'ids':selection})
  assert [v['historyId'] for v in preview['targets']]==selection
  assert preview['targets'][0]['receipt']['directUrl']==link
  row('B4-preview',preview=preview)
  accepted=self.cli(b,'delete.confirm',{'ids':selection,'acknowledgement':preview['acknowledgement']})
  for _ in range(200):
   deletion=self.cli(b,'delete.inspect',{'id':accepted['deleteOperationId']})
   if deletion['state'] not in ('accepted','running'): break
   time.sleep(.1)
  row('B4',passed=all(v['status']=='removed' for v in deletion['items']),deletion=deletion)
  # Receiver refuses a single upload; an explicit retry then uses its normal response.
  offline.Handler.body=original_body
  with offline.lock: offline.state['rules']=[{'call':'upload','status':401,'remaining':1}]
  failed=upload(small); first=wait(failed); assert first['state'] in ('failed','partial') and first['items'][0]['uploadStatus']=='failed',first
  self.cli(b,'operation.retry',{'id':failed}); retried=wait(failed)
  row('B5-retry',passed=retried['state']=='completed',first=first,retried=retried)
 except Exception as e: row('driver-error',passed=False,error=str(e))
 finally:
  self.stop_resident(b); self.close_cover()
  if receiver: receiver.shutdown(); receiver.server_close()
 return 0
r.Driver.main=flow
sys.exit(r.main())
