import pass2 as p,fix6 as f,subprocess,json
P=p.P;ff=P/'ffprofile';ff.mkdir(exist_ok=True);(ff/'user.js').write_text('user_pref("browser.aboutwelcome.enabled",false);user_pref("termsofuse.acceptedVersion",999);user_pref("termsofuse.bypassNotification",true);user_pref("browser.shell.checkDefaultBrowser",false);user_pref("browser.startup.homepage_override.mstone","ignore");')
for i in range(2):
 f.with_fixture('browser-end-'+str(i),['firefox','--no-remote','--profile',str(ff),'--kiosk',(P/'bottom.html').as_uri()],lambda:p.capture('firefox-end-'+str(i)),wait=18)
f.with_fixture('browser-top',['firefox','--no-remote','--profile',str(ff),'--kiosk',(P/'ruler.html').as_uri()],lambda:p.capture('firefox-top'),wait=18)
