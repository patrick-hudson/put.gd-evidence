import pass2 as p,subprocess,time,json,os,rfb,traceback
P=p.P;e=json.loads((P/'env.json').read_text());server=subprocess.Popen(['python3',str(P/'fallback-server.py')],stdout=open(P/'fallback-server.console','w'),stderr=subprocess.STDOUT);(P/'fallback-server.pid').write_text(str(server.pid))
def shot(n):
 v=rfb.RFB(5900);v.frame();v.screenshot(P/n);v.sock.close()
f=None;original=p.rpc
try:
 for _ in range(50):
  if server.poll() is not None:raise RuntimeError('Fallback server could not replace daemon; see owner record')
  if (P/'fallback-server.ready').exists():break
  time.sleep(.1)
 f=subprocess.Popen(['python3',str(P/'full_fixture.py')],env=e,stdout=open(P/'fallback-fixture.log','w'),stderr=subprocess.STDOUT);time.sleep(3)
 original('upload.files',{'paths':[str(P/'cap/capture.png')],'profileId':'scroll-local'});time.sleep(1);shot('balloon-visible.png')
 def traced(m,a={}):
  if m=='scroll.prepare':a=dict(a,rect=[0,0,1900,1080])
  if m=='scroll.start':shot('balloon-before-first-frame.png')
  return original(m,a)
 p.rpc=traced;p.capture('fallback-capture',60,40000)
 shot('tray-restored.png');(P/'fallback-case.done').write_text('done')
except Exception:(P/'fallback-case.error').write_text(traceback.format_exc());raise
finally:
 p.rpc=original
 if f:f.terminate();f.wait(10)
 server.terminate();server.wait(10)
