import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
def sh(i): return [(s['id'],s.get('suggested')) for s in i['shapes']]
opid,ins=edit_open('desktop'); out={}
r=apply(opid,[{'op':'redactText','categories':['name']}]); i=inspect(opid); first=i['shapes']; out['n']=len(first); print('marks',len(first))
last=first[-1]['id']; mid=first[len(first)//2]['id']
for sid in (last,mid,first[0]['id']):
    apply(opid,[{'op':'remove','shapeId':sid}])
n_after=len(inspect(opid)['shapes'])
r2=apply(opid,[{'op':'redactText','categories':['name']}]); i=inspect(opid)
out['deleted3_rerun_added']=r2['result']['counts']['name']; out['after_rerun']=len(i['shapes']); print('deleted 3, re-run added',r2['result']['counts']['name'],'marks',len(i['shapes']),'(expected',n_after,')')
apply(opid,[{'op':'undo'}]); out['undo_marks']=len(inspect(opid)['shapes']); print('undo ->',out['undo_marks'])
apply(opid,[{'op':'add','shape':{'kind':'redact','rect':[20,60,80,24]}}]); i=inspect(opid); print('with hand mark',len(i['shapes']))
v=cli('editor.view',{'id':opid,'action':'removeSuggestions'}); i=inspect(opid); out['removeSuggestions_ok']=v.get('ok'); out['after_remove']=sh(i); print('removeSuggestions',v.get('ok'),sh(i))
a=apply(opid,[{'op':'undo'}]); out['undo_after_remove']=len(inspect(opid)['shapes']); print('undo once ->',out['undo_after_remove'])
apply(opid,[{'op':'redo'}]); v=cli('editor.view',{'id':opid,'action':'removeSuggestions'}); out['again']=(v.get('error') or {}).get('code'); print('again',out['again'])
json.dump(out,open(O+'rF4.json','w'),indent=1); cancel(opid)
