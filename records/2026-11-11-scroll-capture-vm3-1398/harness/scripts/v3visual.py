exec(open('/home/patrick/work/svm1398/v3host.py').read().split('with concurrent.futures.ThreadPoolExecutor(2)')[0].split('def go(k):')[0])
k=keys;r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k
def cmd(c):return lab.guest_session(r,c,timeout=300)
def shot(n):Image.open(lab.screenshot(r,'v3-'+n)['path']).save(o/(n+'.png'))
def spawn(c,n):return int(cmd('nohup '+c+' > /tmp/v3/'+n+'.log 2>&1 < /dev/null & echo $!').strip())
def case(n,rect):
 (o/(n+'.console')).write_text(cmd('python3 /home/lab/v3guest.py case '+n+' '+rect));shot(n+'-end')
if mode=='fraction':
 def scale(v):
  c= ('hyprctl eval '+shlex.quote('hl.monitor({ output = "Virtual-1", mode = "1280x800@74.99", position = "0x0", scale = '+v+' })')) if k=='o' else 'wlr-randr --output Virtual-1 --scale '+v if k=='b' else 'kscreen-doctor output.1.scale.'+v
  (o/('scale-'+v+'.log')).write_text(cmd(c));time.sleep(3)
  (o/('outputs-'+v+'.json')).write_text(cmd('hyprctl monitors -j' if k=='o' else 'wlr-randr --json' if k=='b' else 'kscreen-doctor -j'))
  if k=='o':assert json.loads((o/('outputs-'+v+'.json')).read_text())[0]['scale']==float(v)
 try:
  f=B/'v3fraction.py';f.write_text(Path('/home/patrick/work/sf1398/qt_fixture.py').read_text().replace('960','640').replace('600','400').replace('* 55','* 35').replace(', 55,',', 35,'));lab.put(r,f,'/home/lab/v3fraction.py');scale('1.25')
  pid=spawn('python3 /home/lab/v3fraction.py','fraction');time.sleep(4);shot('fraction-ready');case('fraction','100,100,640,400');cmd('kill '+str(pid))
 finally:scale('1')
elif mode=='user':
 offset=int(cmd('stat -c %s /tmp/v3/helper.log').strip())
 cmd('python3 /home/lab/v3guest.py patch '+shlex.quote(json.dumps({'actions':{'scroll':{'shortcut':'Ctrl+Shift+F9'}},'preferences':{'scrollCaptureFromTop':True}})))
 pid=spawn('env SC_Y=100 python3 /home/lab/v3ruler.py --rows 600','user');time.sleep(4);shot('user-before');lab.key(r,['ctrl','shift','f9']);time.sleep(2);shot('user-selector')
 if k in 'ob':
  for fn in ['wayland_pointer.py','wayland_toplevels.py']:lab.put(r,B/'repo/tools/lab'/fn,'/home/lab/'+fn)
  cmd('python3 /home/lab/wayland_pointer.py drag 100 100 1060 700 --extent 1280 800 --steps 12 --step-ms 80')
 else:
  lab.pointer(r,100,100,1280,800);time.sleep(.4);lab.pointer(r,100,100,1280,800,True);time.sleep(.2)
  for i in range(1,13):lab.pointer(r,100+80*i,100+50*i,1280,800,True);time.sleep(.08)
  lab.pointer(r,1060,700,1280,800,False)
 for i in range(10):shot('user-capture'+str(i));time.sleep(.8)
 (o/'user-active.json').write_text(cmd('python3 /home/lab/v3guest.py rpc history.list '+shlex.quote('{"limit":200}')))
 lab.key(r,['ctrl','shift','f9']);time.sleep(5);shot('user-end');(o/'user-history.json').write_text(cmd('python3 /home/lab/v3guest.py rpc history.list '+shlex.quote('{"limit":200}')));cmd('kill '+str(pid))
if mode=='user':
 record=json.loads((o/'user-history.json').read_text())['records'][0]
 code="""import json,shutil,hashlib
from pathlib import Path
r=json.loads(%r);d=Path('/tmp/v3/cases/user');d.mkdir();f=Path(r['local']['path']);assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];shutil.copyfile(f,d/'capture.png');(d/'helper.log').write_bytes(Path('/tmp/v3/helper.log').read_bytes()[%d:]);(d/'result.json').write_text(json.dumps({'history':r,'capture':{'state':'done','endReason':'see_helper_log'}},indent=2))
"""%(json.dumps(record),offset)
 cmd('python3 -c '+shlex.quote(code))
