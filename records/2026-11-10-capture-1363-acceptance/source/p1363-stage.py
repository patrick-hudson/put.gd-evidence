import sys,subprocess,shlex
from pathlib import Path
from importlib.machinery import SourceFileLoader
c=SourceFileLoader('c','/tmp/p1363-campaign.py').load_module();h,artifact=sys.argv[1:3];src=c.OUT/'packages-13570fca9'/artifact;dest='/home/patrick/work/i1363/work/acceptance-packages-13570fca9/'+artifact;c.remote(h,'mkdir -p '+shlex.quote(dest));subprocess.run(['rsync','-qr','-e',' '.join(c.ssh(h)[:-1]),str(src)+'/',c.ssh(h)[-1]+':'+dest+'/'],check=True)
