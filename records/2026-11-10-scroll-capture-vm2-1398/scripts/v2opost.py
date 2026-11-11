import time,json,sys,shlex,concurrent.futures
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');r=base/'repo/work/lab-runs/of';o=base/'v2evidence/o'
def cmd(c):return lab.guest_session(r,c,timeout=300)
cmd('python3 /home/lab/v2guest.py patch '+shlex.quote(json.dumps({'preferences':{'scrollCaptureMaxHeight':30000}})))
pid=int(cmd('nohup python3 /home/lab/v2ruler.py > /tmp/v2/post-notify-fixture.log 2>&1 < /dev/null & echo $!').strip());time.sleep(3)
Image.open(lab.screenshot(r,'v2-post-notify-before')['path']).save(o/'post-notify-before.png')
with concurrent.futures.ThreadPoolExecutor(1) as pool:
 f=pool.submit(cmd,'python3 /home/lab/v2guest.py case post-notify 100,100,960,600');time.sleep(1);Image.open(lab.screenshot(r,'v2-post-notify-capturing')['path']).save(o/'post-notify-capturing.png');(o/'post-notify.console').write_text(f.result())
cmd('kill '+str(pid));print('o POST-NOTIFY END',flush=True)
