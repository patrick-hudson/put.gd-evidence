import sys,time,shlex,tarfile,json,traceback
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');r=base/'repo/work/lab-runs/of';o=base/'v2evidence/o'
def cmd(c):return lab.guest_session(r,c,timeout=300)
try:
 print(cmd('python3 /home/lab/v2guest.py rpc ui.quit'),flush=True);time.sleep(2)
 (o/'native-install.log').write_text(lab.ssh(r,'sudo -n pacman -U --noconfirm /home/lab/pr.pkg.tar.zst 2>&1 || true',timeout=300))
 for f in ['v2nativeguest.py','v2nreceiver.py']:lab.put(r,base/f,'/home/lab/'+f)
 print(cmd('python3 /home/lab/v2nativeguest.py init'),flush=True)
 pid=int(cmd('nohup python3 /home/lab/v2ruler.py > /tmp/v2n/fixture.log 2>&1 < /dev/null & echo $!').strip());time.sleep(4)
 from PIL import Image
 for i in range(1,4):
  print('o native'+str(i)+' START',flush=True);(o/('native'+str(i)+'.console')).write_text(cmd('python3 /home/lab/v2nativeguest.py case native'+str(i)+' 100,100,960,600'));Image.open(lab.screenshot(r,'v2-native'+str(i))['path']).save(o/('native'+str(i)+'.png'))
 print(cmd('kill '+str(pid)),flush=True);print(cmd('python3 /home/lab/v2nativeguest.py rpc ui.quit'),flush=True)
 cmd('tar -czf /home/lab/v2-native.tgz -C /tmp/v2n cases archive helper.log resident.log version.json rpc.jsonl capabilities.json socket-preflight.json')
 lab.get(r,'/home/lab/v2-native.tgz',o/'native.tgz');(o/'native').mkdir(exist_ok=True);tarfile.open(o/'native.tgz').extractall(o/'native',filter='data');print('o NATIVE END',flush=True)
except Exception:(o/'native-harness-error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
