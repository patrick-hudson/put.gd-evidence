"""Compose on the builder; put.gd draws every call-out. Workstation only transfers."""
import sys,json,subprocess,shlex
from pathlib import Path
from importlib.machinery import SourceFileLoader
c=SourceFileLoader('c','/tmp/p1363-campaign.py').load_module()
d,name,specpath=sys.argv[1:4];h,r,p,g,pin,port,vnc,k,known,wall=c.PROFILES[d];E='/home/patrick/work/i1363/work/acceptance-1363/'+r
for source,dest in [(Path(specpath),'/tmp/p1363-picture-spec.json'),(Path('/tmp/p1363-picture-compose.py'),'/tmp/p1363-picture-compose.py'),(c.S/'annotate.py','/tmp/p1363-annotate.py')]:subprocess.run(['rsync','-q','-e',' '.join(c.ssh(h)[:-1]),str(source),c.ssh(h)[-1]+':'+dest],check=True)
c.remote(h,shlex.join(['python3','/tmp/p1363-picture-compose.py',E,name,'/tmp/p1363-picture-spec.json']))
key='/home/patrick/work/put.gd/work/lab-bootstrap-'+k+'/identity'
c.remote(h,shlex.join(['python3','/tmp/p1363-annotate.py',r,key,E+'/'+name+'-pre.png',E+'/'+name+'.png',E+'/'+name+'-spec.json']))
path=c.OUT/'2026-11-10-capture-1363-acceptance'/'pictures';path.mkdir(exist_ok=True)
subprocess.run(['rsync','-q','-e',' '.join(c.ssh(h)[:-1]),c.ssh(h)[-1]+':'+E+'/'+name+'.png',str(path/(name+'.png'))],check=True)
print(path/(name+'.png'))
