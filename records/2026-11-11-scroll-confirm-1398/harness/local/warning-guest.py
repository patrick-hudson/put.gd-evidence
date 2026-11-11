from pathlib import Path
import sys,time,shlex,json
from PIL import Image
B=Path('/home/patrick/work/svm1398');D=Path('/home/patrick/work/scn');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+'cn');o=D/'ev'/(k+'cn')/'warning-probe';o.mkdir()
def cmd(c):return lab.guest_session(r,c,timeout=180)
pid=int(cmd('nohup env SC_Y=100 python3 /home/lab/v3ruler.py > /tmp/v3/warning-fixture.log 2>&1 < /dev/null & echo $!').strip());time.sleep(3)
try:
 for name in ['cap-warning-probe','postcap-warning-probe']:(o/(name+'.console')).write_text(cmd('python3 /home/lab/v3guest.py case '+name+' 100,100,960,600'))
finally:cmd('kill '+str(pid))
time.sleep(.3);Image.open(lab.screenshot(r,'confirm-warning-after-close')['path']).save(o/'warning-visible.png')
for name in ['cap-warning-probe','postcap-warning-probe']:
 dest=o/name;dest.mkdir()
 for f in ['result.json','capture.png','helper.log']:lab.get(r,'/tmp/v3/cases/'+name+'/'+f,dest/f)
# Keep supplementary cases apart from the counted matrix and retain their original files.
cmd('mkdir /tmp/v3/supplemental; mv /tmp/v3/cases/cap-warning-probe /tmp/v3/supplemental/cap-warning-probe; mv /tmp/v3/cases/postcap-warning-probe /tmp/v3/supplemental/postcap-warning-probe')
