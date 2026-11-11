import sys,time,json
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398')
for k in sys.argv[1]:
 r=base/'repo/work/lab-runs'/(k+'f');o=base/'v2evidence'/k
 lab.pointer(r,410,736,1280,800,True);time.sleep(.2);lab.pointer(r,410,736,1280,800,False);time.sleep(3)
 (o/'user-final-history.json').write_text(lab.guest_session(r,'python3 /home/lab/v2guest.py rpc history.list '+__import__('shlex').quote('{"limit":200}')))
 if (o/'user-fixture.pid').exists():print(lab.guest_session(r,'kill '+(o/'user-fixture.pid').read_text()),flush=True)
