import subprocess,sys,json,hashlib
from pathlib import Path
import record_run
P=Path('/home/patrick/work/pcn');h=sys.argv[1]
commands=[['rpm','-qa','--qf','%{NAME}\n']] if h=='f44' else [['dpkg-query','-W','-f=${binary:Package}\n']]
(P/'packages-before.txt').write_bytes(subprocess.check_output(commands[0]))
if h=='f44':
 e,_=record_run.session_environment();(P/'extensions-before.txt').write_bytes(subprocess.check_output(['gsettings','get','org.gnome.shell','enabled-extensions'],env=e));(P/'disabled-extensions-before.txt').write_bytes(subprocess.check_output(['gsettings','get','org.gnome.shell','disabled-extensions'],env=e));f=next(P.glob('*.rpm'));cmd=['sudo','-n','dnf','install','-y',str(f)]
else:f=next(P.glob('*.deb'));cmd=['sudo','-n','apt-get','install','-y',str(f)]
with (P/'install.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
(P/'packages-after.txt').write_bytes(subprocess.check_output(commands[0]));assert r.returncode==0,r.returncode
(P/'installed.json').write_text(json.dumps({'package':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'build':json.loads(subprocess.check_output(['putgd-cli','--version-json']))},indent=2))
