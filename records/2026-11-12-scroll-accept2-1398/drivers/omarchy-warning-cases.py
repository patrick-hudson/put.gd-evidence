from pathlib import Path
import sys,json,time,subprocess,shlex
from PIL import Image
B=Path('/home/patrick/work/sa2lab');D=Path('/home/patrick/work/sa2vm');sys.path.insert(0,str(B/'tools/lab'));import lab
r=B/'work/lab-runs/sa2o3';o=D/'ev/sa2o3'
def cmd(s):return lab.guest_session(r,s,timeout=240)
f=D/'o3-receiver.py';f.write_text((D/'fixtures/controlled_receiver.py').read_text().replace('/home/patrick/work/sa2','/tmp/v3').replace('19399','19398'));lab.put(r,f,'/tmp/v3/controlled_receiver.py')
code="""from pathlib import Path
import os,subprocess,time,json
p=Path('/tmp/v3');pid=int((p/'receiver.pid').read_text());assert b'/home/lab/v3receiver.py' in (Path('/proc')/str(pid)/'cmdline').read_bytes().split(bytes([0]));os.kill(pid,15);time.sleep(.5);q=subprocess.Popen(['python3',str(p/'controlled_receiver.py')],stdout=open(p/'controlled-receiver.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(p/'receiver.pid').write_text(str(q.pid));(p/'hold-upload').touch()
"""
cmd('python3 -c '+shlex.quote(code));pid=int(cmd('nohup env SC_Y=100 python3 /home/lab/v3ruler.py --rows 600 > /tmp/v3/cap-fixture.log 2>&1 < /dev/null & echo $!').strip());time.sleep(3)
try:(o/'cap.console').write_text(cmd('python3 /home/lab/v3guest.py case cap 100,100,960,600'))
finally:cmd('kill '+str(pid))
time.sleep(.5);Image.open(lab.screenshot(r,'held-upload-cap-warning')['path']).save(o/'cap-warning-visible.png');cmd('python3 -c '+shlex.quote("from pathlib import Path;Path('/tmp/v3/hold-upload').unlink()"));time.sleep(2);subprocess.run(['python3',str(D/'acc.py'),'o3','a','export'],check=True);(o/'warning.done').write_text('done');print('o3 WARNING PHOTO SAVED')
