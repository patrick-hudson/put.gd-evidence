import pass2 as p,fix6 as f,record_run,rfb,json,subprocess,time,os,traceback
from pathlib import Path
from PIL import Image
P=p.P
p.setup()
# Close the isolated resident's optional dashboard so the owned fixture is the only foreground app.
closed=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:
  if (q/'comm').read_text().strip()=='putgd-ui' and ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (q/'environ').read_bytes().split(bytes([0])):closed.append(int(q.name));os.kill(int(q.name),15)
 except OSError:pass
(P/'dashboard-preparation.json').write_text(json.dumps({'closedOwnedUiPids':closed}));web=P/'web';web.mkdir(mode=0o700)
for n in ['shrink']:
 s=(P/(n+'.html')).read_text().replace('setTimeout(()=>sc.scrollTop=999999,1000)','').replace('setTimeout(()=>scrollTo(0,999999),1000)','');(web/(n+'.html')).write_text(s)
server=subprocess.Popen(['python3','-m','http.server','19402','--bind','127.0.0.1','--directory',str(web)],stdout=open(P/'http.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'http.pid').write_text(str(server.pid))
try:
 for n in ['shrink']:
  for i in range(2):
   name='firefox-retry-'+n+'-'+str(i);profile=P/('ff-'+n+'-'+str(i));profile.mkdir();(profile/'user.js').write_text('user_pref("browser.aboutwelcome.enabled",false);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')
   def run():
    import scroll_run
    checks=[]
    for attempt in range(3):
     v=rfb.RFB(5900);v.frame();time.sleep(.5);v.screenshot(P/(name+'-ready-'+str(attempt)+'.png'));v.sock.close();im=Image.open(P/(name+'-ready-'+str(attempt)+'.png')).convert('RGB');bad=0
     for y in range(80):
      bits=scroll_run.pattern(*divmod(y,40));left=120 if n=='sidebar' else 0;top=40 if n=='sticky' else 80 if n=='shrink' else 0
      for c in range(12):bad+=int(max(abs(z-(16 if bits&(0x8000>>c) else 250)) for z in im.getpixel((left+64+c*55+27,top+y)))>12)
     checks.append({'attempt':attempt,'badSamples':bad})
     if bad==0:break
     time.sleep(1)
    (P/(name+'-ready.json')).write_text(json.dumps(checks,indent=2));assert bad==0,checks;print(name,'FIXTURE VERIFIED',flush=True);p.capture(name,60,40000,header=40 if n=='sticky' else 0,footer=40 if n=='sticky' else 0)
   try:f.with_fixture(name,['firefox','--new-instance','--no-remote','--profile',str(profile),'--kiosk','http://127.0.0.1:19402/'+n+'.html'],run,12,MOZ_DBUS_REMOTE='0',MOZ_NO_REMOTE='1',MOZ_ENABLE_WAYLAND='1',MOZ_APP_REMOTINGNAME='putgd-scroll-test-'+str(i)+'-'+n)
   except Exception:(P/(name+'.error')).write_text(traceback.format_exc());print(name,'HARNESS BLOCKED',flush=True)
 (P/'retry.done').write_text('done')
finally:server.terminate();server.wait(10)
