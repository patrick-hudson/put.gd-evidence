import pass2 as p,subprocess,time,json,os,rfb,traceback
from pathlib import Path
from gi.repository import Gio,GLib
P=p.P;original=json.loads((P/'env.json').read_text());b=Gio.bus_get_sync(Gio.BusType.SESSION,None);names=b.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','ListNames',None,GLib.VariantType.new('(as)'),Gio.DBusCallFlags.NONE,3000,None).unpack()[0]
proxyPath=P/'notice-proxy.sock';assert len(str(proxyPath.resolve()).encode())<=107
(P/'notice-proxy-preflight.json').write_text(json.dumps({'path':str(proxyPath),'utf8Bytes':len(str(proxyPath.resolve()).encode()),'denied':'org.freedesktop.Notifications','allowed':sorted(n for n in names if not n.startswith(':') and n!='org.freedesktop.Notifications')}))
p.rpc('ui.quit');time.sleep(3)
cmd=['xdg-dbus-proxy',original['DBUS_SESSION_BUS_ADDRESS'],str(proxyPath),'--filter','--own=org.kde.StatusNotifierItem-*']+['--talk='+n for n in names if not n.startswith(':') and n!='org.freedesktop.Notifications']
proxy=subprocess.Popen(cmd,stdout=open(P/'notification-proxy.log','w'),stderr=subprocess.STDOUT);(P/'notification-proxy.pid').write_text(str(proxy.pid))
def launch(env):
 q=subprocess.Popen(['putgd','--background'],env=env,stdout=open(P/'fallback-resident.log','a'),stderr=subprocess.STDOUT,start_new_session=True);(P/'resident.pid').write_text(str(q.pid));(P/'env.json').write_text(json.dumps(env));time.sleep(3)
def shot(n):
 v=rfb.RFB(5900);v.frame();v.screenshot(P/n);v.sock.close()
f=None;orig=p.rpc
try:
 for _ in range(30):
  if proxyPath.exists():break
  time.sleep(.1)
 env=dict(original,DBUS_SESSION_BUS_ADDRESS='unix:path='+str(proxyPath));launch(env)
 f=subprocess.Popen(['python3',str(P/'full_fixture.py')],env=env,stdout=open(P/'fallback-proxy-fixture.log','w'),stderr=subprocess.STDOUT);time.sleep(3)
 orig('upload.files',{'paths':[str(P/'cap/capture.png')],'profileId':'scroll-local'});time.sleep(1);shot('proxy-balloon-visible.png')
 def traced(m,a={}):
  if m=='scroll.prepare':a=dict(a,rect=[0,0,1900,1080])
  if m=='scroll.start':shot('proxy-balloon-before-first-frame.png')
  return orig(m,a)
 p.rpc=traced;p.capture('fallback-proxy-capture',60,40000);shot('proxy-tray-restored.png');(P/'fallback-proxy.done').write_text('done')
except Exception:(P/'fallback-proxy.error').write_text(traceback.format_exc());raise
finally:
 p.rpc=orig
 if f:f.terminate();f.wait(10)
 try:orig('ui.quit')
 except Exception:pass
 time.sleep(2);proxy.terminate();proxy.wait(10);launch(original)
