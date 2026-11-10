import sys,json,time
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
r='/home/patrick/work/pg-cd/work/lab-runs/bc7';out=Path(r)/'accept'
for name,annotations in [('c-before-after','c-annotations'),('stress-report','stress-report-annotations')]:
 guest='/home/lab/pg-evidence/'+name
 lab.put(r,out/(name+'-base.png'),guest+'-base.png')
 op=lab.cli(r,'editor.open',{'source':'file','path':guest+'-base.png'})['operationId']
 for _ in range(100):
  view=lab.cli(r,'editor.inspect',{'id':op})
  if view.get('phase')=='editing':break
  time.sleep(.2)
 else:raise RuntimeError(view)
 shapes=json.loads((out/(annotations+'.json')).read_text())
 (out/(name+'-editor-apply.json')).write_text(json.dumps(lab.cli(r,'editor.apply',{'id':op,'commands':[{'op':'add','shape':s} for s in shapes]}),indent=2))
 lab.cli(r,'editor.saveCopy',{'id':op,'path':guest+'.png','overwrite':True});lab.cli(r,'editor.cancel',{'id':op});lab.get(r,guest+'.png',out/(name+'.png'))
 print(name,'annotated by exact CI package',flush=True)
