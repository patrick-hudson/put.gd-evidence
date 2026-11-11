from pathlib import Path
import sys,shlex,json
p=Path('/home/patrick/work/scn');sys.argv=['confirm.py','n'];ns={};exec((p/'confirm.py').read_text().split('try:\n for i in range(3):')[0],ns)
cmd=ns['cmd'];o=ns['o']
# Suppress the startup prompt in this synthetic-fixture-only private browser profile.
prefs='user_pref("browser.termsofuse.bypassNotification",true); user_pref("browser.termsofuse.prefState",2);'
(o/'firefox-startup-prefs.log').write_text(cmd('printf %s '+shlex.quote(prefs)+' >> /home/lab/v3firefox/user.js'))
cmd("python3 -c "+shlex.quote("from pathlib import Path;p=Path('/tmp/v3/cases');[(p/n).rename(p/('harness-firefox-'+n)) for n in ['browser-bottom-0','browser-bottom-1','browser-bottom-2','browser-top-0','browser-top-1']]"))
for n in ['export.tgz','hashes.json','final']:(o/n).rename(o/('initial-'+n))
for i in range(3):ns['browser']('browser-bottom-%d'%i,True)
for i in range(2):ns['browser']('browser-top-%d'%i,False)
import subprocess
subprocess.run(['python3',str(p/'acc.py'),'n','cn','export'],check=True)
(o/'browser-retry.done').write_text('done')
