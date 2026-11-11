import sys,json,hashlib,subprocess
from pathlib import Path
B=Path('/home/patrick/work/svm1398');k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k;s=json.loads((r/'state.json').read_text())
assert (o/'workstation-verified.json').is_file()
(o/'completion.json').write_text(json.dumps({'run':str(r),'runId':s['id'],'completed':True,'outcome':'failed'},indent=2))
(o/'retirement-summary.md').write_text('# Completed third VM acceptance pass\n\nPR 1398 head acf681fb0e52494a302e3641c04dd233f7585053; CI merge ebb5bd87b7da95fa78ff640733e5737c5d699f52. PNGs, helper logs, frame cadence, exact source and package identities, run metadata, and saved visuals were exported and checksum verified on d69 and the workstation. Failed acceptance remains failed; golden inputs preserved. See RESULTS-vm-3.md for detailed counts and limitations.\n')
files=[p for p in o.rglob('*') if p.is_file() and p.name not in ['cleanup-manifest.json','cleanup-dry-run.json','cleanup-result.json','overlay-cleanup.json']]
m=o/'cleanup-manifest.json';m.write_text(json.dumps({'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence','run':str(r),'runId':s['id'],'completed':True,'outcome':'failed','files':{str(p.relative_to(o)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2))
cmd=['python3','tools/lab/lab.py'];subprocess.run(cmd+['reset','--run',str(r)],cwd=B/'repo',check=True)
args=cmd+['cleanup','--run',str(r),'--evidence-manifest',str(m),'--images-root','/home/patrick/work/put.gd/work/lab-images']
for suffix,n in [(['--dry-run'],'cleanup-dry-run.json'),([], 'cleanup-result.json')]:
 p=subprocess.run(args+suffix,cwd=B/'repo',capture_output=True,text=True);(o/n).write_text(p.stdout+'\n'+p.stderr);print(k,n,p.returncode,flush=True);p.check_returncode()
(o/'overlay-cleanup.json').write_text((r/'overlay-cleanup.json').read_text());print(k,'RETIRED',s['pid'],flush=True)
