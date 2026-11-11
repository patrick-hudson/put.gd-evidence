# retire.py <key> <suffix> <evidence dir name> <outcome>: stop a guest and remove its overlay through lab.py (after v3retire.py)
import sys,json,hashlib,subprocess
from pathlib import Path
B=Path("/home/patrick/work/svm1398");k,suffix,evname,outcome=sys.argv[1:5];r=B/"repo/work/lab-runs"/(k+suffix);o=Path("/home/patrick/work/scn/ev")/evname;s=json.loads((r/"state.json").read_text())
(o/"completion.json").write_text(json.dumps({"run":str(r),"runId":s["id"],"completed":True,"outcome":outcome},indent=2))
(o/"retirement-summary.md").write_text("# Final scroll capture acceptance, guest "+k+suffix+"\n\nPR 1398 head eaa1ba198fa537d3cac58879b676ad34e268b96a, CI merge 47f90af4ed8bda4630c5865fe82023460f4b4697. Measurements and what was kept are in /home/patrick/work/rolling-capture-research/acceptance/RESULTS-confirm.md on the workstation; raw files stay in this directory on d69. Golden inputs preserved.\n")
assert (o/"workstation-verified.json").is_file()
skip=["cleanup-manifest.json","cleanup-dry-run.json","cleanup-result.json","overlay-cleanup.json"]
files=[p for p in o.rglob("*") if p.is_file() and p.name not in skip]
m=o/"cleanup-manifest.json";m.write_text(json.dumps({"schemaVersion":1,"kind":"vm-overlay-cleanup-evidence","run":str(r),"runId":s["id"],"completed":True,"outcome":outcome,"files":{str(p.relative_to(o)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2))
cmd=["python3","tools/lab/lab.py"];subprocess.run(cmd+["reset","--run",str(r)],cwd=B/"repo",check=True)
args=cmd+["cleanup","--run",str(r),"--evidence-manifest",str(m),"--images-root","/home/patrick/work/put.gd/work/lab-images"]
for extra,n in [(["--dry-run"],"cleanup-dry-run.json"),([],"cleanup-result.json")]:
    p=subprocess.run(args+extra,cwd=B/"repo",capture_output=True,text=True);(o/n).write_text(p.stdout+"\n"+p.stderr);print(k,n,p.returncode,p.stderr[-300:],flush=True);p.check_returncode()
print(k+suffix,"RETIRED",s["pid"],flush=True)
