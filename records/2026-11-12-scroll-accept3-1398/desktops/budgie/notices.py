from pathlib import Path
import pass2 as p,subprocess,os,json,time,traceback,sys,rfb,threading
P=p.P;e=json.loads((P/'env.json').read_text());host=sys.argv[1]
def patch(v):
 s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':v,'expectedRevision':s['metadata']['observedRevision']})
def fixture(script,fn,rows=60):
 f=subprocess.Popen(['python3',str(P/script),'--rows',str(rows)],env=e,stdout=open(P/'notices-fixture.log','a'),stderr=subprocess.STDOUT)
 try:time.sleep(3);fn()
 finally:f.terminate();f.wait(15)
def shot(n):
 v=rfb.RFB(5988);v.frame();v.screenshot(P/n);v.sock.close()
# The original receiver is ours, recorded when upload_setup ran.
pid=int((P/'receiver.pid').read_text());assert (P/'receiver.py').as_posix().encode() in (Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
os.kill(pid,15);time.sleep(.5)
f=subprocess.Popen(['python3',str(P/'controlled_receiver.py')],stdout=open(P/'controlled-receiver.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'receiver.pid').write_text(str(f.pid));time.sleep(.5)
try:
 (P/'hold-upload').touch()
 fixture('qt_fixture.py',lambda:(p.capture('busy-first',60,2000),p.capture('busy-second',60,30000,immediate=True)))
 (P/'hold-upload').unlink();time.sleep(2)
 original=p.rpc
 def fullrpc(m,args={}):
  if m=='scroll.prepare':args=dict(args,rect=[0,0,1900,1080])
  return original(m,args)
 patch({'preferences':{'notifications':True}})
 events=[]
 monitor=subprocess.Popen(['dbus-monitor','--session','--profile',"type='method_call',interface='org.freedesktop.Notifications',member='Notify'"],env=e,stdout=subprocess.PIPE,stderr=open(P/'notify-monitor.stderr','w'),text=True)
 (P/'notify-monitor.pid').write_text(str(monitor.pid))
 def watch():
  for line in monitor.stdout:
   if 'Notify' in line:
    event={'time':time.time(),'line':line.strip()};events.append(event)
    with (P/'notify-method-events.jsonl').open('a') as out:out.write(json.dumps(event)+'\n')
 threading.Thread(target=watch,daemon=True).start();time.sleep(.5)
 def notices():
  for delay in [0,100,300]:
   # A synthetic upload completion causes a put.gd notice; the receiver's held
   # response is released immediately before the requested prepare delay.
   (P/'hold-upload').touch();before=list((P/'received').glob('*.bin'))
   accepted=original('upload.files',{'paths':[str(P/'cap/capture.png')],'profileId':'scroll-local'})
   for _ in range(300):
    if len(list((P/'received').glob('*.bin')))>len(before):break
    time.sleep(.01)
   prior=len(events);release=time.time();(P/'hold-upload').unlink()
   for _ in range(500):
    if len(events)>prior:break
    time.sleep(.01)
   observed=events[prior] if len(events)>prior else None;time.sleep(delay/1000)
   begin=time.time();p.rpc=fullrpc
   try:p.capture('notice-'+str(delay),60,30000,immediate=True)
   finally:p.rpc=original
   (P/('notice-'+str(delay))/'timing.json').write_text(json.dumps({'observedNotify':observed,'receiverRelease':release,'prepareCalled':begin,'requestedDelayMs':delay,'acceptedUpload':accepted},indent=2))
 fixture('full_fixture.py',notices)
 if host=='m74':
  (P/'fail-upload').touch();fixture('qt_fixture.py',lambda:p.capture('history-failure',600,2000),600);time.sleep(4);original('ui.show',{'view':'history'});time.sleep(1);shot('history-failure.png');(P/'history-failure.json').write_text(json.dumps(original('history.list',{'limit':200}),indent=2));(P/'fail-upload').unlink()
 (P/'notices.done').write_text('done')
except Exception:(P/'notices.error').write_text(traceback.format_exc());raise
finally:
 for n in ['hold-upload','fail-upload']:
  if (P/n).exists():(P/n).unlink()
