import sys,time,json,shlex,subprocess
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');r=base/'repo/work/lab-runs/og';o=base/'v2evidence/g'
def cmd(c):return lab.guest_session(r,c,timeout=180)
Image.open(lab.screenshot(r,'v2-g-fraction-end')['path']).save(o/'fraction-end.png')
print(cmd('kill '+(o/'browser.pid').read_text()),flush=True)
(o/'restore-command.log').write_text(cmd('hyprctl eval '+shlex.quote('hl.monitor({ output = "Virtual-1", mode = "1280x800@74.99", position = "0x0", scale = 1 })')));time.sleep(2);mon=json.loads(cmd('hyprctl monitors -j'));assert mon[0]['scale']==1;(o/'monitors-restored.json').write_text(json.dumps(mon,indent=2));print(cmd('python3 /home/lab/v2guest.py rpc ui.quit'),flush=True)
for script in ['v2export.py','v2uploads.py']:
 subprocess.run(['python3',str(base/script),'g'],check=True)
subprocess.run(['python3',str(base/'v2analyze.py'),'g'],check=True)
