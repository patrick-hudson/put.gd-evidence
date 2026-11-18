import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
op=open(os.path.expanduser('~/work/qr1618/state/out/current-op')).read().strip()
i=inspect(op)
print(json.dumps({'shapes':[{k:s.get(k) for k in('id','kind','rect','suggested')} for s in i['shapes']],'selected':i['view'].get('selectedShapeId'),'canUndo':i['canUndo'],'canRedo':i['canRedo'],'sel':i['view'].get('selection')}))
