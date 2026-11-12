from pathlib import Path
import subprocess,sys,json
P=Path('/home/lab/work/s3a');h=sys.argv[1]
cmd=['sudo','-n','dnf','install','-y','chromium'] if h=='f44' else ['sudo','-n','apt-get','install','-y','chromium']
if h!='f44':(P/'apt-manual-before.txt').write_bytes(subprocess.check_output(['apt-mark','showmanual']))
r=subprocess.run(cmd,stdout=(P/'chromium-install.log').open('w'),stderr=subprocess.STDOUT)
print('install Chromium return',r.returncode)
(P/'packages-after.txt').write_bytes(subprocess.check_output(['rpm','-qa','--qf','%{NAME}\n'] if h=='f44' else ['dpkg-query','-W','-f=${binary:Package}\n']))
