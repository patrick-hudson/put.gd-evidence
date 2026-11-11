import sys,json,subprocess
from pathlib import Path
b=Path("/home/patrick/work/svm1398");repo=b/"repo";out=Path("/home/patrick/work/scn")
k,suffix=sys.argv[1],sys.argv[2]
s=json.loads((repo/"work/lab-runs"/(k+"f")/"state.json").read_text());r=repo/"work/lab-runs"/(k+suffix);g=Path(s["golden"])
assert not r.exists(); assert len(str(r/"qmp.sock").encode())<=107
cmd=["python3",str(repo/"tools/lab/lab.py"),"launch","--profile",s["profile"],"--golden",str(g),"--run",str(r),"--bootstrap-key",s["bootstrap_key"],"--known-hosts",s["known_hosts"],"--ssh-port",str(s["ssh_port"]),"--vnc-display",str(s["vnc_display"]),"--timeout","300"]
p=subprocess.run(cmd,cwd=repo,capture_output=True,text=True);(out/("launch-"+k+suffix+".log")).write_text(p.stdout+p.stderr);print(k,p.returncode,p.stdout[-600:],p.stderr[-600:],flush=True)
