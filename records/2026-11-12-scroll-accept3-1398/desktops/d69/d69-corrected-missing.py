from pathlib import Path
import time,subprocess,json
P=Path('/home/patrick/work/s3a')
while Path('/proc/4129145').exists():time.sleep(1)
import pass2 as p,fix6 as f
s=p.rpc('settings.get');p.rpc('settings.patch',{'patch':{'preferences':{'scrollCaptureFromTop':True}},'expectedRevision':s['metadata']['observedRevision']})
subprocess.run(['python3',str(P/'variant-oracle.py')],check=True)
for name in ['overlayforced','blank','hoverforced','shrink']:
 for i in range(2):
  case='firefox-probe-'+name+'-'+str(i);out=P/case;qualified=False
  if (out/'result.json').exists() and (out/'capture.png').exists() and (out/'variant-verification.json').exists():
   r=json.loads((out/'result.json').read_text());v=json.loads((out/'variant-verification.json').read_text());log=(out/'helper.log').read_text();qualified=r.get('capture',{}).get('endReason')=='end_of_content' and v.get('exact') and 'top proved' in log
  if qualified:
   (out/'qualification.json').write_text(json.dumps({'qualified':True,'reason':'all document rows verified, top proved in own helper log; prepare occurred after preference correction'},indent=2));continue
  if out.exists():out.rename(P/(case+'-preference-attempt1'))
  ff=P/('ffverified-'+name+'-'+str(i));ff.mkdir(exist_ok=False);(ff/'user.js').write_text('user_pref("browser.aboutwelcome.enabled",false);user_pref("termsofuse.acceptedVersion",999);user_pref("termsofuse.bypassNotification",true);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')
  try:f.with_fixture(case,['firefox','--no-remote','--profile',str(ff),'--kiosk',(P/(name+'.html')).as_uri()],lambda:p.capture(case,60,30000),wait=18)
  except Exception as e:(P/(case+'-corrected-harness-error.txt')).write_text(repr(e))
for n in ['variant-oracle.py','replay-all-late.py']:
 with (P/('corrected-'+n+'.console')).open('w') as log:subprocess.run(['python3',str(P/n)],stdout=log,stderr=subprocess.STDOUT)
(P/'corrected-missing.done').write_text('done')
