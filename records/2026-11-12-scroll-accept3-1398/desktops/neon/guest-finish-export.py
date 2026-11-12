from pathlib import Path
import json,os,sys,time,hashlib,tarfile,shutil
import pass2 as p
P=p.P;tag=sys.argv[1];out=P.parent/('s3-'+tag+'-evidence.tar.gz');assert not out.exists()
try:p.rpc('ui.quit')
except Exception as ex:(P/'quit-error.txt').write_text(str(ex))
time.sleep(3);stopped=[]
for file,allowed in [('receiver.pid',['receiver.py','controlled_receiver.py']),('notify-monitor.pid',['dbus-monitor'])]:
 f=P/file
 if not f.exists():continue
 pid=int(f.read_text());q=Path('/proc')/str(pid)
 if not q.exists():continue
 a=(q/'cmdline').read_bytes().split(bytes([0]));matching=any(x.encode() in a or str(P/x).encode() in a for x in allowed)
 if matching:os.kill(pid,15);stopped.append({'pid':pid,'source':file})
for q in Path('/proc').iterdir():
 if not q.name.isdigit() or int(q.name)==os.getpid():continue
 try:
  if any(x.startswith(('XDG_CONFIG_HOME='+str(P)+'/').encode()) for x in (q/'environ').read_bytes().split(bytes([0]))):os.kill(int(q.name),15);stopped.append({'pid':int(q.name),'source':'owned private config environment'})
 except OSError:pass
time.sleep(2);(P/'guest-process-cleanup.json').write_text(json.dumps(stopped,indent=2))
for n in ['accept3-packages.log','accept3-packages-sync.log','accept3-firefox-install.log']:
 f=Path.home()/n
 if f.exists():shutil.copyfile(f,P/n)
files=[(f,str(f.relative_to(P))) for f in sorted(P.rglob('*')) if f.is_file() and not f.is_symlink()]
if tag=='omarchy':
 old=P.parent/'s3h-attempt1';files += [(f,'unqualified-attempt1/'+str(f.relative_to(old))) for f in sorted(old.rglob('*')) if f.is_file() and not f.is_symlink()]
index={n:hashlib.sha256(f.read_bytes()).hexdigest() for f,n in files};idx=P/'export-index.json';idx.write_text(json.dumps(index,indent=1))
with tarfile.open(out,'w:gz') as t:
 for f,n in files+[(idx,'export-index.json')]:t.add(f,arcname=n,recursive=False)
out.chmod(0o600)
v={'archive':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'files':len(files)};(P/'export-receipt.json').write_text(json.dumps(v,indent=2));print(json.dumps(v),flush=True)
