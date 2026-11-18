import sys,json,threading;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
op=open(O+'current-op').read().strip(); cancel(op); time.sleep(2)
opid,ins=edit_open('desktop'); save(opid,O+'r7-runaway-orig.png')
box={}
def run():
    t=time.time(); box['r']=apply(opid,[{'op':'redactText','categories':['list']}]); box['t']=time.time()-t
th=threading.Thread(target=run); th.start()
lat=[];n=0
while th.is_alive():
    t=time.time(); x=cli('editor.inspect',{'id':opid}); lat.append(time.time()-t); n+=1; time.sleep(0.1)
th.join()
r=box['r']
print('apply seconds',round(box['t'],2),'inspect polls',n,'max inspect latency',round(max(lat),3) if lat else None, 'ok',r.get('ok'))
print(json.dumps(r.get('result',{}).get('counts')), json.dumps(r.get('error')))
i=inspect(opid)
print([ (s['rect'],s.get('suggested')) for s in i['shapes']])
v=i['view']
print({k:v[k] for k in v if 'uick' in k or k in('message','selection')})
save(opid,O+'r7-runaway-red.png')
json.dump({'apply_seconds':round(box['t'],2),'polls':n,'max_inspect_latency':round(max(lat),3) if lat else None,'counts':r.get('result',{}).get('counts'),'error':r.get('error'),'shapes':[{'rect':s['rect'],'suggested':s.get('suggested')} for s in i['shapes']],'view':{k:v[k] for k in v if 'uick' in k}},open(O+'r7-runaway.json','w'),indent=1)
open(O+'current-op','w').write(opid)
