import sys,re,subprocess
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S))
from tools.lab import lab
n=sys.argv[1]; G=Path.home()/'work/put.gd/work/lab-images/transfer-541c1316ab6b';r=S/'work/lab-runs'/n;r.parent.mkdir(parents=True,exist_ok=True)
k=r.parent/(n+'.known_hosts');k.write_text(re.sub(r'^\[127.0.0.1\]:\d+ ', '[127.0.0.1]:22434 ',(Path.home()/'work/put.gd/work/lab-bootstrap-d69/rec-ws/known_hosts').read_text(),flags=re.M))
subprocess.run([sys.executable,str(S/'tools/diagnostics/check_socket_paths.py'),'--socket',str(r/'qmp.sock')],check=True)
subprocess.run([sys.executable,str(S/'tools/lab/lab.py'),'launch','--profile','kde-wayland','--golden',str(G/'image.qcow2'),'--run',str(r),'--bootstrap-key',str(Path.home()/'work/put.gd/work/lab-bootstrap-d69/rec-ws/identity'),'--known-hosts',str(k),'--ssh-port','22434','--vnc-display','201'],check=True)
