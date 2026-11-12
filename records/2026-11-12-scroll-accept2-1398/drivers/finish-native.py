import pass2 as p,os,subprocess,json,time,sys
from pathlib import Path
P=p.P
try:
 a=p.rpc('scroll.prepare',{'rect':[100,200,960,600]});p.rpc('scroll.cancel',{'id':a['id']})
except Exception as ex:(P/'dismiss-error.txt').write_text(str(ex))
subprocess.run(['python3',str(P/'cleanup.py')],check=True)
f=P/'receiver.pid'
if f.exists():
 pid=int(f.read_text());q=Path('/proc')/str(pid)
 if q.exists():
  cmd=(q/'cmdline').read_bytes().split(b'\0');assert str(P/'receiver.py').encode() in cmd;os.kill(pid,15)
time.sleep(1)
h=sys.argv[1]
if h=='f44':
 base=Path('/home/patrick/work/sa2');before=set((base/'packages-before.txt').read_text().splitlines());after=set((base/'packages-after.txt').read_text().splitlines());gained=sorted(after-before);assert gained==['jasper-libs','libmng','putgd','qt6-qtimageformats'],gained
 cmd=['sudo','-n','dnf','remove','-y',*gained]
else:cmd=['sudo','-n','apt-get','remove','-y','putgd']
with (P/'remove.log').open('w') as log:q=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
assert q.returncode==0,q.returncode
(P/'finished.json').write_text(json.dumps({'removedCommand':cmd,'success':True},indent=2))
