import json,time,os,subprocess,sys,traceback
from pathlib import Path
from gi.repository import Gio,GLib
P=Path('/home/patrick/work/sq4');sys.path.insert(0,str(P));import pass2 as p,record_run,rfb
p.setup();original=json.loads((P/'env.json').read_text());p.rpc('settings.patch',{'patch':{'preferences':{'notifications':True}},'expectedRevision':p.rpc('settings.get')['metadata']['observedRevision']});p.rpc('ui.quit');time.sleep(2)
sock=P/'bus.sock';assert len(str(sock).encode())<=107
conf=P/'bus.conf';conf.write_text('<busconfig><type>session</type><listen>unix:path='+str(sock)+'</listen><auth>EXTERNAL</auth><policy context="default"><allow user="*"/><allow own="*"/><allow send_destination="*"/><allow receive_sender="*"/></policy></busconfig>')
answer=subprocess.check_output(['dbus-daemon','--config-file='+str(conf),'--fork','--print-address=1','--print-pid=1'],text=True).splitlines();address=answer[0];buspid=int(answer[1]);(P/'bus.pid').write_text(str(buspid));e=dict(original,DBUS_SESSION_BUS_ADDRESS=address,QT_QPA_PLATFORMTHEME='generic');(P/'env.json').write_text(json.dumps(e));q=subprocess.Popen(['putgd','-platform','xcb','--background'],env=e,stdout=open(P/'qt-resident.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'resident.pid').write_text(str(q.pid));time.sleep(4)
def shot(n):
 v=rfb.RFB(5900);v.frame();v.screenshot(P/n);v.sock.close()
f=None
try:
 f=subprocess.Popen(['python3',str(P/'balloon_fixture.py')],env=e,stdout=open(P/'fixture.log','w'),stderr=subprocess.STDOUT);time.sleep(2)
 # Actual put.gd upload completion, using only the existing loopback receiver.
 s=p.rpc('settings.get');doc=s['document'];source=json.loads(Path('/home/patrick/work/sa2/c/putgd/settings.json').read_text()) if False else None
 # Import the synthetic local uploader into this fresh isolated configuration.
 u=P/'loopback.sxcu';u.write_text(json.dumps({'Name':'Synthetic local fallback','DestinationType':'ImageUploader','RequestMethod':'POST','RequestURL':'http://127.0.0.1:19399/upload','Body':'MultipartFormData','FileFormName':'file','URL':'{json:url}'}));p.rpc('settings.importUploader',{'path':str(u),'profileId':'scroll-local','credentialMode':'session','allowInsecureHttp':True,'expectedRevision':s['metadata']['observedRevision']});time.sleep(.5)
 r=p.rpc('upload.files',{'paths':['/home/patrick/work/sa2/cap/capture.png'],'profileId':'scroll-local'});(P/'upload-reply.json').write_text(json.dumps(r));
 for _ in range(100):
  op=p.rpc('operation.inspect',{'id':r['operationId']})
  if op.get('state') in ['done','failed','completed','partial']:break
  time.sleep(.02)
 (P/'upload-final.json').write_text(json.dumps(op));shot('balloon-visible.png');time.sleep(.5);shot('balloon-visible-2.png')
 originalrpc=p.rpc
 def rpc(m,a={}):
  if m=='scroll.prepare':a=dict(a,rect=[0,0,1900,1000])
  if m=='scroll.start':shot('before-first-frame.png')
  return originalrpc(m,a)
 p.rpc=rpc;p.capture('capture',60,40000);shot('tray-restored.png');(P/'done').write_text('done')
except Exception:(P/'error.txt').write_text(traceback.format_exc());raise
finally:
 if f:f.terminate();f.wait(10)
 try:p.rpc('ui.quit')
 except Exception:pass
 time.sleep(2);os.kill(buspid,15)
