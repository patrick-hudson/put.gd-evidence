import sys,json,hashlib
from pathlib import Path
from control import GuestControl,ROOT
run,name=sys.argv[1:];c=GuestControl(run,name);p=c.physical
print(p.ssh(p.run,'cd ~/work/ta1532-src\npython3 tools/lab/lab.py reset --run work/lab-runs/'+run))
code="""import tarfile,hashlib,json
from pathlib import Path
r=Path(RUN);d=r.parents[2]/'completed'/r.name;d.mkdir(parents=True,exist_ok=False)
a=d/'evidence.tgz'
with tarfile.open(a,'w:gz') as t:
 for x in r.iterdir():
  if x.name!='disk.qcow2':t.add(x,arcname=x.name)
s=json.loads((r/'state.json').read_text());completion={'run':str(r),'runId':s['id'],'completed':True,'outcome':'failed'}
(d/'completion.json').write_text(json.dumps(completion))
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**completion,'files':{x:h(d/x) for x in ['completion.json','evidence.tgz']}}
(d/'manifest.json').write_text(json.dumps(m));print(json.dumps({'archive':str(a),'sha256':h(a),'manifest':str(d/'manifest.json')}))
""".replace('RUN',repr(c.run))
v=json.loads(p.ssh(p.run,"python3 - <<'RETIRE'\n"+code+'RETIRE\n',timeout=120));a=ROOT/'work/ta1532'/f'{run}-evidence.tgz';p.get(p.run,v['archive'],str(a));assert hashlib.sha256(a.read_bytes()).hexdigest()==v['sha256'];print('export verified',v['sha256'])
base='cd ~/work/ta1532-src\npython3 tools/lab/lab.py cleanup --run '+c.run+' --images-root /home/patrick/work/put.gd/work/lab-images --evidence-manifest '+v['manifest']
print(p.ssh(p.run,base+' --dry-run',timeout=120));print(p.ssh(p.run,base,timeout=120));p.get(p.run,c.run+'/overlay-cleanup.json',str(c.out/'overlay-cleanup.json'))
p.get(p.run,v['manifest'],str(c.out/'retirement-manifest.json'));print('retired',run)
