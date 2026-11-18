import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
opid,ins=edit_open('desktop')
r=apply(opid,[{'op':'redactText','categories':['name']}]); i=inspect(opid)
ids=[(s['id'],s['rect']) for s in i['shapes']]; print('marks',len(ids))
readded=0
for sid,rc in ids[::2]:   # delete every other mark, one at a time, re-running Quick redact after each
    apply(opid,[{'op':'remove','shapeId':sid}])
    r2=apply(opid,[{'op':'redactText','categories':['name']}])
    c=r2['result']['counts']['name']; readded+=c
    print('removed',sid,rc,'-> rerun added',c)
i=inspect(opid); print('marks now',len(i['shapes']),'expected',len(ids)-len(ids[::2]),'readded total',readded)
# undo restores last delete?
apply(opid,[{'op':'undo'}]); print('after one undo marks',len(inspect(opid)['shapes']))
cancel(opid)
