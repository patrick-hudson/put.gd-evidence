#!/usr/bin/python3
import sys,os,shlex,json
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/(os.environ['VM_RUN']+'3');args=sys.argv[1:]
if '--params-stdin' in args:args.remove('--params-stdin');args.append(sys.stdin.read())
s=lab.guest_session(r,'/home/lab/putgd-lab/bin/putgd-cli --socket /tmp/v3/runtime/putgd/session.sock '+shlex.join(args)+' || true',timeout=180);print(s,end='');sys.exit(0 if json.loads(s)['ok'] else 1)
