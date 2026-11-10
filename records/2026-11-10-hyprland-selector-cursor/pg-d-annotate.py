import sys,json,time
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/hc3';out=Path(r)/'accept'
lab.put(r,out/'d-before-after-base.png','/home/lab/pg-evidence/d-before-after-base.png')
opened=lab.cli(r,'editor.open',{'source':'file','path':'/home/lab/pg-evidence/d-before-after-base.png'});op=opened['operationId']
for _ in range(80):
 view=lab.cli(r,'editor.inspect',{'id':op})
 if view.get('phase')=='editing':break
 time.sleep(.2)
else:raise RuntimeError(view)
shapes=json.loads((out/'d-annotations.json').read_text())
result=lab.cli(r,'editor.apply',{'id':op,'commands':[{'op':'add','shape':s} for s in shapes]})
(out/'editor-apply.json').write_text(json.dumps(result))
lab.cli(r,'editor.saveCopy',{'id':op,'path':'/home/lab/pg-evidence/d-before-after.png','overwrite':True})
lab.cli(r,'editor.cancel',{'id':op})
lab.get(r,'/home/lab/pg-evidence/d-before-after.png',out/'d-before-after.png')
print('Annotated with the production editor at native head b88e817a1',flush=True)
