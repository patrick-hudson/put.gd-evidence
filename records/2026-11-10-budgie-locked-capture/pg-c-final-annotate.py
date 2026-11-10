import sys,json,time
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/bc5';out=Path(r)/'accept'
lab.put(r,out/'c-before-after-base.png','/home/lab/pg-evidence/c-before-after-base.png')
opened=lab.cli(r,'editor.open',{'source':'file','path':'/home/lab/pg-evidence/c-before-after-base.png'});op=opened['operationId']
for _ in range(80):
 view=lab.cli(r,'editor.inspect',{'id':op})
 if view.get('phase')=='editing':break
 time.sleep(.2)
else:raise RuntimeError(view)
shapes=json.loads((out/'c-annotations.json').read_text())
result=lab.cli(r,'editor.apply',{'id':op,'commands':[{'op':'add','shape':s} for s in shapes]})
(out/'editor-apply.json').write_text(json.dumps(result))
lab.cli(r,'editor.saveCopy',{'id':op,'path':'/home/lab/pg-evidence/c-before-after.png','overwrite':True})
lab.cli(r,'editor.cancel',{'id':op})
lab.get(r,'/home/lab/pg-evidence/c-before-after.png',out/'c-before-after.png')
print('Annotated with the production editor at native head 4b7e01d2b',flush=True)
