from pathlib import Path
import json,hashlib,sys,shutil
sys.path.insert(0,str(Path.home()/'work/s52/tools/lab'));import lab
r=Path.home()/'work/s52/work/lab-runs/b1';p=Path.home()/'work/s1520/b-retirement';p.mkdir(exist_ok=True)
s=lab.state(str(r));shutil.copyfile(r/'state.json',p/'state.json');root=Path.home()/'work/s1520';shutil.copyfile(root/'b-evidence.tgz',p/'evidence.tgz')
photos=['b-terminal-typed.png','b-r12-key-proof.png','b-r12-clean-final.png']
for n in photos:shutil.copyfile(root/n,p/n)
base={'run':str(r),'runId':s['id'],'completed':True,'outcome':'failed'};(p/'completion.json').write_text(json.dumps(base,indent=2));members=['state.json','evidence.tgz','completion.json']+photos;m={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**base,'files':{x:hashlib.sha256((p/x).read_bytes()).hexdigest() for x in members}};(p/'manifest.json').write_text(json.dumps(m,indent=2));print(p/'manifest.json')
