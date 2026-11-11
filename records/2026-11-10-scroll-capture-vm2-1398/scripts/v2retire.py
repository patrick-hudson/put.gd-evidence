import sys,json,hashlib,subprocess
from pathlib import Path
base=Path('/home/patrick/work/svm1398');k=sys.argv[1];r=base/'repo/work/lab-runs'/('og' if k=='g' else k+'f');o=base/'v2evidence'/k;s=json.loads((r/'state.json').read_text())
(o/'completion.json').write_text(json.dumps({'run':str(r),'runId':s['id'],'completed':True,'outcome':'failed'},indent=2))
(o/'retirement-summary.md').write_text('# Completed VM investigation\n\nExact PR 1398 build a4b85216509cbc23af785eb2266451d5447e2079, head 289a611894100f8f0427688bd4fd739f6334a56d. Custom acceptance campaign complete for this guest. Failures remain and block acceptance. PNGs, helper logs, operation IDs, source counters, saved visuals and package identity have been exported from the guest and SHA-256 verified on the builder and workstation before retirement. Immutable golden is preserved. Full results are in RESULTS-vm-2.md.\n')
files=[p for p in (o/'final').rglob('*') if p.is_file()]+[o/n for n in ['state.json','final-hashes.json','export-verified.json','completion.json','retirement-summary.md']]
for name in ['workstation-export-verified.json','upload-verification.json']:
 if (o/name).exists():files.append(o/name)
manifest={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence','run':str(r),'runId':s['id'],'completed':True,'outcome':'failed','files':{str(p.relative_to(o)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
m=o/'cleanup-manifest.json';m.write_text(json.dumps(manifest,indent=2))
cmd=['python3','tools/lab/lab.py']
subprocess.run(cmd+['reset','--run',str(r)],cwd=base/'repo',check=True)
args=cmd+['cleanup','--run',str(r),'--evidence-manifest',str(m),'--images-root','/home/patrick/work/put.gd/work/lab-images']
for suffix,name in [(['--dry-run'],'cleanup-dry-run.json'),([], 'cleanup-result.json')]:
 p=subprocess.run(args+suffix,cwd=base/'repo',capture_output=True,text=True);(o/name).write_text(p.stdout+'\n'+p.stderr);print(k,name,p.returncode,flush=True);p.check_returncode()
(o/'overlay-cleanup.json').write_text((r/'overlay-cleanup.json').read_text())
print(k,'RETIRED',s['pid'],flush=True)
