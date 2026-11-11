import sys,time,json,shlex,traceback,tarfile
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');k=sys.argv[1];r=base/'repo/work/lab-runs'/(k+'f');o=base/'v2evidence'/k
label='ubuntu26.04' if k=='k' else 'ubuntu24.04';package=next((base/'v2artifacts'/('release-native-'+label)).glob('*.deb'))
def cmd(c):return lab.guest_session(r,c,timeout=300)
try:
 print(cmd('python3 /home/lab/v2guest.py rpc ui.quit'),flush=True);time.sleep(2)
 lab.put(r,package,'/home/lab/pr-native.deb')
 (o/'native-install.log').write_text(lab.ssh(r,'sudo -n apt-get install -y /home/lab/pr-native.deb 2>&1 || true',timeout=300))
 for f in ['v2nativeguest.py','v2nreceiver.py']:lab.put(r,base/f,'/home/lab/'+f)
 print(cmd('python3 /home/lab/v2nativeguest.py init'),flush=True)
 pid=int(cmd('nohup python3 /home/lab/v2ruler.py > /tmp/v2n/fixture.log 2>&1 < /dev/null & echo $!').strip());time.sleep(4)
 for i in range(1,4):
  print(k,'native'+str(i),'START',flush=True);(o/('native'+str(i)+'.console')).write_text(cmd('python3 /home/lab/v2nativeguest.py case native'+str(i)+' 100,100,960,600'))
  from PIL import Image
  Image.open(lab.screenshot(r,'v2-native'+str(i))['path']).save(o/('native'+str(i)+'.png'))
 print(cmd('kill '+str(pid)),flush=True)
 print(cmd('python3 /home/lab/v2nativeguest.py rpc ui.quit'),flush=True)
 cmd('tar -czf /home/lab/v2-native.tgz -C /tmp/v2n cases archive helper.log resident.log version.json rpc.jsonl capabilities.json socket-preflight.json')
 lab.get(r,'/home/lab/v2-native.tgz',o/'native.tgz',timeout=180);(o/'native').mkdir(exist_ok=True);tarfile.open(o/'native.tgz').extractall(o/'native',filter='data')
 print(k,'NATIVE END',flush=True)
except Exception:(o/'native-harness-error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
