import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
log=[]
def sh(i): return [{'id':s['id'],'rect':s['rect'],'suggested':s.get('suggested')} for s in i['shapes']]
def step(name,r,i=None):
    e={'step':name,'ok':r.get('ok'),'error':(r.get('error') or {}).get('code') or None}
    if r.get('ok') and 'result' in r: e['counts']=r['result'].get('counts'); e['created']=r['result'].get('created')
    if i is not None: e['shapes']=sh(i); e['canUndo']=i['canUndo']
    log.append(e); print(json.dumps(e))
opid,ins=edit_open('desktop'); save(opid,O+'r6-orig.png')
r=apply(opid,[{'op':'redactText','categories':sys.argv[1].split(',')}]); i=inspect(opid); step('quick redact',r,i)
first=i['shapes']; assert first, 'no marks'
last=first[-1]['id']
# move first mark keeps tag
s0=first[0]; r=apply(opid,[{'op':'update','shapeId':s0['id'],'shape':{'rect':[s0['rect'][0]+4,s0['rect'][1],s0['rect'][2],s0['rect'][3]]}}]); i=inspect(opid); step('move mark %d by 4px'%s0['id'],r,i)
moved_tag=[s.get('suggested') for s in i['shapes'] if s['id']==s0['id']]
# delete last
r=apply(opid,[{'op':'remove','shapeId':last}]); i=inspect(opid); step('delete mark %d'%last,r,i); n_after_delete=len(i['shapes'])
r=apply(opid,[{'op':'redactText','categories':sys.argv[1].split(',')}]); i=inspect(opid); step('quick redact again',r,i)
readded=len(i['shapes'])>n_after_delete
r=apply(opid,[{'op':'undo'}]); i=inspect(opid); step('undo',r,i)
back=any(s['id']==last for s in i['shapes'])
# hand mark
r=apply(opid,[{'op':'add','shape':{'kind':'redact','rect':[20,60,80,24]}}]); i=inspect(opid); step('add hand mark',r,i)
hand=[s['id'] for s in i['shapes'] if not s.get('suggested')]
# remove suggestions one by one (no session method for Remove suggestions)
for s in [s for s in i['shapes'] if s.get('suggested')]:
    apply(opid,[{'op':'remove','shapeId':s['id']}])
i=inspect(opid); step('remove each suggested mark by id',{'ok':True},i)
res_={'suggested_tag_on_marks':all(s.get('suggested') for s in first),'moved_mark_keeps_tag':moved_tag,'deleted_mark_not_readded':not readded,'undo_brings_it_back':back,'hand_mark_kept':[s['id'] for s in i['shapes']]==hand}
print(json.dumps(res_)); json.dump({'log':log,'result':res_},open(O+'r6-cli.json','w'),indent=1)
cancel(opid)
