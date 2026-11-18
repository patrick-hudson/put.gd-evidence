import sys,json,threading;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
cands=[r'(?:.*){6}Q$', r'.*.*.*.*.*.*.*.*Q$', r'(\w|\d)+\d+\d+\d+Q', r'\b\w*\w*\w*\w*\w*\w*Z\b', r'[a-z]*[a-z]*[a-z]*[a-z]*[a-z]*[a-z]*[a-z]*[a-z]*!']
out=[]
for p in cands:
    g=res('settings.get'); rev=g['metadata']['observedRevision']
    r=cli('settings.patch',{'patch':{'preferences':{'quickRedactPatterns':[p,r'#\d{4}']}},'expectedRevision':rev})
    if not r.get('ok'): print(repr(p),'REFUSED',r['error']['message']); out.append({'p':p,'saved':False,'msg':r['error']['message']}); continue
    opid,ins=edit_open('desktop')
    box={}
    def run():
        t=time.time(); box['r']=apply(opid,[{'op':'redactText','categories':['list']}]); box['t']=time.time()-t
    th=threading.Thread(target=run); th.start(); lat=[];n=0
    while th.is_alive():
        t=time.time(); cli('editor.inspect',{'id':opid}); lat.append(time.time()-t); n+=1; time.sleep(0.1)
    th.join(); rr=box['r']; i=inspect(opid)
    e={'p':p,'saved':True,'apply_s':round(box['t'],2),'polls':n,'max_inspect_s':round(max(lat),3) if lat else None,'counts':(rr.get('result') or {}).get('counts'),'skipped':(rr.get('result') or {}).get('skippedPatterns'),'marks':len(i['shapes'])}
    print(json.dumps(e)); out.append(e); cancel(opid); time.sleep(2)
json.dump(out,open(O+'r4-slow.json','w'),indent=1)
