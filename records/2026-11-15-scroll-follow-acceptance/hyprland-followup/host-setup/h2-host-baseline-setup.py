from pathlib import Path
import shutil,subprocess
P=Path.home()/'work/sfa15/guest-h2';B=Path.home()/'work/sfa15/guest-h2-baseline';assert not B.exists();B.mkdir(mode=0o700)
for f in P.glob('*.py'):shutil.copyfile(f,B/f.name)
s=(B/'accept.py').read_text().replace("/'work/sfa15/guest-h2'","/'work/sfa15/guest-h2-baseline'").replace("GP='/home/lab/work/sfa15'","GP='/home/lab/work/sfa15/b'").replace('/tmp/sh25','/tmp/sb25');(B/'accept.py').write_text(s)
s=(P/'cli').read_text().replace('/home/lab/work/sfa15/cli','/home/lab/work/sfa15/b/cli');(B/'cli').write_text(s);(B/'cli').chmod(0o700)
(B/'helper.log').touch();(B/'runs').mkdir()
import sys;sys.path.insert(0,str(B));import accept as A
cmd=['systemd-run','--user','--unit=sfa15h2-baseline-log','--collect','--property=StandardOutput=append:'+str(B/'helper.log'),'--property=StandardError=append:'+str(B/'helper-stream.err'),'/usr/bin/ssh','-nT',*A.SSH[1:-1],A.SSH[-1],'exec tail -n +1 --sleep-interval=.02 -F /home/lab/work/sfa15/b/helper.log']
subprocess.run(cmd,check=True)
d=A.rpc('diagnostics');assert d['build']['gitTree']=='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3'
import json;(B/'build-proof.json').write_text(json.dumps(d['build'],indent=1));print(json.dumps(d['build']))
