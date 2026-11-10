import os,sys,json,time,subprocess,shutil
from pathlib import Path
from PIL import Image,ImageChops
B=Path('/tmp/p1363k');E=B/'evidence';env=dict(os.environ,**json.loads((B/'environment.json').read_text()));BIN=B/'pkg/usr/bin';sock=B/'r/putgd/session.sock'
def cli(method,params=None):
 p=subprocess.run([str(BIN/'putgd-cli'),'--socket',str(sock),method,json.dumps(params or {})],env=env,capture_output=True,text=True,timeout=30);d=json.loads(p.stdout);assert d['ok'],d;return d['result']
def save(n,d):(E/(n+'.json')).write_text(json.dumps(d,indent=2));return d
def wait(op):
 for _ in range(180):
  d=cli('operation.inspect',{'id':op})
  if d['state'] in ['completed','failed','cancelled','partial']:return d
  time.sleep(.2)
 raise RuntimeError('timeout '+op)
def invoke(a,delay=0):return cli('action.invoke',dict(action=a,**({'delaySeconds':delay} if delay else {})))['operationId']
def result(n,d):
 assert d['state']=='completed',d;path=d['items'][0]['local']['path'];shutil.copyfile(path,E/(n+'.png'));return Image.open(path).convert('RGB')
sys.path.insert(0,str(Path.home()/'work/i1363/tools/lab'));from rfb import RFB
v=RFB(5900);mode=sys.argv[1]
if mode=='monitor':
 v.pointer(900,450);d=save('monitor',wait(invoke('monitor')));im=result('monitor',d);assert im.size==(1920,1080);print(d['id'],im.size)
elif mode=='hover':
 # Coordinates supplied from the saved full-screen General page.
 x,y,hx,hy=map(int,sys.argv[2:6]);op=invoke('monitor',3);time.sleep(.5);v.click(x,y);v.pointer(hx,hy);time.sleep(.35);v.screenshot(E/'hover-countdown.png');d=save('hover-delay',wait(op));im=result('hover-delay',d);assert im.size==(1920,1080);v.key('esc');print(d['id'],d['state'])
elif mode=='region':
 op=invoke('region');time.sleep(.8);v.screenshot(E/'region-selector.png');v.drag(260,240,560,440);d=save('region',wait(op));im=result('region',d);assert im.size==(300,200);v.pointer(1000,700);r=save('repeat',wait(invoke('repeat')));rep=result('repeat',r);assert ImageChops.difference(im,rep).getbbox() is None;print(d['id'],r['id'],'same pixels')
elif mode=='shot':v.screenshot(E/(sys.argv[2]+'.png'))
elif mode=='click':v.click(int(sys.argv[2]),int(sys.argv[3]));time.sleep(1);v.screenshot(E/(sys.argv[4]+'.png'))
elif mode=='key':v.key(*sys.argv[2].split('+'));time.sleep(1);v.screenshot(E/(sys.argv[3]+'.png'))
elif mode=='cli':print(json.dumps(cli(sys.argv[2],json.loads(sys.argv[3]) if len(sys.argv)>3 else {}),indent=2))
elif mode=='identity':
 pid=int((B/'pid').read_text());qt=sorted(set(line.split()[-1] for line in Path('/proc/'+str(pid)+'/maps').read_text().splitlines() if 'libQt6Core.so' in line));save('identity',{'diagnostics':cli('diagnostics'),'loadedQtCore':qt});print(qt)
elif mode=='quit':print(cli('ui.quit'))
v.close()
