import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
op=open(O+'current-op').read().strip(); i=inspect(op)
save(op,O+'rA-ui-red.png')
json.dump({'shapes':[{'rect':s['rect'],'suggested':s.get('suggested')} for s in i['shapes']]},open(O+'rA-ui.json','w'))
print(len(i['shapes'])); cancel(op)
