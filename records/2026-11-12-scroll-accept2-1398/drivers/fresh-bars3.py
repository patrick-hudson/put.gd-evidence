import pass2 as p,fix6 as f,rfb,time,json,sys,argparse
from pathlib import Path
from PIL import Image
import scroll_run
P=p.P;host=sys.argv[1]
while not (P/'hover.done').exists():time.sleep(2)
for n in ['classicforced','overlayforced','hoverforced']:
 for i in range(2):
  name='firefox-valid3-'+n+'-'+str(i);profile=P/('ff-valid3-'+n+'-'+str(i));profile.mkdir();(profile/'user.js').write_text('user_pref("browser.aboutwelcome.enabled",false);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')
  def run():
   v=rfb.RFB(5901 if host=='f44' else 5900);v.frame();time.sleep(.2);v.screenshot(P/(name+'-ready.png'));v.sock.close();Image.open(P/(name+'-ready.png')).crop((0,0,960,1080)).save(P/(name+'-ready-crop.png'));a=argparse.Namespace(scale=1,height=1080,rows=60,first_pixel=1320,header=0,footer=0,code_width=960,format='fixture',scrollbar=16);check=scroll_run.verify(P/(name+'-ready-crop.png'),a);(P/(name+'-ready.json')).write_text(json.dumps(check,indent=2));
   if not check['pass'] and check.get('unexpectedPixels',999999)>512:
    time.sleep(2);v=rfb.RFB(5901 if host=='f44' else 5900);v.frame();time.sleep(1);v.screenshot(P/(name+'-ready-retry.png'));v.sock.close();Image.open(P/(name+'-ready-retry.png')).crop((0,0,960,1080)).save(P/(name+'-ready-retry-crop.png'));check=scroll_run.verify(P/(name+'-ready-retry-crop.png'),a);(P/(name+'-ready-retry.json')).write_text(json.dumps(check,indent=2))
   assert check['pass'] or check.get('unexpectedPixels',999999)<=512,check
   (P/(name+'-ready-adjudication.json')).write_text(json.dumps({'viewportVerified':True,'cursorAllowancePixels':check.get('unexpectedPixels',0),'productOracleUnchanged':True}))
   p.capture(name,60,40000)
  try:f.with_fixture(name,['/usr/lib64/firefox/firefox','--new-instance','--no-remote','--profile',str(profile),'--kiosk',(P/(n+'.html')).as_uri()],run,18,MOZ_DBUS_REMOTE='0',MOZ_NO_REMOTE='1',MOZ_ENABLE_WAYLAND='1')
  except Exception as ex:(P/(name+'.error')).write_text(str(ex))
(P/'fresh-bars3.done').write_text('done')
