from pathlib import Path
import os,json,subprocess,time,threading,hashlib,sys,traceback
import pass2 as p,fix6 as f,record_run,rfb
base=p.P;h=sys.argv[1]
while not (base/'caps.done').exists():time.sleep(2)
try:p.rpc('ui.quit')
except Exception:pass
time.sleep(3);P=base/'fa3';P.mkdir(mode=0o700);e,_=record_run.session_environment()
for n in ['c','d','s','cache','r','archive']:(P/n).mkdir(mode=0o700)
for k,n in [('CONFIG','c'),('DATA','d'),('STATE','s'),('CACHE','cache'),('RUNTIME','r')]:e['XDG_'+k+('_DIR' if k=='RUNTIME' else '_HOME')]=str(P/n)
e.update(PIPEWIRE_RUNTIME_DIR='/run/user/1000',PULSE_SERVER='unix:/run/user/1000/pulse/native',PUTGD_RECORD_DEBUG_LOG=str(P/'helper.log'),SC_Y='200',APPIMAGE_EXTRACT_AND_RUN='1')
paths=[P/'r/putgd/session.sock'];assert all(len(str(x.resolve()).encode())<=107 for x in paths);(P/'socket-preflight.json').write_text(json.dumps({str(x):len(str(x.resolve()).encode()) for x in paths},indent=2));(P/'env.json').write_text(json.dumps(e));os.chmod(P/'env.json',0o600)
image=next(base.glob('*.AppImage'));image.chmod(0o700);(P/'identity.json').write_text(json.dumps({'packageSha256':hashlib.sha256(image.read_bytes()).hexdigest(),'format':'supplementary AppImage for AppImage-only file-manager notice'}))
q=subprocess.Popen([str(image),'--background'],env=e,stdout=open(P/'resident.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'resident.pid').write_text(str(q.pid));p.P=P;f.P=P
for _ in range(300):
 if (P/'r/putgd/session.sock').exists():break
 time.sleep(.1)
s=p.rpc('settings.get');d=s['document'];d['preferences'].update(notifications=True,fileManagerMenu=False);d['archive'].update(keepUploads=True,root=str(P/'archive'));d['actions']['scroll']['destination']='local';p.rpc('settings.save',{'document':d,'expectedRevision':s['metadata']['observedRevision']});time.sleep(2)
for stamp in (P/'d').rglob('appimage.stamp'):
 assert stamp.is_file() and not stamp.is_symlink() and stamp.stat().st_uid==os.getuid() and stamp.parent.name=='file-manager'
 (P/'stamp-reset.json').write_text(json.dumps({'path':str(stamp),'sha256':hashlib.sha256(stamp.read_bytes()).hexdigest(),'purpose':'fresh isolated installation, first enable during capture'},indent=2));stamp.unlink()
fixture=base/'qt_fixture.py';t=fixture.read_text();t=t.replace('w.showFullScreen();',"from PyQt6.QtCore import QTimer\nflag=Path("+repr(str(P/'reveal-notice'))+")\ndef reveal():\n if flag.exists():flag.unlink();w.showNormal();w.resize(1720,980)\ntimer2=QTimer();timer2.timeout.connect(reveal);timer2.start(100)\nw.showFullScreen();");t='from pathlib import Path\n'+t;(P/'fixture.py').write_text(t)
monitor=subprocess.Popen(['dbus-monitor','--session',"type='method_call',interface='org.freedesktop.Notifications',member='Notify'"],env=e,stdout=open(P/'notify.log','w'),stderr=subprocess.STDOUT);(P/'monitor.pid').write_text(str(monitor.pid));events={};original=p.rpc;shotDone=False;enableThread=None
port=5901 if h=='f44' else 5900
def shot(name):
 v=rfb.RFB(port);v.screenshot(P/name);v.sock.close()
def enable():
 time.sleep(2);events['toggleTime']=time.time();events['stateAtToggle']=original('scroll.inspect',{'id':events['id']});s=original('settings.get');events['enableReply']=original('settings.patch',{'patch':{'preferences':{'fileManagerMenu':True}},'expectedRevision':s['metadata']['observedRevision']});time.sleep(.5);shot('during-capture.png')
def rpc(m,a={}):
 global shotDone,enableThread
 r=original(m,a)
 if m=='scroll.prepare':events['id']=r['id']
 if m=='scroll.start':enableThread=threading.Thread(target=enable);enableThread.start()
 if m=='scroll.inspect' and r.get('state') in ['done','failed','cancelled'] and not shotDone:
  shotDone=True;events['terminalObserved']=time.time();(P/'reveal-notice').touch();time.sleep(.2);shot('first-after-capture.png');time.sleep(.6);shot('after-capture.png')
 return r
try:
 p.rpc=rpc;f.with_fixture('file-manager',['python3',str(P/'fixture.py'),'--rows','600','--start','23400'],lambda:p.capture('file-manager-notice',600,40000));
 if enableThread:enableThread.join(20)
 (P/'events.json').write_text(json.dumps(events,indent=2));(base/'file-manager3.done').write_text('done')
except Exception:(base/'file-manager3.error').write_text(traceback.format_exc());raise
finally:
 p.rpc=original
 try:original('ui.quit')
 except Exception:pass
 time.sleep(2);monitor.terminate();monitor.wait(10)
