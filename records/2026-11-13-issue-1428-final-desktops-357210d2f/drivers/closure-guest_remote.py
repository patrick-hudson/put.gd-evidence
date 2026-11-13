from pathlib import Path
import subprocess,sys,shlex,uuid
r=Path('/tmp/b1428');name=sys.argv[1];assert name.startswith('f') and name.isalnum();args=sys.argv[2:];base='/home/patrick/work/b1428';stage=base+'/transfer-'+name
def host(*a):subprocess.run(['python3',str(r/'remote.py'),'f44',*a],check=True)
def guest(*a):host(' '.join(shlex.quote(x) for x in ['python3',base+'/guest.py',name,*a]))
if args[0] in ('--get','--copy'):
 host('mkdir -p -m 700 '+shlex.quote(stage))
 if args[0]=='--get':
  src,dst=args[1:];p=Path(src);out=stage+'/'+p.parent.name+'-'+p.name;guest('--get',src,out);host('--get',out,dst)
 else:
  files=args[1:-1];dst=args[-1];folder=stage+'/'+uuid.uuid4().hex;host('mkdir -m 700 '+shlex.quote(folder));host('--copy',*files,folder+'/');guest('--copy',*[folder+'/'+Path(x).name for x in files],dst)
else:guest(*args)
