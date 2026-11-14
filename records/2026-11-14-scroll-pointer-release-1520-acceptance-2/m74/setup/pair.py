import json,sys,time,subprocess
from pathlib import Path
from trial import cli,flat,cursorpos
l=Path.home()/'work/s5202';a=l/'a';c=str(l/'bin/cli-a')
def call(m,p={}):
 v=cli(c,m,p);assert v['ok'],v
 with open(a/'s3-calls.jsonl','a') as f:f.write(json.dumps({'t':time.monotonic(),'method':m,'reply':v})+'\n')
 return v['result']
def start():
 s=call('scroll.prepare',{'rect':[470,200,980,720],'maxHeight':60000})['id'];call('scroll.start',{'id':s});return s
def wait(s):
 for _ in range(600):
  v=call('scroll.inspect',{'id':s})
  if v['state'] in ['done','failed','cancelled']:return v
  time.sleep(.3)
 raise RuntimeError('capture timeout')
def page():subprocess.run(['firefox','--profile',str(l/'ff'),'file://'+str(l/'page.html')],check=True);time.sleep(5)
def save(n,v):(a/(n+'.json')).write_text(json.dumps(v,indent=2));print(n,json.dumps(v),flush=True)
if sys.argv[1]=='pause':
 page();save('pointer-plain',wait(start()));page();s=start();(a/'pointer-session-id').write_text(s);time.sleep(3);subprocess.run(['python3',str(l/'rfbshot.py'),str(a/'pointer-running.png'),'--vnc','5900'],check=True)
 m=subprocess.Popen(['sudo','-n','python3',str(l/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True);assert m.stdout.readline().startswith('ready');flat();at=cursorpos();m.stdin.write(f'm {960-at[0]} {540-at[1]}\n');m.stdin.flush();time.sleep(.3);m.stdin.write('q\n');m.stdin.flush();m.wait(5)
 v=call('scroll.inspect',{'id':s});save('pointer-paused',v);assert v.get('paused')==True and v.get('pausedBy')=='pointer',v
 subprocess.run(['python3',str(l/'rfbshot.py'),str(a/'pointer-paused.png'),'--vnc','5900'],check=True);offset=(a/'helper.log').stat().st_size;time.sleep(2);lines=(a/'helper.log').read_bytes()[offset:].decode().splitlines();save('pointer-quiet',{'injectionLines':[x for x in lines if 'scroll inject:' in x]})
elif sys.argv[1]=='finish':save('pointer-resumed',wait((a/'pointer-session-id').read_text()))
