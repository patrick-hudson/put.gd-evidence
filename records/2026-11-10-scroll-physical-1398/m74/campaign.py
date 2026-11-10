import json,subprocess,os,time,sys,threading
from pathlib import Path
import rfb
p=Path('/tmp/sp1398');env=json.loads((p/'env.json').read_text());host=os.uname().nodename;port=5901 if host=='fedora' else 5900
kind=sys.argv[1]
def rpc(m,x={}):
 o=json.loads(subprocess.check_output(['putgd-cli','--socket',str(p/'runtime/putgd/session.sock'),m,json.dumps(x)],env=env,text=True));assert o['ok'],o;return o['result']
# Only the fixture PID explicitly started by this campaign may be stopped.
old=p/'qt.pid'
if old.exists():
 pid=int(old.read_text())
 try:
  if str(p/'qt_fixture.py').encode() in Path('/proc/%d/cmdline'%pid).read_bytes():os.kill(pid,15)
 except FileNotFoundError:pass
 time.sleep(.4)
s=rpc('settings.get');rpc('settings.patch',{'patch':{'preferences':{'scrollCaptureFromTop':not kind.endswith('off')}},'expectedRevision':s['metadata']['observedRevision']})
extra=[]
if 'sticky' in kind:extra+=['--sticky']
if 'half' in kind:extra+=['--start','1200']
if 'long' in kind:extra+=['--rows','600']
f=open(p/(kind+'-fixture.log'),'w');fixture=subprocess.Popen(['python3',str(p/('gtk_fixture.py' if kind.startswith('gtk') else 'qt_fixture.py'))]+extra,env=env,stdout=f,stderr=f,start_new_session=True);old.write_text(str(fixture.pid));time.sleep(2)
cmd=['python3',str(p/'scroll_run.py'),'--socket',str(p/'runtime/putgd/session.sock'),'--out',str(p/kind),'--package',str(next(p.glob('*.deb'),next(p.glob('*.rpm'),None))),'--rect','100,100,960,600','--rows','60','--format','fixture','--png-root',str(p/'archive'),'--png-root',str(p/'data')]
if 'sticky' in kind:cmd+=['--header','40','--footer','40']
if kind.endswith('off'):cmd+=['--first-pixel','1200']
if 'cap' in kind:cmd+=['--max-height','2000','--height','2000','--expect-end','height_cap']
if 'stop' in kind:cmd+=['--control','stop','--after','1.5','--expect-end','stopped']
if 'cancel' in kind:cmd+=['--control','cancel','--after','.5']
stop=threading.Event()
def frames():
 try:
  v=rfb.RFB(port);i=0
  while not stop.is_set() and i<30:
   v.screenshot(p/(kind+'-screen-%02d.png'%i));i+=1;stop.wait(.5)
 except Exception as e:(p/(kind+'-visual-error.txt')).write_text(str(e))
t=threading.Thread(target=frames);t.start()
try:subprocess.run(cmd,env=env,stdout=open(p/(kind+'-run.log'),'w'),stderr=subprocess.STDOUT)
finally:stop.set();t.join(timeout=12);fixture.terminate();fixture.wait(timeout=5)
(p/(kind+'-staging.json')).write_text(json.dumps([str(x) for x in (p/'data/putgd/scroll').rglob('*')]))
