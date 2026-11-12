from pathlib import Path
import sys,json,shlex,base64,subprocess,hashlib,shutil
B=Path(__file__).parent;G=B/'2026-11-12-scroll-accept2-1398';sys.path.insert(0,str(B.parent.parent/'acceptance/review'));import control
code="""from pathlib import Path
import json,base64
r=Path('/home/patrick/work/sc2/evidence');d={}
for k in 'obnk':
 for f in (r/k).iterdir():
  if f.name in ['completion.json','retirement-summary.md','cleanup-manifest.json','cleanup-dry-run.json','cleanup-result.json','workstation-verified.json']:
   d[k+'/'+f.name]=base64.b64encode(f.read_bytes()).decode()
print(json.dumps(d))
"""
r=control.ssh('d69','python3 -c '+shlex.quote(code),capture_output=True,text=True,check=True)
for n,v in json.loads(r.stdout).items():
 p=G/'cleanup/cap-proof'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(base64.b64decode(v))
 if n.endswith('cleanup-result.json'):assert json.loads(p.read_text())['status']=='completed'
p=Path('/home/patrick/work/put.gd/tools/qemu-grid/remote-displays.json');original=json.loads((B/'wall-before.json').read_text());current=json.loads(p.read_text());owned={'Scroll accept2 cap payload n':6003,'Scroll accept2 cap payload k':6004};removed=[e for e in current if e['name'] in owned and e['port']==owned[e['name']]];new=[e for e in current if e not in removed];assert new==original
q=p.with_name(p.name+'.accept2-tmp');q.write_text(json.dumps(new,indent=2)+'\n');q.replace(p)
for k in 'nk':subprocess.run(['systemctl','--user','stop','putgd-vm-cap2-'+k+'.service'],check=True)
(G/'cleanup/wall-restoration.json').write_text(json.dumps({'originalEntries':original,'restoredEntries':json.loads(p.read_text()),'exactMatch':json.loads(p.read_text())==original,'lastRemoved':removed,'retiredAllElevenRuns':True},indent=2))
for n in ['retry-cap-k.py','finish-cap-k.py','archive-cap-host.py','delete-cap-owned.py','finalize-cap-proof.py']:
 shutil.copyfile(B/n,G/'drivers'/n)
for n in ['cap-k-ready-failed.png']:
 p=B/n
 if p.exists():q=G/'guests/cap-proof/k/failed-setup'/n;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q)
print('retirement receipts exported; original five wall entries restored')
