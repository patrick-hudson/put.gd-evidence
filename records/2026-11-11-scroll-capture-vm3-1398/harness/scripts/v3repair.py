import sys,shlex,subprocess,time,json
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k
code="""from pathlib import Path
import subprocess,re
p=Path('/tmp/v3/cases/long1');p.rename(p.with_name('harness-no-fixture-long1')) if p.exists() else None
v=subprocess.check_output(['gdbus','call','--session','--dest','org.freedesktop.Notifications','--object-path','/org/freedesktop/Notifications','--method','org.freedesktop.Notifications.Notify','putgd-test','0','','Harness cleanup','','[]','{}','1000'],text=True);i=int(re.search(r'uint32 (\d+)',v)[1])
for n in range(max(1,i-25),i+1):subprocess.run(['gdbus','call','--session','--dest','org.freedesktop.Notifications','--object-path','/org/freedesktop/Notifications','--method','org.freedesktop.Notifications.CloseNotification',str(n)],capture_output=True)
"""
lab.guest_session(r,'python3 -c '+shlex.quote(code))
p=subprocess.run(['python3',str(B/'v3host.py'),'extras',k],capture_output=True,text=True);(o/'extras-corrected.log').write_text(p.stdout+p.stderr);print(k,p.stdout,p.stderr,flush=True)
