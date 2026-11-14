from pathlib import Path
import json,hashlib,sys,shutil
sys.path.insert(0,str(Path.home()/'work/s52/tools/lab'));import lab
r=Path.home()/'work/s52/work/lab-runs/h3';p=Path.home()/'work/s5302/h-retirement';p.mkdir(exist_ok=True)
s=lab.state(str(r));shutil.copyfile(r/'state.json',p/'state.json');root=Path.home()/'work/s5302';shutil.copyfile(root/'h-evidence.tgz',p/'evidence.tgz')
photos=['h-r12-typed.png','h-r12-clean.png']
for n in photos:shutil.copyfile(root/n,p/n)
base={'run':str(r),'runId':s['id'],'completed':True,'outcome':'failed'};(p/'completion.json').write_text(json.dumps(base,indent=2));members=['state.json','evidence.tgz','completion.json']+photos;m={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**base,'files':{x:hashlib.sha256((p/x).read_bytes()).hexdigest() for x in members}};(p/'manifest.json').write_text(json.dumps(m,indent=2));print(p/'manifest.json')
