import sys,time,json,shlex,subprocess,concurrent.futures,traceback,os
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');ev=base/'v2evidence'
def run(k):
 r=base/'repo/work/lab-runs'/(k+'f');o=ev/k
 def cmd(c):return lab.guest_session(r,c,timeout=300)
 def shot(n):
  from PIL import Image
  f=lab.screenshot(r,'v2-'+n);Image.open(f['path']).save(o/(n+'.png'))
 def case(n):
  print(k,n,'START',flush=True);(o/(n+'.console')).write_text(cmd('python3 /home/lab/v2guest.py case '+n+' 100,100,960,600'));shot(n+'-end');print(k,n,'END',flush=True)
 try:
  # Native long ruler with controlled halfway initial position.
  for name,start in [('long1',0),('long2',0),('long3',0),('half-on',12000),('half-off',12000)]:
   pid=int(cmd('SC_Y=100 nohup python3 /home/lab/v2ruler.py --rows 600 --start '+str(start)+' > /tmp/v2/'+name+'.log 2>&1 < /dev/null & echo $!').strip());time.sleep(3);shot(name+'-ready')
   case(name);cmd('kill '+str(pid));time.sleep(.5)
  # User invokes the assigned shortcut and drags through the visible selector.
  cmd('python3 /home/lab/v2guest.py patch '+shlex.quote(json.dumps({'actions':{'scroll':{'shortcut':'Ctrl+Shift+F9'}},'preferences':{'scrollCaptureFromTop':True}})))
  pid=int(cmd('SC_Y=100 nohup python3 /home/lab/v2ruler.py --rows 600 > /tmp/v2/user-fixture.log 2>&1 < /dev/null & echo $!').strip());time.sleep(4);shot('user-before')
  lab.key(r,['ctrl','shift','f9']);time.sleep(1);shot('user-selector')
  lab.pointer(r,100,100,1280,800,True);time.sleep(.2)
  for i in range(1,13):lab.pointer(r,100+80*i,100+50*i,1280,800,True);time.sleep(.03)
  lab.pointer(r,1060,700,1280,800,False)
  for i in range(20):shot('user-capturing-%02d'%i);time.sleep(.4)
  (o/'user-history.json').write_text(cmd('python3 /home/lab/v2guest.py rpc history.list '+shlex.quote('{"limit":200}')))
  # Stop the user operation through the production toggle, then wait for completion.
  # The owned long fixture is left open for review of the live bar before stopping.
  (o/'user-fixture.pid').write_text(str(pid))
  return
  cmd('kill '+str(pid))
 except Exception:(o/'extra-error.txt').write_text(traceback.format_exc())
with concurrent.futures.ThreadPoolExecutor(4) as pool:list(pool.map(run,sys.argv[1] if len(sys.argv)>1 else 'obnk'))
