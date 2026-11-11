import sys,shlex
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
code="""import subprocess,re
v=subprocess.check_output(['gdbus','call','--session','--dest','org.freedesktop.Notifications','--object-path','/org/freedesktop/Notifications','--method','org.freedesktop.Notifications.Notify','putgd-test','0','','Harness cleanup','','[]','{}','1000'],text=True);i=int(re.search(r'uint32 ([0-9]+)',v)[1])
for n in range(max(1,i-30),i+1):subprocess.run(['gdbus','call','--session','--dest','org.freedesktop.Notifications','--object-path','/org/freedesktop/Notifications','--method','org.freedesktop.Notifications.CloseNotification',str(n)],capture_output=True)
"""
for k in sys.argv[1]:lab.guest_session(B/'repo/work/lab-runs'/(k+'3'),'python3 -c '+shlex.quote(code))
