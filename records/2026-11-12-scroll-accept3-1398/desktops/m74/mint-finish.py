from pathlib import Path
import os,json,time,subprocess,hashlib,signal
import pass2 as p
P=p.P
# This owned reference collector drives the desktop; transition as soon as it exits.
def collector_live():
 for q in Path('/proc').iterdir():
  if not q.name.isdigit():continue
  try:
   a=(q/'cmdline').read_bytes().split(bytes([0]))
   if len(a)>1 and a[1] in [b'full-references.py',str(P/'full-references.py').encode()] and (q/'cwd').resolve()==P:return True
  except OSError:pass
 return False
while collector_live():time.sleep(1)
results=[]
try:
 with (P/'late-ruler-verified.console').open('w') as log:
  r=subprocess.run(['python3',str(P/'late-ruler.py')],stdout=log,stderr=subprocess.STDOUT);results.append({'stage':'late-ruler-verified','exitCode':r.returncode})
finally:
 try:
  c=p.rpc('scroll.prepare',{'rect':[100,200,960,600],'maxHeight':30000});p.rpc('scroll.cancel',{'id':c['id']})
 except Exception as ex:results.append({'cleanupPrepareCancel':str(ex)})
 try:p.rpc('ui.quit')
 except Exception:pass
 time.sleep(3);owned=[]
 for q in Path('/proc').iterdir():
  if not q.name.isdigit() or int(q.name)==os.getpid():continue
  try:
   env=(q/'environ').read_bytes().split(bytes([0]));comm=(q/'comm').read_text().strip()
   if any(x.startswith(('XDG_CONFIG_HOME='+str(P)+'/').encode()) for x in env):owned.append({'pid':int(q.name),'comm':comm})
  except OSError:pass
 for v in owned:
  try:os.kill(v['pid'],signal.SIGTERM)
  except ProcessLookupError:pass
 external=[]
 for n,allowed in [('receiver.pid',['receiver.py','controlled_receiver.py']),('notify-monitor.pid',['dbus-monitor'])]:
  f=P/n
  if not f.exists():continue
  pid=int(f.read_text());q=Path('/proc')/str(pid)
  if not q.exists():continue
  args=(q/'cmdline').read_bytes().split(bytes([0]));assert any(x.encode() in args or str(P/x).encode() in args for x in allowed),(n,pid)
  os.kill(pid,signal.SIGTERM);external.append(pid)
 time.sleep(2)
 for package,verb in [('putgd','remove'),('chromium','purge')]:
  with (P/('cleanup-'+package+'.log')).open('w') as log:
   r=subprocess.run(['sudo','-n','apt-get',verb,'-y',package],stdout=log,stderr=subprocess.STDOUT)
  assert r.returncode==0,(package,r.returncode)
 data=subprocess.check_output(['dpkg-query','-W','-f=${binary:Package}\n']);(P/'packages-restored.txt').write_bytes(data)
 before=set((P/'packages-before.txt').read_text().splitlines());after=set(data.decode().splitlines())
 live=[]
 for v in owned:
  q=Path('/proc')/str(v['pid'])
  try:
   if q.exists() and (q/'stat').read_text().split(') ',1)[1].split()[0]!='Z':live.append(v)
  except OSError:pass
 result={'stages':results,'ownedProcessesTerminated':owned,'externalPidsTerminated':external,'packageNamesMatch':before==after,'packageNamesAdded':sorted(after-before),'packageNamesMissing':sorted(before-after),'ownedGuiProcessesRemaining':live,'scaleChanged':False,'persistentHotkeysChanged':False,'desktopNotificationPreferencesChanged':False,'clipboardPriorContentsRead':False}
 (P/'cleanup.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
 assert before==after and not live,'cleanup verification failed'
