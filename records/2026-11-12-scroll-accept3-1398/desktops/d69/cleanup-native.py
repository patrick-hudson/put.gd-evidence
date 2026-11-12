from pathlib import Path
import json,os,subprocess,time,sys
import pass2 as p
P=p.P;h=sys.argv[1]
try:p.rpc('ui.quit')
except Exception:pass
time.sleep(3);owned=[]
for q in Path('/proc').iterdir():
 if not q.name.isdigit():continue
 try:
  if any(x.startswith(('XDG_CONFIG_HOME='+str(P)+'/').encode()) for x in (q/'environ').read_bytes().split(bytes([0]))):owned.append({'pid':int(q.name),'comm':(q/'comm').read_text().strip()})
 except OSError:pass
for v in owned:
 try:os.kill(v['pid'],15)
 except ProcessLookupError:pass
external=[]
for n,allowed in [('receiver.pid',['receiver.py','controlled_receiver.py']),('notify-monitor.pid',['dbus-monitor'])]:
 f=P/n
 if not f.exists():continue
 pid=int(f.read_text());q=Path('/proc')/str(pid)
 if not q.exists():continue
 args=(q/'cmdline').read_bytes().split(bytes([0]));assert any(x.encode() in args or str(P/x).encode() in args for x in allowed),(n,pid)
 os.kill(pid,15);external.append(pid)
time.sleep(2)
before=set((P/'packages-before.txt').read_text().splitlines());after=set((P/'packages-after.txt').read_text().splitlines());gained=sorted(after-before);assert h!='f44' or 'putgd' in gained,gained
cmd=['sudo','-n','dnf','remove','-y','--setopt=clean_requirements_on_remove=False',*gained] if h=='f44' else ['sudo','-n','apt-get','remove','-y','putgd']
with (P/'remove.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,r.returncode
q=['rpm','-qa','--qf','%{NAME}\n'] if h=='f44' else ['dpkg-query','-W','-f=${binary:Package}\n'];data=subprocess.check_output(q);(P/'packages-restored.txt').write_bytes(data);restored=set(data.decode().splitlines());v={'ownedProcessesTerminated':owned,'externalPidsTerminated':external,'removed':cmd,'packageNamesMatch':before==restored,'packageNamesAdded':sorted(restored-before),'packageNamesMissing':sorted(before-restored),'scaleChanged':False,'shortcutPersisted':False};(P/'cleanup.json').write_text(json.dumps(v,indent=2));print(v)
