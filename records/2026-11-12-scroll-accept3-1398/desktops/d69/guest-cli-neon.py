from pathlib import Path
import sys,shlex,subprocess
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
r=Path('/home/patrick/work/put.gd/work/lab-runs/s3n')
# Byte-for-byte stdin transport to the production CLI, including --params-stdin.
payload=sys.stdin.buffer.read();args=lab.ssh_args(r)+[shlex.join(['/home/lab/putgd-lab/bin/putgd-cli',*sys.argv[1:]])]
sys.exit(subprocess.run(args,input=payload).returncode)
