import sys,json,time,re
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/pg-cd/tools/lab');import lab
name,stem,annotations,buildInfo=sys.argv[1:]
assert all(re.fullmatch(r'[A-Za-z0-9-]+',s) for s in (name,stem,annotations))
r=Path('/home/patrick/work/pg-cd/work/lab-runs')/name;o=r/'accept';lab.verify_owned_guest(r)
version=json.loads(lab.guest_session(r,'putgd-cli --version-json'));assert version==json.loads(Path(buildInfo).read_text())
(o/(stem+'-editor-version.json')).write_text(json.dumps(version,indent=2))
guest='/home/lab/pg-evidence/'+stem
lab.put(r,o/(stem+'-base.png'),guest+'-base.png')
op=lab.cli(r,'editor.open',{'source':'file','path':guest+'-base.png'})['operationId']
for _ in range(100):
 view=lab.cli(r,'editor.inspect',{'id':op})
 if view.get('phase')=='editing':break
 time.sleep(.2)
else:raise RuntimeError(view)
shapes=json.loads((o/(annotations+'.json')).read_text())
(o/(stem+'-editor-apply.json')).write_text(json.dumps(lab.cli(r,'editor.apply',{'id':op,'commands':[{'op':'add','shape':s} for s in shapes]}),indent=2))
(o/(stem+'-editor-save.json')).write_text(json.dumps(lab.cli(r,'editor.saveCopy',{'id':op,'path':guest+'.png','overwrite':True}),indent=2))
lab.cli(r,'editor.cancel',{'id':op});lab.get(r,guest+'.png',o/(stem+'.png'))
print('Annotated using exact package '+version['version'],flush=True)
