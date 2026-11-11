import sys,shlex,json
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
for k in sys.argv[1]:
 r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k
 code="""from pathlib import Path
import os,json
paths=[Path('/tmp/v3/runtime/putgd/session.sock'),Path('/run/user/1000')/os.environ['WAYLAND_DISPLAY'],Path('/run/user/1000/bus'),Path('/run/user/1000/pipewire-0')]
sig=os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
if sig:paths += [Path('/tmp/v3/runtime/hypr')/sig/n for n in ['.socket.sock','.socket2.sock']]
out=[{'path':str(p),'resolved':str(p.resolve()),'utf8Bytes':len(str(p.resolve()).encode())} for p in paths];assert all(v['utf8Bytes']<=107 for v in out);print(json.dumps(out,indent=2))
"""
 (o/'resolved-sockets.json').write_text(lab.guest_session(r,'python3 -c '+shlex.quote(code)));p=r/'qmp.sock';assert len(str(p.resolve()).encode())<=107
 print(k,'socket paths valid')
