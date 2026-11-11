import sys,json,subprocess
from pathlib import Path
b=Path("/home/patrick/work/svm1398");repo=b/"repo"
for k in sys.argv[1]:
 s=json.loads((repo/"work/lab-runs"/(k+"f")/"state.json").read_text());r=repo/"work/lab-runs"/(k+"3");g=Path(s["golden"])
 cmd=["python3",str(repo/"tools/lab/lab.py"),"launch","--profile",s["profile"],"--golden",str(g),"--run",str(r),"--bootstrap-key",s["bootstrap_key"],"--known-hosts",s["known_hosts"],"--ssh-port",str(s["ssh_port"]),"--vnc-display",str(s["vnc_display"]),"--timeout","300"]
 p=subprocess.run(cmd,cwd=repo,capture_output=True,text=True);(b/("v3launch-"+k+".log")).write_text(p.stdout+p.stderr);print(k,p.returncode,flush=True);p.check_returncode()
