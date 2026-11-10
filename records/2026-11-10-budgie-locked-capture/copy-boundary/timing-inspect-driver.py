import json,socket,time,uuid,os
from pathlib import Path
path='/run/user/'+str(os.getuid())+'/putgd/session.sock'
assert len(path.encode())<=107
index=0
def call(method,params=None):
 global index
 index+=1
 with socket.socket(socket.AF_UNIX) as s:
  s.settimeout(15);s.connect(path)
  request={'schemaVersion':1,'requestId':str(uuid.uuid4()),'session':path,'method':method,'params':params or {}}
  s.sendall(json.dumps(request).encode()+b'\n');b=b''
  while b'\n' not in b:b+=s.recv(65536)
 r=json.loads(b.split(b'\n')[0]);assert r['requestId']==request['requestId'] and r['ok'],r
 return r['result']
def capture():
 start=time.monotonic_ns();oid=call('action.invoke',{'action':'desktop'})['operationId']
 for _ in range(3000):
  op=call('operation.inspect',{'id':oid})
  if op['state'] in ('completed','failed','cancelled'):break
  time.sleep(.005)
 return {'milliseconds':(time.monotonic_ns()-start)/1e6,'operation':op}
rows=[]
for i in range(21):
 row=capture();assert row['operation']['state']=='completed',row
 if i:rows.append(row)
print(json.dumps({'method':'Production session protocol; single-operation inspect (bounded response independent of history size); monotonic invoke-to-terminal time, 5ms polling, 1 warm-up discarded, 20 consecutive captures','rows':rows},indent=2))
