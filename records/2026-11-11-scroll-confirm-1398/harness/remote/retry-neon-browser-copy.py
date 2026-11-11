from pathlib import Path
import sys,subprocess,shlex
p=Path('/home/patrick/work/scn');sys.argv=['confirm.py','n'];ns={};src=(p/'confirm.py').read_text().split('try:\n for i in range(3):')[0].replace("else 'firefox --no-remote", "else '/home/lab/firefox-fixture/firefox --no-remote");exec(src,ns)
cmd=ns['cmd'];o=ns['o'];assert (o/'browser-retry.done').exists()
(o/'browser-policy-identity.log').write_text(cmd('sha256sum /usr/lib/firefox/firefox /home/lab/firefox-fixture/firefox; cat /home/lab/firefox-fixture/distribution/policies.json'))
cmd("python3 -c "+shlex.quote("from pathlib import Path;p=Path('/tmp/v3/cases');[(p/n).rename(p/('harness-firefox2-'+n)) for n in ['browser-bottom-0','browser-bottom-1','browser-bottom-2','browser-top-0','browser-top-1']]"))
for n in ['export.tgz','hashes.json','final']:(o/n).rename(o/('retry2-'+n))
for i in range(3):ns['browser']('browser-bottom-%d'%i,True)
for i in range(2):ns['browser']('browser-top-%d'%i,False)
subprocess.run(['python3',str(p/'acc.py'),'n','cn','export'],check=True)
(o/'browser-copy-retry.done').write_text('done')
