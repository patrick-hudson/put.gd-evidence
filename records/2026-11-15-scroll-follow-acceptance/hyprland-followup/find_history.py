import time
def find_operation(A,sid,timeout=20):
 deadline=time.monotonic()+timeout
 while time.monotonic()<deadline:
  offset=0
  while True:
   page=A.rpc('history.list',{'limit':200,'offset':offset});records=page['records']
   for r in records:
    if r.get('operationId')==sid:return r
   offset+=len(records)
   if not records or offset>=page['total']:break
  time.sleep(.1)
 raise RuntimeError('No History admission for exact operation '+sid+' within '+str(timeout)+' seconds')
