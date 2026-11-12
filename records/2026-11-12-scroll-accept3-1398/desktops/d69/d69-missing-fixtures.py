import pass2 as p,fix6 as f,json,subprocess
P=p.P
for name in ['overlayforced','blank','hoverforced','shrink']:
 for i in range(2):
  case='firefox-probe-'+name+'-'+str(i)
  assert not (P/case/'result.json').exists(),case
  ff=P/('ffmissing-'+name+'-'+str(i));ff.mkdir(exist_ok=False);(ff/'user.js').write_text('user_pref("browser.aboutwelcome.enabled",false);user_pref("termsofuse.acceptedVersion",999);user_pref("termsofuse.bypassNotification",true);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')
  try:f.with_fixture(name,['firefox','--no-remote','--profile',str(ff),'--kiosk',(P/(name+'.html')).as_uri()],lambda:p.capture(case,60,30000),wait=18)
  except Exception as e:(P/(case+'-harness-error.txt')).write_text(repr(e))
for args in [['variant-oracle.py'],['replay-all-late.py']]:
 with (P/('final-'+args[0]+'.console')).open('w') as log:subprocess.run(['python3',str(P/args[0])],stdout=log,stderr=subprocess.STDOUT)
