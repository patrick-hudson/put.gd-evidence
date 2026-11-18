import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
g=res('settings.get'); rev=g['metadata']['observedRevision']
print('restore patterns',cli('settings.patch',{'patch':{'preferences':{'quickRedactPatterns':[r'#\d{4}',r'(?i)\bquick redact\b']}},'expectedRevision':rev}).get('ok'))
opid,ins=edit_open('desktop')
def sh(i): return [(s['id'],s.get('suggested')) for s in i['shapes']]
log=[]
r=apply(opid,[{'op':'redactText','categories':['name','list']}]); i=inspect(opid); log.append(('redactText name+list',r.get('ok'),(r.get('result') or {}).get('counts'),sh(i)))
r=apply(opid,[{'op':'add','shape':{'kind':'redact','rect':[20,60,80,24]}}]); i=inspect(opid); log.append(('add hand mark',r.get('ok'),None,sh(i)))
v=cli('editor.view',{'id':opid,'action':'removeSuggestions'}); i=inspect(opid)
log.append(('editor.view removeSuggestions',v.get('ok'),json.dumps(v.get('result') or v.get('error'))[:200],sh(i)))
# one undo step?
r=apply(opid,[{'op':'undo'}]); i=inspect(opid); log.append(('undo once',r.get('ok'),None,sh(i)))
r=apply(opid,[{'op':'redo'}]); i=inspect(opid); log.append(('redo once',r.get('ok'),None,sh(i)))
v=cli('editor.view',{'id':opid,'action':'removeSuggestions'}); i=inspect(opid)
log.append(('removeSuggestions again (none left)',v.get('ok'),json.dumps(v.get('error') or v.get('result'))[:200],sh(i)))
for l in log: print(l)
json.dump(log,open(O+'r5-agent-removesuggestions.json','w'),indent=1)
cancel(opid)
