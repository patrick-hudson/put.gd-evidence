from pathlib import Path
import sys,json
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
P=Path('/home/patrick/work/s3a');tag=sys.argv[1];run=sys.argv[2];r=Path('/home/patrick/work/put.gd/work/lab-runs')/run
if tag=='kubuntu':
 lab.put(r,P/'guest-ui-proof.py','/home/lab/work/s3a/guest-ui-proof.py')
 print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 guest-ui-proof.py',timeout=60),flush=True)
lab.put(r,P/'guest-finish-export.py','/home/lab/work/s3a/guest-finish-export.py')
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 guest-finish-export.py '+tag,timeout=600),flush=True)
e=P/(tag+'-export');e.mkdir(exist_ok=False);lab.get(r,'/home/lab/work/s3-'+tag+'-evidence.tar.gz',e/'guest-evidence.tar.gz',timeout=600);lab.get(r,'/home/lab/work/s3a/export-receipt.json',e/'export-receipt.json')
for n in ['state.json','package.json','qmp-features.json']:
 f=r/n
 if f.exists():(e/n).write_bytes(f.read_bytes())
print('EXPORTED',tag,flush=True)
