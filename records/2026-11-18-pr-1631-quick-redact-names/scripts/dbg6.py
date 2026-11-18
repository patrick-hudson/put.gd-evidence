import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
opid,ins=edit_open('desktop')
res('editor.recognize',{'id':opid})
for _ in range(60):
    t=inspect(opid)['text']
    if t['state']=='completed': break
    time.sleep(1)
words=t['words']
r=apply(opid,[{'op':'redactText','categories':['name']}]); i=inspect(opid)
sh=[(s['id'],s['rect']) for s in i['shapes']]; print('marks',sh)
for k in (len(sh),1,len(sh)//2):
    sid=sh[k-1][0]
    r=apply(opid,[{'op':'remove','shapeId':sid}])
    r2=apply(opid,[{'op':'redactText','categories':['name']}])
    i=inspect(opid)
    print('removed',sid,sh[k-1][1],'-> rerun counts',r2['result']['counts'],'created',r2['result']['created'],[ (s['id'],s['rect']) for s in i['shapes'] if s['id'] not in [x[0] for x in sh]])
    # which words overlap the removed rect
    rr=sh[k-1][1]
    print('  words under it:',[w['text'] for w in words if overlap(w['rect'],rr)>0.5*w['rect'][2]*w['rect'][3]])
    apply(opid,[{'op':'undo'}]) if r2['result']['created'] else None
    break
cancel(opid)
